#!/usr/bin/env python3
"""H31-Z lane runner: regime-complementary max-union (JUNC + SCARPX + GRAV).

Frozen by knowledge/2026-10-26_h31z_preregistration.md BEFORE any fitting.
Reuses shared tools unchanged: vendor/gems57 spatial.folds, evaluate_holdout
(gems57-pooled-hide-v2), metric, uniqueness, submission_writer; H31-U helpers
(load_grid, rank01, emit, SGMC, projection, uniqueness audit); H31-X
junction_line exactly. No prior dots enter the candidate.
Stages: lines, canary, exp1, exp2, exp3, package. <=3 experiments (exp1-3).
"""
from __future__ import annotations

import argparse
import gc
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
import run_h31x as X  # noqa: E402
from gems57 import evaluate_holdout as ev  # noqa: E402
from gems57 import metric as vmetric  # noqa: E402
from gems57 import spatial, submission_writer  # noqa: E402
from gemsdoe31.h31z_features import coherence_weighted, max_union, structure_tensor_coherence  # noqa: E402
from gemsdoe31.submission import validate_submission  # noqa: E402

SHAPE = (3730, 3292)
BUDGET = 37_654
B_PX = 2.0
LANE = "H31-Z"
SESSION = "arena/15e685db-gemsdoe31"
CACHE = ROOT / "data" / "h31z"
EVID = ROOT / "evidence" / "h31z"
PREREG = "knowledge/2026-10-26_h31z_preregistration.md"
LINES = ["JUNC", "S0", "SCARPX", "GRAV", "CTRL", "SLOPE"]
ARMS = {
    "JUNC": ["JUNC"],
    "SCARPX": ["SCARPX"],
    "GRAV": ["GRAV"],
    "Z2": ["JUNC", "SCARPX"],
    "Z3": ["JUNC", "SCARPX", "GRAV"],
    "CTRL": ["CTRL"],
    "SLOPE": ["SLOPE"],
}
CANDIDATES = ["SCARPX", "GRAV", "Z2", "Z3"]
COMPARATORS = ["JUNC", "CTRL", "SLOPE"]
CONFIRM_SEED = 3105
log = U.log
sha256_file = U.sha256_file


def prereg_sha() -> str:
    return sha256_file(ROOT / PREREG)


# ---------------------------------------------------------------- lines
def build_lines() -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    EVID.mkdir(parents=True, exist_ok=True)
    sha = prereg_sha()
    foot, cat, *_ = U.load_grid()
    mm = np.memmap(CACHE / "lines.f32", dtype=np.float32, mode="w+", shape=(len(LINES),) + SHAPE)
    t0 = time.time()
    z = U.clean(U.stack_band("det_elev", foot), foot)
    s = U.clean(U.stack_band("det_elev_slope", foot), foot)
    mm[LINES.index("JUNC")] = U.rank01(X.junction_line(z, s, foot, nms=False), foot)
    log("JUNC done", round(time.time() - t0))
    del z
    valid = U.stack_band("valid", foot)
    lidar_ok = foot & np.isfinite(valid) & (valid > 0)
    del valid

    def lidar_band(name: str) -> np.ndarray:
        a = U.stack_band(name, foot)
        a = np.where(np.isfinite(a), np.maximum(a, 0.0), 0.0).astype(np.float32)
        return np.where(lidar_ok, a, 0.0).astype(np.float32)

    step_r = U.rank01(lidar_band("step_max"), foot)
    face = np.maximum(lidar_band("downface_max"), lidar_band("upface_max"))
    face_r = U.rank01(face, foot)
    del face
    s0_field = U.geomean_rank([step_r, face_r])
    del step_r, face_r
    s0_field = np.where(lidar_ok, s0_field, 0.0).astype(np.float32)
    mm[LINES.index("S0")] = U.rank01(s0_field, foot)
    log("S0 done", round(time.time() - t0), "lidar_ok", int(lidar_ok.sum()))
    coh = structure_tensor_coherence(s0_field)
    coh_ok = coh[lidar_ok]
    coh_stats = dict(mean=float(coh_ok.mean()), p50=float(np.percentile(coh_ok, 50)),
                     p90=float(np.percentile(coh_ok, 90)), p99=float(np.percentile(coh_ok, 99)))
    del coh_ok
    mm[LINES.index("SCARPX")] = U.rank01(coherence_weighted(s0_field, coh, lidar_ok), foot)
    del s0_field, coh
    log("SCARPX done", round(time.time() - t0), coh_stats)
    mm[LINES.index("GRAV")] = U.rank01(np.abs(U.clean(U.stack_band("iso_grav_anom_hg", foot), foot)), foot)
    mm[LINES.index("CTRL")] = U.rank01(U.clean(U.stack_band("tmi_hg", foot), foot), foot)
    mm[LINES.index("SLOPE")] = U.rank01(s, foot)
    del s
    mm.flush()
    receipts = {}
    for i, n in enumerate(LINES):
        a = np.asarray(mm[i])[foot]
        receipts[n] = dict(min=float(a.min()), max=float(a.max()), mean=float(a.mean()),
                           frac_zero=float((a == 0).mean()))
    meta = dict(lane=LANE, session_branch=SESSION, preregistration=PREREG, preregistration_sha256=sha,
                lines=LINES, shape=list(SHAPE), lidar_ok_pixels=int(lidar_ok.sum()),
                coherence_on_lidar_ok=coh_stats, receipts=receipts,
                note="label-free footprint percentile-rank lines; JUNC exact H31-X reuse (nms=False)")
    (CACHE / "lines.json").write_text(json.dumps(meta, indent=1) + "\n")
    (EVID / "lines.json").write_text(json.dumps(meta, indent=1) + "\n")
    log("lines written", round(time.time() - t0), "s")
    return meta


def load_line(name: str) -> np.ndarray:
    mm = np.memmap(CACHE / "lines.f32", dtype=np.float32, mode="r", shape=(len(LINES),) + SHAPE)
    return np.asarray(mm[LINES.index(name)], dtype=np.float32).copy()


def surface(arm: str, *, variant: str = "coh") -> np.ndarray:
    names = list(ARMS[arm])
    if variant == "nocoh":
        names = ["S0" if n == "SCARPX" else n for n in names]
    elif variant != "coh":
        raise ValueError(f"unknown variant {variant!r}")
    parts = [load_line(n) for n in names]
    out = parts[0] if len(parts) == 1 else max_union(parts)
    return out.astype(np.float32)


# ---------------------------------------------------------------- canary
def run_canary() -> dict:
    foot, cat, sgmc, off_sgmc, _ = U.load_grid()
    rows = []
    for n in LINES:
        v = load_line(n)
        a_cat, a_off = U.auc_for(v, cat, foot), U.auc_for(v, off_sgmc, foot)
        rows.append(dict(feature=n, kind="line", auc_catalogue=a_cat, auc_off_sgmc=a_off,
                         leakage_flagged=bool(max(a_cat, a_off, 1 - a_cat, 1 - a_off) > 0.90)))
        log("canary line", n, round(a_cat, 4), round(a_off, 4))
        del v
    for arm in CANDIDATES:
        v = surface(arm)
        a_cat, a_off = U.auc_for(v, cat, foot), U.auc_for(v, off_sgmc, foot)
        rows.append(dict(feature=arm, kind="surface", auc_catalogue=a_cat, auc_off_sgmc=a_off,
                         leakage_flagged=bool(max(a_cat, a_off, 1 - a_cat, 1 - a_off) > 0.90)))
        log("canary surface", arm, round(a_cat, 4), round(a_off, 4))
        del v
    rep = dict(lane=LANE, evidence_class="COMPUTED", auc_ceiling=0.90, rows=rows,
               all_pass=bool(all(not r["leakage_flagged"] for r in rows)),
               preregistration_sha256=prereg_sha())
    EVID.mkdir(parents=True, exist_ok=True)
    (EVID / "canary.json").write_text(json.dumps(rep, indent=1) + "\n")
    return rep


# ---------------------------------------------------------------- holdout machinery
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
        del d_vis
        for arm, surf in arm_surfaces.items():
            dots = U.emit_dots(surf, allowed & (surf > 0))
            add(arm, dots.astype(np.float32), f)
            del dots
    return dict(terms=terms, per_fold=per_fold)


def random_component_split(cat: np.ndarray, foot: np.ndarray, seed: int) -> dict:
    return X.random_component_split(cat, foot, seed)


# ---------------------------------------------------------------- EXP-1
def run_exp1() -> dict:
    foot, cat, sgmc, off_sgmc, _ = U.load_grid()
    surfs = {a: surface(a) for a in ARMS}
    folds = list(spatial.folds(cat, foot, buffer_px=213))
    receipts = [f["receipt"] for f in folds]
    log("folds buffer 213", [r["truth_px"] for r in receipts])
    out = score_arms(surfs, folds, foot)
    del surfs
    gc.collect()
    scores_tmp = U.pooled(out["terms"], candidate="Z3")["scores"]
    winner = max(CANDIDATES, key=lambda a: scores_tmp[a]["dti"])
    summ = U.pooled(out["terms"], candidate=winner)
    junc_dti = float(scores_tmp["JUNC"]["dti"])
    r1 = dict(rebuilt_junc_pooled_dti=junc_dti, h31x_raw_final_reference=0.1661,
              abs_deviation=abs(junc_dti - 0.1661), within_0p01=bool(abs(junc_dti - 0.1661) <= 0.01))
    rep = dict(lane=LANE, experiment="EXP-1 screen", evaluator_version=ev.VERSION, buffer_px=213,
               fold_receipts=receipts, per_fold=out["per_fold"], pooled=summ, winner=winner,
               candidates=CANDIDATES, comparators=COMPARATORS, reproducibility_check_R1=r1,
               preregistration_sha256=prereg_sha())
    (EVID / "exp1_screen.json").write_text(json.dumps(rep, indent=1, default=float) + "\n")
    (CACHE / "exp1_winner.json").write_text(json.dumps(dict(winner=winner)) + "\n")
    for a in summ["scores"]:
        log("EXP1 pooled", a, round(summ["scores"][a]["dti"], 4), summ["scores"][a]["ci95"],
            "n=", summ["scores"][a]["withheld_positive_pixels"])
    log("EXP1 winner", winner, "R1", r1)
    return rep


def peer_files_z() -> list[dict]:
    peers = []
    for p in sorted(glob.glob(str(ROOT / "data/prior_audit/**/downloads/*.tif"), recursive=True)):
        peers.append(dict(id="focus:" + Path(p).parent.parent.parent.name + ":" + Path(p).name, path=p))
    for p in sorted(glob.glob(str(ROOT / "docs/downloads/*.tif"))):
        if "h31z" in p.lower():
            continue
        peers.append(dict(id="local:" + Path(p).name, path=p))
    return peers


def literal_witness_z(dots: np.ndarray, foot) -> dict:
    """Literal lattice diagnostic; restores the hash-pinned witness if absent."""
    from audit_shared_registry_stop import load_counterexample
    from gems57 import uniqueness
    pin, ref = load_counterexample(ROOT, restore=True)
    control = foot & np.isfinite(ref) & (ref > 0)
    ov = uniqueness.dot_overlap(dots.astype(np.float32), control.astype(np.float32))
    frac = float((distance_transform_edt(~control)[foot] <= 3.0).mean())
    return dict(witness=pin["counterexample"], lattice_dots=int(control.sum()),
                candidate_overlap_3px=float(ov), footprint_frac_within_3px_of_lattice=frac,
                reading="LITERAL broad-registry reading FAILS for any nonempty candidate because "
                        "the registered spacing-5 lattice covers the footprint; disclosed "
                        "diagnostic only (preregistration IR-U-02, H31-Z section 2).")


# ---------------------------------------------------------------- EXP-2
def run_exp2() -> dict:
    foot, cat, sgmc, off_sgmc, d_cat = U.load_grid()
    winner = json.loads((CACHE / "exp1_winner.json").read_text())["winner"]
    folds = list(spatial.folds(cat, foot, buffer_px=213))
    uses_scarpx = "SCARPX" in ARMS[winner]
    if uses_scarpx:
        coh_key, nocoh_key = winner + "_coh", winner + "_nocoh"
        surfs = {coh_key: surface(winner, variant="coh"),
                 nocoh_key: surface(winner, variant="nocoh")}
        for c in COMPARATORS:
            surfs[c] = surface(c)
        out = score_arms(surfs, folds, foot)
        del surfs
        gc.collect()
        tmp = U.pooled(out["terms"], candidate=coh_key)["scores"]
        d_coh, d_nocoh = float(tmp[coh_key]["dti"]), float(tmp[nocoh_key]["dti"])
        variant = "coh" if d_coh >= d_nocoh else "nocoh"
        final_key = coh_key if variant == "coh" else nocoh_key
        summ = U.pooled(out["terms"], candidate=final_key)
        ablation = dict(kind="coherence_on_vs_off", coh_pooled_dti=d_coh, nocoh_pooled_dti=d_nocoh,
                        kept_variant=variant, tie_rule="coh kept on tie (preregistered)")
        log("EXP2 ablation coh", round(d_coh, 4), "nocoh", round(d_nocoh, 4), "keep", variant)
    else:
        surfs = {winner: surface(winner)}
        for c in COMPARATORS:
            surfs[c] = surface(c)
        out = score_arms(surfs, folds, foot)
        del surfs
        gc.collect()
        variant, final_key = "single", winner
        summ = U.pooled(out["terms"], candidate=winner)
        ablation = dict(kind="none_single_line_winner", kept_variant=variant)
        log("EXP2 single-line winner, no coherence ablation")
    surf = surface(winner, variant="coh" if variant == "single" else variant)
    allowed = foot & (d_cat > B_PX) & (surf > 0)
    dots = U.emit_dots(surf, allowed)
    log("final dots", int(dots.sum()), "on_cat", int((dots & cat).sum()))
    np.save(CACHE / "final_dots.npy", dots)
    (CACHE / "final_choice.json").write_text(json.dumps(
        dict(arm=winner, variant=variant, final_key=final_key, lines=ARMS[winner]), indent=1) + "\n")
    U.peer_files = peer_files_z
    uniq = U.uniqueness_audit(surf, dots, foot)
    rep = dict(lane=LANE, experiment="EXP-2 coherence ablation + uniqueness", winner_from_exp1=winner,
               ablation=dict(**ablation, per_fold=out["per_fold"], pooled=summ, final_variant=final_key),
               uniqueness=uniq, literal_witness=literal_witness_z(dots, foot),
               preregistration_sha256=prereg_sha())
    (EVID / "exp2.json").write_text(json.dumps(rep, indent=1, default=float) + "\n")
    log("EXP2 discrete max overlap", uniq["discrete_max_final_overlap"], "topk",
        uniq["discrete_max_topk_overlap"], "max|rho| surf", uniq["max_abs_surface_spearman"],
        "dots", uniq["max_abs_dots_spearman"])
    return rep


def regime_sgmc(dots, off_sgmc, foot, slope, lo, hi) -> dict:
    return X.regime_sgmc(dots, off_sgmc, foot, slope, lo, hi)


# ---------------------------------------------------------------- EXP-3
def run_exp3() -> dict:
    foot, cat, sgmc, off_sgmc, d_cat = U.load_grid()
    choice = json.loads((CACHE / "final_choice.json").read_text())
    winner, variant = choice["arm"], choice["variant"]
    surf_variant = "coh" if variant == "single" else variant
    dots = np.load(CACHE / "final_dots.npy")
    split = random_component_split(cat, foot, CONFIRM_SEED)
    log("confirmation split", split["receipt"])
    surfs = {winner: surface(winner, variant=surf_variant),
             "JUNC": surface("JUNC"), "CTRL": surface("CTRL")}
    out = score_arms(surfs, [split], foot)
    del surfs
    gc.collect()
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
    del slope
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
                                 per_fold=out["per_fold"], pooled=conf),
               winner=winner, variant=variant, sgmc_full=sg, sgmc_quadrants=quad, projection=proj,
               preregistration_sha256=prereg_sha())
    (EVID / "exp3.json").write_text(json.dumps(rep, indent=1, default=float) + "\n")
    log("EXP3 confirm", winner, round(conf["scores"][winner]["dti"], 4),
        "JUNC", round(conf["scores"]["JUNC"]["dti"], 4), "CTRL", round(conf["scores"]["CTRL"]["dti"], 4))
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
    diffs = pooled_final["paired_differences"]
    pf = exp2["ablation"]["per_fold"]
    qwins_junc = sum(1 for a, b in zip(pf[final_key], pf["JUNC"]) if a["dti"] >= b["dti"])
    final_dti = pooled_final["scores"][final_key]
    conf_diffs = exp3["confirmation"]["pooled"]["paired_differences"]

    def pos(d):
        return bool(d and d["delta"] > 0 and d["ci95"][0] > 0)

    g3 = bool(pos(diffs.get("JUNC")) and pos(diffs.get("CTRL")) and pos(diffs.get("SLOPE"))
              and qwins_junc >= 3 and pos(conf_diffs.get("JUNC")))
    u = exp2["uniqueness"]
    g5 = bool(u["discrete_max_final_overlap"] is not None and u["discrete_max_final_overlap"] <= 0.70
              and (u["discrete_max_topk_overlap"] or 0) <= 0.70
              and (u["max_abs_surface_spearman"] or 0) <= 0.90
              and (u["max_abs_dots_spearman"] or 0) <= 0.90)
    return dict(
        G2_canary=bool(canary["all_pass"]),
        G3_holdout_efficacy=g3,
        G4_sgmc_discovery=bool(exp3["sgmc_full"]["candidate"]["dti"] >= exp3["sgmc_full"]["H33"]["dti"]),
        G5_uniqueness_discrete=g5,
        G6_projection_ge_02778=bool(exp3["projection"]["candidate"]["projection"] >= 0.2778),
        detail=dict(winner=winner, final_variant=final_key, final_holdout=final_dti,
                    exp1_screen_scores=exp1["pooled"]["scores"],
                    reproducibility_check_R1=exp1["reproducibility_check_R1"],
                    paired_vs_junc_screen=diffs.get("JUNC"),
                    paired_vs_ctrl_screen=diffs.get("CTRL"),
                    paired_vs_slope_screen=diffs.get("SLOPE"),
                    quadrant_wins_vs_junc=qwins_junc,
                    paired_vs_junc_confirmation=conf_diffs.get("JUNC"),
                    paired_vs_ctrl_confirmation=conf_diffs.get("CTRL"),
                    confirmation_scores=exp3["confirmation"]["pooled"]["scores"]),
    )


# ---------------------------------------------------------------- package
def run_package() -> dict:
    foot, cat, sgmc, off_sgmc, _ = U.load_grid()
    choice = json.loads((CACHE / "final_choice.json").read_text())
    exp2 = json.loads((EVID / "exp2.json").read_text())
    exp3 = json.loads((EVID / "exp3.json").read_text())
    gates = evaluate_gates()
    if not gates["G2_canary"]:
        raise SystemExit("STOP: leakage canary failed; packaging forbidden (preregistration §7)")
    if not gates["G5_uniqueness_discrete"]:
        # Still write the card-less STOP receipt; no TIFF is packaged as submittable/research.
        stop = dict(lane=LANE, session_branch=SESSION, verdict="negative", stop="duplicate",
                    gates=gates, ok_to_submit=False, ok_to_download_for_research=False,
                    instruction="STOP — duplicate under discrete-peer rule; no TIFF packaged.")
        (EVID / "STOP_duplicate.json").write_text(json.dumps(stop, indent=1, default=float) + "\n")
        log("STOP duplicate; no package")
        return stop
    dots = np.load(CACHE / "final_dots.npy")
    pred = np.where(foot, dots.astype(np.float32), 0.0).astype(np.float32)
    support_sha = hashlib.sha256(np.packbits(dots.ravel()).tobytes()).hexdigest()
    name = f"gemsdoe31-h31z-maxunion-{int(dots.sum())}-20261026-{support_sha[:8]}"
    hold = gates["detail"]["final_holdout"]
    variant_tag = "" if choice["variant"] == "single" else choice["variant"]
    lines_used = [("S0" if (n == "SCARPX" and choice["variant"] == "nocoh") else n) for n in choice["lines"]]
    note = (f"H31-Z {choice['arm']}{('-' + variant_tag) if variant_tag else ''} maxunion "
            f"{'+'.join(lines_used)} {int(dots.sum())}d B2 | HOLDOUT-DTI {hold['dti']:.4f} "
            f"n={hold['withheld_positive_pixels']} | {support_sha[:8]}")[:140]
    out_tif = ROOT / "docs/downloads" / f"{name}-zeros.tif"
    sample = ROOT / "data/sample_submission.tif"
    receipt = submission_writer.write_submission(
        out_tif, pred, sample, foot, note=note, name=name, catalogue=cat,
        metadata=dict(lane=LANE, arm=choice["arm"], variant=choice["variant"], lines=choice["lines"]))
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
        lane=LANE, session_branch=SESSION, generated_utc="2026-10-26",
        hypothesis=("H31-Z: catalogue-missing faults express per physiographic regime (range-front "
                    "junction, coherent LiDAR fan/range scarps, flat-basin gravity steps); a "
                    "max-of-ranks UNION of regime lines beats multiplicative corroboration, which "
                    "dilutes the strongest line, at a fixed 37,654-dot budget"),
        mechanism=(f"{choice['arm']} ({choice['variant']}): element-wise max of footprint percentile "
                   f"ranks of {'+'.join(lines_used)}; JUNC = H31-X directional slope-break (exact "
                   "reuse), SCARPX = LiDAR step strength x cross-cell structure-tensor coherence "
                   "(0.25 floor), GRAV = |iso_grav_anom_hg| rank; Poisson 2.8 px, 37,654 dots, "
                   "d(catalogue) > 2 px; no prior dots used"),
        non_fault_mimic=("Lahontan paleoshoreline benches/fan terraces (linear, coherent; no "
                         "elevation veto possible on detrended DEM), road/canal cuts, lava-flow "
                         "snouts, landslide toes, erosional pediment edges, unfaulted gravity "
                         "lithologic contacts, survey seams"),
        holdout_dti=dict(evidence_class="HOLDOUT-DTI", evaluator_version=ev.VERSION,
                         screen_final_surface=gates["detail"]["final_holdout"],
                         screen_paired_vs_junc=gates["detail"]["paired_vs_junc_screen"],
                         screen_paired_vs_ctrl=gates["detail"]["paired_vs_ctrl_screen"],
                         screen_paired_vs_slope=gates["detail"]["paired_vs_slope_screen"],
                         quadrant_wins_vs_junc=gates["detail"]["quadrant_wins_vs_junc"],
                         reproducibility_check_R1=gates["detail"]["reproducibility_check_R1"],
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
                        anchors="11 USER-REPORTED focus values; no organizer receipts; in-family calibration"),
        correlation_overlap_vs_registry=dict(
            scope="discrete dot-field peers: 9 focus sites (hash-verified fetch) + all local "
                  "GEMSDOE31 downloads; surface top-K checked pre-placement and final dots",
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
        submission_slots_used=0, experiments_used=3,
        instruction=("OK TO DOWNLOAD AND SUBMIT: all automated gates G1-G6 pass; owner uploads "
                     "manually (this repo never contacts DrivenData)."
                     if promote else
                     "DO NOT SUBMIT: at least one automated gate failed; research download only."),
        files=dict(zeros=f"docs/downloads/{out_tif.name}", nan=f"docs/downloads/{nan_tif.name}",
                   zip=f"docs/downloads/{out_tif.with_suffix('.zip').name}",
                   nan_zip=f"docs/downloads/{nan_zip.name}"),
        preregistration=PREREG, preregistration_sha256=prereg_sha(),
        evidence=dict(lines="evidence/h31z/lines.json", canary="evidence/h31z/canary.json",
                      exp1="evidence/h31z/exp1_screen.json", exp2="evidence/h31z/exp2.json",
                      exp3="evidence/h31z/exp3.json"),
    )
    (EVID / "run_card.json").write_text(json.dumps(card, indent=1, default=float) + "\n")
    (ROOT / "docs/downloads/h31z-run-card.json").write_text(json.dumps(card, indent=1, default=float) + "\n")
    (ROOT / "registry/h31z_current_run.json").write_text(json.dumps(card, indent=1, default=float) + "\n")
    log("PACKAGE", name, "verdict", card["verdict"], "gates",
        {k: v for k, v in gates.items() if k.startswith("G")})
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
        gc.collect()
    log("done", round(time.time() - t0), "s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
