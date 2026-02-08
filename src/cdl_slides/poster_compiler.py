"""Poster compilation pipeline for CDL-themed academic posters."""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from cdl_slides.assets import copy_assets_alongside_output, prepare_theme_for_compilation
from cdl_slides.compiler import CompilationError
from cdl_slides.marp_cli import resolve_marp_cli
from cdl_slides.poster_preprocessor import process_poster_markdown


def _expand_poster_formats(format_spec: str) -> list[str]:
    """
    Expand format specification to list of formats.

    Only HTML and PDF are supported for posters (no PPTX).

    Args:
        format_spec: One of 'html', 'pdf', 'both'

    Returns:
        List of format strings

    Raises:
        CompilationError: If invalid format specified
    """
    format_spec = format_spec.lower()
    if format_spec == "both":
        return ["html", "pdf"]
    elif format_spec in ("html", "pdf"):
        return [format_spec]
    else:
        raise CompilationError(
            f"Invalid poster format '{format_spec}'. Posters only support: html, pdf, both (no pptx)"
        )


def _resolve_poster_output_path(
    input_file: Path,
    output: Path | None,
    format_ext: str,
) -> Path:
    """Resolve output path for poster, defaulting to PDF."""
    if output is None:
        return input_file.with_suffix(f".{format_ext}")

    if output.is_dir():
        return output / f"{input_file.stem}.{format_ext}"

    if output.suffix.lower() != f".{format_ext}":
        return output.with_suffix(f".{format_ext}")

    return output


_KATEX_FONT_FACE_RE = re.compile(
    r"@font-face\s*\{[^}]*font-family\s*:\s*[\"']?KaTeX_[^}]*\}",
    re.DOTALL,
)

_AVENIR_STACK = "'Avenir LT Std',Avenir,'Avenir Next',sans-serif"
_KATEX_FONT_FAMILY_RE = re.compile(r"font-family\s*:\s*[\"']?KaTeX_\w+[\"']?")
_KATEX_FONT_SHORTHAND_RE = re.compile(r"(font\s*:\s*[^;]*?)KaTeX_Main[^;]*?(;)")


def _postprocess_katex_fonts(html_path: Path) -> None:
    content = html_path.read_text(encoding="utf-8")
    content = _KATEX_FONT_FACE_RE.sub("", content)
    content = _KATEX_FONT_FAMILY_RE.sub(f"font-family:{_AVENIR_STACK}", content)
    content = _KATEX_FONT_SHORTHAND_RE.sub(rf"\g<1>{_AVENIR_STACK}\2", content)
    html_path.write_text(content, encoding="utf-8")


def _build_poster_marp_command(
    marp_cmd: list[str] | str,
    input_file: Path,
    theme_dir: Path,
    output_format: str,
) -> list[str]:
    """Build Marp CLI command for poster compilation."""
    if isinstance(marp_cmd, str):
        cmd = [marp_cmd]
    else:
        cmd = list(marp_cmd)

    cmd.extend(
        [
            str(input_file),
            "--theme-set",
            str(theme_dir),
            "--html",
            "--allow-local-files",
        ]
    )

    if output_format == "pdf":
        cmd.append("--pdf")

    return cmd


def compile_poster(
    input_file: Path,
    output_file: Path | None = None,
    output_format: str = "pdf",
    keep_temp: bool = False,
) -> dict[str, Any]:
    """
    Compile a poster markdown file to PDF or HTML.

    Args:
        input_file: Path to input .md file
        output_file: Optional output path (defaults to same dir as input)
        output_format: 'html', 'pdf', or 'both'
        keep_temp: Keep temporary files for debugging

    Returns:
        Dict with 'files' (list of output info), 'warnings', 'preprocessing' stats

    Raises:
        CompilationError: If compilation fails
        FileNotFoundError: If input file doesn't exist
    """
    input_file = Path(input_file).resolve()

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    marp_cmd = resolve_marp_cli()
    if marp_cmd is None:
        raise CompilationError("Marp CLI not found. Run 'cdl-slides setup' to install it.")

    formats = _expand_poster_formats(output_format)
    temp_dir = Path(tempfile.mkdtemp(prefix="cdl-poster-"))

    theme_dir = None
    try:
        theme_dir = prepare_theme_for_compilation(
            input_file.parent,
            theme_name="cdl-poster-theme",
        )

        temp_md = temp_dir / "processed_poster.md"
        preprocess_stats = process_poster_markdown(input_file, temp_md)

        output_files: list[dict[str, Any]] = []
        all_warnings = list(preprocess_stats.get("warnings", []))

        for fmt in formats:
            output_path = _resolve_poster_output_path(input_file, output_file, fmt)

            cmd = _build_poster_marp_command(marp_cmd, temp_md, theme_dir, fmt)
            cmd.extend(["-o", str(output_path)])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(input_file.parent),
            )

            if result.returncode != 0:
                raise CompilationError(f"Marp compilation failed:\n{result.stderr}\n{result.stdout}")

            if result.stderr:
                all_warnings.append(f"Marp warnings: {result.stderr}")

            if output_path.exists():
                if fmt == "html":
                    _postprocess_katex_fonts(output_path)
                    copy_assets_alongside_output(output_path)
                output_files.append(
                    {
                        "path": str(output_path),
                        "format": fmt,
                        "size": output_path.stat().st_size,
                    }
                )

        return {
            "files": output_files,
            "warnings": all_warnings,
            "preprocessing": preprocess_stats,
        }

    finally:
        if not keep_temp:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            if theme_dir and theme_dir.exists() and theme_dir.is_dir():
                shutil.rmtree(theme_dir)
