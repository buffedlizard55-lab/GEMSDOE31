"""PGR31 novel features: Poisson pseudo-gravity discordance (preregistered 2026-10-26).

Frozen design: ``knowledge/2026-10-26_pgr31_preregistration.md``.

The pseudo-gravity transform (Baranov, 1957) vertically integrates reduced-to-pole
magnetic data so the magnetic field is expressed at the same derivative order as the
gravity field (Poisson's relation: for a common source with constant
magnetization-to-density ratio, the magnetic potential is proportional to the
directional derivative of the gravity potential).  A buried fault juxtaposing
basement blocks with different ratios therefore appears as a step in the *local
regression* of pseudo-gravity on observed gravity, even where no scarp exists.

Every function here is label-free and deterministic; no catalogue information of
any kind enters these features.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter

NOVEL_NAMES = [
    "pg_z",
    "pg_grad_s15",
    "pg_grad_s30",
    "grav_grad_s15",
    "pg_grav_mincoh",
    "pg_grav_localcorr6",
    "pg_grav_slope6",
    "pg_slope_grad",
    "pg_resid_grad",
]


def robust_z(field: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Median/MAD robust z-score over finite ``mask`` cells; NaN preserved, clipped [-8, 8]."""
    a = np.asarray(field, dtype=np.float64)
    m = np.asarray(mask, bool) & np.isfinite(a)
    values = a[m]
    if values.size == 0:
        raise ValueError("robust_z: no finite values inside mask")
    med = float(np.median(values))
    mad = float(np.median(np.abs(values - med)))
    scale = 1.4826 * mad if mad > 0 else 1.0
    z = (a - med) / scale
    return np.clip(z, -8.0, 8.0).astype(np.float32)


def pseudo_gravity(field: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Baranov vertical integration: ``irfft2(rfft2(x) / |k|)``, ``k=0`` coefficient zeroed.

    Non-finite and outside-mask cells are filled with the finite-in-mask median and the
    finite-in-mask mean is removed before the transform (both frozen in the
    preregistration, disclosed as the edge treatment for the irregular footprint).
    """
    a = np.asarray(field, dtype=np.float64)
    m = np.asarray(mask, bool) & np.isfinite(a)
    if not m.any():
        raise ValueError("pseudo_gravity: no finite values inside mask")
    med = float(np.median(a[m]))
    x = np.where(m, a, med)
    x = x - float(x[m].mean())
    height, width = x.shape
    spectrum = np.fft.rfft2(x)
    ky = 2.0 * np.pi * np.fft.fftfreq(height)[:, None]
    kx = 2.0 * np.pi * np.fft.rfftfreq(width)[None, :]
    kmag = np.sqrt(ky * ky + kx * kx)
    with np.errstate(divide="ignore", invalid="ignore"):
        filt = np.where(kmag > 0, 1.0 / np.where(kmag > 0, kmag, 1.0), 0.0)
    out = np.fft.irfft2(spectrum * filt, s=x.shape)
    return out.astype(np.float32)


def grad_mag(field: np.ndarray, sigma: float) -> np.ndarray:
    """Gaussian-gradient magnitude at ``sigma`` px (mode='nearest')."""
    a = np.asarray(field, dtype=np.float32)
    gy = gaussian_filter(a, sigma=sigma, order=(1, 0), mode="nearest")
    gx = gaussian_filter(a, sigma=sigma, order=(0, 1), mode="nearest")
    return np.hypot(gx, gy).astype(np.float32)


def _masked_smooth(values: np.ndarray, weights: np.ndarray, sigma: float) -> np.ndarray:
    return gaussian_filter(
        (np.asarray(values, dtype=np.float32) * weights), sigma=sigma, mode="nearest"
    )


def local_regression(
    a: np.ndarray, b: np.ndarray, mask: np.ndarray, sigma: float = 6.0
) -> dict[str, np.ndarray]:
    """Footprint-masked Gaussian local Pearson correlation, slope of ``a`` on ``b``, and residual.

    Uses normalised convolution ``mean(v) = G(m*v) / G(m)`` so footprint edges do not
    pull the local statistics toward the outside fill values.
    """
    m = (np.asarray(mask, bool) & np.isfinite(a) & np.isfinite(b)).astype(np.float32)
    af = np.where(m > 0, np.asarray(a, dtype=np.float32), 0.0).astype(np.float32)
    bf = np.where(m > 0, np.asarray(b, dtype=np.float32), 0.0).astype(np.float32)
    denom = gaussian_filter(m, sigma=sigma, mode="nearest")
    denom = np.where(denom > 1e-12, denom, np.nan).astype(np.float32)
    mean_a = _masked_smooth(af, m, sigma) / denom
    mean_b = _masked_smooth(bf, m, sigma) / denom
    mean_ab = _masked_smooth(af * bf, m, sigma) / denom
    mean_aa = _masked_smooth(af * af, m, sigma) / denom
    mean_bb = _masked_smooth(bf * bf, m, sigma) / denom
    cov = mean_ab - mean_a * mean_b
    var_a = np.clip(mean_aa - mean_a * mean_a, 0.0, None)
    var_b = np.clip(mean_bb - mean_b * mean_b, 0.0, None)
    ok = (var_b > 1e-12) & (var_a > 1e-12) & np.isfinite(cov)
    corr = np.zeros_like(cov, dtype=np.float32)
    corr[ok] = (cov[ok] / np.sqrt(var_a[ok] * var_b[ok])).astype(np.float32)
    corr = np.clip(corr, -1.0, 1.0)
    slope = np.zeros_like(cov, dtype=np.float32)
    ok_b = (var_b > 1e-12) & np.isfinite(cov)
    slope[ok_b] = (cov[ok_b] / var_b[ok_b]).astype(np.float32)
    slope = np.clip(slope, -8.0, 8.0)
    resid = (af - (mean_a + slope * (bf - mean_b))).astype(np.float32)
    resid = np.where(np.isfinite(resid), resid, 0.0).astype(np.float32)
    return {
        "corr": corr.astype(np.float32),
        "slope": slope.astype(np.float32),
        "resid": resid,
        "mean_a": np.where(np.isfinite(mean_a), mean_a, 0.0).astype(np.float32),
        "mean_b": np.where(np.isfinite(mean_b), mean_b, 0.0).astype(np.float32),
    }


def build_novel_features(
    rtp_raw: np.ndarray, grav_raw: np.ndarray, footprint: np.ndarray
) -> dict[str, np.ndarray]:
    """The nine frozen PGR31 novel features, finite inside the footprint, 0 outside it."""
    fp = np.asarray(footprint, bool)
    pg = robust_z(pseudo_gravity(rtp_raw, fp), fp)
    pg = np.where(fp, pg, 0.0).astype(np.float32)
    g = robust_z(grav_raw, fp)
    g = np.where(fp & np.isfinite(g), g, 0.0).astype(np.float32)

    pg_grad15 = grad_mag(pg, 1.5)
    pg_grad30 = grad_mag(pg, 3.0)
    grav_grad15 = grad_mag(g, 1.5)
    mincoh = np.minimum(robust_z(pg_grad15, fp), robust_z(grav_grad15, fp))
    reg = local_regression(pg, g, fp, sigma=6.0)
    feats = {
        "pg_z": pg,
        "pg_grad_s15": pg_grad15,
        "pg_grad_s30": pg_grad30,
        "grav_grad_s15": grav_grad15,
        "pg_grav_mincoh": mincoh,
        "pg_grav_localcorr6": reg["corr"],
        "pg_grav_slope6": reg["slope"],
        "pg_slope_grad": grad_mag(reg["slope"], 1.5),
        "pg_resid_grad": grad_mag(reg["resid"], 1.5),
    }
    out: dict[str, np.ndarray] = {}
    for name in NOVEL_NAMES:
        arr = np.where(fp, feats[name], 0.0).astype(np.float32)
        if not np.isfinite(arr[fp]).all():
            raise ValueError(f"PGR31 novel feature {name} has non-finite values inside footprint")
        out[name] = arr
    return out
