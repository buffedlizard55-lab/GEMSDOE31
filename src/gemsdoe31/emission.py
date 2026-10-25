"""Preregistered dotted emitter: ridge NMS + score-ordered Poisson thinning.

The fleet's measured DTI economics favour sparse binary dots at ~2.8 px separation over dense
probability fields (see README "core question"). This module implements that emitter once, for
reuse by every arm/control so comparisons differ only in the input surface.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter, maximum_filter

INCUMBENT_DENSITY = 40199 / 5167373  # H27-4 dots per footprint pixel, fixed a priori


def ridge_nms(surface: np.ndarray, valid: np.ndarray, sigma: float = 1.0) -> np.ndarray:
    """3x3 local-maximum mask of the Gaussian-smoothed surface, restricted to valid cells."""
    filled = np.where(valid & np.isfinite(surface), surface, 0.0).astype(np.float64)
    smoothed = gaussian_filter(filled, sigma) if sigma else filled
    neighbourhood_max = maximum_filter(smoothed, size=3, mode="nearest")
    return (smoothed >= neighbourhood_max) & (smoothed > 0.0) & valid


def poisson_thin(scores: np.ndarray, candidates: np.ndarray, *, min_distance_px: float = 2.8,
                 max_dots: int) -> np.ndarray:
    """Greedy score-ordered thinning: accept a candidate if no accepted dot is closer than d px.

    Deterministic: ties are broken by (row, col) through a stable lexsort, so identical inputs
    always give identical dot sets.
    """
    rows, cols = np.nonzero(candidates)
    if rows.size == 0 or max_dots <= 0:
        return np.zeros(candidates.shape, dtype=bool)
    values = scores[rows, cols].astype(np.float64)
    order = np.lexsort((cols, rows, -values))
    rows, cols = rows[order], cols[order]

    cell = float(min_distance_px)
    radius_sq = cell * cell
    occupied: dict[tuple[int, int], list[tuple[int, int]]] = {}
    accepted_rows: list[int] = []
    accepted_cols: list[int] = []
    for r, c in zip(rows.tolist(), cols.tolist()):
        if len(accepted_rows) >= max_dots:
            break
        gr, gc = int(r // cell), int(c // cell)
        too_close = False
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                for (ar, ac) in occupied.get((gr + dr, gc + dc), ()):
                    if (ar - r) ** 2 + (ac - c) ** 2 < radius_sq:
                        too_close = True
                        break
                if too_close:
                    break
            if too_close:
                break
        if too_close:
            continue
        occupied.setdefault((gr, gc), []).append((r, c))
        accepted_rows.append(r)
        accepted_cols.append(c)
    dots = np.zeros(candidates.shape, dtype=bool)
    if accepted_rows:
        dots[np.asarray(accepted_rows), np.asarray(accepted_cols)] = True
    return dots


def emit_dots(surface: np.ndarray, valid: np.ndarray, *, max_dots: int,
              min_distance_px: float = 2.8, sigma: float = 1.0) -> np.ndarray:
    """Full frozen emitter: smooth -> ridge NMS -> score-ordered Poisson thinning -> top-K."""
    filled = np.where(valid & np.isfinite(surface), surface, 0.0).astype(np.float64)
    smoothed = gaussian_filter(filled, sigma) if sigma else filled
    candidates = ridge_nms(surface, valid, sigma=sigma)
    return poisson_thin(smoothed, candidates, min_distance_px=min_distance_px, max_dots=max_dots)
