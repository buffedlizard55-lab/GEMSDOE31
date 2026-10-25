#!/usr/bin/env python3
"""Independent post-run repetition of fixed surfaces/dots; no new experiment.

Checks all three frozen variants, not just the packaged primary. Does not fit,
tune or write any new candidate TIFF. The original pre-placement audit remains
untouched. Original receipts retain their historical execution context.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "vendor"), str(ROOT / "scripts")]

import numpy as np  # noqa: E402
import rasterio  # noqa: E402
from gemsdoe31.magrest import NAMES, spaced_dots  # noqa: E402
from gemsdoe31 import novelty  # noqa: E402
from run_magrest import BUDGET, PRIMARY, verify_inputs, features, save  # noqa: E402
from gemsdoe31.submission import sha256_file  # noqa: E402


def main():
    grid = verify_inputs()
    f = features(grid)
    index = json.loads((ROOT / "evidence/magrest_registry_index.json").read_text())
    surfaces = dict(zip(NAMES, f))
    final = {n: spaced_dots(s, grid.footprint & ~grid.catalogue, BUDGET) for n, s in surfaces.items()}
    surface = novelty.audit(ROOT, surfaces, grid.footprint,
        {n: novelty.prospective_support(s, grid.footprint & ~grid.catalogue, BUDGET) for n, s in surfaces.items()},
        index, phase="post-run repetition of frozen surfaces; original pre-placement record retained")
    dots = novelty.audit(ROOT, {n: p.astype(np.float32) for n, p in final.items()}, grid.footprint, final,
                          index, phase="post-run repetition of ALL three fixed final-support variants")
    card = json.loads((ROOT / "registry/current_run.json").read_text())
    with rasterio.open(ROOT / card["file"]) as ds:
        served = ds.read(1) > 0
    if not np.array_equal(served, final[PRIMARY]):
        raise AssertionError("packaged dots differ from deterministic primary reconstruction")
    if any(not arm["pass_"] for report in (surface, dots) for arm in report["arms"].values()):
        raise AssertionError("duplicate STOP on independent repetition")
    original = json.loads((ROOT / "evidence/magrest/novelty_surface.json").read_text())
    for n in NAMES:
        for k in ("max_abs_rho", "max_overlap"):
            if abs(original["arms"][n][k] - surface["arms"][n][k]) > 1e-12:
                raise AssertionError("pre-placement diagnostic did not reproduce")
    result = dict(no_new_candidate_or_fit=True, deterministic_primary_reconstruction=True,
                  original_preplacement_report_sha256=sha256_file(ROOT / "evidence/magrest/novelty_surface.json"),
                  inventory_sha256=sha256_file(ROOT / "evidence/sibling_inventory_20261025.json"),
                  surface_recheck=surface, all_final_dots_recheck=dots)
    save(ROOT / "evidence/magrest/independent_novelty_recheck.json", result)
    print(json.dumps({n: {k: a[k] for k in ("pass_", "max_abs_rho", "max_overlap", "support_sha256")}
                      for n, a in dots["arms"].items()}, indent=1))


if __name__ == "__main__":
    main()
