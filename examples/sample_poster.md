---
marp: true
theme: cdl-poster
size: A0
math: katex
---

```poster-layout
TTTTTTTTTTTTTTTTTTTTTTTTTTTT
IIIIIIIIRRRRRRRRRRRRDDDDDDDD
IIIIIIIIRRRRRRRRRRRRDDDDDDDD
IIIIIIIIRRRRRRRRRRRRDDDDDDDD
IIIIIIIIRRRRRRRRRRRRDDDDDDDD
IIIIIIIIRRRRRRRRRRRRDDDDDDDD
MMMMMMMMRRRRRRRRRRRRDDDDDDDD
MMMMMMMMRRRRRRRRRRRRDDDDDDDD
MMMMMMMMRRRRRRRRRRRREEEAAAAA
MMMMMMMMRRRRRRRRRRRREEEAAAAA
```

## T: Your poster title goes here

**Author One**¹, **Author Two**², **Author Three**¹ | corresponding.author@dartmouth.edu

¹ Dartmouth College | ² Collaborating Institution

## I: Introduction and motivation [blue]

<div class="note-box" data-title="Orient your audience">

Start with the **broad question** your research addresses and narrow to your specific contribution. Explain why this topic matters and what gap your work fills.

</div>

<div class="emoji-figure">
<div class="emoji-col">
<span class="emoji emoji-xl emoji-bg emoji-bg-blue">🔬</span>
<span class="label">Phenomenon</span>
</div>
<div class="emoji-col">
<span class="emoji emoji-xl emoji-bg emoji-bg-green">❓</span>
<span class="label">Open question</span>
</div>
<div class="emoji-col">
<span class="emoji emoji-xl emoji-bg emoji-bg-orange">💡</span>
<span class="label">Your approach</span>
</div>
</div>

<div class="note-box" data-title="Hypotheses">

- **H1**: Feature X correlates with outcome Y
- **H2**: Intervention Z modulates this relationship

</div>

<div class="note-box" data-title="Background">

Prior work motivates this study; our approach advances the field by addressing key limitations in existing models.

</div>

## M: Methods [violet]

<div class="scale-90">

<div class="definition-box" data-title="Experimental design">

**Paradigm**: $N=50$ participants, within-subject design, naturalistic video stimuli.

</div>

<div class="flow-diagram">
<span class="flow-box flow-blue">Design</span>
<span class="flow-arrow">→</span>
<span class="flow-box flow-green">Record</span>
<span class="flow-arrow">→</span>
<span class="flow-box flow-orange">Process</span>
<span class="flow-arrow">→</span>
<span class="flow-box flow-purple">Analyze</span>
</div>

<div class="definition-box" data-title="Analysis approach">

- **Preprocessing**: fMRIPrep v20.2.1
- **Modeling**: GLM with custom regressors
- **Inference**: Non-parametric permutation tests

</div>

<div class="emoji-figure">
<div class="emoji-col">
<span class="emoji emoji-xl">🐍</span>
<span class="label">Python</span>
</div>
<div class="emoji-col">
<span class="emoji emoji-xl">🧠</span>
<span class="label">Neuroimaging</span>
</div>
<div class="emoji-col">
<span class="emoji emoji-xl">📊</span>
<span class="label">Visualization</span>
</div>
</div>

</div>

## R: Results [green]

<div class="example-box" data-title="Primary finding">

**Significant interaction** between Condition A and B ($p < 0.001$).

</div>

<div class="chart-row">

```chart
type: bar
labels: Condition A, Condition B, Control
data: 0.89, 0.72, 0.65
ylabel: Accuracy
caption: Accuracy by condition
```

```chart
type: bar
labels: Condition A, Condition B, Control
datasets:
  - label: Accuracy
    data: 0.89, 0.72, 0.65
  - label: F1 score
    data: 0.85, 0.68, 0.60
ylabel: Score
caption: Accuracy and F1 by condition
```

</div>

<div style="text-align: center; white-space: nowrap;">

$$\hat{y} = \beta_0 + \beta_1 x_1 + \beta_2 x_2 + \epsilon, \quad R^2 = 0.73$$

</div>

| Measure | Group A | Group B | Group C | *p*-value |
|---------|---------|---------|---------|-----------|
| Accuracy | 0.89 | 0.72 | 0.65 | < 0.01 |
| RT (ms) | 342 | 418 | 450 | < 0.05 |
| F1 Score | 0.85 | 0.68 | 0.60 | < 0.01 |

<div class="example-box" data-title="Generalization">

Findings **replicate** across datasets and participant groups.

</div>

```chart
type: line
labels: Fold 1, Fold 2, Fold 3, Fold 4, Fold 5
datasets:
  - label: Dataset 1
    data: 0.85, 0.87, 0.83, 0.88, 0.86
  - label: Dataset 2
    data: 0.78, 0.81, 0.79, 0.82, 0.80
  - label: Dataset 3
    data: 0.71, 0.74, 0.70, 0.75, 0.73
xlabel: Cross-validation fold
ylabel: F1 score
caption: Generalization across datasets
```

<div class="example-box" data-title="Robustness">

Cross-validation (k=5) and bootstrap resampling (1000 iterations) confirm stable effect size (Cohen's d = 0.8). Permutation testing corroborates significance (BF > 10).

</div>

## D: Discussion [teal]

<div class="scale-80">

<div class="tip-box" data-title="Key takeaways">

- **Finding 1**: Model outperforms baseline by 15%, supporting H1
- **Finding 2**: Effect is robust across parameter variations
- **Finding 3**: Results suggest a new cognitive control mechanism

</div>

<div class="tip-box" data-title="Implications">

- Evidence for predictive coding frameworks in perception
- Challenges models assuming static representations
- Opens avenues for computational psychiatry

</div>

```chart
type: radar
labels: Accuracy, Speed, Scalability, Robustness, Interpretability
datasets:
  - label: Current work
    data: 88, 72, 65, 80, 90
  - label: Next steps
    data: 93, 85, 80, 88, 92
caption: Current capabilities vs. planned improvements
```

<div class="tip-box" data-title="Limitations and future work">

- Sample limited to college-age participants
- Future: longitudinal designs, larger cohorts

</div>

</div>

## E: References [orange]

<div class="scale-60">

1. Author A *et al.* (2023). *J. Neurosci.*
2. Author C *et al.* (2022). *Nat. Hum. Behav.*
3. Author E *et al.* (2021). *Psychol. Rev.*
4. Author G *et al.* (2020). *PNAS.*
5. Author J *et al.* (2019). *NeuroImage.*

</div>

## A: Acknowledgments [spring]

<div class="scale-65">

**NSF EPSCoR** #1632738 · **NIH R01** MH112357 · **NSF CAREER** #1849109

🌐 context-lab.com · 💻 github.com/ContextLab

</div>
