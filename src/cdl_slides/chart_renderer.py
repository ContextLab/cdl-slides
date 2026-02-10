"""Matplotlib SVG chart renderer for poster output."""

from __future__ import annotations

import io
import re

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("Agg")

from cdl_slides.preprocessor import _get_palette, _parse_chart_block  # noqa: E402

CDL_FONT_FAMILY = "Avenir LT Std"
CDL_FONT_FALLBACKS = ["Avenir", "Avenir Next", "Helvetica Neue", "sans-serif"]
CDL_TEXT_COLOR = "#0a2518"
CDL_GRID_RGBA = (0, 0.412, 0.243, 0.1)
CDL_GRID_DARK_RGBA = (0, 0.412, 0.243, 0.2)

TICK_SIZE = 10
AXIS_TITLE_SIZE = 11
LEGEND_SIZE = 10
POINT_LABEL_SIZE = 12
CAPTION_SIZE = 10


def _hex_to_rgba(hex_color: str, alpha: float) -> tuple:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255
    return (r, g, b, alpha)


def _setup_font():
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = [CDL_FONT_FAMILY] + CDL_FONT_FALLBACKS


def _fig_to_svg(fig: plt.Figure) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="svg", transparent=True, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    svg_str = buf.read().decode("utf-8")
    svg_str = re.sub(r"<\?xml[^>]*\?>", "", svg_str).strip()
    svg_str = re.sub(r"<!DOCTYPE[^>]*>", "", svg_str).strip()
    return svg_str


def _parse_data_values(data_str: str) -> list:
    return [float(v.strip()) for v in data_str.split(",") if v.strip()]


def _parse_scatter_data(data_str: str) -> tuple:
    points = [p.strip() for p in data_str.split(",") if p.strip()]
    xs, ys = [], []
    for point in points:
        parts = point.split()
        if len(parts) >= 2:
            xs.append(float(parts[0]))
            ys.append(float(parts[1]))
    return xs, ys


def render_chart_svg(config: dict) -> str:
    _setup_font()
    chart_type = config["type"]
    if chart_type == "grouped_bar":
        chart_type = "bar"

    renderers = {
        "bar": _render_bar,
        "line": _render_line,
        "scatter": _render_scatter,
        "pie": _render_pie,
        "doughnut": _render_doughnut,
        "radar": _render_radar,
    }

    renderer = renderers.get(chart_type, _render_bar)
    svg = renderer(config)
    return f'<div style="text-align: center; width: 100%;">\n{svg}\n</div>'


def _get_colors(config: dict) -> list:
    chart_type = config["type"]
    if chart_type == "grouped_bar":
        chart_type = "bar"

    n_datasets = len(config["datasets"])
    n_labels = len(config["labels"])
    if chart_type in ("pie", "doughnut"):
        n_colors = n_labels if n_labels > 0 else n_datasets
    elif n_datasets > 1:
        n_colors = n_datasets
    else:
        n_colors = n_labels if n_labels > 0 else 1

    return _get_palette(config.get("palette", "cdl"), n_colors=n_colors)


def _apply_axis_styling(ax, config: dict):
    xlabel = config.get("xlabel", "")
    ylabel = config.get("ylabel", "")

    ax.tick_params(axis="both", labelsize=TICK_SIZE, colors=CDL_TEXT_COLOR)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(CDL_GRID_DARK_RGBA)
    ax.spines["bottom"].set_color(CDL_GRID_DARK_RGBA)
    ax.yaxis.grid(True, color=CDL_GRID_RGBA)
    ax.set_axisbelow(True)

    if xlabel:
        ax.set_xlabel(xlabel, fontsize=AXIS_TITLE_SIZE, color=CDL_TEXT_COLOR)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=AXIS_TITLE_SIZE, color=CDL_TEXT_COLOR)


def _add_caption(fig: plt.Figure, config: dict):
    caption = config.get("caption", "")
    if caption:
        fig.text(0.5, -0.02, caption, ha="center", fontsize=CAPTION_SIZE, color=CDL_TEXT_COLOR)


def _add_legend(ax, config: dict, palette: list):
    chart_type = config["type"]
    always_legend = chart_type in ("pie", "doughnut", "radar")
    show_legend = len(config["datasets"]) > 1 or always_legend
    if show_legend:
        legend = ax.legend(fontsize=LEGEND_SIZE, frameon=False, labelcolor=CDL_TEXT_COLOR)
        if legend:
            legend.get_frame().set_alpha(0)


def _render_bar(config: dict) -> str:
    fig, ax = plt.subplots(figsize=(6, 4))
    palette = _get_colors(config)
    alpha = float(config.get("alpha", 0.5))
    labels = config["labels"]
    datasets = config["datasets"]
    n_datasets = len(datasets)

    if n_datasets <= 1:
        ds = datasets[0]
        data = _parse_data_values(ds["data"]) if isinstance(ds["data"], str) else ds["data"]
        colors = [_hex_to_rgba(palette[i % len(palette)], alpha) for i in range(len(data))]
        edge_colors = [palette[i % len(palette)] for i in range(len(data))]
        ax.bar(labels, data, color=colors, edgecolor=edge_colors, linewidth=1.5)
    else:
        x = np.arange(len(labels))
        width = 0.8 / n_datasets
        for idx, ds in enumerate(datasets):
            data = _parse_data_values(ds["data"]) if isinstance(ds["data"], str) else ds["data"]
            color = _hex_to_rgba(palette[idx % len(palette)], alpha)
            edge = palette[idx % len(palette)]
            offset = (idx - n_datasets / 2 + 0.5) * width
            ax.bar(x + offset, data, width, label=ds.get("label", ""), color=color, edgecolor=edge, linewidth=1.5)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)

    _apply_axis_styling(ax, config)
    _add_legend(ax, config, palette)
    _add_caption(fig, config)
    return _fig_to_svg(fig)


def _render_line(config: dict) -> str:
    fig, ax = plt.subplots(figsize=(6, 4))
    palette = _get_colors(config)
    alpha = float(config.get("alpha", 0.5))
    labels = config["labels"]

    for idx, ds in enumerate(config["datasets"]):
        data = _parse_data_values(ds["data"]) if isinstance(ds["data"], str) else ds["data"]
        color = palette[idx % len(palette)]
        ax.plot(labels, data, color=color, linewidth=2.5, marker="o", markersize=5, label=ds.get("label", ""))
        ax.fill_between(labels, data, alpha=alpha, color=color)

    _apply_axis_styling(ax, config)
    ax.xaxis.grid(True, color=CDL_GRID_RGBA)
    _add_legend(ax, config, palette)
    _add_caption(fig, config)
    return _fig_to_svg(fig)


def _render_scatter(config: dict) -> str:
    fig, ax = plt.subplots(figsize=(6, 4))
    palette = _get_colors(config)
    alpha = float(config.get("alpha", 0.5))

    for idx, ds in enumerate(config["datasets"]):
        xs, ys = _parse_scatter_data(ds["data"]) if isinstance(ds["data"], str) else ([], [])
        color = _hex_to_rgba(palette[idx % len(palette)], alpha)
        edge = palette[idx % len(palette)]
        ax.scatter(xs, ys, c=[color], edgecolors=edge, s=80, linewidths=1.5, label=ds.get("label", ""), zorder=3)

    _apply_axis_styling(ax, config)
    ax.xaxis.grid(True, color=CDL_GRID_RGBA)
    _add_legend(ax, config, palette)
    _add_caption(fig, config)
    return _fig_to_svg(fig)


def _render_pie(config: dict) -> str:
    fig, ax = plt.subplots(figsize=(5, 5))
    palette = _get_colors(config)
    alpha = float(config.get("alpha", 0.5))
    labels = config["labels"]
    ds = config["datasets"][0]
    data = _parse_data_values(ds["data"]) if isinstance(ds["data"], str) else ds["data"]
    colors = [_hex_to_rgba(palette[i % len(palette)], alpha) for i in range(len(data))]
    edge_colors = [palette[i % len(palette)] for i in range(len(data))]

    wedges, _ = ax.pie(data, colors=colors, wedgeprops=dict(edgecolor="white", linewidth=2))
    for w, ec in zip(wedges, edge_colors):
        w.set_edgecolor(ec)

    ax.legend(
        labels,
        fontsize=LEGEND_SIZE,
        frameon=False,
        labelcolor=CDL_TEXT_COLOR,
        loc="center left",
        bbox_to_anchor=(1, 0.5),
    )
    _add_caption(fig, config)
    return _fig_to_svg(fig)


def _render_doughnut(config: dict) -> str:
    fig, ax = plt.subplots(figsize=(5, 5))
    palette = _get_colors(config)
    alpha = float(config.get("alpha", 0.5))
    labels = config["labels"]
    ds = config["datasets"][0]
    data = _parse_data_values(ds["data"]) if isinstance(ds["data"], str) else ds["data"]
    colors = [_hex_to_rgba(palette[i % len(palette)], alpha) for i in range(len(data))]
    edge_colors = [palette[i % len(palette)] for i in range(len(data))]

    wedges, _ = ax.pie(data, colors=colors, wedgeprops=dict(width=0.4, edgecolor="white", linewidth=2))
    for w, ec in zip(wedges, edge_colors):
        w.set_edgecolor(ec)

    ax.legend(
        labels,
        fontsize=LEGEND_SIZE,
        frameon=False,
        labelcolor=CDL_TEXT_COLOR,
        loc="center left",
        bbox_to_anchor=(1, 0.5),
    )
    _add_caption(fig, config)
    return _fig_to_svg(fig)


def _render_radar(config: dict) -> str:
    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    palette = _get_colors(config)
    alpha = float(config.get("alpha", 0.5))
    labels = config["labels"]
    n = len(labels)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]

    datasets = config["datasets"]
    if len(datasets) > 1:

        def _data_sum(ds):
            raw = ds["data"]
            if isinstance(raw, str):
                try:
                    return sum(float(v.strip()) for v in raw.split(",") if v.strip())
                except ValueError:
                    return 0
            return 0

        datasets = sorted(datasets, key=_data_sum, reverse=True)

    for idx, ds in enumerate(datasets):
        data = _parse_data_values(ds["data"]) if isinstance(ds["data"], str) else ds["data"]
        data_closed = data + data[:1]
        color = palette[idx % len(palette)]
        fill_color = _hex_to_rgba(color, alpha)
        ax.plot(angles, data_closed, color=color, linewidth=2, label=ds.get("label", ""))
        ax.fill(angles, data_closed, color=fill_color)

    ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontsize=POINT_LABEL_SIZE, color=CDL_TEXT_COLOR)
    ax.tick_params(axis="y", labelsize=TICK_SIZE, colors=CDL_TEXT_COLOR)
    ax.grid(color=CDL_GRID_RGBA)
    ax.spines["polar"].set_color(CDL_GRID_DARK_RGBA)
    ax.set_facecolor("none")

    ax.legend(
        fontsize=LEGEND_SIZE, frameon=False, labelcolor=CDL_TEXT_COLOR, loc="upper right", bbox_to_anchor=(1.3, 1.1)
    )
    _add_caption(fig, config)
    return _fig_to_svg(fig)


def process_poster_chart_blocks(content: str) -> tuple:
    """Process ```chart code blocks and convert them to inline SVG for posters."""
    chart_pattern = r"```chart\n(.*?)```"
    charts_processed = 0

    def replace_chart_block(match):
        nonlocal charts_processed
        block_content = match.group(1)
        config = _parse_chart_block(block_content)

        if not config["datasets"]:
            return match.group(0)

        charts_processed += 1
        return render_chart_svg(config)

    processed = re.sub(chart_pattern, replace_chart_block, content, flags=re.DOTALL)
    return processed, charts_processed
