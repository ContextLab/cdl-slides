"""Asset resolution and CSS path rewriting for cdl-slides.

This module provides utilities for:
- Locating bundled package assets (themes, fonts, images, JS)
- Detecting the Marp CLI binary
- Rewriting CSS url() references to use absolute file:// paths
- Preparing themes for compilation with proper asset resolution
"""

import re
import shutil
import tempfile
from pathlib import Path
from typing import Optional

try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files  # type: ignore


def get_assets_dir() -> Path:
    """Return the path to the assets directory within the installed package."""
    assets_path = files("cdl_slides").joinpath("assets")
    try:
        return Path(str(assets_path))
    except (TypeError, AttributeError):
        return Path(assets_path)  # type: ignore


def get_themes_dir() -> Path:
    """Return the path to the themes directory."""
    return get_assets_dir() / "themes"


def get_fonts_dir() -> Path:
    """Return the path to the fonts directory."""
    return get_assets_dir() / "fonts"


def get_images_dir() -> Path:
    """Return the path to the images directory."""
    return get_assets_dir() / "images"


def get_js_dir() -> Path:
    """Return the path to the JavaScript directory."""
    return get_assets_dir() / "js"


def detect_marp_cli() -> Optional[Path]:
    """Detect the Marp CLI binary location.

    Checks in order:
    1. System PATH (via shutil.which)
    2. npm global install locations (platform-specific)
    3. Local node_modules/.bin

    Returns:
        Path to marp binary if found, None otherwise
    """
    marp_path = shutil.which("marp")
    if marp_path:
        return Path(marp_path)

    npm_global_paths = [
        Path.home() / ".npm-global" / "bin" / "marp",
        Path.home() / ".npm" / "bin" / "marp",
        Path("/usr/local/bin/marp"),
        Path("/usr/bin/marp"),
    ]

    if Path.home().drive:
        npm_global_paths.extend(
            [
                Path.home() / "AppData" / "Roaming" / "npm" / "marp.cmd",
                Path.home() / "AppData" / "Roaming" / "npm" / "marp",
            ]
        )

    for path in npm_global_paths:
        if path.exists():
            return path

    local_marp = Path.cwd() / "node_modules" / ".bin" / "marp"
    if local_marp.exists():
        return local_marp

    if Path.home().drive:
        local_marp_cmd = Path.cwd() / "node_modules" / ".bin" / "marp.cmd"
        if local_marp_cmd.exists():
            return local_marp_cmd

    return None


def _path_to_file_url(path: Path) -> str:
    """Convert a filesystem path to a file:// URL.

    Handles Windows paths correctly by using forward slashes.
    """
    posix_path = path.as_posix()

    if path.drive:
        return f"file:///{posix_path}"
    else:
        return f"file://{posix_path}"


def _rewrite_css_urls(css_content: str, assets_dir: Path) -> str:
    """Rewrite url() references in CSS to use absolute file:// paths.

    Rewrites:
    - ../../fonts/X -> file:///absolute/path/to/assets/fonts/X
    - themes/X -> file:///absolute/path/to/assets/themes/X

    Leaves https:// URLs untouched.
    """
    fonts_dir = assets_dir / "fonts"
    themes_dir = assets_dir / "themes"

    def replace_url(match: re.Match) -> str:
        url = match.group(1).strip("'\"")

        if url.startswith(("http://", "https://", "data:")):
            return match.group(0)

        if url.startswith("../../fonts/"):
            font_name = url.replace("../../fonts/", "")
            absolute_path = fonts_dir / font_name
            return f"url('{_path_to_file_url(absolute_path)}')"

        if url.startswith("themes/"):
            theme_file = url.replace("themes/", "")
            absolute_path = themes_dir / theme_file
            return f"url('{_path_to_file_url(absolute_path)}')"

        return match.group(0)

    url_pattern = re.compile(r'url\(["\']?([^)]+?)["\']?\)', re.IGNORECASE)
    return url_pattern.sub(replace_url, css_content)


def prepare_theme_for_compilation(work_dir: Path) -> Path:
    """Prepare the CDL theme for Marp compilation with rewritten asset paths.

    Creates a temporary directory in the same location as the work directory,
    copies cdl-theme.css, and rewrites all url() references to use absolute
    file:// paths pointing to the package's bundled assets.

    Args:
        work_dir: Directory containing the input markdown file

    Returns:
        Path to the directory containing the rewritten CSS file
        (suitable for use with marp --theme-set)
    """
    assets_dir = get_assets_dir()
    original_theme = get_themes_dir() / "cdl-theme.css"

    if not original_theme.exists():
        raise FileNotFoundError(f"CDL theme not found at {original_theme}")

    temp_dir = Path(tempfile.mkdtemp(prefix="cdl-theme-", dir=work_dir))

    css_content = original_theme.read_text(encoding="utf-8")
    rewritten_css = _rewrite_css_urls(css_content, assets_dir)

    output_theme = temp_dir / "cdl-theme.css"
    output_theme.write_text(rewritten_css, encoding="utf-8")

    return temp_dir


def get_marp_install_instructions() -> str:
    """Return platform-specific instructions for installing Marp CLI."""
    import platform

    system = platform.system()

    base_instructions = """Marp CLI is required but not found.

Install options:

1. Via npm (recommended):
   npm install -g @marp-team/marp-cli

2. Via Homebrew (macOS):
   brew install marp-cli

3. Via Chocolatey (Windows):
   choco install marp-cli

4. Download standalone binary:
   https://github.com/marp-team/marp-cli/releases
"""

    if system == "Darwin":
        return base_instructions + "\nRecommended for macOS: brew install marp-cli"
    elif system == "Windows":
        return base_instructions + "\nRecommended for Windows: npm install -g @marp-team/marp-cli"
    else:
        return base_instructions + "\nRecommended for Linux: npm install -g @marp-team/marp-cli"
