---
marp: true
theme: cdl-theme
math: katex
transition: fade 0.25s
author: Contextual Dynamics Lab
---

# Getting started with CDL slides
### A tour of every feature in the CDL slide theme

Contextual Dynamics Lab
Dartmouth College

---

# Simple bullet points

- This slide demonstrates basic bullet points
- Each bullet appears on its own line
- You can nest bullets:
  - First sub-item
  - Second sub-item
- Back to the top level

---

# Text emphasis and formatting

- Use **bold** for strong emphasis
- Use *italics* for subtle emphasis
- Use `inline code` for code references
- Combine **bold and *nested italic*** emphasis
- Add [hyperlinks](https://www.context-lab.com) to text
- Use ~~strikethrough~~ for corrections

---

# Callout boxes: note

<div class="note-box" data-title="What are callout boxes?">

Callout boxes are styled containers for important information. This is a **note box**, used for general information, further reading, and supplementary context.

- Supports Markdown inside
- Including bullet points and **formatting**

</div>

---

# Callout boxes: tip and warning

<div class="tip-box" data-title="Pro tip">

Use tip boxes to highlight best practices, shortcuts, or recommendations that help the audience.

</div>

<div class="warning-box" data-title="Caution">

Use warning boxes for common pitfalls, important caveats, or things that might go wrong.

</div>

---

# Callout boxes: definition, example, important

<div class="definition-box" data-title="CDL Slides">

A Python package for compiling Markdown into beautiful, CDL-themed Marp presentations.

</div>

<div class="example-box" data-title="Usage">

`cdl-slides compile presentation.md --format both`

</div>

<div class="important-box" data-title="Key requirement">

Marp CLI is automatically installed on first compile — no setup needed.

</div>

---

# Two-column layout
<!-- _class: scale-90 -->

<div style="display: flex; gap: 1.5em;">
<div style="flex: 1;">

**Left column**
- First advantage
- Second advantage
- Third advantage

<div class="tip-box" data-title="Tip">

Flex layouts work great for comparisons.

</div>

</div>
<div style="flex: 1;">

**Right column**
- First consideration
- Second consideration
- Third consideration

<div class="warning-box" data-title="Note">

Keep columns roughly balanced in content.

</div>

</div>
</div>

---

# Code example

```python
from cdl_slides.compiler import compile_presentation
from pathlib import Path

results = compile_presentation(
    input_file=Path("slides.md"),
    output_format="both",
)

for f in results["files"]:
    print(f"{f['format']}: {f['path']}")
```

---

# Long code block (auto-split demo)

```python
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

def analyze_embeddings(texts, model, n_components=2):
    """Analyze word embeddings using PCA dimensionality reduction."""
    # Generate embeddings for all input texts
    embeddings = []
    for text in texts:
        tokens = model.tokenize(text)
        embedding = model.encode(tokens)
        embeddings.append(embedding.mean(axis=0))

    # Convert to numpy array
    X = np.array(embeddings)

    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Apply PCA
    pca = PCA(n_components=n_components)
    X_reduced = pca.fit_transform(X_scaled)

    # Calculate explained variance
    explained_var = pca.explained_variance_ratio_
    total_var = sum(explained_var)

    # Visualize results
    fig, ax = plt.subplots(figsize=(10, 8))
    scatter = ax.scatter(
        X_reduced[:, 0],
        X_reduced[:, 1],
        c=range(len(texts)),
        cmap="viridis",
        alpha=0.7,
    )
    ax.set_xlabel(f"PC1 ({explained_var[0]:.1%} variance)")
    ax.set_ylabel(f"PC2 ({explained_var[1]:.1%} variance)")
    ax.set_title(f"Embedding Space (Total: {total_var:.1%})")
    plt.colorbar(scatter, label="Text index")
    return X_reduced, explained_var
```

---

# Math support (KaTeX)
<!-- _class: scale-85 -->

<div class="example-box" data-title="Inline math">

The famous equation $E = mc^2$ relates energy and mass.

</div>

Display math for the attention mechanism:

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

Another example with integrals:

$$\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}$$

<div class="note-box" data-title="Math rendering">

KaTeX is used for math rendering. Use `$...$` for inline and `$$...$$` for display math.

</div>

---

# Simple table

| Method | Speed | Quality | OOV Handling |
|--------|-------|---------|--------------|
| Word2Vec | Fast | Good | None |
| GloVe | Fast | Good | None |
| FastText | Medium | Good | Excellent |
| BERT | Slow | Excellent | Good |
| GPT | Slow | Excellent | Good |

---

# Long table (auto-split demo)

| Feature | Python | JavaScript | Rust | Go | Ruby | Julia |
|---------|--------|-----------|------|-----|------|-------|
| Type System | Dynamic | Dynamic | Static | Static | Dynamic | Dynamic |
| Memory Management | GC | GC | Ownership | GC | GC | GC |
| Concurrency | GIL | Event Loop | Fearless | Goroutines | GIL | Tasks |
| Package Manager | pip | npm | cargo | go mod | gem | Pkg |
| REPL | Yes | Yes | No | No | Yes | Yes |
| Compile Speed | N/A | N/A | Slow | Fast | N/A | JIT |
| Runtime Speed | Slow | Medium | Fast | Fast | Slow | Fast |
| Learning Curve | Easy | Easy | Hard | Medium | Easy | Medium |
| Web Framework | Django | Express | Actix | Gin | Rails | Genie |
| ML Libraries | Excellent | Good | Growing | Limited | Limited | Good |
| Community Size | Huge | Huge | Growing | Large | Medium | Small |
| First Release | 1991 | 1995 | 2015 | 2009 | 1995 | 2012 |

---

# Flow diagrams
<!-- _class: scale-80 -->

```flow
[Markdown:blue] --> [Preprocess:teal] --> [Marp CLI:green] --> [Output:orange]
```
<!-- caption: The CDL Slides compilation pipeline -->

Syntax for flow diagrams:

````
```flow
[Input:blue] --> [Process:green] --> [Output:orange]
```
<!-- caption: Optional caption text -->
````

Available colors: `green`, `blue`, `navy`, `teal`, `orange`, `red`, `violet`, `yellow`, `gray`.

---

# Emoji figures
<!-- _class: scale-80 -->

<div class="emoji-figure">
  <div class="emoji-col">
    <span class="emoji emoji-xl emoji-bg emoji-bg-navy">📝</span>
    <span class="label">Write</span>
  </div>
  <div class="emoji-col">
    <span class="emoji emoji-xl emoji-bg emoji-bg-green">⚙️</span>
    <span class="label">Compile</span>
  </div>
  <div class="emoji-col">
    <span class="emoji emoji-xl emoji-bg emoji-bg-orange">🎯</span>
    <span class="label">Present</span>
  </div>
</div>

```html
<div class="emoji-figure">
  <div class="emoji-col">
    <span class="emoji emoji-xl emoji-bg emoji-bg-navy">📝</span>
    <span class="label">Write</span>
  </div>
</div>
```

Sizes: `emoji-sm`, `emoji-md`, `emoji-lg`, `emoji-xl`. Backgrounds: `emoji-bg-navy`, `emoji-bg-green`, `emoji-bg-orange`, `emoji-bg-purple`, `emoji-bg-teal`. Omit `emoji-bg` classes for no background.

---

# Scale directives
<!-- _class: scale-80 -->

When slides have dense content, use scale directives to fit everything.

<div style="display: flex; gap: 1.5em;">
<div style="flex: 1;">

**Manual scaling**
- `<!-- _class: scale-80 -->` reduces to 80%
- Range: `scale-50` to `scale-95`
- Place directive at start of slide

</div>
<div style="flex: 1;">

**Auto-scaling**
- The preprocessor detects overflow
- Automatically injects scale classes
- Manual overrides take priority

</div>
</div>

<div class="note-box" data-title="This slide uses scale-80">

Notice how more content fits compared to default 100% scaling.

</div>

---

<!-- _class: scale-80 -->
# Output formats

CDL Slides compiles Markdown into multiple presentation formats:

| Format | Flag | Use case |
|--------|------|----------|
| HTML | `--format html` | Interactive browser slides |
| PDF | `--format pdf` | Printable, shareable documents |
| PPTX | `--format pptx` | Editable PowerPoint files |
| Both | `--format both` | HTML + PDF (default) |

<div class="tip-box" data-title="Quick start">

```bash
cdl-slides compile slides.md              # HTML + PDF (default)
cdl-slides compile slides.md -f pptx      # PowerPoint only
```

</div>

---

# Questions? Feedback?

<div class="emoji-figure">
  <div class="emoji-col">
    <span class="emoji emoji-xl emoji-bg emoji-bg-navy">📧</span>
    <span class="label"><a href="mailto:contextualdynamics@gmail.com">Email</a> us</span>
  </div>
  <div class="emoji-col">
    <span class="emoji emoji-xl emoji-bg emoji-bg-purple">💻</span>
    <span class="label"><a href="https://github.com/ContextLab/cdl-slides">GitHub</a></span>
  </div>
  <div class="emoji-col">
    <span class="emoji emoji-xl emoji-bg emoji-bg-green">🌐</span>
    <span class="label"><a href="https://www.context-lab.com">Website</a></span>
  </div>
</div>

<div class="note-box" data-title="Get started">

```bash
pip install cdl-slides
cdl-slides compile your_presentation.md
```

</div>
