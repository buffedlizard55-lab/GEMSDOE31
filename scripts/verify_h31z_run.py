#!/usr/bin/env python3
"""Independent automated verification of the packaged H31-Z run (no human inspector).

Re-reads committed TIFF/ZIP bytes without trusting builder state: SHA-256 vs
run card, both validator conventions, binary {0,1} support, dot count, ZIP
single-TIFF byte identity, preregistration hash, catalogue-flank distance
(>2 px), minimum dot spacing (>=2.8 px), and (when mirror data present)
off-catalogue SGMC DTI recomputation vs the card. A scientific verdict of
"negative" is a result, not a verification failure.
"""
from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "vendor")]

from gemsdoe31.submission import sha256_file, validate_submission  # noqa: E402

DL = ROOT / "docs" / "downloads"


def main() -> int:
    failures: list[str] = []
    card = json.loads((ROOT / "evidence/h31z/run_card.json").read_text())
    card_copy = json.loads((DL / "h31z-run-card.json").read_text())
    if card != card_copy:
        failures.append("downloaded run-card copy differs from evidence/h31z/run_card.json")
    registry_copy = json.loads((ROOT / "registry/h31z_current_run.json").read_text())
    if card != registry_copy:
        failures.append("registry/h31z_current_run.json differs from evidence card")
    if sha256_file(ROOT / card["preregistration"]) != card["preregistration_sha256"]:
        failures.append("preregistration sha256 mismatch")

    template = ROOT / "data/sample_submission.tif"
    if not template.is_file():
        template = DL / "gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif"
    name = card["submission_name"]
    n_dots_card = card["validator"]["zeros"]["grid"]["positive_pixels_inside"]
    results = {}
    dots = None
    for kind, convention, key in (("zeros", "all-finite", "zeros"), ("nan", "nan-outside", "nan")):
        path = ROOT / card["files"][key]
        want_sha = card["raster_sha256"] if kind == "zeros" else card["raster_sha256_nan"]
        if sha256_file(path) != want_sha:
            failures.append(f"{kind}: sha256 mismatch vs run card")
        receipt = validate_submission(path, template, convention=convention)
        if receipt["hard_failures"]:
            failures.append(f"{kind}: validator hard failures {receipt['hard_failures']}")
        with rasterio.open(path) as ds:
            a = ds.read(1)
            if ds.count != 1 or ds.dtypes != ("float32",) or ds.crs.to_epsg() != 32611:
                failures.append(f"{kind}: band/dtype/CRS drift")
        finite = a[np.isfinite(a)]
        if set(np.unique(finite).tolist()) != {0.0, 1.0}:
            failures.append(f"{kind}: finite values are not exactly {{0,1}}")
        if kind == "zeros" and not np.isfinite(a).all():
            failures.append("zeros: all-finite file contains non-finite cells ([0,1] portal risk)")
        if int((a == 1).sum()) != n_dots_card:
            failures.append(f"{kind}: dot count {int((a == 1).sum())} != card {n_dots_card}")
        zpath = ROOT / card["files"]["zip" if kind == "zeros" else "nan_zip"]
        with zipfile.ZipFile(zpath) as z:
            if z.namelist() != [path.name] or z.read(path.name) != path.read_bytes():
                failures.append(f"{kind}: ZIP is not a byte-identical single-TIFF archive")
        if kind == "zeros":
            dots = a == 1
        results[kind] = dict(sha256=want_sha, validator_hard_failures=receipt["hard_failures"],
                             dots=int((a == 1).sum()))
    assert dots is not None
    support_sha = __import__("hashlib").sha256(np.packbits(dots.ravel()).tobytes()).hexdigest()
    if support_sha != card["support_sha256"]:
        failures.append("dot support sha256 mismatch vs card")
    ys, xs = np.nonzero(dots)
    tree = cKDTree(np.column_stack([ys, xs]).astype(float))
    dist, _ = tree.query(np.column_stack([ys, xs]).astype(float), k=2)
    min_spacing = float(dist[:, 1].min())
    if min_spacing < 2.8 - 1e-9:
        failures.append(f"minimum dot spacing {min_spacing:.3f} px < 2.8 px")

    checks = dict(min_spacing_px=min_spacing, dots=int(dots.sum()))
    labels = ROOT / "data/labels.tif"
    sgmc_path = ROOT / "data/external/derived_sgmc_faults_100m_u8.tif"
    if labels.is_file() and (ROOT / "data/sample_submission.tif").is_file():
        with rasterio.open(labels) as ds:
            cat = ds.read(1) == 1
        d_cat = distance_transform_edt(~cat)
        min_cat = float(d_cat[dots].min())
        checks["min_catalogue_distance_px"] = min_cat
        if min_cat <= 2.0:
            failures.append(f"dots within 2 px of catalogue (min {min_cat:.3f})")
        if sgmc_path.is_file():
            from gems57 import metric as vmetric
            with rasterio.open(ROOT / "data/sample_submission.tif") as ds:
                foot = np.isfinite(ds.read(1))
            with rasterio.open(sgmc_path) as ds:
                sgmc = (ds.read(1) == 1) & foot
            off = sgmc & (d_cat > 3.0)
            r = vmetric.dti_exact(dots.astype(np.float32), off, valid=foot)
            checks["sgmc_dti_recomputed"] = float(r["dti"])
            checks["sgmc_dti_card"] = float(card["sgmc_proxy"]["candidate"]["dti"])
            if abs(checks["sgmc_dti_recomputed"] - checks["sgmc_dti_card"]) > 1e-9:
                failures.append("SGMC DTI recomputation disagrees with card")
    else:
        checks["catalogue_sgmc_checks"] = "skipped (mirror data absent)"

    gates = card["gates"]
    promote = all(gates[k] for k in gates if k.startswith("G"))
    if (card["verdict"] == "promote") != promote or card["ok_to_submit"] != promote:
        failures.append("verdict/ok_to_submit inconsistent with gates")
    out = dict(name=name, failures=failures, ok=not failures, results=results, checks=checks,
               verdict=card["verdict"], organizer_acceptance_verified=False)
    dest = ROOT / "evidence/h31z/independent_verification.json"
    dest.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
