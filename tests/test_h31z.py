"""H31-Z coherence/max-union features (synthetic) and run-card consistency."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from gemsdoe31.h31z_features import coherence_weighted, max_union, structure_tensor_coherence


def test_coherence_straight_ridge_beats_noise():
    h, w = 41, 41
    ridge = np.zeros((h, w), np.float32)
    ridge[:, 19:22] = 1.0
    rng = np.random.default_rng(0)
    noise = rng.normal(size=(h, w)).astype(np.float32)
    c_ridge = structure_tensor_coherence(ridge)
    c_noise = structure_tensor_coherence(noise)
    assert float(np.percentile(c_ridge[5:36, 19:22], 80)) > 0.9
    assert float(np.percentile(c_ridge, 50)) > float(np.percentile(c_noise, 50)) + 0.3


def test_coherence_constant_field_zero_and_bounds():
    coh = structure_tensor_coherence(np.ones((16, 16), np.float32))
    assert float(coh.max()) < 1e-6
    rng = np.random.default_rng(3)
    coh = structure_tensor_coherence(rng.normal(size=(24, 24)).astype(np.float32))
    assert float(coh.min()) >= 0.0 and float(coh.max()) <= 1.0
    assert np.isfinite(coh).all()


def test_coherence_weighted_floor_and_mask():
    strength = np.full((4, 4), 2.0, np.float32)
    valid = np.ones((4, 4), bool)
    valid[0, 0] = False
    out0 = coherence_weighted(strength, np.zeros((4, 4), np.float32), valid)
    out1 = coherence_weighted(strength, np.ones((4, 4), np.float32), valid)
    assert out0[0, 0] == 0.0 and out0[1, 1] == pytest.approx(0.5)  # 2.0 * 0.25 floor
    assert out1[1, 1] == pytest.approx(2.0)


def test_max_union_is_elementwise_max():
    a = np.array([[0.1, 0.9]], np.float32)
    b = np.array([[0.5, 0.2]], np.float32)
    u = max_union([a, b])
    assert u[0, 0] == pytest.approx(0.5) and u[0, 1] == pytest.approx(0.9)
    with pytest.raises(ValueError):
        max_union([])


ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "evidence/h31z/run_card.json"


@pytest.fixture(scope="module")
def card():
    if not CARD.is_file():
        pytest.skip("H31-Z run card absent (duplicate STOP or not yet packaged)")
    return json.loads(CARD.read_text())


def test_h31z_card_gates_and_verdict(card):
    g = card["gates"]
    gate_keys = [k for k in g if k.startswith("G")]
    assert set(gate_keys) == {"G1_format", "G2_canary", "G3_holdout_efficacy", "G4_sgmc_discovery",
                              "G5_uniqueness_discrete", "G6_projection_ge_02778"}
    promote = all(g[k] for k in gate_keys)
    assert (card["verdict"] == "promote") == promote
    assert card["ok_to_submit"] == promote and card["slot_approved"] == promote
    assert card["submission_slots_used"] == 0
    assert card["experiments_used"] <= 3
    assert 1 <= card["note_chars"] <= 140
    assert card["holdout_dti"]["evidence_class"] == "HOLDOUT-DTI"
    assert card["holdout_dti"]["evaluator_version"] == "gems57-pooled-hide-v2"
    assert card["holdout_dti"]["screen_final_surface"]["withheld_positive_pixels"] == 60988
    assert card["projection"]["evidence_class"].startswith("PROJECTION")
    assert card["correlation_overlap_vs_registry"]["discrete_max_final_overlap_3px"] <= 0.70
    assert card["correlation_overlap_vs_registry"]["discrete_max_topk_overlap_3px"] <= 0.70
    assert ("DO NOT SUBMIT" in card["instruction"]) == (not promote)


def test_h31z_files_and_hashes(card):
    from gemsdoe31.submission import sha256_file
    z = ROOT / card["files"]["zeros"]
    n = ROOT / card["files"]["nan"]
    assert z.is_file() and n.is_file() and (ROOT / card["files"]["zip"]).is_file()
    assert sha256_file(z) == card["raster_sha256"]
    assert sha256_file(n) == card["raster_sha256_nan"]
    assert card["validator"]["zeros"]["ok"] and card["validator"]["nan"]["ok"]
    assert card["validator"]["organizer_acceptance_verified"] is False
    assert card["ok_to_download_for_research"] is True
    prereg = ROOT / card["preregistration"]
    assert sha256_file(prereg) == card["preregistration_sha256"]
