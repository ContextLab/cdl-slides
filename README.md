# CDL Slides

Compile Markdown files into beautiful CDL-themed [Marp](https://marp.app/) presentations. Includes the full Contextual Dynamics Lab slide theme with bundled fonts, images, and CSS.

## Features

- **Cross-platform**: Works on macOS, Windows, and Linux
- **Multiple output formats**: HTML, PDF, and PPTX
- **Bundled theme**: Complete CDL/Dartmouth-branded theme with custom fonts, colors, and layouts
- **Smart preprocessing**: Auto-splits long code blocks and tables across slides
- **Flow diagrams**: Simple ```` ```flow ```` syntax for pipeline diagrams
- **Auto-scaling**: Automatically adjusts font size for dense slides
- **Syntax highlighting**: Code blocks with line numbers via Pygments
- **Math support**: KaTeX for inline and display equations
- **Callout boxes**: Note, tip, warning, definition, example, and important boxes

## Prerequisites

**Marp CLI** is required for compilation. Install one of these ways:

```bash
# Via npm (recommended)
npm install -g @marp-team/marp-cli

# Via Homebrew (macOS)
brew install marp-cli

# Via standalone binary
# Download from: https://github.com/marp-team/marp-cli/releases
```

## Installation

```bash
pip install cdl-slides
```

Or install from source:

```bash
git clone https://github.com/ContextLab/cdl-slides.git
cd cdl-slides
pip install -e .
```

## Quick Start

1. Create a Markdown file with CDL theme front matter:

```markdown
---
marp: true
theme: cdl-theme
math: katex
transition: fade 0.25s
author: Contextual Dynamics Lab
---

# My Presentation Title
### Subtitle

Your Name
Your Institution

---

# Slide Two

- Point one
- Point two
- Point three
```

2. Compile to HTML and PDF:

```bash
cdl-slides compile my_presentation.md
```

3. Output files are created alongside the input:
   - `my_presentation.html`
   - `my_presentation.pdf`

## CLI Reference

### `cdl-slides compile`

Compile a Markdown file into a presentation.

```
Usage: cdl-slides compile [OPTIONS] INPUT_FILE

Options:
  -o, --output PATH      Output file or directory (default: same dir as input)
  -f, --format TEXT       Output format: html, pdf, pptx, both (default: both)
  -l, --lines INTEGER     Max code lines per slide before splitting (default: 20)
  -r, --rows INTEGER      Max table rows per slide before splitting (default: 8)
  --no-split              Disable auto-splitting of code blocks and tables
  --keep-temp             Keep temporary processed files for debugging
  -t, --theme-dir PATH    Custom theme directory (overrides bundled CDL theme)
  --help                  Show this message and exit.
```

**Examples:**

```bash
# Compile to HTML only
cdl-slides compile slides.md --format html

# Compile to PDF only
cdl-slides compile slides.md --format pdf

# Compile to PowerPoint
cdl-slides compile slides.md --format pptx

# Compile with custom output location
cdl-slides compile slides.md --output ./build/

# Compile with custom code splitting threshold
cdl-slides compile slides.md --lines 15 --rows 6
```

### `cdl-slides init`

Create a new presentation from a template.

```bash
cdl-slides init                    # Create template in current directory
cdl-slides init ./my-presentation  # Create template in specific directory
```

### `cdl-slides version`

Show version and Marp CLI status.

```bash
cdl-slides version
```

## Slide Authoring Guide

### Front Matter

Every CDL presentation starts with this YAML front matter:

```yaml
---
marp: true
theme: cdl-theme
math: katex
transition: fade 0.25s
author: Contextual Dynamics Lab
---
```

### Callout Boxes

The CDL theme includes six styled box types:

```html
<div class="note-box" data-title="Title">
Content here with **Markdown** support.
</div>

<div class="tip-box" data-title="Pro Tip">
Helpful advice goes here.
</div>

<div class="warning-box" data-title="Caution">
Important warnings here.
</div>

<div class="definition-box" data-title="Term">
Definition of the term.
</div>

<div class="example-box" data-title="Example">
A worked example.
</div>

<div class="important-box" data-title="Key Point">
Critical information.
</div>
```

### Two-Column Layouts

```html
<div style="display: flex; gap: 1.5em;">
<div style="flex: 1;">

**Left column** content with Markdown.

</div>
<div style="flex: 1;">

**Right column** content with Markdown.

</div>
</div>
```

### Flow Diagrams

Use the ```` ```flow ```` syntax for simple pipeline diagrams:

````markdown
```flow
[Input:blue] --> [Process:green] --> [Output:orange]
```
<!-- caption: A data processing pipeline -->
````

Available colors: `green`, `blue`, `navy`, `teal`, `orange`, `red`, `violet`, `yellow`, `gray`.

### Scale Directives

For dense slides, use scale directives to adjust font size:

```markdown
<!-- _class: scale-80 -->
# Dense Slide Title

Lots of content here...
```

Available scales: `scale-50` through `scale-95` in increments of 5.

Note: The preprocessor auto-injects scale classes when slides overflow, so manual scaling is rarely needed.

### Emoji Figures

```html
<div class="emoji-figure">
  <div class="emoji-col">
    <span class="emoji emoji-xl emoji-bg emoji-bg-navy">📊</span>
    <span class="label">Data</span>
  </div>
  <div class="emoji-col">
    <span class="emoji emoji-xl emoji-bg emoji-bg-green">🔬</span>
    <span class="label">Analysis</span>
  </div>
</div>
```

Available backgrounds: `emoji-bg-navy`, `emoji-bg-green`, `emoji-bg-blue`, `emoji-bg-orange`, `emoji-bg-purple`, `emoji-bg-teal`.

### Math (KaTeX)

Inline: `$E = mc^2$`

Display:
```
$$\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}$$
```

### Code Blocks

Code blocks are automatically:
- Syntax highlighted (via Pygments)
- Line numbered
- Split across slides if they exceed `--lines` threshold (default: 20)

### Tables

Markdown tables are automatically split across slides if they exceed `--rows` threshold (default: 8 data rows).

### Arrow Syntax

Use arrow shorthand in slides:

```markdown
A --[80]-> B --[lg]-> C
```

Options: `--[80]->` (pixel width), `--[lg]->` (named size: sm, md, lg, xl).

## Bundled Fonts

The package includes these fonts for consistent rendering across platforms:

- **Avenir LT Std** (Light, Book, Roman, Medium, Heavy, Black) — body text
- **Fira Code** (Regular, Medium, Bold) — code blocks
- **Noto Sans SC** (Variable) — CJK character support

## Development

```bash
# Clone and install in development mode
git clone https://github.com/ContextLab/cdl-slides.git
cd cdl-slides
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run linter
ruff check src/ tests/
ruff format src/ tests/
```

## License

MIT License. See [LICENSE](LICENSE) for details.

## Links

- **Repository**: https://github.com/ContextLab/cdl-slides
- **Lab Website**: https://www.context-lab.com
- **Marp**: https://marp.app/
