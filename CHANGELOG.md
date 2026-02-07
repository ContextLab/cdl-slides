# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

- Zero-config installation: `pip install cdl-slides`
- Optional animation support: `pip install cdl-slides[animations]`
- Bundled fonts: Avenir LT Std, Fira Code, Noto Sans SC
- Bundled ffmpeg via `imageio-ffmpeg` — no system installation required
- GIF caching by content hash for fast re-compilation
- Graceful degradation: missing manim shows warning-box instead of crash

### CLI Commands

- `cdl-slides compile` — Compile Markdown to presentation
- `cdl-slides init` — Create new presentation from template
- `cdl-slides version` — Show version and Marp CLI status
- `cdl-slides setup` — Pre-download Marp CLI binary

[1.0.0]: https://github.com/ContextLab/cdl-slides/releases/tag/v1.0.0
