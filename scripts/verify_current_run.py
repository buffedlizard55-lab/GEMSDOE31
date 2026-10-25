#!/usr/bin/env python3
"""Re-derive current-file integrity and submission denial without a human inspector.

Only --restore-small-inputs uses the network (the existing pinned GitHub mirror
restorer for sample + catalogue plus one authentic registered control). No
DrivenData calls. Nine-tree repetition is scripts/recheck_magrest.py; the
broader literal registry STOP is independently re-derived from served dots.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "vendor"), str(ROOT / "scripts")]

import numpy as np  # noqa: E402
import rasterio  # noqa: E402
from scipy.spatial import cKDTree  # noqa: E402
from scipy.ndimage import distance_transform_edt  # noqa: E402
from audit_shared_registry_stop import load_counterexample  # noqa: E402
from gemsdoe31.novelty import standardized_ranks  # noqa: E402
from gems57 import evaluate_holdout as ev  # noqa: E402
from gemsdoe31.submission import sha256_file, validate_submission  # noqa: E402

PRIMARY = "magrest_concordant"


def restore_small_inputs(root=ROOT):
    from download_competition_data import restore
    manifest = json.loads((root / "registry/data_manifest.json").read_text())
    for item in manifest["files"]:
        if item["id"] in {"labels", "sample_submission"}:
            restore(item, root / "data")
    load_counterexample(root, restore=True)


def verify(root=ROOT):
    root = Path(root)
    card = json.loads((root / "registry/current_run.json").read_text())
    pins = json.loads((root / "registry/template_pins.json").read_text())
    for name, item in pins["files"].items():
        if sha256_file(root / "vendor/gems57" / name) != item["sha256"]:
            raise ValueError("shared template differs from its pin")
    for copy in ("evidence/magrest/run_card.json", "docs/downloads/magrest-run-card.json"):
        if json.loads((root / copy).read_text()) != card:
            raise ValueError(f"run-card copies drifted: {copy}")
    manifest = json.loads((root / "registry/data_manifest.json").read_text())
    for item in manifest["files"]:
        if item["id"] in {"labels", "sample_submission"}:
            if sha256_file(root / "data" / item["dest"]) != item["sha256"]:
                raise ValueError("small input provenance/hash drift")
    template = root / "data/sample_submission.tif"
    with rasterio.open(template) as ds:
        fp = np.isfinite(ds.read(1))
    with rasterio.open(root / "data/labels.tif") as ds:
        catalogue = ds.read(1) == 1
    reports = {}
    for key, convention in (("file", "all-finite"), ("nan_file", "nan-outside")):
        path = root / card[key]
        reports[key] = validate_submission(path, template, convention=convention)
        if not reports[key]["ok_to_upload_format_only"]:
            raise ValueError(f"format failure in {path.name}: {reports[key]['hard_failures']}")
    path = root / card["file"]
    if sha256_file(path) != card["raster_sha256"]:
        raise ValueError("primary raster bytes changed since experiment receipt")
    if reports["nan_file"]["sha256"] != card["validator"]["nan"]["sha256"]:
        raise ValueError("NaN raster bytes changed since experiment receipt")
    with rasterio.open(path) as ds:
        p = ds.read(1)
    with rasterio.open(root / card["nan_file"]) as ds:
        pn = ds.read(1)
    if not np.array_equal(p[fp], pn[fp]):
        raise ValueError("two encodings carry different footprint predictions")
    if not np.isin(p, [0, 1]).all() or np.any((p > 0) & catalogue):
        raise ValueError("binary dot/catalogue contract violated")
    points = np.argwhere(p > 0)
    nearest = cKDTree(points).query(points, k=2)[0][:, 1]
    if nearest.min() <= 2.8:
        raise ValueError("minimum separation contract violated")
    support_hash = hashlib.sha256(np.packbits((p > 0).ravel()).tobytes()).hexdigest()
    writer_receipt = json.loads(path.with_suffix(".json").read_text())
    if support_hash != writer_receipt["metadata"]["content_support_sha256"]:
        raise ValueError("support content digest drift")
    if len(card["note"]) > 140 or not card["note"].strip() or len(card["submission_name"]) > 140:
        raise ValueError("invalid unique name or note")
    for tif_key, zip_key in (("file", "zip_file"), ("nan_file", "nan_zip")):
        tif, archive = root / card[tif_key], root / card[zip_key]
        with zipfile.ZipFile(archive) as z:
            if z.namelist() != [tif.name] or z.read(tif.name) != tif.read_bytes():
                raise ValueError("ZIP is not an exact one-TIFF roundtrip")
    independent = json.loads((root / "evidence/magrest/independent_novelty_recheck.json").read_text())
    final = independent["all_final_dots_recheck"]["arms"][PRIMARY]
    if final["support_sha256"] != support_hash:
        raise ValueError("registry audit is not tied to the served dot support")
    if independent["inventory_sha256"] != sha256_file(root / "evidence/sibling_inventory_20261025.json"):
        raise ValueError("registry inventory drifted since independent audit")
    if independent["original_preplacement_report_sha256"] != sha256_file(root / "evidence/magrest/novelty_surface.json"):
        raise ValueError("pre-placement audit changed")
    for report in (independent["surface_recheck"], independent["all_final_dots_recheck"]):
        for arm in report["arms"].values():
            duplicate = False
            for row in arm["comparisons"]:
                rho, overlap = row["spearman_rho"], row["overlap_within_3px"]
                measured_overlap = row["within_3px"] / row["candidate_support_pixels"]
                if overlap is None or abs(measured_overlap - overlap) > 1e-12:
                    raise ValueError("registry overlap does not match integer counts")
                duplicate |= (rho is not None and abs(rho) > .90) or overlap > .70
            if duplicate or arm["duplicate"] or not arm["pass_"]:
                raise ValueError("duplicate STOP in independent registry receipt")
    correction = json.loads((root / "evidence/magrest/registry_scope_correction.json").read_text())
    broad_pin, reference = load_counterexample(root)
    if correction["registry_manifest_sha256"] != broad_pin["manifest_sha256"]:
        raise ValueError("broad registry correction manifest drift")
    control = fp & np.isfinite(reference) & (reference > 0)
    halo = distance_transform_edt(~control) <= 3
    actual_overlap = float(halo[p > 0].mean())
    actual_rho = float(np.dot(standardized_ranks(p[fp]), standardized_ranks(control[fp])))
    literal_registry_pass = not (abs(actual_rho) > .90 or actual_overlap > .70)
    corrected_final = correction["arms"][PRIMARY]["final"]
    if (corrected_final["support_sha256"] != support_hash or
        corrected_final["within_3px"] != int((halo & (p > 0)).sum()) or
        abs(corrected_final["overlap_within_3px"] - actual_overlap) > 1e-12 or
        abs(corrected_final["spearman_rho"] - actual_rho) > 1e-12):
        raise ValueError("literal registry counterexample does not reproduce from served bytes")
    if (card["registry"]["literal_rule_pass"] != literal_registry_pass or
        card["registry"]["final"]["pass_"] != literal_registry_pass or
        card["registry"]["final"]["max_overlap"] != actual_overlap or
        correction["literal_gate_pass"] != literal_registry_pass):
        raise ValueError("registry status flags contradict the literal overlap STOP")
    if literal_registry_pass:
        raise ValueError("unexpected passing broad gate for this frozen overlap-STOP artifact")
    prior = json.loads((root / "evidence/sibling_inventory_20261025.json").read_text())
    if card["raster_sha256"] in {r["sha256"] for r in prior["records"]}:
        raise ValueError("candidate bytes copied from an inventoried prior")
    screen = json.loads((root / "evidence/magrest/holdout_seed31.json").read_text())
    terms = {n: np.asarray(t, float) for n, t in screen["metric_terms"].items()}
    reproduced = ev.pooled_summary(terms, draws=1000, seed=310031, candidate=PRIMARY)
    for name, row in screen["holdout"]["scores"].items():
        for key in ("dti", "ci95", "tpw", "fpw", "fnw", "withheld_positive_pixels"):
            np.testing.assert_allclose(reproduced["scores"][name][key], row[key], rtol=0, atol=1e-12)
    if card["holdout_dti"] != reproduced["scores"][PRIMARY]:
        raise ValueError("displayed HOLDOUT-DTI differs from raw pooled terms")
    delta = reproduced["paired_differences"]["physical_hgb"]
    if delta != card["paired_difference"]:
        raise ValueError("paired delta/CI not reproducible")
    proxy_terms = {n: np.asarray(t, float) for n, t in screen["sgmc_terms"].items()}
    reproduced_proxy = ev.pooled_summary(proxy_terms, draws=1000, seed=310031, candidate=PRIMARY)
    if card["sgmc_proxy"] != reproduced_proxy["scores"][PRIMARY]:
        raise ValueError("SGMC proxy DTI/CI does not reproduce from frozen pooled terms")
    wins = sum(f["arms"][PRIMARY]["catalogue"]["dti"] > f["arms"]["physical_hgb"]["catalogue"]["dti"] for f in screen["folds"])
    worst = min(f["arms"][PRIMARY]["catalogue"]["dti"] - f["arms"]["physical_hgb"]["catalogue"]["dti"] for f in screen["folds"])
    scientific_pass = bool(delta["delta"] > 0 and delta["ci95"][0] > 0 and wins >= 3 and worst >= -.010)
    if scientific_pass != screen["holdout"]["screen_passed"]:
        raise ValueError("saved scientific decision does not match registered gates")
    canary = json.loads((root / "evidence/magrest/canaries_seed31.json").read_text())
    maximum_auc = max(max(r["auc"] or .5, r["reversed_auc"] or .5, r["missingness_auc"], 1-r["missingness_auc"]) for r in canary["rows"])
    if maximum_auc > .90 or not canary["pass_"]:
        raise ValueError("feature-alone leakage STOP")
    prereg_hash = sha256_file(root / "knowledge/2026-10-25_magrest_preregistration.md")
    if prereg_hash != writer_receipt["metadata"]["preregistration_sha256"]:
        raise ValueError("preregistration changed after candidate construction")
    features_receipt = json.loads((root / "evidence/magrest/features.json").read_text())
    if features_receipt["preregistration_sha256"] != prereg_hash:
        raise ValueError("feature builder and packager used different protocols")
    if features_receipt["feature_code_sha256"] != sha256_file(root / "src/gemsdoe31/magrest.py"):
        raise ValueError("feature builder changed since feature computation")
    if card["ok_to_submit"] or card["slot_approved"] or card["verdict"] != "negative":
        raise ValueError("unsupported promotion: no confirmation/global-best/provenance/selector receipts")
    if card["submission_slots_used"] != 0 or not card["ok_to_download_for_research"]:
        raise ValueError("submission/download status conflicts with recorded no-slot research run")
    if scientific_pass:
        raise ValueError("unexpected positive screen requires confirmation handling; not a negative-run receipt")
    return dict(schema_version=1, generated_utc=datetime.now(timezone.utc).isoformat(),
        file=card["file"], sha256=card["raster_sha256"],
        ok_to_download_for_research=True, ok_to_submit=False, verdict="negative",
        checks=dict(format_and_exact_template=True, binary_and_catalogue_mask=True,
            encoding_footprint_predictions_identical=True, exact_one_tiff_zip=True,
            exact_pooled_dti_and_ci_reproduced=True, original_preregistration_unchanged=True,
            served_support_matches_nine_site_audit=True, no_prior_byte_copy=True,
            registry_scope_correction_verified=True, registry_literal_rule_pass=literal_registry_pass,
            canaries_pass=True, scientific_screen_pass=False, confirmation_pass=False,
            separate_selector_approval=False, organizer_acceptance=False),
        no_human_inspection_dependency=True, positive_pixels=int((p > 0).sum()),
        registry_counterexample_overlap=actual_overlap, registry_counterexample_rho=actual_rho,
        minimum_dot_separation_m=float(nearest.min() * 100), maximum_single_feature_auc=maximum_auc,
        format_validation=reports, failed_or_unknown_gates=card["failed_or_unknown_gates"],
        scope="Integrity/denial re-derived from bytes and frozen evidence. Full prior-raster recomputation: scripts/recheck_magrest.py. No organizer acceptance or global uniqueness assertion.")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--restore-small-inputs", action="store_true")
    ap.add_argument("--out", default="docs/downloads/readiness.json")
    args = ap.parse_args()
    if args.restore_small_inputs:
        restore_small_inputs()
    result = verify()
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=1, allow_nan=False) + "\n")
    # A negative scientific decision is a successful verification, not a failed
    # build. Corrupt bytes / unsupported approval raise exceptions, failing CI.
    print(json.dumps({k: result[k] for k in ("ok_to_download_for_research", "ok_to_submit", "verdict", "sha256")}, indent=1))


if __name__ == "__main__":
    main()
