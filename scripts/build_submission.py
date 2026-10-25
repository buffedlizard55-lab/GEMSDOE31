#!/usr/bin/env python3
"""Emit a submission-ready GeoTIFF (and its fallbacks) from a binary dot set or a probability map.

Variants produced for every candidate:

* ``<name>-nan.tif``       — the official convention: finite values in ``[0,1]`` inside the footprint,
                             ``NaN`` outside it, ``nodata=nan`` (identical layout to the sample template).
* ``<name>-allfinite.tif`` — every cell finite, zeros outside the footprint; a fallback for portals that
                             evaluate the whole array instead of the masked footprint.
* ``<name>-nan.zip``       — a single-file archive holding the ``-nan`` GeoTIFF.

Every variant is re-validated with ``src/gemsdoe31/submission.py`` and a receipt is written next to it.
"""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import Affine

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gemsdoe31.submission import validate_submission  # noqa: E402

EXPECTED_TRANSFORM = Affine(100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)
PROFILE = {
    "driver": "GTiff", "dtype": "float32", "count": 1, "height": 3730, "width": 3292,
    "crs": "EPSG:32611", "transform": EXPECTED_TRANSFORM, "nodata": float("nan"),
    "compress": "deflate", "tiled": True, "blockxsize": 256, "blockysize": 256,
}


def footprint_mask(template_path: Path) -> np.ndarray:
    with rasterio.open(template_path) as src:
        return np.isfinite(src.read(1))


def load_dots(path: Path) -> np.ndarray:
    with rasterio.open(path) as src:
        values = src.read(1)
    return np.nan_to_num(values, nan=0.0) > 0


def write_variants(dots: np.ndarray, footprint: np.ndarray, out_stem: Path, *, name: str,
                   values: np.ndarray | None = None) -> dict:
    out_stem.parent.mkdir(parents=True, exist_ok=True)
    strength = np.ones(dots.shape, dtype=np.float32) if values is None else values.astype(np.float32)
    inside = np.where(dots, np.clip(strength, 0.0, 1.0), 0.0).astype(np.float32)
    nan_variant = np.where(footprint, inside, np.nan).astype(np.float32)
    finite_variant = np.where(footprint, inside, 0.0).astype(np.float32)
    nan_path = out_stem.with_name(out_stem.name + "-nan.tif")
    allfinite_path = out_stem.with_name(out_stem.name + "-allfinite.tif")
    with rasterio.open(nan_path, "w", **PROFILE) as dst:
        dst.write(nan_variant, 1)
        dst.update_tags(submission_name=name, convention="nan-outside-footprint")
    with rasterio.open(allfinite_path, "w", **PROFILE) as dst:
        dst.write(finite_variant, 1)
        dst.update_tags(submission_name=name, convention="all-finite-zero-outside")
    zip_path = out_stem.with_name(out_stem.name + "-nan.zip")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(nan_path, arcname=nan_path.name)
    return {"nan": nan_path, "allfinite": allfinite_path, "zip": zip_path}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--dots", help="binary/float GeoTIFF whose non-zero cells are the emission")
    source.add_argument("--prob", help="float GeoTIFF of probabilities; thresholded with --threshold")
    parser.add_argument("--threshold", type=float, default=0.4)
    parser.add_argument("--template", default="data/sample_submission.tif")
    parser.add_argument("--outdir", default="docs/downloads")
    parser.add_argument("--name", required=True, help="submission name (used in file names and metadata)")
    parser.add_argument("--note", default="", help="the comment to paste into the portal's Note box")
    args = parser.parse_args()

    template = ROOT / args.template
    footprint = footprint_mask(template)
    if args.dots:
        dots = load_dots(Path(args.dots))
        values = None
    else:
        with rasterio.open(Path(args.prob)) as src:
            prob = src.read(1)
        dots = np.nan_to_num(prob, nan=0.0) >= args.threshold
        values = np.nan_to_num(prob, nan=0.0)
    dots &= footprint

    stem = Path(args.outdir) / args.name
    paths = write_variants(dots, footprint, stem, name=args.name, values=values)
    receipts = {}
    conventions = {"nan": "nan-outside", "allfinite": "all-finite"}
    for key, path in paths.items():
        if path.suffix == ".tif":
            receipts[key] = validate_submission(path, template, convention=conventions[key])
    payload = {
        "schema_version": 1,
        "name": args.name,
        "note": args.note[:200],
        "dots": int(dots.sum()),
        "dots_on_catalogue": int((dots & (rasterio.open(ROOT / "data/labels.tif").read(1) == 1)).sum()),
        "files": {k: str(v if v.is_absolute() else v) for k, v in paths.items()},
        "validation": receipts,
        "warnings": [
            "Format validation is local. It cannot prove organizer acceptance and is not a score.",
            "The score of any file here is owner-reported unless a DrivenData receipt is attached.",
        ],
    }
    receipt_path = stem.with_name(stem.name + "-format-check.json")
    receipt_path.write_text(json.dumps(payload, indent=1) + "\n")
    print(json.dumps({"name": args.name, "dots": payload["dots"],
                      "nan_ok": receipts.get("nan", {}).get("ok_to_upload_format_only"),
                      "allfinite_ok": receipts.get("allfinite", {}).get("ok_to_upload_format_only"),
                      "receipt": str(receipt_path)}, indent=1))


if __name__ == "__main__":
    main()
