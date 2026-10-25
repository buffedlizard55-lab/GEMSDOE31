"""H31-B Multi-Physics Scarp-Hessian-Alteration-Kostrov Fault Detector & Parallel-Run Uniqueness Gate.

Implements four testable geological hypotheses on the 46 prepared Great Basin layers:
- H31-B1: 3DEP 1 m LiDAR & Topographic Scarp Curvature-Throw-Relief Dip-Slip Operator
- H31-B2: Shallow Basement Contact & Multi-Scale Potential-Field Hessian Crest Operator
- H31-B3: GeoDAWN Argillic K-Leaching, Bouguer Terrain Trough & Uranium Redox Mobility Index
- H31-B4: Kostrov Transtensional Strain-Rate, Microseismicity & Spatially-Blocked Fold-OOF Likelihood

Enforces the Parallel-Run Protocol:
1. Single-feature Leakage Canary (holdout ROC-AUC <= 0.90 required for every model feature).
2. Survey-regime-invariant 12 km local standardization (prevents missing airborne survey footprints
   in the SW quadrant from starving western Basin-and-Range fault detection).
3. B=2 (d(catalogue) > 200 m / 2.0 px) catalogue-halo exclusion + Poisson-disk kernel packing
   (min_dist = 2.85 px = 285 m inside the R = 300 m triangular DTI kernel).
4. Uniqueness gate: surface Spearman rank-correlation <= 0.90 before placement AND <= 70% of final
   emitted dots within 3.0 px (300 m) of any registry raster's dots.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.ndimage import distance_transform_edt, gaussian_filter
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

LEAKAGE_AUC_CEILING = 0.90
MAX_SURFACE_SPEARMAN = 0.90
MAX_DOT_OVERLAP_3PX = 0.70


@dataclass(frozen=True)
class UniquenessAudit:
    surface_spearman: dict[str, float]
    dot_overlap_3px: dict[str, float]
    max_surface_spearman: float
    max_dot_overlap_3px: float
    passed_surface_gate: bool
    passed_dot_overlap_gate: bool
    passed_all: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "surface_spearman": {k: round(float(v), 5) for k, v in self.surface_spearman.items()},
            "dot_overlap_3px": {k: round(float(v), 5) for k, v in self.dot_overlap_3px.items()},
            "max_surface_spearman": round(float(self.max_surface_spearman), 5),
            "max_dot_overlap_3px": round(float(self.max_dot_overlap_3px), 5),
            "passed_surface_gate": bool(self.passed_surface_gate),
            "passed_dot_overlap_gate": bool(self.passed_dot_overlap_gate),
            "passed_all": bool(self.passed_all),
        }


def norm_rank(arr: np.ndarray, mask: np.ndarray, *, invert: bool = False) -> np.ndarray:
    """Rank-normalize finite values within mask to [0, 1]; missing survey cells get neutral 0.5."""
    out = np.full(arr.shape, 0.5, dtype=np.float32)
    valid = np.asarray(mask, dtype=bool) & np.isfinite(arr)
    vals = np.asarray(arr[valid], dtype=np.float32)
    if vals.size == 0:
        return out
    if invert:
        vals = -vals
    order = np.argsort(vals, kind="mergesort")
    ranks = np.empty(vals.size, dtype=np.float32)
    if vals.size == 1:
        ranks[0] = 0.5
    else:
        ranks[order] = np.linspace(0.0, 1.0, vals.size, dtype=np.float32)
    out[valid] = ranks
    return out


def compute_hessian_crest(surface: np.ndarray, foot: np.ndarray, *, sigma: float = 1.2) -> np.ndarray:
    """Extract rank-normalized linear ridge crest strength (-lambda_min) from 2D Hessian."""
    smoothed = gaussian_filter(np.asarray(surface, dtype=np.float32), sigma=float(sigma))
    gy, gx = np.gradient(smoothed)
    gyy, gyx = np.gradient(gy)
    gxy, gxx = np.gradient(gx)
    tr = gxx + gyy
    det = gxx * gyy - gxy * gyx
    disc = np.sqrt(np.maximum(0.25 * tr * tr - det, 0.0))
    lam1 = 0.5 * tr - disc
    crest = np.maximum(-lam1, 0.0).astype(np.float32)
    return norm_rank(crest, foot)


def local_survey_invariant_score(
    raw_score: np.ndarray,
    foot: np.ndarray,
    *,
    sigma_px: float = 120.0,
    local_weight: float = 0.65,
) -> np.ndarray:
    """Standardize score relative to a 12 km local Gaussian window to eliminate survey-footprint bias."""
    raw = np.asarray(raw_score, dtype=np.float32)
    mean_loc = gaussian_filter(raw, sigma=float(sigma_px))
    var_loc = np.maximum(gaussian_filter((raw - mean_loc) ** 2, sigma=float(sigma_px)), 1e-6)
    z_loc = (raw - mean_loc) / np.sqrt(var_loc)
    blended = float(local_weight) * z_loc + (1.0 - float(local_weight)) * norm_rank(raw, foot)
    return norm_rank(blended, foot)


def build_h31b_surfaces(
    feats: np.ndarray,
    band_index: dict[str, int],
    foot: np.ndarray,
    oof_b: np.ndarray,
    oof_d: np.ndarray,
) -> dict[str, np.ndarray]:
    """Compute H31-B1, H31-B2, H31-B3, H31-B4 and unified S_H31 geological discovery surfaces."""
    r_relief = norm_rank(feats[band_index["relief"]], foot)
    r_lappos = norm_rank(feats[band_index["lappos_max"]], foot)
    r_step = norm_rank(feats[band_index["step_max"]], foot)
    r_lapneg = norm_rank(feats[band_index["lapneg_max"]], foot)
    r_elev_slope = norm_rank(feats[band_index["det_elev_slope"]], foot)
    r_depth_base = norm_rank(feats[band_index["depth_to_base_surf"]], foot, invert=True)
    r_iso_grav = norm_rank(feats[band_index["iso_grav_anom"]], foot)
    r_th_minus_k = norm_rank(feats[band_index["th_minus_k"]], foot)
    r_tc_inv = norm_rank(feats[band_index["tc"]], foot, invert=True)
    r_k_inv = norm_rank(feats[band_index["K"]], foot, invert=True)
    r_uk = norm_rank(feats[band_index["UK"]], foot)
    r_ieq = norm_rank(feats[band_index["ieq_n100a15"]], foot)
    r_geod2 = norm_rank(feats[band_index["geod_2ndinv"]], foot)
    r_shear = norm_rank(feats[band_index["geod_shearrate"]], foot)

    # H31-B1: 3DEP 1 m LiDAR & Topographic Scarp Curvature-Throw-Relief Dip-Slip Operator
    h31_b1 = (
        0.30 * r_elev_slope
        + 0.20 * r_relief
        + 0.20 * r_lappos
        + 0.15 * r_step
        + 0.15 * r_lapneg
    ).astype(np.float32)

    # H31-B2: Shallow Basement Contact & Multi-Scale Potential-Field Hessian Crest Operator
    pot = (0.45 * r_elev_slope + 0.30 * r_depth_base + 0.25 * r_iso_grav).astype(np.float32)
    crest = compute_hessian_crest(pot, foot, sigma=1.2)
    h31_b2 = (0.45 * r_depth_base + 0.30 * crest + 0.25 * r_iso_grav).astype(np.float32)

    # H31-B3: Argillic K-Leaching, Bouguer Terrain Trough & Uranium Redox Mobility Index
    h31_b3 = (
        0.35 * r_th_minus_k
        + 0.30 * r_k_inv
        + 0.20 * r_tc_inv
        + 0.15 * r_uk
    ).astype(np.float32)

    # H31-B4: Kostrov Strain-Rate, Microseismicity & Spatially-Blocked Fold-OOF Multi-Physics Likelihood
    p_oof = 0.45 * np.asarray(oof_b, dtype=np.float32) + 0.55 * np.asarray(oof_d, dtype=np.float32)
    r_oof = norm_rank(p_oof, foot)
    h31_b4 = (
        0.65 * r_oof
        + 0.15 * r_ieq
        + 0.10 * r_geod2
        + 0.10 * r_shear
    ).astype(np.float32)

    s_raw = (0.35 * h31_b1 + 0.25 * h31_b2 + 0.18 * h31_b3 + 0.22 * h31_b4).astype(np.float32)
    s_h31 = local_survey_invariant_score(s_raw, foot, sigma_px=120.0, local_weight=0.65)

    return {
        "H31_B1": h31_b1,
        "H31_B2": h31_b2,
        "H31_B3": h31_b3,
        "H31_B4": h31_b4,
        "S_RAW": s_raw,
        "S_H31": s_h31,
    }


def poisson_disk_select(
    ys: np.ndarray,
    xs: np.ndarray,
    shape: tuple[int, int],
    *,
    min_dist_px: float = 2.85,
    max_dots: int = 37_654,
    existing: np.ndarray | None = None,
) -> np.ndarray:
    """Deterministic priority-ordered Poisson-disk point-process emission."""
    h, w = shape
    selected = np.zeros(shape, dtype=bool)
    blocked = np.zeros(shape, dtype=bool)
    r_int = int(np.ceil(float(min_dist_px)))
    dy, dx = np.mgrid[-r_int : r_int + 1, -r_int : r_int + 1]
    disk = (dy * dy + dx * dx) <= (float(min_dist_px) * float(min_dist_px))

    if existing is not None:
        ey, ex = np.nonzero(existing)
        for y, x in zip(ey.tolist(), ex.tolist()):
            y0, y1 = max(0, y - r_int), min(h, y + r_int + 1)
            x0, x1 = max(0, x - r_int), min(w, x + r_int + 1)
            ky0, ky1 = y0 - (y - r_int), disk.shape[0] - ((y + r_int + 1) - y1)
            kx0, kx1 = x0 - (x - r_int), disk.shape[1] - ((x + r_int + 1) - x1)
            blocked[y0:y1, x0:x1] |= disk[ky0:ky1, kx0:kx1]

    count = 0
    for y, x in zip(ys.tolist(), xs.tolist()):
        if blocked[y, x]:
            continue
        selected[y, x] = True
        count += 1
        if count >= max_dots:
            break
        y0, y1 = max(0, y - r_int), min(h, y + r_int + 1)
        x0, x1 = max(0, x - r_int), min(w, x + r_int + 1)
        ky0, ky1 = y0 - (y - r_int), disk.shape[0] - ((y + r_int + 1) - y1)
        kx0, kx1 = x0 - (x - r_int), disk.shape[1] - ((x + r_int + 1) - x1)
        blocked[y0:y1, x0:x1] |= disk[ky0:ky1, kx0:kx1]
    return selected


def run_single_feature_leakage_canary(
    feature_arr: np.ndarray,
    truth_mask: np.ndarray,
    eval_mask: np.ndarray,
    *,
    stride: int = 5,
) -> dict[str, Any]:
    """Compute signed and unsigned ROC-AUC of a single feature on holdout cells; flag AUC > 0.90."""
    idx = np.flatnonzero(eval_mask)[:: max(1, int(stride))]
    x = np.asarray(feature_arr.ravel()[idx], dtype=np.float32)
    y = np.asarray(truth_mask.ravel()[idx], dtype=np.int8)
    valid = np.isfinite(x)
    if valid.sum() < 100 or y[valid].sum() == 0 or (y[valid] == 0).sum() == 0:
        return {"signed_auc": 0.5, "unsigned_auc": 0.5, "leakage_flagged": False, "n_eval": int(valid.sum())}
    signed_auc = float(roc_auc_score(y[valid], x[valid]))
    unsigned_auc = float(max(signed_auc, 1.0 - signed_auc))
    return {
        "signed_auc": round(signed_auc, 5),
        "unsigned_auc": round(unsigned_auc, 5),
        "leakage_flagged": bool(unsigned_auc > LEAKAGE_AUC_CEILING),
        "n_eval": int(valid.sum()),
    }


def check_uniqueness_against_registry(
    surface: np.ndarray,
    dots_mask: np.ndarray,
    foot: np.ndarray,
    registry_masks: dict[str, np.ndarray],
    registry_edts: dict[str, np.ndarray] | None = None,
    *,
    subsample_stride: int = 10,
) -> UniquenessAudit:
    """Enforce Parallel-Run Rule 1 on both continuous surface (r_s <= 0.90) and final dots (<= 70% within 3 px)."""
    f_idx = np.flatnonzero(foot)[:: max(1, int(subsample_stride))]
    s_vec = np.asarray(surface.ravel()[f_idx], dtype=np.float32)
    surf_corrs: dict[str, float] = {}
    overlaps: dict[str, float] = {}

    n_dots = int(dots_mask.sum())
    for name, rmask in registry_masks.items():
        r_vec = np.asarray(rmask.ravel()[f_idx], dtype=np.float32)
        corr = float(spearmanr(s_vec, r_vec).statistic)
        if not np.isfinite(corr):
            corr = 0.0
        surf_corrs[name] = abs(corr)
        edt = registry_edts[name] if (registry_edts and name in registry_edts) else distance_transform_edt(~rmask)
        ov = float((edt[dots_mask] <= 3.0).mean()) if n_dots > 0 else 0.0
        overlaps[name] = ov

    max_rs = max(surf_corrs.values()) if surf_corrs else 0.0
    max_ov = max(overlaps.values()) if overlaps else 0.0
    pass_s = max_rs <= MAX_SURFACE_SPEARMAN
    pass_o = max_ov <= MAX_DOT_OVERLAP_3PX
    return UniquenessAudit(
        surface_spearman=surf_corrs,
        dot_overlap_3px=overlaps,
        max_surface_spearman=max_rs,
        max_dot_overlap_3px=max_ov,
        passed_surface_gate=pass_s,
        passed_dot_overlap_gate=pass_o,
        passed_all=bool(pass_s and pass_o),
    )
