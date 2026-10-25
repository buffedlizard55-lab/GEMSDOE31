"""Unit tests for H31-M label-free geophysical channels and 29-cell submodular DTI emitter."""

from __future__ import annotations

import numpy as np
from scipy.ndimage import distance_transform_edt

from gemsdoe31 import metric
from gemsdoe31.h31m_features import H31M_CHANNELS, build_h31m_channels
from gemsdoe31.submodular_emit import submodular_emit_dots


def _synthetic_bands(shape: tuple[int, int] = (80, 90)) -> dict[str, np.ndarray]:
    rows, cols = np.indices(shape, dtype=np.float32)
    # Create a N-S concealed basement fault step around col = 45
    step_x = np.tanh((cols - 45.0) / 2.5)
    z_base = 350.0 + 250.0 * step_x
    grav_vg = -2.0 * step_x
    grav_slope = np.abs(np.gradient(200.0 * step_x)[1]) + 0.05
    rtp = 120.0 * step_x + 5.0 * np.sin(rows / 10.0)
    cond = 2.5 + 0.8 * np.exp(-((cols - 45.0) ** 2) / 6.0)
    det_elev = -50.0 - 25.0 * step_x
    det_slope = np.abs(np.gradient(det_elev)[1]) + 1.0
    return {
        "depth_to_base_surf": z_base.astype(np.float32),
        "iso_grav_anom_slope": grav_slope.astype(np.float32),
        "iso_grav_anom_vg": grav_vg.astype(np.float32),
        "rtp": rtp.astype(np.float32),
        "cond_surf": cond.astype(np.float32),
        "det_elev": det_elev.astype(np.float32),
        "det_elev_slope": det_slope.astype(np.float32),
    }


def test_h31m_channels_sentinel_and_nan_safety():
    bands = _synthetic_bands((64, 72))
    # Inject -3.4028235e38 sentinel outside footprint and on a fringe row
    bands["depth_to_base_surf"][0, :] = np.float32(-3.4028235e38)
    bands["rtp"][:, -1] = np.nan
    out = build_h31m_channels(bands)
    assert list(out.keys()) == H31M_CHANNELS
    for name, arr in out.items():
        assert arr.dtype == np.float32, name
        assert arr.shape == (64, 72), name
        fin = arr[np.isfinite(arr)]
        assert fin.size > 0, name
        assert np.all(np.abs(fin) < 1e10), f"sentinel leaked into {name}"
    assert np.all(np.isnan(out["bstep_grad_norm"][0, :]))
    assert np.all(np.isnan(out["rtp_bandpass_crest"][:, -1]))


def test_h31m_strike_concordance_parallel_vs_orthogonal():
    shape = (80, 80)
    rows, cols = np.indices(shape, dtype=np.float32)
    bands_par = _synthetic_bands(shape)
    out_par = build_h31m_channels(bands_par)
    par_center = float(np.nanmean(out_par["xmod_strike_concordance"][25:55, 42:48]))

    # Now rotate det_elev ridge 90 degrees (E-W shoreline across N-S subsurface fault)
    bands_ortho = _synthetic_bands(shape)
    step_y = np.tanh((rows - 40.0) / 2.5)
    bands_ortho["det_elev"] = (-50.0 - 25.0 * step_y).astype(np.float32)
    bands_ortho["det_elev_slope"] = (np.abs(np.gradient(bands_ortho["det_elev"])[0]) + 1.0).astype(np.float32)
    out_ortho = build_h31m_channels(bands_ortho)
    ortho_center = float(np.nanmean(out_ortho["xmod_strike_concordance"][37:43, 42:48]))

    assert par_center > 0.65
    assert ortho_center < 0.15


def test_submodular_emit_matches_naive_greedy_and_respects_b2_collar():
    rng = np.random.default_rng(42)
    shape = (36, 40)
    surf = rng.uniform(0.0, 1.0, size=shape).astype(np.float32)
    # Plant two strong fault ridges
    surf[10, 6:34] = 0.95
    surf[26, 6:34] = 0.90
    valid = np.ones(shape, dtype=bool)
    vis_cat = np.zeros(shape, dtype=bool)
    vis_cat[10, 8:15] = True

    dots = submodular_emit_dots(
        surf,
        valid,
        max_dots=18,
        visible_catalogue=vis_cat,
        min_sep_px=2.25,
        smooth_sigma=0.0,
        contrast_gamma=1.0,
    )
    assert int(dots.sum()) == 18
    d_vis = distance_transform_edt(~vis_cat)
    assert np.all(d_vis[dots] > 2.0), "B=2 visible-catalogue exclusion violated"

    # Verify minimum pairwise spacing > 2.25 px
    ry, rx = np.nonzero(dots)
    for i in range(len(ry)):
        for j in range(i + 1, len(ry)):
            dist = float(np.hypot(ry[i] - ry[j], rx[i] - rx[j]))
            assert dist > 2.25 - 1e-6

    # Check lazy-greedy exact equivalence to naive step-by-step greedy on small grid
    small_surf = rng.uniform(0.1, 0.9, size=(20, 22)).astype(np.float32)
    small_val = np.ones((20, 22), dtype=bool)
    lazy = submodular_emit_dots(
        small_surf, small_val, max_dots=8, min_sep_px=2.25, smooth_sigma=0.0, contrast_gamma=1.0
    )

    med = float(np.median(small_surf))
    w = np.maximum(small_surf - med, 0.0).astype(np.float32)
    offsets, kernel = metric._offsets(metric.CELL_M, metric.RADIUS_M)
    cov = np.zeros((20, 22), dtype=np.float32)
    naive = np.zeros((20, 22), dtype=bool)
    for _ in range(8):
        best_val = -1.0
        best_rc = None
        for r in range(20):
            for c in range(22):
                if w[r, c] <= 0.0:
                    continue
                if naive.any():
                    nr, nc = np.nonzero(naive)
                    if np.any((nr - r) ** 2 + (nc - c) ** 2 <= 2.25 * 2.25 + 1e-9):
                        continue
                gain = 0.0
                for (dr, dc), kw in zip(offsets, kernel):
                    rr, cc = r + int(dr), c + int(dc)
                    if 0 <= rr < 20 and 0 <= cc < 22:
                        gain += float(w[rr, cc]) * max(float(kw) - float(cov[rr, cc]), 0.0)
                if gain > best_val + 1e-6:
                    best_val = gain
                    best_rc = (r, c)
        assert best_rc is not None
        br, bc = best_rc
        naive[br, bc] = True
        for (dr, dc), kw in zip(offsets, kernel):
            rr, cc = br + int(dr), bc + int(dc)
            if 0 <= rr < 20 and 0 <= cc < 22:
                cov[rr, cc] = max(cov[rr, cc], float(kw))
    assert np.array_equal(lazy, naive)
