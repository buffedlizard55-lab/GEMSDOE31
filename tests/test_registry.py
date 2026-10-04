import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _records():
    paths = (
        list((ROOT / "registry").glob("*.json"))
        + list((ROOT / "docs" / "downloads").glob("*.json"))
        + list((ROOT / "evidence").rglob("*.json"))
    )
    assert paths
    return {path.name: json.loads(path.read_text()) for path in paths}


def test_registry_and_receipt_json_are_valid_and_claim_statuses_fail_closed():
    records = _records()

    score_claims = records["score_claims.json"]
    d28_claim = next(item for item in score_claims["claims"] if item["id"] == "user-stated-gemsdoe25-d28-0.2600-20261004")
    assert d28_claim["evidence_class"] == "USER-REPORTED"
    assert d28_claim["organizer_verification"].startswith("not verified")
    assert score_claims["official_score_receipts"] == []

    pilot_results = records["results.json"]
    assert pilot_results["stage"] == "pilot"
    assert pilot_results["variogram_recommended_buffer_m"] is None
    assert pilot_results["screen_gate_passed"] is False
    diagnostics = records["posthoc_variogram_diagnostics.json"]
    assert diagnostics["all_arms_stable"] is False
    assert diagnostics["recommended_buffer_m"] is None


def test_submissions_register_never_marks_a_file_slot_approved():
    submissions = json.loads((ROOT / "registry" / "submissions.json").read_text())
    assert submissions["current_recommended"]["slot_approved"] is False
    assert submissions["best_research_candidate"]["slot_approved"] is False
    assert submissions["files"], "the register must list the built files"
    for record in submissions["files"]:
        assert record["slot_approved"] is False, f"{record['name']} is slot-approved without a gate record"
        assert record["format_status"].startswith("locally validated")
        if "sha256_nan" in record:
            assert len(record["sha256_nan"]) == 64
            assert record["file_nan"].endswith(".tif")
        assert record.get("organizer_acceptance_verified_nan", False) is False


def test_every_registered_file_exists_and_the_hash_matches_its_receipt():
    import hashlib

    submissions = json.loads((ROOT / "registry" / "submissions.json").read_text())
    for record in submissions["files"]:
        for convention in ("nan", "allfinite"):
            key = f"file_{convention}"
            if key not in record:
                continue
            path = ROOT / record[key]
            assert path.is_file(), f"{record[key]} listed in the register but missing from the repository"
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            assert digest == record[f"sha256_{convention}"], f"{path.name} changed since its receipt was written"


def test_metric_module_reproduces_the_published_identity_and_exact_cases():
    import sys

    sys.path.insert(0, str(ROOT / "src"))
    import numpy as np

    from gemsdoe31 import metric

    truth = np.zeros((9, 9), dtype=bool)
    truth[4, 4] = True
    single = np.zeros((9, 9), dtype=float)
    single[4, 6] = 1.0
    result = metric.dti(single, truth)
    assert abs(result["TPw"] - 1 / 3) < 1e-12
    assert abs(result["FNw"] - 2 / 3) < 1e-12
    assert abs(result["DTI"] - 1 / 3) < 1e-9
    assert abs(result["TPw"] + result["FNw"] - 1.0) < 1e-12
    brute = metric.brute_force(single, truth)
    assert abs(brute["DTI"] - result["DTI"]) < 1e-12
    assert metric._offsets(metric.CELL_M, metric.RADIUS_M)[0].shape[0] == 29


def test_metric_check_evidence_matches_the_committed_claims():
    record = json.loads((ROOT / "evidence" / "metric_check.json").read_text())
    assert record["kernel_offsets_in_support"] == 29
    assert record["max_abs_dti_delta_vs_brute_force"] < 1e-12
    assert record["grids_compared"] >= 10
    for case in record["exact_cases"]:
        assert abs(case["DTI"] - case["DTI_closed_form"]) < 1e-9


def test_buffer_decision_is_derived_not_assumed():
    decision = json.loads((ROOT / "evidence" / "buffer_derivation.json").read_text())["decision"]
    assert decision["buffer_m"] >= decision["empirical_decay_range_m"]
    assert decision["buffer_km"] > 5.0, "an assumed 4-5 pixel collar must not reappear"
    assert decision["observed_lag_support_m"] >= decision["empirical_peak_lag_m"]
    assert "max_bootstrap_p95_m" not in decision or decision["buffer_m"] != decision["max_bootstrap_p95_m"]


def test_union_artifact_shows_the_incumbent_was_never_thinned():
    union = json.loads((ROOT / "evidence" / "union_results.json").read_text())
    incumbent = union["incumbent"]
    assert incumbent["dots"] == 40_199
    assert abs(incumbent["ff_DTI"] - 0.09384814898733441) < 1e-9
    for row in union["unions"]:
        assert row["dots"] >= incumbent["dots"], "union rows must add dots, never remove them"
    best = union["best_union"]
    assert row_present(union, best), "best_union must be reproducible from the sweep rows"
    assert best["delta"] > 0


def row_present(union: dict, best: dict) -> bool:
    return any(row["arm"] == best["arm"] and abs(row["threshold"] - best["threshold"]) < 1e-9
               and row["drop_catalogue_pixels"] and row["dots"] == best["dots"]
               for row in union["unions"])


def test_filter_artifact_documents_that_filtering_loses():
    record = json.loads((ROOT / "evidence" / "incumbent_filter_results.json").read_text())
    assert record["rows"], "the filter sweep must be present"
    assert all(row["ff_delta"] < 0 for row in record["rows"]), \
        "filtering the incumbent must be recorded as a loss; if that changes, the story changes"
