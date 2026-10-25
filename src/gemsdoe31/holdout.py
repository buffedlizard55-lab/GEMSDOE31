"""Hide-and-recover spatial holdout (evaluator ``gemsdoe31-holdout-v1``).

Protocol (preregistered in ``knowledge/2026-10-25_h31e_surface_expression_preregistration.md``):

* withhold **whole fault components** (8-connected catalogue components assigned by centroid to a
  quadrant fold's eroded scoring domain);
* exclude all training samples within the empirical **21.25 km** collar of withheld truth
  (``evidence/buffer_derivation.json``);
* derive nothing from the withheld catalogue: arms may only use label-free raster channels, and
  catalogue-based features are forbidden by the caller contract;
* mask visible (non-withheld) faults **pixel-exactly** before scoring;
* score with the exact pooled DTI (alpha 0.2, beta 0.8, 300 m triangular kernel) from
  :mod:`gemsdoe31.metric`, with a paired spatial-block bootstrap for 95% intervals.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import distance_transform_edt

from . import metric
from .raster import CELL_M, connected_components

EVALUATOR_ID = "gemsdoe31-holdout-v1"
COLLAR_M = 21_250.0
DOMAIN_EROSION_PX = 12
BLOCK_PX = 200  # 20 km bootstrap blocks
FOLD_NAMES = ("NW", "NE", "SW", "SE")


def quadrant_rect(shape: tuple[int, int], fold: int,
                  erosion_px: int = DOMAIN_EROSION_PX) -> tuple[int, int, int, int]:
    """(r0, r1, c0, c1) of a quadrant rectangle shrunk by ``erosion_px`` on every side."""
    height, width = shape
    half_h, half_w = height // 2, width // 2
    r0, r1 = (0, half_h) if fold < 2 else (half_h, height)
    c0, c1 = (0, half_w) if fold % 2 == 0 else (half_w, width)
    return r0 + erosion_px, r1 - erosion_px, c0 + erosion_px, c1 - erosion_px


def fold_split(catalogue: np.ndarray, footprint: np.ndarray, fold: int,
               collar_m: float = COLLAR_M) -> dict:
    """Build one fold's domain / withheld truth / training-allowance masks.

    Returns boolean masks: ``domain`` (scoring area), ``truth`` (withheld component pixels inside
    the domain), ``train_allowed`` (pixels a model may sample from: outside this fold's whole
    quadrant, outside the collar around withheld truth, and not on an excluded straddling
    component), plus component bookkeeping.
    """
    if fold not in range(4):
        raise ValueError(f"fold must be 0..3, got {fold}")
    components = connected_components(catalogue)
    n_components = int(components.max())
    rows, cols = np.nonzero(catalogue)
    comp_ids = components[rows, cols]
    counts = np.bincount(comp_ids, minlength=n_components + 1)
    centroid_r = np.bincount(comp_ids, weights=rows, minlength=n_components + 1) / np.maximum(counts, 1)
    centroid_c = np.bincount(comp_ids, weights=cols, minlength=n_components + 1) / np.maximum(counts, 1)

    r0, r1, c0, c1 = quadrant_rect(catalogue.shape, fold)
    domain = np.zeros(catalogue.shape, dtype=bool)
    domain[r0:r1, c0:c1] = True
    domain &= footprint

    centroid_in_domain = (
        (centroid_r >= r0) & (centroid_r < r1) & (centroid_c >= c0) & (centroid_c < c1)
    )
    withheld_ids = np.nonzero(centroid_in_domain[1:])[0] + 1 if n_components else np.asarray([], int)
    withheld_lookup = np.zeros(n_components + 1, dtype=bool)
    withheld_lookup[withheld_ids] = True
    truth = withheld_lookup[components] & domain

    # Components that touch the domain but are not withheld are excluded from training positives,
    # so no part of a scored-adjacent trace leaks into the fit.
    touching_ids = np.unique(components[domain & catalogue])
    excluded_lookup = np.zeros(n_components + 1, dtype=bool)
    excluded_lookup[touching_ids] = True
    excluded_lookup[withheld_ids] = False
    excluded_pixels = excluded_lookup[components]

    height, width = catalogue.shape
    half_h, half_w = height // 2, width // 2
    quadrant = np.zeros(catalogue.shape, dtype=bool)
    qr0, qr1 = (0, half_h) if fold < 2 else (half_h, height)
    qc0, qc1 = (0, half_w) if fold % 2 == 0 else (half_w, width)
    quadrant[qr0:qr1, qc0:qc1] = True

    collar_px = collar_m / CELL_M
    distance_to_truth_px = distance_transform_edt(~truth)
    outside_collar = distance_to_truth_px > collar_px

    train_allowed = footprint & ~quadrant & outside_collar & ~excluded_pixels & ~truth
    return {
        "fold": fold,
        "fold_name": FOLD_NAMES[fold],
        "domain": domain,
        "truth": truth,
        "train_allowed": train_allowed,
        "bbox": (r0, r1, c0, c1),
        "n_withheld_components": int(len(withheld_ids)),
        "n_excluded_components": int(excluded_lookup[1:].sum()),
        "n_truth_pixels": int(truth.sum()),
        "n_domain_pixels": int(domain.sum()),
        "n_train_positive_pixels": int((catalogue & train_allowed).sum()),
    }


def mask_visible_faults(pred: np.ndarray, catalogue: np.ndarray, truth: np.ndarray,
                        domain: np.ndarray) -> np.ndarray:
    """Zero predictions outside the domain and on every visible (non-withheld) catalogue pixel."""
    masked = np.where(domain & np.isfinite(pred), pred, 0.0).astype(np.float64)
    masked[catalogue & ~truth] = 0.0
    return masked


def score_fold(pred: np.ndarray, catalogue: np.ndarray, split: dict) -> dict:
    """Exact DTI for one fold, plus the pooled-bootstrap block sufficient statistics."""
    masked = mask_visible_faults(pred, catalogue, split["truth"], split["domain"])
    result = metric.dti(masked, split["truth"])
    result["block_stats"] = block_sufficient_statistics(masked, split["truth"], split["domain"])
    return result


def block_sufficient_statistics(pred_masked: np.ndarray, truth: np.ndarray,
                                domain: np.ndarray, block_px: int = BLOCK_PX) -> dict:
    """Per-block (TP credit, FP weight, truth count) so pooled DTI can be bootstrapped."""
    height, width = truth.shape
    block_rows = (np.arange(height) // block_px)[:, None]
    block_cols = (np.arange(width) // block_px)[None, :]
    n_block_cols = int(block_cols.max()) + 1
    block_id = (block_rows * n_block_cols + block_cols).astype(np.int64)

    credit = metric.per_truth_credit(pred_masked, truth)
    truth_blocks = block_id[truth]
    fp = metric.fp_weights(pred_masked, truth)
    domain_blocks = block_id[domain]
    domain_fp = fp[domain]

    max_block = int(block_id.max())
    tp_by_block = np.bincount(truth_blocks, weights=credit, minlength=max_block + 1)
    n_by_block = np.bincount(truth_blocks, minlength=max_block + 1).astype(np.float64)
    fp_by_block = np.bincount(domain_blocks, weights=domain_fp, minlength=max_block + 1)
    # The block universe must be arm-independent (every block intersecting the scoring domain),
    # otherwise paired bootstrap resamples cannot be aligned across arms.
    domain_count_by_block = np.bincount(domain_blocks, minlength=max_block + 1)
    keep = domain_count_by_block > 0
    return {
        "tp": tp_by_block[keep],
        "fp": fp_by_block[keep],
        "n_truth": n_by_block[keep],
        "n_blocks": int(keep.sum()),
    }


def pooled_dti_from_blocks(blocks: list[dict]) -> float:
    tp = float(sum(b["tp"].sum() for b in blocks))
    fp = float(sum(b["fp"].sum() for b in blocks))
    n_truth = float(sum(b["n_truth"].sum() for b in blocks))
    fn = n_truth - tp
    return tp / (tp + metric.ALPHA * fp + metric.BETA * fn + metric.EPSILON)


def paired_block_bootstrap(arms_blocks: dict[str, list[dict]], *, resamples: int = 1000,
                           seed: int = 20261025) -> dict:
    """Paired bootstrap over spatial blocks: identical resampled blocks for every arm.

    ``arms_blocks`` maps arm name -> per-fold block-stat dicts (folds concatenated in the same
    order for every arm). Returns pooled DTI, 95% CI per arm, and paired delta CIs vs the first
    arm alphabetically is NOT assumed: deltas are reported for every ordered pair requested by
    the caller through ``deltas_vs`` — here, versus every other arm for the alphabetically first
    arm; callers needing a specific reference should pass a two-arm dict.
    """
    names = list(arms_blocks)
    stacked = {}
    for name in names:
        stacked[name] = {
            key: np.concatenate([b[key] for b in arms_blocks[name]])
            for key in ("tp", "fp", "n_truth")
        }
    n_blocks = len(next(iter(stacked.values()))["tp"])
    rng = np.random.default_rng(seed)

    def pooled(stats: dict, idx: np.ndarray | None) -> float:
        if idx is None:
            tp, fp, n = stats["tp"].sum(), stats["fp"].sum(), stats["n_truth"].sum()
        else:
            tp, fp, n = stats["tp"][idx].sum(), stats["fp"][idx].sum(), stats["n_truth"][idx].sum()
        return float(tp / (tp + metric.ALPHA * fp + metric.BETA * (n - tp) + metric.EPSILON))

    point = {name: pooled(stacked[name], None) for name in names}
    draws = {name: np.empty(resamples) for name in names}
    for i in range(resamples):
        idx = rng.integers(0, n_blocks, size=n_blocks)
        for name in names:
            draws[name][i] = pooled(stacked[name], idx)

    def ci(values: np.ndarray) -> list[float]:
        return [float(np.percentile(values, 2.5)), float(np.percentile(values, 97.5))]

    out = {
        "resamples": resamples,
        "seed": seed,
        "n_blocks": int(n_blocks),
        "pooled_dti": point,
        "ci95": {name: ci(draws[name]) for name in names},
        "paired_delta_ci95": {},
    }
    if len(names) == 2:
        delta = draws[names[0]] - draws[names[1]]
        out["paired_delta_ci95"][f"{names[0]}_minus_{names[1]}"] = ci(delta)
        out["paired_delta_point"] = {f"{names[0]}_minus_{names[1]}": point[names[0]] - point[names[1]]}
    return out
