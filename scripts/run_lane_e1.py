#!/usr/bin/env python3
"""E1 — label-free LiDAR surface screen with leakage canary (lane experiment 1 of 3).

Hypothesis (fixed before the run, see knowledge/2026-10-25_lane_hypotheses.md): the LiDAR *uphill-facing
(antislope) scarp* component, asking for a coherent scarp that faces against the regional slope, selects
faults more selectively than generic scarp steepness, because the common non-fault 1 m-DEM steps (terrace
risers, shoreline benches, gully headcuts, road cuts) face downslope.

Every surface is built from the LiDAR bands only; no catalogue pixel enters surface construction. The
catalogue is used afterwards in exactly one place: dots within 2 pixels of a *visible* catalogue fault are
removed (the live-tested flank rule, H33-2-B2), and dots on visible faults are masked.

Writes evidence/lane_e1.json.
"""

from __future__ import annotations

import time

import numpy as np
from lane_common import (ROOT, auc, discovery_instrument, emit, holdout_instruments, lane, load_base, load_dots,
                         load_lidar, pct_rank, write_json)
from scipy.ndimage import distance_transform_edt, gaussian_filter

BUDGETS = (10_000, 20_000, 30_000, 38_000, 50_000)
FLANK_PX = 2.0


def build_surfaces(lid: dict, valid: np.ndarray) -> dict[str, np.ndarray]:
    f = {k: v.astype(np.float32) / 255.0 for k, v in lid.items()}
    r = {k: pct_rank(f[k], valid) for k in ("ex_max", "step_max", "upface_max", "downface_max", "coh100",
                                            "lapneg_max", "lappos_max", "cross_max")}
    surfaces = {
        "S0_generic_scarp(ex_max)": r["ex_max"],
        "S1_antislope(upface)": r["upface_max"],
        "S2_antislope_dominant(up-down)": pct_rank(np.maximum(f["upface_max"] - f["downface_max"], 0.0), valid),
        "S3_antislope_x_coherence": r["upface_max"] * r["coh100"],
        "S4_paired_faces(min(up,down))": np.minimum(r["upface_max"], r["downface_max"]),
        "S5_step_x_coherence": r["step_max"] * r["coh100"],
    }
    return {k: gaussian_filter(v, 0.8) * valid for k, v in surfaces.items()}


def main() -> None:
    t0 = time.time()
    base = load_base()
    lid = load_lidar()
    valid = base["footprint"] & (lid["valid"] > 0)
    print(f"lidar-valid footprint fraction {valid.sum() / base['footprint'].sum():.4f}")
    surfaces = build_surfaces(lid, valid)
    insts = [discovery_instrument(base), *holdout_instruments(base)]
    incumbent = load_dots(ROOT / "docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif")
    inc_name = "D28 incumbent (0.2708 USER-REPORTED, 40,199 dots)"

    # stats[instrument][candidate] -> sufficient statistics
    stats: dict[str, dict[str, dict]] = {i.name: {} for i in insts}
    for inst in insts:
        stats[inst.name][inc_name] = lane.sufficient_stats(incumbent, inst)
    results: dict = {"evaluator": lane.EVAL_VERSION, "budgets": BUDGETS, "flank_px": FLANK_PX, "canary": {}}
    for sname, surf in surfaces.items():
        results["canary"][sname] = {"auc_off_catalogue_sgmc": auc(surf, base["far_field"], valid),
                                    "auc_catalogue": auc(surf, base["catalogue"], valid)}
        c = results["canary"][sname]
        print(f"{sname:36s} canary AUC sgmc {c['auc_off_catalogue_sgmc']:.3f}  cat {c['auc_catalogue']:.3f}", flush=True)
        for inst in insts:
            d_vis = distance_transform_edt(~inst.visible)
            order = emit(surf, valid & (d_vis > FLANK_PX) & ~inst.visible, max(BUDGETS), return_order=True)
            for b in BUDGETS:
                if len(order) >= b:
                    stats[inst.name][f"{sname}@{b}"] = lane.sufficient_stats(lane.prefix_mask(order, b, surf.shape), inst)
        print(f"   emitted ({time.time() - t0:.0f}s)", flush=True)

    names = list(stats[insts[0].name])
    gap_names = [i.name for i in insts if i.name.startswith("catalogue-gap")]
    table = {}
    for group, members in (("off-catalogue-sgmc", ["off-catalogue-sgmc"]), ("catalogue-gap (3 seeds pooled)", gap_names)):
        pooled = {n: [stats[m][n] for m in members if n in stats[m]] for n in names}
        pooled = {n: v for n, v in pooled.items() if len(v) == len(members)}
        boot = lane.tile_bootstrap(pooled, n_boot=400)
        table[group] = {n: {"HOLDOUT_DTI": boot[n]["point"], "ci95_tile_bootstrap": boot[n]["ci95"],
                            "credit_per_dot": sum(s["tp"] for s in pooled[n]) / max(sum(s["dots"] for s in pooled[n]), 1),
                            "truth_pixels": int(sum(s["g"] for s in pooled[n]))} for n in pooled}
        print(f"\n== {group}  (truth px {int(sum(s['g'] for s in pooled[names[0]])):,})")
        for n in pooled:
            r = table[group][n]
            print(f"  {n:52s} DTI {r['HOLDOUT_DTI']:.4f} [{r['ci95_tile_bootstrap'][0]:.4f},{r['ci95_tile_bootstrap'][1]:.4f}] c/dot {r['credit_per_dot']:.3f}")
    results["instruments"] = table
    write_json(ROOT / "evidence/lane_e1.json", results)
    print(f"done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
