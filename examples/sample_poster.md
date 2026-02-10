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

<div class="scale-80">

<div class="note-box" data-title="Orient your audience">

Start with the **broad question** your research addresses and narrow to your specific contribution in 3–5 sentences. Explain why this topic matters and what gap in current knowledge your work fills.

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

<div class="note-box" data-title="Research question">

State your specific **hypothesis** or research question. Use a figure instead of a paragraph wherever possible.

- **Hypothesis 1**: Feature X correlates with Y
- **Hypothesis 2**: Intervention Z modulates this relationship

</div>

<div class="note-box" data-title="Background">

Summarize **prior work** that motivates your study and explain how your approach advances the field.

</div>

</div>

## M: Methods [violet]

<div class="scale-75">

<div class="definition-box" data-title="Experimental design">

Describe your **paradigm**: participants ($N=50$), conditions (within-subject), stimuli (naturalistic video), and procedure.

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

Describe the key statistical or computational methods. Prefer a **diagram** over dense notation.

- **Preprocessing**: fMRIPrep v20.2.1
- **Modeling**: GLM with custom regressors
- **Inference**: Non-parametric permutation tests

</div>

<div style="flex: 1; display: flex; align-items: center; justify-content: center;">
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

</div>

## R: Results [green]

<div class="example-box" data-title="Primary finding">

Lead with your **most critical result**. Every figure should have a clear, self-explanatory takeaway.

> **Significant interaction found between Condition&nbsp;A and B** <span style="white-space:nowrap;">**($p < 0.001$).**</span>

</div>

```chart
type: bar
labels: Condition A, Condition B, Control
data: 0.89, 0.72, 0.65
ylabel: Accuracy
caption: Figure 1. Accuracy by experimental condition
height: 220px
```

<div style="text-align: center; white-space: nowrap;">

$$\hat{y} = \beta_0 + \beta_1 x_1 + \beta_2 x_2 + \epsilon, \quad R^2 = 0.73$$

</div>

<div class="example-box" data-title="Supporting evidence">

Use tables for quantitative comparisons across conditions:

</div>

| Measure | Group A | Group B | Group C | *p*-value |
|---------|---------|---------|---------|-----------|
| Accuracy | 0.89 | 0.72 | 0.65 | < 0.01 |
| RT (ms) | 342 | 418 | 450 | < 0.05 |
| F1 Score | 0.85 | 0.68 | 0.60 | < 0.01 |

<div class="example-box" data-title="Generalization">

Show that findings **replicate** across datasets or participant groups to strengthen impact.

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
caption: Figure 2. Generalization across datasets
height: 220px
```

```chart
type: bar
labels: Condition A, Condition B, Control
datasets:
  - label: Accuracy
    data: 0.89, 0.72, 0.65
  - label: F1 score
    data: 0.85, 0.68, 0.60
caption: Figure 1. Accuracy and F1 scores across experimental conditions
height: 250px
```

<div class="example-box" data-title="Robustness check">

We verified our results using cross-validation <span style="white-space:nowrap;">(k&nbsp;=&nbsp;5)</span> and bootstrap resampling <span style="white-space:nowrap;">(1000 iterations).</span> The effect size remains stable <span style="white-space:nowrap;">(Cohen's d&nbsp;=&nbsp;0.8).</span> Sensitivity analyses confirm that results hold across a range of preprocessing choices and model specifications. Permutation testing corroborates significance under non-parametric assumptions <span style="white-space:nowrap;">(BF&nbsp;>&nbsp;10).</span>

</div>


## D: Discussion [teal]

<div class="scale-75">

<div class="tip-box" data-title="Key takeaways">

Summarize your **main findings** and connect them back to the original research question.

- **Finding 1**: Model outperforms baseline by 15%, supporting Hypothesis 1.
- **Finding 2**: Effect is robust to parameter variations and generalizes across datasets.
- **Finding 3**: Results suggest a new cognitive control mechanism consistent with prior theoretical accounts.

</div>

<div class="tip-box" data-title="Implications">

Explain **why these findings matter** for the broader field.

- Provides evidence for predictive coding frameworks in perception.
- Challenges existing models that assume static representations.
- Opens new avenues for computational psychiatry applications.

</div>

```chart
type: radar
labels: Accuracy, Speed, Scalability, Robustness, Interpretability
datasets:
  - label: Current work
    data: 88, 72, 65, 80, 90
  - label: Next steps
    data: 93, 85, 80, 88, 92
caption: Figure 3. Current capabilities vs. planned improvements
height: 220px
```

<div class="tip-box" data-title="Limitations and future work">

Acknowledge **limitations** honestly and describe planned follow-ups.

- Sample limited to college-age participants; generalization needed.
- Future work: longitudinal designs, larger and more diverse cohorts.

</div>

</div>

## E: References [orange]

<div class="scale-45">

<div class="warning-box" data-title="">

1. Author A *et al.* (2023). *J. Neurosci.*
2. Author C *et al.* (2022). *Nat. Hum. Behav.*
3. Author E *et al.* (2021). *Psychol. Rev.*
4. Author G *et al.* (2020). *PNAS.*
5. Author J *et al.* (2019). *NeuroImage.*

</div>

</div>

## A: Acknowledgments [spring]

<div class="scale-55">

<div class="tip-box" data-title="Funding and links">

**NSF EPSCoR** #1632738
**NIH R01** MH112357
**NSF CAREER** #1849109

🌐 context-lab.com
💻 github.com/ContextLab
📂 osf.io/example

</div>

</div>
