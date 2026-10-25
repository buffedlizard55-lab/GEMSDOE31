#!/usr/bin/env python3
"""Execute the single preregistered TGJ31 audit; never upload/select a submission.

Reuses the pinned shared template without evaluator or writer forks. The
continuous surface is the negative research artifact, not a copied incumbent
or a geometrically placed dot set. Duplicate gates close the scientific lane.
"""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "vendor"), str(ROOT / "scripts")]
from gems57 import evaluate_holdout, spatial, submission_writer, uniqueness  # noqa: E402
from gemsdoe31.submission import validate_submission  # noqa: E402
from gemsdoe31.transfer import build_transfer_surface  # noqa: E402
from prepare_shared_cache import CACHE_ROOT, prepare, sha256, verify_template  # noqa: E402

OUT = ROOT / "evidence/tgj31"
PREREG = ROOT / "knowledge/2026-10-25_transfer_preregistration.md"
EXPECTED_BRANCH = "arena/94fc8374-gemsdoe31"
BUFFER_PX = 213
BLOCK_SIDE = 300
BOOTSTRAP_SEED = 20261025
H33_PATH = ROOT / "data/prior_audit/GEMSDOE32/docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"
WITNESS_PATH = ROOT / "data/prior_audit/GEMSDOE48/docs/downloads/gemsdoe48-h58-continuous-pignistic-20261008T175914Z-e58.tif"


def save(name: str, data: dict) -> None:
    (OUT / name).write_text(json.dumps(data, indent=1, allow_nan=False) + "\n")


def read(path: Path) -> np.ndarray:
    with rasterio.open(path) as ds:
        return ds.read(1)


def bbox(region: np.ndarray, pad: int = 6) -> tuple[slice, slice]:
    y, x = np.nonzero(region)
    return (slice(max(0, int(y.min()) - pad), min(region.shape[0], int(y.max()) + pad + 1)),
            slice(max(0, int(x.min()) - pad), min(region.shape[1], int(x.max()) + pad + 1)))


def score_one(prediction, fold, footprint):
    sl = bbox(fold["region"])
    # The shared evaluator applies the visible mask pixel-exactly. Never use the
    # full public catalogue to remove positives from a holdout candidate.
    small = {key: fold[key][sl] for key in ("region", "truth", "visible")}
    return evaluate_holdout.evaluate(
        prediction[sl], small, footprint[sl], block_side=BLOCK_SIDE,
        origin=(sl[0].start, sl[1].start), global_shape=footprint.shape)


def canary(feature, fold, footprint, seed):
    domain = footprint & fold["region"] & ~fold["visible"]
    positives = np.flatnonzero(domain & fold["truth"] & np.isfinite(feature))
    negative = np.flatnonzero(domain & ~fold["truth"] & np.isfinite(feature))
    rng = np.random.default_rng(seed)
    if len(negative) > 50_000:
        negative = rng.choice(negative, 50_000, replace=False)
    if not len(positives) or not len(negative):
        return {"auc": None, "symmetric_auc": None, "leakage_canary_fired": True,
                "reason": "no usable positives or negatives"}
    ids = np.concatenate([positives, negative])
    y = np.concatenate([np.ones(len(positives)), np.zeros(len(negative))])
    auc = float(roc_auc_score(y, feature.ravel()[ids]))
    symmetric = max(auc, 1 - auc)
    return {"evidence_class": "LEAKAGE-CANARY", "auc": auc, "symmetric_auc": symmetric,
            "leakage_canary_fired": symmetric > 0.90, "withheld_positives_sampled": len(positives),
            "background_sampled": len(negative), "seed": seed,
            "missing_policy": "zero response outside supported measurements; no fitted missingness model"}


def runtime_index(path: Path) -> dict:
    record = json.loads(path.read_text())
    for row in record["rasters"]:
        row["cache_file"] = str(ROOT / row["cache_file"])
    return record


def perform_registry_checks(surface, final_field, footprint, grid):
    # Deep mandatory-nine audit; literal dense/off-grid controls are retained.
    index = runtime_index(ROOT / "registry/focus_raster_snapshot.json")
    reports = {}
    for phase, field in (("surface", surface), ("final_support", final_field)):
        print(f"Registry {phase}: {len(index['rasters'])} mandatory-nine byte-distinct references", flush=True)
        report = uniqueness.compare_array_to_registry(
            field, index, footprint, expected_grid=grid,
            progress=lambda i, n, row: print(f"  {phase} {i}/{n}", flush=True) if i % 20 == 0 or i == n else None)
        report["phase"] = phase
        report["no_discrete_placement"] = True
        save(f"registry_{phase}.json", report)
        reports[phase] = report
    # One same-grid universal witness proves failure independently of missing
    # extended inventory entries. Never silently exempt a continuous prior.
    witness = uniqueness.saturation_certificate(
        WITNESS_PATH, footprint, expected_grid=grid)
    witness["source_repo"] = "buffedlizard55-lab/GEMSDOE48"
    save("registry_universal_blocker.json", witness)
    rec = next(r for r in runtime_index(ROOT / "registry/prior_raster_snapshot.json")["rasters"]
               if Path(r["cache_file"]) == WITNESS_PATH)
    witness_index = {"rasters": [rec], "complete_accessible_scan": False,
                     "errors": ["Single verified universal witness, not a full extended registry scan"]}
    witness_phases = {}
    for phase, field in (("surface", surface), ("final_support", final_field)):
        result = uniqueness.compare_array_to_registry(field, witness_index, footprint, expected_grid=grid)
        save(f"registry_witness_{phase}.json", result)
        witness_phases[phase] = result
    return reports, witness, witness_phases


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reproduce", action="store_true", help="explicitly reproduce frozen artifacts; not another experiment")
    args = parser.parse_args()
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    if branch != EXPECTED_BRANCH:
        raise SystemExit(f"wrong session branch: {branch}")
    if (OUT / "run_card.json").exists():
        if not args.reproduce:
            raise SystemExit("TGJ31 is already closed; no new experiments authorized. Use --reproduce for an exact audit.")
        raise SystemExit("Closed scientific lane: retain existing immutable outputs. Re-run unit tests and verify their hashes instead.")
    OUT.mkdir(parents=True, exist_ok=True)
    pin = verify_template()
    cache_receipt = prepare()
    footprint = np.isfinite(read(ROOT / "data/sample_submission.tif"))
    catalogue = (read(ROOT / "data/labels.tif") > 0) & footprint
    rtp = np.load(CACHE_ROOT / ".cache/features/band-02.npy", mmap_mode="r")
    gravity = np.load(CACHE_ROOT / ".cache/features/band-13.npy", mmap_mode="r")
    print("Computing the one frozen TGJ31 operator, no supervised fit", flush=True)
    candidate, control, features, operator = build_transfer_surface(rtp, gravity, footprint)
    save("operator.json", operator)
    work = ROOT / "data/tgj31"
    work.mkdir(parents=True, exist_ok=True)
    np.save(work / "surface.npy", candidate)
    surface_hash = sha256(work / "surface.npy")
    main_fields = {"TGJ31": candidate, "amplitude_control": control,
                   "H33_as_is_noncomparable": read(H33_PATH)}
    # The as-is H33 reference is all-finite on the grid, but never enters a feature.
    sums = {name: np.zeros((13 * 11, 4), np.float64) for name in main_fields}
    feature_terms = {name: np.zeros((13 * 11, 4), np.float64) for name in features}
    canaries, fold_rows, split_rows = [], [], []
    # Canonical shared whole-component splitter, with buffered train masks even
    # though this is a no-fit geological operator.
    for fold in spatial.folds(catalogue, footprint, buffer_px=BUFFER_PX):
        print(f"Holdout fold {fold['fold']}: {int(fold['truth'].sum())} withheld positives", flush=True)
        split_rows.append(fold["receipt"])
        for i, (name, feature) in enumerate(features.items()):
            test = canary(feature, fold, footprint, BOOTSTRAP_SEED + 100 * fold["fold"] + i)
            canaries.append({"feature": name, "fold": fold["fold"], **test})
            result, terms = score_one(feature, fold, footprint)
            feature_terms[name] += terms
            fold_rows.append({"arm": "canary_" + name, "fold": fold["fold"], **result})
        for name, field in main_fields.items():
            result, terms = score_one(field, fold, footprint)
            sums[name] += terms
            fold_rows.append({"arm": name, "fold": fold["fold"], **result})
    summary = evaluate_holdout.pooled_summary(sums, draws=1000, seed=BOOTSTRAP_SEED, candidate="TGJ31")
    summary.update(split_version="label-blind-quadrants-v2", buffer_px=BUFFER_PX,
                   buffer_provenance="historical 21.25 km range rounded up; not a new candidate residual estimate",
                   control_comparability={"amplitude_control": "same-input no-fit physics control, output mass differs",
                                          "H33_as_is_noncomparable": "full-catalogue prune cannot be reconstructed fold-fairly"},
                   current_best_comparable_incumbent_reproduced=False, fresh_confirmation=False)
    save("holdout.json", summary)
    standalone = evaluate_holdout.pooled_summary(feature_terms, draws=1000, seed=BOOTSTRAP_SEED, candidate="jump_3")
    standalone["purpose"] = "Each input feature alone; diagnostic only, not six tuned candidate experiments"
    save("feature_alone_holdout.json", standalone)
    max_auc = max((r.get("symmetric_auc") or 1) for r in canaries)
    canary_report = {"features": canaries, "threshold": 0.90, "max_symmetric_auc": max_auc,
                     "passed": not any(r["leakage_canary_fired"] for r in canaries)}
    save("leakage_canary.json", canary_report)
    save("folds.json", {"folds": split_rows, "per_fold_results": fold_rows,
                         "split_implementation_sha256": sha256(ROOT / "vendor/gems57/spatial.py")})
    # Secondary SGMC diagnostic, independent of the operator and its parameters.
    sgmc = (read(ROOT / "data/external/derived_sgmc_faults_100m_u8.tif") == 1) & footprint
    sgmc &= distance_transform_edt(~catalogue) > 3
    proxy_sums = {name: np.zeros((13 * 11, 4), np.float64) for name in main_fields}
    h, w = footprint.shape
    yy, xx = np.ogrid[:h, :w]
    quad = (yy >= h // 2).astype(np.int8) * 2 + (xx >= w // 2).astype(np.int8)
    for k in range(4):
        fold = {"region": footprint & (quad == k), "truth": sgmc, "visible": catalogue}
        for name, field in main_fields.items():
            _, terms = score_one(field, fold, footprint)
            proxy_sums[name] += terms
    secondary = evaluate_holdout.pooled_summary(proxy_sums, draws=1000, seed=BOOTSTRAP_SEED, candidate="TGJ31")
    secondary.update(proxy="SGMC state-map faults >300 m from public catalogue", used_for_tuning=False,
                     caveat="Secondary mapped-fault proxy, not independent field truth or hidden competition truth")
    save("secondary_sgmc.json", secondary)
    # Artifact mandate: package the continuous pre-placement research field,
    # always fail-closed. No dot placement, candidate selection or slot approval.
    final = candidate.copy()
    final[catalogue] = 0  # final-file convention ONLY; never used on holdout positives
    name = f"gems31-tgj31-transfer-20261025-{surface_hash[:10]}-DO-NOT-SUBMIT"
    note = "TGJ31 gravity-magnetic transfer jumps; new continuous research surface, no copied predictions; automatic gates required; DO NOT SUBMIT"
    if len(note) > 140:
        raise AssertionError("preregistered note length exceeded 140")
    path = ROOT / "docs/downloads" / f"{name}.tif"
    receipt = submission_writer.write_submission(
        path, final, ROOT / "data/sample_submission.tif", footprint, name=name, note=note,
        catalogue=catalogue, metadata={"audit_only": True, "safe_to_submit": False,
            "hypothesis": "TGJ31-v1", "preregistration_sha256": sha256(PREREG),
            "unplaced_surface_npy_sha256": surface_hash, "copied_prior_prediction": False})
    # A second existing validator independently checks the on-disk output.
    independent = validate_submission(path, ROOT / "data/sample_submission.tif", convention="all-finite")
    save("independent_format_validation.json", independent)
    if not independent["ok_to_upload_format_only"]:
        raise AssertionError("independent format validator rejected shared-writer output")
    with rasterio.open(ROOT / "data/sample_submission.tif") as ref:
        grid = (ref.shape, ref.crs, ref.transform)
    reports, witness, witness_phases = perform_registry_checks(candidate, read(path), footprint, grid)
    # Scientific STOP. No transforms, fit, re-budget, replacement, or second
    # operator may follow a literal duplicate result.
    duplicate = any(r["duplicate_count"] for r in (*reports.values(), *witness_phases.values()))
    failures = [
        "Literal registry overlap gate fails: a same-grid prior is positive throughout the footprint",
        "No reproduced same-run current-best incumbent or fresh confirmation",
        "Lane paragraph was not supplied by the request; self-declaration is not assignment",
        "Organizer sample authenticity and current weekly cap are not independently authenticated",
    ]
    if not canary_report["passed"]:
        failures.append("Feature leakage canary requires investigation")
    score = summary["scores"]["TGJ31"]
    all_fields = [candidate, final]
    worst_rho = max((r["worst_spearman_full_footprint"] for r in reports.values()
                     if r["worst_spearman_full_footprint"] is not None), default=None)
    card = {
        "schema_version": 1, "date_utc": "2026-10-25", "hypothesis": "TGJ31-v1",
        "mechanism": "Persistent discontinuities in signed local gravity-on-RTP transfer coefficient at 300/700 m scales",
        "named_non_fault_process": "Unfaulted lithologic or intrusive contacts; source-depth changes and survey leveling seams",
        "hypothesis_class": "INFERENCE tested on public mapped-fault proxies, not a confirmed geological discovery",
        "holdout_dti": score, "paired_control_results": summary["paired_differences"],
        "secondary_holdout_dti": secondary["scores"]["TGJ31"],
        "correlation_overlap_vs_registry": {
            "required_nine_max_spearman": worst_rho,
            "required_nine_surface_max_overlap": reports["surface"]["worst_dot_overlap"],
            "required_nine_final_max_overlap": reports["final_support"]["worst_dot_overlap"],
            "required_nine_surface_report": "registry_surface.json",
            "required_nine_final_report": "registry_final_support.json",
            "extended_universal_witness_overlap": witness_phases["final_support"]["worst_dot_overlap"],
            "universal_witness_sha256": witness["witness_sha256"],
            "extended_inventory_complete": False, "literal_duplicate": bool(duplicate),
            "interpretation": "Newly computed content is not a protocol-unique lane. No density exemption was applied."},
        "raster_sha256": receipt["sha256"], "unplaced_surface_npy_sha256": surface_hash,
        "validator_output": {"shared_all_checks_passed": receipt["validator"]["all_checks_passed"],
            "independent_format_passed": independent["ok_to_upload_format_only"],
            "nan_inside_footprint": int(np.isnan(final[footprint]).sum()),
            "nan_anywhere": int(np.isnan(final).sum()), "range": [float(final.min()), float(final.max())],
            "CRS_shape_transform_match": all(independent["checks"][k]["pass_"] for k in (
                "crs_matches_template", "shape_matches_template", "transform_matches_template")),
            "single_float32_band": True, "outside_footprint_zero": bool((final[~footprint] == 0).all()),
            "zip_verified_single_tiff": True, "organizer_acceptance_verified": False},
        "submission_name": name, "note": note, "note_characters": len(note),
        "files": {"tif": str(path.relative_to(ROOT)), "zip": str(path.with_suffix('.zip').relative_to(ROOT)),
                  "writer_receipt": str(path.with_suffix('.json').relative_to(ROOT))},
        "evaluator": {"version": evaluate_holdout.VERSION, "split_version": "label-blind-quadrants-v2",
                      "withheld_positive_pixels": score["withheld_positive_pixels"],
                      "bootstrap_block_m": BLOCK_SIDE * 100, "bootstrap_resamples": 1000,
                      "implementation_sha256": summary["implementation_sha256"]},
        "leakage_canary": {"passed": canary_report["passed"], "max_symmetric_auc": max_auc, "threshold": 0.90},
        "lineage": {"shared_template_repository": pin["repository"], "shared_template_ref": pin["ref"],
                    "preregistration_sha256": sha256(PREREG), "raw_feature_sha256": cache_receipt["source_sha256"],
                    "code_sha256": sha256(Path(__file__)), "feature_code_sha256": sha256(ROOT / "src/gemsdoe31/transfer.py"),
                    "raw_input_features": ["RTP band 2", "isostatic gravity anomaly band 13"],
                    "prior_prediction_used_as_input": False,
                    "python": sys.version.split()[0],
                    "dependencies": {n: importlib.metadata.version(n) for n in ("numpy", "scipy", "rasterio", "scikit-learn")}},
        "gate_failures": failures, "verdict": "negative", "safe_to_download": True,
        "download_purpose": "Reproduce the newly generated negative audit artifact; not competition upload",
        "safe_to_submit": False, "slot_approved": False, "submission_slots_used": 0,
        "experiments_used": 1, "experiment_limit": 3, "time_limit_hours": 2,
        "scientific_stop": True, "discrete_dot_placement_performed": False,
        "surface_and_file_bounded": all(np.isfinite(a).all() and a.min() >= 0 and a.max() <= 1 for a in all_fields),
        "organizer_confirmed_score": None,
    }
    save("run_card.json", card)
    save("STOP.json", {"scientific_stop": True, "reason": "literal duplicate and unconfirmed promotion gates",
                       "new_experiments_authorized": False, "slots_used": 0})
    print(json.dumps({"verdict": card["verdict"], "safe_to_submit": False,
                      "HOLDOUT-DTI": score, "tif": card["files"]["tif"]}, indent=1))


if __name__ == "__main__":
    main()
