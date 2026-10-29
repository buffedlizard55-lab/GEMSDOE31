"""Unit and integration tests for Lane H31-AA (SLFS) feature physics,
frozen preregistration, GeoTIFF validation, and fail-closed governance."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

from gemsdoe31.h31aa_features import (
    coverage_neutral_lidar_toe,
    crest1px,
    piedmont_window,
    shoreline_null_weight,
    single_scale_log_flexure,
)
from gemsdoe31.submission import sha256_file

ROOT = Path(__file__).resolve().parents[1]


def _simple_rank01(arr: np.ndarray, foot: np.ndarray) -> np.ndarray:
    out = np.zeros(arr.shape, dtype=np.float32)
    vals = arr[foot].astype(np.float64)
    order = np.argsort(vals, kind="mergesort")
    ranks = np.empty(vals.size, dtype=np.float64)
    ranks[order] = np.arange(vals.size, dtype=np.float64)
    sv = vals[order]
    r_sorted = ranks[order]
    i = 0
    while i < vals.size:
        j = i + 1
        while j < vals.size and sv[j] == sv[i]:
            j += 1
        if j - i > 1:
            r_sorted[i:j] = r_sorted[i:j].mean()
        i = j
    ranks[order] = r_sorted
    out[foot] = (ranks / max(vals.size - 1, 1)).astype(np.float32)
    return out


def test_piedmont_window_piecewise_bounds():
    s = np.array([0.0, 0.8, 1.4, 2.0, 6.5, 11.0, 14.5, 18.0, 25.0], dtype=np.float32)
    w = piedmont_window(s)
    assert w[0] == 0.0 and w[1] == 0.0
    assert w[2] == pytest.approx(0.5, abs=1e-5)
    assert w[3] == 1.0 and w[4] == 1.0 and w[5] == 1.0
    assert w[6] == pytest.approx(0.5, abs=1e-5)
    assert w[7] == 0.0 and w[8] == 0.0


def test_shoreline_null_suppresses_horizontal_bench_without_subsurface_step():
    h, w = 40, 40
    foot = np.ones((h, w), dtype=bool)
    rows, cols = np.indices((h, w), dtype=np.float32)
    # Rows 6..14 (20% of scene): strictly horizontal shoreline bench (delta-z along x = 0)
    # Rest of scene: tilted range/piedmont along strike x so delta-z along x > 0
    is_bench = (rows >= 6) & (rows < 14)
    z = 1300.0 - 2.0 * rows + np.where(is_bench, 0.0, 4.0 * cols)
    uy = np.ones((h, w), dtype=np.float32)
    ux = np.zeros((h, w), dtype=np.float32)
    sub_weak = np.full((h, w), 0.05, dtype=np.float32)
    sub_strong = np.full((h, w), 0.90, dtype=np.float32)

    w_weak, _ = shoreline_null_weight(z.astype(np.float32), uy, ux, sub_weak, foot, _simple_rank01)
    w_strong, _ = shoreline_null_weight(z.astype(np.float32), uy, ux, sub_strong, foot, _simple_rank01)

    # Horizontal bench without subsurface step is damped (< 0.60); tilted front stays 1.0
    assert float(w_weak[8:12, 10:30].mean()) < 0.60
    assert float(w_weak[26:34, 10:30].mean()) == pytest.approx(1.0, abs=1e-5)
    # Same horizontal contour WITH strong subsurface gravity/basement step is NOT damped
    assert float(w_strong[8:12, 10:30].mean()) == pytest.approx(1.0, abs=1e-5)


def test_crest1px_extracts_single_pixel_ridge_with_tie_break():
    h, w = 20, 20
    foot = np.ones((h, w), dtype=bool)
    field = np.zeros((h, w), dtype=np.float32)
    # Two-pixel flat plateau at rows 9 and 10, downslope +y (dy=+1, dx=0)
    field[8, :] = 0.5
    field[9, :] = 1.0
    field[10, :] = 1.0
    field[11, :] = 0.4
    uy = np.ones((h, w), dtype=np.float32)
    ux = np.zeros((h, w), dtype=np.float32)
    thinned = crest1px(field, uy, ux, foot)
    # Row 9 has f(9)=1.0 >= f(10)=1.0 and f(9)=1.0 > f(8)=0.5 -> crest!
    # Row 10 has f(10)=1.0 not > f(9)=1.0 -> suppressed to 0.05!
    assert np.allclose(thinned[9, :], 1.0)
    assert np.allclose(thinned[10, :], 0.05)


def test_coverage_neutral_lidar_toe_imputes_half_outside_coverage():
    foot = np.ones((10, 10), dtype=bool)
    foot[0, :] = False
    valid = np.zeros((10, 10), dtype=bool)
    valid[5:, :] = True
    step = np.linspace(0.0, 10.0, 100, dtype=np.float32).reshape(10, 10)
    down = np.linspace(0.0, 5.0, 100, dtype=np.float32).reshape(10, 10)
    out = coverage_neutral_lidar_toe(step, down, valid, foot)
    assert np.all(out[0, :] == 0.0)
    assert np.allclose(out[1:5, :], 0.50)
    assert float(out[5:, :].min()) > 0.0 and float(out[5:, :].max()) <= 1.0


def test_single_scale_log_flexure_fires_at_concave_piedmont_toe():
    h, w = 60, 40
    foot = np.ones((h, w), dtype=bool)
    rows, _cols = np.indices((h, w), dtype=np.float32)
    # Range above row 25 (slope 8 deg -> dz/dr = -14 m per 100 m px), gentle piedmont below (1.5 deg -> -2.6 m/px)
    slope = np.where(rows < 25, 8.0, 1.5).astype(np.float32)
    elev = np.where(rows < 25, 1800.0 - 14.0 * rows, 1450.0 - 2.6 * (rows - 25)).astype(np.float32)
    phi, _zs, _uy, _ux = single_scale_log_flexure(elev, slope, foot, 1.5)
    toe_band = float(phi[23:28, 10:30].max())
    far_flat = float(phi[45:55, 10:30].max())
    assert toe_band > 10.0 * max(far_flat, 1e-6)


def test_h31aa_packaged_artifacts_and_fail_closed_governance():
    card_path = ROOT / "evidence/h31aa/run_card.json"
    assert card_path.is_file()
    card = json.loads(card_path.read_text())
    assert card["lane"] == "H31-AA"
    assert card["verdict"] == "negative"
    assert card["ok_to_download_for_research"] is True
    assert card["ok_to_submit"] is False
    assert card["slot_approved"] is False
    assert card["leaderboard_estimate"] is None
    assert 0 < card["note_chars"] <= 140
    assert len(card["note"]) == card["note_chars"]

    # Preregistration pin immutable
    pin = json.loads((ROOT / "evidence/h31aa/preregistration_pin.json").read_text())
    assert sha256_file(ROOT / pin["preregistration"]) == pin["sha256"]

    # GeoTIFF and ZIP hashes verified
    assert sha256_file(ROOT / card["files"]["zeros"]) == card["raster_sha256"]
    assert sha256_file(ROOT / card["files"]["nan"]) == card["raster_sha256_nan"]
    assert sha256_file(ROOT / card["files"]["zip"]) == card["zip_sha256"]
    assert sha256_file(ROOT / card["files"]["nan_zip"]) == card["nan_zip_sha256"]

    # Standalone verifier script executes cleanly
    spec = importlib.util.spec_from_file_location("verify_h31aa_run", ROOT / "scripts/verify_h31aa_run.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    receipt = mod.verify(ROOT)
    assert receipt["status"] == "VERIFIED"
    assert receipt["ok_to_submit"] is False
    assert receipt["slot_approved"] is False


def test_h31aa_write_mode_refuses_to_downgrade_receipt_without_template(tmp_path):
    """Regression: a write-mode verify without data/sample_submission.tif must raise the
    explicit guard and leave the committed receipt byte-identical."""
    import importlib.util
    import shutil

    spec = importlib.util.spec_from_file_location("verify_h31aa_run_regress", ROOT / "scripts/verify_h31aa_run.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Copy the evidence tree the verifier reads; deliberately omit data/ (template absent).
    fake = tmp_path / "repo"
    for sub in ("evidence", "registry", "docs", "knowledge"):
        shutil.copytree(ROOT / sub, fake / sub, ignore=shutil.ignore_patterns("__pycache__"))
    rec = fake / "evidence/h31aa/verification_receipt.json"
    prev_text = rec.read_text()
    assert '"grid_and_range_verified": true' in prev_text

    with pytest.raises(ValueError, match="Refusing to overwrite a passing H31-AA receipt"):
        mod.verify(fake, check_only=False)
    assert rec.read_text() == prev_text
