"""The executive prior-art table must stay sourced and non-actionable for uploads."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_current_site():
    spec = importlib.util.spec_from_file_location("current_site", ROOT / "scripts/current_site.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_executive_site_matrix_reports_highest_claim_per_requested_site():
    rendered = load_current_site().focus_site_summary()

    for site in (
        "GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
        "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36",
    ):
        assert f"<strong>{site}</strong>" in rendered
    assert "0.2778" in rendered
    assert "USER-REPORTED · no organizer receipt" in rendered
    assert "not eligible as a unique new submission" in rendered
    assert "Do not copy or rename historical files" in rendered
    assert "88.5% of dots within 3 px of H33" in rendered
    assert "same NaN TIFF bytes as GEMSDOE24" not in rendered
    assert "exact identity with other site files not asserted" in rendered
    assert "unscored" in rendered


def test_executive_matrix_links_to_commit_pinned_owner_mirror_artifacts():
    rendered = load_current_site().focus_site_summary()
    assert "github.com/buffedlizard55-lab/GEMSDOE32/blob/" in rendered
    assert "target=\"_blank\" rel=\"noopener\"" in rendered
    assert "score-claimed zeros file" in rendered and "pinned NaN audit twin" in rendered
    assert "not a claim that the encoded bytes are identical" in rendered
    assert "ORGANIZER-CONFIRMED" not in rendered


def test_missing_focus_rows_span_exactly_the_six_remaining_columns(tmp_path):
    module = load_current_site()
    module.ROOT = tmp_path
    (tmp_path / "registry").mkdir()
    (tmp_path / "registry/focus_review.json").write_text('{"rows": []}')
    rendered = module.focus_site_summary()
    assert rendered.count('colspan="6"') == 9
    assert 'colspan="4"' not in rendered


def test_research_page_proposes_only_current_desk_hypotheses_and_marks_them_unrun():
    module = load_current_site()
    section = module.current_desk_hypotheses_section()
    assert "Cross-cutting stratigraphic-contact displacement" in section
    assert "Seasonal thermal-inertia discontinuity" in section
    assert "Post-rain optical phenology" in section
    assert "Validation status: NOT RUN" in section
    assert "No numerical HOLDOUT-DTI estimate" in section
    assert "Not viability-cleared" in section
    assert "H31-AC" in section and "XFCOH31" in section


def test_current_review_notice_distinguishes_research_download_from_submission():
    rendered = load_current_site().repo_review_notice()
    assert "Existing H31-X: research download YES; submission NO; slot approval NO" in rendered
    assert "COMPUTED counting bound, not a score" in rendered
    assert "82.34% overlap" in rendered
    assert "0.00% overlap" not in rendered
    assert "repo-review-2026-10-28-run-card.json" in rendered
    assert "No new HOLDOUT-DTI was measured" in rendered
