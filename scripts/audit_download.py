#!/usr/bin/env python3
"""Read-only download audit. Exit 2 = verified denial; exit 1 = broken/stale evidence.

Never generates TIFFs, restores data, fits models, contacts DrivenData, or grants a
slot. Restore pinned small inputs with verify_current_run.py first if absent.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

from build_release_status import build as verify

ROOT = Path(__file__).resolve().parents[1]


def audit(root: Path = ROOT) -> dict:
    # Normalize tuple grid fields to their saved JSON-array representation.
    # Re-read actual TIFF/ZIP bytes, not just saved booleans.
    fresh = json.loads(json.dumps(verify(root), allow_nan=False))
    for relative in ("registry/release_status.json", "docs/downloads/current-release-status.json"):
        if json.loads((root / relative).read_text()) != fresh:
            raise ValueError(f"stale release evidence: {relative}")
    if fresh["ok_to_submit"] or fresh["slot_approved"] or fresh["verdict"] != "negative":
        raise ValueError("this research-only audit cannot authorize a submission")
    return {
        "status": "VERIFIED_DENIAL",
        "hypothesis": fresh["hypothesis"],
        "mechanism": fresh["mechanism"],
        "non_fault_mimic": fresh["non_fault_mimic"],
        "holdout_dti": fresh["holdout_dti"],
        "holdout_provenance": fresh["holdout_provenance"],
        "correlation_overlap_vs_registry": fresh["correlation_overlap_vs_registry"],
        "raster_sha256": fresh["raster_sha256"],
        "validator": fresh["validator"],
        "existing_research_file": fresh["file"],
        "submission_name": fresh["submission_name"],
        "note": fresh["note"],
        "leaderboard_estimate": None,
        "ok_to_download_for_research": True,
        "ok_to_submit": False,
        "experiments_run": 0,
        "new_tif_generated": False,
        "submission_slots_used": 0,
        "verdict": "negative",
    }


def main() -> int:
    try:
        result = audit()
    except Exception as exc:
        print(json.dumps({"status": "AUDIT_ERROR", "ok_to_submit": False,
                          "error": str(exc)}, allow_nan=False))
        return 1
    print(json.dumps(result, indent=2, allow_nan=False))
    return 2


if __name__ == "__main__":
    sys.exit(main())
