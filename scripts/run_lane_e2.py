#!/usr/bin/env python3
"""E2 — mimic control and coverage-gap test (lane experiment 2 of 3).

Two questions, both fixed before the run (knowledge/2026-10-25_lane_hypotheses.md):

(a) MIMIC CONTROL. Does removing pixels within R metres of a US Census TIGER road/vehicular trail raise the
    holdout DTI of the LiDAR antislope surface? Road cuts and embankments are the named anthropogenic mimic of
    a 1 m-DEM scarp. Neither proxy truth knows about roads, so a gain is evidence the mask removes false
    positives and not an artefact of the truth definition.
(b) COVERAGE GAP. 24.6 % of the footprint has no 3DEP LiDAR in the mirror (valid==0). Do label-free geophysical
    basement-step surfaces (isostatic-gravity horizontal gradient, depth-to-base gradient) earn per-dot credit in
    that gap at or above the incumbent's per-dot credit there?

Writes evidence/lane_e2.json.
"""

from __future__ import annotations

import time

import numpy as np
import rasterio
from lane_common import (DATA, ROOT, auc, discovery_instrument, emit, holdout_instruments, lane, load_base,
                         load_dots, load_lidar, pct_rank, read, write_json)
from run_lane_e1 import build_surfaces
from scipy.ndimage import distance_transform_edt, gaussian_filter

NODATA_BELOW = -1e30
ROAD_RADII_M = (0, 100, 200, 300)
BUDGET = 38_000
FLANK_PX = 2.0


def feature(i: int, footprint: np.ndarray) -> np.ndarray:
    with rasterio.open(DATA / "training_features.tif") as src:
        a = src.read(i).astype(np.float32)
    a[~np.isfinite(a) | (a < NODATA_BELOW)] = np.nan
    a[~footprint] = np.nan
    return a


def grad_mag(a: np.ndarray, sigma: float = 1.0) -> np.ndarray:
    fill = np.where(np.isfinite(a), a, np.nanmedian(a))
    sm = gaussian_filter(fill, sigma)
    gy, gx = np.gradient(sm, 100.0)
    return np.hypot(gx, gy)


def main() -> None:
    t0 = time.time()
    base = load_base()
    lid = load_lidar()
    footprint = base["footprint"]
    valid = footprint & (lid["valid"] > 0)
    gap = footprint & ~valid
    roads_m = read(DATA / "external/tiger_road_distance_m.tif")
    surfaces = build_surfaces(lid, valid)
    insts = [discovery_instrument(base), *holdout_instruments(base)]
    incumbent = load_dots(ROOT / "docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif")
    out: dict = {"evaluator": lane.EVAL_VERSION, "budget": BUDGET, "flank_px": FLANK_PX}

    # ---------------------------------------------------------------- (a) mimic control
    print("== (a) road-mimic control")
    stats: dict[str, dict[str, dict]] = {i.name: {} for i in insts}
    for sname in ("S0_generic_scarp(ex_max)", "S1_antislope(upface)", "S2_antislope_dominant(up-down)"):
        surf = surfaces[sname]
        for inst in insts:
            d_vis = distance_transform_edt(~inst.visible)
            for radius in ROAD_RADII_M:
                cand = valid & (d_vis > FLANK_PX) & ~inst.visible & (roads_m > radius)
                order = emit(surf, cand, BUDGET, return_order=True)
                stats[inst.name][f"{sname} road>{radius}m"] = lane.sufficient_stats(lane.prefix_mask(order, min(BUDGET, len(order)), surf.shape), inst)
    names = list(stats[insts[0].name])
    gap_names = [i.name for i in insts if i.name.startswith("catalogue-gap")]
    out["road_control"] = {}
    for group, members in (("off-catalogue-sgmc", ["off-catalogue-sgmc"]), ("catalogue-gap", gap_names)):
        pooled = {n: [stats[m][n] for m in members] for n in names}
        boot = lane.tile_bootstrap(pooled, n_boot=400)
        out["road_control"][group] = {n: {"DTI": boot[n]["point"], "ci95": boot[n]["ci95"],
                                           "credit_per_dot": sum(s["tp"] for s in pooled[n]) / max(sum(s["dots"] for s in pooled[n]), 1)}
                                      for n in names}
        print(f" {group}")
        for n in names:
            base_name = n.split(" road>")[0] + " road>0m"
            paired = lane.paired_delta(boot[n]["draws"], boot[base_name]["draws"]) if n != base_name else None
            r = out["road_control"][group][n]
            extra = f"  paired vs road>0: {paired['mean']:+.4f} [{paired['ci95'][0]:+.4f},{paired['ci95'][1]:+.4f}] P(better)={paired['p_better']:.2f}" if paired else ""
            print(f"  {n:46s} DTI {r['DTI']:.4f} c/dot {r['credit_per_dot']:.3f}{extra}")
            if paired:
                r["paired_vs_no_mask"] = {k: v for k, v in paired.items()}

    # ---------------------------------------------------------------- (b) coverage gap
    print("\n== (b) coverage gap: no-LiDAR zone")
    sources = {"iso_grav_anom_hg": feature(18, footprint), "depth_to_base_surf": feature(15, footprint),
               "cond_surf": feature(17, footprint), "tmi_hg": feature(3, footprint)}
    rk = {}
    gap_surfaces = {}
    gm = gap & np.isfinite(sources["iso_grav_anom_hg"])
    rk["grav_hg"] = pct_rank(sources["iso_grav_anom_hg"], gm)
    rk["base_grad"] = pct_rank(grad_mag(sources["depth_to_base_surf"]), gm)
    rk["cond_grad"] = pct_rank(grad_mag(sources["cond_surf"]), gm)
    rk["mag_hg"] = pct_rank(sources["tmi_hg"], gm)
    gap_surfaces["G1_gravity_horizontal_gradient"] = rk["grav_hg"]
    gap_surfaces["G2_basement_depth_gradient"] = rk["base_grad"]
    gap_surfaces["G3_gravity_x_basement"] = np.sqrt(rk["grav_hg"] * rk["base_grad"])
    gap_surfaces["G4_conductance_gradient"] = rk["cond_grad"]
    gap_surfaces["G5_magnetic_horizontal_gradient"] = rk["mag_hg"]
    print(f" gap zone: {int(gm.sum()):,} px ({gm.sum() / footprint.sum():.3f} of footprint); "
          f"SGMC far-field px in gap {int((base['far_field'] & gm).sum()):,}; incumbent dots in gap {int((incumbent & gm).sum()):,}")
    canary = {}
    gap_budgets = (3_000, 6_000, 10_000)
    zone_insts = {i.name: lane.restrict_truth(i, gm) for i in insts}
    gstats: dict[str, dict[str, dict]] = {i.name: {} for i in insts}
    for inst in insts:
        gstats[inst.name]["incumbent dots inside gap"] = lane.sufficient_stats(incumbent & gm, zone_insts[inst.name])
    for gname, surf in gap_surfaces.items():
        surf = gaussian_filter(surf, 0.8) * gm
        canary[gname] = {"auc_off_catalogue_sgmc": auc(surf, base["far_field"], gm),
                         "auc_catalogue": auc(surf, base["catalogue"], gm)}
        print(f" {gname:34s} canary AUC sgmc {canary[gname]['auc_off_catalogue_sgmc']:.3f} cat {canary[gname]['auc_catalogue']:.3f}")
        for inst in insts:
            d_vis = distance_transform_edt(~inst.visible)
            order = emit(surf, gm & (d_vis > FLANK_PX) & ~inst.visible, max(gap_budgets), return_order=True)
            for b in gap_budgets:
                if len(order) >= b:
                    gstats[inst.name][f"{gname}@{b}"] = lane.sufficient_stats(lane.prefix_mask(order, b, surf.shape), zone_insts[inst.name])
    out["gap_canary"] = canary
    gnames = list(gstats[insts[0].name])
    out["gap_zone"] = {}
    for group, members in (("off-catalogue-sgmc", ["off-catalogue-sgmc"]), ("catalogue-gap", gap_names)):
        pooled = {n: [gstats[m][n] for m in members if n in gstats[m]] for n in gnames}
        pooled = {n: v for n, v in pooled.items() if len(v) == len(members)}
        out["gap_zone"][group] = {n: {"dots": int(sum(s["dots"] for s in v)), "credit_per_dot": sum(s["tp"] for s in v) / max(sum(s["dots"] for s in v), 1),
                                      "zone_DTI": lane.pooled_dti(v), "truth_px_in_gap": int(sum(s["g"] for s in v))}
                                  for n, v in pooled.items()}
        print(f" {group}")
        for n, r in out["gap_zone"][group].items():
            print(f"  {n:46s} dots {r['dots']:>6,} credit/dot {r['credit_per_dot']:.3f} zoneDTI {r['zone_DTI']:.4f} (truth px {r['truth_px_in_gap']:,})")
    write_json(ROOT / "evidence/lane_e2.json", out)
    print(f"done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
