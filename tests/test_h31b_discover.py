from __future__ import annotations

import numpy as np

from gemsdoe31.h31b_discover import (
    check_uniqueness_against_registry,
    compute_hessian_crest,
    local_survey_invariant_score,
    norm_rank,
    poisson_disk_select,
    run_single_feature_leakage_canary,
)


def test_norm_rank_handles_nan_and_invert() -> None:
    arr = np.array([[1.0, 2.0, np.nan], [4.0, 5.0, 0.0]], dtype=np.float32)
    mask = np.array([[True, True, True], [True, True, False]])
    r = norm_rank(arr, mask)
    assert np.isclose(r[0, 2], 0.5)
    assert np.isclose(r[1, 2], 0.5)
    assert r[0, 0] == 0.0
    assert r[1, 1] == 1.0

    r_inv = norm_rank(arr, mask, invert=True)
    assert r_inv[0, 0] == 1.0
    assert r_inv[1, 1] == 0.0


def test_compute_hessian_crest_detects_ridge() -> None:
    yy, xx = np.mgrid[0:32, 0:32]
    ridge = np.exp(-((xx - 16.0) ** 2) / 4.0).astype(np.float32)
    foot = np.ones_like(ridge, dtype=bool)
    crest = compute_hessian_crest(ridge, foot, sigma=1.0)
    assert crest[:, 16].mean() > crest[:, 4].mean()


def test_local_survey_invariant_score_eliminates_step_offset() -> None:
    rng = np.random.default_rng(42)
    raw = rng.uniform(0.3, 0.7, size=(64, 64)).astype(np.float32)
    raw[:, 32:] += 0.30
    foot = np.ones((64, 64), dtype=bool)
    loc = local_survey_invariant_score(raw, foot, sigma_px=8.0, local_weight=0.85)
    assert abs(float(loc[:, :24].mean() - loc[:, 40:].mean())) < 0.15


def test_poisson_disk_select_enforces_spacing() -> None:
    ys = np.array([10, 10, 11, 20], dtype=np.int64)
    xs = np.array([10, 11, 10, 20], dtype=np.int64)
    sel = poisson_disk_select(ys, xs, (30, 30), min_dist_px=2.85, max_dots=10)
    assert int(sel.sum()) == 2
    assert sel[10, 10] and sel[20, 20]


def test_leakage_canary_flags_perfect_feature() -> None:
    y = np.zeros((40, 40), dtype=bool)
    y[10:20, 10:20] = True
    foot = np.ones_like(y, dtype=bool)
    leaked = y.astype(np.float32)
    res_leak = run_single_feature_leakage_canary(leaked, y, foot, stride=1)
    assert res_leak["leakage_flagged"] is True
    assert res_leak["unsigned_auc"] > 0.99

    noise = np.random.default_rng(0).normal(size=y.shape).astype(np.float32)
    res_ok = run_single_feature_leakage_canary(noise, y, foot, stride=1)
    assert res_ok["leakage_flagged"] is False


def test_uniqueness_gate_detects_duplicate_and_unique() -> None:
    foot = np.ones((50, 50), dtype=bool)
    reg = np.zeros((50, 50), dtype=bool)
    reg[10, 10] = True
    reg[20, 20] = True
    reg[30, 30] = True

    dup_dots = reg.copy()
    surf = np.random.default_rng(7).uniform(size=(50, 50)).astype(np.float32)
    audit_dup = check_uniqueness_against_registry(surf, dup_dots, foot, {"reg": reg}, subsample_stride=1)
    assert audit_dup.passed_dot_overlap_gate is False
    assert audit_dup.passed_all is False

    uniq_dots = np.zeros((50, 50), dtype=bool)
    uniq_dots[10, 10] = True
    uniq_dots[40, 40] = True
    uniq_dots[45, 45] = True
    audit_uniq = check_uniqueness_against_registry(surf, uniq_dots, foot, {"reg": reg}, subsample_stride=1)
    assert audit_uniq.passed_dot_overlap_gate is True
    assert audit_uniq.passed_all is True
