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
    if metadata.get("width"):
        lines.append(f"# width: {metadata['width']}")
    if metadata.get("quality"):
        lines.append(f"# quality: {metadata['quality']}")
    if metadata.get("scale"):
        lines.append(f"# scale: {metadata['scale']}")
    return "\n".join(lines)


def generate_object_code(obj: dict[str, Any], registry: dict[str, str], scale: float | None = None) -> str:
    kind = obj.get("kind")
    name = obj.get("name")

    registry[name] = name

    if kind == "equation":
        content = obj.get("content", "")
        scale_suffix = f".scale({scale})" if scale else ""
        return f'{name} = MathTex(r"{content}"){scale_suffix}'

    if kind == "text":
        content = obj.get("content", "")
        scale_suffix = f".scale({scale})" if scale else ""
        return f'{name} = Text("{content}"){scale_suffix}'

    if kind in ("circle", "square", "arrow"):
        color = obj.get("params", {}).get("color", "white")
        manim_color = COLOR_MAP.get(color, "WHITE")
        class_name = kind.capitalize()
        return f"{name} = {class_name}(color={manim_color})"

    if kind == "axes":
        params = obj.get("params", {})
        x_range = params.get("x_range", [-3, 3, 1])
        y_range = params.get("y_range", [-2, 2, 1])
        x_length = params.get("x_length", 6)
        y_length = params.get("y_length", 4)
        return f'{name} = Axes(x_range={x_range}, y_range={y_range}, x_length={x_length}, y_length={y_length}, axis_config={{"include_numbers": True}})'

    if kind == "graph":
        params = obj.get("params", {})
        formula = params.get("formula", "x")
        x_range = params.get("x_range", [-3, 3])
        color = params.get("color", "blue")
        manim_color = COLOR_MAP.get(color, "BLUE")
        return f"{name} = FunctionGraph(lambda x: {formula}, x_range={x_range}, color={manim_color})"

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
        kind = obj.get("kind")
        if kind == "axes":
            return f"self.play(Create({name}))"
        if kind == "graph":
            return f"self.play(Create({name}))"
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

    if cmd_type == "draw":
        target = cmd.get("target")
        return f"self.play(Create({target}))"

    if cmd_type == "plot":
        return ""

    if cmd_type == "manim":
        return ""

    return ""


def generate_plot_code(cmd: dict[str, Any], registry: dict[str, str]) -> list[str]:
    formula = cmd.get("formula", "x")
    axes_name = cmd.get("axes")
    color = cmd.get("color", "blue")
    name = cmd.get("name")
    manim_color = COLOR_MAP.get(color, "BLUE")

    registry[name] = name
    return [
        f"{name} = {axes_name}.plot(lambda x: {formula}, color={manim_color})",
        f"self.play(Create({name}))",
    ]


def generate_manim_code(cmd: dict[str, Any], registry: dict[str, str]) -> list[str]:
    code = cmd.get("code", "")
    name = cmd.get("name")

    registry[name] = name
    return [f"{name} = {code}"]


def transpile_to_manim(ast: dict[str, Any]) -> str:
    metadata = ast.get("metadata", {})
    commands = ast.get("commands", [])
    scale = metadata.get("scale")

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
            obj_code = generate_object_code(obj, registry, scale)
            if obj_code:
                body_lines.append(obj_code)

            position = cmd.get("position")
            if position:
                name = obj.get("name")
                pos_code = generate_position_code(name, position, registry)
                if pos_code:
                    body_lines.append(pos_code)

        if cmd_type == "plot":
            plot_lines = generate_plot_code(cmd, registry)
            body_lines.extend(plot_lines)
            continue

        if cmd_type == "manim":
            manim_lines = generate_manim_code(cmd, registry)
            body_lines.extend(manim_lines)
            continue

        anim_code = generate_animation_code(cmd, registry)
        if anim_code:
            body_lines.append(anim_code)

    for line in body_lines:
        lines.append(f"        {line}")

    return "\n".join(lines)
