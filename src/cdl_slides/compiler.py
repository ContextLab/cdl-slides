"""Compilation pipeline for cdl-slides.

Orchestrates: preprocessing → Marp CLI → JS injection → output.
"""

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

from cdl_slides.assets import (
    copy_assets_alongside_output,
    get_js_dir,
    get_marp_install_instructions,
    prepare_theme_for_compilation,
)
from cdl_slides.marp_cli import resolve_marp_cli


class CompilationError(Exception):
    """Raised when compilation fails."""


def _inject_js_into_html(html_path: Path) -> None:
    """Inject chart JS files into compiled HTML output.

    - chart-defaults.js → <script> before </head>
    - chart-animations.js → <script> before </body>
    """
    js_dir = get_js_dir()
    html_content = html_path.read_text(encoding="utf-8")

    defaults_js = js_dir / "chart-defaults.js"
    if defaults_js.exists():
        script_tag = f"<script>{defaults_js.read_text(encoding='utf-8')}</script>"
        html_content = html_content.replace("</head>", f"{script_tag}\n</head>", 1)

    animations_js = js_dir / "chart-animations.js"
    if animations_js.exists():
        script_tag = f"<script>{animations_js.read_text(encoding='utf-8')}</script>"
        html_content = html_content.replace("</body>", f"{script_tag}\n</body>", 1)

    html_path.write_text(html_content, encoding="utf-8")


def _build_marp_command(
    marp_cmd: list,
    input_file: Path,
    output_file: Path,
    theme_dir: Path,
    fmt: str,
) -> List[str]:
    """Build the Marp CLI command for a given output format."""
    cmd = marp_cmd + [str(input_file), "--theme-set", str(theme_dir), "--html"]

    cmd.append("--allow-local-files")

    if fmt == "pdf":
        cmd.append("--pdf")
    elif fmt == "pptx":
        cmd.append("--pptx")

    cmd.extend(["-o", str(output_file)])
    return cmd


def _resolve_output_path(input_file: Path, output: Optional[Path], fmt: str) -> Path:
    """Determine the output file path for a given format."""
    ext = f".{fmt}"

    if output is None:
        return input_file.with_suffix(ext)

    if output.is_dir() or (not output.suffix and not output.exists()):
        output.mkdir(parents=True, exist_ok=True)
        return output / (input_file.stem + ext)

    if fmt != "html" and output.suffix == ".html":
        return output.with_suffix(ext)

    return output


def compile_presentation(
    input_file: Path,
    output_file: Optional[Path] = None,
    output_format: str = "both",
    max_lines: int = 30,
    max_table_rows: int = 10,
    no_split: bool = False,
    keep_temp: bool = False,
    theme_dir: Optional[Path] = None,
    skip_animations: bool = False,
) -> dict:
    """Compile a Markdown file into a CDL-themed Marp presentation.

    Args:
        input_file: Path to the input Markdown file.
        output_file: Output file or directory. Defaults to same dir as input.
        output_format: One of 'html', 'pdf', 'pptx', 'both' (html+pdf).
        max_lines: Max code lines per slide before splitting.
        max_table_rows: Max table rows per slide before splitting.
        no_split: Disable auto-splitting of code blocks and tables.
        keep_temp: Keep temporary processed files for debugging.
        theme_dir: Custom theme directory (overrides bundled CDL theme).

    Returns:
        Dict with 'files' (list of created files), 'warnings' (list), and
        'preprocessing' (stats from preprocessor).

    Raises:
        CompilationError: On any failure in the pipeline.
        FileNotFoundError: If input file doesn't exist.
    """
    input_file = Path(input_file).resolve()
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    if not input_file.is_file():
        raise CompilationError(f"Not a file: {input_file}")

    marp_resolved = resolve_marp_cli()
    if marp_resolved is None:
        raise CompilationError(get_marp_install_instructions())

    # resolve_marp_cli returns either a string (binary path) or list (npx command parts)
    marp_is_npx = isinstance(marp_resolved, list)
    marp_path = Path(marp_resolved[0]) if marp_is_npx else Path(marp_resolved)

    formats = _expand_formats(output_format)

    temp_theme_dir: Optional[Path] = None
    temp_md_fd: Optional[int] = None
    temp_md_path: Optional[Path] = None

    try:
        if theme_dir is not None:
            theme_dir = Path(theme_dir).resolve()
            if not theme_dir.is_dir():
                raise CompilationError(f"Theme directory not found: {theme_dir}")
        else:
            temp_theme_dir = prepare_theme_for_compilation(input_file.parent)
            theme_dir = temp_theme_dir

        temp_md_fd, temp_md_str = tempfile.mkstemp(
            suffix=".md",
            prefix=f".{input_file.stem}_processed_",
            dir=input_file.parent,
        )
        temp_md_path = Path(temp_md_str)

        from cdl_slides.preprocessor import process_markdown

        preprocess_stats = process_markdown(
            str(input_file),
            str(temp_md_path),
            max_lines=max_lines,
            max_table_rows=max_table_rows,
            no_split=no_split,
            skip_animations=skip_animations,
        )

        results: Dict[str, object] = {
            "files": [],
            "warnings": [],
            "preprocessing": preprocess_stats,
        }

        for fmt in formats:
            out_path = _resolve_output_path(input_file, output_file, fmt)
            marp_cmd = list(marp_resolved) if marp_is_npx else [str(marp_path)]
            cmd = _build_marp_command(marp_cmd, temp_md_path, out_path, theme_dir, fmt)

            proc = subprocess.run(cmd, capture_output=True, text=True)

            if proc.returncode != 0:
                stderr = proc.stderr.strip()
                raise CompilationError(f"Marp CLI failed for {fmt} output (exit {proc.returncode}):\n{stderr}")

            if proc.stderr:
                for line in proc.stderr.strip().splitlines():
                    if line.strip():
                        results["warnings"].append(line.strip())  # type: ignore[union-attr]

            if fmt == "html" and out_path.exists():
                _inject_js_into_html(out_path)
                copy_assets_alongside_output(out_path, source_dir=input_file.parent)

            if out_path.exists():
                results["files"].append(  # type: ignore[union-attr]
                    {
                        "path": out_path,
                        "format": fmt,
                        "size": out_path.stat().st_size,
                    }
                )

        return results

    finally:
        if temp_md_fd is not None:
            import os

            try:
                os.close(temp_md_fd)
            except OSError:
                pass

        if not keep_temp:
            if temp_md_path is not None and temp_md_path.exists():
                temp_md_path.unlink()
            if temp_theme_dir is not None and temp_theme_dir.exists():
                shutil.rmtree(temp_theme_dir, ignore_errors=True)
        else:
            if temp_md_path is not None:
                results["warnings"].append(  # type: ignore[union-attr]
                    f"Kept temp file: {temp_md_path}"
                )
            if temp_theme_dir is not None:
                results["warnings"].append(  # type: ignore[union-attr]
                    f"Kept temp theme dir: {temp_theme_dir}"
                )


def _expand_formats(output_format: str) -> List[str]:
    """Expand format string into list of individual formats."""
    output_format = output_format.lower().strip()
    valid = {"html", "pdf", "pptx", "both"}
    if output_format not in valid:
        raise CompilationError(f"Invalid output format '{output_format}'. Must be one of: {', '.join(sorted(valid))}")
    if output_format == "both":
        return ["html", "pdf"]
    return [output_format]
