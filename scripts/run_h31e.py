#!/usr/bin/env python3
"""H31-E surface-expression experiment runner (EXP-1 canary, EXP-2 holdout, EXP-3 emission).

Design frozen in ``knowledge/2026-10-25_h31e_surface_expression_preregistration.md`` before any
fit. Stages: ``channels`` -> ``canary`` -> ``holdout`` (screen+confirm) -> ``final`` -> ``report``
(or ``all``). Nothing here contacts DrivenData; inputs are the hash-verified owner mirrors in
``data/`` (``evidence/data_restore.json``).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import spearmanr
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gemsdoe31 import holdout as ho  # noqa: E402
from gemsdoe31 import metric  # noqa: E402
from gemsdoe31.emission import INCUMBENT_DENSITY, emit_dots  # noqa: E402
from gemsdoe31.raster import SHAPE  # noqa: E402
from gemsdoe31.surface_features import NEW_CHANNELS, build_new_channels  # noqa: E402

WORK = ROOT / "data/prepared/h31e_work"
PREPARED = ROOT / "data/prepared"
SCREEN_SEED = 20261025
CONFIRM_SEED = 20261026
NEGATIVE_CAP = 300_000
HGB_PARAMS = dict(max_iter=100, learning_rate=0.12, max_leaf_nodes=31, min_samples_leaf=50,
                  l2_regularization=1.0, early_stopping=False)

BASE_BANDS = ["det_elev", "det_elev_slope",
              "ex_max", "ex_mean", "step_max", "lapneg_max", "lappos_max", "downface_max",
              "upface_max", "cross_max", "relief", "coh100", "strike", "valid",
              "K", "Th", "U", "TC", "ThK", "UK", "UTh", "mean_k_500m", "th_minus_k",
              "upface_minus_downface"]
CANDIDATE_BANDS = BASE_BANDS + NEW_CHANNELS

REGISTRY_RASTERS = {
    "h27_4": "docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif",
    "union_b_p060": "docs/downloads/gemsdoe31-union-b-p060-20261004-8acb75e1-nan.tif",
    "add_arm_d": "docs/downloads/gemsdoe31-add-arm-d28-20261004-8acb75e1-nan.tif",
    "d28_reference": "docs/downloads/gemsdoe31-reference-d28-offcat-44090-20261004-nan.tif",
}


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


class Bands:
    """Unified read access to the prepared stack memmap + H31-E new-channel memmap."""

    def __init__(self) -> None:
        meta = json.loads((PREPARED / "features.json").read_text())
        self.stack_names = meta["bands"]
        self.stack = np.memmap(PREPARED / "features.f32", dtype=np.float32, mode="r",
                               shape=(len(self.stack_names),) + SHAPE)
        self.new_names: list[str] = []
        self.new = None
        new_meta = PREPARED / "h31e.json"
        if new_meta.exists():
            self.new_names = json.loads(new_meta.read_text())["bands"]
            self.new = np.memmap(PREPARED / "h31e.f32", dtype=np.float32, mode="r",
                                 shape=(len(self.new_names),) + SHAPE)

    def band(self, name: str) -> np.ndarray:
        if name in self.new_names:
            return np.asarray(self.new[self.new_names.index(name)])
        return np.asarray(self.stack[self.stack_names.index(name)])

    def gather(self, names: list[str], rows: np.ndarray, cols: np.ndarray) -> np.ndarray:
        return np.column_stack([self.band(name)[rows, cols] for name in names]).astype(np.float32)

    def block(self, names: list[str], r0: int, r1: int, c0: int, c1: int) -> np.ndarray:
        slices = [self.band(name)[r0:r1, c0:c1] for name in names]
        stacked = np.stack(slices, axis=-1)
        return stacked.reshape(-1, len(names)).astype(np.float32)


def load_masks() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    catalogue = rasterio.open(ROOT / "data/labels.tif").read(1) == 1
    footprint = np.isfinite(rasterio.open(ROOT / "data/sample_submission.tif").read(1))
    sgmc = rasterio.open(ROOT / "data/external/derived_sgmc_faults_100m_u8.tif").read(1) == 1
    far_field = sgmc & (distance_transform_edt(~catalogue) * 100.0 > metric.RADIUS_M)
    return catalogue, footprint, far_field


def splits(catalogue: np.ndarray, footprint: np.ndarray) -> list[dict]:
    return [ho.fold_split(catalogue, footprint, fold) for fold in range(4)]


# --------------------------------------------------------------------------------------
# Stage: channels
# --------------------------------------------------------------------------------------

def stage_channels() -> None:
    bands = Bands()
    needed = {name: bands.band(name) for name in
              ["det_elev", "ThK", "UTh", "UK", "upface_minus_downface", "coh100"]}
    log("building H31-E transform channels")
    t0 = time.time()
    channels = build_new_channels(needed)
    assert list(channels) == NEW_CHANNELS
    out = np.memmap(PREPARED / "h31e.f32", dtype=np.float32, mode="w+",
                    shape=(len(NEW_CHANNELS),) + SHAPE)
    stats = {}
    for i, name in enumerate(NEW_CHANNELS):
        out[i] = channels[name]
        finite = channels[name][np.isfinite(channels[name])]
        stats[name] = {"finite": int(finite.size), "min": float(finite.min()),
                       "median": float(np.median(finite)), "max": float(finite.max())}
        log(f"  {name:<16} finite {finite.size:>10,} max {finite.max():.4g}")
    out.flush()
    (PREPARED / "h31e.json").write_text(json.dumps(
        {"bands": NEW_CHANNELS, "stats": stats, "build_seconds": round(time.time() - t0, 1)},
        indent=1) + "\n")
    log(f"channels written in {time.time() - t0:.0f}s")


# --------------------------------------------------------------------------------------
# Stage: canary (EXP-1)
# --------------------------------------------------------------------------------------

def _fold_k(split: dict) -> int:
    return int(round(split["n_domain_pixels"] * INCUMBENT_DENSITY))


def _score_emission(surface: np.ndarray, catalogue: np.ndarray, split: dict) -> dict:
    valid = split["domain"] & np.isfinite(surface)
    dots = emit_dots(surface, valid, max_dots=_fold_k(split))
    result = ho.score_fold(dots.astype(np.float32), catalogue, split)
    return {"dots": int(dots.sum()), "DTI": result["DTI"], "TPw": result["TPw"],
            "FPw": result["FPw"], "truth": result["truth_pixels"]}


def _pooled(rows: list[dict]) -> float:
    tp = sum(r["TPw"] for r in rows)
    fp = sum(r["FPw"] for r in rows)
    n = sum(r["truth"] for r in rows)
    return float(tp / (tp + metric.ALPHA * fp + metric.BETA * (n - tp) + metric.EPSILON))


def stage_canary() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    bands = Bands()
    catalogue, footprint, _ = load_masks()
    fold_splits = splits(catalogue, footprint)
    for s in fold_splits:
        log(f"fold {s['fold_name']}: domain {s['n_domain_pixels']:,} truth {s['n_truth_pixels']:,} "
            f"withheld comps {s['n_withheld_components']} train+ {s['n_train_positive_pixels']:,}")

    # AUC canary: pooled withheld truth vs sampled in-domain background.
    truth_all = np.zeros(SHAPE, dtype=bool)
    domain_all = np.zeros(SHAPE, dtype=bool)
    for s in fold_splits:
        truth_all |= s["truth"]
        domain_all |= s["domain"]
    rng = np.random.default_rng(SCREEN_SEED)
    pos_r, pos_c = np.nonzero(truth_all)
    bg_r_all, bg_c_all = np.nonzero(domain_all & ~catalogue)
    pick = rng.choice(bg_r_all.size, size=min(200_000, bg_r_all.size), replace=False)
    bg_r, bg_c = bg_r_all[pick], bg_c_all[pick]
    y = np.concatenate([np.ones(pos_r.size), np.zeros(bg_r.size)])
    rows = np.concatenate([pos_r, bg_r])
    cols = np.concatenate([pos_c, bg_c])

    aucs = {}
    for name in NEW_CHANNELS + ["oof_B_reference"]:
        if name == "oof_B_reference":
            with np.load(ROOT / "evidence/oof/oof_B_19_plus_lidar_u16.npz") as z:
                values_full = z["probability_u16"].astype(np.float32) / 65535.0
            values = values_full[rows, cols]
        else:
            values = bands.band(name)[rows, cols]
        keep = np.isfinite(values)
        auc = float(roc_auc_score(y[keep], values[keep])) if keep.sum() > 100 else None
        aucs[name] = {"auc": auc, "n_scored": int(keep.sum())}
        log(f"canary AUC {name:<18} {auc if auc is None else round(auc, 4)}")

    # Single-channel emission screen + fixed controls C2 (incumbent) and C3 (OOF-B emission).
    incumbent = np.nan_to_num(
        rasterio.open(ROOT / REGISTRY_RASTERS["h27_4"]).read(1), nan=0.0) > 0
    with np.load(ROOT / "evidence/oof/oof_B_19_plus_lidar_u16.npz") as z:
        oof_b = z["probability_u16"].astype(np.float32) / 65535.0
    oof_b[~footprint] = np.nan

    screen: dict[str, dict] = {}
    surfaces: dict[str, np.ndarray] = {name: bands.band(name) for name in NEW_CHANNELS}
    surfaces["C3_oof_B"] = oof_b
    for name, surface in surfaces.items():
        rows_f = [_score_emission(surface, catalogue, s) for s in fold_splits]
        screen[name] = {"per_fold": rows_f, "pooled_DTI": _pooled(rows_f)}
        log(f"screen {name:<18} pooled HOLDOUT-DTI {screen[name]['pooled_DTI']:.4f}")
    rows_inc = []
    for s in fold_splits:
        result = ho.score_fold(incumbent.astype(np.float32), catalogue, s)
        rows_inc.append({"dots": int((incumbent & s["domain"]).sum()), "DTI": result["DTI"],
                         "TPw": result["TPw"], "FPw": result["FPw"],
                         "truth": result["truth_pixels"]})
    screen["C2_incumbent_h27_4"] = {"per_fold": rows_inc, "pooled_DTI": _pooled(rows_inc)}
    log(f"screen C2 incumbent   pooled HOLDOUT-DTI {screen['C2_incumbent_h27_4']['pooled_DTI']:.4f}")

    payload = {"evaluator": ho.EVALUATOR_ID, "collar_m": ho.COLLAR_M, "aucs": aucs,
               "single_channel_and_controls": screen,
               "fold_bookkeeping": [{k: s[k] for k in
                                      ("fold_name", "n_withheld_components",
                                       "n_excluded_components", "n_truth_pixels",
                                       "n_domain_pixels", "n_train_positive_pixels")}
                                     for s in fold_splits],
               "withheld_positive_pixels_total": int(truth_all.sum())}
    (WORK / "canary.json").write_text(json.dumps(payload, indent=1) + "\n")
    worst = max((v["auc"] or 0) for k, v in aucs.items() if k in NEW_CHANNELS)
    log(f"canary worst new-channel AUC {worst:.4f} (leakage stop > 0.90)")


# --------------------------------------------------------------------------------------
# Stage: holdout (EXP-2)
# --------------------------------------------------------------------------------------

def _train(bands: Bands, names: list[str], catalogue: np.ndarray, split: dict,
           seed: int) -> HistGradientBoostingClassifier:
    allowed = split["train_allowed"]
    pos_r, pos_c = np.nonzero(catalogue & allowed)
    neg_r_all, neg_c_all = np.nonzero(allowed & ~catalogue)
    rng = np.random.default_rng(seed + split["fold"])
    pick = rng.choice(neg_r_all.size, size=min(NEGATIVE_CAP, neg_r_all.size), replace=False)
    rows = np.concatenate([pos_r, neg_r_all[pick]])
    cols = np.concatenate([pos_c, neg_c_all[pick]])
    y = np.concatenate([np.ones(pos_r.size, dtype=np.int8), np.zeros(pick.size, dtype=np.int8)])
    x = bands.gather(names, rows, cols)
    weights = np.where(y == 1, 5.0, 1.0)
    model = HistGradientBoostingClassifier(random_state=seed, **HGB_PARAMS)
    model.fit(x, y, sample_weight=weights)
    return model


def _predict_domain(bands: Bands, names: list[str], model, split: dict) -> np.ndarray:
    surface = np.zeros(SHAPE, dtype=np.float32)
    r0, r1, c0, c1 = split["bbox"]
    x = bands.block(names, r0, r1, c0, c1)
    proba = model.predict_proba(x)[:, 1].reshape(r1 - r0, c1 - c0)
    surface[r0:r1, c0:c1] = proba.astype(np.float32)
    return surface


def stage_holdout(seed: int, label: str) -> None:
    bands = Bands()
    catalogue, footprint, _ = load_masks()
    fold_splits = splits(catalogue, footprint)
    arms = {"candidate": CANDIDATE_BANDS, "base_C1": BASE_BANDS}
    results: dict[str, dict] = {}
    blocks_store: dict[str, list[dict]] = {}
    for arm, names in arms.items():
        per_fold = []
        blocks_store[arm] = []
        for s in fold_splits:
            t0 = time.time()
            model = _train(bands, names, catalogue, s, seed)
            surface = _predict_domain(bands, names, model, s)
            valid = s["domain"]
            dots = emit_dots(surface, valid, max_dots=_fold_k(s))
            result = ho.score_fold(dots.astype(np.float32), catalogue, s)
            blocks_store[arm].append(result["block_stats"])
            per_fold.append({"fold": s["fold_name"], "dots": int(dots.sum()),
                             "DTI": result["DTI"], "TPw": result["TPw"], "FPw": result["FPw"],
                             "truth": result["truth_pixels"]})
            log(f"{label} {arm} {s['fold_name']}: dots {int(dots.sum()):,} "
                f"HOLDOUT-DTI {result['DTI']:.4f} ({time.time() - t0:.0f}s)")
        results[arm] = {"per_fold": per_fold, "pooled_DTI": _pooled(per_fold)}
        log(f"{label} {arm}: pooled HOLDOUT-DTI {results[arm]['pooled_DTI']:.4f}")
    boot = ho.paired_block_bootstrap(
        {"candidate": blocks_store["candidate"], "base_C1": blocks_store["base_C1"]})
    payload = {"seed_label": label, "seed": seed, "arms": results, "bootstrap": boot}
    (WORK / f"holdout_{label}.json").write_text(json.dumps(payload, indent=1) + "\n")
    log(f"{label} bootstrap: candidate CI {boot['ci95']['candidate']} "
        f"paired delta CI {boot['paired_delta_ci95']}")


# --------------------------------------------------------------------------------------
# Stage: final (EXP-3)
# --------------------------------------------------------------------------------------

def stage_final() -> None:
    bands = Bands()
    catalogue, footprint, _ = load_masks()
    pos_r, pos_c = np.nonzero(catalogue & footprint)
    neg_r_all, neg_c_all = np.nonzero(footprint & ~catalogue)
    rng = np.random.default_rng(SCREEN_SEED + 99)
    pick = rng.choice(neg_r_all.size, size=NEGATIVE_CAP, replace=False)
    rows = np.concatenate([pos_r, neg_r_all[pick]])
    cols = np.concatenate([pos_c, neg_c_all[pick]])
    y = np.concatenate([np.ones(pos_r.size, dtype=np.int8), np.zeros(pick.size, dtype=np.int8)])
    x = bands.gather(CANDIDATE_BANDS, rows, cols)
    log(f"final fit: {x.shape[0]:,} samples x {x.shape[1]} bands")
    model = HistGradientBoostingClassifier(random_state=SCREEN_SEED, **HGB_PARAMS)
    model.fit(x, y, sample_weight=np.where(y == 1, 5.0, 1.0))

    surface = np.full(SHAPE, np.nan, dtype=np.float32)
    for r0 in range(0, SHAPE[0], 256):
        r1 = min(r0 + 256, SHAPE[0])
        block_fp = footprint[r0:r1]
        if not block_fp.any():
            continue
        xb = bands.block(CANDIDATE_BANDS, r0, r1, 0, SHAPE[1])
        proba = model.predict_proba(xb)[:, 1].reshape(r1 - r0, SHAPE[1])
        surface[r0:r1] = np.where(block_fp, proba, np.nan).astype(np.float32)
    np.save(WORK / "candidate_surface.npy", surface)

    k = int(round(int(footprint.sum()) * INCUMBENT_DENSITY))
    dots = emit_dots(surface, footprint, max_dots=k)
    log(f"final emission: {int(dots.sum()):,} dots (budget {k:,})")
    np.save(WORK / "candidate_dots.npy", dots)
    transform = rasterio.transform.from_origin(243350.0, 4508550.0, 100.0, 100.0)
    profile = {"driver": "GTiff", "crs": "EPSG:32611", "transform": transform,
               "height": SHAPE[0], "width": SHAPE[1], "count": 1, "dtype": "float32",
               "nodata": float("nan")}
    with rasterio.open(WORK / "candidate_dots.tif", "w", **profile) as dst:
        dst.write(np.where(dots, 1.0, np.nan).astype(np.float32), 1)
    importances = None
    (WORK / "final.json").write_text(json.dumps(
        {"dots": int(dots.sum()), "budget_k": k, "bands": CANDIDATE_BANDS,
         "feature_importances": importances}, indent=1) + "\n")


# --------------------------------------------------------------------------------------
# Stage: report
# --------------------------------------------------------------------------------------

def _dots_of(path: Path) -> np.ndarray:
    return np.nan_to_num(rasterio.open(path).read(1), nan=0.0) > 0


def _within3_fraction(dots: np.ndarray, registry_dots: np.ndarray) -> float:
    distance_px = distance_transform_edt(~registry_dots)
    return float((distance_px[dots] <= 3.0).mean()) if dots.any() else 0.0


def stage_report() -> None:
    catalogue, footprint, far_field = load_masks()
    canary = json.loads((WORK / "canary.json").read_text())
    screen = json.loads((WORK / "holdout_screen.json").read_text())
    confirm_path = WORK / "holdout_confirm.json"
    confirm = json.loads(confirm_path.read_text()) if confirm_path.exists() else None
    final = json.loads((WORK / "final.json").read_text())
    dots = np.load(WORK / "candidate_dots.npy")
    surface = np.load(WORK / "candidate_surface.npy")

    # Discovery proxy (full footprint): candidate, incumbent, OOF-B thinned, selector-only union.
    incumbent = _dots_of(ROOT / REGISTRY_RASTERS["h27_4"])
    with np.load(ROOT / "evidence/oof/oof_B_19_plus_lidar_u16.npz") as z:
        oof_b = z["probability_u16"].astype(np.float32) / 65535.0
    with np.load(ROOT / "evidence/oof/oof_D_19_plus_lidar_radiometric_u16.npz") as z:
        oof_d = z["probability_u16"].astype(np.float32) / 65535.0
    oof_b_dots = emit_dots(np.where(footprint, oof_b, np.nan), footprint,
                           max_dots=int(round(int(footprint.sum()) * INCUMBENT_DENSITY)))

    def proxy(mask: np.ndarray) -> dict:
        f = metric.dti(mask.astype(np.float32), far_field)
        c = metric.dti(mask.astype(np.float32), catalogue)
        return {"dots": int(mask.sum()), "offcatalogue_DTI": f["DTI"], "offcatalogue_TPw": f["TPw"],
                "catalogue_DTI_full": c["DTI"]}

    proxies = {"candidate": proxy(dots), "incumbent_h27_4": proxy(incumbent),
               "oof_B_thinned": proxy(oof_b_dots),
               "selector_info_union_candidate_incumbent": proxy(dots | incumbent)}
    for name, row in proxies.items():
        log(f"proxy {name:<42} offcat {row['offcatalogue_DTI']:.4f} dots {row['dots']:,}")

    # Uniqueness: surface Spearman (seeded 1M-cell sample) + final-dot overlap vs registry.
    rng = np.random.default_rng(7)
    fp_r, fp_c = np.nonzero(footprint)
    pick = rng.choice(fp_r.size, size=1_000_000, replace=False)
    sr, sc = fp_r[pick], fp_c[pick]
    uniqueness = {
        "surface_spearman_vs_oof_B": float(spearmanr(surface[sr, sc], oof_b[sr, sc]).statistic),
        "surface_spearman_vs_oof_D": float(spearmanr(surface[sr, sc], oof_d[sr, sc]).statistic),
        "sample_cells": 1_000_000,
        "dots_vs_registry": {},
    }
    for name, rel in REGISTRY_RASTERS.items():
        reg = _dots_of(ROOT / rel)
        uniqueness["dots_vs_registry"][name] = {
            "within_3px_fraction": _within3_fraction(dots, reg),
            "exact_intersection": int((dots & reg).sum()),
            "binary_spearman_sample": float(
                spearmanr(dots[sr, sc].astype(np.float32), reg[sr, sc].astype(np.float32)).statistic),
        }
        log(f"uniqueness vs {name:<16} within3 {uniqueness['dots_vs_registry'][name]['within_3px_fraction']:.3f}")

    # Gates (preregistered).
    worst_auc = max((v["auc"] or 0.0) for k, v in canary["aucs"].items() if k in NEW_CHANNELS)
    cand_folds = screen["arms"]["candidate"]["per_fold"]
    base_folds = screen["arms"]["base_C1"]["per_fold"]
    fold_deltas = [c["DTI"] - b["DTI"] for c, b in zip(cand_folds, base_folds)]
    delta_ci = screen["bootstrap"]["paired_delta_ci95"]["candidate_minus_base_C1"]
    confirm_sign = None
    if confirm:
        confirm_sign = (confirm["arms"]["candidate"]["pooled_DTI"]
                        > confirm["arms"]["base_C1"]["pooled_DTI"])
    gates = {
        "canary_no_auc_above_0.90": bool(worst_auc <= 0.90),
        "holdout_beats_base_pooled": bool(
            screen["arms"]["candidate"]["pooled_DTI"] > screen["arms"]["base_C1"]["pooled_DTI"]),
        "holdout_paired_delta_ci_excludes_0": bool(delta_ci[0] > 0.0),
        "holdout_better_in_3_of_4_folds": bool(sum(d > 0 for d in fold_deltas) >= 3),
        "holdout_worst_fold_delta_ge_-0.010": bool(min(fold_deltas) >= -0.010),
        "confirmation_same_sign": bool(confirm_sign),
        "discovery_proxy_not_below_incumbent": bool(
            proxies["candidate"]["offcatalogue_DTI"] >= proxies["incumbent_h27_4"]["offcatalogue_DTI"]),
        "surface_spearman_le_0.90": bool(
            max(abs(uniqueness["surface_spearman_vs_oof_B"]),
                abs(uniqueness["surface_spearman_vs_oof_D"])) <= 0.90),
        "dots_within3_le_0.70_all_registry": bool(all(
            v["within_3px_fraction"] <= 0.70 for v in uniqueness["dots_vs_registry"].values())),
    }
    duplicate = not (gates["surface_spearman_le_0.90"] and gates["dots_within3_le_0.70_all_registry"])
    promote = bool(all(gates.values())) and not duplicate

    payload = {
        "schema_version": 1,
        "generated_utc": "2026-10-25",
        "experiment": "H31-E surface-expression (EXP-1/2/3)",
        "evaluator": ho.EVALUATOR_ID,
        "claim_class": "COMPUTED (HOLDOUT-DTI / proxy DTI on owner-mirror inputs); no organizer score",
        "canary": canary,
        "holdout_screen": screen,
        "holdout_confirm": confirm,
        "proxies_full_footprint": proxies,
        "uniqueness": uniqueness,
        "final": final,
        "gates": gates,
        "duplicate": duplicate,
        "verdict": "promote" if promote else "negative",
        "candidate_dots_sha256": hashlib.sha256(
            np.packbits(dots).tobytes()).hexdigest(),
    }
    out = ROOT / "evidence/h31e_results.json"
    out.write_text(json.dumps(payload, indent=1) + "\n")
    log(f"gates: {json.dumps(gates)}")
    log(f"VERDICT: {payload['verdict']} (duplicate={duplicate}) -> {out.relative_to(ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["channels", "canary", "holdout-screen",
                                          "holdout-confirm", "final", "report", "all"])
    args = parser.parse_args()
    WORK.mkdir(parents=True, exist_ok=True)
    if args.stage in ("channels", "all"):
        stage_channels()
    if args.stage in ("canary", "all"):
        stage_canary()
    if args.stage in ("holdout-screen", "all"):
        stage_holdout(SCREEN_SEED, "screen")
    if args.stage in ("holdout-confirm", "all"):
        stage_holdout(CONFIRM_SEED, "confirm")
    if args.stage in ("final", "all"):
        stage_final()
    if args.stage in ("report", "all"):
        stage_report()


if __name__ == "__main__":
    main()
