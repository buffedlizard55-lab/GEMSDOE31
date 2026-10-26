"""Unit tests for Lane H31-T physical crustal-mechanics features & Dinkelbach CELF."""

from __future__ import annotations

import numpy as np
import pytest
from scipy import ndimage as ndi

from gemsdoe31.h31t_dinkelbach import (
    KERNEL_DC,
    KERNEL_DR,
    KERNEL_W,
    emit_dinkelbach_submodular_dots,
    emit_poisson_thinning_dots,
)
from gemsdoe31.h31t_features import (
    H31T_STATIC_CHANNELS,
    H31T_VISIBLE_CHANNELS,
    compute_fold_visible_fracture_fields,
    compute_h31t_static_channels_from_arrays,
    sanitize_band,
)


def _synthetic_inputs(shape: tuple[int, int] = (96, 96)) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(3101)
    H, W = shape
    fp = np.ones((H, W), dtype=bool)
    fp[:4, :] = False
    fp[:, :4] = False

    rr, cc = np.indices((H, W), dtype=np.float32)
    # Synthetic N-S normal fault trace at col = 44 dipping east (basin thickens east)
    z_base = np.where(cc >= 44, (cc - 44.0) * 80.0, 20.0).astype(np.float32)
    # Subsurface gravity step shifted 3 px east into hanging wall (col = 47)
    grav_slope = (0.35 * np.exp(-0.5 * ((cc - 47.0) / 1.8) ** 2) + 0.02).astype(np.float32)
    grav_vg = (1.5 * (cc - 47.0) * np.exp(-0.5 * ((cc - 47.0) / 2.2) ** 2)).astype(np.float32)
    tmi_hg = (80.0 * np.exp(-0.5 * ((cc - 44.0) / 1.6) ** 2) + 5.0).astype(np.float32)
    tmi_vg = (0.30 * np.exp(-0.5 * ((cc - 44.0) / 1.6) ** 2)).astype(np.float32)
    rtp = (-120.0 * np.exp(-0.5 * ((cc - 44.0) / 1.8) ** 2) + rng.normal(0, 2.0, (H, W))).astype(
        np.float32
    )
    # Inject a -3.4e38 NoData sentinel to verify sentinel immunity
    tmi_hg[10, 10] = -3.4028235e38

    probes = np.zeros((H, W), dtype=bool)
    probes[48, 44] = True
    paleo = np.zeros((H, W), dtype=bool)
    paleo[30, 44] = True
    volc = np.zeros((H, W), dtype=bool)
    volc[70, 60] = True

    lidar_up = np.full((H, W), np.nan, dtype=np.float32)
    lidar_dn = np.full((H, W), np.nan, dtype=np.float32)
    lidar_st = np.full((H, W), np.nan, dtype=np.float32)
    lidar_ch = np.full((H, W), np.nan, dtype=np.float32)
    # Partial LiDAR coverage on rows 20..80
    lidar_up[20:80, :] = 10.0 + 40.0 * np.exp(-0.5 * ((cc[20:80, :] - 44.0) / 1.5) ** 2)
    lidar_dn[20:80, :] = 4.0
    lidar_st[20:80, :] = 25.0 * np.exp(-0.5 * ((cc[20:80, :] - 44.0) / 1.5) ** 2)
    lidar_ch[20:80, :] = 180.0

    return {
        "footprint": fp,
        "tmi_hg": tmi_hg,
        "tmi_vg": tmi_vg,
        "rtp": rtp,
        "iso_grav_slope": grav_slope,
        "iso_grav_vg": grav_vg,
        "depth_to_base": z_base,
        "geod_2ndinv": np.full((H, W), 18.0, dtype=np.float32),
        "geod_shearrate": np.full((H, W), 12.0, dtype=np.float32),
        "geod_dilaterate": np.where(np.abs(cc - 44.0) < 8, 14.0, -3.0).astype(np.float32),
        "deq_m": (np.abs(cc - 44.0) * 400.0 + 200.0).astype(np.float32),
        "ieq_density": np.full((H, W), 900.0, dtype=np.float32),
        "cond_surf": (2.5 + 1.2 * np.exp(-0.5 * ((cc - 44.0) / 1.8) ** 2)).astype(np.float32),
        "det_elev": np.where(cc < 44, 200.0, 120.0 - 0.5 * (cc - 44.0)).astype(np.float32),
        "det_elev_slope": np.where(np.abs(cc - 44.0) <= 2, 5.0, 2.0).astype(np.float32),
        "rad_k": (35.0 + 25.0 * np.exp(-0.5 * ((cc - 44.0) / 2.0) ** 2)).astype(np.float32),
        "rad_th": np.full((H, W), 20.0, dtype=np.float32),
        "lidar_upface": lidar_up,
        "lidar_downface": lidar_dn,
        "lidar_step": lidar_st,
        "lidar_coh100": lidar_ch,
        "gdr_probes_mask": probes,
        "gdr_paleo_mask": paleo,
        "gdr_volcanics_mask": volc,
    }


def test_static_channels_sentinel_safety_and_listric_restoration() -> None:
    inp = _synthetic_inputs()
    fp = inp["footprint"]
    ch = compute_h31t_static_channels_from_arrays(**inp)
    assert tuple(ch.keys()) == H31T_STATIC_CHANNELS

    for name, arr in ch.items():
        assert arr.shape == fp.shape
        assert arr.dtype == np.float32
        # Strictly NaN outside footprint
        assert np.all(np.isnan(arr[~fp])), f"{name} leaked finite values outside footprint"
        # No -3.4e38 sentinel blowups anywhere
        finite = arr[np.isfinite(arr)]
        assert finite.size > 0
        assert float(np.max(np.abs(finite))) < 1.0e4, f"{name} sentinel blowup"

    # Partial LiDAR channel must preserve NaN outside LiDAR coverage (rows 4..19)
    assert np.all(np.isnan(ch["lidar_scarp_asymmetry"][6:18, 20:60]))
    assert np.all(np.isfinite(ch["lidar_scarp_asymmetry"][30:70, 20:60]))

    # Up-dip listric restoration: raw gravity peak sits at col 47, whereas up-dip
    # restored trace enhances response westward toward surface trace (col 44-45)
    raw_grav_col45 = float(np.nanmean(ch["asig_grav_crest"][25:75, 45]))
    raw_grav_col52 = float(np.nanmean(ch["asig_grav_crest"][25:75, 52]))
    updip_col45 = float(np.nanmean(ch["updip_listric_trace"][25:75, 45]))
    updip_col52 = float(np.nanmean(ch["updip_listric_trace"][25:75, 52]))
    assert raw_grav_col45 > raw_grav_col52
    assert updip_col45 > updip_col52 * 2.0


def test_fold_visible_fracture_fields_zero_withheld_leakage() -> None:
    H, W = 100, 100
    fp = np.ones((H, W), dtype=bool)
    visible = np.zeros((H, W), dtype=bool)
    # Two en-echelon visible fault segments separated by a ~1.0 km (10 px) relay step-over
    visible[20:45, 30] = True
    visible[48:75, 38] = True

    out_a = compute_fold_visible_fracture_fields(visible, fp)
    assert tuple(out_a.keys()) == H31T_VISIBLE_CHANNELS

    # Even if an earlier-row withheld fault exists elsewhere in `full_catalogue`,
    # passing `visible = full_catalogue & ~withheld` must yield 100% bit-identical arrays!
    withheld_north = np.zeros((H, W), dtype=bool)
    withheld_north[5:15, 10] = True
    full_cat = visible | withheld_north
    out_b = compute_fold_visible_fracture_fields(full_cat & (~withheld_north), fp)
    for k in H31T_VISIBLE_CHANNELS:
        np.testing.assert_array_equal(out_a[k], out_b[k])

    # Relay bridge peaks inside the step-over between (44, 30) and (48, 38), and is 0 far away
    assert float(out_a["vis_relay_dilation_bridge"][46, 34]) > 0.20
    assert float(out_a["vis_relay_dilation_bridge"][90, 90]) == 0.0
    # Wing-crack tip lobe extends southward past row 74 along col 38
    assert float(out_a["vis_wingcrack_tip_lobe"][82, 38]) > 0.30
    assert float(out_a["vis_wingcrack_tip_lobe"][82, 70]) < 1.0e-6


def test_dinkelbach_batch_exact_matches_sequential_celf_and_contract() -> None:
    # 29-cell disk `dr^2 + dc^2 <= 9` has 25 strictly positive offsets (`k > 0`)
    # and 4 zero-weight cardinal boundary cells `(+-3, 0), (0, +-3)` (`k(3.0) == 0`).
    assert KERNEL_W.size == 25
    assert KERNEL_DR.size == 25 and KERNEL_DC.size == 25

    rng = np.random.default_rng(20261025)
    H, W = 64, 64
    fp = np.ones((H, W), dtype=bool)
    fp[:3, :] = False
    vis = np.zeros((H, W), dtype=bool)
    vis[30:36, 30] = True

    prob = rng.uniform(0.0, 0.85, size=(H, W)).astype(np.float32)
    # Add two strong fault ridges
    prob[12:55, 16] = 0.92
    prob[15:52, 48] = 0.88

    res_seq = emit_dinkelbach_submodular_dots(
        prob,
        fp,
        vis,
        budget=35,
        collar_px=2.0,
        min_spacing_px=2.4,
        cost_eta=0.50,
        ridge_gamma=0.35,
        batch_size=1,
    )
    res_batched = emit_dinkelbach_submodular_dots(
        prob,
        fp,
        vis,
        budget=35,
        collar_px=2.0,
        min_spacing_px=2.4,
        cost_eta=0.50,
        ridge_gamma=0.35,
        batch_size=64,
    )

    assert res_seq.n_dots == 35
    np.testing.assert_array_equal(res_seq.binary_dots, res_batched.binary_dots)
    assert pytest.approx(res_seq.total_weighted_gain, rel=1e-7) == res_batched.total_weighted_gain
    assert pytest.approx(res_seq.total_fp_cost, rel=1e-10) == res_batched.total_fp_cost

    # Contract checks: strictly {0.0, 1.0}, 0 outside footprint, 0 within <= 2.0 px of vis,
    # and pairwise dot distance >= 2.4 px
    dots = res_batched.binary_dots
    assert set(np.unique(dots).tolist()).issubset({0.0, 1.0})
    assert float(dots[~fp].sum()) == 0.0
    d_vis = ndi.distance_transform_edt(~vis)
    assert float(dots[d_vis <= 2.0].sum()) == 0.0

    rr, cc = np.nonzero(dots > 0.5)
    for i in range(rr.size):
        for j in range(i + 1, rr.size):
            dist = float(np.hypot(rr[i] - rr[j], cc[i] - cc[j]))
            assert dist >= 2.4 - 1.0e-6

    p_dots = emit_poisson_thinning_dots(prob, fp, vis, budget=35, collar_px=2.0, min_spacing_px=2.8)
    assert int(p_dots.sum()) == 35
    assert float(p_dots[d_vis <= 2.0].sum()) == 0.0


def test_sanitize_band_rejects_large_sentinels() -> None:
    fp = np.array([[True, True], [True, False]])
    raw = np.array([[1.5, -3.4028235e38], [np.inf, 2.0]], dtype=np.float32)
    clean = sanitize_band(raw, fp)
    assert clean[0, 0] == pytest.approx(1.5)
    assert np.isnan(clean[0, 1])
    assert np.isnan(clean[1, 0])
    assert np.isnan(clean[1, 1])


def test_portal_range_error_guard_rejects_out_of_0_1_and_interior_nan(tmp_path) -> None:
    import rasterio
    from rasterio.transform import Affine

    from gemsdoe31.submission import validate_submission

    # Synthetic regression guard ensuring out-of-[0, 1] values or interior NaN
    # fail closed (preventing DrivenData's "Predicted values must be in range [0, 1]").
    tpl = tmp_path / "tpl.tif"
    prof = {
        "driver": "GTiff",
        "dtype": "float32",
        "count": 1,
        "height": 8,
        "width": 8,
        "crs": "EPSG:32611",
        "transform": Affine(100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0),
        "nodata": np.nan,
    }
    tpl_arr = np.zeros((8, 8), dtype=np.float32)
    tpl_arr[0, :] = np.nan
    with rasterio.open(tpl, "w", **prof) as dst:
        dst.write(tpl_arr, 1)

    for bad_val, tag in ((1.01, "above1"), (-0.02, "below0"), (np.nan, "nan_inside")):
        bad_tif = tmp_path / f"bad_{tag}.tif"
        arr = np.zeros((8, 8), dtype=np.float32)
        arr[4, 4] = bad_val
        with rasterio.open(bad_tif, "w", **{**prof, "nodata": None}) as dst:
            dst.write(arr, 1)
        res = validate_submission(bad_tif, tpl, convention="all-finite")
        assert res["ok_to_upload_format_only"] is False
        assert len(res["hard_failures"]) >= 1


def test_h31t_artifacts_and_run_card() -> None:
    import importlib.util
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    if not (root / "data/sample_submission.tif").is_file() or not (
        root / "data/labels.tif"
    ).is_file():
        pytest.skip(
            "CI restores the two pinned small inputs before this test; "
            "run `python scripts/verify_h31t.py --restore-small-inputs`"
        )
    spec = importlib.util.spec_from_file_location("verify_h31t", root / "scripts/verify_h31t.py")
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    summary = mod.verify_h31t()
    assert summary["status"] == "verified"
    assert summary["emitted_dots"] == 37_654
    assert summary["min_distance_to_catalogue_m"] > 200.0
    assert summary["ok_to_download_for_research"] is True
    assert summary["ok_to_submit"] is False
    assert summary["slot_approved"] is False

