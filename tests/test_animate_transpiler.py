"""Tests for animate DSL transpiler that converts AST to manim Python code."""

from cdl_slides.animate_transpiler import (
    generate_animation_code,
    generate_metadata_comments,
    generate_object_code,
    generate_position_code,
    transpile_to_manim,
)


class TestGenerateMetadataComments:
    """Test metadata comment generation."""

    def test_generates_scene_comment(self):
        metadata = {"height": 400, "quality": "high"}
        result = generate_metadata_comments(metadata)
        assert "# scene: AnimateScene" in result

    def test_generates_height_comment(self):
        metadata = {"height": 400, "quality": "high"}
        result = generate_metadata_comments(metadata)
        assert "# height: 400" in result

    def test_generates_quality_comment(self):
        metadata = {"height": 500, "quality": "medium"}
        result = generate_metadata_comments(metadata)
        assert "# quality: medium" in result

    def test_handles_default_values(self):
        metadata = {"height": 500, "quality": "high"}
        result = generate_metadata_comments(metadata)
        assert "# scene: AnimateScene" in result
        assert "# height: 500" in result


class TestGenerateObjectCode:
    """Test object instantiation code generation."""

    def test_equation_object(self):
        obj = {"kind": "equation", "content": "E = mc^2", "name": "eq1"}
        registry = {}
        result = generate_object_code(obj, registry)
        assert result == 'eq1 = MathTex(r"E = mc^2")'
        assert registry["eq1"] == "eq1"

    def test_equation_with_latex(self):
        obj = {"kind": "equation", "content": "\\frac{1}{2}mv^2", "name": "kinetic"}
        registry = {}
        result = generate_object_code(obj, registry)
        assert result == 'kinetic = MathTex(r"\\frac{1}{2}mv^2")'
        assert registry["kinetic"] == "kinetic"

    def test_text_object(self):
        obj = {"kind": "text", "content": "Hello World", "name": "msg"}
        registry = {}
        result = generate_object_code(obj, registry)
        assert result == 'msg = Text("Hello World")'
        assert registry["msg"] == "msg"

    def test_circle_with_color(self):
        obj = {"kind": "circle", "params": {"color": "blue"}, "name": "c1"}
        registry = {}
        result = generate_object_code(obj, registry)
        assert result == "c1 = Circle(color=BLUE)"
        assert registry["c1"] == "c1"

    def test_square_with_color(self):
        obj = {"kind": "square", "params": {"color": "red"}, "name": "sq1"}
        registry = {}
        result = generate_object_code(obj, registry)
        assert result == "sq1 = Square(color=RED)"
        assert registry["sq1"] == "sq1"

    def test_arrow_with_color(self):
        obj = {"kind": "arrow", "params": {"color": "green"}, "name": "arr1"}
        registry = {}
        result = generate_object_code(obj, registry)
        assert result == "arr1 = Arrow(color=GREEN)"
        assert registry["arr1"] == "arr1"

    def test_circle_default_color(self):
        obj = {"kind": "circle", "params": {"color": "white"}, "name": "c2"}
        registry = {}
        result = generate_object_code(obj, registry)
        assert result == "c2 = Circle(color=WHITE)"

    def test_color_mapping_yellow(self):
        obj = {"kind": "circle", "params": {"color": "yellow"}, "name": "c3"}
        registry = {}
        result = generate_object_code(obj, registry)
        assert result == "c3 = Circle(color=YELLOW)"

    def test_color_mapping_orange(self):
        obj = {"kind": "square", "params": {"color": "orange"}, "name": "sq2"}
        registry = {}
        result = generate_object_code(obj, registry)
        assert result == "sq2 = Square(color=ORANGE)"

    def test_color_mapping_black(self):
        obj = {"kind": "arrow", "params": {"color": "black"}, "name": "arr2"}
        registry = {}
        result = generate_object_code(obj, registry)
        assert result == "arr2 = Arrow(color=BLACK)"


class TestGeneratePositionCode:
    """Test position code generation."""

    def test_center_position(self):
        registry = {"eq1": "eq1"}
        position = {"type": "center"}
        result = generate_position_code("eq1", position, registry)
        assert result == "eq1.move_to(ORIGIN)"

    def test_above_position(self):
        registry = {"eq1": "eq1", "eq2": "eq2"}
        position = {"type": "above", "reference": "eq1"}
        result = generate_position_code("eq2", position, registry)
        assert result == "eq2.next_to(eq1, UP)"

    def test_below_position(self):
        registry = {"eq1": "eq1", "eq2": "eq2"}
        position = {"type": "below", "reference": "eq1"}
        result = generate_position_code("eq2", position, registry)
        assert result == "eq2.next_to(eq1, DOWN)"

    def test_left_of_position(self):
        registry = {"eq1": "eq1", "c1": "c1"}
        position = {"type": "left-of", "reference": "eq1"}
        result = generate_position_code("c1", position, registry)
        assert result == "c1.next_to(eq1, LEFT)"

    def test_right_of_position(self):
        registry = {"eq1": "eq1", "c1": "c1"}
        position = {"type": "right-of", "reference": "eq1"}
        result = generate_position_code("c1", position, registry)
        assert result == "c1.next_to(eq1, RIGHT)"

    def test_none_position_returns_empty(self):
        registry = {"eq1": "eq1"}
        result = generate_position_code("eq1", None, registry)
        assert result == ""


class TestGenerateAnimationCode:
    """Test animation code generation."""

    def test_write_animation(self):
        cmd = {"type": "write", "object": {"kind": "equation", "content": "E = mc^2", "name": "eq1"}}
        registry = {"eq1": "eq1"}
        result = generate_animation_code(cmd, registry)
        assert result == "self.play(Write(eq1))"

    def test_create_animation(self):
        cmd = {"type": "create", "object": {"kind": "circle", "params": {"color": "blue"}, "name": "c1"}}
        registry = {"c1": "c1"}
        result = generate_animation_code(cmd, registry)
        assert result == "self.play(Create(c1))"

    def test_fade_in_animation(self):
        cmd = {"type": "fade-in", "target": "c1"}
        registry = {"c1": "c1"}
        result = generate_animation_code(cmd, registry)
        assert result == "self.play(FadeIn(c1))"

    def test_fade_out_animation(self):
        cmd = {"type": "fade-out", "target": "eq1"}
        registry = {"eq1": "eq1"}
        result = generate_animation_code(cmd, registry)
        assert result == "self.play(FadeOut(eq1))"

    def test_transform_animation(self):
        cmd = {"type": "transform", "source": "eq1", "target": "eq2"}
        registry = {"eq1": "eq1", "eq2": "eq2"}
        result = generate_animation_code(cmd, registry)
        assert result == "self.play(Transform(eq1, eq2))"

    def test_wait_animation(self):
        cmd = {"type": "wait", "duration": 0.5}
        registry = {}
        result = generate_animation_code(cmd, registry)
        assert result == "self.wait(0.5)"

    def test_wait_integer_duration(self):
        cmd = {"type": "wait", "duration": 2.0}
        registry = {}
        result = generate_animation_code(cmd, registry)
        assert result == "self.wait(2.0)"


class TestTranspileToManim:
    """Test full transpilation from AST to manim code."""

    def test_simple_transpilation(self):
        ast = {
            "metadata": {"height": 400, "quality": "high"},
            "commands": [
                {
                    "type": "write",
                    "object": {"kind": "equation", "content": "E = mc^2", "name": "eq1"},
                    "position": {"type": "center"},
                }
            ],
        }
        result = transpile_to_manim(ast)

        assert "# scene: AnimateScene" in result
        assert "# height: 400" in result
        assert "class AnimateScene(Scene):" in result
        assert "def construct(self):" in result
        assert 'eq1 = MathTex(r"E = mc^2")' in result
        assert "eq1.move_to(ORIGIN)" in result
        assert "self.play(Write(eq1))" in result

    def test_multiple_commands(self):
        ast = {
            "metadata": {"height": 500, "quality": "high"},
            "commands": [
                {
                    "type": "write",
                    "object": {"kind": "equation", "content": "E = mc^2", "name": "eq1"},
                    "position": {"type": "center"},
                },
                {"type": "wait", "duration": 0.5},
                {"type": "fade-in", "target": "c1"},
            ],
        }
        result = transpile_to_manim(ast)

        assert 'eq1 = MathTex(r"E = mc^2")' in result
        assert "self.play(Write(eq1))" in result
        assert "self.wait(0.5)" in result
        assert "self.play(FadeIn(c1))" in result

    def test_create_shape_with_position(self):
        ast = {
            "metadata": {"height": 400, "quality": "high"},
            "commands": [
                {
                    "type": "write",
                    "object": {"kind": "equation", "content": "x", "name": "eq1"},
                    "position": {"type": "center"},
                },
                {
                    "type": "create",
                    "object": {"kind": "circle", "params": {"color": "blue"}, "name": "c1"},
                    "position": {"type": "right-of", "reference": "eq1"},
                },
            ],
        }
        result = transpile_to_manim(ast)

        assert "c1 = Circle(color=BLUE)" in result
        assert "c1.next_to(eq1, RIGHT)" in result
        assert "self.play(Create(c1))" in result

    def test_transform_animation(self):
        ast = {
            "metadata": {"height": 400, "quality": "high"},
            "commands": [
                {
                    "type": "write",
                    "object": {"kind": "equation", "content": "a", "name": "eq1"},
                    "position": {"type": "center"},
                },
                {
                    "type": "write",
                    "object": {"kind": "equation", "content": "b", "name": "eq2"},
                    "position": {"type": "below", "reference": "eq1"},
                },
                {"type": "transform", "source": "eq1", "target": "eq2"},
            ],
        }
        result = transpile_to_manim(ast)

        assert "self.play(Transform(eq1, eq2))" in result

    def test_full_example_from_spec(self):
        ast = {
            "metadata": {"height": 400, "quality": "high"},
            "commands": [
                {
                    "type": "write",
                    "object": {"kind": "equation", "content": "E = mc^2", "name": "eq1"},
                    "position": {"type": "center"},
                },
                {"type": "wait", "duration": 0.5},
                {"type": "fade-in", "target": "c1"},
            ],
        }
        result = transpile_to_manim(ast)

        # Validate structure
        lines = result.strip().split("\n")
        assert lines[0] == "# scene: AnimateScene"
        assert lines[1] == "# height: 400"
        assert "class AnimateScene(Scene):" in result
        assert "def construct(self):" in result

    def test_empty_commands(self):
        ast = {"metadata": {"height": 500, "quality": "high"}, "commands": []}
        result = transpile_to_manim(ast)

        assert "# scene: AnimateScene" in result
        assert "class AnimateScene(Scene):" in result
        assert "def construct(self):" in result
        assert "pass" in result

    def test_text_object(self):
        ast = {
            "metadata": {"height": 400, "quality": "high"},
            "commands": [
                {
                    "type": "write",
                    "object": {"kind": "text", "content": "Hello World", "name": "t1"},
                    "position": {"type": "center"},
                }
            ],
        }
        result = transpile_to_manim(ast)

        assert 't1 = Text("Hello World")' in result
        assert "self.play(Write(t1))" in result

    def test_square_and_arrow(self):
        ast = {
            "metadata": {"height": 400, "quality": "high"},
            "commands": [
                {
                    "type": "create",
                    "object": {"kind": "square", "params": {"color": "red"}, "name": "sq1"},
                    "position": {"type": "center"},
                },
                {
                    "type": "create",
                    "object": {"kind": "arrow", "params": {"color": "green"}, "name": "arr1"},
                    "position": {"type": "below", "reference": "sq1"},
                },
            ],
        }
        result = transpile_to_manim(ast)

        assert "sq1 = Square(color=RED)" in result
        assert "arr1 = Arrow(color=GREEN)" in result
        assert "arr1.next_to(sq1, DOWN)" in result

    def test_command_without_position(self):
        ast = {
            "metadata": {"height": 400, "quality": "high"},
            "commands": [{"type": "write", "object": {"kind": "equation", "content": "x", "name": "eq1"}}],
        }
        result = transpile_to_manim(ast)

        assert 'eq1 = MathTex(r"x")' in result
        assert "self.play(Write(eq1))" in result
        # Should NOT have move_to since no position specified
        assert "move_to" not in result

    def test_indentation_is_correct(self):
        ast = {
            "metadata": {"height": 400, "quality": "high"},
            "commands": [
                {
                    "type": "write",
                    "object": {"kind": "equation", "content": "x", "name": "eq1"},
                    "position": {"type": "center"},
                }
            ],
        }
        result = transpile_to_manim(ast)

        # Check that construct body is properly indented
        lines = result.split("\n")
        construct_found = False
        for i, line in enumerate(lines):
            if "def construct(self):" in line:
                construct_found = True
                # Next line should be indented with 8 spaces
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if next_line.strip():  # Not empty
                        assert next_line.startswith("        "), f"Expected 8-space indent, got: {next_line!r}"
                break
        assert construct_found, "construct method not found"
