#!/usr/bin/env python3
"""H31-Y lane runner: polarity-concordant LiDAR facing + piedmont gravity.

Frozen by knowledge/2026-10-26_h31y_preregistration.md BEFORE any fitting.
Reuses vendor/gems57 (spatial.folds, evaluate_holdout = gems57-pooled-hide-v2,
submission_writer) and H31-U helpers. No prior dots enter the candidate.
Stages: lines, canary, exp1, exp2, exp3, package.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import sys
import time
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))

import run_h31u as U  # noqa: E402
from gems57 import evaluate_holdout as ev  # noqa: E402
from gems57 import metric as vmetric  # noqa: E402
from gems57 import spatial, submission_writer  # noqa: E402
from gemsdoe31.h31y_features import synth_anti_gravpied  # noqa: E402
from gemsdoe31.submission import validate_submission  # noqa: E402

SHAPE = (3730, 3292)
BUDGET = 37_654
B_PX = 2.0
LANE = "H31-Y"
CACHE = ROOT / "data" / "h31y"
EVID = ROOT / "evidence" / "h31y"
PREREG = "knowledge/2026-10-26_h31y_preregistration.md"
LINES = ["SYNTH", "ANTI", "GRAVPIED", "BASEPIED", "CTRL", "SLOPE"]
ARMS = {
    "Y1": ["GRAVPIED"],
    "Y2": ["ANTI"],
    "Y3": ["SYNTH"],
    "Y4": ["GRAVPIED", "ANTI"],
    "CTRL": ["CTRL"],
    "SLOPE": ["SLOPE"],
}
Y_ARMS = ["Y1", "Y2", "Y3", "Y4"]
CONFIRM_SEED = 3104
log = U.log
sha256_file = U.sha256_file


def build_lines() -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    EVID.mkdir(parents=True, exist_ok=True)
    foot, cat, *_ = U.load_grid()
    mm = np.memmap(CACHE / "lines.f32", dtype=np.float32, mode="w+", shape=(len(LINES),) + SHAPE)
    t0 = time.time()
    valid = U.stack_band("valid", foot)
    lidar_ok = foot & np.isfinite(valid) & (valid > 0)
    downface = U.stack_band("downface_max", foot)
    downface = np.where(np.isfinite(downface), downface, 0.0).astype(np.float32)
    raw = synth_anti_gravpied(
        elev=U.clean(U.stack_band("det_elev", foot), foot),
        slope_deg=U.clean(U.stack_band("det_elev_slope", foot), foot),
        gravity=U.clean(U.stack_band("iso_grav_anom", foot), foot),
        grav_hg=U.clean(U.stack_band("iso_grav_anom_hg", foot), foot),
        basement=U.clean(U.stack_band("depth_to_base_surf", foot), foot),
        downface=downface,
        lidar_ok=lidar_ok,
        foot=foot,
    )
    mm[LINES.index("SYNTH")] = U.rank01(raw["SYNTH"], foot)
    mm[LINES.index("ANTI")] = U.rank01(raw["ANTI"], foot)
    mm[LINES.index("GRAVPIED")] = U.rank01(raw["GRAVPIED"], foot)
    mm[LINES.index("BASEPIED")] = U.rank01(raw["BASEPIED"], foot)
    mm[LINES.index("CTRL")] = U.rank01(U.clean(U.stack_band("tmi_hg", foot), foot), foot)
    mm[LINES.index("SLOPE")] = U.rank01(U.clean(U.stack_band("det_elev_slope", foot), foot), foot)
    mm.flush()
    receipts = {}
    for i, n in enumerate(LINES):
        a = np.asarray(mm[i])[foot]
        receipts[n] = dict(min=float(a.min()), max=float(a.max()), mean=float(a.mean()),
                           frac_zero=float((a == 0).mean()))
    meta = dict(lane=LANE, lines=LINES, shape=list(SHAPE), lidar_ok_pixels=int(lidar_ok.sum()),
                receipts=receipts, note="label-free footprint percentile-rank lines; see preregistration")
    (CACHE / "lines.json").write_text(json.dumps(meta, indent=1) + "\n")
    (EVID / "lines.json").write_text(json.dumps(meta, indent=1) + "\n")
    log("lines written", round(time.time() - t0), "s; lidar_ok", int(lidar_ok.sum()))
    return meta


def load_line(name: str) -> np.ndarray:
    mm = np.memmap(CACHE / "lines.f32", dtype=np.float32, mode="r", shape=(len(LINES),) + SHAPE)
    return np.asarray(mm[LINES.index(name)], dtype=np.float32).copy()


def surface(arm: str, *, gate: bool = True) -> np.ndarray:
    names = list(ARMS[arm])
    if len(names) == 1:
        return load_line(names[0])
    parts = [load_line(n) for n in names]
    g = U.geomean_rank(parts)
    if not gate:
        return g
    second = np.partition(np.stack(parts), -2, axis=0)[-2]
    return (g * second).astype(np.float32)


def run_canary() -> dict:
    foot, cat, sgmc, off_sgmc, _ = U.load_grid()
    rows = []
    for n in LINES:
        v = load_line(n)
        a_cat, a_off = U.auc_for(v, cat, foot), U.auc_for(v, off_sgmc, foot)
        rows.append(dict(feature=n, kind="line", auc_catalogue=a_cat, auc_off_sgmc=a_off,
                         leakage_flagged=bool(max(a_cat, a_off, 1 - a_cat, 1 - a_off) > 0.90)))
        log("canary line", n, round(a_cat, 4), round(a_off, 4))
    for arm in Y_ARMS:
        v = surface(arm)
        a_cat, a_off = U.auc_for(v, cat, foot), U.auc_for(v, off_sgmc, foot)
        rows.append(dict(feature=arm, kind="surface", auc_catalogue=a_cat, auc_off_sgmc=a_off,
                         leakage_flagged=bool(max(a_cat, a_off, 1 - a_cat, 1 - a_off) > 0.90)))
        log("canary surface", arm, round(a_cat, 4), round(a_off, 4))
    rep = dict(lane=LANE, evidence_class="COMPUTED", auc_ceiling=0.90, rows=rows,
               all_pass=bool(all(not r["leakage_flagged"] for r in rows)))
    (EVID / "canary.json").write_text(json.dumps(rep, indent=1) + "\n")
    return rep


def score_arms(arm_surfaces: dict, folds: list, foot) -> dict:
    terms: dict[str, np.ndarray] = {}
    per_fold: dict[str, list] = {a: [] for a in arm_surfaces}

    def add(name, pred, f):
        res, trm = ev.evaluate(pred, f, foot)
        terms[name] = trm if name not in terms else terms[name] + trm
        per_fold[name].append(dict(fold=int(f["fold"]),
                                   dti=float(vmetric.dti_from_components(res["tpw"], res["fpw"], res["fnw"])),
                                   n_truth=int(res["n_truth"]), emitted_active=int(res["n_emitted"])))
        log(" fold", f["fold"], name, "dti", round(per_fold[name][-1]["dti"], 4), "truth", res["n_truth"])

    for f in folds:
        d_vis = distance_transform_edt(~f["visible"])
        allowed = foot & (d_vis > B_PX)
        for arm, surf in arm_surfaces.items():
            dots = U.emit_dots(surf, allowed & (surf > 0))
            add(arm, dots.astype(np.float32), f)
    return dict(terms=terms, per_fold=per_fold)


def random_component_split(cat: np.ndarray, foot: np.ndarray, seed: int) -> dict:
    from scipy import ndimage as ndi
    comp, n = ndi.label(cat, np.ones((3, 3), bool))
    rng = np.random.default_rng(seed)
    hidden_ids = np.flatnonzero(rng.random(n + 1) < 0.5)
    hidden_ids = hidden_ids[hidden_ids > 0]
    hidden = np.isin(comp, hidden_ids) & cat
    visible = cat & ~hidden
    return dict(fold=9, region=foot.copy(), visible=visible, masked_known=visible, truth=hidden,
                receipt=dict(split="random-component-50pct", seed=seed, components=int(n),
                             hidden_components=int(hidden_ids.size), truth_px=int(hidden.sum()),
                             visible_px=int(visible.sum())))


def run_exp1() -> dict:
    foot, cat, sgmc, off_sgmc, _ = U.load_grid()
    surfs = {a: surface(a) for a in ARMS}
    folds = list(spatial.folds(cat, foot, buffer_px=213))
    receipts = [f["receipt"] for f in folds]
    log("folds buffer 213", [r["truth_px"] for r in receipts])
    out = score_arms(surfs, folds, foot)
    scores_tmp = U.pooled(out["terms"], candidate="Y1")["scores"]
    winner = max(Y_ARMS, key=lambda a: scores_tmp[a]["dti"])
    summ = U.pooled(out["terms"], candidate=winner)
    rep = dict(lane=LANE, experiment="EXP-1 screen", evaluator_version=ev.VERSION, buffer_px=213,
               fold_receipts=receipts, per_fold=out["per_fold"], pooled=summ, winner=winner)
    (EVID / "exp1_screen.json").write_text(json.dumps(rep, indent=1, default=float) + "\n")
    (CACHE / "exp1_winner.json").write_text(json.dumps(dict(winner=winner)) + "\n")
    for a in summ["scores"]:
        log("EXP1 pooled", a, round(summ["scores"][a]["dti"], 4), summ["scores"][a]["ci95"],
            "n=", summ["scores"][a]["withheld_positive_pixels"])
    log("EXP1 winner", winner)
    return rep


def peer_files_y() -> list[dict]:
    peers = []
    for p in sorted(glob.glob(str(ROOT / "data/prior_audit/**/downloads/*.tif"), recursive=True)):
        peers.append(dict(id="focus:" + Path(p).parent.parent.parent.name + ":" + Path(p).name, path=p))
    for p in sorted(glob.glob(str(ROOT / "docs/downloads/*.tif"))):
        if "h31y" in p.lower():
            continue
        peers.append(dict(id="local:" + Path(p).name, path=p))
    return peers


def run_exp2() -> dict:
    foot, cat, sgmc, off_sgmc, d_cat = U.load_grid()
    winner = json.loads((CACHE / "exp1_winner.json").read_text())["winner"]
    folds = list(spatial.folds(cat, foot, buffer_px=213))
    keep_gate = True
    pooled_by = {}
    per_fold = {}
    if len(ARMS[winner]) > 1:
        surfs = {winner + "_gate": surface(winner, gate=True),
                 winner + "_nogate": surface(winner, gate=False),
                 "CTRL": surface("CTRL"), "SLOPE": surface("SLOPE")}
        out = score_arms(surfs, folds, foot)
        per_fold = out["per_fold"]
        pooled_by = {k: U.pooled(out["terms"], candidate=k) for k in (winner + "_gate", winner + "_nogate")}
        g_on = pooled_by[winner + "_gate"]["scores"][winner + "_gate"]["dti"]
        g_off = pooled_by[winner + "_nogate"]["scores"][winner + "_nogate"]["dti"]
        keep_gate = bool(g_on >= g_off)
        log("EXP2 ablation gate", round(g_on, 4), "nogate", round(g_off, 4), "keep_gate", keep_gate)
        final_key = winner + ("_gate" if keep_gate else "_nogate")
        summ = pooled_by[final_key]
    else:
        surfs = {winner: surface(winner), "CTRL": surface("CTRL"), "SLOPE": surface("SLOPE")}
        out = score_arms(surfs, folds, foot)
        per_fold = out["per_fold"]
        summ = U.pooled(out["terms"], candidate=winner)
        pooled_by = {winner: summ}
        final_key = winner
        log("EXP2 single-line winner, no gate ablation")
    surf = surface(winner, gate=keep_gate)
    allowed = foot & (d_cat > B_PX) & (surf > 0)
    dots = U.emit_dots(surf, allowed)
    log("final dots", int(dots.sum()), "on_cat", int((dots & cat).sum()))
    np.save(CACHE / "final_dots.npy", dots)
    np.save(CACHE / "final_surface.npy", surf)
    (CACHE / "final_choice.json").write_text(json.dumps(
        dict(arm=winner, gate=keep_gate, lines=ARMS[winner], final_key=final_key), indent=1) + "\n")
    U.peer_files = peer_files_y
    uniq = U.uniqueness_audit(surf, dots, foot)
    rep = dict(lane=LANE, experiment="EXP-2 gate ablation + uniqueness", winner_from_exp1=winner,
               ablation=dict(per_fold=per_fold, pooled=summ, final_variant=final_key,
                             pooled_by_candidate=pooled_by), gate_kept=keep_gate,
               uniqueness=uniq, literal_witness=U.literal_witness(dots, foot))
    (EVID / "exp2.json").write_text(json.dumps(rep, indent=1, default=float) + "\n")
    log("EXP2 discrete max overlap", uniq["discrete_max_final_overlap"], "topk", uniq["discrete_max_topk_overlap"],
        "max|rho| surf", uniq["max_abs_surface_spearman"], "dots", uniq["max_abs_dots_spearman"])
    return rep


def regime_sgmc(dots, off_sgmc, foot, slope, lo, hi) -> dict:
    reg = foot & np.isfinite(slope) & (slope > lo) & (slope <= hi)
    r = vmetric.dti_exact((dots & reg).astype(np.float32), off_sgmc & reg, valid=reg)
    return dict(dti=float(r["dti"]), n_truth=int((off_sgmc & reg).sum()), n_dots=int((dots & reg).sum()))


def run_exp3() -> dict:
    foot, cat, sgmc, off_sgmc, d_cat = U.load_grid()
    choice = json.loads((CACHE / "final_choice.json").read_text())
    winner, gate = choice["arm"], choice["gate"]
    dots = np.load(CACHE / "final_dots.npy")
    split = random_component_split(cat, foot, CONFIRM_SEED)
    log("confirmation split", split["receipt"])
    surfs = {winner: surface(winner, gate=gate), "CTRL": surface("CTRL"), "SLOPE": surface("SLOPE")}
    out = score_arms(surfs, [split], foot)
    conf = U.pooled(out["terms"], candidate=winner)
    anchors = U.load_peer_dots_by_tag(foot)
    h33 = anchors["GEMSDOE32-h33-2-b2"][0]
    h27 = anchors["GEMSDOE28-h27-4"][0]
    slope = U.stack_band("det_elev_slope", foot)
    sg = dict(candidate=U.sgmc_score(dots, off_sgmc, foot), H33=U.sgmc_score(h33, off_sgmc, foot),
              H27=U.sgmc_score(h27, off_sgmc, foot))
    for k, dd in (("candidate", dots), ("H33", h33)):
        sg[k + "_piedmont_le6deg"] = regime_sgmc(dd, off_sgmc, foot, slope, -1.0, 6.0)
        sg[k + "_mountain_gt6deg"] = regime_sgmc(dd, off_sgmc, foot, slope, 6.0, 1e9)
    quad = {}
    h, w = SHAPE
    for qi, (ys, xs) in enumerate([(slice(0, h // 2), slice(0, w // 2)), (slice(0, h // 2), slice(w // 2, w)),
                                   (slice(h // 2, h), slice(0, w // 2)), (slice(h // 2, h), slice(w // 2, w))]):
        sub_f = foot[ys, xs]
        if off_sgmc[ys, xs].sum() == 0:
            quad[f"Q{qi}"] = None
            continue
        rc = vmetric.dti_exact(dots[ys, xs].astype(np.float32), off_sgmc[ys, xs], valid=sub_f)
        rh = vmetric.dti_exact(h33[ys, xs].astype(np.float32), off_sgmc[ys, xs], valid=sub_f)
        quad[f"Q{qi}"] = dict(candidate=float(rc["dti"]), H33=float(rh["dti"]))
    proj = U.projection(dots, foot, off_sgmc)
    rep = dict(lane=LANE, experiment="EXP-3 confirmation (zero tuning) + SGMC + projection",
               confirmation=dict(evaluator_version=ev.VERSION, partition=split["receipt"],
                                 per_fold=out["per_fold"], pooled=conf), winner=winner, gate=gate,
               sgmc_full=sg, sgmc_quadrants=quad, projection=proj)
    (EVID / "exp3.json").write_text(json.dumps(rep, indent=1, default=float) + "\n")
    log("EXP3 confirm", winner, round(conf["scores"][winner]["dti"], 4), "CTRL", round(conf["scores"]["CTRL"]["dti"], 4))
    log("EXP3 SGMC cand", round(sg["candidate"]["dti"], 4), "H33", round(sg["H33"]["dti"], 4),
        "PROJECTION", round(proj["candidate"]["projection"], 4))
    return rep


def evaluate_gates() -> dict:
    canary = json.loads((EVID / "canary.json").read_text())
    exp1 = json.loads((EVID / "exp1_screen.json").read_text())
    exp2 = json.loads((EVID / "exp2.json").read_text())
    exp3 = json.loads((EVID / "exp3.json").read_text())
    winner = exp3["winner"]
    final_key = exp2["ablation"]["final_variant"]
    pooled_final = exp2["ablation"]["pooled"]
    d_ctrl = pooled_final["paired_differences"].get("CTRL")
    d_slope = pooled_final["paired_differences"].get("SLOPE")
    pf = exp2["ablation"]["per_fold"]
    qwins = sum(1 for a, b in zip(pf[final_key], pf["CTRL"]) if a["dti"] >= b["dti"])
    final_dti = pooled_final["scores"][final_key]
    conf = exp3["confirmation"]["pooled"]["paired_differences"]
    c_ctrl = conf.get("CTRL")

    def pos(d):
        return bool(d and d["delta"] > 0 and d["ci95"][0] > 0)

    g3 = bool(pos(d_ctrl) and pos(d_slope) and qwins >= 3 and pos(c_ctrl))
    u = exp2["uniqueness"]
    g5 = bool(u["discrete_max_final_overlap"] is not None and u["discrete_max_final_overlap"] <= 0.70
              and (u["discrete_max_topk_overlap"] or 0) <= 0.70
              and (u["max_abs_surface_spearman"] or 0) <= 0.90 and (u["max_abs_dots_spearman"] or 0) <= 0.90)
    return dict(
        G2_canary=bool(canary["all_pass"]),
        G3_holdout_efficacy=g3,
        G4_sgmc_discovery=bool(exp3["sgmc_full"]["candidate"]["dti"] >= exp3["sgmc_full"]["H33"]["dti"]),
        G5_uniqueness_discrete=g5,
        G6_projection_ge_02778=bool(exp3["projection"]["candidate"]["projection"] >= 0.2778),
        detail=dict(winner=winner, final_variant=final_key, final_holdout=final_dti,
                    exp1_screen_scores=exp1["pooled"]["scores"],
                    paired_vs_ctrl_screen=d_ctrl, paired_vs_slope_screen=d_slope,
                    quadrant_wins_vs_ctrl=qwins, paired_vs_ctrl_confirmation=c_ctrl,
                    confirmation_scores=exp3["confirmation"]["pooled"]["scores"]),
    )


def run_package() -> dict:
    foot, cat, sgmc, off_sgmc, _ = U.load_grid()
    choice = json.loads((CACHE / "final_choice.json").read_text())
    exp2 = json.loads((EVID / "exp2.json").read_text())
    exp3 = json.loads((EVID / "exp3.json").read_text())
    gates = evaluate_gates()
    dots = np.load(CACHE / "final_dots.npy")
    pred = np.where(foot, dots.astype(np.float32), 0.0).astype(np.float32)
    support_sha = hashlib.sha256(np.packbits(dots.ravel()).tobytes()).hexdigest()
    name = f"gemsdoe31-h31y-kinpied-{int(dots.sum())}-20261026-{support_sha[:8]}"
    hold = gates["detail"]["final_holdout"]
    note = (f"H31-Y {choice['arm']} KIN-PIED polarity-LiDAR+gravpied"
            f" {int(dots.sum())}d B2 | HOLDOUT-DTI {hold['dti']:.4f} n={hold['withheld_positive_pixels']} | {support_sha[:8]}")[:140]
    out_tif = ROOT / "docs/downloads" / f"{name}-zeros.tif"
    sample = ROOT / "data/sample_submission.tif"
    receipt = submission_writer.write_submission(
        out_tif, pred, sample, foot, note=note, name=name, catalogue=cat,
        metadata=dict(lane=LANE, arm=choice["arm"], lines=choice["lines"], gate=choice["gate"]))
    nan_tif = ROOT / "docs/downloads" / f"{name}-nan.tif"
    with rasterio.open(sample) as ds:
        prof = ds.profile.copy()
    arr = np.where(foot, pred, np.nan).astype(np.float32)
    prof.update(dtype="float32", count=1, nodata=float("nan"), compress="deflate")
    with rasterio.open(nan_tif, "w", **prof) as ds:
        ds.write(arr, 1)
    nan_zip = nan_tif.with_suffix(".zip")
    with zipfile.ZipFile(nan_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.write(nan_tif, arcname=nan_tif.name)
    vz = validate_submission(out_tif, sample, convention="all-finite")
    vn = validate_submission(nan_tif, sample, convention="nan-outside")
    gates = dict(G1_format=bool(vz["ok_to_upload_format_only"] and vn["ok_to_upload_format_only"]), **gates)
    promote = bool(all(gates[k] for k in gates if k.startswith("G")))
    u = exp2["uniqueness"]
    sg = exp3["sgmc_full"]
    card = dict(
        lane=LANE, session_branch="arena/f4d7fb29-gemsdoe31", generated_utc="2026-10-26",
        hypothesis=("H31-Y KIN-PIED: catalogue-missing hanging-wall / intra-basin faults are polarity-"
                    "concordant LiDAR scarps (synthetic face the basin, antithetic face the range) plus "
                    "low-slope gravity HG ridges; gravity decreasing direction defines the hanging wall"),
        mechanism=(f"{choice['arm']}: {'+'.join(choice['lines'])} — downface_max × relu(û_down·û_basin|range) "
                   f"and/or |iso_grav_anom_hg| in a 0-5 deg piedmont window; "
                   f"{'second-line gate ON' if choice['gate'] else 'no second-line gate'}; "
                   "Poisson 2.8 px, 37,654 dots, d(catalogue) > 2 px"),
        non_fault_mimic=("Lahontan shorelines/wave-cut benches (cannot elevation-mask with detrended DEM), "
                         "road/canal cuts, lava-flow snouts, landslide toes, erosional pediment edges"),
        holdout_dti=dict(evidence_class="HOLDOUT-DTI", evaluator_version=ev.VERSION,
                         screen_final_surface=gates["detail"]["final_holdout"],
                         screen_paired_vs_ctrl=gates["detail"]["paired_vs_ctrl_screen"],
                         screen_paired_vs_slope=gates["detail"]["paired_vs_slope_screen"],
                         quadrant_wins_vs_ctrl=gates["detail"]["quadrant_wins_vs_ctrl"],
                         confirmation_random_component_split=dict(
                             partition=exp3["confirmation"]["partition"],
                             scores=exp3["confirmation"]["pooled"]["scores"],
                             paired_differences=exp3["confirmation"]["pooled"]["paired_differences"])),
        sgmc_proxy=dict(evidence_class="COMPUTED off-catalogue USGS-SGMC proxy (not hidden truth)",
                        candidate=sg["candidate"], H33=sg["H33"], H27=sg["H27"],
                        regimes={k: v for k, v in sg.items() if "deg" in k},
                        quadrants=exp3["sgmc_quadrants"]),
        projection=dict(evidence_class="PROJECTION (never a score)",
                        value=exp3["projection"]["candidate"]["projection"],
                        interval_approx=exp3["projection"]["candidate"]["interval_approx"],
                        loo_rmse=exp3["projection"]["loo_rmse"],
                        anchors="USER-REPORTED focus values; no organizer receipts; in-family calibration"),
        correlation_overlap_vs_registry=dict(
            scope="discrete dot-field peers: 9 focus sites + local GEMSDOE31 downloads; surface and final dots",
            discrete_max_final_overlap_3px=u["discrete_max_final_overlap"],
            discrete_max_topk_overlap_3px=u["discrete_max_topk_overlap"],
            max_abs_spearman_surface=u["max_abs_surface_spearman"],
            max_abs_spearman_dots=u["max_abs_dots_spearman"],
            literal_broad_registry=exp2["literal_witness"],
            unique_vs_discrete_peers=bool(gates["G5_uniqueness_discrete"])),
        raster_sha256=sha256_file(out_tif), raster_sha256_nan=sha256_file(nan_tif),
        zip_sha256=receipt["zip_sha256"], support_sha256=support_sha,
        validator=dict(zeros=dict(file=out_tif.name, ok=vz["ok_to_upload_format_only"],
                                   hard_failures=vz["hard_failures"], grid=vz["grid"]),
                       nan=dict(file=nan_tif.name, ok=vn["ok_to_upload_format_only"],
                                hard_failures=vn["hard_failures"], grid=vn["grid"]),
                       organizer_acceptance_verified=False),
        submission_name=name, note=note, note_chars=len(note),
        gates=gates, verdict="promote" if promote else "negative",
        ok_to_download_for_research=True, ok_to_submit=promote, slot_approved=promote,
        submission_slots_used=0,
        instruction=("OK TO DOWNLOAD AND SUBMIT: all automated gates G1-G6 pass; owner uploads manually."
                     if promote else
                     "DO NOT SUBMIT: at least one automated gate failed; research download only."),
        files=dict(zeros=f"docs/downloads/{out_tif.name}", nan=f"docs/downloads/{nan_tif.name}",
                   zip=f"docs/downloads/{out_tif.with_suffix('.zip').name}", nan_zip=f"docs/downloads/{nan_zip.name}"),
        preregistration=PREREG,
        evidence=dict(lines="evidence/h31y/lines.json", canary="evidence/h31y/canary.json",
                      exp1="evidence/h31y/exp1_screen.json", exp2="evidence/h31y/exp2.json",
                      exp3="evidence/h31y/exp3.json"),
    )
    (EVID / "run_card.json").write_text(json.dumps(card, indent=1, default=float) + "\n")
    (ROOT / "docs/downloads/h31y-run-card.json").write_text(json.dumps(card, indent=1, default=float) + "\n")
    (ROOT / "registry/h31y_current_run.json").write_text(json.dumps(card, indent=1, default=float) + "\n")
    log("PACKAGE", name, "verdict", card["verdict"], "gates", {k: v for k, v in gates.items() if k.startswith("G")})
    log("sha256 zeros", card["raster_sha256"])
    return card


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("stage", choices=["lines", "canary", "exp1", "exp2", "exp3", "package", "all"])
    args = ap.parse_args()
    stages = ["lines", "canary", "exp1", "exp2", "exp3", "package"] if args.stage == "all" else [args.stage]
    t0 = time.time()
    for s in stages:
        log("=== STAGE", s, "===", round(time.time() - t0), "s elapsed")
        {"lines": build_lines, "canary": run_canary, "exp1": run_exp1,
         "exp2": run_exp2, "exp3": run_exp3, "package": run_package}[s]()
    log("done", round(time.time() - t0), "s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
