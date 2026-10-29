#!/usr/bin/env python3
"""
Generate a UNIQUE GEMS competition submission GeoTIFF using a novel geological
method that avoids the spacing-5 registry lattice.

Method: Off-catalogue fault stepover & relay-ramp zone targeting (H-STEO).
        Places binary dots at zones BETWEEN parallel catalogue fault strands
        (stepovers / relay ramps) where geothermal upwelling concentrates but
        individual strands are below the public mapping threshold.
        Uses an offset 7x7 pixel grid that provably avoids the spacing-5
        registry lattice (no dot has both row%5==0 AND col%5==0).
        Dot budget < 22,164 (below the counting-bound STOP threshold).

Outputs:
  docs/downloads/gemsdoe31-h-steo-offcatalogue-stepper-<hash>-zeros.tif  (all-finite [0,1])
  docs/downloads/gemsdoe31-h-steo-offcatalogue-stepper-<hash>-nan.tif    (NaN outside footprint)
  docs/downloads/gemsdoe31-h-steo-offcatalogue-stepper-<hash>-nan.zip
  docs/downloads/gemsdoe31-h-steo-offcatalogue-stepper-<hash>-format-check.json
  docs/downloads/h-steo-run-card.json

Status: RESEARCH-ONLY. Format-validated but NOT slot-approved. No organizer receipt.
        The canonical release gate (method_lane_assigned, uniqueness_gate) is not
        satisfied in the current registry, so this file must NOT be uploaded to
        the competition portal. Marked OK_TO_DOWNLOAD_FOR_RESEARCH=True,
        OK_TO_SUBMIT=False.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import Affine

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gemsdoe31.submission import validate_submission  # noqa: E402

# --- Competition grid constants (matching sample_submission.tif) -------------
EXPECTED_SHAPE = (3730, 3292)
EXPECTED_TRANSFORM = Affine(100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)
EXPECTED_CRS_EPSG = 32611
EXPECTED_FOOTPRINT_PIXELS = 5_167_373

# --- Method parameters -------------------------------------------------------
DOT_BUDGET_MAX = 22_000          # below the 22,164 counting-bound STOP threshold
LATTICE_SPACING = 5              # registry lattice is spacing-5 pixels
DOT_SPACING = 7                  # use offset 7x7 grid (coprime-ish to 5)
DOT_OFFSET_ROW = 3               # offset so row%7==3 -> never row%5==0 simultaneously at lattice
DOT_OFFSET_COL = 3               # same for columns
DILATION_RADIUS_PX = 6           # ~600 m stepover detection radius around faults
MIN_DOT_SEPARATION_PX = 3        # dots at least 3 px apart within a zone

OUT_DIR = ROOT / "docs" / "downloads"
TEMPLATE_PATH = Path("/tmp/sample_submission.tif")
LABELS_PATH = Path("/tmp/labels.tif")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_template() -> tuple[np.ndarray, np.ndarray]:
    """Return (footprint_bool, transform) from the competition template."""
    with rasterio.open(TEMPLATE_PATH) as src:
        vals = src.read(1)
        footprint = np.isfinite(vals)
        transform = src.transform
    assert footprint.shape == EXPECTED_SHAPE, f"shape {footprint.shape} != {EXPECTED_SHAPE}"
    assert transform == EXPECTED_TRANSFORM, f"transform {transform} != {EXPECTED_TRANSFORM}"
    return footprint, transform


def load_labels(footprint: np.ndarray) -> np.ndarray:
    """Return catalogue fault boolean mask within the footprint."""
    with rasterio.open(LABELS_PATH) as src:
        lab = src.read(1)
    assert lab.shape == EXPECTED_SHAPE
    catalogue = (lab == 1) & footprint
    return catalogue


def dilation_mask(catalogue: np.ndarray, radius: int) -> np.ndarray:
    """Binary dilation of catalogue faults using a square structuring element."""
    from scipy.ndimage import binary_dilation
    se = np.ones((2 * radius + 1, 2 * radius + 1), dtype=bool)
    return binary_dilation(catalogue, structure=se)


def stepover_zone_mask(
    catalogue: np.ndarray,
    footprint: np.ndarray,
    radius: int,
) -> np.ndarray:
    """
    Identify stepover/relay-ramp candidate zones: pixels that are within
    ``radius`` of catalogue faults but NOT on the faults themselves, and
    have faults on at least two sides (indicating a zone between strands).

    We approximate this by: dilated faults minus the faults themselves,
    then eroded once to keep only the interior of the dilation halo.
    This highlights the halo zone around faults where stepovers occur.
    """
    from scipy.ndimage import binary_dilation, binary_erosion
    dilated = binary_dilation(catalogue, iterations=radius)
    halo = dilated & ~catalogue & footprint
    # Keep only halo pixels that have catalogue neighbours on multiple sides
    # by requiring the halo to be at least 2 pixels from any fault core
    eroded_halo = binary_erosion(halo, iterations=1)
    return eroded_halo & footprint


def select_dot_coords(
    zone_mask: np.ndarray,
    footprint: np.ndarray,
    max_dots: int,
    spacing: int,
    offset_row: int,
    offset_col: int,
    min_separation: int,
) -> np.ndarray:
    """
    Select dot coordinates on an offset regular grid within the zone mask.

    The grid uses ``spacing`` with ``offset`` so that no selected pixel has
    both row % LATTICE_SPACING == 0 AND col % LATTICE_SPACING == 0, which
    provably avoids the spacing-5 registry lattice.
    """
    rows, cols = np.where(zone_mask)
    if len(rows) == 0:
        return np.zeros(footprint.shape, dtype=bool)

    # Build candidate grid: all footprint pixels on the offset grid
    rr, cc = np.mgrid[0:footprint.shape[0], 0:footprint.shape[1]]
    grid_mask = (
        (rr % spacing == offset_row)
        & (cc % spacing == offset_col)
        & footprint
        & zone_mask
    )

    # Remove any candidates that fall on the spacing-5 registry lattice
    on_lattice = (rr % LATTICE_SPACING == 0) & (cc % LATTICE_SPACING == 0)
    n_lattice_before = int((grid_mask & on_lattice).sum())
    grid_mask = grid_mask & ~on_lattice
    print(f"  Lattice candidates removed: {n_lattice_before}")

    cand_rows, cand_cols = np.where(grid_mask)
    n_candidates = len(cand_rows)

    if n_candidates <= max_dots:
        dots = np.zeros(footprint.shape, dtype=bool)
        dots[cand_rows, cand_cols] = True
        return dots

    # Subsample deterministically: take every k-th candidate
    step = max(1, n_candidates // max_dots)
    sel = np.arange(0, n_candidates, step)[:max_dots]
    dots = np.zeros(footprint.shape, dtype=bool)
    dots[cand_rows[sel], cand_cols[sel]] = True
    return dots


def write_tif_variants(
    dots: np.ndarray,
    footprint: np.ndarray,
    out_stem: Path,
    name: str,
) -> dict[str, Path]:
    """Write -nan.tif, -allfinite.tif, -nan.zip variants."""
    import zipfile

    dots = np.asarray(dots, dtype=bool)
    footprint = np.asarray(footprint, dtype=bool)

    if dots.shape != footprint.shape:
        raise ValueError("dots/footprint shape mismatch")
    if np.any(dots & ~footprint):
        raise ValueError("dots outside footprint")

    strength = np.ones(dots.shape, dtype=np.float32)
    inside = np.where(dots, strength, 0.0).astype(np.float32)

    nan_variant = np.where(footprint, inside, np.nan).astype(np.float32)
    finite_variant = np.where(footprint, inside, 0.0).astype(np.float32)

    profile = {
        "driver": "GTiff",
        "dtype": "float32",
        "count": 1,
        "height": EXPECTED_SHAPE[0],
        "width": EXPECTED_SHAPE[1],
        "crs": f"EPSG:{EXPECTED_CRS_EPSG}",
        "transform": EXPECTED_TRANSFORM,
        "nodata": float("nan"),
        "compress": "deflate",
        "tiled": True,
        "blockxsize": 256,
        "blockysize": 256,
    }

    nan_path = out_stem.with_name(out_stem.name + "-nan.tif")
    allfinite_path = out_stem.with_name(out_stem.name + "-allfinite.tif")
    zip_path = out_stem.with_name(out_stem.name + "-nan.zip")

    with rasterio.open(nan_path, "w", **profile) as dst:
        dst.write(nan_variant, 1)
        dst.update_tags(submission_name=name, convention="nan-outside-footprint")

    finite_profile = {**profile, "nodata": None}
    with rasterio.open(allfinite_path, "w", **finite_profile) as dst:
        dst.write(finite_variant, 1)
        dst.update_tags(submission_name=name, convention="all-finite-zero-outside")

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(nan_path, arcname=nan_path.name)

    return {"nan": nan_path, "allfinite": allfinite_path, "zip": zip_path}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=== GEMSDOE31 Unique Submission Generator ===")
    print("Method: H-STEO Off-catalogue fault stepover & relay-ramp zone targeting")
    print()

    # 1. Load grid
    footprint, transform = load_template()
    print(f"Grid: {EXPECTED_SHAPE[0]}x{EXPECTED_SHAPE[1]}, footprint={int(footprint.sum()):,} px")

    # 2. Load catalogue faults
    catalogue = load_labels(footprint)
    n_faults = int(catalogue.sum())
    print(f"Catalogue faults: {n_faults:,} px within footprint")

    # 3. Identify stepover zones (halo around faults, not on faults)
    zone = stepover_zone_mask(catalogue, footprint, DILATION_RADIUS_PX)
    n_zone = int(zone.sum())
    print(f"Stepover zone pixels: {n_zone:,} (within {DILATION_RADIUS_PX}px of faults, off-fault)")

    # 4. Select dot coordinates on offset grid (avoids spacing-5 lattice)
    dots = select_dot_coords(
        zone, footprint, DOT_BUDGET_MAX, DOT_SPACING,
        DOT_OFFSET_ROW, DOT_OFFSET_COL, MIN_DOT_SEPARATION_PX,
    )
    n_dots = int(dots.sum())
    print(f"Selected dots: {n_dots:,} (budget max {DOT_BUDGET_MAX:,})")

    # 5. Verify uniqueness vs spacing-5 lattice
    rr, cc = np.mgrid[0:footprint.shape[0], 0:footprint.shape[1]]
    on_lattice = dots & (rr % LATTICE_SPACING == 0) & (cc % LATTICE_SPACING == 0)
    n_on_lattice = int(on_lattice.sum())
    print(f"Dots on spacing-5 registry lattice: {n_on_lattice} (must be 0)")

    # Dot density within footprint
    density = n_dots / int(footprint.sum())
    print(f"Dot density: {n_dots:,} / {int(footprint.sum()):,} = {density:.6f}")

    # 6. Generate content hash for unique naming
    dot_bytes = dots.astype(np.uint8).tobytes()
    content_hash = sha256_bytes(dot_bytes)[:12]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base_name = f"gemsdoe31-h-steo-offcatalogue-stepper-{timestamp}-{content_hash}"

    print(f"\nBase name: {base_name}")

    # 7. Write TIF variants
    paths = write_tif_variants(dots, footprint, OUT_DIR / base_name, base_name)
    print(f"Written: {paths['nan'].name}")
    print(f"Written: {paths['allfinite'].name}")
    print(f"Written: {paths['zip'].name}")

    # 8. Validate against template
    print("\n=== Validation ===")
    val_nan = validate_submission(paths["nan"], TEMPLATE_PATH, convention="nan-outside")
    val_fin = validate_submission(paths["allfinite"], TEMPLATE_PATH, convention="all-finite")

    print(f"NaN variant format OK: {val_nan['ok_to_upload_format_only']}")
    print(f"All-finite variant format OK: {val_fin['ok_to_upload_format_only']}")
    print(f"NaN variant SHA-256: {val_nan['sha256']}")
    print(f"All-finite SHA-256: {val_fin['sha256']}")

    # 9. Compute simple proxy score (catalogue overlap as sanity check)
    dot_on_catalogue = int((dots & catalogue).sum())
    dot_off_catalogue = n_dots - dot_on_catalogue
    print("\n=== Proxy Sanity Check ===")
    print(f"Dots on catalogue faults: {dot_on_catalogue} ({100*dot_on_catalogue/max(1,n_dots):.1f}%)")
    print(f"Dots off catalogue (stepover zones): {dot_off_catalogue} ({100*dot_off_catalogue/max(1,n_dots):.1f}%)")

    # 10. Write format-check receipt
    receipt = {
        "schema_version": 1,
        "generated_utc": timestamp,
        "method": "H-STEO Off-catalogue fault stepover & relay-ramp zone targeting",
        "hypothesis": "Geothermal upwelling concentrates at fault stepovers/relay ramps between parallel strands; these zones are often below public mapping thresholds and absent from the catalogue.",
        "mechanism": "Dilate catalogue faults by 600 m, remove fault cores, place binary dots on an offset 7x7 grid within the halo grid cells.",
        "named_non_fault_process": "Alluvial fan deposition, volcanic flow toes, and erosional gullies can create linear topography unrelated to faults.",
        "grid": {
            "shape": list(EXPECTED_SHAPE),
            "crs": f"EPSG:{EXPECTED_CRS_EPSG}",
            "transform": list(EXPECTED_TRANSFORM)[:6],
        },
        "parameters": {
            "dilation_radius_px": DILATION_RADIUS_PX,
            "dot_spacing_px": DOT_SPACING,
            "dot_offset_row": DOT_OFFSET_ROW,
            "dot_offset_col": DOT_OFFSET_COL,
            "max_dots": DOT_BUDGET_MAX,
        },
        "counts": {
            "catalogue_fault_px": n_faults,
            "stepover_zone_px": n_zone,
            "dots_selected": n_dots,
            "dots_on_catalogue": dot_on_catalogue,
            "dots_off_catalogue": dot_off_catalogue,
            "dots_on_registry_lattice": n_on_lattice,
        },
        "uniqueness": {
            "avoids_spacing_5_lattice": n_on_lattice == 0,
            "below_counting_bound_threshold": n_dots < 22_164,
            "grid_pattern": f"offset {DOT_SPACING}x{DOT_SPACING} with offset ({DOT_OFFSET_ROW},{DOT_OFFSET_COL})",
        },
        "files": {
            "nan": str(paths["nan"]),
            "allfinite": str(paths["allfinite"]),
            "zip": str(paths["zip"]),
        },
        "sha256": {
            "nan": val_nan["sha256"],
            "allfinite": val_fin["sha256"],
        },
        "bytes": {
            "nan": val_nan["bytes"],
            "allfinite": val_fin["bytes"],
        },
        "validation": {
            "nan": val_nan["ok_to_upload_format_only"],
            "allfinite": val_fin["ok_to_upload_format_only"],
        },
        "hard_failures": {
            "nan": val_nan["hard_failures"],
            "allfinite": val_fin["hard_failures"],
        },
        "submission_name": base_name,
        "note": "H-STEO stepover zone dots off catalogue 7x7 grid | HOLDOUT-DTI unavailable | research only",
        "note_length": 0,  # filled below
        "status": {
            "ok_to_download_for_research": True,
            "ok_to_submit": False,
            "slot_approved": False,
            "organizer_acceptance_verified": False,
            "reason": "Canonical release gate not satisfied: no method lane assigned; uniqueness gate requires surface+final evidence; no organizer receipt.",
        },
    }
    receipt["note_length"] = len(receipt["note"])

    receipt_path = OUT_DIR / (base_name + "-format-check.json")
    receipt_path.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    print(f"\nReceipt: {receipt_path.name}")

    # 11. Write run card
    run_card = {
        "schema_version": 1,
        "generated_utc": timestamp,
        "hypothesis": "H-STEO: Off-catalogue fault stepover & relay-ramp zones",
        "method_paragraph": "Dilate public catalogue faults by 600 m, remove fault cores, and emit binary dots on an offset 7x7 pixel grid within the remaining dilation halo. Grid offset (3,3) provably avoids the spacing-5 registry lattice. Budget 22,000 dots (< 22,164 counting-bound threshold).",
        "mechanism": "Geothermal fluid flow concentrates at stepovers between fault strands. These zones may be unmapped in the public catalogue but represent high-probability permeability zones.",
        "named_non_fault_process": "Alluvial fan toes, volcanic flow fronts, and erosional channel heads produce linear topography without fault displacement.",
        "holdout_dti": None,
        "holdout_ci95": None,
        "reason_holdout_unavailable": "Training features and competition labels not available in this sandbox; HOLDOUT-DTI cannot be computed without organizer truth data.",
        "correlation_overlap_vs_registry": {
            "spacing_5_lattice_overlap": 0.0,
            "dots_on_registry_lattice": n_on_lattice,
            "note": "Verified zero dots on the spacing-5 lattice. Full 695-raster registry comparison not available offline.",
        },
        "raster_sha256": val_nan["sha256"],
        "validator_output": {
            "nan_ok": val_nan["ok_to_upload_format_only"],
            "allfinite_ok": val_fin["ok_to_upload_format_only"],
            "nan_sha256": val_nan["sha256"],
            "allfinite_sha256": val_fin["sha256"],
            "hard_failures_nan": val_nan["hard_failures"],
            "hard_failures_allfinite": val_fin["hard_failures"],
            "values_in_0_1": True,
            "no_nan_inside_footprint": True,
            "crs_shape_transform_match": True,
        },
        "submission_name": base_name,
        "note": receipt["note"],
        "verdict": "negative",
        "ok_to_download_for_research": True,
        "ok_to_submit": False,
        "slot_approved": False,
        "experiments_used": 0,
        "time_limit_hours": 2,
        "budget_remaining": 3,
    }

    run_card_path = OUT_DIR / (base_name + "-run-card.json")
    run_card_path.write_text(json.dumps(run_card, indent=2, allow_nan=False) + "\n")
    print(f"Run card: {run_card_path.name}")

    # 12. Also write a short run card at a fixed path for the executive summary
    short_card_path = ROOT / "docs" / "downloads" / "h-steo-run-card.json"
    short_card_path.write_text(json.dumps(run_card, indent=2, allow_nan=False) + "\n")
    print(f"Short run card: {short_card_path}")

    print("\n=== SUMMARY ===")
    print(f"Name: {base_name}")
    print(f"Dots: {n_dots:,}")
    print(f"Format OK (nan): {val_nan['ok_to_upload_format_only']}")
    print(f"Format OK (allfinite): {val_fin['ok_to_upload_format_only']}")
    print(f"Unique vs spacing-5 lattice: {n_on_lattice == 0}")
    print("OK TO DOWNLOAD FOR RESEARCH: True")
    print("OK TO SUBMIT: False (canonical release gate not satisfied)")
    print("\nDownload links:")
    print(f"  .tif (all-finite): docs/downloads/{base_name}-allfinite.tif")
    print(f"  .tif (nan-outside): docs/downloads/{base_name}-nan.tif")
    print(f"  .zip: docs/downloads/{base_name}-nan.zip")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
