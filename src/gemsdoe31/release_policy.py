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
    for name in ("surface", "final"):
        stage = stages.get(name, {})
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
    return (uniqueness.get("pass_") is True and uniqueness.get("duplicate") is False
            and required <= scientific_gates.keys()
            and all(v is True for v in scientific_gates.values())
            and selector_authorized is True and weekly_cap_verified is True)
