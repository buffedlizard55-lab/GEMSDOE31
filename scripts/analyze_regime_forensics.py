#!/usr/bin/env python3
"""Regime forensics on EXISTING submissions only (no fit, no new candidate).

Question: why does the user-reported best family (H33-2-B2, GEMSDOE32) beat
this repo's H31-E2 SCGP-Submod on the all-elevation SGMC proxy while losing
on piedmont SGMC? Scores every local download TIFF against off-catalogue
SGMC truth split by the preregistered piedmont/mountain regime
(det_elev <= 50 m vs > 50 m) and measures dot allocation by regime and by
distance-to-catalogue band. All outputs are COMPUTED proxy measurements,
never competition scores.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gemsdoe31 import metric  # noqa: E402

DATA = ROOT / "data"
OUT = ROOT / "evidence/regime31/regime_forensics.json"

CANDIDATES = {
    "h31e_scgp_submod_fa735287": "docs/downloads/gemsdoe31-scgp-submod-37654-20261025-fa735287-nan.tif",
    "h27_4_solo_d28": "docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif",
    "d28_reference_44090": "docs/downloads/gemsdoe31-reference-d28-offcat-44090-20261004-nan.tif",
    "h31b_scarp_hessian": "docs/downloads/gemsdoe31-h31b-scarp-hessian-20261025-37654-nan.tif",
    "h31b_corroborated_b2_hybrid": "docs/downloads/gemsdoe31-h31b-corroborated-b2-hybrid-20261025-37654-nan.tif",
    "magrest_concordant": "docs/downloads/gemsdoe31-magrest-concordant-37654-20261025-2c800a59ff-nan.tif",
    "union_b_p060": "docs/downloads/gemsdoe31-union-b-p060-20261004-8acb75e1-nan.tif",
}


def load_dots(path: Path, footprint: np.ndarray) -> np.ndarray:
    with rasterio.open(path) as src:
        arr = src.read(1)
    return (np.nan_to_num(arr, nan=0.0) > 0.5) & footprint


def main() -> int:
    with rasterio.open(DATA / "sample_submission.tif") as src:
        footprint = np.isfinite(src.read(1))
    with rasterio.open(DATA / "labels.tif") as src:
        catalogue = (src.read(1) == 1) & footprint
    with rasterio.open(DATA / "external/derived_sgmc_faults_100m_u8.tif") as src:
        sgmc = (src.read(1) == 1) & footprint
    with rasterio.open(DATA / "training_features.tif") as src:
        names = [d.split(" - ")[0] for d in src.descriptions]
        det = src.read(names.index("det_elev") + 1).astype(np.float32)
    det[~np.isfinite(det) | (np.abs(det) > 1e20)] = np.nan

    d_cat = distance_transform_edt(~catalogue).astype(np.float32)  # px
    piedmont = footprint & np.isfinite(det) & (det <= 50.0)
    mountain = footprint & np.isfinite(det) & (det > 50.0)
    sgmc_off = sgmc & (d_cat > 3.0)
    truths = {
        "sgmc_offcat_all": sgmc_off,
        "sgmc_offcat_piedmont": sgmc_off & piedmont,
        "sgmc_offcat_mountain": sgmc_off & mountain,
    }

    def dti_terms(dots: np.ndarray, truth: np.ndarray) -> dict:
        r = metric.dti(dots.astype(np.float32), truth)
        return {"dti": float(r["DTI"]), "tpw": float(r["TPw"]), "fpw": float(r["FPw"]),
                "truth_pixels": int(r["truth_pixels"])}

    rows = {}
    # H33 reconstructed exactly as verified: H27 dots with d_cat > 2 px
    extra = {}
    h27 = load_dots(ROOT / CANDIDATES["h27_4_solo_d28"], footprint)
    extra["h33_reconstructed_h27_gt2px"] = h27 & (d_cat > 2.0)

    all_dots = {k: load_dots(ROOT / v, footprint) for k, v in CANDIDATES.items()}
    all_dots.update(extra)
    for name, dots in all_dots.items():
        dd = d_cat[dots]
        rows[name] = {
            "dots": int(dots.sum()),
            "dots_piedmont": int((dots & piedmont).sum()),
            "dots_mountain": int((dots & mountain).sum()),
            "piedmont_dot_share": float((dots & piedmont).sum() / max(dots.sum(), 1)),
            "dots_dcat_le2px": int((dd <= 2.0).sum()),
            "dots_dcat_2_3px": int(((dd > 2.0) & (dd <= 3.0)).sum()),
            "dots_dcat_gt15px_beyond_1p5km": int((dd > 15.0).sum()),
            **{tname: dti_terms(dots, t) for tname, t in truths.items()},
        }
        print(name, json.dumps({k: rows[name][k] for k in
              ("dots", "piedmont_dot_share")}), 
              {t: round(rows[name][t]["dti"], 4) for t in truths}, flush=True)

    payload = {
        "evidence_class": "COMPUTED (SGMC off-catalogue proxy; not a competition score)",
        "regime_definition": "piedmont: det_elev <= 50 m; mountain: det_elev > 50 m (same split as H31-E G5a/G5b)",
        "footprint_pixels": int(footprint.sum()),
        "piedmont_pixels": int(piedmont.sum()),
        "mountain_pixels": int(mountain.sum()),
        "catalogue_pixels": int(catalogue.sum()),
        "catalogue_piedmont": int((catalogue & piedmont).sum()),
        "catalogue_mountain": int((catalogue & mountain).sum()),
        "catalogue_piedmont_share": float((catalogue & piedmont).sum() / catalogue.sum()),
        "truth_pixels": {k: int(v.sum()) for k, v in truths.items()},
        "sgmc_piedmont_share_of_offcat": float(truths["sgmc_offcat_piedmont"].sum() / max(truths["sgmc_offcat_all"].sum(), 1)),
        "candidates": rows,
        "notes": [
            "h33_reconstructed = local H27-4 dots with catalogue distance > 2 px; equality with the "
            "GEMSDOE32 H33-2-B2 file was byte-verified in evidence/h33_forensics_20261025.json.",
            "SGMC is an independent-lineage-unverified proxy (USGS State Geologic Map Compilation); "
            "it disagrees with the catalogue holdout by construction and neither is the private truth.",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=1, allow_nan=False) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
