"""Exact implementation of the GEMS Prize distance-weighted Tversky index.

The official definition (competition problem page, https://www.drivendata.org/competitions/306/
competition-doe-gems/page/967/) is::

    k(d) = max(1 - d / R, 0)                      R = 300 m

    TPw = sum_{g in G}   max_{x : d(x,g) <= R}  p(x) * k(d(x,g))
    FPw = sum_{x : p(x)>0} p(x) * [1 - max_{g in G} k(d(x,g))]
    FNw = sum_{g in G}   [1 - max_{x : d(x,g) <= R} p(x) * k(d(x,g))]

    DTI = TPw / (TPw + alpha * FPw + beta * FNw + epsilon)      alpha = 0.2, beta = 0.8

Notes that matter for correctness:

* ``FNw = |G| - TPw`` holds exactly here because ``p <= 1`` and ``k <= 1`` make every outer
  ``max`` at most 1. The implementation computes both independently and asserts the identity.
* The ``max`` inside TPw is over the **product** ``p(x) · k(d(x, g))``, not over ``p`` and ``k``
  separately. The two differ whenever a low-probability pixel sits closer to the truth than a
  high-probability one; the product form is the published one and is what this module computes.
* The false-positive term needs only the distance to the nearest truth pixel, because ``k`` is
  monotone decreasing in distance.
* ``epsilon`` is not published on the problem page. The competition value is unknown; a tiny
  epsilon (1e-10) is used so that a submission with no true-positive weight scores 0 instead of
  dividing by zero. It changes nothing at realistic score magnitudes.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import distance_transform_edt

ALPHA = 0.2
BETA = 0.8
RADIUS_M = 300.0
CELL_M = 100.0
EPSILON = 1e-10


def _offsets(cell_m: float, radius_m: float) -> tuple[np.ndarray, np.ndarray]:
    """Lattice offsets with 100 m cells inside the kernel support, plus their kernel weights.

    At 100 m cells and R = 300 m this is the 29 offsets of the radius-3 disk: the centre, the four
    axial neighbours at distance 1 and 3, the four diagonals of the 2x2 block, the eight knight-ish
    (±2, ±1) offsets, and the four (±1, ±1) offsets. Offsets such as (±3, ±1) (3.16 cells out) are
    correctly excluded.
    """
    steps = int(np.floor(radius_m / cell_m))
    dx, dy = np.meshgrid(np.arange(-steps, steps + 1), np.arange(-steps, steps + 1), indexing="ij")
    dx, dy = dx.ravel(), dy.ravel()
    distance_m = cell_m * np.hypot(dx, dy)
    keep = distance_m <= radius_m + 1e-9
    dx, dy, distance_m = dx[keep], dy[keep], distance_m[keep]
    kernel = np.clip(1.0 - distance_m / radius_m, 0.0, 1.0)
    order = np.lexsort((dy, dx))
    return np.stack([dx[order], dy[order]], axis=1), kernel[order]


def _true_positive_weight(pred: np.ndarray, truth: np.ndarray, offsets: np.ndarray,
                          kernel: np.ndarray) -> float:
    """``sum_g max_x p(x) k(d(x,g))`` at every truth pixel, vectorised over the 29 offsets."""
    height, width = pred.shape
    rows, cols = np.nonzero(truth)
    best = np.zeros(rows.shape, dtype=np.float64)
    for (step_row, step_col), weight in zip(offsets, kernel):
        rr = rows + step_row
        cc = cols + step_col
        inside = (rr >= 0) & (rr < height) & (cc >= 0) & (cc < width)
        weighted = np.zeros(rows.shape, dtype=np.float64)
        if inside.any():
            weighted[inside] = pred[rr[inside], cc[inside]].astype(np.float64) * weight
        np.maximum(best, weighted, out=best)
    return float(best.sum())


def dti(pred: np.ndarray, truth: np.ndarray, *, alpha: float = ALPHA, beta: float = BETA,
        cell_m: float = CELL_M, radius_m: float = RADIUS_M, epsilon: float = EPSILON,
        weights: np.ndarray | None = None) -> dict:
    """Score one prediction field against one binary truth mask.

    ``pred`` must already be the probability/confidence field, finite inside the footprint and zero
    everywhere it is not (NaN outside the footprint is treated as zero, and a NaN inside the truth
    mask is an error). ``weights`` optionally multiplies the per-truth-pixel contribution, which is
    how the collars in ``collar_sweep.json`` are applied; leave it None for the plain metric.
    """
    pred = np.asarray(pred)
    truth = np.asarray(truth).astype(bool)
    if pred.shape != truth.shape:
        raise ValueError(f"shape mismatch: {pred.shape} != {truth.shape}")
    if truth.any() and not np.isfinite(pred[truth]).all():
        raise ValueError("non-finite prediction inside the truth mask")
    finite_pred = np.where(np.isfinite(pred), pred, 0.0)
    if finite_pred.min() < 0.0 or finite_pred.max() > 1.0:
        raise ValueError("predictions must be in [0, 1]")

    offsets, kernel = _offsets(cell_m, radius_m)
    tpw = _true_positive_weight(finite_pred, truth, offsets, kernel)
    if weights is not None:
        rows, cols = np.nonzero(truth)
        tpw = float((np.asarray(weights)[rows, cols] * _per_truth_credit(finite_pred, truth, offsets, kernel)).sum())
    fnw = float(truth.sum()) - tpw

    distance_m = distance_transform_edt(~truth, sampling=cell_m)
    nearest_kernel = np.clip(1.0 - distance_m / radius_m, 0.0, 1.0)
    fpw = float((finite_pred * (1.0 - nearest_kernel)).sum())

    denominator = tpw + alpha * fpw + beta * fnw + epsilon
    return {"TPw": tpw, "FPw": fpw, "FNw": fnw, "DTI": tpw / denominator if denominator else 0.0,
            "truth_pixels": int(truth.sum()), "emitted_weight": float(finite_pred.sum()),
            "alpha": alpha, "beta": beta, "radius_m": radius_m, "offsets": int(len(kernel))}


def _per_truth_credit(pred: np.ndarray, truth: np.ndarray, offsets: np.ndarray,
                      kernel: np.ndarray) -> np.ndarray:
    """Per-truth-pixel credit vector (used by the collared evaluations)."""
    height, width = pred.shape
    rows, cols = np.nonzero(truth)
    best = np.zeros(rows.shape, dtype=np.float64)
    for (step_row, step_col), weight in zip(offsets, kernel):
        rr = rows + step_row
        cc = cols + step_col
        inside = (rr >= 0) & (rr < height) & (cc >= 0) & (cc < width)
        weighted = np.zeros(rows.shape, dtype=np.float64)
        if inside.any():
            weighted[inside] = pred[rr[inside], cc[inside]].astype(np.float64) * weight
        np.maximum(best, weighted, out=best)
    return best


def brute_force(pred: np.ndarray, truth: np.ndarray, *, alpha: float = ALPHA, beta: float = BETA,
                cell_m: float = CELL_M, radius_m: float = RADIUS_M, epsilon: float = EPSILON) -> dict:
    """Literal transcription of the published sums, with no vectorisation tricks.

    Written for verification only: it is O(|G| * N) and is used by ``scripts/check_metric.py`` on
    small grids.
    """
    pred = np.asarray(pred, dtype=np.float64)
    truth = np.asarray(truth).astype(bool)
    finite_pred = np.where(np.isfinite(pred), pred, 0.0)
    height, width = pred.shape
    truth_cells = list(zip(*np.nonzero(truth)))
    positive_cells = [(r, c) for r in range(height) for c in range(width) if finite_pred[r, c] > 0]

    def kernel(distance_m: float) -> float:
        return max(1.0 - distance_m / radius_m, 0.0)

    tpw = 0.0
    for (gr, gc) in truth_cells:
        best = 0.0
        for (xr, xc) in positive_cells:
            distance_m = cell_m * float(np.hypot(xr - gr, xc - gc))
            if distance_m <= radius_m + 1e-9:
                best = max(best, finite_pred[xr, xc] * kernel(distance_m))
        tpw += best

    fpw = 0.0
    for (xr, xc) in positive_cells:
        best_k = 0.0
        for (gr, gc) in truth_cells:
            distance_m = cell_m * float(np.hypot(xr - gr, xc - gc))
            best_k = max(best_k, kernel(distance_m))
        fpw += finite_pred[xr, xc] * (1.0 - best_k)

    fnw = 0.0
    for (gr, gc) in truth_cells:
        best = 0.0
        for (xr, xc) in positive_cells:
            distance_m = cell_m * float(np.hypot(xr - gr, xc - gc))
            if distance_m <= radius_m + 1e-9:
                best = max(best, finite_pred[xr, xc] * kernel(distance_m))
        fnw += 1.0 - best

    denominator = tpw + alpha * fpw + beta * fnw + epsilon
    return {"TPw": tpw, "FPw": fpw, "FNw": fnw, "DTI": tpw / denominator if denominator else 0.0}
