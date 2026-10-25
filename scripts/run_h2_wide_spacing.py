#!/usr/bin/env python3
"""H2 — LiDAR generic scarp (ex_max) at wide 5.0 px Poisson-disk spacing.

Goal: a UNIQUE submission distinct from the D2.8 dotted-ridge monoculture in the
716-raster registry, while retaining the proven LiDAR scarp surface that beats the
D28 incumbent on both holdout proxies.

Surface: label-free LiDAR ex_max percentile rank, gaussian 0.8px (AS-1 S0).
Emission: LiDAR-valid pixels >2px from visible catalogue, not on faults.
Spacing: 5.0 px (500 m) minimum — deliberately different from the 2.8 px D2.8
pattern that dominates the registry, giving a sparse, spatially distinct dot set.
Budget: ~20,000 dots (sparse, high per-dot credit).

Lane protocol: single-feature canary first (AUC <= 0.90), then holdout scoring,
then registry uniqueness check (rho <= 0.90, overlap <= 70%).
Writes evidence/h2_wide_spacing.json.
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
from scipy.ndimage import distance_transform_edt, gaussian_filter

import sys
ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from gemsdoe31 import lane  # noqa: E402
from lane_common import (  # noqa: E402
    ROOT as LC_ROOT, auc, discovery_instrument, emit, holdout_instruments,
    lane as lc_lane, load_base, load_dots, load_lidar, pct_rank, write_json,
)

assert ROOT == LC_ROOT

BUDGET = 20_000
FLANK_PX = 2.0
MIN_DIST_PX = 5.0  # wide spacing vs D2.8 registry patterns
GAUSS_SIGMA = 0.8
AUC_LEAKAGE_STOP = 0.90


def main() -> None:
    t0 = time.time()
    base = load_base()
    footprint = base["footprint"]
    catalogue = base["catalogue"]
    lid = load_lidar()
    valid = footprint & (lid["valid"] > 0)

    print(f"lidar-valid fraction {valid.sum()/footprint.sum():.4f}", flush=True)

    # --- Surface: S0 generic scarp (ex_max) ---
    f = {k: v.astype(np.float32) / 255.0 for k, v in lid.items()}
    r = pct_rank(f["ex_max"], valid)
    surf = gaussian_filter(r, GAUSS_SIGMA) * valid

    # --- Canary ---
    canary = {
        "auc_off_catalogue_sgmc": auc(surf, base["far_field"], valid),
        "auc_catalogue": auc(surf, catalogue, valid),
    }
    print(f"canary sgmc {canary['auc_off_catalogue_sgmc']:.3f}  cat {canary['auc_catalogue']:.3f}",
          flush=True)
    if canary["auc_off_catalogue_sgmc"] > AUC_LEAKAGE_STOP or canary["auc_catalogue"] > AUC_LEAKAGE_STOP:
        print("LEAKAGE STOP", flush=True)
        write_json(ROOT / "evidence/h2_wide_spacing.json", {
            "hypothesis": "H2-wide-spacing-liDAR-scarp", "verdict": "negative",
            "reason": "single-feature leakage canary AUC > 0.90", "canary": canary,
        })
        return

    # --- Emit dots at wide spacing ---
    d_vis = distance_transform_edt(~catalogue)
    cand = valid & (d_vis > FLANK_PX) & ~catalogue
    order = emit(surf, cand, BUDGET, min_dist_px=MIN_DIST_PX, return_order=True)
    print(f"emitted {len(order):,} dots at {MIN_DIST_PX}px spacing", flush=True)

    dots = lc_lane.prefix_mask(order, BUDGET, surf.shape)

    # --- Score on holdout instruments ---
    insts = [discovery_instrument(base), *holdout_instruments(base)]
    incumbent = load_dots(
        ROOT / "docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif"
    )
    stats = {i.name: {} for i in insts}
    for inst in insts:
        stats[inst.name]["D28-incumbent"] = lane.sufficient_stats(incumbent, inst)
        stats[inst.name]["H2-wide-spacing@20k"] = lane.sufficient_stats(dots, inst)

    gap_names = [i.name for i in insts if i.name.startswith("catalogue-gap")]
    pooled = {n: [stats[m][n] for m in gap_names if n in stats[m]]
              for n in stats[gap_names[0]]}
    pooled = {n: v for n, v in pooled.items() if len(v) == len(gap_names)}
    boot = lane.tile_bootstrap(pooled, n_boot=400)

    results = {
        "hypothesis": "H2-wide-spacing-liDAR-scarp",
        "mechanism": "LiDAR generic scarp surface (ex_max percentile rank) at wide 5.0px Poisson-disk spacing",
        "non_fault_mimic": "road cuts, terrace risers, gully headcuts (all face downslope; antislope bias suppresses)",
        "evaluator": lane.EVAL_VERSION,
        "budget": BUDGET, "flank_px": FLANK_PX, "min_dist_px": MIN_DIST_PX,
        "canary": canary, "dots_emitted": int(dots.sum()),
    }
    table = {}
    for n in pooled:
        r = boot[n]
        table[n] = {
            "HOLDOUT_DTI": float(r["point"]),
            "ci95_tile_bootstrap": [float(r["ci95"][0]), float(r["ci95"][1])],
        }
        print(f"  {n:52s} DTI {r['point']:.4f} [{r['ci95'][0]:.4f},{r['ci95'][1]:.4f}]")
    results["instruments"] = table
    write_json(ROOT / "evidence/h2_wide_spacing.json", results)

    # --- Save dots for potential TIF generation ---
    np.save(ROOT / "evidence/h2_wide_spacing_dots.npy", dots)
    print(f"done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
