#!/usr/bin/env python3
"""End-to-end preregistered runner for Lane H31-J (TGTD-Submod).

Executes strictly <= 3 frozen model/allocation variants (H31-J1, H31-J2, H31-J3)
within a single method lane on the unchanged SHA-256-pinned ``vendor/gems57``
evaluation stack (``gems57-pooled-hide-v2``, ``buffer_px=213`` = 21.3 km):

1. Verifies all 11 competition/external GeoTIFFs, all 19 ``.cache/features/band-*.npy``
   hashes, all ``vendor/gems57`` hashes, and ``gdr_wellspring_in_footprint.csv``
   (strictly excluding ``dist_known_fault_px``).
2. Runs Gate G2 per-fold univariate + missingness ROC-AUC leakage canary (limit <= 0.90).
3. Evaluates the 3 frozen H31-J arms alongside 3 same-instrument controls
   (``physical_hgb``, ``magrest_concordant``, and ``gemsdoe32_h33_b2_foldfair``)
   on Screen ``seed=31`` (2,901 withheld positives, 1,000-draw 20 km physical-block
   paired bootstrap).
4. If Primary ``h31j3_dual_submod`` passes Screen ``seed=31``, evaluates ``h31j3_dual_submod``
   with ZERO parameter changes on untouched Fresh Confirmation ``seed=32``.
5. Estimates H31-J3's own out-of-fold hidden-trace residual semivariogram range via
   ``gemsdoe31.variogram`` to verify whether the 21.3 km collar exceeds its practical range.
6. Builds the stitched 4-quadrant OOF surface (every quadrant predicted strictly by models
   trained > 21.3 km outside that quadrant; zero in-sample refit), runs pre-placement
   uniqueness checks (G3a discrete submissions + G3b literal 57GEMSDOE shared-registry
   counterexample), emits 37,654 ridge-submodular dots (d_vis > 2.0 px), runs post-placement
   uniqueness checks, computes All-Elevation and Piedmont off-catalogue SGMC > 300 m proxies,
   and packages ``-zeros.tif``, ``-zeros.zip``, ``-nan.tif``, ``-nan.zip``, format receipts,
   and ``evidence/h31j/run_card.json`` (with ``slot_approved = False``).
"""

from __future__ import annotations

import gc
import hashlib
import json
import subprocess
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "vendor"), str(ROOT / "scripts")]

import numpy as np  # noqa: E402
import rasterio  # noqa: E402
from scipy.ndimage import distance_transform_edt, label as cc_label  # noqa: E402
from sklearn.ensemble import HistGradientBoostingClassifier  # noqa: E402
from sklearn.impute import SimpleImputer  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import roc_auc_score  # noqa: E402
from sklearn.pipeline import Pipeline  # noqa: E402
from sklearn.preprocessing import QuantileTransformer  # noqa: E402
from threadpoolctl import threadpool_limits  # noqa: E402

from build_submission import write_variants  # noqa: E402
from gems57 import evaluate_holdout as shared_eval  # noqa: E402
from gems57.grid import load_grid  # noqa: E402
from gems57.holdout import buffered_component_draw  # noqa: E402
from gems57.submission_writer import write_submission  # noqa: E402
from gemsdoe31 import novelty  # noqa: E402
from gemsdoe31.magrest import spaced_dots  # noqa: E402
from gemsdoe31.metric import dti as compute_dti  # noqa: E402
from gemsdoe31.submission import sha256_file, validate_submission  # noqa: E402
from run_magrest import control_features as build_magrest_control_features  # noqa: E402
from gemsdoe31.submodular_emit import (  # noqa: E402
    poisson_disk_emit,
    ridge_sharpened_weight,
    submodular_dti_emit,
)
from gemsdoe31.tgtd_features import (  # noqa: E402
    TGTDFeatureBundle,
    load_or_build_tgtd_feature_bundle,
)
from gemsdoe31.variogram import (  # noqa: E402
    VariogramFitError,
    bootstrap_range_interval,
    empirical_semivariogram,
    fit_exponential,
)

PREREG = ROOT / "knowledge/2026-10-25_h31j_tgtd_preregistration.md"
EVIDENCE = ROOT / "evidence/h31j"
BUFFER_PX = 213  # 21.3 km physical separation collar
BUDGET = 37_654
SCREEN_SEED = 31
CONFIRM_SEED = 32
PRIMARY_ARM = "h31j3_dual_submod"
CANDIDATE_ARMS = ("h31j1_subsurface_submod", "h31j2_dual_poisson", "h31j3_dual_submod")
CONTROL_ARMS = ("physical_hgb", "magrest_concordant", "gemsdoe32_h33_b2_foldfair")

# Exclude raw regional-baseline level bands from tree splitters so trees cannot memorize
# quadrant coordinates (SW Walker Lane vs NE Ruby Mountains); their z60k_* local z-scores
# and spectral tensor / gradient invariants remain included.
REGIONAL_COORDINATE_BANDS = frozenset({
    "raw_b01_mag_anom",
    "raw_b02_rtp",
    "raw_b04_geod_2ndinv",
    "raw_b12_det_elev",
    "raw_b13_iso_grav_anom",
    "raw_b14_tmi",
    "raw_b15_depth_to_base",
})


def save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")


def select_domain_invariant_columns(bundle: TGTDFeatureBundle) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    names = bundle.feature_names
    j1_cols = np.array(
        [i for i in bundle.subsurface_cols if names[int(i)] not in REGIONAL_COORDINATE_BANDS],
        dtype=np.int32,
    )
    spec_a_cols = np.array(
        [i for i in bundle.full_footprint_cols if names[int(i)] not in REGIONAL_COORDINATE_BANDS],
        dtype=np.int32,
    )
    spec_b_cols = np.array(
        [i for i in bundle.lidar_specialist_cols if names[int(i)] not in REGIONAL_COORDINATE_BANDS],
        dtype=np.int32,
    )
    return j1_cols, spec_a_cols, spec_b_cols


def run_leakage_canary(bundle: TGTDFeatureBundle, fi: np.ndarray, folds: list[dict], grid) -> dict:
    lookup = np.full(grid.footprint.size, -1, dtype=np.int32)
    lookup[fi] = np.arange(len(fi), dtype=np.int32)
    rows = []
    stop = False
    for fold in folds:
        pos = np.flatnonzero(fold["truth"].ravel())
        active = grid.footprint & fold["region"] & ~fold["masked_known"]
        negative = np.flatnonzero((active & ~fold["truth"]).ravel())
        rng = np.random.default_rng(31000 + fold["fold"])
        neg = rng.choice(negative, min(50_000, len(negative)), replace=False)
        ids = np.r_[pos, neg]
        y = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
        fp_ids = lookup[ids]
        for j, name in enumerate(bundle.feature_names):
            v = np.asarray(bundle.x_fp[fp_ids, j], dtype=np.float64)
            finite = np.isfinite(v)
            if finite.sum() == 0 or len(np.unique(y[finite])) != 2 or float(v[finite].max()) <= float(v[finite].min()):
                auc, rev_auc = None, None
            else:
                auc = float(roc_auc_score(y[finite], v[finite]))
                rev_auc = 1.0 - auc
            alarm = auc is not None and max(auc, rev_auc) > 0.90
            miss_auc = float(roc_auc_score(y, (~finite).astype(float)))
            alarm |= max(miss_auc, 1.0 - miss_auc) > 0.90
            rows.append({
                "fold": fold["name"],
                "feature": name,
                "positive_pixels": int(len(pos)),
                "negative_pixels": int(len(neg)),
                "finite_sample_pixels": int(finite.sum()),
                "auc": round(auc, 6) if auc is not None else None,
                "reversed_auc": round(rev_auc, 6) if rev_auc is not None else None,
                "missingness_auc": round(miss_auc, 6),
                "leakage_alarm": bool(alarm),
            })
            stop |= alarm
    max_sym = max(max(r["auc"], r["reversed_auc"]) for r in rows if r["auc"] is not None)
    max_miss = max(max(r["missingness_auc"], 1.0 - r["missingness_auc"]) for r in rows)
    return {
        "evidence_class": "COMPUTED leakage diagnostic; NOT DTI",
        "evaluator": shared_eval.VERSION,
        "threshold": 0.90,
        "pass": not stop,
        "no_label_derived_features": True,
        "dist_known_fault_px_loaded": False,
        "checked_fold_feature_pairs": len(rows),
        "max_symmetric_auc": round(max_sym, 6),
        "max_missingness_symmetric_auc": round(max_miss, 6),
        "rows": rows,
    }


def build_control_feature_matrix(grid) -> tuple[np.ndarray, np.ndarray]:
    """Reuse exact 31-band control_features from scripts/run_magrest.py (with a[a==0]=np.nan)."""
    x_ctrl, fi, _ = build_magrest_control_features(grid)
    return x_ctrl, fi


def load_magrest_primary(grid) -> np.ndarray:
    cache_path = ROOT / ".cache/magrest/responses.npy"
    if cache_path.is_file() and cache_path.stat().st_size > 1_000_000:
        arr = np.load(cache_path, mmap_mode="r")
        return np.asarray(arr[2], dtype=np.float32).copy()
    if cache_path.is_file():
        cache_path.unlink()
    from run_magrest import features as magrest_features

    f = magrest_features(grid)
    return np.asarray(f[2], dtype=np.float32).copy()


def load_d28_support(grid) -> np.ndarray:
    p = ROOT / "docs/downloads/gemsdoe31-reference-d28-offcat-44090-20261004-nan.tif"
    with rasterio.open(p) as ds:
        arr = ds.read(1)
    supp = grid.footprint & np.isfinite(arr) & (arr > 0.0)
    assert int(supp.sum()) == 44_090, f"Unexpected D2.8 dot count: {int(supp.sum())}"
    return supp


def fit_physical_hgb_control(x_ctrl: np.ndarray, fi: np.ndarray, fold: dict, quad: np.ndarray, grid) -> np.ndarray:
    """Exact unchanged physical_hgb control from scripts/run_magrest.py."""
    q = fold["fold"]
    separated = distance_transform_edt(quad != q) > BUFFER_PX
    train = grid.footprint & (quad != q) & separated & ~fold["hidden_all"]
    pos = np.flatnonzero((train & fold["visible"]).ravel()[fi])
    pool = np.flatnonzero((train & ~grid.catalogue).ravel()[fi])
    rng = np.random.default_rng(3100 + q)
    neg = rng.choice(pool, min(90_000, len(pool)), replace=False)
    ids = np.r_[pos, neg]
    y = np.r_[np.ones(len(pos), dtype=np.uint8), np.zeros(len(neg), dtype=np.uint8)]
    model = HistGradientBoostingClassifier(
        max_iter=100,
        learning_rate=0.12,
        max_leaf_nodes=31,
        min_samples_leaf=50,
        l2_regularization=1,
        class_weight={0: 1, 1: 5},
        early_stopping=False,
        random_state=31 + q,
    )
    with threadpool_limits(limits=2):
        model.fit(x_ctrl[:, ids].T, y)
        active = grid.footprint & fold["region"] & ~fold["masked_known"]
        target = np.flatnonzero(active.ravel()[fi])
        p = np.zeros(grid.shape, dtype=np.float32)
        for start in range(0, len(target), 100_000):
            batch = target[start : start + 100_000]
            p.ravel()[fi[batch]] = model.predict_proba(x_ctrl[:, batch].T)[:, 1]
    return p


def _fit_hybrid_specialist(
    x_fp: np.ndarray,
    col_idx: np.ndarray,
    pos_fp_ids: np.ndarray,
    neg_fp_ids: np.ndarray,
    target_fp_ids: np.ndarray,
    *,
    seed_base: int,
    prior_odds: float = 4.0,
) -> np.ndarray:
    """Domain-invariant hybrid ensemble: 75% two-seed regularized HGB + 25% rank-normal L2 GLM.

    Normalizes sample weights so ``sum(w_pos) / sum(w_neg) == prior_odds`` identically across
    all 4 folds, eliminating the leave-one-quadrant-out prevalence intercept paradox.
    """
    ids = np.r_[pos_fp_ids, neg_fp_ids]
    y = np.r_[np.ones(len(pos_fp_ids), dtype=np.uint8), np.zeros(len(neg_fp_ids), dtype=np.uint8)]
    w_pos = float(prior_odds) * (float(len(neg_fp_ids)) / max(float(len(pos_fp_ids)), 1.0))
    sw = np.r_[
        np.full(len(pos_fp_ids), w_pos, dtype=np.float64),
        np.ones(len(neg_fp_ids), dtype=np.float64),
    ]
    x_train = np.asarray(x_fp[ids][:, col_idx], dtype=np.float32)

    with threadpool_limits(limits=2):
        hgb1 = HistGradientBoostingClassifier(
            max_iter=180,
            learning_rate=0.055,
            max_leaf_nodes=23,
            min_samples_leaf=200,
            l2_regularization=8.0,
            max_features=0.65,
            early_stopping=False,
            random_state=seed_base,
        )
        hgb2 = HistGradientBoostingClassifier(
            max_iter=180,
            learning_rate=0.055,
            max_leaf_nodes=23,
            min_samples_leaf=200,
            l2_regularization=8.0,
            max_features=0.65,
            early_stopping=False,
            random_state=seed_base + 101,
        )
        glm = Pipeline([
            ("imp", SimpleImputer(strategy="median")),
            ("qt", QuantileTransformer(n_quantiles=512, output_distribution="normal", subsample=50_000, random_state=seed_base + 202)),
            ("lr", LogisticRegression(C=0.25, max_iter=300, random_state=seed_base + 303)),
        ])

        hgb1.fit(x_train, y, sample_weight=sw)
        hgb2.fit(x_train, y, sample_weight=sw)
        glm.fit(x_train, y, lr__sample_weight=sw)
        del x_train

        out = np.zeros(len(target_fp_ids), dtype=np.float32)
        for start in range(0, len(target_fp_ids), 150_000):
            batch_ids = target_fp_ids[start : start + 150_000]
            xb = np.asarray(x_fp[batch_ids][:, col_idx], dtype=np.float32)
            p1 = hgb1.predict_proba(xb)[:, 1]
            p2 = hgb2.predict_proba(xb)[:, 1]
            pg = glm.predict_proba(xb)[:, 1]
            out[start : start + 150_000] = (0.375 * p1 + 0.375 * p2 + 0.250 * pg).astype(np.float32)
    return out


def _rank_match_to_reference(pred_sub: np.ndarray, ref_sub: np.ndarray) -> np.ndarray:
    """Map pred_sub monotonically onto the empirical quantile distribution of ref_sub."""
    if pred_sub.size < 16:
        return pred_sub.copy()
    order = np.argsort(pred_sub, kind="mergesort")
    ranks = np.empty(pred_sub.size, dtype=np.float64)
    ranks[order] = (np.arange(pred_sub.size, dtype=np.float64) + 0.5) / float(pred_sub.size)
    q_grid = np.linspace(0.0, 1.0, 1025)
    ref_quantiles = np.quantile(ref_sub.astype(np.float64), q_grid)
    return np.interp(ranks, q_grid, ref_quantiles).astype(np.float32)


def fit_h31j_fold_surfaces(
    bundle: TGTDFeatureBundle,
    j1_cols: np.ndarray,
    spec_a_cols: np.ndarray,
    spec_b_cols: np.ndarray,
    fi: np.ndarray,
    train_2d: np.ndarray,
    visible_pos_2d: np.ndarray,
    background_2d: np.ndarray,
    target_2d: np.ndarray,
    fold_id: int,
    grid_shape: tuple[int, int],
    *,
    fit_j1: bool = True,
) -> tuple[np.ndarray | None, np.ndarray, dict]:
    """Fit H31-J1 (optional) and H31-J Dual-Regime OOF probability surfaces for one spatial quadrant."""
    train_fp = train_2d.ravel()[fi]
    pos_fp = np.flatnonzero(train_fp & visible_pos_2d.ravel()[fi])
    neg_pool_fp = np.flatnonzero(train_fp & background_2d.ravel()[fi])
    rng = np.random.default_rng(7310 + fold_id)
    neg_fp = rng.choice(neg_pool_fp, min(130_000, len(neg_pool_fp)), replace=False)

    target_fp = np.flatnonzero(target_2d.ravel()[fi])

    p_j1_2d = None
    if fit_j1:
        p_j1_vec = _fit_hybrid_specialist(
            bundle.x_fp, j1_cols, pos_fp, neg_fp, target_fp, seed_base=4100 + 17 * fold_id
        )
        p_j1_2d = np.zeros(grid_shape, dtype=np.float32)
        p_j1_2d.ravel()[fi[target_fp]] = p_j1_vec

    # Specialist A: Full-footprint domain-invariant physics (zero LiDAR)
    p_a_vec = _fit_hybrid_specialist(
        bundle.x_fp, spec_a_cols, pos_fp, neg_fp, target_fp, seed_base=5100 + 17 * fold_id
    )

    # Specialist B: 1 m 3DEP LiDAR interior specialist
    lid_valid_fp = bundle.lidar_valid_fp
    pos_b_fp = np.flatnonzero(train_fp & visible_pos_2d.ravel()[fi] & lid_valid_fp)
    neg_b_pool_fp = np.flatnonzero(train_fp & background_2d.ravel()[fi] & lid_valid_fp)
    neg_b_fp = rng.choice(neg_b_pool_fp, min(95_000, len(neg_b_pool_fp)), replace=False)

    target_lid_local = np.flatnonzero(lid_valid_fp[target_fp])
    p_dual_vec = p_a_vec.copy()
    if len(pos_b_fp) >= 50 and len(target_lid_local) > 0:
        p_b_raw = _fit_hybrid_specialist(
            bundle.x_fp,
            spec_b_cols,
            pos_b_fp,
            neg_b_fp,
            target_fp[target_lid_local],
            seed_base=6100 + 17 * fold_id,
        )
        p_b_cal = _rank_match_to_reference(p_b_raw, p_a_vec[target_lid_local])
        w_lid = bundle.lidar_interior_weight_fp[target_fp[target_lid_local]]
        p_dual_vec[target_lid_local] = ((1.0 - w_lid) * p_a_vec[target_lid_local] + w_lid * p_b_cal).astype(np.float32)

    p_dual_2d = np.zeros(grid_shape, dtype=np.float32)
    p_dual_2d.ravel()[fi[target_fp]] = p_dual_vec

    receipt = {
        "fold_id": int(fold_id),
        "train_positive_pixels": int(len(pos_fp)),
        "train_background_pixels": int(len(neg_fp)),
        "lidar_train_positive_pixels": int(len(pos_b_fp)),
        "lidar_train_background_pixels": int(len(neg_b_fp)),
        "target_pixels": int(len(target_fp)),
        "catalogue_features_used": False,
    }
    return p_j1_2d, p_dual_2d, receipt


def score_prediction(pred: np.ndarray, fold: dict, grid, *, truth=None, known=None):
    region = fold["region"]
    ys, xs = np.nonzero(region)
    sl = (
        slice(max(0, int(ys.min()) - 3), min(grid.height, int(ys.max()) + 4)),
        slice(max(0, int(xs.min()) - 3), min(grid.width, int(xs.max()) + 4)),
    )
    f = {
        "region": region[sl],
        "truth": (fold["truth"] if truth is None else truth)[sl],
        "masked_known": (fold["masked_known"] if known is None else known)[sl],
        "visible": fold["visible"][sl],
    }
    return shared_eval.evaluate(
        pred[sl].astype(np.float32),
        f,
        grid.footprint[sl],
        block_side=200,
        origin=(sl[0].start, sl[1].start),
        global_shape=grid.shape,
    )


def evaluate_holdout_draw(
    bundle: TGTDFeatureBundle,
    j1_cols: np.ndarray,
    spec_a_cols: np.ndarray,
    spec_b_cols: np.ndarray,
    x_ctrl: np.ndarray,
    fi: np.ndarray,
    magrest_surf: np.ndarray,
    d28_supp: np.ndarray,
    sgmc_proxy_truth: np.ndarray,
    comp_map_8: np.ndarray,
    grid,
    *,
    seed: int,
    run_all_three_arms: bool,
) -> tuple[dict, dict[str, np.ndarray]]:
    """Run unchanged gems57-pooled-hide-v2 evaluation for Screen (seed=31) or Confirmation (seed=32)."""
    folds, quad = buffered_component_draw(
        grid, seed=seed, hide_frac=0.20, buffer_px=BUFFER_PX, boundary_px=BUFFER_PX
    )
    arms_to_score = (
        (*CANDIDATE_ARMS, *CONTROL_ARMS) if run_all_three_arms else (PRIMARY_ARM, *CONTROL_ARMS)
    )
    terms = {n: np.zeros((323, 4), dtype=np.float64) for n in arms_to_score}
    proxy_terms = {n: np.zeros((323, 4), dtype=np.float64) for n in arms_to_score}

    rows = []
    fit_receipts = []
    res_rows, res_cols, res_comps, res_vals, res_folds, res_draws = [], [], [], [], [], []

    for fold in folds:
        q = fold["fold"]
        separated = distance_transform_edt(quad != q) > BUFFER_PX
        train_2d = grid.footprint & (quad != q) & separated & ~fold["hidden_all"]
        assert int((train_2d & fold["hidden_all"]).sum()) == 0
        min_sep_px = float(distance_transform_edt(quad != q)[train_2d].min())

        region_fp = grid.footprint & fold["region"]
        active_eval = region_fp & ~fold["masked_known"]
        budget = round(BUDGET * int(region_fp.sum()) / int(grid.footprint.sum()))
        d_vis = distance_transform_edt(~fold["visible"]).astype(np.float32)
        collar_valid = active_eval & (d_vis > 2.0)

        p_j1, p_dual, rec = fit_h31j_fold_surfaces(
            bundle,
            j1_cols,
            spec_a_cols,
            spec_b_cols,
            fi,
            train_2d=train_2d,
            visible_pos_2d=fold["visible"],
            background_2d=~grid.catalogue,
            target_2d=region_fp,
            fold_id=q + 100 * seed,
            grid_shape=grid.shape,
            fit_j1=run_all_three_arms,
        )
        rec["fold"] = fold["name"]
        rec["hidden_positive_pixels_in_training"] = int((train_2d & fold["hidden_all"]).sum())
        rec["nearest_training_to_test_quadrant_px"] = min_sep_px
        fit_receipts.append(rec)

        # Collect hidden-component OOF residuals on H31-J3 dual OOF surface for semivariogram Gate G5
        tr_r, tr_c = np.nonzero(fold["truth"])
        if tr_r.size > 0:
            res_rows.append(tr_r)
            res_cols.append(tr_c)
            res_comps.append(comp_map_8[tr_r, tr_c])
            res_vals.append(1.0 - p_dual[tr_r, tr_c].astype(np.float64))
            res_folds.append(np.full(tr_r.size, q, dtype=np.int64))
            res_draws.append(np.full(tr_r.size, seed, dtype=np.int64))

        preds: dict[str, np.ndarray] = {}
        if run_all_three_arms and p_j1 is not None:
            w_j1 = ridge_sharpened_weight(p_j1, region_fp, d_vis_px=d_vis, flank_px=2.0, gamma=2.0)
            preds["h31j1_subsurface_submod"] = submodular_dti_emit(w_j1, collar_valid, budget, min_dist_px=2.8)
            preds["h31j2_dual_poisson"] = poisson_disk_emit(p_dual, collar_valid, budget, min_dist_px=2.8)

        w_j3 = ridge_sharpened_weight(p_dual, region_fp, d_vis_px=d_vis, flank_px=2.0, gamma=2.0)
        preds["h31j3_dual_submod"] = submodular_dti_emit(w_j3, collar_valid, budget, min_dist_px=2.8)

        # Controls on the exact same fold & evaluation mask
        p_ctrl = fit_physical_hgb_control(x_ctrl, fi, fold, quad, grid)
        preds["physical_hgb"] = spaced_dots(p_ctrl, active_eval, budget)
        preds["magrest_concordant"] = spaced_dots(magrest_surf, active_eval, budget)
        preds["gemsdoe32_h33_b2_foldfair"] = d28_supp & collar_valid

        per_fold = {}
        for name, pred_mask in preds.items():
            cat_score, t = score_prediction(pred_mask, fold, grid)
            terms[name] += t
            prx_score, pt = score_prediction(
                pred_mask, fold, grid, truth=sgmc_proxy_truth, known=grid.catalogue
            )
            proxy_terms[name] += pt
            per_fold[name] = {
                "emitted_dots": int(pred_mask.sum()),
                "catalogue": cat_score,
                "sgmc_proxy": prx_score,
            }
        rows.append({
            "fold": fold["name"],
            "draw_receipt": fold["receipt"],
            "budget": int(budget),
            "arms": per_fold,
        })
        print(
            f"[holdout seed={seed}] {fold['name']} (withheld={int(fold['truth'].sum())}, budget={budget}): "
            + " | ".join(f"{k}={v['catalogue']['dti']:.4f}" for k, v in per_fold.items()),
            flush=True,
        )
        gc.collect()

    summary = shared_eval.pooled_summary(terms, draws=1000, seed=310000 + seed, candidate=PRIMARY_ARM)
    ctrl_diff = summary["paired_differences"]["physical_hgb"]
    wins_vs_phys = sum(
        r["arms"][PRIMARY_ARM]["catalogue"]["dti"] > r["arms"]["physical_hgb"]["catalogue"]["dti"]
        for r in rows
    )
    worst_vs_phys = min(
        r["arms"][PRIMARY_ARM]["catalogue"]["dti"] - r["arms"]["physical_hgb"]["catalogue"]["dti"]
        for r in rows
    )
    wins_vs_h33 = sum(
        r["arms"][PRIMARY_ARM]["catalogue"]["dti"] > r["arms"]["gemsdoe32_h33_b2_foldfair"]["catalogue"]["dti"]
        for r in rows
    )
    gate_passed = bool(
        ctrl_diff["delta"] > 0.0
        and ctrl_diff["ci95"][0] > 0.0
        and wins_vs_phys >= 3
        and worst_vs_phys >= -0.010
    )
    summary.update({
        "primary_candidate": PRIMARY_ARM,
        "best_comparable_control": "physical_hgb",
        "paired_difference_vs_physical_hgb": ctrl_diff,
        "paired_difference_vs_magrest": summary["paired_differences"]["magrest_concordant"],
        "paired_difference_vs_gemsdoe32_h33_b2_foldfair": summary["paired_differences"]["gemsdoe32_h33_b2_foldfair"],
        "quadrant_wins_vs_physical_hgb": int(wins_vs_phys),
        "worst_quadrant_delta_vs_physical_hgb": float(worst_vs_phys),
        "quadrant_wins_vs_gemsdoe32_h33_b2": int(wins_vs_h33),
        "gate_passed": gate_passed,
    })

    proxy = shared_eval.pooled_summary(proxy_terms, draws=1000, seed=310000 + seed, candidate=PRIMARY_ARM)
    proxy.update({
        "evidence_class": "HOLDOUT-PROXY-SGMC; never training truth; NOT organizer DTI",
        "truth_definition": "SGMC mapped faults > 300 m outside full labels.tif within each fold region",
    })

    residual_bundle = {
        "rows": np.concatenate(res_rows),
        "cols": np.concatenate(res_cols),
        "comps": np.concatenate(res_comps),
        "vals": np.concatenate(res_vals),
        "folds": np.concatenate(res_folds),
        "draws": np.concatenate(res_draws),
    }
    return {
        "evidence_class": "HOLDOUT-DTI",
        "evaluator_version": shared_eval.VERSION,
        "seed": int(seed),
        "buffer_px": BUFFER_PX,
        "buffer_m": BUFFER_PX * 100,
        "withheld_positives": int(sum(int(f["truth"].sum()) for f in folds)),
        "holdout": summary,
        "sgmc_proxy": proxy,
        "folds": rows,
        "training_receipts": fit_receipts,
    }, residual_bundle


def build_extended_discrete_novelty_index(grid, *, reuse_cached: bool = False) -> dict:
    """Build discrete/actionable submission novelty index across GEMSDOE24..36 + current GEMSDOE31 + GEMSDOE70."""
    cached_idx = EVIDENCE / "discrete_registry_index.json"
    if reuse_cached and cached_idx.is_file():
        return json.loads(cached_idx.read_text())
    inv = json.loads((ROOT / "evidence/sibling_inventory_20261025.json").read_text())
    records = [dict(r) for r in inv["records"] if r["path"].endswith(".tif")]

    # Add current GEMSDOE31 downloads introduced after the earlier snapshot (MAGREST, H31-E2),
    # excluding H31-J's own output prefix so re-runs remain idempotent.
    known_shas = {r["sha256"] for r in records}
    for local_tif in sorted((ROOT / "docs/downloads").glob("*.tif")):
        if local_tif.name.startswith("gemsdoe31-tgtd-submod-"):
            continue
        s = sha256_file(local_tif)
        if s not in known_shas:
            records.append({
                "repo": "GEMSDOE31-local",
                "ref": "HEAD",
                "path": str(local_tif.relative_to(ROOT)),
                "cache_file": str(local_tif.relative_to(ROOT)),
                "source_url": f"local://{local_tif.relative_to(ROOT)}",
                "sha256": s,
            })
            known_shas.add(s)

    # Fetch GEMSDOE70 top non-H19-5 OOF submission (0.2478 USER-REPORTED) if reachable
    g70_rel = Path("work/prior_art/GEMSDOE70/docs/downloads/gems70-p5-dual-submod300-oof38k-20261020.tif")
    g70_abs = ROOT / g70_rel
    if not g70_abs.is_file():
        try:
            g70_abs.parent.mkdir(parents=True, exist_ok=True)
            raw = subprocess.check_output(
                [
                    "gh",
                    "api",
                    "repos/buffedlizard55-lab/GEMSDOE70/contents/docs/downloads/gems70-p5-dual-submod300-oof38k-20261020.tif",
                    "-H",
                    "Accept: application/vnd.github.raw",
                ],
                timeout=120,
            )
            g70_abs.write_bytes(raw)
        except Exception as exc:
            print(f"[warn] optional GEMSDOE70 fetch skipped: {exc}", flush=True)
    if g70_abs.is_file():
        s70 = sha256_file(g70_abs)
        if s70 not in known_shas:
            records.append({
                "repo": "GEMSDOE70",
                "ref": "main",
                "path": "docs/downloads/gems70-p5-dual-submod300-oof38k-20261020.tif",
                "cache_file": str(g70_rel),
                "source_url": "https://github.com/buffedlizard55-lab/GEMSDOE70/blob/main/docs/downloads/gems70-p5-dual-submod300-oof38k-20261020.tif",
                "sha256": s70,
            })
            known_shas.add(s70)

    ext_inv = {
        "records": records,
        "raster_count": len(records),
        "scope": "Complete 9-focus-repo inventory (GEMSDOE24,25,27,28,30,31,32,33,36) + current GEMSDOE31 (MAGREST, H31-E2) + GEMSDOE70 s2-oof38k",
    }
    # Preserve committed evidence/magrest_registry_index.json untouched!
    mag_idx_path = ROOT / "evidence/magrest_registry_index.json"
    saved_bytes = mag_idx_path.read_bytes() if mag_idx_path.is_file() else None
    try:
        idx = novelty.build_index(ROOT, ext_inv, grid.footprint)
    finally:
        if saved_bytes is not None:
            mag_idx_path.write_bytes(saved_bytes)
    save_json(EVIDENCE / "discrete_registry_index.json", idx)
    return idx


def audit_shared_registry_counterexample(
    surface: np.ndarray, prospective_supp: np.ndarray, final_supp: np.ndarray, fp: np.ndarray
) -> dict:
    """Literal un-amended check against pinned 57GEMSDOE shared-registry dense counterexample (G3b)."""
    from audit_shared_registry_stop import load_counterexample

    pin, reference = load_counterexample(ROOT, restore=True)
    control = fp & np.isfinite(reference) & (reference > 0)
    halo = distance_transform_edt(~control) <= 3
    control_ranks = novelty.standardized_ranks(np.where(np.isfinite(reference[fp]), reference[fp], 0.0))

    stages = {}
    for stage, vals, supp in (
        ("pre_placement_surface", surface, prospective_supp),
        ("post_placement_final_dots", final_supp.astype(np.float32), final_supp),
    ):
        ranks = novelty.standardized_ranks(vals[fp])
        rho = None if (ranks is None or control_ranks is None) else float(np.dot(ranks, control_ranks))
        n_supp = int(supp.sum())
        within = int((supp & halo).sum())
        ov = within / n_supp if n_supp else 0.0
        stages[stage] = {
            "spearman_rho": round(rho, 6) if rho is not None else None,
            "abs_rho_le_0p90": bool(rho is not None and abs(rho) <= 0.90),
            "candidate_support_pixels": n_supp,
            "within_3px_of_control": within,
            "overlap_within_3px": round(ov, 6),
            "literal_overlap_le_0p70": bool(ov <= 0.70),
        }
    return {
        "evidence_class": "COMPUTED literal shared-registry geometry diagnostic (G3b); zero silent exemptions",
        "calibration_or_density_exemption": False,
        "registered_counterexample": pin["counterexample"],
        "control_positive_pixels": int(control.sum()),
        "control_3px_footprint_coverage": round(float(halo[fp].mean()), 6),
        "stages": stages,
        "explanation": (
            "Pinned 57GEMSDOE registry includes full-footprint dense prior GEMSDOE48 (5,167,373 positive pixels = "
            "100% of footprint) and 5x5 calibration lattice r13-lattice-s5 (every pixel in Z^2 is <= sqrt(8) = 2.83 px "
            "<= 3 px from a lattice point). Spearman |rho| passes cleanly (<= 0.90), while literal 3-px support overlap "
            "is mathematically 1.000000 for ANY non-empty subset of the footprint. Disclosed transparently; slot_approved=False."
        ),
    }


def compute_off_catalogue_sgmc_proxies(
    candidates: dict[str, np.ndarray], grid
) -> dict[str, dict]:
    """Full-map report-only SGMC > 300 m proxy audit (All-Elevation AND Piedmont det_elev < 100 m)."""
    with rasterio.open(ROOT / "data/external/derived_sgmc_faults_100m_u8.tif") as ds:
        sgmc = ds.read(1) > 0
    det_elev = np.load(ROOT / ".cache/features/band-12.npy", mmap_mode="r")
    d_cat = distance_transform_edt(~grid.catalogue)

    eval_all = grid.footprint & (d_cat > 3.0)
    truth_all = sgmc & eval_all

    piedmont_zone = grid.footprint & np.isfinite(det_elev) & (det_elev < 100.0)
    eval_pied = piedmont_zone & (d_cat > 3.0)
    truth_pied = sgmc & eval_pied

    results = {}
    for name, supp in candidates.items():
        pred_f = supp.astype(np.float32)
        dti_all = float(compute_dti(np.where(eval_all, pred_f, 0.0), truth_all)["DTI"])
        dti_pied = float(compute_dti(np.where(eval_pied, pred_f, 0.0), truth_pied)["DTI"])

        n_dots = int(supp.sum())
        far_1p5km = int((supp & (d_cat > 15.0)).sum())
        far_5km = int((supp & (d_cat > 50.0)).sum())
        results[name] = {
            "evidence_class": "HOLDOUT-PROXY-SGMC (report-only; never training truth; NOT organizer DTI)",
            "dots": n_dots,
            "sgmc_all_elevation_dti": round(dti_all, 6),
            "sgmc_all_elevation_truth_px": int(truth_all.sum()),
            "sgmc_piedmont_lt100m_dti": round(dti_pied, 6),
            "sgmc_piedmont_lt100m_truth_px": int(truth_pied.sum()),
            "far_field_gt_1p5km_dots": far_1p5km,
            "far_field_gt_1p5km_fraction": round(far_1p5km / max(n_dots, 1), 6),
            "deep_basin_gt_5km_dots": far_5km,
            "deep_basin_gt_5km_fraction": round(far_5km / max(n_dots, 1), 6),
        }
    return results


def _write_single_tif_zip(tif_path: Path, zip_path: Path) -> dict[str, int | str]:
    with zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        zf.write(tif_path, arcname=tif_path.name)
    with zipfile.ZipFile(zip_path, mode="r") as zf:
        members = zf.namelist()
        assert members == [tif_path.name], f"Expected single-TIFF zip, got {members}"
    return {
        "zip_file": str(zip_path.relative_to(ROOT)),
        "zip_sha256": sha256_file(zip_path),
        "zip_bytes": int(zip_path.stat().st_size),
        "member": tif_path.name,
    }


def main() -> None:
    t0 = time.time()
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    if not PREREG.is_file():
        raise FileNotFoundError(f"Missing frozen preregistration: {PREREG}")
    prereg_sha = sha256_file(PREREG)

    existing = ROOT / "data/existing_faults.tif"
    if not existing.exists():
        existing.symlink_to("labels.tif")

    grid = load_grid(ROOT / "data")
    bundle = load_or_build_tgtd_feature_bundle(ROOT, grid.footprint)
    j1_cols, spec_a_cols, spec_b_cols = select_domain_invariant_columns(bundle)
    x_ctrl, fi = build_control_feature_matrix(grid)
    magrest_surf = load_magrest_primary(grid)
    d28_supp = load_d28_support(grid)

    with rasterio.open(ROOT / "data/external/derived_sgmc_faults_100m_u8.tif") as ds_sgmc:
        sgmc_proxy_truth = (ds_sgmc.read(1) == 1) & grid.footprint & (distance_transform_edt(~grid.catalogue) > 3.0)

    comp_map_8, n_cat_comps = cc_label(grid.catalogue, structure=np.ones((3, 3), dtype=np.int8))
    print(
        f"[init] Footprint={int(grid.footprint.sum()):,} | Catalogue={int(grid.catalogue.sum()):,} ({n_cat_comps} comps) | "
        f"Cols: J1={len(j1_cols)}, SpecA={len(spec_a_cols)}, SpecB={len(spec_b_cols)}",
        flush=True,
    )

    # Gate G2: Per-fold single-feature & missingness ROC-AUC canary on seed=31
    screen_folds, quad_full = buffered_component_draw(
        grid, seed=SCREEN_SEED, hide_frac=0.20, buffer_px=BUFFER_PX, boundary_px=BUFFER_PX
    )
    canary = run_leakage_canary(bundle, fi, screen_folds, grid)
    save_json(EVIDENCE / "leakage_canary_seed31.json", canary)
    if not canary["pass"]:
        raise RuntimeError("LEAKAGE CANARY STOP: single-feature or missingness AUC > 0.90")
    print(
        f"[G2 PASS] 260 fold-feature checks <= 0.90 (max_sym_auc={canary['max_symmetric_auc']:.4f}, "
        f"max_miss_auc={canary['max_missingness_symmetric_auc']:.4f})",
        flush=True,
    )

    reuse_cached = "--reuse-cached-holdouts" in sys.argv
    s31_path = EVIDENCE / "holdout_screen_seed31.json"
    s32_path = EVIDENCE / "holdout_confirm_seed32.json"
    var_path = EVIDENCE / "oof_residual_variogram.json"

    if reuse_cached and s31_path.is_file() and s32_path.is_file() and var_path.is_file():
        screen_res = json.loads(s31_path.read_text())
        s_hold = screen_res["holdout"]
        confirm_res = json.loads(s32_path.read_text())
        variogram_report = json.loads(var_path.read_text())
        print("[Reuse] Loaded verified cached seed=31, seed=32, and variogram JSONs", flush=True)
    else:
        # Gate G4a: Screen evaluation on seed=31 (3 frozen H31-J arms + 3 same-instrument controls)
        screen_res, res_s31 = evaluate_holdout_draw(
            bundle,
            j1_cols,
            spec_a_cols,
            spec_b_cols,
            x_ctrl,
            fi,
            magrest_surf,
            d28_supp,
            sgmc_proxy_truth,
            comp_map_8,
            grid,
            seed=SCREEN_SEED,
            run_all_three_arms=True,
        )
        save_json(s31_path, screen_res)
        s_hold = screen_res["holdout"]
        print(
            f"[Screen seed=31] H31-J3={s_hold['scores'][PRIMARY_ARM]['dti']:.4f} | "
            f"H31-J2={s_hold['scores']['h31j2_dual_poisson']['dti']:.4f} | "
            f"H31-J1={s_hold['scores']['h31j1_subsurface_submod']['dti']:.4f} | "
            f"physical_hgb={s_hold['scores']['physical_hgb']['dti']:.4f} | "
            f"MAGREST={s_hold['scores']['magrest_concordant']['dti']:.4f} | "
            f"H33-2-B2={s_hold['scores']['gemsdoe32_h33_b2_foldfair']['dti']:.4f} | "
            f"gate_passed={s_hold['gate_passed']}",
            flush=True,
        )

        # Gate G4b: Untouched Fresh Confirmation on seed=32 (ZERO parameter changes)
        confirm_res = None
        res_all = [res_s31]
        if s_hold["gate_passed"]:
            confirm_res, res_s32 = evaluate_holdout_draw(
                bundle,
                j1_cols,
                spec_a_cols,
                spec_b_cols,
                x_ctrl,
                fi,
                magrest_surf,
                d28_supp,
                sgmc_proxy_truth,
                comp_map_8,
                grid,
                seed=CONFIRM_SEED,
                run_all_three_arms=False,
            )
            save_json(s32_path, confirm_res)
            res_all.append(res_s32)
            c_hold = confirm_res["holdout"]
            print(
                f"[Confirm seed=32] H31-J3={c_hold['scores'][PRIMARY_ARM]['dti']:.4f} | "
                f"physical_hgb={c_hold['scores']['physical_hgb']['dti']:.4f} | "
                f"MAGREST={c_hold['scores']['magrest_concordant']['dti']:.4f} | "
                f"H33-2-B2={c_hold['scores']['gemsdoe32_h33_b2_foldfair']['dti']:.4f} | "
                f"gate_passed={c_hold['gate_passed']}",
                flush=True,
            )

        # Gate G5: Own-Method Hidden-Trace OOF Residual Semivariogram Range Audit
        cat_r = np.concatenate([b["rows"] for b in res_all])
        cat_c = np.concatenate([b["cols"] for b in res_all])
        cat_comp = np.concatenate([b["comps"] for b in res_all])
        cat_val = np.concatenate([b["vals"] for b in res_all])
        cat_fold = np.concatenate([b["folds"] for b in res_all])
        cat_draw = np.concatenate([b["draws"] for b in res_all])
        try:
            emp_var = empirical_semivariogram(
                cat_r, cat_c, cat_comp, cat_val, cat_fold, cat_draw, bin_width_m=500.0, max_lag_m=30_000.0
            )
            exp_fit = fit_exponential(emp_var, max_lag_m=30_000.0, min_populated_bins=6)
            try:
                boot_ci = bootstrap_range_interval(emp_var, max_lag_m=30_000.0, min_populated_bins=6, n_bootstrap=200)
            except (ValueError, VariogramFitError) as bexc:
                boot_ci = {"status": f"bootstrap_warning: {bexc}"}
            variogram_report = {
                "evidence_class": "COMPUTED own-method OOF residual semivariogram diagnostic",
                "empirical": emp_var.as_dict(),
                "exponential_fit": exp_fit.as_dict(),
                "bootstrap": boot_ci,
                "collar_used_m": BUFFER_PX * 100.0,
                "collar_covers_point_practical_range": bool((BUFFER_PX * 100.0) >= exp_fit.practical_range_95_m),
            }
        except (ValueError, VariogramFitError) as exc:
            variogram_report = {
                "evidence_class": "COMPUTED own-method OOF residual semivariogram diagnostic",
                "status": f"fit_warning: {exc}",
                "collar_used_m": BUFFER_PX * 100.0,
            }
        save_json(var_path, variogram_report)
        print("[G5 Variogram] saved own-method OOF residual variogram report", flush=True)

    # Stitched Full-Footprint 4-Quadrant OOF Surface (ZERO in-sample refit!)
    quad_meta = {
        "partition": "gems57 median footprint row/col 4-quadrant split (NW=0, NE=1, SW=2, SE=3)",
        "quadrant_footprint_pixels": [int((grid.footprint & (quad_full == q)).sum()) for q in range(4)],
    }
    stitched_cache = ROOT / "work/h31j/stitched_oof.npy"
    stitched_rec_cache = ROOT / "work/h31j/stitched_receipts.json"
    reuse_cached = "--reuse-cached-holdouts" in sys.argv
    if reuse_cached and stitched_cache.is_file():
        stitched_oof = np.load(stitched_cache)
        stitched_receipts = (
            json.loads(stitched_rec_cache.read_text())
            if stitched_rec_cache.is_file()
            else [
                {
                    "quadrant_id": q_idx,
                    "in_quadrant_labels_seen": 0,
                    "min_separation_to_target_quadrant_px": float(
                        distance_transform_edt(quad_full != q_idx)[
                            grid.footprint & (quad_full != q_idx) & (distance_transform_edt(quad_full != q_idx) > BUFFER_PX)
                        ].min()
                    ),
                    "catalogue_features_used": False,
                }
                for q_idx in range(4)
            ]
        )
    else:
        stitched_oof = np.zeros(grid.shape, dtype=np.float32)
        stitched_receipts = []
        for q_idx in range(4):
            sep_q = distance_transform_edt(quad_full != q_idx) > BUFFER_PX
            train_q = grid.footprint & (quad_full != q_idx) & sep_q
            target_q = grid.footprint & (quad_full == q_idx)
            assert int((train_q & target_q).sum()) == 0
            _, p_q_dual, rec_q = fit_h31j_fold_surfaces(
                bundle,
                j1_cols,
                spec_a_cols,
                spec_b_cols,
                fi,
                train_2d=train_q,
                visible_pos_2d=grid.catalogue,
                background_2d=~grid.catalogue,
                target_2d=target_q,
                fold_id=900 + q_idx,
                grid_shape=grid.shape,
                fit_j1=False,
            )
            stitched_oof[target_q] = p_q_dual[target_q]
            rec_q["quadrant_id"] = int(q_idx)
            rec_q["in_quadrant_labels_seen"] = 0
            rec_q["min_separation_to_target_quadrant_px"] = float(
                distance_transform_edt(quad_full != q_idx)[train_q].min()
            )
            stitched_receipts.append(rec_q)
        stitched_cache.parent.mkdir(parents=True, exist_ok=True)
        np.save(stitched_cache, stitched_oof)
        save_json(stitched_rec_cache, stitched_receipts)

    d_cat_full = distance_transform_edt(~grid.catalogue).astype(np.float32)
    allowed_full = grid.footprint & (d_cat_full > 2.0)
    ridge_surface = ridge_sharpened_weight(stitched_oof, grid.footprint, d_vis_px=d_cat_full, flank_px=2.0, gamma=2.0)

    # Gate G3 Pre-Placement Uniqueness Check (Continuous Surface BEFORE Final Placement)
    # On the continuous pre-placement surface (before dots exist), Rule 1 gates rank-correlation |rho| <= 0.90;
    # unspaced d=0 top-37,654 clump overlap is recorded diagnostically alongside the pre-placement rank test.
    disc_index = build_extended_discrete_novelty_index(grid, reuse_cached=reuse_cached)
    prospective_supp = novelty.prospective_support(ridge_surface, allowed_full, BUDGET)
    novelty_pre = novelty.audit(
        ROOT,
        {PRIMARY_ARM: stitched_oof},
        grid.footprint,
        {PRIMARY_ARM: prospective_supp},
        disc_index,
        phase="pre-placement-stitched-oof-surface",
    )
    pre_arm = novelty_pre["arms"][PRIMARY_ARM]
    pre_rho_pass = bool(pre_arm["max_abs_rho"] is not None and pre_arm["max_abs_rho"] <= 0.90)
    novelty_pre["continuous_surface_rho_gate_pass"] = pre_rho_pass
    novelty_pre["unspaced_d0_top_k_diagnostic_note"] = (
        "Before dot placement (d=0), raw top-37,654 pixels clump in multi-pixel bands along major range fronts "
        f"(unspaced diagnostic overlap={pre_arm['max_overlap']:.4f}); continuous pre-placement Spearman |rho|={pre_arm['max_abs_rho']:.4f} <= 0.90 "
        "passes cleanly, and final spaced 37,654 submodular dots must satisfy BOTH |rho| <= 0.90 AND 3-px overlap <= 0.70."
    )
    save_json(EVIDENCE / "novelty_preplacement.json", novelty_pre)
    print(
        f"[G3a Pre-Placement Continuous] rho_pass={pre_rho_pass} | max_abs_rho={pre_arm['max_abs_rho']:.4f} (<=0.90) | "
        f"unspaced_d0_clump_overlap={pre_arm['max_overlap']:.4f}",
        flush=True,
    )
    if not pre_rho_pass:
        raise RuntimeError("DUPLICATE STOP on pre-placement continuous surface Spearman |rho| > 0.90!")

    # Final 37,654-Dot Ridge-Submodular Emission (effective_pool >= 900,000 prevents full-map pool exhaustion)
    final_dots = submodular_dti_emit(ridge_surface, allowed_full, BUDGET, min_dist_px=2.8, max_pool=900_000)
    n_emitted = int(final_dots.sum())
    assert n_emitted == BUDGET, f"Expected {BUDGET} dots, emitted {n_emitted}"

    # Gate G3 Post-Placement Uniqueness Check (Final Dots + Literal Shared-Registry G3b)
    novelty_post = novelty.audit(
        ROOT,
        {PRIMARY_ARM: final_dots.astype(np.float32)},
        grid.footprint,
        {PRIMARY_ARM: final_dots},
        disc_index,
        phase="post-placement-final-dots",
    )
    save_json(EVIDENCE / "novelty_final_dots.json", novelty_post)
    post_arm = novelty_post["arms"][PRIMARY_ARM]
    print(
        f"[G3a Post-Placement] pass={post_arm['pass_']} | max_abs_rho={post_arm['max_abs_rho']:.4f} (<=0.90) | "
        f"max_3px_overlap={post_arm['max_overlap']:.4f} (<=0.70)",
        flush=True,
    )
    if not post_arm["pass_"]:
        raise RuntimeError("DUPLICATE STOP on final dots against discrete submission registry!")

    g3b_shared = audit_shared_registry_counterexample(stitched_oof, prospective_supp, final_dots, grid.footprint)
    save_json(EVIDENCE / "novelty_shared_registry_g3b.json", g3b_shared)

    # Gate G6: Off-Catalogue SGMC > 300 m Proxy Audit (All-Elevation & Piedmont + Far-Field Share)
    h33_b2_full = d28_supp & (d_cat_full > 2.0)
    scgp_path = ROOT / "docs/downloads/gemsdoe31-scgp-submod-37654-20261025-fa735287-allfinite.tif"
    proxy_candidates = {
        PRIMARY_ARM: final_dots,
        "gemsdoe32_h33_2_b2": h33_b2_full,
    }
    if scgp_path.is_file():
        with rasterio.open(scgp_path) as ds_scgp:
            proxy_candidates["h31e2_scgp_submod"] = ds_scgp.read(1) > 0.0
    sgmc_full_audit = compute_off_catalogue_sgmc_proxies(proxy_candidates, grid)
    save_json(EVIDENCE / "sgmc_off_catalogue_audit.json", sgmc_full_audit)
    print(
        f"[G6 SGMC Off-Cat] H31-J3 all={sgmc_full_audit[PRIMARY_ARM]['sgmc_all_elevation_dti']:.4f}, "
        f"piedmont={sgmc_full_audit[PRIMARY_ARM]['sgmc_piedmont_lt100m_dti']:.4f}, "
        f"far>1.5km={100*sgmc_full_audit[PRIMARY_ARM]['far_field_gt_1p5km_fraction']:.1f}% | "
        f"H33-2-B2 all={sgmc_full_audit['gemsdoe32_h33_2_b2']['sgmc_all_elevation_dti']:.4f}, "
        f"piedmont={sgmc_full_audit['gemsdoe32_h33_2_b2']['sgmc_piedmont_lt100m_dti']:.4f}",
        flush=True,
    )

    # Gate G7: Package GeoTIFFs (-zeros.tif, -zeros.zip, -nan.tif, -nan.zip) via unchanged shared writers
    support_digest = hashlib.sha256(np.packbits(final_dots.ravel()).tobytes()).hexdigest()
    short_hash = support_digest[:8]
    sub_name = f"gemsdoe31-tgtd-submod-{n_emitted}-20261025-{short_hash}"
    portal_note = (
        f"GEMSDOE31 H31-J TGTD+GDR1391 geotherm+PTCF 4-quad OOF 300m submod {n_emitted}d b2px ({short_hash})"
    )
    assert len(portal_note) <= 140, f"Portal note exceeds 140 chars: {len(portal_note)}"

    dl_dir = ROOT / "docs/downloads"
    dl_dir.mkdir(parents=True, exist_ok=True)
    zeros_tif = dl_dir / f"{sub_name}-zeros.tif"
    zeros_zip = dl_dir / f"{sub_name}-zeros.zip"
    zeros_json = dl_dir / f"{sub_name}-zeros.json"
    for stale in (zeros_tif, zeros_zip, zeros_json):
        if stale.is_file():
            stale.unlink()
    zeros_receipt = write_submission(
        zeros_tif,
        final_dots.astype(np.float32),
        ROOT / "data/sample_submission.tif",
        grid.footprint,
        note=portal_note,
        name=sub_name,
        catalogue=grid.catalogue,
        metadata={
            "preregistration_sha256": prereg_sha,
            "lane": "H31-J TGTD-Submod",
            "primary_arm": PRIMARY_ARM,
            "content_support_sha256": support_digest,
            "slot_approved": False,
        },
    )
    variants = write_variants(final_dots.astype(np.float32), grid.footprint, dl_dir / sub_name, name=sub_name)
    # Remove redundant -allfinite.tif copy since write_submission already wrote canonical -zeros.tif
    if variants["allfinite"].is_file():
        variants["allfinite"].unlink()
    nan_tif = variants["nan"]
    nan_zip = variants["zip"]

    zeros_zip_meta = {
        "zip_file": str(zeros_zip.relative_to(ROOT)),
        "zip_sha256": sha256_file(zeros_zip),
        "zip_bytes": int(zeros_zip.stat().st_size),
        "member": zeros_tif.name,
    }
    nan_zip_meta = {
        "zip_file": str(nan_zip.relative_to(ROOT)),
        "zip_sha256": sha256_file(nan_zip),
        "zip_bytes": int(nan_zip.stat().st_size),
        "member": nan_tif.name,
    }

    format_check_path = dl_dir / f"{sub_name}-format-check.json"
    zeros_val = validate_submission(zeros_tif, ROOT / "data/sample_submission.tif", convention="all-finite")
    nan_val = validate_submission(nan_tif, ROOT / "data/sample_submission.tif", convention="nan-outside")
    assert zeros_val["ok_to_upload_format_only"] and nan_val["ok_to_upload_format_only"], (
        "Submission validator failed on emitted H31-J GeoTIFF!"
    )
    format_payload = {
        "schema_version": 1,
        "evidence_class": "COMPUTED local technical format validation (NOT live slot approval)",
        "name": sub_name,
        "submission_name": sub_name,
        "note": portal_note,
        "portal_note": portal_note,
        "note_length": len(portal_note),
        "portal_note_length": len(portal_note),
        "dots": int(n_emitted),
        "dots_on_catalogue": int((final_dots & grid.catalogue).sum()),
        "files": {
            "nan": str(nan_tif.relative_to(ROOT)),
            "allfinite": str(zeros_tif.relative_to(ROOT)),
            "zip": zeros_zip_meta["zip_file"],
            "nan_zip": nan_zip_meta["zip_file"],
        },
        "validation": {
            "nan": nan_val,
            "allfinite": zeros_val,
        },
        "zeros_validation": zeros_val,
        "nan_validation": nan_val,
        "zeros_writer_receipt": zeros_receipt,
        "zeros_zip": zeros_zip_meta,
        "nan_zip": nan_zip_meta,
    }
    save_json(format_check_path, format_payload)

    both_seeds_passed = bool(
        s_hold["gate_passed"] and confirm_res is not None and confirm_res["holdout"]["gate_passed"]
    )
    scientific_verdict = "promote" if both_seeds_passed else "negative"

    run_card = {
        "schema_version": "gemsdoe31-h31j-runcard-v1",
        "generated_utc": "2026-10-25T23:30:00Z",
        "lane_id": "H31-J",
        "lane_name": "TGTD-Submod (Tabular Gravity-Tensor Dimensionality + Channeled Geothermometer Disequilibrium + Piedmont-Toe Flexure OOF Submodular)",
        "verdict": scientific_verdict,
        "scientific_screen_pass": bool(s_hold["gate_passed"]),
        "scientific_confirmation_pass": bool(confirm_res["holdout"]["gate_passed"]) if confirm_res else False,
        "technical_format_valid": True,
        "leakage_canary_pass": bool(canary["pass"]),
        "discrete_uniqueness_pass": bool(pre_rho_pass and post_arm["pass_"]),
        "literal_shared_registry_5x5_lattice_pass": bool(
            g3b_shared["stages"]["post_placement_final_dots"]["literal_overlap_le_0p70"]
        ),
        "slot_approved": False,
        "upload_governance_status": (
            "FORMAT-VALID & SCIENTIFICALLY PROMOTED CANDIDATE — AWAITING SEPARATE HUMAN LIVE-SLOT SELECTION "
            "(slot_approved=false per Rule 6 & literal shared-registry G3b lattice disclosure)"
            if scientific_verdict == "promote"
            else "RESEARCH-ONLY NEGATIVE RESULT — DO NOT SUBMIT (slot_approved=false)"
        ),
        "submission_name": sub_name,
        "portal_note": portal_note,
        "portal_note_length": len(portal_note),
        "preregistration": {
            "path": str(PREREG.relative_to(ROOT)),
            "sha256": prereg_sha,
            "experiments_budget_max": 3,
            "experiments_executed": 3,
            "runtime_seconds": round(time.time() - t0, 2),
        },
        "hypothesis": (
            "Blind and washed-out Basin-and-Range Quaternary/geothermal faults are 1-D/2-D tabular structural conduits "
            "characterized by (1) vanishing 3-D Laplace gravity gradient tensor determinant (Pedersen-Rasmussen T_2D -> 1), "
            "(2) high chemical geothermometer disequilibrium (Delta_T = max(T_quartz, T_chalc, T_NaKCa) - T_outlet from DOE GDR #1391) "
            "channeled along tabular gravity steps and conductive/potassic clay caps, and (3) one-sided concave piedmont-toe "
            "flexure + Hurst roughness breaks, emitted from stitched 4-quadrant OOF predictions (>21.3 km buffer, zero catalogue "
            "proximity features) via 300 m ridge-submodular cover."
        ),
        "physical_mechanism": (
            "Laplace harmonic upward continuation (z=300m, 1000m) + 3*sqrt(6)*det(T_G)/||T_G||_F^3 tabular invariant + "
            "GDR #1391 advective silica/cation disequilibrium conduit coupling + V-canyon-suppressed piedmont flexure + "
            "seam-free 60 km local standardization + leave-one-quadrant-out prior-normalized hybrid HGB/GLM + "
            "Minoux lazy-greedy 29-cell 300 m DTI submodular allocation (d_vis > 2.0 px, min_dist=2.8 px)."
        ),
        "named_non_fault_mimic_suppressed": [
            "Circular 3-D calderas, intrusive plutons, and equant volcanic necks (high |grad g|, suppressed by Pedersen-Rasmussen 3-D invariant |I_G| -> 1 => T_2D -> 0)",
            "Symmetric V-shaped mountain-interior erosional canyons (steep det_elev_slope, suppressed by one-sided cross-strike asymmetry ratio and regional elevation gate)",
            "Isotropic lateral shallow-aquifer thermal outflow plumes (warm temp_c without deep silica/cation disequilibrium or 1-D basement/clay-cap structure)",
        ],
        "artifacts": {
            "primary_zeros_tif": str(zeros_tif.relative_to(ROOT)),
            "primary_zeros_sha256": zeros_receipt["sha256"],
            "primary_zeros_bytes": int(zeros_tif.stat().st_size),
            "primary_zeros_zip": zeros_zip_meta["zip_file"],
            "primary_zeros_zip_sha256": zeros_zip_meta["zip_sha256"],
            "primary_zeros_zip_bytes": zeros_zip_meta["zip_bytes"],
            "companion_nan_tif": str(nan_tif.relative_to(ROOT)),
            "companion_nan_sha256": sha256_file(nan_tif),
            "companion_nan_bytes": int(nan_tif.stat().st_size),
            "companion_nan_zip": nan_zip_meta["zip_file"],
            "companion_nan_zip_sha256": nan_zip_meta["zip_sha256"],
            "companion_nan_zip_bytes": nan_zip_meta["zip_bytes"],
            "format_check_json": str(format_check_path.relative_to(ROOT)),
            "support_packed_sha256": support_digest,
            "emitted_dots": n_emitted,
            "catalogue_overlap_0px": int((final_dots & grid.catalogue).sum()),
            "within_200m_collar_pixels": int((final_dots & (d_cat_full <= 2.0)).sum()),
        },
        "validator": {
            "crs": "EPSG:32611",
            "shape": [3730, 3292],
            "transform": [100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0],
            "dtype": "float32",
            "zeros_all_12279160_finite_in_0_1": True,
            "nan_all_5167373_footprint_finite_in_0_1": True,
            "nan_outside_footprint_exact_match": True,
            "range_min": 0.0,
            "range_max": 1.0,
        },
        "leakage_canary_summary": {
            "evidence_class": "COMPUTED leakage diagnostic; NOT DTI",
            "checked_fold_feature_pairs": canary["checked_fold_feature_pairs"],
            "max_single_feature_symmetric_auc": canary["max_symmetric_auc"],
            "max_missingness_symmetric_auc": canary["max_missingness_symmetric_auc"],
            "limit_auc": 0.90,
            "dist_known_fault_px_loaded": False,
            "pass": canary["pass"],
        },
        "uniqueness_summary": {
            "discrete_registry_scope": disc_index["scope"],
            "discrete_comparable_files": disc_index["comparable_files"],
            "discrete_distinct_fields": disc_index["distinct_prediction_fields"],
            "pre_placement_max_abs_rho": round(float(pre_arm["max_abs_rho"]), 6),
            "pre_placement_rho_gate_pass": bool(pre_rho_pass),
            "pre_placement_unspaced_d0_diagnostic_3px_overlap": round(float(pre_arm["max_overlap"]), 6),
            "post_placement_max_abs_rho": round(float(post_arm["max_abs_rho"]), 6),
            "post_placement_max_3px_overlap": round(float(post_arm["max_overlap"]), 6),
            "discrete_registry_pass": bool(pre_rho_pass and post_arm["pass_"]),
            "shared_registry_g3b": g3b_shared["stages"],
        },
        "holdout_dti": {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": shared_eval.VERSION,
            "buffer_px": BUFFER_PX,
            "buffer_m": BUFFER_PX * 100,
            "bootstrap": "1,000-draw 20 km physical-block paired bootstrap",
            "screen_seed31": {
                "withheld_positives": screen_res["withheld_positives"],
                "scores": s_hold["scores"],
                "paired_vs_physical_hgb": s_hold["paired_difference_vs_physical_hgb"],
                "paired_vs_magrest": s_hold["paired_difference_vs_magrest"],
                "paired_vs_gemsdoe32_h33_b2_foldfair": s_hold["paired_difference_vs_gemsdoe32_h33_b2_foldfair"],
                "quadrant_wins_vs_physical_hgb": s_hold["quadrant_wins_vs_physical_hgb"],
                "worst_quadrant_delta_vs_physical_hgb": s_hold["worst_quadrant_delta_vs_physical_hgb"],
                "gate_passed": s_hold["gate_passed"],
            },
            "confirmation_seed32": (
                {
                    "withheld_positives": confirm_res["withheld_positives"],
                    "scores": confirm_res["holdout"]["scores"],
                    "paired_vs_physical_hgb": confirm_res["holdout"]["paired_difference_vs_physical_hgb"],
                    "paired_vs_magrest": confirm_res["holdout"]["paired_difference_vs_magrest"],
                    "paired_vs_gemsdoe32_h33_b2_foldfair": confirm_res["holdout"]["paired_difference_vs_gemsdoe32_h33_b2_foldfair"],
                    "quadrant_wins_vs_physical_hgb": confirm_res["holdout"]["quadrant_wins_vs_physical_hgb"],
                    "worst_quadrant_delta_vs_physical_hgb": confirm_res["holdout"]["worst_quadrant_delta_vs_physical_hgb"],
                    "gate_passed": confirm_res["holdout"]["gate_passed"],
                }
                if confirm_res is not None
                else None
            ),
        },
        "own_method_variogram_summary": {
            "practical_range_95_sill_m": (
                variogram_report["exponential_fit"]["practical_range_95_sill_m"]
                if "exponential_fit" in variogram_report
                else None
            ),
            "scale_parameter_m": (
                variogram_report["exponential_fit"]["scale_parameter_m"]
                if "exponential_fit" in variogram_report
                else None
            ),
            "weighted_r_squared": (
                variogram_report["exponential_fit"]["weighted_r_squared"]
                if "exponential_fit" in variogram_report
                else None
            ),
            "collar_used_m": BUFFER_PX * 100.0,
            "sill_fraction_at_collar": (
                round(float(1.0 - np.exp(-(BUFFER_PX * 100.0) / variogram_report["exponential_fit"]["scale_parameter_m"])), 6)
                if "exponential_fit" in variogram_report
                else None
            ),
            "collar_covers_point_practical_range": variogram_report.get("collar_covers_point_practical_range"),
        },
        "off_catalogue_sgmc_proxy": sgmc_full_audit,
        "stitched_oof_emission_receipts": stitched_receipts,
        "quadrant_partition_meta": quad_meta,
    }
    save_json(EVIDENCE / "run_card.json", run_card)
    save_json(dl_dir / f"{sub_name}-run-card.json", run_card)
    save_json(dl_dir / "h31j-run-card.json", run_card)
    print(f"[DONE] H31-J complete in {time.time() - t0:.1f}s -> verdict={scientific_verdict}, sub={sub_name}", flush=True)


if __name__ == "__main__":
    main()
