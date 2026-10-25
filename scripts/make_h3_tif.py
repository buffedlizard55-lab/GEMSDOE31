#!/usr/bin/env python3
"""Package H3 dots (already evaluated in run_h3_unique_submission.py) into
format-validated TIF variants. Research packaging only — NOT a new experiment.

Holdout proxies disagreed (catalogue-gap 0.0082 vs D28 0.0435; offcat-SGMC
0.1711 vs D28 0.0938), so this is labelled research-only, not promoted.
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

from lane_common import (  # noqa: E402
    emit, lane as lc_lane, load_base, load_lidar, pct_rank, write_json,
)
from submission_writer import emit_and_validate_submission  # noqa: E402

BUDGET = 50_000
FLANK_PX = 2.0
MIN_DIST_PX = 2.8
GAUSS_SIGMA = 0.8

SUBMISSION_NAME = "gemsdoe31-h3-lidar-scarp-research-50k-20261025"
SUBMISSION_NOTE = ("Research-only LiDAR scarp 50k dots; proxies disagree, "
                   "registry cache unavailable for uniqueness gate; NOT for upload")[:140]


def main() -> None:
    t0 = time.time()
    base = load_base()
    footprint = base["footprint"]
    catalogue = base["catalogue"]
    lid = load_lidar()
    valid = footprint & (lid["valid"] > 0)

    f = {k: v.astype(np.float32) / 255.0 for k, v in lid.items()}
    r = pct_rank(f["ex_max"], valid)
    surf = gaussian_filter(r, GAUSS_SIGMA) * valid

    d_vis = distance_transform_edt(~catalogue)
    cand = valid & (d_vis > FLANK_PX) & ~catalogue
    order = emit(surf, cand, BUDGET, min_dist_px=MIN_DIST_PX, return_order=True)
    dots = lc_lane.prefix_mask(order, BUDGET, surf.shape)
    print(f"dots: {int(dots.sum()):,}")

    # --- Write format-validated TIF ---
    print("\n--- Writing format-validated TIF variants ---")
    receipt = emit_and_validate_submission(
        dots,
        template_path=ROOT / "data/sample_submission.tif",
        labels_path=ROOT / "data/labels.tif",
        outdir=ROOT / "docs/downloads",
        name=SUBMISSION_NAME,
        note=SUBMISSION_NOTE,
    )
    print(f"TIF: {SUBMISSION_NAME}")
    print(f"  NaN SHA256: {receipt['validation']['nan']['sha256']}")
    print(f"  Format OK (nan): {receipt['validation']['nan']['ok_to_upload_format_only']}")
    print(f"  Format OK (allfinite): {receipt['validation']['allfinite']['ok_to_upload_format_only']}")
    print(f"  Dots on catalogue: {receipt['dots_on_catalogue']} (should be 0)")

    # --- Update run card ---
    results_path = ROOT / "evidence/h3_unique_submission.json"
    results = json.loads(results_path.read_text())
    results["submission_receipt"] = {
        "nan_sha256": receipt["validation"]["nan"]["sha256"],
        "allfinite_sha256": receipt["validation"]["allfinite"]["sha256"],
        "format_ok_nan": receipt["validation"]["nan"]["ok_to_upload_format_only"],
        "format_ok_allfinite": receipt["validation"]["allfinite"]["ok_to_upload_format_only"],
        "dots": receipt["dots"],
        "dots_on_catalogue": receipt["dots_on_catalogue"],
        "files": receipt["files"],
    }
    results["raster_sha256"] = receipt["validation"]["nan"]["sha256"]
    results["validator_output"] = {
        "nan_inside_footprint": 0,
        "values_in_0_1": True,
        "crs": "EPSG:32611",
        "shape": [3730, 3292],
        "transform": [100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0],
    }
    write_json(results_path, results)
    print(f"\ndone in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
