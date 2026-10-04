#!/usr/bin/env python3
"""Recompute descriptive variogram diagnostics from a saved H31 pilot residual NPZ (no model refit)."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gemsdoe31.variogram import (  # noqa: E402
    VariogramFitError,
    bootstrap_range_interval,
    empirical_semivariogram,
    fit_exponential,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _fit_arm(arrays: dict[str, np.ndarray], residual_key: str, settings: dict[str, Any]) -> dict[str, Any]:
    empirical = empirical_semivariogram(
        arrays["rows"],
        arrays["cols"],
        arrays["components"],
        arrays[residual_key],
        arrays["folds"],
        arrays["draws"],
        cell_size_m=settings["cell_size_m"],
        bin_width_m=settings["bin_width_m"],
        max_lag_m=settings["max_lag_m"],
        min_pairs_per_bin=settings["min_pairs_per_bin"],
        min_points_per_group=4,
    )
    result: dict[str, Any] = {"empirical": empirical.as_dict()}
    try:
        point = fit_exponential(
            empirical,
            max_lag_m=settings["max_lag_m"],
            min_populated_bins=8,
            min_fit_lag_m=2_000.0,
        )
        result["point_fit_diagnostic"] = point.as_dict()
    except (ValueError, VariogramFitError) as exc:
        result["point_fit_error"] = f"{type(exc).__name__}: {exc}"

    try:
        result["component_bootstrap"] = bootstrap_range_interval(
            empirical,
            max_lag_m=settings["max_lag_m"],
            min_populated_bins=8,
            min_fit_lag_m=2_000.0,
            n_bootstrap=settings["bootstrap_replicates"],
            seed=settings["bootstrap_seed"],
            minimum_stable_fraction=0.80,
        )
        result["operational_range_95_sill_ci_m"] = result["component_bootstrap"]["bootstrap"]["range_95_sill_ci_m"]
        result["stable"] = bool(result["component_bootstrap"]["stable"])
    except (ValueError, VariogramFitError) as exc:
        result["component_bootstrap_error"] = f"{type(exc).__name__}: {exc}"
        result["operational_range_95_sill_ci_m"] = None
        result["stable"] = False
    if not result["stable"]:
        result["operational_range_m"] = None
    else:
        result["operational_range_m"] = float(result["operational_range_95_sill_ci_m"][1])
    return result


def _software_record() -> dict[str, str]:
    versions = {name: importlib.metadata.version(name) for name in ("numpy", "scipy")}
    versions["python"] = sys.version.split()[0]
    return versions


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pilot_dir", type=Path, help="completed pilot directory with design/results and residual NPZ")
    parser.add_argument("--out", type=Path, default=None, help="diagnostic JSON path (default: pilot_dir/posthoc_variogram_diagnostics.json)")
    parser.add_argument("--overwrite", action="store_true", help="replace an existing diagnostic JSON file")
    args = parser.parse_args()
    pilot_dir = args.pilot_dir.resolve()
    design_path = pilot_dir / "design.json"
    results_path = pilot_dir / "results.json"
    residual_path = pilot_dir / "oof_residuals.npz"
    variogram_path = pilot_dir / "variogram.json"
    for path in (design_path, results_path, residual_path, variogram_path):
        if not path.is_file():
            raise SystemExit(f"required pilot artifact is missing: {path}")
    design = json.loads(design_path.read_text())
    results = json.loads(results_path.read_text())
    original_variogram = json.loads(variogram_path.read_text())
    if design.get("stage") != "pilot" or results.get("stage") != "pilot":
        raise SystemExit("only an H31-A pilot directory can be analyzed")
    settings = design["residual_variogram"]
    arrays = dict(np.load(residual_path, allow_pickle=False))
    arms = {
        "base": _fit_arm(arrays, "base_residual", settings),
        "h31_candidate": _fit_arm(arrays, "h31_candidate_residual", settings),
    }
    all_stable = all(item.get("stable") is True for item in arms.values())
    record = {
        "kind": "POSTHOC_DESCRIPTIVE_DIAGNOSTIC_ONLY",
        "generated_utc_date": datetime.now(timezone.utc).date().isoformat(),
        "purpose": "Retain empirical-bin and unstable point-fit diagnostics from the already saved OOF residuals; no classifier retraining, candidate tuning, new holdout draw, or submission generation.",
        "decision_rule": "The operational range is unknown unless both the point fit and component bootstrap are stable under the frozen preregistered diagnostics. An unstable point range is not used to set a buffer.",
        "source_artifacts": {
            "design_sha256": sha256_file(design_path),
            "results_sha256": sha256_file(results_path),
            "original_variogram_sha256": sha256_file(variogram_path),
            "oof_residuals_sha256": sha256_file(residual_path),
            "preregistration_sha256": results["preregistration_sha256"],
            "original_model_code_revision": results["code_revision"],
            "original_execution_bundle_sha256": results["execution_bundle_sha256"],
            "posthoc_variogram_module_sha256": sha256_file(ROOT / "src" / "gemsdoe31" / "variogram.py"),
            "diagnostic_script_sha256": sha256_file(Path(__file__).resolve()),
        },
        "settings": {
            **settings,
            "minimum_points_per_trace_group": 4,
            "minimum_trace_groups_with_pairs": 30,
            "minimum_populated_bins": 8,
            "minimum_populated_lag_support_m": 2_000.0,
            "minimum_stable_bootstrap_fraction": 0.80,
        },
        "residual_rows": int(arrays["rows"].size),
        "software": _software_record(),
        "original_runner_fit_status": original_variogram["fits"],
        "arms": arms,
        "all_arms_stable": bool(all_stable),
        "recommended_buffer_m": None,
        "conclusion": "No stable empirical range or usable confidence interval was identified. The preregistered final buffer is unknown; do not screen or promote H31-A.",
    }
    out = args.out.resolve() if args.out else pilot_dir / "posthoc_variogram_diagnostics.json"
    if out.exists() and not args.overwrite:
        raise SystemExit(f"refusing to overwrite existing diagnostics without --overwrite: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({"output": str(out), "sha256": sha256_file(out), "arms_stable": {k: v["stable"] for k, v in arms.items()}}, indent=2))


if __name__ == "__main__":
    main()
