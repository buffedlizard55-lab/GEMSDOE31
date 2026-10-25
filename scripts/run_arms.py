#!/usr/bin/env python3
"""Clean leak-free spatial-block trainer + preregistered H31-HVDC 3-experiment runner.

Closes ``IR-31-TRAINER-NOT-IN-SNAPSHOT`` and executes the frozen 3-experiment budget in
``knowledge/2026-10-25_h31_hvdc_preregistration.md``:

  - Canary: Single-feature holdout ROC-AUC leakage screen across all 55 static + fold-visible features
  - EXP-1 (ArmD-Clean-Poisson): 38 sensor bands (strictly excluding ``valid``, ``dist_cat_km``,
    ``dist_sgmc_km``), 21.25 km buffered HGB + Bayes prior shift + 2.8 px Poisson-disk emitter
  - EXP-2 (H31-HVDC-Physics-Poisson): Coverage-deconfounded Dual-Specialist (0.55 * M_fullfoot +
    0.45 * M_multisensor) with H31-HVDC hydrothermal-vent, magnetite-destruction x potassic-alteration,
    piedmont concealment-belt, and strike-concordance physics + 2.8 px Poisson-disk emitter
  - EXP-3 (H31-HVDC-Submod300): Coverage-deconfounded Dual-Specialist + fold-visible structural-
    hydrothermal accommodation specialist (M_struct) + exact 300 m CELF submodular max-cover emitter
"""

from __future__ import annotations

import argparse
import gc
import json
import os
import resource
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from sklearn.ensemble import HistGradientBoostingClassifier

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gemsdoe31.hvdc_holdout import (  # noqa: E402
    DEFAULT_COLLAR_M,
    EVALUATOR_VERSION,
    FoldSplit,
    HideRecoverDraw,
    additive_dti_pixel_maps,
    build_spatial_folds,
    check_registry_duplicate_canary,
    fold_clean_catalogue_masks,
    make_hide_recover_draw,
    pool_multi_draw_bootstrap,
    run_single_feature_leakage_canary,
    score_holdout_draw,
)
from gemsdoe31.hvdc import (  # noqa: E402
    FOLD_VISIBLE_NAMES,
    HVDC_DERIVED_NAMES,
    bayes_prior_calibrate,
    build_fold_visible_accommodation,
    build_hvdc_feature_cache,
)
from gemsdoe31.metric import ALPHA, BETA, dti  # noqa: E402
from gemsdoe31.raster import SHAPE  # noqa: E402
from gemsdoe31.submodular import allocate_submodular_dots, priority_poisson_thin  # noqa: E402

DOT_BUDGET = 37_654
NEG_SAMPLE_STATIC = 110_000
NEG_SAMPLE_STRUCT = 90_000


def _peak_rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def _make_hgb(seed: int) -> HistGradientBoostingClassifier:
    return HistGradientBoostingClassifier(
        max_iter=180,
        max_leaf_nodes=63,
        learning_rate=0.06,
        min_samples_leaf=50,
        l2_regularization=2.0,
        early_stopping=False,
        random_state=int(seed) % 2_147_483_647,
    )


def _ensure_sample_major_cache(cache_dir: Path, n_feat: int, n_foot: int) -> np.ndarray:
    """Create (n_foot, n_feat) sample-major float32 memmap once for contiguous slice reads."""
    sm_path = cache_dir / "hvdc_samples_by_feat.f32"
    expected_bytes = n_foot * n_feat * 4
    if not sm_path.is_file() or sm_path.stat().st_size != expected_bytes:
        src_mm = np.memmap(
            cache_dir / "hvdc_foot_features.f32",
            dtype=np.float32,
            mode="r",
            shape=(n_feat, n_foot),
        )
        dst_mm = np.memmap(
            sm_path,
            dtype=np.float32,
            mode="w+",
            shape=(n_foot, n_feat),
        )
        chunk = 500_000
        for s in range(0, n_foot, chunk):
            e = min(n_foot, s + chunk)
            dst_mm[s:e, :] = np.asarray(src_mm[:, s:e]).T
        dst_mm.flush()
        del src_mm, dst_mm
    return np.memmap(sm_path, dtype=np.float32, mode="r", shape=(n_foot, n_feat))


def _extract_transpose_submatrix(
    mm_samples: np.ndarray,
    col_indices: list[int],
    foot_positions: np.ndarray,
) -> np.ndarray:
    """Fast gather from sample-major (n_foot, n_feat) memmap."""
    rows = np.asarray(mm_samples[foot_positions], dtype=np.float32)
    return np.ascontiguousarray(rows[:, col_indices], dtype=np.float32)


def _predict_foot_subset(
    clf: HistGradientBoostingClassifier,
    mm: np.ndarray,
    col_indices: list[int],
    foot_positions: np.ndarray,
    *,
    chunk_size: int = 350_000,
) -> np.ndarray:
    """Chunked predict_proba on footprint subset so temporary RAM stays < 80 MB."""
    preds = np.empty(foot_positions.size, dtype=np.float32)
    for start in range(0, foot_positions.size, chunk_size):
        end = min(foot_positions.size, start + chunk_size)
        sub_pos = foot_positions[start:end]
        x_chunk = _extract_transpose_submatrix(mm, col_indices, sub_pos)
        preds[start:end] = clf.predict_proba(x_chunk)[:, 1].astype(np.float32)
        del x_chunk
    return preds


def fit_and_predict_draw(
    *,
    mm: np.ndarray,
    meta: dict,
    aux_upflow: np.ndarray,
    aux_tx: np.ndarray,
    aux_ty: np.ndarray,
    footprint: np.ndarray,
    foot_idx: np.ndarray,
    folds: list[FoldSplit],
    visible_2d: np.ndarray,
    seed: int,
    run_exp1: bool = True,
    run_exp2: bool = True,
    run_exp3: bool = True,
) -> dict[str, np.ndarray]:
    """Fit 21.25 km buffered 4-fold OOF surfaces strictly from ``visible_2d`` (never hidden!)."""
    n_foot = int(foot_idx.size)
    surf_exp1_foot = np.zeros(n_foot, dtype=np.float32) if run_exp1 else None
    surf_exp2_foot = np.zeros(n_foot, dtype=np.float32) if run_exp2 or run_exp3 else None
    surf_exp3_foot = np.zeros(n_foot, dtype=np.float32) if run_exp3 else None

    base_cols: list[int] = meta["baseline_cols"]
    ff_cols: list[int] = meta["fullfoot_specialist_cols"]
    ms_cols: list[int] = meta["multisensor_specialist_cols"]
    # Structural corroboration columns: 14 HVDC derived + key strain/slope/scarp channels
    fname_map = {n: i for i, n in enumerate(meta["feature_names"])}
    struct_static_names = list(HVDC_DERIVED_NAMES) + [
        "det_elev_slope", "geod_shearrate", "geod_2ndinv", "iso_grav_anom_hg", "step_max", "coh100"
    ]
    struct_static_cols = [fname_map[n] for n in struct_static_names]

    # Compute test-time accommodation features from visible_2d ONLY (for EXP-3 OOF prediction)
    if run_exp3:
        vis_acc_test_foot, _ = build_fold_visible_accommodation(
            visible_2d, footprint, aux_upflow, aux_tx, aux_ty
        )
    else:
        vis_acc_test_foot = None

    for fold_split in folds:
        q = fold_split.fold
        cell_seed = (10_000 * int(seed) + 100 * q) % 2_147_483_000
        rng = np.random.default_rng(cell_seed)

        masks = fold_clean_catalogue_masks(
            visible_2d,
            fold_split,
            struct_hide_seed=cell_seed + 7 if run_exp3 else None,
        )
        train_pos_foot = masks["train_pos"].ravel()[foot_idx]
        train_neg_foot = masks["train_neg"].ravel()[foot_idx]
        train_reg_foot = fold_split.train_region.ravel()[foot_idx]
        test_reg_foot = fold_split.test_region.ravel()[foot_idx]

        pos_positions = np.flatnonzero(train_pos_foot)
        neg_pool = np.flatnonzero(train_neg_foot)
        neg_positions = (
            rng.choice(neg_pool, size=NEG_SAMPLE_STATIC, replace=False)
            if neg_pool.size > NEG_SAMPLE_STATIC
            else neg_pool
        )
        train_positions = np.concatenate([pos_positions, neg_positions])
        y_train = np.concatenate(
            [np.ones(pos_positions.size, dtype=np.int8), np.zeros(neg_positions.size, dtype=np.int8)]
        )
        pi_sub = float(pos_positions.size) / float(train_positions.size)
        # Target prior is unmapped/hidden fault prevalence: (0.20 / 0.80) = 0.25 * visible prevalence,
        # placing EXP-1, EXP-2 (p_phys), and EXP-3 (p_struct) on the exact same probability scale.
        pi_true = 0.25 * (float(pos_positions.size) / float(train_reg_foot.sum()))

        test_positions = np.flatnonzero(test_reg_foot)

        # EXP-1: Clean 38-band baseline (no 'valid', no leaked distance bands)
        if run_exp1 and surf_exp1_foot is not None:
            x_tr1 = _extract_transpose_submatrix(mm, base_cols, train_positions)
            clf1 = _make_hgb(cell_seed + 1)
            clf1.fit(x_tr1, y_train)
            del x_tr1
            raw_p1 = _predict_foot_subset(clf1, mm, base_cols, test_positions)
            surf_exp1_foot[test_positions] = bayes_prior_calibrate(
                raw_p1, pi_subsample=pi_sub, pi_true=pi_true
            )
            del clf1, raw_p1

        # EXP-2 (and physical branch of EXP-3): Coverage-deconfounded Dual-Specialist
        if (run_exp2 or run_exp3) and surf_exp2_foot is not None:
            # Specialist 1: 100%-coverage full-footprint geophysical + hydrothermal-vent + piedmont physics
            x_ff = _extract_transpose_submatrix(mm, ff_cols, train_positions)
            clf_ff = _make_hgb(cell_seed + 2)
            clf_ff.fit(x_ff, y_train)
            del x_ff
            p_ff = bayes_prior_calibrate(
                _predict_foot_subset(clf_ff, mm, ff_cols, test_positions),
                pi_subsample=pi_sub,
                pi_true=pi_true,
            )
            del clf_ff

            # Specialist 2: Multi-sensor specialist with coverage-normalized LiDAR (no 'valid' flag!)
            x_ms = _extract_transpose_submatrix(mm, ms_cols, train_positions)
            clf_ms = _make_hgb(cell_seed + 3)
            clf_ms.fit(x_ms, y_train)
            del x_ms
            p_ms = bayes_prior_calibrate(
                _predict_foot_subset(clf_ms, mm, ms_cols, test_positions),
                pi_subsample=pi_sub,
                pi_true=pi_true,
            )
            del clf_ms

            p_phys = (0.55 * p_ff + 0.45 * p_ms).astype(np.float32)
            surf_exp2_foot[test_positions] = p_phys
            del p_ff, p_ms
        else:
            p_phys = None

        # EXP-3: Fold-visible structural-hydrothermal accommodation specialist M_struct
        if run_exp3 and surf_exp3_foot is not None and vis_acc_test_foot is not None and p_phys is not None:
            inner_vis_2d = masks["train_struct_visible"]
            inner_hid_2d = masks["train_struct_hidden"]
            inner_acc_foot, d_inner_vis_2d = build_fold_visible_accommodation(
                inner_vis_2d, footprint, aux_upflow, aux_tx, aux_ty
            )
            d_inner_foot = d_inner_vis_2d.ravel()[foot_idx]
            del d_inner_vis_2d

            elig_tr_foot = train_reg_foot & (d_inner_foot > 2.0)
            hid_foot = inner_hid_2d.ravel()[foot_idx] & elig_tr_foot
            s_pos = np.flatnonzero(hid_foot)
            s_neg_pool = np.flatnonzero(elig_tr_foot & (~train_pos_foot))
            s_neg = (
                rng.choice(s_neg_pool, size=NEG_SAMPLE_STRUCT, replace=False)
                if s_neg_pool.size > NEG_SAMPLE_STRUCT
                else s_neg_pool
            )
            s_positions = np.concatenate([s_pos, s_neg])
            y_struct = np.concatenate(
                [np.ones(s_pos.size, dtype=np.int8), np.zeros(s_neg.size, dtype=np.int8)]
            )
            pi_s_sub = float(s_pos.size) / float(s_positions.size)
            pi_s_true = float(s_pos.size) / float(max(int(elig_tr_foot.sum()), 1))

            x_st_static = _extract_transpose_submatrix(mm, struct_static_cols, s_positions)
            x_st_acc = inner_acc_foot[:, s_positions].T
            x_st = np.hstack([x_st_acc, x_st_static])
            del x_st_static, x_st_acc, inner_acc_foot

            clf_st = _make_hgb(cell_seed + 4)
            clf_st.fit(x_st, y_struct)
            del x_st

            # Predict M_struct on test_positions in chunks
            p_st_raw = np.empty(test_positions.size, dtype=np.float32)
            for start in range(0, test_positions.size, 350_000):
                end = min(test_positions.size, start + 350_000)
                sub_p = test_positions[start:end]
                xs_stat = _extract_transpose_submatrix(mm, struct_static_cols, sub_p)
                xs_acc = vis_acc_test_foot[:, sub_p].T
                xs_all = np.hstack([xs_acc, xs_stat])
                p_st_raw[start:end] = clf_st.predict_proba(xs_all)[:, 1].astype(np.float32)
                del xs_stat, xs_acc, xs_all
            del clf_st

            p_struct = bayes_prior_calibrate(p_st_raw, pi_subsample=pi_s_sub, pi_true=pi_s_true)
            del p_st_raw
            # Equal posterior mixture of coverage-deconfounded sensor specialist & structural-conduit specialist
            surf_exp3_foot[test_positions] = (0.50 * p_phys + 0.50 * p_struct).astype(np.float32)
            del p_struct

        gc.collect()

    out: dict[str, np.ndarray] = {}
    for key, vec in (("EXP-1", surf_exp1_foot), ("EXP-2", surf_exp2_foot), ("EXP-3", surf_exp3_foot)):
        if vec is not None:
            grid = np.full(SHAPE, np.nan, dtype=np.float32)
            grid.ravel()[foot_idx] = vec
            out[key] = grid
    return out


def _tile_pair_for_draw(
    dots: np.ndarray,
    draw: HideRecoverDraw,
    footprint: np.ndarray,
    foot_tiles: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    h, w = footprint.shape
    nr, nc = (h + 199) // 200, (w + 199) // 200
    pad_h, pad_w = nr * 200 - h, nc * 200 - w
    pred_m = (dots & footprint & (~draw.visible)).astype(np.float32)
    tp_m, fn_m, fp_m = additive_dti_pixel_maps(pred_m, draw.hidden & footprint)

    def _tsum(a: np.ndarray) -> np.ndarray:
        return np.pad(a, ((0, pad_h), (0, pad_w)), mode="constant").reshape(nr, 200, nc, 200).sum(axis=(1, 3)).ravel()

    tp_t = _tsum(tp_m)[foot_tiles]
    den_t = tp_t + ALPHA * _tsum(fp_m)[foot_tiles] + BETA * _tsum(fn_m)[foot_tiles]
    return tp_t, den_t


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default=os.environ.get("GEMSDOE31_DATA_DIR", "/tmp/gems_data"))
    parser.add_argument("--prepared-dir", default="/tmp/gems_data/prepared")
    parser.add_argument("--cache-dir", default="/tmp/gems_data/hvdc_cache")
    parser.add_argument("--registry-dir", default="/tmp/gems_registry_audit")
    parser.add_argument("--screen-seeds", type=int, nargs="+", default=[101, 102])
    parser.add_argument("--confirm-seeds", type=int, nargs="+", default=[201, 202])
    parser.add_argument("--out-dir", default="evidence/hvdc")
    parser.add_argument("--surfaces-dir", default="/tmp/gems_data/hvdc_surfaces")
    args = parser.parse_args()

    t_start = time.time()
    data_dir = Path(args.data_dir)
    prepared_dir = Path(args.prepared_dir)
    cache_dir = Path(args.cache_dir)
    out_dir = ROOT / args.out_dir
    surf_dir = Path(args.surfaces_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    surf_dir.mkdir(parents=True, exist_ok=True)

    print("[1/6] Verifying / building H31-HVDC feature cache...")
    meta = build_hvdc_feature_cache(data_dir, prepared_dir, cache_dir)
    n_feat = len(meta["feature_names"])

    with rasterio.open(data_dir / "sample_submission.tif") as src:
        footprint = np.isfinite(src.read(1))
    with rasterio.open(data_dir / "labels.tif") as src:
        catalogue = (src.read(1) == 1) & footprint
    with rasterio.open(data_dir / "external/derived_sgmc_faults_100m_u8.tif") as src:
        sgmc = (src.read(1) == 1) & footprint

    foot_idx = np.flatnonzero(footprint.ravel())
    mm_feat_major = np.memmap(
        cache_dir / "hvdc_foot_features.f32",
        dtype=np.float32,
        mode="r",
        shape=(n_feat, foot_idx.size),
    )
    mm = _ensure_sample_major_cache(cache_dir, n_feat, int(foot_idx.size))
    aux = np.load(cache_dir / "hvdc_struct_aux.npz")
    aux_upflow = aux["upflow_combined"]
    aux_tx = aux["struct_tx"]
    aux_ty = aux["struct_ty"]

    # 2. Single-Feature Leakage Canary (Protocol Rule 4)
    print("[2/6] Running single-feature leakage canary across all 55 static & fold-visible features...")
    canary_draw = make_hide_recover_draw(catalogue, footprint, seed=args.screen_seeds[0])
    canary_acc, canary_dvis = build_fold_visible_accommodation(
        canary_draw.visible, footprint, aux_upflow, aux_tx, aux_ty
    )
    canary_static = run_single_feature_leakage_canary(
        mm_feat_major,
        meta["feature_names"],
        canary_draw.hidden.ravel()[foot_idx],
        canary_draw.visible.ravel()[foot_idx],
        canary_dvis.ravel()[foot_idx],
        seed=args.screen_seeds[0],
    )
    del mm_feat_major
    canary_struct = run_single_feature_leakage_canary(
        canary_acc,
        list(FOLD_VISIBLE_NAMES),
        canary_draw.hidden.ravel()[foot_idx],
        canary_draw.visible.ravel()[foot_idx],
        canary_dvis.ravel()[foot_idx],
        seed=args.screen_seeds[0],
    )
    del canary_acc, canary_dvis
    all_canary_features = sorted(
        canary_static["features"] + canary_struct["features"],
        key=lambda r: r["symmetric_auc"],
        reverse=True,
    )
    canary_report = {
        "schema_version": 1,
        "evaluator_version": EVALUATOR_VERSION,
        "seed": args.screen_seeds[0],
        "auc_ceiling": 0.90,
        "n_features_tested": len(all_canary_features),
        "max_symmetric_auc": all_canary_features[0]["symmetric_auc"],
        "top_feature": all_canary_features[0]["feature"],
        "passed": bool(canary_static["passed"] and canary_struct["passed"]),
        "flagged_features": canary_static["flagged_features"] + canary_struct["flagged_features"],
        "features": all_canary_features,
    }
    (out_dir / "leakage_canary.json").write_text(json.dumps(canary_report, indent=2) + "\n")
    if not canary_report["passed"]:
        raise RuntimeError(f"LEAKAGE CANARY FAILED: {canary_report['flagged_features']}")
    print(f"      Canary PASSED (max symmetric AUC = {canary_report['max_symmetric_auc']:.4f} "
          f"on {canary_report['top_feature']}; ceiling 0.90)")

    # Precompute spatial folds & bootstrap tile mask
    folds = build_spatial_folds(footprint, collar_m=DEFAULT_COLLAR_M)
    h, w = footprint.shape
    nr, nc = (h + 199) // 200, (w + 199) // 200
    pad_h, pad_w = nr * 200 - h, nc * 200 - w
    foot_tiles = (
        np.pad(footprint.astype(np.float64), ((0, pad_h), (0, pad_w)), mode="constant")
        .reshape(nr, 200, nc, 200)
        .sum(axis=(1, 3))
        .ravel()
        > 0
    )

    arm_Specs = {
        "EXP-1": {
            "name": "ArmD-Clean-Poisson",
            "emitter": "poisson",
            "description": "38 clean sensor bands (excluding 'valid'), 21.25 km buffered HGB + 2.8 px Poisson-disk",
        },
        "EXP-2": {
            "name": "H31-HVDC-Physics-Poisson",
            "emitter": "poisson",
            "description": "Coverage-deconfounded Dual-Specialist + H31-HVDC hydrothermal/piedmont physics + 2.8 px Poisson-disk",
        },
        "EXP-3": {
            "name": "H31-HVDC-Submod300",
            "emitter": "submod300",
            "description": "H31-HVDC Dual-Specialist + fold-visible conduit accommodation + exact 300 m CELF submodular max-cover",
        },
    }

    # 3. Screen draws [101, 102] across all 3 preregistered experiments
    print(f"[3/6] Running frozen 3-experiment budget on screen seeds {args.screen_seeds}...")
    screen_draws: dict[str, list[dict]] = {k: [] for k in arm_Specs}
    screen_tiles: dict[str, list[tuple[np.ndarray, np.ndarray]]] = {k: [] for k in arm_Specs}

    for s in args.screen_seeds:
        t_draw = time.time()
        draw = make_hide_recover_draw(catalogue, footprint, seed=s)
        d_vis = distance_transform_edt(~draw.visible)
        elig = footprint & (d_vis > 2.0)

        surfaces = fit_and_predict_draw(
            mm=mm,
            meta=meta,
            aux_upflow=aux_upflow,
            aux_tx=aux_tx,
            aux_ty=aux_ty,
            footprint=footprint,
            foot_idx=foot_idx,
            folds=folds,
            visible_2d=draw.visible,
            seed=s,
            run_exp1=True,
            run_exp2=True,
            run_exp3=True,
        )
        for arm_id, spec in arm_Specs.items():
            surf = surfaces[arm_id]
            if spec["emitter"] == "poisson":
                dots = priority_poisson_thin(surf, elig, budget=DOT_BUDGET, min_dist_px=2.8)
            else:
                dots, _ = allocate_submodular_dots(surf, elig, budget=DOT_BUDGET)
            rep = score_holdout_draw(dots, draw, footprint)
            screen_draws[arm_id].append(rep)
            screen_tiles[arm_id].append(_tile_pair_for_draw(dots, draw, footprint, foot_tiles))
            print(
                f"      seed={s} {arm_id} ({spec['name']}): HOLDOUT-DTI={rep['holdout_dti']:.6f} "
                f"95%CI=[{rep['ci95_low']:.6f}, {rep['ci95_high']:.6f}] "
                f"(halo300m={rep['holdout_dti_halo300m']:.6f})"
            )
        del surfaces
        gc.collect()
        print(f"      completed seed={s} in {time.time() - t_draw:.1f}s (peak RSS {_peak_rss_mb():.0f} MB)")

    screen_summary: dict[str, dict] = {}
    for arm_id, spec in arm_Specs.items():
        mean_dti, ci_lo, ci_hi = pool_multi_draw_bootstrap(screen_tiles[arm_id])
        mean_halo = float(np.mean([d["holdout_dti_halo300m"] for d in screen_draws[arm_id]]))
        screen_summary[arm_id] = {
            "arm_id": arm_id,
            "name": spec["name"],
            "description": spec["description"],
            "emitter": spec["emitter"],
            "metric_label": "HOLDOUT-DTI",
            "evaluator_version": EVALUATOR_VERSION,
            "screen_seeds": args.screen_seeds,
            "screen_mean_holdout_dti": round(mean_dti, 6),
            "screen_ci95": [round(ci_lo, 6), round(ci_hi, 6)],
            "screen_mean_halo300m_dti": round(mean_halo, 6),
            "screen_draws": screen_draws[arm_id],
        }
        print(
            f"  --> SCREEN SUMMARY {arm_id} ({spec['name']}): "
            f"HOLDOUT-DTI = {mean_dti:.6f} (95% CI [{ci_lo:.6f}, {ci_hi:.6f}])"
        )

    best_arm = max(["EXP-1", "EXP-2", "EXP-3"], key=lambda k: screen_summary[k]["screen_mean_holdout_dti"])
    print(f"[4/6] Best screen arm: {best_arm} ({arm_Specs[best_arm]['name']}). "
          f"Running untuned confirmation seeds {args.confirm_seeds} vs EXP-1...")

    # 4. Untuned confirmation draws [201, 202] for EXP-1 (control) and best_arm (plus EXP-2 if best_arm==EXP-3 for full table!)
    confirm_draws: dict[str, list[dict]] = {k: [] for k in arm_Specs}
    confirm_tiles: dict[str, list[tuple[np.ndarray, np.ndarray]]] = {k: [] for k in arm_Specs}
    for s in args.confirm_seeds:
        t_draw = time.time()
        draw = make_hide_recover_draw(catalogue, footprint, seed=s)
        d_vis = distance_transform_edt(~draw.visible)
        elig = footprint & (d_vis > 2.0)

        surfaces = fit_and_predict_draw(
            mm=mm,
            meta=meta,
            aux_upflow=aux_upflow,
            aux_tx=aux_tx,
            aux_ty=aux_ty,
            footprint=footprint,
            foot_idx=foot_idx,
            folds=folds,
            visible_2d=draw.visible,
            seed=s,
            run_exp1=True,
            run_exp2=True,
            run_exp3=True,
        )
        for arm_id, spec in arm_Specs.items():
            surf = surfaces[arm_id]
            if spec["emitter"] == "poisson":
                dots = priority_poisson_thin(surf, elig, budget=DOT_BUDGET, min_dist_px=2.8)
            else:
                dots, _ = allocate_submodular_dots(surf, elig, budget=DOT_BUDGET)
            rep = score_holdout_draw(dots, draw, footprint)
            confirm_draws[arm_id].append(rep)
            confirm_tiles[arm_id].append(_tile_pair_for_draw(dots, draw, footprint, foot_tiles))
            print(
                f"      confirm seed={s} {arm_id} ({spec['name']}): HOLDOUT-DTI={rep['holdout_dti']:.6f} "
                f"95%CI=[{rep['ci95_low']:.6f}, {rep['ci95_high']:.6f}]"
            )
        del surfaces
        gc.collect()
        print(f"      completed confirm seed={s} in {time.time() - t_draw:.1f}s")

    for arm_id in arm_Specs:
        c_mean, c_lo, c_hi = pool_multi_draw_bootstrap(confirm_tiles[arm_id])
        all_tiles = screen_tiles[arm_id] + confirm_tiles[arm_id]
        all_mean, all_lo, all_hi = pool_multi_draw_bootstrap(all_tiles)
        screen_summary[arm_id].update(
            {
                "confirm_seeds": args.confirm_seeds,
                "confirm_mean_holdout_dti": round(c_mean, 6),
                "confirm_ci95": [round(c_lo, 6), round(c_hi, 6)],
                "confirm_draws": confirm_draws[arm_id],
                "pooled_4draw_mean_holdout_dti": round(all_mean, 6),
                "pooled_4draw_ci95": [round(all_lo, 6), round(all_hi, 6)],
                "delta_vs_exp1_confirm": round(
                    c_mean - float(np.mean([d["holdout_dti"] for d in confirm_draws["EXP-1"]])), 6
                ),
                "delta_vs_exp1_pooled4": round(
                    all_mean
                    - float(
                        np.mean(
                            [d["holdout_dti"] for d in (screen_draws["EXP-1"] + confirm_draws["EXP-1"])]
                        )
                    ),
                    6,
                ),
            }
        )

    # 5. Full-footprint 4-fold OOF stitch on full labels.tif (visible = catalogue) for live candidate + OFFCAT-PROXY-DTI
    print("[5/6] Fitting full-footprint 21.25 km buffered 4-fold OOF stitch on labels.tif...")
    d_cat = distance_transform_edt(~catalogue)
    elig_live = footprint & (d_cat > 2.0)
    sgmc_far = sgmc & (d_cat > 3.0)

    live_surfaces = fit_and_predict_draw(
        mm=mm,
        meta=meta,
        aux_upflow=aux_upflow,
        aux_tx=aux_tx,
        aux_ty=aux_ty,
        footprint=footprint,
        foot_idx=foot_idx,
        folds=folds,
        visible_2d=catalogue,
        seed=20261025,
        run_exp1=True,
        run_exp2=True,
        run_exp3=True,
    )

    reg_paths = sorted((ROOT / "docs/downloads").glob("*.tif"))
    reg_dir = Path(args.registry_dir)
    if reg_dir.is_dir():
        reg_paths.extend(sorted(reg_dir.glob("*.tif")))

    for arm_id, spec in arm_Specs.items():
        surf = live_surfaces[arm_id]
        if spec["emitter"] == "poisson":
            dots = priority_poisson_thin(surf, elig_live, budget=DOT_BUDGET, min_dist_px=2.8)
            emit_info = {"emitted_dots": int(dots.sum())}
        else:
            dots, emit_info = allocate_submodular_dots(surf, elig_live, budget=DOT_BUDGET)

        offcat_res = dti(dots.astype(np.float32), sgmc_far)
        dup_res = check_registry_duplicate_canary(surf, dots, footprint, reg_paths)
        screen_summary[arm_id]["live_oof_emitted_dots"] = int(dots.sum())
        screen_summary[arm_id]["emit_info"] = emit_info
        screen_summary[arm_id]["offcat_proxy_dti_sgmc_gt300m"] = round(float(offcat_res["DTI"]), 6)
        screen_summary[arm_id]["duplicate_canary"] = {
            "passed": dup_res["passed"],
            "max_abs_spearman": dup_res["max_abs_spearman"],
            "max_spearman_raster": dup_res["max_spearman_raster"],
            "max_symmetric_3px_overlap": dup_res["max_symmetric_3px_overlap"],
            "max_overlap_raster": dup_res["max_overlap_raster"],
        }
        np.savez_compressed(
            surf_dir / f"{arm_id}_live_oof.npz",
            surface=surf.astype(np.float32),
            dots=dots.astype(np.uint8),
        )
        if arm_id == best_arm:
            (out_dir / "duplicate_canary_full.json").write_text(json.dumps(dup_res, indent=2) + "\n")
        print(
            f"      {arm_id} live OOF ({int(dots.sum()):,} dots): "
            f"OFFCAT-PROXY-DTI={offcat_res['DTI']:.6f} | "
            f"dup_pass={dup_res['passed']} (max |rho|={dup_res['max_abs_spearman']:.4f}, "
            f"max 3px overlap={dup_res['max_symmetric_3px_overlap']:.4f})"
        )

    # Also benchmark all sibling registry rasters on the exact same OFFCAT-PROXY-DTI (SGMC > 300 m)
    print("[6/6] Computing OFFCAT-PROXY-DTI reference table across sibling registry rasters...")
    sibling_offcat = []
    for rpath in sorted(reg_dir.glob("*.tif")) if reg_dir.is_dir() else []:
        with rasterio.open(rpath) as src:
            rarr = src.read(1)
        rbin = (np.nan_to_num(rarr, nan=0.0) > 0.0) & footprint
        rdti = dti(rbin.astype(np.float32), sgmc_far)
        sibling_offcat.append(
            {
                "raster": rpath.name,
                "dots": int(rbin.sum()),
                "dots_in_cat_2px_collar": int((rbin & (d_cat <= 2.0)).sum()),
                "offcat_proxy_dti_sgmc_gt300m": round(float(rdti["DTI"]), 6),
            }
        )
    sibling_offcat.sort(key=lambda r: r["offcat_proxy_dti_sgmc_gt300m"], reverse=True)

    elapsed_s = time.time() - t_start
    results_payload = {
        "schema_version": 1,
        "preregistration": "knowledge/2026-10-25_h31_hvdc_preregistration.md",
        "evaluator_version": EVALUATOR_VERSION,
        "collar_m": DEFAULT_COLLAR_M,
        "dot_budget": DOT_BUDGET,
        "elapsed_seconds": round(elapsed_s, 2),
        "elapsed_minutes": round(elapsed_s / 60.0, 2),
        "budget_limit_experiments": 3,
        "experiments_executed": 3,
        "budget_limit_minutes": 120.0,
        "peak_rss_mb": round(_peak_rss_mb(), 1),
        "leakage_canary_passed": canary_report["passed"],
        "leakage_canary_max_symmetric_auc": canary_report["max_symmetric_auc"],
        "selected_arm": best_arm,
        "selected_arm_name": arm_Specs[best_arm]["name"],
        "experiments": screen_summary,
        "sibling_offcat_proxy_reference": sibling_offcat,
    }
    out_file = out_dir / "hvdc_experiment_results.json"
    out_file.write_text(json.dumps(results_payload, indent=2) + "\n")
    print(f"\nDONE in {elapsed_s / 60.0:.2f} min (peak RSS {_peak_rss_mb():.1f} MB) -> {out_file}")


if __name__ == "__main__":
    main()
