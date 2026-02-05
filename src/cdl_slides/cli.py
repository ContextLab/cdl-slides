"""Click CLI for cdl-slides."""

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
@click.option("--lines", "-l", "max_lines", type=int, default=20, show_default=True, help="Max code lines per slide.")
@click.option(
    "--rows", "-r", "max_table_rows", type=int, default=8, show_default=True, help="Max table rows per slide."
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
def compile(
    input_file: Path,
    output: Optional[Path],
    output_format: str,
    max_lines: int,
    max_table_rows: int,
    no_split: bool,
    keep_temp: bool,
    theme_dir: Optional[Path],
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
    from cdl_slides.assets import detect_marp_cli

    click.echo(f"cdl-slides {__version__}")

    marp = detect_marp_cli()
    if marp:
        click.echo(click.style(f"Marp CLI: {marp}", fg="green"))
    else:
        click.echo(click.style("Marp CLI: not found", fg="red"))
        click.echo("Install with: npm install -g @marp-team/marp-cli")
