#!/usr/bin/env python3
"""Build the current fail-closed release status from the latest research artifact.

The scientific HOLDOUT-DTI and pre-placement audit remain cited from the frozen
H31-CC card; this builder independently re-reads its GeoTIFFs/ZIP and reproduces
the final-dot overlap against one hash-pinned registered control. One literal
counterexample is enough for STOP; this is not an exhaustive registry scan.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]

from gemsdoe31.release_policy import POLICY_VERSION, uniqueness_gate  # noqa: E402
from gemsdoe31.submission import sha256_file  # noqa: E402
from verify_h31cc_run import verify as verify_h31cc  # noqa: E402

STATUS_PATH = "registry/release_status.json"
PUBLIC_PATH = "docs/downloads/current-release-status.json"


def verify(root=ROOT):
    """Return a normalized, byte-backed negative status for the existing H31-CC file."""
    root = Path(root)
    receipt = verify_h31cc(root)
    card = json.loads((root / "evidence/h31cc/run_card.json").read_text())
    surface = receipt["preplacement_surface_check"]
    final_dots = receipt["final_dot_lattice_check"]
    lattice = receipt["lattice_coverage"]
    stages = {
        "surface": {
            "max_abs_rho": surface["max_abs_spearman_vs_tested_submission_rasters"],
            "max_overlap": surface["max_support_overlap_vs_tested_submission_rasters"],
            "coverage_complete": False,
        },
        "final": {
            "max_abs_rho": (abs(final_dots["binary_dot_spearman_rho"])
                            if final_dots["binary_dot_spearman_rho"] is not None else None),
            "max_overlap": final_dots["overlap_3px"],
            "coverage_complete": False,
        },
    }
    gate = uniqueness_gate(stages)
    if not gate["duplicate"]:
        raise ValueError("expected final-dot registered-control STOP was not reproduced")

    return {
        "policy_version": POLICY_VERSION,
        "hypothesis": card["hypothesis"],
        "mechanism": card["mechanism"],
        "non_fault_mimic": card["named_non_fault_mimic"],
        "review_scope": (
            "Current release integrity audit of the existing H31-CC research artifact. "
            "No new experiment, TIFF, slot selection, or upload. HOLDOUT-DTI and the "
            "pre-placement surface metrics are cited from the frozen H31-CC card; only "
            "the served TIFF/ZIP and one registered witness are re-read here."
        ),
        "experiments_run": 0,
        "new_tif_generated": False,
        "holdout_dti": receipt["holdout_dti"],
        "holdout_provenance": receipt["holdout_provenance"],
        "source_run_card_sha256": receipt["source_run_card_sha256"],
        "correlation_overlap_vs_registry": {
            "surface": {
                "max_abs_rho": stages["surface"]["max_abs_rho"],
                "max_overlap": stages["surface"]["max_overlap"],
                "lattice_overlap": surface["lattice_overlap"],
                "coverage_complete": False,
                "provenance": "CITED from frozen H31-CC card; not replayed in this integrity review",
            },
            "final": {
                "max_abs_rho": stages["final"]["max_abs_rho"],
                "max_overlap": stages["final"]["max_overlap"],
                "lattice_overlap": final_dots["overlap_3px"],
                "lattice_dot_spearman_rho": final_dots["binary_dot_spearman_rho"],
                "coverage_complete": False,
                "provenance": (
                    "COMPUTED from final TIFF dots versus one hash-pinned registered "
                    "owner-mirror control; not an exhaustive registry pass"
                ),
            },
        },
        "uniqueness_gate": gate,
        "registered_witness": receipt["registered_witness"],
        "lattice_coverage": lattice,
        "budget_preflight": receipt["budget_preflight"],
        "raster_sha256": receipt["artifact"]["sha256"],
        "file": receipt["artifact"]["file"],
        "validator": receipt["format_validation"]["all_finite"],
        "validator_nan": receipt["format_validation"]["nan_outside"],
        "verification_receipt": "evidence/h31cc/verification_receipt.json",
        "verification_receipt_sha256": sha256_file(root / "evidence/h31cc/verification_receipt.json"),
        "submission_name": receipt["artifact"]["submission_name"],
        "note": receipt["artifact"]["note"],
        "ok_to_download_for_research": True,
        "ok_to_submit": False,
        "slot_approved": False,
        "submission_slots_used": 0,
        "leaderboard_estimate": None,
        "estimate_reason": "No organizer score receipt or calibrated cross-family forecast exists.",
        "verdict": "negative",
        "method_lane_assigned": False,
        "selector_authorized": False,
        "weekly_cap_verified": False,
        "experiments_run_in_this_review": 0,
        "new_tif_generated_in_this_review": False,
    }


def build(root=ROOT):
    root = Path(root)
    card = verify(root)
    # BLAS thread count/backend can change the last bits of a dot product.
    # The verifier has already applied the gate to unrounded diagnostics.
    # Canonicalize only the displayed correlation, never thresholds/permissions.
    final = card["correlation_overlap_vs_registry"]["final"]
    if final["max_abs_rho"] is not None:
        final["max_abs_rho"] = round(final["max_abs_rho"], 12)
        final["lattice_dot_spearman_rho"] = round(final["lattice_dot_spearman_rho"], 12)
    card["diagnostic_serialization"] = (
        "Displayed rank correlations rounded to 12 decimals only after raw-value gate evaluation; "
        "no threshold or permission is rounded."
    )

    selector = json.loads((root / "registry/selector_decision_20261026.json").read_text())
    review = json.loads((root / "registry/review_passes.json").read_text())
    if (selector["primary_submission"] is not None or selector["alternates"]
            or selector["promoted_lanes"] or review["release_decision"] != "DO NOT SUBMIT — literal registry STOP"):
        raise ValueError("current permission registers conflict with literal STOP")
    if review["current_release_status"] != STATUS_PATH:
        raise ValueError("review register points at a different current status")
    if not str(review.get("current_scientific_run", "")).startswith("evidence/h31cc/run_card.json"):
        raise ValueError("review register does not identify H31-CC as the latest scientific artifact")

    card.update(
        schema_version=1,
        review_date="2026-10-28",
        review_id="release-review-arena-41e3ba3f",
        current_release_status=STATUS_PATH,
        historical_scientific_card="evidence/h31cc/run_card.json",
        historical_magrest_card="registry/current_run.json",
        method_lane_assigned=False,
        selector_authorized=False,
        weekly_cap_verified=False,
        failed_or_unknown_gates=[
            "Literal any-registry uniqueness STOP: the final H31-CC dots overlap the pinned spacing-5 witness by 99.612% (>70%).",
            "The pre-placement surface comparison is cited from the frozen card, not replayed in this integrity review.",
            "Only one hash-pinned registered owner-mirror witness was rechecked; no exhaustive 695-raster pass is claimed.",
            "HOLDOUT-DTI is a cited prior result; its paired interval versus NULL crosses zero and no confirmation ran.",
            "The active prompt supplies no single-method paragraph; no new lane or experiment was authorized.",
            "Organizer-authenticated template/score receipts, current weekly cap, and selector approval are unavailable.",
        ],
        provenance_pins={p: sha256_file(root / p) for p in (
            "evidence/h31cc/run_card.json",
            "evidence/h31cc/verification_receipt.json",
            "registry/shared_registry_57_pin.json",
            "registry/shared_registry_57_snapshot.json",
            "registry/data_manifest.json",
        )},
        note="RESEARCH ONLY: H31-CC; negative screen and literal lattice STOP. No new experiment, TIFF, or weekly slot in this review.",
    )
    return card


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    for relative in (STATUS_PATH, PUBLIC_PATH):
        path = ROOT / relative
        if args.check:
            if not path.is_file() or path.read_text() != text:
                raise SystemExit(f"stale or missing {relative}; run python scripts/build_release_status.py")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    print(json.dumps({
        key: result[key]
        for key in ("review_id", "verdict", "ok_to_submit", "correlation_overlap_vs_registry", "budget_preflight")
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
