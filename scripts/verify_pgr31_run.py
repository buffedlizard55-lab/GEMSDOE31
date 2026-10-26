#!/usr/bin/env python3
"""Independent automated verification of the packaged PGR31 run (no human inspector).

Re-reads the committed TIFF/ZIP bytes and checks, without trusting the builder's
in-memory state: SHA-256 vs the run card, single-band float32 EPSG:32611 grid,
finite [0,1] footprint values under both outside conventions, binary {0,1} support,
dot count, one-TIFF ZIP byte identity, preregistration hash, and (when the
competition mirror is present) zero dots within 2 px of the public catalogue.
A scientific verdict of "negative" is a *result*, not a verification failure:
this script fails only when bytes/receipts disagree.
"""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src")]

from gemsdoe31.submission import sha256_file, validate_submission  # noqa: E402

NAME = "gemsdoe31-pgr31-poisson-pseudograv-37654-20261026"
DL = ROOT / "docs" / "downloads"


def main() -> int:
    failures: list[str] = []
    card = json.loads((ROOT / "evidence" / "pgr31" / "run_card.json").read_text())
    card_copy = json.loads((DL / f"{NAME}-run-card.json").read_text())
    if card != card_copy:
        failures.append("downloaded run-card copy differs from evidence/pgr31/run_card.json")

    prereg = ROOT / "knowledge" / "2026-10-26_pgr31_preregistration.md"
    if sha256_file(prereg) != card["preregistration_sha256"]:
        failures.append("preregistration sha256 mismatch")

    template = ROOT / "data/sample_submission.tif"
    if not template.is_file():
        # Clean-checkout fallback: a committed raster on the identical competition grid
        # (NaN exactly outside the same footprint). Grid/footprint checks are unchanged.
        template = DL / "gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif"

    facts = card["facts"]
    results = {}
    for kind, convention in (("zeros", "all-finite"), ("nan", "nan-outside")):
        path = DL / facts[kind]["file"]
        if sha256_file(path) != facts[kind]["sha256"]:
            failures.append(f"{kind}: sha256 mismatch vs run card")
        receipt = validate_submission(path, template, convention=convention)
        if receipt["hard_failures"]:
            failures.append(f"{kind}: validator hard failures {receipt['hard_failures']}")
        with rasterio.open(path) as ds:
            a = ds.read(1)
        finite = a[np.isfinite(a)]
        if set(np.unique(finite).tolist()) != {0.0, 1.0}:
            failures.append(f"{kind}: finite values are not exactly {{0,1}}")
        if int((a == 1).sum()) != facts["dots"]:
            failures.append(f"{kind}: dot count {int((a == 1).sum())} != run card {facts['dots']}")
        zpath = path.with_suffix(".zip")
        with zipfile.ZipFile(zpath) as z:
            if z.namelist() != [path.name] or z.read(path.name) != path.read_bytes():
                failures.append(f"{kind}: ZIP is not a byte-identical single-TIFF archive")
        results[kind] = dict(
            sha256=facts[kind]["sha256"],
            validator_hard_failures=receipt["hard_failures"],
            dots=int((a == 1).sum()),
        )

    catalogue_check = "skipped (data/labels.tif absent)"
    labels = ROOT / "data/labels.tif"
    if labels.is_file():
        with rasterio.open(labels) as ds:
            cat = ds.read(1) == 1
        with rasterio.open(DL / facts["zeros"]["file"]) as ds:
            dots = ds.read(1) == 1
        d_cat = distance_transform_edt(~cat)
        n_within2 = int((dots & (d_cat <= 2.0)).sum())
        catalogue_check = f"dots within 2px of catalogue: {n_within2}"
        if n_within2 != facts["dots_within_2px_catalogue"]:
            failures.append("catalogue 2px count mismatch vs run card")

    holdout = card["holdout_dti"]["screen_seed51"]
    out = dict(
        verified=not failures,
        failures=failures,
        verdict=card["verdict"],
        ok_to_download_for_research=card["ok_to_download_for_research"],
        eligible_for_selector=card["eligible_for_selector"],
        ok_to_submit=card["ok_to_submit"],
        evidence_class="HOLDOUT-DTI",
        evaluator_version=holdout["evaluator_version"] if holdout else None,
        candidate_holdout_dti=holdout["candidate"]["dti"] if holdout else None,
        candidate_holdout_ci95=holdout["candidate"]["ci95"] if holdout else None,
        withheld_positive_pixels=holdout["candidate"]["withheld_positive_pixels"] if holdout else None,
        paired_difference=holdout["paired_difference"] if holdout else None,
        catalogue_check=catalogue_check,
        files=results,
        registry=card["correlation_overlap_vs_registry"],
    )
    print(json.dumps(out, indent=1))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
