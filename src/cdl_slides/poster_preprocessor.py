"""Poster preprocessor for ASCII grid layouts and section-based content."""

from __future__ import annotations

import re
import warnings
from pathlib import Path
from typing import Any

import yaml

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


def extract_poster_sections(content: str) -> dict[str, dict[str, str]]:
    """
    Parse ## X: Section Title headers to extract section content.

    Args:
        content: Markdown content (after frontmatter)

    Returns:
        Dict mapping letter to {"title": str, "content": str}
    """
    pattern = r"^## ([A-Z]):\s*(.+?)$"
    matches = list(re.finditer(pattern, content, re.MULTILINE))
    sections: dict[str, dict[str, str]] = {}
    for i, match in enumerate(matches):
        letter = match.group(1)
        title = match.group(2).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        section_content = content[start:end].strip()
        sections[letter] = {"title": title, "content": section_content}
    return sections


def generate_poster_html(
    frontmatter: dict[str, Any],
    layout: dict[str, Any],
    sections: dict[str, dict[str, str]],
) -> str:
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
  gap: 1em;
  padding: 2em;
}}
</style>"""

    section_divs = []
    for label in layout["labels"]:
        if label not in sections:
            continue
        sec = sections[label]
        css_class = "poster-title" if label == "T" else "poster-section"
        heading = f"# {sec['title']}" if label == "T" else f"### {sec['title']}"
        div = f"""<div style="grid-area: {label};" class="{css_class}">

{heading}

{sec["content"]}

</div>"""
        section_divs.append(div)

    parts = fm_lines + [style, ""] + section_divs
    return "\n".join(parts) + "\n"


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

    html = generate_poster_html(frontmatter, layout, sections)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

    return {
        "sections": len(sections),
        "grid_size": f"{layout['rows']}x{layout['cols']}",
        "warnings": warn_list,
    }
