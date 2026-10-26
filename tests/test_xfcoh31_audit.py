"""Regression checks for the XFCOH31 exact-file STOP and its scope correction."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text())


def test_xfcoh31_shared_registry_receipt_is_a_literal_stop_not_an_exhaustive_scan() -> None:
    audit = load_json("evidence/xfcoh31_registry_stop_audit.json")
    assert audit["candidate"]["sha256"] == "857dd662430c0130c46f920666d70dae5df6148951ad76d42d31a8d540c32972"
    assert audit["registry_witness"]["registered_rasters_in_manifest"] == 695
    assert audit["registry_witness"]["rasters_examined"] == 1
    assert audit["registry_witness"]["coverage_complete"] is False
    assert audit["correlation"]["pass"] is True
    assert audit["correlation"]["absolute_spearman_rho"] < 0.90
    assert audit["overlap"]["candidate_dots_within_3px_of_witness"] == 37_560
    assert audit["overlap"]["candidate_dots"] == 37_654
    assert audit["overlap"]["fraction_within_3px"] > 0.70
    assert audit["overlap"]["pass"] is False
    assert audit["literal_gate_pass"] is False
    assert audit["duplicate_stop"] is True
    assert audit["ok_to_download_for_research"] is True
    assert audit["ok_to_submit"] is False
    assert audit["no_new_experiment_fit_surface_placement_or_tiff_written"] is True


def test_xfcoh31_run_card_does_not_promote_focus_subset_to_global_uniqueness() -> None:
    card = load_json("evidence/xfcoh31_run_card.json")
    assert card["ok_to_download_research"] is True
    assert card["ok_to_submit"] is False
    assert card["verdict"] == "negative"
    assert card["note_length"] == len(card["note"]) <= 140
    assert card["focus_site_comparison_scope"]["interpretation"].startswith("PASS within")
    assert card["literal_shared_registry_audit"]["literal_gate_pass"] is False
    assert card["literal_shared_registry_audit"]["coverage_complete"] is False
    assert card["protocol_compliance_review"]["requested_workflow_deviations"]
    assert not card["protocol_compliance_review"]["holdout_protocol"]["per_block_statistics_retained"]


def test_xfcoh31_holdout_numbers_are_labeled_and_have_ci_and_count() -> None:
    holdout = load_json("evidence/xfcoh31_run_card.json")["holdout_dti"]
    assert holdout["evidence_class"] == "HOLDOUT-DTI"
    assert holdout["evaluator_version"] == "gemsdoe31-holdout-v1"
    assert holdout["candidate"]["withheld_positive_pixels"] == 58_625
    assert len(holdout["candidate"]["ci95"]) == 2
    assert len(holdout["same_run_control_base19"]["ci95"]) == 2
    assert len(holdout["paired_delta_ci95"]) == 2
    assert holdout["paired_delta_xfcoh_minus_base19"] < 0
    assert holdout["paired_delta_ci95"][0] < 0 < holdout["paired_delta_ci95"][1]
