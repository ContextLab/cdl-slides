"""Tests for cdl_slides.manim_renderer."""

import pytest

from cdl_slides.manim_renderer import (
    FFMPEG_AVAILABLE,
    MANIM_AVAILABLE,
    PIL_AVAILABLE,
    check_dependencies,
    extract_scene_class_name,
    generate_warning_html,
    get_content_hash,
    parse_manim_metadata,
)


class TestCheckDependencies:
    def test_returns_tuple(self):
        ok, missing = check_dependencies()
        assert isinstance(ok, bool)
        assert isinstance(missing, list)

    def test_missing_is_list_of_strings(self):
        _, missing = check_dependencies()
        for item in missing:
            assert isinstance(item, str)


class TestParseManimMetadata:
    def test_extracts_scene_name(self):
        code = "# scene: MyScene\nclass MyScene(Scene):\n    pass"
        meta = parse_manim_metadata(code)
        assert meta["scene"] == "MyScene"

    def test_extracts_height(self):
        code = "# height: 600\nclass Test(Scene):\n    pass"
        meta = parse_manim_metadata(code)
        assert meta["height"] == 600

    def test_extracts_quality(self):
        code = "# quality: l\nclass Test(Scene):\n    pass"
        meta = parse_manim_metadata(code)
        assert meta["quality"] == "l"

    def test_extracts_fps(self):
        code = "# fps: 30\nclass Test(Scene):\n    pass"
        meta = parse_manim_metadata(code)
        assert meta["fps"] == 30

    def test_strips_metadata_from_code(self):
        code = "# scene: Test\n# height: 500\nclass Test(Scene):\n    pass"
        meta = parse_manim_metadata(code)
        assert "# scene:" not in meta["code"]
        assert "# height:" not in meta["code"]
        assert "class Test" in meta["code"]

    def test_no_metadata_returns_defaults(self):
        code = "class Test(Scene):\n    pass"
        meta = parse_manim_metadata(code)
        assert meta["scene"] is None
        assert meta["height"] == 500
        assert meta["quality"] == "h"
        assert meta["fps"] == 24
        assert meta["code"] == code


class TestExtractSceneClassName:
    def test_finds_scene_subclass(self):
        code = "class MyAnimation(Scene):\n    def construct(self):\n        pass"
        assert extract_scene_class_name(code) == "MyAnimation"

    def test_finds_basescene_subclass(self):
        code = "class MyAnimation(BaseScene):\n    def construct(self):\n        pass"
        assert extract_scene_class_name(code) == "MyAnimation"

    def test_returns_none_for_no_scene(self):
        code = "def foo():\n    pass"
        assert extract_scene_class_name(code) is None

    def test_handles_whitespace_variations(self):
        code = "class  MyScene  (  Scene  ):\n    pass"
        result = extract_scene_class_name(code)
        assert result == "MyScene"


class TestGetContentHash:
    def test_returns_string(self):
        result = get_content_hash("test content")
        assert isinstance(result, str)

    def test_consistent_hash(self):
        content = "class Test(Scene):\n    pass"
        hash1 = get_content_hash(content)
        hash2 = get_content_hash(content)
        assert hash1 == hash2

    def test_different_content_different_hash(self):
        hash1 = get_content_hash("content1")
        hash2 = get_content_hash("content2")
        assert hash1 != hash2


class TestGenerateWarningHtml:
    def test_returns_warning_box(self):
        result = generate_warning_html("Test error")
        assert 'class="warning-box"' in result
        assert "Test error" in result

    def test_escapes_html_characters(self):
        result = generate_warning_html("<script>alert('xss')</script>")
        assert "<script>" not in result
        assert "&lt;script&gt;" in result


class TestDependencyFlags:
    def test_manim_available_is_bool(self):
        assert isinstance(MANIM_AVAILABLE, bool)

    def test_pil_available_is_bool(self):
        assert isinstance(PIL_AVAILABLE, bool)

    def test_ffmpeg_available_is_bool(self):
        assert isinstance(FFMPEG_AVAILABLE, bool)


class TestCreateRenderScript:
    def test_creates_render_script_with_basescene(self):
        from cdl_slides.manim_renderer import create_render_script

        code = "class Test(Scene):\n    def construct(self):\n        pass"
        result = create_render_script(code, "Test")
        assert "from manim import" in result
        assert "class BaseScene(Scene):" in result

    def test_replaces_scene_inheritance_with_basescene(self):
        from cdl_slides.manim_renderer import create_render_script

        code = "class MyAnimation(Scene):\n    def construct(self):\n        pass"
        result = create_render_script(code, "MyAnimation")
        assert "class MyAnimation(BaseScene):" in result
        assert "class MyAnimation(Scene):" not in result

    def test_preserves_existing_basescene_inheritance(self):
        from cdl_slides.manim_renderer import create_render_script

        code = "class MyAnimation(BaseScene):\n    def construct(self):\n        pass"
        result = create_render_script(code, "MyAnimation")
        assert "class MyAnimation(BaseScene):" in result


@pytest.mark.skipif(not MANIM_AVAILABLE, reason="Manim not installed")
class TestManimRendering:
    """Tests that require manim to be installed."""

    def test_create_render_script_imports(self):
        from cdl_slides.manim_renderer import create_render_script

        code = "class Test(Scene):\n    def construct(self):\n        pass"
        result = create_render_script(code, "Test")
        assert "from manim import" in result
        assert "BaseScene" in result
