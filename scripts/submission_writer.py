#!/usr/bin/env python3
"""Shared fail-closed competition GeoTIFF submission writer + duplicate/contract validator.

Emits:
  - ``<slug>-nan.tif``       (primary template-aligned deliverable: finite [0, 1] inside footprint, NaN outside)
  - ``<slug>-allfinite.tif`` (portal fallback: finite [0, 1] inside footprint, 0.0 outside)
  - ``<slug>-nan.zip``       (zipped primary GeoTIFF for alternative portal upload)
  - ``<out-json>``           (programmatic fail-closed validation receipt + SHA-256 + duplicate canary)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gemsdoe31.holdout import check_registry_duplicate_canary  # noqa: E402
from gemsdoe31.submission import validate_submission  # noqa: E402
from scripts.build_submission import write_variants  # noqa: E402


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_grid(path: Path) -> np.ndarray:
    if path.suffix.lower() == ".npz":
        z = np.load(path)
        for key in ("score", "probability", "dots", "arr_0"):
            if key in z:
                return np.asarray(z[key], dtype=np.float32)
        first = list(z.keys())[0]
        return np.asarray(z[first], dtype=np.float32)
    if path.suffix.lower() == ".npy":
        return np.asarray(np.load(path), dtype=np.float32)
    with rasterio.open(path) as src:
        return src.read(1).astype(np.float32)


def emit_and_validate_submission(
    *,
    dots_2d: np.ndarray,
    surface_2d: np.ndarray,
    sample_path: Path,
    out_dir: Path,
    slug: str,
    note: str,
    registry_paths: list[Path],
    receipt_path: Path,
) -> dict:
    if len(note) > 140:
        raise ValueError(f"submission note exceeds 140 chars ({len(note)} chars)")

    with rasterio.open(sample_path) as src:
        footprint = np.isfinite(src.read(1))

    dots_mask = np.asarray(dots_2d, dtype=bool) & footprint
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = write_variants(dots_mask, footprint, out_dir / slug, name=slug)
    nan_path = paths["nan"]
    af_path = paths["allfinite"]
    zip_path = paths["zip"]

    val_nan = validate_submission(nan_path, template_path=sample_path, convention="nan-outside")
    val_af = validate_submission(af_path, template_path=sample_path, convention="all-finite")
    dup = check_registry_duplicate_canary(
        surface_2d=surface_2d,
        dots_2d=dots_mask,
        footprint=footprint,
        registry_paths=registry_paths,
    )

    # Strict extra checks ensuring ZERO chance of DrivenData range [0, 1] rejection
    with rasterio.open(nan_path) as src:
        arr_nan = src.read(1)
        nodata_tag = src.nodata
    in_vals = arr_nan[footprint]
    out_vals = arr_nan[~footprint]
    strict_checks = {
        "in_footprint_all_finite": bool(np.isfinite(in_vals).all()),
        "in_footprint_min_ge_0": bool(float(in_vals.min()) >= 0.0),
        "in_footprint_max_le_1": bool(float(in_vals.max()) <= 1.0),
        "in_footprint_strictly_binary_0_1": bool(set(np.unique(in_vals).tolist()).issubset({0.0, 1.0})),
        "outside_footprint_all_nan": bool(np.isnan(out_vals).all()),
        "nodata_tag_matches_template_nan": bool(nodata_tag is None or np.isnan(nodata_tag)),
        "nan_variant_passed": bool(val_nan["ok_to_upload_format_only"]),
        "allfinite_variant_passed": bool(val_af["ok_to_upload_format_only"]),
        "unique_vs_registry": bool(dup["passed"]),
        "nonzero_dots_positive": int((in_vals > 0.5).sum()) > 0,
    }
    ok_to_submit = all(strict_checks.values())

    receipt = {
        "schema_version": 1,
        "submission_name": f"{slug}-nan.tif",
        "slug": slug,
        "portal_note": note,
        "portal_note_length": len(note),
        "ok_to_download_and_submit": ok_to_submit,
        "status_banner": (
            "PASS - UNIQUE & COMPETITION-VALID GEOTIFF (OK TO DOWNLOAD)"
            if ok_to_submit
            else "FAIL - DO NOT SUBMIT (SEE FAILED CHECKS)"
        ),
        "strict_checks": strict_checks,
        "primary_nan_variant": {
            "path": str(nan_path),
            **val_nan,
            "zip_path": str(zip_path),
            "zip_bytes": int(zip_path.stat().st_size),
            "zip_sha256": _sha256_file(zip_path),
        },
        "fallback_allfinite_variant": {
            "path": str(af_path),
            **val_af,
        },
        "duplicate_canary": dup,
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    if not ok_to_submit:
        failed = [k for k, v in strict_checks.items() if not v]
        raise RuntimeError(f"Submission failed fail-closed validation gates: {failed}")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dots", required=True, help="2-D binary/float GeoTIFF, .npy, or .npz")
    parser.add_argument("--surface", default=None, help="Optional pre-placement score surface (.tif/.npy/.npz)")
    parser.add_argument(
        "--sample",
        default=str(Path(os.environ.get("GEMSDOE31_DATA_DIR", "data")) / "sample_submission.tif"),
    )
    parser.add_argument("--out-dir", default="docs/downloads")
    parser.add_argument("--slug", required=True)
    parser.add_argument("--note", required=True, help="<=140 character DrivenData portal note")
    parser.add_argument("--registry-glob", action="append", default=[])
    parser.add_argument("--out-json", required=True)
    args = parser.parse_args()

    dots = _load_grid(Path(args.dots))
    surf = _load_grid(Path(args.surface)) if args.surface else dots
    reg_paths: list[Path] = []
    for pat in args.registry_glob:
        reg_paths.extend(sorted(Path("/").glob(pat.lstrip("/")) if pat.startswith("/") else ROOT.glob(pat)))
    # Exclude the file being written itself if re-running
    reg_paths = [p for p in reg_paths if not p.name.startswith(args.slug)]

    receipt = emit_and_validate_submission(
        dots_2d=dots > 0.5,
        surface_2d=surf,
        sample_path=Path(args.sample),
        out_dir=Path(args.out_dir),
        slug=args.slug,
        note=args.note,
        registry_paths=reg_paths,
        receipt_path=Path(args.out_json),
    )
    print(f"{receipt['status_banner']} -> {receipt['primary_nan_variant']['path']} "
          f"(sha256={receipt['primary_nan_variant']['sha256'][:16]}...)")


if __name__ == "__main__":
    main()
