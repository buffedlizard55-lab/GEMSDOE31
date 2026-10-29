"""Fail-closed guard for legacy research packaging, not a slot selector.

The canonical release register is the authorization front door. Frozen historical
cards, caller-supplied gate summaries and local format passes cannot override it.
No files are written and no network is accessed by this check.
"""
from __future__ import annotations

import json
from pathlib import Path

from gemsdoe31.release_policy import POLICY_VERSION, uniqueness_gate

ROOT = Path(__file__).resolve().parents[2]


def require_research_packaging(root: Path = ROOT) -> None:
    """Deny packaging without an assigned lane and complete two-stage uniqueness.

    This is deliberately independent of efficacy: a negative scientific result
    may be packaged for research after uniqueness passes. It never grants upload
    permission. A future authorized run must update the canonical evidence first;
    there is no command-line or environment-variable bypass.
    """
    try:
        status = json.loads((Path(root) / "registry/release_status.json").read_text())
    except (OSError, ValueError) as exc:
        raise ValueError("Research packaging blocked: canonical release status missing or invalid") from exc
    if not isinstance(status, dict):
        raise ValueError("Research packaging blocked: canonical release status must be an object")
    if status.get("policy_version") != POLICY_VERSION:
        raise ValueError("Research packaging blocked: unrecognized release policy")
    if status.get("method_lane_assigned") is not True:
        raise ValueError("Research packaging blocked: no assigned method lane; no new TIFF after STOP")
    stages = status.get("correlation_overlap_vs_registry")
    if not isinstance(stages, dict) or any(
        not isinstance(stages.get(stage), dict) for stage in ("surface", "final")
    ):
        raise ValueError("Research packaging blocked: two-stage uniqueness evidence missing")
    gate = uniqueness_gate(stages)
    if not gate["pass_"]:
        raise ValueError("Research packaging blocked: " + "; ".join(gate["failures"]))
    recorded = status.get("uniqueness_gate")
    if not isinstance(recorded, dict) or recorded != gate:
        raise ValueError("Research packaging blocked: recorded uniqueness decision is inconsistent")


def research_only_permissions() -> dict:
    """Writer receipts describe downloadable research, never submission approval."""
    return {
        "ok_to_download_for_research": True,
        "ok_to_upload_format_only": True,
        "ok_to_download_and_submit": False,
        "ok_to_submit": False,
        "slot_approved": False,
        "organizer_acceptance_verified": False,
        "permission_source": "registry/release_status.json; separate selector required for upload",
    }
