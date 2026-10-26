#!/usr/bin/env python3
"""Independent exact-file verification for an RBU31 / RBU31-B run.

Reopens the packaged GeoTIFFs and, without trusting the runner:
* validates format + [0, 1] range against the template (shared validator),
* checks SHA-256 against the run card,
* recomputes the three off-catalogue SGMC proxy DTIs from the TIFF bytes,
* recomputes final-dot 3-px overlap / exact-shared dots vs the nine focus
  sites' hash-verified top rasters,
* verifies the ZIP contains exactly one TIFF with identical bytes.

Usage: verify_regime31.py [--evidence-dir evidence/regime31b]
Exit code 0 iff every recomputation matches the run card (tolerance 1e-9
for DTIs). Writes ``<evidence-dir>/independent_verification.json``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gemsdoe31 import metric  # noqa: E402
from gemsdoe31.submission import validate_submission  # noqa: E402


def sha256_file(path: Path) -> str:
    d = hashlib.sha256()
    with path.open("rb") as h:
        for chunk in iter(lambda: h.read(1 << 20), b""):
            d.update(chunk)
    return d.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--evidence-dir", default="evidence/regime31b")
    args = ap.parse_args()
    ev = ROOT / args.evidence_dir
    rc = json.loads((ev / "run_card.json").read_text())
    name = rc["submission_name"]
    dl = ROOT / "docs/downloads"
    data = ROOT / "data"
    checks: dict[str, bool] = {}
    detail: dict[str, object] = {}

    for conv, key in (("nan-outside", "nan"), ("all-finite", "allfinite")):
        suffix = "nan" if key == "nan" else "allfinite"
        path = dl / f"{name}-{suffix}.tif"
        res = validate_submission(path, data / "sample_submission.tif", convention=conv)
        card_sha = rc["raster_sha256"]["nan_outside" if key == "nan" else "allfinite"]
        checks[f"format_{key}"] = bool(res["ok_to_upload_format_only"])
        checks[f"sha256_{key}"] = sha256_file(path) == card_sha == res["sha256"]
        with rasterio.open(path) as src:
            arr = src.read(1)
        if key == "allfinite":
            checks["allfinite_all_finite_in_0_1"] = bool(
                np.isfinite(arr).all() and float(arr.min()) >= 0.0 and float(arr.max()) <= 1.0)
            detail["allfinite_min_max"] = [float(arr.min()), float(arr.max())]

    zpath = dl / f"{name}-nan.zip"
    with zipfile.ZipFile(zpath) as zf:
        names = zf.namelist()
        checks["zip_single_tif"] = len(names) == 1 and names[0].endswith(".tif")
        payload = zf.read(names[0]) if names else b""
    checks["zip_bytes_equal_nan_tif"] = hashlib.sha256(payload).hexdigest() == rc["raster_sha256"]["nan_outside"]

    with rasterio.open(data / "sample_submission.tif") as src:
        footprint = np.isfinite(src.read(1))
    with rasterio.open(data / "labels.tif") as src:
        catalogue = (src.read(1) == 1) & footprint
    with rasterio.open(data / "external/derived_sgmc_faults_100m_u8.tif") as src:
        sgmc = (src.read(1) == 1) & footprint
    with rasterio.open(data / "prepared/../training_features.tif") as src:
        band_names = [d.split(" - ")[0] for d in src.descriptions]
        det = src.read(band_names.index("det_elev") + 1).astype(np.float32)
    det[~np.isfinite(det) | (np.abs(det) > 1e20)] = np.nan
    d_cat = distance_transform_edt(~catalogue)
    with rasterio.open(dl / f"{name}-allfinite.tif") as src:
        dots = (src.read(1) > 0.5) & footprint
    checks["dots_match_run_card"] = int(dots.sum()) == int(rc["validator_output"]["dots"])
    checks["zero_dots_on_catalogue"] = int((dots & catalogue).sum()) == 0
    checks["zero_dots_within_2px_of_catalogue"] = int((dots & (d_cat <= 2.0)).sum()) == 0

    sgmc_off = sgmc & (d_cat > 3.0)
    pied = footprint & np.isfinite(det) & (det <= 50.0)
    mtn = footprint & np.isfinite(det) & (det > 50.0)
    recomputed = {
        "sgmc_all_dti": float(metric.dti(dots.astype(np.float32), sgmc_off)["DTI"]),
        "sgmc_piedmont_dti": float(metric.dti(dots.astype(np.float32), sgmc_off & pied)["DTI"]),
        "sgmc_mountain_dti": float(metric.dti(dots.astype(np.float32), sgmc_off & mtn)["DTI"]),
    }
    card_proxy = rc["sgmc_proxy_computed_not_a_score"]["rbu31"]
    checks["sgmc_proxies_recomputed_equal"] = all(
        abs(recomputed[k] - float(card_proxy[k])) < 1e-9 for k in recomputed)
    detail["sgmc_recomputed"] = recomputed

    fetch = json.loads((ROOT / "evidence/regime31/peer_fetch.json").read_text())
    overlaps = {}
    for row in fetch["files"]:
        p = ROOT / (row["dest"] if "dest" in row else row["path"])
        with rasterio.open(p) as src:
            peer = (np.nan_to_num(src.read(1), nan=0.0) > 0.5) & footprint
        dist = distance_transform_edt(~peer)
        overlaps[row["repo"]] = {
            "final_dots_within_3px": float((dist[dots] <= 3.0).mean()),
            "exact_shared_dots": int((dots & peer).sum()),
        }
    detail["peer_overlaps_recomputed"] = overlaps
    checks["final_dots_overlap_le_0p70_vs_9_focus_peers"] = all(
        v["final_dots_within_3px"] <= 0.70 for v in overlaps.values())

    ok = all(checks.values())
    out = {"candidate": name, "evidence_dir": args.evidence_dir, "all_checks_pass": ok,
           "checks": checks, "detail": detail,
           "run_card_verdict": rc["verdict"],
           "note": "Recomputed from packaged bytes; surface-level overlap lives in duplicate_canary.json."}
    (ev / "independent_verification.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
