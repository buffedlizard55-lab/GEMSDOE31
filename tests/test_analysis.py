import pytest

from gemsdoe31.analysis import select_screen_buffer, summarize_stage


def _rows(candidate_deltas, *, draws=(11, 12)):
    rows = []
    for fold in range(4):
        for draw in draws:
            base = 0.10 + 0.001 * fold + 0.0002 * draw
            delta = candidate_deltas[fold]
            for arm, dti, hug in (("base", base, 0.20), ("h31_candidate", base + delta, 0.21)):
                rows.append({
                    "arm": arm,
                    "fold": fold,
                    "draw": draw,
                    "dti": dti,
                    "tp": 20.0,
                    "fp": 30.0,
                    "n_truth": 100,
                    "emitted": 80,
                    "hug": hug,
                    "auc": 0.6,
                })
    return rows


def _fits(upper=1_500.0):
    fit = {"stable": True, "bootstrap": {"range_95_sill_ci_m": [800.0, upper]}}
    return {"base": fit, "h31_candidate": fit}


def test_screen_gate_requires_paired_gain_and_stable_buffer():
    results = summarize_stage(
        _rows([0.002, 0.002, 0.002, 0.002]),
        _fits(),
        stage="screen",
        draws=[11, 12],
        buffer_m=2_000,
        minimum_buffer_m=1_500,
    )
    assert results["metrics"]["metric_gate_passed"] is True
    assert results["buffer_stable"] is True
    assert results["screen_gate_passed"] is True
    assert results["slot_eligible"] is False
    assert results["metrics"]["pooled_sufficient_statistics_across_cells"]["base"]["pooled_dti"] > 0


def test_screen_fails_when_upper_range_exceeds_applied_buffer(tmp_path):
    results = summarize_stage(
        _rows([0.002, 0.002, 0.002, 0.002]),
        _fits(upper=2_400.0),
        stage="screen",
        draws=[11, 12],
        buffer_m=2_000,
        minimum_buffer_m=1_500,
    )
    assert results["metrics"]["metric_gate_passed"] is True
    assert results["buffer_stable"] is False
    assert results["next_buffer_m"] == 2_400
    assert results["screen_gate_passed"] is False


def test_confirmation_requires_a_passing_screen_and_exact_buffer(tmp_path):
    screen = tmp_path / "screen.json"
    screen.write_text('{"screen_gate_passed": true, "buffer_m": 2000, "buffer_stable": true}\n')
    results = summarize_stage(
        _rows([0.002, 0.002, 0.002, 0.002], draws=(13, 14)),
        _fits(upper=1_800.0),
        stage="confirm",
        draws=[13, 14],
        buffer_m=2_000,
        minimum_buffer_m=2_000,
        screen_results_path=screen,
    )
    assert results["confirmation_gate_passed"] is True
    assert results["screen_gate_passed"] is False


def test_negative_screen_gain_fails_gate():
    results = summarize_stage(
        _rows([0.002, 0.002, -0.004, 0.002]),
        _fits(),
        stage="screen",
        draws=[11, 12],
        buffer_m=2_000,
        minimum_buffer_m=1_500,
    )
    assert results["metrics"]["metric_gate_passed"] is False
    assert results["screen_gate_passed"] is False


def test_screen_buffer_attempts_follow_data_derived_retry_chain():
    assert select_screen_buffer(1_700, iteration=1) == 1_700
    with pytest.raises(ValueError, match="exactly"):
        select_screen_buffer(1_700, iteration=1, requested_buffer_m=1_800)

    previous = {
        "stage": "screen",
        "buffer_iteration": 1,
        "buffer_m": 1_700,
        "next_buffer_m": 2_200,
        "buffer_stable": False,
        "metrics": {"metric_gate_passed": True},
    }
    assert select_screen_buffer(1_700, iteration=2, previous_screen=previous) == 2_200
    assert select_screen_buffer(1_700, iteration=2, requested_buffer_m=2_200, previous_screen=previous) == 2_200

    previous2 = {**previous, "buffer_iteration": 2, "buffer_m": 2_200, "next_buffer_m": 2_600}
    assert select_screen_buffer(1_700, iteration=3, previous_screen=previous2) == 2_600


def test_screen_buffer_retry_stops_on_metric_failure_or_after_three_attempts():
    previous = {
        "stage": "screen",
        "buffer_iteration": 1,
        "buffer_m": 1_700,
        "next_buffer_m": 2_200,
        "buffer_stable": False,
        "metrics": {"metric_gate_passed": False},
    }
    with pytest.raises(ValueError, match="pass the metric gate"):
        select_screen_buffer(1_700, iteration=2, previous_screen=previous)
    with pytest.raises(ValueError, match="1..3"):
        select_screen_buffer(1_700, iteration=4)
    with pytest.raises(ValueError, match="previous screen"):
        select_screen_buffer(1_700, iteration=2)
