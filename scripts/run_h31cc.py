#!/usr/bin/env python3
"""H31-CC lane: cover-concealed basement step. Frozen by the preregistration.

Uses the shared template evaluator and writer. Does not contact DrivenData.
Stops on a submission-raster duplicate before packaging. The calibration lattice
is measured and disclosed; it cannot grant upload permission.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt, gaussian_filter, label
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "vendor"), str(ROOT / "scripts")]

from gems57 import evaluate_holdout as ev  # noqa: E402
from gems57 import metric as vmetric  # noqa: E402
from gems57 import spatial  # noqa: E402
from gems57.submission_writer import write_submission  # noqa: E402
from gemsdoe31.submodular_emit import poisson_disk_emit  # noqa: E402
from gemsdoe31.submission import sha256_file, validate_submission  # noqa: E402

LANE = "H31-CC"
BUDGET = 37_654
MIN_DIST = 2.8
B_PX = 2.0
BUFFER = 80
SLOPE_MAX = 4.0
SIGMA = 2.0
SEED = 310031
RHO_LIMIT = 0.90
OVERLAP_LIMIT = 0.70
EVID = ROOT / "evidence" / "h31cc"
SHAPE = (3730, 3292)

FOCUS = [
    ("GEMSDOE24", "h25-1-dotted-h19-5-d1-5", 0.2477,
     "data/prior_audit/GEMSDOE24/docs/downloads/gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-allfinite.tif"),
    ("GEMSDOE25", "dotted-h19-5-d2-8", 0.2600,
     "data/prior_audit/GEMSDOE25/docs/downloads/gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-zeros.tif"),
    ("GEMSDOE27", "topo-gap-closure-t-v2-on-d1-5", 0.2449,
     "data/prior_audit/GEMSDOE27/docs/downloads/gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-allfinite.tif"),
    ("GEMSDOE28", "h36-1-rung30-blind-r1", 0.2710,
     "data/prior_audit/GEMSDOE28/docs/downloads/gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-allfinite.tif"),
    ("GEMSDOE30", "d28-poisson300m-offcat-44090", 0.2600,
     "data/prior_audit/GEMSDOE30/docs/downloads/gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca-nanoutside.tif"),
    ("GEMSDOE31", "h27-4-solo-d28", 0.2708,
     "docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-allfinite.tif"),
    ("GEMSDOE32", "h33-h33-2-b2", 0.2778,
     "data/prior_audit/GEMSDOE32/docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"),
    ("GEMSDOE33", "h33d-analog-tip-stepover-r30", 0.2632,
     "data/prior_audit/GEMSDOE33/docs/downloads/GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e-nanoutside.tif"),
    ("GEMSDOE36", "anderson-geothermal-pinn-38854", 0.2750,
     "data/prior_audit/GEMSDOE36/docs/downloads/gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif"),
]


def log(*parts) -> None:
    print(time.strftime("%H:%M:%S"), *parts, flush=True)


def load_band(index: int) -> np.ndarray:
    return np.load(ROOT / f".cache/features/band-{index:02d}.npy")


def rank01(values: np.ndarray, foot: np.ndarray) -> np.ndarray:
    out = np.zeros(values.shape, np.float32)
    v = values[foot].astype(np.float64)
    order = np.argsort(v, kind="mergesort")
    ranks = np.empty(v.size, np.float64)
    ranks[order] = np.arange(v.size, dtype=np.float64)
    sorted_v = v[order]
    i = 0
    ranked = ranks[order]
    while i < v.size:
        j = i + 1
        while j < v.size and sorted_v[j] == sorted_v[i]:
            j += 1
        if j > i + 1:
            ranked[i:j] = ranked[i:j].mean()
        i = j
    ranks[order] = ranked
    out[foot] = (ranks / max(v.size - 1, 1)).astype(np.float32)
    return out


def geomean(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.exp(0.5 * (np.log(np.maximum(a, 1e-6)) + np.log(np.maximum(b, 1e-6)))).astype(np.float32)


def standardized_ranks(values: np.ndarray) -> np.ndarray | None:
    v = np.asarray(values, np.float64)
    if v.size < 2 or np.min(v) == np.max(v):
        return None
    ranks = rankdata(v, method="average")
    ranks = ranks - ranks.mean()
    norm = np.linalg.norm(ranks)
    if norm == 0:
        return None
    return ranks / norm


def read_prior(path: Path, foot: np.ndarray) -> np.ndarray | None:
    if not path.is_file():
        return None
    with rasterio.open(path) as ds:
        if ds.shape != SHAPE or ds.count != 1 or str(ds.crs) != "EPSG:32611":
            return None
        if [round(x, 6) for x in ds.transform[:6]] != [100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0]:
            return None
        a = ds.read(1)
    return (foot & np.isfinite(a) & (a > 0))


def overlap_and_rho(surface: np.ndarray, dots: np.ndarray, prior: np.ndarray, foot: np.ndarray,
                    prior_ranks: np.ndarray | None) -> dict:
    halo = distance_transform_edt(~prior) <= 3
    n = int(dots.sum())
    ov = float(halo[dots].mean()) if n else None
    mine = standardized_ranks(np.nan_to_num(surface[foot], nan=0.0).astype(np.float64))
    rho = float(np.dot(mine, prior_ranks)) if mine is not None and prior_ranks is not None else None
    return {"overlap": ov, "rho": rho, "dots": n, "prior_dots": int(prior.sum())}


def auc(scores: np.ndarray, pos: np.ndarray, neg: np.ndarray) -> float:
    sp = scores[pos]
    sn = scores[neg]
    sp = sp[np.isfinite(sp)]
    sn = sn[np.isfinite(sn)]
    if sp.size == 0 or sn.size == 0:
        return float("nan")
    # Mann-Whitney, tie-averaged. Subsample negatives if huge.
    if sn.size > 200_000:
        rng = np.random.default_rng(SEED)
        sn = sn[rng.choice(sn.size, 200_000, replace=False)]
    allv = np.concatenate([sp, sn])
    ranks = rankdata(allv, method="average")
    rpos = ranks[: sp.size].sum()
    return float((rpos - sp.size * (sp.size + 1) / 2) / (sp.size * sn.size))


def emit(surface: np.ndarray, allowed: np.ndarray, n: int = BUDGET) -> np.ndarray:
    return poisson_disk_emit(surface, allowed & (surface > 0), n, min_dist_px=MIN_DIST, max_pool=400_000)


def score_prediction(pred: np.ndarray, folds) -> tuple[dict, np.ndarray]:
    terms = None
    per = []
    for fold in folds:
        res, trm = ev.evaluate(pred.astype(np.float32), fold, fold["region"] | fold["train"] | True)
        # evaluate masks with fold visible/region itself; pass the full footprint as valid
        terms = trm if terms is None else terms + trm
        per.append({"fold": int(fold["fold"]), "n_truth": int(res["n_truth"]),
                    "dti": float(vmetric.dti_from_components(res["tpw"], res["fpw"], res["fnw"])),
                    "tpw": float(res["tpw"]), "fpw": float(res["fpw"]), "fnw": float(res["fnw"])})
    return {"per_fold": per}, terms


def evaluate_on_folds(surface: np.ndarray, folds, foot: np.ndarray) -> tuple[dict, np.ndarray]:
    terms = None
    per = []
    for fold in folds:
        dvis = distance_transform_edt(~fold["visible"])
        allowed = foot & (dvis > B_PX)
        dots = emit(surface, allowed)
        pred = dots.astype(np.float32)
        res, trm = ev.evaluate(pred, fold, foot)
        terms = trm if terms is None else terms + trm
        per.append({"fold": int(fold["fold"]), "n_truth": int(res["n_truth"]), "emitted": int(dots.sum()),
                    "dti": float(vmetric.dti_from_components(res["tpw"], res["fpw"], res["fnw"])),
                    "tpw": float(res["tpw"]), "fpw": float(res["fpw"]), "fnw": float(res["fnw"])})
        log(" fold", fold["fold"], "dti", round(per[-1]["dti"], 4), "truth", res["n_truth"], "dots", int(dots.sum()))
    return {"per_fold": per}, terms


def pooled(terms: dict, candidate: str) -> dict:
    summary = ev.pooled_summary(terms, draws=1000, seed=520810, candidate=candidate)
    # pooled_summary returns a dict with candidate score; keep the raw object JSON-safe below
    return summary


def jsonable(obj):
    if isinstance(obj, dict):
        return {str(k): jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [jsonable(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, float) and not np.isfinite(obj):
        return None
    return obj


def component_offset_folds(catalogue, eligible, buffer_px=BUFFER):
    """Label-blind quadrants at height//3, width//3. Frozen confirmation split."""
    h, w = catalogue.shape
    yy, xx = np.indices((h, w), sparse=True)
    y0, x0 = h // 3, w // 3
    quadrant = ((yy >= y0).astype(np.int8) * 2 + (xx >= x0).astype(np.int8))
    comp, n = label(catalogue, np.ones((3, 3), bool))
    for f in range(4):
        region = eligible & (quadrant == f)
        ids = np.unique(comp[catalogue & region])
        ids = ids[ids > 0]
        held_all = (np.isin(comp, ids) & catalogue) if len(ids) else np.zeros_like(catalogue, bool)
        truth = held_all & region
        exclusion = region | held_all
        train = eligible & (distance_transform_edt(~exclusion) > buffer_px)
        visible = catalogue & ~held_all
        yield dict(fold=f, region=region, train=train, truth=truth, visible=visible,
                   held_all=held_all, receipt=dict(
                       fold=f, split="offset-third-label-blind", truth_px=int(truth.sum()),
                       buffer_px=buffer_px, origin=(int(y0), int(x0))))


def main() -> int:
    EVID.mkdir(parents=True, exist_ok=True)
    prereg = ROOT / "knowledge/2026-10-28_h31cc_preregistration.md"
    prereg_sha = hashlib.sha256(prereg.read_bytes()).hexdigest()
    with rasterio.open(ROOT / "data/sample_submission.tif") as ds:
        sample = ds.read(1)
    with rasterio.open(ROOT / "data/labels.tif") as ds:
        labels = ds.read(1)
    foot = np.isfinite(sample)
    cat = foot & (labels == 1)
    if int(foot.sum()) != 5_167_373 or int(cat.sum()) != 60_988:
        raise SystemExit("template/catalogue counts drifted")
    log("bands")
    depth = load_band(15).astype(np.float32)
    slope = load_band(19).astype(np.float32)
    grav = np.abs(load_band(18)).astype(np.float32)
    dil = load_band(8).astype(np.float32)
    # invalid cache cells inside the footprint stay out of the surface
    valid = foot & np.isfinite(depth) & np.isfinite(slope) & np.isfinite(grav) & np.isfinite(dil)
    depth_s = gaussian_filter(np.where(np.isfinite(depth), depth, 0), SIGMA, mode="nearest")
    gy = gaussian_filter(depth_s, 1.0, order=(1, 0), mode="nearest")
    gx = gaussian_filter(depth_s, 1.0, order=(0, 1), mode="nearest")
    grad = np.hypot(gy, gx).astype(np.float32)
    low = valid & (slope < SLOPE_MAX)
    r_grad = rank01(grad, valid)
    r_grav = rank01(grav, valid)
    cc1 = np.where(low, r_grad, 0).astype(np.float32)
    cc2 = np.where(low, geomean(r_grad, r_grav), 0).astype(np.float32)
    cc3 = np.where(low & (dil > 0), cc2, 0).astype(np.float32)
    rng = np.random.default_rng(SEED)
    null = np.zeros(SHAPE, np.float32)
    null[low] = rng.random(int(low.sum()), dtype=np.float32)
    surfaces = {"CC1": cc1, "CC2": cc2, "CC3": cc3, "NULL": null}
    log("support", {k: int((v > 0).sum()) for k, v in surfaces.items()})

    # --- experiment 1: feature-alone canaries on the screen folds ---
    folds = list(spatial.folds(cat, foot, buffer_px=BUFFER))
    withheld = np.zeros(SHAPE, bool)
    for fold in folds:
        withheld |= fold["truth"]
    neg_pool = np.flatnonzero(foot & ~cat & (distance_transform_edt(~cat) > 3))
    if neg_pool.size < 1000 or int(withheld.sum()) < 100:
        raise RuntimeError(f"canary sample collapsed: positives={int(withheld.sum())} negatives={neg_pool.size}")
    neg_idx = rng.choice(neg_pool, size=min(80_000, neg_pool.size), replace=False)
    neg = np.zeros(SHAPE, bool)
    neg.ravel()[neg_idx] = True
    features = {
        "depth_gradient": grad,
        "low_slope_gate": low.astype(np.float32),
        "abs_grav_hg": grav,
        "positive_dilatation": (dil > 0).astype(np.float32),
        "CC1": cc1, "CC2": cc2, "CC3": cc3,
    }
    canary_rows = []
    for name, arr in features.items():
        a = auc(arr, withheld, neg)
        canary_rows.append({"feature": name, "auc": a, "positives": int(withheld.sum()),
                            "negatives": int(neg.sum()), "leakage_flagged": bool(a > 0.90)})
        log("canary", name, round(a, 4), "FLAG" if a > 0.90 else "ok")
    canary = {"evidence_class": "LEAKAGE-CANARY", "auc_ceiling": 0.90,
              "evaluator": "Mann-Whitney on screen-fold withheld catalogue pixels vs frozen off-catalogue negatives",
              "rows": canary_rows,
              "all_pass": all(not r["leakage_flagged"] for r in canary_rows)}
    (EVID / "canary.json").write_text(json.dumps(canary, indent=1) + "\n")
    del depth, depth_s, gy, gx, grav, dil, grad, features
    if not canary["all_pass"]:
        card = base_card(prereg_sha, surfaces, foot, cat)
        card.update(experiments_run=1, verdict="negative", ok_to_submit=False,
                    stop="leakage canary", holdout_dti=None, raster_sha256=None)
        write_card(card)
        log("STOP leakage")
        return 0

    # --- pre-placement uniqueness ---
    priors = prior_catalog(foot)
    log("priors", len(priors))
    d_full = distance_transform_edt(~cat)
    allowed_full = foot & (d_full > B_PX)
    surface_audit = {}
    duplicate_lanes = []
    for name, surf in surfaces.items():
        if name == "NULL":
            continue
        prospective = emit(surf, allowed_full)
        rows = compare(surf, prospective, priors, foot)
        worst_ov = max((r["overlap"] for r in rows if r["class"] == "submission" and r["overlap"] is not None), default=None)
        worst_rho = max((abs(r["rho"]) for r in rows if r["rho"] is not None), default=None)
        lat = next(r for r in rows if r["class"] == "calibration-lattice")
        dup = (worst_ov is not None and worst_ov > OVERLAP_LIMIT) or (worst_rho is not None and worst_rho > RHO_LIMIT)
        surface_audit[name] = {"prospective_dots": int(prospective.sum()), "max_overlap_submission": worst_ov,
                               "max_abs_rho_submission": worst_rho, "lattice_overlap": lat["overlap"],
                               "lattice_rho": lat["rho"], "duplicate_submission_lane": dup,
                               "worst": sorted(rows, key=lambda r: -(r["overlap"] or 0))[:6]}
        log("surface", name, "ov", None if worst_ov is None else round(worst_ov, 4),
            "rho", None if worst_rho is None else round(worst_rho, 4), "lat", round(lat["overlap"], 4),
            "DUP" if dup else "unique-vs-submissions")
        if dup:
            duplicate_lanes.append(name)
    (EVID / "surface_uniqueness.json").write_text(json.dumps(jsonable(surface_audit), indent=1) + "\n")
    if len(duplicate_lanes) == 3:
        card = base_card(prereg_sha, surfaces, foot, cat)
        card.update(experiments_run=1, verdict="negative", ok_to_submit=False, slot_approved=False,
                    stop="pre-placement duplicate versus a submission raster",
                    correlation_overlap_vs_registry=surface_audit, holdout_dti=None, raster_sha256=None,
                    new_tif_generated=False)
        write_card(card)
        log("STOP duplicate before placement")
        return 0

    # --- experiment 2: screen non-duplicate arms plus NULL and fixed H31-X ---
    arms = {k: v for k, v in surfaces.items() if k == "NULL" or k not in duplicate_lanes}
    # Primary must be scored if it survived. If CC3 duplicated, do not substitute another arm as primary.
    terms = {}
    screen = {}
    for name, surf in arms.items():
        log("screen", name)
        info, trm = evaluate_on_folds(surf, folds, foot)
        terms[name] = trm
        screen[name] = info
    href = ROOT / "docs/downloads/gemsdoe31-h31x-piedmont-junction-37654-20261026-5a956da9-zeros.tif"
    h33 = ROOT / "data/prior_audit/GEMSDOE32/docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"
    fixed = {}
    for tag, path in (("REF_H31X", href), ("REF_H33", h33)):
        prior = read_prior(path, foot)
        if prior is None:
            continue
        log("screen", tag)
        info, trm = score_fixed(prior, folds, foot)
        terms[tag] = trm
        fixed[tag] = info
    clean = {}
    for name, trm in terms.items():
        if name == "NULL":
            other = "CC3" if "CC3" in terms else next(k for k in terms if k != "NULL")
            bundle = {"NULL": trm, other: terms[other]}
            summary = ev.pooled_summary(bundle, draws=1000, seed=520810, candidate="NULL")
        else:
            summary = ev.pooled_summary({name: trm, "NULL": terms["NULL"]}, draws=1000, seed=520810, candidate=name)
        clean[name] = pack_summary(summary, name, int(withheld.sum()))
        log("pooled", name, round(clean[name]["dti"], 4), "ci", [round(x, 4) for x in clean[name]["ci95"]])
    (EVID / "screen.json").write_text(json.dumps(jsonable({"per_fold": {**screen, **fixed}, "pooled": clean,
                                                           "fold_receipts": [f["receipt"] for f in folds]}), indent=1) + "\n")

    if "CC3" not in clean:
        card = base_card(prereg_sha, surfaces, foot, cat)
        card.update(experiments_run=2, verdict="negative", ok_to_submit=False, new_tif_generated=False,
                    stop="primary CC3 failed pre-placement uniqueness; no substitute promoted",
                    holdout_dti=clean, correlation_overlap_vs_registry=surface_audit, raster_sha256=None)
        write_card(card)
        return 0

    delta = clean["CC3"].get("paired_vs_null")
    beats_null = bool(delta and delta["ci95"][0] > 0 and clean["CC3"]["dti"] > clean["NULL"]["dti"])
    beats_h31x = "REF_H31X" not in clean or clean["CC3"]["dti"] > clean["REF_H31X"]["dti"]
    log("beats null", beats_null, "beats h31x point", beats_h31x)

    # --- experiment 3: confirmation only if screen gate passes ---
    confirmation = None
    if beats_null and beats_h31x and canary["all_pass"]:
        log("confirmation")
        cf = list(component_offset_folds(cat, foot))
        cterm = {}
        cper = {}
        for name in ("CC3", "NULL"):
            info, trm = evaluate_on_folds(surfaces[name], cf, foot)
            cterm[name] = trm
            cper[name] = info
        confirmation = {"per_fold": cper,
                        "CC3": pack_summary(ev.pooled_summary(cterm, draws=1000, seed=520810, candidate="CC3"), "CC3",
                                            int(sum(f["receipt"]["truth_px"] for f in cf))),
                        "NULL": pack_summary(ev.pooled_summary({"NULL": cterm["NULL"], "CC3": cterm["CC3"]},
                                                               draws=1000, seed=520810, candidate="NULL"), "NULL",
                                             int(sum(f["receipt"]["truth_px"] for f in cf)))}
        (EVID / "confirmation.json").write_text(json.dumps(jsonable(confirmation), indent=1) + "\n")
        conf_delta = confirmation["CC3"].get("paired_vs_null")
        conf_ok = bool(conf_delta and conf_delta["ci95"][0] > 0)
    else:
        conf_ok = False
        log("confirmation not run; screen did not clear the preregistered bar")

    # final dots on the full catalogue collar, then final uniqueness
    final_dots = emit(cc3, allowed_full)
    final_rows = compare(cc3, final_dots, priors, foot)
    final_ov = max((r["overlap"] for r in final_rows if r["class"] == "submission" and r["overlap"] is not None), default=None)
    final_rho = max((abs(r["rho"]) for r in final_rows if r["rho"] is not None), default=None)
    lat = next(r for r in final_rows if r["class"] == "calibration-lattice")
    final_dup = (final_ov is not None and final_ov > OVERLAP_LIMIT) or (final_rho is not None and final_rho > RHO_LIMIT)
    log("final", "ov", final_ov, "rho", final_rho, "lat", lat["overlap"], "dup", final_dup)

    sgmc = sgmc_score(final_dots, foot, cat)
    h33_dots = read_prior(h33, foot)
    sgmc_h33 = sgmc_score(h33_dots, foot, cat) if h33_dots is not None else None

    package = (not final_dup) and canary["all_pass"] and "CC3" not in duplicate_lanes
    files = None
    if package:
        files = package_raster(final_dots, foot, cat, clean["CC3"])
        log("packaged", files["sha256"])
    else:
        log("not packaged", "final_dup" if final_dup else "other")

    literal_submit = False  # lattice overlap is expected to exceed 0.70; never override
    if lat["overlap"] is not None and lat["overlap"] <= OVERLAP_LIMIT and package and beats_null and conf_ok and beats_h31x:
        literal_submit = True
    card = base_card(prereg_sha, surfaces, foot, cat)
    card.update(
        experiments_run=3 if confirmation else 2,
        verdict="promote" if literal_submit else "negative",
        ok_to_submit=literal_submit,
        ok_to_download_for_research=bool(package),
        slot_approved=False,
        submission_slots_used=0,
        new_tif_generated=bool(package),
        stop=None if package else ("final-dot duplicate versus a submission raster" if final_dup else "efficacy or confirmation"),
        holdout_dti=clean.get("CC3"),
        holdout_table=clean,
        confirmation=confirmation,
        confirmation_passed=conf_ok,
        beats_same_run_null=beats_null,
        beats_h31x_point=beats_h31x,
        correlation_overlap_vs_registry={
            "surface": surface_audit.get("CC3"),
            "final": {"max_overlap_submission": final_ov, "max_abs_rho_submission": final_rho,
                      "lattice_overlap": lat["overlap"], "lattice_rho": lat["rho"],
                      "duplicate_submission_lane": final_dup,
                      "rows_head": sorted(final_rows, key=lambda r: -(r["overlap"] or 0))[:8]},
        },
        sgmc_proxy=sgmc,
        sgmc_h33_same_code=sgmc_h33,
        raster_sha256=None if not files else files["sha256"],
        files=files,
        submission_name=None if not files else files["name"],
        note=None if not files else files["note"],
        validator=None if not files else files["validator"],
        leaderboard_estimate=None,
        estimate_reason="No cross-family projection is reported as a score. User-reported 0.2778/0.3195/0.4413 are not organizer receipts.",
    )
    write_card(card)
    log("done", card["verdict"], "submit", card["ok_to_submit"], "research", card["ok_to_download_for_research"])
    return 0


def score_fixed(dots: np.ndarray, folds, foot: np.ndarray):
    terms = None
    per = []
    pred = dots.astype(np.float32)
    for fold in folds:
        res, trm = ev.evaluate(pred, fold, foot)
        terms = trm if terms is None else terms + trm
        per.append({"fold": int(fold["fold"]), "n_truth": int(res["n_truth"]),
                    "dti": float(vmetric.dti_from_components(res["tpw"], res["fpw"], res["fnw"])),
                    "tpw": float(res["tpw"]), "fpw": float(res["fpw"]), "fnw": float(res["fnw"])})
        log(" fold", fold["fold"], "fixed", round(per[-1]["dti"], 4))
    return {"per_fold": per}, terms


def pack_summary(summary: dict, name: str, withheld: int) -> dict:
    score = summary["scores"][name]
    paired = summary.get("paired_differences", {}).get("NULL")
    return {"evidence_class": "HOLDOUT-DTI", "evaluator_version": ev.VERSION, "arm": name,
            "withheld_positive_pixels": int(score["withheld_positive_pixels"]),
            "dti": float(score["dti"]), "ci95": [float(x) for x in score["ci95"]],
            "tpw": float(score["tpw"]), "fpw": float(score["fpw"]), "fnw": float(score["fnw"]),
            "paired_vs_null": paired, "best_comparable_control": summary.get("best_comparable_control")}


def sgmc_score(dots: np.ndarray, foot: np.ndarray, cat: np.ndarray) -> dict:
    with rasterio.open(ROOT / "data/external/derived_sgmc_faults_100m_u8.tif") as ds:
        sg = ds.read(1) > 0
    off = foot & sg & (distance_transform_edt(~cat) > 3)
    pred = dots.astype(np.float32)
    # score against off-catalogue SGMC, masking catalogue pixels
    fold = {"region": foot, "visible": cat, "truth": off, "train": np.zeros(SHAPE, bool)}
    res, _ = ev.evaluate(pred, fold, foot)
    return {"evidence_class": "SGMC-OFFCATALOGUE-PROXY-DTI", "not_a_competition_score": True,
            "evaluator_version": ev.VERSION, "n_truth": int(off.sum()),
            "dti": float(vmetric.dti_from_components(res["tpw"], res["fpw"], res["fnw"])),
            "tpw": float(res["tpw"]), "fpw": float(res["fpw"]), "fnw": float(res["fnw"])}


def prior_catalog(foot: np.ndarray) -> list[dict]:
    """Paths only. Arrays are loaded one at a time so the 4 GB sandbox is not exhausted."""
    rows = []
    for site, name, reported, rel in FOCUS:
        rows.append({"site": site, "name": name, "class": "submission", "path": rel, "reported_user": reported})
    rows.append({"site": "calibration", "name": "r13-lattice-s5", "class": "calibration-lattice",
                 "path": ".cache/registry-scope/registered-lattice.tif"})
    for path in sorted((ROOT / "docs/downloads").glob("*.tif")):
        if "h31cc" in path.name:
            continue
        rows.append({"site": "GEMSDOE31-local", "name": path.name, "class": "local",
                     "path": str(path.relative_to(ROOT))})
    return rows


def compare(surface, dots, priors, foot) -> list[dict]:
    out = []
    mine = standardized_ranks(np.nan_to_num(surface[foot], nan=0.0).astype(np.float32))
    n = int(dots.sum())
    for prior in priors:
        path = ROOT / prior["path"]
        theirs = read_prior(path, foot)
        if theirs is None or int(theirs.sum()) == 0:
            out.append({"site": prior["site"], "name": prior["name"], "class": prior["class"], "missing": True})
            continue
        frac = float(theirs.sum()) / float(foot.sum())
        cls = prior["class"]
        if cls == "local":
            cls = "continuous-surface" if frac > 0.20 else "submission"
        halo = distance_transform_edt(~theirs) <= 3
        their_ranks = standardized_ranks(theirs[foot].astype(np.float32))
        rho = float(np.dot(mine, their_ranks)) if mine is not None and their_ranks is not None else None
        out.append({"site": prior["site"], "name": prior["name"], "class": cls,
                    "overlap": float(halo[dots].mean()) if n else None, "rho": rho,
                    "prior_dots": int(theirs.sum()), "support_fraction": frac,
                    "sha256": sha256_file(path)})
        del theirs, halo, their_ranks
    return out


def package_raster(dots: np.ndarray, foot: np.ndarray, cat: np.ndarray, holdout: dict) -> dict:
    dti = holdout["dti"]
    name = f"gems31-h31cc-basement-step-{int(dots.sum())}d-20261028"
    note = f"H31-CC basement-step low-slope grav dilate {int(dots.sum())}d B2 | HOLDOUT-DTI {dti:.4f} | not a live score"
    if len(note) > 140:
        raise ValueError(note)
    pred = np.where(foot, dots.astype(np.float32), np.nan)
    # Shared writer requires finite [0,1] everywhere and zero outside footprint, and rejects existing files.
    finite = np.where(foot, dots.astype(np.float32), 0).astype(np.float32)
    out = ROOT / "docs/downloads" / f"{name}-zeros.tif"
    if out.exists():
        raise FileExistsError(out)
    write_submission(out, finite, ROOT / "data/sample_submission.tif", foot, note=note, name=name, catalogue=cat)
    # Also write the NaN-outside twin with the local validator, without clipping.
    nan_path = ROOT / "docs/downloads" / f"{name}-nan.tif"
    profile = dict(driver="GTiff", dtype="float32", count=1, height=3730, width=3292, crs="EPSG:32611",
                   transform=rasterio.transform.Affine(100, 0, 243350, 0, -100, 4508550), nodata=float("nan"),
                   compress="deflate", tiled=True, blockxsize=256, blockysize=256)
    with rasterio.open(nan_path, "w", **profile) as ds:
        ds.write(pred.astype(np.float32), 1)
    val_z = validate_submission(out, ROOT / "data/sample_submission.tif", convention="all-finite")
    val_n = validate_submission(nan_path, ROOT / "data/sample_submission.tif", convention="nan-outside")
    if not val_z["ok_to_upload_format_only"] or not val_n["ok_to_upload_format_only"]:
        raise RuntimeError(f"format failed {val_z['hard_failures']} {val_n['hard_failures']}")
    zpath = out.with_suffix(".zip")
    if not zpath.is_file():
        raise FileNotFoundError(zpath)
    return {"name": name, "note": note, "note_chars": len(note),
            "zeros": str(out.relative_to(ROOT)), "nan": str(nan_path.relative_to(ROOT)),
            "zip": str(zpath.relative_to(ROOT)), "sha256": sha256_file(out),
            "sha256_nan": sha256_file(nan_path), "sha256_zip": sha256_file(zpath),
            "dots": int(dots.sum()), "validator": val_z, "validator_nan": val_n,
            "portal_range_file": str(out.relative_to(ROOT)),
            "portal_range_reason": "All-finite zeros-outside float32 in [0, 1]. NaN-outside twin is research-only; a portal that rejects NaN returns Predicted values must be in range [0, 1]."}


def base_card(prereg_sha, surfaces, foot, cat) -> dict:
    return {
        "lane": LANE,
        "hypothesis": "Catalogue-missing normal faults under basin fill sit on basement-depth steps where surface slope is below 4 degrees, corroborated by a gravity horizontal gradient and positive dilatation.",
        "mechanism": "CC3: rank(grad depth_to_base_surf, sigma 2px) geometric-mean rank(|iso_grav_anom_hg|), gated to det_elev_slope<4 and geod_dilaterate>0; Poisson 2.8px, 37654 budget, >2px from visible catalogue.",
        "named_non_fault_mimic": "depositional isopach pinch-out, lithologic density contact, gravity terrain residual, playa compaction",
        "preregistration": "knowledge/2026-10-28_h31cc_preregistration.md",
        "preregistration_sha256": prereg_sha,
        "method_paragraph_in_prompt": False,
        "lane_assignment": "Self-assigned from the prompt order to rank new hypotheses and validate the top one. Disclosed because the coordinator method paragraph was absent.",
        "support_pixels": {k: int((v > 0).sum()) for k, v in surfaces.items()},
        "footprint_pixels": int(foot.sum()),
        "catalogue_pixels": int(cat.sum()),
    }


def write_card(card: dict) -> None:
    text = json.dumps(jsonable(card), indent=1) + "\n"
    (EVID / "run_card.json").write_text(text)
    (ROOT / "docs/downloads/h31cc-run-card.json").write_text(text)


if __name__ == "__main__":
    raise SystemExit(main())
