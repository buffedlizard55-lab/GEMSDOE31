#!/usr/bin/env python3
"""H31-Y lane runner: regime-mosaic dual-specialist emission.

Frozen by knowledge/2026-10-26_h31y_preregistration.md BEFORE any fitting.
Reuses the shared template unchanged (vendor/gems57: spatial.folds,
evaluate_holdout = gems57-pooled-hide-v2, metric, uniqueness, submission_writer),
the H31-U helpers (grid loading, cleaning, ranking, Poisson emission, peer audit,
SGMC scoring) and the H31-X junction-line function (method reused for learning;
no H31-X dots/surfaces enter the candidate).

Implementation constants frozen in this header (before first run):
- regime boundary: smoothed det_elev_slope (gaussian sigma=1.5px of the cleaned
  band) > 6 deg = mountain, <= 6 deg = piedmont.
- FAN piedmont window on the same smoothed slope: 0 below 0.1 deg, rising to 1 at
  0.5 deg, full 0.5-6 deg, falling to 0 at 10 deg.
- FAN components are footprint percentile ranks over LiDAR-valid pixels only
  (rank01 with foot=lidar_ok), zero where LiDAR invalid; FAN_filled substitutes
  the JUNC rank where LiDAR is invalid (frozen fallback in the preregistration).
- Y3 mosaic: mountain budget = BUDGET//2 emitted first from JUNC inside the
  mountain regime; piedmont budget = remainder emitted from FAN_filled inside
  the piedmont regime with the 2.8px neighbourhoods of mountain dots blocked
  (distance to mountain dots >= 2.8px), so global min spacing holds.
- mosaic ranking field for Spearman audits: where(mountain, JUNC, FAN_filled).
Stages: lines, canary, exp1, exp2, exp3, package. DrivenData is never contacted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt, gaussian_filter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))

import run_h31u as U  # noqa: E402
import run_h31x as X  # noqa: E402  (junction_line only)
from gems57 import evaluate_holdout as ev  # noqa: E402
from gems57 import metric as vmetric  # noqa: E402
from gems57 import spatial, submission_writer  # noqa: E402
from gemsdoe31.submodular_emit import poisson_disk_emit  # noqa: E402
from gemsdoe31.submission import validate_submission  # noqa: E402

SHAPE = (3730, 3292)
BUDGET = 37_654
MIN_DIST = 2.8
B_PX = 2.0
LANE = "H31-Y"
CANDIDATE = "Y3"
CACHE = ROOT / "data" / "h31y"
EVID = ROOT / "evidence" / "h31y"
PREREG = "knowledge/2026-10-26_h31y_preregistration.md"
LINES = ["JUNC", "FAN", "FAN_G", "CTRL", "SLOPE"]
ARMS = ["Y1", "Y2", "Y3", "Y4", "CTRL", "SLOPE"]
CONFIRM_SEED = 3104
REGIME_SLOPE_DEG = 6.0
log = U.log
sha256_file = U.sha256_file


# ---------------------------------------------------------------- lines
def fan_window(s: np.ndarray) -> np.ndarray:
    w = np.zeros(s.shape, np.float32)
    rise = (s > 0.1) & (s < 0.5)
    w[rise] = (s[rise] - 0.1) / 0.4
    w[(s >= 0.5) & (s <= 6.0)] = 1.0
    fall = (s > 6.0) & (s < 10.0)
    w[fall] = (10.0 - s[fall]) / 4.0
    return w


def fan_line(foot: np.ndarray, lidar_ok: np.ndarray, *, window: bool) -> np.ndarray:
    """Geomean of LiDAR-valid ranks: step, one-sided dipole, coherence, relief-inverse."""

    def rvalid(raw: np.ndarray) -> np.ndarray:
        r = U.rank01(np.where(np.isfinite(raw), raw, 0).astype(np.float32), lidar_ok)
        return np.where(lidar_ok, r, 0.0).astype(np.float32)

    up = U.stack_band("upface_max", foot)
    down = U.stack_band("downface_max", foot)
    dipole = np.abs(np.where(np.isfinite(up), up, 0) - np.where(np.isfinite(down), down, 0))
    relief = U.stack_band("relief", foot)
    parts = [
        rvalid(U.stack_band("step_max", foot)),
        rvalid(dipole.astype(np.float32)),
        rvalid(U.stack_band("coh100", foot)),
        np.where(lidar_ok, 1.0 - rvalid(relief), 0.0).astype(np.float32),
    ]
    g = U.geomean_rank(parts)
    g = np.where(lidar_ok, g, 0.0).astype(np.float32)
    if window:
        s = U.clean(U.stack_band("det_elev_slope", foot), foot)
        ss = gaussian_filter(s, 1.5, mode="nearest")
        g = (g * fan_window(ss)).astype(np.float32)
    g[~foot] = 0.0
    return g


def build_lines() -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    EVID.mkdir(parents=True, exist_ok=True)
    foot, cat, *_ = U.load_grid()
    mm = np.memmap(CACHE / "lines.f32", dtype=np.float32, mode="w+", shape=(len(LINES),) + SHAPE)
    t0 = time.time()
    z = U.clean(U.stack_band("det_elev", foot), foot)
    s = U.clean(U.stack_band("det_elev_slope", foot), foot)
    j = X.junction_line(z, s, foot, nms=False)  # H31-X EXP-2 kept raw (no NMS)
    mm[LINES.index("JUNC")] = U.rank01(j, foot)
    log("JUNC done", round(time.time() - t0))
    valid = U.stack_band("valid", foot)
    lidar_ok = foot & np.isfinite(valid) & (valid > 0)
    mm[LINES.index("FAN")] = fan_line(foot, lidar_ok, window=True)
    mm[LINES.index("FAN_G")] = fan_line(foot, lidar_ok, window=False)
    log("FAN done", round(time.time() - t0), "lidar_ok", int(lidar_ok.sum()))
    mm[LINES.index("CTRL")] = U.rank01(U.clean(U.stack_band("tmi_hg", foot), foot), foot)
    mm[LINES.index("SLOPE")] = U.rank01(s, foot)
    mm.flush()
    # regime masks (label-free)
    ss = gaussian_filter(s, 1.5, mode="nearest")
    mountain = foot & (ss > REGIME_SLOPE_DEG)
    np.save(CACHE / "mountain.npy", mountain)
    np.save(CACHE / "lidar_ok.npy", lidar_ok)
    receipts = {}
    for i, n in enumerate(LINES):
        a = np.asarray(mm[i])[foot]
        receipts[n] = dict(min=float(a.min()), max=float(a.max()), mean=float(a.mean()),
                           frac_zero=float((a == 0).mean()))
    meta = dict(lane=LANE, lines=LINES, shape=list(SHAPE), receipts=receipts,
                mountain_px=int(mountain.sum()), piedmont_px=int((foot & ~mountain).sum()),
                lidar_ok_px=int(lidar_ok.sum()),
                note="label-free lines; JUNC re-derived by H31-X junction_line(nms=False)")
    (CACHE / "lines.json").write_text(json.dumps(meta, indent=1) + "\n")
    (EVID / "lines.json").write_text(json.dumps(meta, indent=1) + "\n")
    log("lines written", round(time.time() - t0), "s")
    return meta


def load_line(name: str) -> np.ndarray:
    mm = np.memmap(CACHE / "lines.f32", dtype=np.float32, mode="r", shape=(len(LINES),) + SHAPE)
    return np.asarray(mm[LINES.index(name)], dtype=np.float32).copy()


def fan_filled(foot) -> np.ndarray:
    lidar_ok = np.load(CACHE / "lidar_ok.npy")
    out = np.where(lidar_ok, load_line("FAN"), load_line("JUNC")).astype(np.float32)
    out[~foot] = 0.0
    return out


def surface(arm: str, foot) -> np.ndarray:
    if arm == "Y1":
        return load_line("FAN")
    if arm == "Y2":
        return load_line("JUNC")
    if arm == "Y4":
        lidar_ok = np.load(CACHE / "lidar_ok.npy")
        fg = np.where(lidar_ok, load_line("FAN_G"), load_line("JUNC")).astype(np.float32)
        return np.sqrt(np.maximum(load_line("JUNC"), 1e-6) * np.maximum(fg, 1e-6)).astype(np.float32)
    if arm == "Y3":  # mosaic ranking field (for audits/canary; emission is arm-specific)
        mountain = np.load(CACHE / "mountain.npy")
        return np.where(mountain, load_line("JUNC"), fan_filled(foot)).astype(np.float32)
    return load_line(arm)  # CTRL / SLOPE


def mosaic_emit(allowed: np.ndarray, foot, n: int = BUDGET) -> np.ndarray:
    mountain = np.load(CACHE / "mountain.npy")
    piedmont = foot & ~mountain
    n_m = n // 2
    dots_m = poisson_disk_emit(load_line("JUNC"), allowed & mountain, n_m,
                               min_dist_px=MIN_DIST, max_pool=400_000)
    near_m = distance_transform_edt(~dots_m) < MIN_DIST
    ff = fan_filled(foot)
    dots_p = poisson_disk_emit(ff, allowed & piedmont & ~near_m, n - int(dots_m.sum()),
                               min_dist_px=MIN_DIST, max_pool=400_000)
    dots = dots_m | dots_p
    if int(dots.sum()) < n:  # preregistered fallback: fill from mosaic field outside both dot sets
        near = distance_transform_edt(~dots) < MIN_DIST if dots.any() else np.zeros_like(dots)
        extra = poisson_disk_emit(surface("Y3", foot), allowed & ~near & ~dots, n - int(dots.sum()),
                                  min_dist_px=MIN_DIST, max_pool=400_000)
        dots |= extra
    return dots


def emit_arm(arm: str, allowed: np.ndarray, foot) -> np.ndarray:
    if arm == "Y3":
        return mosaic_emit(allowed, foot)
    surf = surface(arm, foot)
    return U.emit_dots(surf, allowed & (surf > 0))


# ---------------------------------------------------------------- holdout
def score(arms: list[str], folds: list, foot, *, truth_regime: str | None = None) -> dict:
    """Per-fold visible-B2 emission scored with the shared evaluator.

    truth_regime None/'piedmont'/'mountain': optionally restrict withheld truth to
    pixels whose smoothed slope is in that regime (dots/FP bookkeeping unchanged),
    measuring how much of each arm's budget earns credit on that truth subset.
    """
    mountain = np.load(CACHE / "mountain.npy")
    terms: dict[str, np.ndarray] = {}
    per_fold: dict[str, list] = {a: [] for a in arms}
    for f in folds:
        f_use = dict(f)
        if truth_regime == "piedmont":
            f_use["truth"] = f["truth"] & ~mountain
        elif truth_regime == "mountain":
            f_use["truth"] = f["truth"] & mountain
        d_vis = distance_transform_edt(~f["visible"])
        allowed = foot & (d_vis > B_PX)
        for arm in arms:
            dots = emit_arm(arm, allowed, foot)
            res, trm = ev.evaluate(dots.astype(np.float32), f_use, foot)
            terms[arm] = trm if arm not in terms else terms[arm] + trm
            per_fold[arm].append(dict(fold=int(f["fold"]),
                                      dti=float(vmetric.dti_from_components(
                                          res["tpw"], res["fpw"], res["fnw"])),
                                      n_truth=int(res["n_truth"]),
                                      emitted_active=int(res["n_emitted"])))
            log(" fold", f["fold"], truth_regime or "all", arm,
                "dti", round(per_fold[arm][-1]["dti"], 4), "truth", res["n_truth"])
    return dict(terms=terms, per_fold=per_fold)


def random_component_split(cat, foot, seed: int) -> dict:
    return X.random_component_split(cat, foot, seed)


# ---------------------------------------------------------------- stages
def run_canary() -> dict:
    foot, cat, sgmc, off_sgmc, _ = U.load_grid()
    mountain = np.load(CACHE / "mountain.npy")
    piedmont = foot & ~mountain
    rows = []
    feats = [(n, load_line(n)) for n in LINES] + [(a, surface(a, foot)) for a in ("Y1", "Y3", "Y4")]
    for name, v in feats:
        a_cat = U.auc_for(v, cat, foot)
        a_off = U.auc_for(v, off_sgmc, foot)
        a_cat_p = U.auc_for(v, cat & piedmont, piedmont)
        worst = max(a_cat, a_off, a_cat_p, 1 - a_cat, 1 - a_off, 1 - a_cat_p)
        rows.append(dict(feature=name, auc_catalogue=a_cat, auc_off_sgmc=a_off,
                         auc_catalogue_piedmont=a_cat_p, leakage_flagged=bool(worst > 0.90)))
        log("canary", name, round(a_cat, 4), round(a_off, 4), round(a_cat_p, 4))
    rep = dict(lane=LANE, evidence_class="COMPUTED", auc_ceiling=0.90, rows=rows,
               all_pass=bool(all(not r["leakage_flagged"] for r in rows)))
    EVID.mkdir(parents=True, exist_ok=True)
    (EVID / "canary.json").write_text(json.dumps(rep, indent=1) + "\n")
    return rep


def run_exp1() -> dict:
    foot, cat, *_ = U.load_grid()
    folds = list(spatial.folds(cat, foot, buffer_px=213))
    receipts = [f["receipt"] for f in folds]
    log("folds buffer 213", [r["truth_px"] for r in receipts])
    out = score(ARMS, folds, foot)
    summ = U.pooled(out["terms"], candidate=CANDIDATE)
    sub_p = score(["Y2", "Y3"], folds, foot, truth_regime="piedmont")
    summ_p = U.pooled(sub_p["terms"], candidate="Y3")
    sub_m = score(["Y2", "Y3"], folds, foot, truth_regime="mountain")
    summ_m = U.pooled(sub_m["terms"], candidate="Y3")
    rep = dict(lane=LANE, experiment="EXP-1 screen", evaluator_version=ev.VERSION, buffer_px=213,
               fold_receipts=receipts, per_fold=out["per_fold"], pooled=summ,
               subgroup_piedmont=dict(per_fold=sub_p["per_fold"], pooled=summ_p),
               subgroup_mountain=dict(per_fold=sub_m["per_fold"], pooled=summ_m),
               note="Candidate is frozen as Y3 in the preregistration; no arm substitution.")
    (EVID / "exp1_screen.json").write_text(json.dumps(rep, indent=1, default=float) + "\n")
    for a in summ["scores"]:
        log("EXP1 pooled", a, round(summ["scores"][a]["dti"], 4), summ["scores"][a]["ci95"])
    return rep


def run_exp2() -> dict:
    foot, cat, sgmc, off_sgmc, d_cat = U.load_grid()
    allowed = foot & (d_cat > B_PX)
    dots = mosaic_emit(allowed, foot)
    log("final dots", int(dots.sum()), "on_cat", int((dots & cat).sum()))
    np.save(CACHE / "final_dots.npy", dots)
    surf = surface("Y3", foot)
    np.save(CACHE / "final_surface.npy", surf)
    rep = dict(lane=LANE, experiment="EXP-2 final emission + uniqueness",
               final_dots=int(dots.sum()), dots_on_catalogue=int((dots & cat).sum()))
    rep["uniqueness"] = U.uniqueness_audit(surf, dots, foot)
    rep["literal_witness"] = U.literal_witness(dots, foot)
    (EVID / "exp2.json").write_text(json.dumps(rep, indent=1, default=float) + "\n")
    u = rep["uniqueness"]
    log("EXP2 discrete max overlap", u["discrete_max_final_overlap"],
        "max|rho| surf", u["max_abs_surface_spearman"], "dots", u["max_abs_dots_spearman"])
    return rep


def regime_sgmc(dots, off_sgmc, foot, mountain) -> dict:
    out = {}

    def one(reg, name):
        r = vmetric.dti_exact((dots & reg).astype(np.float32), off_sgmc & reg, valid=reg)
        return dict(dti=float(r["dti"]), n_truth=int((off_sgmc & reg).sum()),
                    n_dots=int((dots & reg).sum()))
    out["piedmont"] = one(foot & ~mountain, "piedmont")
    out["mountain"] = one(foot & mountain, "mountain")
    return out


def estimates(dots, foot, off_sgmc) -> dict:
    """Three labelled estimates per amended G6; none is a score."""
    cal = json.loads((ROOT / "evidence/cross_family_calibration_20261026.json").read_text())
    s = U.sgmc_score(dots, off_sgmc, foot)
    credit = s["tpw"] / max(s["n_dots"], 1)
    coverage = float(binary_dilation(dots, structure=np.ones((7, 7), bool)).sum() / foot.sum())
    m1 = 0.9275488479808367 * s["tpw"] / (10694.644444444453 + 0.2 * s["n_dots"])
    m3c = cal["zero_catalogue_subset"]["M3"]["coef_loo_fullfit"]
    loo_rmse = cal["zero_catalogue_subset"]["M3"]["rmse"]
    m3 = m3c["intercept"] + m3c["coef"][0] * credit + m3c["coef"][1] * coverage \
        + m3c["coef"][2] * float(np.log(s["n_dots"]))
    return dict(
        sgmc=s, sgmc_credit_per_dot=float(credit), coverage_3px=coverage,
        M1_in_family_upper_bound_diagnostic=dict(
            value=float(m1),
            label="PROJECTION (in-family arithmetic only; out-of-family RMSE 0.196, bias +0.135 — never a score)"),
        M3_cross_family=dict(
            central=float(m3), interval_pm2rmse=[float(m3 - 2 * loo_rmse), float(m3 + 2 * loo_rmse)],
            loo_rmse=float(loo_rmse), n_calibration=cal["zero_catalogue_subset"]["n"],
            label="PROJECTION (cross-family LOO calibration on USER-REPORTED values — never a score)"))


def run_exp3() -> dict:
    foot, cat, sgmc, off_sgmc, d_cat = U.load_grid()
    dots = np.load(CACHE / "final_dots.npy")
    mountain = np.load(CACHE / "mountain.npy")
    split = random_component_split(cat, foot, CONFIRM_SEED)
    log("confirmation split", split["receipt"])
    out = score(["Y3", "Y2", "CTRL"], [split], foot)
    conf = U.pooled(out["terms"], candidate="Y3")
    anchors = U.load_peer_dots_by_tag(foot)
    h33 = anchors["GEMSDOE32-h33-2-b2"][0]
    h31x_path = ROOT / "docs/downloads/gemsdoe31-h31x-piedmont-junction-37654-20261026-5a956da9-zeros.tif"
    h31x, _, _ = U.read_dots(str(h31x_path), foot)
    sg = dict(candidate=U.sgmc_score(dots, off_sgmc, foot),
              H33=U.sgmc_score(h33, off_sgmc, foot),
              H31X=U.sgmc_score(h31x, off_sgmc, foot),
              candidate_regimes=regime_sgmc(dots, off_sgmc, foot, mountain),
              H33_regimes=regime_sgmc(h33, off_sgmc, foot, mountain),
              H31X_regimes=regime_sgmc(h31x, off_sgmc, foot, mountain))
    est = estimates(dots, foot, off_sgmc)
    est_h31x = estimates(h31x, foot, off_sgmc)
    rep = dict(lane=LANE, experiment="EXP-3 confirmation (zero tuning) + SGMC + honest estimates",
               confirmation=dict(evaluator_version=ev.VERSION, partition=split["receipt"],
                                 per_fold=out["per_fold"], pooled=conf),
               sgmc_full=sg, estimates=est, estimates_H31X_for_context=est_h31x)
    (EVID / "exp3.json").write_text(json.dumps(rep, indent=1, default=float) + "\n")
    log("EXP3 confirm Y3", round(conf["scores"]["Y3"]["dti"], 4),
        "Y2", round(conf["scores"]["Y2"]["dti"], 4), "CTRL", round(conf["scores"]["CTRL"]["dti"], 4))
    log("EXP3 SGMC cand", round(sg["candidate"]["dti"], 4), "H33", round(sg["H33"]["dti"], 4),
        "H31X", round(sg["H31X"]["dti"], 4))
    log("EXP3 estimates M1", round(est["M1_in_family_upper_bound_diagnostic"]["value"], 4),
        "M3", round(est["M3_cross_family"]["central"], 4), est["M3_cross_family"]["interval_pm2rmse"])
    return rep


def evaluate_gates() -> dict:
    canary = json.loads((EVID / "canary.json").read_text())
    exp1 = json.loads((EVID / "exp1_screen.json").read_text())
    exp2 = json.loads((EVID / "exp2.json").read_text())
    exp3 = json.loads((EVID / "exp3.json").read_text())
    diffs = exp1["pooled"]["paired_differences"]
    conf_d = exp3["confirmation"]["pooled"]["paired_differences"]
    pied = exp1["subgroup_piedmont"]["pooled"]["scores"]
    g3_parts = dict(
        vs_ctrl_ci_excludes0=bool(diffs["CTRL"]["delta"] > 0 and diffs["CTRL"]["ci95"][0] > 0),
        vs_y2_not_worse_than_minus_0p005=bool(diffs["Y2"]["ci95"][0] > -0.005),
        piedmont_subgroup_point_above_y2=bool(pied["Y3"]["dti"] > pied["Y2"]["dti"]),
        confirmation_vs_ctrl_ci_excludes0=bool(
            conf_d["CTRL"]["delta"] > 0 and conf_d["CTRL"]["ci95"][0] > 0))
    u = exp2["uniqueness"]
    g5 = bool(u["discrete_max_final_overlap"] is not None
              and u["discrete_max_final_overlap"] <= 0.70
              and (u["max_abs_surface_spearman"] or 0) <= 0.90
              and (u["max_abs_dots_spearman"] or 0) <= 0.90)
    est = exp3["estimates"]
    gates = dict(
        G2_canary=bool(canary["all_pass"]),
        G3_holdout_efficacy=bool(all(g3_parts.values())),
        G4_sgmc_discovery=bool(exp3["sgmc_full"]["candidate"]["dti"] >= exp3["sgmc_full"]["H33"]["dti"]),
        G5_uniqueness_discrete=g5,
        G6_honest_estimate_reported=bool(
            est["M3_cross_family"]["interval_pm2rmse"][1] > 0.2778),
        detail=dict(g3_parts=g3_parts, paired_differences_exp1=diffs,
                    paired_differences_confirmation=conf_d,
                    piedmont_subgroup_scores=pied,
                    literal_695_lattice=exp2["literal_witness"]))
    return gates


def run_package() -> dict:
    foot, cat, sgmc, off_sgmc, _ = U.load_grid()
    exp1 = json.loads((EVID / "exp1_screen.json").read_text())
    exp2 = json.loads((EVID / "exp2.json").read_text())
    exp3 = json.loads((EVID / "exp3.json").read_text())
    gates_pre = evaluate_gates()
    dots = np.load(CACHE / "final_dots.npy")
    pred = np.where(foot, dots.astype(np.float32), 0.0).astype(np.float32)
    support_sha = hashlib.sha256(np.packbits(dots.ravel()).tobytes()).hexdigest()
    name = f"gemsdoe31-h31y-regime-mosaic-37654-20261026-{support_sha[:8]}"
    hold = exp1["pooled"]["scores"]["Y3"]
    verdict_pre = all(gates_pre[k] for k in gates_pre if k.startswith("G"))
    tag = "" if verdict_pre else " DO-NOT-SUBMIT"
    note = (f"H31-Y Y3 regime-mosaic junc+FAN 50/50 37654d B2 | HOLDOUT-DTI {hold['dti']:.4f} "
            f"n={hold['withheld_positive_pixels']} | {support_sha[:8]}{tag}")[:140]
    sample = ROOT / "data/sample_submission.tif"
    out_tif = ROOT / "docs/downloads" / f"{name}-zeros.tif"
    meta = dict(lane=LANE, arm="Y3", preregistration=PREREG, support_sha256=support_sha)
    receipt = submission_writer.write_submission(out_tif, pred, sample, foot, note=note,
                                                 name=name, catalogue=cat, metadata=meta)
    nan_tif = ROOT / "docs/downloads" / f"{name}-nan.tif"
    with rasterio.open(sample) as ds:
        prof = ds.profile.copy()
    prof.update(dtype="float32", count=1, nodata=float("nan"), compress="deflate")
    with rasterio.open(nan_tif, "w", **prof) as ds:
        ds.write(np.where(foot, pred, np.nan).astype(np.float32), 1)
    for tif in (out_tif, nan_tif):
        with zipfile.ZipFile(tif.with_suffix(".zip"), "w", compression=zipfile.ZIP_DEFLATED) as z:
            z.write(tif, arcname=tif.name)
    vz = validate_submission(out_tif, sample, convention="all-finite")
    vn = validate_submission(nan_tif, sample, convention="nan-outside")
    # global min spacing check (offset-pair scan below)
    spacing_ok = None
    ys, xs = np.nonzero(dots)
    if len(ys) > 1:
        # blocked check: any dot within <2.8px of another (3x3/5x5 offsets)
        bad = 0
        dotset = dots
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                if dr * dr + dc * dc >= MIN_DIST ** 2 or (dr == 0 and dc == 0):
                    continue
                shifted = np.roll(np.roll(dotset, dr, axis=0), dc, axis=1)
                bad += int((dotset & shifted).sum())
        spacing_ok = bool(bad == 0)
    gates = dict(G1_format=bool(vz["ok_to_upload_format_only"] and vn["ok_to_upload_format_only"]
                                and spacing_ok), **gates_pre)
    promote = bool(all(gates[k] for k in gates if k.startswith("G")))
    u = exp2["uniqueness"]
    est = exp3["estimates"]
    card = dict(
        lane=LANE,
        hypothesis="Regime-mosaic: mountain range-front faults are recovered by the piedmont-junction "
                   "slope-break line, piedmont fan faults by one-sided strike-coherent low-relief "
                   "LiDAR scarps; a 50/50 regime budget beats either specialist alone.",
        mechanism="Y3: 18,827 dots from JUNC rank inside slope>6deg regime + 18,827 from FAN "
                  "(geomean rank of step_max, |upface-downface|, coh100, relief-inverse; JUNC "
                  "fallback off-LiDAR) inside slope<=6deg regime; Poisson 2.8px, d(catalogue)>2px. "
                  "No prior dots/surfaces used.",
        non_fault_mimic="fluvial terrace risers / fan-lobe boundaries (one-sided LiDAR steps), "
                        "Lahontan shoreline benches, erosional pediment edges",
        holdout_dti=dict(evidence_class="HOLDOUT-DTI", evaluator_version=ev.VERSION,
                         candidate=hold, paired_differences=exp1["pooled"]["paired_differences"],
                         confirmation=exp3["confirmation"]["pooled"]),
        sgmc_proxy=dict(evidence_class="COMPUTED", **exp3["sgmc_full"]),
        estimates=est,
        registry=dict(scope="discrete peers: nine focus rasters (hash-verified) + all local downloads",
                      max_final_overlap_3px=u["discrete_max_final_overlap"],
                      max_abs_surface_spearman=u["max_abs_surface_spearman"],
                      max_abs_dots_spearman=u["max_abs_dots_spearman"],
                      literal_695_lattice=exp2["literal_witness"]),
        raster_sha256=sha256_file(out_tif),
        support_sha256=support_sha,
        validator=dict(zeros=receipt, local_zeros=vz, local_nan=vn, min_spacing_ok=spacing_ok),
        submission_name=name,
        submission_note=note,
        submission_note_chars=len(note),
        files=dict(zeros=out_tif.name, nan=nan_tif.name,
                   zeros_zip=out_tif.with_suffix(".zip").name, nan_zip=nan_tif.with_suffix(".zip").name),
        gates=gates,
        verdict="promote" if promote else "negative",
        slot_approved=bool(promote),
        score_label="No ORGANIZER-CONFIRMED score exists; estimates are PROJECTIONs, never scores.")
    (ROOT / "docs/downloads" / f"{name}-run-card.json").write_text(
        json.dumps(card, indent=1, default=float) + "\n")
    (EVID / "run_card.json").write_text(json.dumps(card, indent=1, default=float) + "\n")
    (ROOT / "docs/downloads" / f"{name}-zeros.json").write_text(
        json.dumps(vz, indent=1, default=float) + "\n")
    log("package", name, "verdict", card["verdict"], "gates",
        {k: gates[k] for k in gates if k.startswith("G")})
    return card


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("stage", choices=("lines", "canary", "exp1", "exp2", "exp3", "package", "all"))
    args = ap.parse_args()
    stages = ("lines", "canary", "exp1", "exp2", "exp3", "package") if args.stage == "all" else (args.stage,)
    for st in stages:
        log("=== stage", st)
        {"lines": build_lines, "canary": run_canary, "exp1": run_exp1,
         "exp2": run_exp2, "exp3": run_exp3, "package": run_package}[st]()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
