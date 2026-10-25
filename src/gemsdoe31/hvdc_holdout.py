"""Shared spatially blocked hide-and-recover holdout evaluator, leakage canary, and duplicate gate.

Evaluator ID: ``gemsdoe31-hide-recover-v1``

Implements all Parallel-Run Protocol evaluation rules:
- Whole-component hiding (20% hidden per quadrant stratified by component size)
- 4-quadrant spatial block CV + 21,250 m (213 px) empirical residual-variogram spatial collar
  + whole-component exclusion across fold boundaries
- Pixel-exact masking of visible faults at evaluation
- Exact pooled DTI (alpha=0.2, beta=0.8, 300 m triangular kernel) + 1,000-replicate 20 km x 20 km
  spatial-tile cluster-bootstrap 95% confidence intervals
- Single-feature holdout ROC-AUC leakage canary (flags max(AUC, 1-AUC) > 0.90)
- Pre-placement Spearman rank correlation (<= 0.90) and post-placement 3-px dot overlap (<= 0.70)
  duplicate gate against registry rasters
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

from .metric import ALPHA, BETA, CELL_M, RADIUS_M, _offsets, dti
from .raster import connected_components, quadrant_blocks

EVALUATOR_VERSION = "gemsdoe31-hide-recover-v1"
DEFAULT_COLLAR_M = 21_250.0
DEFAULT_HIDE_FRAC = 0.20
TILE_PX = 200  # 20 km x 20 km spatial bootstrap cluster tiles


@dataclass(frozen=True)
class HideRecoverDraw:
    """Deterministic whole-component hide/visible partition across the 4 spatial quadrants."""

    seed: int
    visible: np.ndarray          # bool (H, W), ~80% of catalogue components
    hidden: np.ndarray           # bool (H, W), ~20% of catalogue components
    comp_quadrant: np.ndarray    # int8 (n_comp + 1,), home quadrant 0..3 per component id
    hidden_comp_ids: np.ndarray  # int32 array of hidden component ids


@dataclass(frozen=True)
class FoldSplit:
    """Spatial block fold with 21.25 km buffer collar and whole-component exclusion."""

    fold: int
    test_region: np.ndarray      # bool (H, W) footprint pixels in quadrant 'fold'
    train_region: np.ndarray     # bool (H, W) footprint pixels > collar_m from test_region
    collar_region: np.ndarray    # bool (H, W) footprint pixels in (0, collar_m] buffer


def build_spatial_folds(
    footprint: np.ndarray,
    *,
    collar_m: float = DEFAULT_COLLAR_M,
    cell_m: float = CELL_M,
) -> list[FoldSplit]:
    """Precompute the 4 quadrant folds with the 21,250 m spatial collar."""
    foot = np.asarray(footprint, dtype=bool)
    blocks = quadrant_blocks(foot.shape)
    folds: list[FoldSplit] = []
    for q in range(4):
        test_reg = foot & (blocks == q)
        d_m = distance_transform_edt(~test_reg, sampling=cell_m)
        train_reg = foot & (d_m > collar_m)
        collar_reg = foot & (~test_reg) & (~train_reg)
        folds.append(
            FoldSplit(
                fold=q,
                test_region=test_reg,
                train_region=train_reg,
                collar_region=collar_reg,
            )
        )
    return folds


def make_hide_recover_draw(
    catalogue: np.ndarray,
    footprint: np.ndarray,
    seed: int,
    *,
    hide_frac: float = DEFAULT_HIDE_FRAC,
) -> HideRecoverDraw:
    """Hide ``hide_frac`` of whole 8-connected components per quadrant, stratified by pixel length."""
    cat = np.asarray(catalogue, dtype=bool) & np.asarray(footprint, dtype=bool)
    comp = connected_components(cat)
    n_comp = int(comp.max())
    blocks = quadrant_blocks(cat.shape)

    ys, xs = np.nonzero(comp > 0)
    cids = comp[ys, xs]
    counts = np.bincount(cids, minlength=n_comp + 1)
    sum_y = np.bincount(cids, weights=ys, minlength=n_comp + 1)
    sum_x = np.bincount(cids, weights=xs, minlength=n_comp + 1)
    cy = np.clip((sum_y / np.maximum(counts, 1)).astype(int), 0, cat.shape[0] - 1)
    cx = np.clip((sum_x / np.maximum(counts, 1)).astype(int), 0, cat.shape[1] - 1)
    comp_quad = blocks[cy, cx].astype(np.int8)

    rng = np.random.default_rng(seed)
    hidden_cids: list[int] = []
    for q in range(4):
        q_cids = np.flatnonzero((np.arange(n_comp + 1) > 0) & (comp_quad == q))
        if q_cids.size == 0:
            continue
        # Stratify into 4 length quartiles so hidden pixel totals are stable across seeds
        q_sizes = counts[q_cids]
        order = np.argsort(q_sizes, kind="mergesort")
        q_sorted = q_cids[order]
        for stratum in np.array_split(q_sorted, 4):
            if stratum.size == 0:
                continue
            n_hide = max(1, int(round(hide_frac * stratum.size)))
            chosen = rng.choice(stratum, size=min(n_hide, stratum.size), replace=False)
            hidden_cids.extend(int(x) for x in chosen)

    hidden_arr = np.array(sorted(hidden_cids), dtype=np.int32)
    is_hidden_comp = np.zeros(n_comp + 1, dtype=bool)
    is_hidden_comp[hidden_arr] = True

    hidden_mask = is_hidden_comp[comp] & cat
    visible_mask = (~is_hidden_comp[comp]) & cat
    return HideRecoverDraw(
        seed=int(seed),
        visible=visible_mask,
        hidden=hidden_mask,
        comp_quadrant=comp_quad,
        hidden_comp_ids=hidden_arr,
    )


def fold_clean_catalogue_masks(
    catalogue: np.ndarray,
    fold_split: FoldSplit,
    *,
    struct_hide_seed: int | None = None,
    hide_frac: float = DEFAULT_HIDE_FRAC,
) -> dict[str, np.ndarray]:
    """Return strict leak-free training masks for ``fold_split``.

    Any 8-connected component touching ``fold_split.test_region`` OR ``fold_split.collar_region``
    is excluded as a whole component from training positives and from training visible faults.
    """
    comp = connected_components(catalogue)
    n_comp = int(comp.max())
    forbidden_zone = fold_split.test_region | fold_split.collar_region
    bad_cids = np.unique(comp[forbidden_zone & (comp > 0)])
    keep_comp = np.ones(n_comp + 1, dtype=bool)
    keep_comp[0] = False
    keep_comp[bad_cids] = False

    train_pos = keep_comp[comp] & fold_split.train_region
    # Buffer negative sampling > 2 px away from any catalogue pixel in train_region
    d_any_train = distance_transform_edt(~(catalogue & fold_split.train_region))
    train_neg = fold_split.train_region & (d_any_train > 2.0) & (~train_pos)

    out = {
        "train_pos": train_pos,
        "train_neg": train_neg,
    }
    if struct_hide_seed is not None:
        valid_train_cids = np.flatnonzero(keep_comp)
        rng = np.random.default_rng(struct_hide_seed)
        n_hide = max(1, int(round(hide_frac * valid_train_cids.size)))
        hid_cids = rng.choice(valid_train_cids, size=min(n_hide, valid_train_cids.size), replace=False)
        is_tr_hid = np.zeros(n_comp + 1, dtype=bool)
        is_tr_hid[hid_cids] = True
        out["train_struct_visible"] = keep_comp[comp] & (~is_tr_hid[comp]) & fold_split.train_region
        out["train_struct_hidden"] = keep_comp[comp] & is_tr_hid[comp] & fold_split.train_region
    return out


def additive_dti_pixel_maps(
    pred: np.ndarray,
    gt: np.ndarray,
    *,
    cell_m: float = CELL_M,
    radius_m: float = RADIUS_M,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Per-pixel TP_w, FN_w, and FP_w maps whose global sums reproduce ``metric.dti(pred, gt)``."""
    p = np.asarray(pred, dtype=np.float64)
    g = np.asarray(gt, dtype=bool)
    h, w = p.shape
    offsets, weights = _offsets(cell_m, radius_m)

    pred_support = p > 0.0
    fn_best = np.zeros((h, w), dtype=np.float64)
    fp_best = np.zeros((h, w), dtype=np.float64)
    for (dr, dc), wt in zip(offsets, weights):
        r0 = max(0, -int(dr))
        r1 = min(h, h - int(dr))
        c0 = max(0, -int(dc))
        c1 = min(w, w - int(dc))
        sr = slice(r0 + int(dr), r1 + int(dr))
        sc = slice(c0 + int(dc), c1 + int(dc))
        tr = slice(r0, r1)
        tc = slice(c0, c1)
        np.maximum(fn_best[tr, tc], p[sr, sc] * float(wt), out=fn_best[tr, tc])
        np.maximum(fp_best[tr, tc], g[sr, sc].astype(np.float64) * float(wt), out=fp_best[tr, tc])

    tp_map = np.where(g, fn_best, 0.0)
    fn_map = np.where(g, 1.0 - fn_best, 0.0)
    fp_map = np.where(pred_support, p * (1.0 - fp_best), 0.0)
    return tp_map, fn_map, fp_map


def score_holdout_draw(
    dots: np.ndarray,
    draw: HideRecoverDraw,
    footprint: np.ndarray,
    *,
    tile_px: int = TILE_PX,
    n_boot: int = 1000,
    boot_seed: int = 20261025,
) -> dict:
    """Score pixel-exact masked holdout DTI + 20 km x 20 km cluster-bootstrap 95% CI."""
    foot = np.asarray(footprint, dtype=bool)
    pred_masked = (np.asarray(dots, dtype=bool) & foot & (~draw.visible)).astype(np.float32)
    gt_hidden = draw.hidden & foot

    tp_map, fn_map, fp_map = additive_dti_pixel_maps(pred_masked, gt_hidden)
    tpw = float(tp_map.sum())
    fnw = float(fn_map.sum())
    fpw = float(fp_map.sum())
    denom = tpw + ALPHA * fpw + BETA * fnw
    point_dti = tpw / denom if denom > 0 else 0.0

    # Aggregate onto 20 km x 20 km (200 x 200 px) spatial cluster tiles
    h, w = foot.shape
    nr = (h + tile_px - 1) // tile_px
    nc = (w + tile_px - 1) // tile_px
    pad_h = nr * tile_px - h
    pad_w = nc * tile_px - w

    def tile_sums(arr: np.ndarray) -> np.ndarray:
        padded = np.pad(arr, ((0, pad_h), (0, pad_w)), mode="constant")
        return padded.reshape(nr, tile_px, nc, tile_px).sum(axis=(1, 3)).ravel()

    foot_tiles = tile_sums(foot.astype(np.float64)) > 0
    tp_t = tile_sums(tp_map)[foot_tiles]
    fn_t = tile_sums(fn_map)[foot_tiles]
    fp_t = tile_sums(fp_map)[foot_tiles]
    den_t = tp_t + ALPHA * fp_t + BETA * fn_t

    rng = np.random.default_rng(boot_seed + int(draw.seed))
    n_tiles = int(tp_t.size)
    idx = rng.integers(0, n_tiles, size=(n_boot, n_tiles))
    boot_tp = tp_t[idx].sum(axis=1)
    boot_den = den_t[idx].sum(axis=1)
    boot_dti = np.divide(boot_tp, np.maximum(boot_den, 1e-12))
    ci_lo, ci_hi = np.percentile(boot_dti, [2.5, 97.5])

    # Also compute per-quadrant DTI breakdown (Q0=NW, Q1=NE, Q2=SW, Q3=SE)
    qblocks = quadrant_blocks(foot.shape)
    quad_dti = {}
    for q in range(4):
        qm = foot & (qblocks == q)
        qtp = float(tp_map[qm].sum())
        qfn = float(fn_map[qm].sum())
        qfp = float(fp_map[qm].sum())
        qden = qtp + ALPHA * qfp + BETA * qfn
        quad_dti[f"Q{q}"] = round(qtp / qden if qden > 0 else 0.0, 6)

    # Also compute strict > 300 m visible-halo sensitivity metric
    d_vis = distance_transform_edt(~draw.visible)
    pred_halo300 = (pred_masked > 0) & (d_vis > 3.0)
    halo300_res = dti(pred_halo300.astype(np.float32), gt_hidden)

    return {
        "evaluator_version": EVALUATOR_VERSION,
        "seed": int(draw.seed),
        "holdout_dti": float(point_dti),
        "ci95_low": float(ci_lo),
        "ci95_high": float(ci_hi),
        "quadrant_dti": quad_dti,
        "n_bootstrap_tiles": n_tiles,
        "n_bootstrap_reps": int(n_boot),
        "withheld_positive_pixels": int(gt_hidden.sum()),
        "withheld_components": int(draw.hidden_comp_ids.size),
        "visible_positive_pixels": int((draw.visible & foot).sum()),
        "evaluated_dot_count": int((pred_masked > 0).sum()),
        "TPw": tpw,
        "FPw": fpw,
        "FNw": fnw,
        "holdout_dti_halo300m": float(halo300_res["DTI"]),
    }


def pool_multi_draw_bootstrap(
    draw_tile_arrays: list[tuple[np.ndarray, np.ndarray]],
    *,
    n_boot: int = 1000,
    boot_seed: int = 20261025,
) -> tuple[float, float, float]:
    """Compute mean holdout DTI across draws and 1,000-rep joint spatial-tile bootstrap 95% CI."""
    # Each entry is (tp_tiles, denom_tiles) aligned to the same spatial footprint tiles
    n_draws = len(draw_tile_arrays)
    n_tiles = int(draw_tile_arrays[0][0].size)
    point_vals = [float(tp.sum() / max(den.sum(), 1e-12)) for tp, den in draw_tile_arrays]
    mean_dti = float(np.mean(point_vals))

    rng = np.random.default_rng(boot_seed)
    idx = rng.integers(0, n_tiles, size=(n_boot, n_tiles))
    boot_means = np.zeros(n_boot, dtype=np.float64)
    for tp_t, den_t in draw_tile_arrays:
        b_tp = tp_t[idx].sum(axis=1)
        b_den = np.maximum(den_t[idx].sum(axis=1), 1e-12)
        boot_means += b_tp / b_den
    boot_means /= max(n_draws, 1)
    lo, hi = np.percentile(boot_means, [2.5, 97.5])
    return mean_dti, float(lo), float(hi)


def run_single_feature_leakage_canary(
    foot_matrix: np.ndarray,
    feature_names: list[str],
    hidden_foot: np.ndarray,
    visible_foot: np.ndarray,
    d_vis_foot: np.ndarray,
    *,
    max_neg_sample: int = 250_000,
    seed: int = 101,
    auc_ceiling: float = 0.90,
) -> dict:
    """Protocol Rule 4: test EVERY feature alone on holdout before trusting any model result."""
    eval_mask = d_vis_foot > 2.0
    pos_idx = np.flatnonzero(hidden_foot & eval_mask)
    neg_pool = np.flatnonzero((~hidden_foot) & (~visible_foot) & eval_mask)
    rng = np.random.default_rng(seed)
    neg_idx = (
        rng.choice(neg_pool, size=max_neg_sample, replace=False)
        if neg_pool.size > max_neg_sample
        else neg_pool
    )
    sample_idx = np.concatenate([pos_idx, neg_idx])
    y = np.concatenate([np.ones(pos_idx.size, dtype=np.int8), np.zeros(neg_idx.size, dtype=np.int8)])

    rows = []
    flagged = []
    for col_i, fname in enumerate(feature_names):
        vals = np.asarray(foot_matrix[col_i, sample_idx], dtype=np.float64)
        fin = np.isfinite(vals)
        if fin.sum() < 100 or y[fin].sum() < 10 or (fin.sum() - y[fin].sum()) < 10:
            auc = 0.5
        else:
            auc = float(roc_auc_score(y[fin], vals[fin]))
        sym_auc = max(auc, 1.0 - auc)
        leaked = sym_auc > auc_ceiling
        row = {
            "feature": fname,
            "roc_auc": round(auc, 6),
            "symmetric_auc": round(sym_auc, 6),
            "finite_fraction": round(float(fin.mean()), 6),
            "flagged_leakage": bool(leaked),
        }
        rows.append(row)
        if leaked:
            flagged.append(fname)

    rows_sorted = sorted(rows, key=lambda r: r["symmetric_auc"], reverse=True)
    return {
        "evaluator_version": EVALUATOR_VERSION,
        "auc_ceiling": auc_ceiling,
        "n_features_tested": len(feature_names),
        "n_positive_pixels": int(pos_idx.size),
        "n_negative_sampled": int(neg_idx.size),
        "max_symmetric_auc": float(rows_sorted[0]["symmetric_auc"]) if rows_sorted else 0.5,
        "top_feature": rows_sorted[0]["feature"] if rows_sorted else None,
        "flagged_features": flagged,
        "passed": len(flagged) == 0,
        "features": rows_sorted,
    }


def check_registry_duplicate_canary(
    surface_2d: np.ndarray,
    dots_2d: np.ndarray,
    footprint: np.ndarray,
    registry_paths: list[Path],
    *,
    spearman_Sample_n: int = 250_000,
    spearman_ceiling: float = 0.90,
    overlap_3px_ceiling: float = 0.70,
    seed: int = 20261025,
) -> dict:
    """Protocol Rule 1: Pre-placement rank correlation AND post-placement 3-px dot overlap gate."""
    foot = np.asarray(footprint, dtype=bool)
    foot_idx = np.flatnonzero(foot.ravel())
    rng = np.random.default_rng(seed)
    sub_idx = (
        rng.choice(foot_idx, size=spearman_Sample_n, replace=False)
        if foot_idx.size > spearman_Sample_n
        else foot_idx
    )

    surf_sub = np.nan_to_num(np.asarray(surface_2d, dtype=np.float64).ravel()[sub_idx], nan=0.0)
    cand_dots = np.asarray(dots_2d, dtype=bool) & foot
    n_cand_dots = int(cand_dots.sum())
    d_from_cand = distance_transform_edt(~cand_dots) if n_cand_dots > 0 else np.full(foot.shape, 1e6)

    comparisons = []
    max_abs_rho = 0.0
    max_rho_name = None
    max_ov3 = 0.0
    max_ov3_name = None

    for rpath in registry_paths:
        if not rpath.is_file():
            continue
        with rasterio.open(rpath) as src:
            reg_arr = src.read(1)
        if reg_arr.shape != foot.shape:
            continue
        reg_sub = np.nan_to_num(reg_arr.ravel()[sub_idx].astype(np.float64), nan=0.0)
        if np.std(surf_sub) < 1e-12 or np.std(reg_sub) < 1e-12:
            rho = 0.0
        else:
            rho = float(spearmanr(surf_sub, reg_sub).statistic)
            if not np.isfinite(rho):
                rho = 0.0

        reg_dots = (np.nan_to_num(reg_arr, nan=0.0) > 0.0) & foot
        n_reg_dots = int(reg_dots.sum())
        if n_cand_dots > 0 and n_reg_dots > 0:
            d_from_reg = distance_transform_edt(~reg_dots)
            # Symmetric max of directional 3-px overlaps so neither subset nor superset slips past!
            cand_in_reg3 = float((d_from_reg[cand_dots] <= 3.0).mean())
            reg_in_cand3 = float((d_from_cand[reg_dots] <= 3.0).mean())
            exact_shared = int((cand_dots & reg_dots).sum())
            ov3 = max(cand_in_reg3, reg_in_cand3)
        else:
            cand_in_reg3 = 0.0
            reg_in_cand3 = 0.0
            exact_shared = 0
            ov3 = 0.0

        is_dup = (abs(rho) > spearman_ceiling) or (ov3 > overlap_3px_ceiling)
        row = {
            "registry_raster": rpath.name,
            "registry_dots": n_reg_dots,
            "surface_spearman_rho": round(rho, 6),
            "cand_within_3px_of_reg": round(cand_in_reg3, 6),
            "reg_within_3px_of_cand": round(reg_in_cand3, 6),
            "symmetric_3px_overlap": round(ov3, 6),
            "exact_pixel_intersection": exact_shared,
            "duplicate_flagged": bool(is_dup),
        }
        comparisons.append(row)
        if abs(rho) > max_abs_rho:
            max_abs_rho = abs(rho)
            max_rho_name = rpath.name
        if ov3 > max_ov3:
            max_ov3 = ov3
            max_ov3_name = rpath.name

    comparisons.sort(key=lambda r: r["symmetric_3px_overlap"], reverse=True)
    any_dup = any(r["duplicate_flagged"] for r in comparisons)
    return {
        "spearman_ceiling": spearman_ceiling,
        "overlap_3px_ceiling": overlap_3px_ceiling,
        "candidate_dots": n_cand_dots,
        "n_registry_checked": len(comparisons),
        "max_abs_spearman": round(max_abs_rho, 6),
        "max_spearman_raster": max_rho_name,
        "max_symmetric_3px_overlap": round(max_ov3, 6),
        "max_overlap_raster": max_ov3_name,
        "passed": not any_dup,
        "comparisons": comparisons,
    }
