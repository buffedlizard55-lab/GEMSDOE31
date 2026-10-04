import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_registry_and_receipt_json_are_valid_and_claim_statuses_fail_closed():
    paths = (
        list((ROOT / "registry").glob("*.json"))
        + list((ROOT / "docs" / "downloads").glob("*.json"))
        + list((ROOT / "evidence").rglob("*.json"))
    )
    assert paths
    records = {path.name: json.loads(path.read_text()) for path in paths}

    score_claims = records["score_claims.json"]
    d28_claim = next(item for item in score_claims["claims"] if item["id"] == "user-stated-gemsdoe25-d28-0.2600-20261004")
    assert d28_claim["evidence_class"] == "USER-REPORTED"
    assert d28_claim["organizer_verification"].startswith("not verified")
    assert score_claims["official_score_receipts"] == []

    h27_user = next(item for item in score_claims["claims"] if item["id"] == "user-reported-gemsdoe28-h27-4-0.2708-20261003")
    h27_owner = next(item for item in score_claims["claims"] if item["id"] == "owner-mirror-gemsdoe28-h27-4-unscored-8acb75e1f2cc")
    high_claim = next(item for item in score_claims["claims"] if item["id"] == "user-reported-public-leader-0.3195-20261003")
    d28_owner = next(item for item in score_claims["claims"] if item["id"] == "owner-reported-gemsdoe28-d28-0.2600")
    assert h27_user["evidence_class"] == "USER-REPORTED"
    assert h27_owner["evidence_class"] == "OWNER-MIRROR" and h27_owner["reported_dti"] is None
    assert high_claim["evidence_class"] == "USER-REPORTED"
    assert d28_owner["evidence_class"] == "OWNER-MIRROR" and d28_owner["reported_dti"] == 0.2600
    assert score_claims["user_supplied_historical_score_list"]["evidence_class"] == "USER-REPORTED"

    submissions = records["submissions.json"]
    assert submissions["current_slot_candidate"] is None
    assert submissions["h31_a_pilot"]["operational_variogram_range_m"] is None
    assert submissions["h31_a_pilot"]["slot_approved"] is False
    assert submissions["files"][0]["organizer_acceptance_verified"] is False

    receipt = next(value for key, value in records.items() if key.endswith("format-check.json"))
    assert receipt["ok_to_upload_format_only"] is True
    assert receipt["organizer_acceptance_verified"] is False

    pilot_results = records["results.json"]
    assert pilot_results["stage"] == "pilot"
    assert pilot_results["variogram_recommended_buffer_m"] is None
    assert pilot_results["screen_gate_passed"] is False
    diagnostics = records["posthoc_variogram_diagnostics.json"]
    assert diagnostics["all_arms_stable"] is False
    assert diagnostics["recommended_buffer_m"] is None
