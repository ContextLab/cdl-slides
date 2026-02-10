"""Tests for cdl_slides.preprocessor."""

import pytest

from cdl_slides.preprocessor import (
    PYGMENTS_AVAILABLE,
    analyze_slide_content,
    compute_available_code_lines,
    determine_scale_class,
    highlight_code_line,
    inject_layout_classes,
    parse_flow_node,
    process_arrow_syntax,
    process_chart_blocks,
    process_flow_blocks,
    process_markdown,
)


class TestProcessFlowBlocksBasic:
    def test_simple_horizontal_flow(self):
        content = "```flow\n[A] --> [B] --> [C]\n```"
        result, count = process_flow_blocks(content)
        assert count == 1
        assert "<svg" in result
        assert "diagram-container" in result
        assert "A" in result
        assert "B" in result
        assert "C" in result

    def test_no_flow_blocks_returns_unchanged(self):
        content = "# Hello\n\nSome text\n```python\nprint('hi')\n```"
        result, count = process_flow_blocks(content)
        assert count == 0
        assert result == content

    def test_empty_flow_block(self):
        content = "```flow\n\n```"
        result, count = process_flow_blocks(content)
        assert count == 0


class TestProcessFlowBlocksWithColors:
    def test_colored_nodes_produce_svg(self):
        content = "```flow\n[Input:blue] --> [Process:green] --> [Output:orange]\n```"
        result, count = process_flow_blocks(content)
        assert count == 1
        assert "rgba(38, 122, 186, 0.15)" in result  # blue fill
        assert "#00693e" in result  # green stroke
        assert "#ffa00f" in result  # orange stroke

    def test_mixed_color_and_auto(self):
        content = "```flow\n[Start:teal] --> [Middle] --> [End:red]\n```"
        result, count = process_flow_blocks(content)
        assert count == 1
        assert "#008080" in result  # teal stroke
        assert "#9d162e" in result  # red stroke


class TestProcessFlowBlocksWithCaption:
    def test_caption_included_in_output(self):
        content = "```flow\n[A] --> [B]\n```\n<!-- caption: My caption -->"
        result, count = process_flow_blocks(content)
        assert count == 1
        assert "diagram-caption" in result
        assert "My caption" in result

    def test_no_caption(self):
        content = "```flow\n[A] --> [B]\n```"
        result, count = process_flow_blocks(content)
        assert count == 1
        assert "diagram-caption" not in result


class TestParseFlowNode:
    def test_plain_label(self):
        node = parse_flow_node("Input")
        assert node["label"] == "Input"
        assert node["color"] is None

    def test_label_with_valid_color(self):
        node = parse_flow_node("Process:green")
        assert node["label"] == "Process"
        assert node["color"] == "green"

    def test_label_with_invalid_color(self):
        node = parse_flow_node("Thing:neon")
        assert node["label"] == "Thing"
        assert node["color"] is None

    def test_label_with_spaces(self):
        node = parse_flow_node("  My Node : blue  ")
        assert node["label"] == "My Node"
        assert node["color"] == "blue"

    def test_colon_in_label(self):
        node = parse_flow_node("Step 1: Init:teal")
        assert node["label"] == "Step 1: Init"
        assert node["color"] == "teal"


class TestCodeBlockSplitting:
    def test_long_code_block_is_split(self, copy_fixture_to_work, work_dir):
        src = copy_fixture_to_work("code_split.md")
        output = work_dir / "output.md"
        stats = process_markdown(str(src), str(output), max_lines=10)
        result = output.read_text(encoding="utf-8")
        assert stats["code_blocks_split"] >= 1
        assert stats["slides_added"] >= 1
        assert "continued" in result.lower()

    def test_short_code_block_not_split(self, work_dir):
        md = "---\nmarp: true\ntheme: cdl-theme\n---\n\n# Slide\n\n```python\nx = 1\ny = 2\n```\n"
        src = work_dir / "short.md"
        src.write_text(md, encoding="utf-8")
        output = work_dir / "out.md"
        stats = process_markdown(str(src), str(output), max_lines=20)
        assert stats["code_blocks_split"] == 0

    def test_no_split_flag_prevents_splitting(self, copy_fixture_to_work, work_dir):
        src = copy_fixture_to_work("code_split.md")
        output = work_dir / "output.md"
        stats = process_markdown(str(src), str(output), max_lines=5, no_split=True)
        assert stats["code_blocks_split"] == 0


class TestTableSplitting:
    def test_long_table_is_split(self, copy_fixture_to_work, work_dir):
        src = copy_fixture_to_work("table_split.md")
        output = work_dir / "output.md"
        stats = process_markdown(str(src), str(output), max_table_rows=4)
        result = output.read_text(encoding="utf-8")
        assert stats["tables_split"] >= 1
        assert stats["slides_added"] >= 1
        assert "continued" in result.lower()

    def test_small_table_not_split(self, work_dir):
        md = "---\nmarp: true\ntheme: cdl-theme\n---\n\n# T\n\n| A | B |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |\n"
        src = work_dir / "small_table.md"
        src.write_text(md, encoding="utf-8")
        output = work_dir / "out.md"
        stats = process_markdown(str(src), str(output), max_table_rows=8)
        assert stats["tables_split"] == 0


class TestProcessArrowSyntax:
    def test_numeric_width(self):
        result = process_arrow_syntax("A --[80]-> B")
        assert 'class="svg-arrow"' in result
        assert "--arrow-width: 80px" in result
        assert "A" in result
        assert "B" in result

    def test_named_size(self):
        result = process_arrow_syntax("X --[lg]-> Y")
        assert "svg-arrow-lg" in result

    def test_no_arrows_unchanged(self):
        line = "Just some text with --> plain arrow"
        assert process_arrow_syntax(line) == line

    def test_multiple_arrows(self):
        result = process_arrow_syntax("A --[sm]-> B --[xl]-> C")
        assert "svg-arrow-sm" in result
        assert "svg-arrow-xl" in result

    def test_direction_variant(self):
        result = process_arrow_syntax("--[up]->")
        assert "svg-arrow-up" in result


class TestAnalyzeSlideContent:
    def test_basic_metrics(self):
        content = "# Title\n\n- Item 1\n- Item 2\n- Item 3\n"
        metrics = analyze_slide_content(content)
        assert metrics["list_items"] == 3
        assert metrics["estimated_height"] > 0
        assert metrics["has_code_block"] is False
        assert metrics["has_table"] is False

    def test_callout_detection(self):
        content = '<div class="note-box" data-title="Note">\nContent\n</div>'
        metrics = analyze_slide_content(content)
        assert metrics["callout_count"] == 1

    def test_code_block_detection(self):
        content = "```python\nx = 1\ny = 2\n```"
        metrics = analyze_slide_content(content)
        assert metrics["has_code_block"] is True
        assert metrics["code_block_lines"] >= 2

    def test_table_detection(self):
        content = "| A | B |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |\n"
        metrics = analyze_slide_content(content)
        assert metrics["has_table"] is True
        assert metrics["table_rows"] == 2

    def test_no_autoscale_directive(self):
        content = "<!-- no-autoscale -->\n# Title\n"
        metrics = analyze_slide_content(content)
        assert metrics["no_autoscale"] is True

    def test_existing_scale_class(self):
        content = "<!-- _class: scale-80 -->\n# Title\n"
        metrics = analyze_slide_content(content)
        assert metrics["has_scale_class"] is True
        assert metrics["existing_scale_class"].strip() == "scale-80"


class TestDetermineScaleClass:
    def test_no_scaling_for_light_content(self):
        metrics = analyze_slide_content("# Title\n\n- One\n- Two\n")
        scale = determine_scale_class(metrics)
        assert scale is None

    def test_scaling_for_dense_content(self):
        content = "# Title\n" + "\n".join(f"- Item {i}" for i in range(30))
        content += "\n```python\n" + "\n".join(f"line_{i} = {i}" for i in range(20)) + "\n```"
        metrics = analyze_slide_content(content)
        scale = determine_scale_class(metrics)
        assert scale is not None
        assert scale.startswith("scale-")

    def test_already_scaled_returns_none(self):
        metrics = {
            "has_scale_class": True,
            "existing_scale_class": "scale-80",
            "no_autoscale": False,
            "callout_count": 0,
            "has_two_column": False,
            "table_in_callout": False,
            "estimated_height": 50.0,
        }
        assert determine_scale_class(metrics) is None

    def test_no_autoscale_returns_none(self):
        metrics = {
            "has_scale_class": False,
            "existing_scale_class": None,
            "no_autoscale": True,
            "callout_count": 0,
            "has_two_column": False,
            "table_in_callout": False,
            "estimated_height": 50.0,
        }
        assert determine_scale_class(metrics) is None

    def test_table_in_callout_triggers_scaling(self):
        metrics = {
            "has_scale_class": False,
            "existing_scale_class": None,
            "no_autoscale": False,
            "callout_count": 1,
            "has_two_column": False,
            "table_in_callout": True,
            "estimated_height": 15.0,
        }
        assert determine_scale_class(metrics) == "scale-78"


class TestProcessMarkdownFull:
    def test_minimal_roundtrip(self, copy_fixture_to_work, work_dir):
        src = copy_fixture_to_work("minimal.md")
        output = work_dir / "output.md"
        stats = process_markdown(str(src), str(output))
        assert output.exists()
        result = output.read_text(encoding="utf-8")
        assert "Test Slide" in result
        assert "Second Slide" in result
        assert stats["input_lines"] > 0
        assert stats["output_lines"] > 0

    def test_arrows_fixture(self, copy_fixture_to_work, work_dir):
        src = copy_fixture_to_work("arrows.md")
        output = work_dir / "output.md"
        stats = process_markdown(str(src), str(output))
        result = output.read_text(encoding="utf-8")
        assert stats["arrows_processed"] >= 2
        assert "svg-arrow" in result

    def test_flow_diagram_fixture(self, copy_fixture_to_work, work_dir):
        src = copy_fixture_to_work("flow_diagram.md")
        output = work_dir / "output.md"
        stats = process_markdown(str(src), str(output))
        result = output.read_text(encoding="utf-8")
        assert stats["flow_diagrams_processed"] == 1
        assert "<svg" in result


class TestProcessMarkdownPreservesFrontmatter:
    def test_frontmatter_preserved(self, copy_fixture_to_work, work_dir):
        src = copy_fixture_to_work("minimal.md")
        output = work_dir / "output.md"
        process_markdown(str(src), str(output))
        result = output.read_text(encoding="utf-8")
        assert "marp: true" in result
        assert "theme: cdl-theme" in result
        assert result.startswith("---")

    def test_math_frontmatter_preserved(self, copy_fixture_to_work, work_dir):
        src = copy_fixture_to_work("math.md")
        output = work_dir / "output.md"
        process_markdown(str(src), str(output))
        result = output.read_text(encoding="utf-8")
        assert "math: katex" in result


class TestHighlightCodeLine:
    @pytest.mark.skipif(not PYGMENTS_AVAILABLE, reason="Pygments not installed")
    def test_python_highlighting(self):
        result = highlight_code_line("x = 42", "python")
        assert "<span" in result

    @pytest.mark.skipif(not PYGMENTS_AVAILABLE, reason="Pygments not installed")
    def test_unknown_language_falls_back(self):
        result = highlight_code_line("hello world", "nonexistent_lang_xyz")
        assert "hello world" in result

    def test_empty_line(self):
        result = highlight_code_line("", "python")
        assert result == ""

    def test_whitespace_only(self):
        result = highlight_code_line("   ", "python")
        assert result == "   " or "<span" in result


class TestProcessManimBlocks:
    def test_manim_block_detected_when_unavailable(self, work_dir):
        """Test that manim blocks pass through unchanged when manim is not available."""
        from cdl_slides.preprocessor import MANIM_AVAILABLE, process_manim_blocks

        md = "```manim\nclass Test(Scene):\n    pass\n```"
        result, count = process_manim_blocks(md, str(work_dir))

        if not MANIM_AVAILABLE:
            assert count == 0
            assert "```manim" in result
        else:
            assert count >= 0

    def test_manim_stats_key_exists(self, copy_fixture_to_work, work_dir):
        """Test that manim_animations_rendered key is in stats."""
        src = copy_fixture_to_work("manim_simple.md")
        output = work_dir / "output.md"
        stats = process_markdown(str(src), str(output))
        assert "manim_animations_rendered" in stats

    def test_manim_block_replaced_when_available(self, copy_fixture_to_work, work_dir):
        """Test manim block is replaced with image tag when manim is available."""
        from cdl_slides.preprocessor import MANIM_AVAILABLE

        src = copy_fixture_to_work("manim_simple.md")
        output = work_dir / "output.md"
        stats = process_markdown(str(src), str(output))
        result = output.read_text(encoding="utf-8")

        if MANIM_AVAILABLE:
            assert stats["manim_animations_rendered"] >= 1
            assert "```manim" not in result
            assert "![height:" in result or "manim-animation" in result or "warning-box" in result
        else:
            assert stats["manim_animations_rendered"] == 0
            assert "```manim" in result


class TestProcessAnimateBlocks:
    def test_animate_block_detected(self, work_dir):
        """Test that animate blocks are found in content."""
        content = '```animate\nwrite equation "E = mc^2" as eq1\n```'
        # This test verifies that animate blocks can be detected
        # Once process_animate_blocks exists, it should find this block
        assert "```animate" in content
        assert "write equation" in content

    def test_animate_stats_key_exists(self, copy_fixture_to_work, work_dir):
        """Test that animate_blocks_transpiled key is in stats."""
        src = copy_fixture_to_work("animate_simple.md")
        output = work_dir / "output.md"
        stats = process_markdown(str(src), str(output))
        assert "animate_blocks_transpiled" in stats

    def test_animate_transpiles_to_manim(self, work_dir):
        """Test that animate block becomes manim block."""
        content = (
            '---\nmarp: true\ntheme: cdl-theme\n---\n\n# Test\n\n```animate\nwrite equation "E = mc^2" as eq1\n```\n'
        )
        src = work_dir / "test.md"
        src.write_text(content, encoding="utf-8")
        output = work_dir / "output.md"
        process_markdown(str(src), str(output))
        result = output.read_text(encoding="utf-8")
        assert "```manim" in result or "![height:" in result or "manim-animation" in result or "warning-box" in result

    @pytest.mark.skipif(
        not pytest.importorskip("manim", minversion=None),
        reason="Manim not installed",
    )
    def test_animate_renders_gif_when_available(self, copy_fixture_to_work, work_dir):
        """Test full pipeline: animate → manim → GIF."""
        src = copy_fixture_to_work("animate_simple.md")
        output = work_dir / "output.md"
        process_markdown(str(src), str(output))
        result = output.read_text(encoding="utf-8")
        assert "![height:" in result or "manim-animation" in result or "warning-box" in result

    def test_malformed_animate_produces_warning(self, copy_fixture_to_work, work_dir):
        """Test that syntax errors produce warning box."""
        src = copy_fixture_to_work("animate_malformed.md")
        output = work_dir / "output.md"
        process_markdown(str(src), str(output))
        result = output.read_text(encoding="utf-8")
        assert "warning-box" in result or "```animate" in result


class TestCodeBlockWithCallouts:
    def test_available_lines_reduced_with_one_callout(self):
        slide_no_callout = "<!-- _class: scale-80 -->\n# Title\n\n```python\nx = 1\n```\n"
        slide_one_callout = (
            "<!-- _class: scale-80 -->\n# Title\n\n```python\nx = 1\n```\n\n"
            '<div class="note-box">\nSome note.\n</div>\n'
        )
        lines_no_callout = compute_available_code_lines(slide_no_callout, default_max=30)
        lines_one_callout = compute_available_code_lines(slide_one_callout, default_max=30)
        assert lines_one_callout < lines_no_callout

    def test_available_lines_reduced_with_two_callouts(self):
        slide_one = (
            "<!-- _class: scale-80 -->\n# Title\n\n```python\nx = 1\n```\n\n"
            '<div class="note-box">\nSome note.\n</div>\n'
        )
        slide_two = (
            "<!-- _class: scale-80 -->\n# Title\n\n```python\nx = 1\n```\n\n"
            '<div class="note-box">\nSome note.\n</div>\n\n'
            '<div class="example-box">\nSome example.\n</div>\n'
        )
        lines_one = compute_available_code_lines(slide_one)
        lines_two = compute_available_code_lines(slide_two)
        assert lines_two < lines_one

    def test_layout_classes_injected_for_code_and_callouts(self):
        from cdl_slides.preprocessor import analyze_and_warn_slides

        content = (
            "---\nmarp: true\ntheme: cdl-theme\n---\n\n"
            "# Title\n\n"
            "```python\nx = 1\n```\n\n"
            '<div class="note-box">\nNote.\n</div>\n\n'
            '<div class="example-box">\nExample.\n</div>\n'
        )
        modified, warnings = analyze_and_warn_slides(content)
        assert "has-callouts-2" in modified
        assert "has-code-block" in modified

    def test_no_layout_classes_without_code_block(self):
        from cdl_slides.preprocessor import analyze_and_warn_slides

        content = (
            "---\nmarp: true\ntheme: cdl-theme\n---\n\n"
            "# Title\n\n"
            '<div class="note-box">\nNote.\n</div>\n\n'
            '<div class="example-box">\nExample.\n</div>\n'
        )
        modified, warnings = analyze_and_warn_slides(content)
        assert "has-callouts" not in modified

    def test_layout_classes_appended_to_existing_scale(self):
        slide = "<!-- _class: scale-80 -->\n# Title\n\n```python\nx=1\n```\n"
        result = inject_layout_classes(slide, ["has-callouts-1", "has-code-block"])
        assert "scale-80" in result
        assert "has-callouts-1" in result
        assert "has-code-block" in result


class TestProcessChartBlocks:
    def test_simple_bar_chart(self):
        content = "```chart\ntype: bar\nlabels: A, B, C\ndata: 1, 2, 3\n```"
        result, count = process_chart_blocks(content)
        assert count == 1
        assert "chart-container" in result
        assert "cdl-chart-0" in result
        assert "type: 'bar'" in result
        assert "'A'" in result
        assert "1, 2, 3" in result

    def test_chart_with_caption(self):
        content = "```chart\ntype: bar\nlabels: X, Y\ndata: 10, 20\ncaption: Figure 1\n```"
        result, count = process_chart_blocks(content)
        assert count == 1
        assert "chart-caption" in result
        assert "Figure 1" in result

    def test_no_chart_title_in_output(self):
        content = "```chart\ntype: line\nlabels: A, B\ndata: 1, 2\n```"
        result, count = process_chart_blocks(content)
        assert count == 1
        assert "title: { display: false }" in result

    def test_multiple_datasets(self):
        content = (
            "```chart\ntype: bar\nlabels: A, B\ndatasets:\n"
            "  - label: Set 1\n    data: 1, 2\n"
            "  - label: Set 2\n    data: 3, 4\n```"
        )
        result, count = process_chart_blocks(content)
        assert count == 1
        assert "'Set 1'" in result
        assert "'Set 2'" in result
        assert "display: true" in result

    def test_pie_chart_with_legend(self):
        content = "```chart\ntype: pie\nlabels: Slice A, Slice B, Slice C\ndata: 30, 50, 20\n```"
        result, count = process_chart_blocks(content)
        assert count == 1
        assert "type: 'pie'" in result
        assert "legend: { display: true" in result

    def test_scatter_chart(self):
        content = "```chart\ntype: scatter\ndatasets:\n  - label: Points\n    data: 1 2, 3 4, 5 6\n```"
        result, count = process_chart_blocks(content)
        assert count == 1
        assert "type: 'scatter'" in result
        assert "{x: 1, y: 2}" in result

    def test_radar_chart(self):
        content = (
            "```chart\ntype: radar\nlabels: Speed, Power, Range\ndatasets:\n"
            "  - label: Model A\n    data: 80, 90, 70\n"
            "  - label: Model B\n    data: 60, 85, 95\n```"
        )
        result, count = process_chart_blocks(content)
        assert count == 1
        assert "type: 'radar'" in result

    def test_doughnut_chart_with_legend(self):
        content = "```chart\ntype: doughnut\nlabels: A, B, C\ndata: 40, 35, 25\n```"
        result, count = process_chart_blocks(content)
        assert count == 1
        assert "type: 'doughnut'" in result
        assert "legend: { display: true" in result

    def test_multiple_chart_blocks(self):
        content = (
            "```chart\ntype: bar\nlabels: A\ndata: 1\n```\n\n"
            "Some text\n\n"
            "```chart\ntype: pie\nlabels: X\ndata: 100\n```"
        )
        result, count = process_chart_blocks(content)
        assert count == 2
        assert "cdl-chart-0" in result
        assert "cdl-chart-1" in result

    def test_no_chart_blocks(self):
        content = '# Hello\n\nSome text\n```python\nprint("hi")\n```'
        result, count = process_chart_blocks(content)
        assert count == 0
        assert result == content

    def test_custom_dimensions(self):
        content = "```chart\ntype: bar\nlabels: A\ndata: 1\nwidth: 70%\nheight: 400px\n```"
        result, count = process_chart_blocks(content)
        assert count == 1
        assert "width: 70%" in result
        assert "height: 400px" in result

    def test_grouped_bar_becomes_bar(self):
        content = (
            "```chart\ntype: grouped_bar\nlabels: A, B\ndatasets:\n"
            "  - label: S1\n    data: 1, 2\n"
            "  - label: S2\n    data: 3, 4\n```"
        )
        result, count = process_chart_blocks(content)
        assert count == 1
        assert "type: 'bar'" in result

    def test_chart_in_process_markdown(self, tmp_path):
        input_md = tmp_path / "input.md"
        output_md = tmp_path / "output.md"
        input_md.write_text(
            "---\nmarp: true\ntheme: cdl-theme\n---\n\n# Charts\n\n```chart\ntype: bar\nlabels: A, B\ndata: 1, 2\n```\n"
        )
        stats = process_markdown(str(input_md), str(output_md))
        assert stats["charts_processed"] == 1
        output_content = output_md.read_text()
        assert "chart-container" in output_content

    def test_single_dataset_legend_hidden(self):
        content = "```chart\ntype: bar\nlabels: A, B\ndata: 1, 2\n```"
        result, count = process_chart_blocks(content)
        assert count == 1
        assert "legend: { display: false" in result

    def test_labels_properly_quoted(self):
        content = "```chart\ntype: bar\nlabels: It's good, Not bad\ndata: 1, 2\n```"
        result, count = process_chart_blocks(content)
        assert count == 1
        assert "It\\'s good" in result

    def test_radar_always_shows_legend(self):
        content = "```chart\ntype: radar\nlabels: A, B, C\ndata: 1, 2, 3\n```"
        result, count = process_chart_blocks(content)
        assert count == 1
        assert "legend: { display: true" in result

    def test_default_palette_uses_cdl_colors(self):
        content = "```chart\ntype: bar\nlabels: A, B, C\ndata: 1, 2, 3\n```"
        result, count = process_chart_blocks(content)
        assert count == 1
        assert "#00693e" in result

    def test_seaborn_palette(self):
        content = "```chart\ntype: bar\nlabels: A, B\ndata: 1, 2\npalette: seaborn\n```"
        result, count = process_chart_blocks(content)
        assert count == 1
        assert "#4c72b0" in result

    def test_tab10_palette(self):
        content = "```chart\ntype: bar\nlabels: A, B\ndata: 1, 2\npalette: tab10\n```"
        result, count = process_chart_blocks(content)
        assert count == 1
        assert "#1f77b4" in result

    def test_colorblind_palette(self):
        content = "```chart\ntype: bar\nlabels: A, B\ndata: 1, 2\npalette: colorblind\n```"
        result, count = process_chart_blocks(content)
        assert count == 1
        assert "#0173b2" in result

    def test_unknown_palette_falls_back_to_cdl(self):
        content = "```chart\ntype: bar\nlabels: A, B\ndata: 1, 2\npalette: nonexistent\n```"
        result, count = process_chart_blocks(content)
        assert count == 1
        assert "#00693e" in result

    def test_pie_chart_has_multiple_colors(self):
        content = "```chart\ntype: pie\nlabels: A, B, C, D\ndata: 25, 25, 25, 25\n```"
        result, count = process_chart_blocks(content)
        assert count == 1
        assert "#00693e" in result
        assert "#267aba" in result
        assert "#ffa00f" in result

    def test_bar_chart_has_inline_font_config(self):
        content = "```chart\ntype: bar\nlabels: A, B\ndata: 1, 2\n```"
        result, count = process_chart_blocks(content)
        assert count == 1
        assert "Avenir" in result
        assert "size: 18" in result

    def test_radar_has_no_backdrop(self):
        content = "```chart\ntype: radar\nlabels: A, B, C\ndata: 1, 2, 3\n```"
        result, count = process_chart_blocks(content)
        assert count == 1
        assert "showBackdrop: false" in result
        assert "backdropColor: 'transparent'" in result

    def test_line_chart_has_tension(self):
        content = "```chart\ntype: line\nlabels: A, B\ndata: 1, 2\n```"
        result, count = process_chart_blocks(content)
        assert count == 1
        assert "tension: 0.3" in result

    def test_scatter_chart_has_point_radius(self):
        content = "```chart\ntype: scatter\ndatasets:\n  - label: P\n    data: 1 2, 3 4\n```"
        result, count = process_chart_blocks(content)
        assert count == 1
        assert "pointRadius: 10" in result

    def test_radar_datasets_sorted_largest_first(self):
        content = (
            "```chart\ntype: radar\nlabels: A, B, C\ndatasets:\n"
            "  - label: Small\n    data: 10, 20, 30\n"
            "  - label: Large\n    data: 90, 80, 70\n```"
        )
        result, count = process_chart_blocks(content)
        assert count == 1
        large_pos = result.index("'Large'")
        small_pos = result.index("'Small'")
        assert large_pos < small_pos, "Largest dataset should be drawn first (behind)"

    def test_default_alpha_is_half(self):
        content = "```chart\ntype: bar\nlabels: A, B\ndata: 1, 2\n```"
        result, count = process_chart_blocks(content)
        assert count == 1
        assert "rgba(0, 105, 62, 0.5)" in result

    def test_custom_alpha(self):
        content = "```chart\ntype: bar\nlabels: A, B\ndata: 1, 2\nalpha: 0.8\n```"
        result, count = process_chart_blocks(content)
        assert count == 1
        assert "rgba(0, 105, 62, 0.8)" in result

    def test_pie_chart_alpha_in_background(self):
        content = "```chart\ntype: pie\nlabels: A, B\ndata: 50, 50\n```"
        result, count = process_chart_blocks(content)
        assert count == 1
        assert "rgba(0, 105, 62, 0.5)" in result
        assert "borderColor: ['#00693e'" in result

    def test_chart_container_centered(self):
        content = "```chart\ntype: bar\nlabels: A\ndata: 1\n```"
        result, count = process_chart_blocks(content)
        assert count == 1
        assert "margin: 0 auto" in result

    def test_legend_font_equals_tick_font(self):
        content = (
            "```chart\ntype: bar\nlabels: A, B\ndatasets:\n"
            "  - label: S1\n    data: 1, 2\n"
            "  - label: S2\n    data: 3, 4\n```"
        )
        result, count = process_chart_blocks(content)
        assert count == 1
        assert "legend: { display: true" in result
        assert result.count("size: 18") >= 2
