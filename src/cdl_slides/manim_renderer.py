#!/usr/bin/env python3
"""
Manim animation rendering for CDL Slides.

This module provides functionality to render Manim animation code blocks
embedded in Markdown slides to GIF files with transparent backgrounds.

Pipeline:
1. Extract manim code from ```manim blocks
2. Render with manim CLI to MP4
3. Convert MP4 to GIF with FFmpeg (palette generation + colorkey for transparency)
4. Post-process with PIL (white→transparent, loop=1 for play-once)

Usage:
    from cdl_slides.manim_renderer import render_manim_block, MANIM_AVAILABLE

    if MANIM_AVAILABLE:
        gif_path = render_manim_block(code, output_dir, scene_name)
"""

import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional, Tuple

# Check for manim availability (deferred import pattern)
MANIM_AVAILABLE = False
try:
    import manim  # noqa: F401

    MANIM_AVAILABLE = True
except ImportError:
    pass

# Check for PIL availability (for GIF post-processing)
PIL_AVAILABLE = False
try:
    from PIL import Image

    PIL_AVAILABLE = True
except ImportError:
    pass

# Check for FFmpeg availability
FFMPEG_AVAILABLE = shutil.which("ffmpeg") is not None


def check_dependencies() -> Tuple[bool, list]:
    """Check if all required dependencies are available.

    Returns:
        Tuple of (all_available, list of missing dependencies)
    """
    missing = []
    if not MANIM_AVAILABLE:
        missing.append("manim (pip install manim)")
    if not FFMPEG_AVAILABLE:
        missing.append("ffmpeg (brew install ffmpeg / apt install ffmpeg)")
    if not PIL_AVAILABLE:
        missing.append("Pillow (pip install Pillow)")
    return len(missing) == 0, missing


def get_content_hash(content: str) -> str:
    """Generate a short hash of content for caching/naming."""
    return hashlib.md5(content.encode()).hexdigest()[:8]


def parse_manim_metadata(code: str) -> dict:
    """Parse metadata comments from manim code block.

    Supported metadata:
        # scene: SceneName
        # height: 500
        # quality: l/m/h/p (low/medium/high/production)
        # fps: 24

    Returns:
        dict with parsed metadata and cleaned code
    """
    metadata = {
        "scene": None,
        "height": 500,
        "quality": "h",  # high quality by default
        "fps": 24,
        "code": code,
    }

    lines = code.split("\n")
    code_lines = []

    for line in lines:
        # Check for metadata comments
        if match := re.match(r"^\s*#\s*scene:\s*(\w+)\s*$", line, re.IGNORECASE):
            metadata["scene"] = match.group(1)
        elif match := re.match(r"^\s*#\s*height:\s*(\d+)\s*$", line, re.IGNORECASE):
            metadata["height"] = int(match.group(1))
        elif match := re.match(r"^\s*#\s*quality:\s*([lmhp])\s*$", line, re.IGNORECASE):
            metadata["quality"] = match.group(1).lower()
        elif match := re.match(r"^\s*#\s*fps:\s*(\d+)\s*$", line, re.IGNORECASE):
            metadata["fps"] = int(match.group(1))
        else:
            code_lines.append(line)

    metadata["code"] = "\n".join(code_lines)
    return metadata


def extract_scene_class_name(code: str) -> Optional[str]:
    """Extract the Scene class name from manim code.

    Looks for: class MyScene(Scene): or class MyScene(BaseScene):
    """
    # Match class definitions that inherit from Scene or any *Scene base
    pattern = r"class\s+(\w+)\s*\(\s*\w*Scene\s*\)"
    match = re.search(pattern, code)
    if match:
        return match.group(1)
    return None


def create_render_script(code: str, scene_name: str) -> str:
    """Create a complete manim script with CDL theme BaseScene.

    Injects the BaseScene class that sets:
    - White background
    - Black default text color
    - CDL-compatible styling
    """
    # Check if the code already defines a BaseScene or imports one
    has_base_scene = "class BaseScene" in code or "from " in code and "BaseScene" in code

    base_scene_code = '''
from manim import *

class BaseScene(Scene):
    """CDL-themed base scene with white background and black text."""

    ANIM_SPEED = 1.0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera.background_color = WHITE
        Mobject.set_default(color=BLACK)

    def wait(self, num_secs=1):
        super().wait(num_secs * self.ANIM_SPEED)

    def play(self, *args, **kwargs):
        if "run_time" in kwargs:
            kwargs["run_time"] *= self.ANIM_SPEED
        else:
            kwargs["run_time"] = 1.0
        super().play(*args, **kwargs)
'''

    # If code doesn't have imports, add them
    if "from manim import" not in code and "import manim" not in code:
        code = "from manim import *\n\n" + code

    # Add BaseScene if not already present
    if not has_base_scene:
        code = re.sub(
            r"class\s+(\w+)\s*\(\s*Scene\s*\)",
            r"class \1(BaseScene)",
            code,
        )

        lines = code.split("\n")
        import_end = 0
        for i, line in enumerate(lines):
            if line.startswith("from ") or line.startswith("import "):
                import_end = i + 1
            elif line.strip() and not line.startswith("#"):
                break

        lines.insert(import_end, base_scene_code)
        code = "\n".join(lines)

    return code


def render_to_mp4(
    code: str,
    scene_name: str,
    output_dir: Path,
    quality: str = "h",
    fps: int = 24,
    timeout: int = 120,
) -> Optional[Path]:
    """Render manim code to MP4 file.

    Args:
        code: Complete manim Python code
        scene_name: Name of the Scene class to render
        output_dir: Directory to store output
        quality: Manim quality flag (l/m/h/p)
        fps: Frames per second
        timeout: Render timeout in seconds

    Returns:
        Path to rendered MP4 file, or None if failed
    """
    if not MANIM_AVAILABLE:
        return None

    # Create temp directory for rendering
    with tempfile.TemporaryDirectory(prefix="cdl_manim_") as temp_dir:
        temp_path = Path(temp_dir)
        script_path = temp_path / "scene.py"

        # Write the script
        script_path.write_text(code)

        # Build manim command
        quality_map = {"l": "-ql", "m": "-qm", "h": "-qh", "p": "-qp"}
        quality_flag = quality_map.get(quality, "-qh")

        cmd = [
            sys.executable,
            "-m",
            "manim",
            quality_flag,
            "--format=mp4",
            "--fps",
            str(fps),
            "--media_dir",
            str(temp_path / "media"),
            str(script_path),
            scene_name,
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=timeout,
                cwd=temp_path,
            )

            if result.returncode != 0:
                stderr = result.stderr.decode() if result.stderr else ""
                print(f"Manim render failed for {scene_name}: {stderr[:500]}", file=sys.stderr)
                return None

            # Find the output MP4
            media_dir = temp_path / "media" / "videos" / "scene"
            for quality_dir in media_dir.glob("*"):
                for mp4_file in quality_dir.glob(f"{scene_name}*.mp4"):
                    # Copy to output directory
                    output_dir.mkdir(parents=True, exist_ok=True)
                    dest = output_dir / f"{scene_name}.mp4"
                    shutil.copy2(mp4_file, dest)
                    return dest

            print(f"No MP4 output found for {scene_name}", file=sys.stderr)
            return None

        except subprocess.TimeoutExpired:
            print(f"Manim render timed out for {scene_name} (>{timeout}s)", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Manim render error for {scene_name}: {e}", file=sys.stderr)
            return None


def convert_mp4_to_gif(
    mp4_path: Path,
    gif_path: Path,
    fps: int = 24,
    scale_width: int = 960,
) -> bool:
    """Convert MP4 to GIF using FFmpeg with palette generation.

    Uses colorkey filter to make white background transparent.

    Args:
        mp4_path: Path to input MP4
        gif_path: Path to output GIF
        fps: Output GIF framerate
        scale_width: Width to scale to (maintains aspect ratio)

    Returns:
        True if successful
    """
    if not FFMPEG_AVAILABLE:
        return False

    palette_path = gif_path.with_suffix(".palette.png")

    try:
        # Step 1: Generate palette with transparency support
        vf_palette = f"fps={fps},scale={scale_width}:-1:flags=lanczos,palettegen=reserve_transparent=1:stats_mode=diff"
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(mp4_path), "-vf", vf_palette, str(palette_path)],
            capture_output=True,
            check=True,
        )

        vf_gif = (
            f"fps={fps},scale={scale_width}:-1:flags=lanczos,"
            f"colorkey=white:0.1:0.0[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3"
        )
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(mp4_path),
                "-i",
                str(palette_path),
                "-lavfi",
                vf_gif,
                str(gif_path),
            ],
            capture_output=True,
            check=True,
        )

        return True

    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode() if e.stderr else ""
        print(f"FFmpeg conversion failed: {stderr[:500]}", file=sys.stderr)
        return False
    finally:
        # Clean up palette file
        if palette_path.exists():
            palette_path.unlink()


def postprocess_gif(gif_path: Path, loop_count: int = 1) -> bool:
    """Post-process GIF: ensure white→transparent and set loop count.

    Args:
        gif_path: Path to GIF file to modify in place
        loop_count: Number of times to loop (1 = play once, 0 = infinite)

    Returns:
        True if successful
    """
    if not PIL_AVAILABLE:
        return False

    try:
        img = Image.open(gif_path)
        frames = []
        durations = []

        # Process each frame
        for frame_num in range(img.n_frames):
            img.seek(frame_num)
            frame = img.convert("RGBA")
            data = frame.getdata()

            # Replace near-white pixels with transparent
            new_data = []
            for item in data:
                # Check if pixel is near-white (R, G, B all > 250)
                if item[0] > 250 and item[1] > 250 and item[2] > 250:
                    new_data.append((255, 255, 255, 0))  # Fully transparent
                else:
                    new_data.append(item)

            frame.putdata(new_data)
            frames.append(frame)
            durations.append(img.info.get("duration", 40))

        # Save with specified loop count
        frames[0].save(
            gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=loop_count,
            disposal=2,  # Restore to background between frames
        )

        return True

    except Exception as e:
        print(f"GIF post-processing failed: {e}", file=sys.stderr)
        return False


def get_cache_path(output_dir: Path, content_hash: str, scene_name: str) -> Path:
    """Get the path where a cached GIF would be stored."""
    return output_dir / f"{scene_name}_{content_hash}.gif"


def is_cached(output_dir: Path, content_hash: str, scene_name: str) -> Optional[Path]:
    """Check if a rendered GIF is cached.

    Returns:
        Path to cached GIF if exists, None otherwise
    """
    cache_path = get_cache_path(output_dir, content_hash, scene_name)
    if cache_path.exists():
        return cache_path
    return None


def render_manim_block(
    code: str,
    output_dir: Path,
    scene_name: Optional[str] = None,
    height: int = 500,
    quality: str = "h",
    fps: int = 24,
    use_cache: bool = True,
) -> Optional[Tuple[Path, int]]:
    """Render a manim code block to a transparent GIF.

    Full pipeline:
    1. Parse metadata from code
    2. Check cache
    3. Create render script with BaseScene
    4. Render to MP4 with manim
    5. Convert to GIF with FFmpeg
    6. Post-process for transparency and loop control

    Args:
        code: Manim Python code (may include metadata comments)
        output_dir: Directory to store output GIF
        scene_name: Override scene name (auto-detected from code if None)
        height: Height for embedding in slides
        quality: Render quality (l/m/h/p)
        fps: Frames per second
        use_cache: Whether to use cached renders

    Returns:
        Tuple of (path to GIF, height) or None if failed
    """
    # Check dependencies
    deps_ok, missing = check_dependencies()
    if not deps_ok:
        print(f"Manim dependencies missing: {', '.join(missing)}", file=sys.stderr)
        return None

    # Parse metadata
    metadata = parse_manim_metadata(code)
    clean_code = metadata["code"]
    height = metadata.get("height", height)
    quality = metadata.get("quality", quality)
    fps = metadata.get("fps", fps)

    # Determine scene name
    if metadata["scene"]:
        scene_name = metadata["scene"]
    elif scene_name is None:
        scene_name = extract_scene_class_name(clean_code)

    if not scene_name:
        # Generate name from content hash
        scene_name = f"Scene_{get_content_hash(clean_code)}"

    # Check cache
    content_hash = get_content_hash(code)
    if use_cache:
        cached = is_cached(output_dir, content_hash, scene_name)
        if cached:
            return (cached, height)

    # Create complete render script
    render_code = create_render_script(clean_code, scene_name)

    # Ensure output directory exists
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Render to MP4
    mp4_path = render_to_mp4(render_code, scene_name, output_dir, quality, fps)
    if not mp4_path:
        return None

    # Convert to GIF
    gif_path = get_cache_path(output_dir, content_hash, scene_name)
    if not convert_mp4_to_gif(mp4_path, gif_path, fps):
        return None

    # Post-process (white→transparent, play once)
    postprocess_gif(gif_path, loop_count=1)

    # Clean up MP4
    if mp4_path.exists():
        mp4_path.unlink()

    return (gif_path, height)


def generate_warning_html(message: str) -> str:
    """Generate HTML for a warning message when rendering fails."""
    escaped = message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f"""<div class="warning-box" data-title="Animation Render Failed">

{escaped}

</div>"""


if __name__ == "__main__":
    # Simple test
    deps_ok, missing = check_dependencies()
    print(f"Dependencies OK: {deps_ok}")
    if missing:
        print(f"Missing: {', '.join(missing)}")
