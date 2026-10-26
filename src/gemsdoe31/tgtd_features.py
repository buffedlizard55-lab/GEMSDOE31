"""Label-free physical feature stack for Lane H31-J (TGTD-Submod).

Combines four orthogonal Basin-and-Range blind/concealed fault mechanisms on top of the
unchanged SHA-256-pinned ``vendor/gems57`` 19-band feature cache, streamed into a
low-memory disk-backed ``float32`` memmap (`< 500 MB` peak RSS):

1. **Tabular Gravity-Tensor Dimensionality (TGTD)** — Pedersen & Rasmussen (1990) / Beiki (2010)
   3-D Laplace spectral gravity gradient tensor ``T_G`` at z = 300 m and z = 1000 m upward
   continuation, isolating elongated 2-D basement fault contacts (``T_2D -> 1``) while
   suppressing axisymmetric 3-D calderas, stocks, and diapirs (``T_2D -> 0``).
2. **Spectral RTP Magnetic Tensor & Hydrothermal Demagnetization** — True magnetic Miller-Singh
   tilt angle (correcting the B06 radiometric-TC header mislabel in ``training_features.tif``),
   2-D magnetic tabular index, magnetite-destruction trough ``max(-RTP_zz, 0) * cond_surf``,
   and pi-periodic strike co-alignment ``cos^2(phi_G - phi_RTP)``.
3. **Channeled Geothermometer Upflow Disequilibrium (DOE GDR #1391)** — Fournier (1977) /
   Fournier & Truesdell (1973) quartz, chalcedony, and Na-K-Ca chemical geothermometer
   disequilibrium ``Delta_T_diseq = max(T_geotherm) - T_outlet`` from ``gdr_wellspring_in_footprint.csv``
   (strictly excluding ``dist_known_fault_px``), channeled onto 1-D tabular gravity steps and
   conductive/potassic alteration corridors rather than isotropic circular blobs.
4. **Piedmont-Toe Concave Flexure (PTCF), One-Sided Relief Asymmetry & Hurst Break** —
   Multi-scale concave-upward piedmont-toe flexure, V-canyon-suppressed cross-strike step
   asymmetry, multi-scale topographic Hurst roughness transition, plus seam-free interior-feathered
   1 m 3DEP LiDAR scarp polarity for Specialist B.

Anti-leakage invariants:
- Never reads ``labels.tif``, ``derived_gdr_qfaults_v2_100m_u8.tif``, ``derived_sgmc_faults_100m_u8.tif``,
  or ``derived_gdr_paleo_100m_u8.tif``.
- Never reads or retains ``dist_known_fault_px`` from ``gdr_wellspring_in_footprint.csv``.
- Zero catalogue-proximity, tip, or relay continuation features anywhere in the stack.
"""

from __future__ import annotations

from dataclasses import dataclass
import gc
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from scipy.fft import irfft2, rfft2
from scipy.ndimage import distance_transform_edt, gaussian_filter, zoom

WELLSPRING_SHA256 = "122718e65bdf55aab0ee12ad20d80062f0deb1de957225a61ad880dd5dc196ea"
ALLOWED_WELLSPRING_COLS = (
    "row",
    "col",
    "temp_c",
    "geothermquartz_c",
    "geothermchalc_c",
    "geothermcat_c",
)
FORBIDDEN_WELLSPRING_COLS = frozenset({"dist_known_fault_px"})
SQRT_54 = float(np.sqrt(54.0))  # Exact normalizer 3*sqrt(6) for trace-free 3x3 harmonic tensors

RAW_BAND_NAMES = (
    "raw_b01_mag_anom",
    "raw_b02_rtp",
    "raw_b03_tmi_hg",
    "raw_b04_geod_2ndinv",
    "raw_b05_iso_grav_slope",
    "raw_b06_rad_tc",
    "raw_b07_geod_shearrate",
    "raw_b08_geod_dilaterate",
    "raw_b09_tmi_vg",
    "raw_b10_deq_density",
    "raw_b11_iso_grav_vg",
    "raw_b12_det_elev",
    "raw_b13_iso_grav_anom",
    "raw_b14_tmi",
    "raw_b15_depth_to_base",
    "raw_b16_ieq_density",
    "raw_b17_cond_surf",
    "raw_b18_iso_grav_signed_hg",
    "raw_b19_det_elev_slope",
)


@dataclass(frozen=True)
class TGTDFeatureBundle:
    x_fp: np.memmap | np.ndarray
    feature_names: tuple[str, ...]
    subsurface_cols: np.ndarray
    full_footprint_cols: np.ndarray
    lidar_specialist_cols: np.ndarray
    lidar_valid_fp: np.ndarray
    lidar_interior_weight_fp: np.ndarray
    wellspring_summary: dict[str, float | int | str]
    memmap_path: str | None = None


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_pinned_cache(root: Path) -> list[Path]:
    t_pins = json.loads((root / "registry/template_pins.json").read_text())["files"]
    for fname, meta in t_pins.items():
        vp = root / "vendor/gems57" / fname
        if not vp.is_file() or _sha256_file(vp) != meta["sha256"]:
            raise ValueError(f"Pinned vendor/gems57 file modified or missing: {fname}")

    cache_meta = json.loads((root / "evidence/feature_cache.json").read_text())["bands"]
    paths: list[Path] = []
    for entry in cache_meta:
        p = root / entry["cache_file"]
        if not p.is_file():
            raise FileNotFoundError(f"Missing shared template cache band: {p}")
        if _sha256_file(p) != entry["sha256"]:
            raise ValueError(f"Shared template cache band SHA-256 mismatch: {entry['cache_file']}")
        paths.append(p)
    return paths


def _inpaint_and_taper(field: np.ndarray, footprint: np.ndarray, *, taper_px: float = 40.0) -> tuple[np.ndarray, float]:
    """Nearest-neighbor EDT inpainting outside valid footprint + smooth Gaussian edge taper."""
    f = np.asarray(field, dtype=np.float32)
    valid = footprint & np.isfinite(f) & (np.abs(f) < 1e20)
    vals = f[valid].astype(np.float64)
    mean = float(vals.mean())
    std = float(vals.std())
    if std < 1e-12:
        std = 1.0
    normed = np.zeros(f.shape, dtype=np.float32)
    normed[valid] = ((vals - mean) / std).astype(np.float32)
    dist_out, nearest_idx = distance_transform_edt(~valid, return_indices=True)
    filled = normed[nearest_idx[0], nearest_idx[1]].astype(np.float32)
    del normed, nearest_idx
    if taper_px > 0.0:
        filled *= np.exp(-((dist_out.astype(np.float32) / float(taper_px)) ** 2)).astype(np.float32)
    return filled, std


def smooth_regional_zscore(
    field: np.ndarray,
    footprint: np.ndarray,
    *,
    downsample: int = 12,
    coarse_sigma: float = 50.0,
) -> np.ndarray:
    """Seam-free 60 km (12 * 50 px = 600 px) label-free local standardization (returns fp vector)."""
    f = np.asarray(field, dtype=np.float32)
    valid = (footprint & np.isfinite(f) & (np.abs(f) < 1e20)).astype(np.float32)
    clean = np.where(valid > 0.5, f, 0.0).astype(np.float32)
    h, w = f.shape

    w_c = zoom(valid, 1.0 / downsample, order=1)
    x_c = zoom(clean, 1.0 / downsample, order=1)
    x2_c = zoom(clean * clean, 1.0 / downsample, order=1)

    denom = gaussian_filter(w_c, sigma=coarse_sigma, mode="nearest") + 1e-6
    mu_c = gaussian_filter(x_c, sigma=coarse_sigma, mode="nearest") / denom
    ex2_c = gaussian_filter(x2_c, sigma=coarse_sigma, mode="nearest") / denom
    sd_c = np.sqrt(np.maximum(ex2_c - mu_c * mu_c, 1e-6)).astype(np.float32)

    zoom_factors = (h / mu_c.shape[0], w / mu_c.shape[1])
    mu_fp = zoom(mu_c.astype(np.float32), zoom_factors, order=1)[:h, :w][footprint]
    sd_fp = zoom(sd_c, zoom_factors, order=1)[:h, :w][footprint]
    valid_fp = valid[footprint] > 0.5
    clean_fp = clean[footprint]
    global_sd = float(np.std(clean_fp[valid_fp])) if np.any(valid_fp) else 1.0
    sd_fp = np.maximum(sd_fp, 0.15 * max(global_sd, 1e-6))

    z_fp = np.clip((clean_fp - mu_fp) / sd_fp, -8.0, 8.0).astype(np.float32)
    z_fp[~valid_fp] = np.nan
    return z_fp


def compute_harmonic_tensor(
    field: np.ndarray,
    footprint: np.ndarray,
    *,
    upward_px: float = 3.0,
    tilt_width_rad: float = 0.35,
) -> dict[str, np.ndarray]:
    """Memory-lean 3-D Laplace spectral potential-field tensor & Pedersen-Rasmussen 2-D index."""
    filled, _ = _inpaint_and_taper(field, footprint)
    h, w = filled.shape

    ky = (2.0 * np.pi * np.fft.fftfreq(h, d=1.0)).astype(np.float32)[:, None]
    kx = (2.0 * np.pi * np.fft.rfftfreq(w, d=1.0)).astype(np.float32)[None, :]
    k_mag = np.hypot(ky, kx).astype(np.float32)
    f_hat = rfft2(filled, workers=2) * np.exp(-k_mag * float(upward_px)).astype(np.float32)
    del filled

    ux = irfft2((1j * kx) * f_hat, s=(h, w), workers=2).astype(np.float32)
    uy = irfft2((1j * ky) * f_hat, s=(h, w), workers=2).astype(np.float32)
    uz = irfft2(k_mag * f_hat, s=(h, w), workers=2).astype(np.float32)

    grad_h = np.hypot(ux, uy).astype(np.float32)
    tilt = np.arctan2(uz, grad_h + 1e-9).astype(np.float32)
    gh2 = grad_h * grad_h + 1e-9
    cos2_strike = ((uy * uy - ux * ux) / gh2).astype(np.float32)
    sin2_strike = ((-2.0 * ux * uy) / gh2).astype(np.float32)
    del ux, uy

    txx = irfft2(-(kx * kx) * f_hat, s=(h, w), workers=2).astype(np.float32)
    tyy = irfft2(-(ky * ky) * f_hat, s=(h, w), workers=2).astype(np.float32)
    txy = irfft2(-(kx * ky) * f_hat, s=(h, w), workers=2).astype(np.float32)
    txz = irfft2((1j * kx * k_mag) * f_hat, s=(h, w), workers=2).astype(np.float32)
    tyz = irfft2((1j * ky * k_mag) * f_hat, s=(h, w), workers=2).astype(np.float32)
    del f_hat, kx, ky, k_mag

    tzz = (-(txx + tyy)).astype(np.float32)

    # Evaluate cubic determinant invariant in float64 on footprint/grid in chunks or directly
    t2d = np.zeros((h, w), dtype=np.float32)
    txx_f = txx[footprint].astype(np.float64)
    tyy_f = tyy[footprint].astype(np.float64)
    tzz_f = tzz[footprint].astype(np.float64)
    txy_f = txy[footprint].astype(np.float64)
    txz_f = txz[footprint].astype(np.float64)
    tyz_f = tyz[footprint].astype(np.float64)

    det_f = (
        txx_f * (tyy_f * tzz_f - tyz_f * tyz_f)
        - txy_f * (txy_f * tzz_f - tyz_f * txz_f)
        + txz_f * (txy_f * tyz_f - tyy_f * txz_f)
    )
    frob_f = np.sqrt(
        np.maximum(txx_f * txx_f + tyy_f * tyy_f + tzz_f * tzz_f + 2.0 * (txy_f * txy_f + txz_f * txz_f + tyz_f * tyz_f), 0.0)
    )
    noise_floor = float(np.percentile(frob_f, 10.0)) if frob_f.size else 1e-4
    denom = (frob_f ** 3) + (max(noise_floor, 1e-4) ** 3)
    inv_i = np.clip(-SQRT_54 * det_f / denom, -1.0, 1.0)
    t2d[footprint] = (1.0 - np.abs(inv_i)).astype(np.float32)
    del txx_f, tyy_f, tzz_f, txy_f, txz_f, tyz_f, det_f, frob_f, inv_i

    tr_h = 0.5 * (txx + tyy)
    rad_h = np.hypot(0.5 * (txx - tyy), txy)
    curv_ridge = (-(tr_h - rad_h)).astype(np.float32)
    del txx, tyy, txy, txz, tyz, tr_h, rad_h

    crest = (t2d * grad_h * np.exp(-((tilt / float(tilt_width_rad)) ** 2))).astype(np.float32)
    return {
        "t2d": t2d,
        "tilt": tilt,
        "grad_h": grad_h,
        "uz": uz,
        "uzz": tzz,
        "crest": crest,
        "curv_ridge": curv_ridge,
        "cos2_strike": cos2_strike,
        "sin2_strike": sin2_strike,
    }


def load_wellspring_geothermometry(
    csv_path: Path,
    shape: tuple[int, int],
    footprint: np.ndarray,
    *,
    requested_cols: tuple[str, ...] = ALLOWED_WELLSPRING_COLS,
) -> dict[str, np.ndarray | dict[str, float | int | str]]:
    """Load DOE GDR #1391 well/spring geothermometry while strictly banning ``dist_known_fault_px``."""
    if any(c in FORBIDDEN_WELLSPRING_COLS for c in requested_cols):
        raise ValueError(f"Forbidden label-derived column requested: {requested_cols}")
    if set(requested_cols) != set(ALLOWED_WELLSPRING_COLS):
        raise ValueError(f"Unexpected well/spring column request: {requested_cols}")
    if not csv_path.is_file():
        raise FileNotFoundError(f"Missing well/spring compilation CSV: {csv_path}")
    actual_sha = _sha256_file(csv_path)
    if actual_sha != WELLSPRING_SHA256:
        raise ValueError(f"Well/spring CSV SHA-256 mismatch: {actual_sha} != {WELLSPRING_SHA256}")

    df = pd.read_csv(csv_path, usecols=list(ALLOWED_WELLSPRING_COLS))
    assert "dist_known_fault_px" not in df.columns, "Leakage guard failed: dist_known_fault_px present"

    h, w = shape
    rows = pd.to_numeric(df["row"], errors="coerce")
    cols = pd.to_numeric(df["col"], errors="coerce")
    valid_rc = rows.notna() & cols.notna()
    df = df.loc[valid_rc].copy()
    r_idx = df["row"].astype(int).to_numpy()
    c_idx = df["col"].astype(int).to_numpy()
    in_bounds = (r_idx >= 0) & (r_idx < h) & (c_idx >= 0) & (c_idx < w)
    df = df.iloc[in_bounds].copy()
    r_idx = r_idx[in_bounds]
    c_idx = c_idx[in_bounds]
    in_fp = footprint[r_idx, c_idx]
    df = df.iloc[in_fp].copy()
    r_idx = r_idx[in_fp]
    c_idx = c_idx[in_fp]

    temp_c = np.clip(pd.to_numeric(df["temp_c"], errors="coerce").to_numpy(dtype=np.float64), 0.0, 320.0)
    t_qtz = np.clip(pd.to_numeric(df["geothermquartz_c"], errors="coerce").to_numpy(dtype=np.float64), 0.0, 320.0)
    t_chl = np.clip(pd.to_numeric(df["geothermchalc_c"], errors="coerce").to_numpy(dtype=np.float64), 0.0, 320.0)
    t_cat = np.clip(pd.to_numeric(df["geothermcat_c"], errors="coerce").to_numpy(dtype=np.float64), 0.0, 320.0)

    geotherm_stack = np.vstack([
        np.where(np.isfinite(t_qtz), t_qtz, -1.0),
        np.where(np.isfinite(t_chl), t_chl, -1.0),
        np.where(np.isfinite(t_cat), t_cat, -1.0),
    ])
    t_res = np.max(geotherm_stack, axis=0)
    has_geotherm = t_res >= 0.0
    outlet_ref = np.where(np.isfinite(temp_c), np.maximum(temp_c, 15.0), 18.0)

    diseq = np.where(has_geotherm, np.maximum(t_res - outlet_ref, 0.0), 0.0).astype(np.float32)
    outlet_excess = np.where(np.isfinite(temp_c), np.maximum(temp_c - 20.0, 0.0), 0.0).astype(np.float32)
    res_excess = np.where(has_geotherm, np.maximum(t_res - 50.0, 0.0), 0.0).astype(np.float32)

    grid_diseq = np.zeros(shape, dtype=np.float32)
    grid_outlet = np.zeros(shape, dtype=np.float32)
    grid_res = np.zeros(shape, dtype=np.float32)
    grid_site = np.zeros(shape, dtype=np.float32)

    np.maximum.at(grid_diseq, (r_idx, c_idx), diseq)
    np.maximum.at(grid_outlet, (r_idx, c_idx), outlet_excess)
    np.maximum.at(grid_res, (r_idx, c_idx), res_excess)
    grid_site[r_idx, c_idx] = 1.0

    def _nw_potential(val_grid: np.ndarray, site_grid: np.ndarray, sigma_px: float, prior_w: float) -> np.ndarray:
        num = gaussian_filter(val_grid, sigma=sigma_px, mode="constant")
        den = gaussian_filter(site_grid, sigma=sigma_px, mode="constant") + float(prior_w)
        return (num / den).astype(np.float32)

    peak_w_15 = 1.0 / (2.0 * np.pi * (15.0 ** 2))
    peak_w_45 = 1.0 / (2.0 * np.pi * (45.0 ** 2))
    diseq_1p5km = _nw_potential(grid_diseq, grid_site, sigma_px=15.0, prior_w=1.5 * peak_w_15)
    diseq_4p5km = _nw_potential(grid_diseq, grid_site, sigma_px=45.0, prior_w=2.0 * peak_w_45)
    thermal_comb = _nw_potential(
        np.maximum(grid_res, 1.25 * grid_outlet), grid_site, sigma_px=25.0, prior_w=1.5 / (2.0 * np.pi * 625.0)
    )

    summary = {
        "sha256": actual_sha,
        "in_footprint_records": int(len(df)),
        "unique_cells": int(grid_site.sum()),
        "cells_with_disequilibrium_gt_25c": int((grid_diseq > 25.0).sum()),
        "max_disequilibrium_c": float(grid_diseq.max()),
        "dist_known_fault_px_loaded": False,
    }
    return {
        "diseq_1p5km": diseq_1p5km,
        "diseq_4p5km": diseq_4p5km,
        "thermal_2p5km": thermal_comb,
        "summary": summary,
    }


def _compute_ptcf_and_hurst_fp(
    det_elev: np.ndarray,
    det_slope: np.ndarray,
    depth_base: np.ndarray,
    footprint: np.ndarray,
) -> dict[str, np.ndarray]:
    """Memory-lean Piedmont-Toe Concave Flexure (PTCF), V-canyon suppressor, & Hurst break (fp vectors)."""
    e_raw = np.asarray(det_elev, dtype=np.float32)
    valid = footprint & np.isfinite(e_raw) & (np.abs(e_raw) < 1e20)
    _, idx = distance_transform_edt(~valid, return_indices=True)
    elev = np.where(valid, e_raw, e_raw[idx[0], idx[1]]).astype(np.float32)
    del e_raw, idx

    def _pos_lap_fp(arr: np.ndarray, sigma: float) -> np.ndarray:
        lap = gaussian_filter(arr, sigma=sigma, order=(2, 0), mode="nearest")
        lap += gaussian_filter(arr, sigma=sigma, order=(0, 2), mode="nearest")
        lap *= float(sigma * sigma)
        np.maximum(lap, 0.0, out=lap)
        return lap[footprint].astype(np.float32)

    ptcf_300m = _pos_lap_fp(elev, 3.0)
    ptcf_800m = _pos_lap_fp(elev, 8.0)
    ptcf_1600m = _pos_lap_fp(elev, 16.0)

    es = gaussian_filter(elev, sigma=3.0, mode="nearest")
    gy = gaussian_filter(es, sigma=2.0, order=(1, 0), mode="nearest")
    gx = gaussian_filter(es, sigma=2.0, order=(0, 1), mode="nearest")
    gnorm = np.hypot(gx, gy) + 1e-6

    h, w = elev.shape
    fp_r, fp_c = np.nonzero(footprint)
    ny_fp = gy[footprint] / gnorm[footprint]
    nx_fp = gx[footprint] / gnorm[footprint]
    del gx, gy, gnorm

    step_px = 6.0
    rp = np.clip(np.round(fp_r + step_px * ny_fp), 0, h - 1).astype(np.int32)
    cp = np.clip(np.round(fp_c + step_px * nx_fp), 0, w - 1).astype(np.int32)
    rm = np.clip(np.round(fp_r - step_px * ny_fp), 0, h - 1).astype(np.int32)
    cm = np.clip(np.round(fp_c - step_px * nx_fp), 0, w - 1).astype(np.int32)
    del fp_r, fp_c, ny_fp, nx_fp

    es_fp = es[footprint]
    zp = es[rp, cp]
    zm = es[rm, cm]
    del rp, cp, rm, cm, es
    one_sided_ratio = (np.abs(zp - zm) / (np.abs(zp - es_fp) + np.abs(zm - es_fp) + 5.0)).astype(np.float32)
    del zp, zm, es_fp

    elev_reg_fp = gaussian_filter(elev, sigma=25.0, mode="nearest")[footprint]
    piedmont_gate = (1.0 / (1.0 + np.exp((elev[footprint] - elev_reg_fp - 120.0) / 80.0))).astype(np.float32)
    del elev_reg_fp
    ptcf_gated = (np.sqrt(ptcf_300m * ptcf_800m + 1e-6) * one_sided_ratio * piedmont_gate).astype(np.float32)

    mu_150 = gaussian_filter(elev, sigma=1.5, mode="nearest")
    var_150 = np.maximum(gaussian_filter((elev - mu_150) ** 2, sigma=2.5, mode="nearest"), 0.25)
    del mu_150
    mu_600 = gaussian_filter(elev, sigma=6.0, mode="nearest")
    var_600 = np.maximum(gaussian_filter((elev - mu_600) ** 2, sigma=6.0, mode="nearest"), 0.25)
    del mu_600, elev
    hurst_local = (0.5 * np.log2(var_600 / var_150)).astype(np.float32)
    del var_150, var_600
    hy = gaussian_filter(hurst_local, sigma=2.5, order=(1, 0), mode="nearest")
    hx = gaussian_filter(hurst_local, sigma=2.5, order=(0, 1), mode="nearest")
    del hurst_local
    hurst_break = np.hypot(hx[footprint], hy[footprint]).astype(np.float32)
    del hx, hy

    db_raw = np.asarray(depth_base, dtype=np.float32)
    valid_db = footprint & np.isfinite(db_raw) & (np.abs(db_raw) < 1e20)
    _, idx_db = distance_transform_edt(~valid_db, return_indices=True)
    db = np.where(valid_db, db_raw, db_raw[idx_db[0], idx_db[1]]).astype(np.float32)
    del db_raw, idx_db
    dby = gaussian_filter(db, sigma=3.0, order=(1, 0), mode="nearest")
    dbx = gaussian_filter(db, sigma=3.0, order=(0, 1), mode="nearest")
    del db
    basin_margin_grad = np.hypot(dbx[footprint], dby[footprint]).astype(np.float32)
    del dbx, dby

    sl_fp = np.asarray(det_slope[footprint], dtype=np.float32)
    sl_fp = np.where(np.isfinite(sl_fp) & (np.abs(sl_fp) < 1e20), sl_fp, 0.0).astype(np.float32)
    slope_one_sided = (sl_fp * one_sided_ratio * piedmont_gate).astype(np.float32)

    return {
        "ptcf_300m": ptcf_300m,
        "ptcf_800m": ptcf_800m,
        "ptcf_1600m": ptcf_1600m,
        "one_sided_step": one_sided_ratio,
        "ptcf_gated_toe": ptcf_gated,
        "hurst_break": hurst_break,
        "basin_margin_grad": basin_margin_grad,
        "slope_one_sided": slope_one_sided,
    }


def build_tgtd_feature_bundle(
    root: Path,
    footprint: np.ndarray,
    *,
    work_dir: Path | None = None,
) -> TGTDFeatureBundle:
    """Build the complete label-free H31-J footprint feature bundle into a low-RAM float32 memmap."""
    fp = np.asarray(footprint, dtype=bool)
    n_fp = int(fp.sum())
    cache_paths = verify_pinned_cache(root)

    out_dir = work_dir if work_dir is not None else (root / "work/h31j")
    out_dir.mkdir(parents=True, exist_ok=True)
    mm_path = out_dir / "tgtd_features_fp.f32"
    meta_path = out_dir / "tgtd_features_meta.json"

    n_expected = 65
    mm = np.memmap(mm_path, dtype=np.float32, mode="w+", shape=(n_fp, n_expected))
    names: list[str] = []
    is_topographic: list[bool] = []
    is_lidar: list[bool] = []

    def _add(name: str, arr2d_or_fp: np.ndarray, *, topo: bool = False, lidar: bool = False) -> None:
        col_idx = len(names)
        v = arr2d_or_fp[fp] if arr2d_or_fp.ndim == 2 else arr2d_or_fp
        mm[:, col_idx] = np.asarray(v, dtype=np.float32)
        names.append(name)
        is_topographic.append(topo)
        is_lidar.append(lidar)

    def _band_mmap(idx_1based: int) -> np.ndarray:
        return np.load(cache_paths[idx_1based - 1], mmap_mode="r")

    # 1. Load 19 SHA-256-pinned template bands via read-only mmap
    for idx in range(1, 20):
        _add(RAW_BAND_NAMES[idx - 1], _band_mmap(idx), topo=(idx in (12, 19)), lidar=False)

    # 2. Seam-free 60 km local standardization for regional-baseline-drifting layers
    for idx, tag in (
        (13, "z60k_iso_grav_anom"),
        (5, "z60k_iso_grav_slope"),
        (2, "z60k_rtp"),
        (15, "z60k_depth_to_base"),
        (17, "z60k_cond_surf"),
        (12, "z60k_det_elev"),
        (19, "z60k_det_elev_slope"),
        (7, "z60k_geod_shearrate"),
    ):
        _add(tag, smooth_regional_zscore(_band_mmap(idx), fp), topo=(idx in (12, 19)), lidar=False)
    gc.collect()

    # 3. Block 1: 3-D Laplace Spectral Gravity Gradient Tensor & Tabular Dimensionality (TGTD)
    grav_300 = compute_harmonic_tensor(_band_mmap(13), fp, upward_px=3.0)
    grav_1000 = compute_harmonic_tensor(_band_mmap(13), fp, upward_px=10.0)
    tgtd_worm_persist_fp = np.sqrt(np.maximum(grav_300["crest"][fp] * grav_1000["crest"][fp], 0.0)).astype(np.float32)

    _add("tgtd_grav_t2d_300m", grav_300["t2d"])
    _add("tgtd_grav_t2d_1000m", grav_1000["t2d"])
    _add("tgtd_grav_tilt_300m", np.abs(grav_300["tilt"][fp]))
    _add("tgtd_grav_crest_300m", grav_300["crest"])
    _add("tgtd_grav_crest_1000m", grav_1000["crest"])
    _add("tgtd_grav_worm_persist", tgtd_worm_persist_fp)
    _add("tgtd_grav_curv_ridge_300m", grav_300["curv_ridge"])
    _add("tgtd_grav_uzz_300m", np.abs(grav_300["uzz"][fp]))

    grav_t2d_fp = grav_300["t2d"][fp].copy()
    grav_crest_fp = grav_300["crest"][fp].copy()
    grav_cos2_fp = grav_300["cos2_strike"][fp].copy()
    grav_sin2_fp = grav_300["sin2_strike"][fp].copy()
    del grav_300, grav_1000, tgtd_worm_persist_fp
    gc.collect()

    # 4. Block 2: Spectral RTP Magnetic Tensor & Hydrothermal Magnetite-Destruction Corridor
    rtp_300 = compute_harmonic_tensor(_band_mmap(2), fp, upward_px=3.0)
    b17_fp = np.asarray(_band_mmap(17)[fp], dtype=np.float32)
    cond_pos_fp = np.where(np.isfinite(b17_fp), np.clip(b17_fp, 0.0, 10.0), 0.0).astype(np.float32)
    demag_clay_fp = (np.maximum(-rtp_300["uzz"][fp], 0.0) * cond_pos_fp).astype(np.float32)
    strike_coalign_gm_fp = (
        0.5
        * (1.0 + grav_cos2_fp * rtp_300["cos2_strike"][fp] + grav_sin2_fp * rtp_300["sin2_strike"][fp])
        * grav_t2d_fp
        * rtp_300["t2d"][fp]
    ).astype(np.float32)

    _add("mag_rtp_t2d_300m", rtp_300["t2d"])
    _add("mag_rtp_true_tilt_abs_300m", np.abs(rtp_300["tilt"][fp]))
    _add("mag_rtp_crest_300m", rtp_300["crest"])
    _add("mag_demag_clay_corridor", demag_clay_fp)
    _add("gm_tabular_strike_coalign", strike_coalign_gm_fp)
    del rtp_300, demag_clay_fp, strike_coalign_gm_fp
    gc.collect()

    # 5. GeoDAWN Radiometric Alteration & Crustal Transtensional Partitioning (Block 5)
    with rasterio.open(root / "data/external/geodawn_rad_u8.tif") as ds_rad:
        rad_k = ds_rad.read(1)[fp].astype(np.float32)
        rad_th = ds_rad.read(2)[fp].astype(np.float32)
        rad_u = ds_rad.read(3)[fp].astype(np.float32)
    with rasterio.open(root / "data/external/geodawn_extensions_u8.tif") as ds_ext:
        tmi_up150 = ds_ext.read(4).astype(np.float32)

    k_over_th_fp = (rad_k / (rad_th + 8.0)).astype(np.float32)
    u_over_th_fp = (rad_u / (rad_th + 8.0)).astype(np.float32)
    del rad_k, rad_th, rad_u

    tmi_up_y = gaussian_filter(tmi_up150, sigma=2.0, order=(1, 0), mode="nearest")
    tmi_up_x = gaussian_filter(tmi_up150, sigma=2.0, order=(0, 1), mode="nearest")
    tmi_up_grad_fp = np.hypot(tmi_up_x[fp], tmi_up_y[fp]).astype(np.float32)
    del tmi_up150, tmi_up_x, tmi_up_y

    b04 = np.nan_to_num(_band_mmap(4)[fp].astype(np.float32), nan=0.0)
    b07 = np.nan_to_num(_band_mmap(7)[fp].astype(np.float32), nan=0.0)
    b08 = np.nan_to_num(_band_mmap(8)[fp].astype(np.float32), nan=0.0)
    b10 = np.maximum(np.nan_to_num(_band_mmap(10)[fp].astype(np.float32), nan=0.0), 0.0)
    b16 = np.maximum(np.nan_to_num(_band_mmap(16)[fp].astype(np.float32), nan=0.0), 0.0)

    kostrov_fp = ((b07 * np.maximum(b08, 0.0)) / (b04 * b04 + 10.0)).astype(np.float32)
    seismo_fp = (np.log1p(b10) - np.log1p(b16)).astype(np.float32)
    del b04, b07, b08, b10, b16

    _add("rad_k_over_th", k_over_th_fp)
    _add("rad_u_over_th", u_over_th_fp)
    _add("ext_tmi_up150_grad", tmi_up_grad_fp)
    _add("crustal_kostrov_transtension", kostrov_fp)
    _add("crustal_seismo_log_excess", seismo_fp)
    del u_over_th_fp, tmi_up_grad_fp, kostrov_fp, seismo_fp

    # 6. Block 3: Channeled Geothermometer Upflow Disequilibrium (DOE GDR #1391) + 2m Probes/Vents
    ws = load_wellspring_geothermometry(
        root / "data/external/gdr_wellspring_in_footprint.csv", fp.shape, fp
    )
    diseq_1p5_fp = ws["diseq_1p5km"][fp]
    diseq_4p5_fp = ws["diseq_4p5km"][fp]
    therm_2p5_fp = ws["thermal_2p5km"][fp]
    ws_summary = ws["summary"]
    del ws

    with rasterio.open(root / "data/external/derived_gdr_2m_probes_100m_u8.tif") as ds_p:
        probes_u8 = ds_p.read(1).astype(np.float32) / 255.0
    with rasterio.open(root / "data/external/derived_gdr_volcanics_100m_u8.tif") as ds_v:
        volc_u8 = ds_v.read(1).astype(np.float32) / 255.0
    shallow_mag_fp = gaussian_filter(np.maximum(probes_u8, 0.75 * volc_u8), sigma=12.0, mode="constant")[fp].astype(np.float32)
    del probes_u8, volc_u8

    _add("geotherm_diseq_1p5km", diseq_1p5_fp)
    _add("geotherm_diseq_4p5km", diseq_4p5_fp)
    _add("geotherm_channeled_grav_crest", (diseq_4p5_fp * grav_crest_fp).astype(np.float32))
    _add("geotherm_channeled_clay_potassic", (diseq_4p5_fp * cond_pos_fp * k_over_th_fp).astype(np.float32))
    _add("geotherm_thermal_tabular_conduit", ((therm_2p5_fp + 25.0 * shallow_mag_fp) * grav_t2d_fp).astype(np.float32))
    del diseq_1p5_fp, diseq_4p5_fp, therm_2p5_fp, shallow_mag_fp, grav_crest_fp, grav_t2d_fp, cond_pos_fp, k_over_th_fp
    gc.collect()

    # 7. Block 4: Piedmont-Toe Concave Flexure (PTCF), Relief Asymmetry & Hurst Roughness Break
    ptcf = _compute_ptcf_and_hurst_fp(_band_mmap(12), _band_mmap(19), _band_mmap(15), fp)
    _add("basin_margin_thickness_grad", ptcf["basin_margin_grad"], topo=False)
    _add("ptcf_concave_300m", ptcf["ptcf_300m"], topo=True)
    _add("ptcf_concave_800m", ptcf["ptcf_800m"], topo=True)
    _add("ptcf_concave_1600m", ptcf["ptcf_1600m"], topo=True)
    _add("ptcf_one_sided_asymmetry", ptcf["one_sided_step"], topo=True)
    _add("ptcf_gated_piedmont_toe", ptcf["ptcf_gated_toe"], topo=True)
    _add("ptcf_hurst_roughness_break", ptcf["hurst_break"], topo=True)
    _add("ptcf_slope_one_sided", ptcf["slope_one_sided"], topo=True)
    del ptcf
    gc.collect()

    # 8. Block 6: 1 m 3DEP LiDAR Scarp Polarity & Strike Coherence (Specialist B ONLY, interior-feathered)
    with rasterio.open(root / "data/external/lidar_scarp_features_u8.tif") as ds_lid:
        lid_valid_2d = fp & (ds_lid.read(12) >= 128)
        dist_inside_lidar = distance_transform_edt(lid_valid_2d).astype(np.float32)
        ramp = np.clip((dist_inside_lidar - 2.0) / 15.0, 0.0, 1.0)
        lidar_weight_fp = (0.40 * 0.5 * (1.0 - np.cos(np.pi * ramp)))[fp].astype(np.float32)
        lidar_valid_fp = lid_valid_2d[fp]
        lidar_weight_fp[~lidar_valid_fp] = 0.0
        del dist_inside_lidar, ramp, lid_valid_2d

        ex_max_fp = ds_lid.read(1)[fp].astype(np.float32)
        step_fp = ds_lid.read(3)[fp].astype(np.float32)
        lapneg_fp = ds_lid.read(4)[fp].astype(np.float32)
        lappos_fp = ds_lid.read(5)[fp].astype(np.float32)
        down_fp = ds_lid.read(6)[fp].astype(np.float32)
        up_fp = ds_lid.read(7)[fp].astype(np.float32)
        cross_fp = ds_lid.read(8)[fp].astype(np.float32)
        relief_fp = ds_lid.read(9)[fp].astype(np.float32)
        coh_fp = ds_lid.read(10)[fp].astype(np.float32)
        strike_fp = ds_lid.read(11)[fp].astype(np.float32)

    lid_polarity_fp = np.abs(up_fp - down_fp).astype(np.float32)
    lid_step_norm_fp = (step_fp / (relief_fp + 10.0)).astype(np.float32)
    lid_lap_asym_fp = (lapneg_fp - 0.5 * lappos_fp).astype(np.float32)
    phi_lid_fp = (strike_fp / 255.0) * np.pi
    lid_grav_coalign_fp = (
        0.5 * (1.0 + np.cos(2.0 * phi_lid_fp) * grav_cos2_fp + np.sin(2.0 * phi_lid_fp) * grav_sin2_fp) * (coh_fp / 255.0)
    ).astype(np.float32)
    del grav_cos2_fp, grav_sin2_fp, step_fp, lapneg_fp, lappos_fp, down_fp, up_fp, relief_fp, strike_fp, phi_lid_fp

    for lname, lvec in (
        ("lidar_ex_max", ex_max_fp),
        ("lidar_step_norm", lid_step_norm_fp),
        ("lidar_scarp_polarity_abs", lid_polarity_fp),
        ("lidar_lapneg_asym", lid_lap_asym_fp),
        ("lidar_coh100", coh_fp),
        ("lidar_cross_max", cross_fp),
        ("lidar_grav_strike_coalign", lid_grav_coalign_fp),
    ):
        _add(lname, np.where(lidar_valid_fp, lvec, np.nan).astype(np.float32), topo=True, lidar=True)
    del ex_max_fp, lid_step_norm_fp, lid_polarity_fp, lid_lap_asym_fp, coh_fp, cross_fp, lid_grav_coalign_fp

    assert len(names) == n_expected, f"Expected {n_expected} features, built {len(names)}"
    mm.flush()

    subsurface_idx = np.array(
        [i for i, (t, lid) in enumerate(zip(is_topographic, is_lidar)) if not t and not lid],
        dtype=np.int32,
    )
    full_fp_idx = np.array(
        [i for i, lid in enumerate(is_lidar) if not lid],
        dtype=np.int32,
    )
    lidar_spec_idx = np.arange(len(names), dtype=np.int32)

    meta = {
        "n_footprint": n_fp,
        "n_features": len(names),
        "feature_names": names,
        "subsurface_cols": subsurface_idx.tolist(),
        "full_footprint_cols": full_fp_idx.tolist(),
        "lidar_specialist_cols": lidar_spec_idx.tolist(),
        "wellspring_summary": ws_summary,
    }
    meta_path.write_text(json.dumps(meta, indent=2) + "\n")
    np.save(out_dir / "lidar_valid_fp.npy", lidar_valid_fp)
    np.save(out_dir / "lidar_weight_fp.npy", lidar_weight_fp)

    mm_ro = np.memmap(mm_path, dtype=np.float32, mode="r", shape=(n_fp, len(names)))
    return TGTDFeatureBundle(
        x_fp=mm_ro,
        feature_names=tuple(names),
        subsurface_cols=subsurface_idx,
        full_footprint_cols=full_fp_idx,
        lidar_specialist_cols=lidar_spec_idx,
        lidar_valid_fp=lidar_valid_fp,
        lidar_interior_weight_fp=lidar_weight_fp,
        wellspring_summary=ws_summary,
        memmap_path=str(mm_path),
    )


def load_or_build_tgtd_feature_bundle(
    root: Path,
    footprint: np.ndarray,
    *,
    work_dir: Path | None = None,
) -> TGTDFeatureBundle:
    """Reload cached H31-J float32 memmap in <0.1s after verifying input SHA-256 pins, or build it."""
    verify_pinned_cache(root)
    ws_path = root / "data/external/gdr_wellspring_in_footprint.csv"
    if _sha256_file(ws_path) != WELLSPRING_SHA256:
        raise ValueError("Well/spring CSV SHA-256 mismatch")

    out_dir = work_dir if work_dir is not None else (root / "work/h31j")
    mm_path = out_dir / "tgtd_features_fp.f32"
    meta_path = out_dir / "tgtd_features_meta.json"
    lv_path = out_dir / "lidar_valid_fp.npy"
    lw_path = out_dir / "lidar_weight_fp.npy"

    n_fp = int(np.asarray(footprint, dtype=bool).sum())
    if mm_path.is_file() and meta_path.is_file() and lv_path.is_file() and lw_path.is_file():
        meta = json.loads(meta_path.read_text())
        if meta.get("n_footprint") == n_fp and mm_path.stat().st_size == n_fp * meta["n_features"] * 4:
            mm_ro = np.memmap(mm_path, dtype=np.float32, mode="r", shape=(n_fp, meta["n_features"]))
            return TGTDFeatureBundle(
                x_fp=mm_ro,
                feature_names=tuple(meta["feature_names"]),
                subsurface_cols=np.asarray(meta["subsurface_cols"], dtype=np.int32),
                full_footprint_cols=np.asarray(meta["full_footprint_cols"], dtype=np.int32),
                lidar_specialist_cols=np.asarray(meta["lidar_specialist_cols"], dtype=np.int32),
                lidar_valid_fp=np.load(lv_path),
                lidar_interior_weight_fp=np.load(lw_path),
                wellspring_summary=meta["wellspring_summary"],
                memmap_path=str(mm_path),
            )
    return build_tgtd_feature_bundle(root, footprint, work_dir=out_dir)
