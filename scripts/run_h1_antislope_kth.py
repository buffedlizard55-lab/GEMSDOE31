#!/usr/bin/env python3
"""H1 — Antislope LiDAR scarp AND radiometric K–Th alteration edge conjunction.

Hypothesis (preregistered in knowledge/2026-10-25_unique_submission_hypotheses.md):
a fault needs only one strong domain (antislope scarp OR K–Th edge) plus moderate
support in the other. Targets blind/hydrothermal faults missing from the USGS/
INGENIOUS catalogue because they lack mappable geologic trace but show subtle
topographic displacement and alteration halos.

Lane protocol: surface is label-free (LiDAR + radiometric only). Catalogue enters
ONLY for emission masking (>2 px from visible faults, not on faults). Single-feature
leakage canary (AUC <= 0.90) gates before holdout scoring.

Writes evidence/h1_antislope_kth.json.
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt, gaussian_filter
from scipy.stats import rankdata

import sys
ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from gemsdoe31 import lane  # noqa: E402
from lane_common import (  # noqa: E402
    DATA, ROOT as LC_ROOT, auc, discovery_instrument, emit, holdout_instruments,
    lane as lc_lane, load_base, load_dots, load_lidar, pct_rank, write_json,
)

assert ROOT == LC_ROOT

BUDGET = 37_654
FLANK_PX = 2.0
MIN_DIST_PX = 2.8
GAUSS_SIGMA = 0.8
AUC_LEAKAGE_STOP = 0.90


def read_training_band(band_index: int, footprint: np.ndarray) -> np.ndarray:
    with rasterio.open(DATA / "training_features.tif") as src:
        a = src.read(band_index).astype(np.float32)
    a[~np.isfinite(a)] = np.nan
    a[~footprint] = np.nan
    return a


def grad_mag(a: np.ndarray, sigma: float = 1.0) -> np.ndarray:
    """Gradient magnitude of a smoothed band, in per-metre units."""
    fill = np.where(np.isfinite(a), a, float(np.nanmedian(a[np.isfinite(a)])))
    sm = gaussian_filter(fill, sigma)
    gy, gx = np.gradient(sm, 100.0)
    return np.hypot(gx, gy)


def build_antislope_surface(lid: dict, valid: np.ndarray) -> np.ndarray:
    """AS-1 antislope surface: gaussian(0.8px) of 0.5*(pct_rank(upface) + pct_rank(max(up-down,0)))."""
    up = lid["upface_max"].astype(np.float32) / 255.0
    down = lid["downface_max"].astype(np.float32) / 255.0
    r_up = pct_rank(up, valid)
    r_dom = pct_rank(np.maximum(up - down, 0.0), valid)
    return gaussian_filter(0.5 * (r_up + r_dom), GAUSS_SIGMA) * valid


def build_kth_edge_surface(footprint: np.ndarray, valid_rad: np.ndarray) -> np.ndarray:
    """K–Th alteration edge: gradient magnitude of K/Th ratio, percentile-ranked, masked to radiometric coverage."""
    k = read_training_band(17, footprint)  # iso_grav_anom? no — need K band index
    # K is radiometric band 0 in geodawn_rad_u8; read from external file
    with rasterio.open(DATA / "external/geodawn_rad_u8.tif") as src:
        rad = src.read()  # K, Th, U, TC
    k = rad[0].astype(np.float32)
    th = rad[1].astype(np.float32)
    k[k == 0] = np.nan
    th[th == 0] = np.nan
    ratio = k / th
    ratio[~footprint] = np.nan
    ratio[~valid_rad] = np.nan
    edge = grad_mag(ratio, sigma=1.0)
    edge[~valid_rad] = 0.0
    # percentile rank within valid radiometric pixels
    out = np.zeros_like(edge)
    finite = np.isfinite(edge) & (edge > 0)
    if finite.any():
        ranks = rankdata(edge[finite], method="average")
        out[finite] = (ranks / ranks.size).astype(np.float32)
    return gaussian_filter(out, GAUSS_SIGMA) * valid_rad


def main() -> None:
    t0 = time.time()
    base = load_base()
    footprint = base["footprint"]
    catalogue = base["catalogue"]
    lid = load_lidar()
    valid = footprint & (lid["valid"] > 0)

    # Radiometric valid mask (nonzero coverage in geodawn_rad)
    with rasterio.open(DATA / "external/geodawn_rad_u8.tif") as src:
        rad_valid = src.read(1) > 0
    valid_rad = footprint & rad_valid

    print(f"lidar-valid fraction {valid.sum()/footprint.sum():.4f}  "
          f"radiometric-valid fraction {valid_rad.sum()/footprint.sum():.4f}", flush=True)

    # --- Surfaces ---
    surf_anti = build_antislope_surface(lid, valid)
    surf_kth = build_kth_edge_surface(footprint, valid_rad)

    # Conjunction: min of the two (a pixel needs support in both domains)
    surf_conj = np.minimum(surf_anti, surf_kth) * (valid & valid_rad)

    # --- Canary: single-feature leakage AUC ---
    canary = {}
    for name, surf in (("antislope_only", surf_anti), ("kth_edge_only", surf_kth),
                        ("conjunction", surf_conj)):
        canary[name] = {
            "auc_off_catalogue_sgmc": auc(surf, base["far_field"], valid & valid_rad),
            "auc_catalogue": auc(surf, catalogue, valid & valid_rad),
        }
        print(f"canary {name:20s} sgmc {canary[name]['auc_off_catalogue_sgmc']:.3f}  "
              f"cat {canary[name]['auc_catalogue']:.3f}", flush=True)

    leakage_stop = any(
        v["auc_off_catalogue_sgmc"] > AUC_LEAKAGE_STOP or v["auc_catalogue"] > AUC_LEAKAGE_STOP
        for v in canary.values()
    )
    if leakage_stop:
        print("LEAKAGE STOP: a single feature exceeds AUC 0.90. Aborting.", flush=True)
        write_json(ROOT / "evidence/h1_antislope_kth.json", {
            "hypothesis": "H1-antislope-KTh-edge", "verdict": "negative",
            "reason": "single-feature leakage canary AUC > 0.90", "canary": canary,
        })
        return

    # --- Emission on holdout instruments ---
    insts = [discovery_instrument(base), *holdout_instruments(base)]
    incumbent = load_dots(
        ROOT / "docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif"
    )
    inc_name = "D28-incumbent (USER-REPORTED 0.2708, 40,199 dots)"

    stats: dict = {i.name: {} for i in insts}
    for inst in insts:
        stats[inst.name][inc_name] = lane.sufficient_stats(incumbent, inst)

    d_vis = distance_transform_edt(~catalogue)
    cand = (valid & valid_rad) & (d_vis > FLANK_PX) & ~catalogue
    order = emit(surf_conj, cand, BUDGET, min_dist_px=MIN_DIST_PX, return_order=True)
    print(f"emitted {len(order):,} candidate dots at full budget", flush=True)

    dots_full = lc_lane.prefix_mask(order, BUDGET, surf_conj.shape)
    for inst in insts:
        stats[inst.name]["H1-antislope-KTh@37654"] = lane.sufficient_stats(dots_full, inst)

    # Pooled holdout DTI with tile bootstrap
    gap_names = [i.name for i in insts if i.name.startswith("catalogue-gap")]
    pooled = {n: [stats[m][n] for m in gap_names if n in stats[m]]
              for n in stats[gap_names[0]]}
    pooled = {n: v for n, v in pooled.items() if len(v) == len(gap_names)}
    boot = lane.tile_bootstrap(pooled, n_boot=400)

    results = {
        "hypothesis": "H1-antislope-KTh-edge",
        "mechanism": "antislope LiDAR scarp AND K–Th radiometric contrast edge conjunction",
        "non_fault_mimic": "road cuts/terrace risers (antislope); playa mineral crusts (K–Th)",
        "evaluator": lane.EVAL_VERSION,
        "budget": BUDGET, "flank_px": FLANK_PX, "min_dist_px": MIN_DIST_PX,
        "canary": canary, "leakage_stop": leakage_stop,
    }
    table = {}
    for n in pooled:
        r = boot[n]
        table[n] = {
            "HOLDOUT_DTI": float(r["point"]),
            "ci95_tile_bootstrap": [float(r["ci95"][0]), float(r["ci95"][1])],
            "credit_per_dot": float(sum(s["tp"] for s in pooled[n]) / max(sum(s["dots"] for s in pooled[n]), 1)),
            "truth_pixels": int(sum(s["g"] for s in pooled[n])),
        }
        print(f"  {n:52s} DTI {r['point']:.4f} [{r['ci95'][0]:.4f},{r['ci95'][1]:.4f}]")
    results["instruments"] = table
    write_json(ROOT / "evidence/h1_antislope_kth.json", results)
    print(f"done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
