"""H31-M label-free subsurface basement-step, phase-tilt & cross-modality concordance channels.

Design frozen in ``knowledge/2026-10-25_h31m_subsurface_concordance_preregistration.md`` before any
fit. Every transform operates strictly on unlabeled geophysical and topographic rasters: invalid /
sentinel cells (``~isfinite`` or ``|x| >= 1e30``) are nearest-neighbor filled only during spatial
differentiation and restored to ``NaN`` in every output channel. No catalogue, SGMC, or survey-mask
flag is accepted anywhere in this module.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import distance_transform_edt, gaussian_filter

SENTINEL_ABS_MAX = 1e30

SUB_BASE_BANDS = [
    "mag_anom", "rtp", "tmi", "tmi_hg", "tmi_vg", "tc", "TMI_up150",
    "iso_grav_anom", "iso_grav_anom_slope", "iso_grav_anom_hg", "iso_grav_anom_vg",
    "depth_to_base_surf", "cond_surf",
    "geod_2ndinv", "geod_shearrate", "geod_dilaterate", "deq_n100a15", "ieq_n100a15",
    "det_elev", "det_elev_slope",
    "K", "Th", "U", "TC", "ThK", "UK", "UTh", "mean_k_500m", "th_minus_k",
]

LIDAR_SCARP_BANDS = [
    "ex_max", "ex_mean", "step_max", "lapneg_max", "lappos_max",
    "downface_max", "upface_max", "cross_max", "relief", "coh100", "upface_minus_downface",
]

H31M_CHANNELS = [
    "bstep_grad_norm",
    "bstep_inflect",
    "grav_tilt_zero",
    "rtp_bandpass_crest",
    "cond_grad_ridge",
    "sub_tensor_coh",
    "surf_piedmont_ridge",
    "xmod_strike_concordance",
]


def _clean_fill(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return (nearest_filled_float32, valid_mask) guarding against finite sentinels."""
    arr = np.asarray(values, dtype=np.float32)
    valid = np.isfinite(arr) & (np.abs(arr) < SENTINEL_ABS_MAX)
    if not valid.any():
        raise ValueError("input band has no valid finite cells")
    if valid.all():
        return arr.copy(), valid
    idx = distance_transform_edt(~valid, return_distances=False, return_indices=True)
    return arr[tuple(idx)].astype(np.float32, copy=False), valid


def _remask(values: np.ndarray, valid: np.ndarray) -> np.ndarray:
    out = np.asarray(values, dtype=np.float32).copy()
    out[~valid] = np.nan
    return out


def _grad_mag(arr: np.ndarray) -> np.ndarray:
    gy, gx = np.gradient(arr.astype(np.float32, copy=False))
    return np.hypot(gy, gx).astype(np.float32)


def _hessian_crest(arr: np.ndarray, sigma: float) -> np.ndarray:
    """2D Hessian linear ridge crest eigenvalue max(0, -lambda_min) at smoothing scale sigma."""
    sm = gaussian_filter(arr.astype(np.float32, copy=False), sigma=float(sigma))
    gy, gx = np.gradient(sm)
    gyy, gyx = np.gradient(gy)
    gxy, gxx = np.gradient(gx)
    tr = gxx + gyy
    det = gxx * gyy - 0.5 * (gxy + gyx) * 0.5 * (gxy + gyx)
    disc = np.sqrt(np.maximum(0.25 * tr * tr - det, 0.0))
    lam_min = 0.5 * tr - disc
    return np.maximum(-lam_min, 0.0).astype(np.float32)


def _iqr_standardize(arr: np.ndarray, valid: np.ndarray) -> np.ndarray:
    vals = arr[valid]
    med = float(np.median(vals))
    q25, q75 = (float(np.percentile(vals, p)) for p in (25.0, 75.0))
    iqr = max(q75 - q25, 1e-6)
    return np.clip((arr - med) / iqr, -10.0, 10.0).astype(np.float32)


def _structure_tensor_orientation(
    arr: np.ndarray,
    valid: np.ndarray,
    *,
    sigma_pre: float = 1.0,
    sigma_int: float = 3.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (coherence, cos_2theta, sin_2theta) from the 2D Gaussian structure tensor.

    Coherence C = ((lambda_1 - lambda_2) / (lambda_1 + lambda_2 + eps))^2 in [0, 1].
    (cos_2theta, sin_2theta) encodes the double-angle principal axis without branch-cut discontinuities.
    """
    sm = gaussian_filter(arr.astype(np.float32, copy=False), sigma=float(sigma_pre))
    gy, gx = np.gradient(sm)
    jxx = gaussian_filter(gx * gx, sigma=float(sigma_int))
    jyy = gaussian_filter(gy * gy, sigma=float(sigma_int))
    jxy = gaussian_filter(gx * gy, sigma=float(sigma_int))

    trace = jxx + jyy
    pos_tr = trace[valid & (trace > 0)]
    eps = (1e-4 * float(np.median(pos_tr)) if pos_tr.size else 0.0) + 1e-12
    diff = jxx - jyy
    two_jxy = 2.0 * jxy
    aniso_sq = diff * diff + two_jxy * two_jxy
    aniso = np.sqrt(aniso_sq + eps * eps)
    coh = np.clip(aniso_sq / ((trace + eps) ** 2), 0.0, 1.0).astype(np.float32)
    c2 = (diff / aniso).astype(np.float32)
    s2 = (two_jxy / aniso).astype(np.float32)
    return coh, c2, s2


def build_h31m_channels(bands: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Compute all 8 frozen H31-M channels from named stack bands."""
    z_base, v_z = _clean_fill(bands["depth_to_base_surf"])
    g_slope, v_gs = _clean_fill(bands["iso_grav_anom_slope"])
    g_vg, v_gv = _clean_fill(bands["iso_grav_anom_vg"])
    rtp, v_rtp = _clean_fill(bands["rtp"])
    cond, v_cond = _clean_fill(bands["cond_surf"])
    det_elev, v_det = _clean_fill(bands["det_elev"])
    det_slope, v_ds = _clean_fill(bands["det_elev_slope"])

    # 1. Scale-invariant fractional basement-throw horizontal gradient & 2. Hessian crest
    z_sm = gaussian_filter(z_base, sigma=1.5)
    bstep_raw = _grad_mag(z_sm) / (np.maximum(z_base, 0.0) + 100.0)
    bstep_inf_raw = _hessian_crest(bstep_raw, sigma=1.2)

    # 3. Miller-Singh / Verduzco gravity tilt-angle zero-crossing ridge
    v_grav = v_gs & v_gv
    pos_gs = g_slope[v_grav & (g_slope > 0)]
    eps_g = 0.01 * float(np.median(pos_gs)) + 1e-6 if pos_gs.size else 1e-4
    theta_g = np.arctan2(g_vg, np.maximum(g_slope, 0.0) + eps_g).astype(np.float32)
    thdr_g = _grad_mag(gaussian_filter(theta_g, sigma=1.0))
    grav_tilt_raw = (np.exp(-np.abs(theta_g) / 0.35) * thdr_g).astype(np.float32)

    # 4. Blakely-Simpson shallow-crustal RTP bandpass horizontal-gradient crest
    rtp_bp = gaussian_filter(rtp, sigma=1.0) - gaussian_filter(rtp, sigma=4.0)
    rtp_crest_raw = _grad_mag(rtp_bp)

    # 5. Subsurface electrical conductance boundary gradient
    cond_grad_raw = _grad_mag(gaussian_filter(cond, sigma=1.5))

    # 6. Multi-field subsurface structure-tensor linear anisotropy coherence (sigma_int = 300 m)
    v_sub = v_z & v_grav & v_rtp & v_cond
    u_sub = (
        _iqr_standardize(bstep_raw, v_z)
        + _iqr_standardize(grav_tilt_raw, v_grav)
        + _iqr_standardize(rtp_crest_raw, v_rtp)
        + _iqr_standardize(cond_grad_raw, v_cond)
    ).astype(np.float32)
    coh_sub, c2_sub, s2_sub = _structure_tensor_orientation(u_sub, v_sub, sigma_pre=0.8, sigma_int=3.0)

    # 7. Piedmont-preserved detrended topographic flexure crest
    v_surf = v_det & v_ds
    surf_crest = _hessian_crest(det_elev, sigma=2.0)
    pied_ridge_raw = (surf_crest / (1.0 + np.maximum(det_slope, 0.0) / 8.0)).astype(np.float32)

    # 8. Cross-modality surface-subsurface structure-tensor strike concordance
    coh_surf, c2_surf, s2_surf = _structure_tensor_orientation(det_elev, v_det, sigma_pre=1.0, sigma_int=3.0)
    cos_2delta = np.clip(c2_surf * c2_sub + s2_surf * s2_sub, -1.0, 1.0)
    xmod_raw = (np.sqrt(coh_surf * coh_sub) * (0.5 * (1.0 + cos_2delta))).astype(np.float32)

    return {
        "bstep_grad_norm": _remask(bstep_raw, v_z),
        "bstep_inflect": _remask(bstep_inf_raw, v_z),
        "grav_tilt_zero": _remask(grav_tilt_raw, v_grav),
        "rtp_bandpass_crest": _remask(rtp_crest_raw, v_rtp),
        "cond_grad_ridge": _remask(cond_grad_raw, v_cond),
        "sub_tensor_coh": _remask(coh_sub, v_sub),
        "surf_piedmont_ridge": _remask(pied_ridge_raw, v_surf),
        "xmod_strike_concordance": _remask(xmod_raw, v_sub & v_det),
    }
