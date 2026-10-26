"""Synthetic physics and safety unit tests for H31-S (UDAP-SSLIC)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from gemsdoe31.h31s_features import (
    _gdr_proximity,
    _read_u8_clean,
    compute_hzad_channels,
    compute_null_suppressors,
    compute_sslic_channels,
    compute_udap_channels,
)


def test_udap_projects_buried_hanging_wall_hgm_back_to_surface_trace() -> None:
    """A 55-deg east-dipping normal fault with surface trace at c=30 has its gravity HGM at c=35;
    UDAP must pull the displaced HGM peak back toward c=30 with positive advected gain there."""
    h, w = 64, 80
    fp = np.ones((h, w), dtype=bool)
    cols = np.arange(w, dtype=np.float32)[None, :]
    # Footwall on west (c < 30, Z_b ~ 20 m), hanging-wall basin on east (c > 30, Z_b ~ 715 m -> 715*cot55 = 500 m = 5 px)
    zb = 20.0 + 695.0 * (0.5 * (1.0 + np.tanh((cols - 32.0) / 3.0)))
    zb = np.broadcast_to(zb, (h, w)).astype(np.float32)
    # Displaced gravity HGM centered 5 px basinward at c = 35
    grav_slope = np.exp(-0.5 * ((cols - 35.0) / 1.5) ** 2)
    grav_slope = np.broadcast_to(grav_slope, (h, w)).astype(np.float32)
    tmi_up = np.broadcast_to(100.0 - 20.0 * np.tanh((cols - 35.0) / 2.0), (h, w)).astype(np.float32)
    dilat = np.full((h, w), 0.05, dtype=np.float32)

    ch, ty, tx = compute_udap_channels(zb, grav_slope, tmi_up, dilat, fp)
    assert set(ch.keys()) == {
        "udap_grav_slope_55",
        "udap_grav_slope_45",
        "udap_grav_slope_65",
        "udap_bstep_55",
        "udap_tmi150_hg_55",
        "udap_grav_gain_55",
        "udap_concordance_55",
        "udap_dilat_coupling",
    }
    for arr in ch.values():
        assert arr.shape == (h, w)
        assert arr.dtype == np.float32
        assert np.isfinite(arr).all()

    # At the true surface fault trace c=30, raw grav_slope is near zero (~0.004), while UDAP pulls the c=35 peak back!
    raw_at_trace = float(grav_slope[32, 30])
    udap_at_trace = float(ch["udap_grav_slope_55"][32, 30])
    gain_at_trace = float(ch["udap_grav_gain_55"][32, 30])
    assert udap_at_trace > raw_at_trace + 0.35
    assert gain_at_trace > 0.35
    # Unit strike vector along N-S trace must point predominantly along rows (|ty| >> |tx|)
    assert float(np.abs(ty[32, 30])) > 0.90


def test_hzad_detects_axial_magnetite_destruction_trough() -> None:
    """An axial RTP trough flanked by magnetic shoulders + elevated K/Th produces positive conduit signal."""
    h, w = 64, 64
    fp = np.ones((h, w), dtype=bool)
    cols = np.arange(w, dtype=np.float32)[None, :]
    # N-S fault zone at c=32 with magnetite destruction trough (RTP drop of 150 nT over ~3 px)
    rtp = np.broadcast_to(200.0 - 150.0 * np.exp(-0.5 * ((cols - 32.0) / 2.2) ** 2), (h, w)).astype(np.float32)
    tmi150 = rtp.copy()
    rad_k = np.broadcast_to(40.0 + 60.0 * np.exp(-0.5 * ((cols - 32.0) / 3.0) ** 2), (h, w)).astype(np.float32)
    rad_th = np.full((h, w), 25.0, dtype=np.float32)
    cond = np.broadcast_to(2.5 + 1.2 * np.exp(-0.5 * ((cols - 32.0) / 3.5) ** 2), (h, w)).astype(np.float32)
    t_prior = np.full((h, w), 1.0, dtype=np.float32)
    strike_ty = np.ones((h, w), dtype=np.float32)
    strike_tx = np.zeros((h, w), dtype=np.float32)

    ch = compute_hzad_channels(rtp, tmi150, rad_k, rad_th, cond, t_prior, strike_ty, strike_tx, fp)
    assert float(ch["hzad_rtp_axial_trough"][32, 32]) > 30.0
    assert float(ch["hzad_rtp_axial_trough"][32, 10]) < 1.0
    assert float(ch["hzad_geothermal_conduit"][32, 32]) > float(ch["hzad_geothermal_conduit"][32, 10]) + 1.0


def test_null_suppressors_flag_contour_bench_and_cardinal_seams() -> None:
    h, w = 64, 64
    fp = np.ones((h, w), dtype=bool)
    rows = np.arange(h, dtype=np.float32)[:, None]
    cols = np.arange(w, dtype=np.float32)[None, :]
    # Pure E-W horizontal contour step (zero variation along contour cols)
    elev_bench = np.broadcast_to(50.0 * np.tanh((rows - 32.0) / 2.0), (h, w)).astype(np.float32)
    slope_bench = np.broadcast_to(12.0 * np.exp(-0.5 * ((rows - 32.0) / 2.0) ** 2), (h, w)).astype(np.float32)
    ch_bench = compute_null_suppressors(elev_bench, slope_bench, fp)

    # Diagonal fault scarp climbing across an alluvial fan
    elev_scarp = (50.0 * np.tanh(((rows + cols) - 64.0) / 2.8) + 1.8 * (rows - cols)).astype(np.float32)
    ch_scarp = compute_null_suppressors(elev_scarp, slope_bench, fp)
    assert float(ch_bench["null_contour_bench"][32, 32]) > float(ch_scarp["null_contour_bench"][32, 32])
    # Cardinal E-W bench has cos(4*psi) > 0.8 while 45-deg scarp has negative cardinal index
    assert float(ch_bench["null_cardinal_seam"][32, 32]) > 0.5
    assert float(ch_scarp["null_cardinal_seam"][32, 32]) < 0.0


def test_sslic_amplifies_continuous_strand_over_isolated_blob() -> None:
    h, w = 64, 64
    fp = np.ones((h, w), dtype=bool)
    rows = np.arange(h, dtype=np.float32)[:, None]
    cols = np.arange(w, dtype=np.float32)[None, :]
    # Continuous N-S fault strand at c=20 vs isolated circular blob at (32, 48)
    strand = 0.8 * np.exp(-0.5 * ((cols - 20.0) / 1.2) ** 2)
    blob = 0.8 * np.exp(-0.5 * (((rows - 32.0) ** 2 + (cols - 48.0) ** 2) / (1.5**2)))
    p1 = np.clip(strand + blob, 0.0, 1.0).astype(np.float32)
    ty = np.ones((h, w), dtype=np.float32)
    tx = np.zeros((h, w), dtype=np.float32)

    ch = compute_sslic_channels(p1, ty, tx, fp)
    assert float(ch["sslic_bilateral_min_800m"][32, 20]) > 0.70
    assert float(ch["sslic_bilateral_min_800m"][32, 48]) < 0.05
    assert float(ch["sslic_cross_contrast_500m"][32, 20]) > 0.60


def test_banned_raster_guard_rejects_qfaults_and_labels() -> None:
    fp = np.ones((8, 8), dtype=bool)
    with pytest.raises(ValueError, match="banned"):
        _read_u8_clean(Path("data/external/derived_gdr_qfaults_v2_100m_u8.tif"), 1, fp)
    with pytest.raises(ValueError, match="banned"):
        _gdr_proximity(Path("data/labels.tif"), fp, 10.0)
    with pytest.raises(ValueError, match="banned"):
        _gdr_proximity(Path("data/external/derived_sgmc_faults_100m_u8.tif"), fp, 10.0)


def test_h31s_packaged_deliverables_and_run_card_pass_automated_validation() -> None:
    import sys

    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "scripts"))
    from verify_h31s_run import verify_h31s

    res = verify_h31s(root)
    assert res["ok_to_download_for_research"] is True
    assert res["ok_to_submit"] is False
    assert res["slot_approved"] is False
    assert res["positive_pixels"] == 37_654
    assert 1 <= res["note_length"] <= 140

