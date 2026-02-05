"""Tests for cdl_slides.marp_cli."""

import platform

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
