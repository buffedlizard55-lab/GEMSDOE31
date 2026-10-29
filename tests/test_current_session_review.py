"""Fail-closed assertions for the 2026-10-29 Arena review record."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD_PATH = ROOT / "evidence/review_eebfaae2/run_card.json"


def test_current_review_has_no_candidate_or_submission_approval():
    card = json.loads(CARD_PATH.read_text())
    assert card["session"] == "arena/eebfaae2-gemsdoe31"
    assert card["verdict"] == "negative"
    assert card["experiments"]["run"] == 0
    assert card["raster_sha256"]["new_raster_generated"] is False
    assert card["holdout_dti"]["new_candidate"]["status"] == "NOT RUN THIS SESSION"
    assert card["holdout_dti"]["new_candidate"]["dti"] is None
    assert card["leaderboard_score_estimate"] is None
    assert card["submission"]["ok_to_download_new_candidate"] is False
    assert card["submission"]["existing_research_artifacts_downloadable"] is True
    assert card["submission"]["ok_to_submit"] is False
    assert card["submission"]["slot_approved"] is False
    assert 0 < card["submission"]["note_characters"] <= 140
    assert len(card["submission"]["note"]) == card["submission"]["note_characters"]


def test_reviewed_artifact_hash_matches_run_card():
    card = json.loads(CARD_PATH.read_text())
    artifact_record = card["raster_sha256"]["canonical_release_artifact_reviewed"]
    artifact = ROOT / artifact_record["file"]
    actual = hashlib.sha256(artifact.read_bytes()).hexdigest()
    assert actual == artifact_record["sha256"]
    assert actual == card["correlation_overlap_vs_registry"]["existing_release_artifact"]["sha256"]

    later = card["raster_sha256"]["later_dated_existing_research_artifact"]
    later_path = ROOT / later["file"]
    assert hashlib.sha256(later_path.read_bytes()).hexdigest() == later["sha256"]
    assert later["holdout_dti"] is None
    assert later["full_registry_comparison"] is False


def test_readme_and_generated_executive_summary_expose_do_not_submit_status():
    readme = (ROOT / "README.md").read_text()
    summary = (ROOT / "docs/executive-summary.html").read_text()
    assert "arena/eebfaae2-gemsdoe31" in readme
    assert "knowledge/repo_review_2026-10-29_arena-eebfaae2.md" in readme
    assert "DO NOT SUBMIT" in summary
    assert "repo_review_2026-10-29_arena-eebfaae2.md" in summary
