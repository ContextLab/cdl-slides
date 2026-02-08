---
marp: true
theme: cdl-poster
size: A0
title: "Full Feature Test Poster"
authors:
  - name: "Jane Doe"
    affiliation: "Dartmouth College"
  - name: "John Smith"
    affiliation: "MIT"
---

```poster-layout
TTTTTTTTTT
IIIIMMMMMM
IIIIMMMMMM
RRRRCCCCCC
RRRRDDDDDD
```

## T: Poster Title

# Neural Network Analysis of Climate Data
**Jane Doe**¹, **John Smith**²

¹Dartmouth College, ²MIT

## I: Introduction

Climate modeling requires sophisticated analysis techniques.

- Global temperature trends
- Precipitation patterns
- Sea level changes

## M: Methods

We used a convolutional neural network:

```python
model = Sequential([
    Conv2D(32, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Dense(10, activation='softmax')
])
```

The loss function is:

$$L = -\sum_{i} y_i \log(\hat{y}_i)$$

## R: Results

<div class="note-box" data-title="Key Finding">
Temperature predictions improved by 23% using our method.
</div>

## C: Conclusion

Our approach demonstrates the effectiveness of deep learning.

## D: References

1. Smith et al. (2024) *Nature Climate Change*
2. Doe et al. (2023) *Science*
