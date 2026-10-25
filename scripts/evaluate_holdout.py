#!/usr/bin/env python3
"""Shared spatially blocked hide-and-recover evaluator CLI (gemsdoe31-hide-recover-v1).

Evaluates any pre-built binary dot GeoTIFF or continuous score surface against deterministic
hide-and-recover draws, reporting ``HOLDOUT-DTI`` with 1,000-replicate 20 km cluster-bootstrap
95% CIs, ``OFFCAT-PROXY-DTI`` on SGMC (>300 m from catalogue), and registry duplicate checks.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gemsdoe31.holdout import (  # noqa: E402
    EVALUATOR_VERSION,
    additive_dti_pixel_maps,
    check_registry_duplicate_canary,
    make_hide_recover_draw,
    pool_multi_draw_bootstrap,
    score_holdout_draw,
)
from gemsdoe31.metric import ALPHA, BETA, dti  # noqa: E402
from gemsdoe31.submodular import allocate_submodular_dots, priority_poisson_thin  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prediction", help="Path to GeoTIFF (.tif) or .npz prediction")
    parser.add_argument("--data-dir", default=os.environ.get("GEMSDOE31_DATA_DIR", "data"))
    parser.add_argument("--seeds", type=int, nargs="+", default=[101, 102])
    parser.add_argument("--emitter", choices=("existing-binary", "poisson", "submod300"), default="existing-binary")
    parser.add_argument("--budget", type=int, default=37654)
    parser.add_argument("--registry-dir", default="/tmp/gems_registry_audit")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    with rasterio.open(data_dir / "sample_submission.tif") as src:
        footprint = np.isfinite(src.read(1))
    with rasterio.open(data_dir / "labels.tif") as src:
        catalogue = (src.read(1) == 1) & footprint
    with rasterio.open(data_dir / "external/derived_sgmc_faults_100m_u8.tif") as src:
        sgmc = (src.read(1) == 1) & footprint

    pred_path = Path(args.prediction)
    if pred_path.suffix.lower() == ".npz":
        z = np.load(pred_path)
        key = list(z.keys())[0]
        raw = np.asarray(z[key], dtype=np.float32)
    else:
        with rasterio.open(pred_path) as src:
            raw = src.read(1).astype(np.float32)

    draw_reports = []
    tile_pairs = []
    h, w = footprint.shape
    nr, nc = (h + 199) // 200, (w + 199) // 200
    pad_h, pad_w = nr * 200 - h, nc * 200 - w

    def _tile(arr: np.ndarray) -> np.ndarray:
        padded = np.pad(arr, ((0, pad_h), (0, pad_w)), mode="constant")
        return padded.reshape(nr, 200, nc, 200).sum(axis=(1, 3)).ravel()

    foot_tiles = _tile(footprint.astype(np.float64)) > 0

    for seed in args.seeds:
        draw = make_hide_recover_draw(catalogue, footprint, seed=seed)
        d_vis = distance_transform_edt(~draw.visible)
        elig = footprint & (d_vis > 2.0)
        if args.emitter == "existing-binary":
            dots = (np.nan_to_num(raw, nan=0.0) > 0.5) & elig
        elif args.emitter == "poisson":
            dots = priority_poisson_thin(raw, elig, budget=args.budget, min_dist_px=2.8)
        else:
            dots, _ = allocate_submodular_dots(raw, elig, budget=args.budget)
        rep = score_holdout_draw(dots, draw, footprint)
        draw_reports.append(rep)
        pred_m = (dots & footprint & (~draw.visible)).astype(np.float32)
        tp_m, fn_m, fp_m = additive_dti_pixel_maps(pred_m, draw.hidden & footprint)
        tp_t = _tile(tp_m)[foot_tiles]
        den_t = tp_t + ALPHA * _tile(fp_m)[foot_tiles] + BETA * _tile(fn_m)[foot_tiles]
        tile_pairs.append((tp_t, den_t))

    mean_dti, ci_lo, ci_hi = pool_multi_draw_bootstrap(tile_pairs)

    d_cat = distance_transform_edt(~catalogue)
    elig_full = footprint & (d_cat > 2.0)
    if args.emitter == "existing-binary":
        dots_full = (np.nan_to_num(raw, nan=0.0) > 0.5) & elig_full
    elif args.emitter == "poisson":
        dots_full = priority_poisson_thin(raw, elig_full, budget=args.budget, min_dist_px=2.8)
    else:
        dots_full, _ = allocate_submodular_dots(raw, elig_full, budget=args.budget)
    offcat = dti(dots_full.astype(np.float32), sgmc & (d_cat > 3.0))

    reg_paths = sorted((ROOT / "docs/downloads").glob("*.tif"))
    reg_dir = Path(args.registry_dir)
    if reg_dir.is_dir():
        reg_paths.extend(sorted(reg_dir.glob("*.tif")))
    stem_base = (
        pred_path.name.removesuffix("-nan.tif")
        .removesuffix("-allfinite.tif")
        .removesuffix(".tif")
        .removesuffix(".npz")
    )
    reg_paths = [
        p for p in reg_paths
        if p.resolve() != pred_path.resolve() and not p.name.startswith(stem_base)
    ]
    dup = check_registry_duplicate_canary(raw, dots_full, footprint, reg_paths)

    live_collar_pruned = bool(
        args.emitter == "existing-binary"
        and ((np.nan_to_num(raw, nan=0.0) > 0.5) & (d_cat <= 2.0)).sum() == 0
    )

    payload = {
        "metric_label": "HOLDOUT-DTI",
        "evaluator_version": EVALUATOR_VERSION,
        "prediction": str(pred_path),
        "emitter": args.emitter,
        "live_full_catalogue_b2_pruned_input": live_collar_pruned,
        "note": (
            "Input is a live full-catalogue B=2 pruned raster (0 dots within <=200 m of full labels.tif, including "
            "withheld hidden components); use scripts/run_arms.py for pre-prune fold-visible hide-and-recover HOLDOUT-DTI."
            if live_collar_pruned
            else "Evaluated on fold-visible hide-and-recover draws."
        ),
        "seeds": args.seeds,
        "mean_holdout_dti": round(mean_dti, 6),
        "ci95": [round(ci_lo, 6), round(ci_hi, 6)],
        "draws": draw_reports,
        "offcat_proxy_dti_sgmc_gt300m": round(float(offcat["DTI"]), 6),
        "duplicate_canary": {
            "passed": dup["passed"],
            "max_abs_spearman": dup["max_abs_spearman"],
            "max_spearman_raster": dup["max_spearman_raster"],
            "max_symmetric_3px_overlap": dup["max_symmetric_3px_overlap"],
            "max_overlap_raster": dup["max_overlap_raster"],
        },
    }
    text = json.dumps(payload, indent=2) + "\n"
    if args.out:
        out_p = Path(args.out)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(text)
    print(text)


if __name__ == "__main__":
    main()
