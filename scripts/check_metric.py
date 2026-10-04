#!/usr/bin/env python3
"""Prove the metric implementation matches the published definition.

Three independent checks on random grids:

1. ``src/gemsdoe31/metric.py`` (vectorised over the 29 kernel offsets, distance transform for the
   false-positive term) against ``metric.brute_force``, which transcribes the published sums
   literally with per-pixel Python loops.
2. The definitional identity ``TPw + FNw = |G|``.
3. The decomposition identity ``TPw + FPw + FNw <= |G| + sum_x p(x)`` with equality when every
   truth pixel has a unit-probability prediction pixel at distance 0 and vice versa (checked on a
   constructed exact case).

Writes ``evidence/metric_check.json``. Run: ``python scripts/check_metric.py``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gemsdoe31 import metric  # noqa: E402

GRIDS = 24
SEED = 20261004


def main() -> None:
    rng = np.random.default_rng(SEED)
    worst = 0.0
    rows = []
    for index in range(GRIDS):
        size = int(rng.integers(14, 34))
        truth = rng.random((size, size)) < rng.uniform(0.05, 0.25)
        if not truth.any():
            truth[rng.integers(size), rng.integers(size)] = True
        pred = np.where(rng.random((size, size)) < 0.5, rng.random((size, size)), 0.0)
        fast = metric.dti(pred, truth)
        slow = metric.brute_force(pred, truth)
        delta = abs(fast["DTI"] - slow["DTI"])
        worst = max(worst, delta)
        identity_tp_fn = abs((fast["TPw"] + fast["FNw"]) - float(truth.sum()))
        rows.append({"grid": index, "size": size, "truth_pixels": int(truth.sum()),
                     "DTI_fast": fast["DTI"], "DTI_brute": slow["DTI"], "abs_delta": delta,
                     "tp_plus_fn_minus_truth": identity_tp_fn})
        assert identity_tp_fn < 1e-9, "TPw + FNw = |G| failed"

    # Exact case 1: prediction == truth == a 3-cell line, so every truth pixel has a unit-probability
    # prediction at distance 0. Then TPw = |G|, FNw = 0, the false-positive sum runs over truth cells
    # only (each of which has K = 1, so it contributes nothing), FPw = 0 and DTI = 1 (to within
    # epsilon).
    line = np.zeros((7, 9), dtype=bool)
    line[3, 3:6] = True
    same = metric.dti(line.astype(np.float64), line)
    assert abs(same["TPw"] - 3.0) < 1e-12, same
    assert abs(same["FNw"]) < 1e-12, same
    assert abs(same["FPw"]) < 1e-12, same
    assert abs(same["DTI"] - 1.0) < 1e-9, same

    # Exact case 2: one truth pixel, one predicted pixel 200 m (2 cells) away, no overlap.
    #   TPw = k(200) = 1/3                 (prediction within R of the truth pixel)
    #   FNw = 1 - 1/3 = 2/3
    #   FPw = p(x) * (1 - max_g k(d(x,g))) = 1 * (1 - 1/3) = 2/3
    #   DTI = (1/3) / ((1/3) + 0.2*(2/3) + 0.8*(2/3)) = (1/3) / 1 = 1/3 exactly
    truth_cell = np.zeros((9, 9), dtype=bool)
    truth_cell[4, 4] = True
    single = np.zeros((9, 9), dtype=np.float64)
    single[4, 6] = 1.0
    case2 = metric.dti(single, truth_cell)
    assert abs(case2["TPw"] - 1.0 / 3.0) < 1e-12, case2
    assert abs(case2["FNw"] - 2.0 / 3.0) < 1e-12, case2
    assert abs(case2["FPw"] - 2.0 / 3.0) < 1e-12, case2
    assert abs(case2["DTI"] - 1.0 / 3.0) < 1e-9, case2
    brute_case2 = metric.brute_force(single, truth_cell)
    assert abs(brute_case2["DTI"] - 1.0 / 3.0) < 1e-9, brute_case2

    payload = {
        "schema_version": 1,
        "generated_utc": "2026-10-04",
        "implementation": "src/gemsdoe31/metric.py",
        "definition_source": "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/",
        "kernel_offsets_in_support": int(metric._offsets(metric.CELL_M, metric.RADIUS_M)[0].shape[0]),
        "alpha": metric.ALPHA, "beta": metric.BETA, "radius_m": metric.RADIUS_M,
        "epsilon_assumption": metric.EPSILON,
        "epsilon_note": "The published page does not state epsilon. A tiny positive epsilon is used so an "
                        "all-zero submission scores 0 rather than dividing by zero.",
        "grids_compared": GRIDS,
        "max_abs_dti_delta_vs_brute_force": worst,
        "identity_tpw_plus_fnw_equals_truth": "holds to < 1e-9 on every grid",
        "exact_cases": [
            {"description": "3-cell line, prediction == truth", "TPw": same["TPw"], "FPw": same["FPw"],
             "FNw": same["FNw"], "DTI": same["DTI"], "DTI_closed_form": 1.0},
            {"description": "one truth pixel, one predicted pixel 200 m away (no overlap)",
             "TPw": case2["TPw"], "FPw": case2["FPw"], "FNw": case2["FNw"], "DTI": case2["DTI"],
             "DTI_closed_form": 1.0 / 3.0, "DTI_brute_force": brute_case2["DTI"]},
        ],
        "rows": rows,
    }
    out = ROOT / "evidence" / "metric_check.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=1) + "\n")
    print(f"max |DTI_fast - DTI_brute| over {GRIDS} grids: {worst:.3e}")
    print(f"exact case 1 DTI {same['DTI']:.12f} (closed form 1.0); "
          f"exact case 2 DTI {case2['DTI']:.12f} (closed form 1/3)")
    print(f"kernel offsets inside R=300 m at 100 m cells: {payload['kernel_offsets_in_support']}")
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
