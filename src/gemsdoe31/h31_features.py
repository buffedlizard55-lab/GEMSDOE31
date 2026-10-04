"""H31-A multiscale magnetic local-wavelength features.

This is a wavelength/scale proxy derived only from the two supplied magnetic-gradient bands. It is not a
physical source-depth inversion and must not be interpreted as a literal depth map.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.ndimage import distance_transform_edt, gaussian_filter

SIGMAS_PX = (1.0, 3.0)
LOCAL_LENGTH_LIMIT_PX = (0.5, 30.0)
FEATURE_NAMES = ("H31_mag_local_length", "H31_mag_scale_edge")


@dataclass(frozen=True)
class MagneticScaleDiagnostics:
    input_valid_pixels: int
    footprint_pixels: int
    invalid_footprint_pixels: int
    eps_by_sigma: dict[str, float]
    edge_q99_by_sigma: dict[str, float]
    length_bounds_px: tuple[float, float]
    output_ranges: dict[str, tuple[float, float]]

    def as_dict(self) -> dict:
        return {
            "input_valid_pixels": self.input_valid_pixels,
            "footprint_pixels": self.footprint_pixels,
            "invalid_footprint_pixels": self.invalid_footprint_pixels,
            "eps_by_sigma": self.eps_by_sigma,
            "edge_q99_by_sigma": self.edge_q99_by_sigma,
            "length_bounds_px": list(self.length_bounds_px),
            "output_ranges": {name: list(values) for name, values in self.output_ranges.items()},
        }


def _clean_band(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float32)
    arr = arr.copy()
    arr[(~np.isfinite(arr)) | (np.abs(arr) >= 1e30)] = np.nan
    return arr


def _nearest_fill(values: np.ndarray) -> np.ndarray:
    finite = np.isfinite(values)
    if not finite.any():
        raise ValueError("magnetic derivative band contains no finite values")
    if finite.all():
        return values.astype(np.float32, copy=False)
    nearest = distance_transform_edt(~finite, return_distances=False, return_indices=True)
    return values[tuple(nearest)].astype(np.float32, copy=False)


def _gradient_magnitude(values: np.ndarray) -> np.ndarray:
    gy, gx = np.gradient(values.astype(np.float64, copy=False))
    return np.hypot(gx, gy)


def build_magnetic_scale_features(
    tmi_hg: np.ndarray,
    tmi_vg: np.ndarray,
    footprint: np.ndarray,
) -> tuple[np.ndarray, MagneticScaleDiagnostics]:
    """Build two H31-A features on an aligned 2-D grid.

    Feature definitions are frozen in `knowledge/2026-10-04_h31_hypotheses_preregistration.md`:

    * `H31_mag_local_length`: `log1p(mean(L_1, L_3))`, where `L_sigma` is the analytic-signal
      characteristic length `A_sigma / (|grad A_sigma| + epsilon)` clipped to 0.5–30 pixels.
    * `H31_mag_scale_edge`: geometric mean of the normalized spatial gradients of `L_1` and `L_3`.

    `epsilon` and the edge normalizers use unlabeled cells in the supplied competition footprint only. Invalid
    input cells are nearest-filled only while filtering and are restored to NaN in both output features.
    """
    hg = _clean_band(tmi_hg)
    vg = _clean_band(tmi_vg)
    foot = np.asarray(footprint, dtype=bool)
    if hg.ndim != 2 or vg.ndim != 2 or foot.ndim != 2 or hg.shape != vg.shape or hg.shape != foot.shape:
        raise ValueError("tmi_hg, tmi_vg and footprint must be aligned 2-D arrays")
    if not foot.any():
        raise ValueError("footprint must contain at least one cell")

    valid = np.isfinite(hg) & np.isfinite(vg)
    if not np.any(valid & foot):
        raise ValueError("no cells have both finite magnetic derivatives inside the footprint")

    analytic = np.hypot(_nearest_fill(hg), _nearest_fill(vg)).astype(np.float32)
    lengths: dict[float, np.ndarray] = {}
    normalized_edges: dict[float, np.ndarray] = {}
    eps_by_sigma: dict[str, float] = {}
    q99_by_sigma: dict[str, float] = {}

    lo, hi = LOCAL_LENGTH_LIMIT_PX
    for sigma in SIGMAS_PX:
        smoothed = gaussian_filter(analytic, sigma=sigma)
        grad_signal = _gradient_magnitude(smoothed)
        usable_gradient = foot & valid & np.isfinite(grad_signal) & (grad_signal > 0)
        if not usable_gradient.any():
            raise ValueError(f"no positive analytic-signal gradient at sigma={sigma}")
        median_gradient = float(np.median(grad_signal[usable_gradient]))
        epsilon = 0.01 * median_gradient
        if not np.isfinite(epsilon) or epsilon <= 0:
            raise ValueError(f"invalid epsilon at sigma={sigma}: {epsilon}")
        length = np.clip(smoothed / (grad_signal + epsilon), lo, hi).astype(np.float32)
        edge = _gradient_magnitude(length)
        usable_edge = foot & valid & np.isfinite(edge)
        q99 = float(np.percentile(edge[usable_edge], 99))
        if not np.isfinite(q99) or q99 <= 0:
            raise ValueError(f"invalid 99th-percentile length-edge scale at sigma={sigma}: {q99}")
        normalized = np.clip(edge / q99, 0.0, 1.0).astype(np.float32)
        length[~valid] = np.nan
        normalized[~valid] = np.nan
        lengths[sigma] = length
        normalized_edges[sigma] = normalized
        eps_by_sigma[f"{sigma:g}"] = epsilon
        q99_by_sigma[f"{sigma:g}"] = q99

    local_length = np.log1p(0.5 * (lengths[1.0] + lengths[3.0])).astype(np.float32)
    scale_edge = np.sqrt(normalized_edges[1.0] * normalized_edges[3.0]).astype(np.float32)
    local_length[~valid] = np.nan
    scale_edge[~valid] = np.nan
    stack = np.stack((local_length, scale_edge), axis=0)
    stack[:, ~foot] = np.nan

    ranges: dict[str, tuple[float, float]] = {}
    for name, array in zip(FEATURE_NAMES, stack, strict=True):
        finite = array[foot & np.isfinite(array)]
        if not finite.size:
            raise ValueError(f"feature {name} has no finite footprint values")
        ranges[name] = (float(finite.min()), float(finite.max()))

    diagnostics = MagneticScaleDiagnostics(
        input_valid_pixels=int(np.count_nonzero(valid)),
        footprint_pixels=int(foot.sum()),
        invalid_footprint_pixels=int(np.count_nonzero(foot & ~valid)),
        eps_by_sigma=eps_by_sigma,
        edge_q99_by_sigma=q99_by_sigma,
        length_bounds_px=LOCAL_LENGTH_LIMIT_PX,
        output_ranges=ranges,
    )
    return stack, diagnostics
