import numpy as np
from scipy.ndimage import gaussian_filter

from gemsdoe31.local_standardize import gaussian_blur_fft, locally_standardized_rank, rank_cdf


def test_gaussian_blur_fft_matches_scipy_in_interior():
    rng = np.random.default_rng(0)
    field = rng.standard_normal((120, 140)).astype(np.float32)
    ours = gaussian_blur_fft(field, sigma_px=5.0)
    theirs = gaussian_filter(field, sigma=5.0, mode="reflect", truncate=6.0)
    interior = np.s_[25:-25, 25:-25]
    assert np.max(np.abs(ours[interior] - theirs[interior])) < 2e-2


def test_rank_cdf_masked_range_and_monotonic():
    field = np.array([[0.0, 2.0], [1.0, 99.0]], dtype=np.float32)
    mask = np.array([[True, True], [True, False]])
    out = rank_cdf(field, mask)
    assert out[1, 1] == 0.0
    assert out[0, 0] < out[1, 0] < out[0, 1] == 1.0


def test_local_standardization_promotes_quiet_region_peak():
    # Region A has globally high scores; region B is quiet except one peak.
    # A global rank buries B's peak; local standardization must surface it.
    field = np.zeros((200, 400), dtype=np.float32)
    field[:, :200] = 0.8
    field[100, 100] = 0.9          # A peak
    field[:, 200:] = 0.1
    field[100, 300] = 0.4          # B peak: locally extreme, globally middling
    mask = np.ones(field.shape, dtype=bool)
    glob = rank_cdf(field, mask)
    local = locally_standardized_rank(field, mask, sigma_px=20.0)
    assert local[100, 300] > glob[100, 300]
    assert local[100, 300] > 0.9
    assert float(local.min()) >= 0.0 and float(local.max()) <= 1.0


def test_local_standardization_constant_field_is_finite():
    out = locally_standardized_rank(np.ones((50, 60), dtype=np.float32),
                                    np.ones((50, 60), dtype=bool), sigma_px=10.0)
    assert np.isfinite(out).all()
