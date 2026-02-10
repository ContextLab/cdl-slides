"""Poster preprocessor for ASCII grid layouts and section-based content."""

from __future__ import annotations

import re
import warnings
from pathlib import Path
from typing import Any

import yaml

try:
    from cdl_slides.chart_renderer import process_poster_chart_blocks
except ImportError:

    def process_poster_chart_blocks(content: str) -> tuple:
        return content, 0


_VALID_SIZES = {"A0", "A0-landscape", "A1", "36x48", "48x36"}
_SIZE_PATTERN = re.compile(r"^\d+x\d+$")


def parse_poster_frontmatter(content: str) -> dict[str, Any]:
    """
    Extract and validate YAML frontmatter from poster markdown.

    Args:
        content: Full markdown file content

    Returns:
        Dict with marp, theme, size, title, authors keys

    Raises:
        ValueError: If frontmatter is missing or invalid
    """
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        raise ValueError("Missing or malformed YAML frontmatter (expected --- delimiters)")

    raw = match.group(1)
    try:
        fm = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in frontmatter: {exc}") from exc

    if not isinstance(fm, dict):
        raise ValueError("Frontmatter must be a YAML mapping")

    if not fm.get("marp"):
        raise ValueError("Frontmatter must contain 'marp: true'")

    theme = fm.get("theme", "")
    if "poster" not in str(theme):
        raise ValueError(f"Theme must contain 'poster', got '{theme}'")

    size = fm.get("size", "A0")
    size_str = str(size)
    if size_str not in _VALID_SIZES and not _SIZE_PATTERN.match(size_str):
        raise ValueError(
            f"Invalid size '{size_str}'. Must be one of {sorted(_VALID_SIZES)} or WxH pattern (e.g. '36x48')"
        )

    return {
        "marp": True,
        "theme": theme,
        "size": size_str,
        "math": fm.get("math", "katex"),
        "title": fm.get("title", ""),
        "authors": fm.get("authors", []),
    }


def parse_ascii_layout(layout_text: str) -> dict[str, Any]:
    """
    Parse ASCII grid layout into structured data.

    Args:
        layout_text: Multi-line ASCII string like "AABB\\nAABB\\nCCDD"

    Returns:
        Dict with:
        - grid: 2D list of characters
        - labels: List of unique letters in sorted order
        - areas: Dict mapping letter to {row_start, row_end, col_start, col_end}
        - rows: Number of rows
        - cols: Number of columns

    Raises:
        ValueError: If rows have different lengths or regions are non-rectangular
    """
    lines = layout_text.strip().split("\n")
    lines = [line.strip() for line in lines if line.strip()]

    if not lines:
        raise ValueError("Empty layout")

    row_lengths = [len(line) for line in lines]
    if len(set(row_lengths)) > 1:
        raise ValueError(f"Ragged rows: row lengths are {row_lengths}")

    grid = [list(line) for line in lines]
    coords: dict[str, list[tuple[int, int]]] = {}
    for r, row in enumerate(grid):
        for c, char in enumerate(row):
            if char != ".":
                coords.setdefault(char, []).append((r, c))

    labels: list[str] = []
    areas: dict[str, dict[str, int]] = {}
    for char in sorted(coords.keys()):
        points = coords[char]
        rows_set = [p[0] for p in points]
        cols_set = [p[1] for p in points]
        min_r, max_r = min(rows_set), max(rows_set)
        min_c, max_c = min(cols_set), max(cols_set)
        expected_area = (max_r - min_r + 1) * (max_c - min_c + 1)
        if len(points) != expected_area:
            raise ValueError(f"Region '{char}' is not rectangular")
        labels.append(char)
        areas[char] = {
            "row_start": min_r,
            "row_end": max_r,
            "col_start": min_c,
            "col_end": max_c,
        }

    return {
        "grid": grid,
        "labels": labels,
        "areas": areas,
        "rows": len(grid),
        "cols": len(grid[0]),
    }


_VALID_COLORS = {"blue", "green", "violet", "purple", "orange", "red", "teal", "spring"}


def extract_poster_sections(content: str) -> dict[str, dict[str, str | None]]:
    """
    Parse ## X: Section Title [color] headers to extract section content.

    The optional [color] suffix sets the default callout-box color for
    that section.  Valid colors: blue, green, violet, purple, orange,
    red, teal, spring.  Individual boxes can override with
    data-color="…" on the div.

    Args:
        content: Markdown content (after frontmatter)

    Returns:
        Dict mapping letter to {"title": str, "content": str, "color": str | None}
    """
    pattern = r"^## ([A-Z]):\s*(.+?)$"
    matches = list(re.finditer(pattern, content, re.MULTILINE))
    sections: dict[str, dict[str, str | None]] = {}
    for i, match in enumerate(matches):
        letter = match.group(1)
        raw_title = match.group(2).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        section_content = content[start:end].strip()

        color_match = re.search(r"\s*\[(\w+)\]\s*$", raw_title)
        color = None
        if color_match:
            candidate = color_match.group(1).lower()
            if candidate in _VALID_COLORS:
                color = candidate
                raw_title = raw_title[: color_match.start()].strip()

        sections[letter] = {"title": raw_title, "content": section_content, "color": color}
    return sections


def _reading_order_labels(layout: dict[str, Any]) -> list[str]:
    """Return section labels sorted in column-major reading order.

    Sorts by (col_start, row_start) so sections are ordered left-to-right
    across columns and top-to-bottom within each column — matching the
    natural reading order of a multi-column academic poster.
    """
    areas = layout["areas"]
    return sorted(
        layout["labels"],
        key=lambda lbl: (areas[lbl]["col_start"], areas[lbl]["row_start"]),
    )


def _auto_number_captions(content: str, fig_count: int, tbl_count: int) -> tuple[str, int, int]:
    """Prepend bold 'Figure X.' / 'Table X.' to caption divs in *content*.

    Only captions with text are numbered; empty caption divs are skipped.
    Returns (updated_content, new_fig_count, new_tbl_count).
    """

    def _replace_fig(m: re.Match) -> str:
        nonlocal fig_count
        tag = m.group(1)
        caption_text = m.group(2).strip()
        if not caption_text:
            return m.group(0)
        fig_count += 1
        return f'<{tag} class="figure-caption"><strong>Figure&nbsp;{fig_count}.</strong>&nbsp;{caption_text}</{tag}>'

    def _replace_tbl(m: re.Match) -> str:
        nonlocal tbl_count
        tag = m.group(1)
        caption_text = m.group(2).strip()
        if not caption_text:
            return m.group(0)
        tbl_count += 1
        return f'<{tag} class="table-caption"><strong>Table&nbsp;{tbl_count}.</strong>&nbsp;{caption_text}</{tag}>'

    content = re.sub(r'<(div|p) class="figure-caption">(.*?)</(?:div|p)>', _replace_fig, content)
    content = re.sub(r'<(div|p) class="table-caption">(.*?)</(?:div|p)>', _replace_tbl, content)
    return content, fig_count, tbl_count


def generate_poster_html(
    frontmatter: dict[str, Any],
    layout: dict[str, Any],
    sections: dict[str, dict[str, str | None]],
) -> tuple[str, int]:
    """
    Generate Marp-compatible markdown with CSS Grid layout.

    Args:
        frontmatter: Parsed frontmatter dict
        layout: Parsed layout from parse_ascii_layout
        sections: Parsed sections from extract_poster_sections

    Returns:
        Complete Marp markdown string with embedded HTML/CSS
    """
    fm_lines = [
        "---",
        "marp: true",
        f"theme: {frontmatter['theme']}",
        f"size: {frontmatter['size']}",
        f"math: {frontmatter.get('math', 'katex')}",
        "---",
        "",
    ]

    area_rows = []
    for row in layout["grid"]:
        area_rows.append('"' + " ".join(row) + '"')
    grid_template = "\n    ".join(area_rows)

    style = f"""<style scoped>
section {{
  display: grid;
  grid-template-areas:
    {grid_template};
  grid-template-rows: repeat({layout["rows"]}, 1fr);
  grid-template-columns: repeat({layout["cols"]}, 1fr);
  gap: 6mm;
  padding: 12mm;
}}
</style>"""

    ordered_labels = _reading_order_labels(layout)
    section_divs = []
    charts_total = 0
    fig_count = 0
    tbl_count = 0
    for label in ordered_labels:
        if label not in sections:
            continue
        sec = sections[label]
        css_class = "poster-title" if label == "T" else "poster-section"
        if sec.get("color"):
            css_class += f" poster-color-{sec['color']}"
        heading = f"# {sec['title']}" if label == "T" else f"### {sec['title']}"
        section_content = sec["content"] or ""
        section_content, chart_count = process_poster_chart_blocks(section_content)
        charts_total += chart_count
        section_content, fig_count, tbl_count = _auto_number_captions(section_content, fig_count, tbl_count)
        div = f"""<div style="grid-area: {label};" class="{css_class}">

{heading}

{section_content}

</div>"""
        section_divs.append(div)

    parts = fm_lines + [style, ""] + section_divs
    result = "\n".join(parts) + "\n"
    return result, charts_total


def process_poster_markdown(input_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    """
    Main entry point: process poster markdown file.

    Args:
        input_path: Path to input .md file
        output_path: Path to write processed output

    Returns:
        Stats dict with sections, grid_size, warnings
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    warn_list: list[str] = []

    content = input_path.read_text(encoding="utf-8")
    frontmatter = parse_poster_frontmatter(content)

    layout_match = re.search(r"```poster-layout\s*\n(.*?)```", content, re.DOTALL)
    if not layout_match:
        raise ValueError("Missing ```poster-layout``` block in poster markdown")
    layout_text = layout_match.group(1)
    layout = parse_ascii_layout(layout_text)

    fm_end_match = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
    body = content[fm_end_match.end() :] if fm_end_match else content
    sections = extract_poster_sections(body)

    grid_labels = set(layout["labels"])
    section_labels = set(sections.keys())

    for label in sorted(grid_labels - section_labels):
        msg = f"Grid label '{label}' has no matching ## {label}: section"
        warnings.warn(msg, stacklevel=2)
        warn_list.append(msg)

    for label in sorted(section_labels - grid_labels):
        msg = f"Section '{label}' not found in grid layout"
        warnings.warn(msg, stacklevel=2)
        warn_list.append(msg)

    html, charts_total = generate_poster_html(frontmatter, layout, sections)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

    return {
        "sections": len(sections),
        "grid_size": f"{layout['rows']}x{layout['cols']}",
        "warnings": warn_list,
        "charts_processed": charts_total,
    }
