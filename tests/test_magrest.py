import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import pytest
from scipy.ndimage import gaussian_filter
from scipy.spatial.distance import pdist
from scipy.stats import spearmanr

from gemsdoe31.magrest import build_features, sample_offset, spaced_dots
from gemsdoe31.novelty import standardized_ranks, prospective_support

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))


def test_integer_sampling_never_wraps():
    a = np.arange(20).reshape(4, 5)
    b = sample_offset(a, 1, -2)
    assert np.array_equal(b[:-1, 2:], a[1:, :-2])
    assert (b[-1] == 0).all() and (b[:, :2] == 0).all()
    assert not sample_offset(a, 0, 9).any()


def test_restoration_operator_detects_a_synthetic_offset_not_a_new_fault_claim():
    rng = np.random.default_rng(123)
    a = gaussian_filter(rng.normal(size=(120, 120)).astype(np.float32), (1, 8))
    displaced = a.copy()
    displaced[:, 60:] = sample_offset(a, 4, 0)[:, 60:]
    f, diag = build_features(displaced, np.ones(a.shape, bool))
    assert f.dtype == np.float32 and f.shape == (3, 120, 120)
    assert np.isfinite(f).all() and f.min() >= 0 and f.max() <= 1
    # Validate the actual registration primitive on the correct orientation.
    # Max over orientations can ALSO respond to undisplaced anisotropic fabric;
    # the geological-specificity question is deliberately left to the holdout.
    from gemsdoe31.magrest import _ncc
    left = sample_offset(displaced, 0, -3)
    right = sample_offset(displaced, 0, 3)
    restored = sample_offset(displaced, -4, 3)
    patch = (slice(30, 90), slice(59, 61))
    assert _ncc(left, restored, 1e-12)[patch].mean() > _ncc(left, right, 1e-12)[patch].mean()
    assert not f[:, :20].any() and not f[:, -20:].any()
    assert diag["labelled_inputs_used"] is False


def test_builder_rejects_missing_and_misaligned_inputs():
    with pytest.raises(ValueError):
        build_features(np.full((60, 60), np.nan), np.ones((60, 60), bool))
    with pytest.raises(ValueError):
        build_features(np.ones((60, 60)), np.ones((61, 60), bool))


def test_emitter_is_deterministic_spaced_and_respects_forbidden_pixels():
    s = np.linspace(.01, 1, 900).reshape(30, 30)
    allowed = np.ones_like(s, bool)
    allowed[:, 20:] = False
    dots = spaced_dots(s, allowed, 40)
    assert dots.sum() == 40
    assert not (dots & ~allowed).any()
    assert pdist(np.argwhere(dots)).min() > 2.8
    assert np.array_equal(dots, spaced_dots(s, allowed, 40))
    assert not spaced_dots(s, allowed, 0).any()
    s[4, 4] = 1.1
    with pytest.raises(ValueError):
        spaced_dots(s, allowed, 40)


def test_exact_rank_correlation_matches_scipy_with_ties():
    a = np.array([0, 0, .2, .2, .8, 1])
    b = np.array([0, .7, .7, 0, .8, .9])
    assert np.dot(standardized_ranks(a), standardized_ranks(b)) == pytest.approx(spearmanr(a, b).statistic)
    assert standardized_ranks(np.ones(12)) is None
    assert prospective_support(a.reshape(2, 3), np.ones((2, 3), bool), 2).sum() == 2


def test_shared_template_is_not_a_private_fork():
    pins = json.loads((ROOT / "registry/template_pins.json").read_text())
    for name, item in pins["files"].items():
        assert hashlib.sha256((ROOT / "vendor/gems57" / name).read_bytes()).hexdigest() == item["sha256"]


def test_shared_evaluator_matches_local_literal_metric_and_pools_terms():
    from gems57 import evaluate_holdout as ev
    from gemsdoe31.metric import brute_force
    rng = np.random.default_rng(551)
    p = rng.random((17, 19)).astype(np.float32)
    truth = rng.random(p.shape) < .04
    visible = rng.random(p.shape) < .03
    truth &= ~visible
    valid = np.ones(p.shape, bool)
    fold = dict(truth=truth, region=valid, visible=visible, masked_known=visible)
    result, terms = ev.evaluate(p, fold, valid, block_side=5)
    expected = brute_force(np.where(visible, 0, p), truth)
    assert result["dti"] == pytest.approx(expected["DTI"], abs=1e-10)
    assert np.array_equal(terms[:, 3], np.rint(terms[:, 3]))
    summary = ev.pooled_summary({"a": terms, "b": terms}, candidate="a", draws=100)
    assert summary["paired_differences"]["b"]["delta"] == 0
    assert summary["paired_differences"]["b"]["ci95"] == [0, 0]


def test_common_writer_rejects_bad_values_before_writing(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("common_builder", ROOT / "scripts/build_submission.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setitem(module.PROFILE, "height", 8)
    monkeypatch.setitem(module.PROFILE, "width", 9)
    fp = np.ones((8, 9), bool)
    dots = fp.copy()
    for bad in [1.01, -.01, np.nan, np.inf]:
        strength = np.ones((8, 9), np.float32)
        strength[2, 3] = bad
        with pytest.raises(ValueError, match="no clipping"):
            module.write_variants(dots, fp, tmp_path / "never", name="test", values=strength)
    assert not list(tmp_path.iterdir())
