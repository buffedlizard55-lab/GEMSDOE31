#!/usr/bin/env python3
"""RBU31 runner — regime-balanced union detector (preregistered, 3 experiments).

Frozen design: ``knowledge/2026-10-25_rbu31_preregistration.md``.
Reuses the shared H31-E evaluator (``scripts/evaluate_holdout.py``), metric,
cached feature stacks and ``scripts/submission_writer.py`` unchanged — no
private evaluator fork. Candidate = ONE HistGradientBoosting model per fold
on the union of raw-39 prepared bands and the 40 translation-invariant
SCGP/LiDAR static features, trained with regime-balanced sample weights
(piedmont ``det_elev <= 50 m`` vs mountain). Comparator = same-fold
Baseline-D (raw-39, class_weight 2:1). Emission (both arms) =
``poisson_disk_emit`` 2.8 px with visible/catalogue distance > 2 px.

Experiments: (1) screen draw 101 + leakage canary, (2) fresh confirmation
draws 202+303 if the screen passes, (3) final OOF emission + SGMC
dual-regime proxies + duplicate canary + validated GeoTIFF packaging.

Variant ``--variant local`` runs the preregistered RBU31-B amendment
(``knowledge/2026-10-25_rbu31b_amendment_preregistration.md``): the
candidate ranking surface is replaced by its masked 12 km locally
standardized rank (``gemsdoe31.local_standardize``) before every emission.
Everything else — folds, features, weights, seeds, gates — is identical.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import evaluate_holdout as eh  # noqa: E402
from gemsdoe31 import metric  # noqa: E402
from gemsdoe31.local_standardize import gaussian_blur_fft, locally_standardized_rank  # noqa: E402
from gemsdoe31.raster import connected_components  # noqa: E402
from gemsdoe31.scgp_features import STATIC_FEATURE_NAMES, build_static_h31e_stack  # noqa: E402
from gemsdoe31.submodular_emit import check_duplicate_canary, poisson_disk_emit  # noqa: E402
from submission_writer import emit_and_validate_submission  # noqa: E402

DATA = ROOT / "data"
DOWNLOADS = ROOT / "docs/downloads"
PIEDMONT_DET_MAX = 50.0


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def regime_sample_weights(y: np.ndarray, is_piedmont: np.ndarray, det_finite: np.ndarray) -> np.ndarray:
    """Balanced risk: each class contributes W_c total, split equally across regimes.

    W_1 = 2 * W_0 (same positive emphasis as Baseline-D). Non-finite regime
    samples receive their class-average weight. Mean-normalised to 1.
    """
    w = np.zeros(y.size, dtype=np.float64)
    for c, w_total in ((0, 1.0), (1, 2.0)):
        m_c = y == c
        for reg in (True, False):
            m = m_c & det_finite & (is_piedmont == reg)
            if m.any():
                w[m] = (w_total / 2.0) / m.sum()
        m_nan = m_c & ~det_finite
        if m_nan.any():
            finite_w = w[m_c & det_finite]
            w[m_nan] = finite_w.mean() if finite_w.size else w_total / max(m_c.sum(), 1)
    w *= y.size / w.sum()
    return w.astype(np.float64)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=("plain", "local"), default="plain")
    cli = parser.parse_args()
    local_variant = cli.variant == "local"
    out = ROOT / ("evidence/regime31b" if local_variant else "evidence/regime31")
    slug = "rbu31b-localunion" if local_variant else "rbu31-regimeunion"
    label = ("RBU31-B locally-standardized regime-balanced union (raw39 + SCGP40)"
             if local_variant else "RBU31 regime-balanced union (raw39 + SCGP40)")
    prereg = ("knowledge/2026-10-25_rbu31b_amendment_preregistration.md"
              if local_variant else "knowledge/2026-10-25_rbu31_preregistration.md")

    def maybe_standardize(grid: np.ndarray, mask: np.ndarray,
                          blurred_mask: np.ndarray | None = None) -> np.ndarray:
        if not local_variant:
            return grid
        return locally_standardized_rank(grid, mask, blurred_mask=blurred_mask)

    t_start = time.monotonic()
    out.mkdir(parents=True, exist_ok=True)
    results: dict[str, Any] = {
        "candidate": label,
        "variant": cli.variant,
        "preregistration": prereg,
        "evaluator_version": eh.EVALUATOR_VERSION,
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "experiments_budget": 3,
    }

    log("[1/6] Loading masks and cached stacks (SCGP stack builds on first run)")
    with rasterio.open(DATA / "sample_submission.tif") as src:
        footprint = np.isfinite(src.read(1))
    with rasterio.open(DATA / "labels.tif") as src:
        catalogue = (src.read(1) == 1) & footprint
    with rasterio.open(DATA / "external/derived_sgmc_faults_100m_u8.tif") as src:
        sgmc = (src.read(1) == 1) & footprint
    n_foot = int(footprint.sum())
    comp_global = connected_components(catalogue)
    raw_quads, eroded_quads, split_rc = eh.build_quadrants(footprint)
    blurred_quad_masks = ([gaussian_blur_fft(q.astype(np.float32)) for q in eroded_quads]
                          if local_variant else [None] * 4)

    h31e_mm, _ = build_static_h31e_stack(DATA, DATA / "prepared" / "h31e_static.f32")
    prep_meta = json.loads((DATA / "prepared" / "features.json").read_text())
    prep_names: list[str] = prep_meta["bands"]
    prep_mm = np.memmap(DATA / "prepared" / "features.f32", dtype=np.float32, mode="r",
                        shape=(len(prep_names), footprint.shape[0], footprint.shape[1]))
    base_indices = list(range(39))
    base_names = [prep_names[i] for i in base_indices]
    scgp_indices = eh.EXP3_LIDAR_INDICES
    scgp_names = [STATIC_FEATURE_NAMES[i] for i in scgp_indices]
    union_names = [f"raw::{n}" for n in base_names] + [f"scgp::{n}" for n in scgp_names]
    assert len(union_names) == 79, len(union_names)
    det_idx = prep_names.index("det_elev")

    foot_r, foot_c = np.nonzero(footprint)
    foot_id_grid = np.full(footprint.shape, -1, dtype=np.int32)
    foot_id_grid[footprint] = np.arange(n_foot, dtype=np.int32)

    def union_matrix(ids: np.ndarray) -> np.ndarray:
        x_raw = eh.read_clean_base_rows(prep_mm, base_indices, foot_r[ids], foot_c[ids])
        x_scgp = np.asarray(h31e_mm[scgp_indices, :][:, ids], dtype=np.float32).T
        return np.hstack([x_raw, x_scgp]).astype(np.float32)

    log("[2/6] Training 4 folds: Baseline-D (raw39) and RBU31 (union79, regime-balanced)")
    cand_config = {k: v for k, v in eh.HGB_CONFIG.items() if k != "class_weight"}
    fold_models_base: list[HistGradientBoostingClassifier] = []
    fold_models_rbu: list[HistGradientBoostingClassifier] = []
    fold_dist_to_quad: list[np.ndarray] = []
    fold_stats = []
    for q in range(4):
        t0 = time.monotonic()
        dist_q = distance_transform_edt(~(raw_quads[q] & footprint)).astype(np.float32)
        fold_dist_to_quad.append(dist_q)
        forbidden = np.unique(comp_global[(dist_q <= eh.BUFFER_PX) & catalogue])
        forbidden = forbidden[forbidden > 0]
        train_domain = footprint & (dist_q > eh.BUFFER_PX) & ~np.isin(comp_global, forbidden)
        train_vis = catalogue & train_domain
        pos_ids = foot_id_grid[train_vis]
        neg_pool = foot_id_grid[train_domain & ~train_vis]
        rng = np.random.default_rng(5000 + q)
        neg_ids = rng.choice(neg_pool, size=min(eh.NEG_SAMPLE_CAP, neg_pool.size), replace=False)
        sample_ids = np.concatenate([pos_ids, neg_ids])
        y = np.concatenate([np.ones(pos_ids.size, dtype=np.int32), np.zeros(neg_ids.size, dtype=np.int32)])

        sr, sc = foot_r[sample_ids], foot_c[sample_ids]
        x_base = eh.read_clean_base_rows(prep_mm, base_indices, sr, sc)
        m_base = HistGradientBoostingClassifier(**eh.HGB_CONFIG, random_state=42 + q)
        m_base.fit(x_base, y)
        fold_models_base.append(m_base)
        del x_base

        det_vals = np.asarray(prep_mm[det_idx, sr, sc], dtype=np.float32).copy()
        det_vals[np.abs(det_vals) > 1e20] = np.nan
        det_finite = np.isfinite(det_vals)
        is_pied = det_finite & (det_vals <= PIEDMONT_DET_MAX)
        weights = regime_sample_weights(y, is_pied, det_finite)
        x_union = union_matrix(sample_ids)
        m_rbu = HistGradientBoostingClassifier(**cand_config, random_state=342 + q)
        m_rbu.fit(x_union, y, sample_weight=weights)
        fold_models_rbu.append(m_rbu)
        fold_stats.append({
            "fold": ("NW", "NE", "SW", "SE")[q], "train_positives": int(pos_ids.size),
            "train_negatives_sampled": int(neg_ids.size),
            "pos_piedmont": int((is_pied & (y == 1)).sum()), "pos_mountain": int(((~is_pied) & det_finite & (y == 1)).sum()),
            "fit_seconds": round(time.monotonic() - t0, 1)})
        log(f"  fold {fold_stats[-1]['fold']}: pos={pos_ids.size:,} neg={neg_ids.size:,} "
            f"(pos pied={fold_stats[-1]['pos_piedmont']:,} mtn={fold_stats[-1]['pos_mountain']:,}) "
            f"{fold_stats[-1]['fit_seconds']}s")
        del x_union
        gc.collect()
    results["fold_training"] = fold_stats
    results["union_features"] = union_names

    # ---------------------------------------------------------------- canary
    def run_union_canary(hidden_tests: list[np.ndarray], vis_quads: list[np.ndarray]) -> dict:
        rng = np.random.default_rng(20261025)
        pos_ids, neg_ids = [], []
        for q in range(4):
            eval_dom = eroded_quads[q] & ~vis_quads[q]
            p = foot_id_grid[hidden_tests[q] & eval_dom]
            n = foot_id_grid[eval_dom & ~hidden_tests[q]]
            if n.size > 50_000:
                n = rng.choice(n, size=50_000, replace=False)
            pos_ids.append(p)
            neg_ids.append(n)
        eval_ids = np.concatenate(pos_ids + neg_ids)
        y_eval = np.concatenate([np.ones(sum(x.size for x in pos_ids), dtype=np.int8),
                                 np.zeros(sum(x.size for x in neg_ids), dtype=np.int8)])
        er, ec = foot_r[eval_ids], foot_c[eval_ids]
        rows = []
        for j, name in enumerate(union_names):
            if j < 39:
                vec = np.asarray(prep_mm[base_indices[j], er, ec], dtype=np.float32).copy()
                vec[np.abs(vec) > 1e20] = np.nan
            else:
                vec = np.asarray(h31e_mm[scgp_indices[j - 39], eval_ids], dtype=np.float32)
            fin = np.isfinite(vec)
            auc = 0.5
            if fin.sum() >= 100 and len(np.unique(y_eval[fin])) == 2:
                raw = float(roc_auc_score(y_eval[fin], vec[fin]))
                auc = max(raw, 1.0 - raw)
            rows.append({"feature": name, "single_feature_auc_two_sided": round(auc, 6),
                         "finite_eval_fraction": round(float(fin.mean()), 4),
                         "leaked": bool(auc > eh.AUC_LEAKAGE_STOP)})
        leaked = [r["feature"] for r in rows if r["leaked"]]
        return {"threshold_auc_stop_gt": eh.AUC_LEAKAGE_STOP, "features_tested": len(rows),
                "max_two_sided_auc": round(max(r["single_feature_auc_two_sided"] for r in rows), 6),
                "leaked_features": leaked, "passed": not leaked,
                "rows": sorted(rows, key=lambda r: -r["single_feature_auc_two_sided"])}

    # ---------------------------------------------------------------- draws
    def evaluate_draw(draw_seed: int, *, with_canary: bool = False) -> dict:
        hidden_tests, vis_quads, seg_counts = [], [], []
        d_vis_list = []
        for q in range(4):
            ht, vq, chosen = eh.hide_whole_segments(catalogue, comp_global, raw_quads[q],
                                                    eroded_quads[q], seed=draw_seed * 100 + q)
            hidden_tests.append(ht)
            vis_quads.append(vq)
            seg_counts.append(len(chosen))
            d_vis_list.append(distance_transform_edt(~vq).astype(np.float32))
        draw_out: dict[str, Any] = {"draw": draw_seed, "withheld_segments_by_fold": seg_counts}
        if with_canary:
            log("[3/6] Leakage canary: 79 union features alone on screen draw 101")
            canary = run_union_canary(hidden_tests, vis_quads)
            (out / "leakage_canary.json").write_text(json.dumps(canary, indent=1) + "\n")
            log(f"  max two-sided AUC {canary['max_two_sided_auc']:.4f} (stop > 0.90) passed={canary['passed']}")
            if not canary["passed"]:
                raise RuntimeError(f"LEAKAGE STOP: {canary['leaked_features']}")
            draw_out["leakage_canary_summary"] = {k: canary[k] for k in
                ("features_tested", "max_two_sided_auc", "passed")}
            results["leakage_canary"] = draw_out["leakage_canary_summary"]
        preds_base, preds_rbu = [], []
        for q in range(4):
            eval_dom = eroded_quads[q] & ~vis_quads[q]
            q_ids = foot_id_grid[eroded_quads[q]]
            n_dots = int(round(eh.BUDGET_DENSITY * int(eroded_quads[q].sum())))
            valid_emit = eval_dom & (d_vis_list[q] > 2.0)
            qr, qc = foot_r[q_ids], foot_c[q_ids]
            p_base = eh.predict_chunked(fold_models_base[q],
                lambda s, e: eh.read_clean_base_rows(prep_mm, base_indices, qr[s:e], qc[s:e]), q_ids.size)
            g_base = np.zeros(footprint.shape, dtype=np.float32)
            g_base[eroded_quads[q]] = p_base
            preds_base.append(poisson_disk_emit(g_base, valid_emit, n_dots, min_dist_px=2.8))
            p_rbu = eh.predict_chunked(fold_models_rbu[q],
                lambda s, e: union_matrix(q_ids[s:e]), q_ids.size)
            g_rbu = np.zeros(footprint.shape, dtype=np.float32)
            g_rbu[eroded_quads[q]] = p_rbu
            if local_variant:
                g_rbu = maybe_standardize(g_rbu, eroded_quads[q],
                                          blurred_mask=blurred_quad_masks[q])
            preds_rbu.append(poisson_disk_emit(g_rbu, valid_emit, n_dots, min_dist_px=2.8))
            del g_base, g_rbu
        truths = [hidden_tests[q] & eroded_quads[q] & ~vis_quads[q] for q in range(4)]
        res_b = eh.pooled_dti_and_bootstrap_ci(preds_base, truths, comp_global, seed=draw_seed + 1000)
        res_r = eh.pooled_dti_and_bootstrap_ci(preds_rbu, truths, comp_global, seed=draw_seed + 1000)
        boot_r, boot_b = res_r.pop("_boot_samples"), res_b.pop("_boot_samples")
        diff = boot_r - boot_b
        draw_out.update({"baseline_d_poisson": res_b, "rbu31_poisson": res_r,
                         "paired_delta_dti": float(res_r["pooled_dti"] - res_b["pooled_dti"]),
                         "paired_delta_ci95": [float(np.quantile(diff, 0.025)), float(np.quantile(diff, 0.975))],
                         "folds_won_out_of_4": int(sum(1 for a, b in zip(res_r["per_fold"], res_b["per_fold"]) if a["dti"] > b["dti"])),
                         "_boot_rbu": boot_r, "_boot_base": boot_b})
        gc.collect()
        return draw_out

    log("[3/6] Experiment 1: screen draw 101")
    screen = evaluate_draw(101, with_canary=True)
    screen.pop("_boot_rbu")
    screen.pop("_boot_base")
    results["experiment_1_screen_draw_101"] = screen
    log(f"  Baseline-D HOLDOUT-DTI {screen['baseline_d_poisson']['pooled_dti']:.5f} | "
        f"RBU31 {screen['rbu31_poisson']['pooled_dti']:.5f} | delta {screen['paired_delta_dti']:+.5f} "
        f"CI {screen['paired_delta_ci95']} | folds {screen['folds_won_out_of_4']}/4")
    screen_pass = bool(screen["paired_delta_dti"] > 0.002 and screen["folds_won_out_of_4"] >= 3)
    results["screen_pass"] = screen_pass
    (out / "results_partial.json").write_text(json.dumps(results, indent=1, allow_nan=False) + "\n")

    confirm = None
    if screen_pass:
        log("[4/6] Experiment 2: fresh confirmation draws 202 + 303")
        draws = [evaluate_draw(d) for d in (202, 303)]
        boot_r = 0.5 * (draws[0].pop("_boot_rbu") + draws[1].pop("_boot_rbu"))
        boot_b = 0.5 * (draws[0].pop("_boot_base") + draws[1].pop("_boot_base"))
        def pool(key: str) -> float:
            tp = sum(r[key]["tpw"] for r in draws)
            fp = sum(r[key]["fpw"] for r in draws)
            fn = sum(r[key]["fnw"] for r in draws)
            return float(tp / (tp + 0.2 * fp + 0.8 * fn + metric.EPSILON))
        confirm = {"draws": [202, 303],
                   "withheld_positives_pooled": int(sum(r["baseline_d_poisson"]["withheld_positives"] for r in draws)),
                   "baseline_d_pooled_dti": pool("baseline_d_poisson"),
                   "baseline_d_ci95": [float(np.quantile(boot_b, 0.025)), float(np.quantile(boot_b, 0.975))],
                   "rbu31_pooled_dti": pool("rbu31_poisson"),
                   "rbu31_ci95": [float(np.quantile(boot_r, 0.025)), float(np.quantile(boot_r, 0.975))],
                   "per_draw": draws}
        confirm["paired_delta_dti"] = float(confirm["rbu31_pooled_dti"] - confirm["baseline_d_pooled_dti"])
        confirm["paired_delta_ci95"] = [float(np.quantile(boot_r - boot_b, 0.025)),
                                        float(np.quantile(boot_r - boot_b, 0.975))]
        log(f"  Confirm pooled: Baseline-D {confirm['baseline_d_pooled_dti']:.5f} | "
            f"RBU31 {confirm['rbu31_pooled_dti']:.5f} | delta {confirm['paired_delta_dti']:+.5f} "
            f"CI {confirm['paired_delta_ci95']}")
        results["experiment_2_confirmation"] = confirm
        (out / "results_partial.json").write_text(json.dumps(results, indent=1, allow_nan=False) + "\n")
    else:
        log("[4/6] Screen failed — confirmation not run (preregistered stop)")

    log("[5/6] Experiment 3: full-footprint OOF surfaces, emission, SGMC proxies")
    d_cat = distance_transform_edt(~catalogue).astype(np.float32)
    oof_num_r = np.zeros(n_foot, dtype=np.float64)
    oof_num_b = np.zeros(n_foot, dtype=np.float64)
    oof_w = np.zeros(n_foot, dtype=np.float64)
    for q in range(4):
        dq = fold_dist_to_quad[q][footprint]
        wq = np.where(dq <= 0.0, 1.0, np.where(dq < eh.BUFFER_PX,
                                               0.5 * (1.0 + np.cos(np.pi * dq / eh.BUFFER_PX)), 0.0))
        sel = np.flatnonzero(wq > 0.0)
        p_r = eh.predict_chunked(fold_models_rbu[q], lambda s, e: union_matrix(sel[s:e]), sel.size)
        sr, sc = foot_r[sel], foot_c[sel]
        p_b = eh.predict_chunked(fold_models_base[q],
            lambda s, e: eh.read_clean_base_rows(prep_mm, base_indices, sr[s:e], sc[s:e]), sel.size)
        oof_num_r[sel] += wq[sel] * p_r
        oof_num_b[sel] += wq[sel] * p_b
        oof_w[sel] += wq[sel]
        log(f"  OOF fold {q} done ({sel.size:,} cells)")
    surf_rbu = np.zeros(footprint.shape, dtype=np.float32)
    surf_base = np.zeros(footprint.shape, dtype=np.float32)
    surf_rbu[footprint] = (oof_num_r / np.maximum(oof_w, 1e-8)).astype(np.float32)
    if local_variant:
        surf_rbu = maybe_standardize(surf_rbu, footprint,
                                     blurred_mask=gaussian_blur_fft(footprint.astype(np.float32)))
    surf_base[footprint] = (oof_num_b / np.maximum(oof_w, 1e-8)).astype(np.float32)

    valid_full = footprint & (d_cat > 2.0)
    dots_rbu = poisson_disk_emit(surf_rbu, valid_full, eh.FULL_DOT_BUDGET, min_dist_px=2.8)
    dots_base = poisson_disk_emit(surf_base, valid_full, eh.FULL_DOT_BUDGET, min_dist_px=2.8)

    det_grid = np.asarray(prep_mm[det_idx], dtype=np.float32).copy()
    det_grid[np.abs(det_grid) > 1e20] = np.nan
    piedmont = footprint & np.isfinite(det_grid) & (det_grid <= PIEDMONT_DET_MAX)
    mountain = footprint & np.isfinite(det_grid) & (det_grid > PIEDMONT_DET_MAX)
    sgmc_off = sgmc & (d_cat > 3.0)
    proxies = {}
    def load_dots(path: Path) -> np.ndarray:
        with rasterio.open(path) as src:
            return (np.nan_to_num(src.read(1), nan=0.0) > 0.5) & footprint
    refs_dots = {
        "rbu31": dots_rbu, "baseline_d_final": dots_base,
        "h33_2_b2_actual_peer_file": load_dots(ROOT / "data/prior_audit/GEMSDOE32/docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"),
        "h31e_scgp_submod_local": load_dots(DOWNLOADS / "gemsdoe31-scgp-submod-37654-20261025-fa735287-nan.tif"),
    }
    for name, dots in refs_dots.items():
        proxies[name] = {
            "dots": int(dots.sum()),
            "sgmc_all_dti": float(metric.dti(dots.astype(np.float32), sgmc_off)["DTI"]),
            "sgmc_piedmont_dti": float(metric.dti(dots.astype(np.float32), sgmc_off & piedmont)["DTI"]),
            "sgmc_mountain_dti": float(metric.dti(dots.astype(np.float32), sgmc_off & mountain)["DTI"]),
        }
        log(f"  proxy {name}: all={proxies[name]['sgmc_all_dti']:.4f} "
            f"pied={proxies[name]['sgmc_piedmont_dti']:.4f} mtn={proxies[name]['sgmc_mountain_dti']:.4f}")
    results["experiment_3_sgmc_proxies"] = {
        "evidence_class": "COMPUTED (off-catalogue SGMC proxy; not a competition score)",
        "truth_pixels": {"all": int(sgmc_off.sum()), "piedmont": int((sgmc_off & piedmont).sum()),
                         "mountain": int((sgmc_off & mountain).sum())},
        "candidates": proxies,
        "rbu31_piedmont_dot_share": float((dots_rbu & piedmont).sum() / max(dots_rbu.sum(), 1)),
    }

    log("[6/6] Duplicate canary (surface + final dots) and GeoTIFF packaging")
    ref_entries: list[dict[str, Any]] = []
    for item in json.loads((ROOT / "registry/submissions.json").read_text())["files"]:
        if "file_nan" in item and (ROOT / item["file_nan"]).is_file():
            ref_entries.append({"id": f"local::{item['id']}", "path": ROOT / item["file_nan"],
                                "source_group": "GEMSDOE31_registry"})
    seen_paths = {str(e["path"]) for e in ref_entries}
    for tif in sorted(DOWNLOADS.glob("*-nan.tif")) + sorted(DOWNLOADS.glob("*-allfinite.tif")):
        if str(tif) not in seen_paths and "rbu31" not in tif.name:
            ref_entries.append({"id": f"local_dl::{tif.stem}", "path": tif, "source_group": "GEMSDOE31_downloads"})
            seen_paths.add(str(tif))
    for row in json.loads((ROOT / "evidence/regime31/peer_fetch.json").read_text())["files"]:
        p = ROOT / (row["dest"] if "dest" in row else row["path"])
        if p.is_file() and str(p) not in seen_paths:
            ref_entries.append({"id": f"peer::{row['repo']}", "path": p, "source_group": row["repo"]})
            seen_paths.add(str(p))
    dup = check_duplicate_canary(surf_rbu, dots_rbu, footprint, ref_entries)
    (out / "duplicate_canary.json").write_text(json.dumps(dup, indent=1, allow_nan=False) + "\n")
    log(f"  duplicate canary over {dup['checked_count']} rasters: passed={dup['passed']} "
        f"max|rho| surf={dup['max_surface_spearman_rho']:.4f} dots={dup['max_final_dots_spearman_rho']:.4f} "
        f"max3px surf={dup['max_surface_topn_within_3px']:.4f} dots={dup['max_final_dots_within_3px']:.4f}")
    results["duplicate_canary_summary"] = {k: dup[k] for k in
        ("checked_count", "max_surface_spearman_rho", "max_surface_topn_within_3px",
         "max_final_dots_spearman_rho", "max_final_dots_within_3px", "duplicates", "passed")}

    g2 = bool(results["leakage_canary"]["passed"])
    g3a = bool(dup["passed"])
    g4 = bool(screen_pass and confirm and confirm["paired_delta_dti"] > 0.002 and confirm["paired_delta_ci95"][0] > 0.0)
    pr = proxies["rbu31"]
    pb = proxies["baseline_d_final"]
    ph = proxies["h33_2_b2_actual_peer_file"]
    g5 = bool(all(pr[k] > pb[k] and pr[k] > ph[k]
                  for k in ("sgmc_all_dti", "sgmc_piedmont_dti", "sgmc_mountain_dti")))

    digest8 = hashlib.sha256(np.packbits(dots_rbu.ravel())).hexdigest()[:8]
    name = f"gemsdoe31-{slug}-37654-20261025-{digest8}"
    hold_r = confirm["rbu31_pooled_dti"] if confirm else screen["rbu31_poisson"]["pooled_dti"]
    hold_b = confirm["baseline_d_pooled_dti"] if confirm else screen["baseline_d_poisson"]["pooled_dti"]
    tag = "RBU31-B local-standardized union" if local_variant else "RBU31 regime-balanced union"
    note = f"GEMSDOE31 {tag} 37654d | HOLDOUT-DTI {hold_r:.4f} vs {hold_b:.4f} | id {digest8}"[:140]
    gates = {"G1_format_and_range_0_1_pass": None, "G2_leakage_canary_pass": g2,
             "G3a_uniqueness_genuine_registry_pass": g3a,
             "G3b_literal_695_registry_lattice": "UNIVERSAL_DEGENERACY_DISCLOSED (spacing-5 lattice covers 100% of interior within 3px for any candidate; see preregistration §5)",
             "G4_holdout_screen_and_fresh_confirmation_pass": g4,
             "G5_sgmc_all_piedmont_mountain_beats_baseline_and_h33": g5,
             "human_inspection_required_for_validation": False,
             "weekly_slot_spent_by_agent": False}
    receipt = emit_and_validate_submission(dots_rbu, template_path=DATA / "sample_submission.tif",
                                           labels_path=DATA / "labels.tif", outdir=DOWNLOADS,
                                           name=name, note=note, gate_summary=gates)
    g1 = bool(receipt["validation"]["nan"]["ok_to_upload_format_only"]
              and receipt["validation"]["allfinite"]["ok_to_upload_format_only"])
    gates["G1_format_and_range_0_1_pass"] = g1
    all_pass = bool(g1 and g2 and g3a and g4 and g5)
    gates["all_automated_gates_passed"] = all_pass
    gates["verdict"] = "promote" if all_pass else "negative"
    receipt_file = DOWNLOADS / f"{name}-format-check.json"
    saved = json.loads(receipt_file.read_text())
    saved["automated_gates"] = gates
    receipt_file.write_text(json.dumps(saved, indent=2, allow_nan=False) + "\n")

    results["automated_gates"] = gates
    results["submission"] = {"name": name, "note": note, "note_chars": len(note),
                             "dots": int(dots_rbu.sum()),
                             "sha256_nan": receipt["validation"]["nan"]["sha256"],
                             "sha256_allfinite": receipt["validation"]["allfinite"]["sha256"],
                             "files": receipt["files"]}
    results["elapsed_seconds"] = round(time.monotonic() - t_start, 1)
    (out / "holdout_results.json").write_text(json.dumps(results, indent=1, allow_nan=False) + "\n")

    if local_variant:
        hypothesis = ("RBU31-B: the RBU31 union/regime-balanced surface, ranked by masked 12 km local "
                      "standardization (sigma=120px, local weight 0.65), beats Baseline-D on the buffered "
                      "holdout and H33-2-B2 on off-catalogue SGMC in every regime.")
        mechanism = ("Global top-budget emission starves low-absolute-score districts (mountain bedrock, "
                     "survey-sparse west) where off-catalogue truth concentrates; ranking each pixel against "
                     "its 12 km neighbourhood forces budget into every district, and under DTI beta=0.8 covering "
                     "more distinct truth segments dominates. Base surface: union raw-39 + SCGP-40 HGB with "
                     "regime-balanced weights. Emission: 2.8px Poisson thinning + >2px catalogue prune "
                     "(verified H33 DTI economics; no prior dots copied).")
    else:
        hypothesis = ("RBU31: a single union (raw-39 + SCGP-40) HGB per fold trained with regime-balanced "
                      "sample weights ranks off-catalogue faults better than Baseline-D in every geomorphic regime.")
        mechanism = ("Catalogue regime mix (72.4% piedmont) is mapping bias; balanced risk equalises regime "
                     "loss. Tree interactions between raw LiDAR scarp bands (mountain scarps) and Gallardo-Meju "
                     "cross-gradient/tilt/upward-continuation physics (buried piedmont faults) fix H31-E2's "
                     "measured mountain placement failure (SGMC TPw/dot 0.122 vs H33 0.188). Emission: 2.8px "
                     "Poisson thinning + >2px catalogue prune (verified H33 DTI economics; no prior dots copied).")
    run_card = {
        "hypothesis": hypothesis,
        "mechanism": mechanism,
        "named_non_fault_mimic": "Pleistocene Lake Lahontan wave-cut shoreline terraces and unfaulted volcanic-flow/erosional piedmont scarps.",
        "holdout_dti": {
            "label": "HOLDOUT-DTI", "evaluator_version": eh.EVALUATOR_VERSION, "buffer_m": eh.BUFFER_PX * 100,
            "screen_draw_101": {"dti": screen["rbu31_poisson"]["pooled_dti"], "ci95": screen["rbu31_poisson"]["ci95"],
                                "withheld_positives": screen["rbu31_poisson"]["withheld_positives"],
                                "baseline_d_dti": screen["baseline_d_poisson"]["pooled_dti"],
                                "paired_delta_dti": screen["paired_delta_dti"], "paired_delta_ci95": screen["paired_delta_ci95"]},
            "fresh_confirmation_draws_202_303": (None if not confirm else {
                "dti": confirm["rbu31_pooled_dti"], "ci95": confirm["rbu31_ci95"],
                "withheld_positives": confirm["withheld_positives_pooled"],
                "baseline_d_dti": confirm["baseline_d_pooled_dti"],
                "paired_delta_dti": confirm["paired_delta_dti"], "paired_delta_ci95": confirm["paired_delta_ci95"]})},
        "organizer_confirmed_score": None,
        "sgmc_proxy_computed_not_a_score": proxies,
        "leakage_canary": results["leakage_canary"],
        "correlation_overlap_vs_registry": results["duplicate_canary_summary"],
        "raster_sha256": {"nan_outside": receipt["validation"]["nan"]["sha256"],
                          "allfinite": receipt["validation"]["allfinite"]["sha256"]},
        "validator_output": {
            "no_nan_inside_footprint": bool(receipt["validation"]["nan"]["checks"]["footprint_all_finite"]["pass_"]),
            "values_in_0_1": bool(receipt["validation"]["nan"]["checks"]["footprint_values_in_0_1"]["pass_"]),
            "crs_shape_transform_match": bool(receipt["validation"]["nan"]["checks"]["crs_matches_template"]["pass_"]
                and receipt["validation"]["nan"]["checks"]["shape_matches_template"]["pass_"]
                and receipt["validation"]["nan"]["checks"]["transform_matches_template"]["pass_"]),
            "allfinite_values_in_0_1_everywhere": bool(receipt["validation"]["allfinite"]["checks"]["allfinite_values_in_0_1"]["pass_"]),
            "dots": int(dots_rbu.sum()), "dots_on_catalogue": int(receipt["dots_on_catalogue"])},
        "submission_name": name, "submission_note": note, "submission_note_chars": len(note),
        "automated_gates": gates, "verdict": gates["verdict"],
        "ok_to_download_and_submit": bool(all_pass),
    }
    (out / "run_card.json").write_text(json.dumps(run_card, indent=1, allow_nan=False) + "\n")
    (DOWNLOADS / f"{name}-run-card.json").write_text(json.dumps(run_card, indent=1, allow_nan=False) + "\n")
    log(f"DONE verdict={gates['verdict']} name={name}")
    print(json.dumps(run_card, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
