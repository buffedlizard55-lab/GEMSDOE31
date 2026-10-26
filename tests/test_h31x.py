"""H31-X lane receipts: consistency of run card, selector decision, files and disclosure."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "evidence/h31x/run_card.json"


@pytest.fixture(scope="module")
def card():
    if not CARD.is_file():
        pytest.skip("H31-X run card absent")
    return json.loads(CARD.read_text())


def test_card_gates_and_verdict_consistent(card):
    g = card["gates"]
    gate_keys = [k for k in g if k.startswith("G")]
    assert set(gate_keys) == {"G1_format", "G2_canary", "G3_holdout_efficacy", "G4_sgmc_discovery",
                              "G5_uniqueness_discrete", "G6_projection_ge_02778"}
    promote = all(g[k] for k in gate_keys)
    assert (card["verdict"] == "promote") == promote
    assert card["ok_to_submit"] == promote and card["slot_approved"] == promote
    assert card["submission_slots_used"] == 0
    assert 1 <= card["note_chars"] <= 140 and len(card["note"]) == card["note_chars"]


def test_card_numbers_are_labelled(card):
    assert card["holdout_dti"]["evidence_class"] == "HOLDOUT-DTI"
    assert card["holdout_dti"]["evaluator_version"] == "gems57-pooled-hide-v2"
    assert card["projection"]["evidence_class"].startswith("PROJECTION")
    assert "not hidden truth" in card["sgmc_proxy"]["evidence_class"]
    sc = card["holdout_dti"]["screen_final_surface"]
    assert sc["withheld_positive_pixels"] == 60988 and sc["ci95"][0] <= sc["dti"] <= sc["ci95"][1]


def test_files_and_hashes(card):
    from gemsdoe31.submission import sha256_file
    z = ROOT / card["files"]["zeros"]
    n = ROOT / card["files"]["nan"]
    assert z.is_file() and n.is_file() and (ROOT / card["files"]["zip"]).is_file()
    assert sha256_file(z) == card["raster_sha256"]
    assert sha256_file(n) == card["raster_sha256_nan"]
    assert card["validator"]["zeros"]["ok"] and card["validator"]["nan"]["ok"]
    assert card["validator"]["zeros"]["hard_failures"] == []
    assert card["validator"]["organizer_acceptance_verified"] is False


def test_lane_vs_selector_disclosure(card):
    dec_p = ROOT / "registry/selector_decision_20261026.json"
    if not dec_p.is_file():
        pytest.skip("selector decision absent")
    dec = json.loads(dec_p.read_text())
    x = dec.get("h31x_new_lane")
    assert x is not None
    assert x["lane_card_verdict"] == card["verdict"]
    u = card["correlation_overlap_vs_registry"]
    # owner's duplicate rule on the submitted dots and the surface rank correlation
    owner_rule_unique = (u["discrete_max_final_overlap_3px"] <= 0.70
                         and u["max_abs_spearman_surface"] <= 0.90 and u["max_abs_spearman_dots"] <= 0.90)
    assert owner_rule_unique
    if card["gates"]["G5_uniqueness_discrete"] is False:
        # the stricter lane gate can only fail through the pre-placement top-K diagnostic
        assert u["discrete_max_topk_overlap_3px"] > 0.70
        assert "top-K" in x["discrepancy_explanation"]
    if x["selector_verdict"] == "promote":
        assert "H31-X" in dec["promoted_lanes"]
        prim = dec["primary_submission"]
        if prim["lane"] == "H31-X":
            assert prim["sha256"] == card["raster_sha256"]
            assert prim["portal_name"] == card["submission_name"]
            assert prim["portal_note"] == card["note"]


def test_preregistration_frozen_text_exists(card):
    pre = ROOT / card["preregistration"]
    assert pre.is_file()
    txt = pre.read_text()
    for token in ("G1 format", "G2 canary", "G3 efficacy", "G4 discovery proxy", "G5 uniqueness", "G6 projection",
                  "EXP-1", "EXP-2", "EXP-3", "X1"):
        assert token in txt
