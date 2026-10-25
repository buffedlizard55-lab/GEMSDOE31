#!/usr/bin/env python3
"""Shared submission GeoTIFF writer and automated multi-gate validator (GEMSDOE31).

Reuses ``scripts/build_submission.py`` and ``src/gemsdoe31/submission.py`` without private forks.
Writes:
* ``<outdir>/<name>-nan.tif``       (official null/NaN outside footprint convention)
* ``<outdir>/<name>-allfinite.tif`` (defensive zero-outside convention)
* ``<outdir>/<name>-nan.zip``       (single-GeoTIFF zip archive)
* ``<outdir>/<name>-format-check.json`` (full machine-verified format & gate receipt)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from build_submission import footprint_mask, write_variants  # noqa: E402
from gemsdoe31.submission import validate_submission  # noqa: E402


def emit_and_validate_submission(
    dots_mask: np.ndarray,
    *,
    template_path: Path,
    labels_path: Path,
    outdir: Path,
    name: str,
    note: str,
    values: np.ndarray | None = None,
    gate_summary: dict | None = None,
) -> dict:
    """Write ``-nan.tif``, ``-allfinite.tif``, ``-nan.zip`` and verify every format & range invariant."""
    if len(note) > 140:
        raise ValueError(f"Submission note exceeds 140 characters ({len(note)} chars): {note!r}")
    footprint = footprint_mask(template_path)
    if dots_mask.shape != footprint.shape:
        raise ValueError(f"dots_mask shape {dots_mask.shape} != template {footprint.shape}")

    clean_dots = np.asarray(dots_mask, dtype=bool) & footprint
    with rasterio.open(labels_path) as src:
        catalogue = (src.read(1) == 1) & footprint

    stem = outdir / name
    paths = write_variants(clean_dots, footprint, stem, name=name, values=values)

    val_nan = validate_submission(paths["nan"], template_path, convention="nan-outside")
    val_fin = validate_submission(paths["allfinite"], template_path, convention="all-finite")
    if not val_nan["ok_to_upload_format_only"] or not val_fin["ok_to_upload_format_only"]:
        raise RuntimeError(
            f"Generated TIFF failed strict validator: nan={val_nan['hard_failures']} "
            f"allfinite={val_fin['hard_failures']}"
        )

    payload = {
        "schema_version": 1,
        "name": name,
        "note": note,
        "note_length": len(note),
        "dots": int(clean_dots.sum()),
        "dots_on_catalogue": int((clean_dots & catalogue).sum()),
        "files": {
            k: str(v.relative_to(ROOT) if v.is_absolute() and v.is_relative_to(ROOT) else v)
            for k, v in paths.items()
        },
        "validation": {"nan": val_nan, "allfinite": val_fin},
        "automated_gates": gate_summary,
        "warnings": [
            "Format validation is local and automated. It cannot prove live DrivenData organizer acceptance.",
            "Promotion to an actual weekly DrivenData slot remains a separate human selector step within the 3/week cap.",
        ],
    }
    receipt_path = stem.with_name(stem.name + "-format-check.json")
    receipt_path.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mask-npy", type=Path, required=True, help="Boolean/float 2D .npy mask of emitted dots")
    parser.add_argument("--template", type=Path, default=ROOT / ".cache/data/sample_submission.tif")
    parser.add_argument("--labels", type=Path, default=ROOT / ".cache/data/labels.tif")
    parser.add_argument("--outdir", type=Path, default=ROOT / "docs/downloads")
    parser.add_argument("--name", required=True)
    parser.add_argument("--note", required=True, help="Short portal comment (<= 140 chars)")
    parser.add_argument("--gates-json", type=Path, default=None)
    args = parser.parse_args()

    arr = np.load(args.mask_npy, allow_pickle=False)
    dots = np.nan_to_num(arr, nan=0.0) > 0.5
    gates = json.loads(args.gates_json.read_text()) if args.gates_json and args.gates_json.is_file() else None
    receipt = emit_and_validate_submission(
        dots,
        template_path=args.template.resolve(),
        labels_path=args.labels.resolve(),
        outdir=args.outdir.resolve(),
        name=args.name,
        note=args.note,
        gate_summary=gates,
    )
    print(
        json.dumps(
            {
                "name": receipt["name"],
                "dots": receipt["dots"],
                "dots_on_catalogue": receipt["dots_on_catalogue"],
                "nan_sha256": receipt["validation"]["nan"]["sha256"],
                "allfinite_sha256": receipt["validation"]["allfinite"]["sha256"],
                "format_ok_nan": receipt["validation"]["nan"]["ok_to_upload_format_only"],
                "format_ok_allfinite": receipt["validation"]["allfinite"]["ok_to_upload_format_only"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
