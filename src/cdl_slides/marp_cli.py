"""Marp CLI detection and automatic installation for cdl-slides.

Handles three tiers of marp-cli resolution:
1. System-installed marp (via npm, brew, etc.)
2. Cached standalone binary (downloaded on first use)
3. npx fallback (if Node.js is available)
"""

import io
import platform
import shutil
import stat
import subprocess
import tarfile
import zipfile
from pathlib import Path
from typing import List, Optional, Union
from urllib.request import urlopen

MARP_CLI_VERSION = "v4.2.3"

_RELEASE_BASE = f"https://github.com/marp-team/marp-cli/releases/download/{MARP_CLI_VERSION}"

_PLATFORM_MAP = {
    ("Darwin", "arm64"): ("mac", "tar.gz"),
    ("Darwin", "x86_64"): ("mac", "tar.gz"),
    ("Linux", "x86_64"): ("linux", "tar.gz"),
    ("Linux", "aarch64"): ("linux", "tar.gz"),
    ("Windows", "AMD64"): ("win", "zip"),
    ("Windows", "x86_64"): ("win", "zip"),
}


def _get_cache_dir() -> Path:
    system = platform.system()
    if system == "Darwin":
        cache_dir = Path.home() / "Library" / "Caches" / "cdl-slides"
    elif system == "Windows":
        local_app_data = Path.home() / "AppData" / "Local"
        cache_dir = local_app_data / "cdl-slides" / "cache"
    else:
        xdg = Path.home() / ".cache"
        cache_dir = xdg / "cdl-slides"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _get_platform_key() -> Optional[tuple]:
    system = platform.system()
    machine = platform.machine()
    key = (system, machine)
    if key in _PLATFORM_MAP:
        return key
    for k in _PLATFORM_MAP:
        if k[0] == system:
            return k
    return None


def _get_cached_marp_path() -> Optional[Path]:
    cache_dir = _get_cache_dir()
    marp_dir = cache_dir / MARP_CLI_VERSION

    system = platform.system()
    if system == "Windows":
        marp_bin = marp_dir / "marp.exe"
    else:
        marp_bin = marp_dir / "marp"

    if marp_bin.exists():
        return marp_bin
    return None


def _download_marp_cli() -> Optional[Path]:
    platform_key = _get_platform_key()
    if platform_key is None:
        return None

    os_name, archive_ext = _PLATFORM_MAP[platform_key]
    filename = f"marp-cli-{MARP_CLI_VERSION}-{os_name}.{archive_ext}"
    url = f"{_RELEASE_BASE}/{filename}"

    cache_dir = _get_cache_dir()
    marp_dir = cache_dir / MARP_CLI_VERSION
    marp_dir.mkdir(parents=True, exist_ok=True)

    try:
        with urlopen(url, timeout=60) as response:
            data = response.read()

        if archive_ext == "tar.gz":
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
                tar.extractall(path=str(marp_dir))
        elif archive_ext == "zip":
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                zf.extractall(path=str(marp_dir))

        system = platform.system()
        if system == "Windows":
            marp_bin = marp_dir / "marp.exe"
        else:
            marp_bin = marp_dir / "marp"

        if marp_bin.exists():
            marp_bin.chmod(marp_bin.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
            return marp_bin

        for f in marp_dir.rglob("marp*"):
            if f.is_file() and f.name in ("marp", "marp.exe"):
                f.chmod(f.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
                return f

    except Exception:
        pass

    return None


def _check_npx() -> Optional[list]:
    npx_path = shutil.which("npx")
    if npx_path is None:
        return None
    try:
        result = subprocess.run(
            [npx_path, "--yes", "@marp-team/marp-cli", "--version"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return [npx_path, "--yes", "@marp-team/marp-cli"]
    except Exception:
        pass
    return None


def resolve_marp_cli() -> Optional[Union[str, List[str]]]:
    """Resolve marp-cli binary, installing if necessary.

    Resolution order:
    1. System PATH (marp already installed globally)
    2. Cached standalone binary (previously downloaded)
    3. Download standalone binary (first-time auto-install)
    4. npx fallback (requires Node.js)

    Returns:
        Path string to marp binary, or list of command parts for npx.
        None if marp-cli cannot be resolved.
    """
    system_marp = shutil.which("marp")
    if system_marp:
        return system_marp

    cached = _get_cached_marp_path()
    if cached:
        return str(cached)

    downloaded = _download_marp_cli()
    if downloaded:
        return str(downloaded)

    npx_cmd = _check_npx()
    if npx_cmd:
        return npx_cmd

    return None


def get_marp_version_info() -> dict:
    """Get information about the marp-cli installation."""
    info = {
        "installed": False,
        "source": None,
        "path": None,
        "version": None,
    }

    system_marp = shutil.which("marp")
    if system_marp:
        info["installed"] = True
        info["source"] = "system"
        info["path"] = system_marp
        try:
            result = subprocess.run([system_marp, "--version"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                info["version"] = result.stdout.strip().split("\n")[0]
        except Exception:
            pass
        return info

    cached = _get_cached_marp_path()
    if cached:
        info["installed"] = True
        info["source"] = "cached"
        info["path"] = str(cached)
        info["version"] = MARP_CLI_VERSION
        return info

    npx_path = shutil.which("npx")
    if npx_path:
        info["source"] = "npx_available"

    return info
