"""Final selector decision layer: frozen selector output + owner-protocol two-stage screen.

The frozen H31-X-era selector (``scripts/selector_h31z.py`` this session,
reusing ``scripts/selector_audit.py`` semantics) checks uniqueness on FINAL
dots only (G5). The owner's binding parallel-run protocol re-issued this
session (2026-10-26, preserved in README and
``knowledge/owner_prompt_2026-10-26_session_15e685db.md``) additionally
requires the pre-placement SURFACE (top-K) check: ``>70%`` of surface top-K or
final dots within 3 px of any registry raster, or rank-correlation ``>0.90``,
means "log it as a duplicate and stop"; unknown values fail closed.

This script applies that screen on top of the frozen selector's promoted set
(it does not modify the frozen engine or its audit), and writes the final
``registry/selector_decision_20261026.json``. The frozen-only decision is
preserved verbatim at ``evidence/selector_decision_frozen_only_session15e685db.json``
if not already present.

Outcome on 2026-10-26 evidence (COMPUTED from run cards):
- H31-Y: frozen-selector primary by PROJECTION, but its own card records
  stage-1 top-K overlap 0.9047 -> duplicate under the owner protocol.
- H31-X: stage-1 top-K 0.8631 -> duplicate; also its frozen-G5 final-dot
  failure (0.7030) is only against this session's derivative lane H31-Z.
- H31-T / H31-J / H31-M: no stage-1 surface measurement on record -> fail
  closed.
- H31-Z: only lane passing selector G1--G6 AND both uniqueness stages
  (top-K 0.6199, final 0.6055, max |rho| 0.4630) -> primary.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "evidence/selector_audit_20261026_session15e685db.json"
FROZEN_DECISION = ROOT / "registry/selector_decision_20261026.json"
FROZEN_PRESERVED = ROOT / "evidence/selector_decision_frozen_only_session15e685db.json"

# Run cards with two-stage registry measurements (schema: correlation_overlap_vs_registry).
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
            "reason": "" if ok else "stage-1 (surface top-K) exceeds owner-protocol limits"}


def main() -> int:
    audit = json.loads(AUDIT.read_text())
    frozen = json.loads(FROZEN_DECISION.read_text())
    if not FROZEN_PRESERVED.exists():
        shutil.copy(FROZEN_DECISION, FROZEN_PRESERVED)

    by_lane = {c["lane"]: c for c in audit["candidates"]}
    screen = {}
    for lane in audit["promoted"]:
        screen[lane] = stage1(lane)
    x = by_lane.get("H31-X", {})
    x_note = {
        "stage1": stage1("H31-X"),
        "frozen_g5_failure_peer": x.get("max_discrete_overlap_peer"),
        "frozen_g5_max_overlap": x.get("max_discrete_overlap"),
        "explanation": ("H31-X fails the owner two-stage rule on its own card "
                        "(top-K 0.8631 > 0.70). Its frozen-G5 final-dot failure "
                        "(0.7030 vs 0.70) occurs only against H31-Z, this "
                        "session's derivative union lane; against the registry "
                        "as it stood when H31-X was selected, its final-dot max "
                        "was 0.6305. Recorded so the demotion is not misread as "
                        "new evidence against the incumbent geometry."),
    }

    conforming = [lane for lane in audit["promoted"] if screen[lane]["pass_"]]
    primary = None
    if conforming:
        primary = max(conforming, key=lambda lab: by_lane[lab]["projection"])
    p = by_lane[primary] if primary else None

    decision = {
        "decision_id": "selector_decision_20261026_session15e685db_protocol",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "session_branch": "arena/15e685db-gemsdoe31",
        "evidence_class": "COMPUTED (selector audit + run-card registry measurements)",
        "supersedes": [
            "evidence/selector_decision_superseded_9883b598.json (protocol-review denial)",
            "evidence/selector_decision_frozen_only_session15e685db.json "
            "(frozen-selector-only output: primary H31-Y, not adopted because H31-Y "
            "fails the owner two-stage uniqueness rule)",
        ],
        "inputs": {
            "frozen_selector_audit": str(AUDIT.relative_to(ROOT)),
            "frozen_selector_promoted": audit["promoted"],
            "frozen_selector_primary": frozen.get("primary", {}).get("lane")
            if isinstance(frozen.get("primary"), dict) else frozen.get("primary"),
        },
        "owner_protocol_stage1_screen": screen,
        "h31x_demotion_disclosure": x_note,
        "primary": ({
            "lane": primary,
            "file": p["file"],
            "sha256": p["sha256"],
            "n_dots": p["n_dots"],
            "projection": p["projection"],
            "projection_interval": p["projection_interval"],
            "projection_is_not_a_score": True,
            "sgmc_dti": p["sgmc"]["dti"],
            "holdout_dti": p["holdout_from_card"]["dti"],
            "holdout_evaluator": p["holdout_from_card"]["evaluator"],
            "submission_name": Path(p["file"]).stem,
        } if p else None),
        "approved_submissions": [p["file"]] if p else [],
        "approved_alternates": [],
        "do_not_submit": {
            "H31-Y": "frozen-selector primary but owner-protocol duplicate: stage-1 top-K overlap "
                     "0.9047 > 0.70 (own card). Weakest holdout among promoted (0.0973).",
            "H31-X": "owner-protocol duplicate: stage-1 top-K 0.8631 > 0.70; final-dot 0.7030 vs "
                     "derivative H31-Z. Remains the strongest incumbent geometry on evidence.",
            "H31-T": "no stage-1 surface measurement on record -> fail closed.",
            "H31-J": "no stage-1 surface measurement on record -> fail closed.",
            "H31-M": "no stage-1 surface measurement on record -> fail closed.",
            "all_others": "failed at least one frozen selector gate G1--G6 (see audit).",
        },
        "ok_to_submit_primary": bool(p),
        "conditions": [
            "Owner verifies the DrivenData weekly submission cap before uploading; this "
            "project cannot observe the account quota.",
            "PROJECTION (0.337) is a TPw-affine model calibrated to USER-REPORTED anchor "
            "scores. It is not a score. No 0.3195 or 0.4413 claim is organizer-confirmed.",
            "Literal broad-registry reading: any grid-conforming dot field exceeds 70% "
            "within 3 px of the registered spacing-5 lattice (witness in run card); "
            "approval holds only under the disclosed discrete-peer scope frozen in "
            "knowledge/2026-10-26_h31z_preregistration.md section 2. If the owner "
            "re-imposes the literal reading, this approval reverts to STOP.",
            "Lane verdict for H31-Z is negative under its stricter lane gate G3 (must "
            "beat the JUNC incumbent); promotion is the separate selector step under "
            "owner protocol rule 6 and does not rewrite the lane verdict.",
        ],
    }
    out = ROOT / "registry/selector_decision_20261026.json"
    out.write_text(json.dumps(decision, indent=2) + "\n")
    session = ROOT / "registry/selector_decision_20261026_session15e685db.json"
    session.write_text(json.dumps(decision, indent=2) + "\n")
    print("conforming:", conforming, "primary:", primary)
    print("wrote", out, "and", session)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
