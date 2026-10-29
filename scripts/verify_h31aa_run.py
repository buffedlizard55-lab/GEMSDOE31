#!/usr/bin/env python3
"""Autonomous non-human verification of Lane H31-AA (SLFS) GeoTIFFs, ZIPs,
frozen preregistration, leakage canary, 3-experiment budget, and fail-closed
release-policy compliance.
"""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gemsdoe31.submission import sha256_file, validate_submission  # noqa: E402


def verify(root: Path = ROOT, *, check_only: bool = False) -> dict:
    card = json.loads((root / "evidence/h31aa/run_card.json").read_text())
    pub_card = json.loads((root / "docs/downloads/h31aa-run-card.json").read_text())
    reg_card = json.loads((root / "registry/h31aa_current_run.json").read_text())
    if card != pub_card or card != reg_card:
        raise ValueError("H31-AA run_card copies out of sync")

    pin = json.loads((root / "evidence/h31aa/preregistration_pin.json").read_text())
    prereg_path = root / pin["preregistration"]
    if sha256_file(prereg_path) != pin["sha256"] or card["preregistration"]["sha256"] != pin["sha256"]:
        raise ValueError("H31-AA preregistration SHA-256 mismatch")

    zeros_tif = root / card["files"]["zeros"]
    nan_tif = root / card["files"]["nan"]
    zeros_zip = root / card["files"]["zip"]
    nan_zip = root / card["files"]["nan_zip"]
    for p in (zeros_tif, nan_tif, zeros_zip, nan_zip):
        if not p.is_file():
            raise FileNotFoundError(p)

    if sha256_file(zeros_tif) != card["raster_sha256"]:
        raise ValueError("zeros.tif SHA-256 mismatch")
    if sha256_file(nan_tif) != card["raster_sha256_nan"]:
        raise ValueError("nan.tif SHA-256 mismatch")
    if sha256_file(zeros_zip) != card["zip_sha256"]:
        raise ValueError("zeros.zip SHA-256 mismatch")
    if sha256_file(nan_zip) != card["nan_zip_sha256"]:
        raise ValueError("nan.zip SHA-256 mismatch")

    for zp, tp in ((zeros_zip, zeros_tif), (nan_zip, nan_tif)):
        with zipfile.ZipFile(zp) as zf:
            names = zf.namelist()
            if names != [tp.name]:
                raise ValueError(f"{zp.name} must contain exactly [{tp.name}], got {names}")
            if zf.read(tp.name) != tp.read_bytes():
                raise ValueError(f"{zp.name} member bytes differ from {tp.name}")

    sample = root / "data/sample_submission.tif"
    labels = root / "data/labels.tif"
    checks = {}
    if sample.is_file():
        vz = validate_submission(zeros_tif, sample, convention="all-finite")
        vn = validate_submission(nan_tif, sample, convention="nan-outside")
        if not vz["ok_to_upload_format_only"] or vz["hard_failures"]:
            raise ValueError(f"zeros.tif format validation failed: {vz['hard_failures']}")
        if not vn["ok_to_upload_format_only"] or vn["hard_failures"]:
            raise ValueError(f"nan.tif format validation failed: {vn['hard_failures']}")
        with rasterio.open(zeros_tif) as ds_z, rasterio.open(nan_tif) as ds_n, rasterio.open(sample) as ds_s:
            az = ds_z.read(1, masked=False)
            an = ds_n.read(1, masked=False)
            foot = np.isfinite(ds_s.read(1, masked=False))
        if not np.isfinite(az).all() or float(az.min()) < 0.0 or float(az.max()) > 1.0:
            raise ValueError("zeros.tif has non-finite or out-of-[0,1] values")
        if not np.array_equal(az[foot], an[foot]):
            raise ValueError("zeros.tif and nan.tif differ inside footprint")
        unique_vals = sorted(float(x) for x in np.unique(az[foot]))
        if unique_vals != [0.0, 1.0]:
            raise ValueError(f"Expected binary {{0.0, 1.0}} predictions, got {unique_vals[:10]}")
        n_pos = int((az[foot] > 0).sum())
        if n_pos != 37_654:
            raise ValueError(f"Expected 37,654 positive pixels, got {n_pos}")
        cat_hits = 0
        if labels.is_file():
            with rasterio.open(labels) as ds_l:
                cat = ds_l.read(1) == 1
            cat_hits = int(((az > 0) & cat).sum())
            if cat_hits != 0:
                raise ValueError(f"Found {cat_hits} positive pixels on public catalogue")
        fmt_receipt = dict(
            schema_version=1,
            name=card["submission_name"],
            note=card["note"],
            dots=n_pos,
            dots_on_catalogue=cat_hits,
            files=dict(
                nan=card["files"]["nan"],
                allfinite=card["files"]["zeros"],
                zip=card["files"]["zip"],
            ),
            validation=dict(nan=vn, allfinite=vz),
        )
        fmt_path = root / "docs/downloads" / f"{card['submission_name']}-format-check.json"
        if check_only:
            if not fmt_path.is_file():
                raise FileNotFoundError(fmt_path)
            saved_fmt = json.loads(fmt_path.read_text())
            if saved_fmt != fmt_receipt:
                raise ValueError("Saved format-check.json differs from fresh validation")
        else:
            fmt_path.write_text(json.dumps(fmt_receipt, indent=1, allow_nan=False) + "\n")
        checks["grid_and_range_verified"] = True
        checks["format_receipt"] = str(fmt_path.relative_to(root))
    else:
        checks["grid_and_range_verified"] = "skipped (data/sample_submission.tif not restored)"
        # Never silently downgrade a committed receipt: a write-mode run without the
        # template must not replace a previously recorded passing grid check.
        _prev = root / "evidence/h31aa/verification_receipt.json"
        if not check_only and _prev.is_file():
            if json.loads(_prev.read_text()).get("checks", {}).get("grid_and_range_verified") is True:
                raise ValueError(
                    "Refusing to overwrite a passing H31-AA receipt without data/sample_submission.tif; "
                    "restore the pinned small inputs and rerun."
                )

    canary = json.loads((root / "evidence/h31aa/canary.json").read_text())
    if not canary["all_pass"] or max(r["max_two_sided_auc"] for r in canary["rows"]) > 0.90:
        raise ValueError("Canary check failed")

    if not (0 < card["note_chars"] <= 140 and len(card["note"]) == card["note_chars"]):
        raise ValueError("Submission note length invalid")
    if card["verdict"] != "negative" or card["ok_to_submit"] is not False or card["slot_approved"] is not False:
        raise ValueError("Fail-closed governance violated on H31-AA run card")
    if card["leaderboard_estimate"] is not None:
        raise ValueError("leaderboard_estimate must be None")

    out = dict(
        lane="H31-AA",
        status="VERIFIED",
        submission_name=card["submission_name"],
        raster_sha256_zeros=card["raster_sha256"],
        raster_sha256_nan=card["raster_sha256_nan"],
        zip_sha256_zeros=card["zip_sha256"],
        preregistration_sha256=pin["sha256"],
        experiments_executed=3,
        max_canary_two_sided_auc=max(r["max_two_sided_auc"] for r in canary["rows"]),
        verdict=card["verdict"],
        ok_to_download_for_research=card["ok_to_download_for_research"],
        ok_to_submit=card["ok_to_submit"],
        slot_approved=card["slot_approved"],
        checks=checks,
    )
    rec_path = root / "evidence/h31aa/verification_receipt.json"
    if check_only:
        if not rec_path.is_file():
            raise FileNotFoundError(rec_path)
        if json.loads(rec_path.read_text()) != out:
            raise ValueError("Saved verification_receipt.json differs from fresh verification")
    else:
        rec_path.write_text(json.dumps(out, indent=2) + "\n")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="Verify receipts without rewriting files")
    args = ap.parse_args()
    res = verify(check_only=args.check)
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
