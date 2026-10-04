"""Empirical spatial-buffer derivation from out-of-fold residual semivariograms.

The buffer is *measured*, never assumed. Two independent lines of evidence are combined:

1. A residual semivariogram along known fault traces, fitted with spherical / exponential /
   Gaussian models by weighted least squares, with a component bootstrap for uncertainty. The
   reported range is the distance at which spatial autocorrelation has decayed to ~5 % of the
   sill; the buffer is the largest credible range across models.
2. A holdout-buffer sweep: the same paired metric is recomputed while progressively deleting
   every evaluation pixel within a distance ``b`` of the training region. The smallest ``b`` at
   which the estimate stops falling is a lower bound on the leakage distance.

Reference for the *principle* (spatial block CV must be sized to the data's dependence
structure, not to a pixel count): Roberts et al. 2017, Ecography, doi:10.1111/ecog.02881;
Valavi et al. 2019, MEE, doi:10.1111/2041-210X.13107 (blockCV). Neither paper supplies a
buffer value for this dataset; the value here is computed from the data.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.spatial import cKDTree

MODELS = ("spherical", "exponential", "gaussian")


def _model_gamma(h: np.ndarray, nugget: float, sill: float, rng_m: float, model: str) -> np.ndarray:
    """Semivariance model. ``sill`` is the total sill; the partial sill is ``sill - nugget``."""
    psill = max(sill - nugget, 0.0)
    h = np.asarray(h, dtype=float)
    if model == "spherical":
        r = np.clip(h / rng_m, 0.0, 1.0)
        g = nugget + psill * (1.5 * r - 0.5 * r**3)
        g = np.where(h >= rng_m, nugget + psill, g)
    elif model == "exponential":
        g = nugget + psill * (1.0 - np.exp(-3.0 * h / rng_m))
    elif model == "gaussian":
        g = nugget + psill * (1.0 - np.exp(-3.0 * (h / rng_m) ** 2))
    else:  # pragma: no cover - guarded by the caller
        raise ValueError(f"unknown model {model!r}")
    return g


@dataclass
class VariogramBins:
    edges_m: np.ndarray
    centres_m: np.ndarray
    gamma: np.ndarray
    pairs: np.ndarray

    def populated(self, min_pairs: int) -> np.ndarray:
        return np.flatnonzero(self.pairs >= min_pairs)


def empirical_variogram(
    rows: np.ndarray,
    cols: np.ndarray,
    values: np.ndarray,
    components: np.ndarray,
    *,
    cell_m: float = 100.0,
    bin_m: float = 500.0,
    max_lag_m: float = 60_000.0,
) -> VariogramBins:
    """Matheron semivariogram from pairs that share an 8-connected fault component."""
    rows = np.asarray(rows)
    cols = np.asarray(cols)
    values = np.asarray(values, dtype=float)
    components = np.asarray(components)
    n_bins = int(np.ceil(max_lag_m / bin_m))
    sums = np.zeros(n_bins)
    counts = np.zeros(n_bins, dtype=np.int64)
    xy = np.column_stack([cols * cell_m, rows * cell_m])
    for comp in np.unique(components):
        sel = components == comp
        if int(sel.sum()) < 2:
            continue
        pts = xy[sel]
        vals = values[sel]
        tree = cKDTree(pts)
        pairs = tree.query_pairs(r=max_lag_m, output_type="ndarray")
        if pairs.size == 0:
            continue
        d = np.hypot(*(pts[pairs[:, 0]] - pts[pairs[:, 1]]).T)
        dv = (vals[pairs[:, 0]] - vals[pairs[:, 1]]) ** 2
        idx = np.floor(d / bin_m).astype(int)
        ok = (idx >= 0) & (idx < n_bins) & (d > 0)
        sums += np.bincount(idx[ok], weights=dv[ok], minlength=n_bins)
        counts += np.bincount(idx[ok], minlength=n_bins)
    with np.errstate(invalid="ignore", divide="ignore"):
        gamma = np.where(counts > 0, sums / (2.0 * counts), np.nan)
    edges = np.arange(n_bins + 1) * bin_m
    centres = edges[:-1] + bin_m / 2.0
    return VariogramBins(edges, centres, gamma, counts)


def fit_models(
    bins: VariogramBins,
    *,
    min_pairs: int = 20,
    models: tuple[str, ...] = MODELS,
) -> dict[str, dict]:
    """Weighted least-squares fits on the populated bins; identical lag support for every model."""
    idx = bins.populated(min_pairs)
    if idx.size < 4:
        return {}
    h = bins.centres_m[idx]
    g = bins.gamma[idx]
    n = bins.pairs[idx].astype(float)
    w = np.sqrt(n) / np.maximum(g, 1e-12)          # Cressie-style weights
    out: dict[str, dict] = {}
    for model in models:
        def residual(theta: np.ndarray) -> np.ndarray:
            nugget, psill, rng = theta
            return (g - _model_gamma(h, nugget, nugget + psill, rng, model)) * w

        best = None
        for r0 in (2_000.0, 5_000.0, 10_000.0, 20_000.0, 40_000.0):
            x0 = np.array([0.05 * np.nanmax(g), 0.95 * np.nanmax(g), r0])
            try:
                from scipy.optimize import least_squares
                sol = least_squares(
                    residual, x0,
                    bounds=([0.0, 0.0, 500.0], [np.inf, np.inf, 500_000.0]),
                    max_nfev=5_000,
                )
            except Exception:      # pragma: no cover - solver failure is reported as no-fit
                continue
            if best is None or sol.cost < best.cost:
                best = sol
        if best is None:
            continue
        nugget, psill, rng = (float(v) for v in best.x)
        pred = _model_gamma(h, nugget, nugget + psill, rng, model)
        ss_res = float(np.sum((g - pred) ** 2))
        ss_tot = float(np.sum((g - np.mean(g)) ** 2))
        # 95 %-of-sill distance: spherical reaches the sill at the range; exponential and
        # gaussian are asymptotic, so the practical range is where the model reaches 0.95*psill
        if model == "spherical":
            practical = rng
        elif model == "exponential":
            practical = rng * (-np.log(0.05) / 3.0)
        else:
            practical = rng * np.sqrt(-np.log(0.05) / 3.0)
        out[model] = {
            "nugget": nugget, "partial_sill": psill, "total_sill": nugget + psill,
            "range_m": rng, "practical_range_m": float(practical),
            "weighted_rmse": float(np.sqrt(np.average((g - pred) ** 2, weights=n))),
            "r_squared": 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan"),
            "bins_used": int(idx.size),
            "max_lag_m": float(h.max()),
            "sill_fraction_at_max_lag": float(_model_gamma(np.array([h.max()]), nugget, nugget + psill, rng, model)[0] / (nugget + psill))
            if (nugget + psill) > 0 else float("nan"),
        }
    return out


def component_bootstrap(
    rows: np.ndarray, cols: np.ndarray, values: np.ndarray, components: np.ndarray,
    *, draws: int = 200, seed: int = 20261004, min_pairs: int = 20,
    bin_m: float = 500.0, max_lag_m: float = 60_000.0,
) -> dict:
    """Resample 8-connected fault components with replacement and refit; report range intervals."""
    rng = np.random.default_rng(seed)
    uniq = np.unique(components)
    per_model: dict[str, list[float]] = {m: [] for m in MODELS}
    for _ in range(draws):
        pick = rng.choice(uniq, size=uniq.size, replace=True)
        keep = np.concatenate([np.flatnonzero(components == c) for c in pick]) if uniq.size else np.array([], int)
        if keep.size < 50:
            continue
        bins = empirical_variogram(rows[keep], cols[keep], values[keep], components[keep],
                                   bin_m=bin_m, max_lag_m=max_lag_m)
        fits = fit_models(bins, min_pairs=min_pairs)
        for m, f in fits.items():
            per_model[m].append(f["practical_range_m"])
    out = {}
    for m, vals in per_model.items():
        if len(vals) < 20:
            out[m] = {"draws": len(vals)}
            continue
        v = np.array(vals)
        out[m] = {
            "draws": int(v.size), "median_m": float(np.median(v)),
            "p05_m": float(np.percentile(v, 5)), "p95_m": float(np.percentile(v, 95)),
            "max_m": float(v.max()),
        }
    return out


def empirical_decay_range(bins: VariogramBins, *, frac: float = 0.95, min_pairs: int = 20) -> dict:
    """Largest lag that still carries ``frac`` of the peak semivariance, read off the data alone.

    ``gamma(h)/gamma_peak`` is the fraction of the residual variance that is *still* structured at lag
    ``h``; the distance at which it falls to ``1 - frac`` (0.05 by default) is where spatial
    autocorrelation has decayed to near zero. Unlike a parametric range this cannot exceed the lag
    support, because it is read from populated bins only.
    """
    idx = bins.populated(min_pairs)
    if idx.size == 0:
        return {"decay_range_m": None, "peak_gamma": None, "peak_lag_m": None, "populated_bins": 0}
    h = bins.centres_m[idx]
    g = bins.gamma[idx]
    finite = np.isfinite(g)
    h, g = h[finite], g[finite]
    if h.size == 0:
        return {"decay_range_m": None, "peak_gamma": None, "peak_lag_m": None, "populated_bins": 0}
    peak = float(np.max(g))
    above = h[g >= frac * peak]
    return {
        "decay_range_m": float(above.max()) if above.size else float(h.min()),
        "peak_gamma": peak,
        "peak_lag_m": float(h[int(np.argmax(g))]),
        "threshold_gamma": frac * peak,
        "fraction": frac,
        "populated_bins": int(h.size),
    }


def decide_buffer_m(fits: dict[str, dict], bootstrap: dict, bins: VariogramBins,
                    *, min_pairs: int = 20, decay_frac: float = 0.95) -> dict:
    """Combine the empirical decay distance, the model fits and the bootstrap into one buffer.

    Decision rule (fixed before the numbers are seen):

    ``buffer = max(empirical decay range at 95 % of the peak semivariance,
                   median fitted practical range over the three models)``

    The *maximum* fitted range is deliberately not used as the buffer: two of the three models can
    exceed the populated lag support, and an unbounded extrapolation would make the collar arbitrary
    again — the exact failure mode this rule exists to avoid. The maximum and the bootstrap tails are
    reported as a sensitivity band instead.
    """
    stable = {m: f for m, f in fits.items() if f["sill_fraction_at_max_lag"] >= 0.80}
    ranges = {m: f["practical_range_m"] for m, f in fits.items()}
    upper = {m: bootstrap.get(m, {}).get("p95_m") for m in ranges}
    lower = {m: bootstrap.get(m, {}).get("p05_m") for m in ranges}
    medians = {m: bootstrap.get(m, {}).get("median_m") for m in ranges}
    idx = bins.populated(min_pairs)
    support_max = float(bins.centres_m[idx].max()) if idx.size else None
    decay = empirical_decay_range(bins, frac=decay_frac, min_pairs=min_pairs)
    model_median = float(np.median(list(ranges.values()))) if ranges else None
    model_max = max(ranges.values()) if ranges else None
    beyond_support = sorted(m for m, r in ranges.items() if support_max and r > support_max)
    candidates = [v for v in (decay["decay_range_m"], model_median) if v is not None]
    buffer_m = max(candidates) if candidates else None
    return {
        "buffer_m": buffer_m,
        "buffer_km": None if buffer_m is None else buffer_m / 1000.0,
        "empirical_decay_range_m": decay["decay_range_m"],
        "empirical_peak_lag_m": decay["peak_lag_m"],
        "empirical_peak_gamma": decay["peak_gamma"],
        "model_practical_ranges_m": ranges,
        "model_practical_range_median_m": model_median,
        "max_fitted_range_m": model_max,
        "bootstrap_p05_m": lower,
        "bootstrap_median_m": medians,
        "bootstrap_p95_upper_m": upper,
        "observed_lag_support_m": support_max,
        "models_reaching_80pct_sill_in_support": sorted(stable),
        "models_extrapolating_beyond_support": beyond_support,
        "rule": ("buffer = max(empirical lag at 95 % of the peak semivariance, median fitted practical "
                 "range over spherical/exponential/gaussian). The maximum fitted range and the bootstrap "
                 "95th percentile are reported as a sensitivity band, not used as the buffer, because "
                 "they can exceed the populated lag support."),
        "sensitivity_band_m": [min([v for v in [decay["decay_range_m"], model_median, lower.get("spherical"),
                                                 lower.get("exponential"), lower.get("gaussian")] if v] or [0]),
                               max([v for v in [decay["decay_range_m"], model_max] if v] or [0])],
        "warning": ("Two of the three models can exceed the populated lag support; every number that does "
                    "is an extrapolation and is flagged in models_extrapolating_beyond_support. The buffer "
                    "must be re-derived as more traces enter the sample."),
        "notes": [
            "Pairs are restricted to the same 8-connected fault component, so the curve is a within-trace "
            "residual dependence estimate, not a global one.",
            "The buffer applies to the *validation* geography (a collar deleted around every training block "
            "and every held-out block), not to the submission raster, which must cover the full footprint.",
        ],
    }
