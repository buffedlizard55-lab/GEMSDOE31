"""Regression tests for scripts/verify_focus_sites.py overlap and chance-adjustment logic."""

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import verify_focus_sites as vfs  # noqa: E402
from gemsdoe31.gate import footprint_blocks  # noqa: E402


def _dots(shape, coords):
    arr = np.zeros(shape, dtype=bool)
    for r, c in coords:
        arr[r, c] = True
    return arr


def test_overlap_counts_only_dots_within_three_pixels():
    shape = (60, 60)
    a = {"dots": _dots(shape, [(10, 10), (30, 30), (50, 50)])}
    b = {"dots": _dots(shape, [(10, 13), (40, 40)])}  # (10,10)->(10,13) is exactly 3 px away
    footprint = np.ones(shape, dtype=bool)
    domain = footprint_blocks(footprint)
    points = vfs.chance_points(footprint)
    out = vfs.pairwise("A", a, "B", b, domain, points)
    assert abs(out["overlap_3px_a_within_b"] - 1 / 3) < 1e-5
    assert out["duplicate_by_overlap_rule"] is False


def test_identical_rasters_are_duplicates_and_chance_adjustment_is_bounded():
    shape = (40, 40)
    coords = [(r, c) for r in range(0, 40, 2) for c in range(0, 40, 2)]
    a = {"dots": _dots(shape, coords)}
    footprint = np.ones(shape, dtype=bool)
    domain = footprint_blocks(footprint)
    points = vfs.chance_points(footprint)
    out = vfs.pairwise("A", a, "A2", a, domain, points)
    assert out["overlap_3px_a_within_b"] == 1.0
    assert out["duplicate_by_raw_overlap_conservative"] is True
    assert out["duplicate_by_rank_rule"] is True
    assert 0.0 <= out["chance_overlap_3px_of_b"] <= 1.0
    assert out["adjusted_overlap_3px"] <= 1.0


def test_pinned_commit_url_parsing():
    url = "https://github.com/owner/repo/blob/abc123/docs/downloads/x.tif"
    assert vfs.published_path(url, "abc123") == "docs/downloads/x.tif"
    try:
        vfs.published_path(url, "other")
    except ValueError:
        return
    raise AssertionError("mismatched pinned ref must be rejected")
