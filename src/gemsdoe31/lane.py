"""Hide-and-recover evaluation, dot emission and uniqueness tools for lane experiments.

Evaluator version string: ``LANE-EVAL-1`` (this module, ``metric.py`` offsets/kernel reused unchanged).

Everything here is deliberately *separable per pixel*: the weighted true-positive credit is a sum over truth
pixels and the weighted false-positive mass is a sum over emitted pixels. That lets a spatial-tile cluster
bootstrap produce a 95 % interval without refitting anything, and lets many candidates be scored against one
cached truth in a fraction of a second. ``tests/test_lane.py`` checks that the pooled number equals
``metric.dti`` exactly.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.ndimage import distance_transform_edt

from . import metric
from .raster import CELL_M, connected_components

EVAL_VERSION = "LANE-EVAL-1"
TILE_ROWS = 8
TILE_COLS = 8


@dataclass
class Instrument:
    """One truth definition with everything needed to score any dot set cheaply."""

    name: str
    truth: np.ndarray            # bool, scored truth pixels (visible faults already removed)
    masked: np.ndarray           # bool, pixels where predictions are zeroed (visible faults)
    fp_weight: np.ndarray        # float32, 1 - kernel(nearest truth); the false-positive charge per unit emission
    rows: np.ndarray
    cols: np.ndarray
    tile_of_truth: np.ndarray
    tile_shape: tuple[int, int]

    @property
    def n_truth(self) -> int:
        return int(self.truth.sum())


def tile_index(rows: np.ndarray, cols: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    tr = np.minimum(rows * TILE_ROWS // shape[0], TILE_ROWS - 1)
    tc = np.minimum(cols * TILE_COLS // shape[1], TILE_COLS - 1)
    return (tr * TILE_COLS + tc).astype(np.int32)


def make_instrument(name: str, truth: np.ndarray, masked: np.ndarray | None = None) -> Instrument:
    truth = np.asarray(truth, dtype=bool)
    masked = np.zeros_like(truth) if masked is None else np.asarray(masked, dtype=bool)
    distance_m = distance_transform_edt(~truth, sampling=CELL_M)
    fp_weight = (1.0 - np.clip(1.0 - distance_m / metric.RADIUS_M, 0.0, 1.0)).astype(np.float32)
    rows, cols = np.nonzero(truth)
    return Instrument(name, truth, masked, fp_weight, rows, cols, tile_index(rows, cols, truth.shape), truth.shape)


def restrict_truth(inst: Instrument, zone: np.ndarray, name: str | None = None) -> Instrument:
    """Score only truth pixels inside ``zone``; the false-positive charge still uses *all* truth (nearest-truth rule)."""
    keep = zone[inst.rows, inst.cols]
    truth = np.zeros_like(inst.truth)
    truth[inst.rows[keep], inst.cols[keep]] = True
    return Instrument(name or inst.name + "|zone", truth, inst.masked, inst.fp_weight, inst.rows[keep], inst.cols[keep],
                      inst.tile_of_truth[keep], inst.tile_shape)


_OFFSETS, _KERNEL = metric._offsets(metric.CELL_M, metric.RADIUS_M)


def truth_credit(dots: np.ndarray, inst: Instrument) -> np.ndarray:
    """Per-truth-pixel credit ``max_x p(x) k(d)`` for a 0/1 emission (visible faults already zeroed)."""
    height, width = dots.shape
    best = np.zeros(inst.rows.shape, dtype=np.float64)
    for (dr, dc), weight in zip(_OFFSETS, _KERNEL):
        rr, cc = inst.rows + dr, inst.cols + dc
        inside = (rr >= 0) & (rr < height) & (cc >= 0) & (cc < width)
        val = np.zeros(inst.rows.shape, dtype=np.float64)
        val[inside] = dots[rr[inside], cc[inside]] * weight
        np.maximum(best, val, out=best)
    return best


def sufficient_stats(dots: np.ndarray, inst: Instrument) -> dict:
    """TPw, FPw, G and per-tile versions of each; ``dots`` is a bool/0-1 array."""
    active = np.asarray(dots, dtype=bool) & ~inst.masked
    credit = truth_credit(active.astype(np.float32), inst)
    fr, fc = np.nonzero(active)
    fp = inst.fp_weight[fr, fc].astype(np.float64)
    n_tiles = TILE_ROWS * TILE_COLS
    tile_fp = np.bincount(tile_index(fr, fc, inst.tile_shape), weights=fp, minlength=n_tiles)
    tile_tp = np.bincount(inst.tile_of_truth, weights=credit, minlength=n_tiles)
    tile_g = np.bincount(inst.tile_of_truth, minlength=n_tiles).astype(np.float64)
    return {"tp": float(credit.sum()), "fp": float(fp.sum()), "g": float(inst.n_truth), "dots": int(active.sum()),
            "tile_tp": tile_tp, "tile_fp": tile_fp, "tile_g": tile_g}


def dti_from(tp: float, fp: float, g: float) -> float:
    return float(tp / (tp + metric.ALPHA * fp + metric.BETA * (g - tp) + metric.EPSILON))


def pooled_dti(stats_list: list[dict]) -> float:
    return dti_from(sum(s["tp"] for s in stats_list), sum(s["fp"] for s in stats_list), sum(s["g"] for s in stats_list))


def tile_bootstrap(stats_by_name: dict[str, list[dict]], n_boot: int = 1000, seed: int = 20261025) -> dict:
    """Paired spatial-tile cluster bootstrap over the 8x8 tile grid (shared resamples for every candidate)."""
    rng = np.random.default_rng(seed)
    names = list(stats_by_name)
    n_tiles = TILE_ROWS * TILE_COLS
    tp = {n: sum(s["tile_tp"] for s in stats_by_name[n]) for n in names}
    fp = {n: sum(s["tile_fp"] for s in stats_by_name[n]) for n in names}
    g = {n: sum(s["tile_g"] for s in stats_by_name[n]) for n in names}
    draws = {n: np.empty(n_boot) for n in names}
    for b in range(n_boot):
        pick = rng.integers(0, n_tiles, n_tiles)
        for n in names:
            draws[n][b] = dti_from(tp[n][pick].sum(), fp[n][pick].sum(), g[n][pick].sum())
    return {n: {"point": pooled_dti(stats_by_name[n]), "ci95": [float(np.percentile(draws[n], 2.5)),
                                                                 float(np.percentile(draws[n], 97.5))],
               "draws": draws[n]} for n in names}


def paired_delta(draws_a: np.ndarray, draws_b: np.ndarray) -> dict:
    delta = draws_a - draws_b
    return {"mean": float(delta.mean()), "ci95": [float(np.percentile(delta, 2.5)), float(np.percentile(delta, 97.5))],
            "p_better": float((delta > 0).mean())}


def hide_components(catalogue: np.ndarray, hidden_fraction: float, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Withhold whole 8-connected fault components until ``hidden_fraction`` of the pixels are hidden."""
    labels = connected_components(catalogue)
    ids = np.arange(1, labels.max() + 1)
    sizes = np.bincount(labels.ravel(), minlength=labels.max() + 1)[1:]
    order = np.random.default_rng(seed).permutation(len(ids))
    hidden_ids, total, target = [], 0, hidden_fraction * catalogue.sum()
    for k in order:
        if total >= target:
            break
        hidden_ids.append(ids[k])
        total += int(sizes[k])
    hidden = np.isin(labels, hidden_ids)
    return hidden, catalogue & ~hidden


# ---------------------------------------------------------------- emission

def poisson_disk(score: np.ndarray, candidates: np.ndarray, min_dist_px: float, budget: int,
                 return_order: bool = False):
    """Greedy highest-score-first Poisson-disk selection among ``candidates`` (bool mask).

    With ``return_order`` the accepted pixels are returned as an ``(n, 2)`` array in acceptance order, so any
    prefix is itself the greedy solution for a smaller budget.
    """
    rows, cols = np.nonzero(candidates)
    order = np.argsort(-score[rows, cols], kind="stable")
    r = int(np.ceil(min_dist_px))
    occupied = np.zeros(score.shape, dtype=bool)
    out = np.zeros(score.shape, dtype=bool)
    accepted: list[tuple[int, int]] = []
    offsets = [(a, b) for a in range(-r, r + 1) for b in range(-r, r + 1) if a * a + b * b < min_dist_px ** 2]
    height, width = score.shape
    count = 0
    for k in order:
        i, j = rows[k], cols[k]
        if occupied[i, j]:
            continue
        out[i, j] = True
        accepted.append((i, j))
        count += 1
        if count >= budget:
            break
        for a, b in offsets:
            ii, jj = i + a, j + b
            if 0 <= ii < height and 0 <= jj < width:
                occupied[ii, jj] = True
    return np.asarray(accepted, dtype=np.int32).reshape(-1, 2) if return_order else out


def prefix_mask(order: np.ndarray, n: int, shape: tuple[int, int]) -> np.ndarray:
    out = np.zeros(shape, dtype=bool)
    out[order[:n, 0], order[:n, 1]] = True
    return out


# ------------------------------------------------------------- uniqueness

def smooth_density(dots: np.ndarray, sigma_px: float = 3.0) -> np.ndarray:
    from scipy.ndimage import gaussian_filter
    return gaussian_filter(dots.astype(np.float32), sigma_px, mode="constant")


def spearman(a: np.ndarray, b: np.ndarray, footprint: np.ndarray, stride: int = 4) -> float:
    from scipy.stats import rankdata
    sel = footprint[::stride, ::stride]
    x, y = a[::stride, ::stride][sel], b[::stride, ::stride][sel]
    rx, ry = rankdata(x), rankdata(y)
    rx, ry = rx - rx.mean(), ry - ry.mean()
    denom = np.sqrt((rx * rx).sum() * (ry * ry).sum())
    return float((rx * ry).sum() / denom) if denom else 0.0
