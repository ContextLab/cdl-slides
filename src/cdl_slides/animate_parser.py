"""Parser for animate DSL blocks that converts markdown-based animation syntax to AST."""

from __future__ import annotations

import re
from typing import Any


def parse_position(pos: str | None) -> dict[str, Any] | None:
    """Parse position like 'below eq1' or 'at center'. Returns dict or None."""
    if not pos or not pos.strip():
        return None

    pos = pos.strip()

    if pos == "at center" or pos == "center":
        return {"type": "center"}

    for rel_type in ("above", "below", "left-of", "right-of"):
        if pos.startswith(rel_type):
            ref = pos[len(rel_type) :].strip()
            return {"type": rel_type, "reference": ref}

    return None


def _parse_range(range_str: str) -> list[float]:
    """Parse a range like '[-3,3,1]' or '[-3,3]' into a list of floats."""
    range_str = range_str.strip().strip("[]")
    parts = [p.strip() for p in range_str.split(",")]
    return [float(p) for p in parts if p]


def parse_object_spec(spec: str) -> dict[str, Any]:
    """Parse object definition like 'equation "E=mc^2" as eq1'. Returns dict."""
    spec = spec.strip()

    if match := re.match(r'^(equation|text)\s+"((?:[^"\\]|\\.)*)"\s+as\s+(\w+)', spec):
        kind = match.group(1)
        content = match.group(2).replace("\\\\", "\\")
        name = match.group(3)
        return {"kind": kind, "content": content, "name": name}

    if match := re.match(r"^(circle|square|arrow)(?:\s+color=(\w+))?\s+as\s+(\w+)", spec):
        kind = match.group(1)
        color = match.group(2) if match.group(2) else "white"
        name = match.group(3)
        return {"kind": kind, "params": {"color": color}, "name": name}

    # Parse axes: axes x=[...] y=[...] as name
    if match := re.match(r"^axes\s+x=(\[[^\]]+\])\s+y=(\[[^\]]+\])(?:\s+length=(\d+),(\d+))?\s+as\s+(\w+)", spec):
        x_range = _parse_range(match.group(1))
        y_range = _parse_range(match.group(2))
        x_length = int(match.group(3)) if match.group(3) else 6
        y_length = int(match.group(4)) if match.group(4) else 4
        name = match.group(5)
        return {
            "kind": "axes",
            "params": {
                "x_range": x_range,
                "y_range": y_range,
                "x_length": x_length,
                "y_length": y_length,
            },
            "name": name,
        }

    # Parse graph: graph "formula" x=[...] color=X as name
    if match := re.match(r'^graph\s+"([^"]+)"\s+x=(\[[^\]]+\])(?:\s+color=(\w+))?\s+as\s+(\w+)', spec):
        formula = match.group(1)
        x_range = _parse_range(match.group(2))
        color = match.group(3) if match.group(3) else "blue"
        name = match.group(4)
        return {
            "kind": "graph",
            "params": {
                "formula": formula,
                "x_range": x_range,
                "color": color,
            },
            "name": name,
        }

    return {}


def parse_command(line: str) -> dict[str, Any] | None:
    """Parse single command line. Returns dict or None for empty/comment lines."""
    if not line:
        return None

    line = line.strip()

    if not line or line.startswith("#"):
        return None

    if line.startswith("wait "):
        duration_str = line[5:].strip()
        return {"type": "wait", "duration": float(duration_str)}

    if line.startswith("fade-in "):
        target = line[8:].strip()
        return {"type": "fade-in", "target": target}

    if line.startswith("fade-out "):
        target = line[9:].strip()
        return {"type": "fade-out", "target": target}

    if match := re.match(r"^transform\s+(\w+)\s*->\s*(\w+)", line):
        return {"type": "transform", "source": match.group(1), "target": match.group(2)}

    if line.startswith("write "):
        return _parse_write_command(line[6:])

    if line.startswith("create "):
        return _parse_create_command(line[7:])

    if line.startswith("draw "):
        target = line[5:].strip()
        return {"type": "draw", "target": target}

    if line.startswith("plot "):
        return _parse_plot_command(line[5:])

    if line.startswith("manim "):
        return _parse_manim_command(line[6:])

    return None


def _parse_plot_command(rest: str) -> dict[str, Any]:
    """Parse: plot "formula" on axes_name color=X as name"""
    if match := re.match(r'^"([^"]+)"\s+on\s+(\w+)(?:\s+color=(\w+))?\s+as\s+(\w+)', rest):
        formula = match.group(1)
        axes_name = match.group(2)
        color = match.group(3) if match.group(3) else "blue"
        name = match.group(4)
        return {
            "type": "plot",
            "formula": formula,
            "axes": axes_name,
            "color": color,
            "name": name,
        }
    return {}


def _parse_manim_command(rest: str) -> dict[str, Any]:
    """Parse: manim <python_code> as name"""
    if match := re.match(r"^(.+)\s+as\s+(\w+)$", rest):
        code = match.group(1).strip()
        name = match.group(2)
        return {
            "type": "manim",
            "code": code,
            "name": name,
        }
    return {}


def _parse_write_command(rest: str) -> dict[str, Any]:
    """Parse write command: equation/text "content" as name [position]."""
    position_keywords = ("at center", "above ", "below ", "left-of ", "right-of ")
    pos_str = None

    for kw in position_keywords:
        idx = rest.rfind(kw)
        if idx != -1:
            pos_str = rest[idx:]
            rest = rest[:idx].strip()
            break

    obj = parse_object_spec(rest)
    position = parse_position(pos_str)

    result: dict[str, Any] = {"type": "write", "object": obj}
    if position:
        result["position"] = position

    return result


def _parse_create_command(rest: str) -> dict[str, Any]:
    """Parse create command: circle/square/arrow color=X as name [position]."""
    position_keywords = ("at center", "above ", "below ", "left-of ", "right-of ")
    pos_str = None

    for kw in position_keywords:
        idx = rest.rfind(kw)
        if idx != -1:
            pos_str = rest[idx:]
            rest = rest[:idx].strip()
            break

    obj = parse_object_spec(rest)
    position = parse_position(pos_str)

    result: dict[str, Any] = {"type": "create", "object": obj}
    if position:
        result["position"] = position

    return result


def parse_metadata(lines: list[str]) -> dict[str, Any]:
    """Extract height, width, quality, scale from metadata lines. Returns dict with defaults."""
    metadata = {"height": 500, "width": None, "quality": "high", "scale": None}

    for line in lines:
        line = line.strip()
        if match := re.match(r"^height:\s*(\d+)\s*$", line, re.IGNORECASE):
            metadata["height"] = int(match.group(1))
        elif match := re.match(r"^width:\s*(\d+)\s*$", line, re.IGNORECASE):
            metadata["width"] = int(match.group(1))
        elif match := re.match(r"^quality:\s*(low|medium|high)\s*$", line, re.IGNORECASE):
            metadata["quality"] = match.group(1).lower()
        elif match := re.match(r"^scale:\s*([\d.]+)\s*$", line, re.IGNORECASE):
            metadata["scale"] = float(match.group(1))

    return metadata


def parse_animate_block(content: str) -> dict[str, Any]:
    """Main entry point. Returns AST dict with 'metadata' and 'commands' keys."""
    lines = content.split("\n") if content else []

    metadata_lines = []
    command_lines = []
    in_metadata = True

    for line in lines:
        stripped = line.strip()

        if not stripped:
            in_metadata = False
            continue

        if in_metadata and re.match(r"^(height|width|quality|scale):", stripped, re.IGNORECASE):
            metadata_lines.append(stripped)
        else:
            in_metadata = False
            command_lines.append(stripped)

    metadata = parse_metadata(metadata_lines)
    commands = []

    for line in command_lines:
        cmd = parse_command(line)
        if cmd:
            commands.append(cmd)

    return {"metadata": metadata, "commands": commands}
