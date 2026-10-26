"""PGR31 feature mathematics on synthetic grids (no competition data needed)."""

import numpy as np

from gemsdoe31.pgr31_features import (
    NOVEL_NAMES,
    build_novel_features,
    local_regression,
    pseudo_gravity,
    robust_z,
)


def test_pseudo_gravity_sinusoid_amplitude_and_phase():
    # Vertical integration divides the Fourier amplitude by |k| and keeps phase:
    # cos(2*pi*3*x/W) -> cos(2*pi*3*x/W) / (2*pi*3/W).
    h, w = 64, 96
    x = np.cos(2 * np.pi * 3 * np.arange(w)[None, :] / w) * np.ones((h, 1))
    mask = np.ones((h, w), bool)
    pg = pseudo_gravity(x.astype(np.float32), mask)
    k = 2 * np.pi * 3 / w
    expected = (x / k).astype(np.float32)
    assert np.abs(pg.mean()) < 1e-4
    np.testing.assert_allclose(pg, expected, rtol=1e-4, atol=1e-3)


def test_pseudo_gravity_constant_field_is_zero():
    x = np.full((32, 48), 7.5, dtype=np.float32)
    pg = pseudo_gravity(x, np.ones_like(x, bool))
    np.testing.assert_allclose(pg, 0.0, atol=1e-5)


def test_local_regression_identical_fields_corr_one_slope_one_resid_zero():
    rng = np.random.default_rng(7)
    a = rng.normal(size=(80, 90)).astype(np.float32)
    reg = local_regression(a, a.copy(), np.ones(a.shape, bool), sigma=4.0)
    interior = np.s_[15:-15, 15:-15]
    np.testing.assert_allclose(reg["corr"][interior], 1.0, atol=1e-4)
    np.testing.assert_allclose(reg["slope"][interior], 1.0, atol=1e-3)
    assert np.abs(reg["resid"][interior]).max() < 0.05


def test_local_regression_step_in_slope_is_detected():
    # b is a smooth ramp; a = 1*b on the left half and 3*b on the right half.
    # The local slope must step across the boundary (the fault analogue).
    yy, xx = np.mgrid[0:80, 0:120]
    b = (xx / 120.0).astype(np.float32)
    a = np.where(xx < 60, b, 3.0 * b).astype(np.float32)
    reg = local_regression(a, b, np.ones(a.shape, bool), sigma=5.0)
    left = reg["slope"][40, 25]
    right = reg["slope"][40, 95]
    assert abs(left - 1.0) < 0.35
    assert abs(right - 3.0) < 0.35


def test_robust_z_preserves_nan_and_clips():
    a = np.array([[0.0, 1.0, np.nan], [2.0, 1e6, 1.0]], dtype=np.float32)
    z = robust_z(a, np.ones(a.shape, bool))
    assert np.isnan(z[0, 2])
    assert np.nanmax(z) <= 8.0 and z[1, 1] == 8.0


def test_build_novel_features_finite_inside_zero_outside():
    rng = np.random.default_rng(3)
    h, w = 70, 90
    fp = np.zeros((h, w), bool)
    fp[10:-10, 12:-12] = True
    rtp = rng.normal(size=(h, w)).astype(np.float32)
    grav = rng.normal(size=(h, w)).astype(np.float32)
    feats = build_novel_features(rtp, grav, fp)
    assert list(feats) == NOVEL_NAMES
    for arr in feats.values():
        assert np.isfinite(arr[fp]).all()
        assert (arr[~fp] == 0).all()
