"""Empirical residual semivariograms along connected fault-trace holdouts.

Pairs are formed only within the same hidden 8-connected catalogue component and the same spatial fold/draw.
The effective practical range is the distance at which a fitted exponential semivariogram reaches 95% of its
partial sill. A component bootstrap supplies a conservative upper interval for the validation collar.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import least_squares
from scipy.spatial import cKDTree


class VariogramFitError(RuntimeError):
    """Raised when a stable residual-dependence range cannot be identified."""


@dataclass(frozen=True)
class EmpiricalVariogram:
    bin_edges_m: np.ndarray
    bin_centers_m: np.ndarray
    gamma: np.ndarray
    pair_counts: np.ndarray
    group_sums: np.ndarray
    group_counts: np.ndarray
    group_keys: tuple[tuple[int, int, int], ...]
    n_residuals: int
    n_groups_seen: int
    min_pairs_per_bin: int

    def as_dict(self) -> dict:
        return {
            "bin_edges_m": self.bin_edges_m.tolist(),
            "bin_centers_m": self.bin_centers_m.tolist(),
            "semivariance": [float(x) if np.isfinite(x) else None for x in self.gamma],
            "pair_counts": self.pair_counts.astype(int).tolist(),
            "n_pairs_total": int(self.pair_counts.sum()),
            "n_residuals": self.n_residuals,
            "n_trace_groups_with_pairs": len(self.group_keys),
            "n_trace_groups_seen": self.n_groups_seen,
            "estimator": "classical Matheron semivariogram: mean(0.5 * (e_i - e_j)^2), same 8-connected trace component, same fold and draw",
        }


@dataclass(frozen=True)
class ExponentialFit:
    nugget: float
    partial_sill: float
    sill: float
    scale_m: float
    practical_range_95_m: float
    weighted_rmse: float
    r_squared: float
    max_lag_sill_fraction: float
    populated_bins: int
    max_populated_lag_m: float
    stable: bool
    stability_reasons: tuple[str, ...]

    def as_dict(self) -> dict:
        return {
            "model": "exponential: nugget + partial_sill * (1 - exp(-h / scale))",
            "nugget": self.nugget,
            "partial_sill": self.partial_sill,
            "total_sill": self.sill,
            "scale_parameter_m": self.scale_m,
            "practical_range_95_sill_m": self.practical_range_95_m,
            "weighted_rmse": self.weighted_rmse,
            "weighted_r_squared": self.r_squared,
            "model_sill_fraction_at_max_populated_lag": self.max_lag_sill_fraction,
            "populated_bins": self.populated_bins,
            "max_populated_lag_m": self.max_populated_lag_m,
            "stable": self.stable,
            "stability_reasons": list(self.stability_reasons),
        }


def _validate_vectors(rows, cols, components, residuals, folds, draws) -> tuple[np.ndarray, ...]:
    arrays = [
        np.asarray(rows, dtype=np.int64),
        np.asarray(cols, dtype=np.int64),
        np.asarray(components, dtype=np.int64),
        np.asarray(residuals, dtype=np.float64),
        np.asarray(folds, dtype=np.int64),
        np.asarray(draws, dtype=np.int64),
    ]
    if any(a.ndim != 1 for a in arrays) or len({a.size for a in arrays}) != 1:
        raise ValueError("rows, cols, components, residuals, folds and draws must be equal-length 1-D vectors")
    r, c, comp, e, fold, draw = arrays
    if not np.isfinite(e).all():
        raise ValueError("residuals must all be finite")
    if (comp <= 0).any():
        raise ValueError("component ids must be positive for along-trace residuals")
    if (r < 0).any() or (c < 0).any():
        raise ValueError("row and column coordinates must be nonnegative")
    return tuple(arrays)


def empirical_semivariogram(
    rows,
    cols,
    components,
    residuals,
    folds,
    draws,
    *,
    cell_size_m: float = 100.0,
    bin_width_m: float = 500.0,
    max_lag_m: float = 50_000.0,
    min_pairs_per_bin: int = 20,
    min_points_per_group: int = 4,
) -> EmpiricalVariogram:
    """Compute pair-count-weighted Matheron bins, never pairing different fault components.

    Coordinates are projected grid row/column indices in the competition's 100 m UTM grid. `fold`, `draw`,
    and connected-component id jointly define an independent trace group; this prevents accidental pairing
    across a fold boundary or across separately mapped faults.
    """
    r, c, comp, e, fold, draw = _validate_vectors(rows, cols, components, residuals, folds, draws)
    constants = np.asarray([cell_size_m, bin_width_m, max_lag_m], dtype=float)
    if not np.isfinite(constants).all() or cell_size_m <= 0 or bin_width_m <= 0 or max_lag_m <= bin_width_m:
        raise ValueError("cell size, bin width and maximum lag must be finite positive distances")
    if isinstance(min_pairs_per_bin, bool) or min_pairs_per_bin < 1:
        raise ValueError("min_pairs_per_bin must be a positive integer")
    if isinstance(min_points_per_group, bool) or min_points_per_group < 2:
        raise ValueError("min_points_per_group must be an integer of at least two")

    n_bins = int(np.floor(max_lag_m / bin_width_m))
    if n_bins < 2:
        raise ValueError("at least two lag bins are required")
    edges = np.arange(n_bins + 1, dtype=np.float64) * bin_width_m
    centers = 0.5 * (edges[:-1] + edges[1:])

    # Lexicographic sorting makes group construction deterministic.
    order = np.lexsort((c, r, draw, fold, comp))
    r, c, comp, e, fold, draw = (a[order] for a in (r, c, comp, e, fold, draw))
    group_start = np.r_[0, 1 + np.flatnonzero((comp[1:] != comp[:-1]) | (fold[1:] != fold[:-1]) | (draw[1:] != draw[:-1]))]
    group_stop = np.r_[group_start[1:], r.size]

    sums: list[np.ndarray] = []
    counts: list[np.ndarray] = []
    keys: list[tuple[int, int, int]] = []
    n_groups_seen = int(group_start.size)
    for start, stop in zip(group_start.tolist(), group_stop.tolist(), strict=True):
        n = stop - start
        if n < min_points_per_group:
            continue
        rr, cc, ee = r[start:stop], c[start:stop], e[start:stop]
        if np.unique(rr.astype(np.int64) * (int(cc.max(initial=0)) + 1) + cc).size != n:
            raise ValueError("duplicate coordinates within a fold/draw/trace group")
        xy = np.column_stack((rr, cc)).astype(np.float64) * cell_size_m
        pairs = cKDTree(xy).query_pairs(r=max_lag_m, output_type="ndarray")
        if not pairs.size:
            continue
        delta = xy[pairs[:, 0]] - xy[pairs[:, 1]]
        distance = np.hypot(delta[:, 0], delta[:, 1])
        keep = (distance > 0.0) & (distance < max_lag_m)
        if not keep.any():
            continue
        pairs = pairs[keep]
        distance = distance[keep]
        bin_idx = np.floor(distance / bin_width_m).astype(np.int64)
        in_range = (bin_idx >= 0) & (bin_idx < n_bins)
        if not in_range.any():
            continue
        pairs = pairs[in_range]
        bin_idx = bin_idx[in_range]
        semivariance = 0.5 * np.square(ee[pairs[:, 0]] - ee[pairs[:, 1]])
        group_sum = np.bincount(bin_idx, weights=semivariance, minlength=n_bins).astype(np.float64)
        group_count = np.bincount(bin_idx, minlength=n_bins).astype(np.int64)
        sums.append(group_sum)
        counts.append(group_count)
        keys.append((int(fold[start]), int(draw[start]), int(comp[start])))

    if not sums:
        raise VariogramFitError("no same-trace residual pairs fell within the registered maximum lag")
    group_sums = np.stack(sums)
    group_counts = np.stack(counts)
    pair_counts = group_counts.sum(axis=0)
    gamma = np.full(n_bins, np.nan, dtype=np.float64)
    enough = pair_counts >= min_pairs_per_bin
    gamma[enough] = group_sums.sum(axis=0)[enough] / pair_counts[enough]
    return EmpiricalVariogram(
        bin_edges_m=edges,
        bin_centers_m=centers,
        gamma=gamma,
        pair_counts=pair_counts,
        group_sums=group_sums,
        group_counts=group_counts,
        group_keys=tuple(keys),
        n_residuals=int(e.size),
        n_groups_seen=n_groups_seen,
        min_pairs_per_bin=int(min_pairs_per_bin),
    )


def _model(h: np.ndarray, nugget: float, partial_sill: float, scale: float) -> np.ndarray:
    return nugget + partial_sill * (1.0 - np.exp(-h / scale))


def fit_exponential(
    variogram: EmpiricalVariogram,
    *,
    max_lag_m: float = 50_000.0,
    min_populated_bins: int = 8,
    min_fit_lag_m: float = 2_000.0,
) -> ExponentialFit:
    """Fit a bounded exponential curve to empirical bins with at least their registered pair count."""
    ok = np.isfinite(variogram.gamma) & (variogram.pair_counts > 0)
    h = variogram.bin_centers_m[ok]
    y = variogram.gamma[ok]
    counts = variogram.pair_counts[ok].astype(np.float64)
    reasons: list[str] = []
    if h.size < min_populated_bins:
        raise VariogramFitError(f"only {h.size} populated bins; need at least {min_populated_bins}")
    if float(h.max(initial=0.0)) < min_fit_lag_m:
        raise VariogramFitError(f"largest populated lag {h.max(initial=0.0):.0f} m is below {min_fit_lag_m:.0f} m")
    if (y < 0).any() or not np.isfinite(y).all():
        raise VariogramFitError("empirical semivariance contains invalid values")

    max_y = float(y.max(initial=0.0))
    if max_y <= 1e-10:
        raise VariogramFitError("empirical semivariance is effectively zero; no residual dependence range is identifiable")
    cap = max(5.0 * max_y, 1e-8)
    lower_scale = max(1.0, float(np.min(np.diff(variogram.bin_edges_m))) / 10.0)
    upper_scale = max_lag_m / 6.0
    if upper_scale <= lower_scale:
        raise ValueError("maximum lag is too small for exponential range fitting")
    high = y[h >= np.quantile(h, 0.75)]
    sill0 = float(np.median(high)) if high.size else max_y
    sill0 = float(np.clip(sill0, max_y * 0.05, cap * 0.8))
    nugget0 = float(np.clip(y[0] * 0.5, 0.0, sill0 * 0.8))
    psill0 = max(sill0 - nugget0, max_y * 0.05)
    scale0 = float(np.clip(max_lag_m / 12.0, lower_scale * 1.1, upper_scale * 0.9))
    weights = np.sqrt(counts / counts.max())

    def residual(params: np.ndarray) -> np.ndarray:
        return weights * (_model(h, *params) - y)

    result = least_squares(
        residual,
        x0=np.asarray([nugget0, psill0, scale0], dtype=np.float64),
        bounds=(np.asarray([0.0, 1e-10, lower_scale]), np.asarray([cap, cap, upper_scale])),
        method="trf",
        max_nfev=5000,
        xtol=1e-12,
        ftol=1e-12,
        gtol=1e-12,
    )
    if not result.success or not np.isfinite(result.x).all():
        raise VariogramFitError(f"bounded exponential fit failed: {result.message}")
    nugget, partial_sill, scale = map(float, result.x)
    sill = nugget + partial_sill
    practical = float(-np.log(0.05) * scale)
    residuals = result.fun
    weighted_rmse = float(np.sqrt(np.mean(residuals**2)))
    centered = y - np.average(y, weights=weights**2)
    denominator = float(np.sum((weights * centered) ** 2))
    r_squared = 1.0 - float(np.sum(residuals**2)) / denominator if denominator > 0 else float("nan")
    max_lag_sill_fraction = float(1.0 - np.exp(-float(h.max()) / scale))

    if practical >= 0.90 * max_lag_m:
        reasons.append("95%-sill practical range approaches the maximum fitted lag")
    if max_lag_sill_fraction < 0.95:
        reasons.append("observed lag support does not reach 95% of the fitted partial sill")
    if partial_sill <= max_y * 1e-4:
        reasons.append("fitted partial sill is negligible relative to observed semivariance")
    if not np.isfinite(r_squared) or r_squared < 0.0:
        reasons.append("weighted fit explains no empirical-bin variance")
    if practical < variogram.bin_centers_m[0]:
        reasons.append("fitted practical range is below the first lag-bin center")
    stable = not reasons
    return ExponentialFit(
        nugget=nugget,
        partial_sill=partial_sill,
        sill=sill,
        scale_m=scale,
        practical_range_95_m=practical,
        weighted_rmse=weighted_rmse,
        r_squared=r_squared,
        max_lag_sill_fraction=max_lag_sill_fraction,
        populated_bins=int(h.size),
        max_populated_lag_m=float(h.max()),
        stable=stable,
        stability_reasons=tuple(reasons),
    )


def bootstrap_range_interval(
    variogram: EmpiricalVariogram,
    *,
    max_lag_m: float = 50_000.0,
    min_populated_bins: int = 8,
    min_fit_lag_m: float = 2_000.0,
    n_bootstrap: int = 200,
    seed: int = 20261004,
    minimum_stable_fraction: float = 0.80,
) -> dict:
    """Resample fold/draw/component groups with replacement and refit the practical range."""
    if isinstance(n_bootstrap, bool) or n_bootstrap < 50:
        raise ValueError("at least 50 component-bootstrap replicates are required")
    if variogram.group_sums.ndim != 2 or variogram.group_sums.shape != variogram.group_counts.shape:
        raise ValueError("trace-group sufficient statistics are malformed")
    n_groups = variogram.group_sums.shape[0]
    if n_groups < 30:
        raise VariogramFitError(f"only {n_groups} trace groups with pairs; need at least 30 for the component bootstrap")
    point = fit_exponential(
        variogram, max_lag_m=max_lag_m, min_populated_bins=min_populated_bins, min_fit_lag_m=min_fit_lag_m
    )
    if not point.stable:
        raise VariogramFitError("point fit is unstable: " + "; ".join(point.stability_reasons))

    rng = np.random.default_rng(seed)
    ranges: list[float] = []
    failure_counts: dict[str, int] = {}
    for _ in range(n_bootstrap):
        take = rng.integers(0, n_groups, size=n_groups)
        sums = variogram.group_sums[take].sum(axis=0)
        counts = variogram.group_counts[take].sum(axis=0)
        gamma = np.full(counts.shape, np.nan, dtype=np.float64)
        ok = counts >= variogram.min_pairs_per_bin
        gamma[ok] = sums[ok] / counts[ok]
        sample = EmpiricalVariogram(
            bin_edges_m=variogram.bin_edges_m,
            bin_centers_m=variogram.bin_centers_m,
            gamma=gamma,
            pair_counts=counts,
            group_sums=variogram.group_sums[take],
            group_counts=variogram.group_counts[take],
            group_keys=tuple(variogram.group_keys[i] for i in take),
            n_residuals=variogram.n_residuals,
            n_groups_seen=n_groups,
            min_pairs_per_bin=variogram.min_pairs_per_bin,
        )
        try:
            fit = fit_exponential(
                sample,
                max_lag_m=max_lag_m,
                min_populated_bins=min_populated_bins,
                min_fit_lag_m=min_fit_lag_m,
            )
            if not fit.stable:
                raise VariogramFitError("unstable bootstrap fit")
            ranges.append(fit.practical_range_95_m)
        except (ValueError, VariogramFitError) as exc:
            key = str(exc)
            failure_counts[key] = failure_counts.get(key, 0) + 1

    stable_fraction = len(ranges) / n_bootstrap
    if stable_fraction < minimum_stable_fraction:
        raise VariogramFitError(
            f"only {len(ranges)}/{n_bootstrap} bootstrap fits were stable; need {minimum_stable_fraction:.0%}; "
            f"failure counts={failure_counts}"
        )
    values = np.asarray(ranges, dtype=np.float64)
    lo, hi = np.quantile(values, [0.025, 0.975])
    return {
        "point_fit": point.as_dict(),
        "bootstrap": {
            "unit": "fold × draw × connected fault component",
            "seed": int(seed),
            "requested_replicates": int(n_bootstrap),
            "stable_replicates": int(values.size),
            "stable_fraction": float(stable_fraction),
            "range_95_sill_ci_m": [float(lo), float(hi)],
            "range_95_sill_ci_px_at_100m": [float(lo / 100.0), float(hi / 100.0)],
            "failed_fit_reasons": failure_counts,
        },
        "stable": True,
    }


def recommend_buffer_m(variogram_fits: dict[str, dict], *, metric_radius_m: float = 300.0, cell_size_m: float = 100.0) -> int:
    """Round up the largest upper 95% fitted practical range (and the 300 m metric support) to a grid cell."""
    if not variogram_fits or metric_radius_m < 0 or cell_size_m <= 0:
        raise ValueError("variogram fits and valid metric/grid distances are required")
    upper_ranges = []
    for arm, item in variogram_fits.items():
        if not item.get("stable"):
            raise VariogramFitError(f"{arm} variogram is not stable")
        ci = item.get("bootstrap", {}).get("range_95_sill_ci_m")
        if not isinstance(ci, list) or len(ci) != 2 or not np.isfinite(ci).all():
            raise VariogramFitError(f"{arm} variogram has no finite bootstrap interval")
        upper_ranges.append(float(ci[1]))
    target = max(metric_radius_m, *upper_ranges)
    return int(np.ceil(target / cell_size_m) * cell_size_m)
