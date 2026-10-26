"""H31-Y polarity-concordant LiDAR facing and piedmont gravity lines.

Label-free. Catalogue distances are never used. Unit-tested on synthetic arrays.
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter

GRAV_SIGMA_PX = 2.0
ELEV_SIGMA_PX = 1.5


def piedmont_window(slope_deg: np.ndarray) -> np.ndarray:
    """Full weight on 0–5°, linear taper 5–10°, zero above 10° (playas included)."""
    s = np.asarray(slope_deg, dtype=np.float32)
    w = np.zeros(s.shape, np.float32)
    w[s <= 5.0] = 1.0
    mid = (s > 5.0) & (s < 10.0)
    w[mid] = (10.0 - s[mid]) / 5.0
    return w


def unit_increasing(field: np.ndarray, sigma: float) -> tuple[np.ndarray, np.ndarray]:
    """Unit vector of the increasing direction of a smoothed scalar field."""
    sm = gaussian_filter(np.asarray(field, dtype=np.float32), sigma, mode="nearest")
    gy = gaussian_filter(sm, 1.0, order=(1, 0), mode="nearest")
    gx = gaussian_filter(sm, 1.0, order=(0, 1), mode="nearest")
    mag = np.hypot(gy, gx).astype(np.float32)
    mag = np.maximum(mag, 1e-6)
    return (gy / mag).astype(np.float32), (gx / mag).astype(np.float32)


def downslope_unit(elev: np.ndarray, sigma: float = ELEV_SIGMA_PX) -> tuple[np.ndarray, np.ndarray]:
    """Downslope unit vector of smoothed elevation = opposite of increasing elevation."""
    uy, ux = unit_increasing(elev, sigma)
    return (-uy).astype(np.float32), (-ux).astype(np.float32)


def basinward_unit(gravity: np.ndarray, sigma: float = GRAV_SIGMA_PX) -> tuple[np.ndarray, np.ndarray]:
    """Basinward = direction of decreasing isostatic gravity (mass deficit of basin fill)."""
    uy, ux = unit_increasing(gravity, sigma)
    return (-uy).astype(np.float32), (-ux).astype(np.float32)


def polarity_weight(
    facing: np.ndarray,
    down_y: np.ndarray,
    down_x: np.ndarray,
    target_y: np.ndarray,
    target_x: np.ndarray,
) -> np.ndarray:
    """facing × relu(downslope · target). Zero where facing is non-finite or ≤0."""
    align = down_y * target_y + down_x * target_x
    w = np.maximum(align, 0.0).astype(np.float32)
    f = np.where(np.isfinite(facing), np.maximum(facing, 0.0), 0.0).astype(np.float32)
    return (f * w).astype(np.float32)


def synth_anti_gravpied(
    *,
    elev: np.ndarray,
    slope_deg: np.ndarray,
    gravity: np.ndarray,
    grav_hg: np.ndarray,
    basement: np.ndarray,
    downface: np.ndarray,
    lidar_ok: np.ndarray,
    foot: np.ndarray,
) -> dict[str, np.ndarray]:
    """Return raw (non-ranked) SYNTH, ANTI, GRAVPIED, BASEPIED, CTRL-ready gravity HG."""
    dy, dx = downslope_unit(elev)
    by, bx = basinward_unit(gravity)
    ry, rx = (-by).astype(np.float32), (-bx).astype(np.float32)
    df = np.where(lidar_ok, downface, 0.0).astype(np.float32)
    synth = polarity_weight(df, dy, dx, by, bx)
    anti = polarity_weight(df, dy, dx, ry, rx)
    synth[~foot] = 0.0
    anti[~foot] = 0.0
    pw = piedmont_window(slope_deg)
    gravpied = (np.abs(np.asarray(grav_hg, dtype=np.float32)) * pw).astype(np.float32)
    gravpied[~foot] = 0.0
    by_b, bx_b = unit_increasing(basement, GRAV_SIGMA_PX)
    base_g = np.hypot(by_b, bx_b).astype(np.float32)
    basepied = (base_g * pw).astype(np.float32)
    basepied[~foot] = 0.0
    return {
        "SYNTH": synth,
        "ANTI": anti,
        "GRAVPIED": gravpied,
        "BASEPIED": basepied,
        "piedmont_window": pw.astype(np.float32),
    }
