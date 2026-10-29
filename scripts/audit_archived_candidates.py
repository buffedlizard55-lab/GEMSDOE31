#!/usr/bin/env python3
"""Read-only integrity and literal-uniqueness audit of archived H-STEO/CSDU bytes.

This does not fit, tune, package, write or upload a TIFF. It replays only the
saved H-STEO mask construction on the pinned public catalogue, audits the two
existing raster families against the pinned sample grid, and writes a
machine-readable negative review card. One hash-pinned registered control is
sufficient for a literal STOP; this is not an exhaustive 695-raster scan.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts"), str(ROOT / "vendor")]

import numpy as np  # noqa: E402
import rasterio  # noqa: E402
from scipy.ndimage import binary_dilation, binary_erosion, distance_transform_edt  # noqa: E402
from audit_shared_registry_stop import load_counterexample  # noqa: E402
from gemsdoe31.gate import block_density, footprint_blocks, spearman_blocks  # noqa: E402
from gemsdoe31.novelty import standardized_ranks  # noqa: E402
from gemsdoe31.submission import sha256_file, validate_submission  # noqa: E402

OUTPUT = "evidence/review_9f242e65/run_card.json"
HSTEO_NAME = "gemsdoe31-h-steo-offcatalogue-stepper-20261029T164949Z-4bbba08696ed"
CSDU_NAME = "gemsdoe31-csdu-stepover-8cf9dc27"
HSTEO_ORIGINAL_GENERATOR_SHA256 = "bafbd6469e25724f53b021d3d93e49ca233aec279c3f3557d52e5040b4ee4ad0"
CSDU_ORIGINAL_GENERATOR_SHA256 = "112fd0441b618916247eb4b5473f081616e6373df9cf85e9ce2450730dd5c293"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def packed_mask_sha256(mask: np.ndarray) -> str:
    return sha256_bytes(np.packbits(np.asarray(mask, dtype=bool).ravel()).tobytes())


def rank_rho(left: np.ndarray, right: np.ndarray) -> float | None:
    x = standardized_ranks(np.asarray(left, dtype=float))
    y = standardized_ranks(np.asarray(right, dtype=float))
    if x is None or y is None:
        return None
    return float(np.dot(x, y))


def rounded(value: float | None) -> float | None:
    return None if value is None else round(float(value), 12)


def check_zip(zip_path: Path, tif_path: Path) -> dict:
    with zipfile.ZipFile(zip_path) as archive:
        members = archive.namelist()
        if members != [tif_path.name]:
            raise ValueError(f"{zip_path.name}: expected one member {tif_path.name}; got {members}")
        payload = archive.read(members[0])
    if sha256_bytes(payload) != sha256_file(tif_path):
        raise ValueError(f"{zip_path.name}: archived TIFF differs from the standalone TIFF")
    return {
        "sha256": sha256_file(zip_path),
        "bytes": zip_path.stat().st_size,
        "members": members,
        "embedded_tiff_sha256_matches": True,
    }


def _manifest_entry(root: Path, file_id: str) -> dict:
    manifest = json.loads((root / "registry/data_manifest.json").read_text())
    matches = [row for row in manifest["files"] if row["id"] == file_id]
    if len(matches) != 1:
        raise ValueError(f"expected one manifest row for {file_id}; found {len(matches)}")
    return matches[0]


def _validate_pair(root: Path, stem: str) -> dict:
    nan_path = root / f"docs/downloads/{stem}-nan.tif"
    finite_path = root / f"docs/downloads/{stem}-allfinite.tif"
    template = root / "data/sample_submission.tif"
    return {
        "nan_outside": validate_submission(nan_path, template, convention="nan-outside"),
        "all_finite": validate_submission(finite_path, template, convention="all-finite"),
        "nan_zip": check_zip(root / f"docs/downloads/{stem}-nan.zip", nan_path),
    }


def _overlap_metrics(support: np.ndarray, control: np.ndarray, halo: np.ndarray,
                     footprint: np.ndarray) -> dict:
    count = int(support.sum())
    within = int((support & halo).sum())
    pixel_rho = rank_rho(support[footprint].astype(float), control[footprint].astype(float))
    block_rho = spearman_blocks(block_density(support), block_density(control), footprint_blocks(footprint))
    return {
        "candidate_support_pixels": count,
        "within_3px_of_registered_control": within,
        "overlap_within_3px": (within / count) if count else None,
        "exact_common_positive_pixels": int((support & control).sum()),
        "pixelwise_spearman": rounded(pixel_rho),
        "5px_block_density_spearman": rounded(block_rho),
        "max_abs_rank_correlation": rounded(max(
            (abs(v) for v in (pixel_rho, block_rho) if v is not None), default=0.0
        )),
        "packed_support_sha256": packed_mask_sha256(support),
    }


def _read_mask(path: Path) -> np.ndarray:
    with rasterio.open(path) as ds:
        return ds.read(1) > 0


def audit(root: Path = ROOT) -> dict:
    root = Path(root)
    release = json.loads((root / "registry/release_status.json").read_text())
    if release.get("ok_to_submit") is not False or release.get("slot_approved") is not False:
        raise ValueError("canonical release status is not a negative fail-closed decision")

    template = root / "data/sample_submission.tif"
    labels_path = root / "data/labels.tif"
    template_pin = _manifest_entry(root, "sample_submission")
    labels_pin = _manifest_entry(root, "labels")
    for path, pin in ((template, template_pin), (labels_path, labels_pin)):
        if sha256_file(path) != pin["sha256"]:
            raise ValueError(f"input hash mismatch: {path.relative_to(root)}")

    with rasterio.open(template) as ds:
        template_array = ds.read(1)
        footprint = np.isfinite(template_array)
    with rasterio.open(labels_path) as ds:
        labels = ds.read(1)
    if template_array.shape != labels.shape:
        raise ValueError("pinned template and public catalogue shapes differ")
    catalogue = (labels == 1) & footprint

    # Reconstruct the archived H-STEO implementation's pre-placement hard mask
    # and its exact 7x7 candidates. This is an audit replay, not a new hypothesis,
    # parameter search, fit, or output raster.
    hsteo_run_path = root / "docs/downloads/h-steo-run-card.json"
    hsteo_saved = json.loads(hsteo_run_path.read_text())
    hsteo_stem = hsteo_saved["submission_name"]
    if hsteo_stem != HSTEO_NAME:
        raise ValueError(f"unexpected H-STEO artifact identity: {hsteo_stem}")
    if hsteo_saved.get("ok_to_submit") is not False:
        raise ValueError("saved H-STEO card must remain non-approved")

    radius = 6
    dilated = binary_dilation(catalogue, iterations=radius)
    halo_mask = dilated & ~catalogue & footprint
    surface = binary_erosion(halo_mask, iterations=1) & footprint
    rows, cols = np.indices(footprint.shape)
    raw_grid = surface & (rows % 7 == 3) & (cols % 7 == 3) & footprint
    exact_spacing5 = (rows % 5 == 0) & (cols % 5 == 0)
    raw_grid_exact_collisions = int((raw_grid & exact_spacing5).sum())
    placed = raw_grid & ~exact_spacing5

    hsteo_nan = root / f"docs/downloads/{hsteo_stem}-nan.tif"
    hsteo_finite = root / f"docs/downloads/{hsteo_stem}-allfinite.tif"
    actual_hsteo = _read_mask(hsteo_nan) & footprint
    if not np.array_equal(placed, actual_hsteo):
        raise ValueError("H-STEO mask replay does not exactly reproduce the pinned TIFF support")
    if sha256_file(hsteo_nan) != hsteo_saved.get("raster_sha256"):
        raise ValueError("H-STEO raster SHA-256 differs from its saved run card")
    hsteo_pair = _validate_pair(root, hsteo_stem)
    hsteo_note = hsteo_saved["note"]
    if len(hsteo_note) > 140:
        raise ValueError("H-STEO note exceeds 140 characters")

    registry_pin, registered_raster = load_counterexample(root)
    control = footprint & np.isfinite(registered_raster) & (registered_raster > 0)
    distance_halo = distance_transform_edt(~control) <= 3
    if not control.any():
        raise ValueError("registered control has no positive cells inside the submission footprint")
    hsteo_metrics = {
        "surface": _overlap_metrics(surface, control, distance_halo, footprint),
        "preplacement_7x7_grid_before_exact_lattice_filter": _overlap_metrics(
            raw_grid, control, distance_halo, footprint
        ),
        "final_dots": _overlap_metrics(actual_hsteo, control, distance_halo, footprint),
    }
    hsteo_duplicate = any(
        stage["overlap_within_3px"] is not None and stage["overlap_within_3px"] > 0.70
        or stage["max_abs_rank_correlation"] is not None and stage["max_abs_rank_correlation"] > 0.90
        for stage in hsteo_metrics.values()
    )
    hsteo_hashes = {
        "nan": sha256_file(hsteo_nan),
        "all_finite": sha256_file(hsteo_finite),
        "nan_zip": sha256_file(root / f"docs/downloads/{hsteo_stem}-nan.zip"),
    }
    if hsteo_hashes["all_finite"] != hsteo_saved["validator_output"]["allfinite_sha256"]:
        raise ValueError("H-STEO all-finite bytes differ from the saved format receipt")
    hsteo_zip = check_zip(root / f"docs/downloads/{hsteo_stem}-nan.zip", hsteo_nan)

    # The archived CSDU script explicitly writes a synthetic ellipse footprint
    # and an all-zero catalogue. Revalidate only its already-existing TIFF bytes
    # against the actual pinned template; do not rebuild or alter them.
    csdu_run_path = root / f"docs/downloads/{CSDU_NAME}-run-card.json"
    csdu_saved = json.loads(csdu_run_path.read_text())
    csdu_nan = root / f"docs/downloads/{CSDU_NAME}-nan.tif"
    csdu_finite = root / f"docs/downloads/{CSDU_NAME}-allfinite.tif"
    if sha256_file(csdu_nan) != csdu_saved["raster_sha256"]["nan_outside_primary"]:
        raise ValueError("CSDU NaN TIFF SHA-256 differs from its saved run card")
    if sha256_file(csdu_finite) != csdu_saved["raster_sha256"]["allfinite_fallback"]:
        raise ValueError("CSDU all-finite TIFF SHA-256 differs from its saved run card")
    csdu_pair = _validate_pair(root, CSDU_NAME)
    with rasterio.open(csdu_nan) as ds:
        csdu_nan_values = ds.read(1)
    with rasterio.open(csdu_finite) as ds:
        csdu_finite_values = ds.read(1)
    csdu_total = int(np.count_nonzero(csdu_finite_values > 0))
    csdu_inside = int(np.count_nonzero((csdu_finite_values > 0) & footprint))
    csdu_outside = int(np.count_nonzero((csdu_finite_values > 0) & ~footprint))
    csdu_on_actual_catalogue = int(np.count_nonzero((csdu_finite_values > 0) & catalogue))
    csdu_nan_inside = int(np.count_nonzero(~np.isfinite(csdu_nan_values[footprint])))
    csdu_finite_outside = int(np.count_nonzero(np.isfinite(csdu_nan_values[~footprint])))
    if csdu_total != 4000 or csdu_inside + csdu_outside != csdu_total:
        raise ValueError("CSDU positive-pixel accounting does not match its frozen run card")
    csdu_script = root / "scripts/run_unique_stepover_submission.py"
    hsteo_script = root / "scripts/generate_unique_submission.py"
    csdu_note = csdu_saved["submission_note"]
    if len(csdu_note) > 140:
        raise ValueError("CSDU note exceeds 140 characters")

    # The user protocol is literal: a single verified registered witness causes
    # STOP. Passing file-format checks or a zero exact intersection cannot waive
    # the >70% 3-px support limit. No full-registry pass is claimed.
    hsteo_stopped = hsteo_duplicate
    if not hsteo_stopped:
        raise ValueError("expected H-STEO overlap STOP was not reproduced")
    if csdu_pair["all_finite"]["ok_to_upload_format_only"]:
        raise ValueError("CSDU should fail the actual-template all-finite footprint check")
    if csdu_pair["nan_outside"]["ok_to_upload_format_only"]:
        raise ValueError("CSDU should fail the actual-template NaN-outside check")

    return {
        "schema_version": 1,
        "review_id": "review-arena-9f242e65",
        "review_date_utc": "2026-10-29",
        "review_scope": (
            "Read-only audit of two already-existing archive families. No scientific lane was assigned; "
            "no experiment, new TIFF, slot selection, DrivenData access or submission occurred."
        ),
        "experiments_run_in_this_review": 0,
        "new_tif_generated_in_this_review": False,
        "submission_slots_used": 0,
        "hypothesis": hsteo_saved["hypothesis"],
        "mechanism": hsteo_saved["mechanism"],
        "named_non_fault_mimic": hsteo_saved["named_non_fault_process"],
        "scientific_method_audit": {
            "evidence_class": "CODE REVIEW of the preserved pre-audit source revision",
            "historical_generator_sha256": HSTEO_ORIGINAL_GENERATOR_SHA256,
            "current_generator_is_disabled": True,
            "implementation": (
                "Binary dilation of the public catalogue mask by six pixels, removal of the catalogue core, "
                "one erosion, then an offset 7x7 grid. The source does not test for two fault strands or "
                "construct a stepover-specific structural feature."
            ),
            "stepover_specificity_supported": False,
            "geophysical_or_topographic_feature_used": False,
            "min_separation_parameter_used": False,
            "qualification": (
                "The archived H-STEO name/mechanism overstate the implementation: it is a sparse mask "
                "around known catalogue faults, not an independently observed stepover detector."
            ),
        },
        "holdout_dti": {
            "evidence_class": "HOLDOUT-DTI",
            "status": "NOT RUN",
            "evaluator_version": None,
            "withheld_positive_pixels": None,
            "dti": None,
            "ci95": None,
            "reason": (
                "The existing H-STEO is a catalogue-mask geometry, not a trained geological feature model; "
                "private truth was not available, the feature stack was not restored, and no method paragraph assigned a lane."
            ),
        },
        "single_feature_leakage_canary": {
            "status": "NOT RUN",
            "reason": "No feature stack was restored and no model was fitted in this read-only audit.",
        },
        "correlation_overlap_vs_registry": {
            "scope": "One hash-pinned registered owner-mirror lattice listed in a 695-raster manifest; not exhaustive.",
            "evidence_class": "COMPUTED on pinned owner-mirror bytes",
            "coverage_complete": False,
            "literal_gate": "STOP if any stage has |rank correlation| > 0.90 or >70% of candidate support within 3 px.",
            "registered_witness": registry_pin["counterexample"],
            "registered_rasters_in_manifest": registry_pin["registered_rasters"],
            "manifest_sha256": registry_pin["manifest_sha256"],
            "preplacement_and_final": hsteo_metrics,
            "raw_7x7_grid_exact_spacing5_collisions_removed": raw_grid_exact_collisions,
            "literal_duplicate_stop": hsteo_stopped,
            "decision_reason": (
                "The final dots have 9,135/9,140 (99.9453%) within 3 px of one registered raster. "
                "The surface support has 99.9650% within 3 px. Rank correlations are small but do not waive the overlap rule."
            ),
        },
        "hsteo_artifact": {
            "submission_name": hsteo_stem,
            "note": hsteo_note,
            "note_characters": len(hsteo_note),
            "files": {
                "nan": f"docs/downloads/{hsteo_stem}-nan.tif",
                "all_finite": f"docs/downloads/{hsteo_stem}-allfinite.tif",
                "nan_zip": f"docs/downloads/{hsteo_stem}-nan.zip",
                "saved_run_card": "docs/downloads/h-steo-run-card.json",
            },
            "historical_generator_source_sha256": HSTEO_ORIGINAL_GENERATOR_SHA256,
            "current_generator_guard_sha256": sha256_file(hsteo_script),
            "sha256": hsteo_hashes,
            "nan_zip_integrity": hsteo_zip,
            "validator": hsteo_pair,
            "format_valid_against_pinned_template": all(
                hsteo_pair[k]["ok_to_upload_format_only"] for k in ("nan_outside", "all_finite")
            ),
            "historical_exact_lattice_intersection": {
                "reported_in_saved_card": hsteo_saved["correlation_overlap_vs_registry"]["dots_on_registry_lattice"],
                "recomputed_final_exact_common_pixels": hsteo_metrics["final_dots"]["exact_common_positive_pixels"],
                "qualification": (
                    "Exact-cell intersection only. The 7x7 offset alone does not avoid a 5x5 lattice; "
                    "the generator explicitly filtered 394 exact intersections from 9,534 raw grid cells. "
                    "This does not satisfy the required 3-pixel overlap gate."
                ),
            },
            "verdict": "negative — literal registered-registry overlap STOP",
            "ok_to_download_for_research": True,
            "ok_to_submit": False,
            "slot_approved": False,
            "leaderboard_estimate": None,
        },
        "csdu_artifact": {
            "submission_name": csdu_saved["submission_name"],
            "note": csdu_note,
            "note_characters": len(csdu_note),
            "files": {
                "nan": f"docs/downloads/{CSDU_NAME}-nan.tif",
                "all_finite": f"docs/downloads/{CSDU_NAME}-allfinite.tif",
                "nan_zip": f"docs/downloads/{CSDU_NAME}-nan.zip",
                "saved_run_card": f"docs/downloads/{CSDU_NAME}-run-card.json",
            },
            "sha256": {
                "nan": sha256_file(csdu_nan),
                "all_finite": sha256_file(csdu_finite),
                "nan_zip": sha256_file(root / f"docs/downloads/{CSDU_NAME}-nan.zip"),
            },
            "nan_zip_integrity": check_zip(root / f"docs/downloads/{CSDU_NAME}-nan.zip", csdu_nan),
            "original_template_and_labels": {
                "provenance": "The archived generator source constructed a synthetic ellipse footprint and an all-zero labels raster.",
                "historical_generator_source_sha256": CSDU_ORIGINAL_GENERATOR_SHA256,
                "current_generator_guard_sha256": sha256_file(csdu_script),
                "not_competition_inputs": True,
                "positive_pixels_in_saved_file": csdu_total,
                "positive_pixels_inside_actual_template_footprint": csdu_inside,
                "positive_pixels_outside_actual_template_footprint": csdu_outside,
                "positive_pixels_on_actual_public_catalogue": csdu_on_actual_catalogue,
                "saved_zero_catalogue_count_used_synthetic_all_zero_labels": csdu_saved["validator_output"]["dots_on_public_catalogue"] == 0,
                "nan_pixels_inside_actual_template_footprint": csdu_nan_inside,
                "finite_pixels_outside_actual_template_footprint": csdu_finite_outside,
            },
            "validator_against_actual_pinned_template": csdu_pair,
            "format_valid_against_actual_pinned_template": False,
            "registry_uniqueness": "NOT TESTED: invalid footprint fails before candidate uniqueness is meaningful.",
            "verdict": "negative — synthetic grid/labels; actual-template validation fails",
            "ok_to_download_for_research": True,
            "ok_to_submit": False,
            "slot_approved": False,
            "leaderboard_estimate": None,
        },
        "data_provenance": {
            "sample_submission_sha256": template_pin["sha256"],
            "public_catalogue_labels_sha256": labels_pin["sha256"],
            "shared_registry_manifest_sha256": registry_pin["manifest_sha256"],
            "registered_control_sha256": registry_pin["counterexample"]["sha256"],
            "all_are_owner_mirror_bytes_not_organizer_authenticated": True,
        },
        "canonical_release_status": {
            "path": "registry/release_status.json",
            "review_id": release.get("review_id"),
            "verdict": release.get("verdict"),
            "ok_to_submit": release.get("ok_to_submit"),
            "slot_approved": release.get("slot_approved"),
            "method_lane_assigned": release.get("method_lane_assigned"),
        },
        "leaderboard_estimate_for_new_file": None,
        "leaderboard_estimate_reason": (
            "No new candidate was created; neither existing archive artifact has a validated holdout or organizer score receipt."
        ),
        "overall_verdict": "DO NOT SUBMIT — no file approved; H-STEO fails the 3-px literal registry gate; CSDU is invalid on the actual template.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare the deterministic audit with its saved run card")
    args = parser.parse_args()
    result = audit()
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    path = ROOT / OUTPUT
    if args.check:
        if not path.is_file() or path.read_text() != text:
            raise SystemExit(f"stale/missing {OUTPUT}; run python scripts/audit_archived_candidates.py")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    print(json.dumps({
        "overall_verdict": result["overall_verdict"],
        "experiments_run_in_this_review": result["experiments_run_in_this_review"],
        "new_tif_generated_in_this_review": result["new_tif_generated_in_this_review"],
        "hsteo_final_overlap_3px": result["correlation_overlap_vs_registry"]["preplacement_and_final"]["final_dots"]["overlap_within_3px"],
        "csdu_actual_template_valid": result["csdu_artifact"]["format_valid_against_actual_pinned_template"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
