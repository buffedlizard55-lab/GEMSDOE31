#!/usr/bin/env python3
"""H3 — LiDAR generic scarp (ex_max) at 2.8px spacing: full holdout + uniqueness + TIF.

Goal: produce a UNIQUE, format-validated GeoTIFF submission distinct from every
raster in the 716-raster shared registry, using the proven LiDAR generic scarp
surface (S0: ex_max percentile rank, gaussian 0.8px) that beats the D28 incumbent
on both holdout proxies.

Uniqueness strategy: the dot pattern is driven by LiDAR scarp strength (not a
regular lattice), so it is spatially distinct from the D2.8 dotted-ridge rasters
that dominate the registry. We verify with the full uniqueness gate
(rho <= 0.90, overlap <= 70% vs ALL 716 registry rasters).

Gate sequence:
  1. Single-feature leakage canary (AUC <= 0.90) — hard stop
  2. Holdout DTI on catalogue-gap (3 seeds pooled) and off-catalogue-SGMC
  3. Registry uniqueness vs all 716 rasters
  4. If all pass: write -nan.tif, -allfinite.tif, -nan.zip, format-check.json
     via scripts/submission_writer.py (strict validator: EPSG:32611, 3730x3292,
     float32, [0,1] inside footprint, NaN outside)

Writes evidence/h3_unique_submission.json and docs/downloads/<name>*.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
from scipy.ndimage import distance_transform_edt, gaussian_filter

import sys
ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from gemsdoe31 import lane, metric  # noqa: E402
from lane_common import (  # noqa: E402
    ROOT as LC_ROOT, auc, discovery_instrument,
    emit, holdout_instruments, lane as lc_lane, load_base, load_dots, load_lidar,
    pct_rank, write_json,
)
from submission_writer import emit_and_validate_submission  # noqa: E402
from gemsdoe31.gate import uniqueness_report as gate_uniqueness  # noqa: E402

assert ROOT == LC_ROOT

ALPHA, BETA, EPSILON = metric.ALPHA, metric.BETA, metric.EPSILON

BUDGET = 50_000
FLANK_PX = 2.0
MIN_DIST_PX = 2.8
GAUSS_SIGMA = 0.8
AUC_LEAKAGE_STOP = 0.90

SUBMISSION_NAME = "gemsdoe31-h3-lidar-scarp-unique-50k-20261025"
SUBMISSION_NOTE = ("LiDAR generic scarp ex_max 2.8px Poisson dots; HOLDOUT-DTI "
                   "catalogue-gap + offcat-SGMC; unique vs 716-raster registry")[:140]


def dti_from_stats(tp: float, fp: float, g: float) -> float:
    fn = g - tp
    return tp / (tp + ALPHA * fp + BETA * fn + EPSILON)


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
        print("LEAKAGE STOP: aborting.", flush=True)
        write_json(ROOT / "evidence/h3_unique_submission.json", {
            "hypothesis": "H3-lidar-scarp-unique", "verdict": "negative",
            "reason": "single-feature leakage canary AUC > 0.90", "canary": canary,
        })
        return

    # --- Emit dots ---
    d_vis = distance_transform_edt(~catalogue)
    cand = valid & (d_vis > FLANK_PX) & ~catalogue
    order = emit(surf, cand, BUDGET, min_dist_px=MIN_DIST_PX, return_order=True)
    print(f"emitted {len(order):,} dots at {MIN_DIST_PX}px spacing", flush=True)
    dots = lc_lane.prefix_mask(order, BUDGET, surf.shape)
    print(f"final dots: {int(dots.sum()):,}", flush=True)

    # --- Holdout scoring ---
    insts = [discovery_instrument(base), *holdout_instruments(base)]
    incumbent = load_dots(
        ROOT / "docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif"
    )
    stats = {i.name: {} for i in insts}
    for inst in insts:
        stats[inst.name]["D28-incumbent"] = lane.sufficient_stats(incumbent, inst)
        stats[inst.name]["H3-lidar-scarp-unique"] = lane.sufficient_stats(dots, inst)

    gap_names = [i.name for i in insts if i.name.startswith("catalogue-gap")]
    pooled_gap = {n: [stats[m][n] for m in gap_names if n in stats[m]]
                  for n in stats[gap_names[0]]}
    pooled_gap = {n: v for n, v in pooled_gap.items() if len(v) == len(gap_names)}
    boot_gap = lane.tile_bootstrap(pooled_gap, n_boot=400)

    sgmc_inst = discovery_instrument(base)
    sgmc_stats = lane.sufficient_stats(dots, sgmc_inst)
    dti_sgmc = dti_from_stats(sgmc_stats["tp"], sgmc_stats["fp"], sgmc_stats["g"])

    results = {
        "hypothesis": "H3-lidar-scarp-unique",
        "mechanism": "LiDAR generic scarp ex_max percentile rank at 2.8px Poisson-disk spacing",
        "non_fault_mimic": "road cuts, terrace risers, gully headcuts (downslope-facing; scarp ranking suppresses)",
        "evaluator": lane.EVAL_VERSION,
        "budget": BUDGET, "flank_px": FLANK_PX, "min_dist_px": MIN_DIST_PX,
        "canary": canary, "dots_emitted": int(dots.sum()),
        "holdout_catalogue_gap": {},
        "holdout_off_catalogue_sgmc": {
            "HOLDOUT_DTI": float(dti_sgmc),
            "truth_pixels": int(sgmc_stats["g"]),
            "dots": int(sgmc_stats["dots"]),
        },
    }
    for n in boot_gap:
        r = boot_gap[n]
        results["holdout_catalogue_gap"][n] = {
            "HOLDOUT_DTI": float(r["point"]),
            "ci95_tile_bootstrap": [float(r["ci95"][0]), float(r["ci95"][1])],
        }
        print(f"  catalogue-gap {n:52s} DTI {r['point']:.4f} [{r['ci95'][0]:.4f},{r['ci95'][1]:.4f}]")

    print(f"  off-catalogue-SGMC DTI {dti_sgmc:.4f} (truth px {sgmc_stats['g']:,}, dots {sgmc_stats['dots']:,})")

    # --- Registry uniqueness check ---
    registry_path = ROOT / "registry/raster_registry.json"
    cache_dir = ROOT / "data/registry_rasters"
    reg = json.loads(registry_path.read_text())["rasters"]

    uniq = gate_uniqueness(dots, reg, cache_dir, footprint)
    results["uniqueness"] = {
        "registry_rasters_compared": uniq["registry_rasters_compared"],
        "registry_rasters_missing": uniq["registry_rasters_missing"],
        "max_spearman_500m": uniq["max_spearman_500m"],
        "max_overlap_3px_non_vacuous": uniq["max_overlap_3px_non_vacuous"],
        "max_adjusted_overlap": uniq["max_adjusted_overlap"],
        "duplicates_by_overlap": uniq["duplicates_by_overlap"],
        "duplicates_by_rank_correlation": uniq["duplicates_by_rank_correlation"],
        "identical_dot_set_in_registry": uniq["identical_dot_set_in_registry"],
    }
    print("\n=== UNIQUENESS ===")
    print(f"compared: {uniq['registry_rasters_compared']}, missing: {uniq['registry_rasters_missing']}")
    print(f"max Spearman: {uniq['max_spearman_500m']} (limit 0.90)")
    print(f"max 3px overlap: {uniq['max_overlap_3px_non_vacuous']} (limit 0.70)")
    print(f"duplicates by overlap: {len(uniq['duplicates_by_overlap'])}")
    print(f"duplicates by correlation: {len(uniq['duplicates_by_rank_correlation'])}")
    print(f"identical dot set: {uniq['identical_dot_set_in_registry']}")

    unique_ok = (
        uniq["registry_rasters_compared"] > 0
        and uniq["registry_rasters_missing"] == 0
        and (uniq["max_spearman_500m"] is None or uniq["max_spearman_500m"] <= 0.90)
        and (uniq["max_overlap_3px_non_vacuous"] is None or uniq["max_overlap_3px_non_vacuous"] <= 0.70)
        and not uniq["identical_dot_set_in_registry"]
        and len(uniq["duplicates_by_overlap"]) == 0
        and len(uniq["duplicates_by_rank_correlation"]) == 0
    )
    results["uniqueness_ok"] = unique_ok

    # --- Verdict ---
    gap_best = max((v["HOLDOUT_DTI"] for v in results["holdout_catalogue_gap"].values()), default=0)
    d28_gap = 0.0435  # D28 incumbent on catalogue-gap
    beats_d28 = gap_best > d28_gap

    verdict = "negative"
    if (canary["auc_off_catalogue_sgmc"] <= AUC_LEAKAGE_STOP
            and beats_d28 and unique_ok):
        verdict = "promote"
    results["verdict"] = verdict
    results["beats_d28_catalogue_gap"] = beats_d28
    results["submission_name"] = SUBMISSION_NAME
    results["submission_note"] = SUBMISSION_NOTE

    print(f"\n=== VERDICT: {verdict} ===")
    print(f"beats D28 on catalogue-gap: {beats_d28} ({gap_best:.4f} vs {d28_gap})")
    print(f"unique vs registry: {unique_ok}")

    if verdict == "promote":
        # --- Generate TIF ---
        print("\n--- Generating validated submission TIF ---")
        receipt = emit_and_validate_submission(
            dots,
            template_path=ROOT / "data/sample_submission.tif",
            labels_path=ROOT / "data/labels.tif",
            outdir=ROOT / "docs/downloads",
            name=SUBMISSION_NAME,
            note=SUBMISSION_NOTE,
        )
        results["submission_receipt"] = {
            "nan_sha256": receipt["validation"]["nan"]["sha256"],
            "allfinite_sha256": receipt["validation"]["allfinite"]["sha256"],
            "format_ok_nan": receipt["validation"]["nan"]["ok_to_upload_format_only"],
            "format_ok_allfinite": receipt["validation"]["allfinite"]["ok_to_upload_format_only"],
            "dots": receipt["dots"],
            "dots_on_catalogue": receipt["dots_on_catalogue"],
        }
        print(f"TIF generated: {SUBMISSION_NAME}")
        print(f"  NaN SHA256: {receipt['validation']['nan']['sha256']}")
        print(f"  Format OK (nan): {receipt['validation']['nan']['ok_to_upload_format_only']}")
        print(f"  Format OK (allfinite): {receipt['validation']['allfinite']['ok_to_upload_format_only']}")

    write_json(ROOT / "evidence/h3_unique_submission.json", results)
    print(f"\ndone in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
