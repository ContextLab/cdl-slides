# CDL-SLIDES KNOWLEDGE BASE

**Generated:** 2026-02-06
**Commit:** 6e9bc74
**Branch:** main

## OVERVIEW

Python CLI tool that compiles Markdown into CDL-themed Marp presentations. Core stack: Click CLI, Pygments highlighting, optional Manim animations.

## STRUCTURE

```
cdl-slides/
├── src/cdl_slides/
│   ├── cli.py              # Entry point (cdl-slides command)
│   ├── preprocessor.py     # Main logic: flow diagrams, code splitting, animations
│   ├── compiler.py         # Orchestrates Marp CLI execution
│   ├── animate_parser.py   # DSL parser for ```animate blocks
│   ├── animate_transpiler.py # Converts DSL AST to Manim Python
│   ├── manim_renderer.py   # Executes Manim, generates GIFs
│   └── assets/             # Bundled fonts, CSS, images
├── tests/                  # Pytest suite (238 tests)
└── examples/               # Sample presentations
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add CLI command | `cli.py` | Uses Click decorators |
| Modify slide preprocessing | `preprocessor.py` | Battle-tested regexes - don't refactor |
| Add DSL command | `animate_parser.py` + `animate_transpiler.py` | Add regex pattern + generation logic |
| Fix animation rendering | `manim_renderer.py` | Handles GIF caching |
| Update theme styles | `assets/themes/cdl-theme.css` | POSIX paths only |

## CRITICAL: ANIMATE DSL USAGE

**ALWAYS use the DSL markdown syntax for animations.** The DSL approach is preferred because it handles object creation and animation separation correctly, avoids Manim quirks, and produces cleaner, more maintainable code.

**Escape hatch:** For complex animations not expressible in DSL, use `manim <python_code> as NAME` within an animate block. This is the ONLY acceptable way to use raw Manim code.

### DSL Syntax (use this):
```
write equation "y = \sin(x)" as label
fade-in label
```

### Supported DSL Commands:
- `write equation "LATEX" as NAME [position]` - Create equation
- `write text "string" as NAME [position]` - Create text
- `create axes x=[min,max,step] y=[min,max,step] as NAME` - Coordinate system
- `create graph "formula" x=[min,max] color=COLOR as NAME` - Standalone function graph
- `plot "formula" on AXES color=COLOR stroke=N as NAME` - Plot on existing axes (stroke sets line width)
- `create [circle|square|arrow] color=COLOR as NAME` - Shapes
- `fade-in NAME` / `fade-out NAME` - Animations
- `draw NAME` - Create animation (for axes/graphs)
- `transform NAME1 -> NAME2` - Morph animation
- `wait SECONDS` - Pause
- `manim <python_code> as NAME` - Escape hatch for complex cases

### Position Modifiers:
- `at center`
- `above/below/left-of/right-of REFERENCE`

### Metadata (block header):
- `height: 400`, `width: 600`, `quality: high`, `scale: 2.5`

## ANTI-PATTERNS

| Forbidden | Reason |
|-----------|--------|
| Mock objects in tests | Must use real files/calls for verification |
| Refactoring preprocessor regexes | Battle-tested, port faithfully |
| Adding manim to core deps | Animation support is optional |
| External image references | All assets must be bundled |
| Silently swallowing errors | Must produce warning-box in HTML output |
| Using gifsicle | Use Pillow for GIF processing |

## CONVENTIONS

- **Line length**: 120 chars (Ruff)
- **Python**: >=3.9
- `preprocessor.py` ignores E501 (embedded templates)
- Tests must be "real-world" - no mocks

## COMMANDS

```bash
# Development
pip install -e ".[dev,animations]"
pytest tests/ -v
ruff check src/ tests/ && ruff format src/ tests/

# Usage
cdl-slides compile slides.md --format html
cdl-slides compile slides.md --format pdf
```

## NOTES

- Animation support included by default with `pip install cdl-slides`
- Marp CLI auto-downloads on first use
- GIFs cached by content hash in output directory (e.g., `animations/` alongside slides)
- Graceful degradation: missing manim shows warning-box, not crash
