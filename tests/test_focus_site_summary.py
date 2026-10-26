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
    assert "Do not copy or rename them" in rendered
    assert "88.5% of dots within 3 px of H33" in rendered
    assert "same NaN TIFF bytes as GEMSDOE24" not in rendered
    assert "exact identity with other site files not asserted" in rendered
    assert "unscored" in rendered


def test_executive_matrix_links_to_commit_pinned_owner_mirror_artifacts():
    rendered = load_current_site().focus_site_summary()
    assert "github.com/buffedlizard55-lab/GEMSDOE32/blob/" in rendered
    assert "target=\"_blank\" rel=\"noopener\"" in rendered
    assert "ORGANIZER-CONFIRMED" not in rendered
