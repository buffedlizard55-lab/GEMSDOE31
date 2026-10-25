#!/usr/bin/env python3
"""E3 — confirmation of the frozen candidate AS-1 on fresh draws (lane experiment 3 of 3).

PREREGISTERED (committed before this script was first run; see git history of the branch):

  candidate   AS-1, exactly as defined in scripts/lane_candidate.py (no parameter may change after this commit)
  fresh data  catalogue hide-and-recover seeds 11..15, 50 % of fault pixels hidden per draw (E1/E2 used seeds 1..3)
  not fresh   the off-catalogue SGMC proxy (it was seen in E1/E2); it is reported but cannot confirm
  comparators the live-best file h33-2-b2 (USER-REPORTED 0.2778), the D28 incumbent (USER-REPORTED 0.2708), the
              generic-scarp control S0 at the same budget, and a random-score null at the same budget/candidates
  metric      LANE-EVAL-1 pooled DTI; 95 % intervals from a paired 8x8 spatial-tile cluster bootstrap (1000 draws)
  PROMOTION   promote to the selector only if ALL hold:
              (1) AS-1 beats h33-2-b2 on the pooled fresh catalogue-gap draws AND on the SGMC proxy, each with a
                  paired-bootstrap 95 % lower bound > 0;
              (2) AS-1 beats h33-2-b2 in at least 3 of 4 spatial quadrants on each instrument;
              (3) no component surface has a single-feature AUC above 0.90 (leakage canary);
              (4) AS-1 beats the random-score null by a paired lower bound > 0 on both instruments.
              Otherwise the verdict is NEGATIVE and the file is labelled not promoted.

Writes evidence/lane_e3.json.
"""

from __future__ import annotations

import glob
import time

import numpy as np
from lane_candidate import BUDGET, CANDIDATE_ID, emit_candidate, surface
from lane_common import (CELL_M, ROOT, auc, discovery_instrument, emit, holdout_instruments, lane, load_base, load_dots,
                         load_lidar, pct_rank, write_json)
from scipy.ndimage import distance_transform_edt, gaussian_filter

FRESH_SEEDS = (11, 12, 13, 14, 15)
N_BOOT = 1000


def quadrant_dti(stats_list: list[dict]) -> dict[str, float]:
    tp = sum(s["tile_tp"] for s in stats_list)
    fp = sum(s["tile_fp"] for s in stats_list)
    g = sum(s["tile_g"] for s in stats_list)
    tiles = np.arange(lane.TILE_ROWS * lane.TILE_COLS)
    tr, tc = tiles // lane.TILE_COLS, tiles % lane.TILE_COLS
    out = {}
    for name, sel in (("NW", (tr < 4) & (tc < 4)), ("NE", (tr < 4) & (tc >= 4)),
                      ("SW", (tr >= 4) & (tc < 4)), ("SE", (tr >= 4) & (tc >= 4))):
        out[name] = lane.dti_from(tp[sel].sum(), fp[sel].sum(), g[sel].sum())
    return out


def find_registry_raster(fragment: str) -> np.ndarray:
    hits = sorted(glob.glob(str(ROOT / "data/registry_rasters" / f"*{fragment}*nan.tif")) +
                  glob.glob(str(ROOT / "data/registry_rasters" / f"*{fragment}*nanoutside.tif")))
    if not hits:
        raise SystemExit(f"registry raster for {fragment!r} not restored; run scripts/build_raster_registry.py --restore")
    return load_dots(hits[0])


def main() -> None:
    t0 = time.time()
    base = load_base()
    lid = load_lidar()
    valid = base["footprint"] & (lid["valid"] > 0)
    cand_surface, parts = surface(lid, valid, parts=True)
    canary = {"AS-1 surface": {"auc_off_catalogue_sgmc": auc(cand_surface, base["far_field"], valid),
                               "auc_catalogue": auc(cand_surface, base["catalogue"], valid)}}
    for k, v in parts.items():
        canary[k] = {"auc_off_catalogue_sgmc": auc(v, base["far_field"], valid), "auc_catalogue": auc(v, base["catalogue"], valid)}
    control_surface = gaussian_filter(pct_rank(lid["ex_max"].astype(np.float32), valid), 0.8) * valid
    null_surface = np.random.default_rng(20261025).random(valid.shape).astype(np.float32) * valid
    print("canary:", {k: round(v["auc_off_catalogue_sgmc"], 3) for k, v in canary.items()})

    fixed = {"h33-2-b2 (live-best, USER-REPORTED 0.2778)": find_registry_raster("h33-h33-2-b2"),
             "D28 incumbent (USER-REPORTED 0.2708)": load_dots(ROOT / "docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif")}
    insts = [*holdout_instruments(base, seeds=FRESH_SEEDS), discovery_instrument(base)]
    stats: dict[str, dict[str, dict]] = {i.name: {} for i in insts}
    for inst in insts:
        for name, dots in fixed.items():
            stats[inst.name][name] = lane.sufficient_stats(dots, inst)
        stats[inst.name][f"{CANDIDATE_ID} (this lane)"] = lane.sufficient_stats(emit_candidate(cand_surface, valid, inst.visible), inst)
        stats[inst.name]["control S0 generic scarp"] = lane.sufficient_stats(emit_candidate(control_surface, valid, inst.visible), inst)
        stats[inst.name]["null random score"] = lane.sufficient_stats(emit_candidate(null_surface, valid, inst.visible), inst)
        print(f"  {inst.name} done ({time.time() - t0:.0f}s)", flush=True)

    names = list(stats[insts[0].name])
    groups = {"catalogue-gap FRESH seeds 11-15": [i.name for i in insts if i.name.startswith("catalogue-gap")],
              "off-catalogue SGMC (NOT fresh)": ["off-catalogue-sgmc"]}
    cand = f"{CANDIDATE_ID} (this lane)"
    b2 = "h33-2-b2 (live-best, USER-REPORTED 0.2778)"
    inc = "D28 incumbent (USER-REPORTED 0.2708)"
    out: dict = {"evaluator": lane.EVAL_VERSION, "candidate": CANDIDATE_ID, "budget": BUDGET, "fresh_seeds": FRESH_SEEDS,
                 "canary": canary, "groups": {}}
    gates: dict = {}
    for gname, members in groups.items():
        pooled = {n: [stats[m][n] for m in members] for n in names}
        boot = lane.tile_bootstrap(pooled, n_boot=N_BOOT)
        block = {}
        for n in names:
            quad = quadrant_dti(pooled[n])
            block[n] = {"HOLDOUT_DTI": boot[n]["point"], "ci95": boot[n]["ci95"],
                        "dots": int(np.mean([s["dots"] for s in pooled[n]])),
                        "credit_per_dot": sum(s["tp"] for s in pooled[n]) / max(sum(s["dots"] for s in pooled[n]), 1),
                        "withheld_positive_pixels": int(sum(s["g"] for s in pooled[n])), "quadrants": quad}
        for ref in (b2, inc, "control S0 generic scarp", "null random score"):
            d = lane.paired_delta(boot[cand]["draws"], boot[ref]["draws"])
            qwins = sum(block[cand]["quadrants"][q] > block[ref]["quadrants"][q] for q in ("NW", "NE", "SW", "SE"))
            block[cand].setdefault("paired_vs", {})[ref] = {**d, "quadrants_won": qwins}
        out["groups"][gname] = block
        print(f"\n== {gname}  (withheld positives {block[cand]['withheld_positive_pixels']:,})")
        for n in names:
            r = block[n]
            print(f"  {n:46s} DTI {r['HOLDOUT_DTI']:.4f} [{r['ci95'][0]:.4f},{r['ci95'][1]:.4f}] c/dot {r['credit_per_dot']:.3f} "
                  f"quad {', '.join(f'{k}:{v:.3f}' for k, v in r['quadrants'].items())}")
        for ref, d in block[cand]["paired_vs"].items():
            print(f"   AS-1 minus {ref:46s} {d['mean']:+.4f} [{d['ci95'][0]:+.4f},{d['ci95'][1]:+.4f}] P(better)={d['p_better']:.3f} quadrants {d['quadrants_won']}/4")
        gates[gname] = {"beats_live_best_lower_bound_positive": block[cand]["paired_vs"][b2]["ci95"][0] > 0,
                        "quadrants_won_vs_live_best": block[cand]["paired_vs"][b2]["quadrants_won"],
                        "beats_null_lower_bound_positive": block[cand]["paired_vs"]["null random score"]["ci95"][0] > 0}
    leakage_ok = all(v["auc_off_catalogue_sgmc"] <= 0.90 and v["auc_catalogue"] <= 0.90 for v in canary.values())
    promote = (all(g["beats_live_best_lower_bound_positive"] and g["quadrants_won_vs_live_best"] >= 3 and g["beats_null_lower_bound_positive"]
                   for g in gates.values()) and leakage_ok)
    out["preregistered_gates"] = {"per_instrument": gates, "leakage_canary_ok": leakage_ok, "PROMOTE_TO_SELECTOR": bool(promote)}
    print("\nGATES:", out["preregistered_gates"])
    write_json(ROOT / "evidence/lane_e3.json", out)
    print(f"done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
