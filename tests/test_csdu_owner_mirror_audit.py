"""The concurrent CSDU artifact remains a reproducibly recorded negative audit."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "verify_csdu_footprint_audit", ROOT / "scripts/verify_csdu_footprint_audit.py"
)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


@pytest.mark.skipif(not (ROOT / "data/sample_submission.tif").is_file(), reason="pinned small sample is not restored")
def test_csdu_exact_footprint_failure_is_reproducible_and_fail_closed():
    result = module.verify(ROOT)
    assert result["audit_reproduced"] is True
    assert result["candidate_format_valid_for_pinned_sample"] is False
    assert result["holdout_tested"] is False
    assert result["registry_uniqueness_tested"] is False
    assert result["slot_approved"] is False
    assert "outside_footprint_zero" in result["variants"]["all_finite"]["hard_failures"]
    assert set(result["variants"]["nan_outside"]["hard_failures"]) == {
        "footprint_all_finite",
        "footprint_values_in_0_1",
        "outside_footprint_nan",
        "nan_mask_matches_template",
    }


def test_original_csdu_generator_is_quarantined(capsys):
    generator_spec = importlib.util.spec_from_file_location(
        "quarantined_csdu_generator", ROOT / "scripts/run_unique_stepover_submission.py"
    )
    generator = importlib.util.module_from_spec(generator_spec)
    assert generator_spec.loader is not None
    generator_spec.loader.exec_module(generator)

    assert generator.main() == 2
    assert "DO NOT RUN" in capsys.readouterr().err
