#!/usr/bin/env python3
"""Run the preregistered H31-A magnetic-scale pilot, screen, or fresh confirmation.

The script is intentionally fail-closed. It requires a clean GEMSDOE31 worktree, the exact pinned GEMSDOE25
reference commit, SHA-256-verified owner-mirror inputs/caches, and a new empty output directory. It never
contacts DrivenData or creates a submission TIFF.
"""

from __future__ import annotations

import os

import argparse
import gc
import hashlib
import importlib.metadata
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gemsdoe31.analysis import select_screen_buffer, summarize_stage  # noqa: E402
from gemsdoe31.h31_features import FEATURE_NAMES  # noqa: E402
from gemsdoe31.runtime import build_context  # noqa: E402
from gemsdoe31.variogram import (  # noqa: E402
    VariogramFitError,
    bootstrap_range_interval,
    empirical_semivariogram,
    recommend_buffer_m,
)

PREREG_PATH = ROOT / "knowledge" / "2026-10-04_h31_hypotheses_preregistration.md"
# The session branch guard is fail-closed but not hard-coded to one session id: a stale literal would
# silently stop being a guard the moment the work moved to another arena branch. Override it with
# GEMSDOE31_BRANCH when a later session runs this runner.
EXPECTED_BRANCH = os.environ.get("GEMSDOE31_BRANCH", "arena/01a104f4-gemsdoe31")
PILOT_DRAWS = [10]
SCREEN_DRAWS = [11, 12]
CONFIRM_DRAWS = [13, 14]
PILOT_BUFFER_M = 500
CELL_SIZE_M = 100.0
BIN_WIDTH_M = 500.0
MAX_LAG_M = 50_000.0
MIN_PAIRS_PER_BIN = 20
BOOTSTRAPS = 200
BOOTSTRAP_SEED = 20261004
TOP_K_FRACTION = 0.035
DOT_DISTANCE_PX = 2.4


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def execution_bundle_sha256() -> str:
    """Hash the executable project code and dependency specification, excluding mutable reports/site copy."""
    paths = [ROOT / "scripts" / "run_h31.py", ROOT / "pyproject.toml", ROOT / "requirements.txt"]
    paths.extend(sorted((ROOT / "src" / "gemsdoe31").rglob("*.py")))
    digest = hashlib.sha256()
    for path in sorted(set(paths)):
        digest.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def git_output(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def require_clean_worktree() -> str:
    status = git_output("status", "--porcelain")
    if status:
        raise SystemExit("refusing to fit with a dirty GEMSDOE31 worktree; commit/freeze code and preregistration first")
    branch = git_output("branch", "--show-current")
    if branch != EXPECTED_BRANCH:
        raise SystemExit(f"wrong working branch {branch!r}; set GEMSDOE31_BRANCH to override {EXPECTED_BRANCH!r}")
    return git_output("rev-parse", "HEAD")


def _load_json(path: Path) -> dict[str, Any]:
    try:
        result = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"cannot read valid JSON from {path}: {exc}") from exc
    if not isinstance(result, dict):
        raise SystemExit(f"expected a JSON object in {path}")
    return result


def _choose_stage(
    args: argparse.Namespace, execution_sha256: str, environment_sha256: str
) -> tuple[list[int], int, int | None, Path | None, Path | None]:
    prereg_sha = sha256_file(PREREG_PATH)
    if args.stage == "pilot":
        if args.buffer_m is not None and args.buffer_m != PILOT_BUFFER_M:
            raise SystemExit(f"pilot buffer is frozen at {PILOT_BUFFER_M} m; it is not the final holdout buffer")
        if args.pilot_dir or args.screen_results or args.previous_screen_results or args.buffer_iteration != 1:
            raise SystemExit("pilot stage does not take prior-run paths or a screen buffer iteration")
        return PILOT_DRAWS, PILOT_BUFFER_M, None, None, None

    if args.stage == "screen":
        if not args.pilot_dir:
            raise SystemExit("screen stage requires --pilot-dir from the completed H31 pilot")
        if args.screen_results:
            raise SystemExit("screen stage does not take --screen-results")
        pilot = _load_json(Path(args.pilot_dir) / "results.json")
        if pilot.get("stage") != "pilot" or pilot.get("preregistration_sha256") != prereg_sha:
            raise SystemExit("pilot result is not from this frozen preregistration")
        if pilot.get("execution_bundle_sha256") != execution_sha256:
            raise SystemExit("pilot was produced by a different executable code/dependency bundle")
        if pilot.get("environment_sha256") != environment_sha256:
            raise SystemExit("pilot was produced by a different Python/package environment")
        if not pilot.get("variograms_stable") or pilot.get("variogram_recommended_buffer_m") is None:
            raise SystemExit("pilot variogram is not stable; the data-derived buffer is unknown and H31 stops")
        minimum = int(pilot["variogram_recommended_buffer_m"])
        previous_path = args.previous_screen_results
        previous = None
        if args.buffer_iteration == 1:
            if previous_path is not None:
                raise SystemExit("buffer iteration 1 must not include --previous-screen-results")
        else:
            if previous_path is None:
                raise SystemExit(f"buffer iteration {args.buffer_iteration} requires --previous-screen-results")
            previous = _load_json(Path(previous_path))
            if previous.get("preregistration_sha256") != prereg_sha:
                raise SystemExit("previous screen result is not from this frozen preregistration")
            if previous.get("execution_bundle_sha256") != execution_sha256:
                raise SystemExit("previous screen used a different executable code/dependency bundle")
            if previous.get("environment_sha256") != environment_sha256:
                raise SystemExit("previous screen used a different Python/package environment")
        try:
            buffer_m = select_screen_buffer(
                minimum,
                iteration=args.buffer_iteration,
                requested_buffer_m=args.buffer_m,
                previous_screen=previous,
                cell_size_m=int(CELL_SIZE_M),
            )
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        return SCREEN_DRAWS, buffer_m, minimum, None, previous_path

    if args.stage == "confirm":
        if not args.screen_results:
            raise SystemExit("confirmation requires --screen-results from the stable, passing final screen")
        if args.pilot_dir or args.previous_screen_results or args.buffer_iteration != 1:
            raise SystemExit("confirmation does not take pilot/previous-screen paths or a buffer iteration")
        screen_path = Path(args.screen_results)
        screen = _load_json(screen_path)
        if screen.get("stage") != "screen" or screen.get("preregistration_sha256") != prereg_sha:
            raise SystemExit("confirmation screen result is not from this frozen preregistration")
        if screen.get("execution_bundle_sha256") != execution_sha256:
            raise SystemExit("confirmation screen used a different executable code/dependency bundle")
        if screen.get("environment_sha256") != environment_sha256:
            raise SystemExit("confirmation screen used a different Python/package environment")
        if screen.get("buffer_iteration") not in (1, 2, 3):
            raise SystemExit("confirmation screen result has no valid buffer iteration")
        if not screen.get("screen_gate_passed") or not screen.get("buffer_stable"):
            raise SystemExit("confirmation prohibited: final-buffer screen did not pass all gates")
        minimum = int(screen.get("buffer_m", -1))
        buffer_m = minimum if args.buffer_m is None else int(args.buffer_m)
        if buffer_m != minimum:
            raise SystemExit("confirmation must use the final screen's exact frozen buffer")
        return CONFIRM_DRAWS, buffer_m, minimum, screen_path, None
    raise SystemExit(f"unknown stage: {args.stage}")


def _residual_rows(cell, context, probability: np.ndarray) -> tuple[np.ndarray, ...]:
    global_flat = context.fi[cell.q]
    heldout = cell.draw.hidden_test.ravel()[global_flat]
    score_domain = cell.domain.ravel()[global_flat]
    select = heldout & score_domain
    if not select.any():
        empty_i = np.empty(0, np.int32)
        empty_f = np.empty(0, np.float32)
        return empty_i, empty_i, empty_i, empty_f
    flat = global_flat[select]
    rows, cols = np.divmod(flat, context.foot.shape[1])
    components = context.holdout.comp.ravel()[flat]
    good = components > 0
    residual = 1.0 - np.asarray(probability[select], dtype=np.float32)
    return rows[good].astype(np.int32), cols[good].astype(np.int32), components[good].astype(np.int32), residual[good]


def _fit_variogram_arm(arrays: dict[str, np.ndarray], arm: str) -> dict[str, Any]:
    residual_key = "base_residual" if arm == "base" else "h31_candidate_residual"
    empirical = None
    try:
        empirical = empirical_semivariogram(
            arrays["rows"],
            arrays["cols"],
            arrays["components"],
            arrays[residual_key],
            arrays["folds"],
            arrays["draws"],
            cell_size_m=CELL_SIZE_M,
            bin_width_m=BIN_WIDTH_M,
            max_lag_m=MAX_LAG_M,
            min_pairs_per_bin=MIN_PAIRS_PER_BIN,
            min_points_per_group=4,
        )
        fitted = bootstrap_range_interval(
            empirical,
            max_lag_m=MAX_LAG_M,
            min_populated_bins=8,
            min_fit_lag_m=2_000.0,
            n_bootstrap=BOOTSTRAPS,
            seed=BOOTSTRAP_SEED,
            minimum_stable_fraction=0.80,
        )
        fitted["empirical"] = empirical.as_dict()
        return fitted
    except (ValueError, VariogramFitError) as exc:
        result = {"stable": False, "error": f"{type(exc).__name__}: {exc}"}
        if empirical is not None:
            result["empirical"] = empirical.as_dict()
        return result


def _environment() -> dict[str, str]:
    versions = {}
    for package in ("numpy", "scipy", "rasterio", "scikit-learn"):
        versions[package] = importlib.metadata.version(package)
    versions["python"] = sys.version.split()[0]
    return versions


def _environment_sha256(environment: dict[str, str]) -> str:
    payload = json.dumps(environment, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("pilot", "screen", "confirm"), required=True)
    parser.add_argument("--sibling-root", type=Path, required=True, help="clean GEMSDOE25 checkout at the frozen commit")
    parser.add_argument("--data-dir", type=Path, required=True, help="owner-mirror raw inputs restored from the pinned sibling")
    parser.add_argument("--work-dir", type=Path, required=True, help="prepared work/cache directory from the pinned sibling")
    parser.add_argument("--out", type=Path, required=True, help="new empty output directory, preferably under evidence/")
    parser.add_argument("--pilot-dir", type=Path, default=None, help="completed pilot output (screen only)")
    parser.add_argument("--screen-results", type=Path, default=None, help="passing final-screen results.json (confirm only)")
    parser.add_argument("--buffer-iteration", type=int, choices=(1, 2, 3), default=1, help="screen-only, preregistered retry count")
    parser.add_argument(
        "--previous-screen-results", type=Path, default=None,
        help="immediately prior, metric-passing unstable screen result (iteration 2 or 3 only)",
    )
    parser.add_argument(
        "--buffer-m", type=int, default=None,
        help="screen buffer; must equal the pilot or previous-screen data-derived recommendation",
    )
    args = parser.parse_args()
    for name in ("sibling_root", "data_dir", "work_dir", "out", "pilot_dir", "screen_results", "previous_screen_results"):
        value = getattr(args, name)
        if value is not None and not value.is_absolute():
            setattr(args, name, ROOT / value)

    code_revision = require_clean_worktree()
    executable_bundle_sha256 = execution_bundle_sha256()
    environment = _environment()
    environment_sha256 = _environment_sha256(environment)
    draws, buffer_m, minimum_buffer_m, screen_results_path, previous_screen_path = _choose_stage(
        args, executable_bundle_sha256, environment_sha256
    )
    buffer_px = int(buffer_m / CELL_SIZE_M)
    if buffer_px < 1 or buffer_px * CELL_SIZE_M != buffer_m:
        raise SystemExit("validation buffer must be an integer multiple of the 100 m grid")
    out = args.out if args.out.is_absolute() else ROOT / args.out
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise SystemExit(f"refusing to overwrite nonempty H31 run directory: {out}")
    out.mkdir(parents=True, exist_ok=True)

    context, holdout_module, experiment_module, provenance = build_context(
        args.sibling_root, args.data_dir, args.work_dir, buffer_px=buffer_px
    )
    if int(holdout_module.COLLAR_PX) != buffer_px:
        raise SystemExit("reference holdout did not retain the requested collar")
    from gems25.h30 import H30_BASE_EXTRAS

    base_cols = context.columns("BDE") + context.named(H30_BASE_EXTRAS)
    candidate_cols = base_cols + context.named(list(FEATURE_NAMES))
    if not base_cols or len(candidate_cols) != len(base_cols) + len(FEATURE_NAMES):
        raise SystemExit("reference feature-column construction failed")

    design = {
        "hypothesis_id": "H31-A",
        "stage": args.stage,
        "code_revision": code_revision,
        "execution_bundle_sha256": executable_bundle_sha256,
        "branch": EXPECTED_BRANCH,
        "preregistration": PREREG_PATH.relative_to(ROOT).as_posix(),
        "preregistration_sha256": sha256_file(PREREG_PATH),
        "sibling_provenance": provenance,
        "environment": environment,
        "environment_sha256": environment_sha256,
        "folds": ["NW", "NE", "SW", "SE"],
        "draws": draws,
        "holdout": {
            "type": "four contiguous quadrant catalogue-gap hide-and-recover",
            "hide_fraction": 0.20,
            "component_connectivity": 8,
            "buffer_m": buffer_m,
            "buffer_px": buffer_px,
            "minimum_pilot_buffer_m": minimum_buffer_m,
            "buffer_iteration": args.buffer_iteration if args.stage == "screen" else None,
            "previous_screen_results": (
                {"path": str(previous_screen_path), "sha256": sha256_file(previous_screen_path)}
                if previous_screen_path is not None
                else None
            ),
            "scoring_domain_erosion_px": int(experiment_module.DOMAIN_ERODE),
            "seed_formulas": "pinned GEMSDOE25 Holdout.draw and Cell negative sampler",
        },
        "feature_arms": {
            "base": "BDE plus fixed X1-X3 add-ons (same-run H19-5 parent comparator)",
            "h31_candidate": "base plus H31_mag_local_length and H31_mag_scale_edge",
            "base_column_indices": base_cols,
            "candidate_column_indices": candidate_cols,
        },
        "model": {
            "class": "sklearn.ensemble.HistGradientBoostingClassifier",
            "parameters": {str(k): v for k, v in experiment_module.HGB_PARAMS.items()},
            "negative_sample_count_max": int(experiment_module.N_NEG),
            "model_seed": "draw id; same fold/draw training sample for both arms",
        },
        "emission": {
            "ridge_nms_sigma_px": 1.0,
            "top_k_fraction_of_eroded_scoring_domain": TOP_K_FRACTION,
            "poisson_dot_spacing_px": DOT_DISTANCE_PX,
            "visible_fault_pixels_removed": True,
            "binary_dti_prediction": True,
        },
        "residual_variogram": {
            "residual": "e = y - p on held-out hidden catalogue fault pixels only",
            "pairs": "same fold, draw, and 8-connected fault component",
            "estimator": "Matheron 0.5 * (e_i - e_j)^2",
            "cell_size_m": CELL_SIZE_M,
            "bin_width_m": BIN_WIDTH_M,
            "max_lag_m": MAX_LAG_M,
            "min_pairs_per_bin": MIN_PAIRS_PER_BIN,
            "bootstrap_replicates": BOOTSTRAPS,
            "bootstrap_seed": BOOTSTRAP_SEED,
        },
        "feature_diagnostics": context.h31_feature_diagnostics,
        "notes": [
            "Catalogue-gap proxy only; not hidden competition truth or leaderboard evidence.",
            "Pilot collar is temporary and is never described as the empirical range.",
            "No submission raster is created by this experiment runner.",
        ],
    }
    _write_json(out / "design.json", design)  # Frozen before this stage's first model fit.

    from gems25.experiment import Cell
    from gems25.thinning import score_ordered_dots

    rows: list[dict[str, Any]] = []
    residual_parts: dict[str, list[np.ndarray]] = {
        key: [] for key in ("rows", "cols", "components", "folds", "draws", "base_residual", "h31_candidate_residual")
    }
    stage_start = time.time()
    cells_path = out / "cells.jsonl"
    with cells_path.open("w") as sink:
        for fold in range(4):
            for draw in draws:
                cell_start = time.time()
                cell = Cell(context, fold, draw, extras=True)
                k = int(round(TOP_K_FRACTION * cell.dom_c.sum()))
                arm_probabilities: dict[str, np.ndarray] = {}
                for arm, columns in (("base", base_cols), ("h31_candidate", candidate_cols)):
                    probability, timing = cell.fit_predict(columns, seed=draw)
                    score_crop, candidates = cell.candidates(probability, k=k)
                    emitted = score_ordered_dots(score_crop, candidates, DOT_DISTANCE_PX)
                    metric = cell.evaluate(emitted)
                    auc = cell.auc(probability)
                    auc_value = float(auc) if np.isfinite(auc) else None
                    row = {
                        "stage": args.stage,
                        "fold": fold,
                        "fold_name": ("NW", "NE", "SW", "SE")[fold],
                        "draw": draw,
                        "arm": arm,
                        "buffer_m": buffer_m,
                        "k": k,
                        "top_k_fraction": TOP_K_FRACTION,
                        "dot_spacing_px": DOT_DISTANCE_PX,
                        "auc": auc_value,
                        **metric,
                        **timing,
                        "cell_preparation_s": cell.prep_seconds,
                        "elapsed_s": time.time() - cell_start,
                    }
                    row = {key: (value.item() if isinstance(value, np.generic) else value) for key, value in row.items()}
                    sink.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
                    sink.flush()
                    rows.append(row)
                    arm_probabilities[arm] = probability
                    print(
                        f"[{args.stage} fold {fold} draw {draw} {arm}] DTI={float(metric['dti']):.6f} "
                        f"emit={int(metric['emitted'])} fit={float(timing['fit_s']):.1f}s",
                        flush=True,
                    )
                    del score_crop, candidates, emitted

                # Both arms use the same test rows/labels; retain y-p residuals for the registered variogram.
                rows_i, cols_i, comp_i, residual_base = _residual_rows(cell, context, arm_probabilities["base"])
                rows_c, cols_c, comp_c, residual_candidate = _residual_rows(cell, context, arm_probabilities["h31_candidate"])
                if not (np.array_equal(rows_i, rows_c) and np.array_equal(cols_i, cols_c) and np.array_equal(comp_i, comp_c)):
                    raise RuntimeError("base/candidate residual rows differ despite a shared holdout draw")
                n = rows_i.size
                if n:
                    residual_parts["rows"].append(rows_i)
                    residual_parts["cols"].append(cols_i)
                    residual_parts["components"].append(comp_i)
                    residual_parts["folds"].append(np.full(n, fold, dtype=np.int16))
                    residual_parts["draws"].append(np.full(n, draw, dtype=np.int16))
                    residual_parts["base_residual"].append(residual_base.astype(np.float32))
                    residual_parts["h31_candidate_residual"].append(residual_candidate.astype(np.float32))
                del arm_probabilities, cell
                gc.collect()

    residuals = {
        key: (np.concatenate(parts) if parts else np.empty(0, dtype=np.float32 if "residual" in key else np.int32))
        for key, parts in residual_parts.items()
    }
    np.savez_compressed(out / "oof_residuals.npz", **residuals)
    variogram_fits: dict[str, dict[str, Any]] = {
        arm: _fit_variogram_arm(residuals, arm) for arm in ("base", "h31_candidate")
    }
    recommendation = None
    if all(item.get("stable") for item in variogram_fits.values()):
        try:
            recommendation = recommend_buffer_m(variogram_fits)
        except (ValueError, VariogramFitError):
            recommendation = None
    variogram_record = {
        "stage": args.stage,
        "buffer_m_applied": buffer_m,
        "cell_size_m": CELL_SIZE_M,
        "bin_width_m": BIN_WIDTH_M,
        "max_lag_m": MAX_LAG_M,
        "fits": variogram_fits,
        "recommended_buffer_m": recommendation,
        "residual_rows": int(residuals["rows"].size),
    }
    _write_json(out / "variogram.json", variogram_record)

    results = summarize_stage(
        rows,
        variogram_fits,
        stage=args.stage,
        draws=draws,
        buffer_m=buffer_m,
        minimum_buffer_m=minimum_buffer_m,
        screen_results_path=screen_results_path,
    )
    results["code_revision"] = code_revision
    results["execution_bundle_sha256"] = executable_bundle_sha256
    results["environment_sha256"] = environment_sha256
    results["preregistration_sha256"] = design["preregistration_sha256"]
    results["pilot_dir"] = str(args.pilot_dir) if args.pilot_dir else None
    results["screen_results_path"] = str(screen_results_path) if screen_results_path else None
    results["buffer_iteration"] = args.buffer_iteration if args.stage == "screen" else None
    results["previous_screen_results"] = (
        {"path": str(previous_screen_path), "sha256": sha256_file(previous_screen_path)}
        if previous_screen_path is not None
        else None
    )
    results["runtime_s"] = time.time() - stage_start
    results["residual_file"] = {
        "path": "oof_residuals.npz",
        "sha256": sha256_file(out / "oof_residuals.npz"),
        "bytes": (out / "oof_residuals.npz").stat().st_size,
    }
    _write_json(out / "results.json", results)
    print(json.dumps(results, indent=2, sort_keys=True, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
