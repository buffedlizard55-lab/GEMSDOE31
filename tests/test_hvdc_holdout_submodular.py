import json
from pathlib import Path

import numpy as np
import rasterio
from affine import Affine

from gemsdoe31.holdout import (
    additive_dti_pixel_maps,
    build_spatial_folds,
    check_registry_duplicate_canary,
    fold_clean_catalogue_masks,
    make_hide_recover_draw,
    run_single_feature_leakage_canary,
)
from gemsdoe31.hvdc import (
    CLEAN_BASELINE_BANDS,
    FORBIDDEN_PREPARED_BANDS,
    bayes_prior_calibrate,
    build_fold_visible_accommodation,
)
from gemsdoe31.metric import ALPHA, BETA, dti
from gemsdoe31.raster import SHAPE
from gemsdoe31.submodular import (
    allocate_submodular_dots,
    naive_greedy_submodular_dots,
    priority_poisson_thin,
)

ROOT = Path(__file__).resolve().parents[1]


def test_celf_submodular_matches_naive_greedy_bit_for_bit():
    rng = np.random.default_rng(20261025)
    for trial in range(8):
        prob = (rng.uniform(0.0, 1.0, size=(22, 26)).astype(np.float32)) * 0.01
        prob[0, 0] = np.nan
        elig = rng.random((22, 26)) > 0.15
        celf_dots, info = allocate_submodular_dots(prob, elig, budget=16)
        naive_dots = naive_greedy_submodular_dots(prob, elig, budget=16)
        assert np.array_equal(celf_dots, naive_dots), f"CELF mismatch on trial {trial}"
        assert info["emitted_dots"] == int(naive_dots.sum())


def test_priority_poisson_thin_enforces_min_distance():
    rng = np.random.default_rng(11)
    score = rng.uniform(0.1, 1.0, size=(30, 30)).astype(np.float32)
    elig = np.ones((30, 30), dtype=bool)
    dots = priority_poisson_thin(score, elig, budget=25, min_dist_px=2.8)
    ys, xs = np.nonzero(dots)
    assert ys.size > 0
    for i in range(ys.size):
        for j in range(i + 1, ys.size):
            dist = np.hypot(ys[i] - ys[j], xs[i] - xs[j])
            assert dist >= 2.8 - 1e-6


def test_additive_dti_pixel_maps_reproduce_exact_metric_dti():
    rng = np.random.default_rng(99)
    for _ in range(5):
        pred = (rng.random((32, 36)) > 0.92).astype(np.float32)
        gt = rng.random((32, 36)) > 0.94
        tp_m, fn_m, fp_m = additive_dti_pixel_maps(pred, gt)
        ref = dti(pred, gt)
        assert abs(float(tp_m.sum()) - ref["TPw"]) < 1e-10
        assert abs(float(fn_m.sum()) - ref["FNw"]) < 1e-10
        assert abs(float(fp_m.sum()) - ref["FPw"]) < 1e-10
        den = float(tp_m.sum()) + ALPHA * float(fp_m.sum()) + BETA * float(fn_m.sum())
        assert abs((float(tp_m.sum()) / den) - ref["DTI"]) < 1e-12


def test_hide_recover_and_spatial_collar_exclude_straddling_components():
    foot = np.ones((60, 60), dtype=bool)
    cat = np.zeros((60, 60), dtype=bool)
    # Component 1 straddles Q0 (rows < 30, cols < 30) into Q1 (cols >= 30)
    cat[10, 20:45] = True
    # Component 2 sits strictly inside Q3 far from Q0
    cat[52, 50:56] = True
    # Component 3 sits inside Q2
    cat[45, 5:12] = True

    draw = make_hide_recover_draw(cat, foot, seed=101, hide_frac=0.5)
    assert np.array_equal(draw.visible | draw.hidden, cat)
    assert not (draw.visible & draw.hidden).any()

    folds = build_spatial_folds(foot, collar_m=1500.0, cell_m=100.0)
    masks = fold_clean_catalogue_masks(cat, folds[0])
    # Component 1 touches Q0 so its ENTIRE trace (including cols 30..44) must be excluded!
    assert not masks["train_pos"][10, 44]
    assert masks["train_pos"][52, 52]


def test_leakage_and_duplicate_canaries_flag_violations(tmp_path):
    rng = np.random.default_rng(5)
    hidden = np.zeros(2000, dtype=bool)
    hidden[:200] = True
    visible = np.zeros(2000, dtype=bool)
    d_vis = np.full(2000, 10.0, dtype=np.float32)

    clean_feat = rng.normal(0.0, 1.0, size=2000).astype(np.float32)
    leaked_feat = hidden.astype(np.float32) + rng.normal(0.0, 0.05, size=2000).astype(np.float32)
    mat = np.vstack([clean_feat, leaked_feat])

    rep = run_single_feature_leakage_canary(
        mat, ["clean", "leaked"], hidden, visible, d_vis, seed=1
    )
    assert rep["passed"] is False
    assert rep["flagged_features"] == ["leaked"]

    # Duplicate canary check on a synthetic 20x20 GeoTIFF
    reg_tif = tmp_path / "reg.tif"
    foot = np.ones((20, 20), dtype=bool)
    dots = np.zeros((20, 20), dtype=bool)
    dots[5, 5:15] = True
    with rasterio.open(
        reg_tif,
        "w",
        driver="GTiff",
        height=20,
        width=20,
        count=1,
        dtype="float32",
        crs="EPSG:32611",
        transform=Affine(100.0, 0.0, 0.0, 0.0, -100.0, 2000.0),
    ) as dst:
        dst.write(dots.astype(np.float32), 1)

    dup_bad = check_registry_duplicate_canary(dots.astype(np.float32), dots, foot, [reg_tif])
    assert dup_bad["passed"] is False
    orth = np.zeros((20, 20), dtype=bool)
    orth[18, 2:12] = True
    dup_ok = check_registry_duplicate_canary(orth.astype(np.float32), orth, foot, [reg_tif])
    assert dup_ok["passed"] is True


def test_hvdc_forbidden_bands_and_bayes_calibration():
    assert FORBIDDEN_PREPARED_BANDS.isdisjoint(set(CLEAN_BASELINE_BANDS))
    p_sub = np.array([0.2, 0.5, 0.8], dtype=np.float32)
    p_cal = bayes_prior_calibrate(p_sub, pi_subsample=0.5, pi_true=0.01)
    assert np.all(np.diff(p_cal) > 0)
    # At p_sub = 0.5 and pi_sub = 0.5, calibrated probability must equal pi_true = 0.01 exactly!
    assert abs(float(p_cal[1]) - 0.01) < 1e-6


def test_fold_visible_accommodation_zeros_near_visible_collar():
    # Lightweight synthetic test on full competition grid dimensions using sparse 2-segment trace
    foot = np.zeros(SHAPE, dtype=bool)
    foot[100:160, 100:160] = True
    vis = np.zeros(SHAPE, dtype=bool)
    vis[120, 110:122] = True
    vis[122, 128:140] = True
    n_foot = int(foot.sum())
    up = np.full(n_foot, 0.5, dtype=np.float32)
    tx = np.ones(n_foot, dtype=np.float32)
    ty = np.zeros(n_foot, dtype=np.float32)

    acc, d_vis = build_fold_visible_accommodation(vis, foot, up, tx, ty)
    assert acc.shape == (3, n_foot)
    near = d_vis[foot] <= 2.0
    assert np.all(acc[:, near] == 0.0)
    assert float(acc[1].max()) > 0.0  # relay bridge active in the step-over gap


def test_committed_hvdc_submission_and_experiment_evidence():
    res = json.loads((ROOT / "evidence/hvdc/hvdc_experiment_results.json").read_text())
    assert res["leakage_canary_passed"] is True
    assert res["leakage_canary_max_symmetric_auc"] <= 0.90
    assert res["experiments_executed"] == 3
    assert res["elapsed_minutes"] <= 120.0
    exp1 = res["experiments"]["EXP-1"]
    exp3 = res["experiments"]["EXP-3"]
    assert exp3["screen_mean_holdout_dti"] > exp1["screen_mean_holdout_dti"] + 0.005
    assert exp3["confirm_mean_holdout_dti"] > exp1["confirm_mean_holdout_dti"]
    assert exp3["duplicate_canary"]["passed"] is True

    receipt = json.loads((ROOT / "evidence/hvdc/submission_validation_receipt.json").read_text())
    assert receipt["ok_to_download_and_submit"] is True
    assert all(receipt["strict_checks"].values())
