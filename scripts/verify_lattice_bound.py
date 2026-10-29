#!/usr/bin/env python3
"""Recompute the 3-px counting bound against the registered spacing-5 control (audit only).

For a candidate with N dots inside the template footprint, the number of candidate dots that can sit
more than 3 px from every control dot is at most U (the footprint pixels farther than 3 px from every
control dot). So at least N - U dots fall within 3 px, i.e. a forced overlap of (N - U) / N.
This script recomputes U from the hash-pinned cached control and checks it against the registry.
Evidence class: COMPUTED counting bound (not HOLDOUT-DTI, not a score). No exemption is applied.
Run: ``python scripts/verify_lattice_bound.py``. Writes ``evidence/review_48c411be/lattice_bound.json``.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence" / "review_48c411be" / "lattice_bound.json"
CONTROL = ROOT / ".cache" / "registry-scope" / "registered-lattice.tif"
SAMPLE = ROOT / "data" / "sample_submission.tif"
RELEASE = ROOT / "registry" / "release_status.json"
PIN = ROOT / "registry" / "shared_registry_57_pin.json"
RADIUS_PX = 3.0
BUDGET = 37654


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    pin = json.loads(PIN.read_text())["counterexample"]
    if sha256_file(CONTROL) != pin["sha256"]:
        raise SystemExit("cached control does not match the registry pin; run verify_current_run.py --restore-small-inputs")
    if not SAMPLE.is_file():
        raise SystemExit("data/sample_submission.tif missing; run verify_current_run.py --restore-small-inputs")

    with rasterio.open(SAMPLE) as ds:
        footprint = np.isfinite(ds.read(1))
    with rasterio.open(CONTROL) as ds:
        control_vals = ds.read(1).astype(np.float64)
        control_grid = (ds.shape, ds.crs.to_string(), tuple(ds.transform)[:6])
    control_fin = np.isfinite(control_vals)
    control_dots = np.nan_to_num(control_vals, nan=0.0) > 0

    dist = distance_transform_edt(~control_dots)  # px distance from each pixel to the nearest control dot
    within = footprint & (dist <= RADIUS_PX + 1e-9)
    uncovered = int((footprint & ~(dist <= RADIUS_PX + 1e-9)).sum())
    footprint_px = int(footprint.sum())
    covered_share = float(within.sum() / footprint_px)
    forced_min_overlap = (BUDGET - uncovered) / BUDGET

    release = json.loads(RELEASE.read_text())["lattice_coverage"]
    checks = {
        "footprint_pixels_match_registry": footprint_px == release["footprint_pixels"],
        "uncovered_pixels_match_registry": uncovered == release["outside_3px_halo"],
        "coverage_fraction_matches_registry": abs(covered_share - release["coverage_fraction"]) < 1e-12,
        "min_forced_overlap_matches_registry": abs(forced_min_overlap - release["minimum_overlap_any_same_budget"]) < 1e-12,
        "control_finite_equals_footprint": bool(np.array_equal(control_fin, footprint)),
    }
    out = {
        "schema_version": 1,
        "evidence_class": "COMPUTED counting bound; not HOLDOUT-DTI and not a score",
        "control": {"path": pin["cache_file"], "repo": pin["repo"], "ref": pin["ref"], "sha256": pin["sha256"],
                    "grid": {"shape": list(control_grid[0]), "crs": control_grid[1], "transform": list(control_grid[2])},
                    "dots": int(control_dots.sum())},
        "budget_dots": BUDGET,
        "radius_px": RADIUS_PX,
        "footprint_pixels": footprint_px,
        "pixels_within_radius_of_control_dots": int(within.sum()),
        "pixels_uncovered_by_radius": uncovered,
        "coverage_fraction": covered_share,
        "forced_minimum_overlap_for_budget": forced_min_overlap,
        "checks_against_registry": checks,
        "qualification": "Bound for a candidate with exactly BUDGET dots inside the footprint. It is not a statement that "
                         "every nonempty raster must overlap; a smaller budget changes the bound. No exemption, no bypass.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"uncovered": uncovered, "forced_min_overlap": forced_min_overlap, "checks": checks}, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
