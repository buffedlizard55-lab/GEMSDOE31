"""Final selector decision: frozen selector output amended by the owner two-stage screen.

Base document is the frozen-selector-only decision preserved at
``evidence/selector_decision_frozen_only_session15e685db.json`` (written by
``scripts/selector_h31z.py`` reusing the frozen ``selector_audit.py``
semantics; its G5 checks FINAL dots only). The owner's binding parallel-run
protocol re-issued this session (2026-10-26) additionally requires the
pre-placement SURFACE check with BOTH tests at both stages: rank-correlation
> 0.90, or > 70% of dots (surface top-K at stage 1, final dots at stage 2)
within 3 px of any registry raster, means duplicate-and-stop; unknown values
fail closed. That two-stage reading ("Reading B") was frozen before any
H31-Z result in ``knowledge/2026-10-26_h31z_preregistration.md`` section 2.

An earlier session used "Reading A" (surface check = Spearman rho only;
top-K overlap treated as a diagnostic). Under Reading A, H31-X/H31-Y are not
duplicates and the frozen primary (H31-Y) would stand. Both readings and
their outcomes are recorded in the decision; the stricter Reading B is
applied because it matches the protocol text ("use both tests at both
stages") and this session's explicit anti-copy instruction. The owner can
direct Reading A instead; the decision then flips to the frozen output.

This script never modifies the frozen engine, its audit, or any run card.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "evidence/selector_audit_20261026_session15e685db.json"
DECISION = ROOT / "registry/selector_decision_20261026.json"
FROZEN_PRESERVED = ROOT / "evidence/selector_decision_frozen_only_session15e685db.json"

CARDS = {
    "H31-X": ROOT / "registry/h31x_current_run.json",
    "H31-Y": ROOT / "registry/h31y_current_run.json",
    "H31-Z": ROOT / "registry/h31z_current_run.json",
}


def stage1(lane: str) -> dict:
    path = CARDS.get(lane)
    if path is None or not path.exists():
        return {"measured": False, "pass_": False,
                "reason": "no two-stage registry measurement on record (fail closed)"}
    corr = json.loads(path.read_text()).get("correlation_overlap_vs_registry") or {}
    topk = corr.get("discrete_max_topk_overlap_3px")
    rho = corr.get("max_abs_spearman_surface")
    if topk is None or rho is None:
        return {"measured": False, "pass_": False,
                "reason": "card lacks top-K surface overlap / surface rho (fail closed)",
                "card": str(path.relative_to(ROOT))}
    ok = topk <= 0.70 and abs(rho) <= 0.90
    return {"measured": True, "pass_": bool(ok), "topk_overlap_3px": topk,
            "max_abs_spearman_surface": rho, "card": str(path.relative_to(ROOT)),
            "reason": "" if ok else "stage-1 surface top-K exceeds the 0.70 limit"}


def main() -> int:
    audit = json.loads(AUDIT.read_text())
    if not FROZEN_PRESERVED.exists():
        shutil.copy(DECISION, FROZEN_PRESERVED)
    dec = json.loads(FROZEN_PRESERVED.read_text())  # frozen-only base, schema kept
    by_lane = {c["lane"]: c for c in audit["candidates"]}

    screen = {lane: stage1(lane) for lane in audit["promoted"]}
    conforming = [lane for lane in audit["promoted"] if screen[lane]["pass_"]]
    primary_lane = (max(conforming, key=lambda lab: by_lane[lab]["projection"])
                    if conforming else None)
    p = by_lane[primary_lane] if primary_lane else None
    pcard = json.loads(CARDS[primary_lane].read_text()) if primary_lane in CARDS else {}

    x = by_lane.get("H31-X", {})
    dec.update({
        "policy_version": "frozen-selector+owner-two-stage-20261026-15e685db",
        "amended_utc": datetime.now(timezone.utc).isoformat(),
        "session_branch": "arena/15e685db-gemsdoe31",
        "evidence_class": "COMPUTED (selector audit + run-card registry measurements)",
        "supersedes": [
            "evidence/selector_decision_superseded_9883b598.json (protocol-review denial)",
            "evidence/selector_decision_frozen_only_session15e685db.json "
            "(frozen-selector-only output; preserved verbatim, amended by this document)",
        ],
        "frozen_selector_primary": "H31-Y",
        "frozen_promoted_lanes": audit["promoted"],
        "owner_protocol_stage1_screen": screen,
        "readings_disclosure": {
            "reading_applied": "B (both uniqueness tests at both stages)",
            "reading_B": "Surface stage applies |Spearman rho| <= 0.90 AND surface top-K "
                         "<= 70% within 3 px; final-dot stage applies both again. Frozen "
                         "pre-results in the H31-Z preregistration section 2. Outcome: "
                         "H31-Y (top-K 0.9047) and H31-X (top-K 0.8631) are duplicates; "
                         "H31-Z (top-K 0.6199, final 0.6055) is the only conforming lane.",
            "reading_A": "H31-X-era interpretation: surface check = rho only, top-K is a "
                         "diagnostic. Outcome would be the frozen-selector-only decision "
                         "(primary H31-Y; H31-X demoted only by its derivative H31-Z at "
                         "70.30% final-dot overlap). The owner may direct Reading A; this "
                         "decision then reverts to the preserved frozen output.",
        },
        "h31x_demotion_disclosure": {
            "stage1": stage1("H31-X"),
            "frozen_g5_failure_peer": x.get("max_discrete_overlap_peer"),
            "frozen_g5_max_overlap": x.get("max_discrete_overlap"),
            "explanation": "H31-X fails Reading B on its own card (surface top-K 0.8631). "
                           "Its frozen-G5 final-dot failure (0.7030 vs 0.70) occurs only "
                           "against H31-Z, this session's derivative union lane; against "
                           "the registry as it stood when H31-X was selected its max was "
                           "0.6305. Recorded so the demotion is not misread as new "
                           "evidence against the incumbent geometry.",
        },
        "h31x_new_lane": {
            "lane_card_verdict": "negative",
            "selector_verdict": "negative (owner two-stage screen, Reading B)",
            "discrepancy_explanation": "H31-X lane G5 failed through the pre-placement "
                                       "top-K diagnostic (86.3% > 70%); under Reading B "
                                       "that top-K failure is disqualifying, and its "
                                       "final-dot overlap vs derivative H31-Z is 70.30%.",
        },
        "promoted_lanes": conforming,
        "primary_submission": ({
            "lane": primary_lane,
            "file": p["file"],
            "sha256": p["sha256"],
            "portal_name": pcard.get("submission_name"),
            "portal_note": pcard.get("note"),
            "portal_note_chars": pcard.get("note_chars"),
            "n_dots": p["n_dots"],
            "projection": p["projection"],
            "projection_interval": p["projection_interval"],
            "projection_is_not_a_score": True,
            "sgmc_dti": p["sgmc"]["dti"],
            "holdout_dti": p["holdout_from_card"],
        } if p else None),
        "alternates": [],
        "alternates_note": "No other lane passes selector G1--G6 under Reading B.",
        "approved_submissions": [p["file"]] if p else [],
        "ok_to_submit_primary": bool(p),
        "do_not_submit": {
            "H31-Y": "Frozen-selector primary but a duplicate under Reading B: stage-1 "
                     "surface top-K overlap 0.9047 > 0.70 (own card); weakest holdout "
                     "among promoted lanes (0.0973).",
            "H31-X": "Duplicate under Reading B: stage-1 top-K 0.8631 > 0.70; final-dot "
                     "0.7030 vs derivative H31-Z. Remains the strongest incumbent "
                     "geometry on holdout/SGMC evidence.",
            "H31-T": "No stage-1 surface measurement on record -> fail closed.",
            "H31-J": "No stage-1 surface measurement on record -> fail closed.",
            "H31-M": "No stage-1 surface measurement on record -> fail closed.",
            "all_others": "Failed at least one frozen selector gate G1--G6 (see audit).",
        },
        "conditions": [
            "Owner verifies the DrivenData weekly submission cap before uploading; this "
            "project cannot observe the account quota (0 slots spent by this project).",
            "PROJECTION (0.337) is a TPw-affine model calibrated to USER-REPORTED anchor "
            "scores. It is never a score. The owner-cited 0.3195 / 0.4413 values are "
            "unverified and mutually inconsistent; no organizer receipt exists for any file.",
            "Literal broad-registry reading: any grid-conforming dot field exceeds 70% "
            "within 3 px of the registered spacing-5 lattice (witness preserved in the "
            "H31-Z run card). This approval holds only under the disclosed discrete-peer "
            "scope; under the literal reading it reverts to STOP.",
            "H31-Z lane verdict stays negative (its stricter lane G3 required beating the "
            "JUNC incumbent). Promotion is the separate selector step (owner protocol "
            "rule 6) and does not rewrite the lane card.",
        ],
    })
    DECISION.write_text(json.dumps(dec, indent=2) + "\n")
    session = ROOT / "registry/selector_decision_20261026_session15e685db.json"
    session.write_text(json.dumps(dec, indent=2) + "\n")
    print("conforming:", conforming, "primary:", primary_lane)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
