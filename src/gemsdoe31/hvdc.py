"""H31-HVDC: Hydrothermal-Vent & Dilational Accommodation Conduit feature builder and models.

Implements the preregistered single-lane architecture in
``knowledge/2026-10-25_h31_hvdc_preregistration.md`` with streaming disk-backed memory discipline
(< 700 MB peak RSS on zero-swap 3.8 GiB containers).
"""

from __future__ import annotations

import gc
import json
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import (
    distance_transform_edt,
    gaussian_filter,
    maximum_filter,
    minimum_filter,
)

from .raster import SHAPE, connected_components

FORBIDDEN_PREPARED_BANDS = frozenset({"valid", "dist_cat_km", "dist_sgmc_km"})

CLEAN_BASELINE_BANDS: tuple[str, ...] = (
    # 19 competition bands
    "mag_anom", "rtp", "tmi_hg", "geod_2ndinv", "iso_grav_anom_slope", "tc", "geod_shearrate",
    "geod_dilaterate", "tmi_vg", "deq_n100a15", "iso_grav_anom_vg", "det_elev", "iso_grav_anom",
    "tmi", "depth_to_base_surf", "ieq_n100a15", "cond_surf", "iso_grav_anom_hg", "det_elev_slope",
    # 11 LiDAR bands (strictly excluding 'valid')
    "ex_max", "ex_mean", "step_max", "lapneg_max", "lappos_max", "downface_max",
    "upface_max", "cross_max", "relief", "coh100", "strike",
    # 4 GeoDAWN radiometric + 4 GeoDAWN extension bands
    "K", "Th", "U", "TC",
    "ThK", "UK", "UTh", "TMI_up150",
)

HVDC_DERIVED_NAMES: tuple[str, ...] = (
    "hvdc_rtp_trough_s2_s8",
    "hvdc_mag_upward_resid",
    "hvdc_k_th_alteration",
    "hvdc_alteration_x_demag",
    "hvdc_cond_grad_log",
    "hvdc_vent_corridor_3km",
    "hvdc_probe_sinter_corridor_3km",
    "hvdc_vent_strike_concordance",
    "hvdc_elev_dog_1_4",
    "hvdc_elev_hessian_ridge",
    "hvdc_piedmont_belt_curv",
    "hvdc_basement_grav_step",
    "hvdc_transtension_index",
    "hvdc_lidar_scarp_norm",
)

FOLD_VISIBLE_NAMES: tuple[str, ...] = (
    "vis_tip_horsetail_lobe",
    "vis_relay_bridge",
    "vis_vent_tip_bridge",
)


def _nan_smooth(arr: np.ndarray, sigma: float, footprint: np.ndarray) -> np.ndarray:
    """Normalized Gaussian convolution that ignores NaNs without bleeding outside-footprint zeros."""
    valid = np.isfinite(arr) & footprint
    filled = np.where(valid, arr, 0.0).astype(np.float32)
    weights = valid.astype(np.float32)
    num = gaussian_filter(filled, sigma=sigma, mode="nearest")
    den = gaussian_filter(weights, sigma=sigma, mode="nearest")
    del filled, weights
    out = np.full(arr.shape, np.nan, dtype=np.float32)
    ok = footprint & (den > 1e-4)
    out[ok] = (num[ok] / den[ok]).astype(np.float32)
    return out


def _robust_zscore(arr: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Median/IQR z-score computed over footprint pixels only."""
    valid = mask & np.isfinite(arr)
    if not valid.any():
        return np.zeros(arr.shape, dtype=np.float32)
    vals = arr[valid]
    med = float(np.median(vals))
    q25, q75 = np.percentile(vals, [25.0, 75.0])
    scale = float(q75 - q25) / 1.349
    if scale <= 1e-8:
        scale = float(np.std(vals)) + 1e-6
    out = np.full(arr.shape, np.nan, dtype=np.float32)
    out[valid] = np.clip((arr[valid] - med) / scale, -8.0, 8.0).astype(np.float32)
    return out


def _unit_rank_clip(arr: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Smooth [0, 1] scale mapping [p05, p99] of finite values in mask."""
    valid = mask & np.isfinite(arr)
    out = np.full(arr.shape, np.nan, dtype=np.float32)
    if not valid.any():
        return out
    lo, hi = np.percentile(arr[valid], [5.0, 99.0])
    span = float(hi - lo) if float(hi - lo) > 1e-8 else 1.0
    out[valid] = np.clip((arr[valid] - float(lo)) / span, 0.0, 1.0).astype(np.float32)
    return out


def _grad_mag(arr: np.ndarray, footprint: np.ndarray, sigma: float = 1.5) -> np.ndarray:
    sm = _nan_smooth(arr, sigma=sigma, footprint=footprint)
    med = float(np.nanmedian(sm[footprint]))
    fill = np.where(np.isfinite(sm), sm, med).astype(np.float32)
    gy, gx = np.gradient(fill)
    del fill
    mag = np.hypot(gx, gy).astype(np.float32)
    mag[~footprint | ~np.isfinite(sm)] = np.nan
    return mag


def _read_prep_band(prep_file: Path, band_idx: int, footprint: np.ndarray) -> np.ndarray:
    """Read a single (3730, 3292) float32 slice via pread/seek without holding a 2.3 GB memmap."""
    n_px = SHAPE[0] * SHAPE[1]
    with prep_file.open("rb") as f:
        f.seek(band_idx * n_px * 4)
        arr = np.fromfile(f, dtype=np.float32, count=n_px).reshape(SHAPE)
    arr[(~np.isfinite(arr)) | (np.abs(arr) >= 1e30) | (~footprint)] = np.nan
    return arr


def _write_foot_row(f_out, row_idx: int, n_foot: int, arr2d: np.ndarray, foot_idx: np.ndarray) -> None:
    vec = arr2d.ravel()[foot_idx].astype(np.float32, copy=True)
    vec[~np.isfinite(vec)] = np.nan
    f_out.seek(row_idx * n_foot * 4)
    vec.tofile(f_out)


def build_hvdc_feature_cache(
    data_dir: Path,
    prepared_dir: Path,
    cache_dir: Path,
) -> dict:
    """Build disk-backed float32 footprint-indexed feature cache ``(n_features, 5_167_373)``.

    Streams via file offsets (no multi-GB dirty mmap) so peak RSS stays < 650 MB.
    Never touches ``labels.tif`` or ``derived_sgmc_faults_100m_u8.tif``.
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    meta_path = cache_dir / "hvdc_cache.json"
    matrix_path = cache_dir / "hvdc_foot_features.f32"
    struct_path = cache_dir / "hvdc_struct_aux.npz"
    prep_file = prepared_dir / "features.f32"

    prep_meta = json.loads((prepared_dir / "features.json").read_text())
    band_names: list[str] = prep_meta["bands"]
    for forbidden in FORBIDDEN_PREPARED_BANDS:
        if forbidden in CLEAN_BASELINE_BANDS:
            raise AssertionError(f"forbidden band {forbidden} in CLEAN_BASELINE_BANDS")

    with rasterio.open(data_dir / "sample_submission.tif") as src:
        footprint = np.isfinite(src.read(1))
    foot_idx = np.flatnonzero(footprint.ravel())
    n_foot = int(foot_idx.size)

    all_names = list(CLEAN_BASELINE_BANDS) + list(HVDC_DERIVED_NAMES)
    if meta_path.is_file() and matrix_path.is_file() and struct_path.is_file():
        existing = json.loads(meta_path.read_text())
        expected_bytes = len(all_names) * n_foot * 4
        if existing.get("feature_names") == all_names and matrix_path.stat().st_size == expected_bytes:
            return existing

    bmap = {name: i for i, name in enumerate(band_names)}
    name_to_row = {name: i for i, name in enumerate(all_names)}

    def read_b(name: str) -> np.ndarray:
        assert name not in FORBIDDEN_PREPARED_BANDS
        return _read_prep_band(prep_file, bmap[name], footprint)

    with matrix_path.open("wb") as f_out:
        # 1. Stream 38 clean sensor bands one band at a time (~50 MB peak)
        for out_i, bname in enumerate(CLEAN_BASELINE_BANDS):
            arr = read_b(bname)
            _write_foot_row(f_out, out_i, n_foot, arr, foot_idx)
            del arr
        gc.collect()

        # 2. Hydrothermal alteration & magnetite-destruction channels
        rtp = read_b("rtp")
        rtp_s15 = _nan_smooth(rtp, sigma=1.5, footprint=footprint)
        rtp_s80 = _nan_smooth(rtp, sigma=8.0, footprint=footprint)
        rtp_trough = np.where(
            np.isfinite(rtp_s15) & np.isfinite(rtp_s80),
            np.maximum(0.0, rtp_s80 - rtp_s15),
            np.nan,
        ).astype(np.float32)
        del rtp_s15, rtp_s80
        _write_foot_row(f_out, name_to_row["hvdc_rtp_trough_s2_s8"], n_foot, rtp_trough, foot_idx)

        tmi_up150 = read_b("TMI_up150")
        mag_up_resid = (_robust_zscore(rtp, footprint) - _robust_zscore(tmi_up150, footprint)).astype(np.float32)
        del tmi_up150
        _write_foot_row(f_out, name_to_row["hvdc_mag_upward_resid"], n_foot, mag_up_resid, foot_idx)
        del mag_up_resid

        k_band = read_b("K")
        th_band = read_b("Th")
        thk_band = read_b("ThK")
        valid_rad = np.isfinite(k_band) & np.isfinite(th_band) & footprint
        k_over_th = np.full(SHAPE, np.nan, dtype=np.float32)
        k_over_th[valid_rad] = k_band[valid_rad] / (th_band[valid_rad] + 5.0)
        del k_band, th_band, valid_rad
        valid_thk = np.isfinite(thk_band) & footprint
        kth_comp = np.where(
            valid_thk,
            _robust_zscore(k_over_th, footprint) - 0.5 * _robust_zscore(thk_band, footprint),
            np.nan,
        ).astype(np.float32)
        del k_over_th, thk_band, valid_thk
        k_th_alt = (
            _nan_smooth(kth_comp, sigma=1.5, footprint=footprint)
            - _nan_smooth(kth_comp, sigma=10.0, footprint=footprint)
        ).astype(np.float32)
        del kth_comp
        _write_foot_row(f_out, name_to_row["hvdc_k_th_alteration"], n_foot, k_th_alt, foot_idx)

        demag_u = _unit_rank_clip(rtp_trough, footprint)
        del rtp_trough
        kalt_u = _unit_rank_clip(np.maximum(0.0, np.nan_to_num(k_th_alt, nan=0.0)), footprint)
        kalt_u[~np.isfinite(k_th_alt)] = np.nan
        del k_th_alt
        alt_x_demag = np.sqrt(np.clip(demag_u * kalt_u, 0.0, 1.0)).astype(np.float32)
        del demag_u, kalt_u
        _write_foot_row(f_out, name_to_row["hvdc_alteration_x_demag"], n_foot, alt_x_demag, foot_idx)
        del alt_x_demag
        gc.collect()

        cond_surf = read_b("cond_surf")
        log_cond = np.where(
            np.isfinite(cond_surf) & footprint,
            np.log1p(np.maximum(0.0, cond_surf)),
            np.nan,
        ).astype(np.float32)
        del cond_surf
        cond_grad = _grad_mag(log_cond, footprint, sigma=2.0)
        del log_cond
        _write_foot_row(f_out, name_to_row["hvdc_cond_grad_log"], n_foot, cond_grad, foot_idx)
        del cond_grad
        gc.collect()

        # 3. Geothermal Vent, 2 m Probe & Paleo-Sinter Structural Corridors + Strike Concordance
        with rasterio.open(data_dir / "external/derived_gdr_volcanics_100m_u8.tif") as src:
            volc = (src.read(1) > 0) & footprint
        with rasterio.open(data_dir / "external/derived_gdr_2m_probes_100m_u8.tif") as src:
            probes = (src.read(1) > 0) & footprint
        with rasterio.open(data_dir / "external/derived_gdr_paleo_100m_u8.tif") as src:
            paleo = (src.read(1) > 0) & footprint

        d_vent_km = (distance_transform_edt(~volc, sampling=100.0) / 1000.0).astype(np.float32)
        vent_corridor = np.exp(-d_vent_km / 3.0).astype(np.float32)
        del d_vent_km
        vent_corridor[~footprint] = np.nan
        _write_foot_row(f_out, name_to_row["hvdc_vent_corridor_3km"], n_foot, vent_corridor, foot_idx)

        upflow_mask = probes | paleo
        d_ps_km = (distance_transform_edt(~upflow_mask, sampling=100.0) / 1000.0).astype(np.float32)
        probe_sinter_corridor = np.exp(-d_ps_km / 3.0).astype(np.float32)
        del d_ps_km
        probe_sinter_corridor[~footprint] = np.nan
        _write_foot_row(
            f_out, name_to_row["hvdc_probe_sinter_corridor_3km"], n_foot, probe_sinter_corridor, foot_idx
        )

        upflow_combined_foot = np.maximum(
            np.nan_to_num(vent_corridor.ravel()[foot_idx], nan=0.0),
            np.nan_to_num(probe_sinter_corridor.ravel()[foot_idx], nan=0.0),
        ).astype(np.float32)
        del vent_corridor, probe_sinter_corridor

        any_upflow = volc | upflow_mask
        del volc, probes, paleo, upflow_mask
        d_any_upflow = (distance_transform_edt(~any_upflow, sampling=100.0) / 1000.0).astype(np.float32)
        del any_upflow
        uy, ux = np.gradient(d_any_upflow)
        unorm = np.hypot(ux, uy) + 1e-6
        rad_tx = (ux / unorm).astype(np.float32)
        rad_ty = (uy / unorm).astype(np.float32)
        del ux, uy, unorm

        det_elev = read_b("det_elev")
        iso_grav = read_b("iso_grav_anom")
        j_xx = np.zeros(SHAPE, dtype=np.float32)
        j_yy = np.zeros(SHAPE, dtype=np.float32)
        j_xy = np.zeros(SHAPE, dtype=np.float32)
        for field_arr, weight in ((det_elev, 1.0), (iso_grav, 0.8), (rtp, 0.6)):
            sm = _nan_smooth(_robust_zscore(field_arr, footprint), sigma=2.0, footprint=footprint)
            sm_fill = np.nan_to_num(sm, nan=0.0)
            del sm
            gy, gx = np.gradient(sm_fill)
            del sm_fill
            j_xx += weight * gaussian_filter(gx * gx, sigma=3.0)
            j_yy += weight * gaussian_filter(gy * gy, sigma=3.0)
            j_xy += weight * gaussian_filter(gx * gy, sigma=3.0)
            del gx, gy
        del iso_grav, rtp
        grad_angle = 0.5 * np.arctan2(2.0 * j_xy, j_xx - j_yy)
        del j_xx, j_yy, j_xy
        struct_tx = (-np.sin(grad_angle)).astype(np.float32)
        struct_ty = np.cos(grad_angle).astype(np.float32)
        del grad_angle

        cos_align = struct_tx * rad_tx + struct_ty * rad_ty
        del rad_tx, rad_ty
        vent_strike_concordance = ((cos_align * cos_align) * np.exp(-d_any_upflow / 5.0)).astype(np.float32)
        del cos_align, d_any_upflow
        vent_strike_concordance[~footprint] = np.nan
        _write_foot_row(
            f_out, name_to_row["hvdc_vent_strike_concordance"], n_foot, vent_strike_concordance, foot_idx
        )
        del vent_strike_concordance

        struct_tx_foot = struct_tx.ravel()[foot_idx].astype(np.float32, copy=True)
        struct_ty_foot = struct_ty.ravel()[foot_idx].astype(np.float32, copy=True)
        del struct_tx, struct_ty
        gc.collect()

        # 4. Full-footprint Piedmont Concealment-Belt, Basement-Gravity Step & Transtension
        elev_s1 = _nan_smooth(det_elev, sigma=1.0, footprint=footprint)
        elev_s4 = _nan_smooth(det_elev, sigma=4.0, footprint=footprint)
        elev_dog = (elev_s1 - elev_s4).astype(np.float32)
        del elev_s4
        _write_foot_row(f_out, name_to_row["hvdc_elev_dog_1_4"], n_foot, elev_dog, foot_idx)
        del elev_dog

        elev_fill = np.where(np.isfinite(elev_s1), elev_s1, 0.0).astype(np.float32)
        del elev_s1
        egy, egx = np.gradient(elev_fill)
        del elev_fill
        ehyy, ehyx = np.gradient(egy)
        del egy
        ehxy, ehxx = np.gradient(egx)
        del egx
        ehxy = 0.5 * (ehxy + ehyx)
        del ehyx
        etmp = np.sqrt(((ehxx - ehyy) * 0.5) ** 2 + ehxy * ehxy)
        del ehxy
        lam_min = 0.5 * (ehxx + ehyy) - etmp
        del etmp
        elev_hessian_ridge = np.maximum(0.0, -lam_min).astype(np.float32)
        del lam_min
        elev_hessian_ridge[~footprint | ~np.isfinite(det_elev)] = np.nan
        del det_elev
        _write_foot_row(f_out, name_to_row["hvdc_elev_hessian_ridge"], n_foot, elev_hessian_ridge, foot_idx)

        elev_slope = read_b("det_elev_slope")
        depth_base = read_b("depth_to_base_surf")
        valid_pied = footprint & np.isfinite(elev_slope) & np.isfinite(depth_base) & np.isfinite(elev_hessian_ridge)
        del elev_hessian_ridge
        s_med = float(np.median(elev_slope[valid_pied]))
        s_iqr = float(np.percentile(elev_slope[valid_pied], 75) - np.percentile(elev_slope[valid_pied], 25)) + 1e-5
        piedmont_weight = np.exp(-0.5 * ((elev_slope - s_med) / s_iqr) ** 2)
        del elev_slope
        piedmont_belt_curv = np.where(
            valid_pied,
            np.hypot(ehxx, ehyy) * piedmont_weight * np.log1p(np.maximum(0.0, depth_base)),
            np.nan,
        ).astype(np.float32)
        del ehxx, ehyy, piedmont_weight, valid_pied
        _write_foot_row(f_out, name_to_row["hvdc_piedmont_belt_curv"], n_foot, piedmont_belt_curv, foot_idx)
        del piedmont_belt_curv

        grav_hg = read_b("iso_grav_anom_hg")
        depth_grad = _grad_mag(depth_base, footprint, sigma=2.0)
        del depth_base
        basement_grav_step = (
            _unit_rank_clip(depth_grad, footprint) * _unit_rank_clip(np.abs(grav_hg), footprint)
        ).astype(np.float32)
        del depth_grad, grav_hg
        _write_foot_row(f_out, name_to_row["hvdc_basement_grav_step"], n_foot, basement_grav_step, foot_idx)
        del basement_grav_step

        shear = read_b("geod_shearrate")
        dilat = read_b("geod_dilaterate")
        ieq = read_b("ieq_n100a15")
        transtension = (
            _unit_rank_clip(shear, footprint)
            * _unit_rank_clip(np.maximum(0.0, dilat), footprint)
            * _unit_rank_clip(np.log1p(np.maximum(0.0, ieq)), footprint)
        ).astype(np.float32)
        del shear, dilat, ieq
        _write_foot_row(f_out, name_to_row["hvdc_transtension_index"], n_foot, transtension, foot_idx)
        del transtension

        # 5. Coverage-deconfounded within-LiDAR scarp composite (strictly NaN outside LiDAR)
        step_max = read_b("step_max")
        coh100 = read_b("coh100")
        upface = read_b("upface_max")
        downface = read_b("downface_max")
        lidar_cov = footprint & np.isfinite(step_max) & np.isfinite(coh100)
        lidar_scarp_norm = np.full(SHAPE, np.nan, dtype=np.float32)
        if lidar_cov.any():
            s_u = _unit_rank_clip(step_max, lidar_cov)
            c_u = _unit_rank_clip(coh100, lidar_cov)
            asym_u = _unit_rank_clip(np.abs(upface - downface), lidar_cov)
            lidar_scarp_norm[lidar_cov] = (
                0.50 * s_u[lidar_cov] + 0.30 * c_u[lidar_cov] + 0.20 * asym_u[lidar_cov]
            ).astype(np.float32)
            del s_u, c_u, asym_u
        del step_max, coh100, upface, downface, lidar_cov
        _write_foot_row(f_out, name_to_row["hvdc_lidar_scarp_norm"], n_foot, lidar_scarp_norm, foot_idx)
        del lidar_scarp_norm
        f_out.flush()
    gc.collect()

    np.savez_compressed(
        struct_path,
        upflow_combined=upflow_combined_foot,
        struct_tx=struct_tx_foot,
        struct_ty=struct_ty_foot,
    )

    lidar_set = {
        "ex_max", "ex_mean", "step_max", "lapneg_max", "lappos_max", "downface_max",
        "upface_max", "cross_max", "relief", "coh100", "strike", "hvdc_lidar_scarp_norm",
    }
    fullfoot_cols = [i for i, n in enumerate(all_names) if n not in lidar_set]
    multisensor_cols = list(range(len(all_names)))
    baseline_cols = list(range(len(CLEAN_BASELINE_BANDS)))

    meta = {
        "schema_version": 1,
        "shape_2d": list(SHAPE),
        "footprint_pixels": n_foot,
        "feature_names": all_names,
        "baseline_cols": baseline_cols,
        "fullfoot_specialist_cols": fullfoot_cols,
        "multisensor_specialist_cols": multisensor_cols,
        "forbidden_excluded": sorted(FORBIDDEN_PREPARED_BANDS),
        "bytes": int(matrix_path.stat().st_size),
    }
    meta_path.write_text(json.dumps(meta, indent=2) + "\n")
    return meta


def build_fold_visible_accommodation(
    visible_faults: np.ndarray,
    footprint: np.ndarray,
    upflow_foot: np.ndarray,
    struct_tx_foot: np.ndarray,
    struct_ty_foot: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute Group II structural accommodation features strictly from ``visible_faults``."""
    vis = np.asarray(visible_faults, dtype=bool) & footprint
    foot_idx = np.flatnonzero(footprint.ravel())
    n_foot = int(foot_idx.size)
    if not vis.any():
        return np.zeros((3, n_foot), dtype=np.float32), np.full(SHAPE, 1e4, dtype=np.float32)

    comp = connected_components(vis)
    n_comp = int(comp.max())

    d_vis_f64, nearest_rc = distance_transform_edt(~vis, return_distances=True, return_indices=True)
    d_vis_px = d_vis_f64.astype(np.float32)
    del d_vis_f64
    owner = comp[nearest_rc[0], nearest_rc[1]]
    del nearest_rc
    far_mask = (d_vis_px > 2.0) & footprint

    max_own = maximum_filter(owner, size=5)
    min_own = minimum_filter(owner, size=5)
    seam = (max_own != min_own) & (d_vis_px <= 22.0) & (d_vis_px >= 1.5) & footprint
    del owner, max_own, min_own
    relay_raw = seam.astype(np.float32) * np.exp(-d_vis_px / 10.0).astype(np.float32)
    del seam
    relay_smooth = gaussian_filter(relay_raw, sigma=2.5).astype(np.float32)
    del relay_raw
    if float(relay_smooth.max()) > 1e-8:
        p99 = float(np.percentile(relay_smooth[footprint], 99.5))
        relay_smooth = np.clip(relay_smooth / max(p99, 1e-6), 0.0, 1.0)
    relay_smooth[~far_mask] = 0.0
    rl_foot = relay_smooth.ravel()[foot_idx].astype(np.float32, copy=True)
    del relay_smooth

    ys, xs = np.nonzero(vis)
    cids = comp[ys, xs]
    del comp
    counts = np.bincount(cids, minlength=n_comp + 1).astype(np.float64)
    sum_y = np.bincount(cids, weights=ys, minlength=n_comp + 1)
    sum_x = np.bincount(cids, weights=xs, minlength=n_comp + 1)
    valid_c = counts >= 5.0
    mean_y = np.divide(sum_y, np.maximum(counts, 1.0))
    mean_x = np.divide(sum_x, np.maximum(counts, 1.0))

    dy = ys - mean_y[cids]
    dx = xs - mean_x[cids]
    s_xx = np.bincount(cids, weights=dx * dx, minlength=n_comp + 1)
    s_yy = np.bincount(cids, weights=dy * dy, minlength=n_comp + 1)
    s_xy = np.bincount(cids, weights=dx * dy, minlength=n_comp + 1)
    theta = 0.5 * np.arctan2(2.0 * s_xy, s_xx - s_yy)
    ux_c = np.cos(theta)
    uy_c = np.sin(theta)

    proj = dx * ux_c[cids] + dy * uy_c[cids]
    order_asc = np.lexsort((proj, cids))
    min_tip_idx = order_asc[np.unique(cids[order_asc], return_index=True)[1]]
    order_desc = np.lexsort((-proj, cids))
    max_tip_idx = order_desc[np.unique(cids[order_desc], return_index=True)[1]]

    tip_mask = np.zeros(SHAPE, dtype=bool)
    tip_ux_grid = np.zeros(SHAPE, dtype=np.float32)
    tip_uy_grid = np.zeros(SHAPE, dtype=np.float32)
    for idx_arr, sign in ((min_tip_idx, -1.0), (max_tip_idx, 1.0)):
        keep = valid_c[cids[idx_arr]]
        sel = idx_arr[keep]
        ty, tx = ys[sel], xs[sel]
        tc = cids[sel]
        tip_mask[ty, tx] = True
        tip_ux_grid[ty, tx] = (sign * ux_c[tc]).astype(np.float32)
        tip_uy_grid[ty, tx] = (sign * uy_c[tc]).astype(np.float32)

    if tip_mask.any():
        _, tip_rc = distance_transform_edt(~tip_mask, return_distances=True, return_indices=True)
        # Compute forward splay cone strictly on footprint coordinates (5.17M floats = 20 MB!)
        fy = (foot_idx // SHAPE[1]).astype(np.float32)
        fx = (foot_idx % SHAPE[1]).astype(np.float32)
        near_ty = tip_rc[0].ravel()[foot_idx].astype(np.float32)
        near_tx = tip_rc[1].ravel()[foot_idx].astype(np.float32)
        tip_ux_foot = tip_ux_grid[tip_rc[0], tip_rc[1]].ravel()[foot_idx]
        tip_uy_foot = tip_uy_grid[tip_rc[0], tip_rc[1]].ravel()[foot_idx]
        del tip_rc, tip_ux_grid, tip_uy_grid

        rel_x = fx - near_tx
        rel_y = fy - near_ty
        del fx, fy, near_tx, near_ty
        s_par = rel_x * tip_ux_foot + rel_y * tip_uy_foot
        s_perp = np.abs(rel_x * tip_uy_foot - rel_y * tip_ux_foot)
        del rel_x, rel_y
        cone_width = 2.0 + 0.35 * np.maximum(s_par, 0.0)
        ht_foot = (
            (s_par > 0.0).astype(np.float32)
            * np.exp(-np.maximum(s_par, 0.0) / 25.0).astype(np.float32)
            * np.exp(-0.5 * (s_perp / cone_width) ** 2).astype(np.float32)
        )
        del s_par, s_perp, cone_width
        ht_foot[d_vis_px.ravel()[foot_idx] <= 2.0] = 0.0
    else:
        ht_foot = np.zeros(n_foot, dtype=np.float32)
        tip_ux_foot = np.zeros(n_foot, dtype=np.float32)
        tip_uy_foot = np.zeros(n_foot, dtype=np.float32)

    strike_match = np.abs(struct_tx_foot * tip_ux_foot + struct_ty_foot * tip_uy_foot)
    vent_tip_bridge = np.clip(
        (0.6 * ht_foot + 0.4 * rl_foot) * (0.3 + 0.7 * upflow_foot) * (0.4 + 0.6 * strike_match),
        0.0,
        1.0,
    ).astype(np.float32)

    return np.stack((ht_foot, rl_foot, vent_tip_bridge), axis=0), d_vis_px


def bayes_prior_calibrate(
    prob_subsample: np.ndarray,
    *,
    pi_subsample: float,
    pi_true: float,
) -> np.ndarray:
    """Exact Bayes case-control prior-odds shift (King & Zeng 2001)."""
    p = np.clip(np.asarray(prob_subsample, dtype=np.float64), 1e-6, 1.0 - 1e-6)
    pi_s = float(np.clip(pi_subsample, 1e-6, 1.0 - 1e-6))
    pi_t = float(np.clip(pi_true, 1e-6, 1.0 - 1e-6))
    odds_factor = (pi_t / (1.0 - pi_t)) * ((1.0 - pi_s) / pi_s)
    odds = (p / (1.0 - p)) * odds_factor
    return (odds / (1.0 + odds)).astype(np.float32)
