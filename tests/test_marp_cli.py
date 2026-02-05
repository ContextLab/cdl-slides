"""Tests for cdl_slides.marp_cli."""

import platform

import click.testing

from cdl_slides.cli import main
from cdl_slides.marp_cli import (
    MARP_CLI_VERSION,
    _get_cache_dir,
    _get_platform_key,
    get_marp_version_info,
    resolve_marp_cli,
)


class TestGetCacheDir:
    def test_returns_path(self):
        cache_dir = _get_cache_dir()
        assert cache_dir.is_dir()

    def test_platform_appropriate_location(self):
        cache_dir = _get_cache_dir()
        system = platform.system()
        if system == "Darwin":
            assert "Caches" in str(cache_dir)
        elif system == "Windows":
            assert "AppData" in str(cache_dir)
        else:
            assert ".cache" in str(cache_dir)


class TestGetPlatformKey:
    def test_returns_valid_key(self):
        key = _get_platform_key()
        assert key is not None
        assert len(key) == 2


class TestResolveMarpCli:
    def test_resolves_something(self):
        result = resolve_marp_cli()
        assert result is not None

    def test_returns_str_or_list(self):
        result = resolve_marp_cli()
        assert isinstance(result, (str, list))


class TestGetMarpVersionInfo:
    def test_returns_dict(self):
        info = get_marp_version_info()
        assert isinstance(info, dict)
        assert "installed" in info
        assert "source" in info


class TestMarpCliVersion:
    def test_version_is_semver(self):
        assert MARP_CLI_VERSION.startswith("v")
        parts = MARP_CLI_VERSION[1:].split(".")
        assert len(parts) == 3


class TestResolveMarpCliIdempotency:
    """Test that resolve_marp_cli() is idempotent."""

    def test_resolve_marp_cli_returns_same_result_on_repeated_calls(self):
        """Verify resolve_marp_cli() returns identical results when called twice."""
        result1 = resolve_marp_cli()
        result2 = resolve_marp_cli()
        assert result1 == result2

    def test_resolve_marp_cli_returns_same_type_on_repeated_calls(self):
        """Verify resolve_marp_cli() returns the same type on repeated calls."""
        result1 = resolve_marp_cli()
        result2 = resolve_marp_cli()
        assert result1.__class__ is result2.__class__

    def test_cached_binary_persists_between_calls(self):
        """Verify that if a binary is found, it persists across calls."""
        result1 = resolve_marp_cli()
        result2 = resolve_marp_cli()
        # If result1 is a string (path to binary), it should be the same path
        if isinstance(result1, str):
            assert isinstance(result2, str)
            assert result1 == result2
        # If result1 is a list (npx command), it should be the same list
        elif isinstance(result1, list):
            assert isinstance(result2, list)
            assert result1 == result2


class TestGetMarpVersionInfoIdempotency:
    """Test that get_marp_version_info() is idempotent."""

    def test_get_marp_version_info_returns_consistent_data(self):
        """Verify get_marp_version_info() returns consistent data on repeated calls."""
        info1 = get_marp_version_info()
        info2 = get_marp_version_info()
        assert info1 == info2

    def test_get_marp_version_info_has_required_keys(self):
        """Verify get_marp_version_info() returns all required keys."""
        info = get_marp_version_info()
        required_keys = {"installed", "source", "path", "version"}
        assert required_keys.issubset(set(info.keys()))

    def test_get_marp_version_info_installed_is_bool(self):
        """Verify 'installed' key is a boolean."""
        info = get_marp_version_info()
        assert isinstance(info["installed"], bool)

    def test_get_marp_version_info_source_is_string(self):
        """Verify 'source' key is a string."""
        info = get_marp_version_info()
        assert isinstance(info["source"], str)


class TestCliSetupCommand:
    """Test the cdl-slides setup CLI command."""

    def test_setup_command_runs_successfully(self):
        """Verify the setup command runs without errors."""
        runner = click.testing.CliRunner()
        result = runner.invoke(main, ["setup"])
        # Command should exit with code 0 (success) or 1 (if Marp already installed)
        assert result.exit_code in (0, 1)

    def test_setup_command_produces_output(self):
        """Verify the setup command produces some output."""
        runner = click.testing.CliRunner()
        result = runner.invoke(main, ["setup"])
        assert len(result.output) > 0

    def test_setup_command_output_contains_marp_reference(self):
        """Verify the setup command output mentions Marp."""
        runner = click.testing.CliRunner()
        result = runner.invoke(main, ["setup"])
        output_lower = result.output.lower()
        assert "marp" in output_lower

    def test_setup_command_idempotent_on_repeated_calls(self):
        """Verify setup command can be called multiple times without error."""
        runner = click.testing.CliRunner()
        result1 = runner.invoke(main, ["setup"])
        result2 = runner.invoke(main, ["setup"])
        # Both calls should succeed (exit code 0 or 1)
        assert result1.exit_code in (0, 1)
        assert result2.exit_code in (0, 1)
