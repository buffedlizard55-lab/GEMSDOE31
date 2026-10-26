#!/usr/bin/env python3
"""Correct the original nine-download-tree scope using a shared-registry counterexample.

An existential duplicate STOP needs one authentic registered raster, not an
exhaustive scan. No comparator is excluded for being dense/calibration-only.
This audits only the three already-frozen surfaces/supports, never fits/tunes or
writes a new TIFF. The original pre-placement reports remain untouched.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "vendor")]
import numpy as np  # noqa: E402
import rasterio  # noqa: E402
from scipy.ndimage import distance_transform_edt  # noqa: E402
from gemsdoe31.magrest import NAMES, spaced_dots  # noqa: E402
from gemsdoe31.novelty import prospective_support, standardized_ranks  # noqa: E402


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_counterexample(root=ROOT, *, restore=False):
    pin = json.loads((root / "registry/shared_registry_57_pin.json").read_text())
    manifest = root / pin["manifest"]
    if sha(manifest) != pin["manifest_sha256"]:
        raise ValueError("shared registry manifest changed")
    rows = json.loads(manifest.read_text())["rasters"]
    ref = pin["counterexample"]
    if not any(r["sha256"] == ref["sha256"] for r in rows):
        raise ValueError("counterexample is not actually registered")
    path = root / ref["cache_file"]
    if not path.exists() and restore:
        sys.path.insert(0, str(ROOT / "scripts"))
        from download_competition_data import _download
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".partial")
        tmp.unlink(missing_ok=True)
        try:
            _download(ref["repo"], ref["ref"], ref["path"], tmp)
            if sha(tmp) != ref["sha256"]:
                raise ValueError("downloaded registry control hash mismatch")
            tmp.replace(path)
        finally:
            tmp.unlink(missing_ok=True)
    if not path.exists() or sha(path) != ref["sha256"]:
        raise ValueError("registered counterexample absent/changed; use --restore-small-inputs")
    with rasterio.open(path) as ds, rasterio.open(root / "data/sample_submission.tif") as sample:
        if ds.shape != sample.shape or ds.crs != sample.crs or ds.transform != sample.transform or ds.count != 1:
            raise ValueError("registered control is not comparable to the exact grid")
        a = ds.read(1)
    return pin, a


def main():
    # This is an audit of immutable, already-computed variants, NOT another fit
    # or candidate. The loop must not be used to search a passing new variant.
    with rasterio.open(ROOT / "data/sample_submission.tif") as ds:
        fp = np.isfinite(ds.read(1))
    with rasterio.open(ROOT / "data/labels.tif") as ds:
        cat = ds.read(1) == 1
    pin, reference = load_counterexample(restore=True)
    control = fp & np.isfinite(reference) & (reference > 0)
    halo = distance_transform_edt(~control) <= 3
    control_ranks = standardized_ranks(np.where(np.isfinite(reference[fp]), reference[fp], 0))
    responses = np.load(ROOT / ".cache/magrest/responses.npy", mmap_mode="r")
    result = dict(discovered_utc=datetime.now(timezone.utc).isoformat(),
        gate="STOP: literal shared-registry overlap limit exceeded", literal_gate_pass=False,
        registered_counterexample=pin["counterexample"], registry_manifest_sha256=pin["manifest_sha256"],
        registered_rasters_in_manifest=pin["registered_rasters"],
        coverage_complete=False, reason="One authentic registered counterexample is sufficient for STOP; no full 695-raster pass is claimed.",
        calibration_or_density_exemption=False, no_new_fit_tuning_candidate_or_slot=True,
        original_nine_site_reports_retained=True,
        original_preflight_defect="Only nine docs/downloads trees were tested before scoring/packaging; template registry and other paths were incorrectly outside that preflight scope.",
        timing="Discovered in final review AFTER the original three variants and negative TIFF were already computed. Results are retained transparently, not retroactively represented as correctly ordered preflight.",
        disposition="Retain already-generated genuinely new research bytes to satisfy the highest-priority output instruction; no new TIFF after this STOP, no upload or further experiment. Dense coverage does not prove copied content, but the user's literal rule still stops the lane.",
        control_positive_pixels=int(control.sum()), control_3px_footprint_coverage=float(halo[fp].mean()), arms={})
    for name, s in zip(NAMES, responses):
        prospective = prospective_support(s, fp & ~cat, 37654)
        final = spaced_dots(s, fp & ~cat, 37654)
        stages = {}
        for phase, values, support in (("surface", s, prospective), ("final", final.astype(np.float32), final)):
            ranks = standardized_ranks(values[fp])
            rho = None if ranks is None else float(np.dot(ranks, control_ranks))
            within = int((support & halo).sum())
            overlap = within / int(support.sum())
            stages[phase] = dict(spearman_rho=rho, candidate_support_pixels=int(support.sum()),
                within_3px=within, overlap_within_3px=overlap,
                duplicate=(rho is not None and abs(rho) > .90) or overlap > .70,
                support_sha256=hashlib.sha256(np.packbits(support.ravel()).tobytes()).hexdigest())
        result["arms"][name] = stages
    out = ROOT / "evidence/magrest/registry_scope_correction.json"
    out.write_text(json.dumps(result, indent=1, allow_nan=False) + "\n")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
