#!/usr/bin/env python3
"""Emit locally format-checked research GeoTIFFs; this never grants submission approval.

Variants produced for every candidate:

* ``<name>-nan.tif``       — historically recorded official wording: finite ``[0,1]`` in the footprint,
                             ``NaN`` outside it, ``nodata=nan`` (identical layout to the sample template).
* ``<name>-allfinite.tif`` — every cell finite, zeros outside the footprint; a fallback for portals that
                             evaluate the whole array instead of the masked footprint.
* ``<name>-nan.zip``       — a single-file archive holding the ``-nan`` GeoTIFF.

Every variant is re-validated with ``src/gemsdoe31/submission.py`` and a receipt is written next to it.
"""

from __future__ import annotations

import argparse
import json
import re
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
    dots = np.asarray(dots, dtype=bool)
    footprint = np.asarray(footprint, dtype=bool)
    if dots.shape != footprint.shape or dots.shape != (PROFILE["height"], PROFILE["width"]):
        raise ValueError("dots/footprint must match the exact output grid")
    if np.any(dots & ~footprint):
        raise ValueError("dots outside the footprint; no silent masking")
    strength = np.ones(dots.shape, dtype=np.float32) if values is None else np.asarray(values)
    if strength.shape != dots.shape or np.iscomplexobj(strength):
        raise ValueError("prediction strengths must be real and grid-aligned")
    active = strength[footprint]
    if not np.isfinite(active).all() or (active < 0).any() or (active > 1).any():
        raise ValueError("predictions must already be finite in [0,1]; no clipping or repair")
    out_stem.parent.mkdir(parents=True, exist_ok=True)
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
    parser.add_argument("--labels", default=None, help="optional path to labels.tif (defaults to <template_dir>/labels.tif or data/labels.tif)")
    parser.add_argument("--outdir", default="docs/downloads")
    parser.add_argument("--name", required=True, help="submission name (used in file names and metadata)")
    parser.add_argument("--note", default="", help="the comment to paste into the portal's Note box")
    args = parser.parse_args()

    t_arg = Path(args.template)
    template = t_arg if t_arg.is_absolute() else (ROOT / t_arg)
    if args.labels:
        l_arg = Path(args.labels)
        labels_path = l_arg if l_arg.is_absolute() else (ROOT / l_arg)
    elif (template.parent / "labels.tif").is_file():
        labels_path = template.parent / "labels.tif"
    else:
        labels_path = ROOT / "data/labels.tif"
    footprint = footprint_mask(template)
    source_path = Path(args.dots or args.prob)
    with rasterio.open(source_path) as src, rasterio.open(template) as ref:
        if src.count != 1 or src.shape != ref.shape or src.crs != ref.crs or src.transform != ref.transform:
            raise ValueError("input predictions do not match the single-band template grid")
        prob = src.read(1)
    if not np.isfinite(prob[footprint]).all() or (prob[footprint] < 0).any() or (prob[footprint] > 1).any():
        raise ValueError("input footprint predictions must already be finite in [0,1]; no silent repair")
    if len(args.note) > 140 or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,139}", args.name):
        raise ValueError("name must be a path-safe 1..140 character slug; note at most 140")
    if args.dots and np.any(np.isfinite(prob[~footprint]) & (prob[~footprint] > 0)):
        raise ValueError("input dots outside the footprint; no silent masking")
    if not np.isfinite(args.threshold) or not 0 <= args.threshold <= 1:
        raise ValueError("threshold must be finite in [0,1]")
    dots = ((prob > 0) if args.dots else (prob >= args.threshold)) & footprint
    values = None if args.dots else prob

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
        "dots_on_catalogue": int((dots & (rasterio.open(labels_path).read(1) == 1)).sum()),
        "files": {k: str(v if v.is_absolute() else v) for k, v in paths.items()},
        "validation": receipts,
        "warnings": [
            "Format validation is local. It cannot prove organizer acceptance and is not a score.",
            "Competition claims without exact-file organizer receipts are USER-REPORTED; local metrics are separate HOLDOUT-DTI.",
            "Outside-footprint convention and organizer acceptance are unresolved; no scientific/slot approval is granted.",
        ],
    }
    receipt_path = stem.with_name(stem.name + "-format-check.json")
    receipt_path.write_text(json.dumps(payload, indent=1) + "\n")
    if not all(r["ok_to_upload_format_only"] for r in receipts.values()):
        raise ValueError("written artifact failed local format validation; see receipt")
    print(json.dumps({"name": args.name, "dots": payload["dots"],
                      "nan_ok": receipts.get("nan", {}).get("ok_to_upload_format_only"),
                      "allfinite_ok": receipts.get("allfinite", {}).get("ok_to_upload_format_only"),
                      "receipt": str(receipt_path)}, indent=1))


if __name__ == "__main__":
    main()
