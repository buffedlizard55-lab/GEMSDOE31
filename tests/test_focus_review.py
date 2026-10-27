"""Publication must not turn historical evidence into an upload permission or forecast."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('focus_review', ROOT / 'scripts/focus_review.py')
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


def test_nine_sites_not_a_selector():
    d = review.build()
    assert len(d['rows']) == 9
    assert len({r['site'] for r in d['rows']}) == 9
    assert d['best_reported_site'] == 'GEMSDOE32'
    assert d['selection_performed'] is False
    for r in d['rows']:
        assert r['ok_to_submit'] is False
        assert r['unique_new_submission'] is False
        assert r['estimated_leaderboard_score'] is None
        assert len(r['sha256']) == 64
        assert '/blob/' in r['source_url']
        assert r['historical_file'].endswith('.tif')


def test_proxy_not_passed_off_as_fresh_holdout():
    text = review.section()
    assert 'not fresh hide-and-recover validation' in text
    assert 'No TIFF was generated in this review' in text
    assert text.count('No — prior submission. DO NOT SUBMIT.') == 9
    assert 'Estimate: unavailable' in text


def test_missing_evidence_fails_closed(tmp_path):
    with pytest.raises(FileNotFoundError):
        review.build(tmp_path)
