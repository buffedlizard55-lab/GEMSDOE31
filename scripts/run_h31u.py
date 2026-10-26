#!/usr/bin/env python3
"""H31-U lane runner: strain-seismic corroborated potential-field ridges.

Frozen by knowledge/2026-10-26_h31u_preregistration.md BEFORE any fitting.
Reuses the shared template unchanged: vendor/gems57 spatial.folds,
evaluate_holdout (gems57-pooled-hide-v2), metric, uniqueness, submission_writer.
Emission geometry (score-ordered Poisson thinning, 2.8 px, 37,654 dots, B2
catalogue-flank pruning) is inherited live-proven geometry only; no prior dots
or surfaces enter the candidate. Implementation constants frozen here:
gradient sigma = 1.5 px for potential-field/DEM/basement/alteration lines,
3.0 px for strain/seismicity (native km-scale fields); winsorize each band at
footprint [0.1, 99.9] percentiles before gradients; NaN filled with footprint
median before filtering, masked after. Stages: lines, canary, exp1, exp2,
exp3, package. Each writes a JSON receipt under evidence/h31u/.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt, gaussian_filter
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))

from gems57 import evaluate_holdout as ev  # noqa: E402
from gems57 import metric as vmetric  # noqa: E402
from gems57 import spatial, submission_writer, uniqueness  # noqa: E402
from gemsdoe31.submodular_emit import poisson_disk_emit  # noqa: E402
from gemsdoe31.submission import validate_submission  # noqa: E402

SHAPE = (3730, 3292)
BUDGET = 37_654
MIN_DIST = 2.8
B_PX = 2.0
CACHE = ROOT / "data" / "h31u"
EVID = ROOT / "evidence" / "h31u"
LINES = ["STRAIN", "SEIS", "TILT", "SCARP", "BASE", "ALT", "CTRL"]
ARMS = {
    "U1": ["STRAIN", "SEIS", "TILT", "SCARP"],
    "U2": ["TILT"],
    "U3": ["BASE"],
    "U4": ["TILT", "SCARP", "ALT"],
    "U5": ["STRAIN", "SEIS", "TILT", "SCARP", "BASE", "ALT"],
    "CTRL": ["CTRL"],
}


def log(*a):
    print(*a, flush=True)


def sha256_file(p: Path) -> str:
    d = hashlib.sha256()
    with p.open("rb") as h:
        for c in iter(lambda: h.read(1 << 20), b""):
            d.update(c)
    return d.hexdigest()


def load_grid():
    with rasterio.open(ROOT / "data/sample_submission.tif") as ds:
        foot = np.isfinite(ds.read(1))
    with rasterio.open(ROOT / "data/labels.tif") as ds:
        cat = ds.read(1) == 1
    with rasterio.open(ROOT / "data/external/derived_sgmc_faults_100m_u8.tif") as ds:
        sgmc = (ds.read(1) == 1) & foot
    d_cat = distance_transform_edt(~cat)
    off_sgmc = sgmc & (d_cat > 3.0)
    return foot, cat, sgmc, off_sgmc, d_cat


def stack_band(name: str, foot: np.ndarray) -> np.ndarray:
    meta = json.loads((ROOT / "data/prepared/features.json").read_text())
    idx = meta["bands"].index(name)
    mm = np.memmap(ROOT / "data/prepared/features.f32", dtype=np.float32, mode="r",
                   shape=(len(meta["bands"]),) + SHAPE)
    a = np.asarray(mm[idx], dtype=np.float32).copy()
    return a


def clean(a: np.ndarray, foot: np.ndarray) -> np.ndarray:
    """Winsorize + median-fill NaN (label-free, footprint statistics only)."""
    v = a[foot & np.isfinite(a)]
    lo, hi = np.percentile(v, [0.1, 99.9])
    med = float(np.median(v))
    out = np.where(np.isfinite(a), np.clip(a, lo, hi), med).astype(np.float32)
    return out


def gradmag(a: np.ndarray, sigma: float) -> np.ndarray:
    gy = gaussian_filter(a, sigma=sigma, order=(1, 0), mode="nearest")
    gx = gaussian_filter(a, sigma=sigma, order=(0, 1), mode="nearest")
    return np.hypot(gy, gx).astype(np.float32)


def rank01(a: np.ndarray, foot: np.ndarray) -> np.ndarray:
    out = np.zeros(a.shape, np.float32)
    v = a[foot].astype(np.float64)
    order = np.argsort(v, kind="mergesort")
    ranks = np.empty(v.size, np.float64)
    ranks[order] = np.arange(v.size)
    # average ties
    sv = v[order]
    i = 0
    r_sorted = ranks[order]
    while i < v.size:
        j = i + 1
        while j < v.size and sv[j] == sv[i]:
            j += 1
        if j - i > 1:
            r_sorted[i:j] = r_sorted[i:j].mean()
        i = j
    ranks[order] = r_sorted
    out[foot] = (ranks / max(v.size - 1, 1)).astype(np.float32)
    return out


def geomean_rank(parts: list[np.ndarray]) -> np.ndarray:
    acc = np.zeros(parts[0].shape, np.float32)
    for p in parts:
        acc += np.log(np.maximum(p, 1e-3))
    return np.exp(acc / len(parts)).astype(np.float32)


# ---------------------------------------------------------------- lines
def build_lines() -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    foot, cat, *_ = load_grid()
    out_path = CACHE / "lines.f32"
    mm = np.memmap(out_path, dtype=np.float32, mode="w+", shape=(len(LINES),) + SHAPE)
    receipts = {}

    def band(n):
        return clean(stack_band(n, foot), foot)

    t0 = time.time()
    # STRAIN: gradient ridges of geodetic strain-rate invariants (sigma 3)
    parts = [rank01(gradmag(band(b), 3.0), foot) for b in
             ("geod_dilaterate", "geod_shearrate", "geod_2ndinv")]
    mm[LINES.index("STRAIN")] = geomean_rank(parts)
    log("STRAIN done", round(time.time() - t0))
    # SEIS: gradient of log seismicity-density rank blend (sigma 3)
    deq = rank01(np.log1p(np.maximum(band("deq_n100a15"), 0)), foot)
    ieq = rank01(np.log1p(np.maximum(band("ieq_n100a15"), 0)), foot)
    dens = (0.5 * deq + 0.5 * ieq).astype(np.float32)
    mm[LINES.index("SEIS")] = rank01(gradmag(dens, 3.0), foot)
    log("SEIS done", round(time.time() - t0))
    # TILT: mag HG + grav HG + |grad tilt|
    hg = band("tmi_hg")
    vg = band("tmi_vg")
    tilt = np.arctan2(vg, np.maximum(hg, 1e-6)).astype(np.float32)
    parts = [rank01(hg, foot), rank01(np.abs(band("iso_grav_anom_hg")), foot),
             rank01(gradmag(tilt, 1.5), foot)]
    mm[LINES.index("TILT")] = geomean_rank(parts)
    log("TILT done", round(time.time() - t0))
    # SCARP: LiDAR step/ex/cross ranks; zero where no LiDAR coverage
    valid = stack_band("valid", foot)
    lidar_ok = foot & np.isfinite(valid) & (valid > 0)
    parts = []
    for b in ("step_max", "ex_max", "cross_max"):
        raw = stack_band(b, foot)
        r = rank01(np.where(np.isfinite(raw), raw, 0).astype(np.float32), lidar_ok | foot)
        r = np.where(lidar_ok, r, 0.0).astype(np.float32)
        parts.append(r)
    sc = geomean_rank(parts)
    mm[LINES.index("SCARP")] = np.where(lidar_ok, sc, 0.0).astype(np.float32)
    log("SCARP done", round(time.time() - t0), "lidar_ok", int(lidar_ok.sum()))
    # BASE: basement-depth + conductance gradients + gravity slope
    parts = [rank01(gradmag(band("depth_to_base_surf"), 1.5), foot),
             rank01(gradmag(band("cond_surf"), 1.5), foot),
             rank01(np.abs(band("iso_grav_anom_slope")), foot)]
    mm[LINES.index("BASE")] = geomean_rank(parts)
    log("BASE done", round(time.time() - t0))
    # ALT: radiometric ratio edges
    parts = [rank01(gradmag(band("ThK"), 1.5), foot),
             rank01(gradmag(band("UK"), 1.5), foot),
             rank01(gradmag(band("tc"), 1.5), foot)]
    mm[LINES.index("ALT")] = geomean_rank(parts)
    log("ALT done", round(time.time() - t0))
    # CTRL: generic magnetic ridge
    mm[LINES.index("CTRL")] = rank01(band("tmi_hg"), foot)
    mm.flush()
    for i, n in enumerate(LINES):
        a = np.asarray(mm[i])[foot]
        receipts[n] = dict(min=float(a.min()), max=float(a.max()), mean=float(a.mean()),
                           frac_zero=float((a == 0).mean()))
    meta = dict(lines=LINES, shape=list(SHAPE), receipts=receipts,
                note="label-free footprint percentile-rank lines; see preregistration")
    (CACHE / "lines.json").write_text(json.dumps(meta, indent=1) + "\n")
    log("lines written", out_path, round(time.time() - t0), "s")
    return meta


def load_line(name: str) -> np.ndarray:
    mm = np.memmap(CACHE / "lines.f32", dtype=np.float32, mode="r", shape=(len(LINES),) + SHAPE)
    return np.asarray(mm[LINES.index(name)], dtype=np.float32).copy()


def surface(arm: str, gate: bool = True, foot=None) -> np.ndarray:
    names = ARMS[arm]
    if len(names) == 1:
        return load_line(names[0])
    parts = [load_line(n) for n in names]
    g = geomean_rank(parts)
    if not gate:
        return g
    stack = np.stack(parts)
    second = np.partition(stack, -2, axis=0)[-2]
    return (g * second).astype(np.float32)


# ---------------------------------------------------------------- canary
def auc_for(vals: np.ndarray, pos_mask: np.ndarray, foot: np.ndarray, seed=310031) -> float:
    rng = np.random.default_rng(seed)
    pos = np.flatnonzero(pos_mask & foot)
    neg_all = np.flatnonzero(foot & ~pos_mask)
    neg = rng.choice(neg_all, size=min(200_000, neg_all.size), replace=False)
    y = np.r_[np.ones(pos.size), np.zeros(neg.size)]
    s = np.r_[vals.ravel()[pos], vals.ravel()[neg]].astype(np.float64)
    s = np.where(np.isfinite(s), s, 0.0)
    return float(roc_auc_score(y, s))


def run_canary() -> dict:
    foot, cat, sgmc, off_sgmc, _ = load_grid()
    rows = []
    for n in LINES:
        v = load_line(n)
        a_cat = auc_for(v, cat, foot)
        a_off = auc_for(v, off_sgmc, foot)
        rows.append(dict(feature=n, kind="line", auc_catalogue=a_cat, auc_off_sgmc=a_off,
                         leakage_flagged=bool(max(a_cat, a_off, 1 - a_cat, 1 - a_off) > 0.90)))
        log("canary line", n, round(a_cat, 4), round(a_off, 4))
    for arm in ("U1", "U4", "U5"):
        v = surface(arm)
        a_cat = auc_for(v, cat, foot)
        a_off = auc_for(v, off_sgmc, foot)
        rows.append(dict(feature=arm, kind="surface", auc_catalogue=a_cat, auc_off_sgmc=a_off,
                         leakage_flagged=bool(max(a_cat, a_off, 1 - a_cat, 1 - a_off) > 0.90)))
        log("canary surface", arm, round(a_cat, 4), round(a_off, 4))
    rep = dict(evidence_class="COMPUTED", auc_ceiling=0.90, rows=rows,
               all_pass=bool(all(not r["leakage_flagged"] for r in rows)))
    EVID.mkdir(parents=True, exist_ok=True)
    (EVID / "canary.json").write_text(json.dumps(rep, indent=1) + "\n")
    return rep


# ---------------------------------------------------------------- holdout machinery
def emit_dots(surf: np.ndarray, allowed: np.ndarray, n=BUDGET) -> np.ndarray:
    return poisson_disk_emit(surf, allowed, n, min_dist_px=MIN_DIST, max_pool=400_000)


def score_arms(arm_surfaces: dict[str, np.ndarray], buffer_px: int, foot, cat,
               ref_dots: np.ndarray | None = None) -> dict:
    """Pooled hide-and-recover scoring; per-fold visible-B2 emission (protocol)."""
    terms: dict[str, np.ndarray] = {}
    per_fold: dict[str, list] = {a: [] for a in arm_surfaces}
    if ref_dots is not None:
        per_fold["H27REF"] = []
    folds = list(spatial.folds(cat, foot, buffer_px=buffer_px))
    receipts = [f["receipt"] for f in folds]
    log("folds buffer", buffer_px, [r["truth_px"] for r in receipts])
    for f in folds:
        d_vis = distance_transform_edt(~f["visible"])
        allowed = foot & (d_vis > B_PX)
        for arm, surf in arm_surfaces.items():
            dots = emit_dots(surf, allowed & (surf > 0))
            pred = dots.astype(np.float32)
            res, trm = ev.evaluate(pred, f, foot)
            terms[arm] = trm if arm not in terms else terms[arm] + trm
            per_fold[arm].append(dict(
                fold=int(f["fold"]), dti=float(vmetric.dti_from_components(
                    res["tpw"], res["fpw"], res["fnw"])),
                n_truth=int(res["n_truth"]), emitted_active=int(res["n_emitted"])))
            log(" fold", f["fold"], arm, "dti", round(per_fold[arm][-1]["dti"], 4),
                "truth", res["n_truth"])
        if ref_dots is not None:
            res, trm = ev.evaluate(ref_dots.astype(np.float32), f, foot)
            terms["H27REF"] = trm if "H27REF" not in terms else terms["H27REF"] + trm
            per_fold["H27REF"].append(dict(
                fold=int(f["fold"]), dti=float(vmetric.dti_from_components(
                    res["tpw"], res["fpw"], res["fnw"])),
                n_truth=int(res["n_truth"]), emitted_active=int(res["n_emitted"])))
    return dict(terms=terms, per_fold=per_fold, fold_receipts=receipts)


def pooled(terms: dict, candidate: str) -> dict:
    return ev.pooled_summary(terms, draws=2000, seed=520810, candidate=candidate)


def load_h27_ref(foot) -> np.ndarray:
    p = ROOT / "docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-allfinite.tif"
    with rasterio.open(p) as ds:
        a = ds.read(1)
    return (a > 0) & foot


# ---------------------------------------------------------------- EXP-1
def run_exp1() -> dict:
    foot, cat, sgmc, off_sgmc, _ = load_grid()
    surfs = {a: surface(a) for a in ARMS}
    ref = load_h27_ref(foot)
    out = score_arms(surfs, 213, foot, cat, ref_dots=ref)
    summ = pooled(out["terms"], candidate="U1")
    # winner among U-arms by pooled dti
    scores = summ["scores"]
    u_arms = ["U1", "U2", "U3", "U4", "U5"]
    winner = max(u_arms, key=lambda a: scores[a]["dti"])
    best_single = max(["U2", "U3"], key=lambda a: scores[a]["dti"])
    win_summ = pooled(out["terms"], candidate=winner) if winner != "U1" else summ
    rep = dict(experiment="EXP-1 screen", evaluator_version=ev.VERSION, buffer_px=213,
               fold_receipts=out["fold_receipts"], per_fold=out["per_fold"],
               pooled=win_summ, winner=winner, best_single_line=best_single,
               h27ref_caveat="H27REF dots were B1-pruned against the FULL catalogue "
                             "(including withheld segments); handicapped reference only, "
                             "never a promotion comparator.")
    (EVID / "exp1_screen.json").write_text(json.dumps(rep, indent=1) + "\n")
    np.save(CACHE / "exp1_winner.npy", np.array([winner]))
    for a in scores:
        log("EXP1 pooled", a, round(scores[a]["dti"], 4), scores[a]["ci95"],
            "n=", scores[a]["withheld_positive_pixels"])
    log("EXP1 winner", winner, "best_single", best_single)
    return rep


# ---------------------------------------------------------------- uniqueness / peers
def peer_files() -> list[dict]:
    peers = []
    for p in sorted(glob.glob(str(ROOT / "data/prior_audit/**/downloads/*.tif"), recursive=True)):
        peers.append(dict(id="focus:" + Path(p).parent.parent.parent.name + ":" + Path(p).name,
                          path=p))
    for p in sorted(glob.glob(str(ROOT / "docs/downloads/*.tif"))):
        if "h31u" in p.lower():
            continue
        peers.append(dict(id="local:" + Path(p).name, path=p))
    # de-duplicate identical nan/zeros twins by stem core: keep one per sha later
    return peers


def read_dots(path: str, foot) -> tuple[np.ndarray, int, str]:
    h = sha256_file(Path(path))
    with rasterio.open(path) as ds:
        a = ds.read(1)
    dots = np.isfinite(a) & (a > 0) & foot
    return dots, int(dots.sum()), h


def uniqueness_audit(surf: np.ndarray, dots: np.ndarray, foot) -> dict:
    rows = []
    seen_sha = {}
    n_mine = int(dots.sum())
    # pre-placement top-K support of the continuous surface
    flat = np.where(foot, surf, -np.inf)
    vals = flat[foot]
    thr = float(np.partition(vals, -n_mine)[-n_mine]) if n_mine < vals.size else float(vals.min())
    topk = foot & (flat >= thr)
    if int(topk.sum()) > n_mine:  # deterministic tie trim
        idx = np.flatnonzero(topk)
        keep = idx[np.argsort(-flat.ravel()[idx], kind="mergesort")[:n_mine]]
        topk = np.zeros_like(foot)
        topk.ravel()[keep] = True
    for peer in peer_files():
        try:
            pdots, n_theirs, h = read_dots(peer["path"], foot)
        except Exception as exc:  # noqa: BLE001
            rows.append(dict(peer=peer["id"], error=str(exc)))
            continue
        if h in seen_sha:
            rows.append(dict(peer=peer["id"], duplicate_bytes_of=seen_sha[h],
                             sha256=h, note="same bytes as earlier peer; measured once"))
            continue
        seen_sha[h] = peer["id"]
        rep_class = uniqueness.representation_class(n_theirs, int(foot.sum()))["kind"]
        ov_final = uniqueness.dot_overlap(dots.astype(np.float32), pdots.astype(np.float32))
        ov_topk = uniqueness.dot_overlap(topk.astype(np.float32), pdots.astype(np.float32))
        rho = uniqueness.surface_rho(surf, pdots.astype(np.float32), foot)
        rho_dot = uniqueness.surface_rho(dots.astype(np.float32), pdots.astype(np.float32), foot)
        rows.append(dict(peer=peer["id"], sha256=h, their_dots=n_theirs,
                         representation=rep_class,
                         final_overlap_3px=float(ov_final), topk_overlap_3px=float(ov_topk),
                         surface_spearman_full=rho["spearman_full_footprint"],
                         dots_spearman_full=rho_dot["spearman_full_footprint"],
                         jaccard=rho_dot["jaccard_dot_sets"]))
        log("peer", peer["id"][:60], rep_class, "ov", round(ov_final, 3),
            "rho_s", None if rho["spearman_full_footprint"] is None else round(rho["spearman_full_footprint"], 3))
    two = uniqueness.two_phase_summary(
        [dict(submission=r["peer"], repo=r["peer"].split(":")[0],
              my_dots_within_3px_of_theirs=r["final_overlap_3px"],
              their_dots_within_3px_of_mine=None,
              spearman_full_footprint=r["dots_spearman_full"],
              jaccard_dot_sets=r["jaccard"], their_dots=r["their_dots"],
              representation=r["representation"])
         for r in rows if "final_overlap_3px" in r],
        int(foot.sum()))
    discrete = [r for r in rows if r.get("representation") == "dot_field"]
    return dict(my_dots=n_mine, rows=rows, two_phase=two,
                discrete_max_final_overlap=max((r["final_overlap_3px"] for r in discrete), default=None),
                discrete_max_topk_overlap=max((r["topk_overlap_3px"] for r in discrete), default=None),
                max_abs_surface_spearman=max((abs(r["surface_spearman_full"]) for r in rows
                                              if r.get("surface_spearman_full") is not None), default=None),
                max_abs_dots_spearman=max((abs(r["dots_spearman_full"]) for r in rows
                                           if r.get("dots_spearman_full") is not None), default=None))


def literal_witness(dots: np.ndarray, foot) -> dict:
    sys.path.insert(0, str(ROOT / "scripts"))
    from audit_shared_registry_stop import load_counterexample
    pin, ref = load_counterexample(ROOT, restore=False)
    control = foot & np.isfinite(ref) & (ref > 0)
    ov = uniqueness.dot_overlap(dots.astype(np.float32), control.astype(np.float32))
    # Fraction of the whole footprint within 3px of the lattice (degeneracy proof)
    from scipy.ndimage import distance_transform_edt as edt
    frac = float((edt(~control)[foot] <= 3.0).mean())
    return dict(witness=pin["counterexample"], lattice_dots=int(control.sum()),
                candidate_overlap_3px=float(ov), footprint_frac_within_3px_of_lattice=frac,
                reading="LITERAL broad-registry reading FAILS for any nonempty candidate "
                        "because the registered spacing-5 lattice covers the footprint; "
                        "disclosed diagnostic only (preregistration IR-U-02).")


# ---------------------------------------------------------------- EXP-2
def run_exp2() -> dict:
    foot, cat, sgmc, off_sgmc, d_cat = load_grid()
    exp1 = json.loads((EVID / "exp1_screen.json").read_text())
    winner = exp1["winner"]
    rep: dict = dict(experiment="EXP-2 gate ablation + uniqueness", winner_from_exp1=winner)
    final_arm, final_gate = winner, True
    if len(ARMS[winner]) > 1:
        surfs = {winner + "_gate": surface(winner, gate=True),
                 winner + "_nogate": surface(winner, gate=False),
                 "CTRL": surface("CTRL")}
        out = score_arms(surfs, 213, foot, cat)
        summ = pooled(out["terms"], candidate=winner + "_gate")
        rep["ablation"] = dict(per_fold=out["per_fold"], pooled=summ)
        g = summ["scores"][winner + "_gate"]["dti"]
        ng = summ["scores"][winner + "_nogate"]["dti"]
        final_gate = bool(g >= ng)
        rep["gate_kept"] = final_gate
        log("EXP2 ablation gate", round(g, 4), "nogate", round(ng, 4), "keep_gate", final_gate)
    surf = surface(final_arm, gate=final_gate)
    allowed = foot & (d_cat > B_PX) & (surf > 0)
    dots = emit_dots(surf, allowed)
    log("final dots", int(dots.sum()), "on_cat", int((dots & cat).sum()))
    np.save(CACHE / "final_dots.npy", dots)
    np.save(CACHE / "final_surface.npy", surf)
    (CACHE / "final_choice.json").write_text(json.dumps(
        dict(arm=final_arm, gate=final_gate, lines=ARMS[final_arm]), indent=1) + "\n")
    rep["uniqueness"] = uniqueness_audit(surf, dots, foot)
    rep["literal_witness"] = literal_witness(dots, foot)
    (EVID / "exp2.json").write_text(json.dumps(rep, indent=1, default=float) + "\n")
    u = rep["uniqueness"]
    log("EXP2 discrete max overlap", u["discrete_max_final_overlap"],
        "max|rho| surf", u["max_abs_surface_spearman"], "dots", u["max_abs_dots_spearman"])
    return rep


# ---------------------------------------------------------------- SGMC + projection
def sgmc_score(dots: np.ndarray, off_sgmc, foot) -> dict:
    p = dots.astype(np.float32)
    res = vmetric.dti_exact(p, off_sgmc, valid=foot)
    covers, _, _ = vmetric.max_cover(p.astype(np.float64), off_sgmc)
    return dict(dti=float(res["dti"]), tpw=float(covers.sum()), fpw=float(res["fp"]),
                n_truth=int(off_sgmc.sum()), n_dots=int(dots.sum()))


def load_peer_dots_by_tag(foot) -> dict[str, tuple[np.ndarray, float]]:
    """11 USER-REPORTED anchors: dots + owner-typed live value (learning only).

    Bugfix (Pass 2): the first version keyed fetched files by repository, so all
    four GEMSDOE28 anchors silently loaded the single fetched h36-1 raster.
    Resolution is now per-artifact using the nine-site audit's pinned paths and
    SHA-256 values; missing GEMSDOE28 artifacts are fetched hash-verified from
    the snapshot-pinned commit. Any anchor whose bytes do not verify (or whose
    dot count disagrees with the audit) is dropped and logged, never guessed.
    """
    from download_competition_data import _download
    audit = json.loads((ROOT / "evidence/nine_site_forensic_audit.json").read_text())
    fetch = {r["repo"]: r for r in json.loads(
        (ROOT / "evidence/regime31/peer_fetch.json").read_text())["files"]}
    snap = {r["repo"]: r["commit"] for r in json.loads(
        (ROOT / "registry/focus_raster_snapshot.json").read_text())["repositories"]}
    out = {}
    for row in audit["focus_submissions"]:
        tag = row["site_tag"]
        repo = row["repository"].rstrip("/").split("/")[-1]
        path = None
        if tag == "GEMSDOE28-h27-4":
            # Local re-emission registered pixel-identical to the GEMSDOE28 dots.
            path = ROOT / "docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-allfinite.tif"
        elif tag in ("GEMSDOE28-h32-1", "GEMSDOE28-h38-1"):
            dest = ROOT / "data/prior_audit/GEMSDOE28-extra" / Path(row["artifact_path"]).name
            dest.parent.mkdir(parents=True, exist_ok=True)
            if not (dest.is_file() and sha256_file(dest) == row["sha256"]):
                _download(f"buffedlizard55-lab/{repo}", snap[f"buffedlizard55-lab/{repo}"],
                          row["artifact_path"], dest)
            if dest.is_file() and sha256_file(dest) == row["sha256"]:
                path = dest
        elif repo in fetch and "dest" in fetch[repo]:
            path = ROOT / fetch[repo]["dest"]
        if path is None or not Path(path).is_file():
            log("anchor DROPPED (unresolved)", tag)
            continue
        dots, n, h = read_dots(str(path), foot)
        if n != int(row["emitted_dots"]):
            log("anchor DROPPED (dot count mismatch)", tag, n, row["emitted_dots"])
            continue
        out[tag] = (dots, float(row["user_reported_live_dti"]), str(path))
    return out


def projection(candidate_dots, foot, off_sgmc) -> dict:
    anchors = load_peer_dots_by_tag(foot)
    rows = []
    for tag, (dots, live, path) in anchors.items():
        s = sgmc_score(dots, off_sgmc, foot)
        rows.append(dict(tag=tag, live_user_reported=live, n_dots=s["n_dots"],
                         sgmc_tpw=s["tpw"], sgmc_dti=s["dti"], path=path))
        log("anchor", tag, "live", live, "n", s["n_dots"], "sgmcDTI", round(s["dti"], 4),
            "TPw", round(s["tpw"], 1))
    by = {r["tag"]: r for r in rows}
    # D0 from D2.8 (GEMSDOE25) / H27-4 equal-live-TPw pair (method of nine-site audit)
    a, b = by["GEMSDOE25"], by["GEMSDOE28-h27-4"]
    denom_b = 0.2 * (a["n_dots"] - b["n_dots"]) / (b["live_user_reported"] / a["live_user_reported"] - 1.0)
    d0 = float(denom_b - 0.2 * b["n_dots"])

    def fit_scale(rs):
        x = np.array([r["sgmc_tpw"] / (d0 + 0.2 * r["n_dots"]) for r in rs])
        y = np.array([r["live_user_reported"] for r in rs])
        return float((x @ y) / (x @ x))

    scale = fit_scale(rows)
    for r in rows:
        r["projection"] = scale * r["sgmc_tpw"] / (d0 + 0.2 * r["n_dots"])
        r["residual"] = r["live_user_reported"] - r["projection"]
    loo = []
    for i, r in enumerate(rows):
        s_i = fit_scale([q for j, q in enumerate(rows) if j != i])
        loo.append(r["live_user_reported"] - s_i * r["sgmc_tpw"] / (d0 + 0.2 * r["n_dots"]))
    loo_rmse = float(np.sqrt(np.mean(np.square(loo))))
    cs = sgmc_score(candidate_dots, off_sgmc, foot)
    cand_proj = scale * cs["tpw"] / (d0 + 0.2 * cs["n_dots"])
    return dict(method="anchor inversion: D0 from D2.8/H27-4 equal-TPw pair; scale by "
                       "least squares through origin on SGMC TPw; LOO refits scale only",
                d0=d0, implied_hidden_truth_px=d0 / 0.8, scale=scale,
                anchors=rows, loo_residuals=loo, loo_rmse=loo_rmse,
                candidate=dict(sgmc=cs, projection=float(cand_proj),
                               interval_approx=[float(cand_proj - 2 * loo_rmse),
                                                float(cand_proj + 2 * loo_rmse)]),
                label="PROJECTION — never a score; anchors are USER-REPORTED, no organizer receipts")


# ---------------------------------------------------------------- EXP-3
def run_exp3() -> dict:
    foot, cat, sgmc, off_sgmc, d_cat = load_grid()
    exp1 = json.loads((EVID / "exp1_screen.json").read_text())
    choice = json.loads((CACHE / "final_choice.json").read_text())
    winner, gate = choice["arm"], choice["gate"]
    best_single = exp1["best_single_line"]
    surfs = {winner: surface(winner, gate=gate), "CTRL": surface("CTRL"),
             best_single: surface(best_single)}
    out = score_arms(surfs, 80, foot, cat)
    summ = pooled(out["terms"], candidate=winner)
    dots = np.load(CACHE / "final_dots.npy")
    # SGMC references recomputed same code/day
    anchors = load_peer_dots_by_tag(foot)
    h33_dots = anchors["GEMSDOE32-h33-2-b2"][0]
    ref_sgmc = dict(H33=sgmc_score(h33_dots, off_sgmc, foot),
                    H27=sgmc_score(anchors["GEMSDOE28-h27-4"][0], off_sgmc, foot),
                    candidate=sgmc_score(dots, off_sgmc, foot))
    # per-quadrant candidate SGMC
    quad = {}
    h, w = SHAPE
    for qi, (ys, xs) in enumerate([(slice(0, h // 2), slice(0, w // 2)),
                                   (slice(0, h // 2), slice(w // 2, w)),
                                   (slice(h // 2, h), slice(0, w // 2)),
                                   (slice(h // 2, h), slice(w // 2, w))]):
        sub_f = foot[ys, xs]
        if off_sgmc[ys, xs].sum() == 0:
            quad[f"Q{qi}"] = None
            continue
        r = vmetric.dti_exact(dots[ys, xs].astype(np.float32), off_sgmc[ys, xs], valid=sub_f)
        quad[f"Q{qi}"] = float(r["dti"])
    proj = projection(dots, foot, off_sgmc)
    rep = dict(experiment="EXP-3 confirmation (zero tuning)", buffer_px=80,
               per_fold=out["per_fold"], pooled=summ, winner=winner, gate=gate,
               best_single_line=best_single, sgmc_full=ref_sgmc,
               sgmc_candidate_quadrants=quad, projection=proj)
    (EVID / "exp3.json").write_text(json.dumps(rep, indent=1, default=float) + "\n")
    log("EXP3 pooled", winner, round(summ["scores"][winner]["dti"], 4),
        "CTRL", round(summ["scores"]["CTRL"]["dti"], 4),
        best_single, round(summ["scores"][best_single]["dti"], 4))
    log("EXP3 SGMC cand", round(ref_sgmc["candidate"]["dti"], 4),
        "H33", round(ref_sgmc["H33"]["dti"], 4),
        "PROJECTION", round(proj["candidate"]["projection"], 4), "+/-", round(2 * proj["loo_rmse"], 4))
    return rep


# ---------------------------------------------------------------- gates + package
def evaluate_gates() -> dict:
    canary = json.loads((EVID / "canary.json").read_text())
    exp1 = json.loads((EVID / "exp1_screen.json").read_text())
    exp2 = json.loads((EVID / "exp2.json").read_text())
    exp3 = json.loads((EVID / "exp3.json").read_text())
    winner = exp3["winner"]
    best_single = exp3["best_single_line"]
    # G3 is judged on the FINAL packaged surface (EXP-2 gate choice applied).
    # EXP-3 re-scores exactly that surface; because every arm is label-free,
    # spatial.folds' buffer changes only the unused train mask, so EXP-3
    # quadrant scores equal the EXP-1 fold geometry (buffer-invariance
    # disclosed; the independent-truth confirmation is SGMC/G4).
    diffs = exp3["pooled"].get("paired_differences", {})
    diffs_screen = exp1["pooled"].get("paired_differences", {})
    pf = exp3["per_fold"]
    qwins = sum(1 for a, b in zip(pf[winner], pf["CTRL"]) if a["dti"] >= b["dti"])
    def ci_excludes0(name):
        d = diffs.get(name)
        return bool(d and d["delta"] > 0 and d["ci95"][0] > 0)
    g3 = bool(ci_excludes0("CTRL") and ci_excludes0(best_single) and qwins >= 3)
    diffs3 = diffs
    u = exp2["uniqueness"]
    g5 = bool(u["discrete_max_final_overlap"] is not None
              and u["discrete_max_final_overlap"] <= 0.70
              and (u["discrete_max_topk_overlap"] or 0) <= 0.70
              and (u["max_abs_surface_spearman"] or 0) <= 0.90
              and (u["max_abs_dots_spearman"] or 0) <= 0.90)
    gates = dict(
        G2_canary=bool(canary["all_pass"]),
        G3_holdout_efficacy=g3,
        G4_sgmc_discovery=bool(exp3["sgmc_full"]["candidate"]["dti"] >= exp3["sgmc_full"]["H33"]["dti"]),
        G5_uniqueness_discrete=g5,
        G6_projection_ge_02778=bool(exp3["projection"]["candidate"]["projection"] >= 0.2778),
        detail=dict(winner=winner, best_single_line=best_single, quadrant_wins_vs_ctrl=qwins,
                    exp1_screen_paired_differences=diffs_screen,
                    exp3_final_surface_paired_differences=diffs3,
                    buffer_invariance="label-free arms: buffer_px changes only the unused "
                                      "train mask in spatial.folds; region/truth/visible identical"),
    )
    return gates


def run_package() -> dict:
    foot, cat, sgmc, off_sgmc, _ = load_grid()
    choice = json.loads((CACHE / "final_choice.json").read_text())
    exp3 = json.loads((EVID / "exp3.json").read_text())
    exp1 = json.loads((EVID / "exp1_screen.json").read_text())
    exp2 = json.loads((EVID / "exp2.json").read_text())
    gates = evaluate_gates()
    dots = np.load(CACHE / "final_dots.npy")
    pred = np.where(foot, dots.astype(np.float32), 0.0).astype(np.float32)
    stem_base = "gemsdoe31-h31u-strainseis-corrob-37654-20261026"
    tmp_meta = dict(lane="H31-U", arm=choice["arm"], lines=choice["lines"], gate=choice["gate"])
    # hash pre-pass for unique name: write via vendor writer to temp name, then rename? Writer
    # refuses overwrite and embeds name in receipt; use content hash of dot support instead.
    support_sha = hashlib.sha256(np.packbits(dots.ravel()).tobytes()).hexdigest()
    name = f"{stem_base}-{support_sha[:8]}"
    hold = exp3["pooled"]["scores"][exp3["winner"]]  # final packaged surface
    note = (f"H31-U {choice['arm']} strain+seis corroborated ridges 37654d B2 | "
            f"HOLDOUT-DTI {hold['dti']:.4f} | {support_sha[:8]}")[:140]
    out_tif = ROOT / "docs/downloads" / f"{name}-zeros.tif"
    sample = ROOT / "data/sample_submission.tif"
    receipt = submission_writer.write_submission(
        out_tif, pred, sample, foot, note=note, name=name, catalogue=cat,
        metadata=tmp_meta)
    # NaN-outside twin (same footprint values) via sample profile
    nan_tif = ROOT / "docs/downloads" / f"{name}-nan.tif"
    with rasterio.open(sample) as ds:
        prof = ds.profile.copy()
    arr = np.where(foot, pred, np.nan).astype(np.float32)
    prof.update(dtype="float32", count=1, nodata=float("nan"), compress="deflate")
    with rasterio.open(nan_tif, "w", **prof) as ds:
        ds.write(arr, 1)
    import zipfile
    nan_zip = nan_tif.with_suffix(".zip")
    with zipfile.ZipFile(nan_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.write(nan_tif, arcname=nan_tif.name)
    vz = validate_submission(out_tif, sample, convention="all-finite")
    vn = validate_submission(nan_tif, sample, convention="nan-outside")
    gates = dict(G1_format=bool(vz["ok_to_upload_format_only"] and vn["ok_to_upload_format_only"]),
                 **gates)
    promote = bool(all(gates[k] for k in gates if k.startswith("G")))
    u = exp2["uniqueness"]
    card = dict(
        hypothesis="H31-U: active buried faults co-localize geodetic strain-rate gradient ridges, "
                   "seismicity-density fronts, potential-field tilt/HG ridges and LiDAR scarps; "
                   ">=2-line corroboration finds catalogue-missing faults",
        mechanism=f"{choice['arm']} geometric-mean of footprint percentile ranks of "
                  f"{'+'.join(choice['lines'])}"
                  + (" x second-line rank gate" if choice["gate"] else " (no gate)")
                  + "; Poisson 2.8px emission, 37,654 dots, d(catalogue)>2px",
        non_fault_mimic="volcanic flow margins / survey seams (TILT), Lahontan shorelines & roads "
                        "(SCARP), GPS block-model artifacts (STRAIN), quarry blasts (SEIS)",
        holdout_dti=dict(evidence_class="HOLDOUT-DTI", evaluator_version=ev.VERSION,
                         final_surface=exp3["pooled"]["scores"][exp3["winner"]],
                         final_paired_vs_ctrl=exp3["pooled"]["paired_differences"].get("CTRL"),
                         final_paired_vs_best_single=exp3["pooled"]["paired_differences"].get(
                             exp3["best_single_line"]),
                         screen_gated_variant=exp1["pooled"]["scores"][exp3["winner"]]),
        sgmc_proxy=dict(evidence_class="HOLDOUT-DTI (off-catalogue SGMC proxy; not hidden truth)",
                        candidate=exp3["sgmc_full"]["candidate"], h33_reference=exp3["sgmc_full"]["H33"]),
        projection=dict(evidence_class="PROJECTION (never a score)",
                        value=exp3["projection"]["candidate"]["projection"],
                        interval_approx=exp3["projection"]["candidate"]["interval_approx"],
                        loo_rmse=exp3["projection"]["loo_rmse"],
                        anchors="11 USER-REPORTED focus values; no organizer receipts"),
        correlation_overlap_vs_registry=dict(
            scope="discrete dot-field peers: 9 focus sites (hash-verified fetch) + all local "
                  "GEMSDOE31 downloads; surface checked pre-placement (top-K) and on final dots",
            discrete_max_final_overlap_3px=u["discrete_max_final_overlap"],
            discrete_max_topk_overlap_3px=u["discrete_max_topk_overlap"],
            max_abs_spearman_surface=u["max_abs_surface_spearman"],
            max_abs_spearman_dots=u["max_abs_dots_spearman"],
            literal_broad_registry=exp2["literal_witness"],
            unique_vs_discrete_peers=bool(gates["G5_uniqueness_discrete"])),
        raster_sha256=sha256_file(out_tif),
        raster_sha256_nan=sha256_file(nan_tif),
        support_sha256=support_sha,
        validator=dict(zeros=dict(file=out_tif.name, ok=vz["ok_to_upload_format_only"],
                                   hard_failures=vz["hard_failures"], grid=vz["grid"]),
                       nan=dict(file=nan_tif.name, ok=vn["ok_to_upload_format_only"],
                                hard_failures=vn["hard_failures"], grid=vn["grid"]),
                       vendor_writer_receipt=str(Path(receipt["file"]).name) if isinstance(receipt, dict) else "written",
                       organizer_acceptance_verified=False),
        submission_name=name, note=note, note_chars=len(note),
        gates=gates, verdict="promote" if promote else "negative",
        ok_to_download_for_research=True,
        ok_to_submit=promote, slot_approved=promote,
        submission_slots_used=0,
        instruction=("OK TO DOWNLOAD AND SUBMIT: all automated gates G1-G6 pass; owner uploads "
                     "manually on DrivenData (this repo never contacts DrivenData)."
                     if promote else
                     "DO NOT SUBMIT: at least one automated gate failed (see gates); "
                     "research download only."),
        files=dict(zeros=f"docs/downloads/{out_tif.name}", nan=f"docs/downloads/{nan_tif.name}",
                   zip=f"docs/downloads/{out_tif.with_suffix('.zip').name}",
                   nan_zip=f"docs/downloads/{nan_zip.name}"),
        preregistration="knowledge/2026-10-26_h31u_preregistration.md",
        evidence=dict(canary="evidence/h31u/canary.json", exp1="evidence/h31u/exp1_screen.json",
                      exp2="evidence/h31u/exp2.json", exp3="evidence/h31u/exp3.json"),
    )
    (EVID / "run_card.json").write_text(json.dumps(card, indent=1, default=float) + "\n")
    (ROOT / "docs/downloads/h31u-run-card.json").write_text(json.dumps(card, indent=1, default=float) + "\n")
    (ROOT / "registry/h31u_current_run.json").write_text(json.dumps(card, indent=1, default=float) + "\n")
    log("PACKAGE", name, "verdict", card["verdict"], "gates",
        {k: v for k, v in gates.items() if k.startswith("G")})
    log("sha256 zeros", card["raster_sha256"])
    return card


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("stage", choices=["lines", "canary", "exp1", "exp2", "exp3", "package", "all"])
    args = ap.parse_args()
    stages = ["lines", "canary", "exp1", "exp2", "exp3", "package"] if args.stage == "all" else [args.stage]
    for s in stages:
        log("=== STAGE", s, "===")
        {"lines": build_lines, "canary": run_canary, "exp1": run_exp1,
         "exp2": run_exp2, "exp3": run_exp3, "package": run_package}[s]()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
