import numpy as np

from gemsdoe31 import lane, metric


def _scene(seed=0, shape=(60, 70)):
    rng = np.random.default_rng(seed)
    truth = np.zeros(shape, bool)
    truth[10:50, 20] = True
    truth[30, 40:65] = True
    dots = rng.random(shape) < 0.04
    dots[10:50, 21] = True
    return truth, dots


def test_pooled_dti_matches_the_reference_metric_on_a_single_tile_set():
    truth, dots = _scene()
    inst = lane.make_instrument("t", truth)
    stats = lane.sufficient_stats(dots, inst)
    reference = metric.dti(dots.astype(np.float32), truth)["DTI"]
    assert abs(lane.pooled_dti([stats]) - reference) < 1e-9


def test_masked_visible_pixels_are_zeroed_and_cost_nothing():
    truth, dots = _scene(1)
    visible = np.zeros_like(truth)
    visible[0:5, 0:70] = True
    dots = dots | visible
    inst = lane.make_instrument("t", truth, masked=visible)
    with_mask = lane.sufficient_stats(dots, inst)
    without = lane.sufficient_stats(dots & ~visible, lane.make_instrument("t", truth))
    assert with_mask["dots"] == without["dots"]
    assert abs(with_mask["tp"] - without["tp"]) < 1e-9 and abs(with_mask["fp"] - without["fp"]) < 1e-9


def test_restrict_truth_scores_only_the_zone_but_keeps_the_false_positive_rule():
    truth, dots = _scene(2)
    inst = lane.make_instrument("t", truth)
    zone = np.zeros_like(truth)
    zone[:, :35] = True
    sub = lane.restrict_truth(inst, zone)
    assert sub.n_truth == int((truth & zone).sum())
    full, part = lane.sufficient_stats(dots, inst), lane.sufficient_stats(dots, sub)
    assert part["fp"] == full["fp"]              # FP charge still uses all truth
    assert part["tp"] <= full["tp"] + 1e-9
    assert part["g"] == sub.n_truth


def test_prefix_mask_takes_exactly_the_first_n_ordered_cells():
    order = np.array([[0, 0], [1, 2], [3, 3], [4, 4]])
    mask = lane.prefix_mask(order, 2, (6, 6))
    assert mask.sum() == 2 and mask[0, 0] and mask[1, 2] and not mask[3, 3]
