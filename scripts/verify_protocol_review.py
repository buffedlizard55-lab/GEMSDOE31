#!/usr/bin/env python3
"""Audit existing H31-X bytes against the literal registry; never fit/write TIFFs.

Surface diagnostics are explicitly cited from the frozen run card, not replayed:
its ignored pre-placement array is unavailable. A fresh final witness suffices
for STOP. Does not claim an exhaustive uniqueness pass or reproduce holdout.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts"), str(ROOT / "vendor")]

import numpy as np  # noqa: E402
import rasterio  # noqa: E402
from scipy.ndimage import distance_transform_edt  # noqa: E402
from audit_shared_registry_stop import load_counterexample  # noqa: E402
from gemsdoe31.novelty import standardized_ranks  # noqa: E402
from gemsdoe31.release_policy import POLICY_VERSION, uniqueness_gate  # noqa: E402
from gemsdoe31.submission import sha256_file, validate_submission  # noqa: E402


def verify(root=ROOT):
    root = Path(root)
    card_path = root / "evidence/h31x/run_card.json"
    card = json.loads(card_path.read_text())
    sample = root / "data/sample_submission.tif"
    manifest = json.loads((root / "registry/data_manifest.json").read_text())
    sample_pin = next(r for r in manifest["files"] if r["id"] == "sample_submission")
    if sha256_file(sample) != sample_pin["sha256"]:
        raise ValueError("template hash mismatch")
    path = root / card["files"]["zeros"]
    if sha256_file(path) != card["raster_sha256"]:
        raise ValueError("H31-X file hash mismatch")
    validation = validate_submission(path, sample, convention="all-finite")
    if not validation["ok_to_upload_format_only"]:
        raise ValueError("H31-X format failed")
    with rasterio.open(sample) as ds:
        foot = np.isfinite(ds.read(1))
    with rasterio.open(path) as ds:
        values = ds.read(1)
    dots = foot & (values > 0)
    pin, reference = load_counterexample(root)
    refdots = foot & np.isfinite(reference) & (reference > 0)
    halo = distance_transform_edt(~refdots) <= 3
    overlap = float(halo[dots].mean()) if dots.any() else None
    x = standardized_ranks(values[foot])
    y = standardized_ranks(np.nan_to_num(reference[foot], nan=0))
    rho = float(np.dot(x, y)) if x is not None and y is not None else None
    u = card["correlation_overlap_vs_registry"]
    stages = {
        "surface": dict(max_abs_rho=u["max_abs_spearman_surface"],
                        max_overlap=u["discrete_max_topk_overlap_3px"],
                        coverage_complete=False,
                        provenance="CITED from frozen H31-X card; array not replayed"),
        "final": dict(max_abs_rho=abs(rho) if rho is not None else None,
                      max_overlap=overlap, coverage_complete=False,
                      provenance="RECOMPUTED against hash-pinned registered lattice only"),
    }
    gate = uniqueness_gate(stages)
    if not gate["duplicate"]:
        raise ValueError("expected registered duplicate witness was not reproduced")
    outside = int((foot & ~halo).sum())
    n = int(dots.sum())
    return dict(
        policy_version=POLICY_VERSION, hypothesis=card["hypothesis"],
        mechanism=card["mechanism"], non_fault_mimic=card["non_fault_mimic"],
        review_scope="Existing artifact audit; no new lane assigned, fit, TIFF or slot. No full uniqueness pass.",
        experiments_run=0, new_tif_generated=False,
        holdout_dti=card["holdout_dti"]["screen_final_surface"],
        holdout_provenance="CITED prior receipt, not rerun or independently reproduced this session",
        source_run_card_sha256=sha256_file(card_path),
        correlation_overlap_vs_registry=stages, uniqueness_gate=gate,
        registered_witness=pin["counterexample"],
        lattice_coverage=dict(footprint_pixels=int(foot.sum()), outside_3px_halo=outside,
                              coverage_fraction=float(halo[foot].mean()),
                              candidate_dots=n,
                              minimum_overlap_any_same_budget=max(0., 1-outside/n) if n else None,
                              qualification="Counting bound for this dot budget, NOT every nonempty raster"),
        raster_sha256=sha256_file(path), file=card["files"]["zeros"], validator=validation,
        submission_name=card["submission_name"],
        note="RESEARCH ONLY: H31-X existing artifact; literal registry duplicate STOP; no new raster or submission slot.",
        ok_to_download_for_research=True, ok_to_submit=False, slot_approved=False,
        leaderboard_estimate=None,
        estimate_reason="Cross-family calibration unvalidated; no defensible numerical forecast",
        verdict="negative",
    )


def main():
    result = verify()
    for rel in ("evidence/review_9883b598/run_card.json", "docs/downloads/protocol-review-run-card.json"):
        p = ROOT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: result[k] for k in ("verdict", "ok_to_submit", "raster_sha256", "lattice_coverage")}, indent=2))


if __name__ == "__main__":
    main()
