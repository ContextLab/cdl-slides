# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-02-10

### Added

- **Auto-numbered captions**: Poster compiler automatically prepends bold "Figure X." and "Table X." labels to caption elements
- **Hardcoded color palettes**: viridis, plasma, inferno, magma, cividis palettes work in CI environments without matplotlib installed

### Fixed

- Viridis palette lookup for matplotlib 3.9+ (use dict access instead of deprecated `.get()`)
- CI cross-platform failures across macOS, Linux, and Windows
- Caption label isolation: flex layout no longer forces "Figure X." onto its own line when caption is the last child of a poster section

### Changed

- Poster layout refinements: chart-row layout, vertical centering, Figure 2 clipping fix
- Extended Figure 2 caption to multi-line with descriptive text
- Trimmed Limitations box to prevent text overflow

## [1.1.1] - 2026-02-08

### Fixed

- PyPI image links now use absolute URLs for correct rendering on pypi.org

### Added

- PyPI version badge, CI status badge, and download count badge to README

## [1.1.0] - 2026-02-08

### Added

- **Academic poster extension**: ASCII grid layout system with `cdl-slides poster compile` command
  - Per-section callout boxes with color theming
  - Avenir math fonts, balanced layout, styled reference/acknowledgment boxes
  - Rounded-rect emoji backgrounds
- **Inline Chart.js support**: Bar, line, scatter, pie, doughnut, and radar charts via ```` ```chart ```` blocks
  - 14 built-in color palettes (CDL, seaborn, matplotlib, colorblind-friendly, and more)
  - Support for any matplotlib colormap or seaborn palette by name
  - Per-bar colors, axis labels, alpha transparency, italic captions
- **SVG chart renderer**: Matplotlib-based SVG rendering for poster charts (print quality)
- **pyyaml** added as a dependency (required for poster front matter parsing)

### Fixed

- Code block overflow when callout boxes are present on the same slide

## [1.0.0] - 2026-02-06

### Added

- **Animate DSL**: Declarative syntax for creating Manim animations without writing Python code
  - Object commands: `write equation`, `write text`, `create axes`, `create graph`, `plot`, `create circle/square/arrow`
  - Animation commands: `fade-in`, `fade-out`, `draw`, `transform`, `wait`
  - Position modifiers: `at center`, `above/below/left-of/right-of`
  - Metadata options: `height`, `width`, `quality`, `scale`
  - Escape hatch: `manim <python_code> as NAME` for complex animations
- **Flow diagrams**: Simple ```` ```flow ```` syntax for pipeline diagrams with Dartmouth brand colors
- **Smart preprocessing**: Auto-splits long code blocks and tables across slides
- **Callout boxes**: Note, tip, warning, definition, example, and important box styles
- **Two-column layouts**: Flexbox-based column layouts with callout box styling
- **Scale directives**: Manual and automatic font scaling for dense slides
- **Emoji figures**: Styled emoji icons with colored backgrounds
- **Arrow syntax**: Shorthand for styled arrows (`--[80]->`, `--[lg]->`)
- **Syntax highlighting**: Code blocks with line numbers via Pygments
- **Math support**: KaTeX for inline and display equations
- **Cross-platform Marp CLI**: Auto-downloads standalone binary on first use (macOS, Linux, Windows)
- **Multiple output formats**: HTML, PDF, and PPTX

### Features

- Zero-config installation: `pip install cdl-slides` includes everything (Manim, FFmpeg, fonts)
- Bundled fonts: Avenir LT Std, Fira Code, Noto Sans SC
- Bundled ffmpeg via `imageio-ffmpeg` — no system installation required
- GIF caching by content hash for fast re-compilation
- Graceful degradation: animation errors show warning-box instead of crash

### CLI Commands

- `cdl-slides compile` — Compile Markdown to presentation
- `cdl-slides init` — Create new presentation from template
- `cdl-slides version` — Show version and Marp CLI status
- `cdl-slides setup` — Pre-download Marp CLI binary

[1.2.0]: https://github.com/ContextLab/cdl-slides/compare/v1.1.1...v1.2.0
[1.1.1]: https://github.com/ContextLab/cdl-slides/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/ContextLab/cdl-slides/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/ContextLab/cdl-slides/releases/tag/v1.0.0
