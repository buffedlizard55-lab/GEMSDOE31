"""H31-CC must stay a negative, format-valid research file."""
import json
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
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
