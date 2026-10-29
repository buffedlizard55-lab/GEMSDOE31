"""No raster generation: synthetic policy objects and mocked format-only writers."""
import copy
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

from gemsdoe31.packaging_policy import require_research_packaging, research_only_permissions
from gemsdoe31.release_policy import POLICY_VERSION, uniqueness_gate

ROOT = Path(__file__).resolve().parents[1]


def status_fixture():
    stages = {s: {"max_abs_rho": .2, "max_overlap": .5, "coverage_complete": True}
              for s in ("surface", "final")}
    return {"policy_version": POLICY_VERSION, "method_lane_assigned": True,
            "correlation_overlap_vs_registry": stages, "uniqueness_gate": uniqueness_gate(stages),
            "verdict": "negative", "ok_to_submit": False}


def store(root, status):
    path = root / "registry/release_status.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(status))


def test_current_canonical_stop_blocks_packaging():
    with pytest.raises(ValueError, match="no assigned method lane"):
        require_research_packaging(ROOT)


@pytest.mark.parametrize("value", [None, False, 1, "true"])
def test_lane_requires_literal_true(tmp_path, value):
    status = status_fixture()
    status["method_lane_assigned"] = value
    store(tmp_path, status)
    with pytest.raises(ValueError, match="no assigned method lane"):
        require_research_packaging(tmp_path)


@pytest.mark.parametrize("stage", ["surface", "final"])
@pytest.mark.parametrize("key,value", [("max_overlap", .70001), ("max_abs_rho", .90001),
                                      ("max_abs_rho", None), ("max_overlap", True),
                                      ("max_overlap", -1), ("coverage_complete", "true")])
def test_all_stage_failures_block_before_packaging(tmp_path, stage, key, value):
    status = status_fixture()
    status["correlation_overlap_vs_registry"][stage][key] = value
    # Even a caller's stale passing decision cannot waive raw diagnostics.
    store(tmp_path, status)
    with pytest.raises(ValueError, match="Research packaging blocked"):
        require_research_packaging(tmp_path)


@pytest.mark.parametrize("payload", [[], None, "promote", {"policy_version": "other"},
                                      {"policy_version": POLICY_VERSION, "method_lane_assigned": True}])
def test_bad_status_fails_closed(tmp_path, payload):
    store(tmp_path, payload)
    with pytest.raises(ValueError, match="Research packaging blocked"):
        require_research_packaging(tmp_path)


def test_missing_invalid_and_inconsistent_status(tmp_path):
    with pytest.raises(ValueError, match="missing or invalid"):
        require_research_packaging(tmp_path)
    store(tmp_path, status_fixture())
    (tmp_path / "registry/release_status.json").write_text("{invalid")
    with pytest.raises(ValueError, match="missing or invalid"):
        require_research_packaging(tmp_path)
    status = status_fixture()
    status["uniqueness_gate"]["duplicate"] = True
    store(tmp_path, status)
    with pytest.raises(ValueError, match="inconsistent"):
        require_research_packaging(tmp_path)


def test_negative_efficacy_and_exact_thresholds_do_not_grant_submission(tmp_path):
    status = status_fixture()
    for stage in status["correlation_overlap_vs_registry"].values():
        stage.update(max_overlap=.70, max_abs_rho=.90)
    status["uniqueness_gate"] = uniqueness_gate(status["correlation_overlap_vs_registry"])
    store(tmp_path, status)
    require_research_packaging(tmp_path)  # A research-only negative may be packaged after uniqueness.
    permission = research_only_permissions()
    assert permission["ok_to_download_for_research"] is True
    for key in ("ok_to_submit", "ok_to_download_and_submit", "slot_approved", "organizer_acceptance_verified"):
        assert permission[key] is False


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_common_builder_does_not_create_output_after_stop(tmp_path, monkeypatch):
    builder = load_script("build_submission")
    monkeypatch.setattr(builder, "PROFILE", {"height": 4, "width": 4})
    output = tmp_path / "must-not-exist" / "candidate"
    with pytest.raises(ValueError, match="no assigned method lane"):
        builder.write_variants(np.eye(4, dtype=bool), np.ones((4, 4), bool), output, name="candidate")
    assert not output.parent.exists()


@pytest.mark.parametrize("function", ["write_validated_submission_variants", "emit_and_validate_submission"])
def test_wrappers_block_before_input_reads_or_output_writes(tmp_path, function):
    writer = load_script("submission_writer")
    with pytest.raises(ValueError, match="no assigned method lane"):
        if function == "emit_and_validate_submission":
            writer.emit_and_validate_submission(np.eye(4, dtype=bool), template_path=tmp_path / "absent",
                                               labels_path=tmp_path / "absent", outdir=tmp_path / "output",
                                               name="research", note="Research only")
        else:
            writer.write_validated_submission_variants(np.eye(4, dtype=bool), tmp_path / "absent",
                                                       tmp_path / "absent", tmp_path / "output",
                                                       "research", "Research only")
    assert not (tmp_path / "output").exists()


def test_format_pass_and_caller_promote_flags_never_become_upload_approval(tmp_path, monkeypatch):
    writer = load_script("submission_writer")
    monkeypatch.setattr(writer, "require_research_packaging", lambda root: None)
    monkeypatch.setattr(writer, "footprint_mask", lambda path: np.ones((5, 5), bool))

    class FakeDataset:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self, *args):
            return np.zeros((5, 5))

    monkeypatch.setattr(writer.rasterio, "open", lambda *a, **kw: FakeDataset())
    paths = {k: tmp_path / f"{k}.bin" for k in ("nan", "allfinite", "zip")}
    for path in paths.values():
        path.write_bytes(b"not a raster; mocked writer fixture")
    monkeypatch.setattr(writer, "write_variants", lambda *a, **kw: paths)
    monkeypatch.setattr(writer, "sha256_file", lambda path: "mocked-digest")
    report = {"ok_to_upload_format_only": True, "hard_failures": [], "sha256": "mocked-digest", "bytes": 1}
    monkeypatch.setattr(writer, "validate_submission", lambda *a, **kw: copy.deepcopy(report))
    first = writer.write_validated_submission_variants(np.eye(5), tmp_path / "template", tmp_path / "labels",
                                                      tmp_path, "research", "Research only")
    second = writer.emit_and_validate_submission(np.eye(5), template_path=tmp_path / "template",
                                                labels_path=tmp_path / "labels", outdir=tmp_path,
                                                name="research", note="Research only",
                                                gate_summary={"ok_to_submit": True, "verdict": "promote"})
    for receipt in (first, second):
        for key, value in research_only_permissions().items():
            assert receipt[key] == value
    assert not list(tmp_path.glob("*.tif"))
