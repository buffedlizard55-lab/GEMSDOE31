#!/usr/bin/env python3
"""How the incumbent dot set responds to (a) corroboration filtering and (b) adding detections.

Two measurements, both against the same two truth proxies:

* **Filter** — keep only the incumbent dots whose fold-OOF detector probability is above a
  quantile. This asks whether our likelihood is a superset of whatever produced the incumbent.
* **Union** — keep every incumbent dot and add the cells where the fold-OOF probability exceeds a
  threshold and (optionally) the cell is not on the public catalogue. Adding is the direction the
  metric algebra allows; thinning is not.

Inputs (all hash-pinned, see ``registry/data_manifest.json``): the incumbent dot set is read out of
the published submission raster so there is exactly one definition of it; the detector probabilities
are the fold-OOF maps in ``evidence/oof/``; truth proxies are the public catalogue raster and the
USGS SGMC state-map faults more than 300 m from it.

Writes ``evidence/union_results.json`` and ``evidence/incumbent_filter_results.json``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gemsdoe31 import metric  # noqa: E402
from gemsdoe31.raster import CELL_M, distance_km  # noqa: E402

INCUMBENT = "docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif"
QUANTILES = (0.10, 0.25, 0.50, 0.75)
THRESHOLDS = (0.50, 0.60, 0.65, 0.70, 0.75, 0.80, 0.90, 0.95)
OOF_MAPS = {
    "B_19_plus_lidar": "evidence/oof/oof_B_19_plus_lidar_u16.npz",
    "D_19_plus_lidar_radiometric": "evidence/oof/oof_D_19_plus_lidar_radiometric_u16.npz",
}


def load_probability(path: Path) -> np.ndarray:
    """Read a fold-OOF probability map from the committed quantised artifact (or a raw .npy)."""
    if path.suffix == ".npz":
        with np.load(path) as bundle:
            return bundle["probability_u16"].astype(np.float32) / 65535.0
    return np.load(path)


def load_truth(data_dir: Path) -> tuple[np.ndarray, np.ndarray]:
    with rasterio.open(data_dir / "labels.tif") as src:
        catalogue = src.read(1) == 1
    with rasterio.open(data_dir / "external/derived_sgmc_faults_100m_u8.tif") as src:
        sgmc = src.read(1) == 1
    far_field = sgmc & (distance_km(catalogue, CELL_M) > metric.RADIUS_M / 1000.0)
    return catalogue, far_field


def score(dots: np.ndarray, catalogue: np.ndarray, far_field: np.ndarray) -> dict:
    cat = metric.dti(dots.astype(np.float32), catalogue)
    ff = metric.dti(dots.astype(np.float32), far_field)
    return {"dots": int(dots.sum()), "cat_DTI": cat["DTI"], "cat_TPw": cat["TPw"], "ff_DTI": ff["DTI"],
            "ff_TPw": ff["TPw"]}


def _best_union(unions: list[dict]) -> dict:
    """The catalogue-dropping union with the highest off-catalogue DTI."""
    candidates = [row for row in unions if row["drop_catalogue_pixels"]]
    if not candidates:
        return {}
    best = max(candidates, key=lambda row: row["ff_DTI"])
    return {"arm": best["arm"], "threshold": best["threshold"], "added": best["added"],
            "dots": best["dots"], "cat_DTI": best["cat_DTI"], "ff_DTI": best["ff_DTI"],
            "delta": best["ff_delta"], "added_credit_per_dot": best["added_ff_credit_per_dot"]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--out", default="evidence/union_results.json")
    parser.add_argument("--filter-out", default="evidence/incumbent_filter_results.json")
    parser.add_argument("--write-best", metavar="TIFF",
                        help="write the best union (highest off-catalogue DTI among the catalogue-dropping "
                             "variants) as a float32 0/1 raster for scripts/build_submission.py")
    args = parser.parse_args()
    data_dir = (ROOT / args.data_dir).resolve()

    with rasterio.open(ROOT / INCUMBENT) as src:
        incumbent_values = np.nan_to_num(src.read(1), nan=0.0)
    incumbent = incumbent_values > 0.0
    catalogue, far_field = load_truth(data_dir)
    print(f"incumbent dots           {int(incumbent.sum()):,}")
    print(f"catalogue truth pixels   {int(catalogue.sum()):,}")
    print(f"off-catalogue truth px   {int(far_field.sum()):,} (>300 m from the catalogue)")
    if int(catalogue.sum()) != 60_988 or int(far_field.sum()) != 61_664:
        raise SystemExit("truth-proxy pixel counts drifted from the registered values; refusing to write")

    incumbent_scores = score(incumbent, catalogue, far_field)
    print(f"incumbent: cat_DTI {incumbent_scores['cat_DTI']:.4f}  ff_DTI {incumbent_scores['ff_DTI']:.4f}")
    if abs(incumbent_scores["cat_DTI"] - 0.04909549919996513) > 1e-9 or abs(incumbent_scores["ff_DTI"] - 0.09384814898733441) > 1e-9:
        raise SystemExit("incumbent rescoring does not reproduce the registered values; refusing to write")

    unions = []
    filters = []
    for arm, path in OOF_MAPS.items():
        probability = load_probability(ROOT / path)
        if probability.shape != incumbent.shape:
            raise SystemExit(f"{path} is not on the competition grid")
        if not np.isfinite(probability[incumbent]).all():
            raise SystemExit(f"{path} has non-finite values inside the incumbent dot set")
        print(f"\n{arm}: p at incumbent dots min {probability[incumbent].min():.4f} "
              f"median {np.median(probability[incumbent]):.4f} max {probability[incumbent].max():.4f}")

        for quantile in QUANTILES:
            cutoff = float(np.quantile(probability[incumbent], quantile))
            kept = incumbent & (probability >= cutoff)
            scores = score(kept, catalogue, far_field)
            row = {"arm": arm, "quantile": quantile, "cutoff_probability": cutoff, **scores,
                   "cat_delta": scores["cat_DTI"] - incumbent_scores["cat_DTI"],
                   "ff_delta": scores["ff_DTI"] - incumbent_scores["ff_DTI"],
                   "ff_credit_per_dot": scores["ff_TPw"] / max(scores["dots"], 1)}
            filters.append(row)
            print(f"  filter q={quantile:<5} dots {row['dots']:>6,} cat {row['cat_DTI']:.4f} "
                  f"ff {row['ff_DTI']:.4f} (Δff {row['ff_delta']:+.4f}, {row['ff_credit_per_dot']:.4f} credit/dot)")

        for threshold in THRESHOLDS:
            detected = probability >= threshold
            for drop_catalogue in (False, True):
                added_mask = detected & ~incumbent
                if drop_catalogue:
                    added_mask &= ~catalogue
                dots = incumbent | added_mask
                scores = score(dots, catalogue, far_field)
                added = score(added_mask, catalogue, far_field)
                row = {"arm": arm, "threshold": threshold, "drop_catalogue_pixels": drop_catalogue,
                       "added": int(added_mask.sum()), **scores,
                       "cat_delta": scores["cat_DTI"] - incumbent_scores["cat_DTI"],
                       "ff_delta": scores["ff_DTI"] - incumbent_scores["ff_DTI"],
                       "added_cat_TPw": added["cat_TPw"], "added_ff_TPw": added["ff_TPw"],
                       "added_ff_credit": scores["ff_TPw"] - incumbent_scores["ff_TPw"],
                       "added_ff_credit_per_dot": (scores["ff_TPw"] - incumbent_scores["ff_TPw"]) / max(int(added_mask.sum()), 1),
                       "added_cat_credit_per_dot": (scores["cat_TPw"] - incumbent_scores["cat_TPw"]) / max(int(added_mask.sum()), 1)}
                unions.append(row)
                print(f"  union p>={threshold:<5} drop_cat={int(drop_catalogue)} added {row['added']:>7,} "
                      f"dots {row['dots']:>7,} cat {scores['cat_DTI']:.4f} ff {scores['ff_DTI']:.4f} "
                      f"(Δff {row['ff_delta']:+.4f}, {row['added_ff_credit_per_dot']:.4f} credit/dot)")

    incumbent_credit = incumbent_scores["ff_TPw"] / incumbent_scores["dots"]

    if args.write_best:
        candidates = [row for row in unions if row["drop_catalogue_pixels"]]
        best = max(candidates, key=lambda row: row["ff_DTI"])
        mask = incumbent | ((load_probability(ROOT / OOF_MAPS[best["arm"]]) >= best["threshold"]) & ~catalogue)
        if int(mask.sum()) != best["dots"]:
            raise SystemExit("dot-count mismatch while materialising the best union")
        transform = rasterio.transform.from_origin(243350.0, 4508550.0, 100.0, 100.0)
        profile = {"driver": "GTiff", "crs": "EPSG:32611", "transform": transform,
                   "height": mask.shape[0], "width": mask.shape[1], "count": 1, "dtype": "float32",
                   "nodata": float("nan")}
        with rasterio.open(ROOT / args.write_best, "w", **profile) as dst:
            dst.write(np.where(mask, 1.0, np.nan).astype(np.float32), 1)
        print(f"\nwrote best union ({best['arm']} p>={best['threshold']}, {best['dots']:,} dots) to {args.write_best}")
    (ROOT / args.out).write_text(json.dumps({
        "schema_version": 1,
        "generated_utc": "2026-10-04",
        "claim_class": "COMPUTED on owner-mirror inputs with the official metric (evidence/metric_check.json)",
        "incumbent_source": INCUMBENT,
        "incumbent": {**incumbent_scores, "ff_credit_per_dot": incumbent_credit},
        "oof_maps": OOF_MAPS,
        "best_union": _best_union(unions),
        "truth_proxies": {"catalogue_gap_pixels": int(catalogue.sum()),
                          "off_catalogue_pixels": int(far_field.sum()),
                          "off_catalogue_definition": "USGS SGMC state-map fault cells more than 300 m from the public catalogue"},
        "unions": unions,
    }, indent=1) + "\n")

    (ROOT / args.filter_out).write_text(json.dumps({
        "schema_version": 1,
        "generated_utc": "2026-10-04",
        "claim_class": "COMPUTED on owner-mirror inputs with the official metric",
        "question": "Is the incumbent dot set a subset of what the fold-OOF detector likes?",
        "incumbent": {**incumbent_scores, "ff_credit_per_dot": incumbent_credit},
        "rows": filters,
    }, indent=1) + "\n")
    print(f"\nwrote {args.out} and {args.filter_out}")


if __name__ == "__main__":
    main()
