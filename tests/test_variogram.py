import numpy as np
import pytest

from gemsdoe31.variogram import (
    VariogramFitError,
    bootstrap_range_interval,
    empirical_semivariogram,
    recommend_buffer_m,
)


def _ar1_trace_data(n_traces=48, length=120, scale_m=800.0):
    rng = np.random.default_rng(411)
    phi = float(np.exp(-100.0 / scale_m))
    rows, cols, components, residuals = [], [], [], []
    for component in range(1, n_traces + 1):
        e = np.empty(length, np.float64)
        e[0] = rng.normal()
        for i in range(1, length):
            e[i] = phi * e[i - 1] + np.sqrt(1.0 - phi * phi) * rng.normal()
        rows.extend([component * 3] * length)
        cols.extend(range(length))
        components.extend([component] * length)
        residuals.extend((0.2 * e).tolist())
    n = len(rows)
    return (
        np.asarray(rows),
        np.asarray(cols),
        np.asarray(components),
        np.asarray(residuals),
        np.zeros(n, dtype=np.int16),
        np.ones(n, dtype=np.int16),
    )


def test_empirical_semivariogram_and_component_bootstrap_recover_scale():
    data = _ar1_trace_data()
    empirical = empirical_semivariogram(
        *data,
        cell_size_m=100,
        bin_width_m=200,
        max_lag_m=8_000,
        min_pairs_per_bin=20,
        min_points_per_group=4,
    )
    fit = bootstrap_range_interval(
        empirical,
        max_lag_m=8_000,
        min_populated_bins=8,
        min_fit_lag_m=1_000,
        n_bootstrap=50,
        seed=91,
    )

    assert empirical.n_groups_seen == 48
    assert empirical.pair_counts.sum() > 100_000
    assert fit["stable"] is True
    point_range = fit["point_fit"]["practical_range_95_sill_m"]
    lo, hi = fit["bootstrap"]["range_95_sill_ci_m"]
    assert 600.0 < point_range < 6_000.0
    assert 0 < lo <= hi < 8_000.0
    assert fit["bootstrap"]["stable_fraction"] >= 0.80


def test_constant_within_trace_residuals_fail_closed():
    rows, cols, components, _, folds, draws = _ar1_trace_data(n_traces=40, length=80)
    residuals = np.repeat(np.linspace(0.1, 0.8, 40), 80)
    empirical = empirical_semivariogram(
        rows,
        cols,
        components,
        residuals,
        folds,
        draws,
        cell_size_m=100,
        bin_width_m=200,
        max_lag_m=8_000,
        min_pairs_per_bin=20,
    )
    with pytest.raises(VariogramFitError, match="effectively zero"):
        bootstrap_range_interval(empirical, max_lag_m=8_000, n_bootstrap=50)


def test_empirical_semivariogram_rejects_duplicate_coordinates_in_trace_group():
    rows = np.array([4, 4, 4, 4], dtype=int)
    cols = np.array([1, 1, 2, 3], dtype=int)
    components = np.ones(4, dtype=int)
    residuals = np.array([0.1, 0.2, 0.3, 0.4])
    folds = np.zeros(4, dtype=int)
    draws = np.zeros(4, dtype=int)
    with pytest.raises(ValueError, match="duplicate coordinates"):
        empirical_semivariogram(rows, cols, components, residuals, folds, draws)


def test_buffer_rounds_up_maximum_upper_interval_and_metric_support():
    stable = {"stable": True, "bootstrap": {"range_95_sill_ci_m": [820.0, 1_234.0]}}
    other = {"stable": True, "bootstrap": {"range_95_sill_ci_m": [350.0, 640.0]}}
    assert recommend_buffer_m({"base": stable, "candidate": other}) == 1_300
    assert recommend_buffer_m({"base": other}, metric_radius_m=900.0) == 900
