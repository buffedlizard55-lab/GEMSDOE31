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
    dots = np.asarray(dots, bool)
    footprint = np.asarray(footprint, bool)
    if dots.ndim != 2 or dots.shape != footprint.shape:
        raise ValueError("dot and footprint grids must match")
    if np.any(dots & ~footprint):
        raise ValueError("positive support outside footprint; no silent repair")
    strength = np.ones(dots.shape, dtype=np.float32) if values is None else np.asarray(values)
    if strength.shape != dots.shape:
        raise ValueError("prediction values must match the dot grid")
    if not np.isfinite(strength[footprint]).all() or np.any((strength[footprint] < 0) | (strength[footprint] > 1)):
        raise ValueError("prediction values must already be finite in [0,1]; no silent clipping")
    if dots.shape != (PROFILE["height"], PROFILE["width"]):
        raise ValueError("aligned arrays must also match the exact competition template grid")
    inside = np.where(dots, strength, 0.0).astype(np.float32)
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

    if not 0.0 <= args.threshold <= 1.0 or not np.isfinite(args.threshold):
        raise ValueError("threshold must be finite in [0,1]")
    if len(args.note) > 140:
        raise ValueError("note must be at most 140 characters; not silently truncated")
    if not args.name or Path(args.name).name != args.name:
        raise ValueError("name must be a nonempty file stem, not a path")
    template = ROOT / args.template
    footprint = footprint_mask(template)
    with rasterio.open(template) as ref, rasterio.open(Path(args.dots or args.prob)) as src:
        if (ref.shape != (PROFILE["height"], PROFILE["width"]) or ref.crs is None
                or ref.crs.to_epsg() != 32611 or ref.transform != EXPECTED_TRANSFORM or ref.count != 1):
            raise ValueError("template itself must match the exact competition grid")
        if not footprint.any():
            raise ValueError("template must have a nonempty finite footprint")
        if src.count != 1 or (src.shape, src.crs, src.transform) != (ref.shape, ref.crs, ref.transform):
            raise ValueError("source must be single-band and match the exact template grid")
        raw = src.read(1)
    inside_raw = raw[footprint]
    if not np.isfinite(inside_raw).all() or np.any((inside_raw < 0) | (inside_raw > 1)):
        raise ValueError("source footprint values must already be finite in [0,1]; no repair")
    dots = footprint & (raw > 0) & (True if args.dots else raw >= args.threshold)
    values = None if args.dots else raw

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
        "note": args.note,
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
