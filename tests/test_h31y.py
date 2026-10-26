"""H31-Y polarity features (synthetic) and run-card consistency."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from gemsdoe31.h31y_features import (
    basinward_unit,
    downslope_unit,
    piedmont_window,
    polarity_weight,
    synth_anti_gravpied,
)


def test_piedmont_window_breakpoints():
    s = np.array([[0.0, 5.0, 7.5, 10.0, 20.0]], dtype=np.float32)
    w = piedmont_window(s)
    assert w[0, 0] == 1.0 and w[0, 1] == 1.0
    assert abs(float(w[0, 2]) - 0.5) < 1e-5
    assert w[0, 3] == 0.0 and w[0, 4] == 0.0


def test_basinward_points_toward_low_gravity():
    g = np.zeros((21, 21), np.float32)
    g[:, :] = np.linspace(10.0, 0.0, 21)[None, :]  # gravity decreases to the right
    uy, ux = basinward_unit(g, sigma=1.0)
    assert float(np.mean(ux[5:16, 5:16])) > 0.5  # +x = basinward
    assert abs(float(np.mean(uy[5:16, 5:16]))) < 0.3


def test_downslope_points_toward_low_elev():
    z = np.zeros((21, 21), np.float32)
    z[:, :] = np.linspace(100.0, 0.0, 21)[None, :]
    uy, ux = downslope_unit(z, sigma=1.0)
    assert float(np.mean(ux[5:16, 5:16])) > 0.5


def test_polarity_splits_synth_and_anti():
    facing = np.ones((5, 5), np.float32)
    down_y = np.zeros((5, 5), np.float32)
    down_x = np.ones((5, 5), np.float32)  # downslope +x
    basin_y = np.zeros((5, 5), np.float32)
    basin_x = np.ones((5, 5), np.float32)
    synth = polarity_weight(facing, down_y, down_x, basin_y, basin_x)
    anti = polarity_weight(facing, down_y, down_x, -basin_y, -basin_x)
    assert float(synth.mean()) > 0.9
    assert float(anti.mean()) == 0.0


def test_synth_anti_gravpied_shapes_and_masks():
    rng = np.random.default_rng(7)
    h, w = 32, 32
    foot = np.ones((h, w), bool)
    foot[:, -2:] = False
    lidar_ok = foot.copy()
    lidar_ok[:4, :] = False
    out = synth_anti_gravpied(
        elev=rng.normal(size=(h, w)).astype(np.float32),
        slope_deg=np.full((h, w), 3.0, np.float32),
        gravity=rng.normal(size=(h, w)).astype(np.float32),
        grav_hg=np.abs(rng.normal(size=(h, w))).astype(np.float32),
        basement=rng.normal(size=(h, w)).astype(np.float32),
        downface=np.abs(rng.normal(size=(h, w))).astype(np.float32),
        lidar_ok=lidar_ok,
        foot=foot,
    )
    for k in ("SYNTH", "ANTI", "GRAVPIED", "BASEPIED"):
        assert out[k].shape == (h, w)
        assert np.isfinite(out[k]).all()
        assert (out[k][~foot] == 0).all()
        assert (out[k] >= 0).all()
    assert (out["SYNTH"][~lidar_ok] == 0).all()
    assert (out["ANTI"][~lidar_ok] == 0).all()


ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "evidence/h31y/run_card.json"


@pytest.fixture(scope="module")
def card():
    if not CARD.is_file():
        pytest.skip("H31-Y run card absent")
    return json.loads(CARD.read_text())


def test_h31y_card_gates_and_verdict(card):
    g = card["gates"]
    gate_keys = [k for k in g if k.startswith("G")]
    assert set(gate_keys) == {"G1_format", "G2_canary", "G3_holdout_efficacy", "G4_sgmc_discovery",
                              "G5_uniqueness_discrete", "G6_projection_ge_02778"}
    promote = all(g[k] for k in gate_keys)
    assert (card["verdict"] == "promote") == promote
    assert card["ok_to_submit"] == promote and card["slot_approved"] == promote
    assert card["submission_slots_used"] == 0
    assert 1 <= card["note_chars"] <= 140
    assert card["holdout_dti"]["evidence_class"] == "HOLDOUT-DTI"
    assert card["holdout_dti"]["evaluator_version"] == "gems57-pooled-hide-v2"
    assert card["projection"]["evidence_class"].startswith("PROJECTION")
    assert g["G5_uniqueness_discrete"] is False
    assert g["G1_format"] and g["G2_canary"] and g["G3_holdout_efficacy"]
    assert g["G4_sgmc_discovery"] and g["G6_projection_ge_02778"]
    assert card["correlation_overlap_vs_registry"]["discrete_max_final_overlap_3px"] <= 0.70
    assert card["correlation_overlap_vs_registry"]["discrete_max_topk_overlap_3px"] > 0.70


def test_h31y_files_and_hashes(card):
    from gemsdoe31.submission import sha256_file
    z = ROOT / card["files"]["zeros"]
    n = ROOT / card["files"]["nan"]
    assert z.is_file() and n.is_file() and (ROOT / card["files"]["zip"]).is_file()
    assert sha256_file(z) == card["raster_sha256"]
    assert sha256_file(n) == card["raster_sha256_nan"]
    assert card["validator"]["zeros"]["ok"] and card["validator"]["nan"]["ok"]
    assert card["validator"]["organizer_acceptance_verified"] is False
    assert card["ok_to_download_for_research"] is True
    assert "DO NOT SUBMIT" in card["instruction"]
