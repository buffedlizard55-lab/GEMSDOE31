import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_registry_and_receipt_json_are_valid_and_claim_statuses_fail_closed():
    paths = list((ROOT / "registry").glob("*.json")) + list((ROOT / "docs" / "downloads").glob("*.json"))
    assert paths
    records = {path.name: json.loads(path.read_text()) for path in paths}

    score_claims = records["score_claims.json"]
    d28_claim = next(item for item in score_claims["claims"] if item["id"] == "user-stated-gemsdoe25-d28-0.2600-20261004")
    assert d28_claim["evidence_class"] == "USER-REPORTED"
    assert d28_claim["organizer_verification"].startswith("not verified")

    submissions = records["submissions.json"]
    assert submissions["current_slot_candidate"] is None
    assert submissions["files"][0]["organizer_acceptance_verified"] is False

    receipt = next(value for key, value in records.items() if key.endswith("format-check.json"))
    assert receipt["ok_to_upload_format_only"] is True
    assert receipt["organizer_acceptance_verified"] is False
