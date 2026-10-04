import numpy as np
import pytest

from gemsdoe31.h31_features import FEATURE_NAMES, build_magnetic_scale_features


def test_magnetic_scale_features_are_bounded_and_masked():
    rows, cols = np.mgrid[:80, :72]
    hg = (2.0 + np.sin(cols / 4.0) * np.cos(rows / 9.0)).astype(np.float32)
    vg = (1.0 + 0.5 * np.cos(rows / 5.0) + 0.15 * np.sin(cols / 7.0)).astype(np.float32)
    footprint = np.ones(hg.shape, bool)
    footprint[:2, :] = False
    hg[25, 31] = np.nan

    features, diagnostics = build_magnetic_scale_features(hg, vg, footprint)

    assert features.shape == (2, *hg.shape)
    assert diagnostics.invalid_footprint_pixels == 1
    assert np.isnan(features[:, :2, :]).all()
    assert np.isnan(features[:, 25, 31]).all()
    assert np.isfinite(features[:, footprint & np.isfinite(hg)]).all()
    assert np.nanmin(features[0]) >= np.log1p(0.5) - 1e-6
    assert np.nanmax(features[0]) <= np.log1p(30.0) + 1e-6
    assert 0.0 <= float(np.nanmin(features[1])) <= float(np.nanmax(features[1])) <= 1.0
    assert tuple(diagnostics.output_ranges) == FEATURE_NAMES


def test_magnetic_scale_features_require_valid_derivative_data():
    footprint = np.ones((12, 12), bool)
    with pytest.raises(ValueError, match="no cells have both finite"):
        build_magnetic_scale_features(np.full((12, 12), np.nan), np.ones((12, 12)), footprint)


def test_magnetic_scale_features_reject_grid_mismatch():
    with pytest.raises(ValueError, match="aligned 2-D"):
        build_magnetic_scale_features(np.ones((10, 10)), np.ones((10, 9)), np.ones((10, 10), bool))
