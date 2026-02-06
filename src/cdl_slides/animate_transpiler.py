"""Transpiler that converts parsed animate AST into manim Python code."""

from __future__ import annotations

from typing import Any

COLOR_MAP = {
    "blue": "BLUE",
    "red": "RED",
    "green": "GREEN",
    "yellow": "YELLOW",
    "orange": "ORANGE",
    "white": "WHITE",
    "black": "BLACK",
}

POSITION_DIRECTIONS = {
    "above": "UP",
    "below": "DOWN",
    "left-of": "LEFT",
    "right-of": "RIGHT",
}


def generate_metadata_comments(metadata: dict[str, Any]) -> str:
    lines = [
        "# scene: AnimateScene",
        f"# height: {metadata.get('height', 500)}",
    ]
    if "quality" in metadata:
        lines.append(f"# quality: {metadata['quality']}")
    return "\n".join(lines)


def generate_object_code(obj: dict[str, Any], registry: dict[str, str]) -> str:
    kind = obj.get("kind")
    name = obj.get("name")

    registry[name] = name

    if kind == "equation":
        content = obj.get("content", "")
        return f'{name} = MathTex(r"{content}")'

    if kind == "text":
        content = obj.get("content", "")
        return f'{name} = Text("{content}")'

    if kind in ("circle", "square", "arrow"):
        color = obj.get("params", {}).get("color", "white")
        manim_color = COLOR_MAP.get(color, "WHITE")
        class_name = kind.capitalize()
        return f"{name} = {class_name}(color={manim_color})"

    return ""


def generate_position_code(var_name: str, position: dict[str, Any] | None, registry: dict[str, str]) -> str:
    if not position:
        return ""

    pos_type = position.get("type")

    if pos_type == "center":
        return f"{var_name}.move_to(ORIGIN)"

    if pos_type in POSITION_DIRECTIONS:
        reference = position.get("reference")
        direction = POSITION_DIRECTIONS[pos_type]
        return f"{var_name}.next_to({reference}, {direction})"

    return ""


def generate_animation_code(cmd: dict[str, Any], registry: dict[str, str]) -> str:
    cmd_type = cmd.get("type")

    if cmd_type == "write":
        obj = cmd.get("object", {})
        name = obj.get("name")
        return f"self.play(Write({name}))"

    if cmd_type == "create":
        obj = cmd.get("object", {})
        name = obj.get("name")
        return f"self.play(Create({name}))"

    if cmd_type == "fade-in":
        target = cmd.get("target")
        return f"self.play(FadeIn({target}))"

    if cmd_type == "fade-out":
        target = cmd.get("target")
        return f"self.play(FadeOut({target}))"

    if cmd_type == "transform":
        source = cmd.get("source")
        target = cmd.get("target")
        return f"self.play(Transform({source}, {target}))"

    if cmd_type == "wait":
        duration = cmd.get("duration", 1)
        return f"self.wait({duration})"

    return ""


def transpile_to_manim(ast: dict[str, Any]) -> str:
    metadata = ast.get("metadata", {})
    commands = ast.get("commands", [])

    lines: list[str] = []
    lines.append(generate_metadata_comments(metadata))
    lines.append("")
    lines.append("class AnimateScene(Scene):")
    lines.append("    def construct(self):")

    if not commands:
        lines.append("        pass")
        return "\n".join(lines)

    registry: dict[str, str] = {}
    body_lines: list[str] = []

    for cmd in commands:
        cmd_type = cmd.get("type")

        if cmd_type in ("write", "create"):
            obj = cmd.get("object", {})
            obj_code = generate_object_code(obj, registry)
            if obj_code:
                body_lines.append(obj_code)

            position = cmd.get("position")
            if position:
                name = obj.get("name")
                pos_code = generate_position_code(name, position, registry)
                if pos_code:
                    body_lines.append(pos_code)

        anim_code = generate_animation_code(cmd, registry)
        if anim_code:
            body_lines.append(anim_code)

    for line in body_lines:
        lines.append(f"        {line}")

    return "\n".join(lines)
