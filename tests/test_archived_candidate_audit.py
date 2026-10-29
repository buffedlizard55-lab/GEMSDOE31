"""Regression tests for old TIFFs and disabled unsafe prototype generators."""
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def _load_script(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _archive_hashes() -> dict[str, str]:
    out = {}
    for path in sorted((ROOT / "docs/downloads").glob("*.tif")):
        out[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return out


def test_archived_hsteo_and_csdu_audit_is_deterministic_and_negative():
    from audit_archived_candidates import audit

    measured = audit(ROOT)
    saved = (ROOT / "evidence/review_9f242e65/run_card.json").read_text()
    import json

    assert measured == json.loads(saved)
    assert measured["experiments_run_in_this_review"] == 0
    assert measured["new_tif_generated_in_this_review"] is False
    assert measured["leaderboard_estimate_for_new_file"] is None

    stages = measured["correlation_overlap_vs_registry"]["preplacement_and_final"]
    assert stages["surface"]["candidate_support_pixels"] == 465_907
    assert stages["surface"]["overlap_within_3px"] > 0.70
    assert stages["preplacement_7x7_grid_before_exact_lattice_filter"]["candidate_support_pixels"] == 9_534
    assert measured["correlation_overlap_vs_registry"]["raw_7x7_grid_exact_spacing5_collisions_removed"] == 394
    assert stages["final_dots"]["candidate_support_pixels"] == 9_140
    assert stages["final_dots"]["within_3px_of_registered_control"] == 9_135
    assert stages["final_dots"]["exact_common_positive_pixels"] == 0
    assert stages["final_dots"]["overlap_within_3px"] > 0.70
    assert measured["correlation_overlap_vs_registry"]["literal_duplicate_stop"] is True
    assert measured["hsteo_artifact"]["format_valid_against_pinned_template"] is True
    assert measured["hsteo_artifact"]["ok_to_submit"] is False

    csdu = measured["csdu_artifact"]
    assert csdu["format_valid_against_actual_pinned_template"] is False
    assert csdu["original_template_and_labels"]["not_competition_inputs"] is True
    assert csdu["original_template_and_labels"]["positive_pixels_in_saved_file"] == 4_000
    assert csdu["original_template_and_labels"]["positive_pixels_outside_actual_template_footprint"] == 1_899
    assert csdu["original_template_and_labels"]["nan_pixels_inside_actual_template_footprint"] == 2_610_312
    assert csdu["ok_to_submit"] is False


def test_retired_generators_cannot_write_or_change_any_tiff():
    before = _archive_hashes()
    for script_name, message_fragment in (
        ("generate_unique_submission", "H-STEO is retired"),
        ("run_unique_stepover_submission", "CSDU is an invalid synthetic-grid prototype"),
    ):
        module = _load_script(script_name)
        with pytest.raises(SystemExit) as exc:
            module.main()
        assert message_fragment in str(exc.value)
    assert _archive_hashes() == before


def test_retired_scripts_are_explicitly_not_raster_generators():
    for script_name in ("generate_unique_submission", "run_unique_stepover_submission"):
        source = (ROOT / "scripts" / f"{script_name}.py").read_text()
        assert "intentionally cannot" in source
        assert "def main()" in source
        assert "raise SystemExit" in source
        assert "rasterio.open(" not in source


def test_project_feed_labels_the_new_review_as_current():
    import json

    pointer = json.loads((ROOT / "registry/current_review.json").read_text())
    feed = json.loads((ROOT / "docs/feed.json").read_text())
    assert feed["latest_review"]["review_id"] == pointer["review_id"]
    assert feed["current_repository_review"]["review_id"] == pointer["review_id"]
    assert feed["current_repository_review"]["overall_verdict"].startswith("DO NOT SUBMIT")
    assert feed["previous_repository_review"]["session"] == "arena/48c411be-gemsdoe31"


def test_nine_site_executive_table_offers_pinned_direct_file_downloads():
    import json

    focus = json.loads((ROOT / "registry/session_cc130eb1_decision.json").read_text())
    summary = (ROOT / "docs/executive-summary.html").read_text()
    for row in focus["focus_site_rows"]:
        direct = row["source_url"].replace("/blob/", "/raw/", 1)
        assert direct in summary
