"""Unit checks for the frozen H31-N pseudogravity transform. No catalogue inputs."""

import inspect

import numpy as np
import pytest

from gemsdoe31.h31n_pseudogravity import (
    FEATURE_NAMES,
    local_poisson_residual,
    pseudogravity,
    pseudogravity_features,
)


def test_feature_function_does_not_accept_labels():
    params = set(inspect.signature(pseudogravity_features).parameters)
    assert params == {"rtp", "gravity", "tmi_hg", "footprint", "pixel_m"}


def test_inverse_wavenumber_spectrum_identity_without_taper():
    rng = np.random.default_rng(0)
    rtp = rng.normal(size=(64, 64))
    footprint = np.ones((64, 64), dtype=bool)
    pg = pseudogravity(rtp, footprint, pixel_m=100.0, taper_px=0)
    spec_rtp = np.fft.fft2(rtp - rtp.mean())
    spec_pg = np.fft.fft2(np.nan_to_num(pg, nan=0.0))
    ky = np.fft.fftfreq(64, d=100.0)[:, None]
    kx = np.fft.fftfreq(64, d=100.0)[None, :]
    k_rad = 2.0 * np.pi * np.sqrt(kx * kx + ky * ky)
    k_rad[0, 0] = np.inf
    expected = spec_rtp / k_rad
    expected[0, 0] = 0.0
    np.testing.assert_allclose(spec_pg, expected, rtol=1e-8, atol=1e-8)


def test_proportional_gravity_has_near_zero_residual():
    rng = np.random.default_rng(1)
    footprint = np.ones((48, 48), dtype=bool)
    pg = rng.normal(size=(48, 48))
    gravity = 1.7 * pg - 0.4
    residual = local_poisson_residual(gravity, pg, footprint, sigma_px=6.0)
    assert np.nanmax(np.abs(residual)) < 1e-6


def test_unexplained_gravity_step_survives_in_the_residual():
    footprint = np.ones((64, 64), dtype=bool)
    pg = np.zeros((64, 64))
    gravity = np.zeros((64, 64))
    gravity[:, 32:] = 5.0
    residual = local_poisson_residual(gravity, pg, footprint, sigma_px=4.0)
    assert np.nanstd(residual) > 0.5


def test_features_are_finite_and_named():
    rng = np.random.default_rng(2)
    shape = (40, 40)
    footprint = np.ones(shape, dtype=bool)
    footprint[:2, :] = False
    rtp = rng.normal(size=shape)
    gravity = rng.normal(size=shape)
    tmi_hg = np.abs(rng.normal(size=shape))
    features = pseudogravity_features(rtp, gravity, tmi_hg, footprint, pixel_m=100.0)
    assert tuple(features) == FEATURE_NAMES
    for array in features.values():
        assert array.shape == shape
        assert np.isfinite(array).all()
        assert array[~footprint].sum() == 0


def test_missing_rtp_raises():
    footprint = np.zeros((8, 8), dtype=bool)
    with pytest.raises(ValueError):
        pseudogravity(np.zeros((8, 8)), footprint)
