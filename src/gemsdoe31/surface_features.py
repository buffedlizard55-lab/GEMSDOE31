"""H31-E surface-expression transform channels (preregistered 2026-10-25).

Label-free transforms of restored stack bands. Every function takes a float array that may contain
NaN (outside footprint / no survey coverage), filters on a nearest-neighbour-filled copy, and
re-masks the originally-invalid cells to NaN. No catalogue, SGMC, or other label-derived input is
accepted anywhere in this module.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import (
    distance_transform_edt,
    gaussian_filter,
    gaussian_laplace,
    grey_dilation,
    grey_erosion,
)

NEW_CHANNELS = [
    "tophat_det_3", "tophat_det_7", "tophat_det_15",
    "flex_det_2", "flex_det_5",
    "ratio_grad_thk", "ratio_grad_uth", "ratio_grad_uk", "ratio_ridge_gm",
    "dipole_coh",
]


SENTINEL_ABS_MAX = 1e30  # nodata sentinels (e.g. -3.4028235e38) are finite but not data


def _valid_mask(values: np.ndarray) -> np.ndarray:
    return np.isfinite(values) & (np.abs(values) < SENTINEL_ABS_MAX)


def _nearest_fill(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return (filled, valid_mask): invalid cells take the nearest valid value (EDT indices)."""
    valid = _valid_mask(values)
    if valid.all():
        return values.astype(np.float32, copy=False), valid
    _, indices = distance_transform_edt(~valid, return_indices=True)
    filled = values[tuple(indices)].astype(np.float32, copy=False)
    return filled, valid


def _remask(values: np.ndarray, valid: np.ndarray) -> np.ndarray:
    out = np.asarray(values, dtype=np.float32).copy()
    out[~valid] = np.nan
    return out


def _grey_opening_square(values: np.ndarray, half_width: int) -> np.ndarray:
    """Flat square opening via separable 1-D erosion/dilation (identical for flat SEs)."""
    k = 2 * half_width + 1
    eroded = grey_erosion(values, size=(k, 1))
    eroded = grey_erosion(eroded, size=(1, k))
    opened = grey_dilation(eroded, size=(k, 1))
    return grey_dilation(opened, size=(1, k))


def _grey_closing_square(values: np.ndarray, half_width: int) -> np.ndarray:
    k = 2 * half_width + 1
    dilated = grey_dilation(values, size=(k, 1))
    dilated = grey_dilation(dilated, size=(1, k))
    closed = grey_erosion(dilated, size=(k, 1))
    return grey_erosion(closed, size=(1, k))


def tophat_magnitude(det_elev: np.ndarray, half_width: int) -> np.ndarray:
    """|white top-hat| + |black top-hat| of detrended elevation at one square scale."""
    filled, valid = _nearest_fill(det_elev)
    white = filled - _grey_opening_square(filled, half_width)
    black = _grey_closing_square(filled, half_width) - filled
    return _remask(np.abs(white) + np.abs(black), valid)


def flexure(det_elev: np.ndarray, sigma: float) -> np.ndarray:
    """|Laplacian-of-Gaussian| of detrended elevation (flexure / curvature magnitude)."""
    filled, valid = _nearest_fill(det_elev)
    return _remask(np.abs(gaussian_laplace(filled.astype(np.float64), sigma)), valid)


def _standardise(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    valid = np.isfinite(values)
    finite = values[valid]
    median = float(np.median(finite))
    q25, q75 = (float(np.percentile(finite, p)) for p in (25, 75))
    iqr = (q75 - q25) or 1.0
    filled = np.where(valid, values, median).astype(np.float64)
    return (filled - median) / iqr, valid


def ratio_gradient(ratio_band: np.ndarray, sigma: float = 1.0) -> np.ndarray:
    """Gradient magnitude of a robustly standardised, smoothed radiometric ratio band."""
    standardised, valid = _standardise(ratio_band)
    smoothed = gaussian_filter(standardised, sigma)
    grad_y, grad_x = np.gradient(smoothed)
    return _remask(np.hypot(grad_y, grad_x), valid)


def _percentile_clip01(values: np.ndarray, percentile: float = 99.0) -> np.ndarray:
    valid = _valid_mask(values)
    scale = float(np.percentile(values[valid], percentile)) or 1.0
    return np.clip(np.nan_to_num(values, nan=0.0) / scale, 0.0, 1.0), valid


def geometric_mean_channels(channels: list[np.ndarray]) -> np.ndarray:
    """Geometric mean of percentile-clipped channels; NaN where any input is NaN."""
    clipped = []
    valid = None
    for channel in channels:
        values, channel_valid = _percentile_clip01(channel)
        clipped.append(values)
        valid = channel_valid if valid is None else (valid & channel_valid)
    product = np.prod(np.stack(clipped), axis=0)
    return _remask(product ** (1.0 / len(clipped)), valid)


def dipole_coherence(upface_minus_downface: np.ndarray, coh100: np.ndarray) -> np.ndarray:
    """|signed LiDAR dipole| gated by the 100 m strike-coherence band (u8-scaled)."""
    valid = np.isfinite(upface_minus_downface) & np.isfinite(coh100)
    values = np.abs(np.nan_to_num(upface_minus_downface, nan=0.0)) * (
        np.nan_to_num(coh100, nan=0.0) / 255.0
    )
    return _remask(values, valid)


def build_new_channels(bands: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Build every preregistered H31-E transform channel from named stack bands."""
    det = bands["det_elev"]
    grad_thk = ratio_gradient(bands["ThK"])
    grad_uth = ratio_gradient(bands["UTh"])
    grad_uk = ratio_gradient(bands["UK"])
    return {
        "tophat_det_3": tophat_magnitude(det, 3),
        "tophat_det_7": tophat_magnitude(det, 7),
        "tophat_det_15": tophat_magnitude(det, 15),
        "flex_det_2": flexure(det, 2.0),
        "flex_det_5": flexure(det, 5.0),
        "ratio_grad_thk": grad_thk,
        "ratio_grad_uth": grad_uth,
        "ratio_grad_uk": grad_uk,
        "ratio_ridge_gm": geometric_mean_channels([grad_thk, grad_uth, grad_uk]),
        "dipole_coh": dipole_coherence(bands["upface_minus_downface"], bands["coh100"]),
    }
