#!/usr/bin/env python3
"""PGR31 campaign runner (preregistered in knowledge/2026-10-26_pgr31_preregistration.md).

Stages: build -> exp1 (canary + screen draw 51) -> exp2 (confirmation draw 52, gated)
-> exp3 (final surface, registry gates, packaging). Reuses the unchanged shared template
evaluator/writer in vendor/gems57 and the in-repo spaced_dots emitter / validators.
No DrivenData contact; no slot is picked (selector step is separate).
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import subprocess
import sys
import time
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import spearmanr
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "vendor"), str(ROOT / "scripts")]

from gems57 import evaluate_holdout as shared_eval  # noqa: E402
from gems57.grid import Grid  # noqa: E402
from gems57.holdout import buffered_component_draw  # noqa: E402
from gems57.submission_writer import write_submission  # noqa: E402
from gemsdoe31.magrest import spaced_dots  # noqa: E402
from gemsdoe31.metric import dti as metric_dti  # noqa: E402
from gemsdoe31.pgr31_features import NOVEL_NAMES, build_novel_features, robust_z  # noqa: E402
from gemsdoe31.submission import sha256_file, validate_submission  # noqa: E402

EVIDENCE = ROOT / "evidence" / "pgr31"
CACHE = ROOT / ".cache"
DL = ROOT / "docs" / "downloads"
BUDGET = 37_654
BUFFER_PX = 213
BASE19 = [
    "mag_anom", "rtp", "tmi_hg", "geod_2ndinv", "iso_grav_anom_slope", "tc", "geod_shearrate",
    "geod_dilaterate", "tmi_vg", "deq_n100a15", "iso_grav_anom_vg", "det_elev", "iso_grav_anom",
    "tmi", "depth_to_base_surf", "ieq_n100a15", "cond_surf", "iso_grav_anom_hg", "det_elev_slope",
]
LIDAR11 = [
    "lidar_ex_max", "lidar_ex_mean", "lidar_step_max", "lidar_lapneg_max", "lidar_lappos_max",
    "lidar_downface_max", "lidar_upface_max", "lidar_cross_max", "lidar_relief", "lidar_coh100",
    "lidar_strike",
]
RAD8 = ["rad_K", "rad_Th", "rad_U", "rad_TC", "ext_ThK", "ext_UK", "ext_UTh", "ext_TMI_up150"]
NAMES = BASE19 + LIDAR11 + RAD8 + [f"pgr_{n}" for n in NOVEL_NAMES]
N_BASE = len(BASE19) + len(LIDAR11) + len(RAD8)  # 38
NF = len(NAMES)  # 47
NAME = "gemsdoe31-pgr31-poisson-pseudograv-37654-20261026"
CANDIDATE = "pgr31_candidate"
CONTROL = "base38_control"


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def save_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, sort_keys=True, default=_default) + "\n")


def _default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.bool_,)):
        return bool(o)
    raise TypeError(type(o).__name__)


def load_grid() -> tuple[Grid, np.ndarray, np.ndarray]:
    with rasterio.open(ROOT / "data/sample_submission.tif") as ds:
        fp = np.isfinite(ds.read(1))
        crs, transform = ds.crs, ds.transform
    with rasterio.open(ROOT / "data/labels.tif") as ds:
        cat = (ds.read(1) == 1) & fp
    return Grid(fp, cat, crs, transform, *fp.shape), fp, cat


def stack_path() -> Path:
    return CACHE / "pgr31_X.f32"


def open_stack(mode: str = "r") -> np.memmap:
    grid_shape = (3730, 3292)
    return np.memmap(stack_path(), dtype=np.float32, mode=mode, shape=(NF, *grid_shape))


# ---------------------------------------------------------------- build
def build() -> None:
    CACHE.mkdir(exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    grid, fp, _cat = load_grid()
    h, w = fp.shape
    mm = np.memmap(stack_path(), dtype=np.float32, mode="w+", shape=(NF, h, w))
    finite_inside = {}
    t0 = time.time()

    def read_band(path: Path, band: int) -> np.ndarray:
        with rasterio.open(path) as ds:
            return ds.read(band)

    for i, nm in enumerate(BASE19):
        raw = read_band(ROOT / "data/training_features.tif", i + 1).astype(np.float64)
        raw[~np.isfinite(raw) | (raw <= -1e30)] = np.nan
        raw[~fp] = np.nan
        z = robust_z(raw, fp)
        z[~fp] = np.nan
        mm[i] = z
        finite_inside[nm] = int(np.isfinite(z[fp]).sum())
        log(f"base19 {nm} finite={finite_inside[nm]}")
        del raw, z
    j = len(BASE19)
    for b, nm in enumerate(LIDAR11):  # lidar bands 1..11; band 12 'valid' excluded
        u = read_band(ROOT / "data/external/lidar_scarp_features_u8.tif", b + 1).astype(np.float32)
        arr = np.where((u > 0) & fp, u / 255.0, np.nan).astype(np.float32)
        mm[j] = arr
        finite_inside[nm] = int(np.isfinite(arr[fp]).sum())
        j += 1
        del u, arr
    log("lidar11 done (valid excluded)")
    rad_files = [(ROOT / "data/external/geodawn_rad_u8.tif", 4), (ROOT / "data/external/geodawn_extensions_u8.tif", 4)]
    k = 0
    for path, nb in rad_files:
        for b in range(nb):
            u = read_band(path, b + 1).astype(np.float32)
            arr = np.where((u > 0) & fp, u / 255.0, np.nan).astype(np.float32)
            mm[j] = arr
            finite_inside[RAD8[k]] = int(np.isfinite(arr[fp]).sum())
            j += 1
            k += 1
            del u, arr
    log("rad8 done")
    rtp_raw = read_band(ROOT / "data/training_features.tif", 2).astype(np.float32)
    rtp_raw[~np.isfinite(rtp_raw) | (rtp_raw <= -1e30)] = np.nan
    grav_raw = read_band(ROOT / "data/training_features.tif", 13).astype(np.float32)
    grav_raw[~np.isfinite(grav_raw) | (grav_raw <= -1e30)] = np.nan
    log("computing pseudo-gravity + local Poisson regression features ...")
    novel = build_novel_features(rtp_raw, grav_raw, fp)
    del rtp_raw, grav_raw
    for nm in NOVEL_NAMES:
        arr = novel[nm]
        mm[j] = arr
        finite_inside[f"pgr_{nm}"] = int(np.isfinite(arr[fp]).sum())
        j += 1
        log(f"novel pgr_{nm} finite={finite_inside[f'pgr_{nm}']}/{int(fp.sum())}")
    mm.flush()
    del mm, novel
    gc.collect()
    save_json(
        EVIDENCE / "stack.json",
        dict(
            names=NAMES,
            n_base=N_BASE,
            n_features=NF,
            shape=[NF, h, w],
            footprint_pixels=int(fp.sum()),
            catalogue_pixels=int(grid.catalogue.sum()),
            finite_inside_footprint=finite_inside,
            stack_file=str(stack_path().relative_to(ROOT)),
            stack_bytes=int(stack_path().stat().st_size),
            build_seconds=round(time.time() - t0, 1),
        ),
    )
    log("build done")


# ---------------------------------------------------------------- model helpers
def gather(mm: np.memmap, feat_idx: list[int], flat_idx: np.ndarray) -> np.ndarray:
    out = np.empty((len(flat_idx), len(feat_idx)), dtype=np.float32)
    for c, j in enumerate(feat_idx):
        out[:, c] = np.asarray(mm[j]).reshape(-1)[flat_idx]
    return out


def fit_model(mm, feat_idx, tr_flat, y, seed: int) -> HistGradientBoostingClassifier:
    model = HistGradientBoostingClassifier(
        max_iter=100,
        learning_rate=0.12,
        max_leaf_nodes=31,
        min_samples_leaf=50,
        l2_regularization=1.0,
        class_weight={0: 1, 1: 5},
        early_stopping=False,
        random_state=seed,
    )
    model.fit(gather(mm, feat_idx, tr_flat), y)
    return model


def predict_flat(mm, model, feat_idx, flat_idx: np.ndarray) -> np.ndarray:
    out = np.empty(len(flat_idx), dtype=np.float32)
    for s in range(0, len(flat_idx), 120_000):
        batch = flat_idx[s : s + 120_000]
        out[s : s + 120_000] = model.predict_proba(gather(mm, feat_idx, batch))[:, 1]
    return out


def score_prediction(pred: np.ndarray, fold: dict, grid: Grid, *, truth=None, known=None):
    """Crop adapter onto the unchanged shared evaluator (pattern from scripts/run_h31s.py)."""
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


# ---------------------------------------------------------------- canary
def run_canary(mm, folds, grid: Grid) -> dict:
    region = np.zeros(grid.shape, bool)
    truth = np.zeros(grid.shape, bool)
    for f in folds:
        region |= f["region"]
        truth |= f["truth"]
    pos_flat = np.flatnonzero((truth & region & grid.footprint).ravel())
    neg_pool = np.flatnonzero((region & grid.footprint & ~grid.catalogue).ravel())
    rng = np.random.default_rng(5151)
    neg_flat = rng.choice(neg_pool, min(200_000, len(neg_pool)), replace=False)
    sub = np.r_[pos_flat, neg_flat]
    y = np.r_[np.ones(len(pos_flat), np.uint8), np.zeros(len(neg_flat), np.uint8)]
    rows = []
    for idx, nm in enumerate(NOVEL_NAMES):
        vals = np.asarray(mm[N_BASE + idx]).reshape(-1)[sub]
        miss = ~np.isfinite(vals)
        m_auc = float(roc_auc_score(y, miss.astype(np.float32))) if miss.any() and not miss.all() else 0.5
        fin = ~miss
        if fin.sum() >= 20 and np.unique(y[fin]).size == 2 and float(np.std(vals[fin])) > 0:
            v_raw = float(roc_auc_score(y[fin], vals[fin]))
        else:
            v_raw = 0.5
        rows.append(
            dict(
                feature=f"pgr_{nm}",
                raw_auc=v_raw,
                value_auc_two_sided=max(v_raw, 1 - v_raw),
                missing_fraction=float(miss.mean()),
                missing_auc_two_sided=max(m_auc, 1 - m_auc),
                leakage_flag=bool(max(v_raw, 1 - v_raw, m_auc, 1 - m_auc) > 0.90),
            )
        )
        log(f"canary pgr_{nm}: two-sided AUC={rows[-1]['value_auc_two_sided']:.4f}")
    out = dict(
        stage="EXP-1 leakage canary (draw seed 51 withheld truth)",
        threshold=0.90,
        evaluated_positive_pixels=int(len(pos_flat)),
        evaluated_background_sample=int(len(neg_flat)),
        max_value_auc_two_sided=max(r["value_auc_two_sided"] for r in rows),
        max_missing_auc_two_sided=max(r["missing_auc_two_sided"] for r in rows),
        pass_=bool(all(not r["leakage_flag"] for r in rows)),
        features=rows,
    )
    save_json(EVIDENCE / "canary_seed51.json", out)
    return out


# ---------------------------------------------------------------- holdout draws
def run_draw(seed: int, *, with_canary: bool) -> dict:
    grid, fp, cat = load_grid()
    mm = open_stack("r")
    folds, quad = buffered_component_draw(
        grid, seed=seed, hide_frac=0.20, buffer_px=BUFFER_PX, boundary_px=BUFFER_PX
    )
    canary = None
    if with_canary:
        canary = run_canary(mm, folds, grid)
        if not canary["pass_"]:
            out = dict(seed=seed, leakage_stop=True, canary=canary)
            save_json(EVIDENCE / f"holdout_seed{seed}.json", out)
            raise SystemExit("LEAKAGE CANARY STOP: no holdout trust, no TIFF (see canary_seed51.json)")
    with rasterio.open(ROOT / "data/external/derived_sgmc_faults_100m_u8.tif") as ds:
        sgmc = (ds.read(1) == 1) & fp
    d_cat = distance_transform_edt(~cat)
    proxy_truth = sgmc & (d_cat > 3.0)
    arms = {CONTROL: list(range(N_BASE)), CANDIDATE: list(range(NF))}
    terms: dict[str, np.ndarray | None] = {a: None for a in arms}
    proxy_terms: dict[str, np.ndarray | None] = {a: None for a in arms}
    fold_rows = []
    for fold in folds:
        q = int(fold["fold"])
        t0 = time.time()
        allowed = fp & fold["region"] & ~fold["masked_known"] & (distance_transform_edt(~fold["masked_known"]) > 2.0)
        budget = int(round(BUDGET * int((fp & fold["region"]).sum()) / int(fp.sum())))
        separated = distance_transform_edt(quad != q) > BUFFER_PX
        train = fp & (quad != q) & separated & ~fold["hidden_all"]
        pos_flat = np.flatnonzero((train & fold["visible"]).ravel())
        neg_pool = np.flatnonzero((train & ~cat & (d_cat > 3.0)).ravel())
        rng = np.random.default_rng(51_000 + 100 * seed + q)
        neg_flat = rng.choice(neg_pool, min(120_000, len(neg_pool)), replace=False)
        tr_flat = np.r_[pos_flat, neg_flat]
        y = np.r_[np.ones(len(pos_flat), np.uint8), np.zeros(len(neg_flat), np.uint8)]
        target_flat = np.flatnonzero((fp & (quad == q)).ravel())
        per_fold = {}
        for arm, feat_idx in arms.items():
            model = fit_model(mm, feat_idx, tr_flat, y, seed=31 + q)
            surf = np.zeros(fp.shape, np.float32)
            surf.reshape(-1)[target_flat] = predict_flat(mm, model, feat_idx, target_flat)
            dots = spaced_dots(surf, allowed, budget)
            pred = dots.astype(np.float32)
            sc, t = score_prediction(pred, fold, grid)
            _psc, pt = score_prediction(pred, fold, grid, truth=proxy_truth, known=cat)
            terms[arm] = t.copy() if terms[arm] is None else terms[arm] + t
            proxy_terms[arm] = pt.copy() if proxy_terms[arm] is None else proxy_terms[arm] + pt
            per_fold[arm] = dict(dti=float(sc["dti"]), n_emitted=int(sc["n_emitted"]), n_truth=int(sc["n_truth"]))
            del model, surf, dots, pred
        gc.collect()
        log(
            f"seed{seed} {fold['name']} ({time.time()-t0:.0f}s) budget={budget} train_pos={len(pos_flat)} | "
            + " | ".join(f"{a}={per_fold[a]['dti']:.4f}" for a in arms)
        )
        fold_rows.append(
            dict(fold=fold["name"], budget=budget, receipt=fold["receipt"], arms=per_fold,
                 train_positives=int(len(pos_flat)), train_negatives=int(len(neg_flat)))
        )
    summary = shared_eval.pooled_summary(
        {a: terms[a] for a in arms}, draws=1000, seed=310_051 + seed, candidate=CANDIDATE
    )
    proxy = shared_eval.pooled_summary(
        {a: proxy_terms[a] for a in arms}, draws=1000, seed=310_051 + seed, candidate=CANDIDATE
    )
    proxy["instrument"] = "SGMC-PROXY (off-catalogue >300m); never training truth; NOT hidden competition truth"
    delta = summary["paired_differences"][CONTROL]
    proxy_delta = proxy["paired_differences"][CONTROL]["delta"]
    wins = sum(r["arms"][CANDIDATE]["dti"] > r["arms"][CONTROL]["dti"] for r in fold_rows)
    worst = min(r["arms"][CANDIDATE]["dti"] - r["arms"][CONTROL]["dti"] for r in fold_rows)
    screen_pass = bool(
        delta["delta"] > 0.002 and delta["ci95"][0] > 0 and wins >= 3 and worst >= -0.010 and proxy_delta > 0
    )
    out = dict(
        seed=seed,
        buffer_px=BUFFER_PX,
        evaluator_version=shared_eval.VERSION,
        evidence_class="HOLDOUT-DTI",
        canary=canary,
        holdout=summary,
        sgmc_proxy=proxy,
        folds=fold_rows,
        screen=dict(
            delta_vs_control=float(delta["delta"]),
            delta_ci95=[float(x) for x in delta["ci95"]],
            quadrant_wins=int(wins),
            worst_quadrant_delta=float(worst),
            sgmc_proxy_delta=float(proxy_delta),
            passed=screen_pass,
        ),
    )
    save_json(EVIDENCE / f"holdout_seed{seed}.json", out)
    log(
        f"seed{seed} pooled candidate={summary['scores'][CANDIDATE]['dti']:.5f} "
        f"control={summary['scores'][CONTROL]['dti']:.5f} delta={delta['delta']:+.5f} "
        f"CI={delta['ci95']} wins={wins}/4 sgmc_delta={proxy_delta:+.5f} pass={screen_pass}"
    )
    return out


# ---------------------------------------------------------------- final (EXP-3)
def registry_files() -> list[Path]:
    files = [p for p in sorted(DL.rglob("*.tif")) if NAME not in p.name]
    prior = ROOT / "data" / "prior_audit"
    if prior.is_dir():
        files += sorted(prior.rglob("*.tif"))
    return files


def exp3() -> dict:
    grid, fp, cat = load_grid()
    mm = open_stack("r")
    # Final full-footprint candidate fit (frozen recipe; all catalogue positives).
    d_cat = distance_transform_edt(~cat)
    pos_flat = np.flatnonzero(cat.ravel())
    neg_pool = np.flatnonzero((fp & ~cat & (d_cat > 3.0)).ravel())
    rng = np.random.default_rng(51_099)
    neg_flat = rng.choice(neg_pool, min(200_000, len(neg_pool)), replace=False)
    tr_flat = np.r_[pos_flat, neg_flat]
    y = np.r_[np.ones(len(pos_flat), np.uint8), np.zeros(len(neg_flat), np.uint8)]
    log(f"final fit: pos={len(pos_flat)} neg={len(neg_flat)} feats={NF}")
    model = fit_model(mm, list(range(NF)), tr_flat, y, seed=31)
    fp_flat = np.flatnonzero(fp.ravel())
    surf = np.zeros(fp.shape, np.float32)
    surf.reshape(-1)[fp_flat] = predict_flat(mm, model, list(range(NF)), fp_flat)
    del model
    CACHE.mkdir(exist_ok=True)
    np.save(CACHE / "pgr31_surface.npy", surf)
    surface_sha = hashlib.sha256(surf.tobytes()).hexdigest()
    log(f"final surface sha256={surface_sha}")

    # Registry (learning/uniqueness only): local downloads + fetched nine-focus bests.
    fetch = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "fetch_peer_rasters.py")],
        capture_output=True, text=True, timeout=1200,
    )
    log(f"peer fetch rc={fetch.returncode}")
    regs = registry_files()
    sample_rng = np.random.default_rng(31)
    sample = sample_rng.choice(fp_flat, 200_000, replace=False)
    surf_sample = surf.reshape(-1)[sample]
    rows = []
    reg_paths: list[Path] = []
    for p in regs:
        with rasterio.open(p) as ds:
            a = ds.read(1)
        if a.shape != fp.shape:
            continue
        av = np.where(np.isfinite(a), a, 0.0)
        dots_reg = (av > 0) & fp
        rho_s = float(spearmanr(surf_sample, av.reshape(-1)[sample]).statistic)
        rows.append(dict(file=str(p.relative_to(ROOT)), dots=int(dots_reg.sum()), surface_spearman=rho_s))
        reg_paths.append(p)
        del a, av, dots_reg
    max_rho_s = max((abs(r["surface_spearman"]) for r in rows), default=0.0)
    surface_gate = dict(scope=f"{len(rows)} registry rasters (local docs/downloads + fetched nine-focus bests)",
                        max_abs_surface_spearman=float(max_rho_s), threshold_rho=0.90,
                        pass_=bool(max_rho_s <= 0.90), rows=rows,
                        peer_fetch_returncode=int(fetch.returncode))
    save_json(EVIDENCE / "registry_surface.json", surface_gate)
    log(f"surface gate max|rho|={max_rho_s:.4f} pass={surface_gate['pass_']}")
    if not surface_gate["pass_"]:
        card = _run_card(surface_sha, None, surface_gate, None, verdict="negative",
                         stop="DUPLICATE STOP at pre-placement surface gate; no TIFF packaged")
        save_json(EVIDENCE / "run_card.json", card)
        raise SystemExit("DUPLICATE STOP (surface): no TIFF packaged")

    allowed = fp & (d_cat > 2.0)
    dots = spaced_dots(surf, allowed, BUDGET)
    n_dots = int(dots.sum())
    log(f"emitted dots={n_dots}")
    dots_sample = dots.reshape(-1)[sample].astype(np.float32)
    for r, p in zip(rows, reg_paths):
        with rasterio.open(p) as ds:
            a = ds.read(1)
        av = np.where(np.isfinite(a), a, 0.0)
        reg = (av > 0) & fp
        if not reg.any():
            r["final_3px_overlap"] = 0.0
        else:
            dist = distance_transform_edt(~reg)
            r["final_3px_overlap"] = float((dist[dots] <= 3).mean()) if n_dots else 0.0
            del dist
        r["final_spearman"] = float(spearmanr(dots_sample, av.reshape(-1)[sample]).statistic)
        del a, av, reg
    max_ov = max((r["final_3px_overlap"] for r in rows), default=0.0)
    worst_ov_file = max(rows, key=lambda r: r["final_3px_overlap"])["file"] if rows else None
    max_rho_d = max((abs(r["final_spearman"]) for r in rows), default=0.0)
    final_gate = dict(max_final_3px_overlap=float(max_ov), worst_overlap_file=worst_ov_file,
                      max_abs_final_spearman=float(max_rho_d), threshold_overlap=0.70, threshold_rho=0.90,
                      pass_=bool(max_ov <= 0.70 and max_rho_d <= 0.90), rows=rows)
    save_json(EVIDENCE / "registry_final.json", final_gate)
    log(f"final gate max_overlap={max_ov:.4f} ({worst_ov_file}) max|rho|={max_rho_d:.4f} pass={final_gate['pass_']}")
    if not final_gate["pass_"]:
        card = _run_card(surface_sha, None, surface_gate, final_gate, verdict="negative",
                         stop="DUPLICATE STOP at final-dots gate; no TIFF packaged")
        save_json(EVIDENCE / "run_card.json", card)
        raise SystemExit("DUPLICATE STOP (final dots): no TIFF packaged")

    # Verdict from frozen screens (draws 51 + 52 must both pass for promote).
    h51 = _load(EVIDENCE / "holdout_seed51.json")
    h52 = _load(EVIDENCE / "holdout_seed52.json")
    canary_ok = bool(h51 and h51.get("canary") and h51["canary"]["pass_"])
    promote = bool(
        canary_ok
        and h51 and h51["screen"]["passed"]
        and h52 and h52["screen"]["passed"]
    )
    verdict = "promote" if promote else "negative"
    d51 = h51["holdout"]["scores"][CANDIDATE]["dti"] if h51 else float("nan")
    c51 = h51["holdout"]["scores"][CONTROL]["dti"] if h51 else float("nan")
    status = "selector-eligible" if promote else "research-only DO NOT SUBMIT"
    note = f"PGR31 Poisson pseudo-grav discordance {n_dots}d | HOLDOUT-DTI s51 {d51:.4f} vs {c51:.4f} | {status}"[:140]

    pred = np.where(dots, 1.0, 0.0).astype(np.float32)
    zeros_path = DL / f"{NAME}-zeros.tif"
    write_submission(
        zeros_path, pred, ROOT / "data/sample_submission.tif", fp,
        note=note, name=NAME, catalogue=cat,
        metadata=dict(lane="PGR31", verdict=verdict, experiments="EXP-1..3 of 3"),
    )
    log(f"wrote {zeros_path.name} via shared submission_writer")
    nan_path = DL / f"{NAME}-nan.tif"
    with rasterio.open(ROOT / "data/sample_submission.tif") as ds:
        prof = ds.profile.copy()
    prof.update(dtype="float32", count=1, nodata=float("nan"))
    with rasterio.open(nan_path, "w", **prof) as ds:
        ds.write(np.where(fp, pred, np.nan).astype(np.float32), 1)
    with zipfile.ZipFile(nan_path.with_suffix(".zip"), "w", zipfile.ZIP_DEFLATED) as z:
        z.write(nan_path, nan_path.name)

    val_zeros = validate_submission(zeros_path, ROOT / "data/sample_submission.tif", convention="all-finite")
    val_nan = validate_submission(nan_path, ROOT / "data/sample_submission.tif", convention="nan-outside")
    save_json(DL / f"{NAME}-format-check.json", dict(all_finite=val_zeros, nan_outside=val_nan))

    with rasterio.open(ROOT / "data/external/derived_sgmc_faults_100m_u8.tif") as ds:
        sgmc = (ds.read(1) == 1) & fp
    proxy_truth = sgmc & (d_cat > 3.0)
    sgmc_full = metric_dti(pred, proxy_truth)
    facts = dict(
        dots=n_dots,
        dots_on_catalogue=int((dots & cat).sum()),
        dots_within_2px_catalogue=int((dots & (d_cat <= 2.0)).sum()),
        zeros=dict(file=zeros_path.name, sha256=sha256_file(zeros_path), bytes=int(zeros_path.stat().st_size)),
        nan=dict(file=nan_path.name, sha256=sha256_file(nan_path), bytes=int(nan_path.stat().st_size)),
        validator_all_finite_hard_failures=val_zeros.get("hard_failures"),
        validator_nan_hard_failures=val_nan.get("hard_failures"),
        sgmc_full_footprint_proxy=dict(
            evidence_class="SGMC-PROXY-DTI (full footprint, off-catalogue >300m; NOT holdout, NOT a competition score)",
            dti=float(sgmc_full["DTI"]), truth_pixels=int(proxy_truth.sum()),
        ),
        note=note,
        verdict=verdict,
    )
    card = _run_card(surface_sha, facts, surface_gate, final_gate, verdict=verdict, stop=None)
    save_json(EVIDENCE / "run_card.json", card)
    save_json(DL / f"{NAME}-run-card.json", card)
    log(f"EXP-3 done verdict={verdict} sha256={facts['zeros']['sha256']}")
    return card


def _load(path: Path):
    return json.loads(path.read_text()) if path.is_file() else None


def _holdout_block(seed: int):
    h = _load(EVIDENCE / f"holdout_seed{seed}.json")
    if not h or h.get("leakage_stop"):
        return None
    s = h["holdout"]
    return dict(
        evidence_class="HOLDOUT-DTI",
        evaluator_version=s["evaluator_version"],
        draw_seed=seed,
        candidate=s["scores"][CANDIDATE],
        control=s["scores"][CONTROL],
        paired_difference=s["paired_differences"][CONTROL],
        sgmc_proxy_candidate=h["sgmc_proxy"]["scores"][CANDIDATE],
        screen=h["screen"],
    )


def _run_card(surface_sha, facts, surface_gate, final_gate, *, verdict, stop) -> dict:
    canary = _load(EVIDENCE / "canary_seed51.json")
    return dict(
        hypothesis=(
            "PGR31: Poisson pseudo-gravity discordance - a buried fault juxtaposing basement blocks with "
            "different magnetization-to-density ratios steps the local regression of Baranov pseudo-gravity "
            "(vertical integral of RTP) on observed isostatic gravity, revealing catalogue-missing faults "
            "with no surface scarp"
        ),
        mechanism=(
            "38-feature base stack (19 competition + 11 LiDAR [valid excluded] + 8 GeoDAWN radiometric) + 9 "
            "label-free pseudo-gravity/local-Poisson features; HGB; 2.8px score-ordered spaced dots; "
            "37,654-dot budget; >2px catalogue exclusion at emission only; zero incumbent dots copied"
        ),
        named_non_fault_process=(
            "Unfaulted pluton margins / caldera ring contacts (magnetization-to-density ratio change without "
            "brittle offset); GeoDAWN survey-block levelling seams"
        ),
        leakage_canary=canary,
        holdout_dti=dict(screen_seed51=_holdout_block(51), confirmation_seed52=_holdout_block(52),
                         note="HOLDOUT-DTI is a local hide-and-recover proxy, never a competition score"),
        correlation_overlap_vs_registry=dict(
            scope=(surface_gate or {}).get("scope"),
            max_abs_surface_spearman=(surface_gate or {}).get("max_abs_surface_spearman"),
            max_final_3px_overlap=(final_gate or {}).get("max_final_3px_overlap"),
            worst_overlap_file=(final_gate or {}).get("worst_overlap_file"),
            max_abs_final_spearman=(final_gate or {}).get("max_abs_final_spearman"),
            pass_=bool((surface_gate or {}).get("pass_") and (final_gate or {}).get("pass_")),
            calibration_lattice_disclosure=(
                "The shared 695-raster registry also contains a spacing-5 calibration lattice (non-submission "
                "control) whose support lies within 3px of essentially every interior cell, so the literal "
                "70% rule against ALL registry entries is degenerate for any non-empty candidate "
                "(evidence/tgj31/registry_universal_blocker.json). It is reported here, not silently exempted; "
                "the lane gate above is scoped to genuine submission rasters. No global uniqueness is claimed."
            ),
        ),
        surface_sha256=surface_sha,
        raster_sha256=(facts or {}).get("zeros", {}).get("sha256"),
        raster_sha256_nan_twin=(facts or {}).get("nan", {}).get("sha256"),
        validator_output=dict(
            all_finite_hard_failures=(facts or {}).get("validator_all_finite_hard_failures"),
            nan_outside_hard_failures=(facts or {}).get("validator_nan_hard_failures"),
            grid="EPSG:32611, 3730x3292, Affine(100,0,243350,0,-100,4508550), single float32 band",
            footprint_values="finite in [0,1] (binary {0,1} dots); all-finite file has 0 NaN anywhere",
            organizer_acceptance_verified=False,
        ),
        submission_name=NAME,
        note=(facts or {}).get("note"),
        facts=facts,
        verdict=verdict,
        stop=stop,
        ok_to_download_for_research=bool(facts),
        eligible_for_selector=bool(verdict == "promote"),
        ok_to_submit=False,
        submit_explanation=(
            "Promotion to a weekly slot is a separate selector step (protocol rule 6); this card never picks a "
            "slot. eligible_for_selector=true only if verdict=promote (canary + both registry gates + screen "
            "passed on draws 51 AND 52)."
        ),
        organizer_confirmed_score=None,
        experiments_used="EXP-1 canary+screen (51), EXP-2 confirmation (52, gated), EXP-3 final+package; max 3",
        preregistration="knowledge/2026-10-26_pgr31_preregistration.md",
        preregistration_sha256="a161635faadb95eefd301e1058c688f0da6e00a961893abf8dacf622380a7ae1",
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("stage", choices=("build", "exp1", "exp2", "exp3"))
    args = ap.parse_args()
    if args.stage == "build":
        build()
    elif args.stage == "exp1":
        run_draw(51, with_canary=True)
    elif args.stage == "exp2":
        h51 = _load(EVIDENCE / "holdout_seed51.json")
        if not (h51 and h51.get("screen", {}).get("passed")):
            raise SystemExit("EXP-2 gated off: EXP-1 screen did not pass (no burned-draw tuning)")
        run_draw(52, with_canary=False)
    elif args.stage == "exp3":
        exp3()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
