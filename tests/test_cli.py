"""Tests for cdl_slides.cli."""

from pathlib import Path

from click.testing import CliRunner

from cdl_slides.cli import main


class TestVersionCommand:
    def test_shows_version_string(self):
        runner = CliRunner()
        result = runner.invoke(main, ["version"])
        assert result.exit_code == 0
        assert "cdl-slides" in result.output


class TestCompileMissingFile:
    def test_nonexistent_input_errors(self):
        runner = CliRunner()
        result = runner.invoke(main, ["compile", "/tmp/nonexistent_xyz_98765.md"])
        assert result.exit_code != 0


class TestCompileInvalidFormat:
    def test_invalid_format_errors(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("test.md").write_text("---\nmarp: true\n---\n# Hi\n")
            result = runner.invoke(main, ["compile", "test.md", "--format", "docx"])
            assert result.exit_code != 0


class TestInitCreatesTemplate:
    def test_creates_slides_md(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init", "."])
            assert result.exit_code == 0
            target = Path("slides.md")
            assert target.exists()
            content = target.read_text(encoding="utf-8")
            assert "marp: true" in content
            assert "cdl-theme" in content


class TestInitExistingFileNoOverwrite:
    def test_prompts_before_overwrite(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("slides.md").write_text("existing content")
            result = runner.invoke(main, ["init", "."], input="n\n")
            assert result.exit_code == 0
            assert "Overwrite?" in result.output or "already exists" in result.output
            content = Path("slides.md").read_text()
            assert content == "existing content"

    def test_overwrite_when_confirmed(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("slides.md").write_text("old content")
            result = runner.invoke(main, ["init", "."], input="y\n")
            assert result.exit_code == 0
            content = Path("slides.md").read_text()
            assert "marp: true" in content


class TestCompileHelp:
    def test_help_shows_usage(self):
        runner = CliRunner()
        result = runner.invoke(main, ["compile", "--help"])
        assert result.exit_code == 0
        assert "INPUT_FILE" in result.output
        assert "--format" in result.output
        assert "--output" in result.output


class TestMainGroupHelp:
    def test_top_level_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "compile" in result.output
        assert "init" in result.output
        assert "version" in result.output

    def test_version_option(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "cdl-slides" in result.output
