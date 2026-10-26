#!/usr/bin/env python3
"""Read-only exact-file audit of XFCOH31 against one pinned shared-registry witness.

One authentic counterexample is enough to fail the literal overlap gate. This script
never scans for a passing comparator, fits a model, changes a surface, places dots, or
writes a TIFF. By default it prints a fresh diagnostic; ``--write`` persists the audit
receipt, while ``--check-record`` recomputes and verifies the committed receipt.
"""
from __future__ import annotations

from datetime import datetime, timezone
import argparse
import json
from pathlib import Path
import sys

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "vendor"), str(ROOT / "scripts")]

from audit_shared_registry_stop import load_counterexample  # noqa: E402
from gemsdoe31.novelty import standardized_ranks  # noqa: E402
from gemsdoe31.submission import sha256_file, validate_submission  # noqa: E402

CANDIDATE = Path("docs/downloads/gems31-xfcoh31-xfield-coherence-37654-20261026-zeros.tif")
CARD = Path("evidence/xfcoh31_run_card.json")
PIN = Path("registry/shared_registry_57_pin.json")
MANIFEST_KEY = "manifest_sha256"
OVERLAP_LIMIT = 0.70
CORRELATION_LIMIT = 0.90


def audit(root: Path = ROOT, *, restore_witness: bool = False) -> dict:
    """Compute exact format and one-witness duplicate diagnostics for the existing TIFF."""
    candidate_path = root / CANDIDATE
    card_path = root / CARD
    if not candidate_path.is_file() or not card_path.is_file():
        raise FileNotFoundError("XFCOH31 TIFF or run card is absent")

    card = json.loads(card_path.read_text())
    candidate_sha = sha256_file(candidate_path)
    if candidate_sha != card["raster_sha256"]:
        raise ValueError("XFCOH31 TIFF hash differs from its evidence run card")

    pin, reference = load_counterexample(root, restore=restore_witness)
    pin_document = json.loads((root / PIN).read_text())
    manifest_path = root / pin_document["manifest"]
    manifest = json.loads(manifest_path.read_text())
    if len(manifest["rasters"]) != pin_document["registered_rasters"]:
        raise ValueError("pinned registry count differs from its manifest")

    template_path = root / "data/sample_submission.tif"
    with rasterio.open(template_path) as template:
        template_values = template.read(1, masked=False)
        footprint = np.isfinite(template_values)
        template_crs = template.crs
        template_transform = template.transform
        template_meta = {
            "shape": list(template.shape),
            "crs": template_crs.to_string() if template_crs else None,
            "transform": list(template_transform)[:6],
            "dtype": list(template.dtypes),
            "count": template.count,
            "footprint_pixels": int(footprint.sum()),
        }

    with rasterio.open(candidate_path) as candidate:
        if candidate.count != 1:
            raise ValueError(f"candidate has {candidate.count} bands, expected one")
        if candidate.shape != footprint.shape:
            raise ValueError("candidate grid shape differs from the template")
        if candidate.crs is None or candidate.crs.to_epsg() != 32611:
            raise ValueError("candidate CRS is not EPSG:32611")
        if candidate.crs != template_crs:
            raise ValueError("candidate CRS differs from the exact template")
        if candidate.transform != template_transform:
            raise ValueError("candidate transform differs from the exact template")
        values = candidate.read(1, masked=False)
        candidate_meta = {
            "shape": list(candidate.shape),
            "crs": candidate.crs.to_string(),
            "transform": list(candidate.transform)[:6],
            "dtype": list(candidate.dtypes),
            "count": candidate.count,
            "nodata": candidate.nodata,
            "bytes": candidate_path.stat().st_size,
        }

    if not np.isfinite(values).all():
        raise ValueError("the zeros-outside XFCOH31 TIFF is not finite everywhere")
    if not np.isfinite(reference[footprint]).any():
        raise ValueError("registered witness has no comparable finite values inside the template footprint")

    positive = footprint & (values > 0)
    witness_positive = footprint & np.isfinite(reference) & (reference > 0)
    if not positive.any() or not witness_positive.any():
        raise ValueError("candidate or registered witness has no positive footprint pixels")
    witness_halo = distance_transform_edt(~witness_positive) <= 3.0
    within_3px = int((positive & witness_halo).sum())
    positive_count = int(positive.sum())
    overlap = within_3px / positive_count

    candidate_ranks = standardized_ranks(values[footprint])
    witness_values = np.where(np.isfinite(reference[footprint]), reference[footprint], 0.0)
    witness_ranks = standardized_ranks(witness_values)
    if candidate_ranks is None or witness_ranks is None:
        rho = None
    else:
        rho = float(np.dot(candidate_ranks, witness_ranks))

    format_receipt = validate_submission(
        candidate_path, template_path, convention="all-finite", require_competition_grid=True
    )
    if format_receipt["sha256"] != candidate_sha:
        raise ValueError("format validator read different candidate bytes")

    rows = manifest["rasters"]
    witness_manifest_row = next(
        (row for row in rows if row.get("sha256") == pin["counterexample"]["sha256"]), None
    )
    if witness_manifest_row is None:
        raise ValueError("pinned witness is not present in the pinned shared-registry manifest")

    correlation_pass = rho is not None and abs(rho) <= CORRELATION_LIMIT
    overlap_pass = overlap <= OVERLAP_LIMIT
    literal_pass = correlation_pass and overlap_pass
    result = {
        "schema_version": 1,
        "audited_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "evidence_class": "COMPUTED exact-file duplicate-stop diagnostic; not a HOLDOUT-DTI or competition score",
        "candidate": {
            "path": CANDIDATE.as_posix(),
            "sha256": candidate_sha,
            "bytes": candidate_meta["bytes"],
            "grid": candidate_meta,
            "positive_dots_inside_footprint": positive_count,
            "nan_or_inf_inside_footprint": int((~np.isfinite(values[footprint])).sum()),
            "finite_everywhere": bool(np.isfinite(values).all()),
        },
        "template": template_meta,
        "registry_witness": {
            "registry_pin": PIN.as_posix(),
            "manifest": pin_document["manifest"],
            "manifest_sha256": pin_document[MANIFEST_KEY],
            "registered_rasters_in_manifest": len(rows),
            "registered_rasters_pinned": pin_document["registered_rasters"],
            "rasters_examined": 1,
            "coverage_complete": False,
            "reason": "One authentic registered counterexample is sufficient for STOP; no exhaustive scan of all 695 rasters is claimed.",
            "source_repository": pin["repository"],
            "source_commit": pin["commit"],
            "source_url": pin["source_url"],
            "witness": pin["counterexample"],
            "witness_registered": True,
            "witness_positive_pixels_inside_footprint": int(witness_positive.sum()),
        },
        "surface_scope": {
            "preplacement_surface_tested_against_shared_registry": False,
            "reason": "This is a post-placement audit of the exact existing TIFF. The final-dot overlap alone triggers STOP, so no new placement or surface search was run.",
        },
        "correlation": {
            "method": f"exact Spearman rank correlation (average ties) over the full {int(footprint.sum()):,}-pixel template footprint",
            "spearman_rho": rho,
            "absolute_spearman_rho": abs(rho) if rho is not None else None,
            "limit": CORRELATION_LIMIT,
            "pass": bool(correlation_pass),
        },
        "overlap": {
            "distance_pixels": 3,
            "candidate_dots_within_3px_of_witness": within_3px,
            "candidate_dots": positive_count,
            "fraction_within_3px": overlap,
            "limit": OVERLAP_LIMIT,
            "pass": bool(overlap_pass),
        },
        "format_validation": {
            "convention": "all-finite zeros outside footprint",
            "ok_to_upload_format_only": format_receipt["ok_to_upload_format_only"],
            "organizer_acceptance_verified": format_receipt["organizer_acceptance_verified"],
            "hard_failures": format_receipt["hard_failures"],
            "checks": format_receipt["checks"],
            "receipt_path": "evidence/xfcoh31_validate_all-finite.json",
        },
        "literal_gate_pass": bool(literal_pass),
        "duplicate_stop": not literal_pass,
        "verdict": "STOP / NEGATIVE / DO NOT SUBMIT" if not literal_pass else "PASS",
        "ok_to_download_for_research": True,
        "ok_to_submit": False,
        "slot_approved": False,
        "no_new_experiment_fit_surface_placement_or_tiff_written": True,
        "scope_correction": "The prior focus-site comparison is a limited comparator subset, not a global uniqueness approval. The user's literal shared-registry rule includes the pinned calibration lattice; no density or control exemption is applied.",
    }
    return result


def check_record(actual: dict, record_path: Path) -> None:
    """Fail if the committed evidence receipt drifts from a fresh exact-file audit."""
    if not record_path.is_file():
        raise FileNotFoundError(record_path)
    expected = json.loads(record_path.read_text())
    scalar_paths = (
        ("candidate", "sha256"),
        ("registry_witness", "manifest_sha256"),
        ("registry_witness", "rasters_examined"),
        ("correlation", "spearman_rho"),
        ("overlap", "candidate_dots_within_3px_of_witness"),
        ("overlap", "candidate_dots"),
        ("overlap", "fraction_within_3px"),
        ("literal_gate_pass",),
        ("duplicate_stop",),
    )
    for path in scalar_paths:
        observed = actual
        recorded = expected
        for key in path:
            observed = observed[key]
            recorded = recorded[key]
        if isinstance(observed, float):
            if recorded is None or abs(observed - float(recorded)) > 1e-12:
                raise ValueError(f"committed XFCOH31 audit drift at {'.'.join(path)}")
        elif observed != recorded:
            raise ValueError(f"committed XFCOH31 audit drift at {'.'.join(path)}")
    if expected["registry_witness"]["coverage_complete"]:
        raise ValueError("the stored audit must not claim exhaustive coverage")
    if actual["literal_gate_pass"] or not actual["duplicate_stop"] or actual["ok_to_submit"]:
        raise ValueError("the recomputed literal STOP/negative result is not preserved")
    if not actual["format_validation"]["ok_to_upload_format_only"]:
        raise ValueError("the recorded local format-only validation no longer passes")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--restore-witness", action="store_true", help="restore only the pinned witness if absent")
    parser.add_argument("--write", action="store_true", help="write evidence/xfcoh31_registry_stop_audit.json")
    parser.add_argument("--check-record", action="store_true", help="compare a fresh audit with the committed JSON receipt")
    args = parser.parse_args()

    result = audit(restore_witness=args.restore_witness)
    record_path = ROOT / "evidence/xfcoh31_registry_stop_audit.json"
    if args.check_record:
        check_record(result, record_path)
    if args.write:
        record_path.write_text(json.dumps(result, indent=1, allow_nan=False) + "\n")
    print(json.dumps(result, indent=1, allow_nan=False))


if __name__ == "__main__":
    main()
