#!/usr/bin/env python3
"""One current review/permission front door; immutable scientific cards stay historical.

Re-read the actual TIFF, pinned sample and registered witness through the common
verifier. Never fit, write a TIFF, select a slot or convert a projection to a score.
--check detects stale status, permission drift and artifact tampering in CI.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]

from gemsdoe31.release_policy import overlap_budget_preflight  # noqa: E402
from gemsdoe31.submission import sha256_file  # noqa: E402
from verify_protocol_review import verify  # noqa: E402

STATUS_PATH = "registry/release_status.json"
PUBLIC_PATH = "docs/downloads/current-release-status.json"


def build(root=ROOT):
    root = Path(root)
    card = verify(root)
    selector = json.loads((root / "registry/selector_decision_20261026.json").read_text())
    review = json.loads((root / "registry/review_passes.json").read_text())
    if (selector["primary_submission"] is not None or selector["alternates"]
            or selector["promoted_lanes"] or review["release_decision"] != "DO NOT SUBMIT — literal registry STOP"):
        raise ValueError("current permission registers conflict with literal STOP")
    if review["current_release_status"] != STATUS_PATH:
        raise ValueError("review register points at a different current status")
    c = card["lattice_coverage"]
    preflight = overlap_budget_preflight(footprint_pixels=c["footprint_pixels"],
                                        outside_halo_pixels=c["outside_3px_halo"],
                                        candidate_dots=c["candidate_dots"])
    if not preflight["forced_duplicate_stop"]:
        raise ValueError("registered budget bound no longer reproduces STOP")
    # Preserve scientific evidence + exact local validator without altering its provenance.
    card.update(
        schema_version=1, review_date="2026-10-26", review_id="release-review-bf9d261d",
        review_scope="Current release audit of existing H31-X bytes. No assigned scientific method; no new experiment or TIFF.",
        current_release_status=STATUS_PATH,
        historical_scientific_card="evidence/h31x/run_card.json",
        historical_magrest_card="registry/current_run.json",
        method_lane_assigned=False, selector_authorized=False, weekly_cap_verified=False,
        budget_preflight=preflight,
        failed_or_unknown_gates=[
            "Literal any-registry uniqueness STOP (registered lattice); incomplete broad-registry coverage",
            "Pre-placement surface is cited history, not replayed from unavailable cache",
            "No single-method paragraph supplied; no new scientific lane assigned",
            "No same-run retrained global incumbent / fresh confirmation in this review",
            "Organizer-authenticated template, score receipt and current weekly cap unavailable",
            "No selector action authorized by this parallel-run protocol",
        ],
        provenance_pins={p: sha256_file(root / p) for p in (
            "evidence/h31x/run_card.json", "registry/shared_registry_57_pin.json",
            "registry/shared_registry_57_snapshot.json", "registry/data_manifest.json",
        )},
        note="RESEARCH ONLY: existing H31-X; literal registry duplicate STOP. No new TIFF, fit or weekly submission slot.",
    )
    return card


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    for rel in (STATUS_PATH, PUBLIC_PATH):
        path = ROOT / rel
        if args.check:
            if not path.is_file() or path.read_text() != text:
                raise SystemExit(f"stale or missing {rel}; run python scripts/build_release_status.py")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    print(json.dumps({k: result[k] for k in ("review_id", "verdict", "ok_to_submit", "budget_preflight")}, indent=2))


if __name__ == "__main__":
    main()
