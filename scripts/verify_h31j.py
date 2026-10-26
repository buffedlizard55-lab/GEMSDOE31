#!/usr/bin/env python3
"""Zero-human-intervention automated gate & GeoTIFF/ZIP verifier for Lane H31-J (TGTD-Submod).

Independently re-verifies from disk bytes:
  1. Immutable shared template SHA-256 pins (`registry/template_pins.json`) and preregistration pin.
  2. Primary `-zeros.tif` / `-zeros.zip` and companion `-nan.tif` / `-nan.zip` GeoTIFFs:
     - 1-band float32, EPSG:32611, shape (3730, 3292), exact 100 m UTM transform
     - Regression lock against "Predicted values must be in range [0, 1]":
       * `-zeros.tif`: all 12,279,160 cells finite in [0.0, 1.0], zeros outside footprint, {0.0, 1.0} inside
       * `-nan.tif`: all 5,167,373 footprint cells finite in [0.0, 1.0], exact NaN outside, pixel-identical inside
     - Exact 37,654 emitted dots, 0 public-catalogue overlap, 0 <= 200 m (2 px) dead-collar overlap
     - Single-file ZIP roundtrip byte-for-byte SHA-256 identity and packed support digest match (`ab35d4e8`)
  3. Gate G2 single-feature leakage canary (260 fold-feature checks <= 0.90, no `dist_known_fault_px` loaded).
  4. Gate G3a discrete sibling registry uniqueness (pre-placement |rho| <= 0.90; final dots |rho| <= 0.90 & 3-px <= 0.70)
     and Gate G3b literal 5x5 shared-registry calibration-lattice disclosure.
  5. Gate G4a (seed=31) & Gate G4b (untouched seed=32) HOLDOUT-DTI pooled results (21.3 km buffer, positive paired 95% CI,
     4/4 quadrant sweep on both seeds = 8/8 quadrants), Gate G5 own-method OOF residual variogram (<= 21.3 km),
     Gate G6 off-catalogue SGMC (> 300 m) proxy audit, and Rule 6 `slot_approved == False`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "vendor"), str(ROOT / "scripts")]

import numpy as np  # noqa: E402
import rasterio  # noqa: E402
from scipy.ndimage import distance_transform_edt  # noqa: E402

from gemsdoe31.submission import sha256_file, validate_submission  # noqa: E402
from verify_current_run import restore_small_inputs  # noqa: E402


EXPECTED_SUB_NAME = "gemsdoe31-tgtd-submod-37654-20261025-ab35d4e8"
EXPECTED_SHAPE = (3730, 3292)
EXPECTED_TRANSFORM = (100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)
EXPECTED_FOOTPRINT_PIXELS = 5_167_373
EXPECTED_DOTS = 37_654


def _verify_single_tiff_zip(zip_path: Path, expected_tif: Path, expected_zip_sha: str, expected_zip_bytes: int) -> None:
    if not zip_path.is_file():
        raise FileNotFoundError(f"Missing ZIP archive: {zip_path}")
    actual_zip_sha = sha256_file(zip_path)
    if actual_zip_sha != expected_zip_sha:
        raise ValueError(f"ZIP SHA-256 mismatch for {zip_path.name}: {actual_zip_sha} != {expected_zip_sha}")
    if zip_path.stat().st_size != expected_zip_bytes:
        raise ValueError(f"ZIP byte count mismatch for {zip_path.name}")
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        if names != [expected_tif.name]:
            raise ValueError(f"ZIP {zip_path.name} must contain exactly [{expected_tif.name}], got {names}")
        extracted_sha = hashlib.sha256(zf.read(expected_tif.name)).hexdigest()
    tif_sha = sha256_file(expected_tif)
    if extracted_sha != tif_sha:
        raise ValueError(f"ZIP member bytes in {zip_path.name} differ from {expected_tif.name}")


def verify_h31j(root: Path = ROOT) -> dict:
    root = Path(root)
    card_path = root / "evidence/h31j/run_card.json"
    if not card_path.is_file():
        raise FileNotFoundError(card_path)
    card = json.loads(card_path.read_text())

    # 1. Run card copies, template pins, and governance locks
    if card["submission_name"] != EXPECTED_SUB_NAME:
        raise ValueError(f"Unexpected submission_name: {card['submission_name']}")
    if card["slot_approved"] is not False:
        raise ValueError("Rule 6 violation: slot_approved must remain False until human weekly-slot sign-off")
    if not (1 <= len(card["portal_note"]) <= 140) or card["portal_note_length"] != len(card["portal_note"]):
        raise ValueError(f"Invalid portal_note length: {len(card['portal_note'])}")
    if card["preregistration"]["experiments_executed"] > card["preregistration"]["experiments_budget_max"]:
        raise ValueError("Experiment budget exceeded")
    prereg_path = root / card["preregistration"]["path"]
    if sha256_file(prereg_path) != card["preregistration"]["sha256"]:
        raise ValueError("Preregistration file drifted after H31-J run")

    for copy_rel in (
        f"docs/downloads/{EXPECTED_SUB_NAME}-run-card.json",
        "docs/downloads/h31j-run-card.json",
    ):
        copy_path = root / copy_rel
        if not copy_path.is_file() or json.loads(copy_path.read_text()) != card:
            raise ValueError(f"H31-J run-card copy missing or drifted: {copy_rel}")

    pins = json.loads((root / "registry/template_pins.json").read_text())
    for name, item in pins["files"].items():
        if sha256_file(root / "vendor/gems57" / name) != item["sha256"]:
            raise ValueError(f"Immutable vendor/gems57/{name} drifted from template_pins.json")

    # 2. GeoTIFF & [0, 1] range & single-TIFF ZIP verification
    art = card["artifacts"]
    zeros_tif = root / art["primary_zeros_tif"]
    zeros_zip = root / art["primary_zeros_zip"]
    nan_tif = root / art["companion_nan_tif"]
    nan_zip = root / art["companion_nan_zip"]

    if sha256_file(zeros_tif) != art["primary_zeros_sha256"]:
        raise ValueError("Primary -zeros.tif SHA-256 mismatch")
    if sha256_file(nan_tif) != art["companion_nan_sha256"]:
        raise ValueError("Companion -nan.tif SHA-256 mismatch")

    _verify_single_tiff_zip(zeros_zip, zeros_tif, art["primary_zeros_zip_sha256"], art["primary_zeros_zip_bytes"])
    _verify_single_tiff_zip(nan_zip, nan_tif, art["companion_nan_zip_sha256"], art["companion_nan_zip_bytes"])

    template_path = root / "data/sample_submission.tif"
    labels_path = root / "data/labels.tif"
    if not template_path.is_file() or not labels_path.is_file():
        raise FileNotFoundError(
            "Missing data/sample_submission.tif or data/labels.tif; run with --restore-small-inputs first"
        )

    v_zeros = validate_submission(zeros_tif, template_path, convention="all-finite")
    v_nan = validate_submission(nan_tif, template_path, convention="nan-outside")
    if not v_zeros["ok_to_upload_format_only"]:
        raise ValueError(f"-zeros.tif failed format check: {v_zeros['hard_failures']}")
    if not v_nan["ok_to_upload_format_only"]:
        raise ValueError(f"-nan.tif failed format check: {v_nan['hard_failures']}")

    with rasterio.open(template_path) as ds_tmpl:
        fp = np.isfinite(ds_tmpl.read(1))
    if int(fp.sum()) != EXPECTED_FOOTPRINT_PIXELS:
        raise ValueError(f"Unexpected footprint count: {int(fp.sum())}")

    with rasterio.open(zeros_tif) as ds0:
        arr0 = ds0.read(1)
        if ds0.count != 1 or ds0.dtypes != ("float32",) or str(ds0.crs) != "EPSG:32611":
            raise ValueError("Primary -zeros.tif band/dtype/CRS contract failed")
        if ds0.shape != EXPECTED_SHAPE or tuple(ds0.transform)[:6] != EXPECTED_TRANSFORM:
            raise ValueError("Primary -zeros.tif shape/transform contract failed")

    with rasterio.open(nan_tif) as dsn:
        arrn = dsn.read(1)
        if dsn.count != 1 or dsn.dtypes != ("float32",) or str(dsn.crs) != "EPSG:32611":
            raise ValueError("Companion -nan.tif band/dtype/CRS contract failed")
        if dsn.shape != EXPECTED_SHAPE or tuple(dsn.transform)[:6] != EXPECTED_TRANSFORM:
            raise ValueError("Companion -nan.tif shape/transform contract failed")

    # Explicit "Predicted values must be in range [0, 1]" defense
    if not np.isfinite(arr0).all():
        raise ValueError("-zeros.tif contains NaN or Inf values!")
    if float(arr0.min()) < 0.0 or float(arr0.max()) > 1.0:
        raise ValueError(f"-zeros.tif out of [0, 1] range: [{arr0.min()}, {arr0.max()}]")
    if float(np.abs(arr0[~fp]).max()) != 0.0:
        raise ValueError("-zeros.tif has non-zero values outside footprint!")
    if not np.isfinite(arrn[fp]).all():
        raise ValueError("-nan.tif contains NaN/Inf inside active footprint!")
    if not np.isnan(arrn[~fp]).all():
        raise ValueError("-nan.tif contains finite values outside active footprint!")
    if not np.array_equal(arr0[fp], arrn[fp]):
        raise ValueError("Footprint predictions differ between -zeros.tif and -nan.tif!")
    uniq_vals = set(np.unique(arr0[fp]).tolist())
    if not uniq_vals.issubset({0.0, 1.0}):
        raise ValueError(f"Expected binary {{0.0, 1.0}} dot raster, got unique values { sorted(uniq_vals)[:10] }")

    dots = arr0 > 0.5
    if int(dots.sum()) != EXPECTED_DOTS:
        raise ValueError(f"Expected {EXPECTED_DOTS} dots, found {int(dots.sum())}")
    support_sha = hashlib.sha256(np.packbits(dots.ravel()).tobytes()).hexdigest()
    if support_sha != art["support_packed_sha256"] or not EXPECTED_SUB_NAME.endswith(support_sha[:8]):
        raise ValueError("Packed dot-support SHA-256 mismatch!")

    with rasterio.open(labels_path) as ds_lbl:
        cat = (ds_lbl.read(1) == 1) & fp
    if int((dots & cat).sum()) != 0:
        raise ValueError("Emitted dots overlap public fault catalogue!")
    d_cat = distance_transform_edt(~cat)
    if int((dots & (d_cat <= 2.0)).sum()) != 0:
        raise ValueError("Emitted dots violate the > 2.0 px (200 m) dead-collar exclusion!")

    # 3. Leakage canary (G2)
    canary = json.loads((root / "evidence/h31j/leakage_canary_seed31.json").read_text())
    if not canary["pass"] or canary["dist_known_fault_px_loaded"] is not False:
        raise ValueError("Gate G2 leakage canary failed or loaded catalogue distance")
    if canary["checked_fold_feature_pairs"] != 260 or canary["max_symmetric_auc"] > 0.90:
        raise ValueError("Gate G2 single-feature AUC exceeded 0.90")
    if canary["max_missingness_symmetric_auc"] > 0.90:
        raise ValueError("Gate G2 single-feature missingness AUC exceeded 0.90")

    # 4. Uniqueness (G3a discrete & G3b literal shared-registry disclosure)
    pre_nov = json.loads((root / "evidence/h31j/novelty_preplacement.json").read_text())
    post_nov = json.loads((root / "evidence/h31j/novelty_final_dots.json").read_text())
    pre_arm = pre_nov["arms"]["h31j3_dual_submod"]
    post_arm = post_nov["arms"]["h31j3_dual_submod"]
    if pre_arm["max_abs_rho"] > 0.90 or not pre_nov["continuous_surface_rho_gate_pass"]:
        raise ValueError("Gate G3a pre-placement continuous |rho| > 0.90")
    if not post_arm["pass_"] or post_arm["max_abs_rho"] > 0.90 or post_arm["max_overlap"] > 0.70:
        raise ValueError("Gate G3a post-placement uniqueness failed")
    g3b = card["uniqueness_summary"]["shared_registry_g3b"]["post_placement_final_dots"]
    if g3b["literal_overlap_le_0p70"] is not False:
        raise ValueError("Gate G3b synthetic 5x5 lattice overlap must be transparently disclosed as False")

    # 5. Holdout DTI (G4a screen + G4b untouched confirmation), variogram (G5), and SGMC proxy (G6)
    hd = card["holdout_dti"]
    if hd["evidence_class"] != "HOLDOUT-DTI" or hd["evaluator_version"] != "gems57-pooled-hide-v2" or hd["buffer_px"] != 213:
        raise ValueError("Holdout evaluator contract mismatch")
    for split_key, expected_pos in (("screen_seed31", 2901), ("confirmation_seed32", 2808)):
        sp = hd[split_key]
        if sp["withheld_positives"] != expected_pos or not sp["gate_passed"]:
            raise ValueError(f"{split_key} failed gate or withheld count check")
        if sp["quadrant_wins_vs_physical_hgb"] != 4:
            raise ValueError(f"{split_key} did not sweep 4/4 quadrants")
        if sp["paired_vs_physical_hgb"]["ci95"][0] <= 0.0:
            raise ValueError(f"{split_key} paired 95% CI lower bound <= 0")
        for arm_score in sp["scores"].values():
            if arm_score["evidence_class"] != "HOLDOUT-DTI":
                raise ValueError(f"Missing HOLDOUT-DTI evidence class in {split_key}")

    vario = card["own_method_variogram_summary"]
    if not vario["collar_covers_point_practical_range"] or vario["practical_range_95_sill_m"] > 21300.0:
        raise ValueError("Own-method OOF residual practical range exceeds 21.3 km holdout buffer")

    sgmc = card["off_catalogue_sgmc_proxy"]
    j3_sgmc = sgmc["h31j3_dual_submod"]
    h33_sgmc = sgmc["gemsdoe32_h33_2_b2"]
    if not str(j3_sgmc["evidence_class"]).startswith("HOLDOUT-PROXY-SGMC"):
        raise ValueError("SGMC proxy must carry HOLDOUT-PROXY-SGMC evidence class")
    if j3_sgmc["sgmc_all_elevation_dti"] <= h33_sgmc["sgmc_all_elevation_dti"]:
        raise ValueError("H31-J3 did not beat H33-2-B2 on all-elevation off-catalogue SGMC proxy")
    if j3_sgmc["sgmc_piedmont_lt100m_dti"] <= h33_sgmc["sgmc_piedmont_lt100m_dti"]:
        raise ValueError("H31-J3 did not beat H33-2-B2 on piedmont off-catalogue SGMC proxy")

    return {
        "ok": True,
        "submission_name": EXPECTED_SUB_NAME,
        "dots": EXPECTED_DOTS,
        "screen_dti": hd["screen_seed31"]["scores"]["h31j3_dual_submod"]["dti"],
        "confirm_dti": hd["confirmation_seed32"]["scores"]["h31j3_dual_submod"]["dti"],
        "sgmc_all_dti": j3_sgmc["sgmc_all_elevation_dti"],
        "sgmc_piedmont_dti": j3_sgmc["sgmc_piedmont_lt100m_dti"],
        "slot_approved": card["slot_approved"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--restore-small-inputs", action="store_true")
    args = parser.parse_args()
    if args.restore_small_inputs:
        restore_small_inputs(ROOT)
    summary = verify_h31j(ROOT)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
