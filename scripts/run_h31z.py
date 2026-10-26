#!/usr/bin/env python3
"""H31-Z lane runner: hard regime quota split (successor to H31-Y ROUTE duplicate STOP).

Frozen by knowledge/2026-10-26_h31z_quota_split_preregistration.md BEFORE any H31-Z
fitting. Lines, split emission, evaluator, SGMC/projection machinery are reused unchanged
from scripts/run_h31y_regimesplit.py (which itself reuses run_h31u/run_h31x and vendor/gems57).
This module only restricts the candidate set to {SPLIT50, SPLIT35}, uses a fresh
confirmation seed (3105), and writes its own evidence/run card under evidence/h31z/.

Stages: exp1, exp2, exp3, package. DrivenData is never contacted; nothing is uploaded.
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))

import run_h31u as U  # noqa: E402
import run_h31y_regimesplit as Y  # noqa: E402  (lines cache + split emission, frozen in Y preregistration)
from gems57 import evaluate_holdout as ev  # noqa: E402
from gems57 import metric as vmetric  # noqa: E402
from gems57 import spatial, submission_writer  # noqa: E402
from gemsdoe31.submission import validate_submission  # noqa: E402

SHAPE = Y.SHAPE
BUDGET = Y.BUDGET
B_PX = Y.B_PX
LANE = "H31-Z"
SESSION_BRANCH = "arena/579233d5-gemsdoe31"
CACHE = ROOT / "data" / "h31z"
EVID = ROOT / "evidence" / "h31z"
PREREG = "knowledge/2026-10-26_h31z_quota_split_preregistration.md"
CONFIRM_SEED = 3105
CANDIDATE_ARMS = ["SPLIT50", "SPLIT35"]
SCREEN_ARMS = ["SPLIT50", "SPLIT35", "JUNC", "PIED", "CTRL", "SLOPE"]
Y_SCREEN_EXPECTED = {"SPLIT50": 0.1473, "SPLIT35": 0.1349, "JUNC": 0.1661329569994631,
                     "PIED": 0.0705, "CTRL": 0.0671, "SLOPE": 0.0488}
log = U.log
sha256_file = U.sha256_file


def run_exp1() -> dict:
    foot, cat, sgmc, off_sgmc, _ = U.load_grid()
    surfs = Y.surfaces(foot)
    fixed = Y.load_fixed_refs(foot)
    folds = list(spatial.folds(cat, foot, buffer_px=213))
    out = Y.score_arms(SCREEN_ARMS, surfs, folds, foot, fixed)
    scores_tmp = U.pooled(out["terms"], candidate="SPLIT50")["scores"]
    replication = {
        a: dict(expected_from_h31y_exp1=v, got=scores_tmp[a]["dti"],
                abs_diff=abs(scores_tmp[a]["dti"] - v))
        for a, v in Y_SCREEN_EXPECTED.items()}
    replicated = bool(all(r["abs_diff"] < 5e-3 for r in replication.values())
                      and scores_tmp["JUNC"]["withheld_positive_pixels"] == 60988)
    log("REPLICATION vs H31-Y EXP1:", replicated, {a: round(r["abs_diff"], 6) for a, r in replication.items()})
    canary = json.loads((ROOT / "evidence/h31y_regimesplit/canary.json").read_text())
    winner = max(CANDIDATE_ARMS, key=lambda a: scores_tmp[a]["dti"])
    summ = U.pooled(out["terms"], candidate=winner)
    rep = dict(lane=LANE, experiment="EXP-1 screen replication (arms frozen from H31-Y)",
               evaluator_version=ev.VERSION, buffer_px=213,
               canary_cited=dict(source="evidence/h31y_regimesplit/canary.json", all_pass=canary["all_pass"],
                                 rows=canary["rows"]),
               fold_receipts=[f["receipt"] for f in folds], per_fold=out["per_fold"],
               emit_receipts=out["emit_receipts"], pooled=summ, winner=winner,
               replication_check=dict(rows=replication, reproduced=replicated,
                                      note="Screen outcome for shared arms was measured in H31-Y EXP-1; "
                                           "this re-run is a replication receipt (see Z preregistration)."),
               fixed_reference_caveat="REF_* dots were B2-pruned by their authors against the FULL "
                                      "catalogue: handicapped references only.")
    EVID.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    (EVID / "exp1_screen.json").write_text(json.dumps(rep, indent=1, default=float) + "\n")
    (CACHE / "exp1_winner.json").write_text(json.dumps(dict(winner=winner)) + "\n")
    for a in summ["scores"]:
        log("EXP1 pooled", a, round(summ["scores"][a]["dti"], 4), "n=", summ["scores"][a]["withheld_positive_pixels"])
    log("EXP1 winner", winner)
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


def run_exp2() -> dict:
    foot, cat, sgmc, off_sgmc, d_cat = U.load_grid()
    winner = json.loads((CACHE / "exp1_winner.json").read_text())["winner"]
    surfs = Y.surfaces(foot)
    folds = list(spatial.folds(cat, foot, buffer_px=213))
    arms = [winner, "JUNC", "CTRL", "SLOPE"]
    out_on = Y.score_arms(arms, surfs, folds, foot)
    out_off = Y.score_arms([winner], surfs, folds, foot, emit_kwargs=dict(restrict_pied=False))
    d_on = U.pooled(out_on["terms"], candidate=winner)["scores"][winner]["dti"]
    d_off = U.pooled(out_off["terms"], candidate=winner)["scores"][winner]["dti"]
    keep_on = bool(d_on >= d_off)
    log("EXP2 ablation restrict ON", round(d_on, 4), "OFF", round(d_off, 4), "keep_on", keep_on)
    allowed = foot & (d_cat > B_PX)
    pied_mask = Y.piedmont_mask()
    kwargs = {} if keep_on else dict(restrict_pied=False)
    dots, emit_rec = Y.emit_arm(winner, surfs, allowed, pied_mask, foot=foot, **kwargs)
    log("final dots", int(dots.sum()), "on_cat", int((dots & cat).sum()), emit_rec)
    np.save(CACHE / "final_dots.npy", dots)
    audit_surf = Y.route_surface(foot, routed=True)
    choice = dict(arm=winner, keep_regime_on=keep_on,
                  ablation_kind="PIED quota restricted to slope<=6deg vs unrestricted",
                  frac_junc=Y.SPLIT_FRAC[winner], emit_receipt=emit_rec)
    (CACHE / "final_choice.json").write_text(json.dumps(choice, indent=1) + "\n")
    U.peer_files = peer_files_z
    uniq = U.uniqueness_audit(audit_surf, dots, foot)
    if keep_on:
        pooled_final = U.pooled(out_on["terms"], candidate=winner)
        per_fold_final = out_on["per_fold"]
    else:
        merged = dict(out_off["terms"])
        for k in ("JUNC", "CTRL", "SLOPE"):
            merged[k] = out_on["terms"][k]
        pooled_final = U.pooled(merged, candidate=winner)
        per_fold_final = dict(out_on["per_fold"])
        per_fold_final[winner] = out_off["per_fold"][winner]
    rep = dict(lane=LANE, experiment="EXP-2 restriction ablation + uniqueness", winner_from_exp1=winner,
               ablation=dict(kind=choice["ablation_kind"], dti_on=d_on, dti_off=d_off, keep_on=keep_on,
                             per_fold_final=per_fold_final, pooled_final=pooled_final,
                             emit_receipts_off=out_off["emit_receipts"]),
               final_choice=choice, uniqueness=uniq, literal_witness=U.literal_witness(dots, foot),
               audit_surface_note="ROUTE blend proxy for Spearman/top-K only; final-dot overlap exact.")
    (EVID / "exp2.json").write_text(json.dumps(rep, indent=1, default=float) + "\n")
    log("EXP2 discrete max overlap", uniq["discrete_max_final_overlap"], "topk(proxy)",
        uniq["discrete_max_topk_overlap"], "max|rho| surf(proxy)", uniq["max_abs_surface_spearman"],
        "dots", uniq["max_abs_dots_spearman"])
    return rep


def run_exp3() -> dict:
    foot, cat, sgmc, off_sgmc, d_cat = U.load_grid()
    choice = json.loads((CACHE / "final_choice.json").read_text())
    winner, keep_on = choice["arm"], choice["keep_regime_on"]
    dots = np.load(CACHE / "final_dots.npy")
    surfs = Y.surfaces(foot)
    kwargs = {} if keep_on else dict(restrict_pied=False)
    split = Y.random_component_split(cat, foot, CONFIRM_SEED)
    log("confirmation split", split["receipt"])
    fixed = Y.load_fixed_refs(foot)
    out = Y.score_arms([winner, "JUNC", "CTRL", "SLOPE"], surfs, [split], foot, fixed,
                       emit_kwargs=kwargs)
    conf = U.pooled(out["terms"], candidate=winner)
    anchors = U.load_peer_dots_by_tag(foot)
    h33 = anchors["GEMSDOE32-h33-2-b2"][0]
    h27 = anchors["GEMSDOE28-h27-4"][0]
    slope = U.stack_band("det_elev_slope", foot)
    sg = dict(candidate=U.sgmc_score(dots, off_sgmc, foot), H33=U.sgmc_score(h33, off_sgmc, foot),
              H27=U.sgmc_score(h27, off_sgmc, foot))
    for k, dd in (("candidate", dots), ("H33", h33)):
        sg[k + "_piedmont_le6deg"] = Y.regime_sgmc(dd, off_sgmc, foot, slope, -1.0, 6.0)
        sg[k + "_mountain_gt6deg"] = Y.regime_sgmc(dd, off_sgmc, foot, slope, 6.0, 1e9)
    for k in Y.FIXED_REFS:
        if k in fixed:
            sg[k] = U.sgmc_score(fixed[k], off_sgmc, foot)
            sg[k + "_piedmont_le6deg"] = Y.regime_sgmc(fixed[k], off_sgmc, foot, slope, -1.0, 6.0)
            sg[k + "_mountain_gt6deg"] = Y.regime_sgmc(fixed[k], off_sgmc, foot, slope, 6.0, 1e9)
    # H31-Y ROUTE fixed dots as an additional full-footprint SGMC reference (not handicapped here)
    y_card = ROOT / "evidence/h31y_regimesplit/run_card.json"
    if y_card.is_file():
        yc = json.loads(y_card.read_text())
        yd, yn, yh = U.read_dots(str(ROOT / yc["files"]["zeros"]), foot)
        sg["REF_H31Y"] = U.sgmc_score(yd, off_sgmc, foot)
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
                                 per_fold=out["per_fold"], pooled=conf,
                                 emit_receipts=out["emit_receipts"]),
               winner=winner, keep_regime_on=keep_on, sgmc_full=sg, sgmc_quadrants=quad,
               projection=proj)
    (EVID / "exp3.json").write_text(json.dumps(rep, indent=1, default=float) + "\n")
    log("EXP3 confirm", winner, round(conf["scores"][winner]["dti"], 4),
        "JUNC", round(conf["scores"]["JUNC"]["dti"], 4),
        "CTRL", round(conf["scores"]["CTRL"]["dti"], 4))
    log("EXP3 SGMC cand", round(sg["candidate"]["dti"], 4), "H33", round(sg["H33"]["dti"], 4),
        "H31X", round(sg.get("REF_H31X", {}).get("dti", float("nan")), 4),
        "H31Y", round(sg.get("REF_H31Y", {}).get("dti", float("nan")), 4),
        "PROJECTION", round(proj["candidate"]["projection"], 4))
    return rep


def evaluate_gates() -> dict:
    exp1 = json.loads((EVID / "exp1_screen.json").read_text())
    exp2 = json.loads((EVID / "exp2.json").read_text())
    exp3 = json.loads((EVID / "exp3.json").read_text())
    winner = exp3["winner"]
    pooled_final = exp2["ablation"]["pooled_final"]
    d_ctrl = pooled_final["paired_differences"].get("CTRL")
    d_slope = pooled_final["paired_differences"].get("SLOPE")
    d_junc = pooled_final["paired_differences"].get("JUNC")
    pf = exp2["ablation"]["per_fold_final"]
    qwins = sum(1 for a, b in zip(pf[winner], pf["CTRL"]) if a["dti"] >= b["dti"])
    conf = exp3["confirmation"]["pooled"]["paired_differences"]

    def pos(d):
        return bool(d and d["delta"] > 0 and d["ci95"][0] > 0)

    u = exp2["uniqueness"]
    return dict(
        G2_canary=bool(exp1["canary_cited"]["all_pass"]),
        G3_holdout_efficacy=bool(pos(d_ctrl) and pos(d_slope) and qwins >= 3 and pos(conf.get("CTRL"))),
        G4_sgmc_discovery=bool(exp3["sgmc_full"]["candidate"]["dti"] >= exp3["sgmc_full"]["H33"]["dti"]),
        G5_uniqueness_discrete=bool(u["discrete_max_final_overlap"] is not None
                                    and u["discrete_max_final_overlap"] <= 0.70
                                    and (u["max_abs_surface_spearman"] or 0) <= 0.90
                                    and (u["max_abs_dots_spearman"] or 0) <= 0.90),
        G6_projection_ge_02778=bool(exp3["projection"]["candidate"]["projection"] >= 0.2778),
        detail=dict(winner=winner, final_holdout=pooled_final["scores"][winner],
                    replication_check=exp1["replication_check"],
                    exp1_screen_scores=exp1["pooled"]["scores"],
                    paired_vs_ctrl_screen=d_ctrl, paired_vs_slope_screen=d_slope,
                    paired_vs_junc_screen=d_junc, quadrant_wins_vs_ctrl=qwins,
                    paired_vs_ctrl_confirmation=conf.get("CTRL"),
                    paired_vs_junc_confirmation=conf.get("JUNC"),
                    confirmation_scores=exp3["confirmation"]["pooled"]["scores"],
                    topk_overlap_proxy_disclosed=u["discrete_max_topk_overlap"]),
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
    name = f"gemsdoe31-h31z-quotasplit-{choice['arm'].lower()}-{int(dots.sum())}-20261026-{support_sha[:8]}"
    hold = gates["detail"]["final_holdout"]
    note = (f"H31-Z {choice['arm']} hard quota JUNC+PIED(piedmont) {int(dots.sum())}d B2 | "
            f"HOLDOUT-DTI {hold['dti']:.4f} n={hold['withheld_positive_pixels']} | {support_sha[:8]}")[:140]
    out_tif = ROOT / "docs/downloads" / f"{name}-zeros.tif"
    sample = ROOT / "data/sample_submission.tif"
    receipt = submission_writer.write_submission(
        out_tif, pred, sample, foot, note=note, name=name, catalogue=cat,
        metadata=dict(lane=LANE, arm=choice["arm"], keep_regime_on=choice["keep_regime_on"],
                      frac_junc=choice.get("frac_junc")))
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
    gates = dict(G1_format=bool(vz["ok_to_upload_format_only"] and vn["ok_to_upload_format_only"]
                                 and int(dots.sum()) == BUDGET and int((dots & cat).sum()) == 0), **gates)
    promote = bool(all(gates[k] for k in gates if k.startswith("G")))
    u = exp2["uniqueness"]
    sg = exp3["sgmc_full"]
    card = dict(
        lane=LANE, session_branch=SESSION_BRANCH, generated_utc="2026-10-26",
        hypothesis="H31-Z: the catalogue-missing fault population is regime-composite (piedmont-junction "
                   "range fronts + buried piedmont basement faults); a HARD quota split between the "
                   "terrain specialist and a piedmont potential-field specialist covers more distinct "
                   "hidden truth per dot than either full field, and - unlike H31-Y's blended ROUTE "
                   "surface (92.4% dot overlap vs H31-X, duplicate STOP) - structurally bounds the "
                   "identical-dot share at the JUNC quota fraction.",
        mechanism=f"{choice['arm']}: JUNC quota frac={choice.get('frac_junc')} (H31-X X1 junction line "
                  f"verbatim) emitted first, then PIED quota (ASIG+BASE+GRAV geometric mean x second-line "
                  f"gate) "
                  + ("restricted to slope<=6deg" if choice["keep_regime_on"] else "unrestricted (ablation kept OFF)")
                  + f", excluding pixels within 2.8 px of JUNC dots; shared Poisson 2.8 px, "
                  f"{int(dots.sum())} dots, d(catalogue) > 2 px; emit receipt {choice['emit_receipt']}",
        non_fault_mimic="JUNC: erosional pediment edges, Lahontan shorelines, fan-terrace risers, lava-flow "
                        "snouts. PIED: tabular basalt-flow margins/caldera rims, unfaulted volcanic "
                        "lithologic contacts, conductive playa edges, magnetic survey seams.",
        holdout_dti=dict(evidence_class="HOLDOUT-DTI", evaluator_version=ev.VERSION,
                         screen_final_surface=gates["detail"]["final_holdout"],
                         screen_paired_vs_ctrl=gates["detail"]["paired_vs_ctrl_screen"],
                         screen_paired_vs_slope=gates["detail"]["paired_vs_slope_screen"],
                         screen_paired_vs_junc_incumbent=gates["detail"]["paired_vs_junc_screen"],
                         quadrant_wins_vs_ctrl=gates["detail"]["quadrant_wins_vs_ctrl"],
                         replication_check_vs_h31y=gates["detail"]["replication_check"],
                         confirmation_random_component_split=dict(
                             partition=exp3["confirmation"]["partition"],
                             scores=exp3["confirmation"]["pooled"]["scores"],
                             paired_differences=exp3["confirmation"]["pooled"]["paired_differences"])),
        sgmc_proxy=dict(evidence_class="COMPUTED off-catalogue USGS-SGMC proxy (not hidden truth)",
                        candidate=sg["candidate"], H33=sg["H33"], H27=sg["H27"],
                        regimes={k: v for k, v in sg.items() if "deg" in k},
                        fixed_refs={k: v for k, v in sg.items() if k.startswith("REF_") and "deg" not in k},
                        quadrants=exp3["sgmc_quadrants"]),
        projection=dict(evidence_class="PROJECTION (never a score)",
                        value=exp3["projection"]["candidate"]["projection"],
                        interval_approx=exp3["projection"]["candidate"]["interval_approx"],
                        loo_rmse=exp3["projection"]["loo_rmse"],
                        anchors="11 USER-REPORTED focus values; no organizer receipts; in-family calibration"),
        correlation_overlap_vs_registry=dict(
            scope="discrete dot-field peers: 9 focus sites (hash-verified fetch) + all local GEMSDOE31 "
                  "downloads incl. H31-X and H31-Y; exact check on final dots; ROUTE-blend proxy surface "
                  "for Spearman/top-K (disclosed)",
            discrete_max_final_overlap_3px=u["discrete_max_final_overlap"],
            discrete_max_topk_overlap_3px_proxy=u["discrete_max_topk_overlap"],
            max_abs_spearman_surface_proxy=u["max_abs_surface_spearman"],
            max_abs_spearman_dots=u["max_abs_dots_spearman"],
            literal_broad_registry=exp2["literal_witness"],
            unique_vs_discrete_peers=bool(gates["G5_uniqueness_discrete"])),
        raster_sha256=sha256_file(out_tif), raster_sha256_nan=sha256_file(nan_tif),
        zip_sha256=receipt["zip_sha256"], support_sha256=support_sha,
        validator=dict(zeros=dict(file=out_tif.name, ok=vz["ok_to_upload_format_only"],
                                   hard_failures=vz["hard_failures"], grid=vz["grid"]),
                       nan=dict(file=nan_tif.name, ok=vn["ok_to_upload_format_only"],
                                hard_failures=vn["hard_failures"], grid=vn["grid"]),
                       vendor_writer_receipt=Path(receipt["file"]).with_suffix(".json").name,
                       organizer_acceptance_verified=False),
        submission_name=name, note=note, note_chars=len(note),
        gates=gates, verdict="promote" if promote else "negative",
        ok_to_download_for_research=True, ok_to_submit=promote, slot_approved=promote,
        submission_slots_used=0,
        instruction=("OK TO DOWNLOAD AND SUBMIT: all automated gates G1-G6 pass; owner uploads manually on "
                     "DrivenData (this repo never contacts DrivenData). Selector step decides primary vs "
                     "H31-X/H31-Y." if promote else
                     "DO NOT SUBMIT: at least one automated gate failed (see gates); research download only."),
        files=dict(zeros=f"docs/downloads/{out_tif.name}", nan=f"docs/downloads/{nan_tif.name}",
                   zip=f"docs/downloads/{out_tif.with_suffix('.zip').name}", nan_zip=f"docs/downloads/{nan_zip.name}"),
        preregistration=PREREG,
        evidence=dict(lines="evidence/h31y_regimesplit/lines.json (reused cache)", canary="evidence/h31y_regimesplit/canary.json (cited)",
                      exp1="evidence/h31z/exp1_screen.json", exp2="evidence/h31z/exp2.json",
                      exp3="evidence/h31z/exp3.json"),
    )
    (EVID / "run_card.json").write_text(json.dumps(card, indent=1, default=float) + "\n")
    (ROOT / "docs/downloads/h31z-run-card.json").write_text(json.dumps(card, indent=1, default=float) + "\n")
    (ROOT / "registry/h31z_current_run.json").write_text(json.dumps(card, indent=1, default=float) + "\n")
    log("PACKAGE", name, "verdict", card["verdict"], "gates", {k: v for k, v in gates.items() if k.startswith("G")})
    log("sha256 zeros", card["raster_sha256"])
    return card


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("stage", choices=["exp1", "exp2", "exp3", "package", "all"])
    args = ap.parse_args()
    stages = ["exp1", "exp2", "exp3", "package"] if args.stage == "all" else [args.stage]
    t0 = time.time()
    CACHE.mkdir(parents=True, exist_ok=True)
    EVID.mkdir(parents=True, exist_ok=True)
    for s in stages:
        log("=== STAGE", s, "===", round(time.time() - t0), "s elapsed")
        {"exp1": run_exp1, "exp2": run_exp2, "exp3": run_exp3, "package": run_package}[s]()
    log("done", round(time.time() - t0), "s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
