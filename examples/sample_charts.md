---
marp: true
theme: cdl-theme
math: katex
transition: fade 0.25s
author: Contextual Dynamics Lab
---

# Chart examples
### Inline Chart.js charts with CDL theming

Contextual Dynamics Lab

---

# Language model parameters

```chart
type: bar
labels: GPT-2, LLaMA, Mistral, Claude, LLaMA-2
data: 1.5, 70, 7, 52, 70
ylabel: Parameters (B)
caption: LLaMA and LLaMA-2 lead at 70B parameters
```

---

# Training loss over epochs

```chart
type: line
labels: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
datasets:
  - label: Baseline
    data: 2.8, 2.1, 1.7, 1.4, 1.2, 1.05, 0.95, 0.88, 0.83, 0.80
  - label: Optimized
    data: 2.5, 1.6, 1.1, 0.8, 0.65, 0.55, 0.48, 0.43, 0.40, 0.38
xlabel: Epoch
ylabel: Loss
caption: Optimized model converges 2x faster than baseline
```

---

# Model performance comparison

```chart
type: bar
labels: GPT-4, Claude, Gemini, LLaMA-3
datasets:
  - label: Accuracy
    data: 92, 90, 88, 82
  - label: F1 score
    data: 89, 88, 85, 79
  - label: Recall
    data: 87, 91, 83, 76
ylabel: Score (%)
caption: GPT-4 leads across all three metrics
```

---

# Research funding distribution

```chart
type: pie
labels: Federal grants, Industry, Foundation, University
data: 45, 25, 18, 12
caption: Federal grants account for nearly half of all funding
```

---

# Faculty time allocation

```chart
type: doughnut
labels: Research, Teaching, Service, Administration
data: 40, 25, 20, 15
caption: Research dominates at 40% of faculty effort
```

---

# Model size vs. accuracy

```chart
type: scatter
datasets:
  - label: Transformer models
    data: 1.5 78, 7 85, 13 87, 52 91, 70 90, 175 93
  - label: RNN baselines
    data: 0.5 62, 2 68, 5 72, 10 74, 20 76
xlabel: Parameters (B)
ylabel: Accuracy (%)
caption: Accuracy plateaus above 50B parameters
```

---

# Model capabilities

```chart
type: radar
labels: Reasoning, Coding, Math, Writing, Analysis, Creativity
datasets:
  - label: GPT-4
    data: 95, 92, 90, 93, 91, 88
  - label: Claude
    data: 93, 90, 88, 95, 94, 90
  - label: Open source
    data: 78, 82, 75, 80, 76, 72
caption: Claude excels in writing; open source lags across all dimensions
```

---

# Neural network layer activations (viridis palette)

```chart
type: bar
labels: Conv1, Conv2, Conv3, Pool1, FC1, FC2, Output
data: 0.82, 0.91, 0.67, 0.45, 0.93, 0.78, 0.56
palette: viridis
ylabel: Mean activation
caption: FC1 shows highest activation; pooling layer is lowest
```
