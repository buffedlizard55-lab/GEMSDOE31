"""Mechanical research and submission gates. No portal interaction or selection."""
from __future__ import annotations


REQUIRED_PROMOTION_GATES = (
    "format", "leakage_canary", "literal_registry", "paired_metric_improvement",
    "three_quadrant_wins", "current_best_reproduced", "fresh_confirmation",
    "owner_assigned_lane", "organizer_template_authenticated",
)


def make_decision(card: dict, holdout: dict, surface_audit: dict, final_audit: dict,
                  witness: dict, fold_results: dict) -> dict:
    """Derive an explicit negative/promote-to-selector decision from artifacts.

    Lack of evidence is false, not a waiver. A research promotion never selects
    a weekly slot. An independently recorded selector authorization and current
    cap would still be required before any file could be marked submit-approved.
    """
    paired = holdout.get("paired_differences", {}).get("amplitude_control", {})
    ci = paired.get("ci95", [])
    rows = fold_results.get("per_fold_results", [])
    by_fold = {}
    for row in rows:
        if row["arm"] in ("TGJ31", "amplitude_control"):
            by_fold.setdefault(row["fold"], {})[row["arm"]] = row["dti"]
    wins = sum(r.get("TGJ31", -1) > r.get("amplitude_control", 2) for r in by_fold.values())
    gates = {
        "format": bool(card["validator_output"].get("shared_all_checks_passed")
                       and card["validator_output"].get("independent_format_passed")),
        "leakage_canary": card.get("leakage_canary", {}).get("passed") is True,
        "literal_registry": (surface_audit.get("unique") is True and final_audit.get("unique") is True
                             and not witness.get("universal_overlap_blocker", True)
                             and card.get("correlation_overlap_vs_registry", {}).get("extended_inventory_complete") is True),
        "paired_metric_improvement": (len(ci) == 2 and ci[0] > 0 and paired.get("delta", 0) > 0),
        "three_quadrant_wins": len(by_fold) == 4 and wins >= 3,
        "current_best_reproduced": holdout.get("current_best_comparable_incumbent_reproduced") is True,
        "fresh_confirmation": holdout.get("fresh_confirmation") is True,
        "owner_assigned_lane": False,  # no assigned method paragraph in the recorded request
        "organizer_template_authenticated": False,  # hash-matching owner mirror only
    }
    research_pass = all(gates.get(name) is True for name in REQUIRED_PROMOTION_GATES)
    return {
        "schema_version": 1, "evidence_class": "AUTOMATED-DECISION", "hypothesis": card["hypothesis"],
        "gates": gates, "failed_gates": [n for n in REQUIRED_PROMOTION_GATES if not gates[n]],
        "paired_metric_result": paired, "quadrants_won_against_amplitude_control": wins,
        "quadrants_evaluated": len(by_fold),
        "verdict": "promote" if research_pass else "negative",
        "promotion_meaning": "Eligible for a separate selector only; never an automatic submission",
        "safe_to_download": True, "safe_to_submit": False, "slot_approved": False,
        "selector_authorization": None, "current_weekly_cap_verified": False,
        "organizer_outside_encoding_verified": False,
        "local_format_policy": "Unchanged shared writer: finite everywhere, explicit zero outside. Historical null/NaN convention is unresolved; local PASS is not portal conformity.",
        "submission_slots_used": 0, "organizer_confirmed_score": None,
        "reason": "Every missing or failed gate blocks submission; negative findings and a format pass are separate deliverables.",
    }
