"""Label-free Poisson / Baranov pseudogravity residual features.

The feature function accepts geophysical arrays only. It must not be given a
catalogue, a distance-to-fault grid, or any other label-derived field.
Scale of the pseudogravity is arbitrary: local regression absorbs it.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import distance_transform_edt, gaussian_filter

FEATURE_NAMES = (
    "pg_resid_s30",
    "pg_resid_hg_s30",
    "pg_resid_hg_s12",
    "pg_quiet_edge",
)
TAPER_PX = 20
BOUNDARY_MASK_PX = 15
SIGMA_LONG_PX = 30.0
SIGMA_SHORT_PX = 12.0


def pseudogravity(rtp: np.ndarray, footprint: np.ndarray, *, pixel_m: float = 100.0,
                  taper_px: int = TAPER_PX) -> np.ndarray:
    """RTP anomaly filtered by ``|k|^{-1}`` (rad/m). DC bin is zero.

    Outside the footprint the input is treated as missing and the output is NaN.
    A linear taper over ``taper_px`` reduces wrap-around at the survey edge.
    ``taper_px=0`` keeps the spectrum identity used by the unit test.
    """
    if pixel_m <= 0:
        raise ValueError("pixel_m must be positive")
    fp = np.asarray(footprint, dtype=bool)
    src = np.asarray(rtp, dtype=np.float64)
    if src.shape != fp.shape or src.ndim != 2:
        raise ValueError("rtp and footprint must be matching 2-D arrays")
    observed = fp & np.isfinite(src)
    if not observed.any():
        raise ValueError("rtp has no finite footprint pixels")
    mean = float(src[observed].mean())
    filled = np.where(observed, src - mean, 0.0)
    if taper_px > 0:
        taper = np.clip(distance_transform_edt(fp) / float(taper_px), 0.0, 1.0)
        filled *= taper
    spectrum = np.fft.fft2(filled)
    ky = np.fft.fftfreq(src.shape[0], d=pixel_m)[:, None]
    kx = np.fft.fftfreq(src.shape[1], d=pixel_m)[None, :]
    k_rad = 2.0 * np.pi * np.sqrt(kx * kx + ky * ky)
    k_rad[0, 0] = np.inf
    spectrum = spectrum / k_rad
    spectrum[0, 0] = 0.0
    pg = np.fft.ifft2(spectrum).real
    out = np.full(src.shape, np.nan, dtype=np.float64)
    out[fp] = pg[fp]
    return out


def _normalized_smooth(values: np.ndarray, footprint: np.ndarray, sigma_px: float) -> np.ndarray:
    weight = footprint.astype(np.float64)
    filled = np.where(footprint, values, 0.0)
    den = gaussian_filter(weight, sigma_px, mode="nearest")
    num = gaussian_filter(filled, sigma_px, mode="nearest")
    return num / np.maximum(den, 1e-8)


def local_poisson_residual(gravity: np.ndarray, pg: np.ndarray, footprint: np.ndarray,
                           *, sigma_px: float) -> np.ndarray:
    """Footprint-normalized local regression residual ``grav - (a + b * pg)``."""
    fp = np.asarray(footprint, dtype=bool)
    g = np.where(fp & np.isfinite(gravity), gravity, 0.0)
    p = np.where(fp & np.isfinite(pg), pg, 0.0)
    mg = _normalized_smooth(g, fp, sigma_px)
    mp = _normalized_smooth(p, fp, sigma_px)
    mgp = _normalized_smooth(g * p, fp, sigma_px)
    mpp = _normalized_smooth(p * p, fp, sigma_px)
    var = np.maximum(mpp - mp * mp, 1e-12)
    slope = (mgp - mg * mp) / var
    intercept = mg - slope * mp
    residual = g - (intercept + slope * p)
    out = np.full(g.shape, np.nan, dtype=np.float64)
    out[fp] = residual[fp]
    return out


def _horizontal_gradient(field: np.ndarray, footprint: np.ndarray, pixel_m: float) -> np.ndarray:
    filled = np.where(footprint & np.isfinite(field), field, 0.0)
    gy, gx = np.gradient(filled, pixel_m)
    return np.hypot(gx, gy)


def _robust_z(field: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    values = field[footprint & np.isfinite(field)]
    med = float(np.median(values))
    mad = float(np.median(np.abs(values - med)))
    scale = 1.4826 * mad if mad > 0 else 1.0
    z = (np.where(np.isfinite(field), field, med) - med) / scale
    return np.clip(z, -8.0, 8.0).astype(np.float32)


def pseudogravity_features(rtp: np.ndarray, gravity: np.ndarray, tmi_hg: np.ndarray,
                           footprint: np.ndarray, *, pixel_m: float = 100.0) -> dict[str, np.ndarray]:
    """Return the four frozen features. Inputs are geophysical grids only."""
    fp = np.asarray(footprint, dtype=bool)
    pg = pseudogravity(rtp, fp, pixel_m=pixel_m)
    resid_long = local_poisson_residual(gravity, pg, fp, sigma_px=SIGMA_LONG_PX)
    resid_short = local_poisson_residual(gravity, pg, fp, sigma_px=SIGMA_SHORT_PX)
    hg_long = _horizontal_gradient(resid_long, fp, pixel_m)
    hg_short = _horizontal_gradient(resid_short, fp, pixel_m)
    # Rank CDF of magnetic gradient, computed on the footprint only.
    mag = np.asarray(tmi_hg, dtype=np.float64)
    if not np.isfinite(mag[fp]).any():
        raise ValueError("tmi_hg has no finite footprint pixels")
    from scipy.stats import rankdata
    cdf = np.zeros(fp.shape, dtype=np.float64)
    cdf[fp] = rankdata(np.where(np.isfinite(mag[fp]), mag[fp], np.nanmedian(mag[fp])), method="average")
    cdf[fp] /= float(fp.sum() + 1.0)
    quiet = np.where(fp, hg_long * (1.0 - cdf), np.nan)
    interior = distance_transform_edt(fp) >= BOUNDARY_MASK_PX
    features = {
        "pg_resid_s30": _robust_z(resid_long, fp),
        "pg_resid_hg_s30": _robust_z(hg_long, fp),
        "pg_resid_hg_s12": _robust_z(hg_short, fp),
        "pg_quiet_edge": _robust_z(quiet, fp),
    }
    for name, array in features.items():
        array[~interior] = 0.0
        array[~fp] = 0.0
        features[name] = array
    return features
