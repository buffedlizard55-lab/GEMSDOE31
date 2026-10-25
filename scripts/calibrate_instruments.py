#!/usr/bin/env python3
"""How well do the local instruments rank files whose live score the user reported? (diagnostic, not an experiment)

For every registry raster whose name matches an entry of registry/user_reported_scores.json (class USER-REPORTED),
score it on the off-catalogue SGMC proxy and on catalogue-gap hide-and-recover draws (seeds 21..25, none used in
E1-E3) and report Spearman rank correlations with the reported leaderboard value. Also reports two trivial
predictors (dot count distance to 40k, and an in-footprint coverage fraction) as controls.
Files whose fragment matches more than one distinct dot set are skipped as ambiguous.

Writes evidence/instrument_calibration.json.
"""

from __future__ import annotations

import json
import time

import numpy as np
from lane_common import ROOT, discovery_instrument, holdout_instruments, lane, load_base, load_dots, write_json
from gemsdoe31.gate import match_scores
from scipy.ndimage import binary_dilation
from scipy.stats import spearmanr

SEEDS = (21, 22, 23, 24, 25)


def main() -> None:
    t0 = time.time()
    base = load_base()
    registry = json.loads((ROOT / "registry/raster_registry.json").read_text())["rasters"]
    scores = json.loads((ROOT / "registry/user_reported_scores.json").read_text())["entries"]
    insts = [discovery_instrument(base), *holdout_instruments(base, seeds=SEEDS)]
    rows = []
    _, ambiguous, unmatched = match_scores(registry, scores)
    for ent in scores:
        if ent["fragment"] in ambiguous or ent["fragment"] in unmatched:
            continue
        matches = [e for e in registry if any(ent["fragment"].lower() in n.lower() for n in [e["path"]] + [v.split(":", 1)[1] for v in e["variants"]])]
        dots = load_dots(ROOT / "data/registry_rasters" / matches[0]["cache_name"]) & base["footprint"]
        sgmc = lane.sufficient_stats(dots, insts[0])
        gap = [lane.sufficient_stats(dots, i) for i in insts[1:]]
        coverage = float(binary_dilation(dots, structure=np.ones((7, 7), bool)).sum() / base["footprint"].sum())
        rows.append({"fragment": ent["fragment"], "site": ent["site"], "live_user_reported": ent["score"],
                     "dots": int(dots.sum()), "coverage_3px": coverage, "sgmc_DTI": lane.pooled_dti([sgmc]),
                     "sgmc_credit_per_dot": sgmc["tp"] / max(sgmc["dots"], 1), "gap_DTI": lane.pooled_dti(gap),
                     "dots_on_catalogue": int((dots & base["catalogue"]).sum())})
    live = np.array([r["live_user_reported"] for r in rows])
    out = {"evaluator": lane.EVAL_VERSION, "seeds": SEEDS, "n_files": len(rows), "ambiguous": ambiguous, "unmatched": unmatched,
           "claim_class": "USER-REPORTED live values vs COMPUTED proxies; n small, files not all independent", "spearman": {}}
    for key in ("sgmc_DTI", "sgmc_credit_per_dot", "gap_DTI", "coverage_3px", "dots"):
        rho, p = spearmanr([r[key] for r in rows], live)
        out["spearman"][key] = {"rho": float(rho), "p": float(p)}
    near = -np.abs(np.array([r["dots"] for r in rows]) - 40_000)
    rho, p = spearmanr(near, live)
    out["spearman"]["neg_abs(dots-40000)"] = {"rho": float(rho), "p": float(p)}
    # restricted to files that do not touch the catalogue at all: the live-vs-proxy relation among dot sets that are comparable
    sub = [r for r in rows if r["dots_on_catalogue"] == 0 and 10_000 <= r["dots"] <= 130_000]
    if len(sub) > 5:
        out["spearman_zero_catalogue_dots_10k_130k"] = {"n": len(sub), **{k: dict(zip(("rho", "p"), map(float, spearmanr([r[k] for r in sub], [r["live_user_reported"] for r in sub])))) for k in ("sgmc_DTI", "sgmc_credit_per_dot", "gap_DTI")}}
    out["rows"] = sorted(rows, key=lambda r: -r["live_user_reported"])
    write_json(ROOT / "evidence/instrument_calibration.json", out)
    print(f"{len(rows)} files; ambiguous {len(ambiguous)}; unmatched {len(unmatched)}")
    for k, v in out["spearman"].items():
        print(f"  {k:24s} rho {v['rho']:+.3f} p {v['p']:.3f}")
    print(out.get("spearman_zero_catalogue_dots_10k_130k"))
    for r in out["rows"][:25]:
        print(f"  {r['live_user_reported']:.4f} {r['fragment'][:52]:52s} dots {r['dots']:>7,} sgmc {r['sgmc_DTI']:.4f} gap {r['gap_DTI']:.4f} oncat {r['dots_on_catalogue']}")
    print(f"done {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
