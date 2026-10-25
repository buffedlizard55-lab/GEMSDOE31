import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio
from affine import Affine

from gemsdoe31.metric import CELL_M, RADIUS_M, _offsets
from gemsdoe31.raster import connected_components
from gemsdoe31.scgp_features import (
    BANNED_PREPARED_BANDS,
    STATIC_FEATURE_NAMES,
    cross_gradient_concordance,
    exact_two_component_distances_m,
    fft_upward_continue,
    nearest_finite_fill,
    robust_z,
    sanitize_nodata,
)
from gemsdoe31.submodular_emit import (
    check_duplicate_canary,
    ridge_sharpened_weight,
    submodular_dti_emit,
)

ROOT = Path(__file__).resolve().parents[1]


def test_static_feature_names_exclude_banned_leakage_and_proxy_bands():
    for banned in BANNED_PREPARED_BANDS:
        assert banned not in STATIC_FEATURE_NAMES


def test_cross_gradient_concordance_is_polarity_invariant_and_vanishes_orthogonally():
    gy_a = np.full((8, 8), 2.0, dtype=np.float32)
    gx_a = np.zeros((8, 8), dtype=np.float32)
    mag_a = np.hypot(gy_a, gx_a)

    # Antiparallel gradient (180 degrees opposite, e.g., footwall gravity high vs basin depth low)
    gy_b = np.full((8, 8), -3.0, dtype=np.float32)
    gx_b = np.zeros((8, 8), dtype=np.float32)
    mag_b = np.hypot(gy_b, gx_b)
    conc_anti, sin_anti = cross_gradient_concordance(gy_a, gx_a, mag_a, gy_b, gx_b, mag_b)
    assert np.allclose(sin_anti, 0.0, atol=1e-5)
    assert np.allclose(conc_anti, np.sqrt(6.0), atol=1e-4)

    # Orthogonal gradient (90 degrees, e.g., contour shoreline crossing basement trend)
    gy_orth = np.zeros((8, 8), dtype=np.float32)
    gx_orth = np.full((8, 8), 3.0, dtype=np.float32)
    conc_orth, sin_orth = cross_gradient_concordance(gy_a, gx_a, mag_a, gy_orth, gx_orth, mag_b)
    assert np.allclose(sin_orth, 1.0, atol=1e-5)
    assert np.allclose(conc_orth, 0.0, atol=1e-4)


def test_fft_upward_continuation_attenuates_high_frequencies_and_preserves_mean():
    rng = np.random.default_rng(42)
    field = (10.0 + rng.normal(0.0, 2.0, size=(32, 32))).astype(np.float32)
    up200 = fft_upward_continue(field, 200.0, cell_m=100.0)
    up800 = fft_upward_continue(field, 800.0, cell_m=100.0)
    assert np.std(up800) < np.std(up200) < np.std(field)
    assert abs(float(np.mean(up200)) - float(np.mean(field))) < 0.25


def test_exact_two_component_distances_matches_brute_force():
    vis = np.zeros((18, 20), dtype=bool)
    vis[2:5, 3] = True     # component 1
    vis[10, 12:16] = True  # component 2
    vis[15, 4:7] = True    # component 3
    comp = connected_components(vis)
    d1, d2 = exact_two_component_distances_m(vis, cell_m=100.0)

    comp_ids = [1, 2, 3]
    coords_by_c = {c: np.argwhere(comp == c) for c in comp_ids}
    for r in range(0, 18, 3):
        for c in range(0, 20, 3):
            dists = []
            for cid in comp_ids:
                pts = coords_by_c[cid]
                dd = 100.0 * float(np.min(np.hypot(pts[:, 0] - r, pts[:, 1] - c)))
                dists.append(dd)
            dists.sort()
            assert abs(float(d1[r, c]) - dists[0]) < 1e-3
            assert abs(float(d2[r, c]) - dists[1]) < 1e-3


def test_submodular_lazy_greedy_matches_exact_naive_greedy():
    rng = np.random.default_rng(7)
    w = rng.uniform(0.0, 1.0, size=(16, 16)).astype(np.float32)
    valid = np.ones((16, 16), dtype=bool)
    valid[0, :] = False
    w[~valid] = 0.0

    n_dots = 6
    min_dist = 2.2
    lazy = submodular_dti_emit(w, valid, n_dots, min_dist_px=min_dist)
    assert int(lazy.sum()) == n_dots

    # Brute-force sequential greedy check
    offsets, kernel = _offsets(CELL_M, RADIUS_M)
    cov = np.zeros_like(w)
    blocked = ~valid.copy()
    naive = np.zeros_like(valid)
    for _ in range(n_dots):
        best_gain = -1.0
        best_rc = None
        for r in range(16):
            for c in range(16):
                if blocked[r, c]:
                    continue
                gain = 0.0
                for (dr, dc), kv in zip(offsets, kernel):
                    rr, cc = r + int(dr), c + int(dc)
                    if 0 <= rr < 16 and 0 <= cc < 16:
                        gain += float(w[rr, cc]) * max(0.0, float(kv) - float(cov[rr, cc]))
                if gain > best_gain + 1e-12:
                    best_gain = gain
                    best_rc = (r, c)
        assert best_rc is not None
        br, bc = best_rc
        naive[br, bc] = True
        for (dr, dc), kv in zip(offsets, kernel):
            rr, cc = br + int(dr), bc + int(dc)
            if 0 <= rr < 16 and 0 <= cc < 16:
                cov[rr, cc] = max(cov[rr, cc], float(kv))
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                if dr * dr + dc * dc < min_dist ** 2 - 1e-9:
                    rr, cc = br + dr, bc + dc
                    if 0 <= rr < 16 and 0 <= cc < 16:
                        blocked[rr, cc] = True

    assert np.array_equal(lazy, naive)


def test_duplicate_canary_flags_identical_and_passes_independent(tmp_path):
    foot = np.ones((24, 24), dtype=bool)
    foot[0, :] = False
    ref_dots = np.zeros((24, 24), dtype=np.float32)
    ref_dots[4, 4] = 1.0
    ref_dots[4, 10] = 1.0
    ref_dots[4, 16] = 1.0

    ref_path = tmp_path / "ref.tif"
    with rasterio.open(
        ref_path,
        "w",
        driver="GTiff",
        height=24,
        width=24,
        count=1,
        dtype="float32",
        crs="EPSG:32611",
        transform=Affine(100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0),
    ) as dst:
        dst.write(ref_dots, 1)

    refs = [{"id": "ref1", "path": ref_path, "source_group": "test"}]

    # Identical candidate must trigger duplicate stop
    dup_res = check_duplicate_canary(ref_dots, ref_dots > 0.5, foot, refs)
    assert dup_res["passed"] is False
    assert "ref1" in dup_res["duplicates"]

    # Spatially separated candidate (>3 px away) must pass
    ind_surf = np.zeros((24, 24), dtype=np.float32)
    ind_surf[18, 4] = 0.9
    ind_surf[18, 10] = 0.8
    ind_surf[18, 16] = 0.7
    rw = ridge_sharpened_weight(ind_surf, foot)
    assert rw.shape == (24, 24)
    ok_res = check_duplicate_canary(ind_surf, ind_surf > 0.5, foot, refs)
    assert ok_res["passed"] is True
    assert ok_res["duplicates"] == []


def test_float32_nodata_sentinel_sanitization_prevents_fft_overflow():
    foot = np.ones((16, 16), dtype=bool)
    foot[0, :] = False
    arr = np.full((16, 16), 25.0, dtype=np.float32)
    arr[0, :] = -3.4028235e38  # outside-footprint sentinel
    arr[5, 5] = -3.4028235e38  # inside-footprint border sentinel (IR-31-FLOAT32-NODATA-SENTINEL-3061PX)

    clean = sanitize_nodata(arr, foot)
    assert np.isnan(clean[0, 0]) and np.isnan(clean[5, 5])
    filled = nearest_finite_fill(arr, foot)
    assert np.all(np.isfinite(filled)) and np.allclose(filled, 25.0)
    z = robust_z(arr, foot)
    assert np.all(np.isfinite(z[foot & ~np.isnan(clean)]))
    cont = fft_upward_continue(arr, 200.0, cell_m=100.0)
    assert np.all(np.isfinite(cont)) and np.allclose(cont, 25.0, atol=1e-3)


def test_generated_h31e2_submission_and_run_card_invariants():
    rc = json.loads((ROOT / "evidence/h31e/run_card.json").read_text())
    assert rc["holdout_dti"]["label"] == "HOLDOUT-DTI"
    assert rc["holdout_dti"]["buffer_m"] >= 21_250
    assert rc["leakage_canary"]["passed"] is True
    assert rc["leakage_canary"]["max_single_feature_auc"] <= 0.90
    assert rc["correlation_overlap_vs_registry"]["passed"] is True
    assert rc["correlation_overlap_vs_registry"]["max_surface_spearman_rho"] <= 0.90
    assert rc["correlation_overlap_vs_registry"]["max_final_dots_within_3px"] <= 0.70
    assert rc["submission_note_chars"] <= 140
    assert rc["verdict"] in ("promote", "negative")

    sub_name = rc["submission_name"]
    nan_path = ROOT / "docs/downloads" / f"{sub_name}-nan.tif"
    fin_path = ROOT / "docs/downloads" / f"{sub_name}-allfinite.tif"
    assert nan_path.is_file() and fin_path.is_file()
    assert hashlib.sha256(nan_path.read_bytes()).hexdigest() == rc["raster_sha256"]["nan_outside_primary"]
    assert hashlib.sha256(fin_path.read_bytes()).hexdigest() == rc["raster_sha256"]["allfinite_fallback"]

    with rasterio.open(nan_path) as src:
        assert src.count == 1
        assert src.dtypes[0] == "float32"
        assert str(src.crs) == "EPSG:32611"
        assert (src.height, src.width) == (3730, 3292)
        data = src.read(1)
        finite = data[np.isfinite(data)]
        assert finite.size == 5_167_373
        assert float(finite.min()) >= 0.0 and float(finite.max()) <= 1.0
        assert int((finite > 0.5).sum()) == 37_654

