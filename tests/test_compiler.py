"""Tests for cdl_slides.compiler."""

from pathlib import Path
from unittest.mock import patch

import pytest

from cdl_slides.compiler import (
    CompilationError,
    _expand_formats,
    _inject_js_into_html,
    _resolve_output_path,
    compile_presentation,
)


class TestExpandFormatsBoth:
    def test_both_expands_to_html_and_pdf(self):
        assert _expand_formats("both") == ["html", "pdf"]

    def test_case_insensitive(self):
        assert _expand_formats("Both") == ["html", "pdf"]
        assert _expand_formats("BOTH") == ["html", "pdf"]


class TestExpandFormatsSingle:
    def test_html(self):
        assert _expand_formats("html") == ["html"]

    def test_pdf(self):
        assert _expand_formats("pdf") == ["pdf"]

    def test_pptx(self):
        assert _expand_formats("pptx") == ["pptx"]


class TestExpandFormatsInvalid:
    def test_invalid_raises_compilation_error(self):
        with pytest.raises(CompilationError, match="Invalid output format"):
            _expand_formats("docx")

    def test_empty_raises_compilation_error(self):
        with pytest.raises(CompilationError):
            _expand_formats("invalid")


class TestCompileNonexistentFile:
    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            compile_presentation(Path("/tmp/nonexistent_file_xyz_98765.md"))


class TestCompileNoMarpCli:
    def test_raises_when_marp_not_found(self, tmp_path):
        md_file = tmp_path / "test.md"
        md_file.write_text("---\nmarp: true\ntheme: cdl-theme\n---\n\n# Slide\n")
        with patch("cdl_slides.compiler.detect_marp_cli", return_value=None):
            with pytest.raises(CompilationError, match="Marp CLI"):
                compile_presentation(md_file)


class TestResolveOutputPathDefault:
    def test_default_output_alongside_input(self, tmp_path):
        input_file = tmp_path / "slides.md"
        input_file.touch()
        result = _resolve_output_path(input_file, None, "html")
        assert result == tmp_path / "slides.html"

    def test_default_pdf(self, tmp_path):
        input_file = tmp_path / "slides.md"
        input_file.touch()
        result = _resolve_output_path(input_file, None, "pdf")
        assert result == tmp_path / "slides.pdf"


class TestResolveOutputPathDirectory:
    def test_output_to_directory(self, tmp_path):
        input_file = tmp_path / "slides.md"
        input_file.touch()
        out_dir = tmp_path / "build"
        out_dir.mkdir()
        result = _resolve_output_path(input_file, out_dir, "html")
        assert result == out_dir / "slides.html"

    def test_output_to_nonexistent_directory(self, tmp_path):
        input_file = tmp_path / "slides.md"
        input_file.touch()
        out_dir = tmp_path / "new_build"
        result = _resolve_output_path(input_file, out_dir, "pdf")
        assert result == out_dir / "slides.pdf"
        assert out_dir.is_dir()


class TestInjectJsIntoHtml:
    def test_js_injected_into_head_and_body(self, tmp_path):
        html_file = tmp_path / "test.html"
        html_file.write_text(
            "<html><head><title>Test</title></head><body><p>Hello</p></body></html>",
            encoding="utf-8",
        )
        _inject_js_into_html(html_file)
        content = html_file.read_text(encoding="utf-8")
        assert "<script>" in content
        assert "</head>" in content
        assert "</body>" in content
