"""Multi-physics structural cross-gradient, upward-continuation, and fold-safe relay features (H31-E).

All static features in this module are strictly label-free and SGMC-free:
* ``dist_cat_km`` and ``dist_sgmc_km`` are never read or produced here.
* Missing outside-footprint or partial-coverage values are nearest-neighbor padded only for spatial
  filtering/FFT boundary continuity and immediately re-masked to NaN where raw coverage is absent.
* Fold-dynamic structural accommodation features (``compute_visible_structural_features``) accept an
  explicit ``visible_faults`` boolean mask so each spatial fold computes tip/relay/corridor geometry
  exclusively from its own visible faults.
"""

from __future__ import annotations

import gc
import json
from pathlib import Path

import numpy as np
import rasterio
from scipy.fft import irfft2 as sp_irfft2
from scipy.fft import rfft2 as sp_rfft2
from scipy.ndimage import distance_transform_edt, gaussian_filter, maximum_filter, minimum_filter

from .raster import CELL_M, connected_components

FULL_FEATURE_NAMES: tuple[str, ...] = (
    # Group P1: Gallardo-Meju (2003) multi-physics structural cross-gradient concordance
    "scgp_grav_base_150m",
    "scgp_grav_base_400m",
    "scgp_rtp_grav_200m",
    "scgp_cond_base_300m",
    "scgp_topo_grav_300m",
    "scgp_lahontan_mimic_score",
    # Group P2: Laplace FFT upward-continuation attenuation & potential-field tilt ridges
    "rtp_shallow_res_200m",
    "rtp_mid_res_800m",
    "rtp_laplacian_trough",
    "rtp_tilt_angle",
    "grav_tilt_ridge",
    "tmi_up150_norm_diff",
    # Group P3: Multi-scale geomorphic ridgeness & piedmont regime indicators
    "elev_hessian_ridge_200m",
    "elev_hessian_ridge_500m",
    "elev_local_relief_500m",
    "piedmont_apron_index",
    "log_depth_to_base",
    "grad_log_depth_base",
    # Group P4: GeoDAWN radiometric hydrothermal alteration & GDR-1391 paleo-geothermal outflow
    "k_local_anom_1km",
    "thk_edge_grad",
    "uth_anom",
    "k_over_tc_anom",
    "dist_paleo_sinter_km",
    "dist_2m_probe_km",
    "dist_quat_vent_km",
    # Group P5: Crustal strain & microseismicity
    "strain_dilatation",
    "strain_shear",
    "strain_extensional_ratio",
    "log_deq_density",
    # Group P6: Core continuous physical reference bands
    "raw_det_elev",
    "raw_det_slope",
    "raw_tmi_hg",
    "raw_iso_grav_slope",
    "raw_cond_surf",
    "raw_tc_depth",
)

LIDAR_FEATURE_NAMES: tuple[str, ...] = (
    "lidar_step_coh",
    "lidar_signed_polarity_abs",
    "lidar_polarity_coh",
    "lidar_laplacian_dipole",
    "lidar_ex_max",
    "lidar_cross_max",
    "lidar_relief",
    "lidar_coh100",
)

STATIC_FEATURE_NAMES: tuple[str, ...] = FULL_FEATURE_NAMES + LIDAR_FEATURE_NAMES

VISIBLE_STRUCTURAL_NAMES: tuple[str, ...] = (
    "vis_d1_clamped_km",
    "vis_relay_bridge",
    "vis_tip_continuation",
    "vis_belt_annulus_5km",
)

BANNED_PREPARED_BANDS: frozenset[str] = frozenset({"dist_cat_km", "dist_sgmc_km"})


def sanitize_nodata(field: np.ndarray, valid_mask: np.ndarray | None = None) -> np.ndarray:
    """Replace non-finite entries and GeoTIFF float32 sentinels (|x| > 1e20) with NaN."""
    arr = np.asarray(field, dtype=np.float32)
    bad = ~np.isfinite(arr) | (np.abs(arr) > 1e20)
    if valid_mask is not None:
        bad = bad | ~valid_mask
    if not bad.any():
        return arr.copy()
    out = arr.copy()
    out[bad] = np.nan
    return out


def nearest_finite_fill(field: np.ndarray, valid_mask: np.ndarray | None = None) -> np.ndarray:
    """Fill non-finite or sentinel pixels with the nearest finite pixel value for spatial filtering."""
    arr = sanitize_nodata(field, valid_mask)
    finite = np.isfinite(arr)
    if finite.all():
        return arr
    if not finite.any():
        return np.zeros_like(arr, dtype=np.float32)
    _, indices = distance_transform_edt(~finite, return_indices=True)
    return arr[indices[0], indices[1]].astype(np.float32)


def robust_z(field: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    """Standardize a 2D array by median and MAD over finite non-sentinel in-footprint cells."""
    clean = sanitize_nodata(field)
    valid = footprint & np.isfinite(clean)
    vals = clean[valid]
    med = float(np.median(vals))
    mad = float(np.median(np.abs(vals - med))) * 1.4826
    scale = max(mad, 1e-6)
    return np.clip((clean - med) / scale, -20.0, 20.0).astype(np.float32)


def smooth_gradients(filled_field: np.ndarray, sigma_px: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (gy, gx, magnitude) using Gaussian-derivative kernels."""
    gy = gaussian_filter(filled_field, sigma=sigma_px, order=(1, 0), mode="nearest").astype(np.float32)
    gx = gaussian_filter(filled_field, sigma=sigma_px, order=(0, 1), mode="nearest").astype(np.float32)
    mag = np.hypot(gy, gx).astype(np.float32)
    return gy, gx, mag


def cross_gradient_concordance(
    gy_a: np.ndarray,
    gx_a: np.ndarray,
    mag_a: np.ndarray,
    gy_b: np.ndarray,
    gx_b: np.ndarray,
    mag_b: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Gallardo & Meju (2003) structural cross-gradient concordance and orthogonal discordance.

    Returns ``(concordance, sin_delta_theta)`` where:
    * ``sin_delta_theta = |gx_a * gy_b - gy_a * gx_b| / (mag_a * mag_b + eps)`` in ``[0, 1]``
    * ``concordance = sqrt(mag_a * mag_b) * (1 - sin_delta_theta)`` (invariant to +/- gradient polarity)
    """
    denom = mag_a * mag_b + 1e-6
    cross_abs = np.abs(gx_a * gy_b - gy_a * gx_b)
    sin_theta = np.clip(cross_abs / denom, 0.0, 1.0).astype(np.float32)
    geom_mag = np.sqrt(np.maximum(mag_a * mag_b, 0.0)).astype(np.float32)
    concordance = (geom_mag * (1.0 - sin_theta)).astype(np.float32)
    return concordance, sin_theta


def fft_upward_continue(filled_field: np.ndarray, height_m: float, cell_m: float = CELL_M) -> np.ndarray:
    """Exact Laplace potential-field upward continuation via single-precision 2D FFT."""
    clean_fill = nearest_finite_fill(filled_field)
    if height_m <= 0.0:
        return clean_fill
    h, w = clean_fill.shape
    pad_y, pad_x = min(64, h // 8), min(64, w // 8)
    padded = np.pad(clean_fill, ((pad_y, pad_y), (pad_x, pad_x)), mode="edge")
    ky = np.fft.fftfreq(padded.shape[0], d=cell_m).astype(np.float32)
    kx = np.fft.rfftfreq(padded.shape[1], d=cell_m).astype(np.float32)
    k_rad = (2.0 * np.pi) * np.hypot(ky[:, None], kx[None, :])
    transfer = np.exp(-float(height_m) * k_rad).astype(np.float32)
    spectrum = sp_rfft2(padded)
    continued = sp_irfft2(spectrum * transfer, s=padded.shape)
    return continued[pad_y : pad_y + h, pad_x : pad_x + w].astype(np.float32)


def hessian_max_abs_curvature(filled_field: np.ndarray, sigma_px: float) -> np.ndarray:
    """Largest principal Hessian curvature magnitude |lambda|_max at scale ``sigma_px``."""
    fyy = gaussian_filter(filled_field, sigma=sigma_px, order=(2, 0), mode="nearest")
    fxx = gaussian_filter(filled_field, sigma=sigma_px, order=(0, 2), mode="nearest")
    fxy = gaussian_filter(filled_field, sigma=sigma_px, order=(1, 1), mode="nearest")
    trace = 0.5 * (fxx + fyy)
    rad = np.hypot(0.5 * (fxx - fyy), fxy)
    lam1 = np.abs(trace + rad)
    lam2 = np.abs(trace - rad)
    return np.maximum(lam1, lam2).astype(np.float32)


def build_static_h31e_stack(
    data_dir: Path,
    out_memmap_path: Path,
    *,
    force: bool = False,
) -> tuple[np.memmap, dict]:
    """Build or reopen the disk-backed (43, N_footprint) float32 static H31-E feature stack."""
    meta_out = out_memmap_path.with_suffix(".json")
    with rasterio.open(data_dir / "sample_submission.tif") as src:
        footprint = np.isfinite(src.read(1))
    n_foot = int(footprint.sum())
    n_feat = len(STATIC_FEATURE_NAMES)

    if out_memmap_path.is_file() and meta_out.is_file() and not force:
        saved = json.loads(meta_out.read_text())
        if saved.get("feature_names") == list(STATIC_FEATURE_NAMES) and saved.get("n_footprint") == n_foot:
            mm = np.memmap(out_memmap_path, dtype=np.float32, mode="r", shape=(n_feat, n_foot))
            return mm, saved

    prep_meta = json.loads((data_dir / "prepared" / "features.json").read_text())
    band_names: list[str] = prep_meta["bands"]
    prep_shape = (len(band_names), footprint.shape[0], footprint.shape[1])
    prep = np.memmap(data_dir / "prepared" / "features.f32", dtype=np.float32, mode="r", shape=prep_shape)

    def get_band(name: str) -> np.ndarray:
        if name in BANNED_PREPARED_BANDS:
            raise ValueError(f"Attempted to read banned leakage/proxy band: {name}")
        return sanitize_nodata(prep[band_names.index(name)], footprint)

    out_memmap_path.parent.mkdir(parents=True, exist_ok=True)
    mm = np.memmap(out_memmap_path, dtype=np.float32, mode="w+", shape=(n_feat, n_foot))
    idx_map = {name: i for i, name in enumerate(STATIC_FEATURE_NAMES)}

    def write_feat(name: str, grid2d: np.ndarray) -> None:
        mm[idx_map[name]] = np.asarray(grid2d[footprint], dtype=np.float32)

    # Load and standardize core continuous fields one group at a time to stay <450 MB RAM
    iso_grav = nearest_finite_fill(robust_z(get_band("iso_grav_anom"), footprint), footprint)
    depth_raw = np.maximum(nearest_finite_fill(get_band("depth_to_base_surf"), footprint), 0.0)
    log_depth = np.log1p(depth_raw).astype(np.float32)
    log_depth_z = nearest_finite_fill(robust_z(log_depth, footprint), footprint)
    rtp_raw = nearest_finite_fill(get_band("rtp"), footprint)
    rtp_z = nearest_finite_fill(robust_z(rtp_raw, footprint), footprint)
    cond_raw = get_band("cond_surf")
    cond_z = nearest_finite_fill(robust_z(cond_raw, footprint), footprint)
    elev_raw = get_band("det_elev")
    slope_raw = get_band("det_elev_slope")
    elev_fill = nearest_finite_fill(elev_raw, footprint)
    elev_z = nearest_finite_fill(robust_z(elev_fill, footprint), footprint)

    # Group P1: Gallardo-Meju structural cross-gradients (freeing temporaries eagerly)
    gy_g15, gx_g15, mg_g15 = smooth_gradients(iso_grav, 1.5)
    gy_b15, gx_b15, mg_b15 = smooth_gradients(log_depth_z, 1.5)
    c_gb_150, _ = cross_gradient_concordance(gy_g15, gx_g15, mg_g15, gy_b15, gx_b15, mg_b15)
    write_feat("scgp_grav_base_150m", c_gb_150)
    del gy_g15, gx_g15, mg_g15, gy_b15, gx_b15, mg_b15, c_gb_150

    gy_g40, gx_g40, mg_g40 = smooth_gradients(iso_grav, 4.0)
    gy_b40, gx_b40, mg_b40 = smooth_gradients(log_depth_z, 4.0)
    c_gb_400, _ = cross_gradient_concordance(gy_g40, gx_g40, mg_g40, gy_b40, gx_b40, mg_b40)
    write_feat("scgp_grav_base_400m", c_gb_400)
    del gy_g40, gx_g40, mg_g40, gy_b40, gx_b40, mg_b40, c_gb_400

    gy_r20, gx_r20, mg_r20 = smooth_gradients(rtp_z, 2.0)
    gy_g20, gx_g20, mg_g20 = smooth_gradients(iso_grav, 2.0)
    c_rg_200, _ = cross_gradient_concordance(gy_r20, gx_r20, mg_r20, gy_g20, gx_g20, mg_g20)
    write_feat("scgp_rtp_grav_200m", c_rg_200)
    del gy_r20, gx_r20, mg_r20, gy_g20, gx_g20, mg_g20, c_rg_200

    gy_c30, gx_c30, mg_c30 = smooth_gradients(cond_z, 3.0)
    gy_b30, gx_b30, mg_b30 = smooth_gradients(log_depth_z, 3.0)
    c_cb_300, _ = cross_gradient_concordance(gy_c30, gx_c30, mg_c30, gy_b30, gx_b30, mg_b30)
    write_feat("scgp_cond_base_300m", c_cb_300)
    del gy_c30, gx_c30, mg_c30, gy_b30, gx_b30, mg_b30, c_cb_300, cond_z, log_depth_z

    gy_e30, gx_e30, mg_e30 = smooth_gradients(elev_z, 3.0)
    gy_g30, gx_g30, mg_g30 = smooth_gradients(iso_grav, 3.0)
    c_eg_300, sin_eg_300 = cross_gradient_concordance(gy_e30, gx_e30, mg_e30, gy_g30, gx_g30, mg_g30)
    write_feat("scgp_topo_grav_300m", c_eg_300)
    del gy_e30, gx_e30, mg_e30, gy_g30, gx_g30, mg_g30, c_eg_300, iso_grav

    _, _, mg_e15 = smooth_gradients(elev_z, 1.5)
    lahontan_zone = np.exp(-0.5 * ((elev_fill + 90.0) / 110.0) ** 2).astype(np.float32)
    lahontan_mimic = (mg_e15 * sin_eg_300 * lahontan_zone).astype(np.float32)
    write_feat("scgp_lahontan_mimic_score", lahontan_mimic)
    del mg_e15, sin_eg_300, lahontan_zone, lahontan_mimic, elev_z
    mm.flush()
    gc.collect()

    # Group P2: Laplace upward continuation & tilt ridges
    rtp_up200 = fft_upward_continue(rtp_raw, 200.0)
    rtp_up800 = fft_upward_continue(rtp_raw, 800.0)
    _, _, rtp_sh_mag = smooth_gradients(rtp_raw - rtp_up200, 1.2)
    _, _, rtp_mid_mag = smooth_gradients(rtp_up200 - rtp_up800, 2.5)
    write_feat("rtp_shallow_res_200m", rtp_sh_mag)
    write_feat("rtp_mid_res_800m", rtp_mid_mag)
    del rtp_raw, rtp_up200, rtp_up800, rtp_sh_mag, rtp_mid_mag

    rtp_lap = (
        gaussian_filter(rtp_z, sigma=2.0, order=(2, 0), mode="nearest")
        + gaussian_filter(rtp_z, sigma=2.0, order=(0, 2), mode="nearest")
    )
    write_feat("rtp_laplacian_trough", np.maximum(rtp_lap, 0.0).astype(np.float32))
    del rtp_z, rtp_lap
    mm.flush()
    gc.collect()

    tmi_hg = np.maximum(nearest_finite_fill(get_band("tmi_hg"), footprint), 0.0)
    tmi_vg = nearest_finite_fill(get_band("tmi_vg"), footprint)
    rtp_tilt = np.arctan2(tmi_vg, tmi_hg + 1.0).astype(np.float32)
    write_feat("rtp_tilt_angle", rtp_tilt)

    grav_vg = nearest_finite_fill(get_band("iso_grav_anom_vg"), footprint)
    grav_sl = np.maximum(nearest_finite_fill(get_band("iso_grav_anom_slope"), footprint), 0.0)
    grav_tilt = np.arctan2(grav_vg, grav_sl + 0.02).astype(np.float32)
    _, _, grav_tilt_hg = smooth_gradients(grav_tilt, 1.5)
    write_feat("grav_tilt_ridge", grav_tilt_hg)

    tmi_raw = get_band("tmi")
    tmi_up150_u8 = get_band("TMI_up150")
    tmi_diff = robust_z(nearest_finite_fill(tmi_raw, footprint), footprint) - robust_z(
        nearest_finite_fill(tmi_up150_u8, footprint), footprint
    )
    tmi_diff[~np.isfinite(tmi_up150_u8)] = np.nan
    write_feat("tmi_up150_norm_diff", tmi_diff)

    # Group P3: Geomorphic ridgeness & piedmont regime
    write_feat("elev_hessian_ridge_200m", hessian_max_abs_curvature(elev_fill, 2.0))
    write_feat("elev_hessian_ridge_500m", hessian_max_abs_curvature(elev_fill, 5.0))
    local_rel = maximum_filter(elev_fill, size=9) - minimum_filter(elev_fill, size=9)
    write_feat("elev_local_relief_500m", local_rel.astype(np.float32))

    slope_fill = nearest_finite_fill(slope_raw, footprint)
    piedmont = np.exp(-0.5 * ((elev_fill + 60.0) / 180.0) ** 2) * np.exp(
        -0.5 * ((slope_fill - 6.0) / 8.0) ** 2
    )
    write_feat("piedmont_apron_index", piedmont.astype(np.float32))
    write_feat("log_depth_to_base", log_depth)
    _, _, grad_log_db = smooth_gradients(log_depth, 2.0)
    write_feat("grad_log_depth_base", grad_log_db)

    # Group P4: Radiometric alteration & GDR-1391 paleo-geothermal outflow
    k_band = get_band("K")
    k_valid = np.isfinite(k_band) & footprint
    k_fill = nearest_finite_fill(k_band, k_valid)
    k_anom = (k_fill - gaussian_filter(k_fill, sigma=10.0, mode="nearest")).astype(np.float32)
    k_anom[~k_valid] = np.nan
    write_feat("k_local_anom_1km", k_anom)

    thk_band = get_band("ThK")
    thk_valid = np.isfinite(thk_band) & footprint
    _, _, thk_grad = smooth_gradients(nearest_finite_fill(thk_band, thk_valid), 1.5)
    thk_grad[~thk_valid] = np.nan
    write_feat("thk_edge_grad", thk_grad)

    uth_band = get_band("UTh")
    write_feat("uth_anom", uth_band)

    tc_rad = get_band("TC")
    k_tc = robust_z(k_fill, footprint) - 0.7 * robust_z(nearest_finite_fill(tc_rad, footprint), footprint)
    k_tc[~k_valid] = np.nan
    write_feat("k_over_tc_anom", k_tc.astype(np.float32))

    with rasterio.open(data_dir / "external" / "derived_gdr_paleo_100m_u8.tif") as src:
        paleo_mask = (src.read(1) > 0) & footprint
    dist_paleo = (distance_transform_edt(~paleo_mask, sampling=CELL_M) / 1000.0).astype(np.float32)
    write_feat("dist_paleo_sinter_km", dist_paleo)
    write_feat("dist_2m_probe_km", get_band("dist_probe_km"))
    write_feat("dist_quat_vent_km", get_band("dist_vent_km"))

    # Group P5 & P6: Crustal strain, microseismicity, and core reference channels
    dil = nearest_finite_fill(get_band("geod_dilaterate"), footprint)
    shr = np.maximum(nearest_finite_fill(get_band("geod_shearrate"), footprint), 0.0)
    inv2 = np.maximum(nearest_finite_fill(get_band("geod_2ndinv"), footprint), 0.0)
    deq = np.maximum(nearest_finite_fill(get_band("deq_n100a15"), footprint), 0.0)
    write_feat("strain_dilatation", dil)
    write_feat("strain_shear", shr)
    write_feat("strain_extensional_ratio", (dil / (inv2 + 1.0)).astype(np.float32))
    write_feat("log_deq_density", np.log1p(deq).astype(np.float32))

    write_feat("raw_det_elev", elev_fill)
    write_feat("raw_det_slope", slope_fill)
    write_feat("raw_tmi_hg", tmi_hg)
    write_feat("raw_iso_grav_slope", grav_sl)
    write_feat("raw_cond_surf", nearest_finite_fill(cond_raw, footprint))
    write_feat("raw_tc_depth", nearest_finite_fill(get_band("tc"), footprint))

    # Group L: 1 m 3DEP LiDAR scarp-polarity features (strictly NaN outside LiDAR coverage)
    step_max = get_band("step_max")
    coh100 = get_band("coh100")
    upface = get_band("upface_max")
    downface = get_band("downface_max")
    lapneg = get_band("lapneg_max")
    lappos = get_band("lappos_max")

    write_feat("lidar_step_coh", ((step_max / 255.0) * (coh100 / 255.0)).astype(np.float32))
    pol_abs = (np.abs(upface - downface) / 255.0).astype(np.float32)
    write_feat("lidar_signed_polarity_abs", pol_abs)
    write_feat("lidar_polarity_coh", (pol_abs * (coh100 / 255.0)).astype(np.float32))
    write_feat("lidar_laplacian_dipole", (np.minimum(lapneg, lappos) / 255.0).astype(np.float32))
    write_feat("lidar_ex_max", get_band("ex_max"))
    write_feat("lidar_cross_max", get_band("cross_max"))
    write_feat("lidar_relief", get_band("relief"))
    write_feat("lidar_coh100", coh100)

    mm.flush()
    meta_payload = {
        "schema_version": 1,
        "feature_names": list(STATIC_FEATURE_NAMES),
        "full_feature_names": list(FULL_FEATURE_NAMES),
        "lidar_feature_names": list(LIDAR_FEATURE_NAMES),
        "n_footprint": n_foot,
        "grid_shape": list(footprint.shape),
        "banned_bands_verified_absent": sorted(BANNED_PREPARED_BANDS),
    }
    meta_out.write_text(json.dumps(meta_payload, indent=2) + "\n")
    mm_ro = np.memmap(out_memmap_path, dtype=np.float32, mode="r", shape=(n_feat, n_foot))
    return mm_ro, meta_payload


def exact_two_component_distances_m(
    visible_faults: np.ndarray,
    cell_m: float = CELL_M,
) -> tuple[np.ndarray, np.ndarray]:
    """Return exact Euclidean distances ``(d1_m, d2_m)`` to the two nearest *distinct* 8-connected components.

    Proof of exactness:
    1. One EDT on ``~visible_faults`` yields ``d1_m(x)`` and nearest component ID ``c1(x) in 1..K``.
    2. Any distinct component ``c2 != c1(x)`` differs from ``c1(x)`` in at least one binary bit ``b``.
    3. Taking ``min_b EDT(components with bit_b != bit_b(c1(x)))`` inspects only components ``!= c1(x)``
       and is guaranteed to include ``c2*(x)`` at every bit where ``c2*(x)`` and ``c1(x)`` differ.
    """
    vis = np.asarray(visible_faults, dtype=bool)
    if not vis.any():
        inf_grid = np.full(vis.shape, 1e6, dtype=np.float32)
        return inf_grid, inf_grid.copy()

    comp = connected_components(vis)
    max_id = int(comp.max())
    d1, idx = distance_transform_edt(~vis, sampling=cell_m, return_indices=True)
    d1 = d1.astype(np.float32)
    c1 = comp[idx[0], idx[1]]

    if max_id <= 1:
        return d1, np.full(vis.shape, 1e6, dtype=np.float32)

    n_bits = int(max_id).bit_length()
    d2 = np.full(vis.shape, 1e6, dtype=np.float32)
    for bit in range(n_bits):
        bit_val = (comp >> bit) & 1
        mask0 = vis & (bit_val == 0)
        mask1 = vis & (bit_val == 1)
        edt0 = (
            distance_transform_edt(~mask0, sampling=cell_m).astype(np.float32)
            if mask0.any()
            else np.full(vis.shape, 1e6, dtype=np.float32)
        )
        edt1 = (
            distance_transform_edt(~mask1, sampling=cell_m).astype(np.float32)
            if mask1.any()
            else np.full(vis.shape, 1e6, dtype=np.float32)
        )
        c1_bit = (c1 >> bit) & 1
        candidate = np.where(c1_bit == 1, edt0, edt1)
        np.minimum(d2, candidate, out=d2)
    return d1, d2


def compute_visible_structural_features(
    visible_faults: np.ndarray,
    footprint: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute the 4 fold-safe structural accommodation features strictly from ``visible_faults``.

    Returns ``(features_on_footprint, d_vis_px_full_grid)`` where ``features_on_footprint`` has shape
    ``(4, N_footprint)`` corresponding to ``VISIBLE_STRUCTURAL_NAMES``.
    """
    vis = np.asarray(visible_faults, dtype=bool) & footprint
    d1_m, d2_m = exact_two_component_distances_m(vis, cell_m=CELL_M)
    d_vis_px = (d1_m / CELL_M).astype(np.float32)

    # 1. Clamped visible distance (floored at 300 m so near-fault digitization halos get zero privilege)
    d1_clamped_km = np.clip(d1_m / 1000.0, 0.30, 15.0).astype(np.float32)

    # 2. En-echelon step-over / relay-ramp accommodation bridge between two distinct fault segments
    relay_raw = np.exp(-(d1_m + d2_m) / 2500.0).astype(np.float32)
    taper_flank = np.clip((d1_m - 200.0) / 200.0, 0.0, 1.0).astype(np.float32)
    relay_bridge = (relay_raw * taper_flank).astype(np.float32)

    # 3. Along-strike fault-tip continuation lobe (200 m - 2,500 m ahead of visible segment terminations)
    vis_f = vis.astype(np.float32)
    # Count visible fault pixels in 3x3 vs 9x9 to detect segment tips (low one-sided density)
    nb3 = gaussian_filter(vis_f, sigma=1.0, mode="constant")
    nb9 = gaussian_filter(vis_f, sigma=3.5, mode="constant")
    # Structure tensor of smoothed visible traces gives local fault strike tangent (tx, ty)
    sm_vis = gaussian_filter(vis_f, sigma=2.0, mode="constant")
    gy_v, gx_v = np.gradient(sm_vis)
    # Tangent vector is perpendicular to gradient: tx = -gy, ty = gx
    norm_v = np.hypot(gx_v, gy_v) + 1e-8
    tx = (-gy_v / norm_v).astype(np.float32)
    ty = (gx_v / norm_v).astype(np.float32)

    tip_seed = vis & (nb3 > 0.05) & (nb9 < 0.45 * np.maximum(nb3, 1e-6))
    if not tip_seed.any():
        tip_seed = vis
    if tip_seed.any():
        d_tip_m, tip_idx = distance_transform_edt(~tip_seed, sampling=CELL_M, return_indices=True)
        d_tip_m = d_tip_m.astype(np.float32)
        rows_grid, cols_grid = np.indices(vis.shape, dtype=np.float32)
        dy_m = (rows_grid - tip_idx[0]) * CELL_M
        dx_m = (cols_grid - tip_idx[1]) * CELL_M
        dist_norm = np.hypot(dx_m, dy_m) + 1e-6
        tip_tx = tx[tip_idx[0], tip_idx[1]]
        tip_ty = ty[tip_idx[0], tip_idx[1]]
        cos_psi = np.abs(dx_m * tip_tx + dy_m * tip_ty) / dist_norm
        tip_lobe = (
            (cos_psi ** 4)
            * np.exp(-d_tip_m / 1200.0)
            * np.clip((d1_m - 200.0) / 200.0, 0.0, 1.0)
        ).astype(np.float32)
    else:
        tip_lobe = np.zeros(vis.shape, dtype=np.float32)

    # 4. Regional fault-belt annular density (500 m < r <= 5,000 m via difference of Gaussians)
    outer_belt = gaussian_filter(vis_f, sigma=25.0, mode="constant")
    inner_halo = gaussian_filter(vis_f, sigma=3.5, mode="constant")
    annulus_5km = np.maximum(outer_belt - 0.35 * inner_halo, 0.0).astype(np.float32)

    stacked = np.stack(
        [
            d1_clamped_km[footprint],
            relay_bridge[footprint],
            tip_lobe[footprint],
            annulus_5km[footprint],
        ],
        axis=0,
    ).astype(np.float32)
    return stacked, d_vis_px
