#!/usr/bin/env python3
"""H31-N lane runner. Preregistered in knowledge/2026-10-26_h31n_pseudogravity_preregistration.md.

Three experiments maximum. Does not copy prior dots. Uses the shared template
evaluator and submission writer. A format-valid TIFF is not slot approval.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt, label
from scipy.stats import rankdata
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "vendor"), str(ROOT / "scripts")]

from gems57.evaluate_holdout import evaluate, pooled_summary  # noqa: E402
from gems57.grid import TRANSFORM, Grid  # noqa: E402
from gems57.holdout import buffered_component_draw  # noqa: E402
from gems57.metric import dti_exact  # noqa: E402
from gems57.submission_writer import write_submission  # noqa: E402
from gemsdoe31.emission import emit_dots  # noqa: E402
from gemsdoe31.h31n_pseudogravity import FEATURE_NAMES, pseudogravity_features  # noqa: E402
from gemsdoe31.variogram import (  # noqa: E402
    VariogramFitError,
    bootstrap_range_interval,
    empirical_semivariogram,
)

BUDGET = 37654
SEPARATION_PX = 2.8
COLLAR_PX = 250  # 25 km, preregistered conservative exclusion, not an empirical range
NEGATIVES = 150_000
SEED = 31026
SCREEN_SEED = 41
CONFIRM_SEED = 42
RHO_LIMIT = 0.90
OVERLAP_LIMIT = 0.70


def log(message: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {message}", flush=True)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_grid():
    with rasterio.open(ROOT / "data/sample_submission.tif") as sample:
        footprint = np.isfinite(sample.read(1))
        crs = sample.crs
    with rasterio.open(ROOT / "data/labels.tif") as labels:
        catalogue = (labels.read(1) == 1) & footprint
    grid = Grid(footprint=footprint, catalogue=catalogue, crs=crs, transform=TRANSFORM,
                height=footprint.shape[0], width=footprint.shape[1])
    return grid


def load_band(number: int) -> np.ndarray:
    path = ROOT / f".cache/features/band-{number:02d}.npy"
    array = np.load(path, mmap_mode="r")
    out = np.array(array, dtype=np.float32, copy=True)
    del array
    out[~np.isfinite(out)] = 0.0
    return out


def symmetric_auc(y_true, scores) -> float:
    if len(np.unique(y_true)) < 2:
        return float("nan")
    auc = float(roc_auc_score(y_true, scores))
    return max(auc, 1.0 - auc)


def fit_hgb(x_train, y_train):
    model = HistGradientBoostingClassifier(
        max_iter=100, learning_rate=0.08, max_leaf_nodes=31, min_samples_leaf=50,
        l2_regularization=1.0, early_stopping=False, random_state=SEED,
    )
    model.fit(x_train, y_train)
    return model


def stack_rows(bands, novel, columns, flat_index) -> np.ndarray:
    pieces = []
    for column in columns:
        source = bands[column] if column < 19 else novel[column - 19]
        pieces.append(np.asarray(source, dtype=np.float32).ravel()[flat_index])
    matrix = np.stack(pieces, axis=1)
    matrix[~np.isfinite(matrix)] = 0.0
    return matrix


def predict_surface(model, bands, novel, columns, shape) -> np.ndarray:
    height, width = shape
    out = np.zeros(shape, dtype=np.float32)
    for r0 in range(0, height, 128):
        r1 = min(height, r0 + 128)
        block = np.stack([
            np.asarray(bands[c][r0:r1] if c < 19 else novel[c - 19][r0:r1], dtype=np.float32).reshape(-1)
            for c in columns
        ], axis=1)
        block[~np.isfinite(block)] = 0.0
        out[r0:r1] = model.predict_proba(block)[:, 1].reshape(r1 - r0, width)
    return out


def train_indices(positive, negative, rng):
    pos = np.flatnonzero(np.asarray(positive, dtype=bool).ravel())
    neg_pool = np.flatnonzero(np.asarray(negative, dtype=bool).ravel())
    if pos.size < 20 or neg_pool.size < 20:
        raise RuntimeError(f"training split too small: pos={pos.size} neg={neg_pool.size}")
    neg = rng.choice(neg_pool, size=min(NEGATIVES, neg_pool.size), replace=False)
    return np.concatenate([pos, neg])


def score_emission(dots, fold, footprint):
    pred = np.where(footprint, dots.astype(np.float32), 0.0)
    result, terms = evaluate(pred, fold, footprint, block_side=200)
    return result, terms


def disk(radius: float = 3.0) -> np.ndarray:
    r = int(np.ceil(radius))
    yy, xx = np.ogrid[-r:r + 1, -r:r + 1]
    return yy * yy + xx * xx <= radius * radius


STRUCT = disk(3.0)


def spearman(candidate_ranks, other, footprint) -> float:
    values = np.where(np.isfinite(other[footprint]), other[footprint], 0.0)
    ranks = rankdata(values).astype(np.float64)
    ranks -= ranks.mean()
    denom = ranks.std()
    if denom == 0 or candidate_ranks is None:
        return 0.0
    ranks /= denom
    return float(np.dot(candidate_ranks, ranks) / ranks.size)


def footprint_ranks(field, footprint):
    values = np.where(np.isfinite(field[footprint]), field[footprint], 0.0)
    if np.unique(values).size < 2:
        return None
    ranks = rankdata(values).astype(np.float64)
    ranks -= ranks.mean()
    ranks /= ranks.std() + 1e-12
    return ranks


def dot_overlap(mine, theirs, footprint) -> float:
    mine_on = np.asarray(mine, dtype=bool) & footprint
    theirs_on = footprint & np.isfinite(theirs) & (theirs > 0)
    if not mine_on.any() or not theirs_on.any():
        return 0.0
    return float(binary_dilation(theirs_on, structure=STRUCT)[mine_on].mean())


def iter_comparison_rasters():
    roots = [ROOT / "docs/downloads", ROOT / "data/prior_audit/peers"]
    seen = set()
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.tif")):
            digest = sha256_file(path)
            if digest in seen:
                continue
            seen.add(digest)
            yield path, digest


def compare(field, dots, footprint, limit_rows=None):
    ranks = footprint_ranks(field, footprint)
    rows = []
    worst_rho = 0.0
    worst_ov = 0.0
    for path, digest in iter_comparison_rasters():
        try:
            with rasterio.open(path) as src:
                if src.shape != footprint.shape:
                    rows.append({"file": str(path.relative_to(ROOT)), "error": "shape mismatch", "sha256": digest})
                    continue
                other = src.read(1)
        except Exception as exc:  # raster-specific, recorded, not swallowed silently
            rows.append({"file": str(path.relative_to(ROOT)), "error": str(exc), "sha256": digest})
            continue
        rho = None if ranks is None else abs(spearman(ranks, other, footprint))
        overlap = dot_overlap(dots, other, footprint) if dots is not None else None
        row = {
            "file": str(path.relative_to(ROOT)),
            "sha256": digest,
            "abs_spearman": rho,
            "dot_overlap_3px": overlap,
        }
        rows.append(row)
        if rho is not None:
            worst_rho = max(worst_rho, rho)
        if overlap is not None:
            worst_ov = max(worst_ov, overlap)
        if limit_rows and len(rows) >= limit_rows:
            break
    return {
        "compared": len(rows),
        "worst_abs_spearman": worst_rho,
        "worst_dot_overlap_3px": worst_ov,
        "rho_limit": RHO_LIMIT,
        "overlap_limit": OVERLAP_LIMIT,
        "scientific_duplicate": worst_rho > RHO_LIMIT or worst_ov > OVERLAP_LIMIT,
        "rows": rows,
    }


def write_card(payload: dict) -> None:
    out = ROOT / "evidence/h31n"
    out.mkdir(parents=True, exist_ok=True)
    (out / "run_card.json").write_text(json.dumps(payload, indent=1, allow_nan=False) + "\n")
    log(f"wrote evidence/h31n/run_card.json verdict={payload.get('verdict')}")


def main() -> int:
    log("H31-N start")
    grid = load_grid()
    fp, cat = grid.footprint, grid.catalogue
    log(f"footprint {int(fp.sum())} catalogue {int(cat.sum())}")
    rtp = load_band(2)
    tmi_hg = load_band(3)
    grav = load_band(13)
    log("computing pseudogravity features")
    novel_map = pseudogravity_features(rtp, grav, tmi_hg, fp)
    novel = [novel_map[name] for name in FEATURE_NAMES]
    del rtp, tmi_hg, grav
    bands = [load_band(i) for i in range(1, 20)]
    log("19 template bands loaded")

    # EXP-1 canary
    rng = np.random.default_rng(SEED)
    sample = rng.choice(np.flatnonzero(fp.ravel()), size=400_000, replace=False)
    y = cat.ravel()[sample]
    canary = {}
    for name, array in zip(FEATURE_NAMES, novel, strict=True):
        canary[name] = symmetric_auc(y, array.ravel()[sample])
    canary["control_rtp_band02"] = symmetric_auc(y, bands[1].ravel()[sample])
    max_auc = max(canary[name] for name in FEATURE_NAMES)
    log(f"EXP-1 canary max symmetric AUC {max_auc:.4f} {canary}")
    if max_auc > 0.90:
        write_card({
            "hypothesis": "Poisson pseudogravity residual edge",
            "verdict": "negative",
            "stop": "leakage canary",
            "leakage_canary": canary,
            "ok_to_download_for_research": False,
            "ok_to_submit": False,
            "slot_approved": False,
        })
        log("LEAKAGE STOP")
        return 2

    # Lattice coverage, measured this run.
    lattice_path = ROOT / ".cache/registry-scope/registered-lattice.tif"
    with rasterio.open(lattice_path) as src:
        lattice = src.read(1)
    lattice_on = fp & np.isfinite(lattice) & (lattice > 0)
    lattice_dist = distance_transform_edt(~lattice_on)
    lattice_coverage = float((lattice_dist[fp] <= 3).mean())
    log(f"lattice 3px footprint coverage {lattice_coverage:.6f}")

    columns = {"base19": list(range(19)), "h31n": list(range(23))}

    def run_seed(seed: int, tag: str):
        folds, quad = buffered_component_draw(grid, seed=seed, hide_frac=0.20, buffer_px=3, boundary_px=12)
        terms = {name: [] for name in columns}
        fold_dti = {name: [] for name in columns}
        surfaces = {}
        hidden = folds[0]["hidden_all"]
        for fold in folds:
            # Collar is around THIS fold's withheld truth only. A map-wide collar around every
            # quadrant's hidden strands left 39 training positives (implementation bug, stopped
            # before any DTI was recorded). Visible faults already exclude the global hidden draw.
            d_truth = distance_transform_edt(~fold["truth"])
            outside = fp & (quad != fold["fold"]) & (d_truth > COLLAR_PX)
            positive = fold["visible"] & outside
            negative = outside & ~cat
            n_pos = int(positive.sum())
            if n_pos < 500:
                raise RuntimeError(f"{tag} {fold['name']} has only {n_pos} training positives; collar/split is degenerate")
            train_idx = train_indices(positive, negative, rng)
            y_train = cat.ravel()[train_idx].astype(np.int8)
            d_known = distance_transform_edt(~fold["masked_known"])
            emit_valid = fold["region"] & fp & (d_known > 2.0)
            n_dots = int(round(BUDGET * fold["region"].sum() / fp.sum()))
            log(f"{tag} fold {fold['name']} truth {int(fold['truth'].sum())} train_pos {int(y_train.sum())} dots {n_dots}")
            for name, cols in columns.items():
                model = fit_hgb(stack_rows(bands, novel, cols, train_idx), y_train)
                surface = predict_surface(model, bands, novel, cols, fp.shape)
                surfaces[(name, fold["fold"])] = surface
                dots = emit_dots(surface, emit_valid, max_dots=n_dots, min_distance_px=SEPARATION_PX)
                result, block_terms = score_emission(dots, fold, fp)
                terms[name].append(block_terms)
                fold_dti[name].append({
                    "fold": fold["name"],
                    "dti": result["dti"],
                    "withheld_positive_pixels": result["n_truth"],
                    "emitted": result["emitted"],
                })
                log(f"  {name} DTI {result['dti']:.4f}")
        stacked = {name: np.concatenate(parts, axis=0) for name, parts in terms.items()}
        summary = pooled_summary(stacked, draws=1000, seed=520810, candidate="h31n")
        return summary, fold_dti, surfaces, hidden, folds

    log("EXP-2 screen seed 41")
    screen, fold_dti, surfaces, hidden, folds = run_seed(SCREEN_SEED, "screen")
    h31n_score = screen["scores"]["h31n"]
    base_score = screen["scores"]["base19"]
    paired = screen["paired_differences"]["base19"]
    log(f"screen h31n {h31n_score['dti']:.4f} base {base_score['dti']:.4f} delta {paired['delta']:.4f} CI {paired['ci95']}")

    # Variogram from OOF probability residuals on withheld traces.
    variogram_report = {"status": "not_fit"}
    try:
        comp, _n = label(hidden)
        rows, cols = np.nonzero(hidden & fp)
        # Average the four fold surfaces only where that fold withheld the pixel.
        residual = np.zeros(rows.shape, dtype=np.float64)
        fold_id = np.full(rows.shape, -1, dtype=np.int32)
        for fold in folds:
            sel = fold["truth"][rows, cols]
            surface = surfaces[("h31n", fold["fold"])]
            residual[sel] = 1.0 - surface[rows[sel], cols[sel]]
            fold_id[sel] = fold["fold"]
        in_some = fold_id >= 0
        for fold in folds:
            in_some |= fold["truth"][rows, cols]
        vario = empirical_semivariogram(
            rows[in_some], cols[in_some], comp[rows[in_some], cols[in_some]], residual[in_some],
            fold_id[in_some], np.zeros(int(in_some.sum()), dtype=np.int32),
        )
        fitted = bootstrap_range_interval(vario, n_bootstrap=50, seed=20261026)
        upper_m = float(fitted["bootstrap"]["range_95_sill_ci_m"][1])
        variogram_report = {
            "status": "fit",
            "practical_range_95_m": fitted["point_fit"]["practical_range_95_sill_m"],
            "upper_95_m": upper_m,
            "collar_used_m": COLLAR_PX * 100,
            "collar_covers_upper_95": upper_m <= COLLAR_PX * 100,
            "n_residuals": vario.n_residuals,
            "stable": fitted["stable"],
        }
        log(f"variogram range {variogram_report['practical_range_95_m']:.0f} m upper {upper_m:.0f} m")
    except (VariogramFitError, ValueError) as exc:
        variogram_report = {"status": "failed", "error": str(exc), "collar_used_m": COLLAR_PX * 100,
                            "note": "25 km exclusion was preregistered and is not this method's measured range"}
        log(f"variogram failed: {exc}")

    wins = sum(a["dti"] > b["dti"] for a, b in zip(fold_dti["h31n"], fold_dti["base19"], strict=True))
    screen_pass = (
        paired["delta"] > 0
        and paired["ci95"][0] > 0
        and wins >= 3
        and variogram_report.get("collar_covers_upper_95") is True
    )
    log(f"screen_pass={screen_pass} quadrant_wins={wins}/4 variogram={variogram_report.get('status')}")

    confirmation = None
    if screen_pass:
        log("EXP-3 confirmation seed 42")
        confirmation, conf_folds, _, _, _ = run_seed(CONFIRM_SEED, "confirm")
        conf_wins = sum(a["dti"] > b["dti"] for a, b in zip(conf_folds["h31n"], conf_folds["base19"], strict=True))
        conf_paired = confirmation["paired_differences"]["base19"]
        confirm_pass = conf_paired["delta"] > 0 and conf_paired["ci95"][0] > 0 and conf_wins >= 3
    else:
        confirm_pass = False
        log("EXP-3 confirmation skipped; screen gate did not pass")

    # Full-map surface for uniqueness, then dots only if the surface is not a peer duplicate.
    log("full-catalogue fit")
    full_idx = train_indices(cat, fp & ~cat, rng)
    full_model = fit_hgb(stack_rows(bands, novel, columns["h31n"], full_idx), cat.ravel()[full_idx].astype(np.int8))
    surface = predict_surface(full_model, bands, novel, columns["h31n"], fp.shape)
    d_cat = distance_transform_edt(~cat)
    prospective = np.zeros(fp.shape, dtype=bool)
    valid_final = fp & (d_cat > 2.0)
    order = np.argsort(np.where(valid_final, surface, -1.0).ravel())[::-1]
    take = order[:BUDGET]
    prospective.ravel()[take] = True
    prospective &= valid_final
    log("uniqueness vs local downloads and pinned peers")
    pre = compare(surface, prospective, fp)
    worst_pre = max(pre["rows"], key=lambda r: r.get("dot_overlap_3px") or -1)
    log(f"pre-placement worst |rho| {pre['worst_abs_spearman']:.4f} prospective overlap {pre['worst_dot_overlap_3px']:.4f} file {worst_pre.get('file')}")
    # Surface rank-correlation is the pre-placement gate. Raw top-K overlap is recorded but is not
    # the preregistered emitter; the 70% rule is applied to the Poisson dots below.
    if pre["worst_abs_spearman"] > RHO_LIMIT:
        write_card({
            "hypothesis": "Poisson pseudogravity residual edge of isostatic gravity against RTP",
            "mechanism": "Baranov |k|^{-1} pseudogravity, local residual horizontal-gradient ridges",
            "non_fault_mimic": "non-magnetic pluton roofs and FFT survey-boundary leakage",
            "verdict": "negative",
            "stop": "scientific duplicate on surface rank-correlation",
            "leakage_canary": canary,
            "holdout_dti": {"evidence_class": "HOLDOUT-DTI", "evaluator_version": "gems57-pooled-hide-v2",
                            "screen": h31n_score, "control": base_score, "paired": paired},
            "preplacement": {k: v for k, v in pre.items() if k != "rows"},
            "worst_preplacement_file": worst_pre,
            "ok_to_download_for_research": False,
            "ok_to_submit": False,
            "slot_approved": False,
            "experiments_run": 3,
        })
        log("DUPLICATE STOP — no TIFF")
        return 3

    dots = emit_dots(surface, valid_final, max_dots=BUDGET, min_distance_px=SEPARATION_PX)
    final_cmp = compare(surface, dots, fp)
    worst_final = max(final_cmp["rows"], key=lambda r: r.get("dot_overlap_3px") or -1)
    log(
        f"final dots {int(dots.sum())} worst |rho| {final_cmp['worst_abs_spearman']:.4f} "
        f"overlap {final_cmp['worst_dot_overlap_3px']:.4f} file {worst_final.get('file')}"
    )
    if final_cmp["scientific_duplicate"]:
        write_card({
            "hypothesis": "Poisson pseudogravity residual edge of isostatic gravity against RTP",
            "mechanism": "Baranov |k|^{-1} pseudogravity, local residual horizontal-gradient ridges",
            "non_fault_mimic": "non-magnetic pluton roofs and FFT survey-boundary leakage",
            "verdict": "negative",
            "stop": "scientific duplicate on final dots",
            "leakage_canary": canary,
            "final_comparison_summary": {k: v for k, v in final_cmp.items() if k != "rows"},
            "ok_to_download_for_research": False,
            "ok_to_submit": False,
            "slot_approved": False,
        })
        log("DUPLICATE STOP — no TIFF")
        return 3

    lattice_overlap = dot_overlap(dots, lattice, fp)
    log(f"lattice overlap {lattice_overlap:.4f}")

    # SGMC proxy
    with rasterio.open(ROOT / "data/external/derived_sgmc_faults_100m_u8.tif") as src:
        sgmc = src.read(1) > 0
    off = sgmc & fp & (d_cat > 3.0)
    pred = np.where(fp, dots.astype(np.float32), 0.0)
    sgmc_score = dti_exact(pred, off, valid=fp, known=cat)
    log(f"SGMC proxy DTI {sgmc_score['dti']:.4f} n {int(off.sum())}")

    array_hash = hashlib.sha256(np.packbits(dots.ravel()).tobytes()).hexdigest()[:8]
    name = f"gemsdoe31-h31n-pseudograv-37654-20261026-{array_hash}"
    note = (
        f"H31-N pseudogravity residual edge 37654d b2 | HOLDOUT-DTI screen {h31n_score['dti']:.4f} "
        f"vs base {base_score['dti']:.4f} | research-only {array_hash}"
    )
    if len(note) > 140:
        note = note[:140]
    zeros = np.where(fp, dots.astype(np.float32), 0.0).astype(np.float32)
    out_dir = ROOT / "docs/downloads"
    zeros_path = out_dir / f"{name}-zeros.tif"
    log(f"writing {zeros_path.name}")
    receipt = write_submission(
        zeros_path, zeros, ROOT / "data/sample_submission.tif", fp,
        note=note, name=name, catalogue=cat,
        metadata={"lane": "H31-N", "evidence_class": "COMPUTED", "slot_approved": False},
    )
    nan_path = out_dir / f"{name}-nan.tif"
    nan_values = np.where(fp, zeros, np.nan).astype(np.float32)
    with rasterio.open(ROOT / "data/sample_submission.tif") as sample:
        profile = sample.profile.copy()
    profile.update(dtype="float32", count=1, nodata=None, compress="deflate")
    with rasterio.open(nan_path, "w", **profile) as dst:
        dst.write(nan_values, 1)

    verdict = "promote" if screen_pass and confirm_pass and lattice_overlap <= OVERLAP_LIMIT else "negative"
    ok_submit = bool(verdict == "promote")
    card = {
        "hypothesis": "Non-magnetic density-step faults are horizontal-gradient ridges of the local Poisson pseudogravity residual",
        "mechanism": "Baranov |k|^{-1} filter of RTP, local regression against isostatic gravity at 1.2 km and 3 km, quiet-magnetic edge weight, Poisson 2.8 px emission outside a 2 px catalogue halo",
        "non_fault_mimic": "non-magnetic pluton roofs; FFT survey-boundary leakage (masked at 15 px)",
        "holdout_dti": {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": "gems57-pooled-hide-v2",
            "screen_seed": SCREEN_SEED,
            "candidate": h31n_score,
            "same_run_control_base19": base_score,
            "paired_difference_vs_base19": paired,
            "quadrant_wins_vs_base19": wins,
            "screen_gate_pass": screen_pass,
            "fold_dti": fold_dti,
            "confirmation": None if confirmation is None else {
                "seed": CONFIRM_SEED,
                "candidate": confirmation["scores"]["h31n"],
                "control": confirmation["scores"]["base19"],
                "paired_difference_vs_base19": confirmation["paired_differences"]["base19"],
                "confirm_gate_pass": confirm_pass,
            },
            "variogram": variogram_report,
            "caveat": "Catalogue-segment holdout is not the private expert test set and is not a leaderboard score.",
        },
        "sgmc_proxy": {
            "evidence_class": "HOLDOUT-PROXY-SGMC",
            "evaluator_version": "gems57-metric-dti_exact",
            "off_catalogue_pixels_gt_300m": int(off.sum()),
            "dti": sgmc_score["dti"],
            "tp": sgmc_score["tp"],
            "fp": sgmc_score["fp"],
            "fn": sgmc_score["fn"],
            "caveat": "SGMC is a state-map fault proxy, not competition truth, and must not promote an arm.",
        },
        "leakage_canary": {"max_symmetric_auc": max_auc, "threshold": 0.90, "features": canary, "pass": max_auc <= 0.90},
        "correlation_overlap_vs_registry": {
            "scope": "This repo docs/downloads plus pinned peer files in data/prior_audit/peers. Not a complete 695-raster scan.",
            "preplacement_prospective_topk": {k: v for k, v in pre.items() if k != "rows"},
            "final_dots": {k: v for k, v in final_cmp.items() if k != "rows"},
            "worst_rows": sorted(
                [r for r in final_cmp["rows"] if "dot_overlap_3px" in r and r["dot_overlap_3px"] is not None],
                key=lambda r: r["dot_overlap_3px"], reverse=True,
            )[:12],
        },
        "lattice": {
            "file": str(lattice_path.relative_to(ROOT)),
            "sha256": sha256_file(lattice_path),
            "footprint_fraction_within_3px": lattice_coverage,
            "final_dot_overlap_3px": lattice_overlap,
            "literal_rule": "overlap > 0.70 is a STOP; no density exemption",
            "literal_stop": lattice_overlap > OVERLAP_LIMIT,
        },
        "raster_sha256": receipt["sha256"],
        "validator": receipt["validator"],
        "submission_name": name,
        "note": note,
        "note_chars": len(note),
        "artifacts": {
            "zeros_tif": str(zeros_path.relative_to(ROOT)),
            "zeros_zip": str(zeros_path.with_suffix(".zip").relative_to(ROOT)),
            "zeros_sha256": receipt["sha256"],
            "nan_tif": str(nan_path.relative_to(ROOT)),
            "nan_sha256": sha256_file(nan_path),
            "dots": int(dots.sum()),
            "dots_on_catalogue": int((dots & cat).sum()),
        },
        "verdict": verdict,
        "ok_to_download_for_research": True,
        "ok_to_submit": ok_submit,
        "slot_approved": False,
        "experiments_run": 3 if screen_pass else 2,
        "organizer_confirmed_score": None,
    }
    # Save the heavy comparison rows beside the card, not inside the homepage payload only.
    (ROOT / "evidence/h31n").mkdir(parents=True, exist_ok=True)
    (ROOT / "evidence/h31n/uniqueness_rows.json").write_text(json.dumps({
        "preplacement": pre["rows"], "final": final_cmp["rows"],
    }, indent=1) + "\n")
    write_card(card)
    (out_dir / f"{name}-run-card.json").write_text(json.dumps(card, indent=1, allow_nan=False) + "\n")
    log(f"DONE verdict={verdict} ok_to_submit={ok_submit} sha={receipt['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
