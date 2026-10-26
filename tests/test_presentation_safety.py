"""Public wording must not turn a subset pass into protocol approval."""
from collections import Counter
from html.parser import HTMLParser
import importlib.util
import json
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


def test_homepage_uses_active_run_instead_of_stale_rbu31_card():
    site = load_script("current_site")
    card = json.loads((ROOT / "registry/current_run.json").read_text())
    hero, body = site.overview(card)
    rendered = hero + body

    assert card["submission_name"] in hero
    assert "RESEARCH DOWNLOAD ONLY · DO NOT SUBMIT" in hero
    assert f'href="downloads/{Path(card["file"]).name}"' in hero
    assert "newest unique candidate: RBU31" not in rendered
    assert "Download the RBU31 submission .tif" not in rendered
    assert "Historical RBU31 research artifact" in rendered
    assert "Download RBU31 research TIFF — DO NOT SUBMIT" in rendered
    assert "99.8713%" in rendered
    assert "GEMSDOE48" in rendered


class _Ids(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = Counter()

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key == "id" and value:
                self.ids[value] += 1


def test_public_run_gate_attribution_is_corrected_without_rewriting_receipts():
    site = load_script("current_site")
    card = json.loads((ROOT / "registry/current_run.json").read_text())
    messages = site.public_failed_gate_messages(card)
    corrected = messages[0]
    assert "99.8713%" in corrected
    assert "distinct full-support witness" in corrected
    assert "GEMSDOE48" in corrected
    assert "100% of primary dots within 3 px of a registered spacing-5 lattice" not in corrected

    rendered = site.executive(card)
    assert "99.8713%" in rendered
    assert "GEMSDOE48" in rendered
    assert "100% of primary dots within 3 px of a registered spacing-5 lattice" not in rendered

    frozen = json.loads((ROOT / "evidence/magrest/run_card.json").read_text())
    download = json.loads((ROOT / "docs/downloads/magrest-run-card.json").read_text())
    assert card == frozen == download
    register = json.loads((ROOT / "registry/submissions.json").read_text())
    active = next(row for row in register["files"] if row["id"] == "magrest-current-negative")
    assert "99.8713%" in active["why_not_slot_approved"]
    assert "GEMSDOE48" in active["why_not_slot_approved"]
    assert "100% of primary dots within 3 px of a registered spacing-5 lattice" not in active["why_not_slot_approved"]


def test_h3_holdout_cells_render_without_template_fragments_or_duplicate_ids():
    site = load_script("current_site")
    card = json.loads((ROOT / "registry/current_run.json").read_text())
    hero, body = site.overview(card)
    rendered = hero + body
    parser = _Ids()
    parser.feed(rendered)

    assert "if dti_sgmc is not None" not in rendered
    assert "if dti_gap is not None" not in rendered
    assert parser.ids["h3-download"] == 1
    assert parser.ids["h3-heading"] == 1
    assert "HOLDOUT-DTI n/a" not in rendered


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
