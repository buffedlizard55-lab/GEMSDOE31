#!/usr/bin/env python3
"""Validate the restored inputs and build a disk-backed feature stack on the competition grid.

The stack is written to ``data/prepared/features.f32`` (float32, band-major memmap) with a JSON
sidecar listing bands and quantisation. ``--verify-only`` performs the hash/grid checks alone.

Inputs are owner-mirror files (see ``registry/data_manifest.json``): byte identity to the mirror is
verified, organizer authenticity is not claimed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.signal import fftconvolve

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gemsdoe31.raster import CRS_EPSG, FOOTPRINT_PIXELS, SHAPE, TRANSFORM  # noqa: E402

COMPETITION_BANDS = [
    "mag_anom", "rtp", "tmi_hg", "geod_2ndinv", "iso_grav_anom_slope", "tc", "geod_shearrate",
    "geod_dilaterate", "tmi_vg", "deq_n100a15", "iso_grav_anom_vg", "det_elev", "iso_grav_anom",
    "tmi", "depth_to_base_surf", "ieq_n100a15", "cond_surf", "iso_grav_anom_hg", "det_elev_slope",
]
LIDAR_BANDS = ["ex_max", "ex_mean", "step_max", "lapneg_max", "lappos_max", "downface_max",
               "upface_max", "cross_max", "relief", "coh100", "strike", "valid"]
RAD_BANDS = ["K", "Th", "U", "TC"]
EXT_BANDS = ["ThK", "UK", "UTh", "TMI_up150"]
# A static cache must never contain distances to catalogue or evaluation truth.
# Catalogue features, if a future lane needs them, belong inside the fold-visible
# context builder. SGMC is an evaluation instrument, never a predictor.
DERIVED_BANDS = ["mean_k_500m", "upface_minus_downface", "th_minus_k"]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(manifest: dict, data_dir: Path) -> list[dict]:
    rows = []
    for entry in manifest["files"]:
        path = data_dir / entry["dest"]
        row = {"id": entry["id"], "dest": entry["dest"], "exists": path.is_file()}
        if row["exists"]:
            row["bytes"] = path.stat().st_size
            row["sha256_match"] = sha256_file(path) == entry["sha256"]
            with rasterio.open(path) as src:
                row["shape"] = list(src.shape)
                row["crs_epsg"] = src.crs.to_epsg() if src.crs else None
                row["dtype"] = src.dtypes[0]
                row["bands"] = src.count
                row["transform"] = list(src.transform)[:6]
                row["grid_matches"] = (src.shape == SHAPE and row["crs_epsg"] == CRS_EPSG
                                       and tuple(src.transform)[:6] == tuple(TRANSFORM))
        rows.append(row)
    return rows


def build(data_dir: Path, out_dir: Path, *, include_derived: bool = True) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    names = COMPETITION_BANDS + LIDAR_BANDS + RAD_BANDS + EXT_BANDS
    if include_derived:
        names += DERIVED_BANDS
    stack = np.memmap(out_dir / "features.f32", dtype=np.float32, mode="w+", shape=(len(names),) + SHAPE)
    with rasterio.open(data_dir / "training_features.tif") as src:
        assert [d.split(" - ")[0] for d in src.descriptions] == COMPETITION_BANDS, "band order drift"
        for i in range(len(COMPETITION_BANDS)):
            band = src.read(i + 1, masked=True).filled(np.nan).astype(np.float32)
            band[(~np.isfinite(band)) | (np.abs(band) > 1e30)] = np.nan
            stack[i] = band
    base = len(COMPETITION_BANDS)
    for offset, path in ((0, "external/lidar_scarp_features_u8.tif"), (len(LIDAR_BANDS), "external/geodawn_rad_u8.tif"),
                         (len(LIDAR_BANDS) + len(RAD_BANDS), "external/geodawn_extensions_u8.tif")):
        with rasterio.open(data_dir / path) as src:
            for b in range(src.count):
                band = src.read(b + 1).astype(np.float32)
                band[band == 0] = np.nan            # 0 marks "no survey coverage" in these layers
                stack[base + offset + b] = band
    if include_derived:
        derived = base + len(LIDAR_BANDS) + len(RAD_BANDS) + len(EXT_BANDS)
        potassium = stack[base + len(LIDAR_BANDS)].astype(np.float32)
        finite = np.isfinite(potassium).astype(np.float32)
        filled = np.nan_to_num(potassium, nan=0.0)
        box = np.ones((5, 5), np.float32)
        numerator = fftconvolve(filled, box, mode="same")
        denominator = fftconvolve(finite, box, mode="same")
        with np.errstate(invalid="ignore", divide="ignore"):
            stack[derived] = np.where(denominator > 0, numerator / denominator, np.nan).astype(np.float32)
        upface = stack[base + LIDAR_BANDS.index("upface_max")].astype(np.float32)
        downface = stack[base + LIDAR_BANDS.index("downface_max")].astype(np.float32)
        stack[derived + 1] = (upface - downface).astype(np.float32)
        thorium = stack[base + len(LIDAR_BANDS) + 1].astype(np.float32)
        stack[derived + 2] = (thorium - potassium).astype(np.float32)
    stack.flush()
    meta = {"bands": names, "shape": list(SHAPE), "crs_epsg": CRS_EPSG,
            "transform": list(TRANSFORM), "footprint_pixels": FOOTPRINT_PIXELS,
            "bytes": int((out_dir / "features.f32").stat().st_size),
            "missing_data_policy": ("0 means 'no survey coverage' in the LiDAR and GeoDAWN layers and is "
                                    "converted to NaN; the competition layers keep their own -3.4028235e38 "
                                    "nodata and are also converted to NaN."),
            "provenance": "owner-mirror competition and derived external layers; not organizer-authenticated",
            "label_derived_features": False,
            "retired_unsafe_planes": ["dist_cat_km", "dist_sgmc_km"],
            "warning": "Catalogue-derived features must be rebuilt per fold from visible faults; SGMC never enters features."}
    (out_dir / "features.json").write_text(json.dumps(meta, indent=1) + "\n")
    return meta


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--out-dir", default="data/prepared")
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--manifest", default="registry/data_manifest.json")
    parser.add_argument("--out", default="evidence/data_preparation.json")
    args = parser.parse_args()
    data_dir = (ROOT / args.data_dir).resolve()
    manifest = json.loads((ROOT / args.manifest).read_text())
    rows = verify(manifest, data_dir if not args.verify_only else data_dir)
    hashes_ok = bool(rows) and all(r.get("sha256_match") for r in rows)
    grids_ok = bool(rows) and all(r.get("grid_matches") for r in rows)
    ok = hashes_ok and grids_ok
    payload = {"schema_version": 2, "verify_only": args.verify_only, "files": rows,
               "all_hashes_match": hashes_ok, "all_grids_match": grids_ok, "ok": ok}
    if args.verify_only:
        print(json.dumps({"all_hashes_match": hashes_ok, "all_grids_match": grids_ok, "files": len(rows)}, indent=1))
    else:
        if not ok:
            raise SystemExit("input hashes/grids do not match registry/data_manifest.json; refusing to prepare")
        payload["prepared"] = build(data_dir, (ROOT / args.out_dir).resolve())
        print(f"prepared {payload['prepared']['bytes']:,} bytes, {len(payload['prepared']['bands'])} bands")
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=1) + "\n")
    print(f"wrote {out.relative_to(ROOT)}")
    if not ok:
        raise SystemExit("input hash/grid validation failed; report is not a successful validation")


if __name__ == "__main__":
    main()
