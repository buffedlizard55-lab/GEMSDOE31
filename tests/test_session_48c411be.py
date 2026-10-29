"""Regression tests for the 2026-10-29 GEMSDOE32 forensic and uniqueness-bound audit.

These tests read committed evidence only (no network). They fail if the register, the run card or the
site addendum drift from the verified JSON. Scores are USER-REPORTED and are never recomputed here.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

FORENSICS = ROOT / "evidence/review_48c411be/gemsdoe32_forensics.json"
LATTICE = ROOT / "evidence/review_48c411be/lattice_bound.json"
CARD = ROOT / "evidence/review_48c411be/run_card.json"
ADDENDUM = ROOT / "registry/session_48c411be_addendum.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_gemsdoe32_dot_chain_is_nested_and_counts_match():
    f = _load(FORENSICS)
    assert f["dot_counts"] == {"D28": 44090, "H27_4": 40199, "H33_2_B2": 37654}
    assert f["chain"]["B_subset_of_H27"] is True
    assert f["chain"]["H27_subset_of_D28"] is True
    assert f["chain"]["removed_D28_to_B"] == 6436
    assert f["chain"]["removed_D28_to_H27"] == 3891
    assert f["chain"]["removed_H27_to_B"] == 2545


def test_two_px_claim_holds_exactly_and_no_dot_lies_on_catalogue():
    f = _load(FORENSICS)
    assert f["claim_check"]["claim_holds_exactly"] is True
    assert f["claim_check"]["removed_dots_within_2px_of_catalogue"] == f["claim_check"]["removed_dots_total"] == 6436
    assert f["dots_on_catalogue"]["B_dots_on_catalogue"] == 0
    assert f["kept_distance_to_catalogue_px_B"]["min"] > 2.0


def test_radius_ladder_reproduces_repo_files_and_3px_step_is_duplicate():
    f = _load(FORENSICS)
    ladder = f["radius_ladder_D28"]
    assert ladder["1.0"]["equals_H27_4_file"] is True
    assert ladder["2.0"]["equals_H33_2_B2_file"] is True
    assert ladder["1.5"]["equals_H27_4_file"] is False and ladder["1.5"]["equals_H33_2_B2_file"] is False
    v3 = f["radius_3px_variant_of_GEMSDOE32"]
    assert v3["dots_remaining"] == 35483
    assert v3["share_within_3px_of_GEMSDOE32"] > 0.99
    assert v3["duplicate_by_70pct_rule"] is True


def test_gemsdoe32_variants_identical_inside_footprint_and_zeros_outside():
    v = _load(FORENSICS)["variant_check"]
    assert v["identical_inside_footprint"] is True
    assert v["footprint_pixels"] == 5167373
    assert v["zeros_variant_nan_pixels"] == 0
    assert v["zeros_variant_outside_footprint_values"] == [0.0]
    assert v["nan_variant_outside_footprint_is_nan"] is True


def test_lattice_bound_recomputed_checks_all_match_registry():
    lat = _load(LATTICE)
    assert all(lat["checks_against_registry"].values())
    assert lat["pixels_uncovered_by_radius"] == 6649
    assert abs(lat["forced_minimum_overlap_for_budget"] - 0.8234184947150369) < 1e-12


def test_run_card_is_negative_and_never_approves_submission():
    c = _load(CARD)
    assert c["verdict"] == "negative"
    assert c["ok_to_submit"] is False
    assert c["experiments_run"] == 0
    assert c["raster_sha256"] is None and c["submission_name"] is None
    assert c["holdout_dti"]["value"] is None
    assert c["leaderboard_estimate"]["value"] is None
    assert 0 < c["note_chars"] <= 140
    assert len(c["note"]) == c["note_chars"]


def test_addendum_and_run_card_are_current_with_their_inputs():
    import build_session_addendum as b
    assert json.loads(ADDENDUM.read_text(encoding="utf-8")) == json.loads(json.dumps(b.build()))
    assert _load(CARD) == json.loads(json.dumps(b.run_card(b.build())))


def test_site_addendum_renders_decision_and_no_stray_escapes():
    import build_site as site
    html = site.addendum_panel()
    assert "Session 48c411be addendum" in html
    assert "Submission permission: none (DO NOT SUBMIT)" in html
    assert "\\" not in html


def test_irregularities_register_has_48c4_entries():
    items = _load(ROOT / "registry/irregularities.json")["items"]
    ids = {i["id"] for i in items}
    assert {f"IR-48C4-0{n}" for n in range(1, 10)} <= ids
