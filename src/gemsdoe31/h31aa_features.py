"""Label-free geological feature operators for Lane H31-AA (SLFS).

Implements the exact frozen equations of
``knowledge/2026-10-27_h31aa_preregistration.md``:
1. Multi-scale (sigma in {1.5, 3.0} px) logarithmic piedmont flexure
   ``-grad(ln(s + 1.5 deg)) . u_down`` windowed to piedmont-to-lower-front
   slopes (0.8-18 deg, flat peak 2-11 deg) and steered along local contour
   strike (half-length 4 px, sigma_k 2.5 px).
2. Equipotential paleoshoreline null suppressor ``w_shore in [0.35, 1.0]``
   penalizing contours that are nearly horizontal over +-600 m along strike
   while lacking subsurface gravity / basement / magnetic-contact support.
3. Strict 1-pixel cross-strike directional crest extraction ``crest1px`` so
   pre-placement top-K mass lies on 1-pixel-thin fault-toe crests rather than
   multi-pixel steep-cliff ribbons.
"""
from __future__ import annotations

from typing import Callable

import numpy as np
from scipy.ndimage import gaussian_filter

S0_DEG: float = 1.5
PIEDMONT_WINDOW_DEG: tuple[float, float, float, float] = (0.8, 2.0, 11.0, 18.0)
SCALES_PX: tuple[float, float] = (1.5, 3.0)
STRIKE_HALF_LEN_PX: int = 4
STRIKE_SIGMA_PX: float = 2.5
SHORE_OFFSETS_PX: tuple[int, ...] = (-6, -3, 3, 6)
OFF_CREST_SCALE: float = 0.05


def piedmont_window(slope_deg: np.ndarray,
                    window: tuple[float, float, float, float] = PIEDMONT_WINDOW_DEG) -> np.ndarray:
    """Piecewise-linear piedmont-to-lower-range-front habitat window in [0, 1]."""
    a, b, c, d = window
    w = np.zeros(slope_deg.shape, dtype=np.float32)
    rise = (slope_deg > a) & (slope_deg < b)
    w[rise] = (slope_deg[rise] - a) / (b - a)
    w[(slope_deg >= b) & (slope_deg <= c)] = 1.0
    fall = (slope_deg > c) & (slope_deg < d)
    w[fall] = (d - slope_deg[fall]) / (d - c)
    return w


def steered_strike_average(field: np.ndarray, uy_down: np.ndarray, ux_down: np.ndarray,
                           foot: np.ndarray, *, half_len: int = STRIKE_HALF_LEN_PX,
                           sigma_k: float = STRIKE_SIGMA_PX) -> np.ndarray:
    """Symmetric Gaussian-weighted average along local contour-strike tangent."""
    h, w = field.shape
    rows, cols = np.indices((h, w), dtype=np.float32)
    sy = ux_down.astype(np.float32)
    sx = (-uy_down).astype(np.float32)
    valid_field = np.where(foot, field, 0.0).astype(np.float32)
    foot_f = foot.astype(np.float32)

    num = np.zeros((h, w), dtype=np.float32)
    den = np.zeros((h, w), dtype=np.float32)
    for k in range(-half_len, half_len + 1):
        wk = float(np.exp(-0.5 * (k / sigma_k) ** 2))
        rk = np.clip(np.rint(rows + k * sy).astype(np.int32), 0, h - 1)
        ck = np.clip(np.rint(cols + k * sx).astype(np.int32), 0, w - 1)
        in_fp = foot_f[rk, ck]
        num += wk * valid_field[rk, ck] * in_fp
        den += wk * in_fp
    out = np.zeros((h, w), dtype=np.float32)
    ok = foot & (den > 0)
    out[ok] = num[ok] / den[ok]
    return out


def single_scale_log_flexure(elev: np.ndarray, slope_deg: np.ndarray, foot: np.ndarray,
                             sigma: float, *, s0: float = S0_DEG) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return steered log-flexure, smoothed elevation, and downslope unit vector (uy, ux)."""
    zs = gaussian_filter(elev.astype(np.float32), sigma, mode="nearest")
    gy = gaussian_filter(zs, 1.0, order=(1, 0), mode="nearest")
    gx = gaussian_filter(zs, 1.0, order=(0, 1), mode="nearest")
    mag = np.hypot(gy, gx) + 1e-6
    uy = (-gy / mag).astype(np.float32)
    ux = (-gx / mag).astype(np.float32)

    ss = gaussian_filter(slope_deg.astype(np.float32), sigma, mode="nearest")
    ls = np.log(np.maximum(ss, 0.0) + np.float32(s0)).astype(np.float32)
    ly = gaussian_filter(ls, 1.0, order=(1, 0), mode="nearest")
    lx = gaussian_filter(ls, 1.0, order=(0, 1), mode="nearest")
    d_down = ly * uy + lx * ux
    phi = np.maximum(-d_down, 0.0).astype(np.float32) * piedmont_window(ss)
    phi[~foot] = 0.0
    phi_bar = steered_strike_average(phi, uy, ux, foot)
    return phi_bar, zs, uy, ux


def shoreline_null_weight(z_15: np.ndarray, uy_30: np.ndarray, ux_30: np.ndarray,
                          sub_edge_rank: np.ndarray, foot: np.ndarray,
                          rank_fn: Callable[[np.ndarray, np.ndarray], np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    """Equipotential paleoshoreline survival weight in [0.35, 1.0] and RMS strike delta-z."""
    h, w = z_15.shape
    rows, cols = np.indices((h, w), dtype=np.float32)
    sy = ux_30.astype(np.float32)
    sx = (-uy_30).astype(np.float32)
    sq_sum = np.zeros((h, w), dtype=np.float32)
    cnt = np.zeros((h, w), dtype=np.float32)
    for k in SHORE_OFFSETS_PX:
        rk = np.clip(np.rint(rows + k * sy).astype(np.int32), 0, h - 1)
        ck = np.clip(np.rint(cols + k * sx).astype(np.int32), 0, w - 1)
        in_fp = foot[rk, ck].astype(np.float32)
        diff = (z_15[rk, ck] - z_15) * in_fp
        sq_sum += diff * diff
        cnt += in_fp
    dz_strike = np.zeros((h, w), dtype=np.float32)
    ok = foot & (cnt > 0)
    dz_strike[ok] = np.sqrt(sq_sum[ok] / cnt[ok])

    p_hor = 1.0 - rank_fn(dz_strike, foot)
    c_hor = np.clip((p_hor - 0.60) / 0.40, 0.0, 1.0)
    c_nosub = np.clip((0.55 - sub_edge_rank) / 0.55, 0.0, 1.0)
    m_shore = c_hor * c_nosub
    w_shore = np.ones((h, w), dtype=np.float32)
    w_shore[foot] = (1.0 - 0.65 * m_shore[foot]).astype(np.float32)
    return w_shore, dz_strike


def crest1px(field: np.ndarray, uy_down: np.ndarray, ux_down: np.ndarray,
             foot: np.ndarray, *, off_crest_scale: float = OFF_CREST_SCALE) -> np.ndarray:
    """Strict 1-pixel cross-strike directional non-maximum suppression."""
    h, w = field.shape
    rows, cols = np.indices((h, w), dtype=np.int32)
    dy = np.rint(uy_down).astype(np.int32)
    dx = np.rint(ux_down).astype(np.int32)
    zero = (dy == 0) & (dx == 0)
    dx = np.where(zero, 1, dx)
    rp = np.clip(rows + dy, 0, h - 1)
    cp = np.clip(cols + dx, 0, w - 1)
    rm = np.clip(rows - dy, 0, h - 1)
    cm = np.clip(cols - dx, 0, w - 1)
    f_down = np.where(foot[rp, cp], field[rp, cp], 0.0)
    f_up = np.where(foot[rm, cm], field[rm, cm], 0.0)
    is_crest = foot & (field > 0) & (field >= f_down) & (field > f_up)
    out = np.where(is_crest, field, np.float32(off_crest_scale) * field).astype(np.float32)
    out[~foot] = 0.0
    return out


def coverage_neutral_lidar_toe(step_max: np.ndarray, downface_max: np.ndarray,
                               lidar_valid: np.ndarray, foot: np.ndarray) -> np.ndarray:
    """Within-coverage geometric-mean percentile rank; exact 0.50 outside LiDAR coverage."""
    out = np.where(foot, np.float32(0.50), np.float32(0.0))
    cov = foot & lidar_valid & np.isfinite(step_max) & np.isfinite(downface_max)
    n = int(cov.sum())
    if n < 2:
        return out

    def rank_sub(vals: np.ndarray) -> np.ndarray:
        order = np.argsort(vals, kind="mergesort")
        ranks = np.empty(n, dtype=np.float64)
        ranks[order] = np.arange(n, dtype=np.float64)
        sv = vals[order]
        r_sorted = ranks[order]
        i = 0
        while i < n:
            j = i + 1
            while j < n and sv[j] == sv[i]:
                j += 1
            if j - i > 1:
                r_sorted[i:j] = r_sorted[i:j].mean()
            i = j
        ranks[order] = r_sorted
        return (ranks / max(n - 1, 1)).astype(np.float32)

    rs = np.maximum(rank_sub(step_max[cov].astype(np.float64)), 1e-3)
    rd = np.maximum(rank_sub(downface_max[cov].astype(np.float64)), 1e-3)
    out[cov] = np.sqrt(rs * rd).astype(np.float32)
    return out


def compute_h31aa_fields(
    *,
    elev: np.ndarray,
    slope_deg: np.ndarray,
    iso_grav_hg: np.ndarray,
    depth_base: np.ndarray,
    tmi_hg: np.ndarray,
    tmi_vg: np.ndarray,
    step_max: np.ndarray,
    downface_max: np.ndarray,
    lidar_valid: np.ndarray,
    foot: np.ndarray,
    rank_fn: Callable[[np.ndarray, np.ndarray], np.ndarray],
    gradmag_fn: Callable[[np.ndarray, float], np.ndarray],
    geomean_fn: Callable[[list[np.ndarray]], np.ndarray],
) -> dict[str, np.ndarray]:
    """Compute all raw and crest-thinned H31-AA fields deterministically."""
    phi15, z15, uy15, ux15 = single_scale_log_flexure(elev, slope_deg, foot, 1.5)
    phi30, _z30, uy30, ux30 = single_scale_log_flexure(elev, slope_deg, foot, 3.0)
    f_flex = np.sqrt(np.maximum(phi15, 0.0) * np.maximum(phi30, 0.0)).astype(np.float32)
    f_flex[~foot] = 0.0

    r_grav = rank_fn(np.abs(iso_grav_hg), foot)
    r_base = rank_fn(gradmag_fn(depth_base, 2.0), foot)
    r_asig = rank_fn(np.hypot(tmi_hg, tmi_vg).astype(np.float32), foot)
    sub_edge = geomean_fn([r_grav, r_base, r_asig])
    sub_edge[~foot] = 0.0

    w_shore, dz_strike = shoreline_null_weight(z15, uy30, ux30, sub_edge, foot, rank_fn)
    f_shore = (f_flex * w_shore).astype(np.float32)
    f_shore[~foot] = 0.0

    lidar_toe = coverage_neutral_lidar_toe(step_max, downface_max, lidar_valid, foot)

    raw_aa1 = f_flex
    raw_aa2 = f_shore
    raw_aa3 = (f_shore * (0.65 + 0.35 * sub_edge)).astype(np.float32)
    raw_aa4 = (f_shore * (0.55 + 0.25 * sub_edge + 0.20 * lidar_toe)).astype(np.float32)

    return {
        "LFLEX_COH": rank_fn(crest1px(raw_aa1, uy15, ux15, foot), foot),
        "LFLEX_SHORE": rank_fn(crest1px(raw_aa2, uy15, ux15, foot), foot),
        "SUB_EDGE": sub_edge,
        "LIDAR_TOE": lidar_toe,
        "AA1_crest": rank_fn(crest1px(raw_aa1, uy15, ux15, foot), foot),
        "AA2_crest": rank_fn(crest1px(raw_aa2, uy15, ux15, foot), foot),
        "AA3_crest": rank_fn(crest1px(raw_aa3, uy15, ux15, foot), foot),
        "AA4_crest": rank_fn(crest1px(raw_aa4, uy15, ux15, foot), foot),
        "AA1_nocrest": rank_fn(raw_aa1, foot),
        "AA2_nocrest": rank_fn(raw_aa2, foot),
        "AA3_nocrest": rank_fn(raw_aa3, foot),
        "AA4_nocrest": rank_fn(raw_aa4, foot),
        "w_shore": w_shore,
        "dz_strike": dz_strike,
    }
