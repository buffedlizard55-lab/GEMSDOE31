"""Dated source verification must not imply a current raster/leaderboard audit."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_source_receipt_has_nine_distinct_focus_heads_and_hashed_official_bytes():
    base = ROOT / "evidence/review_a668bcb6"
    receipt = json.loads((base / "source_access.json").read_text())
    assert receipt["drivendata_contact"] is False
    assert receipt["leaderboard_accessed"] is False
    assert {h["site"] for h in receipt["owner_repository_heads"]} == {
        f"GEMSDOE{n}" for n in (24, 25, 27, 28, 30, 31, 32, 33, 36)
    }
    assert len(receipt["owner_repository_heads"]) == 9
    for head in receipt["owner_repository_heads"]:
        assert len(head["reviewed_head"]) == 40
        assert head["changed_since_all_pins"] == all(
            ref != head["reviewed_head"] for ref in head["pinned_artifact_refs"]
        )
        assert "Metadata only" in head["scope"]
    official = receipt["official_reference"]
    assert hashlib.sha256((base / "official-reference-README.md").read_bytes()).hexdigest() == official["sha256"]
    assert f"/blob/{official['ref']}/" in official["url"]
    assert "drivendataorg/gems-prize-reference-solution" in official["url"]


def test_new_review_notice_distinguishes_current_metadata_from_frozen_raster_audit():
    spec = importlib.util.spec_from_file_location("current_site", ROOT / "scripts/current_site.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    text = module.review_notice()
    assert "29 October" in text
    assert "9 focus repositories" in text
    assert "9 have changed" in text
    assert "does not refresh their raster audit" in text
    assert "DO NOT SUBMIT" in text
    assert "Historical HOLDOUT-DTI remains cited, not rerun" in text


def test_review_card_does_not_claim_new_tiff_holdout_or_permission():
    card = json.loads((ROOT / "evidence/review_a668bcb6/run_card.json").read_text())
    assert card["experiments_run"] == 0
    assert card["new_tif_generated"] is False
    assert card["ok_to_submit"] is False
    assert card["leaderboard_estimate"] is None
    assert card["holdout_dti"]["provenance"].startswith("CITED")
    assert card["verdict"] == "negative"
    assert 0 < len(card["note"]) <= 140
    assert card["validator"]["organizer_acceptance_verified"] is False
    assert card["raster_sha256"] == json.loads((ROOT / "registry/release_status.json").read_text())["raster_sha256"]
