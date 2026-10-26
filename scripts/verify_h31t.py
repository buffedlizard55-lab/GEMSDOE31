#!/usr/bin/env python3
"""Automated zero-human-input verification of the H31-T research GeoTIFFs & Run Card.

Verifies from a fresh repository checkout (requiring only committed artifacts in
`data/`, `docs/downloads/`, `evidence/h31t/`, `knowledge/`, and `.cache/registry*`):
1. Frozen H31-T preregistration SHA-256 integrity.
2. Primary all-finite (`-zeros.tif`) and companion (`-nan.tif`) GeoTIFFs + single-TIFF ZIPs:
   - Exact CRS (`EPSG:32611`), shape (`3730 x 3292`), geotransform (`Affine(100,0,243350,0,-100,4508550)`),
     single `float32` band;
   - Zero NaN/Inf inside the 5,167,373-cell valid footprint and values strictly in `[0.0, 1.0]`
     (preventing DrivenData's `"Predicted values must be in range [0, 1]"` upload rejection);
   - Exact 37,654 binary `{0.0, 1.0}` predictions, identical inside-footprint pixels across
     both encodings, and 0 dots within `<= 200 m` (`2 px`) of public catalogue faults;
   - Exact SHA-256 match against `evidence/h31t/run_card.json` and `registry/submissions.json`.
3. Scientific & governance gates in `evidence/h31t/*.json`:
   - Strict JSON compliance (no `NaN`/`Infinity`);
   - Leakage canary `<= 0.90`, own-method variogram collar `>= 21,250 m`, paired 95% CI `> 0`
     across `gems57-pooled-hide-v2`, `gemsdoe31-holdout-v1` Screen, and untouched Confirmation;
   - Fail-closed governance (`ok_to_download_for_research=True`, `ok_to_submit=False`,
     `slot_approved=False`, `verdict="negative"`) under the unexempted 695-raster `r13-lattice-s5` STOP.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gemsdoe31.submission import validate_submission  # noqa: E402

EXPECTED_PREREG_SHA256 = "f1669fb7f94a67b6cb4556b2d674318016497ddd915736bb77bb7e18ea021feb"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_h31t() -> dict:
    prereg = ROOT / "knowledge/2026-10-25_h31t_transtension_dinkelbach_preregistration.md"
    assert prereg.is_file(), f"Missing preregistration: {prereg}"
    prereg_sha = _sha256(prereg)
    assert prereg_sha == EXPECTED_PREREG_SHA256, (
        f"Preregistration SHA-256 mismatch: {prereg_sha} != {EXPECTED_PREREG_SHA256}"
    )

    rc_path = ROOT / "evidence/h31t/run_card.json"
    e1_diag_path = ROOT / "evidence/h31t/exp1_vis_self_inclusion_diagnostic.json"
    e1_path = ROOT / "evidence/h31t/exp1_canary_variogram_gems57.json"
    e2_path = ROOT / "evidence/h31t/exp2_holdout_screen_confirm.json"
    e3_path = ROOT / "evidence/h31t/exp3_uniqueness_offcat_package.json"
    def _forbid_nonfinite(tok: str) -> None:
        raise AssertionError(f"Non-finite JSON constant {tok!r}")

    for p in (rc_path, e1_diag_path, e1_path, e2_path, e3_path):
        assert p.is_file(), f"Missing H31-T evidence JSON: {p}"
        json.loads(p.read_text(), parse_constant=_forbid_nonfinite)

    rc = json.loads(rc_path.read_text())
    assert rc["experiments_used"] == 3 and rc["experiment_cap"] == 3
    assert rc["ok_to_download_for_research"] is True
    assert rc["ok_to_submit"] is False
    assert rc["slot_approved"] is False
    assert rc["verdict"] == "negative"
    assert len(rc["submission_note"]) <= 140

    # Scientific gates
    assert rc["leakage_canary"]["passed"] is True
    assert rc["leakage_canary"]["max_symmetric_auc"] <= 0.90
    assert rc["own_method_variogram_collar"]["adopted_holdout_buffer_m"] >= 21250.0
    hd = rc["holdout_dti"]
    assert hd["primary_shared_template_gems57_pooled_hide_v2"]["paired_delta_vs_ctrl_ci95"][0] > 0.0
    assert hd["gemsdoe31_holdout_v1_screen"]["paired_delta_vs_ctrl_ci95"][0] > 0.0
    assert hd["gemsdoe31_holdout_v1_untouched_confirm"]["paired_delta_vs_ctrl_ci95"][0] > 0.0

    # GeoTIFF + ZIP verification
    sample_path = ROOT / "data/sample_submission.tif"
    labels_path = ROOT / "data/labels.tif"
    if not sample_path.is_file() or not labels_path.is_file():
        raise FileNotFoundError(
            "Missing data/sample_submission.tif or data/labels.tif; run "
            "`python scripts/verify_current_run.py --restore-small-inputs` first."
        )

    art = rc["artifacts"]
    zeros_tif = ROOT / art["primary_zeros_tif"]
    zeros_zip = ROOT / art["primary_zeros_zip"]
    nan_tif = ROOT / art["companion_nan_tif"]
    nan_zip = ROOT / art["companion_nan_zip"]

    assert _sha256(zeros_tif) == art["primary_zeros_tif_sha256"]
    assert _sha256(zeros_zip) == art["primary_zeros_zip_sha256"]
    assert _sha256(nan_tif) == art["companion_nan_tif_sha256"]
    assert _sha256(nan_zip) == art["companion_nan_zip_sha256"]

    # Single-TIFF ZIP roundtrip verification
    for zp, tp in ((zeros_zip, zeros_tif), (nan_zip, nan_tif)):
        with zipfile.ZipFile(zp, "r") as zf:
            names = zf.namelist()
            assert names == [tp.name], f"Expected single TIFF [{tp.name}] in {zp}, got {names}"
            assert hashlib.sha256(zf.read(tp.name)).hexdigest() == _sha256(tp)

    val_zeros = validate_submission(zeros_tif, sample_path, convention="all-finite")
    val_nan = validate_submission(nan_tif, sample_path, convention="nan-outside")
    assert val_zeros["ok_to_upload_format_only"] is True, val_zeros["hard_failures"]
    assert val_nan["ok_to_upload_format_only"] is True, val_nan["hard_failures"]

    with (
        rasterio.open(sample_path) as s_src,
        rasterio.open(labels_path) as l_src,
        rasterio.open(zeros_tif) as z_src,
        rasterio.open(nan_tif) as n_src,
    ):
        footprint = np.isfinite(s_src.read(1))
        catalogue = footprint & (l_src.read(1) == 1)
        z_arr = z_src.read(1)
        n_arr = n_src.read(1)

    # Explicit portal range-error check: "Predicted values must be in range [0, 1]"
    assert np.isfinite(z_arr).all(), "All-finite zeros.tif contains non-finite values"
    assert float(z_arr.min()) >= 0.0 and float(z_arr.max()) <= 1.0
    assert np.isfinite(n_arr[footprint]).all(), "NaN companion contains NaN inside valid footprint"
    assert float(n_arr[footprint].min()) >= 0.0 and float(n_arr[footprint].max()) <= 1.0
    assert np.isnan(n_arr[~footprint]).all(), "NaN companion has finite values outside footprint"
    assert np.array_equal(z_arr[footprint], n_arr[footprint])
    assert set(np.unique(z_arr[footprint]).tolist()).issubset({0.0, 1.0})

    dots = z_arr > 0.5
    assert int(dots.sum()) == 37_654
    d_cat_m = ndi.distance_transform_edt(~catalogue) * 100.0
    min_d_cat_m = float(d_cat_m[dots].min())
    assert min_d_cat_m > 200.0, f"Found emitted dot within <=200 m of catalogue ({min_d_cat_m} m)"

    # Registry cross-check
    sub_reg = json.loads((ROOT / "registry/submissions.json").read_text())
    rec = next(
        (r for r in sub_reg["files"] if r["id"] == "candidate-h31t-transtension-dinkelbach"),
        None,
    )
    assert rec is not None, "H31-T missing from registry/submissions.json"
    assert rec["slot_approved"] is False
    assert rec["sha256_allfinite"] == art["primary_zeros_tif_sha256"]
    assert rec["sha256_nan"] == art["companion_nan_tif_sha256"]
    assert rec["sha256_zip"] == art["primary_zeros_zip_sha256"]

    return {
        "status": "verified",
        "lane_id": "H31-T",
        "primary_zeros_tif_sha256": art["primary_zeros_tif_sha256"],
        "emitted_dots": int(dots.sum()),
        "min_distance_to_catalogue_m": round(min_d_cat_m, 2),
        "gems57_pooled_hide_v2_dti": hd["primary_shared_template_gems57_pooled_hide_v2"][
            "h31t_dinkelbach_dti"
        ],
        "gemsdoe31_confirm_dti": hd["gemsdoe31_holdout_v1_untouched_confirm"][
            "h31t_dinkelbach_dti"
        ],
        "ok_to_download_for_research": True,
        "ok_to_submit": False,
        "slot_approved": False,
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--restore-small-inputs",
        action="store_true",
        help="Restore data/sample_submission.tif and data/labels.tif via verify_current_run.py if absent.",
    )
    args = ap.parse_args()
    if args.restore_small_inputs:
        spec = importlib.util.spec_from_file_location(
            "verify_current_run", ROOT / "scripts/verify_current_run.py"
        )
        assert spec is not None and spec.loader is not None
        vcr = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(vcr)
        vcr.restore_small_inputs()
    summary = verify_h31t()
    print(json.dumps(summary, indent=2))
