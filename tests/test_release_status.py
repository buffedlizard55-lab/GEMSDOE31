"""Current release status cannot drift from bytes, permissions or the public feed."""
import importlib.util
import itertools
import json
from pathlib import Path

import pytest

from gemsdoe31.release_policy import overlap_budget_preflight

ROOT = Path(__file__).resolve().parents[1]


def test_bound_matches_exhaustive_small_footprints():
    # Includes strict equality at 70%, empty sets, zero/full halo and all budgets.
    for cells in range(1, 11):
        for outside in range(cells + 1):
            halo = set(range(outside, cells))
            for budget in range(cells + 1):
                report = overlap_budget_preflight(footprint_pixels=cells,
                                                  outside_halo_pixels=outside, candidate_dots=budget)
                exact = min(len(set(s) & halo) for s in itertools.combinations(range(cells), budget))
                assert report['minimum_overlap_pixels'] == exact
                assert report['forced_duplicate_stop'] == (budget > 0 and exact * 10 > budget * 7)
                assert report['uniqueness_pass'] is False


@pytest.mark.parametrize('counts', [(0, 0, 0), (10, 11, 1), (10, 1, 11), (10, -1, 1),
                                    (10, 1, True), (10, 1, 1.0), (10, 1, None)])
def test_bound_rejects_invalid_counts(counts):
    with pytest.raises(ValueError):
        overlap_budget_preflight(footprint_pixels=counts[0], outside_halo_pixels=counts[1], candidate_dots=counts[2])


def test_bound_boundary_and_no_inference_of_global_impossibility():
    assert not overlap_budget_preflight(footprint_pixels=10, outside_halo_pixels=3,
                                        candidate_dots=10)['forced_duplicate_stop']
    r = overlap_budget_preflight(footprint_pixels=5167373, outside_halo_pixels=6649, candidate_dots=37654)
    assert r['minimum_overlap_pixels'] == 31005 and r['forced_duplicate_stop']
    assert not overlap_budget_preflight(footprint_pixels=5167373, outside_halo_pixels=6649,
                                        candidate_dots=100)['forced_duplicate_stop']


def test_current_status_matches_registers_and_public_copy():
    status = json.loads((ROOT / 'registry/release_status.json').read_text())
    public = json.loads((ROOT / 'docs/downloads/current-release-status.json').read_text())
    review = json.loads((ROOT / 'registry/review_passes.json').read_text())
    assert status == public
    assert review['current_release_status'] == 'registry/release_status.json'
    assert review['release_decision'] == 'DO NOT SUBMIT — literal registry STOP'
    assert status['verdict'] == 'negative' and status['ok_to_submit'] is False
    assert status['slot_approved'] is False and status['leaderboard_estimate'] is None
    assert status['holdout_provenance'].startswith('CITED')
    assert status['validator']['hard_failures'] == []
    assert 0 < len(status['note']) <= 140


def test_status_build_rechecks_bytes_and_rejects_stale_register(monkeypatch):
    if not (ROOT / 'data/sample_submission.tif').exists():
        pytest.skip('restore small inputs for exact-byte integration')
    spec = importlib.util.spec_from_file_location('build_release_status', ROOT / 'scripts/build_release_status.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    status = json.loads((ROOT / 'registry/release_status.json').read_text())
    assert m.build() == status
    read_text = Path.read_text

    def stale(path, *args, **kwargs):
        text = read_text(path, *args, **kwargs)
        if path == ROOT / 'registry/review_passes.json':
            r = json.loads(text)
            r['release_decision'] = 'SUBMIT H31-X'
            return json.dumps(r)
        return text

    monkeypatch.setattr(Path, 'read_text', stale)
    with pytest.raises(ValueError, match='permission registers conflict'):
        m.build()


def test_public_feed_uses_current_status_not_historical_magrest():
    feed = json.loads((ROOT / 'docs/feed.json').read_text())
    status = json.loads((ROOT / 'registry/release_status.json').read_text())
    assert feed['current_release_status'] == status
    assert feed['current_download']['raster_sha256'] == status['raster_sha256']
    assert feed['current_download']['ok_to_submit'] is False
    assert feed['historical_magrest_download']['name'] != feed['current_download']['name']
    assert feed['current_download']['holdout_provenance'].startswith('CITED')
