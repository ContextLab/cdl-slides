"""Tests for poster compiler module."""

import pytest

from cdl_slides.compiler import CompilationError
from cdl_slides.poster_compiler import (
    _expand_poster_formats,
    _resolve_poster_output_path,
    compile_poster,
)


class TestExpandPosterFormats:
    """Tests for format expansion."""

    def test_html(self):
        assert _expand_poster_formats("html") == ["html"]

    def test_pdf(self):
        assert _expand_poster_formats("pdf") == ["pdf"]

    def test_both(self):
        assert _expand_poster_formats("both") == ["html", "pdf"]

    def test_case_insensitive(self):
        assert _expand_poster_formats("HTML") == ["html"]
        assert _expand_poster_formats("PDF") == ["pdf"]

    def test_pptx_raises(self):
        """PPTX is not supported for posters."""
        with pytest.raises(CompilationError) as exc_info:
            _expand_poster_formats("pptx")
        assert "pptx" in str(exc_info.value).lower()

    def test_invalid_format_raises(self):
        with pytest.raises(CompilationError):
            _expand_poster_formats("docx")


class TestResolvePosterOutputPath:
    """Tests for output path resolution."""

    def test_default_output_uses_input_dir(self, tmp_path):
        input_file = tmp_path / "poster.md"
        input_file.touch()
        result = _resolve_poster_output_path(input_file, None, "pdf")
        assert result == tmp_path / "poster.pdf"

    def test_output_dir_uses_input_stem(self, tmp_path):
        input_file = tmp_path / "poster.md"
        input_file.touch()
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        result = _resolve_poster_output_path(input_file, output_dir, "html")
        assert result == output_dir / "poster.html"


class TestCompilePosterMissingFile:
    """Tests for error handling."""

    def test_missing_file_raises(self, tmp_path):
        missing = tmp_path / "does_not_exist.md"
        with pytest.raises(FileNotFoundError):
            compile_poster(missing)


class TestCompilePosterHtml:
    """Integration tests for HTML compilation (requires Marp CLI)."""

    @pytest.fixture(autouse=True)
    def cleanup_outputs(self, poster_minimal_md):
        """Clean up generated files after test."""
        yield
        for ext in [".html", ".pdf"]:
            output = poster_minimal_md.with_suffix(ext)
            if output.exists():
                output.unlink()

    def test_produces_html_output(self, poster_minimal_md):
        """Compile poster to HTML."""
        result = compile_poster(poster_minimal_md, output_format="html")
        assert "files" in result
        assert len(result["files"]) == 1
        assert result["files"][0]["format"] == "html"
        assert result["files"][0]["size"] > 0

    def test_html_contains_grid(self, poster_minimal_md):
        """Verify HTML output contains grid layout."""
        from pathlib import Path

        result = compile_poster(poster_minimal_md, output_format="html")
        html_path = Path(result["files"][0]["path"])
        content = html_path.read_text()
        assert "grid" in content.lower()
