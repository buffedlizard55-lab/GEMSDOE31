"""H31-T physical crustal-mechanics, analytic-signal & hydrothermal conduit features.

Preregistration: knowledge/2026-10-25_h31t_transtension_dinkelbach_preregistration.md

Design invariants:
  1. Static channels (12) are strictly label-free: never read `labels.tif`,
     `derived_sgmc_faults_100m_u8.tif`, `derived_gdr_qfaults_v2_100m_u8.tif`,
     or the LiDAR binary coverage indicator `valid`.
  2. Potential-field 3D analytic signals use verified SI-compatible units on
     `training_features.tif`:
       - Magnetic derivatives in nT/m (`0.005 * tmi_hg` vs `tmi_vg`),
       - Isostatic gravity derivatives in mGal/km (`10.0 * iso_grav_anom_slope`
         vs `iso_grav_anom_vg`).
  3. Fold-visible fracture-mechanics channels (2) are rebuilt inside each fold
     strictly from `visible_mask = catalogue & ~withheld_truth` using canonical
     component-anchor hashing (`(min_row, min_col)`), guaranteeing exact `0.0`
     sensitivity to withheld fault mutations.
  4. Reads single `float32` bands (~49.1 MB/band) sequentially to hold peak RSS
     well inside the 3.8 GiB zero-swap sandbox budget.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

H31T_STATIC_CHANNELS: tuple[str, ...] = (
    "asig_mag_crest",
    "euler_mag_invdepth",
    "asig_grav_crest",
    "euler_grav_invdepth",
    "updip_listric_trace",
    "transtensional_coulomb",
    "seismic_proximity_intensity",
    "hydrothermal_alteration_demag",
    "hydrothermal_vent_corridor",
    "piedmont_flexure_bridge",
    "lidar_scarp_asymmetry",
    "crustal_coaxial_alignment",
)

H31T_VISIBLE_CHANNELS: tuple[str, ...] = (
    "vis_wingcrack_tip_lobe",
    "vis_relay_dilation_bridge",
)

H31T_ALL_CHANNELS: tuple[str, ...] = H31T_STATIC_CHANNELS + H31T_VISIBLE_CHANNELS

FORBIDDEN_BAND_NAMES: frozenset[str] = frozenset(
    {
        "valid",
        "dist_cat_km",
        "dist_sgmc_km",
        "labels",
        "sgmc_faults",
        "qfaults_v2",
    }
)


def sanitize_band(arr: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    """Replace non-finite values, |x|>=1e30 sentinels, and outside-footprint cells with NaN."""
    out = np.asarray(arr, dtype=np.float32).copy()
    bad = (~np.isfinite(out)) | (np.abs(out) >= 1.0e30) | (~footprint)
    out[bad] = np.nan
    return out


def valid_gaussian(arr: np.ndarray, sigma: float, min_weight: float = 1.0e-4) -> np.ndarray:
    """Normalized Gaussian filter ignoring NaNs without bleeding NoData sentinels."""
    valid = np.isfinite(arr)
    filled = np.where(valid, arr, 0.0).astype(np.float32, copy=False)
    weights = valid.astype(np.float32, copy=False)
    num = ndi.gaussian_filter(filled, sigma=float(sigma), mode="nearest")
    den = ndi.gaussian_filter(weights, sigma=float(sigma), mode="nearest")
    out = np.full(arr.shape, np.nan, dtype=np.float32)
    ok = den > float(min_weight)
    out[ok] = (num[ok] / den[ok]).astype(np.float32)
    return out


def robust_positive_z(
    arr: np.ndarray,
    footprint: np.ndarray,
    clip_max: float = 8.0,
) -> np.ndarray:
    """Median/MAD positive z-score clipped to [0, clip_max] inside `footprint`."""
    out = np.zeros(arr.shape, dtype=np.float32)
    valid = footprint & np.isfinite(arr)
    if not np.any(valid):
        return out
    vals = arr[valid]
    med = float(np.median(vals))
    mad = float(np.median(np.abs(vals - med)))
    scale = max(1.4826 * mad, 1.0e-6)
    z = (vals - med) / scale
    out[valid] = np.clip(z, 0.0, float(clip_max)).astype(np.float32)
    return out


def _grad_mag_px(arr: np.ndarray, footprint: np.ndarray, sigma: float = 1.0) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Smoothed finite-difference gradient (gy, gx, hypot) in pixel units (100 m)."""
    sm = valid_gaussian(arr, sigma=sigma) if sigma > 0.0 else arr.copy()
    valid = footprint & np.isfinite(sm)
    med = float(np.median(sm[valid])) if np.any(valid) else 0.0
    filled = np.where(np.isfinite(sm), sm, med).astype(np.float32)
    gy, gx = np.gradient(filled)
    gm = np.hypot(gx, gy).astype(np.float32)
    gy[~footprint] = np.nan
    gx[~footprint] = np.nan
    gm[~footprint] = np.nan
    return gy.astype(np.float32), gx.astype(np.float32), gm


def _structure_tensor_orientation(
    scalar_field: np.ndarray,
    footprint: np.ndarray,
    grad_sigma: float = 1.5,
    integ_sigma: float = 4.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return double-angle `(cos2theta, sin2theta, coherence)` of ridge/contact strike."""
    gy, gx, _ = _grad_mag_px(scalar_field, footprint, sigma=grad_sigma)
    gx0 = np.where(np.isfinite(gx), gx, 0.0).astype(np.float32)
    gy0 = np.where(np.isfinite(gy), gy, 0.0).astype(np.float32)
    jxx = ndi.gaussian_filter(gx0 * gx0, sigma=integ_sigma, mode="nearest")
    jyy = ndi.gaussian_filter(gy0 * gy0, sigma=integ_sigma, mode="nearest")
    jxy = ndi.gaussian_filter(gx0 * gy0, sigma=integ_sigma, mode="nearest")
    trace = jxx + jyy + 1.0e-12
    diff = jxx - jyy
    two_jxy = 2.0 * jxy
    aniso = np.hypot(diff, two_jxy)
    coh = np.clip(aniso / trace, 0.0, 1.0).astype(np.float32)
    # Normal angle phi satisfies cos(2*phi)=diff/aniso, sin(2*phi)=two_jxy/aniso.
    # Strike theta = phi + pi/2 flips the sign of (cos 2phi, sin 2phi); relative
    # cos 2(theta_1 - theta_2) is invariant under simultaneous +pi/2 rotation.
    denom = aniso + 1.0e-12
    c2 = (diff / denom).astype(np.float32)
    s2 = (two_jxy / denom).astype(np.float32)
    coh[~footprint] = 0.0
    return c2, s2, coh


class PreparedBandReader:
    """Single-band seek reader over prepared `features.f32` (~49.1 MB per read)."""

    def __init__(self, prepared_dir: Path) -> None:
        meta_path = Path(prepared_dir) / "features.json"
        self.bin_path = Path(prepared_dir) / "features.f32"
        meta = json.loads(meta_path.read_text())
        self.bands: list[str] = list(meta["bands"])
        self.shape: tuple[int, int] = (int(meta["shape"][0]), int(meta["shape"][1]))
        self.index: dict[str, int] = {name: idx for idx, name in enumerate(self.bands)}
        self.band_bytes: int = self.shape[0] * self.shape[1] * 4

    def read(self, name: str, footprint: np.ndarray) -> np.ndarray:
        if name in FORBIDDEN_BAND_NAMES:
            raise ValueError(f"Refusing to read forbidden band {name!r}")
        if name not in self.index:
            raise KeyError(f"Band {name!r} not in prepared stack")
        offset = self.index[name] * self.band_bytes
        with self.bin_path.open("rb") as fh:
            fh.seek(offset)
            raw = np.frombuffer(fh.read(self.band_bytes), dtype=np.float32)
        arr = raw.reshape(self.shape).copy()
        return sanitize_band(arr, footprint)


def _read_u8_mask(path: Path, expected_shape: tuple[int, int]) -> np.ndarray:
    with rasterio.open(path) as src:
        arr = src.read(1)
    if arr.shape != expected_shape:
        raise ValueError(f"Shape mismatch on {path}: {arr.shape} != {expected_shape}")
    return np.isfinite(arr) & (arr > 0)


def compute_h31t_static_channels_from_arrays(
    *,
    footprint: np.ndarray,
    tmi_hg: np.ndarray,
    tmi_vg: np.ndarray,
    rtp: np.ndarray,
    iso_grav_slope: np.ndarray,
    iso_grav_vg: np.ndarray,
    depth_to_base: np.ndarray,
    geod_2ndinv: np.ndarray,
    geod_shearrate: np.ndarray,
    geod_dilaterate: np.ndarray,
    deq_m: np.ndarray,
    ieq_density: np.ndarray,
    cond_surf: np.ndarray,
    det_elev: np.ndarray,
    det_elev_slope: np.ndarray,
    rad_k: np.ndarray,
    rad_th: np.ndarray,
    lidar_upface: np.ndarray,
    lidar_downface: np.ndarray,
    lidar_step: np.ndarray,
    lidar_coh100: np.ndarray,
    gdr_probes_mask: np.ndarray,
    gdr_paleo_mask: np.ndarray,
    gdr_volcanics_mask: np.ndarray,
) -> dict[str, np.ndarray]:
    """Pure array-in / array-out implementation of the 12 static H31-T channels."""
    fp = np.asarray(footprint, dtype=bool)
    shape = fp.shape
    out: dict[str, np.ndarray] = {}

    # 1-2. SI-calibrated 3D Magnetic Analytic Signal (nT/m) & Thompson inverse depth
    hg_nt_m = 0.005 * np.maximum(0.0, sanitize_band(tmi_hg, fp))
    vg_nt_m = sanitize_band(tmi_vg, fp)
    amag = np.hypot(hg_nt_m, vg_nt_m).astype(np.float32)
    amag_bg = valid_gaussian(amag, sigma=8.0)
    asig_mag_crest = np.log1p(np.maximum(0.0, amag / (amag_bg + 0.01))).astype(np.float32)
    asig_mag_crest[~fp] = np.nan
    out["asig_mag_crest"] = asig_mag_crest

    _, _, amag_grad = _grad_mag_px(amag, fp, sigma=1.0)
    amag_valid = amag[fp & np.isfinite(amag)]
    amag_med = float(np.median(amag_valid)) if amag_valid.size else 0.05
    euler_mag = (amag_grad / (valid_gaussian(amag, sigma=1.0) + max(amag_med, 1.0e-3))).astype(
        np.float32
    )
    euler_mag[~fp] = np.nan
    out["euler_mag_invdepth"] = euler_mag

    # 3-4. SI-calibrated 3D Gravity Analytic Signal (mGal/km) & inverse contact depth
    ghg_mgal_km = 10.0 * np.maximum(0.0, sanitize_band(iso_grav_slope, fp))
    gvg_mgal_km = sanitize_band(iso_grav_vg, fp)
    agrav = np.hypot(ghg_mgal_km, gvg_mgal_km).astype(np.float32)
    agrav_bg = valid_gaussian(agrav, sigma=10.0)
    asig_grav_crest = np.log1p(np.maximum(0.0, agrav / (agrav_bg + 0.10))).astype(np.float32)
    asig_grav_crest[~fp] = np.nan
    out["asig_grav_crest"] = asig_grav_crest

    _, _, agrav_grad = _grad_mag_px(agrav, fp, sigma=1.2)
    agrav_valid = agrav[fp & np.isfinite(agrav)]
    agrav_med = float(np.median(agrav_valid)) if agrav_valid.size else 0.5
    euler_grav = (
        agrav_grad / (valid_gaussian(agrav, sigma=1.2) + max(agrav_med, 5.0e-2))
    ).astype(np.float32)
    euler_grav[~fp] = np.nan
    out["euler_grav_invdepth"] = euler_grav

    # 5. Up-dip listric 55-deg footwall restoration of hanging-wall basement/gravity step
    # Physically, hanging-wall sediment thickness `z_base(x_hw)` is large AT the
    # down-dip subsurface inflection `x_hw`, whereas `z_base` at the surface trace
    # is near zero. Forward-splatting each hanging-wall subsurface step `sub_step(x_hw)`
    # UP-DIP along `-u_dip(x_hw)` by `clip(0.55 * z_base(x_hw) / 100 m, 0, 5 px)`
    # maps the basinward gravity/basement inflection directly onto the surface fault trace.
    z_base = np.maximum(0.0, sanitize_band(depth_to_base, fp))
    log_zb = np.log(100.0 + z_base).astype(np.float32)
    _, _, b_step = _grad_mag_px(log_zb, fp, sigma=1.5)
    sub_step = (
        0.55 * robust_positive_z(b_step, fp) + 0.45 * robust_positive_z(agrav, fp)
    ).astype(np.float32)
    gy_zb, gx_zb, gm_zb = _grad_mag_px(z_base, fp, sigma=2.5)
    ur = np.where(np.isfinite(gy_zb), gy_zb / (gm_zb + 1.0e-6), 0.0).astype(np.float32)
    uc = np.where(np.isfinite(gx_zb), gx_zb / (gm_zb + 1.0e-6), 0.0).astype(np.float32)
    zb_fill = np.where(np.isfinite(z_base), z_base, 0.0).astype(np.float32)
    shift_px = np.clip(0.55 * zb_fill / 100.0, 0.0, 5.0).astype(np.float32)
    rr, cc = np.indices(shape, dtype=np.float32)
    tgt_r = np.clip(np.rint(rr - shift_px * ur).astype(np.int32), 0, shape[0] - 1)
    tgt_c = np.clip(np.rint(cc - shift_px * uc).astype(np.int32), 0, shape[1] - 1)
    splat = np.zeros(shape, dtype=np.float32)
    valid_hw = fp & np.isfinite(sub_step)
    np.maximum.at(splat, (tgt_r[valid_hw], tgt_c[valid_hw]), sub_step[valid_hw])
    updip = ndi.gaussian_filter(splat, sigma=0.9, mode="nearest").astype(np.float32)
    updip[~fp] = np.nan
    out["updip_listric_trace"] = updip

    # 6. Kostrov-Byerlee active transtensional dilatation-shear partitioning
    g2 = np.maximum(0.0, sanitize_band(geod_2ndinv, fp))
    gsh = np.maximum(0.0, sanitize_band(geod_shearrate, fp))
    gdil = np.maximum(0.0, sanitize_band(geod_dilaterate, fp))
    transtens = ((gdil / (g2 + 2.0)) * np.log1p(gsh)).astype(np.float32)
    transtens[~fp] = np.nan
    out["transtensional_coulomb"] = transtens

    # 7. Active microseismic proximity-intensity localization (deq in meters)
    deq_clean = np.maximum(0.0, sanitize_band(deq_m, fp))
    ieq_clean = np.maximum(0.0, sanitize_band(ieq_density, fp))
    seis_loc = (np.log1p(ieq_clean) / (1.0 + deq_clean / 5000.0)).astype(np.float32)
    seis_loc[~fp] = np.nan
    out["seismic_proximity_intensity"] = seis_loc

    # 8. Hydrothermal magnetite-destruction x potassic alteration x lateral clay-cap ridge
    rtp_s = sanitize_band(rtp, fp)
    rtp_trough = valid_gaussian(rtp_s, sigma=6.0) - valid_gaussian(rtp_s, sigma=1.5)
    z_demag = robust_positive_z(rtp_trough, fp)

    cond_s = sanitize_band(cond_surf, fp)
    cond_ridge = valid_gaussian(cond_s, sigma=1.0) - valid_gaussian(cond_s, sigma=6.0)
    z_cond = robust_positive_z(cond_ridge, fp)

    k_s = sanitize_band(rad_k, fp)
    th_s = sanitize_band(rad_th, fp)
    k_over_th = np.full(shape, np.nan, dtype=np.float32)
    rad_ok = fp & np.isfinite(k_s) & np.isfinite(th_s) & ((k_s > 0.0) | (th_s > 0.0))
    k_over_th[rad_ok] = (np.maximum(0.0, k_s[rad_ok]) / (np.maximum(0.0, th_s[rad_ok]) + 5.0)).astype(
        np.float32
    )
    z_kth = robust_positive_z(k_over_th, fp)
    # Neutral value outside GeoDAWN coverage so missing radiometrics never leak footprint
    rad_med = float(np.median(z_kth[rad_ok])) if np.any(rad_ok) else 0.0
    z_kth[~rad_ok & fp] = rad_med

    hydro_alt = (
        np.cbrt((z_demag + 0.25) * (z_kth + 0.25) * (z_cond + 0.25)) - 0.25
    ).astype(np.float32)
    hydro_alt[~fp] = np.nan
    out["hydrothermal_alteration_demag"] = hydro_alt

    # 9. GDR-1391 geothermal manifestation corridor modulated by transtensional dilatation
    def _exp_prox(mask: np.ndarray, scale_m: float) -> np.ndarray:
        if not np.any(mask):
            return np.zeros(shape, dtype=np.float32)
        dist_m = ndi.distance_transform_edt(~mask).astype(np.float32) * 100.0
        return np.exp(-dist_m / float(scale_m)).astype(np.float32)

    vent_prox = (
        _exp_prox(gdr_probes_mask, 2500.0)
        + 0.8 * _exp_prox(gdr_paleo_mask, 2500.0)
        + 0.5 * _exp_prox(gdr_volcanics_mask, 3500.0)
    )
    z_tr = robust_positive_z(transtens, fp)
    vent_corr = (vent_prox * (1.0 + 0.35 * z_tr)).astype(np.float32)
    vent_corr[~fp] = np.nan
    out["hydrothermal_vent_corridor"] = vent_corr

    # 10. Slope-deconfounded piedmont alluvial-bajada flexure
    elev_s = valid_gaussian(sanitize_band(det_elev, fp), sigma=2.0)
    elev_med = float(np.median(elev_s[fp & np.isfinite(elev_s)])) if np.any(fp & np.isfinite(elev_s)) else 0.0
    elev_fill = np.where(np.isfinite(elev_s), elev_s, elev_med).astype(np.float32)
    ey, ex = np.gradient(elev_fill)
    eyy, eyx = np.gradient(ey)
    exy, exx = np.gradient(ex)
    hxy = 0.5 * (exy + eyx)
    tr_h = exx + eyy
    det_disc = np.hypot(exx - eyy, 2.0 * hxy)
    lam_min = 0.5 * (tr_h - det_disc)
    concavity = np.maximum(0.0, -lam_min).astype(np.float32)
    slope_deg = np.maximum(0.0, sanitize_band(det_elev_slope, fp))
    piedmont_flex = (concavity / (1.0 + slope_deg / 7.0)).astype(np.float32)
    piedmont_flex[~fp] = np.nan
    out["piedmont_flexure_bridge"] = piedmont_flex

    # 11. Coverage-clean 1m 3DEP LiDAR directional scarp polarity (NaN outside LiDAR returns)
    up_s = sanitize_band(lidar_upface, fp)
    dn_s = sanitize_band(lidar_downface, fp)
    st_s = sanitize_band(lidar_step, fp)
    ch_s = sanitize_band(lidar_coh100, fp)
    lidar_ok = fp & np.isfinite(up_s) & np.isfinite(dn_s) & np.isfinite(st_s) & np.isfinite(ch_s)
    lidar_asym = np.full(shape, np.nan, dtype=np.float32)
    lidar_asym[lidar_ok] = (
        (np.abs(up_s[lidar_ok] - dn_s[lidar_ok]) / (up_s[lidar_ok] + dn_s[lidar_ok] + 1.0))
        * np.log1p(np.maximum(0.0, st_s[lidar_ok]))
        * np.clip(ch_s[lidar_ok] / 255.0, 0.0, 1.0)
    ).astype(np.float32)
    out["lidar_scarp_asymmetry"] = lidar_asym

    # 12. Double-angle structure-tensor coaxial alignment (magnetic AS vs listric step)
    c2_mag, s2_mag, coh_mag = _structure_tensor_orientation(asig_mag_crest, fp, 1.5, 4.0)
    c2_lis, s2_lis, coh_lis = _structure_tensor_orientation(updip, fp, 1.5, 4.0)
    cos2_delta = np.clip(c2_mag * c2_lis + s2_mag * s2_lis, -1.0, 1.0)
    coaxial = (0.5 * (1.0 + cos2_delta) * np.sqrt(coh_mag * coh_lis)).astype(np.float32)
    coaxial[~fp] = np.nan
    out["crustal_coaxial_alignment"] = coaxial

    return out


def build_or_load_h31t_static_cache(
    *,
    prepared_dir: Path,
    data_dir: Path,
    footprint: np.ndarray,
    cache_dir: Path,
) -> dict[str, np.ndarray]:
    """Stream group-by-group (<450 MB peak RSS) to build `.npy` cache for all 12 static channels."""
    import gc

    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    fp = np.asarray(footprint, dtype=bool)
    shape = fp.shape

    if not all((cache_dir / f"{name}.npy").exists() for name in H31T_STATIC_CHANNELS):
        reader = PreparedBandReader(prepared_dir)
        ext_dir = Path(data_dir) / "external"

        def _save(cname: str, arr: np.ndarray) -> None:
            arr[~fp] = np.nan
            np.save(cache_dir / f"{cname}.npy", arr.astype(np.float32, copy=False))

        # Group 1: Magnetic Analytic Signal & inverse contact depth (2 bands in RAM)
        hg_nt_m = 0.005 * np.maximum(0.0, reader.read("tmi_hg", fp))
        vg_nt_m = reader.read("tmi_vg", fp)
        amag = np.hypot(hg_nt_m, vg_nt_m).astype(np.float32)
        del hg_nt_m, vg_nt_m
        asig_mag_crest = np.log1p(
            np.maximum(0.0, amag / (valid_gaussian(amag, sigma=8.0) + 0.01))
        ).astype(np.float32)
        _save("asig_mag_crest", asig_mag_crest)
        _, _, amag_grad = _grad_mag_px(amag, fp, sigma=1.0)
        amag_med = float(np.median(amag[fp & np.isfinite(amag)]))
        euler_mag = (amag_grad / (valid_gaussian(amag, sigma=1.0) + max(amag_med, 1.0e-3))).astype(
            np.float32
        )
        _save("euler_mag_invdepth", euler_mag)
        del amag, amag_grad, euler_mag
        gc.collect()

        # Group 2: Gravity Analytic Signal, inverse depth, Up-Dip Listric & Coaxial Alignment
        ghg = 10.0 * np.maximum(0.0, reader.read("iso_grav_anom_slope", fp))
        gvg = reader.read("iso_grav_anom_vg", fp)
        agrav = np.hypot(ghg, gvg).astype(np.float32)
        del ghg, gvg
        asig_grav_crest = np.log1p(
            np.maximum(0.0, agrav / (valid_gaussian(agrav, sigma=10.0) + 0.10))
        ).astype(np.float32)
        _save("asig_grav_crest", asig_grav_crest)
        del asig_grav_crest
        _, _, agrav_grad = _grad_mag_px(agrav, fp, sigma=1.2)
        agrav_med = float(np.median(agrav[fp & np.isfinite(agrav)]))
        euler_grav = (
            agrav_grad / (valid_gaussian(agrav, sigma=1.2) + max(agrav_med, 5.0e-2))
        ).astype(np.float32)
        _save("euler_grav_invdepth", euler_grav)
        del agrav_grad, euler_grav

        z_base = np.maximum(0.0, reader.read("depth_to_base_surf", fp))
        _, _, b_step = _grad_mag_px(np.log(100.0 + z_base).astype(np.float32), fp, sigma=1.5)
        sub_step = (
            0.55 * robust_positive_z(b_step, fp) + 0.45 * robust_positive_z(agrav, fp)
        ).astype(np.float32)
        del b_step, agrav
        gy_zb, gx_zb, gm_zb = _grad_mag_px(z_base, fp, sigma=2.5)
        ur = np.where(np.isfinite(gy_zb), gy_zb / (gm_zb + 1.0e-6), 0.0).astype(np.float32)
        uc = np.where(np.isfinite(gx_zb), gx_zb / (gm_zb + 1.0e-6), 0.0).astype(np.float32)
        del gy_zb, gx_zb, gm_zb
        zb_fill = np.where(np.isfinite(z_base), z_base, 0.0).astype(np.float32)
        del z_base
        shift_px = np.clip(0.55 * zb_fill / 100.0, 0.0, 5.0).astype(np.float32)
        del zb_fill
        rr = np.arange(shape[0], dtype=np.float32)[:, None]
        cc = np.arange(shape[1], dtype=np.float32)[None, :]
        tgt_r = np.clip(np.rint(rr - shift_px * ur).astype(np.int32), 0, shape[0] - 1)
        tgt_c = np.clip(np.rint(cc - shift_px * uc).astype(np.int32), 0, shape[1] - 1)
        del shift_px, ur, uc
        splat = np.zeros(shape, dtype=np.float32)
        valid_hw = fp & np.isfinite(sub_step)
        np.maximum.at(splat, (tgt_r[valid_hw], tgt_c[valid_hw]), sub_step[valid_hw])
        del tgt_r, tgt_c, sub_step, valid_hw
        updip = ndi.gaussian_filter(splat, sigma=0.9, mode="nearest").astype(np.float32)
        del splat
        _save("updip_listric_trace", updip)

        c2_mag, s2_mag, coh_mag = _structure_tensor_orientation(asig_mag_crest, fp, 1.5, 4.0)
        del asig_mag_crest
        c2_lis, s2_lis, coh_lis = _structure_tensor_orientation(updip, fp, 1.5, 4.0)
        del updip
        cos2_delta = np.clip(c2_mag * c2_lis + s2_mag * s2_lis, -1.0, 1.0)
        coaxial = (0.5 * (1.0 + cos2_delta) * np.sqrt(coh_mag * coh_lis)).astype(np.float32)
        _save("crustal_coaxial_alignment", coaxial)
        del c2_mag, s2_mag, coh_mag, c2_lis, s2_lis, coh_lis, cos2_delta, coaxial
        gc.collect()

        # Group 3: Transtensional Coulomb, Microseismic Localization & GDR Vent Corridor
        g2 = np.maximum(0.0, reader.read("geod_2ndinv", fp))
        gsh = np.maximum(0.0, reader.read("geod_shearrate", fp))
        gdil = np.maximum(0.0, reader.read("geod_dilaterate", fp))
        transtens = ((gdil / (g2 + 2.0)) * np.log1p(gsh)).astype(np.float32)
        del g2, gsh, gdil
        _save("transtensional_coulomb", transtens)

        deq_clean = np.maximum(0.0, reader.read("deq_n100a15", fp))
        ieq_clean = np.maximum(0.0, reader.read("ieq_n100a15", fp))
        seis_loc = (np.log1p(ieq_clean) / (1.0 + deq_clean / 5000.0)).astype(np.float32)
        del deq_clean, ieq_clean
        _save("seismic_proximity_intensity", seis_loc)
        del seis_loc

        def _exp_prox(m_path: Path, scale_m: float) -> np.ndarray:
            mask = _read_u8_mask(m_path, shape)
            if not np.any(mask):
                return np.zeros(shape, dtype=np.float32)
            dist_m = ndi.distance_transform_edt(~mask).astype(np.float32) * 100.0
            return np.exp(-dist_m / float(scale_m)).astype(np.float32)

        vent_prox = (
            _exp_prox(ext_dir / "derived_gdr_2m_probes_100m_u8.tif", 2500.0)
            + 0.8 * _exp_prox(ext_dir / "derived_gdr_paleo_100m_u8.tif", 2500.0)
            + 0.5 * _exp_prox(ext_dir / "derived_gdr_volcanics_100m_u8.tif", 3500.0)
        )
        z_tr = robust_positive_z(transtens, fp)
        del transtens
        vent_corr = (vent_prox * (1.0 + 0.35 * z_tr)).astype(np.float32)
        _save("hydrothermal_vent_corridor", vent_corr)
        del vent_prox, z_tr, vent_corr
        gc.collect()

        # Group 4: Hydrothermal magnetite-destruction x potassic K/Th x clay-cap ridge
        rtp_s = reader.read("rtp", fp)
        z_demag = robust_positive_z(
            valid_gaussian(rtp_s, sigma=6.0) - valid_gaussian(rtp_s, sigma=1.5), fp
        )
        del rtp_s
        cond_s = reader.read("cond_surf", fp)
        z_cond = robust_positive_z(
            valid_gaussian(cond_s, sigma=1.0) - valid_gaussian(cond_s, sigma=6.0), fp
        )
        del cond_s
        k_s = reader.read("K", fp)
        th_s = reader.read("Th", fp)
        k_over_th = np.full(shape, np.nan, dtype=np.float32)
        rad_ok = fp & np.isfinite(k_s) & np.isfinite(th_s) & ((k_s > 0.0) | (th_s > 0.0))
        k_over_th[rad_ok] = (
            np.maximum(0.0, k_s[rad_ok]) / (np.maximum(0.0, th_s[rad_ok]) + 5.0)
        ).astype(np.float32)
        del k_s, th_s
        z_kth = robust_positive_z(k_over_th, fp)
        del k_over_th
        rad_med = float(np.median(z_kth[rad_ok])) if np.any(rad_ok) else 0.0
        z_kth[~rad_ok & fp] = rad_med
        del rad_ok
        hydro_alt = (
            np.cbrt((z_demag + 0.25) * (z_kth + 0.25) * (z_cond + 0.25)) - 0.25
        ).astype(np.float32)
        _save("hydrothermal_alteration_demag", hydro_alt)
        del z_demag, z_cond, z_kth, hydro_alt
        gc.collect()

        # Group 5: Piedmont flexure & Coverage-clean 3DEP LiDAR scarp polarity
        elev_s = valid_gaussian(reader.read("det_elev", fp), sigma=2.0)
        elev_med = float(np.median(elev_s[fp & np.isfinite(elev_s)]))
        elev_fill = np.where(np.isfinite(elev_s), elev_s, elev_med).astype(np.float32)
        del elev_s
        ey, ex = np.gradient(elev_fill)
        del elev_fill
        eyy, eyx = np.gradient(ey)
        del ey
        exy, exx = np.gradient(ex)
        del ex
        hxy = 0.5 * (exy + eyx)
        del exy, eyx
        lam_min = 0.5 * ((exx + eyy) - np.hypot(exx - eyy, 2.0 * hxy))
        del exx, eyy, hxy
        concavity = np.maximum(0.0, -lam_min).astype(np.float32)
        del lam_min
        slope_deg = np.maximum(0.0, reader.read("det_elev_slope", fp))
        piedmont_flex = (concavity / (1.0 + slope_deg / 7.0)).astype(np.float32)
        _save("piedmont_flexure_bridge", piedmont_flex)
        del concavity, slope_deg, piedmont_flex
        gc.collect()

        up_s = reader.read("upface_max", fp)
        dn_s = reader.read("downface_max", fp)
        st_s = reader.read("step_max", fp)
        ch_s = reader.read("coh100", fp)
        lidar_ok = fp & np.isfinite(up_s) & np.isfinite(dn_s) & np.isfinite(st_s) & np.isfinite(ch_s)
        lidar_asym = np.full(shape, np.nan, dtype=np.float32)
        lidar_asym[lidar_ok] = (
            (np.abs(up_s[lidar_ok] - dn_s[lidar_ok]) / (up_s[lidar_ok] + dn_s[lidar_ok] + 1.0))
            * np.log1p(np.maximum(0.0, st_s[lidar_ok]))
            * np.clip(ch_s[lidar_ok] / 255.0, 0.0, 1.0)
        ).astype(np.float32)
        _save("lidar_scarp_asymmetry", lidar_asym)
        del up_s, dn_s, st_s, ch_s, lidar_ok, lidar_asym
        gc.collect()

    return {
        name: np.load(cache_dir / f"{name}.npy", mmap_mode="r")
        for name in H31T_STATIC_CHANNELS
    }


def _splitmix64_anchor(min_row: int, min_col: int) -> int:
    """Deterministic 64-bit hash of a component's canonical `(min_row, min_col)` anchor."""
    x = ((int(min_row) & 0xFFFFFFFF) << 32) ^ (int(min_col) & 0xFFFFFFFF) ^ 0x9E3779B97F4A7C15
    x = ((x ^ (x >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
    x = ((x ^ (x >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
    return (x ^ (x >> 31)) & 0xFFFFFFFFFFFFFFFF


def compute_fold_visible_fracture_fields(
    visible_catalogue: np.ndarray,
    footprint: np.ndarray,
    *,
    min_component_px: int = 8,
    n_color_planes: int = 8,
) -> dict[str, np.ndarray]:
    """Build fold-visible-only tip propagation & en-echelon relay step-over fields.

    CRITICAL LEAKAGE GUARANTEE:
      Uses `visible_catalogue` ONLY. Component hash signatures depend exclusively
      on each visible component's own `(min_row, min_col)` anchor, so mutating or
      withholding disjoint components produces zero numerical change on visible
      component hashes.
    """
    vis = np.asarray(visible_catalogue, dtype=bool) & np.asarray(footprint, dtype=bool)
    H, W = vis.shape
    tip_lobe = np.zeros((H, W), dtype=np.float32)
    relay_bridge = np.zeros((H, W), dtype=np.float32)

    if not np.any(vis):
        tip_lobe[~footprint] = np.nan
        relay_bridge[~footprint] = np.nan
        return {
            "vis_wingcrack_tip_lobe": tip_lobe,
            "vis_relay_dilation_bridge": relay_bridge,
        }

    structure8 = np.ones((3, 3), dtype=np.int8)
    comp_labels, n_comp = ndi.label(vis, structure=structure8)
    if n_comp == 0:
        tip_lobe[~footprint] = np.nan
        relay_bridge[~footprint] = np.nan
        return {
            "vis_wingcrack_tip_lobe": tip_lobe,
            "vis_relay_dilation_bridge": relay_bridge,
        }

    counts = np.bincount(comp_labels.ravel())
    slices = ndi.find_objects(comp_labels)

    # 1. Wing-crack tip propagation lobes from principal extremities of visible traces
    patch_r = 36  # 3.6 km radius
    local_grid_r, local_grid_c = np.mgrid[-patch_r : patch_r + 1, -patch_r : patch_r + 1].astype(
        np.float32
    )

    # Deterministic color bitmasks per component ID (0 unused)
    comp_hashes = np.zeros(n_comp + 1, dtype=np.uint64)

    for cid in range(1, n_comp + 1):
        if counts[cid] < min_component_px:
            continue
        sl = slices[cid - 1]
        if sl is None:
            continue
        sub = comp_labels[sl] == cid
        rr_loc, cc_loc = np.nonzero(sub)
        if rr_loc.size < min_component_px:
            continue
        r0_off = int(sl[0].start)
        c0_off = int(sl[1].start)
        rr = rr_loc.astype(np.float32) + r0_off
        cc = cc_loc.astype(np.float32) + c0_off

        # Canonical anchor for order-invariant color-coding
        min_r = int(rr_loc.min()) + r0_off
        min_c = int(cc_loc[rr_loc == rr_loc.min()].min()) + c0_off
        comp_hashes[cid] = np.uint64(_splitmix64_anchor(min_r, min_c))

        # Principal axis & two extremities of this trace component
        mr = float(rr.mean())
        mc = float(cc.mean())
        dr = rr - mr
        dc = cc - mc
        cov_rr = float(np.dot(dr, dr))
        cov_cc = float(np.dot(dc, dc))
        cov_rc = float(np.dot(dr, dc))
        angle = 0.5 * np.arctan2(2.0 * cov_rc, cov_rr - cov_cc)
        ar = float(np.cos(angle))
        ac = float(np.sin(angle))
        proj = dr * ar + dc * ac
        idx_min = int(np.argmin(proj))
        idx_max = int(np.argmax(proj))

        for tip_idx in (idx_min, idx_max):
            tr = float(rr[tip_idx])
            tc = float(cc[tip_idx])
            # Local tangent pointing outward from neighboring trace pixels within 9 px
            d2 = (rr - tr) ** 2 + (cc - tc) ** 2
            near = (d2 > 0.0) & (d2 <= 81.0)
            if np.count_nonzero(near) >= 2:
                vr = tr - float(rr[near].mean())
                vc = tc - float(cc[near].mean())
            else:
                vr = tr - mr
                vc = tc - mc
            vnorm = float(np.hypot(vr, vc))
            if vnorm < 1.0e-4:
                continue
            tr_u = vr / vnorm
            tc_u = vc / vnorm

            ir = int(round(tr))
            ic = int(round(tc))
            r_lo = max(0, ir - patch_r)
            r_hi = min(H, ir + patch_r + 1)
            c_lo = max(0, ic - patch_r)
            c_hi = min(W, ic + patch_r + 1)

            gr = local_grid_r[(r_lo - ir + patch_r) : (r_hi - ir + patch_r), (c_lo - ic + patch_r) : (c_hi - ic + patch_r)]
            gc = local_grid_c[(r_lo - ir + patch_r) : (r_hi - ir + patch_r), (c_lo - ic + patch_r) : (c_hi - ic + patch_r)]

            s_par_m = (gr * tr_u + gc * tc_u) * 100.0
            s_perp_m = (-gr * tc_u + gc * tr_u) * 100.0
            ahead = (s_par_m > 100.0) & (s_par_m <= 3500.0)
            if not np.any(ahead):
                continue
            sigma_perp = 300.0 + 0.18 * np.maximum(0.0, s_par_m)
            lobe = np.zeros_like(s_par_m, dtype=np.float32)
            lobe[ahead] = (
                np.exp(-s_par_m[ahead] / 1800.0)
                * np.exp(-0.5 * (s_perp_m[ahead] / sigma_perp[ahead]) ** 2)
            ).astype(np.float32)
            cur = tip_lobe[r_lo:r_hi, c_lo:c_hi]
            np.maximum(cur, lobe, out=cur)

    # 2. Color-coded inter-component en-echelon relay bridge (order-invariant anchor hash)
    active_comp = counts >= min_component_px
    active_comp[0] = False
    for bit in range(int(n_color_planes)):
        bit_zero_lut = active_comp & (((comp_hashes >> np.uint64(bit)) & np.uint64(1)) == 0)
        bit_one_lut = active_comp & (((comp_hashes >> np.uint64(bit)) & np.uint64(1)) == 1)
        m0 = bit_zero_lut[comp_labels]
        m1 = bit_one_lut[comp_labels]
        if (not np.any(m0)) or (not np.any(m1)):
            continue
        d0_m = ndi.distance_transform_edt(~m0).astype(np.float32) * 100.0
        d1_m = ndi.distance_transform_edt(~m1).astype(np.float32) * 100.0
        sum_d = d0_m + d1_m
        valid_bridge = (d0_m <= 2500.0) & (d1_m <= 2500.0) & (sum_d >= 300.0)
        if not np.any(valid_bridge):
            continue
        score = np.zeros((H, W), dtype=np.float32)
        score[valid_bridge] = np.exp(-sum_d[valid_bridge] / 1600.0).astype(np.float32)
        np.maximum(relay_bridge, score, out=relay_bridge)

    tip_lobe[~footprint] = np.nan
    relay_bridge[~footprint] = np.nan
    return {
        "vis_wingcrack_tip_lobe": tip_lobe,
        "vis_relay_dilation_bridge": relay_bridge,
    }
