"""Tests for poster CLI commands."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from cdl_slides.cli import main


@pytest.fixture
def runner():
    return CliRunner()


class TestPosterGroup:
    """Tests for poster command group."""

    def test_poster_in_help(self, runner):
        """Poster group appears in main help."""
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "poster" in result.output

    def test_poster_subcommands(self, runner):
        """Poster group has compile and init subcommands."""
        result = runner.invoke(main, ["poster", "--help"])
        assert result.exit_code == 0
        assert "compile" in result.output
        assert "init" in result.output


class TestPosterCompileCommand:
    """Tests for poster compile command."""

    def test_compile_help_shows_options(self, runner):
        """Compile help shows expected options."""
        result = runner.invoke(main, ["poster", "compile", "--help"])
        assert result.exit_code == 0
        assert "INPUT_FILE" in result.output
        assert "--format" in result.output
        assert "--output" in result.output

    def test_compile_no_pptx_option(self, runner):
        """PPTX is not an option for poster compile."""
        result = runner.invoke(main, ["poster", "compile", "--help"])
        assert "html" in result.output
        assert "pdf" in result.output
        assert "both" in result.output

    def test_compile_missing_file(self, runner):
        """Error when input file doesn't exist."""
        result = runner.invoke(main, ["poster", "compile", "nonexistent.md"])
        assert result.exit_code != 0

    def test_compile_minimal_poster(self, runner, poster_minimal_md):
        """Compile minimal poster fixture."""
        result = runner.invoke(main, ["poster", "compile", str(poster_minimal_md), "--format", "html"])
        output = poster_minimal_md.with_suffix(".html")
        if output.exists():
            output.unlink()
        assert result.exit_code == 0
        assert "successfully" in result.output.lower() or "\u2713" in result.output


class TestPosterInitCommand:
    """Tests for poster init command."""

    def test_init_creates_template(self, runner):
        """Init creates poster.md template."""
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["poster", "init", "."])
            assert result.exit_code == 0
            poster = Path("poster.md")
            assert poster.exists()
            content = poster.read_text()
            assert "theme: cdl-poster" in content
            assert "poster-layout" in content

    def test_init_refuses_overwrite(self, runner):
        """Init won't overwrite existing file."""
        with runner.isolated_filesystem():
            Path("poster.md").write_text("existing")
            result = runner.invoke(main, ["poster", "init", "."])
            assert result.exit_code != 0
            assert "exists" in result.output.lower()

    def test_init_creates_directory(self, runner):
        """Init creates directory if needed."""
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["poster", "init", "new_dir"])
            assert result.exit_code == 0
            assert Path("new_dir/poster.md").exists()
