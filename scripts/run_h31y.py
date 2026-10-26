#!/usr/bin/env python3
"""H31-Y lane runner: regime budget-split (piedmont-junction x buried-basement piedmont).

Frozen by knowledge/2026-10-26_h31y_regime_split_preregistration.md BEFORE any fitting.
Reuses the shared template unchanged (vendor/gems57: spatial.folds, evaluate_holdout =
gems57-pooled-hide-v2, metric, uniqueness, submission_writer), the H31-U helper functions
(grid loading, cleaning, ranking, Poisson emission, peer uniqueness audit, SGMC scoring,
anchor-inversion projection) and the H31-X junction-line implementation verbatim. New here
only: the PIED potential-field/basement specialist lines, the quota-split and routed
emission geometries, and this lane's receipts/run card.

Stages: lines, canary, exp1, exp2, exp3, package (each writes a JSON receipt under
evidence/h31y/). DrivenData is never contacted; nothing is uploaded.
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

import run_h31u as U  # noqa: E402  (shared helpers; nothing lane-specific)
import run_h31x as X  # noqa: E402  (junction line implementation, reused verbatim)
from gems57 import evaluate_holdout as ev  # noqa: E402
from gems57 import metric as vmetric  # noqa: E402
from gems57 import spatial, submission_writer  # noqa: E402
from gemsdoe31.submission import validate_submission  # noqa: E402
from gemsdoe31.submodular_emit import poisson_disk_emit  # noqa: E402

SHAPE = (3730, 3292)
BUDGET = 37_654
MIN_DIST = 2.8
B_PX = 2.0
LANE = "H31-Y"
SESSION_BRANCH = "arena/579233d5-gemsdoe31"
CACHE = ROOT / "data" / "h31y"
EVID = ROOT / "evidence" / "h31y"
PREREG = "knowledge/2026-10-26_h31y_regime_split_preregistration.md"
LINES = ["JUNC_RAW", "ASIG", "BASE", "GRAV", "CTRL", "SLOPE"]
PIEDMONT_MAX_DEG = 6.0
CONFIRM_SEED = 3104
# candidate arms eligible for promotion (SPLIT65REF is scored for information only)
CANDIDATE_ARMS = ["SPLIT50", "SPLIT35", "ROUTE"]
SCREEN_ARMS = ["JUNC", "PIED", "SPLIT50", "SPLIT35", "ROUTE", "CTRL", "SLOPE", "SPLIT65REF"]
FIXED_REFS = {
    "REF_H33": "data/prior_audit/GEMSDOE32/docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif",
    "REF_H31X": "docs/downloads/gemsdoe31-h31x-piedmont-junction-37654-20261026-5a956da9-zeros.tif",
    "REF_H31T": "docs/downloads/gemsdoe31-h31t-transtension-dinkelbach-20261025-b37654-zeros.tif",
}
log = U.log
sha256_file = U.sha256_file


# ---------------------------------------------------------------- lines
def build_lines() -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    EVID.mkdir(parents=True, exist_ok=True)
    foot, cat, *_ = U.load_grid()
    mm = np.memmap(CACHE / "lines.f32", dtype=np.float32, mode="w+", shape=(len(LINES),) + SHAPE)
    t0 = time.time()

    def band(n):
        return U.clean(U.stack_band(n, foot), foot)

    # JUNC_RAW: H31-X X1 formula verbatim (sigma 1.5, window 1/3/15/25 deg, no NMS)
    z = band("det_elev")
    s = band("det_elev_slope")
    j_raw = X.junction_line(z, s, foot, nms=False)
    mm[LINES.index("JUNC_RAW")] = U.rank01(j_raw, foot)
    log("JUNC_RAW done", round(time.time() - t0), "s; nonzero frac", float((j_raw[foot] > 0).mean()))
    del z, j_raw
    # regime mask from the same cleaned slope used by the junction window
    pied_mask = foot & (s <= PIEDMONT_MAX_DEG)
    np.save(CACHE / "piedmont_mask.npy", pied_mask)
    mm[LINES.index("SLOPE")] = U.rank01(s, foot)
    del s
    # ASIG: analytic-signal amplitude of the magnetic field (hg = horizontal gradient magnitude)
    hg = band("tmi_hg")
    vg = band("tmi_vg")
    mm[LINES.index("ASIG")] = U.rank01(np.hypot(hg, vg).astype(np.float32), foot)
    mm[LINES.index("CTRL")] = U.rank01(hg, foot)
    del hg, vg
    log("ASIG/CTRL done", round(time.time() - t0))
    # BASE: H31-U definition verbatim (basement depth + conductance gradients + gravity slope)
    parts = [U.rank01(U.gradmag(band("depth_to_base_surf"), 1.5), foot),
             U.rank01(U.gradmag(band("cond_surf"), 1.5), foot),
             U.rank01(np.abs(band("iso_grav_anom_slope")), foot)]
    mm[LINES.index("BASE")] = U.geomean_rank(parts)
    del parts
    mm[LINES.index("GRAV")] = U.rank01(np.abs(band("iso_grav_anom_hg")), foot)
    mm.flush()
    log("BASE/GRAV done", round(time.time() - t0))
    receipts = {}
    for i, n in enumerate(LINES):
        a = np.asarray(mm[i])[foot]
        receipts[n] = dict(min=float(a.min()), max=float(a.max()), mean=float(a.mean()),
                           frac_zero=float((a == 0).mean()))
    meta = dict(lane=LANE, lines=LINES, shape=list(SHAPE), piedmont_max_deg=PIEDMONT_MAX_DEG,
                piedmont_pixels=int(pied_mask.sum()), footprint_pixels=int(foot.sum()),
                receipts=receipts,
                note="label-free footprint percentile-rank lines; JUNC_RAW = H31-X X1 verbatim; see preregistration")
    (CACHE / "lines.json").write_text(json.dumps(meta, indent=1) + "\n")
    (EVID / "lines.json").write_text(json.dumps(meta, indent=1) + "\n")
    log("lines written", round(time.time() - t0), "s; piedmont px", meta["piedmont_pixels"])
    return meta


def load_line(name: str) -> np.ndarray:
    mm = np.memmap(CACHE / "lines.f32", dtype=np.float32, mode="r", shape=(len(LINES),) + SHAPE)
    return np.asarray(mm[LINES.index(name)], dtype=np.float32).copy()


def piedmont_mask() -> np.ndarray:
    return np.load(CACHE / "piedmont_mask.npy")


def pied_surface() -> np.ndarray:
    """PIED = geometric mean of ASIG/BASE/GRAV ranks x second-line gate (frozen)."""
    parts = [load_line(n) for n in ("ASIG", "BASE", "GRAV")]
    g = U.geomean_rank(parts)
    second = np.partition(np.stack(parts), -2, axis=0)[-2]
    return (g * second).astype(np.float32)


def route_surface(foot, routed: bool = True) -> np.ndarray:
    """ROUTE blend exp(w ln JUNC + (1-w) ln PIED); w from cleaned slope, or w=0.5 if not routed."""
    j = load_line("JUNC_RAW")
    p = pied_surface()
    if routed:
        s = U.clean(U.stack_band("det_elev_slope", foot), foot)
        w = np.clip((s - 3.0) / 6.0, 0.0, 1.0).astype(np.float32)
        del s
    else:
        w = np.full(j.shape, 0.5, np.float32)
    out = np.exp(w * np.log(np.maximum(j, 1e-3)) + (1.0 - w) * np.log(np.maximum(p, 1e-3)))
    return out.astype(np.float32)


def surfaces(foot) -> dict:
    """All single-surface arms needed by the screen (split arms are emission geometries)."""
    return {
        "JUNC": load_line("JUNC_RAW"),
        "PIED": pied_surface(),
        "ROUTE": route_surface(foot, routed=True),
        "CTRL": load_line("CTRL"),
        "SLOPE": load_line("SLOPE"),
    }


# ---------------------------------------------------------------- emission
def emit_split(junc, pied, allowed, pied_mask, frac_j: float, *, restrict_pied: bool = True,
               n: int = BUDGET) -> tuple[np.ndarray, dict]:
    """Quota-split emission with one shared 2.8 px exclusion (frozen in the preregistration).

    JUNC quota first; PIED quota second excluding pixels within MIN_DIST of JUNC dots.
    Shortfalls are topped up from the other surface (JUNC first) and recorded.
    """
    n_j = int(round(frac_j * n))
    n_p = n - n_j
    dots_j = poisson_disk_emit(junc, allowed & (junc > 0), n_j, min_dist_px=MIN_DIST, max_pool=400_000)
    got_j = int(dots_j.sum())
    d = distance_transform_edt(~dots_j)
    a_p = allowed & (pied > 0) & (d >= MIN_DIST)
    if restrict_pied:
        a_p &= pied_mask
    dots_p = poisson_disk_emit(pied, a_p, n_p, min_dist_px=MIN_DIST, max_pool=400_000)
    got_p = int(dots_p.sum())
    dots = dots_j | dots_p
    topup_j = topup_p = 0
    short = n - int(dots.sum())
    if short > 0:  # top up from JUNC under the same exclusion
        d = distance_transform_edt(~dots)
        extra = poisson_disk_emit(junc, allowed & (junc > 0) & (d >= MIN_DIST) & ~dots, short,
                                  min_dist_px=MIN_DIST, max_pool=400_000)
        topup_j = int(extra.sum())
        dots |= extra
        short = n - int(dots.sum())
    if short > 0:  # then from PIED (unrestricted regime only as last resort)
        d = distance_transform_edt(~dots)
        extra = poisson_disk_emit(pied, allowed & (pied > 0) & (d >= MIN_DIST) & ~dots, short,
                                  min_dist_px=MIN_DIST, max_pool=400_000)
        topup_p = int(extra.sum())
        dots |= extra
    return dots, dict(quota_junc=n_j, quota_pied=n_p, emitted_junc=got_j, emitted_pied=got_p,
                      topup_junc=topup_j, topup_pied=topup_p, emitted_total=int(dots.sum()))


SPLIT_FRAC = {"SPLIT50": 0.50, "SPLIT35": 0.35, "SPLIT65REF": 0.65}


def emit_arm(arm: str, surfs: dict, allowed, pied_mask, *, restrict_pied: bool = True,
             routed: bool = True, foot=None) -> tuple[np.ndarray, dict]:
    if arm in SPLIT_FRAC:
        return emit_split(surfs["JUNC"], surfs["PIED"], allowed, pied_mask, SPLIT_FRAC[arm],
                          restrict_pied=restrict_pied)
    if arm == "ROUTE":
        surf = surfs["ROUTE"] if routed else route_surface(foot, routed=False)
        dots = U.emit_dots(surf, allowed & (surf > 0))
        return dots, dict(emitted_total=int(dots.sum()), routed=routed)
    surf = surfs[arm]
    dots = U.emit_dots(surf, allowed & (surf > 0))
    return dots, dict(emitted_total=int(dots.sum()))


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
    for name, v in (("PIED", pied_surface()), ("ROUTE", route_surface(foot, routed=True))):
        a_cat, a_off = U.auc_for(v, cat, foot), U.auc_for(v, off_sgmc, foot)
        rows.append(dict(feature=name, kind="surface", auc_catalogue=a_cat, auc_off_sgmc=a_off,
                         leakage_flagged=bool(max(a_cat, a_off, 1 - a_cat, 1 - a_off) > 0.90)))
        log("canary surface", name, round(a_cat, 4), round(a_off, 4))
        del v
    rep = dict(lane=LANE, evidence_class="COMPUTED", auc_ceiling=0.90, rows=rows,
               all_pass=bool(all(not r["leakage_flagged"] for r in rows)))
    EVID.mkdir(parents=True, exist_ok=True)
    (EVID / "canary.json").write_text(json.dumps(rep, indent=1) + "\n")
    return rep


# ---------------------------------------------------------------- holdout machinery
def score_arms(arm_names: list[str], surfs: dict, folds: list, foot,
               fixed: dict | None = None, emit_kwargs: dict | None = None) -> dict:
    """Per-fold visible-B2 emission for arms; fixed dot sets scored as-is (handicapped)."""
    terms: dict[str, np.ndarray] = {}
    per_fold: dict[str, list] = {a: [] for a in list(arm_names) + list(fixed or {})}
    emit_receipts: dict[str, list] = {a: [] for a in arm_names}
    pied_mask = piedmont_mask()

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
        for arm in arm_names:
            dots, rec = emit_arm(arm, surfs, allowed, pied_mask, foot=foot, **(emit_kwargs or {}))
            emit_receipts[arm].append(rec)
            add(arm, dots.astype(np.float32), f)
        for name, dots in (fixed or {}).items():
            add(name, dots.astype(np.float32), f)
    return dict(terms=terms, per_fold=per_fold, emit_receipts=emit_receipts)


def load_fixed_refs(foot) -> dict[str, np.ndarray]:
    out = {}
    for k, rel in FIXED_REFS.items():
        p = ROOT / rel
        if not p.is_file():
            log("fixed ref missing (skipped)", k, rel)
            continue
        dots, n, h = U.read_dots(str(p), foot)
        out[k] = dots
        log("fixed ref", k, n, "dots", h[:12])
    return out


def random_component_split(cat: np.ndarray, foot: np.ndarray, seed: int) -> dict:
    return X.random_component_split(cat, foot, seed)


# ---------------------------------------------------------------- EXP-1
def run_exp1() -> dict:
    foot, cat, sgmc, off_sgmc, _ = U.load_grid()
    surfs = surfaces(foot)
    fixed = load_fixed_refs(foot)
    folds = list(spatial.folds(cat, foot, buffer_px=213))
    receipts = [f["receipt"] for f in folds]
    log("folds buffer 213", [r["truth_px"] for r in receipts])
    out = score_arms(SCREEN_ARMS, surfs, folds, foot, fixed)
    scores_tmp = U.pooled(out["terms"], candidate="JUNC")["scores"]
    # replication check vs H31-X X1-raw screen (same evaluator/folds/surface formula)
    rep_junc = scores_tmp["JUNC"]
    replication = dict(
        expected_dti=0.1661329569994631, expected_ci95=[0.14985841711445055, 0.18210651085093407],
        got_dti=rep_junc["dti"], got_ci95=rep_junc["ci95"],
        withheld=rep_junc["withheld_positive_pixels"],
        abs_diff=abs(rep_junc["dti"] - 0.1661329569994631),
        reproduced=bool(abs(rep_junc["dti"] - 0.1661329569994631) < 5e-3
                        and rep_junc["withheld_positive_pixels"] == 60988),
        source="evidence/h31x/run_card.json screen_final_surface (EXP-2 raw variant, same folds)")
    log("REPLICATION JUNC vs H31-X:", replication)
    winner = max(CANDIDATE_ARMS, key=lambda a: scores_tmp[a]["dti"])
    summ = U.pooled(out["terms"], candidate=winner)
    rep = dict(lane=LANE, experiment="EXP-1 screen", evaluator_version=ev.VERSION, buffer_px=213,
               fold_receipts=receipts, per_fold=out["per_fold"], emit_receipts=out["emit_receipts"],
               pooled=summ, winner=winner, replication_check=replication,
               split65ref_note="SPLIT65REF is a reference arm only (65% JUNC quota risks the 70% "
                               "duplicate rule vs H31-X); never eligible for promotion in this lane.",
               fixed_reference_caveat="REF_* dots were B2-pruned by their authors against the FULL "
                                      "catalogue (including withheld segments): handicapped references "
                                      "only, never a promotion comparator.")
    (EVID / "exp1_screen.json").write_text(json.dumps(rep, indent=1, default=float) + "\n")
    (CACHE / "exp1_winner.json").write_text(json.dumps(dict(winner=winner)) + "\n")
    for a in summ["scores"]:
        log("EXP1 pooled", a, round(summ["scores"][a]["dti"], 4), summ["scores"][a]["ci95"],
            "n=", summ["scores"][a]["withheld_positive_pixels"])
    log("EXP1 winner", winner)
    if not replication["reproduced"]:
        log("WARNING: JUNC replication did NOT reproduce H31-X within tolerance - diagnose before use")
    return rep


# ---------------------------------------------------------------- EXP-2
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
    surfs = surfaces(foot)
    folds = list(spatial.folds(cat, foot, buffer_px=213))
    # ablation: regime restriction/routing ON (= screen geometry) vs OFF
    arms = [winner, "JUNC", "CTRL", "SLOPE"]
    out_on = score_arms(arms, surfs, folds, foot)
    if winner == "ROUTE":
        out_off = score_arms([winner], surfs, folds, foot, emit_kwargs=dict(routed=False))
        ablation_kind = "slope-routed exponent vs fixed 50/50 log-blend"
    else:
        out_off = score_arms([winner], surfs, folds, foot, emit_kwargs=dict(restrict_pied=False))
        ablation_kind = "PIED quota restricted to slope<=6deg vs unrestricted"
    d_on = U.pooled(out_on["terms"], candidate=winner)["scores"][winner]["dti"]
    d_off = U.pooled(out_off["terms"], candidate=winner)["scores"][winner]["dti"]
    keep_on = bool(d_on >= d_off)
    chosen_terms = out_on if keep_on else None
    log("EXP2 ablation", ablation_kind, "ON", round(d_on, 4), "OFF", round(d_off, 4), "keep_on", keep_on)
    # final emission on the full catalogue with the kept geometry
    allowed = foot & (d_cat > B_PX)
    pied_mask = piedmont_mask()
    kwargs = {} if keep_on else (dict(routed=False) if winner == "ROUTE" else dict(restrict_pied=False))
    dots, emit_rec = emit_arm(winner, surfs, allowed, pied_mask, foot=foot, **kwargs)
    log("final dots", int(dots.sum()), "on_cat", int((dots & cat).sum()), emit_rec)
    np.save(CACHE / "final_dots.npy", dots)
    audit_surf = route_surface(foot, routed=True)  # disclosed audit proxy for quota emissions
    np.save(CACHE / "audit_surface.npy", audit_surf)
    choice = dict(arm=winner, keep_regime_on=keep_on, ablation_kind=ablation_kind,
                  frac_junc=SPLIT_FRAC.get(winner), emit_receipt=emit_rec)
    (CACHE / "final_choice.json").write_text(json.dumps(choice, indent=1) + "\n")
    U.peer_files = peer_files_y          # same audit code; only the self-exclusion token differs
    uniq = U.uniqueness_audit(audit_surf, dots, foot)
    # pooled summary for the packaged geometry (ON terms are complete; OFF needs controls re-pooled)
    if keep_on:
        pooled_final = U.pooled(chosen_terms["terms"], candidate=winner)
        per_fold_final = out_on["per_fold"]
    else:
        merged = dict(out_off["terms"])
        for k in ("JUNC", "CTRL", "SLOPE"):
            merged[k] = out_on["terms"][k]
        pooled_final = U.pooled(merged, candidate=winner)
        per_fold_final = dict(out_on["per_fold"])
        per_fold_final[winner] = out_off["per_fold"][winner]
    rep = dict(lane=LANE, experiment="EXP-2 regime ablation + uniqueness", winner_from_exp1=winner,
               ablation=dict(kind=ablation_kind, dti_on=d_on, dti_off=d_off, keep_on=keep_on,
                             per_fold_final=per_fold_final, pooled_final=pooled_final,
                             emit_receipts_off=out_off["emit_receipts"]),
               final_choice=choice, uniqueness=uniq, literal_witness=U.literal_witness(dots, foot),
               audit_surface_note="Quota emissions have no single surface; Spearman/top-K uniqueness "
                                  "numbers use the ROUTE blend of the same lines as a disclosed proxy. "
                                  "Final-dot 3-px overlap (the owner's rule) is exact.")
    (EVID / "exp2.json").write_text(json.dumps(rep, indent=1, default=float) + "\n")
    log("EXP2 discrete max overlap", uniq["discrete_max_final_overlap"], "topk(proxy)",
        uniq["discrete_max_topk_overlap"], "max|rho| surf(proxy)", uniq["max_abs_surface_spearman"],
        "dots", uniq["max_abs_dots_spearman"])
    return rep


# ---------------------------------------------------------------- EXP-3
def regime_sgmc(dots, off_sgmc, foot, slope, lo, hi) -> dict:
    return X.regime_sgmc(dots, off_sgmc, foot, slope, lo, hi)


def run_exp3() -> dict:
    foot, cat, sgmc, off_sgmc, d_cat = U.load_grid()
    choice = json.loads((CACHE / "final_choice.json").read_text())
    winner, keep_on = choice["arm"], choice["keep_regime_on"]
    dots = np.load(CACHE / "final_dots.npy")
    surfs = surfaces(foot)
    kwargs = {} if keep_on else (dict(routed=False) if winner == "ROUTE" else dict(restrict_pied=False))
    # (a) untouched confirmation: random whole-component split, fresh seed 3104
    split = random_component_split(cat, foot, CONFIRM_SEED)
    log("confirmation split", split["receipt"])
    fixed = load_fixed_refs(foot)
    out = score_arms([winner, "JUNC", "CTRL", "SLOPE"], surfs, [split], foot, fixed,
                     emit_kwargs=kwargs)
    conf = U.pooled(out["terms"], candidate=winner)
    # (b) SGMC proxy: full, quadrants, slope regimes; references recomputed same code same day
    anchors = U.load_peer_dots_by_tag(foot)
    h33 = anchors["GEMSDOE32-h33-2-b2"][0]
    h27 = anchors["GEMSDOE28-h27-4"][0]
    slope = U.stack_band("det_elev_slope", foot)
    sg = dict(candidate=U.sgmc_score(dots, off_sgmc, foot), H33=U.sgmc_score(h33, off_sgmc, foot),
              H27=U.sgmc_score(h27, off_sgmc, foot))
    for k, dd in (("candidate", dots), ("H33", h33)):
        sg[k + "_piedmont_le6deg"] = regime_sgmc(dd, off_sgmc, foot, slope, -1.0, 6.0)
        sg[k + "_mountain_gt6deg"] = regime_sgmc(dd, off_sgmc, foot, slope, 6.0, 1e9)
    for k in FIXED_REFS:
        if k in fixed:
            sg[k] = U.sgmc_score(fixed[k], off_sgmc, foot)
            sg[k + "_piedmont_le6deg"] = regime_sgmc(fixed[k], off_sgmc, foot, slope, -1.0, 6.0)
            sg[k + "_mountain_gt6deg"] = regime_sgmc(fixed[k], off_sgmc, foot, slope, 6.0, 1e9)
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
        "CTRL", round(conf["scores"]["CTRL"]["dti"], 4),
        "SLOPE", round(conf["scores"]["SLOPE"]["dti"], 4))
    log("EXP3 SGMC cand", round(sg["candidate"]["dti"], 4), "H33", round(sg["H33"]["dti"], 4),
        "H31X", round(sg.get("REF_H31X", {}).get("dti", float("nan")), 4),
        "PROJECTION", round(proj["candidate"]["projection"], 4), "+/-", round(2 * proj["loo_rmse"], 4))
    return rep


# ---------------------------------------------------------------- gates + package
def evaluate_gates() -> dict:
    canary = json.loads((EVID / "canary.json").read_text())
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
    final_dti = pooled_final["scores"][winner]
    conf = exp3["confirmation"]["pooled"]["paired_differences"]
    c_ctrl = conf.get("CTRL")
    c_junc = conf.get("JUNC")

    def pos(d):
        return bool(d and d["delta"] > 0 and d["ci95"][0] > 0)

    g3 = bool(pos(d_ctrl) and pos(d_slope) and qwins >= 3 and pos(c_ctrl))
    u = exp2["uniqueness"]
    g5 = bool(u["discrete_max_final_overlap"] is not None and u["discrete_max_final_overlap"] <= 0.70
              and (u["max_abs_surface_spearman"] or 0) <= 0.90 and (u["max_abs_dots_spearman"] or 0) <= 0.90)
    return dict(
        G2_canary=bool(canary["all_pass"]),
        G3_holdout_efficacy=g3,
        G4_sgmc_discovery=bool(exp3["sgmc_full"]["candidate"]["dti"] >= exp3["sgmc_full"]["H33"]["dti"]),
        G5_uniqueness_discrete=g5,
        G6_projection_ge_02778=bool(exp3["projection"]["candidate"]["projection"] >= 0.2778),
        detail=dict(winner=winner, final_holdout=final_dti,
                    replication_check=exp1["replication_check"],
                    exp1_screen_scores=exp1["pooled"]["scores"],
                    paired_vs_ctrl_screen=d_ctrl, paired_vs_slope_screen=d_slope,
                    paired_vs_junc_screen=d_junc,
                    quadrant_wins_vs_ctrl=qwins, paired_vs_ctrl_confirmation=c_ctrl,
                    paired_vs_junc_confirmation=c_junc,
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
    arm_tag = choice["arm"].lower()
    name = f"gemsdoe31-h31y-regimesplit-{arm_tag}-{int(dots.sum())}-20261026-{support_sha[:8]}"
    hold = gates["detail"]["final_holdout"]
    note = (f"H31-Y {choice['arm']} regime-split JUNC+PIED {int(dots.sum())}d B2 | "
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
        hypothesis="H31-Y: the catalogue-missing fault population is regime-composite - range-bounding "
                   "faults at the piedmont-junction slope break plus buried piedmont faults with no "
                   "terrain expression that offset magnetic basement / basin thickness; a fixed-quota "
                   "budget split between a terrain specialist and a potential-field specialist covers "
                   "more distinct hidden truth per dot than either full field (kernel-max TPw).",
        mechanism=f"{choice['arm']}: JUNC (H31-X X1 piedmont-junction line verbatim, recomputed) + PIED "
                  f"(geometric mean x second-line gate of ASIG analytic signal, BASE basement/conductance "
                  f"gradients, GRAV gravity HG ranks); "
                  + (f"quota frac_junc={choice.get('frac_junc')}, PIED "
                     + ("restricted to slope<=6deg" if choice["keep_regime_on"] else "unrestricted (ablation kept OFF)")
                     if choice["arm"] != "ROUTE" else
                     ("slope-routed log-blend w=clip((slope-3)/6,0,1)" if choice["keep_regime_on"]
                      else "fixed 50/50 log-blend (ablation kept unrouted)"))
                  + f"; shared Poisson 2.8 px exclusion, {int(dots.sum())} dots, d(catalogue) > 2 px; "
                  + f"emit receipt {choice['emit_receipt']}",
        non_fault_mimic="JUNC: erosional pediment edges, Lahontan shorelines, fan-terrace risers, lava-flow "
                        "snouts. PIED: tabular basalt-flow margins/caldera rims (analytic-signal highs with "
                        "no basement step), unfaulted volcanic lithologic contacts, conductive playa edges, "
                        "magnetic survey seams.",
        holdout_dti=dict(evidence_class="HOLDOUT-DTI", evaluator_version=ev.VERSION,
                         screen_final_surface=gates["detail"]["final_holdout"],
                         screen_paired_vs_ctrl=gates["detail"]["paired_vs_ctrl_screen"],
                         screen_paired_vs_slope=gates["detail"]["paired_vs_slope_screen"],
                         screen_paired_vs_junc_incumbent=gates["detail"]["paired_vs_junc_screen"],
                         quadrant_wins_vs_ctrl=gates["detail"]["quadrant_wins_vs_ctrl"],
                         replication_check_junc_vs_h31x=gates["detail"]["replication_check"],
                         confirmation_random_component_split=dict(
                             partition=exp3["confirmation"]["partition"],
                             scores=exp3["confirmation"]["pooled"]["scores"],
                             paired_differences=exp3["confirmation"]["pooled"]["paired_differences"]),
                         fixed_reference_caveat=json.loads((EVID / "exp1_screen.json").read_text())[
                             "fixed_reference_caveat"]),
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
                  "downloads; exact check on final dots; ROUTE-blend proxy surface for Spearman/top-K "
                  "(disclosed in evidence/h31y/exp2.json)",
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
                     "H31-X." if promote else
                     "DO NOT SUBMIT: at least one automated gate failed (see gates); research download only."),
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
