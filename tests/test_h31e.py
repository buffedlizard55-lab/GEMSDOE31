"""Tests for the H31-E lane: surface transforms, emitter, hide-and-recover holdout, metric helpers."""

from __future__ import annotations

import numpy as np
import pytest
from scipy.spatial import cKDTree

from gemsdoe31 import emission, holdout, metric, surface_features


def test_tophat_ignores_nodata_sentinel_and_remasks_nan():
    a = np.zeros((60, 60), dtype=np.float32)
    a[30, :] = 10.0                      # a one-cell ridge
    a[:5, :] = -3.4028235e38             # competition nodata sentinel (finite, not data)
    a[40:45, :] = np.nan
    out = surface_features.tophat_magnitude(a, 3)
    assert np.isnan(out[:5]).all() and np.isnan(out[40:45]).all()
    assert np.isfinite(out[5:40]).all()
    assert out[30, 30] > 5.0             # ridge responds
    assert np.nanmax(out) < 1e30         # sentinel never leaks into values


def test_ratio_gradient_and_geometric_mean_shapes():
    rng = np.random.default_rng(1)
    band = rng.normal(0, 1, (40, 40)).astype(np.float32)
    band[:, :5] = np.nan
    grad = surface_features.ratio_gradient(band)
    assert grad.shape == band.shape
    assert np.isnan(grad[:, :5]).all()
    gm = surface_features.geometric_mean_channels([grad, grad])
    assert np.nanmax(gm) <= 1.0


def test_emission_min_distance_determinism_and_budget():
    rng = np.random.default_rng(2)
    surface = rng.random((120, 120)).astype(np.float32)
    valid = np.ones(surface.shape, dtype=bool)
    d1 = emission.emit_dots(surface, valid, max_dots=80)
    d2 = emission.emit_dots(surface, valid, max_dots=80)
    assert np.array_equal(d1, d2)
    assert d1.sum() <= 80
    pts = np.column_stack(np.nonzero(d1))
    dist, _ = cKDTree(pts).query(pts, k=2)
    assert dist[:, 1].min() >= 2.8 - 1e-9


def test_metric_helpers_sum_to_dti_terms():
    rng = np.random.default_rng(3)
    pred = rng.random((40, 40)).astype(np.float32)
    truth = rng.random((40, 40)) > 0.92
    result = metric.dti(pred, truth)
    assert metric.per_truth_credit(pred, truth).sum() == pytest.approx(result["TPw"], abs=1e-9)
    assert metric.fp_weights(pred, truth).sum() == pytest.approx(result["FPw"], abs=1e-9)


def _toy_catalogue() -> tuple[np.ndarray, np.ndarray]:
    catalogue = np.zeros((400, 400), dtype=bool)
    catalogue[100:160, 100] = True       # NW component
    catalogue[300:360, 300] = True       # SE component
    catalogue[100, 200:280] = True       # NE component (centroid in NE domain)
    return catalogue, np.ones_like(catalogue)


def test_holdout_withholds_whole_components_and_masks_visible():
    catalogue, footprint = _toy_catalogue()
    split = holdout.fold_split(catalogue, footprint, fold=0, collar_m=1000.0)
    assert split["truth"].sum() == 60                      # the whole NW component
    assert not (split["truth"] & split["train_allowed"]).any()
    assert not (catalogue & split["train_allowed"] & split["truth"]).any()
    pred = np.ones(catalogue.shape, dtype=np.float32)
    masked = holdout.mask_visible_faults(pred, catalogue, split["truth"], split["domain"])
    assert (masked[catalogue & ~split["truth"]] == 0).all()   # visible faults pixel-exactly masked
    assert (masked[~split["domain"]] == 0).all()
    result = holdout.score_fold(pred, catalogue, split)
    assert 0.0 <= result["DTI"] <= 1.0
    blocks = [result["block_stats"]]
    assert holdout.pooled_dti_from_blocks(blocks) == pytest.approx(result["DTI"], rel=1e-9)


def test_block_universe_is_arm_independent_and_bootstrap_pairs():
    catalogue, footprint = _toy_catalogue()
    split = holdout.fold_split(catalogue, footprint, fold=0, collar_m=1000.0)
    pred_a = np.ones(catalogue.shape, dtype=np.float32)
    pred_b = np.zeros(catalogue.shape, dtype=np.float32)
    pred_b[100:160, 100] = 1.0
    blocks_a = [holdout.score_fold(pred_a, catalogue, split)["block_stats"]]
    blocks_b = [holdout.score_fold(pred_b, catalogue, split)["block_stats"]]
    assert blocks_a[0]["n_blocks"] == blocks_b[0]["n_blocks"]
    boot = holdout.paired_block_bootstrap({"a": blocks_a, "b": blocks_b}, resamples=25, seed=1)
    assert boot["pooled_dti"]["b"] > boot["pooled_dti"]["a"]   # exact-truth emission beats all-ones
    assert "a_minus_b" in boot["paired_delta_ci95"]


def test_holdout_training_excludes_quadrant_and_collar():
    catalogue, footprint = _toy_catalogue()
    split = holdout.fold_split(catalogue, footprint, fold=0, collar_m=5000.0)
    assert not split["train_allowed"][:200, :200].any()    # whole NW quadrant excluded
    allowed_pos = catalogue & split["train_allowed"]
    assert allowed_pos.sum() == 140                        # NE + SE components only
