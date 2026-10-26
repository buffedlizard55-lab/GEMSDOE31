from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "vendor"), str(ROOT / "scripts")]

from gemsdoe31.submodular_emit import submodular_dti_emit  # noqa: E402
from gemsdoe31.tgtd_features import (  # noqa: E402
    FORBIDDEN_WELLSPRING_COLS,
    compute_harmonic_tensor,
)
from verify_h31j import EXPECTED_DOTS, EXPECTED_SUB_NAME, verify_h31j  # noqa: E402


def test_h31j_end_to_end_artifact_and_gate_integrity():
    """Verify GeoTIFFs, single-file ZIPs, [0, 1] range, leakage canary, uniqueness, and holdout CIs."""
    summary = verify_h31j(ROOT)
    assert summary["ok"] is True
    assert summary["submission_name"] == EXPECTED_SUB_NAME
    assert summary["dots"] == EXPECTED_DOTS
    assert summary["slot_approved"] is False
    assert summary["screen_dti"] > 0.085
    assert summary["confirm_dti"] > 0.075
    assert summary["sgmc_all_dti"] > 0.100
    assert summary["sgmc_piedmont_dti"] > 0.140


def test_pedersen_rasmussen_tabular_vs_3d_caldera_discrimination():
    """Verify T_2D -> 1 on a 2-D tabular vertical fault step and T_2D -> 0 over a 3-D point/caldera source."""
    n = 128
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    fp = np.ones((n, n), dtype=bool)
    z0 = 8.0

    # 1. Pure 2-D infinite N-S planar fault contact at x = 64 (invariant along y)
    fault_2d = np.arctan2(xx - 64.0, z0).astype(np.float32)
    res_2d = compute_harmonic_tensor(fault_2d, fp, upward_px=2.0)
    # Interior along fault trace (avoiding periodic wraparound boundary)
    trace_t2d = float(np.median(res_2d["t2d"][32:96, 63:66]))
    assert trace_t2d > 0.97, f"Expected T_2D ~ 1 on 2-D planar fault step, got {trace_t2d}"

    # 2. Axisymmetric 3-D buried point source / circular pluton centered at (64, 64)
    r3 = np.sqrt((xx - 64.0) ** 2 + (yy - 64.0) ** 2 + z0**2)
    pluton_3d = (100.0 / r3).astype(np.float32)
    res_3d = compute_harmonic_tensor(pluton_3d, fp, upward_px=2.0)
    apex_t2d = float(res_3d["t2d"][64, 64])
    assert apex_t2d < 0.05, f"Expected T_2D ~ 0 at 3-D axisymmetric pluton apex, got {apex_t2d}"


def test_submodular_emit_scales_pool_and_respects_range():
    """Regression test: max_pool smaller than n_dots*24 must never silently truncate full-budget emission."""
    rng = np.random.default_rng(31)
    prob = rng.uniform(0.01, 0.99, size=(120, 120)).astype(np.float32)
    allowed = np.ones((120, 120), dtype=bool)
    allowed[:4, :] = False
    target_dots = 450
    # Pass tiny max_pool=100; effective_pool = max(100, 450*24) = 10,800 must still emit all 450 dots
    dots = submodular_dti_emit(prob, allowed, n_dots=target_dots, min_dist_px=2.8, max_pool=100)
    assert dots.dtype == np.bool_
    assert int(dots.sum()) == target_dots
    assert not bool((dots & ~allowed).any())
    as_f32 = dots.astype(np.float32)
    assert float(as_f32.min()) == 0.0 and float(as_f32.max()) == 1.0


def test_tgtd_anti_leakage_column_exclusion():
    """Ensure `dist_known_fault_px` is explicitly forbidden in GDR #1391 wellspring ingestion."""
    assert "dist_known_fault_px" in FORBIDDEN_WELLSPRING_COLS
    card = json.loads((ROOT / "evidence/h31j/run_card.json").read_text())
    assert card["leakage_canary_summary"]["dist_known_fault_px_loaded"] is False
    assert card["leakage_canary_summary"]["max_single_feature_symmetric_auc"] <= 0.90


def test_h31j_readme_and_submission_registry_hashes_match_disk():
    """Ensure README.md and registry/submissions.json match exact served H31-J GeoTIFF/ZIP hashes and keep slot_approved=False."""
    card = json.loads((ROOT / "evidence/h31j/run_card.json").read_text())
    art = card["artifacts"]
    readme = (ROOT / "README.md").read_text()
    for key in (
        "primary_zeros_sha256",
        "primary_zeros_zip_sha256",
        "companion_nan_sha256",
        "companion_nan_zip_sha256",
    ):
        assert art[key] in readme, f"README.md missing exact SHA-256 for {key}: {art[key]}"
    assert card["submission_name"] in readme
    assert card["portal_note"] in readme

    reg = json.loads((ROOT / "registry/submissions.json").read_text())
    entry = next(f for f in reg["files"] if f["id"] == "candidate-h31j-tgtd-submod")
    assert entry["slot_approved"] is False
    assert entry["name"] == card["submission_name"]
    assert entry["sha256_allfinite"] == art["primary_zeros_sha256"]
    assert entry["sha256_nan"] == art["companion_nan_sha256"]
    assert entry["sha256_zip"] == art["primary_zeros_zip_sha256"]
    assert entry["sha256_zip_nan"] == art["companion_nan_zip_sha256"]

