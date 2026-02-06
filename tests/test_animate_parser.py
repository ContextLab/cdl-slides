"""Tests for animate DSL parser."""

from cdl_slides.animate_parser import (
    parse_animate_block,
    parse_command,
    parse_metadata,
    parse_object_spec,
    parse_position,
)


class TestParseMetadata:
    """Test metadata parsing from animate block header."""

    def test_extracts_height(self):
        lines = ["height: 400", "quality: high"]
        meta = parse_metadata(lines)
        assert meta["height"] == 400

    def test_extracts_quality(self):
        lines = ["height: 500", "quality: medium"]
        meta = parse_metadata(lines)
        assert meta["quality"] == "medium"

    def test_quality_low(self):
        lines = ["quality: low"]
        meta = parse_metadata(lines)
        assert meta["quality"] == "low"

    def test_quality_high(self):
        lines = ["quality: high"]
        meta = parse_metadata(lines)
        assert meta["quality"] == "high"

    def test_defaults_when_empty(self):
        meta = parse_metadata([])
        assert meta["height"] == 500
        assert meta["quality"] == "high"

    def test_defaults_when_no_metadata(self):
        lines = ["write equation"]  # Not metadata, should be ignored
        meta = parse_metadata(lines)
        assert meta["height"] == 500
        assert meta["quality"] == "high"

    def test_ignores_whitespace(self):
        lines = ["  height:  600  ", "  quality:  low  "]
        meta = parse_metadata(lines)
        assert meta["height"] == 600
        assert meta["quality"] == "low"


class TestParsePosition:
    """Test position specification parsing."""

    def test_center(self):
        pos = parse_position("at center")
        assert pos["type"] == "center"

    def test_above(self):
        pos = parse_position("above eq1")
        assert pos["type"] == "above"
        assert pos["reference"] == "eq1"

    def test_below(self):
        pos = parse_position("below myobj")
        assert pos["type"] == "below"
        assert pos["reference"] == "myobj"

    def test_left_of(self):
        pos = parse_position("left-of circle1")
        assert pos["type"] == "left-of"
        assert pos["reference"] == "circle1"

    def test_right_of(self):
        pos = parse_position("right-of eq2")
        assert pos["type"] == "right-of"
        assert pos["reference"] == "eq2"

    def test_empty_returns_none(self):
        pos = parse_position("")
        assert pos is None

    def test_none_input(self):
        pos = parse_position(None)
        assert pos is None


class TestParseObjectSpec:
    """Test object specification parsing."""

    def test_equation_with_name(self):
        spec = parse_object_spec('equation "E = mc^2" as eq1')
        assert spec["kind"] == "equation"
        assert spec["content"] == "E = mc^2"
        assert spec["name"] == "eq1"

    def test_equation_with_latex(self):
        spec = parse_object_spec('equation "\\\\frac{1}{2}mv^2" as kinetic')
        assert spec["kind"] == "equation"
        assert spec["content"] == "\\frac{1}{2}mv^2"
        assert spec["name"] == "kinetic"

    def test_text(self):
        spec = parse_object_spec('text "Hello World" as msg')
        assert spec["kind"] == "text"
        assert spec["content"] == "Hello World"
        assert spec["name"] == "msg"

    def test_circle_with_color(self):
        spec = parse_object_spec("circle color=blue as c1")
        assert spec["kind"] == "circle"
        assert spec["params"]["color"] == "blue"
        assert spec["name"] == "c1"

    def test_square_with_color(self):
        spec = parse_object_spec("square color=red as sq1")
        assert spec["kind"] == "square"
        assert spec["params"]["color"] == "red"
        assert spec["name"] == "sq1"

    def test_arrow_with_color(self):
        spec = parse_object_spec("arrow color=green as arr1")
        assert spec["kind"] == "arrow"
        assert spec["params"]["color"] == "green"
        assert spec["name"] == "arr1"

    def test_circle_default_color(self):
        spec = parse_object_spec("circle as c2")
        assert spec["kind"] == "circle"
        assert spec["params"]["color"] == "white"
        assert spec["name"] == "c2"


class TestParseCommand:
    """Test individual command parsing."""

    def test_write_equation(self):
        cmd = parse_command('write equation "E = mc^2" as eq1 at center')
        assert cmd["type"] == "write"
        assert cmd["object"]["kind"] == "equation"
        assert cmd["object"]["content"] == "E = mc^2"
        assert cmd["object"]["name"] == "eq1"
        assert cmd["position"]["type"] == "center"

    def test_write_equation_with_position(self):
        cmd = parse_command('write equation "x^2" as eq2 below eq1')
        assert cmd["type"] == "write"
        assert cmd["object"]["kind"] == "equation"
        assert cmd["position"]["type"] == "below"
        assert cmd["position"]["reference"] == "eq1"

    def test_write_text(self):
        cmd = parse_command('write text "Hello" as t1 at center')
        assert cmd["type"] == "write"
        assert cmd["object"]["kind"] == "text"
        assert cmd["object"]["content"] == "Hello"

    def test_create_circle(self):
        cmd = parse_command("create circle color=blue as c1 right-of eq2")
        assert cmd["type"] == "create"
        assert cmd["object"]["kind"] == "circle"
        assert cmd["object"]["params"]["color"] == "blue"
        assert cmd["position"]["type"] == "right-of"

    def test_create_square(self):
        cmd = parse_command("create square color=red as s1 at center")
        assert cmd["type"] == "create"
        assert cmd["object"]["kind"] == "square"
        assert cmd["object"]["params"]["color"] == "red"

    def test_create_arrow(self):
        cmd = parse_command("create arrow color=yellow as a1 below s1")
        assert cmd["type"] == "create"
        assert cmd["object"]["kind"] == "arrow"
        assert cmd["object"]["params"]["color"] == "yellow"

    def test_fade_in(self):
        cmd = parse_command("fade-in c1")
        assert cmd["type"] == "fade-in"
        assert cmd["target"] == "c1"

    def test_fade_out(self):
        cmd = parse_command("fade-out eq1")
        assert cmd["type"] == "fade-out"
        assert cmd["target"] == "eq1"

    def test_transform(self):
        cmd = parse_command("transform eq1 -> eq2")
        assert cmd["type"] == "transform"
        assert cmd["source"] == "eq1"
        assert cmd["target"] == "eq2"

    def test_wait(self):
        cmd = parse_command("wait 0.5")
        assert cmd["type"] == "wait"
        assert cmd["duration"] == 0.5

    def test_wait_integer(self):
        cmd = parse_command("wait 2")
        assert cmd["type"] == "wait"
        assert cmd["duration"] == 2.0

    def test_empty_line_returns_none(self):
        cmd = parse_command("")
        assert cmd is None

    def test_comment_line_returns_none(self):
        cmd = parse_command("# this is a comment")
        assert cmd is None

    def test_whitespace_only_returns_none(self):
        cmd = parse_command("   ")
        assert cmd is None


class TestParseAnimateBlock:
    """Test full animate block parsing."""

    def test_simple_block(self):
        content = """height: 400
quality: high

write equation "E = mc^2" as eq1 at center"""

        result = parse_animate_block(content)

        assert result["metadata"]["height"] == 400
        assert result["metadata"]["quality"] == "high"
        assert len(result["commands"]) == 1
        assert result["commands"][0]["type"] == "write"

    def test_multiple_commands(self):
        content = """write equation "E = mc^2" as eq1 at center
wait 0.5
write equation "F = ma" as eq2 below eq1"""

        result = parse_animate_block(content)

        assert len(result["commands"]) == 3
        assert result["commands"][0]["type"] == "write"
        assert result["commands"][1]["type"] == "wait"
        assert result["commands"][2]["type"] == "write"

    def test_full_example(self):
        content = """height: 400
quality: high

write equation "E = mc^2" as eq1 at center
wait 0.5
write equation "\\frac{1}{2}mv^2" as eq2 below eq1
transform eq1 -> eq2
create circle color=blue as c1 right-of eq2
fade-in c1"""

        result = parse_animate_block(content)

        # Check metadata
        assert result["metadata"]["height"] == 400
        assert result["metadata"]["quality"] == "high"

        # Check commands
        assert len(result["commands"]) == 6

        # First command: write equation
        assert result["commands"][0]["type"] == "write"
        assert result["commands"][0]["object"]["kind"] == "equation"
        assert result["commands"][0]["object"]["content"] == "E = mc^2"
        assert result["commands"][0]["object"]["name"] == "eq1"
        assert result["commands"][0]["position"]["type"] == "center"

        # Second: wait
        assert result["commands"][1]["type"] == "wait"
        assert result["commands"][1]["duration"] == 0.5

        # Third: write equation with frac
        assert result["commands"][2]["type"] == "write"
        assert result["commands"][2]["object"]["content"] == "\\frac{1}{2}mv^2"

        # Fourth: transform
        assert result["commands"][3]["type"] == "transform"
        assert result["commands"][3]["source"] == "eq1"
        assert result["commands"][3]["target"] == "eq2"

        # Fifth: create circle
        assert result["commands"][4]["type"] == "create"
        assert result["commands"][4]["object"]["kind"] == "circle"
        assert result["commands"][4]["object"]["params"]["color"] == "blue"

        # Sixth: fade-in
        assert result["commands"][5]["type"] == "fade-in"
        assert result["commands"][5]["target"] == "c1"

    def test_default_metadata(self):
        content = 'write equation "x" as eq1 at center'
        result = parse_animate_block(content)

        assert result["metadata"]["height"] == 500
        assert result["metadata"]["quality"] == "high"

    def test_ignores_blank_lines(self):
        content = """write equation "a" as a at center

wait 1

fade-out a"""

        result = parse_animate_block(content)
        assert len(result["commands"]) == 3

    def test_ignores_comments(self):
        content = """# This is a comment
write equation "x" as x at center
# Another comment
wait 0.5"""

        result = parse_animate_block(content)
        assert len(result["commands"]) == 2

    def test_empty_content(self):
        result = parse_animate_block("")
        assert result["metadata"]["height"] == 500
        assert result["metadata"]["quality"] == "high"
        assert result["commands"] == []

    def test_only_metadata(self):
        content = """height: 600
quality: low"""

        result = parse_animate_block(content)
        assert result["metadata"]["height"] == 600
        assert result["metadata"]["quality"] == "low"
        assert result["commands"] == []
