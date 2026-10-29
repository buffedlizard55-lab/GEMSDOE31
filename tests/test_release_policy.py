"""Literal protocol regressions: missing evidence and prior approvals cannot waive STOP."""
import importlib.util
import json
from pathlib import Path

import pytest

from gemsdoe31.release_policy import selector_permission, uniqueness_gate

ROOT = Path(__file__).resolve().parents[1]


def stages(rho=.9, overlap=.7):
    return {s: dict(max_abs_rho=rho, max_overlap=overlap, coverage_complete=True)
            for s in ('surface', 'final')}


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / f'{name}.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_thresholds_are_strict_and_both_stages_binding():
    assert uniqueness_gate(stages())['pass_']
    for stage in ('surface', 'final'):
        for key, value in (('max_abs_rho', .90001), ('max_overlap', .70001)):
            s = stages()
            s[stage][key] = value
            g = uniqueness_gate(s)
            assert g['duplicate'] and not g['pass_']


@pytest.mark.parametrize('value', [None, float('nan'), float('inf'), -.1, 1.1, True, '0.2'])
def test_unknown_invalid_and_nonfinite_fail_closed(value):
    s = stages()
    s['surface']['max_abs_rho'] = value
    assert not uniqueness_gate(s)['pass_']


def test_partial_scope_cannot_be_approved_but_can_prove_stop():
    s = stages()
    s['final'].update(coverage_complete=False, max_overlap=1.)
    g = uniqueness_gate(s)
    assert g['duplicate'] and not g['pass_']
    assert not uniqueness_gate({'final': s['final']})['pass_']
    assert not selector_permission(uniqueness=g, scientific_gates={'projection': True},
                                   selector_authorized=True, weekly_cap_verified=True)


def test_no_slot_without_cap_and_separate_authorization():
    args = dict(uniqueness=uniqueness_gate(stages()), scientific_gates={k: True for k in ('format', 'canary', 'same_run_best',
                                                     'fresh_confirmation', 'discovery_proxy', 'provenance')},
                selector_authorized=True, weekly_cap_verified=True)
    assert selector_permission(**args)
    for key in ('selector_authorized', 'weekly_cap_verified'):
        assert not selector_permission(**(args | {key: False}))
    assert not selector_permission(**(args | {'scientific_gates': {}}))
    assert not selector_permission(**(args | {'scientific_gates': {'efficacy': 'true'}}))


@pytest.mark.parametrize('malformed', [None, [], 'surface', 1])
def test_malformed_uniqueness_stages_fail_closed(malformed):
    assert not uniqueness_gate(malformed)['pass_']
    assert not uniqueness_gate({'surface': malformed, 'final': stages()['final']})['pass_']


def test_selector_rejects_contradictory_or_missing_failures():
    gates = {k: True for k in ('format', 'canary', 'same_run_best',
                               'fresh_confirmation', 'discovery_proxy', 'provenance')}
    for uniqueness in (None, {}, {'pass_': True, 'duplicate': False},
                       {'pass_': True, 'duplicate': False, 'failures': ['duplicate STOP']}):
        assert not selector_permission(uniqueness=uniqueness, scientific_gates=gates,
                                       selector_authorized=True, weekly_cap_verified=True)
    assert not selector_permission(uniqueness=uniqueness_gate(stages()), scientific_gates=None,
                                   selector_authorized=True, weekly_cap_verified=True)


def test_current_decision_and_ui_deny_prior_selector_approvals():
    dec = json.loads((ROOT / 'registry/selector_decision_20261026.json').read_text())
    assert dec['primary_submission'] is None and not dec['promoted_lanes']
    site = load_script('current_site')
    card = json.loads((ROOT / 'registry/current_run.json').read_text())
    rendered = '\n'.join((*site.overview(card), site.executive(card)))
    assert 'DO NOT SUBMIT' in rendered and 'protocol-review-run-card.json' in rendered
    for stale in ('SUBMIT THIS FILE', 'OK TO DOWNLOAD AND SUBMIT', 'OK TO SUBMIT',
                  'One file is cleared', 'Exactly one file'):
        assert stale not in rendered.replace("NOT OK TO SUBMIT", "DO NOT SUBMIT")
    assert 'Unavailable' in rendered


def test_protocol_card_and_counting_bound():
    card = json.loads((ROOT / 'evidence/review_9883b598/run_card.json').read_text())
    assert card['uniqueness_gate']['duplicate'] and card['verdict'] == 'negative'
    assert card['ok_to_submit'] is False and card['new_tif_generated'] is False
    assert card['validator']['hard_failures'] == []
    assert card['holdout_provenance'].startswith('CITED')
    assert 0 < len(card['note']) <= 140
    coverage = card['lattice_coverage']
    assert coverage['minimum_overlap_any_same_budget'] == pytest.approx(
        1 - coverage['outside_3px_halo'] / coverage['candidate_dots'])
    assert coverage['minimum_overlap_any_same_budget'] > .7
    assert card['leaderboard_estimate'] is None


def test_disabled_selector_cannot_reissue_approval():
    selector = load_script('selector_audit')
    path = ROOT / 'registry/selector_decision_20261026.json'
    before = path.read_bytes()
    with pytest.raises(SystemExit, match='STOP'):
        selector.main()
    assert path.read_bytes() == before


def test_fresh_review_reproduces_witness_and_rejects_tamper(monkeypatch):
    if not (ROOT / 'data/sample_submission.tif').exists():
        pytest.skip('restore small inputs to exercise real-file witness')
    verifier = load_script('verify_protocol_review')
    fresh = verifier.verify()
    saved = json.loads((ROOT / 'evidence/review_9883b598/run_card.json').read_text())
    assert fresh == saved
    original = verifier.sha256_file
    monkeypatch.setattr(verifier, 'sha256_file', lambda p: 'tampered' if 'h31x-piedmont' in str(p) else original(p))
    with pytest.raises(ValueError, match='H31-X file hash mismatch'):
        verifier.verify()
