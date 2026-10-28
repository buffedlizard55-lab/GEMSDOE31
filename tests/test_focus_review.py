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
        assert r['sgmc_proxy_provenance'].startswith('CITED historical SGMC proxy')
        assert r['sgmc_proxy_dti'] is None or r['sgmc_proxy_dti']['withheld_positives_total'] > 0
        assert len(r['sha256']) == 64
        assert '/blob/' in r['source_url']
        assert r['historical_file'].endswith('.tif')


def test_sgmc_proxy_not_mislabeled_as_hide_and_recover_holdout():
    text = review.section()
    assert 'COMPUTED SGMC-PROXY-DTI' in text
    assert 'not a hide-and-recover holdout' in text
    assert 'HOLDOUT-DTI' not in text
    assert 'No TIFF was generated in this review' in text
    assert text.count('No — prior submission. DO NOT SUBMIT.') == 9
    assert 'Estimate: unavailable' in text


def test_missing_evidence_fails_closed(tmp_path):
    with pytest.raises(FileNotFoundError):
        review.build(tmp_path)
