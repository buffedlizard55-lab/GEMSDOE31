#!/usr/bin/env python3
"""Derive the validation buffer from out-of-fold residual semivariograms along known fault traces.

This replaces an assumed "4-5 pixel" collar with a measured range. Inputs are the out-of-fold
probability map produced by ``scripts/run_arms.py`` (``evidence/oof/oof_<arm>.npy``) and the
public catalogue raster (``data/labels.tif``).

Outputs ``evidence/buffer_derivation.json`` with the empirical variogram, the spherical /
exponential / gaussian fits, a component bootstrap, and the resulting buffer.

Nothing here is tuned to make the buffer large or small: the rule is fixed in
``src/gemsdoe31/buffer.py`` and the same rule is applied to every model.
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
from gemsdoe31.buffer import (  # noqa: E402
    component_bootstrap, decide_buffer_m, empirical_variogram, fit_models,
)
from gemsdoe31.raster import connected_components  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oof", default="evidence/oof/oof_D_19_plus_lidar_radiometric.npy")
    parser.add_argument("--labels", default="data/labels.tif")
    parser.add_argument("--out", default="evidence/buffer_derivation.json")
    parser.add_argument("--bin-m", type=float, default=500.0)
    parser.add_argument("--max-lag-m", type=float, default=60_000.0)
    parser.add_argument("--min-pairs", type=int, default=20)
    parser.add_argument("--bootstrap", type=int, default=200)
    parser.add_argument("--seed", type=int, default=20261004)
    args = parser.parse_args()

    oof_path = ROOT / args.oof
    if not oof_path.is_file():
        raise SystemExit(f"missing out-of-fold map {oof_path}; run scripts/run_arms.py first")
    probs = np.load(oof_path)
    with rasterio.open(ROOT / args.labels) as src:
        labels = src.read(1)
    catalogue = labels == 1
    oof_region = np.isfinite(probs) & (probs > 0)
    mask = catalogue & oof_region
    if int(mask.sum()) < 1_000:
        raise SystemExit(f"only {int(mask.sum())} held-out catalogue pixels: no variogram is identifiable")

    components = connected_components(catalogue)
    rows, cols = np.nonzero(mask)
    values = 1.0 - probs[rows, cols]          # regression residual on catalogue pixels
    comp = components[rows, cols]

    bins = empirical_variogram(rows, cols, values, comp, bin_m=args.bin_m, max_lag_m=args.max_lag_m)
    fits = fit_models(bins, min_pairs=args.min_pairs)
    if not fits:
        raise SystemExit("no model converged on the populated bins: range is not identifiable")
    bootstrap = component_bootstrap(rows, cols, values, comp, draws=args.bootstrap, seed=args.seed,
                                    min_pairs=args.min_pairs, bin_m=args.bin_m, max_lag_m=args.max_lag_m)
    decision = decide_buffer_m(fits, bootstrap, bins, min_pairs=args.min_pairs)

    payload = {
        "schema_version": 1,
        "method": "Matheron residual semivariogram, pairs restricted to the same 8-connected fault component",
        "inputs": {"oof": args.oof, "labels": args.labels, "residual": "e = 1 - p at held-out catalogue pixels"},
        "support": {"residual_pixels": int(mask.sum()), "components": int(np.unique(comp).size),
                    "bin_m": args.bin_m, "max_lag_m": args.max_lag_m, "min_pairs": args.min_pairs},
        "empirical": bins.as_dict() if hasattr(bins, "as_dict") else {
            "bin_centres_m": bins.centres_m.tolist(),
            "semivariance": [None if not np.isfinite(g) else float(g) for g in bins.gamma],
            "pair_counts": bins.pairs.astype(int).tolist(),
        },
        "fits": fits,
        "bootstrap": bootstrap,
        "decision": decision,
        "provenance": {
            "claim_class": "COMPUTED (owner-mirror inputs; not organizer-authenticated)",
            "references": [
                "Roberts et al. 2017, Ecography, doi:10.1111/ecog.02881 (spatial blocking must match the "
                "data's dependence structure; no universal pixel buffer is given there)",
                "Valavi et al. 2019, Methods in Ecology and Evolution, doi:10.1111/2041-210X.13107 (blockCV)",
            ],
        },
    }
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=1) + "\n")
    print(json.dumps({k: payload["decision"][k] for k in
                      ("buffer_m", "buffer_km", "empirical_decay_range_m",
                       "model_practical_range_median_m", "max_fitted_range_m",
                       "observed_lag_support_m")}, indent=1))
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
