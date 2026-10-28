"""H31-CC must stay a negative, format-valid research file."""
import json
from pathlib import Path
import sys

import numpy as np
import pytest
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from verify_h31cc_run import verify  # noqa: E402

TIF = ROOT / "docs/downloads/gems31-h31cc-basement-step-37654d-20261028-zeros.tif"


def test_run_card_denies_upload():
    card = json.loads((ROOT / "evidence/h31cc/run_card.json").read_text())
    assert card["verdict"] == "negative"
    assert card["ok_to_submit"] is False
    assert card["slot_approved"] is False
    assert card["leaderboard_estimate"] is None
    assert card["holdout_dti"]["evidence_class"] == "HOLDOUT-DTI"
    assert card["holdout_dti"]["evaluator_version"] == "gems57-pooled-hide-v2"
    assert card["holdout_dti"]["withheld_positive_pixels"] == 60988
    assert card["holdout_dti"]["paired_vs_null"]["ci95"][0] < 0
    assert card["correlation_overlap_vs_registry"]["final"]["lattice_overlap"] > 0.70
    assert card["correlation_overlap_vs_registry"]["final"]["max_overlap_submission"] <= 0.70
    assert len(card["files"]["note"]) <= 140


def test_existing_artifact_integrity_and_registered_stop():
    if not (ROOT / "data/sample_submission.tif").is_file():
        pytest.skip("restore pinned small inputs and registered witness for exact-byte verification")
    receipt = verify(ROOT)
    assert receipt["status"] == "VERIFIED_NEGATIVE_RESEARCH_ONLY"
    assert receipt["artifact"]["sha256"] == "0e82a9e8b80052d0bc61e8f550b2ac5204d012ab1f53fb2208051f285f10ad44"
    assert receipt["final_dot_lattice_check"]["overlap_3px"] > 0.70
    assert receipt["final_dot_lattice_check"]["literal_stop"] is True
    assert receipt["final_dot_lattice_check"]["registry_coverage_complete"] is False
    assert receipt["registered_witness"]["evidence_class"] == "OWNER-MIRROR"
    assert receipt["registered_witness"]["registered_rasters_in_manifest"] == 695
    assert receipt["leaderboard_estimate"] is None
    assert receipt["experiments_run_in_this_review"] == 0
    assert receipt["new_tif_generated_in_this_review"] is False
    assert receipt["submission_slots_used_in_this_review"] == 0
    assert receipt["ok_to_submit"] is False


def test_allfinite_values_are_in_unit_interval():
    with rasterio.open(TIF) as ds:
        values = ds.read(1)
        assert ds.crs.to_epsg() == 32611
        assert ds.shape == (3730, 3292)
        assert ds.dtypes == ("float32",)
    assert np.isfinite(values).all()
    assert float(values.min()) >= 0
    assert float(values.max()) <= 1
    assert int((values > 0).sum()) == 37654
