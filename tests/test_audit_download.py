"""The convenience command must not turn successful verification into approval."""
import copy
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import audit_download  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def fixture_status(tmp_path, monkeypatch):
    status = json.loads((ROOT / "registry/release_status.json").read_text())
    for rel in ("registry/release_status.json", "docs/downloads/current-release-status.json"):
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(status))
    monkeypatch.setattr(audit_download, "verify", lambda root: copy.deepcopy(status))
    return status


def test_verified_denial(tmp_path, monkeypatch):
    fixture_status(tmp_path, monkeypatch)
    result = audit_download.audit(tmp_path)
    assert result["status"] == "VERIFIED_DENIAL"
    assert result["ok_to_submit"] is False
    assert result["leaderboard_estimate"] is None
    assert len(result["note"]) <= 140


def test_stale_public_status(tmp_path, monkeypatch):
    fixture_status(tmp_path, monkeypatch)
    (tmp_path / "docs/downloads/current-release-status.json").write_text("{}")
    with pytest.raises(ValueError, match="stale release evidence"):
        audit_download.audit(tmp_path)


def test_never_grants_slot(tmp_path, monkeypatch):
    status = fixture_status(tmp_path, monkeypatch)
    status["ok_to_submit"] = True
    for rel in ("registry/release_status.json", "docs/downloads/current-release-status.json"):
        (tmp_path / rel).write_text(json.dumps(status))
    with pytest.raises(ValueError, match="cannot authorize"):
        audit_download.audit(tmp_path)


def test_cli_error_is_json_denial(monkeypatch, capsys):
    def broken():
        raise FileNotFoundError("missing pinned sample")
    monkeypatch.setattr(audit_download, "audit", broken)
    assert audit_download.main() == 1
    assert json.loads(capsys.readouterr().out)["ok_to_submit"] is False


def test_cli_negative_exit_code(monkeypatch, capsys):
    monkeypatch.setattr(audit_download, "audit", lambda: {"ok_to_submit": False})
    assert audit_download.main() == 2
    assert json.loads(capsys.readouterr().out)["ok_to_submit"] is False
