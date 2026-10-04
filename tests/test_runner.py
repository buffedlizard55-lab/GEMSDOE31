from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
import pytest

from gemsdoe31.variogram import VariogramFitError


RUNNER_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_h31.py"
SPEC = spec_from_file_location("gemsdoe31_h31_runner_test", RUNNER_PATH)
assert SPEC is not None and SPEC.loader is not None
RUNNER = module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class _EmpiricalStub:
    def as_dict(self):
        return {"n_residuals": 4, "pair_counts": [6, 3]}


def test_runner_accepts_the_fixed_arena_session_branch(monkeypatch):
    outputs = {
        ("status", "--porcelain"): "",
        ("branch", "--show-current"): RUNNER.EXPECTED_BRANCH,
        ("rev-parse", "HEAD"): "deadbeef",
    }
    monkeypatch.setattr(RUNNER, "git_output", lambda *args: outputs[args])

    assert RUNNER.require_clean_worktree() == "deadbeef"


def test_runner_rejects_any_other_branch(monkeypatch):
    outputs = {
        ("status", "--porcelain"): "",
        ("branch", "--show-current"): "main",
    }
    monkeypatch.setattr(RUNNER, "git_output", lambda *args: outputs[args])

    with pytest.raises(SystemExit, match="wrong working branch"):
        RUNNER.require_clean_worktree()


def test_unstable_variogram_result_retains_empirical_diagnostics(monkeypatch):
    empirical = _EmpiricalStub()
    monkeypatch.setattr(RUNNER, "empirical_semivariogram", lambda *args, **kwargs: empirical)

    def fail_fit(*args, **kwargs):
        raise VariogramFitError("range is unstable")

    monkeypatch.setattr(RUNNER, "bootstrap_range_interval", fail_fit)
    arrays = {
        "rows": np.arange(4),
        "cols": np.arange(4),
        "components": np.ones(4, dtype=np.int32),
        "folds": np.zeros(4, dtype=np.int16),
        "draws": np.full(4, 10, dtype=np.int16),
        "base_residual": np.linspace(0.1, 0.4, 4),
    }

    result = RUNNER._fit_variogram_arm(arrays, "base")

    assert result["stable"] is False
    assert result["error"] == "VariogramFitError: range is unstable"
    assert result["empirical"] == empirical.as_dict()
