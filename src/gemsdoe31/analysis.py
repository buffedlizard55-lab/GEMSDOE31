"""Stage-level paired gate and evidence summaries for the H31-A screen."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from .variogram import VariogramFitError, recommend_buffer_m

ARMS = ("base", "h31_candidate")
FOLD_NAMES = ("NW", "NE", "SW", "SE")
MIN_GAIN = 0.001
MAX_FOLD_LOSS = 0.010
MAX_HUG_INCREASE = 0.10
MAX_BUFFER_ITERATIONS = 3


def select_screen_buffer(
    pilot_buffer_m: int,
    *,
    iteration: int,
    requested_buffer_m: int | None = None,
    previous_screen: dict | None = None,
    cell_size_m: int = 100,
) -> int:
    """Return the preregistered buffer for a screen attempt, with at most three iterations.

    Attempt one must use the pilot's exact recommendation. Attempts two and three require the immediately
    preceding, metric-passing screen to have an unstable buffer and a larger ``next_buffer_m``. The next
    attempt must use that exact recommendation; a metric-failing or stable screen cannot be retried.
    """
    if isinstance(iteration, bool) or not isinstance(iteration, int) or iteration not in range(1, MAX_BUFFER_ITERATIONS + 1):
        raise ValueError(f"buffer iteration must be an integer in 1..{MAX_BUFFER_ITERATIONS}")
    if isinstance(pilot_buffer_m, bool) or not isinstance(pilot_buffer_m, int) or pilot_buffer_m <= 0:
        raise ValueError("pilot buffer must be a positive integer number of metres")
    if isinstance(cell_size_m, bool) or not isinstance(cell_size_m, int) or cell_size_m <= 0:
        raise ValueError("cell size must be a positive integer number of metres")
    if pilot_buffer_m % cell_size_m:
        raise ValueError("pilot-recommended buffer must be a grid-cell multiple")

    if iteration == 1:
        if previous_screen is not None:
            raise ValueError("iteration 1 must not include a previous screen result")
        expected = pilot_buffer_m
    else:
        if not isinstance(previous_screen, dict):
            raise ValueError(f"iteration {iteration} requires the immediately previous screen result")
        previous_iteration = previous_screen.get("buffer_iteration")
        if (
            previous_screen.get("stage") != "screen"
            or isinstance(previous_iteration, bool)
            or not isinstance(previous_iteration, int)
            or previous_iteration != iteration - 1
        ):
            raise ValueError("previous screen result does not match the immediately preceding buffer iteration")
        previous_buffer = previous_screen.get("buffer_m")
        next_buffer = previous_screen.get("next_buffer_m")
        metrics = previous_screen.get("metrics")
        if isinstance(previous_buffer, bool) or not isinstance(previous_buffer, int):
            raise ValueError("previous screen result has no valid applied buffer")
        if previous_screen.get("buffer_stable") is not False or not isinstance(metrics, dict) or metrics.get("metric_gate_passed") is not True:
            raise ValueError("previous screen must pass the metric gate but fail only buffer stability")
        if isinstance(next_buffer, bool) or not isinstance(next_buffer, int) or next_buffer <= previous_buffer:
            raise ValueError("previous screen has no larger data-derived next buffer")
        if next_buffer < pilot_buffer_m or next_buffer % cell_size_m:
            raise ValueError("previous screen next buffer violates the pilot minimum or grid")
        expected = next_buffer

    if requested_buffer_m is not None:
        if isinstance(requested_buffer_m, bool) or not isinstance(requested_buffer_m, int):
            raise ValueError("requested buffer must be an integer number of metres")
        if requested_buffer_m != expected:
            raise ValueError(f"screen iteration {iteration} must use exactly the preregistered {expected} m buffer")
    return expected


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows = []
    with Path(path).open() as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON at {path}:{line_number}: {exc}") from exc
            rows.append(row)
    return rows


def _pooled_dti(rows: list[dict[str, Any]]) -> dict[str, float | int]:
    tp = float(sum(row["tp"] for row in rows))
    fp = float(sum(row["fp"] for row in rows))
    n_truth = int(sum(row["n_truth"] for row in rows))
    fn = float(n_truth) - tp
    if n_truth <= 0:
        value = 0.0
    else:
        value = tp / (tp + 0.2 * fp + 0.8 * fn + 1e-7)
    return {"tp": tp, "fp": fp, "fn": fn, "n_truth": n_truth, "pooled_dti": float(value)}


def _validate_cell_rows(rows: list[dict[str, Any]], draws: list[int]) -> None:
    expected = {(arm, fold, draw) for arm in ARMS for fold in range(4) for draw in draws}
    actual = set()
    for row in rows:
        key = (row.get("arm"), row.get("fold"), row.get("draw"))
        if key in actual:
            raise ValueError(f"duplicate H31 cell row: {key}")
        actual.add(key)
        required = ("dti", "tp", "fp", "n_truth", "emitted", "hug")
        for name in required:
            value = row.get(name)
            if value is None or not np.isfinite(float(value)):
                raise ValueError(f"nonfinite or absent {name} in H31 cell {key}")
        auc = row.get("auc")
        if auc is not None and not np.isfinite(float(auc)):
            raise ValueError(f"AUC must be finite or null in H31 cell {key}")
        if not 0.0 <= float(row["dti"]) <= 1.0:
            raise ValueError(f"DTI outside [0,1] in H31 cell {key}")
    if actual != expected:
        raise ValueError(f"H31 cell set differs from preregistration; missing={sorted(expected-actual)}, extra={sorted(actual-expected)}")


def summarize_stage(
    rows: list[dict[str, Any]],
    variogram_fits: dict[str, dict],
    *,
    stage: str,
    draws: list[int],
    buffer_m: int,
    minimum_buffer_m: int | None = None,
    screen_results_path: str | Path | None = None,
) -> dict[str, Any]:
    """Summarize paired model outcomes and fail closed on buffer/gate/confirmation problems."""
    _validate_cell_rows(rows, draws)
    by_arm = {arm: [r for r in rows if r["arm"] == arm] for arm in ARMS}
    pooled = {arm: _pooled_dti(arm_rows) for arm, arm_rows in by_arm.items()}
    fold_rows: dict[int, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        fold_rows[int(row["fold"])][str(row["arm"])].append(row)

    per_fold = []
    for fold in range(4):
        base = fold_rows[fold]["base"]
        candidate = fold_rows[fold]["h31_candidate"]
        base_mean = float(np.mean([r["dti"] for r in base]))
        candidate_mean = float(np.mean([r["dti"] for r in candidate]))
        base_hug = float(np.mean([r["hug"] for r in base]))
        candidate_hug = float(np.mean([r["hug"] for r in candidate]))
        per_fold.append({
            "fold": fold,
            "fold_name": FOLD_NAMES[fold],
            "base_mean_dti": base_mean,
            "candidate_mean_dti": candidate_mean,
            "paired_delta_dti": candidate_mean - base_mean,
            "base_mean_hug_share": base_hug,
            "candidate_mean_hug_share": candidate_hug,
            "hug_share_delta": candidate_hug - base_hug,
            "base_by_draw": {str(r["draw"]): float(r["dti"]) for r in base},
            "candidate_by_draw": {str(r["draw"]): float(r["dti"]) for r in candidate},
        })
    deltas = np.asarray([r["paired_delta_dti"] for r in per_fold], dtype=np.float64)
    hug_deltas = np.asarray([r["hug_share_delta"] for r in per_fold], dtype=np.float64)
    metric_gate = bool(
        float(deltas.mean()) > MIN_GAIN
        and int(np.count_nonzero(deltas > 0.0)) >= 3
        and float(deltas.min()) >= -MAX_FOLD_LOSS
        and float(hug_deltas.mean()) <= MAX_HUG_INCREASE
    )

    variogram_errors = {}
    upper_by_arm = {}
    all_variograms_stable = set(variogram_fits) == set(ARMS)
    for arm in ARMS:
        fit = variogram_fits.get(arm)
        if not isinstance(fit, dict) or not fit.get("stable"):
            all_variograms_stable = False
            variogram_errors[arm] = "missing or unstable fit"
            continue
        try:
            upper_by_arm[arm] = float(fit["bootstrap"]["range_95_sill_ci_m"][1])
        except (KeyError, TypeError, IndexError, ValueError) as exc:
            all_variograms_stable = False
            variogram_errors[arm] = f"missing upper interval: {exc}"
    if all_variograms_stable:
        try:
            recommended_buffer_m = recommend_buffer_m(variogram_fits)
        except (ValueError, VariogramFitError) as exc:
            all_variograms_stable = False
            recommended_buffer_m = None
            variogram_errors["buffer"] = str(exc)
    else:
        recommended_buffer_m = None

    initial_ok = minimum_buffer_m is None or buffer_m >= minimum_buffer_m
    stable_buffer = bool(
        all_variograms_stable
        and initial_ok
        and recommended_buffer_m is not None
        and recommended_buffer_m <= buffer_m
    )
    next_buffer_m = None
    if all_variograms_stable and recommended_buffer_m is not None and recommended_buffer_m > buffer_m:
        next_buffer_m = recommended_buffer_m

    confirm_gate = None
    if stage == "confirm":
        if screen_results_path is None:
            raise ValueError("confirmation analysis requires the passing final screen results path")
        screen = json.loads(Path(screen_results_path).read_text())
        if not screen.get("screen_gate_passed") or int(screen.get("buffer_m", -1)) != int(buffer_m):
            raise ValueError("confirmation is not authorized: screen gate failed or buffer differs")
        confirm_gate = bool(metric_gate and stable_buffer)

    mean_gain = float(deltas.mean())
    summary: dict[str, Any] = {
        "stage": stage,
        "draws": [int(x) for x in draws],
        "buffer_m": int(buffer_m),
        "minimum_required_buffer_m": int(minimum_buffer_m) if minimum_buffer_m is not None else None,
        "variogram_upper_range_m_by_arm": upper_by_arm,
        "variogram_recommended_buffer_m": int(recommended_buffer_m) if recommended_buffer_m is not None else None,
        "variograms_stable": bool(all_variograms_stable),
        "buffer_stable": stable_buffer,
        "next_buffer_m": int(next_buffer_m) if next_buffer_m is not None else None,
        "variogram_errors": variogram_errors,
        "metrics": {
            "mean_paired_delta_dti_over_four_spatial_blocks": mean_gain,
            "positive_folds": int(np.count_nonzero(deltas > 0.0)),
            "worst_fold_delta_dti": float(deltas.min()),
            "mean_hug_share_delta": float(hug_deltas.mean()),
            "thresholds": {
                "mean_gain_strictly_greater_than": MIN_GAIN,
                "positive_spatial_blocks_at_least": 3,
                "worst_fold_delta_at_least": -MAX_FOLD_LOSS,
                "mean_hug_share_delta_at_most": MAX_HUG_INCREASE,
            },
            "metric_gate_passed": metric_gate,
            "per_fold": per_fold,
            "pooled_sufficient_statistics_across_cells": pooled,
            "cell_rows": len(rows),
            "interpretation": "pooled DTI is descriptive across folds/draws; the preregistered gate uses paired fold-mean DTI, not a proxy competition score",
        },
        "screen_gate_passed": bool(stage == "screen" and metric_gate and stable_buffer),
        "confirmation_gate_passed": confirm_gate,
        "slot_eligible": False,
        "slot_decision": "not approved: owner-mirror proxy only; separate exact-file and official provenance gates remain",
    }
    return summary
