#!/usr/bin/env python3
"""Run the frozen MAGREST lane, with shared template cache/evaluator/writer.

No DrivenData/network calls. Run restore/audit first. All large derived arrays
stay in .cache/ or work/. A duplicate or leakage stop prevents TIFF packaging.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import time

# Keep this reproducible and avoid 64-thread overhead on the small HGB fits.
os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "vendor"), str(ROOT / "scripts")]

import numpy as np  # noqa: E402
import rasterio  # noqa: E402
from scipy.ndimage import distance_transform_edt  # noqa: E402
from sklearn.ensemble import HistGradientBoostingClassifier  # noqa: E402
from sklearn.metrics import roc_auc_score  # noqa: E402
from threadpoolctl import threadpool_limits  # noqa: E402

from gems57 import evaluate_holdout as shared_eval  # noqa: E402
from gems57.grid import Grid  # noqa: E402
from gems57.holdout import buffered_component_draw  # noqa: E402
from gems57.submission_writer import write_submission  # noqa: E402
from gemsdoe31.magrest import NAMES, build_features, spaced_dots  # noqa: E402
from gemsdoe31 import novelty  # noqa: E402
from gemsdoe31.submission import sha256_file, validate_submission  # noqa: E402

CACHE = ROOT / ".cache/magrest"
EVIDENCE = ROOT / "evidence/magrest"
BUDGET = 37_654
BUFFER_PX = 213
PRIMARY = "magrest_concordant"
PREREG = ROOT / "knowledge/2026-10-25_magrest_preregistration.md"


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=1, allow_nan=False) + "\n")


def verify_inputs():
    pins = json.loads((ROOT / "registry/template_pins.json").read_text())
    for name, item in pins["files"].items():
        if sha256_file(ROOT / "vendor/gems57" / name) != item["sha256"]:
            raise ValueError(f"shared template modified: {name}")
    manifest = json.loads((ROOT / "registry/data_manifest.json").read_text())
    for item in manifest["files"]:
        if sha256_file(ROOT / "data" / item["dest"]) != item["sha256"]:
            raise ValueError(f'input hash drift: {item["id"]}')
    cached = json.loads((ROOT / "evidence/feature_cache.json").read_text())
    if cached["source_sha256"] != manifest["files"][0]["sha256"]:
        raise ValueError("feature cache source drift")
    for item in cached["bands"]:
        if sha256_file(ROOT / item["cache_file"]) != item["sha256"]:
            raise ValueError("feature cache byte drift")
    with rasterio.open(ROOT / "data/sample_submission.tif") as ds:
        fp = np.isfinite(ds.read(1))
        crs, transform = ds.crs, ds.transform
    with rasterio.open(ROOT / "data/labels.tif") as ds:
        cat = ds.read(1) == 1
    return Grid(fp, cat, crs, transform, *fp.shape)


def features(grid):
    path = CACHE / "responses.npy"
    receipt_path = EVIDENCE / "features.json"
    frozen = dict(preregistration_sha256=sha256_file(PREREG),
                  feature_code_sha256=sha256_file(ROOT / "src/gemsdoe31/magrest.py"),
                  raw_cached_band_sha256=sha256_file(ROOT / ".cache/features/band-02.npy"))
    if path.exists():
        receipt = json.loads(receipt_path.read_text())
        if any(receipt.get(k) != v for k, v in frozen.items()) or sha256_file(path) != receipt["array_sha256"]:
            raise ValueError("stale feature cache; do not silently overwrite experimental evidence")
    else:
        rtp = np.load(ROOT / ".cache/features/band-02.npy", mmap_mode="r")
        f, diag = build_features(rtp, grid.footprint)
        np.save(path, f)
        save(receipt_path, {**diag, **frozen, "array_sha256": sha256_file(path),
                            "built_utc": datetime.now(timezone.utc).isoformat()})
    return np.load(path, mmap_mode="r")


def control_features(grid):
    path = CACHE / "control_features.npy"
    fi = np.flatnonzero(grid.footprint.ravel())
    names = [f"physical_band_{i:02d}" for i in range(1, 20)]
    with rasterio.open(ROOT / "data/external/lidar_scarp_features_u8.tif") as ds:
        names += [f"lidar_{s or i}" for i, s in enumerate(ds.descriptions, 1)]
    if not path.exists():
        x = np.lib.format.open_memmap(path, mode="w+", dtype="float32", shape=(31, len(fi)))
        for i in range(19):
            x[i] = np.load(ROOT / f".cache/features/band-{i+1:02d}.npy", mmap_mode="r").ravel()[fi]
        with rasterio.open(ROOT / "data/external/lidar_scarp_features_u8.tif") as ds:
            for i in range(12):
                a = ds.read(i + 1).astype(np.float32).ravel()[fi]
                a[a == 0] = np.nan
                x[19 + i] = a
        x.flush()
    return np.load(path, mmap_mode="r"), fi, names


def canaries(arrays, names, fi, folds, grid):
    lookup = np.full(grid.footprint.size, -1, np.int32)
    lookup[fi] = np.arange(len(fi))
    rows, stop = [], False
    for fold in folds:
        pos = np.flatnonzero(fold["truth"].ravel())
        active = grid.footprint & fold["region"] & ~fold["masked_known"]
        negative = np.flatnonzero((active & ~fold["truth"]).ravel())
        rng = np.random.default_rng(31000 + fold["fold"])
        neg = rng.choice(negative, min(50_000, len(negative)), replace=False)
        ids = np.r_[pos, neg]
        y = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
        for name, values in zip(names, arrays):
            v = np.asarray(values[lookup[ids]], float)
            finite = np.isfinite(v)
            if finite.sum() == 0 or len(np.unique(y[finite])) != 2:
                auc = None
                reversed_auc = None
            else:
                auc = float(roc_auc_score(y[finite], v[finite]))
                reversed_auc = 1 - auc
            alarm = auc is not None and max(auc, reversed_auc) > .90
            # Missingness is a separate univariate canary, not quietly discarded.
            missing_auc = float(roc_auc_score(y, (~finite).astype(float)))
            alarm |= max(missing_auc, 1 - missing_auc) > .90
            rows.append(dict(fold=fold["name"], feature=name, positive_pixels=len(pos),
                             negative_pixels=len(neg), finite_sample_pixels=int(finite.sum()),
                             auc=auc, reversed_auc=reversed_auc, missingness_auc=missing_auc,
                             leakage_alarm=bool(alarm)))
            stop |= alarm
    return dict(evidence_class="COMPUTED leakage diagnostic; NOT DTI", threshold=.90,
                pass_=not stop, no_label_derived_features=True, rows=rows)


def score_prediction(pred, fold, grid, *, truth=None, known=None):
    region = fold["region"]
    ys, xs = np.nonzero(region)
    sl = (slice(max(0, int(ys.min()) - 3), min(grid.height, int(ys.max()) + 4)),
          slice(max(0, int(xs.min()) - 3), min(grid.width, int(xs.max()) + 4)))
    f = dict(region=region[sl], truth=(fold["truth"] if truth is None else truth)[sl],
             masked_known=(fold["masked_known"] if known is None else known)[sl], visible=fold["visible"][sl])
    return shared_eval.evaluate(pred[sl].astype(np.float32), f, grid.footprint[sl],
                                block_side=200, origin=(sl[0].start, sl[1].start), global_shape=grid.shape)


def fit_control(x, fi, fold, quad, grid):
    q = fold["fold"]
    separated = distance_transform_edt(quad != q) > BUFFER_PX
    train = grid.footprint & (quad != q) & separated & ~fold["hidden_all"]
    pos = np.flatnonzero((train & fold["visible"]).ravel()[fi])
    pool = np.flatnonzero((train & ~grid.catalogue).ravel()[fi])
    rng = np.random.default_rng(3100 + q)
    neg = rng.choice(pool, min(90_000, len(pool)), replace=False)
    ids = np.r_[pos, neg]
    y = np.r_[np.ones(len(pos), dtype=np.uint8), np.zeros(len(neg), dtype=np.uint8)]
    if not len(pos) or not len(neg):
        raise ValueError("empty buffered training class")
    model = HistGradientBoostingClassifier(max_iter=100, learning_rate=.12, max_leaf_nodes=31,
        min_samples_leaf=50, l2_regularization=1, class_weight={0: 1, 1: 5}, early_stopping=False,
        random_state=31 + q)
    with threadpool_limits(limits=2):
        model.fit(x[:, ids].T, y)
        active = grid.footprint & fold["region"] & ~fold["masked_known"]
        target = np.flatnonzero(active.ravel()[fi])
        p = np.zeros(grid.shape, np.float32)
        for start in range(0, len(target), 100_000):
            batch = target[start:start+100_000]
            p.ravel()[fi[batch]] = model.predict_proba(x[:, batch].T)[:, 1]
    return p, dict(fold=fold["name"], train_positive_pixels=len(pos), train_background_pixels=len(neg),
                   spatial_buffer_px=BUFFER_PX, catalogue_features_used=False,
                   hidden_positive_pixels_in_training=int((train & fold["hidden_all"]).sum()),
                   nearest_training_to_test_quadrant_px=float(distance_transform_edt(quad != q)[train].min()))


def evaluate_screen(f, x, fi, grid, *, seed):
    folds, quad = buffered_component_draw(grid, seed=seed, hide_frac=.20, buffer_px=BUFFER_PX,
                                          boundary_px=BUFFER_PX)
    raw_names = [f"physical_{i:02d}" for i in range(1, 32)]
    canary = canaries(list(f.reshape(3, -1)[:, fi]) + list(x), list(NAMES) + raw_names, fi, folds, grid)
    save(EVIDENCE / f"canaries_seed{seed}.json", canary)
    if not canary["pass_"]:
        raise RuntimeError("LEAKAGE STOP: a single-feature/missingness AUC exceeds .90")
    terms = {n: np.zeros((323, 4), float) for n in (*NAMES, "physical_hgb")}
    proxy_terms = {n: np.zeros((323, 4), float) for n in terms}
    with rasterio.open(ROOT / "data/external/derived_sgmc_faults_100m_u8.tif") as ds:
        sgmc = ds.read(1) == 1
    proxy_truth = sgmc & grid.footprint & (distance_transform_edt(~grid.catalogue) > 3)
    rows, control_receipts = [], []
    for fold in folds:
        allowed = grid.footprint & fold["region"] & ~fold["masked_known"]
        budget = round(BUDGET * int((grid.footprint & fold["region"]).sum()) / int(grid.footprint.sum()))
        p, rec = fit_control(x, fi, fold, quad, grid)
        control_receipts.append(rec)
        predictions = {n: spaced_dots(f[i], allowed, budget) for i, n in enumerate(NAMES)}
        predictions["physical_hgb"] = spaced_dots(p, allowed, budget)
        per_fold = {}
        for name, pred in predictions.items():
            score, t = score_prediction(pred, fold, grid)
            terms[name] += t
            proxy, pt = score_prediction(pred, fold, grid, truth=proxy_truth, known=grid.catalogue)
            proxy_terms[name] += pt
            per_fold[name] = dict(catalogue=score, sgmc_proxy=proxy)
        rows.append(dict(fold=fold["name"], draw_receipt=fold["receipt"], budget=budget, arms=per_fold))
        print(f"[holdout seed={seed}] {fold['name']}: withheld={fold['truth'].sum()} budget={budget}", flush=True)
    summary = shared_eval.pooled_summary(terms, draws=1000, seed=310031, candidate=PRIMARY)
    # Other candidate arms are diagnostics, not genuine control methods.
    control_delta = summary["paired_differences"]["physical_hgb"]
    summary["best_comparable_control"] = "physical_hgb"
    summary["candidate_arms_are_not_controls"] = list(NAMES)
    summary["paired_difference_vs_physical_control"] = control_delta
    wins = sum(r["arms"][PRIMARY]["catalogue"]["dti"] > r["arms"]["physical_hgb"]["catalogue"]["dti"] for r in rows)
    worst = min(r["arms"][PRIMARY]["catalogue"]["dti"] - r["arms"]["physical_hgb"]["catalogue"]["dti"] for r in rows)
    summary["screen_passed"] = bool(control_delta["delta"] > 0 and control_delta["ci95"][0] > 0 and wins >= 3 and worst >= -.010)
    summary["quadrant_wins"] = wins
    summary["worst_quadrant_delta"] = worst
    proxy = shared_eval.pooled_summary(proxy_terms, draws=1000, seed=310031, candidate=PRIMARY)
    proxy.update(instrument="SGMC-PROXY; never training truth; NOT hidden competition truth",
                 truth_count_meaning="SGMC positives outside catalogue >300m in the same evaluation regions; withheld from all fitting",
                 best_comparable_control="physical_hgb")
    out = dict(seed=seed, holdout=summary, sgmc_proxy=proxy, folds=rows, control_training=control_receipts,
               metric_terms={n: t.tolist() for n, t in terms.items()},
               sgmc_terms={n: t.tolist() for n, t in proxy_terms.items()},
               range_status="inherited 21.25km historical residual range rounded to 21.3km; own-MAGREST range unestimated",
               global_current_holdout_best_status="unknown: legacy instruments/masks not comparable; blocks promotion")
    save(EVIDENCE / f"holdout_seed{seed}.json", out)
    return out


def package(f, grid, index, preflight, screen, confirmation):
    # Placement is not trained/tuned against registry halos or holdout outcomes.
    allowed = grid.footprint & ~grid.catalogue
    pred = spaced_dots(f[2], allowed, BUDGET)
    final_audit = novelty.audit(ROOT, {PRIMARY: pred.astype(np.float32)}, grid.footprint,
                                {PRIMARY: pred}, index, phase="final-dots")
    save(EVIDENCE / "novelty_final.json", final_audit)
    if not final_audit["arms"][PRIMARY]["pass_"]:
        raise RuntimeError("DUPLICATE STOP: final dots exceed a registry threshold")
    content_digest = hashlib.sha256(np.packbits(pred.ravel()).tobytes()).hexdigest()
    name = f"gemsdoe31-magrest-concordant-{int(pred.sum())}-20261025-{content_digest[:10]}"
    note = "MAGREST reciprocal magnetic texture restoration; 2/4px same-sign concordance; independent dots; research-only, not slot-approved"
    path = ROOT / "docs/downloads" / f"{name}-zeros.tif"
    receipt = write_submission(path, pred.astype(np.float32), ROOT / "data/sample_submission.tif", grid.footprint,
        note=note, name=name, catalogue=grid.catalogue,
        metadata=dict(preregistration_sha256=sha256_file(PREREG), primary_arm=PRIMARY,
                      content_support_sha256=content_digest, scientific_status="research-only"))
    # Reuse the existing common NaN-convention writer, after its no-clipping fix.
    from build_submission import write_variants
    variants = write_variants(pred, grid.footprint, ROOT / "docs/downloads" / name, name=name)
    # The shared writer already produced the primary zeros encoding. Do not
    # publish a redundant third TIFF with the same predictions under another name.
    variants["allfinite"].unlink()
    nan_validation = validate_submission(variants["nan"], ROOT / "data/sample_submission.tif")
    zeros_validation = validate_submission(path, ROOT / "data/sample_submission.tif", convention="all-finite")
    if not nan_validation["ok_to_upload_format_only"] or not zeros_validation["ok_to_upload_format_only"]:
        raise ValueError("packaged file failed final template validation")
    failed = []
    if not screen["holdout"]["screen_passed"]:
        failed.append("paired spatial holdout screen failed")
    if confirmation is None:
        failed.append("fresh confirmation not passed")
    elif not confirmation["holdout"]["screen_passed"]:
        failed.append("fresh confirmation failed")
    failed += ["own-method residual range not estimated", "global current-best comparison unavailable on identical instrument",
               "organizer-authenticated data/template provenance unverified", "outside-footprint organizer convention unresolved",
               "separate selector has not promoted this artifact; weekly cap not checked"]
    summary = screen["holdout"]["scores"][PRIMARY]
    card = dict(schema_version=1, hypothesis="MAGREST: lateral restoration of displaced magnetic texture",
        mechanism="same-sign 2/4px cross-flank patch-correlation gain over unshifted null; no inherited dots",
        non_fault_mimic="volcanic-flow lithologic contacts or airborne magnetic survey-line seams",
        holdout_dti=summary, holdout_comparator=screen["holdout"]["scores"]["physical_hgb"],
        paired_difference=screen["holdout"]["paired_difference_vs_physical_control"],
        sgmc_proxy=screen["sgmc_proxy"]["scores"][PRIMARY],
        registry=dict(scope=index["scope"], comparable_files=index["comparable_files"],
            distinct_prediction_fields=len(index["entries"]),
            surface={k: v for k, v in preflight["arms"][PRIMARY].items() if k != "comparisons"},
            final={k: v for k, v in final_audit["arms"][PRIMARY].items() if k != "comparisons"},
            global_uniqueness_proven=False),
        raster_sha256=receipt["sha256"], validator=dict(zeros=zeros_validation, nan=nan_validation),
        submission_name=name, note=note, verdict="negative", ok_to_download_for_research=True,
        ok_to_submit=False, slot_approved=False, submission_slots_used=0, failed_or_unknown_gates=failed,
        file=str(path.relative_to(ROOT)), zip_file=str(path.with_suffix(".zip").relative_to(ROOT)),
        nan_file=str(variants["nan"].relative_to(ROOT)), nan_zip=str(variants["zip"].relative_to(ROOT)),
        generated_utc=datetime.now(timezone.utc).isoformat(),
        evaluator_implementation_sha256=shared_eval.implementation_hashes(),
        no_organizer_receipt=True)
    save(EVIDENCE / "run_card.json", card)
    save(ROOT / "docs/downloads/magrest-run-card.json", card)
    save(ROOT / "registry/current_run.json", card)
    return card


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", choices=("features", "novelty", "screen", "package", "all"), default="all")
    args = ap.parse_args()
    correction_path = EVIDENCE / "registry_scope_correction.json"
    if correction_path.exists() and not json.loads(correction_path.read_text())["literal_gate_pass"]:
        raise SystemExit("STOP: registered lattice overlap exceeds 70%; no further fit, tuning or TIFF. Use verify_current_run.py for read-only release verification.")
    start = time.monotonic()
    CACHE.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    grid = verify_inputs()
    f = features(grid)
    if args.stage == "features":
        print("MAGREST feature cache verified")
        return
    inventory = json.loads((ROOT / "evidence/sibling_inventory_20261025.json").read_text())
    index_path = ROOT / "evidence/magrest_registry_index.json"
    index = json.loads(index_path.read_text()) if index_path.exists() else novelty.build_index(ROOT, inventory, grid.footprint)
    pre_path = EVIDENCE / "novelty_surface.json"
    if pre_path.exists():
        preflight = json.loads(pre_path.read_text())
    else:
        surfaces = dict(zip(NAMES, f))
        supports = {n: novelty.prospective_support(s, grid.footprint & ~grid.catalogue, BUDGET) for n, s in surfaces.items()}
        preflight = novelty.audit(ROOT, surfaces, grid.footprint, supports, index, phase="surface-before-placement")
        save(pre_path, preflight)
    if any(not v["pass_"] for v in preflight["arms"].values()):
        raise RuntimeError("DUPLICATE STOP: surface/prospective support exceeds registry limit")
    print("[novelty] pre-placement PASS for all three frozen variants", flush=True)
    if args.stage == "novelty":
        return
    screen_path = EVIDENCE / "holdout_seed31.json"
    if screen_path.exists():
        screen = json.loads(screen_path.read_text())
    else:
        x, fi, _ = control_features(grid)
        screen = evaluate_screen(f, x, fi, grid, seed=31)
    confirmation = None
    if screen["holdout"]["screen_passed"]:
        x, fi, _ = control_features(grid)
        confirm_path = EVIDENCE / "holdout_seed32.json"
        confirmation = json.loads(confirm_path.read_text()) if confirm_path.exists() else evaluate_screen(f, x, fi, grid, seed=32)
    if args.stage == "screen":
        return
    if time.monotonic() - start > 7200:
        raise RuntimeError("two-hour budget exhausted; packaging stopped")
    card = package(f, grid, index, preflight, screen, confirmation)
    print(json.dumps({k: card[k] for k in ("file", "raster_sha256", "holdout_dti", "verdict", "ok_to_submit")}, indent=1))


if __name__ == "__main__":
    main()
