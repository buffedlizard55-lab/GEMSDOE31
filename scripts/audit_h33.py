#!/usr/bin/env python3
"""Forensic comparison of prior prediction rasters; never a predictor builder."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/prior_audit"
H33_REL = "GEMSDOE32/docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"
H27_REL = "GEMSDOE28/docs/downloads/gems28-h27-4-r1-solo-d2-8-20261003-8acb75e1f2cc-nan.tif"
D28_REL = "GEMSDOE25/docs/downloads/gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif"
USER_CLAIMS = [
    ("GEMSDOE24", "h25-1-dotted-h19-5-d1-5", 0.2477),
    ("GEMSDOE25", "dotted-h19-5-d2-8", 0.2600),
    ("GEMSDOE27", "topo-gap-closure-t-v2-on-d1-5", 0.2449),
    ("GEMSDOE28", "h36-1-rung30-blind-r1", 0.2710),
    ("GEMSDOE30", "d28-poisson300m-offcat-44090", 0.2600),
    ("GEMSDOE31", "h27-4-solo-d28", 0.2708),
    ("GEMSDOE32", "h33-h33-2-b2", 0.2778),
    ("GEMSDOE33", "h33d-analog-tip-stepover-r30", 0.2632),
    ("GEMSDOE36", "anderson-geothermal-pinn-38854", 0.2750),
]


def read(path: Path) -> np.ndarray:
    with rasterio.open(path) as ds:
        return ds.read(1)


def main() -> None:
    with rasterio.open(ROOT / "data/sample_submission.tif") as ds:
        fp = np.isfinite(ds.read(1))
    cat = (read(ROOT / "data/labels.tif") > 0) & fp
    dist = distance_transform_edt(~cat)
    h33_raw = read(BASE / H33_REL)
    h33, h27, d28 = [np.isfinite(a) & (a > 0) & fp for a in
                     (h33_raw, read(BASE / H27_REL), read(BASE / D28_REL))]
    expected_h33 = h27 & (dist > 2)
    expected_h27 = d28 & (dist > 1)
    yx = np.column_stack(np.nonzero(h33))
    nn = cKDTree(yx).query(yx, k=2)[0][:, 1]
    audit = {
        "evidence_class": "RASTER-MEASUREMENT", "generated_utc": "2026-10-25",
        "h33_file": H33_REL, "h33_sha256": hashlib.sha256((BASE / H33_REL).read_bytes()).hexdigest(),
        "h33_positive_pixels": int(h33.sum()), "h27_positive_pixels": int(h27.sum()),
        "d28_positive_pixels": int(d28.sum()), "h33_equals_h27_pruned_at_2px": bool(np.array_equal(h33, expected_h33)),
        "h27_equals_d28_pruned_at_1px": bool(np.array_equal(h27, expected_h27)),
        "h33_pixels_added_vs_h27": int((h33 & ~h27).sum()),
        "h33_pixels_removed_vs_h27": int((h27 & ~h33).sum()),
        "h33_on_catalogue_pixels": int((h33 & cat).sum()),
        "h33_min_catalogue_distance_px": float(dist[h33].min()),
        "h33_nearest_dot_distance_m": {"min": float(nn.min() * 100), "median": float(np.median(nn) * 100)},
        "all_prediction_values_finite": bool(np.isfinite(h33_raw).all()),
        "prediction_range": [float(h33_raw.min()), float(h33_raw.max())],
        "reference_used_for_learning_only": True, "organizer_confirmed_score": None,
        "score_receipt_exists": False,
        "mechanistic_inference": "The geometry changes only by catalogue-flank deletion. It adds no new geological "
                                 "information. Sparse spacing limits redundant kernel coverage. A benefit requires "
                                 "the removed FP weight to outweigh lost truth credit; that condition cannot be "
                                 "verified for the private truth from these files.",
        "metric_algebra": {"T": "sum over truth pixels of maximum p*k", "F": "prediction mass minus self-credit M",
                           "K": "number of truth pixels", "DTI": "T/(0.2*T+0.2*F+0.8*K+epsilon)",
                           "prune_improves_iff": "lost_T < 0.2*S/(1-0.2*S) * removed_F, for current DTI S"},
        "limits": ["User-reported 0.2778 is not organizer-confirmed and is never used as a model target.",
                   "The reported outcome does not prove causation or a geological discovery.",
                   "No verified data support a claim that a new file will exceed 0.2778, 0.3195 or 0.4413."],
    }
    trees = {json.loads(p.read_text())["repo"].split("/")[-1]: json.loads(p.read_text()) for p in BASE.glob("*_tree.json")}
    comparison = []
    for repo, pattern, value in USER_CLAIMS:
        tree = trees[repo]
        matches = [b["path"] for b in tree["tree"] if b["path"].startswith("docs/downloads/")
                   and b["path"].endswith(".tif") and pattern in b["path"]]
        paths = sorted(matches, key=lambda p: ("nan" in p, len(p)))
        file = BASE / repo / paths[0] if paths else None
        row = {"repo": repo, "ref": tree["commit"], "requested_artifact": pattern,
               "reported_value_quarantined": value, "reported_value_class": "USER-REPORTED-NOT-AUTHENTICATED",
               "organizer_confirmed_score": None, "receipt_exists": False,
               "source_url": f"https://github.com/buffedlizard55-lab/{repo}/tree/{tree['commit']}",
               "published_paths_matching_request": matches}
        if file is not None and file.exists():
            a = read(file)
            row.update(file=str(file.relative_to(ROOT)), sha256=hashlib.sha256(file.read_bytes()).hexdigest(),
                       positive_pixels=int((np.isfinite(a) & (a > 0) & fp).sum()),
                       values_in_range_on_footprint=bool(np.isfinite(a[fp]).all() and (a[fp] >= 0).all()
                                                         and (a[fp] <= 1).all()))
        comparison.append(row)
    audit["requested_site_comparison"] = comparison
    (ROOT / "evidence/h33_forensics_20261025.json").write_text(json.dumps(audit, indent=1, allow_nan=False) + "\n")
    print(json.dumps({k: v for k, v in audit.items() if k in (
        "h33_positive_pixels", "h33_equals_h27_pruned_at_2px", "h27_equals_d28_pruned_at_1px",
        "h33_pixels_removed_vs_h27", "score_receipt_exists")}, indent=1))


if __name__ == "__main__":
    main()
