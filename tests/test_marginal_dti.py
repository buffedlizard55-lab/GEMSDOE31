"""Keep public mathematical explanations aligned with shared metric arithmetic."""
import importlib.util
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('check_marginal_dti', ROOT / 'scripts/check_marginal_dti.py')
audit_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_module)


def test_random_finite_changes_match_shared_metric():
    result = audit_module.audit()
    assert result['all_signs_agree']
    assert result['illustration']['gain_to_fp_ratio'] == pytest.approx(0.05882851213417476)
    assert result['illustration']['isolated_one_truth_credit'] == pytest.approx(0.05556)


@pytest.mark.parametrize('dt,df,expected', [(0, 0, 0), (1, 0, 1), (0, 1, -1), (0, -1, 1)])
def test_zero_gain_cost_and_noop(dt, df, expected):
    score = audit_module.from_terms
    before = score([10, 20, 90, 100])
    after = score([10 + dt, 20 + df, 90 - dt, 100])
    assert np.sign(after - before) == expected


def test_public_prose_does_not_restore_wrong_denominator_or_confirmation():
    readme = (ROOT / 'README.md').read_text().split('## Complete owner prompt')[0]
    renderer = (ROOT / 'scripts/current_site.py').read_text()
    assert '(1 - D*)' not in readme
    assert '(1 − D*)' not in renderer
    assert 'best confirmed unique score' not in readme
    assert 'private truth' in renderer
