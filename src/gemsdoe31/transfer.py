"""TGJ31: label-free, scale-persistent local gravity/magnetic coupling jumps.

This is a descriptive physical hypothesis, not a density/susceptibility inversion
or a calibrated fault probability. Parameters are frozen in the preregistration.
No fault raster, submission raster or SGMC feature is accepted by this module.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.ndimage import gaussian_filter, minimum_filter

REGIONAL_SIGMA = 20.0
SCALES = (3.0, 7.0)
REGULARIZATION = 0.05
JUMP_THRESHOLD = 0.5
FEATURE_NAMES = ("rtp", "gravity", "jump_3", "coupling_3", "jump_7", "coupling_7")


def _standardize(a: np.ndarray, valid: np.ndarray) -> tuple[np.ndarray, dict]:
    values = np.asarray(a, np.float32)[valid]
    if not values.size:
        raise ValueError("no jointly valid physical measurements")
    med = float(np.median(values))
    q25, q75 = np.quantile(values, [0.25, 0.75])
    scale = max(float(q75 - q25), 1e-6)
    out = np.where(valid, (a - med) / scale, 0).astype(np.float32)
    return out, {"median": med, "iqr_scale": scale}


def _normalize_gradient(a: np.ndarray, valid: np.ndarray) -> tuple[np.ndarray, float]:
    gy, gx = np.gradient(a)
    magnitude = np.hypot(gy, gx)
    q95 = float(np.quantile(magnitude[valid], 0.95)) if valid.any() else 0.0
    normalized = np.clip(magnitude / max(q95, 1e-8), 0, 1).astype(np.float32)
    normalized[~valid] = 0
    return normalized, q95


def build_transfer_surface(
    rtp: np.ndarray,
    gravity: np.ndarray,
    footprint: np.ndarray,
    *,
    regional_sigma: float = REGIONAL_SIGMA,
    scales: tuple[float, float] = SCALES,
) -> tuple[np.ndarray, np.ndarray, dict[str, np.ndarray], dict]:
    """Return candidate, same-input amplitude control, canary features and audit.

    Non-default scales exist for small synthetic regression tests, not a search
    interface. Production code asserts the preregistered defaults. Unsupported
    cells predict zero, retaining all footprint positives in the evaluation.
    """
    rtp = np.asarray(rtp, np.float32)
    gravity = np.asarray(gravity, np.float32)
    fp = np.asarray(footprint, bool)
    if rtp.ndim != 2 or rtp.shape != gravity.shape or rtp.shape != fp.shape:
        raise ValueError("RTP, gravity and footprint must be aligned 2-D grids")
    if len(scales) != 2 or min(scales) <= 0 or regional_sigma <= 0:
        raise ValueError("two positive local scales and a positive regional scale required")
    valid = fp & np.isfinite(rtp) & np.isfinite(gravity)
    valid &= (np.abs(rtp) < 1e30) & (np.abs(gravity) < 1e30)
    magnetic, magnetic_audit = _standardize(rtp, valid)
    grav, gravity_audit = _standardize(gravity, valid)
    halo = int(math.ceil(4 * regional_sigma + 4 * max(scales) + 2))
    supported = minimum_filter(
        valid.astype(np.uint8), size=2 * halo + 1, mode="constant", cval=0
    ).astype(bool)
    magnetic -= gaussian_filter(magnetic, regional_sigma)
    grav -= gaussian_filter(grav, regional_sigma)
    features: dict[str, np.ndarray] = {}
    # Bounded raw-feature transforms are label-free and fixed, not AUC-tuned.
    for name, raw in (("rtp", rtp), ("gravity", gravity)):
        z, _ = _standardize(raw, valid)
        features[name] = np.where(valid, 0.5 + np.arctan(z) / np.pi, 0).astype(np.float32)
    scale_audits = []
    jumps, couplings = [], []
    for sigma in scales:
        mm = gaussian_filter(magnetic, sigma)
        mg = gaussian_filter(grav, sigma)
        covariance = gaussian_filter(magnetic * grav, sigma) - mm * mg
        vm = np.maximum(gaussian_filter(magnetic * magnetic, sigma) - mm * mm, 0)
        vg = np.maximum(gaussian_filter(grav * grav, sigma) - mg * mg, 0)
        pos_m = vm[valid & (vm > 0)]
        pos_g = vg[valid & (vg > 0)]
        lm = max(REGULARIZATION * float(np.median(pos_m)) if pos_m.size else 0.0, 1e-8)
        lg = max(REGULARIZATION * float(np.median(pos_g)) if pos_g.size else 0.0, 1e-8)
        coefficient = covariance / (vm + lm)
        jump, jump_q95 = _normalize_gradient(np.arctan(coefficient), valid)
        coupling = np.clip(covariance**2 / ((vm + lm) * (vg + lg)), 0, 1).astype(np.float32)
        coupling[~valid] = 0
        name = f"{sigma:g}"
        features[f"jump_{name}"] = jump
        features[f"coupling_{name}"] = coupling
        jumps.append(jump)
        couplings.append(coupling)
        scale_audits.append({"sigma_px": sigma, "lambda_m": lm, "lambda_g": lg, "jump_q95": jump_q95})
    candidate = np.sqrt(jumps[0] * jumps[1]) * np.sqrt(couplings[0] * couplings[1])
    candidate[~supported | (jumps[0] <= JUMP_THRESHOLD) | (jumps[1] <= JUMP_THRESHOLD)] = 0
    gm, gm_q95 = _normalize_gradient(magnetic, valid)
    gg, gg_q95 = _normalize_gradient(grav, valid)
    control = np.sqrt(gm * gg)
    control[~supported | (gm <= JUMP_THRESHOLD) | (gg <= JUMP_THRESHOLD)] = 0
    for arr in (candidate, control, *features.values()):
        if not np.isfinite(arr).all() or np.any((arr < 0) | (arr > 1)):
            raise AssertionError("feature builder must produce finite bounded descriptors")
        arr[~fp] = 0
    audit = {
        "method": "TGJ31-v1", "uses_catalogue_or_sgmc": False,
        "parameters": {"regional_sigma_px": regional_sigma, "local_scales_px": list(scales),
                       "regularization": REGULARIZATION, "jump_threshold": JUMP_THRESHOLD},
        "normalization": {"rtp": magnetic_audit, "gravity": gravity_audit},
        "valid_measurement_pixels": int(valid.sum()), "supported_pixels": int(supported.sum()),
        "footprint_pixels": int(fp.sum()), "required_valid_halo_px": halo,
        "candidate_positive_pixels_before_catalogue_mask": int((candidate > 0).sum()),
        "candidate_confidence_mass_before_catalogue_mask": float(candidate.sum(dtype=np.float64)),
        "control_positive_pixels_before_catalogue_mask": int((control > 0).sum()),
        "control_confidence_mass_before_catalogue_mask": float(control.sum(dtype=np.float64)),
        "scale_audits": scale_audits, "control_gradient_q95": [gm_q95, gg_q95],
        "confidence_caveat": "Bounded physical response, not a calibrated probability or source inversion.",
    }
    return candidate.astype(np.float32), control.astype(np.float32), features, audit
