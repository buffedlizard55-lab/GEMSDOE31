"""Public wording must not turn a subset pass into protocol approval."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_h31e_component_exposes_binding_stop_and_no_portal_acceptance():
    rendered = load_script('current_site').scgp_download_and_gates()
    assert 'DO NOT SUBMIT · REGISTRY STOP' in rendered
    assert 'RESEARCH DOWNLOAD ONLY' in rendered
    assert 'SUBSET ONLY — NOT UNIQUENESS APPROVAL' in rendered
    assert 'Portal Format' not in rendered
    assert 'Artifact Name (not uniqueness approval)' in rendered


def test_h31t_component_exposes_binding_stop_and_no_portal_acceptance():
    rendered = load_script('current_site').h31t_download_and_gates()
    assert 'DO NOT SUBMIT · REGISTRY STOP' in rendered
    assert 'RESEARCH DOWNLOAD ONLY' in rendered
    assert 'SUBSET ONLY — NOT UNIQUENESS APPROVAL' in rendered
    assert 'Portal Format' not in rendered
    assert 'Artifact Name (not uniqueness approval)' in rendered
    assert '83fbc267a754d5d58c950baddc92891b53a4cad2c2f90a114f1c2177b4567298' in rendered


def test_archived_readme_generator_cannot_replace_active_release():
    before = (ROOT / 'README.md').read_bytes()
    with pytest.raises(ValueError, match='cannot overwrite'):
        load_script('update_readme').content()
    assert (ROOT / 'README.md').read_bytes() == before


def test_readme_leads_with_binding_stop_before_standing_owner_prompt():
    lead = (ROOT / 'README.md').read_text().split('## Read first every session')[0]
    assert 'No current artifact is approved' in lead
    assert 'No human sign-off can override' in lead
    assert '22-SUBMISSION UNIQUENESS' not in lead


def test_historical_pages_do_not_promote_stale_rbu31_status():
    build_site = load_script('build_site')
    rendered = build_site.shell('' , 'Validation', '', 'Validation', '', '<section>old experiment</section>')
    assert 'Current protocol decision: no file is approved for submission' in rendered
    assert 'active review register' in rendered
    assert 'data/current-review.json' in rendered
    assert 'knowledge/2026-10-26_protocol_review_9883b598.md' not in rendered
    assert 'Newest candidate: RBU31' not in rendered
