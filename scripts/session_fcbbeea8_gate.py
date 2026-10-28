#!/usr/bin/env python3
"""Session fcbbeea8 (2026-10-28): re-derive the literal registry-lattice gate; write a negative run card.

No raster is generated, no dots are placed, no experiment is fit and no slot is used. The script re-runs
the repository's existing counting verifier on the pinned H31-X bytes (its registered-lattice halo count
is independent of the dot placement) and applies the same count-only bound to any raster with N dots:

    min_overlap(N) = (N - outside_3px_halo) / N

It also records the threshold N at which that bound alone forces the 70% STOP, and applies the bound to
the highest user-reported file's dot count (GEMSDOE32 H33-2-B2, 37,654 positives per its forensic card).
Run after `python scripts/verify_current_run.py --restore-small-inputs`.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts")]

import verify_protocol_review as vpr  # noqa: E402

GATE = 0.70
OUT = ROOT / "evidence/review_fcbbeea8/run_card.json"


def main() -> int:
    result = vpr.verify(ROOT)
    cov = result["lattice_coverage"]
    halo_outside = int(cov["outside_3px_halo"])
    footprint = int(cov["footprint_pixels"])
    budget = int(cov["candidate_dots"])

    def min_overlap(n: int) -> float:
        return max(0.0, (n - halo_outside) / n)

    threshold_n = math.ceil(halo_outside / (1 - GATE))
    h33_forensics = json.loads((ROOT / "evidence/h33_forensics_20261025.json").read_text())
    h33_n = int(h33_forensics["h33_positive_pixels"])
    card = {
        "session": "fcbbeea8",
        "date_utc": "2026-10-28",
        "branch": "arena/fcbbeea8-gemsdoe31",
        "experiments_run": 0,
        "new_tif_generated": False,
        "dots_placed": 0,
        "slot_approved": False,
        "submission_slots_used": 0,
        "ok_to_submit": False,
        "new_file_download_for_research_this_session": False,
        "existing_research_only_file": "docs/downloads/gems31-h31cc-basement-step-37654d-20261028-zeros.tif (from session bb6d6287; DO NOT SUBMIT)",
        "verdict": "negative",
        "stop_reason": "Literal registry-lattice rule: a 37,654-dot raster has at least 82.34% of dots within 3 px "
        "of the registered spacing-5 lattice (counting bound, > 70% gate). Stop before placement.",
        "pre_placement_count_bound": {
            "evidence_class": "COMPUTED",
            "footprint_pixels": footprint,
            "outside_3px_halo": halo_outside,
            "candidate_dots": budget,
            "min_overlap_at_candidate_dots": cov["minimum_overlap_any_same_budget"],
            "gate_overlap": GATE,
            "forced_stop_at_candidate_dots": min_overlap(budget) > GATE,
            "min_dots_for_forced_stop": threshold_n,
            "below_threshold_bound_does_not_force_stop": True,
            "caveat": "A counting bound against one registered lattice, not a proof about every raster. "
            "Below min_dots_for_forced_stop the count alone forces nothing. Exploiting that is a density "
            "change the repository forbids; flagged for owner review, not acted on.",
        },
        "same_bound_applied_to_highest_user_reported_file": {
            "evidence_class": "COMPUTED from RASTER-MEASUREMENT dot count",
            "file": h33_forensics["h33_file"],
            "positive_pixels": h33_n,
            "min_overlap_by_count": round(min_overlap(h33_n), 6),
            "forced_stop_by_same_rule": min_overlap(h33_n) > GATE,
            "note": "The literal rule would stop the highest user-reported file too. Owner must decide which rule governs.",
        },
        "user_reported_scores_not_verified": ["0.2778 (GEMSDOE32 H33-2-B2)", "0.3195", "0.4413"],
        "estimated_leaderboard_score_for_new_file": "unavailable",
        "scope": "Count-bound verification only. Holdout DTI not recomputed in this session; cited HOLDOUT-DTI "
        "figures belong to their original run cards.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(card, indent=2) + "\n")
    print(json.dumps(card["pre_placement_count_bound"], indent=2))
    print(json.dumps(card["same_bound_applied_to_highest_user_reported_file"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
