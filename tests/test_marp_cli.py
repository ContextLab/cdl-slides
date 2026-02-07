"""Tests for cdl_slides.marp_cli."""

import platform
import stat
import subprocess
import urllib.request
from urllib.request import urlopen

import click.testing

from cdl_slides.cli import main
from cdl_slides.marp_cli import (
    _PLATFORM_MAP,
    _RELEASE_BASE,
    MARP_CLI_VERSION,
    _get_cache_dir,
    _get_cached_marp_path,
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


class TestInstallerDownloadUrl:
    """Test the download URL construction for Marp CLI installer."""

    def test_release_base_url_format(self):
        """Verify the release base URL is correctly formatted."""
        assert _RELEASE_BASE.startswith("https://github.com/marp-team/marp-cli/releases/download/")
        assert MARP_CLI_VERSION in _RELEASE_BASE

    def test_download_url_is_accessible(self):
        """Verify the download URL for current platform is accessible (HEAD request)."""
        platform_key = _get_platform_key()
        assert platform_key is not None, "Platform should be supported"

        os_name, archive_ext = _PLATFORM_MAP[platform_key]
        filename = f"marp-cli-{MARP_CLI_VERSION}-{os_name}.{archive_ext}"
        url = f"{_RELEASE_BASE}/{filename}"

        # Use HEAD request to verify URL exists without downloading

        req = urllib.request.Request(url, method="HEAD")
        try:
            response = urlopen(req, timeout=30)
            assert response.status == 200, f"Expected 200, got {response.status}"
        except Exception as e:
            # If HEAD fails, try GET with small range
            req = urllib.request.Request(url)
            req.add_header("Range", "bytes=0-0")
            response = urlopen(req, timeout=30)
            assert response.status in (200, 206), f"URL not accessible: {e}"


class TestInstallerPlatformMapping:
    """Test platform detection and mapping for the installer."""

    def test_all_platform_keys_have_valid_structure(self):
        """Verify all platform map entries have correct structure."""
        for key, value in _PLATFORM_MAP.items():
            assert len(key) == 2, f"Key {key} should be (system, machine) tuple"
            assert len(value) == 2, f"Value {value} should be (os_name, archive_ext) tuple"
            os_name, archive_ext = value
            assert os_name in ("mac", "linux", "win"), f"Unknown OS: {os_name}"
            assert archive_ext in ("tar.gz", "zip"), f"Unknown archive: {archive_ext}"

    def test_current_platform_is_supported(self):
        """Verify the current platform is in the supported list."""
        key = _get_platform_key()
        assert key is not None, "Current platform should be supported"
        assert key in _PLATFORM_MAP or key[0] in [k[0] for k in _PLATFORM_MAP]

    def test_windows_uses_zip(self):
        """Verify Windows platforms use zip archives."""
        for key, value in _PLATFORM_MAP.items():
            if key[0] == "Windows":
                assert value[1] == "zip", "Windows should use zip archives"

    def test_unix_uses_tar_gz(self):
        """Verify Unix platforms use tar.gz archives."""
        for key, value in _PLATFORM_MAP.items():
            if key[0] in ("Darwin", "Linux"):
                assert value[1] == "tar.gz", "Unix should use tar.gz archives"


class TestInstallerCachedBinary:
    """Test the cached binary detection and execution."""

    def test_cached_path_in_version_directory(self):
        """Verify cached binary path includes version directory."""
        cached = _get_cached_marp_path()
        if cached is not None:
            assert MARP_CLI_VERSION in str(cached), "Cached path should include version"

    def test_cached_binary_is_executable(self):
        """Verify the cached binary has executable permissions."""
        cached = _get_cached_marp_path()
        if cached is not None:
            assert cached.exists(), "Cached binary should exist"
            mode = cached.stat().st_mode
            assert mode & stat.S_IXUSR, "Binary should be user-executable"


class TestInstallerBinaryExecution:
    """Test that the resolved Marp CLI binary actually works."""

    def test_resolved_binary_executes_version_command(self):
        """Verify the resolved binary can execute --version."""
        result = resolve_marp_cli()
        assert result is not None, "Should resolve to something"

        if isinstance(result, str):
            # Direct binary path
            proc = subprocess.run([result, "--version"], capture_output=True, text=True, timeout=30)
        else:
            # npx command list
            proc = subprocess.run(result + ["--version"], capture_output=True, text=True, timeout=60)

        assert proc.returncode == 0, f"--version failed: {proc.stderr}"
        assert "marp" in proc.stdout.lower() or len(proc.stdout) > 0, "Should output version info"

    def test_resolved_binary_help_command(self):
        """Verify the resolved binary can execute --help."""
        result = resolve_marp_cli()
        assert result is not None

        if isinstance(result, str):
            proc = subprocess.run([result, "--help"], capture_output=True, text=True, timeout=30)
        else:
            proc = subprocess.run(result + ["--help"], capture_output=True, text=True, timeout=60)

        assert proc.returncode == 0, f"--help failed: {proc.stderr}"
        # Help output should mention common options
        output_lower = proc.stdout.lower()
        assert "html" in output_lower or "pdf" in output_lower or "output" in output_lower


class TestInstallerCacheDirectory:
    """Test cache directory creation and structure."""

    def test_cache_dir_is_created(self):
        """Verify cache directory is created if it doesn't exist."""
        cache_dir = _get_cache_dir()
        assert cache_dir.exists(), "Cache directory should be created"
        assert cache_dir.is_dir(), "Cache directory should be a directory"

    def test_cache_dir_is_writable(self):
        """Verify cache directory is writable."""
        cache_dir = _get_cache_dir()
        test_file = cache_dir / ".write_test"
        try:
            test_file.write_text("test")
            assert test_file.exists()
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_cache_dir_contains_version_subdir_after_resolve(self):
        """Verify version subdirectory exists after resolving."""
        resolve_marp_cli()  # Ensure binary is downloaded/cached
        cache_dir = _get_cache_dir()
        version_dir = cache_dir / MARP_CLI_VERSION
        # Only check if we're using cached binary (not system marp or npx)
        info = get_marp_version_info()
        if info["source"] == "cached":
            assert version_dir.exists(), "Version directory should exist for cached binary"
