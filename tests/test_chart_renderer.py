"""Tests for the matplotlib SVG chart renderer used in posters."""

import pytest

pytest.importorskip("matplotlib", reason="matplotlib required for chart renderer tests")

from cdl_slides.chart_renderer import process_poster_chart_blocks, render_chart_svg  # noqa: E402
from cdl_slides.preprocessor import _parse_chart_block  # noqa: E402


class TestRenderChartSvg:
    def test_bar_chart_produces_svg(self):
        config = _parse_chart_block("type: bar\nlabels: A, B, C\ndata: 10, 20, 30")
        result = render_chart_svg(config)
        assert "<svg" in result
        assert "</svg>" in result

    def test_line_chart_produces_svg(self):
        config = _parse_chart_block("type: line\nlabels: A, B\ndata: 1, 2")
        result = render_chart_svg(config)
        assert "<svg" in result

    def test_scatter_chart_produces_svg(self):
        config = _parse_chart_block("type: scatter\ndatasets:\n  - label: Points\n    data: 1 2, 3 4, 5 6")
        result = render_chart_svg(config)
        assert "<svg" in result

    def test_pie_chart_produces_svg(self):
        config = _parse_chart_block("type: pie\nlabels: A, B, C\ndata: 30, 50, 20")
        result = render_chart_svg(config)
        assert "<svg" in result

    def test_doughnut_chart_produces_svg(self):
        config = _parse_chart_block("type: doughnut\nlabels: A, B\ndata: 60, 40")
        result = render_chart_svg(config)
        assert "<svg" in result

    def test_radar_chart_produces_svg(self):
        config = _parse_chart_block(
            "type: radar\nlabels: A, B, C\ndatasets:\n"
            "  - label: Set 1\n    data: 80, 90, 70\n"
            "  - label: Set 2\n    data: 60, 85, 95"
        )
        result = render_chart_svg(config)
        assert "<svg" in result

    def test_svg_wrapped_in_centered_div(self):
        config = _parse_chart_block("type: bar\nlabels: A\ndata: 10")
        result = render_chart_svg(config)
        assert "text-align: center" in result
        assert "width: 100%" in result

    def test_caption_in_svg(self):
        config = _parse_chart_block("type: bar\nlabels: A, B\ndata: 1, 2\ncaption: My caption")
        result = render_chart_svg(config)
        assert "My caption" in result

    def test_xlabel_in_svg(self):
        config = _parse_chart_block("type: bar\nlabels: A, B\ndata: 1, 2\nxlabel: Categories")
        result = render_chart_svg(config)
        assert "Categories" in result

    def test_ylabel_in_svg(self):
        config = _parse_chart_block("type: bar\nlabels: A, B\ndata: 1, 2\nylabel: Count")
        result = render_chart_svg(config)
        assert "Count" in result

    def test_viridis_palette_in_svg(self):
        config = _parse_chart_block("type: bar\nlabels: A, B, C\ndata: 1, 2, 3\npalette: viridis")
        result = render_chart_svg(config)
        assert "<svg" in result

    def test_grouped_bar_becomes_bar(self):
        config = _parse_chart_block(
            "type: grouped_bar\nlabels: A, B\ndatasets:\n  - label: S1\n    data: 1, 2\n  - label: S2\n    data: 3, 4"
        )
        result = render_chart_svg(config)
        assert "<svg" in result

    def test_no_xml_declaration_in_svg(self):
        config = _parse_chart_block("type: bar\nlabels: A\ndata: 10")
        result = render_chart_svg(config)
        assert "<?xml" not in result

    def test_multi_dataset_bar(self):
        config = _parse_chart_block(
            "type: bar\nlabels: A, B\ndatasets:\n  - label: S1\n    data: 1, 2\n  - label: S2\n    data: 3, 4"
        )
        result = render_chart_svg(config)
        assert "<svg" in result
        assert "S1" in result
        assert "S2" in result


class TestProcessPosterChartBlocks:
    def test_replaces_chart_block_with_svg(self):
        content = "```chart\ntype: bar\nlabels: A, B\ndata: 1, 2\n```"
        result, count = process_poster_chart_blocks(content)
        assert count == 1
        assert "<svg" in result
        assert "```chart" not in result

    def test_multiple_chart_blocks(self):
        content = (
            "```chart\ntype: bar\nlabels: A\ndata: 1\n```\n\n"
            "Some text\n\n"
            "```chart\ntype: pie\nlabels: X, Y\ndata: 50, 50\n```"
        )
        result, count = process_poster_chart_blocks(content)
        assert count == 2

    def test_no_chart_blocks_returns_original(self):
        content = "# Hello\n\nSome text"
        result, count = process_poster_chart_blocks(content)
        assert count == 0
        assert result == content

    def test_empty_dataset_not_replaced(self):
        content = "```chart\ntype: bar\n```"
        result, count = process_poster_chart_blocks(content)
        assert count == 0
