"""Fail-closed presentation, provenance, legacy CLI and restoration regressions."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import pytest

from gemsdoe31.decision import make_decision

ROOT = Path(__file__).resolve().parents[1]


def script(name):
    spec = importlib.util.spec_from_file_location("delivery_" + name, ROOT / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def artifact(name):
    return json.loads((ROOT / "evidence/tgj31" / name).read_text())


def test_decision_recomputed_from_actual_results_stays_negative():
    card = artifact("run_card.json")
    result = make_decision(card, artifact("holdout.json"), artifact("registry_surface.json"),
                           artifact("registry_final_support.json"), artifact("registry_universal_blocker.json"),
                           artifact("folds.json"))
    assert result == artifact("decision.json")
    assert result["quadrants_won_against_amplitude_control"] == 1
    assert result["gates"]["paired_metric_improvement"] is False
    assert result["gates"]["literal_registry"] is False
    assert result["verdict"] == "negative" and not result["safe_to_submit"]


def test_new_prediction_and_preregistration_sources_match_run_hashes():
    card = artifact("run_card.json")
    pairs = [("src/gemsdoe31/transfer.py", "feature_code_sha256"),
             ("scripts/run_tgj31.py", "code_sha256"),
             ("knowledge/2026-10-25_transfer_preregistration.md", "preregistration_sha256")]
    for path, key in pairs:
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == card["lineage"][key]


def test_original_shared_evaluator_regressions_are_unchanged():
    pin = json.loads((ROOT / "registry/shared_template_tests.json").read_text())
    assert pin["modifications"] == []
    assert hashlib.sha256((ROOT / pin["path"]).read_bytes()).hexdigest() == pin["sha256"]


def test_complete_current_owner_prompt_remains_in_readme():
    prompt = (ROOT / "knowledge/owner_request_2026-10-25.md").read_text()
    readme = (ROOT / "README.md").read_text()
    assert prompt in readme
    assert "Maximize P(Win)" in readme and "Own the Outcome" in readme
    assert "DO NOT SUBMIT" in readme


def test_site_exposes_new_file_and_negative_approval_without_an_old_submit_claim():
    card = artifact("run_card.json")
    for path in ("index.html", "executive-summary.html", "validation.html"):
        text = (ROOT / "docs" / path).read_text()
        assert 'data-safe-to-submit="false"' in text
        assert "DO NOT SUBMIT" in text
        assert "Submit it" not in text
    homepage = (ROOT / "docs/index.html").read_text()
    assert "<a download " in homepage
    assert Path(card["files"]["tif"]).name in homepage
    assert len(list((ROOT / "docs").rglob("*.html"))) == 20


def test_website_hypotheses_come_from_the_frozen_preregistration():
    text = (ROOT / "docs/research.html").read_text()
    for name in ("TGJ31 transfer-coefficient jump", "Offset texture transport", "Coupling-sign boundary",
                 "Radiometric texture displacement at gravity contacts"):
        assert name in text
    # An early site draft mixed in unregistered depth/strain ideas: prevent recurrence.
    assert "Conductive-base inversion discordance" not in text
    assert "Strain-tensor compatibility residual" not in text


def test_source_feed_is_metadata_only_and_missing_auth_is_not_a_score():
    feed = json.loads((ROOT / "docs/feed.json").read_text())
    snapshot = json.loads((ROOT / "docs/source-health.json").read_text())
    assert feed["organizer_confirmed_score"] is None
    assert feed["safe_to_submit"] is False
    assert len(feed["public_sources"]) == 10
    assert snapshot["evidence_class"] == "PUBLIC-GITHUB-METADATA"
    assert len(snapshot["checks"]) == len(feed["public_sources"])
    assert "No leaderboard" in snapshot["limitation"]
    js = (ROOT / "docs/assets/feed.js").read_text()
    assert "source-health.json" in js and "published snapshot" in js
    assert "localhost" not in js and "127.0.0.1" not in js


@pytest.mark.parametrize("flags,message", [
    (["--note", "x" * 141], "140"),
    (["--threshold", "nan"], "finite"),
    (["--threshold", "1.001"], "finite"),
    (["--name", "../unsafe"], "stem"),
])
def test_legacy_cli_rejects_invalid_note_threshold_or_name_before_io(monkeypatch, flags, message):
    builder = script("build_submission")
    monkeypatch.setattr(sys, "argv", ["build_submission.py", "--prob", "missing.tif", "--name", "test", *flags])
    with pytest.raises(ValueError, match=message):
        builder.main()


def test_legacy_writer_must_not_resample_aligned_but_wrong_sized_arrays(tmp_path):
    builder = script("build_submission")
    fp = np.ones((8, 9), bool)
    with pytest.raises(ValueError, match="exact competition template grid"):
        builder.write_variants(fp, fp, tmp_path / "bad-grid", name="bad-grid")
    assert not list(tmp_path.glob("*.tif"))


def test_restorer_does_not_trust_an_existing_file_without_hash(tmp_path, monkeypatch):
    restore = script("download_competition_data")
    dest = tmp_path / "fixture.bin"
    dest.write_bytes(b"corrupt")
    expected = b"verified"
    def download(repo, ref, remote, target):
        target.write_bytes(expected)
    monkeypatch.setattr(restore, "_download", download)
    entry = {"id": "fixture", "dest": dest.name, "repo": "test/test", "ref": "pinned",
             "path": "fixture.bin", "sha256": hashlib.sha256(expected).hexdigest()}
    result = restore.restore(entry, tmp_path)
    assert result["status"] == "restored" and dest.read_bytes() == expected


def test_failed_multipart_restore_cleans_partial_files_and_never_accepts_bad_hash(tmp_path, monkeypatch):
    restore = script("download_competition_data")
    def download(repo, ref, remote, target):
        target.write_bytes(b"wrong bytes")
        raise RuntimeError("simulated transport failure")
    monkeypatch.setattr(restore, "_download", download)
    entry = {"id": "fixture", "dest": "fixture.bin", "repo": "test/test", "ref": "pinned",
             "parts": ["part1", "part2"], "sha256": hashlib.sha256(b"expected").hexdigest()}
    with pytest.raises(RuntimeError):
        restore.restore(entry, tmp_path)
    assert not list(tmp_path.iterdir())


def test_authentication_failure_has_no_silent_unapproved_network_fallback(tmp_path, monkeypatch):
    restore = script("download_competition_data")
    monkeypatch.setattr(restore.shutil, "which", lambda _: "/bin/gh")
    class Result:
        returncode = 1
        stderr = b"Bad credentials"
    monkeypatch.setattr(restore.subprocess, "run", lambda *a, **kw: Result())
    with pytest.raises(RuntimeError, match="reconnect GitHub in Arena"):
        restore._download("test/test", "pin", "file", tmp_path / "partial")
