import numpy as np
import pytest

from gemsdoe31 import metric


def test_empty_truth_has_no_phantom_edt_boundary_credit():
    p = np.full((9, 10), .25)
    truth = np.zeros_like(p, bool)
    np.testing.assert_array_equal(metric.fp_weights(p, truth), p)
    assert metric.dti(p, truth)["FPw"] == p.sum()
    assert metric.dti(p, truth)["FPw"] == metric.brute_force(p, truth)["FPw"]
    assert metric.per_truth_credit(p, truth).size == 0


@pytest.mark.parametrize("name", ["dti", "fp_weights", "per_truth_credit", "brute_force"])
def test_common_metric_and_public_contribution_helpers_share_input_contract(name):
    call = getattr(metric, name)
    with pytest.raises(ValueError, match="aligned"):
        call(np.ones((3, 4)), np.ones((4, 3), bool))
    with pytest.raises(ValueError, match=r"\[0, 1\]"):
        call(np.full((3, 4), 1.1), np.ones((3, 4), bool))
