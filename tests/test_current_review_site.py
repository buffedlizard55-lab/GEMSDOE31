"""The generated site must lead with the active review, never a stale session card."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def load_build_site():
    spec = importlib.util.spec_from_file_location("build_site", ROOT / "scripts/build_site.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_active_session_panel_uses_current_review_register():
    rendered = load_build_site().session_panel(full=True)

    assert "arena/a5caa430-gemsdoe31" in rendered
    assert "arena/cc130eb1-gemsdoe31" not in rendered
    assert "NO FILE IS CLEARED TO SUBMIT" in rendered
    assert "no weekly slot was used" in rendered
    assert "Nine-site executive table" in rendered
    for site in (
        "GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
        "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36",
    ):
        assert site in rendered
    assert "USER-REPORTED; no organizer receipt" in rendered
    assert "unavailable / not estimable" in rendered
    assert "DOWNLOAD:" in rendered
    assert "SUBMIT: NO" in rendered
    assert "all 36 pairwise overlaps exceed 70% at 3 px" in rendered
    assert "Cited HOLDOUT-DTI" in rendered
    assert "gems57-pooled-hide-v2" in rendered
    assert "not exhaustive registry coverage" in rendered


def test_active_panel_separates_hsteo_download_from_submission_permission():
    rendered = load_build_site().session_panel(full=True)

    assert 'Download prior H-STEO research TIFF — DO NOT SUBMIT' in rendered
    assert 'Download:</strong> research/learning only.' in rendered
    assert 'Submit/upload:</strong> NO.' in rendered
    assert 'not established' in rendered
    assert 'HOLDOUT-DTI' in rendered
    assert 'No new name/note was reserved for this review.' in rendered
    assert '600 m' in rendered
    assert '7x7' in rendered
    assert 'does not measure stepovers' in rendered
    assert '0/9 threshold duplicates' in rendered
    assert '0.339606' in rendered
    assert '0.084012' in rendered
    assert 'hsteo-focus-uniqueness.json' in rendered
    assert 'data/hsteo-validation-nan.json' in rendered
    assert 'data/hsteo-validation-allfinite.json' in rendered


def test_hypotheses_and_access_status_are_visible_without_numeric_projections():
    rendered = load_build_site().session_panel(full=True)

    for hypothesis in (
        "H-CC-A thermal-manifestation point-pattern alignment",
        "H-CC-B World Stress Map conditioned lineament prior",
        "H-CC-C ComCat focal-mechanism geometry",
        "H-CC-D SMU heat-flow residual corridors",
    ):
        assert hypothesis in rendered
    assert "named non-fault mimic" in rendered.lower()
    assert "NOT VALIDATED" in rendered
    assert "no numeric delta is estimated" in rendered
    assert "not fetched this session" in rendered
    assert "leaderboard" in rendered
    assert "conflicting 0.3195 and 0.4413" in rendered


def test_active_index_panel_links_to_local_review_artifacts():
    rendered = load_build_site().session_panel(full=False)

    assert "executive-summary.html" in rendered
    assert "data/current-review.json" in rendered
    assert "data/current-run-card.json" in rendered
    assert "data/current-verification.json" in rendered
    assert "downloads/gemsdoe31-h-steo-offcatalogue-stepper-20261029T164949Z-4bbba08696ed-nan.tif" in rendered
    assert "DO NOT SUBMIT" in rendered


def test_executive_hero_does_not_relabel_archived_h31aa_as_current():
    site = load_build_site()
    rendered = site.build_executive_summary(
        site.load("registry/submissions.json"),
        site.load("evidence/buffer_derivation.json"),
        site.submission_receipts(),
    )

    assert "Current repository review" in rendered
    assert "No file is cleared to submit" in rendered
    assert "Historical panels below are prior-session evidence only" in rendered
    assert "newly generated H31-AA" not in rendered
    assert "new-file estimate is unavailable" in rendered


def test_html_feed_starts_with_current_session_notice_not_legacy_recommendation():
    site = load_build_site()
    feed_json, feed_html = site.build_feed(
        site.load("registry/submissions.json"),
        site.load("evidence/buffer_derivation.json"),
        site.load("evidence/union_results.json"),
        site.load("evidence/arm_results.json"),
        site.load("registry/sources.json"),
    )
    assert "arena/a5caa430-gemsdoe31" in feed_html
    assert "Current review JSON" in feed_html
    assert "DO NOT SUBMIT" in feed_html
    assert "arena/cc130eb1-gemsdoe31" not in feed_html
    assert '"current_download"' in feed_json
    assert '"current_review_verification"' in feed_json
