"""Click CLI for cdl-slides."""

import subprocess
import sys
from pathlib import Path
from typing import Optional

import click

from cdl_slides import __version__

TEMPLATE_MARKDOWN = """\
---
marp: true
theme: cdl-theme
paginate: true
header: 'Your Presentation Title'
footer: 'Contextual Dynamics Lab'
---

<!-- _class: title -->

# Your Presentation Title

## Subtitle Goes Here

**Your Name**
Contextual Dynamics Lab · Dartmouth College

---

# First Slide

- Bullet point one
- Bullet point two
- Bullet point three

---

# Code Example

```python
def hello():
    print("Hello from CDL Slides!")
```

---

<!-- _class: title -->

# Thank You!

Questions?
"""

POSTER_TEMPLATE_MARKDOWN = """\
---
marp: true
theme: cdl-poster
size: A0
title: "Your Poster Title"
authors:
  - name: "Your Name"
    affiliation: "Your Institution"
---

```poster-layout
TTTTTTTTTT
IIIMMMMRRR
IIIMMMMRRR
CCCCMMMMDD
```

## T: Poster Title

# Your Poster Title Here
**Your Name** · Your Institution

## I: Introduction

Write your introduction here. Explain the background and motivation for your research.

- Key background point
- Research question
- Significance

## M: Methods

Describe your methodology:

```python
# Example code
def analyze(data):
    return process(data)
```

## R: Results

Present your key findings:

$$y = mx + b$$

<div class="note-box" data-title="Key Finding">
Highlight important results here.
</div>

## C: Conclusion

Summarize your conclusions and future directions.

## D: References

1. Author et al. (2024) *Journal Name*
2. Other Author (2023) *Conference*
"""


def _format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


@click.group()
@click.version_option(version=__version__, prog_name="cdl-slides")
def main() -> None:
    pass


@main.command()
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path), default=None, help="Output file or directory.")
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["html", "pdf", "pptx", "both"], case_sensitive=False),
    default="both",
    show_default=True,
    help="Output format.",
)
@click.option("--lines", "-l", "max_lines", type=int, default=30, show_default=True, help="Max code lines per slide.")
@click.option(
    "--rows", "-r", "max_table_rows", type=int, default=10, show_default=True, help="Max table rows per slide."
)
@click.option("--no-split", is_flag=True, default=False, help="Disable auto-splitting of code blocks and tables.")
@click.option("--keep-temp", is_flag=True, default=False, help="Keep temporary processed files for debugging.")
@click.option(
    "--theme-dir",
    "-t",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Custom theme directory.",
)
@click.option(
    "--no-animations",
    is_flag=True,
    default=False,
    help="Skip processing of manim and animate blocks (useful for CI).",
)
def compile(
    input_file: Path,
    output: Optional[Path],
    output_format: str,
    max_lines: int,
    max_table_rows: int,
    no_split: bool,
    keep_temp: bool,
    theme_dir: Optional[Path],
    no_animations: bool,
) -> None:
    """Compile a Markdown file into a CDL-themed Marp presentation."""
    from cdl_slides.compiler import CompilationError, compile_presentation

    click.echo(click.style(f"Compiling {input_file.name}...", fg="cyan"))

    try:
        results = compile_presentation(
            input_file=input_file,
            output_file=output,
            output_format=output_format,
            max_lines=max_lines,
            max_table_rows=max_table_rows,
            no_split=no_split,
            keep_temp=keep_temp,
            theme_dir=theme_dir,
            skip_animations=no_animations,
        )
    except FileNotFoundError as exc:
        click.echo(click.style(f"Error: {exc}", fg="red"), err=True)
        sys.exit(1)
    except CompilationError as exc:
        click.echo(click.style(f"Compilation failed: {exc}", fg="red"), err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo(click.style("\nInterrupted.", fg="yellow"), err=True)
        sys.exit(130)

    for warning in results.get("warnings", []):
        click.echo(click.style(f"  Warning: {warning}", fg="yellow"))

    click.echo(click.style("\nOutput:", fg="green", bold=True))
    for file_info in results.get("files", []):
        size_str = _format_size(file_info["size"])
        click.echo(f"  {file_info['format'].upper():5s}  {file_info['path']}  ({size_str})")

    click.echo(click.style("Done.", fg="green"))


@main.command()
@click.argument("directory", type=click.Path(path_type=Path), default=".")
def init(directory: Path) -> None:
    """Initialize a new presentation directory with a template .md file."""
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=True)

    target = directory / "slides.md"
    if target.exists():
        click.echo(click.style(f"File already exists: {target}", fg="yellow"))
        if not click.confirm("Overwrite?", default=False):
            click.echo("Aborted.")
            return

    target.write_text(TEMPLATE_MARKDOWN, encoding="utf-8")
    click.echo(click.style(f"Created {target}", fg="green"))
    click.echo(f"Edit the file, then compile with:\n  cdl-slides compile {target}")


@main.command()
def version() -> None:
    """Show version info and Marp CLI status."""
    from cdl_slides.marp_cli import get_marp_version_info

    click.echo(f"cdl-slides {__version__}")

    info = get_marp_version_info()
    if info["installed"]:
        source_label = {"system": "system", "cached": "auto-installed"}.get(info["source"], info["source"])
        click.echo(click.style(f"Marp CLI: {info['path']} ({source_label})", fg="green"))
        if info["version"]:
            click.echo(f"  Version: {info['version']}")
    else:
        click.echo(click.style("Marp CLI: not found (will auto-install on first compile)", fg="yellow"))
        if info["source"] == "npx_available":
            click.echo("  npx detected — can use @marp-team/marp-cli via npx")


def _check_system_deps() -> bool:
    """Check if manim system dependencies are available. Returns True if OK."""
    try:
        import manim  # noqa: F401

        return True
    except ImportError as e:
        error_msg = str(e).lower()
        return "pango" not in error_msg and "cairo" not in error_msg and "gobject" not in error_msg


def _install_system_deps() -> bool:
    """Install system dependencies. Returns True on success."""
    import platform
    import shutil
    import subprocess

    system = platform.system()

    if system == "Linux":
        if shutil.which("apt-get"):
            cmd = ["sudo", "apt-get", "update"]
            subprocess.run(cmd, check=True)
            cmd = ["sudo", "apt-get", "install", "-y", "libpango1.0-dev", "libcairo2-dev", "ffmpeg"]
            subprocess.run(cmd, check=True)
            return True
        elif shutil.which("dnf"):
            cmd = ["sudo", "dnf", "install", "-y", "pango-devel", "cairo-devel", "ffmpeg"]
            subprocess.run(cmd, check=True)
            return True
        elif shutil.which("pacman"):
            cmd = ["sudo", "pacman", "-S", "--noconfirm", "pango", "cairo", "ffmpeg"]
            subprocess.run(cmd, check=True)
            return True
        else:
            return False
    elif system == "Darwin":
        if shutil.which("brew"):
            cmd = ["brew", "install", "pango", "cairo", "ffmpeg"]
            subprocess.run(cmd, check=True)
            return True
        else:
            return False
    else:
        return True


@main.command()
def setup() -> None:
    """Set up cdl-slides: install system dependencies and Marp CLI."""
    import platform

    from cdl_slides.marp_cli import get_marp_version_info, resolve_marp_cli

    system = platform.system()

    if system in ("Linux", "Darwin"):
        if _check_system_deps():
            click.echo(click.style("System dependencies: OK", fg="green"))
        else:
            click.echo("Installing system dependencies (pango, cairo, ffmpeg)...")
            try:
                if _install_system_deps():
                    click.echo(click.style("System dependencies installed.", fg="green"))
                else:
                    click.echo(click.style("Could not detect package manager.", fg="red"), err=True)
                    click.echo("Install manually: pango, cairo, ffmpeg", err=True)
            except subprocess.CalledProcessError as e:
                click.echo(click.style(f"Installation failed: {e}", fg="red"), err=True)
                sys.exit(1)

    info = get_marp_version_info()
    if info["installed"]:
        source_label = {"system": "system", "cached": "auto-installed"}.get(info["source"], info["source"])
        click.echo(click.style(f"Marp CLI: OK ({source_label})", fg="green"))
    else:
        click.echo("Downloading Marp CLI standalone binary...")
        result = resolve_marp_cli()
        if result:
            click.echo(click.style("Marp CLI installed.", fg="green"))
        else:
            click.echo(click.style("Failed to install Marp CLI.", fg="red"), err=True)
            click.echo("Try installing manually: npm install -g @marp-team/marp-cli", err=True)
            sys.exit(1)

    click.echo(click.style("\nSetup complete!", fg="green", bold=True))


@main.group()
def poster() -> None:
    """Commands for academic poster creation."""
    pass


@poster.command()
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output file or directory.",
)
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["html", "pdf", "both"], case_sensitive=False),
    default="pdf",
    show_default=True,
    help="Output format (no pptx for posters).",
)
@click.option(
    "--keep-temp",
    is_flag=True,
    default=False,
    help="Keep temporary processed files for debugging.",
)
def compile(input_file: Path, output: Optional[Path], output_format: str, keep_temp: bool) -> None:  # noqa: F811
    """Compile a Markdown file into a CDL-themed academic poster."""
    from cdl_slides.compiler import CompilationError
    from cdl_slides.poster_compiler import compile_poster

    click.echo(click.style(f"Compiling {input_file.name}...", fg="cyan"))

    try:
        result = compile_poster(
            input_file=input_file,
            output_file=output,
            output_format=output_format,
            keep_temp=keep_temp,
        )

        # Display results
        click.echo(click.style("✓ Poster compiled successfully!", fg="green", bold=True))
        for file_info in result["files"]:
            size_kb = file_info["size"] / 1024
            click.echo(f"  → {file_info['path']} ({size_kb:.1f} KB)")

        if result.get("warnings"):
            click.echo(click.style("\nWarnings:", fg="yellow"))
            for warning in result["warnings"]:
                click.echo(f"  ⚠ {warning}")

    except CompilationError as e:
        click.echo(click.style(f"✗ Compilation failed: {e}", fg="red"), err=True)
        sys.exit(1)
    except FileNotFoundError as e:
        click.echo(click.style(f"✗ File not found: {e}", fg="red"), err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo(click.style("\n✗ Compilation cancelled.", fg="yellow"), err=True)
        sys.exit(130)


@poster.command()
@click.argument("directory", type=click.Path(path_type=Path), default=".")
def init(directory: Path) -> None:  # noqa: F811
    """Initialize a new poster directory with a template .md file."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    poster_file = directory / "poster.md"
    if poster_file.exists():
        click.echo(click.style(f"✗ {poster_file} already exists.", fg="red"), err=True)
        sys.exit(1)

    poster_file.write_text(POSTER_TEMPLATE_MARKDOWN, encoding="utf-8")
    click.echo(click.style(f"✓ Created {poster_file}", fg="green"))
    click.echo(f"  Edit the file, then run: cdl-slides poster compile {poster_file}")
