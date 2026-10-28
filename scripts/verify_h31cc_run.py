#!/usr/bin/env python3
"""Recheck the existing H31-CC research artifact without rerunning science.

This verifier reads the already-published H31-CC pair, pinned sample/labels,
registered lattice witness, and one-TIFF ZIP. It does not rebuild a feature
surface, rerun HOLDOUT-DTI, emit dots, or authorize an upload/slot.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]

import numpy as np  # noqa: E402
import rasterio  # noqa: E402
from scipy.ndimage import distance_transform_edt  # noqa: E402
from scipy.spatial import cKDTree  # noqa: E402
from audit_shared_registry_stop import load_counterexample  # noqa: E402
from gemsdoe31.novelty import standardized_ranks  # noqa: E402
from gemsdoe31.release_policy import POLICY_VERSION, overlap_budget_preflight  # noqa: E402
from gemsdoe31.submission import sha256_file, validate_submission  # noqa: E402

CARD_PATH = "evidence/h31cc/run_card.json"
PUBLIC_CARD_PATH = "docs/downloads/h31cc-run-card.json"
RECEIPT_PATH = "evidence/h31cc/verification_receipt.json"
PUBLIC_RECEIPT_PATH = "docs/downloads/h31cc-verification.json"


def _json(root: Path, relative: str) -> dict:
    return json.loads((root / relative).read_text())


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def verify(root: Path = ROOT) -> dict:
    """Re-derive byte, format, ZIP, and one registered-witness checks."""
    root = Path(root)
    card = _json(root, CARD_PATH)
    public_card = _json(root, PUBLIC_CARD_PATH)
    _assert(card == public_card, "H31-CC run-card copies differ")

    data_manifest = _json(root, "registry/data_manifest.json")
    pins = {row["id"]: row for row in data_manifest["files"]}
    for input_id in ("sample_submission", "labels"):
        item = pins[input_id]
        path = root / "data" / item["dest"]
        if not path.is_file():
            raise FileNotFoundError(f"{path}; run verify_current_run.py --restore-small-inputs")
        _assert(sha256_file(path) == item["sha256"], f"pinned {input_id} byte hash mismatch")

    prereg_path = root / card["preregistration"]
    _assert(sha256_file(prereg_path) == card["preregistration_sha256"],
            "H31-CC preregistration hash mismatch")
    _assert(card.get("method_paragraph_in_prompt") is False,
            "H31-CC provenance no longer records the missing assigned method paragraph")
    _assert(card.get("verdict") == "negative" and card.get("ok_to_submit") is False
            and card.get("slot_approved") is False and card.get("submission_slots_used") == 0,
            "H31-CC run card does not fail closed")
    _assert(card.get("leaderboard_estimate") is None,
            "H31-CC must not carry a leaderboard estimate")
    hold = card.get("holdout_dti") or {}
    _assert(hold.get("evidence_class") == "HOLDOUT-DTI"
            and hold.get("evaluator_version") == "gems57-pooled-hide-v2"
            and hold.get("withheld_positive_pixels") == 60_988,
            "H31-CC HOLDOUT-DTI metadata drift")
    paired = hold.get("paired_vs_null") or {}
    _assert(paired.get("delta", 0) < 0,
            "H31-CC no longer records a negative paired screen versus its same-run NULL")

    files = card["files"]
    zeros = root / files["zeros"]
    nan = root / files["nan"]
    archive = root / files["zip"]
    for path in (zeros, nan, archive):
        if not path.is_file():
            raise FileNotFoundError(path)
    _assert(sha256_file(zeros) == files["sha256"] == card["raster_sha256"],
            "H31-CC primary TIFF SHA-256 mismatch")
    _assert(sha256_file(nan) == files["sha256_nan"], "H31-CC NaN-outside TIFF SHA-256 mismatch")
    _assert(sha256_file(archive) == files["sha256_zip"], "H31-CC ZIP SHA-256 mismatch")

    for path in (zeros, nan):
        with rasterio.open(path) as ds:
            _assert(ds.count == 1 and ds.dtypes == ("float32",), f"{path.name}: band/dtype mismatch")
            _assert(ds.crs is not None and ds.crs.to_epsg() == 32611, f"{path.name}: CRS mismatch")
            _assert(ds.shape == (3730, 3292), f"{path.name}: shape mismatch")
            _assert(tuple(ds.transform)[:6] == (100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0),
                    f"{path.name}: affine transform mismatch")

    sample = root / "data" / pins["sample_submission"]["dest"]
    labels_path = root / "data" / pins["labels"]["dest"]
    with rasterio.open(sample) as ds:
        template = ds.read(1, masked=False)
        foot = np.isfinite(template)
    with rasterio.open(labels_path) as ds:
        catalogue = ds.read(1, masked=False) == 1
    _assert(int(foot.sum()) == 5_167_373 and int(catalogue.sum()) == 60_988,
            "pinned template/catalogue footprint counts drifted")

    vz = validate_submission(zeros, sample, convention="all-finite")
    vn = validate_submission(nan, sample, convention="nan-outside")
    for name, report in (("all-finite", vz), ("NaN-outside", vn)):
        _assert(report["ok_to_upload_format_only"] and not report["hard_failures"],
                f"H31-CC {name} format validation failed: {report['hard_failures']}")
    _assert(vz == files["validator"], "saved H31-CC all-finite validator receipt is stale")
    _assert(vn == files["validator_nan"], "saved H31-CC NaN-outside validator receipt is stale")

    with rasterio.open(zeros) as ds:
        values = ds.read(1, masked=False)
    with rasterio.open(nan) as ds:
        nan_values = ds.read(1, masked=False)
    _assert(np.isfinite(values).all() and np.all((values >= 0) & (values <= 1)),
            "H31-CC all-finite raster is not finite in [0,1]")
    _assert(np.array_equal(values[foot], nan_values[foot]),
            "H31-CC encodings disagree inside the template footprint")
    _assert(np.all(values[~foot] == 0), "H31-CC all-finite raster has nonzero outside-footprint values")
    _assert(np.isnan(nan_values[~foot]).all(), "H31-CC NaN twin is not NaN outside the footprint")
    _assert(np.isin(values[foot], (0.0, 1.0)).all(), "H31-CC primary raster is not binary")
    dots = foot & (values > 0)
    dot_count = int(dots.sum())
    _assert(dot_count == files["dots"] == 37_654, "H31-CC dot count mismatch")
    catalogue_hits = int((dots & catalogue).sum())
    _assert(catalogue_hits == 0, "H31-CC includes a positive on the public catalogue")
    nearest = cKDTree(np.argwhere(dots)).query(np.argwhere(dots), k=2)[0][:, 1]
    minimum_separation_px = float(nearest.min())
    _assert(minimum_separation_px > 2.8, "H31-CC violates its preregistered 2.8 px minimum spacing")

    with zipfile.ZipFile(archive) as zf:
        _assert(zf.testzip() is None, "H31-CC ZIP has a CRC failure")
        _assert(zf.namelist() == [zeros.name], "H31-CC ZIP must contain exactly its all-finite TIFF")
        _assert(zf.read(zeros.name) == zeros.read_bytes(), "H31-CC ZIP member differs from the TIFF")

    writer_path = zeros.with_suffix(".json")
    writer = _json(root, str(writer_path.relative_to(root)))
    _assert(writer.get("sha256") == files["sha256"] and writer.get("bytes") == zeros.stat().st_size,
            "H31-CC shared-writer receipt differs from primary TIFF bytes")
    _assert(writer.get("submission_name") == files["name"] and writer.get("note") == files["note"],
            "H31-CC shared-writer name/note drift")
    _assert(writer.get("zip_sha256") == files["sha256_zip"] and writer.get("promoted") is False
            and writer.get("approved_for_weekly_slot") is False,
            "H31-CC shared-writer permission/ZIP receipt drift")
    _assert(len(files["note"]) <= 140 and files["note_chars"] == len(files["note"]),
            "H31-CC note length invalid")

    pin, reference = load_counterexample(root)
    control = foot & np.isfinite(reference) & (reference > 0)
    halo = distance_transform_edt(~control) <= 3
    within = int((dots & halo).sum())
    measured_overlap = within / dot_count
    final_gate = card["correlation_overlap_vs_registry"]["final"]
    _assert(abs(measured_overlap - final_gate["lattice_overlap"]) <= 1e-12,
            "H31-CC final-dot lattice overlap does not reproduce from served bytes")
    final_dot_ranks = standardized_ranks(dots[foot].astype(np.float32))
    witness_ranks = standardized_ranks(np.nan_to_num(reference[foot], nan=0.0).astype(np.float32))
    final_dot_rho_raw = (float(np.dot(final_dot_ranks, witness_ranks))
                         if final_dot_ranks is not None and witness_ranks is not None else None)
    # BLAS backends can change the last bits; this is a supplemental diagnostic,
    # never a permission threshold. Serialize canonically after the raw check.
    final_dot_rho = (round(final_dot_rho_raw, 12)
                     if final_dot_rho_raw is not None else None)
    _assert(measured_overlap > 0.70,
            "H31-CC no longer reproduces the binding literal registered-raster STOP")

    outside_halo = int((foot & ~halo).sum())
    budget = overlap_budget_preflight(footprint_pixels=int(foot.sum()),
                                      outside_halo_pixels=outside_halo,
                                      candidate_dots=dot_count)
    _assert(budget["forced_duplicate_stop"], "H31-CC stated-budget lattice bound no longer stops")
    lattice_coverage = {
        "footprint_pixels": int(foot.sum()),
        "outside_3px_halo": outside_halo,
        "coverage_fraction": float(halo[foot].mean()),
        "candidate_dots": dot_count,
        "minimum_overlap_any_same_budget": budget["minimum_overlap_fraction"],
        "evidence_class": "COMPUTED counting bound; not HOLDOUT-DTI or a score",
        "qualification": "Specific to the 37,654-dot budget; not a claim that every nonempty raster must fail.",
    }
    surface = card["correlation_overlap_vs_registry"]["surface"]
    _assert(surface.get("duplicate_submission_lane") is False,
            "H31-CC original pre-placement comparison no longer reports its pinned-peer result")

    receipt = {
        "schema_version": 1,
        "lane": "H31-CC",
        "status": "VERIFIED_NEGATIVE_RESEARCH_ONLY",
        "policy_version": POLICY_VERSION,
        "artifact": {
            "file": files["zeros"],
            "sha256": files["sha256"],
            "bytes": zeros.stat().st_size,
            "nan_file": files["nan"],
            "nan_sha256": files["sha256_nan"],
            "zip_file": files["zip"],
            "zip_sha256": files["sha256_zip"],
            "submission_name": files["name"],
            "note": files["note"],
            "positive_pixels": dot_count,
            "minimum_dot_separation_px": minimum_separation_px,
            "positive_pixels_on_catalogue": catalogue_hits,
        },
        "format_validation": {"all_finite": vz, "nan_outside": vn},
        "zip_roundtrip": True,
        "preregistration_sha256": card["preregistration_sha256"],
        "source_run_card_sha256": sha256_file(root / CARD_PATH),
        "holdout_provenance": "CITED from frozen H31-CC run card; not rerun in this integrity review",
        "registered_witness": {
            **pin["counterexample"],
            "registry_manifest_sha256": pin["manifest_sha256"],
            "registered_rasters_in_manifest": pin["registered_rasters"],
            "evidence_class": "OWNER-MIRROR",
            "qualification": "Hash-pinned repository mirror bytes; not organizer-authenticated.",
        },
        "lattice_coverage": lattice_coverage,
        "budget_preflight": budget,
        "final_dot_lattice_check": {
            "evidence_class": "COMPUTED",
            "within_3px": within,
            "candidate_dots": dot_count,
            "overlap_3px": measured_overlap,
            "binary_dot_spearman_rho": final_dot_rho,
            "literal_stop": measured_overlap > 0.70,
            "registry_coverage_complete": False,
        },
        "preplacement_surface_check": {
            "evidence_class": "CITED",
            "max_abs_spearman_vs_tested_submission_rasters": surface["max_abs_rho_submission"],
            "max_support_overlap_vs_tested_submission_rasters": surface["max_overlap_submission"],
            "lattice_overlap": surface["lattice_overlap"],
            "replayed_in_this_review": False,
            "scope": "Frozen H31-CC computation; nine focus rasters and local downloadable rasters plus registered witness, not exhaustive registry coverage",
        },
        "holdout_dti": hold,
        "leaderboard_estimate": None,
        "experiments_run_in_this_review": 0,
        "new_tif_generated_in_this_review": False,
        "submission_slots_used_in_this_review": 0,
        "ok_to_download_for_research": True,
        "ok_to_submit": False,
        "slot_approved": False,
        "organizer_acceptance_verified": False,
        "verdict": "negative",
    }
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify saved receipts without rewriting them")
    args = parser.parse_args()
    result = verify()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    for relative in (RECEIPT_PATH, PUBLIC_RECEIPT_PATH):
        path = ROOT / relative
        if args.check:
            if not path.is_file() or path.read_text() != serialized:
                raise SystemExit(f"stale or missing {relative}; run scripts/verify_h31cc_run.py")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(serialized)
    print(json.dumps({
        "status": result["status"],
        "file": result["artifact"]["file"],
        "sha256": result["artifact"]["sha256"],
        "final_lattice_overlap": result["final_dot_lattice_check"]["overlap_3px"],
        "leaderboard_estimate": result["leaderboard_estimate"],
        "ok_to_submit": result["ok_to_submit"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
