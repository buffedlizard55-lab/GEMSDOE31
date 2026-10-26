"""H31-S (UDAP-SSLIC) physical feature engineering for buried & blind fault discovery.

Implements four physically disjoint groups without touching any banned or catalogue-derived raster:
1. UDAP: Predictor-corrector Up-Dip Basin-Depth Advected Potential-Field projection along -grad(Z_b)
   pulling hanging-wall gravity HGM, basement-step, and upward-continued TMI gradients back to
   their surface subcrop trace across 45/55/65 deg normal-fault dip brackets.
2. HZAD: Strike-orthogonal Hydrothermal Magnetite-Destruction Axial Trough (positive cross-strike
   Laplacian of RTP and TMI_up150) interacted with local K/Th potassic enrichment, shallow
   conductivity clay-cap anomalies, and smooth GDR-1391 thermal/sinter/volcanic context.
3. Geomorphic & Survey-Seam Null Suppressors: Pleistocene contour-parallel shoreline bench index
   and cardinal 0/90 deg raster-seam concentration index.
4. SSLIC: Leak-free Stage-2 Strike-Steered Line-Integral Continuity and cross-strike ridge contrast
   computed strictly from nested OOF Stage-1 physical fault probabilities.
"""

from __future__ import annotations

import gc
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt, gaussian_filter, map_coordinates

BANNED_SUBSTRINGS = ("qfaults_v2", "labels.tif", "sgmc_faults")


def _clean_2d(arr: np.ndarray, footprint: np.ndarray) -> tuple[np.ndarray, float]:
    """Replace non-finite values with the footprint median and return (clean_2d, median)."""
    out = np.asarray(arr, dtype=np.float32).copy()
    valid = footprint & np.isfinite(out)
    med = float(np.median(out[valid])) if np.any(valid) else 0.0
    out[~np.isfinite(out)] = med
    out[~footprint] = med
    return out, med


def _sample_shifted(
    field: np.ndarray,
    dy: np.ndarray,
    dx: np.ndarray,
) -> np.ndarray:
    """Bilinearly sample ``field[r + dy, c + dx]`` with low peak memory."""
    h, w = field.shape
    out = np.empty((h, w), dtype=np.float32)
    chunk = 512
    cols = np.arange(w, dtype=np.float32)[None, :]
    for r0 in range(0, h, chunk):
        r1 = min(h, r0 + chunk)
        rows = np.arange(r0, r1, dtype=np.float32)[:, None]
        coords = np.empty((2, r1 - r0, w), dtype=np.float32)
        coords[0] = np.clip(rows + dy[r0:r1], 0.0, float(h - 1))
        coords[1] = np.clip(cols + dx[r0:r1], 0.0, float(w - 1))
        out[r0:r1] = map_coordinates(field, coords, order=1, mode="nearest")
    return out


def compute_udap_channels(
    depth_to_base_m: np.ndarray,
    grav_slope: np.ndarray,
    tmi_up150: np.ndarray,
    geod_dilat: np.ndarray,
    footprint: np.ndarray,
    *,
    cell_m: float = 100.0,
    max_shift_m: float = 1200.0,
) -> tuple[dict[str, np.ndarray], np.ndarray, np.ndarray]:
    """Compute Up-Dip Basin-Depth Advected Potential-Field (UDAP) 2D channels.

    Returns ``(channels_dict, strike_ty, strike_tx)`` where ``(strike_ty, strike_tx)`` is the
    unit structural strike tangent vector estimated from smoothed basement + gravity structure.
    """
    zb_raw, _ = _clean_2d(depth_to_base_m, footprint)
    zb_pos = np.clip(zb_raw, 0.0, 6000.0)
    zb_smooth = gaussian_filter(zb_pos, sigma=6.0)
    gy, gx = np.gradient(zb_smooth)
    bstep = np.hypot(gy, gx).astype(np.float32)
    norm = np.maximum(bstep, 1e-4)
    # Unit vector pointing down-gradient into the deeper hanging-wall basin
    uy = (gy / norm).astype(np.float32)
    ux = (gx / norm).astype(np.float32)

    # Sample un-attenuated hanging-wall basin depth 6 px (600 m) down-gradient into the basin
    zb_hw = _sample_shifted(zb_pos, 6.0 * uy, 6.0 * ux)
    zb_eff = np.maximum(zb_pos, zb_hw)
    max_px = float(max_shift_m / cell_m)

    g_slope, _ = _clean_2d(grav_slope, footprint)
    tmi150_clean, _ = _clean_2d(tmi_up150, footprint)
    tmi150_smooth = gaussian_filter(tmi150_clean, sigma=2.0)
    ty_m, tx_m = np.gradient(tmi150_smooth)
    tmi150_hg = np.hypot(ty_m, tx_m).astype(np.float32)
    dilat_clean, _ = _clean_2d(geod_dilat, footprint)

    cot55 = float(1.0 / np.tan(np.deg2rad(55.0)))  # ~0.7002
    cot45 = 1.0
    cot65 = float(1.0 / np.tan(np.deg2rad(65.0)))  # ~0.4663

    s55 = np.clip(zb_eff * cot55 / cell_m, 0.0, max_px).astype(np.float32)
    s45 = np.clip(zb_eff * cot45 / cell_m, 0.0, max_px).astype(np.float32)
    s65 = np.clip(zb_eff * cot65 / cell_m, 0.0, max_px).astype(np.float32)

    udap_g55 = _sample_shifted(g_slope, s55 * uy, s55 * ux)
    udap_g45 = _sample_shifted(g_slope, s45 * uy, s45 * ux)
    udap_g65 = _sample_shifted(g_slope, s65 * uy, s65 * ux)
    udap_bstep55 = _sample_shifted(bstep, s55 * uy, s55 * ux)
    udap_tmi150_55 = _sample_shifted(tmi150_hg, s55 * uy, s55 * ux)

    udap_gain55 = (udap_g55 - g_slope).astype(np.float32)
    udap_concord55 = np.sqrt(np.maximum(udap_g55, 0.0) * np.maximum(udap_bstep55, 0.0)).astype(np.float32)
    dilat_pos = np.clip(dilat_clean, 0.0, None)
    udap_dilat = (udap_concord55 * np.log1p(np.maximum(dilat_pos, 0.0) * 100.0)).astype(np.float32)

    # Structural strike tangent from combined basement + gravity slope gradient
    g_smooth = gaussian_filter(g_slope, sigma=4.0)
    ggy, ggx = np.gradient(g_smooth)
    ny = (0.7 * uy + 0.3 * (ggy / np.maximum(np.hypot(ggy, ggx), 1e-4))).astype(np.float32)
    nx = (0.7 * ux + 0.3 * (ggx / np.maximum(np.hypot(ggy, ggx), 1e-4))).astype(np.float32)
    nnorm = np.maximum(np.hypot(ny, nx), 1e-4)
    ny /= nnorm
    nx /= nnorm
    strike_ty = (-nx).astype(np.float32)
    strike_tx = ny.astype(np.float32)

    channels = {
        "udap_grav_slope_55": udap_g55,
        "udap_grav_slope_45": udap_g45,
        "udap_grav_slope_65": udap_g65,
        "udap_bstep_55": udap_bstep55,
        "udap_tmi150_hg_55": udap_tmi150_55,
        "udap_grav_gain_55": udap_gain55,
        "udap_concordance_55": udap_concord55,
        "udap_dilat_coupling": udap_dilat,
    }
    return channels, strike_ty, strike_tx


def compute_hzad_channels(
    rtp: np.ndarray,
    tmi_up150: np.ndarray,
    rad_k: np.ndarray,
    rad_th: np.ndarray,
    cond_surf: np.ndarray,
    thermal_prior: np.ndarray,
    strike_ty: np.ndarray,
    strike_tx: np.ndarray,
    footprint: np.ndarray,
) -> dict[str, np.ndarray]:
    """Compute Hydrothermal Magnetite-Destruction Axial Trough (HZAD) 2D channels."""
    # Fault-normal unit vector perpendicular to strike_t
    ny = strike_tx
    nx = -strike_ty

    rtp_c, _ = _clean_2d(rtp, footprint)
    rtp_s = gaussian_filter(rtp_c, sigma=1.5)
    rtp_p = _sample_shifted(rtp_s, 4.0 * ny, 4.0 * nx)
    rtp_m = _sample_shifted(rtp_s, -4.0 * ny, -4.0 * nx)
    # Positive when RTP has a cross-strike local trough (magnetite destruction zone)
    hzad_rtp_trough = (0.5 * (rtp_p + rtp_m) - rtp_s).astype(np.float32)

    tmi_c, _ = _clean_2d(tmi_up150, footprint)
    tmi_s = gaussian_filter(tmi_c, sigma=2.0)
    tmi_p = _sample_shifted(tmi_s, 5.0 * ny, 5.0 * nx)
    tmi_m = _sample_shifted(tmi_s, -5.0 * ny, -5.0 * nx)
    hzad_tmi150_trough = (0.5 * (tmi_p + tmi_m) - tmi_s).astype(np.float32)

    k_c, _ = _clean_2d(rad_k, footprint)
    th_c, _ = _clean_2d(rad_th, footprint)
    k_over_th = (np.maximum(k_c, 0.0) / (np.maximum(th_c, 0.0) + 5.0)).astype(np.float32)
    hzad_k_th_anom = (k_over_th - gaussian_filter(k_over_th, sigma=40.0)).astype(np.float32)

    cond_c, _ = _clean_2d(cond_surf, footprint)
    hzad_cond_saddle = (cond_c - gaussian_filter(cond_c, sigma=30.0)).astype(np.float32)

    trough_pos = np.log1p(np.maximum(hzad_rtp_trough, 0.0))
    kth_pos = np.maximum(hzad_k_th_anom, 0.0)
    t_prior = np.clip(np.asarray(thermal_prior, dtype=np.float32), 0.0, 3.0)
    hzad_conduit = (trough_pos * (0.25 + kth_pos) * (0.5 + t_prior)).astype(np.float32)

    return {
        "hzad_rtp_axial_trough": hzad_rtp_trough,
        "hzad_tmi150_axial_trough": hzad_tmi150_trough,
        "hzad_k_over_th_anom": hzad_k_th_anom,
        "hzad_cond_saddle": hzad_cond_saddle,
        "hzad_geothermal_conduit": hzad_conduit,
    }


def compute_null_suppressors(
    det_elev: np.ndarray,
    det_slope: np.ndarray,
    footprint: np.ndarray,
) -> dict[str, np.ndarray]:
    """Compute pluvial contour-bench and N-S/E-W survey-seam null-suppressor channels."""
    elev_c, _ = _clean_2d(det_elev, footprint)
    slope_c, _ = _clean_2d(det_slope, footprint)
    elev_s = gaussian_filter(elev_c, sigma=2.0)
    ey, ex = np.gradient(elev_s)
    enorm = np.maximum(np.hypot(ey, ex), 1e-4)
    # Unit tangent along local topographic contour
    cty = (-ex / enorm).astype(np.float32)
    ctx = (ey / enorm).astype(np.float32)

    e_p6 = _sample_shifted(elev_s, 6.0 * cty, 6.0 * ctx)
    e_m6 = _sample_shifted(elev_s, -6.0 * cty, -6.0 * ctx)
    along_contour_disp = (0.5 * (np.abs(e_p6 - elev_s) + np.abs(e_m6 - elev_s))).astype(np.float32)
    # High on horizontal wave-cut pluvial shoreline benches (steep cross-step, flat along-contour)
    null_contour_bench = (np.maximum(slope_c, 0.0) / (along_contour_disp + 1.0)).astype(np.float32)

    # Cardinal 0/90 deg raster/flight-line seam indicator: cos(4 * theta) = +1 on N-S/E-W, -1 on 45 deg
    psi = np.arctan2(ey, ex)
    null_cardinal_seam = (np.cos(4.0 * psi) * np.tanh(enorm / 2.0)).astype(np.float32)

    return {
        "null_contour_bench": null_contour_bench,
        "null_cardinal_seam": null_cardinal_seam,
    }


def compute_sslic_channels(
    prob_stage1: np.ndarray,
    strike_ty: np.ndarray,
    strike_tx: np.ndarray,
    footprint: np.ndarray,
) -> dict[str, np.ndarray]:
    """Compute Stage-2 Strike-Steered Line-Integral Continuity (SSLIC) channels from Stage-1 prob."""
    p = np.where(footprint & np.isfinite(prob_stage1), np.clip(prob_stage1, 0.0, 1.0), 0.0).astype(np.float32)
    # Smooth topographic/probabilistic ridge structure tensor to refine local strike
    ps = gaussian_filter(p, sigma=2.0)
    py, px = np.gradient(ps)
    pnorm = np.hypot(py, px)
    # Blend probabilistic ridge tangent (-px, py) where strong with physical strike (strike_ty, strike_tx)
    w_prob = np.clip(pnorm / (np.percentile(pnorm[footprint], 85) + 1e-5), 0.0, 0.65).astype(np.float32)
    pty = -px / np.maximum(pnorm, 1e-5)
    ptx = py / np.maximum(pnorm, 1e-5)
    # Align sign of pty/ptx with strike_ty/strike_tx before blending
    dot = pty * strike_ty + ptx * strike_tx
    pty = np.where(dot < 0.0, -pty, pty)
    ptx = np.where(dot < 0.0, -ptx, ptx)
    ty = ((1.0 - w_prob) * strike_ty + w_prob * pty).astype(np.float32)
    tx = ((1.0 - w_prob) * strike_tx + w_prob * ptx).astype(np.float32)
    tnorm = np.maximum(np.hypot(ty, tx), 1e-4)
    ty /= tnorm
    tx /= tnorm
    ny = tx
    nx = -ty

    p_p4 = _sample_shifted(p, 4.0 * ty, 4.0 * tx)
    p_m4 = _sample_shifted(p, -4.0 * ty, -4.0 * tx)
    p_p8 = _sample_shifted(p, 8.0 * ty, 8.0 * tx)
    p_m8 = _sample_shifted(p, -8.0 * ty, -8.0 * tx)
    p_p16 = _sample_shifted(p, 16.0 * ty, 16.0 * tx)
    p_m16 = _sample_shifted(p, -16.0 * ty, -16.0 * tx)

    mean_400 = ((p + p_p4 + p_m4) / 3.0).astype(np.float32)
    pos_800 = 0.5 * (p_p4 + p_p8)
    neg_800 = 0.5 * (p_m4 + p_m8)
    mean_800 = ((p + p_p4 + p_m4 + p_p8 + p_m8) / 5.0).astype(np.float32)
    mean_1600 = ((p + p_p4 + p_m4 + p_p8 + p_m8 + p_p16 + p_m16) / 7.0).astype(np.float32)
    bilateral_min_800 = np.minimum(pos_800, neg_800).astype(np.float32)

    p_n5p = _sample_shifted(p, 5.0 * ny, 5.0 * nx)
    p_n5m = _sample_shifted(p, -5.0 * ny, -5.0 * nx)
    cross_contrast_500 = (p - 0.5 * (p_n5p + p_n5m)).astype(np.float32)
    aniso_ratio = (mean_800 / (0.5 * (p_n5p + p_n5m) + 0.05)).astype(np.float32)

    return {
        "sslic_prob_raw": p,
        "sslic_mean_400m": mean_400,
        "sslic_mean_800m": mean_800,
        "sslic_mean_1600m": mean_1600,
        "sslic_bilateral_min_800m": bilateral_min_800,
        "sslic_cross_contrast_500m": cross_contrast_500,
        "sslic_aniso_ratio": aniso_ratio,
    }


def _read_u8_clean(path: Path, band: int, footprint: np.ndarray, *, zero_is_nodata: bool = True) -> np.ndarray:
    name_low = str(path).lower()
    if any(b in name_low for b in BANNED_SUBSTRINGS):
        raise ValueError(f"Refusing to load banned or label-derived raster: {path}")
    with rasterio.open(path) as ds:
        raw = ds.read(band).astype(np.float32)
    if zero_is_nodata:
        raw[raw == 0.0] = np.nan
    raw[raw == 255.0] = np.nan
    clean, _ = _clean_2d(raw, footprint)
    return clean


def _gdr_proximity(path: Path, footprint: np.ndarray, scale_px: float) -> np.ndarray:
    name_low = str(path).lower()
    if any(b in name_low for b in BANNED_SUBSTRINGS):
        raise ValueError(f"Refusing to load banned or label-derived raster: {path}")
    with rasterio.open(path) as ds:
        raw = ds.read(1)
    hits = footprint & (raw > 0) & (raw != 255)
    if not np.any(hits):
        return np.zeros(footprint.shape, dtype=np.float32)
    dist_px = distance_transform_edt(~hits).astype(np.float32)
    return np.exp(-dist_px / float(scale_px)).astype(np.float32)


def build_h31s_stage1_stack(
    cache_dir: Path,
    external_dir: Path,
    footprint: np.ndarray,
) -> tuple[np.ndarray, list[str], np.ndarray, np.ndarray]:
    """Assemble the footprint-indexed (n_features, n_fp) Stage-1 physical feature matrix.

    Returns ``(x_fp, feature_names, strike_ty, strike_tx)`` with peak memory < 1.5 GiB.
    """
    fp = np.asarray(footprint, dtype=bool)
    fi = np.flatnonzero(fp.ravel())
    n_fp = int(fi.size)

    # 19 base bands + 8 GeoDAWN + 5 LiDAR + 3 GDR proximity + 8 UDAP + 5 HZAD + 2 Null = 50 features
    names: list[str] = []
    cols: list[np.ndarray] = []

    band_Cache: dict[int, np.ndarray] = {}
    keep_2d = {2, 5, 8, 12, 15, 17, 19}
    for b in range(1, 20):
        arr = np.load(cache_dir / f"band-{b:02d}.npy")
        clean, _ = _clean_2d(arr, fp)
        del arr
        names.append(f"base_band_{b:02d}")
        cols.append(clean.ravel()[fi].astype(np.float32, copy=True))
        if b in keep_2d:
            band_Cache[b] = clean
        else:
            del clean

    rad_path = external_dir / "geodawn_rad_u8.tif"
    ext_path = external_dir / "geodawn_extensions_u8.tif"
    lidar_path = external_dir / "lidar_scarp_features_u8.tif"

    rad_k = _read_u8_clean(rad_path, 1, fp)
    rad_th = _read_u8_clean(rad_path, 2, fp)
    rad_u = _read_u8_clean(rad_path, 3, fp)
    rad_tc = _read_u8_clean(rad_path, 4, fp)
    for nm, a in [("geodawn_K", rad_k), ("geodawn_Th", rad_th), ("geodawn_U", rad_u), ("geodawn_TC", rad_tc)]:
        names.append(nm)
        cols.append(a.ravel()[fi].astype(np.float32, copy=True))
    del rad_u, rad_tc

    ext_thk = _read_u8_clean(ext_path, 1, fp)
    ext_uk = _read_u8_clean(ext_path, 2, fp)
    ext_uth = _read_u8_clean(ext_path, 3, fp)
    tmi_up150 = _read_u8_clean(ext_path, 4, fp)
    for nm, a in [("geodawn_ThK", ext_thk), ("geodawn_UK", ext_uk), ("geodawn_UTh", ext_uth), ("geodawn_TMI_up150", tmi_up150)]:
        names.append(nm)
        cols.append(a.ravel()[fi].astype(np.float32, copy=True))
    del ext_thk, ext_uk, ext_uth

    lid_ex = _read_u8_clean(lidar_path, 1, fp)
    lid_step = _read_u8_clean(lidar_path, 3, fp)
    lid_down = _read_u8_clean(lidar_path, 6, fp)
    lid_up = _read_u8_clean(lidar_path, 7, fp)
    lid_cross = _read_u8_clean(lidar_path, 8, fp)
    lid_relief = _read_u8_clean(lidar_path, 9, fp)
    lid_coh = _read_u8_clean(lidar_path, 10, fp)
    lid_asym = (np.abs(lid_up - lid_down) / (lid_cross + 5.0)).astype(np.float32)
    for nm, a in [
        ("lidar_ex_max", lid_ex),
        ("lidar_step_max", lid_step),
        ("lidar_relief", lid_relief),
        ("lidar_coh100", lid_coh),
        ("lidar_face_asym", lid_asym),
    ]:
        names.append(nm)
        cols.append(a.ravel()[fi].astype(np.float32, copy=True))
    del lid_ex, lid_step, lid_down, lid_up, lid_cross, lid_relief, lid_coh, lid_asym
    gc.collect()

    prox_probes = _gdr_proximity(external_dir / "derived_gdr_2m_probes_100m_u8.tif", fp, scale_px=50.0)
    prox_paleo = _gdr_proximity(external_dir / "derived_gdr_paleo_100m_u8.tif", fp, scale_px=60.0)
    prox_volc = _gdr_proximity(external_dir / "derived_gdr_volcanics_100m_u8.tif", fp, scale_px=80.0)
    for nm, a in [("gdr_2m_probe_prox", prox_probes), ("gdr_paleo_prox", prox_paleo), ("gdr_volcanics_prox", prox_volc)]:
        names.append(nm)
        cols.append(a.ravel()[fi].astype(np.float32, copy=True))
    thermal_prior = (prox_probes + prox_paleo + 0.5 * prox_volc).astype(np.float32)
    del prox_probes, prox_paleo, prox_volc

    udap_dict, strike_ty, strike_tx = compute_udap_channels(
        band_Cache[15],
        band_Cache[5],
        tmi_up150,
        band_Cache[8],
        fp,
    )
    for nm, a in udap_dict.items():
        names.append(nm)
        cols.append(a.ravel()[fi].astype(np.float32, copy=True))
    del udap_dict
    gc.collect()

    hzad_dict = compute_hzad_channels(
        band_Cache[2],
        tmi_up150,
        rad_k,
        rad_th,
        band_Cache[17],
        thermal_prior,
        strike_ty,
        strike_tx,
        fp,
    )
    for nm, a in hzad_dict.items():
        names.append(nm)
        cols.append(a.ravel()[fi].astype(np.float32, copy=True))
    del hzad_dict, rad_k, rad_th, tmi_up150, thermal_prior
    gc.collect()

    null_dict = compute_null_suppressors(band_Cache[12], band_Cache[19], fp)
    for nm, a in null_dict.items():
        names.append(nm)
        cols.append(a.ravel()[fi].astype(np.float32, copy=True))
    del null_dict, band_Cache
    gc.collect()

    x_fp = np.empty((len(cols), n_fp), dtype=np.float32)
    for i, col in enumerate(cols):
        x_fp[i] = col
    del cols
    gc.collect()
    return x_fp, names, strike_ty, strike_tx
