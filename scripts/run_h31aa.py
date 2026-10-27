#!/usr/bin/env python3
"""Execute Lane H31-AA (SLFS): Strike-Coherent Logarithmic Piedmont Flexure
with Equipotential Paleoshoreline Rejection & Subsurface Basin-Edge Corroboration.

Frozen preregistration: ``knowledge/2026-10-27_h31aa_preregistration.md``
Pinned SHA-256 receipt: ``evidence/h31aa/preregistration_pin.json``

Reuses shared ``vendor/gems57/evaluate_holdout.py`` (``gems57-pooled-hide-v2``),
``vendor/gems57/spatial.py``, ``vendor/gems57/submission_writer.py``,
``vendor/gems57/uniqueness.py``, and ``scripts/run_h31u.py`` primitives.

3-Experiment Budget (Protocol §6):
- Stage 0 (pre-experiment): Preregistration SHA check + feature lines +
  single-feature leakage canary (two-sided AUC <= 0.90) + pre-placement
  surface discrete uniqueness check (|rho| <= 0.90, top-K 3-px overlap <= 0.70).
- EXP-1: 4-arm screen (AA1..AA4) vs same-run rebuilt H31-X (JUNC_INC), CTRL,
  SLOPE on 213-px buffered quadrant folds (60,988 withheld positives).
- EXP-2: Crest-thinning ablation (crest1px vs nocrest) on EXP-1 winner +
  final 37,654-dot emission + full two-stage discrete & literal registry audit.
- EXP-3: Untouched random-component confirmation split (seed=3107) +
  off-catalogue USGS-SGMC discovery proxy + cross-family calibration diagnostic.
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
from scipy import ndimage as ndi
from scipy.ndimage import distance_transform_edt, gaussian_filter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))

import run_h31u as U  # noqa: E402
from gems57 import evaluate_holdout as ev  # noqa: E402
from gems57 import metric as vmetric  # noqa: E402
from gems57 import spatial, submission_writer, uniqueness  # noqa: E402
from gemsdoe31.h31aa_features import compute_h31aa_fields  # noqa: E402
from gemsdoe31.release_policy import overlap_budget_preflight  # noqa: E402
from gemsdoe31.submission import sha256_file, validate_submission  # noqa: E402

LANE = "H31-AA"
PREREG = "knowledge/2026-10-27_h31aa_preregistration.md"
PREREG_PIN = ROOT / "evidence/h31aa/preregistration_pin.json"
CACHE = ROOT / "work/h31aa_lines"
EVID = ROOT / "evidence/h31aa"
BUDGET = 37_654
B_PX = 2.0
CONFIRM_SEED = 3107

CANDIDATE_ARMS = ("AA1", "AA2", "AA3", "AA4")
COMPARATORS = ("JUNC_INC", "CTRL", "SLOPE")
ALL_ARMS = CANDIDATE_ARMS + COMPARATORS

ARM_DESC = {
    "AA1": "LFLEX_COH (multi-scale steered log-flexure 1-px crest)",
    "AA2": "LFLEX_SHORE (steered log-flexure x paleoshoreline null 1-px crest)",
    "AA3": "LFLEX_SHORE x (0.65 + 0.35 * SUB_EDGE) 1-px crest",
    "AA4": "LFLEX_SHORE x (0.55 + 0.25 * SUB_EDGE + 0.20 * LIDAR_TOE) 1-px crest",
}

FIXED_REFS = {
    "REF_H33_2778": "data/prior_audit/GEMSDOE32/docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif",
    "REF_G27_DRCG_2250": "data/prior_audit/GEMSDOE27/docs/downloads/gems27-h31-drcg-wl-celf28-20261026-cf8e1bbef244-allfinite.tif",
    "REF_G27_H29_2190": "data/prior_audit/GEMSDOE27/docs/downloads/gems27-h29-hydrothermal-piedmont-celf-20261025-511898747886-allfinite.tif",
    "REF_G36_KPL36_1647": "data/prior_audit/GEMSDOE36/docs/downloads/gemsdoe36-kpl36-exp3-20261026-fc869911e88c-zeros.tif",
    "REF_H31X_DOTS": "docs/downloads/gemsdoe31-h31x-piedmont-junction-37654-20261026-5a956da9-zeros.tif",
}


def log(*a) -> None:
    print(f"[{LANE}]", *a, flush=True)


def verify_preregistration_frozen() -> dict:
    pin = json.loads(PREREG_PIN.read_text())
    actual = sha256_file(ROOT / PREREG)
    if actual != pin["sha256"]:
        raise RuntimeError(f"Preregistration drift: {actual} != pinned {pin['sha256']}")
    return pin


def _compute_junc_inc(elev: np.ndarray, slope: np.ndarray, foot: np.ndarray) -> np.ndarray:
    """Exact rebuild of H31-X winning X1 (JUNC_RAW, holdout best 0.166133)."""
    zs = gaussian_filter(elev, 1.5, mode="nearest")
    gy = gaussian_filter(zs, 1.0, order=(1, 0), mode="nearest")
    gx = gaussian_filter(zs, 1.0, order=(0, 1), mode="nearest")
    mag = np.hypot(gy, gx) + 1e-6
    uy, ux = -gy / mag, -gx / mag
    ss = gaussian_filter(slope, 1.5, mode="nearest")
    sy = gaussian_filter(ss, 1.0, order=(1, 0), mode="nearest")
    sx = gaussian_filter(ss, 1.0, order=(0, 1), mode="nearest")
    d_down = sy * uy + sx * ux
    w = np.zeros_like(ss, dtype=np.float32)
    rise = (ss > 1.0) & (ss < 3.0)
    w[rise] = (ss[rise] - 1.0) / 2.0
    w[(ss >= 3.0) & (ss <= 15.0)] = 1.0
    fall = (ss > 15.0) & (ss < 25.0)
    w[fall] = (25.0 - ss[fall]) / 10.0
    j = np.maximum(-d_down, 0.0) * w
    j[~foot] = 0.0
    return U.rank01(j.astype(np.float32), foot)


# ---------------------------------------------------------------- Stage 0a: lines
def build_lines() -> dict:
    pin = verify_preregistration_frozen()
    CACHE.mkdir(parents=True, exist_ok=True)
    EVID.mkdir(parents=True, exist_ok=True)
    foot, *_ = U.load_grid()

    elev = U.clean(U.stack_band("det_elev", foot), foot)
    slope = U.clean(U.stack_band("det_elev_slope", foot), foot)
    iso_hg = U.clean(U.stack_band("iso_grav_anom_hg", foot), foot)
    dbase = U.clean(U.stack_band("depth_to_base_surf", foot), foot)
    tmi_hg = U.clean(U.stack_band("tmi_hg", foot), foot)
    tmi_vg = U.clean(U.stack_band("tmi_vg", foot), foot)
    step_max = U.stack_band("step_max", foot)
    downface_max = U.stack_band("downface_max", foot)
    raw_valid = U.stack_band("valid", foot)
    lidar_valid = np.isfinite(raw_valid) & (raw_valid > 0)

    fields = compute_h31aa_fields(
        elev=elev,
        slope_deg=slope,
        iso_grav_hg=iso_hg,
        depth_base=dbase,
        tmi_hg=tmi_hg,
        tmi_vg=tmi_vg,
        step_max=step_max,
        downface_max=downface_max,
        lidar_valid=lidar_valid,
        foot=foot,
        rank_fn=U.rank01,
        gradmag_fn=U.gradmag,
        geomean_fn=U.geomean_rank,
    )
    fields["JUNC_INC"] = _compute_junc_inc(elev, slope, foot)
    fields["CTRL"] = U.rank01(tmi_hg, foot)
    fields["SLOPE"] = U.rank01(slope, foot)

    saved = {}
    for k, arr in fields.items():
        p = CACHE / f"{k}.npy"
        np.save(p, arr.astype(np.float32))
        vals = arr[foot]
        saved[k] = dict(
            path=str(p.relative_to(ROOT)),
            min=float(vals.min()),
            median=float(np.median(vals)),
            p99=float(np.percentile(vals, 99.0)),
            max=float(vals.max()),
        )
        log("saved", k, "med=", round(saved[k]["median"], 4), "p99=", round(saved[k]["p99"], 4))

    meta = dict(
        lane=LANE,
        preregistration=pin,
        footprint_pixels=int(foot.sum()),
        lidar_coverage_fraction=float((foot & lidar_valid).sum() / foot.sum()),
        shoreline_damped_fraction_lt_080=float((fields["w_shore"][foot] < 0.80).mean()),
        fields=saved,
    )
    (EVID / "lines.json").write_text(json.dumps(meta, indent=2) + "\n")
    return meta


def load_field(name: str) -> np.ndarray:
    return np.load(CACHE / f"{name}.npy")


def arm_surface(arm: str, *, crest: bool = True) -> np.ndarray:
    if arm in CANDIDATE_ARMS:
        suffix = "crest" if crest else "nocrest"
        return load_field(f"{arm}_{suffix}")
    return load_field(arm)


# ---------------------------------------------------------------- Peer loading & uniqueness
def collect_peer_catalog(foot: np.ndarray, exclude_prefix: str = "gemsdoe31-h31aa-") -> list[dict]:
    """Load all discrete & soft peers: 9 historical focus rasters + 9 Oct 25-26
    newly scored focus rasters + all local GEMSDOE31 downloads (deduplicated by SHA-256)."""
    seen_sha: dict[str, dict] = {}

    def register(peer_id: str, path: Path) -> None:
        if not path.is_file() or path.name.startswith(exclude_prefix):
            return
        pdots, n_theirs, h = U.read_dots(str(path), foot)
        if h in seen_sha:
            seen_sha[h]["aliases"].append(peer_id)
            return
        rep_class = uniqueness.representation_class(n_theirs, int(foot.sum()))["kind"]
        halo = uniqueness._near(pdots)
        seen_sha[h] = dict(
            id=peer_id,
            aliases=[peer_id],
            path=str(path.relative_to(ROOT)),
            sha256=h,
            their_dots=int(n_theirs),
            representation=rep_class,
            pdots=pdots,
            halo=halo,
        )

    fetch = json.loads((ROOT / "evidence/regime31/peer_fetch.json").read_text())
    for it in fetch["files"]:
        if "dest" in it:
            register(f"{it['repo']}:{Path(it['dest']).name}", ROOT / it["dest"])

    for p in sorted((ROOT / "data/prior").glob("*.tif")):
        register(f"prior:{p.name}", p)

    for p in sorted((ROOT / "data/prior_audit").rglob("*.tif")):
        register(f"prior_audit:{p.name}", p)

    for p in sorted((ROOT / "docs/downloads").glob("*.tif")):
        if p.name.endswith("-nan.tif"):
            continue
        register(f"GEMSDOE31:{p.name}", p)

    return list(seen_sha.values())


def topk_mask(surf: np.ndarray, foot: np.ndarray, k: int = BUDGET) -> np.ndarray:
    flat = np.where(foot, surf, -np.inf)
    vals = flat[foot]
    if k >= vals.size:
        return foot.copy()
    order = np.argpartition(vals, -k)[-k:]
    mask_1d = np.zeros(vals.size, dtype=bool)
    mask_1d[order] = True
    out = np.zeros(surf.shape, dtype=bool)
    out[foot] = mask_1d
    return out


def _fast_spearman_vs_binary(ranks_01: np.ndarray, bin_mask_1d: np.ndarray) -> float:
    """Exact Spearman correlation between pre-ranked [0, 1] vector and binary vector."""
    n = ranks_01.size
    n1 = int(bin_mask_1d.sum())
    if n1 == 0 or n1 == n or float(np.ptp(ranks_01)) == 0.0:
        return 0.0
    n0 = n - n1
    mr = float(ranks_01.mean())
    sr = float(ranks_01.std())
    if sr == 0.0:
        return 0.0
    mean1 = float(ranks_01[bin_mask_1d].mean())
    p = n1 / float(n)
    q = n0 / float(n)
    return float((mean1 - mr) * np.sqrt(p / q) / sr)


def _lattice_outside_halo_pixels(foot: np.ndarray) -> int:
    from audit_shared_registry_stop import load_counterexample
    _pin, ref = load_counterexample(ROOT, restore=True)
    control = foot & np.isfinite(ref) & (ref > 0)
    covered = uniqueness._near(control)
    return int((foot & ~covered).sum())


def audit_against_peers(surf: np.ndarray, dots: np.ndarray | None,
                        foot: np.ndarray, peers: list[dict], *,
                        allowed: np.ndarray | None = None,
                        exact_scipy: bool = False) -> dict:
    """Two-stage uniqueness audit (pre-placement top-K AND final dots)."""
    k_target = int(dots.sum()) if dots is not None else BUDGET
    domain = allowed if allowed is not None else foot
    tk = topk_mask(surf, domain, k_target)
    ranks_s = U.rank01(surf, foot)[foot].astype(np.float64)
    dots_1d = dots[foot] if dots is not None else None
    ranks_d = U.rank01(dots.astype(np.float32), foot)[foot].astype(np.float64) if dots is not None else None
    rows = []
    for p in peers:
        halo = p["halo"]
        pdots_f = p["pdots"].astype(np.float32)
        p_1d = p["pdots"][foot]
        ov_topk = float(halo[tk].mean()) if tk.any() else 0.0
        ov_final = float(halo[dots].mean()) if (dots is not None and dots.any()) else None
        if exact_scipy:
            rho_s = uniqueness.surface_rho(surf, pdots_f, foot)["spearman_full_footprint"]
            rho_d = (uniqueness.surface_rho(dots.astype(np.float32), pdots_f, foot)["spearman_full_footprint"]
                     if dots is not None else None)
        else:
            rho_s = _fast_spearman_vs_binary(ranks_s, p_1d)
            rho_d = _fast_spearman_vs_binary(ranks_d, p_1d) if dots_1d is not None else None
        jac = (uniqueness._jaccard(dots, p["pdots"]) if dots is not None else None)
        is_local = all(a.startswith("GEMSDOE31:") for a in p["aliases"])
        rows.append(dict(
            peer=p["id"],
            aliases=p["aliases"],
            is_local_gemsdoe31=is_local,
            sha256=p["sha256"],
            their_dots=p["their_dots"],
            representation=p["representation"],
            topk_overlap_3px=ov_topk,
            final_overlap_3px=ov_final,
            surface_spearman_full=rho_s,
            dots_spearman_full=rho_d,
            jaccard=jac,
        ))
    discrete = [r for r in rows if r["representation"] == "dot_field"]
    ext_disc = [r for r in discrete if not r["is_local_gemsdoe31"]]
    max_topk = max((r["topk_overlap_3px"] for r in discrete), default=0.0)
    worst_topk_peer = max(discrete, key=lambda r: r["topk_overlap_3px"], default=None)
    ext_max_topk = max((r["topk_overlap_3px"] for r in ext_disc), default=0.0)
    ext_worst_topk_peer = max(ext_disc, key=lambda r: r["topk_overlap_3px"], default=None)
    max_final = (max((r["final_overlap_3px"] for r in discrete if r["final_overlap_3px"] is not None), default=0.0)
                 if dots is not None else None)
    worst_final_peer = (max(discrete, key=lambda r: r["final_overlap_3px"] or 0.0, default=None)
                        if dots is not None else None)
    ext_max_final = (max((r["final_overlap_3px"] for r in ext_disc if r["final_overlap_3px"] is not None), default=0.0)
                     if dots is not None else None)
    ext_worst_final_peer = (max(ext_disc, key=lambda r: r["final_overlap_3px"] or 0.0, default=None)
                            if dots is not None else None)
    max_rho_s = max((abs(r["surface_spearman_full"]) for r in rows
                     if r["surface_spearman_full"] is not None), default=0.0)
    max_rho_d = (max((abs(r["dots_spearman_full"]) for r in rows
                      if r["dots_spearman_full"] is not None), default=0.0)
                 if dots is not None else None)
    pre_all_ok = bool(max_topk <= 0.70 and max_rho_s <= 0.90)
    pre_ext_ok = bool(ext_max_topk <= 0.70 and max_rho_s <= 0.90)
    protocol_rho_final_ok = bool(
        max_rho_s <= 0.90
        and (max_final is not None and max_final <= 0.70)
        and (max_rho_d is not None and max_rho_d <= 0.90)
    ) if dots is not None else None
    ext_two_stage_ok = bool(
        pre_ext_ok
        and (ext_max_final is not None and ext_max_final <= 0.70)
        and (max_rho_d is not None and max_rho_d <= 0.90)
    ) if dots is not None else None
    all_two_stage_ok = bool(
        pre_all_ok
        and (max_final is not None and max_final <= 0.70)
        and (max_rho_d is not None and max_rho_d <= 0.90)
    ) if dots is not None else None
    return dict(
        n_peers_checked=len(rows),
        n_discrete_peers=len(discrete),
        n_external_focus_discrete_peers=len(ext_disc),
        topk_budget=int(tk.sum()),
        my_dots=int(dots.sum()) if dots is not None else None,
        discrete_max_topk_overlap=float(max_topk),
        worst_topk_peer=(worst_topk_peer["peer"] if worst_topk_peer else None),
        external_focus_max_topk_overlap=float(ext_max_topk),
        external_focus_worst_topk_peer=(ext_worst_topk_peer["peer"] if ext_worst_topk_peer else None),
        discrete_max_final_overlap=(float(max_final) if max_final is not None else None),
        worst_final_peer=(worst_final_peer["peer"] if worst_final_peer else None),
        external_focus_max_final_overlap=(float(ext_max_final) if ext_max_final is not None else None),
        external_focus_worst_final_peer=(ext_worst_final_peer["peer"] if ext_worst_final_peer else None),
        max_abs_surface_spearman=float(max_rho_s),
        max_abs_dots_spearman=(float(max_rho_d) if max_rho_d is not None else None),
        preplacement_surface_rho_pass=bool(max_rho_s <= 0.90),
        preplacement_external_focus_topk_pass=pre_ext_ok,
        preplacement_discrete_pass=pre_all_ok,
        protocol_surface_rho_and_final_dots_pass=protocol_rho_final_ok,
        external_focus_two_stage_pass=ext_two_stage_ok,
        two_stage_discrete_pass=all_two_stage_ok,
        rows=rows,
    )


# ---------------------------------------------------------------- Stage 0b: Canary + Pre-placement uniqueness
def run_canary() -> dict:
    verify_preregistration_frozen()
    foot, cat, sgmc, off_sgmc, _ = U.load_grid()
    rows = []
    line_names = ("LFLEX_COH", "LFLEX_SHORE", "SUB_EDGE", "LIDAR_TOE", "JUNC_INC", "CTRL", "SLOPE")
    for k in line_names:
        arr = load_field(k)
        a_cat = U.auc_for(arr, cat, foot)
        a_off = U.auc_for(arr, off_sgmc, foot & ~cat)
        two_sided = float(max(a_cat, a_off, 1.0 - a_cat, 1.0 - a_off))
        rows.append(dict(
            feature=k, kind="single_line",
            auc_catalogue=float(a_cat), auc_off_sgmc=float(a_off),
            max_two_sided_auc=two_sided,
            leakage_flagged=bool(two_sided > 0.90),
        ))
        log("canary line", k, "cat=", round(a_cat, 4), "off_sgmc=", round(a_off, 4))

    for arm in CANDIDATE_ARMS:
        for crest_flag in (True, False):
            tag = f"{arm}_{'crest' if crest_flag else 'nocrest'}"
            arr = arm_surface(arm, crest=crest_flag)
            a_cat = U.auc_for(arr, cat, foot)
            a_off = U.auc_for(arr, off_sgmc, foot & ~cat)
            two_sided = float(max(a_cat, a_off, 1.0 - a_cat, 1.0 - a_off))
            rows.append(dict(
                feature=tag, kind="candidate_surface",
                auc_catalogue=float(a_cat), auc_off_sgmc=float(a_off),
                max_two_sided_auc=two_sided,
                leakage_flagged=bool(two_sided > 0.90),
            ))
            log("canary surface", tag, "cat=", round(a_cat, 4), "off_sgmc=", round(a_off, 4))

    rep = dict(
        lane=LANE,
        evidence_class="COMPUTED",
        auc_ceiling=0.90,
        rows=rows,
        all_pass=bool(all(not r["leakage_flagged"] for r in rows)),
    )
    (EVID / "canary.json").write_text(json.dumps(rep, indent=2) + "\n")
    if not rep["all_pass"]:
        raise RuntimeError("STOP: Leakage canary failed (> 0.90 two-sided AUC)!")

    # Stage-0 Pre-placement surface uniqueness check BEFORE EXP-1
    _foot2, _cat2, _sg2, _off2, d_cat = U.load_grid()
    allowed_full = foot & (d_cat > B_PX)
    peers = collect_peer_catalog(foot)
    log("loaded unique peer rasters:", len(peers))
    pre = {}
    for arm in CANDIDATE_ARMS:
        for crest_flag in (True, False):
            tag = f"{arm}_{'crest' if crest_flag else 'nocrest'}"
            aud = audit_against_peers(arm_surface(arm, crest=crest_flag), None, foot, peers,
                                      allowed=allowed_full)
            pre[tag] = dict(
                discrete_max_topk_overlap=aud["discrete_max_topk_overlap"],
                worst_topk_peer=aud["worst_topk_peer"],
                external_focus_max_topk_overlap=aud["external_focus_max_topk_overlap"],
                external_focus_worst_topk_peer=aud["external_focus_worst_topk_peer"],
                max_abs_surface_spearman=aud["max_abs_surface_spearman"],
                preplacement_surface_rho_pass=aud["preplacement_surface_rho_pass"],
                preplacement_external_focus_topk_pass=aud["preplacement_external_focus_topk_pass"],
                preplacement_discrete_pass=aud["preplacement_discrete_pass"],
            )
            log("pre-placement", tag,
                "ext_topk=", round(aud["external_focus_max_topk_overlap"], 4),
                "all_topk=", round(aud["discrete_max_topk_overlap"], 4),
                "rho_s=", round(aud["max_abs_surface_spearman"], 4))

    outside_halo = _lattice_outside_halo_pixels(foot)
    preflight = overlap_budget_preflight(
        footprint_pixels=int(foot.sum()),
        outside_halo_pixels=outside_halo,
        candidate_dots=BUDGET,
    )
    pre_rep = dict(
        lane=LANE,
        stage="pre-placement-uniqueness",
        n_unique_peers=len(peers),
        arms=pre,
        literal_registry_preflight=preflight,
    )
    (EVID / "preplacement_uniqueness.json").write_text(json.dumps(pre_rep, indent=2) + "\n")
    return rep


# ---------------------------------------------------------------- Holdout helpers
def load_fixed_refs(foot: np.ndarray) -> dict[str, np.ndarray]:
    out = {}
    for k, rel in FIXED_REFS.items():
        p = ROOT / rel
        if p.is_file():
            dots, n, h = U.read_dots(str(p), foot)
            out[k] = dots
            log("fixed ref", k, n, "dots", h[:12])
    return out


def score_arms(arm_surfaces: dict[str, np.ndarray], folds: list[dict],
               foot: np.ndarray, fixed: dict[str, np.ndarray] | None = None) -> dict:
    terms: dict[str, np.ndarray] = {}
    per_fold: dict[str, list] = {a: [] for a in list(arm_surfaces) + list(fixed or {})}

    def add(name: str, pred: np.ndarray, f: dict) -> None:
        res, trm = ev.evaluate(pred, f, foot)
        terms[name] = trm if name not in terms else terms[name] + trm
        dti_val = float(vmetric.dti_from_components(res["tpw"], res["fpw"], res["fnw"]))
        per_fold[name].append(dict(
            fold=int(f["fold"]),
            dti=dti_val,
            n_truth=int(res["n_truth"]),
            emitted_active=int(res["n_emitted"]),
        ))
        log(" fold", f["fold"], name, "dti=", round(dti_val, 4), "truth=", res["n_truth"])

    for f in folds:
        d_vis = distance_transform_edt(~f["visible"])
        allowed = foot & (d_vis > B_PX)
        for arm, surf in arm_surfaces.items():
            dots = U.emit_dots(surf, allowed & (surf > 0))
            add(arm, dots.astype(np.float32), f)
        for name, dots in (fixed or {}).items():
            add(name, dots.astype(np.float32), f)
    return dict(terms=terms, per_fold=per_fold)


def random_component_split(cat: np.ndarray, foot: np.ndarray, seed: int) -> dict:
    comp, n = ndi.label(cat, np.ones((3, 3), bool))
    rng = np.random.default_rng(seed)
    hidden_ids = np.flatnonzero(rng.random(n + 1) < 0.5)
    hidden_ids = hidden_ids[hidden_ids > 0]
    hidden = np.isin(comp, hidden_ids) & cat
    visible = cat & ~hidden
    return dict(
        fold=9,
        region=foot.copy(),
        visible=visible,
        masked_known=visible,
        truth=hidden,
        receipt=dict(
            split="random-component-50pct",
            seed=seed,
            components=int(n),
            hidden_components=int(hidden_ids.size),
            truth_px=int(hidden.sum()),
            visible_px=int(visible.sum()),
        ),
    )


# ---------------------------------------------------------------- EXP-1
def run_exp1() -> dict:
    verify_preregistration_frozen()
    foot, cat, *_ = U.load_grid()
    pre = json.loads((EVID / "preplacement_uniqueness.json").read_text())["arms"]
    rho_eligible = [a for a in CANDIDATE_ARMS if pre[f"{a}_crest"]["preplacement_surface_rho_pass"]]
    ext_topk_eligible = [a for a in CANDIDATE_ARMS if pre[f"{a}_crest"]["preplacement_external_focus_topk_pass"]]
    strict_all_topk_eligible = [a for a in CANDIDATE_ARMS if pre[f"{a}_crest"]["preplacement_discrete_pass"]]
    if not rho_eligible:
        raise RuntimeError("STOP: Zero candidate arms passed pre-placement |Spearman rho| <= 0.90!")
    eligible = strict_all_topk_eligible or ext_topk_eligible or rho_eligible

    surfs = {a: arm_surface(a, crest=True) for a in ALL_ARMS}
    fixed = load_fixed_refs(foot)
    folds = list(spatial.folds(cat, foot, buffer_px=213))
    receipts = [f["receipt"] for f in folds]
    out = score_arms(surfs, folds, foot, fixed)
    scores_tmp = U.pooled(out["terms"], candidate=eligible[0])["scores"]
    winner = max(eligible, key=lambda a: scores_tmp[a]["dti"])
    best_overall_arm = max(CANDIDATE_ARMS, key=lambda a: scores_tmp[a]["dti"])
    summ = U.pooled(out["terms"], candidate=winner)
    rep = dict(
        lane=LANE,
        experiment="EXP-1 4-arm screen",
        evaluator_version=ev.VERSION,
        buffer_px=213,
        eligible_strict_all_topk=strict_all_topk_eligible,
        eligible_external_focus_topk=ext_topk_eligible,
        eligible_surface_rho=rho_eligible,
        eligible_used=eligible,
        best_unconstrained_arm=best_overall_arm,
        fold_receipts=receipts,
        per_fold=out["per_fold"],
        pooled=summ,
        winner=winner,
        winner_description=ARM_DESC[winner],
        fixed_reference_caveat=(
            "REF_* rasters were emitted once outside the full catalogue (d_cat > 2 px), "
            "not re-emitted per fold, so their hide-and-recover numbers carry a ~2 px collar "
            "handicap on hidden faults; same-run JUNC_INC rebuilds H31-X on identical fold rules."
        ),
    )
    (EVID / "exp1_screen.json").write_text(json.dumps(rep, indent=2, default=float) + "\n")
    for k, v in summ["scores"].items():
        log("EXP-1", k, "DTI=", round(v["dti"], 5), "CI95=", [round(x, 5) for x in v["ci95"]])
    log("EXP-1 WINNER:", winner, "vs JUNC_INC delta=",
        round(summ["paired_differences"]["JUNC_INC"]["delta"], 5),
        "CI95=", [round(x, 5) for x in summ["paired_differences"]["JUNC_INC"]["ci95"]])
    return rep


# ---------------------------------------------------------------- EXP-2
def run_exp2() -> dict:
    verify_preregistration_frozen()
    foot, cat, _sgmc, _off_sgmc, d_cat = U.load_grid()
    exp1 = json.loads((EVID / "exp1_screen.json").read_text())
    winner = exp1["winner"]
    folds = list(spatial.folds(cat, foot, buffer_px=213))
    surfs = {
        f"{winner}_crest": arm_surface(winner, crest=True),
        f"{winner}_nocrest": arm_surface(winner, crest=False),
        "JUNC_INC": arm_surface("JUNC_INC"),
        "CTRL": arm_surface("CTRL"),
        "SLOPE": arm_surface("SLOPE"),
    }
    out = score_arms(surfs, folds, foot)
    peers = collect_peer_catalog(foot)
    allowed_full = foot & (d_cat > B_PX)

    variant_audits = {}
    for crest_flag in (True, False):
        key = f"{winner}_{'crest' if crest_flag else 'nocrest'}"
        s = surfs[key]
        d = U.emit_dots(s, allowed_full & (s > 0))
        aud = audit_against_peers(s, d, foot, peers, allowed=allowed_full)
        variant_audits[key] = dict(
            dots=int(d.sum()),
            discrete_max_topk_overlap=aud["discrete_max_topk_overlap"],
            worst_topk_peer=aud["worst_topk_peer"],
            external_focus_max_topk_overlap=aud["external_focus_max_topk_overlap"],
            external_focus_worst_topk_peer=aud["external_focus_worst_topk_peer"],
            discrete_max_final_overlap=aud["discrete_max_final_overlap"],
            worst_final_peer=aud["worst_final_peer"],
            external_focus_max_final_overlap=aud["external_focus_max_final_overlap"],
            max_abs_surface_spearman=aud["max_abs_surface_spearman"],
            max_abs_dots_spearman=aud["max_abs_dots_spearman"],
            protocol_surface_rho_and_final_dots_pass=aud["protocol_surface_rho_and_final_dots_pass"],
            external_focus_two_stage_pass=aud["external_focus_two_stage_pass"],
            two_stage_discrete_pass=aud["two_stage_discrete_pass"],
        )

    summ_tmp = U.pooled(out["terms"], candidate=f"{winner}_crest")["scores"]
    passing = (
        [k for k in (f"{winner}_crest", f"{winner}_nocrest")
         if variant_audits[k]["two_stage_discrete_pass"]]
        or [k for k in (f"{winner}_crest", f"{winner}_nocrest")
            if variant_audits[k]["external_focus_two_stage_pass"]]
        or [k for k in (f"{winner}_crest", f"{winner}_nocrest")
            if variant_audits[k]["protocol_surface_rho_and_final_dots_pass"]]
    )
    if passing:
        final_key = max(passing, key=lambda k: (summ_tmp[k]["dti"], 1 if k.endswith("_crest") else 0))
    else:
        final_key = f"{winner}_crest"
    use_crest = final_key.endswith("_crest")
    summ = U.pooled(out["terms"], candidate=final_key)

    final_surf = surfs[final_key]
    final_dots = U.emit_dots(final_surf, allowed_full & (final_surf > 0))
    full_audit = audit_against_peers(final_surf, final_dots, foot, peers,
                                     allowed=allowed_full, exact_scipy=True)
    lit = U.literal_witness(final_dots, foot)
    outside_halo = _lattice_outside_halo_pixels(foot)
    preflight = overlap_budget_preflight(
        footprint_pixels=int(foot.sum()),
        outside_halo_pixels=outside_halo,
        candidate_dots=int(final_dots.sum()),
    )

    slope = U.clean(U.stack_band("det_elev_slope", foot), foot)
    s_dots = slope[final_dots]
    dc_dots = d_cat[final_dots]
    diagnostics = dict(
        emitted_dots=int(final_dots.sum()),
        min_d_cat_px=float(dc_dots.min()),
        median_d_cat_px=float(np.median(dc_dots)),
        frac_d_cat_le_15px=float((dc_dots <= 15.0).mean()),
        slope_deg_median=float(np.median(s_dots)),
        frac_slope_lt_3deg=float((s_dots < 3.0).mean()),
        frac_slope_3_to_15deg=float(((s_dots >= 3.0) & (s_dots <= 15.0)).mean()),
        frac_slope_gt_15deg=float((s_dots > 15.0).mean()),
        frac_slope_gt_18deg=float((s_dots > 18.0).mean()),
    )

    np.save(CACHE / "final_surface.npy", final_surf.astype(np.float32))
    np.save(CACHE / "final_dots.npy", final_dots)
    (CACHE / "final_choice.json").write_text(
        json.dumps(dict(arm=winner, crest=use_crest, final_variant=final_key,
                        description=ARM_DESC[winner]), indent=2) + "\n"
    )

    rep = dict(
        lane=LANE,
        experiment="EXP-2 crest ablation + final emission + two-stage uniqueness",
        winner_from_exp1=winner,
        ablation=dict(
            final_variant=final_key,
            crest_kept=use_crest,
            variant_uniqueness_summary=variant_audits,
            per_fold=out["per_fold"],
            pooled=summ,
        ),
        diagnostics=diagnostics,
        uniqueness=full_audit,
        literal_witness=lit,
        literal_registry_preflight=preflight,
    )
    (EVID / "exp2.json").write_text(json.dumps(rep, indent=2, default=float) + "\n")
    log("EXP-2 final", final_key, "DTI=", round(summ["scores"][final_key]["dti"], 5),
        "topk_ov=", round(full_audit["discrete_max_topk_overlap"], 4),
        "final_ov=", round(full_audit["discrete_max_final_overlap"], 4),
        "two_stage_pass=", full_audit["two_stage_discrete_pass"])
    log("EXP-2 diagnostics:", diagnostics)
    return rep


# ---------------------------------------------------------------- EXP-3
def run_exp3() -> dict:
    verify_preregistration_frozen()
    foot, cat, _sgmc, off_sgmc, _d_cat = U.load_grid()
    choice = json.loads((CACHE / "final_choice.json").read_text())
    winner = choice["arm"]
    final_surf = np.load(CACHE / "final_surface.npy")
    final_dots = np.load(CACHE / "final_dots.npy")

    cfold = random_component_split(cat, foot, seed=CONFIRM_SEED)
    surfs = {
        winner: final_surf,
        "JUNC_INC": arm_surface("JUNC_INC"),
        "CTRL": arm_surface("CTRL"),
        "SLOPE": arm_surface("SLOPE"),
    }
    fixed = load_fixed_refs(foot)
    cout = score_arms(surfs, [cfold], foot, fixed)
    conf = U.pooled(cout["terms"], candidate=winner)

    h33, _, _ = U.read_dots(str(ROOT / FIXED_REFS["REF_H33_2778"]), foot)
    g27, _, _ = U.read_dots(str(ROOT / FIXED_REFS["REF_G27_DRCG_2250"]), foot)
    h31x, _, _ = U.read_dots(str(ROOT / FIXED_REFS["REF_H31X_DOTS"]), foot)

    slope = U.clean(U.stack_band("det_elev_slope", foot), foot)
    eval_mask = foot & ~cat
    sg = dict(
        candidate=U.sgmc_score(final_dots & eval_mask, off_sgmc & eval_mask, eval_mask),
        H33=U.sgmc_score(h33 & eval_mask, off_sgmc & eval_mask, eval_mask),
        G27_DRCG=U.sgmc_score(g27 & eval_mask, off_sgmc & eval_mask, eval_mask),
        H31X=U.sgmc_score(h31x & eval_mask, off_sgmc & eval_mask, eval_mask),
    )
    for label, m in [
        ("basin_lt3deg", slope < 3.0),
        ("piedmont_3_15deg", (slope >= 3.0) & (slope < 15.0)),
        ("steep_ge15deg", slope >= 15.0),
    ]:
        sub = eval_mask & m
        sg[f"candidate_{label}"] = U.sgmc_score(final_dots & sub, off_sgmc & sub, sub)
        sg[f"H33_{label}"] = U.sgmc_score(h33 & sub, off_sgmc & sub, sub)
        sg[f"H31X_{label}"] = U.sgmc_score(h31x & sub, off_sgmc & sub, sub)

    rows_idx, cols_idx = np.where(foot)
    rmid, cmid = float(np.median(rows_idx)), float(np.median(cols_idx))
    rr, cc = np.indices(foot.shape)
    sg_quad = {}
    for qn, qm in [
        ("NW", (rr < rmid) & (cc < cmid)),
        ("NE", (rr < rmid) & (cc >= cmid)),
        ("SW", (rr >= rmid) & (cc < cmid)),
        ("SE", (rr >= rmid) & (cc >= cmid)),
    ]:
        sub = eval_mask & qm
        sg_quad[qn] = dict(
            candidate=U.sgmc_score(final_dots & sub, off_sgmc & sub, sub),
            H33=U.sgmc_score(h33 & sub, off_sgmc & sub, sub),
            H31X=U.sgmc_score(h31x & sub, off_sgmc & sub, sub),
        )

    calib = json.loads((ROOT / "evidence/cross_family_calibration_20261026.json").read_text())
    ov_h33 = float(uniqueness.dot_overlap(final_dots.astype(np.float32), h33.astype(np.float32)))
    n_dots = int(final_dots.sum())
    credit_per_dot = float(sg["candidate"]["tpw"] / max(n_dots, 1))
    cov_3px = float(uniqueness._near(final_dots)[foot].mean())
    m3_spec = calib["zero_catalogue_subset"]["M3"]
    c3 = m3_spec["coef_loo_fullfit"]["coef"]
    m3_val = float(np.clip(
        m3_spec["coef_loo_fullfit"]["intercept"]
        + c3[0] * credit_per_dot
        + c3[1] * cov_3px
        + c3[2] * np.log(max(n_dots, 1)),
        0.0, 1.0,
    ))
    m3_rmse = float(m3_spec["rmse"])
    m1_spec = calib["models"]["M1_selector_formula_frozen"]
    m1_val = float(np.clip(
        m1_spec["coef"]["scale"] * sg["candidate"]["tpw"] / (n_dots + m1_spec["coef"]["d0"]),
        0.0, 1.0,
    ))
    m1_rmse = float(m1_spec["rmse"])

    rep = dict(
        lane=LANE,
        experiment="EXP-3 untouched confirmation + off-catalogue SGMC + cross-family calibration diagnostic",
        winner=winner,
        confirmation=dict(partition=cfold["receipt"], per_fold=cout["per_fold"], pooled=conf),
        sgmc_full=sg,
        sgmc_quadrants=sg_quad,
        cross_family_projection_diagnostic=dict(
            evidence_class="PROJECTION (unvalidated cross-family diagnostic; NEVER a score; leaderboard_estimate=null)",
            overlap_3px_vs_h33=ov_h33,
            sgmc_credit_per_dot=credit_per_dot,
            footprint_coverage_3px=cov_3px,
            m3_zero_catalogue_central=m3_val,
            m3_loo_rmse_n62=m3_rmse,
            m3_interval_2rmse=[max(0.0, m3_val - 2.0 * m3_rmse), min(1.0, m3_val + 2.0 * m3_rmse)],
            m1_frozen_formula_output=m1_val,
            m1_cross_family_rmse_n67=m1_rmse,
            retired_for_point_prediction=True,
        ),
    )
    (EVID / "exp3.json").write_text(json.dumps(rep, indent=2, default=float) + "\n")
    log("EXP-3 confirm", winner, round(conf["scores"][winner]["dti"], 5),
        "vs JUNC_INC", round(conf["scores"]["JUNC_INC"]["dti"], 5),
        "delta=", round(conf["paired_differences"]["JUNC_INC"]["delta"], 5))
    log("EXP-3 SGMC cand=", round(sg["candidate"]["dti"], 4),
        "H33=", round(sg["H33"]["dti"], 4), "H31X=", round(sg["H31X"]["dti"], 4))
    return rep


# ---------------------------------------------------------------- Gates + Package
def evaluate_gates() -> dict:
    canary = json.loads((EVID / "canary.json").read_text())
    exp1 = json.loads((EVID / "exp1_screen.json").read_text())
    exp2 = json.loads((EVID / "exp2.json").read_text())
    exp3 = json.loads((EVID / "exp3.json").read_text())
    winner = exp3["winner"]
    final_key = exp2["ablation"]["final_variant"]
    ps = exp2["ablation"]["pooled"]
    pc = exp3["confirmation"]["pooled"]

    def pos_ci(diff: dict | None) -> bool:
        return bool(diff and diff["delta"] > 0 and diff["ci95"][0] > 0)

    d_inc_s = ps["paired_differences"].get("JUNC_INC")
    d_ctrl_s = ps["paired_differences"].get("CTRL")
    d_slope_s = ps["paired_differences"].get("SLOPE")
    d_inc_c = pc["paired_differences"].get("JUNC_INC")
    d_ctrl_c = pc["paired_differences"].get("CTRL")

    g2 = bool(canary["all_pass"])
    g3_vs_baselines = bool(pos_ci(d_ctrl_s) and pos_ci(d_slope_s) and pos_ci(d_ctrl_c))
    g3_beats_holdout_best = bool(g3_vs_baselines and pos_ci(d_inc_s) and pos_ci(d_inc_c))
    g4 = bool(exp3["sgmc_full"]["candidate"]["dti"] >= exp3["sgmc_full"]["H33"]["dti"])
    u = exp2["uniqueness"]
    g5_protocol_rho_final = bool(u["protocol_surface_rho_and_final_dots_pass"])
    g5_external_focus_two_stage = bool(u["external_focus_two_stage_pass"])
    g5_discrete = bool(u["two_stage_discrete_pass"])
    g5_literal = bool(exp2["literal_witness"]["candidate_overlap_3px"] <= 0.70
                      and not exp2["literal_registry_preflight"]["forced_duplicate_stop"])
    return dict(
        G2_canary=g2,
        G3_beats_baselines=g3_vs_baselines,
        G3_beats_holdout_best=g3_beats_holdout_best,
        G4_sgmc_discovery=g4,
        G5_protocol_surface_rho_and_final_dots=g5_protocol_rho_final,
        G5_external_focus_two_stage=g5_external_focus_two_stage,
        G5_discrete_two_stage=g5_discrete,
        G5_literal_broad_registry=g5_literal,
        detail=dict(
            winner=winner,
            final_variant=final_key,
            final_holdout=ps["scores"][final_key],
            incumbent_holdout=ps["scores"]["JUNC_INC"],
            screen_paired_vs_junc_inc=d_inc_s,
            screen_paired_vs_ctrl=d_ctrl_s,
            screen_paired_vs_slope=d_slope_s,
            confirmation_scores=pc["scores"],
            confirmation_paired_vs_junc_inc=d_inc_c,
            confirmation_paired_vs_ctrl=d_ctrl_c,
            exp1_screen_scores=exp1["pooled"]["scores"],
        ),
    )


def run_package() -> dict:
    pin = verify_preregistration_frozen()
    foot, cat, *_ = U.load_grid()
    choice = json.loads((CACHE / "final_choice.json").read_text())
    exp2 = json.loads((EVID / "exp2.json").read_text())
    exp3 = json.loads((EVID / "exp3.json").read_text())
    gates = evaluate_gates()
    dots = np.load(CACHE / "final_dots.npy")
    pred = np.where(foot, dots.astype(np.float32), 0.0).astype(np.float32)
    support_sha = hashlib.sha256(np.packbits(dots.ravel()).tobytes()).hexdigest()
    name = f"gemsdoe31-h31aa-slfs-flexure-{int(dots.sum())}-20261027-{support_sha[:8]}"
    hold = gates["detail"]["final_holdout"]
    note = (
        f"H31-AA {choice['arm']} SLFS log-flexure+shoreline-null {int(dots.sum())}d B2 | "
        f"HOLDOUT-DTI {hold['dti']:.4f} n={hold['withheld_positive_pixels']} | {support_sha[:8]}"
    )[:140]

    out_tif = ROOT / "docs/downloads" / f"{name}-zeros.tif"
    nan_tif = ROOT / "docs/downloads" / f"{name}-nan.tif"
    for existing in (
        out_tif,
        out_tif.with_suffix(".zip"),
        out_tif.with_suffix(".json"),
        nan_tif,
        nan_tif.with_suffix(".zip"),
    ):
        if existing.exists():
            existing.unlink()
    sample = ROOT / "data/sample_submission.tif"
    receipt = submission_writer.write_submission(
        out_tif, pred, sample, foot, note=note, name=name, catalogue=cat,
        metadata=dict(lane=LANE, arm=choice["arm"], crest=choice["crest"], prereg_sha256=pin["sha256"]),
    )
    with rasterio.open(sample) as ds:
        prof = ds.profile.copy()
    arr_nan = np.where(foot, pred, np.nan).astype(np.float32)
    prof.update(dtype="float32", count=1, nodata=float("nan"), compress="deflate")
    with rasterio.open(nan_tif, "w", **prof) as ds:
        ds.write(arr_nan, 1)
    nan_zip = nan_tif.with_suffix(".zip")
    with zipfile.ZipFile(nan_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.write(nan_tif, arcname=nan_tif.name)

    vz = validate_submission(out_tif, sample, convention="all-finite")
    vn = validate_submission(nan_tif, sample, convention="nan-outside")
    g1 = bool(vz["ok_to_upload_format_only"] and vn["ok_to_upload_format_only"])
    gates_full = dict(G1_format=g1, **gates)

    scientific_discrete_pass = bool(
        gates_full["G1_format"]
        and gates_full["G2_canary"]
        and gates_full["G3_beats_holdout_best"]
        and gates_full["G4_sgmc_discovery"]
        and gates_full["G5_discrete_two_stage"]
    )
    # Fail-closed under binding literal-registry-20261026-9883b598 policy & Protocol §6 selector rule:
    literal_and_all_pass = bool(scientific_discrete_pass and gates_full["G5_literal_broad_registry"])
    u = exp2["uniqueness"]
    sg = exp3["sgmc_full"]

    card = dict(
        lane=LANE,
        session_branch="arena/f5b2211b-gemsdoe31",
        generated_utc="2026-10-27",
        hypothesis=(
            "H31-AA (SLFS): Unmapped Great Basin range-bounding and degraded pre-Holocene piedmont "
            "faults exhibit a strike-persistent concave-up break in LOGARITHMIC slope "
            "-grad(ln(s + 1.5 deg)).u_down across 2-11 deg piedmont-to-lower-front transitions "
            "(tapering to zero above 18 deg intra-range cliffs), distinguishable from horizontal "
            "Pleistocene Lake Lahontan wave-cut benches via along-strike elevation variation and "
            "subsurface gravity / depth-to-basement / magnetic-contact steps, and localizable on "
            "strict 1-pixel cross-strike directional crests without any catalogue label input."
        ),
        mechanism=(
            f"{choice['arm']} ({choice['final_variant']}): {choice['description']}; "
            f"scales sigma in {{1.5, 3.0}} px, strike steering +-4 px, shoreline survival weight "
            f"w_shore in [0.35, 1.0], {'1-px cross-strike crest' if choice['crest'] else 'unthinned'}, "
            f"Poisson 2.8 px emission, {int(dots.sum())} binary dots on d(catalogue) > 2 px."
        ),
        non_fault_mimic=(
            "Pleistocene Lake Lahontan / pluvial equipotential wave-cut shorelines (damped by "
            "low along-strike delta-z + weak subsurface step), intra-range bedrock cliff/talus "
            "breaks >18 deg (zeroed by piedmont habitat window), V-valley canyon mouths (suppressed "
            "by +-400 m contour-strike steering), alluvial fan terrace risers, and volcanic flow toes."
        ),
        holdout_dti=dict(
            evidence_class="HOLDOUT-DTI",
            evaluator_version=ev.VERSION,
            screen_final_surface=gates_full["detail"]["final_holdout"],
            incumbent_h31x_same_run=gates_full["detail"]["incumbent_holdout"],
            screen_paired_vs_h31x=gates_full["detail"]["screen_paired_vs_junc_inc"],
            screen_paired_vs_ctrl=gates_full["detail"]["screen_paired_vs_ctrl"],
            screen_paired_vs_slope=gates_full["detail"]["screen_paired_vs_slope"],
            confirmation_random_component_split=dict(
                partition=exp3["confirmation"]["partition"],
                scores=gates_full["detail"]["confirmation_scores"],
                paired_vs_h31x=gates_full["detail"]["confirmation_paired_vs_junc_inc"],
                paired_vs_ctrl=gates_full["detail"]["confirmation_paired_vs_ctrl"],
            ),
            fixed_reference_caveat=json.loads((EVID / "exp1_screen.json").read_text())["fixed_reference_caveat"],
        ),
        sgmc_proxy=dict(
            evidence_class="COMPUTED off-catalogue USGS-SGMC proxy (not hidden competition truth)",
            candidate=sg["candidate"],
            H33=sg["H33"],
            G27_DRCG=sg["G27_DRCG"],
            H31X=sg["H31X"],
            regimes={k: v for k, v in sg.items() if "deg" in k},
            quadrants=exp3["sgmc_quadrants"],
        ),
        diagnostics=exp2["diagnostics"],
        leaderboard_estimate=None,
        projection=exp3["cross_family_projection_diagnostic"],
        correlation_overlap_vs_registry=dict(
            scope=(
                "26+ hash-verified peer rasters (9 historical focus rasters + 9 newly scored "
                "Oct 25-26 focus rasters + all local GEMSDOE31 discrete lanes) checked on BOTH "
                "pre-placement top-K surface support and final emitted dots, plus literal "
                "695-raster shared registry preflight & spacing-5 lattice witness."
            ),
            n_peers_checked=u["n_peers_checked"],
            n_discrete_peers=u["n_discrete_peers"],
            n_external_focus_discrete_peers=u["n_external_focus_discrete_peers"],
            external_focus_max_topk_overlap_3px=u["external_focus_max_topk_overlap"],
            external_focus_worst_topk_peer=u["external_focus_worst_topk_peer"],
            external_focus_max_final_overlap_3px=u["external_focus_max_final_overlap"],
            external_focus_worst_final_peer=u["external_focus_worst_final_peer"],
            discrete_max_topk_overlap_3px=u["discrete_max_topk_overlap"],
            worst_topk_peer=u["worst_topk_peer"],
            discrete_max_final_overlap_3px=u["discrete_max_final_overlap"],
            worst_final_peer=u["worst_final_peer"],
            max_abs_spearman_surface=u["max_abs_surface_spearman"],
            max_abs_spearman_dots=u["max_abs_dots_spearman"],
            unique_vs_protocol_surface_rho_and_final_dots=bool(gates_full["G5_protocol_surface_rho_and_final_dots"]),
            unique_vs_external_focus_two_stage=bool(gates_full["G5_external_focus_two_stage"]),
            unique_vs_discrete_peers_two_stage=bool(gates_full["G5_discrete_two_stage"]),
            literal_broad_registry=exp2["literal_witness"],
            literal_registry_preflight=exp2["literal_registry_preflight"],
        ),
        raster_sha256=sha256_file(out_tif),
        raster_sha256_nan=sha256_file(nan_tif),
        zip_sha256=receipt["zip_sha256"],
        nan_zip_sha256=sha256_file(nan_zip),
        support_sha256=support_sha,
        validator=dict(
            zeros=dict(
                file=out_tif.name,
                convention="all-finite",
                ok=vz["ok_to_upload_format_only"],
                no_nan_inside_footprint=bool(vz["checks"]["footprint_all_finite"]["pass_"]),
                all_array_finite_in_0_1=bool(vz["checks"]["allfinite_values_in_0_1"]["pass_"]),
                values_in_0_1=bool(vz["checks"]["footprint_values_in_0_1"]["pass_"]),
                crs_shape_transform_match=bool(
                    vz["checks"]["crs_matches_template"]["pass_"]
                    and vz["checks"]["shape_matches_template"]["pass_"]
                    and vz["checks"]["transform_matches_template"]["pass_"]
                ),
                hard_failures=vz["hard_failures"],
                grid=vz["grid"],
            ),
            nan=dict(
                file=nan_tif.name,
                convention="nan-outside",
                ok=vn["ok_to_upload_format_only"],
                no_nan_inside_footprint=bool(vn["checks"]["footprint_all_finite"]["pass_"]),
                values_in_0_1=bool(vn["checks"]["footprint_values_in_0_1"]["pass_"]),
                crs_shape_transform_match=bool(
                    vn["checks"]["crs_matches_template"]["pass_"]
                    and vn["checks"]["shape_matches_template"]["pass_"]
                    and vn["checks"]["transform_matches_template"]["pass_"]
                ),
                hard_failures=vn["hard_failures"],
                grid=vn["grid"],
            ),
            vendor_writer_receipt=Path(receipt["file"]).with_suffix(".json").name,
            organizer_acceptance_verified=False,
        ),
        submission_name=name,
        note=note,
        note_chars=len(note),
        gates=gates_full,
        scientific_and_discrete_gates_all_pass=scientific_discrete_pass,
        verdict="promote" if literal_and_all_pass else "negative",
        ok_to_download_for_research=True,
        ok_to_submit=False,
        slot_approved=False,
        submission_slots_used=0,
        instruction=(
            "DO NOT SUBMIT WITHOUT SELECTOR OVERRIDE OF LITERAL LATTICE STOP: "
            + ("H31-AA passes all scientific & two-stage discrete-peer gates (G1-G4 + G5_discrete_two_stage), "
               if scientific_discrete_pass else
               "At least one scientific or discrete-peer gate did not clear; ")
            + "literal 695-raster broad-registry gate G5_literal_broad_registry remains blocked by "
              "registered whole-footprint continuous surface (17GEMSDOE_E-proba-multiscale, 100%) and "
              "synthetic spacing-5 lattice (r13-lattice-s5, >=82.34% mathematical floor at 37,654 dots). "
              "Packaged all-finite (-zeros.tif / .zip) is validated in [0, 1] for research inspection."
        ),
        files=dict(
            zeros=f"docs/downloads/{out_tif.name}",
            nan=f"docs/downloads/{nan_tif.name}",
            zip=f"docs/downloads/{out_tif.with_suffix('.zip').name}",
            nan_zip=f"docs/downloads/{nan_zip.name}",
        ),
        preregistration=pin,
        evidence=dict(
            lines="evidence/h31aa/lines.json",
            canary="evidence/h31aa/canary.json",
            preplacement_uniqueness="evidence/h31aa/preplacement_uniqueness.json",
            exp1="evidence/h31aa/exp1_screen.json",
            exp2="evidence/h31aa/exp2.json",
            exp3="evidence/h31aa/exp3.json",
        ),
    )
    for dest in (
        EVID / "run_card.json",
        ROOT / "docs/downloads/h31aa-run-card.json",
        ROOT / "registry/h31aa_current_run.json",
    ):
        dest.write_text(json.dumps(card, indent=2, default=float) + "\n")
    log("PACKAGE", name, "verdict=", card["verdict"],
        "sci_discrete_pass=", scientific_discrete_pass,
        "gates=", {k: v for k, v in gates_full.items() if k.startswith("G")})
    log("sha256 zeros:", card["raster_sha256"])
    return card


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("stage", choices=["lines", "canary", "exp1", "exp2", "exp3", "package", "all"])
    args = ap.parse_args()
    stages = ["lines", "canary", "exp1", "exp2", "exp3", "package"] if args.stage == "all" else [args.stage]
    t0 = time.time()
    for s in stages:
        log("=== STAGE", s, "===", round(time.time() - t0, 1), "s elapsed")
        {
            "lines": build_lines,
            "canary": run_canary,
            "exp1": run_exp1,
            "exp2": run_exp2,
            "exp3": run_exp3,
            "package": run_package,
        }[s]()
    log("DONE in", round(time.time() - t0, 1), "s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
