"""Binding release policy for the owner's literal parallel-run protocol.

A research download, a passing file format, and a slot approval are different.
Missing evidence fails closed. A projection cannot waive a failed gate.
"""
from __future__ import annotations

import math

POLICY_VERSION = "literal-registry-20261026-9883b598"


def uniqueness_gate(stages: dict) -> dict:
    """Require both stages, complete registry coverage and finite diagnostics.

One witnessed violation is enough for STOP even when coverage is incomplete.
Undefined rank correlation is not evidence of uniqueness.
"""
    failures = []
    duplicate = False
    if not isinstance(stages, dict):
        stages = {}
    for name in ("surface", "final"):
        stage = stages.get(name)
        if not isinstance(stage, dict):
            stage = {}
        for key, limit in (("max_abs_rho", .90), ("max_overlap", .70)):
            value = stage.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                failures.append(f"{name}.{key}: missing/undefined")
            elif value < 0 or value > 1:
                failures.append(f"{name}.{key}: invalid")
            elif value > limit:
                duplicate = True
                failures.append(f"{name}.{key}: duplicate STOP")
        if stage.get("coverage_complete") is not True:
            failures.append(f"{name}: registry coverage incomplete")
    return {"pass_": not failures, "duplicate": duplicate, "failures": failures}


def selector_permission(*, uniqueness: dict, scientific_gates: dict,
                        selector_authorized: bool, weekly_cap_verified: bool) -> bool:
    """No soft/projection override and no truthy-string approvals."""
    required = {"format", "canary", "same_run_best", "fresh_confirmation", "discovery_proxy", "provenance"}
    if not isinstance(uniqueness, dict) or not isinstance(scientific_gates, dict):
        return False
    return (uniqueness.get("pass_") is True and uniqueness.get("duplicate") is False
            and uniqueness.get("failures") == []
            and required <= scientific_gates.keys()
            and all(v is True for v in scientific_gates.values())
            and selector_authorized is True and weekly_cap_verified is True)


def overlap_budget_preflight(*, footprint_pixels: int, outside_halo_pixels: int,
                             candidate_dots: int) -> dict:
    """A necessary-only feasibility check for the literal >70% overlap STOP.

    With U cells outside a registry raster's 3px halo, at least max(0,N-U)
    of N distinct candidate cells must hit that halo. No placement, thinning,
    model fit or density exemption is performed. A non-forced STOP is NOT a
    uniqueness pass: all ordinary surface/final comparisons are still needed.
    Integer arithmetic preserves the strict >70% boundary exactly.
    """
    for name, value in (("footprint_pixels", footprint_pixels),
                        ("outside_halo_pixels", outside_halo_pixels),
                        ("candidate_dots", candidate_dots)):
        if type(value) is not int or value < 0:
            raise ValueError(f"{name} must be a nonnegative integer")
    if footprint_pixels == 0 or max(outside_halo_pixels, candidate_dots) > footprint_pixels:
        raise ValueError("invalid footprint or counts exceeding footprint")
    minimum_hits = max(0, candidate_dots - outside_halo_pixels)
    return {
        "evidence_class": "COMPUTED counting bound; not HOLDOUT-DTI or a score",
        "footprint_pixels": footprint_pixels,
        "outside_halo_pixels": outside_halo_pixels,
        "candidate_dots": candidate_dots,
        "minimum_overlap_pixels": minimum_hits,
        "minimum_overlap_fraction": minimum_hits / candidate_dots if candidate_dots else None,
        "forced_duplicate_stop": candidate_dots > 0 and 10 * minimum_hits > 7 * candidate_dots,
        "empty_candidate": candidate_dots == 0,
        "uniqueness_pass": False,
        "qualification": "Necessary bound only; does not prove copying or rule out every nonempty raster. No registry exemptions.",
    }
