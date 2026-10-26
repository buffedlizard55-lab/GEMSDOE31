#!/usr/bin/env python3
"""Execute the preregistered 3-experiment H31-S (UDAP-SSLIC) campaign on gems57-pooled-hide-v2."""

from __future__ import annotations

import gc
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import rankdata
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "vendor"), str(ROOT / "scripts")]

from gems57 import evaluate_holdout as shared_eval  # noqa: E402
from gems57.grid import Grid  # noqa: E402
from gems57.holdout import buffered_component_draw, quadrant_ids  # noqa: E402
from gems57.submission_writer import write_submission  # noqa: E402
from gemsdoe31.buffer import (  # noqa: E402
    component_bootstrap,
    decide_buffer_m,
    empirical_variogram,
    fit_models,
)
from gemsdoe31.h31s_features import build_h31s_stage1_stack, compute_sslic_channels  # noqa: E402
from gemsdoe31.magrest import spaced_dots  # noqa: E402
from gemsdoe31.metric import dti  # noqa: E402
from gemsdoe31.raster import connected_components  # noqa: E402
from gemsdoe31.submission import sha256_file, validate_submission  # noqa: E402
from gemsdoe31.submodular import allocate_submodular_dots  # noqa: E402

PREREG = ROOT / "knowledge/2026-10-26_h31s_udap_sslic_preregistration.md"
EVIDENCE = ROOT / "evidence/h31s"
WORK = Path("/tmp/gemsdoe31_h31s_work")
DATA_EXT = Path("/tmp/gemsdoe31_data/external")
PEER_DIR = Path("/tmp/gems_peer_audit")
BUDGET = 37_654
MIN_BUFFER_PX = 213
SCREEN_SEED = 41
CONFIRM_SEED = 42
PRIMARY = "h31s_full_sslic"


def save_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def load_grid() -> tuple[Grid, np.ndarray]:
    with rasterio.open(ROOT / "data/sample_submission.tif") as ds:
        fp = np.isfinite(ds.read(1))
        crs = ds.crs
        transform = ds.transform
    with rasterio.open(ROOT / "data/labels.tif") as ds:
        cat = (ds.read(1) == 1) & fp
    grid = Grid(fp, cat, crs, transform, *fp.shape)
    fi = np.flatnonzero(fp.ravel())
    return grid, fi


def load_magrest_physical_x(grid: Grid, fi: np.ndarray) -> np.ndarray:
    """Exact 31-band physical matrix used by scripts/run_magrest.py:fit_control."""
    cols = [np.load(ROOT / f".cache/features/band-{i:02d}.npy", mmap_mode="r").ravel()[fi].astype(np.float32) for i in range(1, 20)]
    with rasterio.open(DATA_EXT / "lidar_scarp_features_u8.tif") as ds:
        lid = ds.read().astype(np.float32)
    lid[lid == 0] = np.nan
    for b in range(12):
        cols.append(lid[b].ravel()[fi])
    del lid
    x = np.vstack(cols)
    del cols
    gc.collect()
    return x


def bayes_calibrate(p_raw: np.ndarray, n_pos: int, n_neg: int, pos_weight: float, true_prev: float = 0.0155) -> np.ndarray:
    """Exact parameter-free Bayes prior-odds adjustment back to true spatial prevalence."""
    eff_train_prev = (pos_weight * n_pos) / max(pos_weight * n_pos + n_neg, 1.0)
    odd_true = true_prev / max(1.0 - true_prev, 1e-6)
    odd_train = eff_train_prev / max(1.0 - eff_train_prev, 1e-6)
    alpha = float(odd_true / max(odd_train, 1e-6))
    p = np.clip(p_raw, 1e-6, 1.0 - 1e-6)
    num = alpha * p
    return (num / (num + (1.0 - p))).astype(np.float32)


def predict_batched(model: HistGradientBoostingClassifier, x_feat: np.ndarray, feat_idx: list[int] | slice, target_idx: np.ndarray) -> np.ndarray:
    out = np.empty(len(target_idx), dtype=np.float32)
    for s in range(0, len(target_idx), 120_000):
        b = target_idx[s : s + 120_000]
        sub = x_feat[feat_idx, :][:, b].T
        out[s : s + 120_000] = model.predict_proba(sub)[:, 1]
    return out


def score_prediction(pred: np.ndarray, fold: dict, grid: Grid, *, truth: np.ndarray | None = None, known: np.ndarray | None = None):
    region = fold["region"]
    ys, xs = np.nonzero(region)
    sl = (
        slice(max(0, int(ys.min()) - 3), min(grid.height, int(ys.max()) + 4)),
        slice(max(0, int(xs.min()) - 3), min(grid.width, int(xs.max()) + 4)),
    )
    f = dict(
        region=region[sl],
        truth=(fold["truth"] if truth is None else truth)[sl],
        masked_known=(fold["masked_known"] if known is None else known)[sl],
        visible=fold["visible"][sl],
    )
    return shared_eval.evaluate(
        pred[sl].astype(np.float32),
        f,
        grid.footprint[sl],
        block_side=200,
        origin=(sl[0].start, sl[1].start),
        global_shape=grid.shape,
    )


def run_canaries(x_fp: np.ndarray, names: list[str], fi: np.ndarray, folds: list[dict], grid: Grid, *, tag: str) -> dict:
    region = np.zeros(grid.shape, bool)
    truth = np.zeros(grid.shape, bool)
    known = np.zeros(grid.shape, bool)
    for f in folds:
        region |= f["region"]
        truth |= f["truth"]
        known |= f["masked_known"]
    eval_fp = (region & grid.footprint & ~(known & ~truth)).ravel()[fi]
    y_all = truth.ravel()[fi][eval_fp].astype(np.uint8)
    rng = np.random.default_rng(31_026)
    pos = np.flatnonzero(y_all == 1)
    neg = np.flatnonzero(y_all == 0)
    sub = np.r_[pos, rng.choice(neg, min(150_000, len(neg)), replace=False)]
    ys = y_all[sub]

    rows = []
    for idx, nm in enumerate(names):
        vals = x_fp[idx, eval_fp][sub]
        miss = ~np.isfinite(vals)
        m_auc = float(roc_auc_score(ys, miss.astype(np.float32))) if miss.any() and not miss.all() else 0.5
        m_auc2 = max(m_auc, 1.0 - m_auc)
        fin = ~miss
        if fin.sum() >= 20 and len(np.unique(ys[fin])) == 2 and np.nanstd(vals[fin]) > 0:
            v_raw = float(roc_auc_score(ys[fin], vals[fin]))
            v_auc2 = max(v_raw, 1.0 - v_raw)
        else:
            v_raw, v_auc2 = 0.5, 0.5
        rows.append(
            dict(
                feature=nm,
                raw_auc=round(v_raw, 5),
                value_auc_two_sided=round(v_auc2, 5),
                missing_fraction=round(float(miss.mean()), 5),
                missing_auc_two_sided=round(m_auc2, 5),
                leakage_flag=bool(max(v_auc2, m_auc2) > 0.90),
            )
        )
    max_val = max(r["value_auc_two_sided"] for r in rows)
    max_miss = max(r["missing_auc_two_sided"] for r in rows)
    out = dict(
        tag=tag,
        threshold=0.90,
        evaluated_positive_pixels=int(len(pos)),
        evaluated_background_sample=int(len(sub) - len(pos)),
        max_value_auc_two_sided=max_val,
        max_missing_auc_two_sided=max_miss,
        pass_=bool(max(max_val, max_miss) <= 0.90),
        features=rows,
    )
    save_json(EVIDENCE / f"canaries_{tag}.json", out)
    if not out["pass_"]:
        raise RuntimeError(f"LEAKAGE STOP ({tag}): max value AUC={max_val:.4f}, missing AUC={max_miss:.4f} > 0.90")
    return out


def fit_control_magrest_hgb(x_phys: np.ndarray, fi: np.ndarray, fold: dict, quad: np.ndarray, grid: Grid, buffer_px: int) -> np.ndarray:
    """Exact MAGREST physical_hgb control on the identical fold."""
    q = fold["fold"]
    separated = distance_transform_edt(quad != q) > buffer_px
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
        l2_regularization=1.0,
        class_weight={0: 1, 1: 5},
        early_stopping=False,
        random_state=31 + q,
    )
    with threadpool_limits(limits=2):
        model.fit(x_phys[:, ids].T, y)
        active = grid.footprint & fold["region"] & ~fold["masked_known"]
        target = np.flatnonzero(active.ravel()[fi])
        p = np.zeros(grid.shape, np.float32)
        p.ravel()[fi[target]] = predict_batched(model, x_phys, slice(None), target)
    return p


def fit_stage1_dual_head(
    x_s1: np.ndarray,
    feat_indices: list[int],
    slope_fp: np.ndarray,
    fi: np.ndarray,
    train_mask_2d: np.ndarray,
    pos_mask_2d: np.ndarray,
    known_nonhidden_2d: np.ndarray,
    target_mask_2d: np.ndarray,
    grid: Grid,
    *,
    seed_offset: int,
    dual_regime: bool = True,
) -> tuple[np.ndarray, dict]:
    """Fit global + piedmont-specialist HGB with Bayes prevalence-prior calibration."""
    d_known = distance_transform_edt(~known_nonhidden_2d)
    pos_fp = np.flatnonzero((train_mask_2d & pos_mask_2d).ravel()[fi])
    neg_pool = np.flatnonzero((train_mask_2d & (d_known > 3.0)).ravel()[fi])
    rng = np.random.default_rng(4100 + seed_offset)
    neg_fp = rng.choice(neg_pool, min(120_000, len(neg_pool)), replace=False)
    ids = np.r_[pos_fp, neg_fp]
    y = np.r_[np.ones(len(pos_fp), dtype=np.uint8), np.zeros(len(neg_fp), dtype=np.uint8)]

    target_fp = np.flatnonzero(target_mask_2d.ravel()[fi])
    with threadpool_limits(limits=2):
        m_glob = HistGradientBoostingClassifier(
            max_iter=150,
            learning_rate=0.08,
            max_leaf_nodes=31,
            min_samples_leaf=60,
            l2_regularization=2.0,
            class_weight={0: 1.0, 1: 4.0},
            early_stopping=False,
            random_state=101 + seed_offset,
        )
        m_glob.fit(x_s1[feat_indices, :][:, ids].T, y)
        p_glob_raw = predict_batched(m_glob, x_s1, feat_indices, target_fp)
        p_glob = bayes_calibrate(p_glob_raw, len(pos_fp), len(neg_fp), pos_weight=4.0)

        if dual_regime:
            pied_tr = slope_fp <= 8.0
            pos_p = np.flatnonzero(((train_mask_2d & pos_mask_2d).ravel()[fi]) & pied_tr)
            neg_p_pool = np.flatnonzero(((train_mask_2d & (d_known > 3.0)).ravel()[fi]) & pied_tr)
            if len(pos_p) >= 500 and len(neg_p_pool) >= 5_000:
                neg_p = rng.choice(neg_p_pool, min(80_000, len(neg_p_pool)), replace=False)
                ids_p = np.r_[pos_p, neg_p]
                y_p = np.r_[np.ones(len(pos_p), dtype=np.uint8), np.zeros(len(neg_p), dtype=np.uint8)]
                m_pied = HistGradientBoostingClassifier(
                    max_iter=130,
                    learning_rate=0.07,
                    max_leaf_nodes=23,
                    min_samples_leaf=80,
                    l2_regularization=3.0,
                    class_weight={0: 1.0, 1: 4.0},
                    early_stopping=False,
                    random_state=201 + seed_offset,
                )
                m_pied.fit(x_s1[feat_indices, :][:, ids_p].T, y_p)
                p_pied_raw = predict_batched(m_pied, x_s1, feat_indices, target_fp)
                p_pied = bayes_calibrate(p_pied_raw, len(pos_p), len(neg_p), pos_weight=4.0, true_prev=0.011)
                gate = 1.0 / (1.0 + np.exp((slope_fp[target_fp] - 6.5) / 1.5))
                p_comb = ((1.0 - 0.45 * gate) * p_glob + (0.45 * gate) * p_pied).astype(np.float32)
            else:
                p_comb = p_glob
        else:
            p_comb = p_glob

    out = np.zeros(grid.shape, dtype=np.float32)
    out.ravel()[fi[target_fp]] = p_comb
    rec = dict(
        train_positive_pixels=int(len(pos_fp)),
        train_background_pixels=int(len(neg_fp)),
        catalogue_features_used=False,
        dual_regime=bool(dual_regime),
    )
    return out, rec


def fit_stage2_sslic_fold(
    x_s1: np.ndarray,
    s1_indices: list[int],
    top_s1_keep: list[int],
    slope_fp: np.ndarray,
    strike_ty: np.ndarray,
    strike_tx: np.ndarray,
    fi: np.ndarray,
    quad: np.ndarray,
    q_outer: int,
    train_outer: np.ndarray,
    pos_mask_2d: np.ndarray,
    known_nonhidden_2d: np.ndarray,
    target_outer: np.ndarray,
    grid: Grid,
    buffer_px: int,
    *,
    p1_outer_pred: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Nested inner-quadrant OOF Stage-1 -> SSLIC continuity -> Stage-2 calibrated probability."""
    train_quads = [qq for qq in range(4) if qq != q_outer]
    p1_oof_2d = np.zeros(grid.shape, dtype=np.float32)

    # Inner 3-quadrant spatial OOF for leak-free Stage-1 probabilities on train_outer
    for q_val in train_quads:
        sep_in = distance_transform_edt(quad != q_val) > max(buffer_px // 2, 100)
        tr_in = train_outer & (quad != q_val) & sep_in
        tg_in = grid.footprint & (quad == q_val)
        p_in, _ = fit_stage1_dual_head(
            x_s1,
            s1_indices,
            slope_fp,
            fi,
            tr_in,
            pos_mask_2d,
            known_nonhidden_2d,
            tg_in,
            grid,
            seed_offset=q_outer * 10 + q_val,
            dual_regime=True,
        )
        p1_oof_2d[tg_in] = p_in[tg_in]

    if p1_outer_pred is None:
        tg_out_q = grid.footprint & (quad == q_outer)
        p1_outer_pred, _ = fit_stage1_dual_head(
            x_s1,
            s1_indices,
            slope_fp,
            fi,
            train_outer,
            pos_mask_2d,
            known_nonhidden_2d,
            tg_out_q,
            grid,
            seed_offset=q_outer,
            dual_regime=True,
        )
    p1_oof_2d[grid.footprint & (quad == q_outer)] = p1_outer_pred[grid.footprint & (quad == q_outer)]

    sslic_dict = compute_sslic_channels(p1_oof_2d, strike_ty, strike_tx, grid.footprint)
    sslic_names = list(sslic_dict.keys())
    n_s2 = len(sslic_names) + len(top_s1_keep)
    d_known = distance_transform_edt(~known_nonhidden_2d)
    pos_fp = np.flatnonzero((train_outer & pos_mask_2d).ravel()[fi])
    neg_pool = np.flatnonzero((train_outer & (d_known > 3.0)).ravel()[fi])
    rng = np.random.default_rng(7100 + q_outer)
    neg_fp = rng.choice(neg_pool, min(120_000, len(neg_pool)), replace=False)
    ids = np.r_[pos_fp, neg_fp]
    y = np.r_[np.ones(len(pos_fp), dtype=np.uint8), np.zeros(len(neg_fp), dtype=np.uint8)]

    x_tr = np.empty((len(ids), n_s2), dtype=np.float32)
    for j, nm in enumerate(sslic_names):
        x_tr[:, j] = sslic_dict[nm].ravel()[fi[ids]]
    for j, fidx in enumerate(top_s1_keep):
        x_tr[:, len(sslic_names) + j] = x_s1[fidx, ids]

    target_fp = np.flatnonzero(target_outer.ravel()[fi])
    x_te = np.empty((len(target_fp), n_s2), dtype=np.float32)
    for j, nm in enumerate(sslic_names):
        x_te[:, j] = sslic_dict[nm].ravel()[fi[target_fp]]
    for j, fidx in enumerate(top_s1_keep):
        x_te[:, len(sslic_names) + j] = x_s1[fidx, target_fp]

    with threadpool_limits(limits=2):
        m_s2 = HistGradientBoostingClassifier(
            max_iter=120,
            learning_rate=0.06,
            max_leaf_nodes=23,
            min_samples_leaf=80,
            l2_regularization=4.0,
            class_weight={0: 1.0, 1: 4.0},
            early_stopping=False,
            random_state=501 + q_outer,
        )
        m_s2.fit(x_tr, y)
        p2_raw = m_s2.predict_proba(x_te)[:, 1].astype(np.float32)
    p2_cal = bayes_calibrate(p2_raw, len(pos_fp), len(neg_fp), pos_weight=4.0)
    # Blend calibrated Stage-2 SSLIC probability with Stage-1 to preserve fine local amplitude
    p1_te = p1_oof_2d.ravel()[fi[target_fp]]
    p_final = (0.70 * p2_cal + 0.30 * p1_te).astype(np.float32)

    out = np.zeros(grid.shape, dtype=np.float32)
    out.ravel()[fi[target_fp]] = p_final
    del x_tr, x_te
    return out, p1_oof_2d


def derive_own_variogram(x_s1: np.ndarray, s1_indices: list[int], slope_fp: np.ndarray, fi: np.ndarray, grid: Grid) -> dict:
    """Compute H31-S's own 4-quadrant buffered OOF residual semivariogram along fault components."""
    quad = quadrant_ids(grid.footprint)
    oof_p = np.zeros(grid.shape, dtype=np.float32)
    for q in range(4):
        sep = distance_transform_edt(quad != q) > MIN_BUFFER_PX
        tr = grid.footprint & (quad != q) & sep
        tg = grid.footprint & (quad == q)
        pq, _ = fit_stage1_dual_head(
            x_s1,
            s1_indices,
            slope_fp,
            fi,
            tr,
            grid.catalogue,
            grid.catalogue,
            tg,
            grid,
            seed_offset=80 + q,
            dual_regime=True,
        )
        oof_p[tg] = pq[tg]

    mask = grid.catalogue & (oof_p > 0)
    comps = connected_components(grid.catalogue)
    rows, cols = np.nonzero(mask)
    # Subsample every 2nd pixel if >25k so 80-draw component bootstrap runs in ~6s with identical 500 m lag bins
    if len(rows) > 25_000:
        rows, cols = rows[::2], cols[::2]
    vals = (1.0 - oof_p[rows, cols]).astype(np.float64)
    c_ids = comps[rows, cols]

    bins = empirical_variogram(rows, cols, vals, c_ids, bin_m=500.0, max_lag_m=60_000.0)
    fits = fit_models(bins, min_pairs=20)
    boot = component_bootstrap(rows, cols, vals, c_ids, draws=80, seed=20261026, min_pairs=20, bin_m=500.0, max_lag_m=60_000.0)
    decision = decide_buffer_m(fits, boot, bins, min_pairs=20)
    raw_buf_m = float(decision["buffer_m"] or 21_300.0)
    # Quadrant erosion feasibility: >240 px erodes narrow NE/SW Nevada quadrants excessively; enforce >= 213 px floor
    adopted_px = max(MIN_BUFFER_PX, min(240, int(np.ceil(raw_buf_m / 100.0))))
    payload = dict(
        method="Matheron OOF residual semivariogram along 8-connected fault components (H31-S own residuals)",
        residual_pixels_used=int(len(rows)),
        components_used=int(np.unique(c_ids).size),
        fits=fits,
        bootstrap=boot,
        decision=decision,
        raw_derived_buffer_m=raw_buf_m,
        adopted_buffer_px=adopted_px,
        adopted_buffer_m=float(adopted_px * 100.0),
        note=(
            f"Own H31-S OOF residual buffer rule gives {raw_buf_m:.1f} m; adopted holdout collar is "
            f"{adopted_px} px ({adopted_px * 0.1:.1f} km), honoring >= 21.3 km historical floor and quadrant geometry."
        ),
    )
    save_json(EVIDENCE / "buffer_derivation.json", payload)
    return payload


def emit_b2_submodular(prob_2d: np.ndarray, region_mask: np.ndarray, known_mask: np.ndarray, budget: int) -> np.ndarray:
    """Apply B=2 (>200 m off known traces) hygiene and exact 29-cell submodular dot cover."""
    d_known = distance_transform_edt(~known_mask)
    eligible = region_mask & (d_known > 2.0)
    dots, _ = allocate_submodular_dots(prob_2d, eligible, budget)
    return dots


def evaluate_seed(
    seed: int,
    buffer_px: int,
    x_phys: np.ndarray,
    x_s1: np.ndarray,
    s1_names: list[str],
    incumbent_indices: list[int],
    s1_all_indices: list[int],
    top_s1_keep: list[int],
    slope_fp: np.ndarray,
    strike_ty: np.ndarray,
    strike_tx: np.ndarray,
    fi: np.ndarray,
    grid: Grid,
    *,
    include_exp2_stage1_arm: bool = True,
) -> dict:
    folds, quad = buffered_component_draw(
        grid, seed=seed, hide_frac=0.20, buffer_px=buffer_px, boundary_px=buffer_px
    )
    if seed == SCREEN_SEED:
        run_canaries(x_s1, s1_names, fi, folds, grid, tag=f"stage1_seed{seed}")

    arm_names = ["physical_hgb", "incumbent_h31m_submod"]
    if include_exp2_stage1_arm:
        arm_names.append("h31s_stage1_udap_hzad")
    arm_names.append(PRIMARY)

    terms = {n: np.zeros((323, 4), float) for n in arm_names}
    proxy_terms = {n: np.zeros((323, 4), float) for n in arm_names}

    with rasterio.open(DATA_EXT / "derived_sgmc_faults_100m_u8.tif") as ds:
        sgmc = (ds.read(1) == 1) & grid.footprint
    proxy_truth = sgmc & (distance_transform_edt(~grid.catalogue) > 3.0)

    fold_rows = []
    sslic_canary_cols = None
    sslic_canary_names: list[str] = []

    for fold in folds:
        q = fold["fold"]
        t0 = time.time()
        allowed_raw = grid.footprint & fold["region"] & ~fold["masked_known"]
        budget = round(BUDGET * int((grid.footprint & fold["region"]).sum()) / int(grid.footprint.sum()))
        separated = distance_transform_edt(quad != q) > buffer_px
        train_outer = grid.footprint & (quad != q) & separated & ~fold["hidden_all"]
        target_outer = grid.footprint & (quad == q)

        p_ctrl = fit_control_magrest_hgb(x_phys, fi, fold, quad, grid, buffer_px)
        pred_ctrl = spaced_dots(p_ctrl, allowed_raw, budget)

        p_inc, _ = fit_stage1_dual_head(
            x_s1,
            incumbent_indices,
            slope_fp,
            fi,
            train_outer,
            fold["visible"],
            fold["masked_known"],
            target_outer,
            grid,
            seed_offset=seed * 10 + q,
            dual_regime=False,
        )
        pred_inc = emit_b2_submodular(p_inc, allowed_raw, fold["masked_known"], budget)

        p_s1, _ = fit_stage1_dual_head(
            x_s1,
            s1_all_indices,
            slope_fp,
            fi,
            train_outer,
            fold["visible"],
            fold["masked_known"],
            target_outer,
            grid,
            seed_offset=seed * 20 + q,
            dual_regime=True,
        )
        preds = {
            "physical_hgb": pred_ctrl,
            "incumbent_h31m_submod": pred_inc,
        }
        if include_exp2_stage1_arm:
            preds["h31s_stage1_udap_hzad"] = emit_b2_submodular(p_s1, allowed_raw, fold["masked_known"], budget)

        p_s2, p1_oof_2d = fit_stage2_sslic_fold(
            x_s1,
            s1_all_indices,
            top_s1_keep,
            slope_fp,
            strike_ty,
            strike_tx,
            fi,
            quad,
            q,
            train_outer,
            fold["visible"],
            fold["masked_known"],
            target_outer,
            grid,
            buffer_px,
            p1_outer_pred=p_s1,
        )
        if seed == SCREEN_SEED:
            ss_d = compute_sslic_channels(p1_oof_2d, strike_ty, strike_tx, grid.footprint)
            sslic_canary_names = list(ss_d.keys())
            if sslic_canary_cols is None:
                sslic_canary_cols = np.zeros((len(sslic_canary_names), len(fi)), dtype=np.float32)
            q_fp = (fold["region"] & grid.footprint).ravel()[fi]
            for j, nm in enumerate(sslic_canary_names):
                sslic_canary_cols[j, q_fp] = ss_d[nm].ravel()[fi[q_fp]]
            del ss_d

        preds[PRIMARY] = emit_b2_submodular(p_s2, allowed_raw, fold["masked_known"], budget)

        per_fold = {}
        for name, pred in preds.items():
            sc, t = score_prediction(pred, fold, grid)
            terms[name] += t
            psc, pt = score_prediction(pred, fold, grid, truth=proxy_truth, known=grid.catalogue)
            proxy_terms[name] += pt
            per_fold[name] = dict(catalogue=sc, sgmc_proxy=psc)

        dt = time.time() - t0
        print(
            f"[seed={seed} {fold['name']} {dt:.1f}s] withheld={int(fold['truth'].sum())} budget={budget} | "
            + " | ".join(f"{k}={per_fold[k]['catalogue']['dti']:.4f}" for k in arm_names),
            flush=True,
        )
        fold_rows.append(dict(fold=fold["name"], draw_receipt=fold["receipt"], budget=budget, arms=per_fold))
        gc.collect()

    if seed == SCREEN_SEED and sslic_canary_cols is not None:
        run_canaries(sslic_canary_cols, sslic_canary_names, fi, folds, grid, tag=f"stage2_sslic_seed{seed}")

    summary = shared_eval.pooled_summary(terms, draws=1000, seed=310031 + seed, candidate=PRIMARY)
    delta_ctrl = summary["paired_differences"]["physical_hgb"]
    delta_inc = summary["paired_differences"]["incumbent_h31m_submod"]
    wins_ctrl = sum(r["arms"][PRIMARY]["catalogue"]["dti"] > r["arms"]["physical_hgb"]["catalogue"]["dti"] for r in fold_rows)
    worst_ctrl = min(r["arms"][PRIMARY]["catalogue"]["dti"] - r["arms"]["physical_hgb"]["catalogue"]["dti"] for r in fold_rows)
    wins_inc = sum(r["arms"][PRIMARY]["catalogue"]["dti"] > r["arms"]["incumbent_h31m_submod"]["catalogue"]["dti"] for r in fold_rows)
    worst_inc = min(r["arms"][PRIMARY]["catalogue"]["dti"] - r["arms"]["incumbent_h31m_submod"]["catalogue"]["dti"] for r in fold_rows)

    pass_vs_ctrl = bool(delta_ctrl["delta"] > 0 and delta_ctrl["ci95"][0] > 0 and wins_ctrl >= 3 and worst_ctrl >= -0.010)
    pass_vs_inc = bool(delta_inc["delta"] > 0 and delta_inc["ci95"][0] > 0 and wins_inc >= 3 and worst_inc >= -0.010)
    summary["vs_physical_hgb"] = dict(**delta_ctrl, quadrant_wins=wins_ctrl, worst_quadrant_delta=worst_ctrl, passed=pass_vs_ctrl)
    summary["vs_incumbent_h31m_submod"] = dict(**delta_inc, quadrant_wins=wins_inc, worst_quadrant_delta=worst_inc, passed=pass_vs_inc)
    summary["both_gates_passed"] = bool(pass_vs_ctrl and pass_vs_inc)

    proxy = shared_eval.pooled_summary(proxy_terms, draws=1000, seed=310031 + seed, candidate=PRIMARY)
    proxy["instrument"] = "SGMC-PROXY; never training truth; NOT hidden competition truth"

    out = dict(
        seed=seed,
        buffer_px=buffer_px,
        holdout=summary,
        sgmc_proxy=proxy,
        folds=fold_rows,
    )
    save_json(EVIDENCE / f"holdout_seed{seed}.json", out)
    return out


def build_full_oof_surface(
    x_s1: np.ndarray,
    s1_all_indices: list[int],
    top_s1_keep: list[int],
    slope_fp: np.ndarray,
    strike_ty: np.ndarray,
    strike_tx: np.ndarray,
    fi: np.ndarray,
    grid: Grid,
    buffer_px: int,
) -> np.ndarray:
    """Predict every pixel in Nevada strictly out-of-quadrant via 4-quadrant buffered OOF."""
    quad = quadrant_ids(grid.footprint)
    full_p = np.zeros(grid.shape, dtype=np.float32)
    for q in range(4):
        sep = distance_transform_edt(quad != q) > buffer_px
        tr_outer = grid.footprint & (quad != q) & sep
        tg_outer = grid.footprint & (quad == q)
        pq, _ = fit_stage2_sslic_fold(
            x_s1,
            s1_all_indices,
            top_s1_keep,
            slope_fp,
            strike_ty,
            strike_tx,
            fi,
            quad,
            q,
            tr_outer,
            grid.catalogue,
            grid.catalogue,
            tg_outer,
            grid,
            buffer_px,
        )
        full_p[tg_outer] = pq[tg_outer]
    return full_p


def audit_uniqueness_all_scopes(
    surface_2d: np.ndarray,
    final_dots_2d: np.ndarray,
    grid: Grid,
    fi: np.ndarray,
) -> dict:
    """Check pre-placement surface & post-placement final-dot uniqueness across all 9 sites + literal 695 registry."""
    surf_fp = surface_2d.ravel()[fi].astype(np.float64)
    surf_rk = (rankdata(surf_fp) - 1.0).astype(np.float64)
    surf_rk -= surf_rk.mean()
    surf_norm = float(np.linalg.norm(surf_rk))

    # Top-budget prospective support of continuous surface off catalogue (>2 px)
    d_cat = distance_transform_edt(~grid.catalogue)
    elig_fp = (grid.footprint & (d_cat > 2.0)).ravel()
    cand_flat = np.flatnonzero(elig_fp)
    top_idx = cand_flat[np.argsort(-surface_2d.ravel()[cand_flat])[:BUDGET]]
    surf_top_supp = np.zeros(grid.shape, dtype=bool)
    surf_top_supp.ravel()[top_idx] = True
    surf_top_halo = distance_transform_edt(~surf_top_supp) <= 3.0
    dots_halo = distance_transform_edt(~final_dots_2d) <= 3.0

    peer_files: list[tuple[str, Path]] = []
    if PEER_DIR.exists():
        for p in sorted(PEER_DIR.rglob("*.tif")):
            peer_files.append((f"peer:{p.relative_to(PEER_DIR)}", p))
    for p in sorted((ROOT / "docs/downloads").glob("*.tif")):
        if p.name.endswith("-nan.tif") and (p.with_name(p.name.replace("-nan.tif", "-zeros.tif")).exists() or p.with_name(p.name.replace("-nan.tif", "-allfinite.tif")).exists()):
            continue
        if "h31s-udap-sslic" in p.name:
            continue
        peer_files.append((f"local:{p.name}", p))

    seen_sha = set()
    discrete_rows = []
    for label, path in peer_files:
        sha = sha256_file(path)
        if sha in seen_sha:
            continue
        seen_sha.add(sha)
        with rasterio.open(path) as ds:
            if ds.shape != grid.shape:
                continue
            arr = ds.read(1)
        vals = np.where(np.isfinite(arr.ravel()[fi]), arr.ravel()[fi], 0.0).astype(np.float64)
        rk = (rankdata(vals) - 1.0).astype(np.float64)
        rk -= rk.mean()
        denom = surf_norm * float(np.linalg.norm(rk))
        rho = float(abs(surf_rk @ rk) / denom) if denom > 0 else 0.0

        peer_supp = grid.footprint & np.isfinite(arr) & (arr > 0)
        n_peer = int(peer_supp.sum())
        if n_peer == 0 or n_peer > 500_000:
            continue
        peer_halo = distance_transform_edt(~peer_supp) <= 3.0
        surf_ov = max(float(peer_halo[surf_top_supp].mean()), float(surf_top_halo[peer_supp].mean()))
        dots_ov_to_peer = float(peer_halo[final_dots_2d].mean())
        dots_ov_from_peer = float(dots_halo[peer_supp].mean())
        dots_ov = max(dots_ov_to_peer, dots_ov_from_peer)
        discrete_rows.append(
            dict(
                comparator=label,
                sha256=sha,
                peer_positive_pixels=n_peer,
                surface_abs_spearman=round(rho, 5),
                surface_top_3px_overlap=round(surf_ov, 5),
                final_dots_3px_overlap_max=round(dots_ov, 5),
                final_dots_in_peer_3px=round(dots_ov_to_peer, 5),
                peer_dots_in_final_3px=round(dots_ov_from_peer, 5),
            )
        )

    max_surf_rho = max(r["surface_abs_spearman"] for r in discrete_rows)
    max_surf_ov = max(r["surface_top_3px_overlap"] for r in discrete_rows)
    max_dots_ov = max(r["final_dots_3px_overlap_max"] for r in discrete_rows)
    discrete_pass = bool(max_surf_rho <= 0.90 and max_surf_ov <= 0.70 and max_dots_ov <= 0.70)

    # Literal unexempted 695-raster shared registry counterexample check (AGENTS.md mandatory disclosure)
    from audit_shared_registry_stop import load_counterexample

    pin, reference = load_counterexample(ROOT, restore=True)
    ref_meta = pin["counterexample"]
    lat_supp = grid.footprint & np.isfinite(reference) & (reference > 0)
    lat_halo = distance_transform_edt(~lat_supp) <= 3.0
    lat_surf_ov = float(lat_halo[surf_top_supp].mean())
    lat_dots_ov = float(lat_halo[final_dots_2d].mean())

    out = dict(
        thresholds=dict(abs_spearman_max=0.90, overlap_3px_max=0.70),
        discrete_competitor_scope=dict(
            comparators_checked=len(discrete_rows),
            max_surface_abs_spearman=max_surf_rho,
            max_surface_top_3px_overlap=max_surf_ov,
            max_final_dots_3px_overlap=max_dots_ov,
            pass_=discrete_pass,
            rows=discrete_rows,
        ),
        literal_695_shared_registry_scope=dict(
            counterexample_repo=ref_meta["repo"],
            counterexample_path=ref_meta["path"],
            counterexample_sha256=ref_meta["sha256"],
            surface_top_in_lattice_3px=lat_surf_ov,
            final_dots_in_lattice_3px=lat_dots_ov,
            gemsdoe48_dense_continuous_witness="evidence/tgj31/registry_universal_blocker.json (5,167,373/5,167,373 positive footprint cells = 100% overlap)",
            pass_=bool(lat_surf_ov <= 0.70 and lat_dots_ov <= 0.70),
            rule_note=(
                "Per AGENTS.md, no dense/calibration comparator is exempted silently: the 13GEMSDOE spacing-5 "
                "lattice and GEMSDOE48 dense continuous baseline cover ~99.5%-100% of Nevada within 3 px, "
                "forcing literal 695-registry STOP (slot_approved=false) unless an owner/selector explicitly scopes them."
            ),
        ),
    )
    save_json(EVIDENCE / "uniqueness_audit.json", out)
    return out


def compute_sgmc_regimes(final_dots_2d: np.ndarray, slope_fp: np.ndarray, fi: np.ndarray, grid: Grid) -> dict:
    with rasterio.open(DATA_EXT / "derived_sgmc_faults_100m_u8.tif") as ds:
        sgmc = (ds.read(1) == 1) & grid.footprint
    d_cat = distance_transform_edt(~grid.catalogue)
    sgmc_off = sgmc & (d_cat > 3.0)
    pied_2d = np.zeros(grid.shape, dtype=bool)
    pied_2d.ravel()[fi] = slope_fp <= 6.0
    mtn_2d = grid.footprint & (~pied_2d)

    pred_f = final_dots_2d.astype(np.float32)
    s_all = dti(pred_f, sgmc_off)["DTI"]
    s_pied = dti(np.where(pied_2d, pred_f, 0.0), sgmc_off & pied_2d)["DTI"]
    s_mtn = dti(np.where(mtn_2d, pred_f, 0.0), sgmc_off & mtn_2d)["DTI"]
    return dict(
        instrument="SGMC-PROXY; external 1:500k bedrock geology (>300 m off catalogue); never training truth; NOT hidden competition truth",
        h31s_sgmc_all_dti=s_all,
        h31s_sgmc_piedmont_dti=s_pied,
        h31s_sgmc_mountain_dti=s_mtn,
        piedmont_dot_fraction=float(pied_2d[final_dots_2d].mean()),
        comparators=dict(
            gemsdoe32_h33_2_b2=dict(all=0.093965, piedmont=0.058585, mountain=0.082809),
            gemsdoe27_h29_hpvc=dict(all=0.081987, piedmont=0.050045, mountain=0.076687),
            gemsdoe31_h31m=dict(all=0.100994, piedmont=0.064106, mountain=0.094711),
            gemsdoe31_magrest=dict(all=0.070677, piedmont=0.038469, mountain=0.071770),
        ),
    )


def main() -> None:
    t_start = time.time()
    WORK.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    prereg_sha = sha256_file(PREREG)
    print(f"[H31-S] Frozen preregistration SHA-256: {prereg_sha}", flush=True)

    grid, fi = load_grid()
    if (WORK / "x_stage1.npy").exists() and (WORK / "s1_names.json").exists() and (WORK / "strike_ty.npy").exists():
        print("[H31-S] Reusing cached Stage-1 physical stack from /tmp/gemsdoe31_h31s_work/...", flush=True)
        s1_names = json.loads((WORK / "s1_names.json").read_text())
        strike_ty = np.load(WORK / "strike_ty.npy")
        strike_tx = np.load(WORK / "strike_tx.npy")
    else:
        print("[H31-S] Building 50-feature Stage-1 physical stack (UDAP + HZAD + Nulls)...", flush=True)
        x_ram, s1_names, strike_ty, strike_tx = build_h31s_stage1_stack(ROOT / ".cache/features", DATA_EXT, grid.footprint)
        x_mm = np.lib.format.open_memmap(WORK / "x_stage1.npy", mode="w+", dtype=np.float32, shape=x_ram.shape)
        x_mm[:] = x_ram[:]
        del x_ram
        gc.collect()
        (WORK / "s1_names.json").write_text(json.dumps(s1_names))
        np.save(WORK / "strike_ty.npy", strike_ty)
        np.save(WORK / "strike_tx.npy", strike_tx)
    x_s1 = np.load(WORK / "x_stage1.npy", mmap_mode="r")
    slope_fp = np.array(x_s1[s1_names.index("base_band_19"), :], dtype=np.float32, copy=True)

    # Incumbent H31-M-style raw feature subset (base + GeoDAWN + LiDAR + GDR + raw bstep/dilat without UDAP/HZAD/Nulls)
    incumbent_indices = [
        i
        for i, nm in enumerate(s1_names)
        if nm.startswith(("base_band_", "geodawn_", "lidar_", "gdr_"))
    ]
    s1_all_indices = list(range(len(s1_names)))
    # Compact Stage-2 physical context indices alongside the 7 SSLIC channels
    keep_names = [
        "base_band_05",
        "base_band_08",
        "base_band_12",
        "base_band_15",
        "base_band_17",
        "base_band_19",
        "lidar_step_max",
        "lidar_coh100",
        "udap_grav_slope_55",
        "udap_grav_gain_55",
        "udap_concordance_55",
        "udap_dilat_coupling",
        "hzad_rtp_axial_trough",
        "hzad_geothermal_conduit",
        "null_contour_bench",
        "null_cardinal_seam",
    ]
    top_s1_keep = [s1_names.index(nm) for nm in keep_names]

    if (EVIDENCE / "buffer_derivation.json").exists():
        buf_info = json.loads((EVIDENCE / "buffer_derivation.json").read_text())
        print("[EXP-1a] Reusing saved H31-S OOF residual semivariogram collar...", flush=True)
    else:
        print("[EXP-1a] Deriving H31-S candidate-specific OOF residual semivariogram collar...", flush=True)
        buf_info = derive_own_variogram(x_s1, s1_all_indices, slope_fp, fi, grid)
    buffer_px = int(buf_info["adopted_buffer_px"])
    print(f"[EXP-1a] Derived raw buffer={buf_info['raw_derived_buffer_m']:.1f} m -> adopted collar={buffer_px} px", flush=True)

    if not (WORK / "x_phys31.npy").exists():
        print("[EXP-1b] Building MAGREST 31-band physical matrix...", flush=True)
        x_phys_ram = load_magrest_physical_x(grid, fi)
        xp_mm = np.lib.format.open_memmap(WORK / "x_phys31.npy", mode="w+", dtype=np.float32, shape=x_phys_ram.shape)
        xp_mm[:] = x_phys_ram[:]
        del x_phys_ram
        gc.collect()
    x_phys = np.load(WORK / "x_phys31.npy", mmap_mode="r")

    if (EVIDENCE / f"holdout_seed{SCREEN_SEED}.json").exists():
        print(f"[EXP-1b / EXP-2 / EXP-3a] Reusing completed Screen seed={SCREEN_SEED}...", flush=True)
        screen = json.loads((EVIDENCE / f"holdout_seed{SCREEN_SEED}.json").read_text())
    else:
        screen = evaluate_seed(
            SCREEN_SEED,
            buffer_px,
            x_phys,
            x_s1,
            s1_names,
            incumbent_indices,
            s1_all_indices,
            top_s1_keep,
            slope_fp,
            strike_ty,
            strike_tx,
            fi,
            grid,
            include_exp2_stage1_arm=True,
        )

    if (EVIDENCE / f"holdout_seed{CONFIRM_SEED}.json").exists():
        print(f"[EXP-3b] Reusing completed Confirmation seed={CONFIRM_SEED}...", flush=True)
        confirm = json.loads((EVIDENCE / f"holdout_seed{CONFIRM_SEED}.json").read_text())
    else:
        print("[EXP-3b] Evaluating untouched Fresh Confirmation seed=42 (zero hyperparameter changes)...", flush=True)
        confirm = evaluate_seed(
            CONFIRM_SEED,
            buffer_px,
            x_phys,
            x_s1,
            s1_names,
            incumbent_indices,
            s1_all_indices,
            top_s1_keep,
            slope_fp,
            strike_ty,
            strike_tx,
            fi,
            grid,
            include_exp2_stage1_arm=False,
        )

    if (WORK / "full_surface.npy").exists():
        print("[Packaging] Reusing cached full-footprint 4-quadrant buffered OOF surface...", flush=True)
        full_surface = np.load(WORK / "full_surface.npy")
    else:
        print("[Packaging] Computing full-footprint 4-quadrant buffered OOF surface & 37,654 submodular B=2 dots...", flush=True)
        full_surface = build_full_oof_surface(
            x_s1, s1_all_indices, top_s1_keep, slope_fp, strike_ty, strike_tx, fi, grid, buffer_px
        )
        np.save(WORK / "full_surface.npy", full_surface)
    final_dots = emit_b2_submodular(full_surface, grid.footprint, grid.catalogue, BUDGET)
    assert int(final_dots.sum()) == BUDGET
    assert int((final_dots & grid.catalogue).sum()) == 0

    uniq = audit_uniqueness_all_scopes(full_surface, final_dots, grid, fi)
    sgmc_regimes = compute_sgmc_regimes(final_dots, slope_fp, fi, grid)
    save_json(EVIDENCE / "sgmc_regimes.json", sgmc_regimes)

    content_digest = hashlib.sha256(np.packbits(final_dots.ravel()).tobytes()).hexdigest()
    name = f"gemsdoe31-h31s-udap-sslic-{int(final_dots.sum())}-20261026-{content_digest[:10]}"
    s_dti = screen["holdout"]["scores"][PRIMARY]["dti"]
    c_dti = confirm["holdout"]["scores"][PRIMARY]["dti"]
    note = (
        f"H31-S UDAP+HZAD+SSLIC {BUDGET}d B2 | HOLDOUT-DTI s41={s_dti:.4f} s42={c_dti:.4f} "
        f"| research-only {content_digest[:8]}"
    )
    assert len(note) <= 140

    zeros_path = ROOT / "docs/downloads" / f"{name}-zeros.tif"
    receipt = write_submission(
        zeros_path,
        final_dots.astype(np.float32),
        ROOT / "data/sample_submission.tif",
        grid.footprint,
        note=note,
        name=name,
        catalogue=grid.catalogue,
        metadata=dict(
            preregistration_sha256=prereg_sha,
            primary_arm=PRIMARY,
            content_support_sha256=content_digest,
            scientific_status="research-only; literal-695-registry-stop; selector-not-promoted",
        ),
    )

    from build_submission import write_variants

    variants = write_variants(final_dots, grid.footprint, ROOT / "docs/downloads" / name, name=name)
    variants["allfinite"].unlink(missing_ok=True)
    nan_path = variants["nan"]
    nan_val = validate_submission(nan_path, ROOT / "data/sample_submission.tif", convention="nan-outside")
    zeros_val = validate_submission(zeros_path, ROOT / "data/sample_submission.tif", convention="all-finite")
    if not nan_val["ok_to_upload_format_only"] or not zeros_val["ok_to_upload_format_only"]:
        raise RuntimeError("Packaged H31-S GeoTIFF failed automated format/range validation")

    both_holdout_pass = bool(screen["holdout"]["both_gates_passed"] and confirm["holdout"]["both_gates_passed"])
    disc_uniq_pass = bool(uniq["discrete_competitor_scope"]["pass_"])
    lit_uniq_pass = bool(uniq["literal_695_shared_registry_scope"]["pass_"])

    blockers = []
    if not lit_uniq_pass:
        blockers.append(
            f"Literal 695-registry overlap STOP (AGENTS.md unexempted rule): "
            f"{uniq['literal_695_shared_registry_scope']['final_dots_in_lattice_3px']*100:.2f}% of dots fall within "
            f"3 px of registered 13GEMSDOE spacing-5 lattice r13-lattice-s5 (and 100% within GEMSDOE48 dense baseline)."
        )
    if not disc_uniq_pass:
        blockers.append("Discrete competitor uniqueness threshold exceeded.")
    if not both_holdout_pass:
        blockers.append(
            "Preregistered efficacy gate vs both physical_hgb AND same-instrument incumbent_h31m_submod "
            "did not pass across both screen seed=41 and confirmation seed=42."
        )
    blockers.append("No assigned method paragraph was supplied in the 2026-10-26 prompt; promotion requires separate selector/owner step.")

    zip_full_path = ROOT / "docs/downloads" / receipt["zip_file"]
    elapsed_s = round(time.time() - t_start, 1)
    run_card = dict(
        schema="gemsdoe31-parallel-run-card-v2",
        generated_utc=datetime.now(timezone.utc).isoformat(),
        lane_id="H31-S-UDAP-SSLIC",
        lane_assignment_status="none_supplied_in_prompt; self-declared disjoint lane preregistered prior to execution",
        preregistration=dict(path=str(PREREG.relative_to(ROOT)), sha256=prereg_sha),
        budget_used=dict(experiments_run=3, max_experiments=3, wall_seconds=elapsed_s, max_seconds=7200),
        shared_template=dict(
            evaluator_version=shared_eval.VERSION,
            holdout_version="buffered-whole-components-loqo-v2",
            submission_writer="vendor/gems57/submission_writer.py",
            cached_bands_verified=19,
        ),
        spatial_collar=buf_info,
        leakage_canary=dict(
            threshold=0.90,
            stage1_max_value_auc=json.loads((EVIDENCE / f"canaries_stage1_seed{SCREEN_SEED}.json").read_text())["max_value_auc_two_sided"],
            stage1_max_missing_auc=json.loads((EVIDENCE / f"canaries_stage1_seed{SCREEN_SEED}.json").read_text())["max_missing_auc_two_sided"],
            stage2_max_value_auc=json.loads((EVIDENCE / f"canaries_stage2_sslic_seed{SCREEN_SEED}.json").read_text())["max_value_auc_two_sided"],
            pass_=True,
        ),
        experiments=[
            dict(
                id="EXP-1",
                description="Leakage canaries + H31-S empirical OOF residual variogram + Control-Physical-HGB & same-instrument Incumbent-H31M-Submod on Screen seed=41",
                evaluator_version=shared_eval.VERSION,
                withheld_positive_pixels=screen["holdout"]["scores"]["physical_hgb"]["withheld_positive_pixels"],
                physical_hgb_holdout_dti=screen["holdout"]["scores"]["physical_hgb"]["dti"],
                physical_hgb_ci95=screen["holdout"]["scores"]["physical_hgb"]["ci95"],
                incumbent_h31m_submod_holdout_dti=screen["holdout"]["scores"]["incumbent_h31m_submod"]["dti"],
                incumbent_h31m_submod_ci95=screen["holdout"]["scores"]["incumbent_h31m_submod"]["ci95"],
            ),
            dict(
                id="EXP-2",
                description="Stage-1 UDAP + HZAD + Null Suppressors + Regime Dual-Head HGB + Bayes prior calibration + 29-cell Submodular B=2 cover on Screen seed=41",
                evaluator_version=shared_eval.VERSION,
                withheld_positive_pixels=screen["holdout"]["scores"]["h31s_stage1_udap_hzad"]["withheld_positive_pixels"],
                holdout_dti=screen["holdout"]["scores"]["h31s_stage1_udap_hzad"]["dti"],
                ci95=screen["holdout"]["scores"]["h31s_stage1_udap_hzad"]["ci95"],
            ),
            dict(
                id="EXP-3",
                description="Full 2-Stage Nested OOF Strike-Steered Line-Integral Continuity (SSLIC) + 29-cell Submodular B=2 cover on Screen seed=41 & untouched Confirmation seed=42",
                evaluator_version=shared_eval.VERSION,
                screen_seed41=dict(
                    withheld_positive_pixels=screen["holdout"]["scores"][PRIMARY]["withheld_positive_pixels"],
                    holdout_dti=screen["holdout"]["scores"][PRIMARY]["dti"],
                    ci95=screen["holdout"]["scores"][PRIMARY]["ci95"],
                    vs_physical_hgb=screen["holdout"]["vs_physical_hgb"],
                    vs_incumbent_h31m_submod=screen["holdout"]["vs_incumbent_h31m_submod"],
                ),
                confirmation_seed42=dict(
                    withheld_positive_pixels=confirm["holdout"]["scores"][PRIMARY]["withheld_positive_pixels"],
                    physical_hgb_dti=confirm["holdout"]["scores"]["physical_hgb"]["dti"],
                    incumbent_h31m_submod_dti=confirm["holdout"]["scores"]["incumbent_h31m_submod"]["dti"],
                    holdout_dti=confirm["holdout"]["scores"][PRIMARY]["dti"],
                    ci95=confirm["holdout"]["scores"][PRIMARY]["ci95"],
                    vs_physical_hgb=confirm["holdout"]["vs_physical_hgb"],
                    vs_incumbent_h31m_submod=confirm["holdout"]["vs_incumbent_h31m_submod"],
                ),
            ),
        ],
        sgmc_external_proxy=sgmc_regimes,
        uniqueness=dict(
            discrete_competitor_scope=dict(
                comparators_checked=uniq["discrete_competitor_scope"]["comparators_checked"],
                max_surface_abs_spearman=uniq["discrete_competitor_scope"]["max_surface_abs_spearman"],
                max_surface_top_3px_overlap=uniq["discrete_competitor_scope"]["max_surface_top_3px_overlap"],
                max_final_dots_3px_overlap=uniq["discrete_competitor_scope"]["max_final_dots_3px_overlap"],
                pass_=disc_uniq_pass,
            ),
            literal_695_shared_registry_scope=uniq["literal_695_shared_registry_scope"],
        ),
        artifact=dict(
            name=name,
            note_140=note,
            note_length=len(note),
            positive_pixels=int(final_dots.sum()),
            positive_pixels_on_public_catalogue=int((final_dots & grid.catalogue).sum()),
            file_zeros=str(zeros_path.relative_to(ROOT)),
            sha256_zeros=receipt["sha256"],
            bytes_zeros=receipt["bytes"],
            file_nan=str(nan_path.relative_to(ROOT)),
            sha256_nan=nan_val["sha256"],
            bytes_nan=nan_val["bytes"],
            zip_zeros=str(zip_full_path.relative_to(ROOT)),
            sha256_zip=receipt["zip_sha256"],
            bytes_zip=zip_full_path.stat().st_size,
            receipt_json=str((ROOT / "docs/downloads" / f"{name}-zeros.json").relative_to(ROOT)),
            format_0_1_valid_zeros=bool(zeros_val["ok_to_upload_format_only"]),
            format_0_1_valid_nan=bool(nan_val["ok_to_upload_format_only"]),
        ),
        governance=dict(
            ok_to_download_for_research=True,
            ok_to_submit=False,
            slot_approved=False,
            weekly_slot_spent=False,
            efficacy_vs_physical_control_both_seeds=bool(
                screen["holdout"]["vs_physical_hgb"]["passed"] and confirm["holdout"]["vs_physical_hgb"]["passed"]
            ),
            efficacy_vs_same_instrument_h31m_both_seeds=bool(
                screen["holdout"]["vs_incumbent_h31m_submod"]["passed"] and confirm["holdout"]["vs_incumbent_h31m_submod"]["passed"]
            ),
            discrete_competitor_unique=disc_uniq_pass,
            literal_695_registry_unique=lit_uniq_pass,
            verdict="research_only_blocked_by_literal_695_registry" if (both_holdout_pass and disc_uniq_pass) else "negative",
            blocking_reasons=blockers,
        ),
    )
    save_json(EVIDENCE / "run_card.json", run_card)
    save_json(ROOT / "docs/downloads/h31s-run-card.json", run_card)
    save_json(ROOT / "registry/h31s_current_run.json", run_card)
    print(json.dumps(run_card["governance"], indent=2), flush=True)
    print(f"[H31-S] Done in {elapsed_s:.1f}s -> {zeros_path.name}", flush=True)


if __name__ == "__main__":
    main()
