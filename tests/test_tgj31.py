"""Regressions for the new audit lane and the unchanged shared template."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

from gems57 import evaluate_holdout, metric, spatial, uniqueness
from gemsdoe31.transfer import build_transfer_surface

ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location("test_" + name, ROOT / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_shared_template_source_bytes_have_not_drifted():
    pin = json.loads((ROOT / "registry/shared_template.json").read_text())
    assert pin["modifications"] == []
    for row in pin["files"]:
        assert hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"]


def test_transfer_operator_is_bounded_label_free_and_deterministic():
    y, x = np.mgrid[:140, :160]
    m = np.sin(x / 10) + np.cos(y / 12)
    g = np.where(x < 80, 0.8 * m, -0.7 * m) + 0.1 * np.sin(y / 7)
    fp = np.ones(m.shape, bool)
    a, control, feats, report = build_transfer_surface(m, g, fp, regional_sigma=3, scales=(1, 2))
    b = build_transfer_surface(m, g, fp, regional_sigma=3, scales=(1, 2))[0]
    np.testing.assert_array_equal(a, b)
    assert a.dtype == np.float32
    assert report["uses_catalogue_or_sgmc"] is False
    assert report["supported_pixels"] > 0
    for arr in (a, control, *feats.values()):
        assert np.isfinite(arr).all() and arr.min() >= 0 and arr.max() <= 1
    assert (a > 0).any()


def test_constant_fields_do_not_generate_a_fault():
    a = np.ones((140, 160), np.float32)
    surface, control, _, _ = build_transfer_surface(a, a, np.ones_like(a, bool), regional_sigma=3, scales=(1, 2))
    assert not surface.any()
    assert not control.any()


def test_sentinel_and_missing_measurements_cannot_create_edge_halos():
    rng = np.random.default_rng(31)
    m = rng.normal(size=(140, 160)).astype(np.float32)
    g = m.copy()
    m[70, 80] = -3.4028235e38
    fp = np.ones(m.shape, bool)
    surface, _, _, report = build_transfer_surface(m, g, fp, regional_sigma=3, scales=(1, 2))
    radius = report["required_valid_halo_px"]
    assert not surface[70-radius:71+radius, 80-radius:81+radius].any()
    assert np.isfinite(surface).all()


def test_shape_and_empty_inputs_fail_closed():
    with pytest.raises(ValueError, match="aligned"):
        build_transfer_surface(np.zeros((3, 4)), np.zeros((4, 3)), np.ones((3, 4), bool))
    with pytest.raises(ValueError, match="no jointly valid"):
        build_transfer_surface(np.full((12, 12), np.nan), np.ones((12, 12)), np.ones((12, 12), bool))


def test_whole_component_split_is_label_blind_and_buffered():
    cat = np.zeros((48, 48), bool)
    cat[8:40, 23] = True  # entire component crosses the horizontal boundary
    cat[10:18, 35] = True
    eligible = np.ones_like(cat)
    for fold in spatial.folds(cat, eligible, buffer_px=3):
        assert fold["receipt"]["evaluation_region_label_blind"] is True
        assert fold["receipt"]["shared_train_truth_components"] == 0
        assert not (fold["train"] & fold["held_all"]).any()
        assert not (fold["truth"] & fold["visible"]).any()
        if fold["truth"][10, 23]:
            assert fold["held_all"][35, 23]  # tail not clipped into a training positive


def test_shared_evaluator_masks_only_exact_visible_pixels():
    p = np.zeros((12, 13), np.float32)
    truth = np.zeros_like(p, bool)
    truth[5, 5] = True
    visible = np.zeros_like(truth)
    visible[5, 6] = True
    p[5, 6] = p[5, 7] = 1
    fold = {"truth": truth, "visible": visible, "region": np.ones_like(truth)}
    result, terms = evaluate_holdout.evaluate(p, fold, np.ones_like(truth), block_side=4)
    expected = metric.dti_exact(p, truth, valid=fold["region"], known=visible)
    assert result["dti"] == pytest.approx(expected["dti"])
    assert result["emitted"] == 1  # neighbor is NOT silently buffered out
    assert result["tp"] == pytest.approx(1 / 3)
    np.testing.assert_allclose(terms.sum(axis=0), [result['tp'], result['fp'], result['fn'], 1])


def test_literal_dense_witness_must_block_every_nonempty_surface():
    surface = np.zeros((15, 16), np.float32)
    surface[5, 6] = 0.001  # no unauthorized >=0.5 support threshold
    dense = np.full_like(surface, 0.0001)
    assert uniqueness.dot_overlap(surface, dense) == 1.0
    assert uniqueness.dot_overlap(surface, np.zeros_like(surface)) == 0
    assert uniqueness.OVERLAP_LIMIT == 0.70


def test_legacy_writer_rejects_bad_values_before_serialization(tmp_path, monkeypatch):
    builder = load_script("build_submission")
    # Keep this a valid-grid fixture so it tests the range contract rather than
    # being rejected earlier by the hardened exact-grid contract.
    monkeypatch.setitem(builder.PROFILE, "height", 12)
    monkeypatch.setitem(builder.PROFILE, "width", 13)
    dots = np.zeros((12, 13), bool)
    dots[5, 5] = True
    fp = np.ones_like(dots)
    for value in (1.0001, -0.01, np.inf, np.nan):
        values = np.full(dots.shape, 0.5, np.float64)
        values[2, 2] = value  # invalid even at a non-emitted footprint pixel
        with pytest.raises(ValueError, match="finite in \\[0,1\\]"):
            builder.write_variants(dots, fp, tmp_path / "bad", name="bad", values=values)
    assert not list(tmp_path.glob("*.tif"))


def test_static_preparation_has_no_full_catalogue_or_sgmc_distance_channel():
    prepare = load_script("prepare_data")
    assert "dist_cat_km" not in prepare.DERIVED_BANDS
    assert "dist_sgmc_km" not in prepare.DERIVED_BANDS


def test_new_run_card_is_negative_and_exact_file_is_not_a_copy():
    path = ROOT / "evidence/tgj31/run_card.json"
    if not path.exists():
        pytest.skip("one frozen operator has not run yet")
    card = json.loads(path.read_text())
    assert card["verdict"] == "negative"
    assert card["safe_to_submit"] is False
    assert card["submission_slots_used"] == 0
    assert card["lineage"]["prior_prediction_used_as_input"] is False
    assert card["evaluator"]["version"] == evaluate_holdout.VERSION
    assert len(card["holdout_dti"]["ci95"]) == 2
    assert card["holdout_dti"]["withheld_positive_pixels"] > 0
    tif = ROOT / card["files"]["tif"]
    assert hashlib.sha256(tif.read_bytes()).hexdigest() == card["raster_sha256"]
    registry = json.loads((ROOT / "registry/prior_raster_snapshot.json").read_text())
    assert card["raster_sha256"] not in {r["sha256"] for r in registry["rasters"]}
    assert card["validator_output"]["nan_inside_footprint"] == 0
    assert len(card["note"]) <= 140
