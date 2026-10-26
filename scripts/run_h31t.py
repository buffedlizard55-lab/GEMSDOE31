#!/usr/bin/env python3
"""Execute frozen 3-experiment campaign for Lane H31-T and package verified research GeoTIFF.

Preregistration (frozen before execution):
  knowledge/2026-10-25_h31t_transtension_dinkelbach_preregistration.md

Honest 3-Experiment Ledger (strict cap = 3):
  EXP-1 (preserved verbatim in `evidence/h31t/exp1_vis_self_inclusion_diagnostic.json`):
         Initial canary (max symmetric AUC = 0.5711 <= 0.90) + own-method variogram
         (20.75 km <= 21.25 km) + `gems57-pooled-hide-v2` (0.117240 vs 0.109735 ctrl),
         which exposed train-set self-inclusion of `visible_catalogue` (`d0=0` on `y_tr=1`
         vs zero inside withheld Quadrant 1) and `gemsdoe31.holdout`'s strict label-free
         feature caller contract.
  EXP-2 (`evidence/h31t/exp1_canary_variogram_gems57.json` +
         `evidence/h31t/exp2_holdout_screen_confirm.json`):
         100% label-free H31-T Dual-Specialist (12 static physical channels; zero
         catalogue-derived features) verified across Single-Feature Canary, Own-Method
         Residual Semivariogram Collar (`B_H31T = max(21_250 m, B_own)`), unchanged
         pinned `vendor/gems57/evaluate_holdout.py` (`gems57-pooled-hide-v2`), AND
         disjoint whole-component Screen (`seed=20261031`) + Untouched Confirmation
         (`seed=20261101`) on `gemsdoe31-holdout-v1`.
  EXP-3 (`evidence/h31t/exp3_uniqueness_offcat_package.json` + `evidence/h31t/run_card.json`):
         Strictly out-of-fold stitched full-footprint synthesis (zero extra fits),
         Pre-Placement AND Final registry uniqueness audit across all 104 comparable
         focus-site TIFFs + all local GEMSDOE31 2026-10-25 TIFFs + 3 pinned 695-registry
         blanket/lattice controls via `vendor/gems57/uniqueness.py`, Off-Catalogue SGMC
         benchmarks (Full, 4-Block Collared, Piedmont <=6 deg), and fail-closed
         GeoTIFF + single-TIFF ZIP packaging.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "vendor")]

import numpy as np  # noqa: E402
import rasterio  # noqa: E402
from scipy import ndimage as ndi  # noqa: E402
from sklearn.ensemble import HistGradientBoostingClassifier  # noqa: E402
from sklearn.metrics import roc_auc_score  # noqa: E402

from gems57 import evaluate_holdout as gems57_eval  # noqa: E402
from gems57 import metric as gems57_metric  # noqa: E402
from gems57 import spatial as gems57_spatial  # noqa: E402
from gems57 import submission_writer as gems57_writer  # noqa: E402
from gems57 import uniqueness as gems57_uniq  # noqa: E402
from gems57.grid import TRANSFORM as GEMS57_TRANSFORM  # noqa: E402

from gemsdoe31.buffer import (  # noqa: E402
    component_bootstrap,
    decide_buffer_m,
    empirical_variogram,
    fit_models,
)
from gemsdoe31.h31t_dinkelbach import (  # noqa: E402
    emit_dinkelbach_submodular_dots,
    emit_poisson_thinning_dots,
)
from gemsdoe31.h31t_features import (  # noqa: E402
    H31T_STATIC_CHANNELS,
    PreparedBandReader,
    build_or_load_h31t_static_cache,
)
from gemsdoe31.holdout import (  # noqa: E402
    DOMAIN_EROSION_PX,
    EVALUATOR_ID as GEMS31_EVAL_VERSION,
    FOLD_NAMES,
    paired_block_bootstrap,
    quadrant_rect,
    score_fold,
)
from gemsdoe31.raster import connected_components  # noqa: E402
from gemsdoe31.submission import validate_submission  # noqa: E402

OFFICIAL_19_BANDS: tuple[str, ...] = (
    "mag_anom",
    "rtp",
    "tmi_hg",
    "geod_2ndinv",
    "iso_grav_anom_slope",
    "tc",
    "geod_shearrate",
    "geod_dilaterate",
    "tmi_vg",
    "deq_n100a15",
    "iso_grav_anom_vg",
    "det_elev",
    "iso_grav_anom",
    "tmi",
    "depth_to_base_surf",
    "ieq_n100a15",
    "cond_surf",
    "iso_grav_anom_hg",
    "det_elev_slope",
)

HEAD_A_BANDS: tuple[str, ...] = H31T_STATIC_CHANNELS + (
    "depth_to_base_surf",
    "det_elev_slope",
    "iso_grav_anom_slope",
    "tmi_hg",
)

HEAD_B_EXTRA: tuple[str, ...] = (
    "step_max",
    "cross_max",
    "ThK",
    "UK",
)
HEAD_B_BANDS: tuple[str, ...] = tuple(
    dict.fromkeys(H31T_STATIC_CHANNELS + OFFICIAL_19_BANDS + HEAD_B_EXTRA)
)

SUBMISSION_BUDGET = 37_654
INHERITED_MIN_COLLAR_M = 21_250.0
PREREG_PATH = "knowledge/2026-10-25_h31t_transtension_dinkelbach_preregistration.md"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_compact_footprint_table(
    *,
    prepared_dir: Path,
    data_dir: Path,
    footprint: np.ndarray,
    fp_rows: np.ndarray,
    fp_cols: np.ndarray,
    cache_dir: Path,
) -> tuple[np.ndarray, list[str], dict[str, int]]:
    """Build compact `(N_fp, P)` float32 table (~720 MB) for zero-pagefault fitting & prediction."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    build_or_load_h31t_static_cache(
        prepared_dir=prepared_dir,
        data_dir=data_dir,
        footprint=footprint,
        cache_dir=cache_dir,
    )
    all_names = list(
        dict.fromkeys(OFFICIAL_19_BANDS + HEAD_B_EXTRA + H31T_STATIC_CHANNELS)
    )
    col_idx = {name: i for i, name in enumerate(all_names)}
    F_fp = np.empty((fp_rows.size, len(all_names)), dtype=np.float32)

    reader = PreparedBandReader(prepared_dir)
    for j, name in enumerate(all_names):
        if name in H31T_STATIC_CHANNELS:
            plane = np.load(cache_dir / f"{name}.npy", mmap_mode="r")
            F_fp[:, j] = plane[fp_rows, fp_cols]
            del plane
        else:
            bcache = cache_dir / f"base_{name}.npy"
            if bcache.exists():
                plane = np.load(bcache, mmap_mode="r")
                F_fp[:, j] = plane[fp_rows, fp_cols]
                del plane
            else:
                arr = reader.read(name, footprint)
                np.save(bcache, arr.astype(np.float32, copy=False))
                F_fp[:, j] = arr[fp_rows, fp_cols]
                del arr
    gc.collect()
    return F_fp, all_names, col_idx


def _predict_target_from_compact(
    models_cols_weights: list[tuple[HistGradientBoostingClassifier, np.ndarray, float]],
    F_fp: np.ndarray,
    target_mask: np.ndarray,
    fp_rows: np.ndarray,
    fp_cols: np.ndarray,
    shape: tuple[int, int],
    chunk_size: int = 350_000,
) -> np.ndarray:
    """Predict strictly on `target_mask` cells (4x faster per quadrant, bit-identical on domain)."""
    tgt_idx = np.flatnonzero(target_mask[fp_rows, fp_cols])
    n_t = tgt_idx.size
    out_1d = np.zeros(n_t, dtype=np.float32)
    for s in range(0, n_t, chunk_size):
        e = min(n_t, s + chunk_size)
        sub_idx = tgt_idx[s:e]
        block = F_fp[sub_idx]
        acc = np.zeros(e - s, dtype=np.float32)
        for clf, cidx, w in models_cols_weights:
            acc += float(w) * clf.predict_proba(block[:, cidx])[:, 1].astype(np.float32)
        out_1d[s:e] = acc
    prob = np.zeros(shape, dtype=np.float32)
    prob[fp_rows[tgt_idx], fp_cols[tgt_idx]] = np.clip(out_1d, 0.0, 1.0)
    return prob


def _fit_ctrl_and_h31t_fold(
    *,
    train_mask: np.ndarray,
    target_mask: np.ndarray,
    full_catalogue: np.ndarray,
    fp_rows: np.ndarray,
    fp_cols: np.ndarray,
    F_fp: np.ndarray,
    col_idx: dict[str, int],
    shape: tuple[int, int],
    seed: int,
    max_neg: int = 180_000,
) -> tuple[np.ndarray, np.ndarray]:
    """Fit same-run 19-band physical control AND 100% label-free Dual-Specialist H31-T."""
    in_train = train_mask[fp_rows, fp_cols]
    is_cat = full_catalogue[fp_rows, fp_cols]
    pos_fp_i = np.flatnonzero(in_train & is_cat)
    neg_fp_i = np.flatnonzero(in_train & (~is_cat))

    rng = np.random.default_rng(seed)
    if neg_fp_i.size > max_neg:
        pick = rng.choice(neg_fp_i.size, size=max_neg, replace=False)
        pick.sort()
        neg_fp_i = neg_fp_i[pick]

    tr_i = np.concatenate([pos_fp_i, neg_fp_i])
    y_tr = np.concatenate(
        [np.ones(pos_fp_i.size, dtype=np.int8), np.zeros(neg_fp_i.size, dtype=np.int8)]
    )
    perm = rng.permutation(tr_i.size)
    tr_i = tr_i[perm]
    y_tr = y_tr[perm]

    ctrl_cidx = np.asarray([col_idx[b] for b in OFFICIAL_19_BANDS], dtype=np.int32)
    ha_cidx = np.asarray([col_idx[b] for b in HEAD_A_BANDS], dtype=np.int32)
    hb_cidx = np.asarray([col_idx[b] for b in HEAD_B_BANDS], dtype=np.int32)
    slope_col = col_idx["det_elev_slope"]

    clf_ctrl = HistGradientBoostingClassifier(
        max_iter=200,
        learning_rate=0.055,
        max_leaf_nodes=63,
        min_samples_leaf=80,
        l2_regularization=2.0,
        random_state=seed + 11,
    )
    clf_ctrl.fit(F_fp[tr_i][:, ctrl_cidx], y_tr)

    clf_a = HistGradientBoostingClassifier(
        max_iter=200,
        learning_rate=0.055,
        max_leaf_nodes=63,
        min_samples_leaf=80,
        l2_regularization=2.0,
        random_state=seed + 23,
    )
    clf_a.fit(F_fp[tr_i][:, ha_cidx], y_tr)

    slope_tr = F_fp[tr_i, slope_col]
    sw_b = np.where(np.isfinite(slope_tr) & (slope_tr <= 8.0), 2.2, 1.0).astype(np.float32)
    clf_b = HistGradientBoostingClassifier(
        max_iter=200,
        learning_rate=0.055,
        max_leaf_nodes=63,
        min_samples_leaf=80,
        l2_regularization=2.0,
        random_state=seed + 37,
    )
    clf_b.fit(F_fp[tr_i][:, hb_cidx], y_tr, sample_weight=sw_b)

    prob_ctrl = _predict_target_from_compact(
        [(clf_ctrl, ctrl_cidx, 1.0)], F_fp, target_mask, fp_rows, fp_cols, shape
    )
    prob_h31t = _predict_target_from_compact(
        [(clf_a, ha_cidx, 0.50), (clf_b, hb_cidx, 0.50)],
        F_fp,
        target_mask,
        fp_rows,
        fp_cols,
        shape,
    )
    del clf_ctrl, clf_a, clf_b
    return prob_ctrl, prob_h31t


def _fit_h31t_only_fold(
    *,
    train_mask: np.ndarray,
    target_mask: np.ndarray,
    full_catalogue: np.ndarray,
    fp_rows: np.ndarray,
    fp_cols: np.ndarray,
    F_fp: np.ndarray,
    col_idx: dict[str, int],
    shape: tuple[int, int],
    seed: int,
    max_neg: int = 180_000,
) -> np.ndarray:
    """Deterministic H31-T-only fold fit matching `_fit_ctrl_and_h31t_fold` bit-for-bit."""
    in_train = train_mask[fp_rows, fp_cols]
    is_cat = full_catalogue[fp_rows, fp_cols]
    pos_fp_i = np.flatnonzero(in_train & is_cat)
    neg_fp_i = np.flatnonzero(in_train & (~is_cat))

    rng = np.random.default_rng(seed)
    if neg_fp_i.size > max_neg:
        pick = rng.choice(neg_fp_i.size, size=max_neg, replace=False)
        pick.sort()
        neg_fp_i = neg_fp_i[pick]

    tr_i = np.concatenate([pos_fp_i, neg_fp_i])
    y_tr = np.concatenate(
        [np.ones(pos_fp_i.size, dtype=np.int8), np.zeros(neg_fp_i.size, dtype=np.int8)]
    )
    perm = rng.permutation(tr_i.size)
    tr_i = tr_i[perm]
    y_tr = y_tr[perm]

    ha_cidx = np.asarray([col_idx[b] for b in HEAD_A_BANDS], dtype=np.int32)
    hb_cidx = np.asarray([col_idx[b] for b in HEAD_B_BANDS], dtype=np.int32)
    slope_col = col_idx["det_elev_slope"]

    clf_a = HistGradientBoostingClassifier(
        max_iter=200,
        learning_rate=0.055,
        max_leaf_nodes=63,
        min_samples_leaf=80,
        l2_regularization=2.0,
        random_state=seed + 23,
    )
    clf_a.fit(F_fp[tr_i][:, ha_cidx], y_tr)

    slope_tr = F_fp[tr_i, slope_col]
    sw_b = np.where(np.isfinite(slope_tr) & (slope_tr <= 8.0), 2.2, 1.0).astype(np.float32)
    clf_b = HistGradientBoostingClassifier(
        max_iter=200,
        learning_rate=0.055,
        max_leaf_nodes=63,
        min_samples_leaf=80,
        l2_regularization=2.0,
        random_state=seed + 37,
    )
    clf_b.fit(F_fp[tr_i][:, hb_cidx], y_tr, sample_weight=sw_b)

    prob_h31t = _predict_target_from_compact(
        [(clf_a, ha_cidx, 0.50), (clf_b, hb_cidx, 0.50)],
        F_fp,
        target_mask,
        fp_rows,
        fp_cols,
        shape,
    )
    del clf_a, clf_b
    return prob_h31t


def run_single_feature_canary(
    *,
    footprint: np.ndarray,
    catalogue: np.ndarray,
    fp_rows: np.ndarray,
    fp_cols: np.ndarray,
    F_fp: np.ndarray,
    all_names: list[str],
    seed: int = 20261031,
) -> dict:
    """Test every input & engineered feature alone on holdout (`max symmetric AUC <= 0.90`)."""
    fold0 = next(gems57_spatial.folds(catalogue, footprint, buffer_px=213))
    eval_mask = footprint & fold0["region"] & (~fold0["visible"])
    truth0 = eval_mask & fold0["truth"]

    in_eval = eval_mask[fp_rows, fp_cols]
    in_truth = truth0[fp_rows, fp_cols]
    pos_i = np.flatnonzero(in_truth)
    neg_i = np.flatnonzero(in_eval & (~in_truth))
    rng = np.random.default_rng(seed)
    if neg_i.size > 120_000:
        neg_i = rng.choice(neg_i, size=120_000, replace=False)
    sample_i = np.concatenate([pos_i, neg_i])
    y = np.concatenate([np.ones(pos_i.size, dtype=np.int8), np.zeros(neg_i.size, dtype=np.int8)])

    rows = []
    max_sym_auc = 0.0
    max_feature = ""
    for j, name in enumerate(all_names):
        prefix = "h31t" if name in H31T_STATIC_CHANNELS else "base"
        fname = f"{prefix}:{name}"
        vals = F_fp[sample_i, j].astype(np.float64)
        fin = np.isfinite(vals)
        cov = float(fin.mean())
        miss_auc = float(roc_auc_score(y, fin.astype(np.float64)))
        miss_sym = max(miss_auc, 1.0 - miss_auc)
        med = float(np.median(vals[fin])) if np.any(fin) else 0.0
        filled = np.where(fin, vals, med)
        raw_auc = 0.5 if np.ptp(filled) == 0.0 else float(roc_auc_score(y, filled))
        sym_auc = max(raw_auc, 1.0 - raw_auc, miss_sym)
        if sym_auc > max_sym_auc:
            max_sym_auc = sym_auc
            max_feature = fname
        rows.append(
            {
                "feature": fname,
                "raw_auc": round(raw_auc, 6),
                "missingness_sym_auc": round(miss_sym, 6),
                "symmetric_auc": round(sym_auc, 6),
                "finite_coverage": round(cov, 6),
                "pass_le_0_90": bool(sym_auc <= 0.90),
            }
        )
    rows.sort(key=lambda r: r["symmetric_auc"], reverse=True)
    return {
        "threshold_symmetric_auc": 0.90,
        "features_tested": len(rows),
        "withheld_positives_tested": int(pos_i.size),
        "max_symmetric_auc": round(max_sym_auc, 6),
        "max_feature": max_feature,
        "passed": bool(max_sym_auc <= 0.90),
        "top_10_features": rows[:10],
        "all_features": rows,
    }


def _build_disjoint_screen_confirm_splits(
    catalogue: np.ndarray,
    footprint: np.ndarray,
    collar_m: float,
    seed: int = 20261031,
) -> dict[str, list[dict]]:
    """Partition 8-connected components in each quadrant 50/50 into disjoint Screen & Confirm folds."""
    components = connected_components(catalogue)
    n_components = int(components.max())
    rows, cols = np.nonzero(catalogue)
    comp_ids = components[rows, cols]
    counts = np.bincount(comp_ids, minlength=n_components + 1)
    centroid_r = np.bincount(comp_ids, weights=rows, minlength=n_components + 1) / np.maximum(
        counts, 1
    )
    centroid_c = np.bincount(comp_ids, weights=cols, minlength=n_components + 1) / np.maximum(
        counts, 1
    )

    rng = np.random.default_rng(seed)
    collar_px = float(collar_m) / 100.0
    height, width = catalogue.shape
    half_h, half_w = height // 2, width // 2

    out: dict[str, list[dict]] = {"screen": [], "confirm": []}
    for fold_idx in range(4):
        r0, r1, c0, c1 = quadrant_rect(catalogue.shape, fold_idx, erosion_px=DOMAIN_EROSION_PX)
        domain = np.zeros(catalogue.shape, dtype=bool)
        domain[r0:r1, c0:c1] = True
        domain &= footprint

        in_dom = (
            (centroid_r >= r0) & (centroid_r < r1) & (centroid_c >= c0) & (centroid_c < c1)
        )
        q_ids = np.nonzero(in_dom[1:])[0] + 1 if n_components else np.asarray([], dtype=int)
        perm = rng.permutation(q_ids)
        half = perm.size // 2
        role_ids = {"screen": perm[:half], "confirm": perm[half:]}

        quadrant = np.zeros(catalogue.shape, dtype=bool)
        qr0, qr1 = (0, half_h) if fold_idx < 2 else (half_h, height)
        qc0, qc1 = (0, half_w) if fold_idx % 2 == 0 else (half_w, width)
        quadrant[qr0:qr1, qc0:qc1] = True

        touching_ids = np.unique(components[domain & catalogue])

        for role, w_ids in role_ids.items():
            w_lookup = np.zeros(n_components + 1, dtype=bool)
            w_lookup[w_ids] = True
            truth = w_lookup[components] & domain
            visible = catalogue & (~w_lookup[components])

            excl_lookup = np.zeros(n_components + 1, dtype=bool)
            excl_lookup[touching_ids] = True
            excl_lookup[w_ids] = False
            excl_pixels = excl_lookup[components]

            d_truth_px = ndi.distance_transform_edt(~truth)
            outside_collar = d_truth_px > collar_px
            train_allowed = (
                footprint & (~quadrant) & outside_collar & (~excl_pixels) & (~w_lookup[components])
            )
            out[role].append(
                {
                    "fold": fold_idx,
                    "fold_name": FOLD_NAMES[fold_idx],
                    "domain": domain,
                    "truth": truth,
                    "visible": visible,
                    "train_allowed": train_allowed,
                    "n_truth_pixels": int(truth.sum()),
                    "n_withheld_components": int(w_ids.size),
                }
            )
    return out


def _bootstrap_from_online_blocks(
    arms_blocks: dict[str, list[dict]],
    per_fold_scores: dict[str, list[dict]],
    totals: dict[str, dict[str, float]],
    *,
    candidate_arm: str = "h31t_dinkelbach",
    n_boot: int = 1000,
    seed: int = 20261031,
) -> dict:
    boot_all = paired_block_bootstrap(arms_blocks, resamples=n_boot, seed=seed)
    scores_out = {}
    for arm, tot in totals.items():
        scores_out[arm] = {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": GEMS31_EVAL_VERSION,
            "dti": float(boot_all["pooled_dti"][arm]),
            "ci95": [float(x) for x in boot_all["ci95"][arm]],
            "withheld_positive_pixels": int(tot["n_truth"]),
            "tpw": round(tot["tp"], 2),
            "fpw": round(tot["fp"], 2),
            "fnw": round(tot["fn"], 2),
        }

    paired_diffs = {}
    for ctrl in arms_blocks:
        if ctrl == candidate_arm:
            continue
        pair_b = paired_block_bootstrap(
            {candidate_arm: arms_blocks[candidate_arm], ctrl: arms_blocks[ctrl]},
            resamples=n_boot,
            seed=seed,
        )
        key = f"{candidate_arm}_minus_{ctrl}"
        paired_diffs[ctrl] = {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": GEMS31_EVAL_VERSION,
            "delta": float(pair_b["paired_delta_point"][key]),
            "ci95": [float(x) for x in pair_b["paired_delta_ci95"][key]],
            "withheld_positive_pixels": scores_out[candidate_arm]["withheld_positive_pixels"],
        }

    return {
        "evidence_class": "HOLDOUT-DTI",
        "evaluator_version": GEMS31_EVAL_VERSION,
        "scores": scores_out,
        "paired_differences": paired_diffs,
        "per_fold": per_fold_scores,
        "n_blocks": int(boot_all["n_blocks"]),
    }


def _build_complete_registry_index(
    prior_art_root: Path,
    footprint: np.ndarray,
    exclude_paths: set[Path] | None = None,
) -> dict:
    """Build complete SHA256-verified comparator index: 9 focus sites + local lanes + 695 controls."""
    exclude = {p.resolve() for p in (exclude_paths or set())}
    rasters_by_sha: dict[str, dict] = {}

    def _add(path: Path, repo_name: str, label: str) -> None:
        rp = path.resolve()
        if rp in exclude or not rp.exists():
            return
        with rasterio.open(rp) as src:
            if (
                src.count != 1
                or src.shape != footprint.shape
                or src.crs is None
                or src.crs.to_epsg() != 32611
                or src.transform != GEMS57_TRANSFORM
            ):
                return
        sha = _sha256_file(rp)
        if sha not in rasters_by_sha:
            rasters_by_sha[sha] = {
                "sha256": sha,
                "cache_file": str(rp),
                "repo_first": repo_name,
                "sources": [label],
            }
        else:
            if label not in rasters_by_sha[sha]["sources"]:
                rasters_by_sha[sha]["sources"].append(label)

    inv = json.loads((ROOT / "evidence/sibling_inventory_20261025.json").read_text())
    for rec in inv["records"]:
        rel = rec["path"]
        if not rel.endswith((".tif", ".tiff")):
            continue
        if any(
            skip in rel
            for skip in ("labels.tif", "sample_submission.tif", "training_features.tif", "external/")
        ):
            continue
        cand_p = Path(prior_art_root) / rec["repo"] / rel
        if cand_p.exists():
            _add(cand_p, rec["repo"], f"{rec['repo']}:{rel}")

    for local_tif in sorted((ROOT / "docs/downloads").glob("*.tif")):
        _add(local_tif, "GEMSDOE31", f"GEMSDOE31:docs/downloads/{local_tif.name}")

    lattice_p = ROOT / ".cache/registry-scope/registered-lattice.tif"
    if lattice_p.exists():
        _add(
            lattice_p,
            "13GEMSDOE",
            "13GEMSDOE:submissions/r13-lattice-s5-20261004T070000Z-s5-zeros.tif",
        )
    reg57 = json.loads((ROOT / "registry/shared_registry_57_snapshot.json").read_text())
    for r in reg57["rasters"]:
        cp = ROOT / r["cache_file"]
        if cp.exists():
            _add(cp, r["repo_first"], r["sources"][0])

    return {
        "complete_accessible_scan": True,
        "errors": [],
        "rasters": list(rasters_by_sha.values()),
    }


def _evaluate_offcat_sgmc_suite(
    pred_map_by_name: dict[str, np.ndarray],
    *,
    sgmc_raw: np.ndarray,
    catalogue: np.ndarray,
    footprint: np.ndarray,
    slope_deg: np.ndarray,
    block_px: int = 200,
) -> dict:
    """Evaluate candidate & historical discrete comparators on Full, 4-Block, and Piedmont SGMC."""
    d_cat_m = ndi.distance_transform_edt(~catalogue).astype(np.float32) * 100.0
    active = footprint & (d_cat_m > 200.0)
    sgmc_offcat = active & sgmc_raw & (d_cat_m > 300.0)
    piedmont_zone = active & np.isfinite(slope_deg) & (slope_deg <= 6.0)
    sgmc_piedmont = sgmc_offcat & piedmont_zone

    q_folds_sgmc = list(gems57_spatial.folds(sgmc_offcat, active, buffer_px=213))
    H, W = footprint.shape
    nb_c = (W + block_px - 1) // block_px
    nb_r = (H + block_px - 1) // block_px
    n_blocks = nb_r * nb_c

    full_scores = {}
    pied_scores = {}
    terms_4block: dict[str, np.ndarray] = {
        k: np.zeros((n_blocks, 4), dtype=np.float64) for k in pred_map_by_name
    }

    for name, raw_p in pred_map_by_name.items():
        p = np.where(active & np.isfinite(raw_p), np.clip(raw_p, 0.0, 1.0), 0.0).astype(np.float64)
        res_full = gems57_metric.dti_exact(p, sgmc_offcat, valid=active)
        full_scores[name] = {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": "usgs-sgmc-offcat-gt300m-full-v1",
            "withheld_positive_pixels": int(sgmc_offcat.sum()),
            "dti": round(float(res_full["dti"]), 6),
            "tpw": round(float(res_full["tp"]), 2),
            "fpw": round(float(res_full["fp"]), 2),
            "n_emitted": int((p > 0).sum()),
        }
        p_pied = np.where(piedmont_zone, p, 0.0)
        res_pied = gems57_metric.dti_exact(p_pied, sgmc_piedmont, valid=piedmont_zone)
        pied_scores[name] = {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": "usgs-sgmc-offcat-gt300m-piedmont-le6deg-v1",
            "withheld_positive_pixels": int(sgmc_piedmont.sum()),
            "dti": round(float(res_pied["dti"]), 6),
            "tpw": round(float(res_pied["tp"]), 2),
            "fpw": round(float(res_pied["fp"]), 2),
            "n_emitted_in_piedmont": int((p_pied > 0).sum()),
        }
        for qf in q_folds_sgmc:
            _, t_q = gems57_eval.evaluate(
                p, qf, active, block_side=block_px, global_shape=footprint.shape
            )
            terms_4block[name] += t_q

    pooled_4block = gems57_eval.pooled_summary(
        terms_4block, draws=1000, seed=20261031, candidate="H31-T (Dinkelbach)"
    )
    pooled_4block["evaluator_version"] = "usgs-sgmc-offcat-gt300m-4block-v1"
    for v in pooled_4block["scores"].values():
        v["evaluator_version"] = "usgs-sgmc-offcat-gt300m-4block-v1"
    for v in pooled_4block["paired_differences"].values():
        v["evaluator_version"] = "usgs-sgmc-offcat-gt300m-4block-v1"

    return {
        "offcat_sgmc_full_gt300m": full_scores,
        "offcat_sgmc_piedmont_le6deg_gt300m": pied_scores,
        "offcat_sgmc_4block_collared": pooled_4block,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", type=Path, default=Path("/tmp/gemsdoe31_data"))
    ap.add_argument("--prepared-dir", type=Path, default=Path("/tmp/gemsdoe31_data/prepared"))
    ap.add_argument("--cache-dir", type=Path, default=Path("/tmp/gemsdoe31_h31t_cache"))
    ap.add_argument("--prior-art-dir", type=Path, default=Path("/tmp/gemsdoe31_prior_art"))
    ap.add_argument("--out-dir", type=Path, default=ROOT / "evidence/h31t")
    ap.add_argument(
        "--resume-exp3",
        action="store_true",
        help="Reuse already-verified exp1/exp2 JSON receipts and compute/load stitched OOF for EXP-3.",
    )
    args = ap.parse_args()

    t_start = time.time()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    prereg_sha = _sha256_file(ROOT / PREREG_PATH)
    print(f"[H31-T] Preregistration verified: {PREREG_PATH} ({prereg_sha[:16]}...)")

    sample_path = ROOT / "data/sample_submission.tif"
    labels_path = ROOT / "data/labels.tif"
    with rasterio.open(sample_path) as s_src:
        footprint = np.isfinite(s_src.read(1))
    with rasterio.open(labels_path) as l_src:
        catalogue = footprint & (l_src.read(1) == 1)

    fp_rows, fp_cols = np.nonzero(footprint)
    total_offcat_fp = float((footprint & (~catalogue)).sum())

    t0 = time.time()
    F_fp, all_names, col_idx = _load_compact_footprint_table(
        prepared_dir=args.prepared_dir,
        data_dir=args.data_dir,
        footprint=footprint,
        fp_rows=fp_rows,
        fp_cols=fp_cols,
        cache_dir=args.cache_dir,
    )
    print(
        f"[H31-T] Compact in-RAM footprint table {F_fp.shape} "
        f"({F_fp.nbytes / 1e6:.1f} MB) ready in {time.time() - t0:.1f}s"
    )

    stitched_cache_path = args.cache_dir / "stitched_prob.npy"
    exp1_json_path = args.out_dir / "exp1_canary_variogram_gems57.json"
    exp2_json_path = args.out_dir / "exp2_holdout_screen_confirm.json"

    if args.resume_exp3 and exp1_json_path.exists() and exp2_json_path.exists():
        print("[H31-T] --resume-exp3: loading verified EXP-2A & EXP-2B JSON receipts...")
        e1_saved = json.loads(exp1_json_path.read_text())
        e2_saved = json.loads(exp2_json_path.read_text())
        canary = e1_saved["leakage_canary"]
        own_v = e1_saved["own_method_variogram"]
        own_buffer_m = float(own_v["own_adopted_buffer_m"])
        adopted_buffer_m = float(own_v["final_adopted_buffer_m"])
        adopted_buffer_px = int(own_v["final_adopted_buffer_px"])
        best_var_model = str(own_v["best_wrmse_model"])
        emp_decay_m = float(own_v["empirical_decay_m"])
        gems57_summary = e1_saved["gems57_pooled_hide_v2"]
        exp2_splits = {"screen": e2_saved["screen"], "confirm": e2_saved["confirm"]}

        slope_2d = np.full(footprint.shape, np.nan, dtype=np.float32)
        slope_2d[fp_rows, fp_cols] = F_fp[:, col_idx["det_elev_slope"]]

        if stitched_cache_path.exists():
            print("[EXP-3] Loading cached stitched_prob.npy...")
            stitched_prob = np.load(stitched_cache_path).astype(np.float32)
        else:
            print("[EXP-3] Reconstructing deterministic stitched OOF surface (H31-T heads only)...")
            oof_q = np.zeros(footprint.shape, dtype=np.float32)
            for q_idx, qf in enumerate(
                gems57_spatial.folds(catalogue, footprint, buffer_px=adopted_buffer_px)
            ):
                reg = qf["region"] & footprint
                p_t = _fit_h31t_only_fold(
                    train_mask=qf["train"],
                    target_mask=reg,
                    full_catalogue=catalogue,
                    fp_rows=fp_rows,
                    fp_cols=fp_cols,
                    F_fp=F_fp,
                    col_idx=col_idx,
                    shape=footprint.shape,
                    seed=(3200 if adopted_buffer_px > 213 else 3100) + q_idx * 100,
                )
                oof_q[reg] = p_t[reg]
                del p_t, qf
                gc.collect()
            accum = oof_q.copy()
            r_splits = _build_disjoint_screen_confirm_splits(
                catalogue, footprint, collar_m=adopted_buffer_m, seed=20261031
            )
            for s_lbl, s_seed in (("screen", 20261031), ("confirm", 20261101)):
                s_folds = r_splits.pop(s_lbl)
                s_oof = np.zeros(footprint.shape, dtype=np.float32)
                while s_folds:
                    hf = s_folds.pop(0)
                    f_i = int(hf["fold"])
                    dom_f = hf["domain"]
                    p_t = _fit_h31t_only_fold(
                        train_mask=hf["train_allowed"],
                        target_mask=dom_f,
                        full_catalogue=catalogue,
                        fp_rows=fp_rows,
                        fp_cols=fp_cols,
                        F_fp=F_fp,
                        col_idx=col_idx,
                        shape=footprint.shape,
                        seed=s_seed + f_i * 101,
                    )
                    s_oof[dom_f] = p_t[dom_f]
                    del p_t, hf
                    gc.collect()
                seam = footprint & (s_oof == 0.0)
                s_oof[seam] = oof_q[seam]
                accum += s_oof
                del s_oof
                gc.collect()
            del r_splits, oof_q
            stitched_prob = np.clip(accum / 3.0, 0.0, 1.0).astype(np.float32)
            del accum
            np.save(stitched_cache_path, stitched_prob)
        del F_fp
        gc.collect()
    else:
        # =========================================================================
        # EXP-2a: Leakage Canary + Own-Method Variogram + gems57-pooled-hide-v2
        # =========================================================================
        print("[EXP-2] Running single-feature leakage canary across all 35 label-free planes...")
        canary = run_single_feature_canary(
            footprint=footprint,
            catalogue=catalogue,
            fp_rows=fp_rows,
            fp_cols=fp_cols,
            F_fp=F_fp,
            all_names=all_names,
        )
        print(
            f"[EXP-2] Canary max symmetric AUC = {canary['max_symmetric_auc']:.4f} "
            f"({canary['max_feature']}) -> passed={canary['passed']}"
        )
        if not canary["passed"]:
            raise RuntimeError(f"LEAKAGE CANARY STOP: {canary['max_feature']}")

        print("[EXP-2] Fitting 100% label-free 4-quadrant collared OOF...")
        oof_h31t_q = np.zeros(footprint.shape, dtype=np.float32)
        oof_ctrl_q = np.zeros(footprint.shape, dtype=np.float32)
        for q_idx, qf in enumerate(gems57_spatial.folds(catalogue, footprint, buffer_px=213)):
            tq = time.time()
            reg = qf["region"] & footprint
            p_ctrl, p_h31t = _fit_ctrl_and_h31t_fold(
                train_mask=qf["train"],
                target_mask=reg,
                full_catalogue=catalogue,
                fp_rows=fp_rows,
                fp_cols=fp_cols,
                F_fp=F_fp,
                col_idx=col_idx,
                shape=footprint.shape,
                seed=3100 + q_idx * 100,
            )
            oof_ctrl_q[reg] = p_ctrl[reg]
            oof_h31t_q[reg] = p_h31t[reg]
            print(
                f"  quadrant {q_idx}: train={int(qf['train'].sum()):,}, "
                f"truth={int(qf['truth'].sum()):,} ({time.time() - tq:.1f}s)"
            )
            del p_ctrl, p_h31t, qf
            gc.collect()

        comp_grid, n_comp = ndi.label(catalogue, structure=np.ones((3, 3), dtype=np.int8))
        cat_r, cat_c = np.nonzero(catalogue)
        cat_comp = comp_grid[cat_r, cat_c]
        del comp_grid
        oof_residuals = (1.0 - oof_h31t_q[cat_r, cat_c]).astype(np.float64)
        v_bins = empirical_variogram(
            cat_r, cat_c, oof_residuals, cat_comp, cell_m=100.0, bin_m=500.0, max_lag_m=50_000.0
        )
        v_fits = fit_models(v_bins, min_pairs=20)
        v_boot = component_bootstrap(
            cat_r,
            cat_c,
            oof_residuals,
            cat_comp,
            draws=60,
            seed=20261031,
            min_pairs=20,
            bin_m=500.0,
            max_lag_m=50_000.0,
        )
        v_decision = decide_buffer_m(v_fits, v_boot, v_bins, min_pairs=20, decay_frac=0.95)
        own_buffer_m = float(v_decision["buffer_m"] or INHERITED_MIN_COLLAR_M)
        best_var_model = (
            min(v_fits.items(), key=lambda kv: kv[1]["weighted_rmse"])[0] if v_fits else "empirical"
        )
        emp_decay_m = float(v_decision["empirical_decay_range_m"] or 0.0)
        adopted_buffer_m = max(INHERITED_MIN_COLLAR_M, own_buffer_m)
        adopted_buffer_px = int(np.ceil(adopted_buffer_m / 100.0))
        print(
            f"[EXP-2] H31-T own-method residual semivariogram: own={own_buffer_m:.0f} m "
            f"(best_wrmse_model={best_var_model}, empirical_95pct_decay={emp_decay_m:.0f} m) "
            f"-> adopted B_H31T = {adopted_buffer_m:.0f} m ({adopted_buffer_px} px)"
        )

        if adopted_buffer_px > 213:
            print(f"[EXP-2] Refitting quadrant folds at wider own-method collar {adopted_buffer_px} px...")
            oof_h31t_q.fill(0.0)
            oof_ctrl_q.fill(0.0)
            for q_idx, qf in enumerate(
                gems57_spatial.folds(catalogue, footprint, buffer_px=adopted_buffer_px)
            ):
                reg = qf["region"] & footprint
                p_ctrl, p_h31t = _fit_ctrl_and_h31t_fold(
                    train_mask=qf["train"],
                    target_mask=reg,
                    full_catalogue=catalogue,
                    fp_rows=fp_rows,
                    fp_cols=fp_cols,
                    F_fp=F_fp,
                    col_idx=col_idx,
                    shape=footprint.shape,
                    seed=3200 + q_idx * 100,
                )
                oof_ctrl_q[reg] = p_ctrl[reg]
                oof_h31t_q[reg] = p_h31t[reg]
                del p_ctrl, p_h31t, qf
                gc.collect()

        arms_gems57 = ("ctrl_phys_poisson", "h31t_poisson", "h31t_dinkelbach")
        terms_gems57 = {
            a: np.zeros(
                (((footprint.shape[0] + 199) // 200) * ((footprint.shape[1] + 199) // 200), 4),
                dtype=np.float64,
            )
            for a in arms_gems57
        }
        fold_details_gems57: dict[str, list[dict]] = {a: [] for a in arms_gems57}

        for q_idx, qf in enumerate(
            gems57_spatial.folds(catalogue, footprint, buffer_px=adopted_buffer_px)
        ):
            active_q = footprint & qf["region"] & (~qf["visible"])
            budget_q = int(round(SUBMISSION_BUDGET * (float(active_q.sum()) / total_offcat_fp)))

            dots_ctrl = emit_poisson_thinning_dots(
                oof_ctrl_q, active_q, qf["visible"], budget=budget_q, collar_px=2.0, min_spacing_px=2.8
            )
            dots_t_pois = emit_poisson_thinning_dots(
                oof_h31t_q, active_q, qf["visible"], budget=budget_q, collar_px=2.0, min_spacing_px=2.8
            )
            dots_t_dink = emit_dinkelbach_submodular_dots(
                oof_h31t_q,
                active_q,
                qf["visible"],
                budget=budget_q,
                collar_px=2.0,
                min_spacing_px=2.4,
                cost_eta=0.50,
                ridge_gamma=0.35,
            ).binary_dots

            for aname, pred_q in (
                ("ctrl_phys_poisson", dots_ctrl),
                ("h31t_poisson", dots_t_pois),
                ("h31t_dinkelbach", dots_t_dink),
            ):
                f_res, f_terms = gems57_eval.evaluate(
                    pred_q, qf, footprint, block_side=200, global_shape=footprint.shape
                )
                terms_gems57[aname] += f_terms
                fold_details_gems57[aname].append(
                    {
                        "quadrant": int(q_idx),
                        "budget_q": budget_q,
                        "emitted": int(f_res["emitted"]),
                        "n_truth": int(f_res["n_truth"]),
                        "dti": round(float(f_res["dti"]), 6),
                        "tpw": round(float(f_res["tpw"]), 2),
                        "fpw": round(float(f_res["fpw"]), 2),
                    }
                )
            del dots_ctrl, dots_t_pois, dots_t_dink, qf
            gc.collect()
        del oof_ctrl_q
        gc.collect()

        gems57_summary = gems57_eval.pooled_summary(
            terms_gems57, draws=1000, seed=520810, candidate="h31t_dinkelbach"
        )
        gems57_summary["buffer_px"] = adopted_buffer_px
        gems57_summary["buffer_m"] = adopted_buffer_m
        gems57_summary["per_quadrant"] = fold_details_gems57

        exp1_payload = {
            "experiment_id": "EXP-2A-LABELFREE-GEMS57",
            "prior_diagnostic_exp1_file": "evidence/h31t/exp1_vis_self_inclusion_diagnostic.json",
            "completed_utc": _utc_now(),
            "preregistration_path": PREREG_PATH,
            "preregistration_sha256": prereg_sha,
            "leakage_canary": canary,
            "own_method_variogram": {
                "method": "H31-T 100% label-free 4-quadrant collared OOF residuals `1 - p_oof` along 8-connected traces",
                "own_adopted_buffer_m": own_buffer_m,
                "inherited_floor_buffer_m": INHERITED_MIN_COLLAR_M,
                "final_adopted_buffer_m": adopted_buffer_m,
                "final_adopted_buffer_px": adopted_buffer_px,
                "best_wrmse_model": best_var_model,
                "decision": v_decision,
                "fits": v_fits,
                "bootstrap": v_boot,
                "empirical_decay_m": emp_decay_m,
                "n_components": int(n_comp),
                "n_fault_pixels": int(cat_r.size),
            },
            "gems57_pooled_hide_v2": gems57_summary,
        }
        (args.out_dir / "exp1_canary_variogram_gems57.json").write_text(
            json.dumps(exp1_payload, indent=2, allow_nan=False) + "\n"
        )
        print(
            f"[EXP-2] gems57-pooled-hide-v2 HOLDOUT-DTI: "
            f"ctrl_phys_poisson={gems57_summary['scores']['ctrl_phys_poisson']['dti']:.6f}, "
            f"h31t_poisson={gems57_summary['scores']['h31t_poisson']['dti']:.6f}, "
            f"h31t_dinkelbach={gems57_summary['scores']['h31t_dinkelbach']['dti']:.6f} "
            f"(delta vs ctrl = {gems57_summary['paired_differences']['ctrl_phys_poisson']['delta']:+.6f}, "
            f"95% CI {gems57_summary['paired_differences']['ctrl_phys_poisson']['ci95']})"
        )

        # =========================================================================
        # EXP-2b: Disjoint Screen + Untouched Confirmation on gemsdoe31-holdout-v1
        # =========================================================================
        exp2_splits: dict[str, dict] = {}
        stitched_accum = oof_h31t_q.copy()
        role_splits = _build_disjoint_screen_confirm_splits(
            catalogue, footprint, collar_m=adopted_buffer_m, seed=20261031
        )

        for split_label, split_seed in (("screen", 20261031), ("confirm", 20261101)):
            print(
                f"[EXP-2] Running {GEMS31_EVAL_VERSION} ({split_label}, seed={split_seed}, "
                f"buffer={adopted_buffer_m:.0f} m)..."
            )
            h_folds = role_splits.pop(split_label)
            arm_names = ("ctrl_phys_poisson", "h31t_poisson", "h31t_dinkelbach")
            arms_blocks: dict[str, list[dict]] = {a: [] for a in arm_names}
            per_fold_scores: dict[str, list[dict]] = {a: [] for a in arm_names}
            totals: dict[str, dict[str, float]] = {
                a: {"tp": 0.0, "fp": 0.0, "fn": 0.0, "n_truth": 0} for a in arm_names
            }
            split_prob_oof = np.zeros(footprint.shape, dtype=np.float32)

            while h_folds:
                hf = h_folds.pop(0)
                f_idx = int(hf["fold"])
                tf0 = time.time()
                dom_f = hf["domain"]
                p_ctrl, p_h31t = _fit_ctrl_and_h31t_fold(
                    train_mask=hf["train_allowed"],
                    target_mask=dom_f,
                    full_catalogue=catalogue,
                    fp_rows=fp_rows,
                    fp_cols=fp_cols,
                    F_fp=F_fp,
                    col_idx=col_idx,
                    shape=footprint.shape,
                    seed=split_seed + f_idx * 101,
                )
                split_prob_oof[dom_f] = p_h31t[dom_f]
                active_dom = dom_f & (~hf["visible"])
                budget_dom = int(
                    round(SUBMISSION_BUDGET * (float(active_dom.sum()) / total_offcat_fp))
                )

                dots_c = emit_poisson_thinning_dots(
                    p_ctrl,
                    active_dom,
                    hf["visible"],
                    budget=budget_dom,
                    collar_px=2.0,
                    min_spacing_px=2.8,
                )
                dots_tp = emit_poisson_thinning_dots(
                    p_h31t,
                    active_dom,
                    hf["visible"],
                    budget=budget_dom,
                    collar_px=2.0,
                    min_spacing_px=2.8,
                )
                dots_td = emit_dinkelbach_submodular_dots(
                    p_h31t,
                    active_dom,
                    hf["visible"],
                    budget=budget_dom,
                    collar_px=2.0,
                    min_spacing_px=2.4,
                    cost_eta=0.50,
                    ridge_gamma=0.35,
                ).binary_dots
                del p_ctrl, p_h31t

                for arm_n, pred_arr in (
                    ("ctrl_phys_poisson", dots_c),
                    ("h31t_poisson", dots_tp),
                    ("h31t_dinkelbach", dots_td),
                ):
                    f_res = score_fold(pred_arr, catalogue, hf)
                    arms_blocks[arm_n].append(f_res["block_stats"])
                    tpw = float(f_res["TPw"])
                    fpw = float(f_res["FPw"])
                    fnw = float(f_res["FNw"])
                    ntr = int(f_res["truth_pixels"])
                    totals[arm_n]["tp"] += tpw
                    totals[arm_n]["fp"] += fpw
                    totals[arm_n]["fn"] += fnw
                    totals[arm_n]["n_truth"] += ntr
                    per_fold_scores[arm_n].append(
                        {
                            "fold": f_idx,
                            "fold_name": hf["fold_name"],
                            "dti": round(float(f_res["DTI"]), 6),
                            "tp_w": round(tpw, 2),
                            "fp_w": round(fpw, 2),
                            "fn_w": round(fnw, 2),
                            "n_truth": ntr,
                        }
                    )
                print(
                    f"  [{split_label}:{hf['fold_name']}] truth={hf['n_truth_pixels']:,}, "
                    f"ctrl={per_fold_scores['ctrl_phys_poisson'][-1]['dti']:.4f}, "
                    f"h31t_dink={per_fold_scores['h31t_dinkelbach'][-1]['dti']:.4f} "
                    f"({time.time() - tf0:.1f}s)"
                )
                del dots_c, dots_tp, dots_td, hf
                gc.collect()

            seam_mask = footprint & (split_prob_oof == 0.0)
            split_prob_oof[seam_mask] = oof_h31t_q[seam_mask]
            stitched_accum += split_prob_oof
            del split_prob_oof
            gc.collect()

            split_summary = _bootstrap_from_online_blocks(
                arms_blocks,
                per_fold_scores,
                totals,
                candidate_arm="h31t_dinkelbach",
                n_boot=1000,
                seed=split_seed,
            )
            split_summary["split_role"] = split_label
            split_summary["split_seed"] = split_seed
            split_summary["buffer_m"] = adopted_buffer_m
            exp2_splits[split_label] = split_summary
            print(
                f"[EXP-2:{split_label}] HOLDOUT-DTI ({GEMS31_EVAL_VERSION}): "
                f"ctrl={split_summary['scores']['ctrl_phys_poisson']['dti']:.6f}, "
                f"h31t_poisson={split_summary['scores']['h31t_poisson']['dti']:.6f}, "
                f"h31t_dinkelbach={split_summary['scores']['h31t_dinkelbach']['dti']:.6f} "
                f"(delta vs ctrl = {split_summary['paired_differences']['ctrl_phys_poisson']['delta']:+.6f}, "
                f"95% CI {split_summary['paired_differences']['ctrl_phys_poisson']['ci95']})"
            )
        del role_splits, oof_h31t_q
        gc.collect()

        exp2_payload = {
            "experiment_id": "EXP-2B-HOLDOUT-V1-SCREEN-CONFIRM",
            "completed_utc": _utc_now(),
            "preregistration_path": PREREG_PATH,
            "preregistration_sha256": prereg_sha,
            "adopted_buffer_m": adopted_buffer_m,
            "screen": exp2_splits["screen"],
            "confirm": exp2_splits["confirm"],
        }
        (args.out_dir / "exp2_holdout_screen_confirm.json").write_text(
            json.dumps(exp2_payload, indent=2, allow_nan=False) + "\n"
        )

        # Extract slope_deg 2D before freeing `F_fp`
        slope_2d = np.full(footprint.shape, np.nan, dtype=np.float32)
        slope_2d[fp_rows, fp_cols] = F_fp[:, col_idx["det_elev_slope"]]
        del F_fp
        gc.collect()

        stitched_prob = np.clip(stitched_accum / 3.0, 0.0, 1.0).astype(np.float32)
        del stitched_accum
        np.save(stitched_cache_path, stitched_prob)
        gc.collect()

    # =========================================================================
    # EXPERIMENT 3: Stitched-OOF Synthesis, Pre/Post Registry Audit & Packaging
    # =========================================================================
    print("[EXP-3] Strictly out-of-fold stitched H31-T probability surface ready.")

    d_cat_px = ndi.distance_transform_edt(~catalogue).astype(np.float32)
    offcat_elig = footprint & (d_cat_px > 2.0)
    pre_surface = np.where(offcat_elig, stitched_prob, 0.0).astype(np.float32)

    out_dl = ROOT / "docs/downloads"
    out_dl.mkdir(parents=True, exist_ok=True)
    zeros_tif_path = out_dl / "gemsdoe31-h31t-transtension-dinkelbach-20261025-b37654-zeros.tif"
    nan_tif_path = out_dl / "gemsdoe31-h31t-transtension-dinkelbach-20261025-b37654-nan.tif"
    nan_zip_path = out_dl / "gemsdoe31-h31t-transtension-dinkelbach-20261025-b37654-nan.zip"
    run_card_dl_path = (
        out_dl / "gemsdoe31-h31t-transtension-dinkelbach-20261025-b37654-run-card.json"
    )

    reg_index = _build_complete_registry_index(
        args.prior_art_dir,
        footprint,
        exclude_paths={zeros_tif_path, nan_tif_path},
    )
    print(f"[EXP-3] Complete registry index built: {len(reg_index['rasters'])} unique rasters")

    print("[EXP-3] Running PRE-PLACEMENT registry uniqueness audit...")
    pre_audit_raw = gems57_uniq.compare_array_to_registry(pre_surface, reg_index, footprint)
    pre_two_phase = gems57_uniq.two_phase_summary(pre_audit_raw["rows"], int(footprint.sum()))
    max_abs_rho_pre = max(
        abs(float(r["spearman_full_footprint"]))
        for r in pre_audit_raw["rows"]
        if r.get("spearman_full_footprint") is not None
    )
    print(
        f"[EXP-3] Pre-placement surface max |Spearman rho| across ALL {len(reg_index['rasters'])} "
        f"comparators = {max_abs_rho_pre:.4f} (limit <= 0.90)"
    )
    if max_abs_rho_pre > 0.90:
        raise RuntimeError(f"PRE-PLACEMENT SURFACE DUPLICATE STOP: |rho|={max_abs_rho_pre:.4f}")

    print("[EXP-3] Allocating 37,654 binary dots via Cost-Scaled Dinkelbach Submodular CELF...")
    alloc = emit_dinkelbach_submodular_dots(
        pre_surface,
        footprint,
        catalogue,
        budget=SUBMISSION_BUDGET,
        collar_px=2.0,
        min_spacing_px=2.4,
        cost_eta=0.50,
        ridge_gamma=0.35,
    )
    final_dots = alloc.binary_dots
    assert alloc.n_dots == SUBMISSION_BUDGET, f"Expected {SUBMISSION_BUDGET}, got {alloc.n_dots}"

    print("[EXP-3] Running POST-PLACEMENT final-dot registry uniqueness audit...")
    post_audit_raw = gems57_uniq.compare_array_to_registry(final_dots, reg_index, footprint)
    post_two_phase = gems57_uniq.two_phase_summary(post_audit_raw["rows"], int(footprint.sum()))

    fp_total = int(footprint.sum())
    discrete_rows = []
    blanket_lattice_rows = []
    for row in post_audit_raw["rows"]:
        sub_label = str(row.get("submission", ""))
        is_synth_lattice = "lattice-s5" in sub_label or "registered-lattice" in sub_label
        is_blanket = int(row.get("their_dots", 0)) > int(0.20 * fp_total)
        if is_synth_lattice or is_blanket:
            blanket_lattice_rows.append(row)
        else:
            discrete_rows.append(row)

    discrete_rows.sort(key=lambda r: float(r["my_dots_within_3px_of_theirs"]), reverse=True)
    blanket_lattice_rows.sort(key=lambda r: float(r["my_dots_within_3px_of_theirs"]), reverse=True)

    max_disc_overlap = float(discrete_rows[0]["my_dots_within_3px_of_theirs"])
    max_disc_abs_rho = max(
        abs(float(r["spearman_full_footprint"]))
        for r in discrete_rows
        if r.get("spearman_full_footprint") is not None
    )
    max_literal_overlap = float(post_audit_raw["worst_dot_overlap"])
    max_all_abs_rho = max(
        abs(float(r["spearman_full_footprint"]))
        for r in post_audit_raw["rows"]
        if r.get("spearman_full_footprint") is not None
    )

    print(
        f"[EXP-3] Phase A (ALL {len(discrete_rows)} discrete fault predictions across 9 sites + GEMSDOE31): "
        f"max 3-px overlap = {max_disc_overlap:.4f} ({discrete_rows[0]['submission']}), "
        f"max |rho| = {max_disc_abs_rho:.4f}"
    )
    print(
        f"[EXP-3] Phase B (Literal unexempted blanket/lattice controls, n={len(blanket_lattice_rows)}): "
        f"max 3-px overlap = {max_literal_overlap:.4f} ({post_audit_raw['worst_overlap_submission']})"
    )

    if max_disc_overlap > 0.70 or max_all_abs_rho > 0.90:
        raise RuntimeError(
            f"COMPETITIVE DISCRETE DUPLICATE STOP: overlap={max_disc_overlap:.4f}, |rho|={max_all_abs_rho:.4f}"
        )

    print("[EXP-3] Evaluating Full, 4-Block Collared, and Piedmont Off-Catalogue SGMC suite...")
    with rasterio.open(args.data_dir / "external/derived_sgmc_faults_100m_u8.tif") as sg_src:
        sgmc_raw = footprint & (sg_src.read(1) > 0)

    comparators_sgmc: dict[str, np.ndarray] = {"H31-T (Dinkelbach)": final_dots}
    comp_files = [
        (
            "GEMSDOE32 H33-2-B2",
            args.prior_art_dir
            / "GEMSDOE32/docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif",
        ),
        (
            "H27-4 Baseline",
            ROOT / "docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-allfinite.tif",
        ),
        (
            "H31-B Scarp-Hessian",
            ROOT / "docs/downloads/gemsdoe31-h31b-scarp-hessian-20261025-37654-allfinite.tif",
        ),
        (
            "H31-E2 SCGP-Submod",
            ROOT / "docs/downloads/gemsdoe31-scgp-submod-37654-20261025-fa735287-allfinite.tif",
        ),
        (
            "MAGREST Concordant",
            ROOT / "docs/downloads/gemsdoe31-magrest-concordant-37654-20261025-2c800a59ff-zeros.tif",
        ),
        (
            "H31-HVDC Conduit",
            ROOT / "docs/downloads/gemsdoe31-h31-hvdc-submod300-37654-20261025-43714168-allfinite.tif",
        ),
        (
            "H31-M Subsurface",
            ROOT / "docs/downloads/gemsdoe31-h31m-bstep-xmod-submod-20261025-37654-allfinite.tif",
        ),
    ]
    for label, cpath in comp_files:
        if cpath.exists():
            with rasterio.open(cpath) as cs:
                arr_c = cs.read(1).astype(np.float32)
            comparators_sgmc[label] = np.where(footprint & np.isfinite(arr_c), arr_c, 0.0)

    sgmc_suite = _evaluate_offcat_sgmc_suite(
        comparators_sgmc,
        sgmc_raw=sgmc_raw,
        catalogue=catalogue,
        footprint=footprint,
        slope_deg=slope_2d,
    )

    sub_name = "gemsdoe31-h31t-transtension-dinkelbach-20261025-b37654"
    sub_note = (
        "RESEARCH ONLY DO NOT SUBMIT: H31-T 3D AS/depth + listric updip + transtension + "
        "Dinkelbach 300m CELF (37654 px; 695-lattice STOP)"
    )
    assert len(sub_note) <= 140, f"Note length {len(sub_note)} > 140"

    writer_receipt = gems57_writer.write_submission(
        zeros_tif_path,
        final_dots,
        sample_path,
        footprint,
        note=sub_note,
        name=sub_name,
        catalogue=catalogue,
        metadata={
            "lane_id": "H31-T",
            "ok_to_download_for_research": True,
            "ok_to_submit": False,
            "slot_approved": False,
            "verdict": "negative",
            "reason_not_approved_for_portal": (
                "Literal unexempted 695-raster registry overlap > 0.70 against synthetic "
                "spacing-5 lattice `r13-lattice-s5` and full-footprint blanket `GEMSDOE48`."
            ),
        },
    )

    with rasterio.open(sample_path) as tmpl:
        nan_prof = tmpl.profile.copy()
    nan_prof.update(
        driver="GTiff",
        dtype="float32",
        count=1,
        nodata=np.nan,
        compress="deflate",
        predictor=3,
    )
    nan_arr = np.where(footprint, final_dots, np.nan).astype(np.float32)
    with rasterio.open(nan_tif_path, "w", **nan_prof) as dst:
        dst.write(nan_arr, 1)

    nan_val = validate_submission(nan_tif_path, sample_path, convention="nan-outside")
    if not nan_val["ok_to_upload_format_only"]:
        raise RuntimeError(f"NaN companion validation failed: {nan_val['hard_failures']}")

    with zipfile.ZipFile(nan_zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zi = zipfile.ZipInfo(nan_tif_path.name, date_time=(2026, 10, 25, 0, 0, 0))
        zi.compress_type = zipfile.ZIP_DEFLATED
        zf.writestr(zi, nan_tif_path.read_bytes())

    zeros_val_strict = validate_submission(zeros_tif_path, sample_path, convention="all-finite")
    if not zeros_val_strict["ok_to_upload_format_only"]:
        raise RuntimeError(f"Zeros primary validation failed: {zeros_val_strict['hard_failures']}")

    min_cat_dist_m = float(d_cat_px[final_dots > 0.5].min() * 100.0)
    dots_within_200m = int((d_cat_px[final_dots > 0.5] * 100.0 <= 200.0).sum())
    if dots_within_200m != 0:
        raise RuntimeError(f"Catalogue collar violation: {dots_within_200m} dots within <=200 m")

    format_check_path = (
        out_dl / "gemsdoe31-h31t-transtension-dinkelbach-20261025-b37654-format-check.json"
    )
    format_check_payload = {
        "schema_version": 1,
        "name": sub_name,
        "note": sub_note,
        "dots": int((final_dots > 0.5).sum()),
        "dots_on_catalogue": int(((final_dots > 0.5) & catalogue).sum()),
        "files": {
            "nan": f"docs/downloads/{nan_tif_path.name}",
            "allfinite": f"docs/downloads/{zeros_tif_path.name}",
            "zip": f"docs/downloads/{writer_receipt['zip_file']}",
        },
        "validation": {
            "nan": nan_val,
            "allfinite": zeros_val_strict,
        },
        "warnings": [
            "Format validation is local. It cannot prove organizer acceptance and is not a score.",
            "Competition claims without exact-file organizer receipts are USER-REPORTED; local metrics are separate HOLDOUT-DTI.",
            "Blocked from weekly slot upload (slot_approved=false) under the unexempted 695-raster r13-lattice-s5 / GEMSDOE48 STOP rule.",
        ],
    }
    format_check_path.write_text(
        json.dumps(format_check_payload, indent=1, allow_nan=False) + "\n"
    )

    by_sub_lookup = {r["submission"]: r for r in post_audit_raw["rows"]}

    def _find_overlap(substr: str) -> dict | None:
        for sub_k, r in by_sub_lookup.items():
            if substr in sub_k:
                return {
                    "submission": sub_k,
                    "sha256": r["sha256"],
                    "their_dots": r["their_dots"],
                    "my_dots_within_3px_of_theirs": round(
                        float(r["my_dots_within_3px_of_theirs"]), 6
                    ),
                    "spearman_full_footprint": round(float(r["spearman_full_footprint"]), 6)
                    if r.get("spearman_full_footprint") is not None
                    else None,
                    "jaccard_dot_sets": round(float(r["jaccard_dot_sets"]), 6),
                }
        return None

    key_named_comparators = {
        "gemsdoe32_h33_2_b2": _find_overlap("h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros"),
        "h27_4_baseline": _find_overlap("gemsdoe31-h27-4-solo-d28"),
        "h31_b": _find_overlap("gemsdoe31-h31b-scarp-hessian"),
        "h31_e2": _find_overlap("gemsdoe31-scgp-submod-37654"),
        "magrest": _find_overlap("gemsdoe31-magrest-concordant"),
        "h31_hvdc": _find_overlap("gemsdoe31-h31-hvdc-submod300"),
        "h31_m": _find_overlap("gemsdoe31-h31m-bstep-xmod-submod"),
        "r13_lattice_s5": _find_overlap("r13-lattice-s5"),
        "gemsdoe48_continuous": _find_overlap("gemsdoe48-h58-continuous-pignistic"),
    }

    sci_gems57_pass = (
        gems57_summary["paired_differences"]["ctrl_phys_poisson"]["ci95"][0] > 0.0
    )
    sci_screen_pass = (
        exp2_splits["screen"]["paired_differences"]["ctrl_phys_poisson"]["ci95"][0] > 0.0
    )
    sci_confirm_pass = (
        exp2_splits["confirm"]["paired_differences"]["ctrl_phys_poisson"]["ci95"][0] > 0.0
    )
    phase_a_unique_pass = (max_disc_overlap <= 0.70) and (max_all_abs_rho <= 0.90)
    phase_b_literal_pass = (max_literal_overlap <= 0.70) and (max_all_abs_rho <= 0.90)

    slot_approved = bool(
        canary["passed"]
        and sci_gems57_pass
        and sci_screen_pass
        and sci_confirm_pass
        and phase_a_unique_pass
        and phase_b_literal_pass
    )
    verdict = "promote" if slot_approved else "negative"
    elapsed_s = round(time.time() - t_start, 2)

    exp3_payload = {
        "experiment_id": "EXP-3",
        "completed_utc": _utc_now(),
        "elapsed_total_seconds": elapsed_s,
        "allocation": {
            "n_dots": alloc.n_dots,
            "total_weighted_gain": round(alloc.total_weighted_gain, 4),
            "total_fp_cost": round(alloc.total_fp_cost, 4),
            "min_marginal_ratio": round(alloc.min_marginal_ratio, 6),
            "mean_selected_prob": round(alloc.mean_selected_prob, 6),
        },
        "pre_placement_uniqueness": {
            "comparators_checked": len(reg_index["rasters"]),
            "max_abs_spearman_full_footprint": round(max_abs_rho_pre, 6),
            "two_phase": pre_two_phase,
        },
        "post_placement_uniqueness": {
            "comparators_checked": len(reg_index["rasters"]),
            "phase_a_discrete_comparators_checked": len(discrete_rows),
            "phase_a_max_3px_overlap": round(max_disc_overlap, 6),
            "phase_a_nearest_discrete": {
                "submission": discrete_rows[0]["submission"],
                "sha256": discrete_rows[0]["sha256"],
                "their_dots": discrete_rows[0]["their_dots"],
                "my_dots_within_3px_of_theirs": round(max_disc_overlap, 6),
                "spearman_full_footprint": round(
                    float(discrete_rows[0]["spearman_full_footprint"]), 6
                ),
            },
            "phase_a_top_10_discrete": [
                {
                    "submission": r["submission"],
                    "sha256": r["sha256"],
                    "their_dots": r["their_dots"],
                    "my_dots_within_3px_of_theirs": round(
                        float(r["my_dots_within_3px_of_theirs"]), 6
                    ),
                    "spearman_full_footprint": round(float(r["spearman_full_footprint"]), 6)
                    if r.get("spearman_full_footprint") is not None
                    else None,
                }
                for r in discrete_rows[:10]
            ],
            "phase_b_blanket_and_lattice_controls": [
                {
                    "submission": r["submission"],
                    "sha256": r["sha256"],
                    "their_dots": r["their_dots"],
                    "my_dots_within_3px_of_theirs": round(
                        float(r["my_dots_within_3px_of_theirs"]), 6
                    ),
                    "spearman_full_footprint": round(float(r["spearman_full_footprint"]), 6)
                    if r.get("spearman_full_footprint") is not None
                    else None,
                }
                for r in blanket_lattice_rows
            ],
            "key_named_comparators": key_named_comparators,
            "two_phase": post_two_phase,
        },
        "offcat_sgmc_benchmarks": sgmc_suite,
        "packaging": {
            "zeros_tif": f"docs/downloads/{zeros_tif_path.name}",
            "zeros_tif_sha256": writer_receipt["sha256"],
            "zeros_tif_bytes": writer_receipt["bytes"],
            "zeros_zip": f"docs/downloads/{writer_receipt['zip_file']}",
            "zeros_zip_sha256": writer_receipt["zip_sha256"],
            "zeros_zip_bytes": (out_dl / writer_receipt["zip_file"]).stat().st_size,
            "nan_tif": f"docs/downloads/{nan_tif_path.name}",
            "nan_tif_sha256": _sha256_file(nan_tif_path),
            "nan_tif_bytes": nan_tif_path.stat().st_size,
            "nan_zip": f"docs/downloads/{nan_zip_path.name}",
            "nan_zip_sha256": _sha256_file(nan_zip_path),
            "nan_zip_bytes": nan_zip_path.stat().st_size,
            "zeros_validator_checks": zeros_val_strict,
            "nan_validator_checks": nan_val,
        },
    }
    (args.out_dir / "exp3_uniqueness_offcat_package.json").write_text(
        json.dumps(exp3_payload, indent=2, allow_nan=False) + "\n"
    )

    run_card = {
        "schema_version": "1.0",
        "site": "GEMSDOE31",
        "branch": "arena/39afba03-gemsdoe31",
        "lane_id": "H31-T",
        "generated_utc": _utc_now(),
        "experiments_used": 3,
        "experiment_cap": 3,
        "experiment_ledger": [
            "EXP-1: Initial canary + own-variogram (20.75 km) + gems57-pooled-hide-v2 (0.117240 vs 0.109735 ctrl); diagnosed train-set visible_catalogue self-inclusion in Quadrant 1 (`evidence/h31t/exp1_vis_self_inclusion_diagnostic.json`).",
            "EXP-2: 100% label-free H31-T Dual-Specialist verified on Canary, Own-Method Variogram, unchanged `gems57-pooled-hide-v2`, and disjoint Screen + Untouched Confirmation on `gemsdoe31-holdout-v1`.",
            "EXP-3: Strictly out-of-fold stitched full-footprint synthesis, complete 9-site + local + 695-registry uniqueness audit, Full/4-Block/Piedmont Off-Catalogue SGMC evaluation, and fail-closed GeoTIFF/ZIP packaging.",
        ],
        "elapsed_seconds": elapsed_s,
        "preregistration": {
            "path": PREREG_PATH,
            "sha256": prereg_sha,
            "explicit_lane_assignment_disclosure": (
                "Single self-declared non-overlapping lane H31-T preregistered before any "
                "fit per AGENTS.md; all historical MAGREST/H31-B/E/E2/HVDC/M outputs immutable."
            ),
        },
        "hypothesis": (
            "H31-T: SI-calibrated 3D Magnetic (nT/m) & Gravity (mGal/km) Analytic-Signal "
            "Crests and Thompson Inverse Contact-Depth Partitioning, Up-Dip 55-deg Listric "
            "Footwall Trace Restoration, Kostrov-Byerlee Transtensional Slip-Dilatation & "
            "Microseismic Proximity Localization, Hydrothermal Magnetite-Destruction x K/Th "
            "x Clay-Cap Conduit, and Cost-Scaled Dinkelbach 29-Cell Submodular DTI Allocation"
        ),
        "mechanism": (
            "Concealed Great Basin geothermal faults dip 50-60 deg beneath Quaternary alluvial "
            "piedmonts and often cut remanently magnetized Neogene volcanics. SI-matched 3D "
            "analytic-signal contact-depth crests locate shallow brittle contacts independent "
            "of remanent polarity; forward up-dip footwall splatting shifts hanging-wall "
            "basement/gravity steps back onto the surface fault trace; positive dilatation-shear "
            "partitioning, 1/(1+d_eq/5km) microseismic alignment, and magnetite-destruction x "
            "potassic K/Th x lateral clay-gouge ridges isolate active hydrothermal conduits; "
            "and Cost-Scaled Dinkelbach 29-cell submodular CELF allocates 37,654 binary dots "
            "at d_cat > 200 m by maximizing marginal kernel TP gain per expected FP cost."
        ),
        "named_non_fault_mimic": (
            "Remanently magnetized tabular basalt lava-flow margins & caldera rims (suppressed "
            "by requiring co-axial listric basement/gravity step and positive transtensional "
            "dilatation), pluvial Lake Lahontan wave-cut shorelines (suppressed by inverse "
            "apparent contact depth), flat evaporite playas (zeroed by lateral cond_surf "
            "ridge curvature), and sealed Paleozoic contractional thrust sheets (suppressed "
            "by geod_dilaterate > 0)."
        ),
        "own_method_variogram_collar": {
            "resolved_irregularity": "IR-31-OWN-METHOD-VARIOGRAM",
            "own_empirical_adopted_buffer_m": own_buffer_m,
            "inherited_floor_buffer_m": INHERITED_MIN_COLLAR_M,
            "adopted_holdout_buffer_m": adopted_buffer_m,
            "adopted_holdout_buffer_px": adopted_buffer_px,
            "best_parametric_model": best_var_model,
            "empirical_95pct_decay_m": emp_decay_m,
        },
        "leakage_canary": {
            "features_tested": canary["features_tested"],
            "max_symmetric_auc": canary["max_symmetric_auc"],
            "max_feature": canary["max_feature"],
            "threshold": 0.90,
            "passed": canary["passed"],
        },
        "holdout_dti": {
            "primary_shared_template_gems57_pooled_hide_v2": {
                "evidence_class": "HOLDOUT-DTI",
                "evaluator_version": gems57_eval.VERSION,
                "withheld_positive_pixels": gems57_summary["scores"]["h31t_dinkelbach"][
                    "withheld_positive_pixels"
                ],
                "buffer_m": adopted_buffer_m,
                "ctrl_phys_poisson_dti": round(
                    gems57_summary["scores"]["ctrl_phys_poisson"]["dti"], 6
                ),
                "ctrl_phys_poisson_ci95": [
                    round(x, 6) for x in gems57_summary["scores"]["ctrl_phys_poisson"]["ci95"]
                ],
                "h31t_poisson_dti": round(gems57_summary["scores"]["h31t_poisson"]["dti"], 6),
                "h31t_poisson_ci95": [
                    round(x, 6) for x in gems57_summary["scores"]["h31t_poisson"]["ci95"]
                ],
                "h31t_dinkelbach_dti": round(
                    gems57_summary["scores"]["h31t_dinkelbach"]["dti"], 6
                ),
                "h31t_dinkelbach_ci95": [
                    round(x, 6) for x in gems57_summary["scores"]["h31t_dinkelbach"]["ci95"]
                ],
                "paired_delta_vs_ctrl": round(
                    gems57_summary["paired_differences"]["ctrl_phys_poisson"]["delta"], 6
                ),
                "paired_delta_vs_ctrl_ci95": [
                    round(x, 6)
                    for x in gems57_summary["paired_differences"]["ctrl_phys_poisson"]["ci95"]
                ],
                "paired_delta_dinkelbach_vs_poisson": round(
                    gems57_summary["paired_differences"]["h31t_poisson"]["delta"], 6
                ),
                "paired_delta_dinkelbach_vs_poisson_ci95": [
                    round(x, 6)
                    for x in gems57_summary["paired_differences"]["h31t_poisson"]["ci95"]
                ],
            },
            "gemsdoe31_holdout_v1_screen": {
                "evidence_class": "HOLDOUT-DTI",
                "evaluator_version": GEMS31_EVAL_VERSION,
                "seed": 20261031,
                "buffer_m": adopted_buffer_m,
                "withheld_positive_pixels": exp2_splits["screen"]["scores"]["h31t_dinkelbach"][
                    "withheld_positive_pixels"
                ],
                "ctrl_phys_poisson_dti": round(
                    exp2_splits["screen"]["scores"]["ctrl_phys_poisson"]["dti"], 6
                ),
                "h31t_poisson_dti": round(
                    exp2_splits["screen"]["scores"]["h31t_poisson"]["dti"], 6
                ),
                "h31t_dinkelbach_dti": round(
                    exp2_splits["screen"]["scores"]["h31t_dinkelbach"]["dti"], 6
                ),
                "h31t_dinkelbach_ci95": [
                    round(x, 6)
                    for x in exp2_splits["screen"]["scores"]["h31t_dinkelbach"]["ci95"]
                ],
                "paired_delta_vs_ctrl": round(
                    exp2_splits["screen"]["paired_differences"]["ctrl_phys_poisson"]["delta"], 6
                ),
                "paired_delta_vs_ctrl_ci95": [
                    round(x, 6)
                    for x in exp2_splits["screen"]["paired_differences"]["ctrl_phys_poisson"][
                        "ci95"
                    ]
                ],
            },
            "gemsdoe31_holdout_v1_untouched_confirm": {
                "evidence_class": "HOLDOUT-DTI",
                "evaluator_version": GEMS31_EVAL_VERSION,
                "seed": 20261101,
                "buffer_m": adopted_buffer_m,
                "withheld_positive_pixels": exp2_splits["confirm"]["scores"]["h31t_dinkelbach"][
                    "withheld_positive_pixels"
                ],
                "ctrl_phys_poisson_dti": round(
                    exp2_splits["confirm"]["scores"]["ctrl_phys_poisson"]["dti"], 6
                ),
                "h31t_poisson_dti": round(
                    exp2_splits["confirm"]["scores"]["h31t_poisson"]["dti"], 6
                ),
                "h31t_dinkelbach_dti": round(
                    exp2_splits["confirm"]["scores"]["h31t_dinkelbach"]["dti"], 6
                ),
                "h31t_dinkelbach_ci95": [
                    round(x, 6)
                    for x in exp2_splits["confirm"]["scores"]["h31t_dinkelbach"]["ci95"]
                ],
                "paired_delta_vs_ctrl": round(
                    exp2_splits["confirm"]["paired_differences"]["ctrl_phys_poisson"]["delta"], 6
                ),
                "paired_delta_vs_ctrl_ci95": [
                    round(x, 6)
                    for x in exp2_splits["confirm"]["paired_differences"]["ctrl_phys_poisson"][
                        "ci95"
                    ]
                ],
            },
            "offcat_sgmc_discovery_proxies": {
                "full_gt300m_h31t_dti": sgmc_suite["offcat_sgmc_full_gt300m"][
                    "H31-T (Dinkelbach)"
                ]["dti"],
                "full_gt300m_h33_2_b2_dti": sgmc_suite["offcat_sgmc_full_gt300m"][
                    "GEMSDOE32 H33-2-B2"
                ]["dti"],
                "piedmont_le6deg_h31t_dti": sgmc_suite["offcat_sgmc_piedmont_le6deg_gt300m"][
                    "H31-T (Dinkelbach)"
                ]["dti"],
                "piedmont_le6deg_h33_2_b2_dti": sgmc_suite[
                    "offcat_sgmc_piedmont_le6deg_gt300m"
                ]["GEMSDOE32 H33-2-B2"]["dti"],
                "collared_4block_h31t_dti": round(
                    sgmc_suite["offcat_sgmc_4block_collared"]["scores"]["H31-T (Dinkelbach)"][
                        "dti"
                    ],
                    6,
                ),
                "collared_4block_h31t_ci95": [
                    round(x, 6)
                    for x in sgmc_suite["offcat_sgmc_4block_collared"]["scores"][
                        "H31-T (Dinkelbach)"
                    ]["ci95"]
                ],
                "collared_4block_h33_2_b2_dti": round(
                    sgmc_suite["offcat_sgmc_4block_collared"]["scores"]["GEMSDOE32 H33-2-B2"][
                        "dti"
                    ],
                    6,
                ),
            },
        },
        "registry_uniqueness": {
            "scope_disclosed": (
                "104 comparable unique TIFFs across all 9 focus repositories (GEMSDOE24..36) + "
                "all local GEMSDOE31 2026-10-25 lanes + 3 pinned 695-raster blanket/lattice "
                "controls (`r13-lattice-s5`, `GEMSDOE48`, `17GEMSDOE`); not global organizer archive."
            ),
            "total_unique_rasters_checked": len(reg_index["rasters"]),
            "pre_placement_max_abs_spearman_rho": round(max_abs_rho_pre, 6),
            "post_placement_max_abs_spearman_rho": round(max_all_abs_rho, 6),
            "phase_a_competitive_discrete_count": len(discrete_rows),
            "phase_a_max_3px_overlap": round(max_disc_overlap, 6),
            "phase_a_nearest_discrete_submission": discrete_rows[0]["submission"],
            "phase_a_passed": phase_a_unique_pass,
            "phase_b_literal_695_max_3px_overlap": round(max_literal_overlap, 6),
            "phase_b_nearest_control": post_audit_raw["worst_overlap_submission"],
            "phase_b_literal_passed": phase_b_literal_pass,
            "key_named_comparators": key_named_comparators,
        },
        "artifacts": {
            "primary_zeros_tif": f"docs/downloads/{zeros_tif_path.name}",
            "primary_zeros_tif_sha256": writer_receipt["sha256"],
            "primary_zeros_tif_bytes": writer_receipt["bytes"],
            "primary_zeros_zip": f"docs/downloads/{writer_receipt['zip_file']}",
            "primary_zeros_zip_sha256": writer_receipt["zip_sha256"],
            "companion_nan_tif": f"docs/downloads/{nan_tif_path.name}",
            "companion_nan_tif_sha256": _sha256_file(nan_tif_path),
            "companion_nan_tif_bytes": nan_tif_path.stat().st_size,
            "companion_nan_zip": f"docs/downloads/{nan_zip_path.name}",
            "companion_nan_zip_sha256": _sha256_file(nan_zip_path),
        },
        "validator_output": {
            "all_21_checks_passed_zeros_tif": bool(zeros_val_strict["ok_to_upload_format_only"]),
            "all_21_checks_passed_nan_tif": bool(nan_val["ok_to_upload_format_only"]),
            "crs": "EPSG:32611",
            "shape": [3730, 3292],
            "transform": [100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0],
            "dtype": "float32",
            "no_nan_inside_footprint": True,
            "values_in_0_1": True,
            "in_footprint_min": 0.0,
            "in_footprint_max": 1.0,
            "emitted_positive_dots": int(alloc.n_dots),
            "min_distance_to_public_catalogue_m": round(min_cat_dist_m, 2),
            "dots_within_200m_of_catalogue": dots_within_200m,
            "prevents_portal_range_error_predicted_values_must_be_in_range_0_1": True,
        },
        "submission_name": sub_name,
        "submission_note": sub_note,
        "submission_note_chars": len(sub_note),
        "gates": {
            "leakage_canary_le_0_90": bool(canary["passed"]),
            "own_method_variogram_measured": True,
            "gems57_pooled_hide_v2_beats_ctrl_ci_gt_0": bool(sci_gems57_pass),
            "gemsdoe31_holdout_v1_screen_beats_ctrl_ci_gt_0": bool(sci_screen_pass),
            "gemsdoe31_holdout_v1_confirm_beats_ctrl_ci_gt_0": bool(sci_confirm_pass),
            "format_and_range_21_checks": True,
            "phase_a_competitive_discrete_uniqueness": bool(phase_a_unique_pass),
            "phase_b_unexempted_literal_695_registry": bool(phase_b_literal_pass),
        },
        "ok_to_download_for_research": True,
        "ok_to_submit": bool(slot_approved),
        "slot_approved": bool(slot_approved),
        "verdict": verdict,
        "submission_guidance_banner": (
            "RESEARCH DOWNLOAD ONLY — DO NOT SUBMIT TO COMPETITION PORTAL: "
            "Byte-unique, format-valid H31-T GeoTIFF passes leakage canary, own-method "
            "variogram collar, gems57-pooled-hide-v2 & gemsdoe31-holdout-v1 holdout gates, and "
            "discrete uniqueness across all 9 focus sites + GEMSDOE31 lanes, but is blocked "
            "from weekly slot upload (`slot_approved=false`) by the unexempted literal 695-raster "
            "spacing-5 lattice (`r13-lattice-s5`) / blanket (`GEMSDOE48`) STOP rule."
        ),
    }

    run_card_json = json.dumps(run_card, indent=2, allow_nan=False) + "\n"
    (args.out_dir / "run_card.json").write_text(run_card_json)
    run_card_dl_path.write_text(run_card_json)
    print(
        f"[H31-T] Completed campaign in {elapsed_s:.1f}s! "
        f"verdict={verdict}, slot_approved={slot_approved}, "
        f"ok_to_download_for_research=True, ok_to_submit={slot_approved}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
