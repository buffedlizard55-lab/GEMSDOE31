"""H31-U runner pure-function tests (synthetic arrays only; no data/ needed)."""
import importlib.util
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "vendor"), str(ROOT / "scripts")]
spec = importlib.util.spec_from_file_location("run_h31u", ROOT / "scripts/run_h31u.py")
U = importlib.util.module_from_spec(spec)
spec.loader.exec_module(U)

spec2 = importlib.util.spec_from_file_location("selector_audit", ROOT / "scripts/selector_audit.py")
S = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(S)


def test_rank01_ties_and_range():
    foot = np.ones((4, 4), bool)
    a = np.array([[1, 1, 2, 3]] * 4, dtype=np.float32)
    r = U.rank01(a, foot)
    assert r.min() >= 0.0 and r.max() <= 1.0
    # tied values share the averaged rank
    assert r[0, 0] == r[0, 1]
    assert r[0, 3] > r[0, 2] > r[0, 0]


def test_rank01_outside_footprint_zero():
    foot = np.zeros((3, 3), bool)
    foot[:2, :2] = True
    r = U.rank01(np.arange(9, dtype=np.float32).reshape(3, 3), foot)
    assert (r[~foot] == 0).all()


def test_geomean_rank_bounds():
    rng = np.random.default_rng(1)
    parts = [rng.random((10, 10), dtype=np.float32) for _ in range(3)]
    g = U.geomean_rank(parts)
    assert g.shape == (10, 10) and g.min() >= 0.0 and g.max() <= 1.0


def test_clean_winsorizes_and_fills():
    foot = np.ones((200, 200), bool)
    a = np.full((200, 200), 2.0, dtype=np.float32)
    a[0, 0] = np.nan
    a[0, 1] = 1e9
    out = U.clean(a, foot)
    assert np.isfinite(out).all() and out.max() < 1e6


def test_phi_equals_spearman_for_binary():
    from gems57 import uniqueness
    rng = np.random.default_rng(7)
    foot = np.ones((200, 200), bool)
    a = rng.random((200, 200)) < 0.01
    b = rng.random((200, 200)) < 0.01
    phi = S.phi_binary(a, b, foot)
    rho = uniqueness.surface_rho(a.astype(np.float32), b.astype(np.float32), foot)
    assert abs(phi - rho["spearman_full_footprint"]) < 1e-9


def test_projection_anchor_algebra_recovers_known_values():
    # Two anchors with equal live TPw T and known D0 reproduce D0 exactly.
    d0_true, t_live = 10694.6, 5000.0
    n1, n2 = 44090, 40199
    s1 = t_live / (d0_true + 0.2 * n1)
    s2 = t_live / (d0_true + 0.2 * n2)
    denom_b = 0.2 * (n1 - n2) / (s2 / s1 - 1.0)
    assert abs((denom_b - 0.2 * n2) - d0_true) < 1e-6


def test_selector_decision_primary_consistency():
    import json
    dec = json.loads((ROOT / "registry/selector_decision_20261026.json").read_text())
    card = json.loads((ROOT / "evidence/h31u/run_card.json").read_text())
    assert card["verdict"] == "negative" and card["ok_to_submit"] is False
    # Current owner protocol restores both-stage literal checks; no selector in this lane.
    assert dec["primary_submission"] is None
    assert dec["promoted_lanes"] == []
    assert dec["alternates"] == []
    assert dec["policy_version"] == "literal-registry-20261026-9883b598"
    # every focus historical best is a duplicate of the H33 lane (except H33 itself trivially)
    assert all(r["duplicate_of_h33_lane"] for r in dec["focus_sites"])
