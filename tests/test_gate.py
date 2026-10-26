import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
import rasterio
from affine import Affine

from gemsdoe31 import gate

ROOT = Path(__file__).resolve().parents[1]
TRANSFORM = Affine(100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)


def _write(path, values):
    with rasterio.open(path, "w", driver="GTiff", width=values.shape[1], height=values.shape[0], count=1, dtype="float32",
                       crs="EPSG:32611", transform=TRANSFORM, nodata=np.nan) as dst:
        dst.write(values.astype("float32"), 1)


def _scene(tmp_path, dots):
    footprint = np.zeros(dots.shape, bool)
    footprint[2:-2, 2:-2] = True
    template = np.where(footprint, 0.0, np.nan)
    _write(tmp_path / "template.tif", template)
    return footprint


def test_block_density_counts_every_dot():
    dots = np.zeros((20, 30), bool)
    dots[1, 1] = dots[7, 12] = dots[19, 29] = True
    assert gate.block_density(dots).sum() == 3


def test_match_scores_skips_ambiguous_fragments_and_never_guesses():
    reg = [{"path": "a/x-one.tif", "variants": [], "cache_name": "1", "dot_set_sha256": "A"},
           {"path": "a/x-two.tif", "variants": [], "cache_name": "2", "dot_set_sha256": "B"},
           {"path": "a/solo.tif", "variants": ["r:b/solo-copy.tif"], "cache_name": "3", "dot_set_sha256": "C"}]
    mapping, ambiguous, unmatched = gate.match_scores(reg, [{"fragment": "x-", "score": 0.1}, {"fragment": "solo", "score": 0.2},
                                                           {"fragment": "absent", "score": 0.3}])
    assert mapping == {"3": 0.2} and ambiguous == ["x-"] and unmatched == ["absent"]


def test_a_shifted_copy_of_a_registry_raster_is_flagged_a_duplicate_and_a_distant_one_is_not(tmp_path):
    rng = np.random.default_rng(3)
    base = np.zeros((120, 140), bool)
    rr, cc = rng.integers(5, 115, 400), rng.integers(5, 135, 400)
    base[rr, cc] = True
    footprint = np.ones_like(base)
    cache = tmp_path / "cache"
    cache.mkdir()
    _write(cache / "r.tif", base.astype("float32"))
    entry = {"repo": "r", "path": "r.tif", "cache_name": "r.tif", "variants": [], "dot_set_sha256": "zz"}
    shifted = np.roll(base, 1, axis=1)             # one pixel: well inside the 3 px rule
    report = gate.uniqueness_report(shifted, [entry], cache, footprint)
    assert report["duplicates_by_overlap"] == ["r.tif"]
    other = np.zeros_like(base)
    other[rng.integers(5, 115, 400), rng.integers(5, 135, 400)] = True
    report2 = gate.uniqueness_report(other, [entry], cache, footprint)
    assert report2["identical_dot_set_in_registry"] is False


def test_gate_blocks_out_of_range_values_and_rejects_long_notes(tmp_path):
    dots = np.zeros((30, 30), bool)
    dots[10, 10] = True
    footprint = _scene(tmp_path, dots)
    labels = np.where(footprint, 0, -1).astype("int8")
    with rasterio.open(tmp_path / "labels.tif", "w", driver="GTiff", width=30, height=30, count=1, dtype="int8",
                       crs="EPSG:32611", transform=TRANSFORM, nodata=-1) as dst:
        dst.write(labels, 1)
    values = np.where(footprint, 0.0, np.nan).astype("float32")
    values[10, 10] = 1.0000001
    _write(tmp_path / "bad.tif", values)
    (tmp_path / "reg.json").write_text(json.dumps({"rasters": []}))
    receipt = gate.run_gate(tif=tmp_path / "bad.tif", template=tmp_path / "template.tif", labels=tmp_path / "labels.tif",
                            registry_path=tmp_path / "reg.json", cache_dir=tmp_path, convention="nan-outside",
                            name="a-valid-looking-name", note="x" * 141, evidence_path=None, procedure_sha256=None, used_names=set())
    assert receipt["verdict"] == "BLOCKED"
    assert not receipt["gates"]["G2_range_0_1_no_nan_inside"]["pass"]
    assert not receipt["gates"]["G6_unique_name_and_short_note"]["pass"]
    assert receipt["submit_recommended"] is False and receipt["organizer_acceptance_verified"] is False


def test_shipped_candidate_receipts_match_the_files_and_are_never_recommended():
    build = json.loads((ROOT / "evidence/lane_candidate_build.json").read_text())
    for key in ("allfinite", "nan"):
        path = ROOT / build["files"][key]
        receipt = json.loads((path.parent / f"{build['name']}-gate-{key}.json").read_text())
        assert hashlib.sha256(path.read_bytes()).hexdigest() == receipt["sha256"]
        assert receipt["submit_recommended"] is False and receipt["verdict"] != "READY_TO_SUBMIT"
    assert len(build["note"]) <= 140
    card = json.loads((ROOT / "evidence/run_card_lane_as1.json").read_text())
    assert card["verdict"] == "negative" and card["organizer_confirmed"] is False
    with pytest.raises(KeyError):
        card["holdout_dti"]["catalogue_gap_fresh_seeds_11_15"]["score"]


def test_legacy_tool_cannot_approve_even_if_older_gates_all_pass(tmp_path, monkeypatch):
    """Its density exemptions are archival diagnostics, never current permission."""
    dots = np.zeros((30, 30), bool)
    dots[10, 10] = True
    footprint = _scene(tmp_path, dots)
    _write(tmp_path / 'candidate.tif', np.where(footprint, dots, np.nan))
    _write(tmp_path / 'labels.tif', np.zeros_like(dots, dtype=float))
    (tmp_path / 'registry.json').write_text('{"rasters": []}')
    original_gate = gate.gate

    def optimistic_legacy_checks(kind, passed, detail, hard=True):
        # Even a hypothetical pass of EVERY earlier gate must not bypass G8.
        return original_gate(kind, passed if kind == 'protocol' else True, detail, hard=hard)

    monkeypatch.setattr(gate, 'gate', optimistic_legacy_checks)
    receipt = gate.run_gate(tif=tmp_path / 'candidate.tif', template=tmp_path / 'template.tif',
                            labels=tmp_path / 'labels.tif', registry_path=tmp_path / 'registry.json',
                            cache_dir=tmp_path, convention='nan-outside', name='new-lane-name', note='research only',
                            evidence_path=None, procedure_sha256=None, used_names=set())
    assert receipt['hard_failures'] == ['G8_literal_registry_protocol']
    assert receipt['verdict'] == 'BLOCKED' and receipt['submit_recommended'] is False
