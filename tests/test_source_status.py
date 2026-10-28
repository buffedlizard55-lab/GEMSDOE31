"""The public-source HEAD feed stays separate from scores and DrivenData access."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("refresh_source_status", ROOT / "scripts/refresh_source_status.py")
refresh = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(refresh)


def _write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


def test_load_targets_prefers_generated_feed_and_validates_pins(tmp_path):
    targets = [
        {"repo": "owner/site-a", "pin": "a" * 40},
        {"repo": "owner/site-b", "pin": "b" * 40},
    ]
    _write_json(tmp_path / "docs/feed.json", {"public_sources": targets})
    _write_json(tmp_path / "docs/source-health.json", {"checks": [{"repo": "ignored/site", "pin": "c" * 40}]})
    assert refresh.load_targets(tmp_path) == targets


def test_load_targets_falls_back_to_snapshot_for_prebuild_feed(tmp_path):
    targets = [{"repo": "owner/site-a", "pin": "a" * 40}]
    _write_json(tmp_path / "docs/source-health.json", {"checks": [
        {**targets[0], "ok": True, "current": "d" * 40},
    ]})
    assert refresh.load_targets(tmp_path) == targets


@pytest.mark.parametrize("source", [
    {"repo": "https://example.invalid/owner/repo", "pin": "a" * 40},
    {"repo": "owner/repo", "pin": "not-a-commit"},
])
def test_load_targets_rejects_unbounded_or_bad_target(tmp_path, source):
    _write_json(tmp_path / "docs/feed.json", {"public_sources": [source]})
    with pytest.raises(ValueError):
        refresh.load_targets(tmp_path)


def test_load_targets_rejects_duplicate_repository(tmp_path):
    target = {"repo": "owner/site-a", "pin": "a" * 40}
    _write_json(tmp_path / "docs/feed.json", {"public_sources": [target, target]})
    with pytest.raises(ValueError, match="duplicate"):
        refresh.load_targets(tmp_path)


def test_published_feed_and_sources_widget_share_public_targets():
    feed = json.loads((ROOT / "docs/feed.json").read_text())
    snapshot = json.loads((ROOT / "docs/source-health.json").read_text())
    expected = [{"repo": row["repo"], "pin": row["pin"]} for row in snapshot["checks"]]
    assert feed["public_sources"] == expected
    assert feed["source_health_snapshot"]["file"] == "source-health.json"
    assert feed["current_repository_review"]["verdict"] == "negative"
    sources = (ROOT / "docs/sources.html").read_text()
    assert 'id="feed-status"' in sources and 'id="source-health"' in sources
    assert 'src="assets/feed.js"' in sources
    js = (ROOT / "docs/assets/feed.js").read_text()
    assert "feed.public_sources" in js
    assert "api.github.com/repos/${source.repo}/commits?per_page=1" in js
    assert "fromSnapshot: true" in js and "snapshotChecked" in js
    assert "drivendata.org" not in js.lower()
    assert "leaderboard" in js.lower()  # explicit non-access disclosure
    refresh_source = (ROOT / "scripts/refresh_source_status.py").read_text()
    assert 'f"repos/{repo}/commits?per_page=1"' in refresh_source
    assert "drivendata.org" not in refresh_source.lower()
