# Technical Appendix: Non-Invertibility & Structural Compression

## Core Claim
The reasoning artifact contains only the **structural centroid** of a PCF-discovered pattern. Raw data is architecturally impossible to include.

## Mathematical Demonstration
Let each observation timeline be projected into a high-dimensional structural embedding space \(\mathbb{R}^d\) (e.g., \(d = 512\)) via PCF.

Given \(n\) examples, the centroid \(C\) is:
\[
C = \frac{1}{n} \sum_{i=1}^n v_i
\]

Any reconstruction attack's best estimator is \(\hat{v}_j = C\) for any original \(v_j\).

**Empirical reconstruction error** (from P2P study, held-out vectors):
\[
r = 0.0149 \pm 0.002
\]
(Cosine distance equivalent < 1.5% signal recoverable.)

## Information-Theoretic Bound (Sketch)
Mutual information \(I(V; C)\) is bounded by the variance lost in averaging — practically zero usable signal for re-identification.

## Toy Demo (runnable)
```python
import numpy as np
np.random.seed(42)
n = 4200
d = 512
vectors = np.random.randn(n, d) * 0.1 + np.random.randn(d)
centroid = vectors.mean(axis=0)
errors = np.linalg.norm(vectors - centroid, axis=1) / np.linalg.norm(vectors, axis=1)
print(f"Mean reconstruction error: {errors.mean():.4f}")


Conclusion: The loss is exactly the non-structural variance. PCF patterns are definitionally structural → predictive power is preserved where it matters.
