#!/usr/bin/env python3
"""Automated non-human verification of the 2026-10-26 H31-S (UDAP-SSLIC) deliverables."""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src")]

from gemsdoe31.submission import (  # noqa: E402
    EXPECTED_CRS_EPSG,
    EXPECTED_FOOTPRINT_PIXELS,
    EXPECTED_SHAPE,
    EXPECTED_TRANSFORM,
    sha256_file,
    validate_submission,
)


def verify_h31s(root: Path = ROOT) -> dict:
    rc_path = root / "evidence/h31s/run_card.json"
    dl_rc_path = root / "docs/downloads/h31s-run-card.json"
    reg_rc_path = root / "registry/h31s_current_run.json"
    for p in (rc_path, dl_rc_path, reg_rc_path):
        if not p.is_file():
            raise FileNotFoundError(f"Missing H31-S run card: {p}")

    rc = json.loads(rc_path.read_text())
    if json.loads(dl_rc_path.read_text()) != rc or json.loads(reg_rc_path.read_text()) != rc:
        raise ValueError("H31-S run card copies drifted out of sync")

    art = rc["artifact"]
    zeros_path = root / art["file_zeros"]
    nan_path = root / art["file_nan"]
    zip_path = root / art["zip_zeros"]
    rec_path = root / art["receipt_json"]
    tmpl_path = root / "data/sample_submission.tif"
    lbl_path = root / "data/labels.tif"

    if sha256_file(zeros_path) != art["sha256_zeros"] or zeros_path.stat().st_size != art["bytes_zeros"]:
        raise ValueError("H31-S zeros GeoTIFF hash/size mismatch")
    if sha256_file(nan_path) != art["sha256_nan"] or nan_path.stat().st_size != art["bytes_nan"]:
        raise ValueError("H31-S nan GeoTIFF hash/size mismatch")
    if sha256_file(zip_path) != art["sha256_zip"] or zip_path.stat().st_size != art["bytes_zip"]:
        raise ValueError("H31-S ZIP hash/size mismatch")

    with zipfile.ZipFile(zip_path) as zf:
        if zf.namelist() != [zeros_path.name] or zf.read(zeros_path.name) != zeros_path.read_bytes():
            raise ValueError("H31-S single-TIFF ZIP round-trip mismatch")

    val_zeros = validate_submission(zeros_path, tmpl_path, convention="all-finite")
    val_nan = validate_submission(nan_path, tmpl_path, convention="nan-outside")
    if not val_zeros["ok_to_upload_format_only"] or not val_nan["ok_to_upload_format_only"]:
        raise ValueError("H31-S GeoTIFF failed automated template/range validation")

    with rasterio.open(tmpl_path) as ds_t, rasterio.open(lbl_path) as ds_l:
        fp = np.isfinite(ds_t.read(1))
        cat = ds_l.read(1) == 1
    assert int(fp.sum()) == EXPECTED_FOOTPRINT_PIXELS

    with rasterio.open(zeros_path) as ds_z, rasterio.open(nan_path) as ds_n:
        for ds in (ds_z, ds_n):
            assert ds.shape == EXPECTED_SHAPE
            assert ds.count == 1
            assert ds.dtypes == ("float32",)
            assert ds.crs.to_epsg() == EXPECTED_CRS_EPSG
            assert ds.transform == EXPECTED_TRANSFORM
        az = ds_z.read(1)
        an = ds_n.read(1)

    # All-finite zeros variant cannot trigger "Predicted values must be in range [0, 1]" even on unmasked portals
    assert bool(np.isfinite(az).all())
    assert float(az.min()) >= 0.0 and float(az.max()) <= 1.0
    assert bool((az[~fp] == 0.0).all())
    # NaN-outside variant matches official sample_submission NaN mask pixel-for-pixel
    assert bool(np.isfinite(an[fp]).all())
    assert float(an[fp].min()) >= 0.0 and float(an[fp].max()) <= 1.0
    assert bool(np.isnan(an[~fp]).all())
    assert np.array_equal(az[fp], an[fp])

    supp = fp & (az > 0.0)
    assert int(supp.sum()) == art["positive_pixels"] == 37_654
    assert int((supp & cat).sum()) == 0
    assert 1 <= len(art["note_140"]) <= 140

    gov = rc["governance"]
    assert gov["ok_to_download_for_research"] is True
    assert gov["ok_to_submit"] is False
    assert gov["slot_approved"] is False
    assert gov["weekly_slot_spent"] is False
    assert rec_path.is_file()

    return {
        "ok_to_download_for_research": True,
        "ok_to_submit": False,
        "slot_approved": False,
        "verdict": gov["verdict"],
        "name": art["name"],
        "sha256_zeros": art["sha256_zeros"],
        "sha256_nan": art["sha256_nan"],
        "sha256_zip": art["sha256_zip"],
        "positive_pixels": int(supp.sum()),
        "note_length": len(art["note_140"]),
    }


def main() -> None:
    res = verify_h31s(ROOT)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
