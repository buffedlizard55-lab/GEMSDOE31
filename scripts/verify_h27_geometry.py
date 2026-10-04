#!/usr/bin/env python3
"""Verify the geometry of the best-known submission from the files themselves.

The owner mirror describes the h27-4 file as a *one-pixel catalogue-flank prune* of the D2.8 sparse
emission: 44,090 cells reduced to 40,199. That description lives in an owner-run repository, so this
script tests it against the two published rasters and the catalogue raster, and records what is
measurable:

* nearest-neighbour spacing inside the dot set (is it a dotted emission or a solid field?),
* how many D2.8 cells lie within one cell of the public catalogue, and whether removing exactly those
  cells reproduces the h27-4 cell set bit for bit,
* the distance distribution of retained cells from the catalogue.

Writes ``evidence/h27_geometry.json``. Run: ``python scripts/verify_h27_geometry.py``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
PRISTINE = "docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif"
BASE_D28 = "docs/downloads/gemsdoe31-reference-d28-offcat-44090-20261004-nan.tif"
OWNER_PAGE_SHA256 = "ab02300152248fdda04e988e2cd2a0c13f35eec42fcf670a15e8b76b19e24a73"


def mask(path: Path) -> np.ndarray:
    with rasterio.open(path) as src:
        return np.nan_to_num(src.read(1), nan=0.0) > 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalogue", default="data/labels.tif")
    parser.add_argument("--out", default="evidence/h27_geometry.json")
    args = parser.parse_args()
    catalogue_path = ROOT / args.catalogue
    if not catalogue_path.is_file():
        raise SystemExit(f"{catalogue_path} is missing; run scripts/download_competition_data.sh first")

    pristine = mask(ROOT / PRISTINE)
    base = mask(ROOT / BASE_D28)
    with rasterio.open(catalogue_path) as src:
        catalogue = src.read(1) == 1

    rows, cols = np.nonzero(pristine)
    points = np.column_stack([rows, cols])
    tree = cKDTree(points)
    distance, _ = tree.query(points, k=2)
    spacing = distance[:, 1] * 100.0

    distance_to_catalogue = distance_transform_edt(~catalogue, sampling=100.0)
    retained_distance = distance_to_catalogue[rows, cols]

    pruned = base & (distance_to_catalogue > 100.0)
    payload = {
        "schema_version": 1,
        "generated_utc": "2026-10-04",
        "claim_class": "COMPUTED from the two published rasters and the catalogue raster",
        "files": {"best_known": PRISTINE, "d28_base": BASE_D28},
        "owner_page_sha256_for_the_best_known_file": OWNER_PAGE_SHA256,
        "owner_page_sha256_note": "the owner page publishes this SHA-256; it was not byte-matched here because "
                                  "the raw.githubusercontent host is unreachable from the sandbox",
        "counts": {
            "best_known_cells": int(pristine.sum()),
            "d28_base_cells": int(base.sum()),
            "catalogue_cells": int(catalogue.sum()),
            "best_known_cells_within_100m_of_catalogue": int((retained_distance <= 100.0).sum()),
            "d28_cells_within_100m_of_catalogue": int((distance_to_catalogue[base] <= 100.0).sum()),
            "d28_cells_removed_from_base": int(base.sum() - pruned.sum()),
            "cells_in_both": int((pristine & base).sum()),
            "cells_only_in_best_known": int((pristine & ~base).sum()),
            "cells_only_in_d28": int((base & ~pristine).sum()),
        },
        "prune_test": {
            "rule": "remove every D2.8 cell within 100 m (one cell) of the public catalogue",
            "reproduces_best_known_exactly": bool(np.array_equal(pruned, pristine)),
            "pruned_cells": int(pruned.sum()),
        },
        "nearest_neighbour_spacing_m": {
            "min": float(spacing.min()),
            "p05": float(np.percentile(spacing, 5)),
            "median": float(np.median(spacing)),
            "mean": float(spacing.mean()),
            "p95": float(np.percentile(spacing, 95)),
            "note": "100 m cells; 300 m is the metric's triangular-kernel support, so a dotted emission at this "
                    "spacing still reaches almost every truth pixel while paying 0.2 of the denominator per dot",
        },
        "distance_to_catalogue_m_for_retained_cells": {
            "median": float(np.median(retained_distance)),
            "p05": float(np.percentile(retained_distance, 5)),
            "p95": float(np.percentile(retained_distance, 95)),
            "within_200m": int((retained_distance <= 200.0).sum()),
        },
    }
    out = ROOT / args.out
    out.write_text(json.dumps(payload, indent=1) + "\n")
    counts = payload["counts"]
    print(f"best-known cells {counts['best_known_cells']:,} | D2.8 cells {counts['d28_base_cells']:,}")
    print(f"cells within 100 m of the catalogue: best-known {counts['best_known_cells_within_100m_of_catalogue']},"
          f" D2.8 {counts['d28_cells_within_100m_of_catalogue']}")
    print(f"prune test reproduces the best-known cell set exactly: "
          f"{payload['prune_test']['reproduces_best_known_exactly']} "
          f"(counts: both {counts['cells_in_both']:,}, best-known-only {counts['cells_only_in_best_known']:,},"
          f" D2.8-only {counts['cells_only_in_d28']:,})")
    print(f"nearest-neighbour spacing: min {spacing.min():.0f} m, median {np.median(spacing):.0f} m, "
          f"mean {spacing.mean():.0f} m")
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
