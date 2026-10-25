#!/usr/bin/env python3
"""Compose the single JSON run card for the lane (every number is read from an evidence file, none typed by hand)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text())


def main() -> None:
    e3, build, calib = load("evidence/lane_e3.json"), load("evidence/lane_candidate_build.json"), load("evidence/instrument_calibration.json")
    name = build["name"]
    gate = {k: load(f"docs/downloads/blocked/{name}-gate-{k}.json") for k in ("allfinite", "nan")}
    cand = e3["candidate"]
    gap = e3["groups"]["catalogue-gap FRESH seeds 11-15"]
    sg = e3["groups"]["off-catalogue SGMC (NOT fresh)"]
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    from gemsdoe31.gate import match_scores
    registry = load("registry/raster_registry.json")["rasters"]
    score_map, _, _ = match_scores(registry, load("registry/user_reported_scores.json")["entries"])
    by_path = {r["path"]: score_map.get(r["cache_name"]) for r in registry}
    cand = "AS-1 (this lane)"
    cg, sgm = gap[cand], sg[cand]
    uniq = gate["allfinite"]["uniqueness"]
    card = {
        "schema": "lane-run-card-1",
        "lane": "LiDAR antislope scarp (AS-1)",
        "hypothesis": "Fault scarps with a dominant up-facing (antislope) component in 3DEP LiDAR, ranked label-free, locate expert-mapped faults that "
                      "are absent from the USGS/INGENIOUS catalogue better than a generic LiDAR scarp score or random coverage.",
        "mechanism": "Normal-fault scarps and antithetic/antislope facets produce a coherent step in the bare-earth surface at 1-10 m scale that the "
                     "100 m GeoDAWN stack cannot resolve; the up-face/down-face asymmetry separates tectonic steps from symmetric ridges.",
        "mimicking_non_fault_processes": ["road cuts and embankments (tested: E2a, refuted as a filter)", "mine benches and quarries",
                                          "irrigation berms and canals", "pluvial paleoshorelines (Lake Lahontan wave-cut scarps; NOT tested)",
                                          "landslide headscarps", "lava-flow margins and volcanic cones"],
        "evaluator": e3["evaluator"],
        "holdout_dti": {
            "catalogue_gap_fresh_seeds_11_15": {"label": "HOLDOUT-DTI", "value": cg["HOLDOUT_DTI"], "ci95": cg["ci95"], "withheld_positive_pixels": cg["withheld_positive_pixels"],
                                                "random_score_null": gap["null random score"]["HOLDOUT_DTI"],
                                                "paired_vs_null": cg["paired_vs"]["null random score"]},
            "off_catalogue_sgmc_not_fresh": {"label": "HOLDOUT-DTI", "value": sgm["HOLDOUT_DTI"], "ci95": sgm["ci95"], "withheld_positive_pixels": sgm["withheld_positive_pixels"],
                                             "random_score_null": sg["null random score"]["HOLDOUT_DTI"],
                                             "paired_vs_null": sgm["paired_vs"]["null random score"]},
            "projection_note": "Projections are never scores; no organizer score exists for this file.",
        },
        "preregistered_gates": e3["preregistered_gates"],
        "leakage_canary": e3["canary"],
        "instrument_calibration": {"n_files": calib["n_files"], "spearman": calib["spearman"],
                                   "reading": "the proxies rank weakly across geometry families (rho 0.1 to 0.4); scarp-led registry files with high SGMC DTI scored live far below the D28 family"},
        "overlap_vs_registry": {"registry_rasters_compared": uniq["registry_rasters_compared"], "max_spearman_500m": uniq["max_spearman_500m"],
                                "max_non_vacuous_3px_overlap": uniq["max_overlap_3px_non_vacuous"], "duplicates_by_overlap": uniq["duplicates_by_overlap"],
                                "duplicates_with_user_reported_live_score": {p: by_path[p] for p in uniq["duplicates_by_overlap"] if by_path.get(p) is not None},
                                "duplicates_by_rank_correlation": uniq["duplicates_by_rank_correlation"],
                                "pre_placement_surface_max_spearman": build["pre_placement_surface_check"]["max_spearman_surface_vs_registry_density"]},
        "raster_sha256": {k: v["sha256"] for k, v in gate.items()},
        "validator_output": {k: {"verdict": v["verdict"], "gates": {g: {"pass": x["pass"], "detail": x["detail"]} for g, x in v["gates"].items()}} for k, v in gate.items()},
        "submission_name": name, "submission_note": build["note"], "note_chars": build["note_chars"],
        "verdict": "negative",
        "verdict_reason": "Preregistered E3 gate failed (AS-1 does not beat the random-score null on the fresh catalogue-gap draws) AND the file duplicates "
                          f"{len(uniq['duplicates_by_overlap'])} registry rasters under the lane overlap rule. Per protocol: logged as duplicate, not promoted.",
        "organizer_confirmed": False,
        "slot_recommendation": "none. Do not spend a weekly slot on this file.",
    }
    (ROOT / "evidence/run_card_lane_as1.json").write_text(json.dumps(card, indent=1, default=float) + "\n")
    print("run card written; verdict", card["verdict"])


if __name__ == "__main__":
    main()
