"""Masked 12 km local standardization of a ranking surface (RBU31-B).

Implements the frozen transform in
``knowledge/2026-10-25_rbu31b_amendment_preregistration.md``::

    mean  = G_sigma(s*m) / G_sigma(m)                       sigma = 120 px
    z     = (s - mean) / sqrt(G_sigma((s-mean)^2 * m) / G_sigma(m) + 1e-6)
    blend = 0.65*z + 0.35*rank_CDF(s | m)
    out   = rank_CDF(blend | m)

``G_sigma`` is an exact Gaussian blur evaluated by FFT (reflect-padded),
which is the untruncated limit of the ``scipy.ndimage.gaussian_filter``
used by H31-B's ``local_survey_invariant_score``. Masking restricts every
local statistic to the prediction domain so fold evaluation stays honest.
The transform is label-free and deterministic.
"""
from __future__ import annotations

import numpy as np
from scipy.fft import irfft2, rfft2

SIGMA_PX = 120.0
LOCAL_WEIGHT = 0.65


def gaussian_blur_fft(field: np.ndarray, sigma_px: float = SIGMA_PX) -> np.ndarray:
    """Exact Gaussian blur (transfer exp(-2 pi^2 sigma^2 f^2)), reflect-padded."""
    arr = np.asarray(field, dtype=np.float32)
    if sigma_px <= 0:
        return arr.copy()
    pad = int(np.ceil(3.0 * sigma_px))
    padded = np.pad(arr, ((pad, pad), (pad, pad)), mode="reflect")
    ky = np.fft.fftfreq(padded.shape[0]).astype(np.float32)
    kx = np.fft.rfftfreq(padded.shape[1]).astype(np.float32)
    transfer = np.exp(-2.0 * (np.pi * sigma_px) ** 2 * (ky[:, None] ** 2 + kx[None, :] ** 2))
    blurred = irfft2(rfft2(padded, workers=2) * transfer, s=padded.shape, workers=2)
    return blurred[pad:pad + arr.shape[0], pad:pad + arr.shape[1]].astype(np.float32)


def rank_cdf(field: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Rank-normalize finite in-mask values to [0, 1]; 0 outside the mask."""
    out = np.zeros(field.shape, dtype=np.float32)
    valid = np.asarray(mask, dtype=bool) & np.isfinite(field)
    vals = np.asarray(field[valid], dtype=np.float32)
    if vals.size == 0:
        return out
    order = np.argsort(vals, kind="mergesort")
    ranks = np.empty(vals.size, dtype=np.float32)
    if vals.size == 1:
        ranks[0] = 0.5
    else:
        ranks[order] = np.linspace(0.0, 1.0, vals.size, dtype=np.float32)
    out[valid] = ranks
    return out


def locally_standardized_rank(
    score: np.ndarray,
    mask: np.ndarray,
    *,
    sigma_px: float = SIGMA_PX,
    local_weight: float = LOCAL_WEIGHT,
    blurred_mask: np.ndarray | None = None,
) -> np.ndarray:
    """Return the masked locally-standardized rank surface in [0, 1]."""
    m = np.asarray(mask, dtype=bool)
    s = np.where(m & np.isfinite(score), score, 0.0).astype(np.float32)
    m_f = m.astype(np.float32)
    den = gaussian_blur_fft(m_f, sigma_px) if blurred_mask is None else blurred_mask
    den = np.maximum(den, 1e-6)
    mean = gaussian_blur_fft(s * m_f, sigma_px) / den
    resid = np.where(m, s - mean, 0.0).astype(np.float32)
    var = np.maximum(gaussian_blur_fft(resid * resid, sigma_px) / den, 1e-6)
    z = (resid / np.sqrt(var)).astype(np.float32)
    blend = (local_weight * z + (1.0 - local_weight) * rank_cdf(s, m)).astype(np.float32)
    out = rank_cdf(blend, m)
    out[~m] = 0.0
    return out
