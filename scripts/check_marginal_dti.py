#!/usr/bin/env python3
"""Audit explanatory marginal algebra against the unchanged shared evaluator.

This is a mathematical regression check, not a geological experiment or holdout.
No raster is created and no score is projected from the illustrative claim.
"""
from pathlib import Path
import json
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'vendor'))
from gems57.evaluate_holdout import from_terms, implementation_hashes  # noqa: E402
from gems57.metric import ALPHA, BETA  # noqa: E402


def audit(seed=1028355, cases=10000):
    rng = np.random.default_rng(seed)
    truth = rng.integers(1, 10000, cases)
    tp = rng.uniform(size=cases) * truth
    fp = rng.uniform(0, 20000, cases)
    # Both additions and removals; all resulting components remain feasible.
    dt = rng.uniform(size=cases) * truth - tp
    df = rng.uniform(0, 20000, cases) - fp
    before = from_terms(np.stack([tp, fp, truth - tp, truth], axis=1))
    after = from_terms(np.stack([tp + dt, fp + df, truth - tp - dt, truth], axis=1))
    margin = (1 - (1 - BETA) * before) * dt - ALPHA * before * df
    np.testing.assert_array_equal(after > before, margin > 0)
    # Algebra illustration ONLY: not a forecast or organizer-confirmed result.
    claim = 0.2778
    ratio = ALPHA * claim / (1 - (1 - BETA) * claim)
    return dict(
        evidence_class='COMPUTED-MATHEMATICAL-CHECK',
        geological_experiments=0, seed=seed, cases=cases, all_signs_agree=True,
        fixed_truth_formula='S = T / ((1-beta)*T + alpha*F + beta*N + epsilon)',
        exact_improvement_condition='(1-(1-beta)*S)*delta_T > alpha*S*delta_F',
        positive_delta_F_ratio='delta_T/delta_F > alpha*S/(1-(1-beta)*S)',
        illustration=dict(input=claim, input_class='USER-REPORTED; unverified',
                          gain_to_fp_ratio=ratio, isolated_one_truth_credit=ALPHA*claim,
                          caveat='The isolated-credit simplification requires delta_T=k and delta_F=1-k; not general hit probability.'),
        shared_implementation_sha256=implementation_hashes(),
        limits='Fixed truth/mask only. Private TP/FP changes are unknown. No causal leaderboard claim.')


if __name__ == '__main__':
    result = audit()
    (ROOT / 'evidence/marginal_dti_audit_20261026.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
