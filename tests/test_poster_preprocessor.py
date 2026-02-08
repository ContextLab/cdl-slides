"""Tests for poster preprocessor module."""

from __future__ import annotations

import pytest

from cdl_slides.poster_preprocessor import (
    extract_poster_sections,
    generate_poster_html,
    parse_ascii_layout,
    parse_poster_frontmatter,
    process_poster_markdown,
)


class TestParseAsciiLayout:
    """Tests for ASCII grid layout parsing."""

    def test_simple_2x2_grid(self):
        """Parse a simple 2x2 grid."""
        layout = parse_ascii_layout("AABB\nAABB")
        assert layout["rows"] == 2
        assert layout["cols"] == 4
        assert set(layout["labels"]) == {"A", "B"}
        assert layout["areas"]["A"]["row_start"] == 0
        assert layout["areas"]["A"]["row_end"] == 1

    def test_single_cell(self):
        """Parse a single-cell grid."""
        layout = parse_ascii_layout("A")
        assert layout["rows"] == 1
        assert layout["cols"] == 1
        assert layout["labels"] == ["A"]

    def test_with_empty_cells(self):
        """Parse grid with dot placeholders."""
        layout = parse_ascii_layout("A.B\nA.B")
        assert "." not in layout["labels"]
        assert set(layout["labels"]) == {"A", "B"}

    def test_full_poster_grid(self):
        """Parse a realistic poster grid."""
        grid = "TTTT\nIIMM\nIIMM\nCCDD"
        layout = parse_ascii_layout(grid)
        assert layout["rows"] == 4
        assert layout["cols"] == 4
        assert set(layout["labels"]) == {"T", "I", "M", "C", "D"}

    def test_ragged_rows_raises(self):
        """Reject grids with different row lengths."""
        with pytest.raises(ValueError) as exc_info:
            parse_ascii_layout("AAB\nAABB")
        assert "length" in str(exc_info.value).lower() or "ragged" in str(exc_info.value).lower()

    def test_non_rectangular_region_raises(self):
        """Reject non-rectangular regions (L-shapes)."""
        with pytest.raises(ValueError) as exc_info:
            parse_ascii_layout("AB\nBA")
        assert "rectangular" in str(exc_info.value).lower()

    def test_empty_grid_raises(self):
        """Reject empty grid input."""
        with pytest.raises(ValueError):
            parse_ascii_layout("")

    def test_whitespace_only_raises(self):
        """Reject whitespace-only input."""
        with pytest.raises(ValueError):
            parse_ascii_layout("   \n   ")


class TestExtractPosterSections:
    """Tests for section extraction from markdown."""

    def test_extracts_lettered_sections(self):
        """Extract sections with letter prefixes."""
        md = "## A: Introduction\nHello\n\n## B: Methods\nWorld"
        sections = extract_poster_sections(md)
        assert "A" in sections
        assert "B" in sections
        assert sections["A"]["title"] == "Introduction"
        assert sections["B"]["title"] == "Methods"

    def test_section_content_includes_markdown(self):
        """Section content preserves markdown formatting."""
        md = "## A: Test\n**bold** and *italic*\n\n- list item"
        sections = extract_poster_sections(md)
        content = sections["A"]["content"]
        assert content is not None
        assert "**bold**" in content
        assert "- list item" in content

    def test_handles_single_section(self):
        """Handle file with only one section."""
        md = "## T: Title\nContent here"
        sections = extract_poster_sections(md)
        assert len(sections) == 1
        assert "T" in sections

    def test_empty_content_allowed(self):
        """Allow sections with minimal content."""
        md = "## A: Empty\n\n## B: Also Empty"
        sections = extract_poster_sections(md)
        assert "A" in sections
        assert "B" in sections

    def test_color_tag_extracted(self):
        """Extract [color] suffix from section header."""
        md = "## A: Introduction [blue]\nContent here"
        sections = extract_poster_sections(md)
        assert sections["A"]["title"] == "Introduction"
        assert sections["A"]["color"] == "blue"

    def test_color_stripped_from_title(self):
        """Color tag is removed from the section title text."""
        md = "## M: Methods [violet]\nSome methods"
        sections = extract_poster_sections(md)
        title = sections["M"]["title"]
        assert title is not None
        assert "[violet]" not in title
        assert title == "Methods"

    def test_all_valid_colors(self):
        """All valid color names are parsed correctly."""
        valid = ["blue", "green", "violet", "purple", "orange", "red", "teal", "spring"]
        for color in valid:
            md = f"## A: Title [{color}]\nContent"
            sections = extract_poster_sections(md)
            assert sections["A"]["color"] == color, f"Failed for color: {color}"
            assert sections["A"]["title"] == "Title"

    def test_invalid_color_ignored(self):
        """Unrecognised color names are left in the title, color is None."""
        md = "## A: Introduction [magenta]\nContent"
        sections = extract_poster_sections(md)
        assert sections["A"]["color"] is None
        title = sections["A"]["title"]
        assert title is not None
        assert "magenta" in title

    def test_no_color_tag_returns_none(self):
        """Sections without [color] have color=None."""
        md = "## A: Introduction\nContent"
        sections = extract_poster_sections(md)
        assert sections["A"]["color"] is None
        assert sections["A"]["title"] == "Introduction"

    def test_multiple_sections_with_colors(self):
        """Multiple sections can each have their own color."""
        md = (
            "## I: Intro [blue]\nIntro text\n\n"
            "## M: Methods [violet]\nMethods text\n\n"
            "## R: Results [green]\nResults text"
        )
        sections = extract_poster_sections(md)
        assert sections["I"]["color"] == "blue"
        assert sections["M"]["color"] == "violet"
        assert sections["R"]["color"] == "green"

    def test_color_case_insensitive(self):
        """Color tags are matched case-insensitively."""
        md = "## A: Title [Blue]\nContent"
        sections = extract_poster_sections(md)
        assert sections["A"]["color"] == "blue"
        assert sections["A"]["title"] == "Title"


class TestParsePosterFrontmatter:
    """Tests for frontmatter parsing."""

    def test_valid_frontmatter(self):
        """Parse valid poster frontmatter."""
        content = "---\nmarp: true\ntheme: cdl-poster\nsize: A0\n---\n\nContent"
        fm = parse_poster_frontmatter(content)
        assert fm["marp"] is True
        assert fm["theme"] == "cdl-poster"
        assert fm["size"] == "A0"

    def test_missing_marp_raises(self):
        """Reject frontmatter without marp: true."""
        content = "---\ntheme: cdl-poster\nsize: A0\n---\n"
        with pytest.raises(ValueError):
            parse_poster_frontmatter(content)

    def test_accepts_valid_sizes(self):
        """Accept all valid size presets."""
        for size in ["A0", "A0-landscape", "A1", "36x48", "48x36"]:
            content = f"---\nmarp: true\ntheme: cdl-poster\nsize: {size}\n---\n"
            fm = parse_poster_frontmatter(content)
            assert fm["size"] == size


class TestGeneratePosterHtml:
    """Tests for HTML generation."""

    def test_output_contains_grid_template_areas(self):
        """Generated HTML includes CSS Grid template."""
        layout = parse_ascii_layout("AB\nAB")
        sections: dict[str, dict[str, str | None]] = {
            "A": {"title": "Intro", "content": "Hello", "color": None},
            "B": {"title": "Methods", "content": "World", "color": None},
        }
        fm = {"marp": True, "theme": "cdl-poster", "size": "A0"}
        html = generate_poster_html(fm, layout, sections)
        assert "grid-template-areas" in html

    def test_output_has_section_divs(self):
        """Generated HTML includes section divs."""
        layout = parse_ascii_layout("AB\nAB")
        sections: dict[str, dict[str, str | None]] = {
            "A": {"title": "Intro", "content": "Hello", "color": None},
            "B": {"title": "Methods", "content": "World", "color": None},
        }
        fm = {"marp": True, "theme": "cdl-poster", "size": "A0"}
        html = generate_poster_html(fm, layout, sections)
        assert "grid-area: A" in html or "grid-area:A" in html
        assert "grid-area: B" in html or "grid-area:B" in html

    def test_color_class_in_generated_html(self):
        """Color class is included in generated section div."""
        layout = parse_ascii_layout("AB\nAB")
        sections: dict[str, dict[str, str | None]] = {
            "A": {"title": "Intro", "content": "Hello", "color": "blue"},
            "B": {"title": "Methods", "content": "World", "color": "violet"},
        }
        fm = {"marp": True, "theme": "cdl-poster", "size": "A0"}
        html = generate_poster_html(fm, layout, sections)
        assert "poster-color-blue" in html
        assert "poster-color-violet" in html

    def test_no_color_class_when_none(self):
        """No poster-color-* class when color is None."""
        layout = parse_ascii_layout("A\nA")
        sections: dict[str, dict[str, str | None]] = {
            "A": {"title": "Intro", "content": "Hello", "color": None},
        }
        fm = {"marp": True, "theme": "cdl-poster", "size": "A0"}
        html = generate_poster_html(fm, layout, sections)
        assert "poster-color-" not in html


class TestProcessPosterMarkdown:
    """Tests for full pipeline processing."""

    def test_full_pipeline_with_minimal_fixture(self, poster_minimal_md, tmp_path):
        """Process minimal poster fixture."""
        output = tmp_path / "output.md"
        stats = process_poster_markdown(poster_minimal_md, output)
        assert output.exists()
        content = output.read_text()
        assert "grid-template-areas" in content
        assert stats["sections"] >= 2

    def test_full_pipeline_with_full_fixture(self, poster_full_md, tmp_path):
        """Process full poster fixture."""
        output = tmp_path / "output.md"
        stats = process_poster_markdown(poster_full_md, output)
        assert output.exists()
        assert stats["sections"] >= 5

    def test_warns_on_missing_section(self, poster_missing_section_md, tmp_path):
        """Warn when grid letter has no matching section."""
        output = tmp_path / "output.md"
        stats = process_poster_markdown(poster_missing_section_md, output)
        # Should have warnings about missing section
        assert len(stats.get("warnings", [])) > 0

    def test_invalid_grid_raises(self, poster_invalid_grid_md, tmp_path):
        """Reject invalid grid layouts."""
        output = tmp_path / "output.md"
        with pytest.raises(ValueError):
            process_poster_markdown(poster_invalid_grid_md, output)
