import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import zipfile

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("verify_current_run", ROOT / "scripts/verify_current_run.py")
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


@pytest.fixture
def isolated_run(tmp_path):
    if not (ROOT / "data/labels.tif").exists():
        pytest.skip("CI restores the two pinned small inputs before this test; run verifier --restore-small-inputs")
    for directory in ("registry", "docs/downloads", "vendor/gems57", "knowledge", "src/gemsdoe31"):
        shutil.copytree(ROOT / directory, tmp_path / directory)
    shutil.copytree(ROOT / "evidence/magrest", tmp_path / "evidence/magrest")
    shutil.copyfile(ROOT / "evidence/sibling_inventory_20261025.json", tmp_path / "evidence/sibling_inventory_20261025.json")
    (tmp_path / "data").mkdir()
    for name in ("labels.tif", "sample_submission.tif"):
        shutil.copyfile(ROOT / "data" / name, tmp_path / "data" / name)
    control = tmp_path / ".cache/registry-scope"
    control.mkdir(parents=True)
    shutil.copyfile(ROOT / ".cache/registry-scope/registered-lattice.tif", control / "registered-lattice.tif")
    return tmp_path


def test_current_artifact_verifies_negative_decision_without_human_input(isolated_run):
    result = verifier.verify(isolated_run)
    assert result["ok_to_download_for_research"] is True
    assert result["ok_to_submit"] is False
    assert result["checks"]["scientific_screen_pass"] is False
    assert result["checks"]["registry_literal_rule_pass"] is False
    assert result["registry_counterexample_overlap"] == 1.0
    assert result["checks"]["exact_pooled_dti_and_ci_reproduced"] is True
    assert result["positive_pixels"] == 37654


def test_changed_tiff_bytes_fail_before_a_download_is_cleared(isolated_run):
    card = json.loads((isolated_run / "registry/current_run.json").read_text())
    path = isolated_run / card["file"]
    # Appending bytes leaves a readable TIFF but invalidates the exact-file receipt.
    with path.open("ab") as out:
        out.write(b"not-the-reviewed-file")
    with pytest.raises(ValueError, match="bytes changed"):
        verifier.verify(isolated_run)


def test_unsupported_approval_cannot_be_enabled_by_a_status_flag(isolated_run):
    card = json.loads((isolated_run / "registry/current_run.json").read_text())
    card["ok_to_submit"] = True
    for name in ("registry/current_run.json", "evidence/magrest/run_card.json", "docs/downloads/magrest-run-card.json"):
        (isolated_run / name).write_text(json.dumps(card))
    with pytest.raises(ValueError, match="unsupported promotion"):
        verifier.verify(isolated_run)


def test_extra_zip_member_is_rejected(isolated_run):
    card = json.loads((isolated_run / "registry/current_run.json").read_text())
    with zipfile.ZipFile(isolated_run / card["zip_file"], "a") as z:
        z.writestr("extra.json", "{}")
    with pytest.raises(ValueError, match="one-TIFF"):
        verifier.verify(isolated_run)


def test_registry_flags_do_not_override_the_literal_overlap_limit(isolated_run):
    path = isolated_run / "evidence/magrest/independent_novelty_recheck.json"
    evidence = json.loads(path.read_text())
    arm = evidence["all_final_dots_recheck"]["arms"]["magrest_concordant"]
    row = arm["comparisons"][0]
    row["within_3px"] = row["candidate_support_pixels"]
    row["overlap_within_3px"] = 1.0
    arm["pass_"], arm["duplicate"] = True, False
    path.write_text(json.dumps(evidence))
    with pytest.raises(ValueError, match="duplicate STOP"):
        verifier.verify(isolated_run)


def test_a_label_copy_triggers_the_single_feature_leakage_canary():
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from run_magrest import canaries
    from gems57.grid import Grid
    fp = np.ones((20, 20), bool)
    truth = np.zeros_like(fp)
    truth[3:8, 3:8] = True
    visible = np.zeros_like(fp)
    grid = Grid(fp, truth, None, None, 20, 20)
    fold = dict(truth=truth, region=fp, masked_known=visible, fold=0, name="test")
    result = canaries([truth.ravel().astype(float)], ["deliberate_label_leak"], np.arange(fp.size), [fold], grid)
    assert result["pass_"] is False
    assert result["rows"][0]["auc"] == 1.0


def test_complete_normalized_owner_prompt_is_embedded_in_readme():
    receipt = json.loads((ROOT / "evidence/owner_prompt_preservation.json").read_text())
    copy = (ROOT / receipt["copy"]).read_text()
    body = copy[copy.index("Review the repo."):].strip()
    assert hashlib.sha256(body.encode()).hexdigest() == receipt["normalized_body_sha256"]
    readme = (ROOT / "README.md").read_text()
    section = readme[readme.index("## Complete owner prompt"):]
    embedded = section[section.index("Review the repo."):section.rindex("</details>")].strip()
    assert body == embedded
    for requirement in ("PARALLEL-RUN PROTOCOL", "MUST GENERATE A UNIQUE TIF", "GEMSDOE92", "Pass 3:"):
        assert requirement in body


def test_literal_shared_registry_stop_cannot_be_waived_by_flags(isolated_run):
    card = json.loads((isolated_run / "registry/current_run.json").read_text())
    card["registry"]["literal_rule_pass"] = True
    card["registry"]["final"]["pass_"] = True
    for name in ("registry/current_run.json", "evidence/magrest/run_card.json", "docs/downloads/magrest-run-card.json"):
        (isolated_run / name).write_text(json.dumps(card))
    with pytest.raises(ValueError, match="contradict the literal overlap STOP"):
        verifier.verify(isolated_run)


def test_recorded_duplicate_stop_prevents_even_feature_stage_reexecution():
    import subprocess
    import sys
    result = subprocess.run([sys.executable, str(ROOT / "scripts/run_magrest.py"), "--stage", "features"],
                            capture_output=True, text=True, cwd=ROOT)
    assert result.returncode != 0
    assert "STOP: registered lattice overlap" in result.stderr
