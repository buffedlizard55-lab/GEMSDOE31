#!/usr/bin/env python3
"""Verify the frozen negative deliverable; optionally reproduce its exact surface.

This is an integrity check, not a new experiment or permission to retune a
closed lane. No prediction file is overwritten and no competition is contacted.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "vendor"), str(ROOT / "scripts")]
from gemsdoe31.decision import make_decision  # noqa: E402
from gemsdoe31.submission import sha256_file  # noqa: E402
from gemsdoe31.transfer import build_transfer_surface  # noqa: E402
from prepare_shared_cache import CACHE_ROOT, prepare, verify_template  # noqa: E402


def load(name):
    return json.loads((ROOT / "evidence/tgj31" / name).read_text())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rebuild-surface", action="store_true",
                    help="exact fixed-code reconstruction using the restored original-template cache")
    args = ap.parse_args()
    verify_template()
    card = load("run_card.json")
    tif, archive = (ROOT / card["files"][k] for k in ("tif", "zip"))
    if sha256_file(tif) != card["raster_sha256"]:
        raise AssertionError("delivered TIFF bytes changed")
    with zipfile.ZipFile(archive) as z:
        if z.namelist() != [tif.name] or z.read(tif.name) != tif.read_bytes():
            raise AssertionError("ZIP must contain exactly the byte-identical TIFF")
    with rasterio.open(tif) as ds:
        a = ds.read(1)
        if ds.count != 1 or ds.dtypes != ("float32",) or ds.crs.to_epsg() != 32611:
            raise AssertionError("GeoTIFF grid/dtype contract failed")
        if ds.shape != (3730, 3292) or tuple(ds.transform)[:6] != (100, 0, 243350, 0, -100, 4508550):
            raise AssertionError("GeoTIFF grid/transform contract failed")
        if not np.isfinite(a).all() or a.min() < 0 or a.max() > 1:
            raise AssertionError("Predicted values must be in range [0, 1]")
    if len(card["note"]) > 140 or card["safe_to_submit"] or card["verdict"] != "negative":
        raise AssertionError("closed negative result must remain clearly blocked")
    decision = make_decision(card, load("holdout.json"), load("registry_surface.json"),
                             load("registry_final_support.json"), load("registry_universal_blocker.json"),
                             load("folds.json"))
    (ROOT / "evidence/tgj31/decision.json").write_text(json.dumps(decision, indent=1, allow_nan=False) + "\n")
    if args.rebuild_surface:
        if sha256_file(ROOT / "src/gemsdoe31/transfer.py") != card["lineage"]["feature_code_sha256"]:
            raise AssertionError("cannot reproduce with drifted feature code")
        prepare()
        with rasterio.open(ROOT / "data/sample_submission.tif") as ref:
            fp = np.isfinite(ref.read(1))
        with rasterio.open(ROOT / "data/labels.tif") as src:
            cat = (src.read(1) > 0) & fp
        m = np.load(CACHE_ROOT / ".cache/features/band-02.npy", mmap_mode="r")
        g = np.load(CACHE_ROOT / ".cache/features/band-13.npy", mmap_mode="r")
        response, _, _, _ = build_transfer_surface(m, g, fp)
        buffer = io.BytesIO()
        np.save(buffer, response)
        if hashlib.sha256(buffer.getvalue()).hexdigest() != card["unplaced_surface_npy_sha256"]:
            raise AssertionError("unplaced physical surface is not reproducible")
        response[cat] = 0
        np.testing.assert_array_equal(a, response)
    print(json.dumps({"tif_sha256_verified": True, "single_tiff_zip_verified": True,
                      "bounded_finite_exact_grid": True, "reconstructed_surface_exact": args.rebuild_surface,
                      "decision": decision["verdict"], "safe_to_submit": False,
                      "failed_gates": decision["failed_gates"]}, indent=1))


if __name__ == "__main__":
    main()
