#!/usr/bin/env python3
"""Build registry/session_48c411be_addendum.json from verified evidence (no hand-typed numbers).

Inputs (all verified JSON produced by scripts in this repository):
- evidence/review_48c411be/gemsdoe32_forensics.json  (scripts/verify_gemsdoe32_forensics.py)
- evidence/review_cc130eb1/focus_site_verification.json (scripts/verify_focus_sites.py)
- registry/release_status.json (scripts/build_release_status.py; lattice counting bound)
- registry/session_cc130eb1_decision.json (prior nine-site register; user-reported claims)

Text fields are fixed wording. Every number is read from the inputs above and is checked against
its expected value, so a stale input fails the build rather than printing a wrong figure.
Run: ``python scripts/build_session_addendum.py``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "registry" / "session_48c411be_addendum.json"
RUN_CARD = ROOT / "evidence" / "review_48c411be" / "run_card.json"
LATTICE = ROOT / "evidence" / "review_48c411be" / "lattice_bound.json"
FORENSICS = ROOT / "evidence" / "review_48c411be" / "gemsdoe32_forensics.json"
VERIFY = ROOT / "evidence" / "review_cc130eb1" / "focus_site_verification.json"
RELEASE = ROOT / "registry" / "release_status.json"
PRIOR = ROOT / "registry" / "session_cc130eb1_decision.json"

SESSION = "arena/48c411be-gemsdoe31"
DATE_UTC = "2026-10-29"


# Fixed wording for the source and hypothesis checks run on 2026-10-29 (results of fetch-tool calls).
SOURCE_CHECKS = [
    {"name": "DrivenData problem page (metric, submission format)",
     "url": "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/",
     "result": "reachable; quotes checked: 'data outside the bounds is null or nan'; values 'between 0 and 1'; DTI alpha 0.2, beta 0.8, 300 m triangular kernel",
     "class": "OFFICIAL"},
    {"name": "DrivenData data download tab",
     "url": "https://www.drivendata.org/competitions/306/competition-doe-gems/data/",
     "result": "login-gated in earlier sessions; not re-requested in this session",
     "class": "OFFICIAL"},
    {"name": "World Stress Map Database Release 2025 (GFZ DOI)",
     "url": "https://doi.org/10.5880/WSM.2025.001",
     "result": "resolves to GFZ Data Services record; abstract states 100,842 records and A-C quality flags; the licence text was not read in this session (CC BY 4.0 remains unverified here)",
     "class": "OFFICIAL"},
    {"name": "Nevada Bureau of Mines and Geology site descriptions",
     "url": "https://nbmg.unr.edu/geothermal/sitedescriptions.html",
     "result": "reachable; index of more than 200 geothermal sites; licence not checked",
     "class": "OFFICIAL"},
    {"name": "SMU Geothermal Laboratory heat-flow database (NGDS node)",
     "url": "http://search.geothermaldata.org/dataset/115609c8-6f52-49fe-a0af-9d379d516340",
     "result": "fetch failed on 2026-10-29; UNVERIFIED (not reachable, licence not checked)",
     "class": "OFFICIAL"},
    {"name": "USGS earthquake FDSN event service (documentation)",
     "url": "https://earthquake.usgs.gov/fdsnws/event/1/",
     "result": "documentation reachable; no data query was issued from this sandbox",
     "class": "OFFICIAL"},
]

HYPOTHESIS_RECHECK = [
    {"id": "H-CC-A", "name": "thermal-spring collinearity", "tried_in_repo": False,
     "repo_evidence": "term appears only in 29 Oct cc130eb1 artifacts", "data_status": "site list not yet obtained",
     "verdict": "untested; positional error of springs versus the 300 m kernel is the main risk"},
    {"id": "H-CC-B", "name": "stress-orientation prior (World Stress Map)", "tried_in_repo": False,
     "repo_evidence": "World Stress / SHmax appear only in 29 Oct cc130eb1 artifacts", "data_status": "WSM DOI resolves; licence text not read",
     "verdict": "untested; needs the licence read before any use"},
    {"id": "H-CC-C", "name": "seismicity nodal-plane alignment", "tried_in_repo": False,
     "repo_evidence": "knowledge/2026-10-25_lane_hypotheses.md lists it as H5, NOT RUN (location error far above 300 m)",
     "data_status": "USGS FDSN documented; sandbox query not issued",
     "verdict": "not run; prior note says expected gain is low at 300 m"},
    {"id": "H-CC-D", "name": "heat-flow residual (SMU database)", "tried_in_repo": False,
     "repo_evidence": "heat flow appears in archive notes only", "data_status": "SMU node unreachable; licence unverified",
     "verdict": "blocked until the data source is reachable and licensed"},
    {"id": "H48-E", "name": "catalogue-flank radius on the D2.8 family (1, 2 px already in repo; 3 px step)", "tried_in_repo": True,
     "repo_evidence": "1 px (H27-4, 40,199 dots) and 2 px (H33-2-B2, 37,654 dots) variants exist in the repo; the 3 px step is a 100% duplicate of GEMSDOE32 (not a new family)",
     "data_status": "all inputs local; holdout needs the feature stack and a lane",
     "verdict": "the ladder cannot be climbed inside the uniqueness rule; a new dot family is required to beat 0.2778"},
]


def load(path: Path) -> dict:
    if not path.is_file():
        raise SystemExit(f"missing verified input: {path.relative_to(ROOT)} (run its verifier first)")
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"verified-input check failed: {message}")


def build() -> dict:
    f = load(FORENSICS)
    v = load(VERIFY)
    r = load(RELEASE)
    p = load(PRIOR)

    chain = f["chain"]
    counts = f["dot_counts"]
    claim = f["claim_check"]
    variant = f["variant_check"]
    removed = f["removed_distance_to_catalogue_px_D28_to_B"]
    kept = f["kept_distance_to_catalogue_px_B"]
    srcs = f["sources"]

    require(counts == {"D28": 44090, "H27_4": 40199, "H33_2_B2": 37654}, f"dot counts {counts}")
    require(chain["B_subset_of_H27"] and chain["H27_subset_of_D28"], "set-inclusion chain broken")
    require(claim["claim_holds_exactly"] and claim["removed_dots_total"] == claim["removed_dots_within_2px_of_catalogue"]
            == chain["removed_D28_to_B"] == 6436, "2 px deletion claim does not hold exactly")
    require(f["dots_on_catalogue"]["B_dots_on_catalogue"] == 0, "GEMSDOE32 dots lie on the catalogue")
    require(variant["identical_inside_footprint"] and variant["footprint_pixels"] == 5167373, "variant mismatch")
    require(variant["zeros_variant_nan_pixels"] == 0 and variant["zeros_variant_outside_footprint_values"] == [0.0],
            "zeros variant convention changed")
    require(v["all_sha256_match"] is True and v["all_values_in_0_1"] is True, "focus-site verification not clean")
    lattice = r["lattice_coverage"]
    require(lattice["candidate_dots"] == 37654, "lattice budget changed")

    ladder = f["radius_ladder_D28"]
    v3 = f["radius_3px_variant_of_GEMSDOE32"]
    require(ladder["1.0"]["equals_H27_4_file"] and ladder["2.0"]["equals_H33_2_B2_file"],
            "radius ladder no longer reproduces the H27-4 and H33-2-B2 files")
    require(not ladder["1.5"]["equals_H27_4_file"] and not ladder["1.5"]["equals_H33_2_B2_file"],
            "1.5 px cut unexpectedly matches a repo file")
    require(v3["duplicate_by_70pct_rule"] and v3["share_within_3px_of_GEMSDOE32"] > 0.99,
            "3 px variant no longer a duplicate of GEMSDOE32")

    kept_min = kept["min"]
    require(abs(kept_min - 5 ** 0.5) < 1e-6, f"kept minimum distance {kept_min} is not sqrt(5)")

    rows = []
    for site in p["focus_site_rows"]:
        rows.append({"site": site["site"], "reported_top_score_USER_REPORTED": site["reported_top_score_USER_REPORTED"]})
    gem32 = next(row for row in rows if row["site"] == "GEMSDOE32")
    require(gem32["reported_top_score_USER_REPORTED"] == 0.2778, "GEMSDOE32 reported score changed")

    return {
        "schema_version": 1,
        "session": SESSION,
        "date_utc": DATE_UTC,
        "evidence_class": "COMPUTED from pinned bytes; scores are USER-REPORTED",
        "decision": "No file is cleared to submit. No new TIFF was generated and no experiment was run.",
        "download_permission": "research download only",
        "submission_permission": "none (DO NOT SUBMIT)",
        "gemsdoe32": {
            "user_reported_score": 0.2778,
            "owner_list_name": "h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros",
            "registry_row_name": "gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-nan.tif",
            "zeros_file": {
                "path": srcs["gemsdoe32_zeros"]["path"], "commit": srcs["gemsdoe32_zeros"]["commit"],
                "sha256": srcs["gemsdoe32_zeros"]["sha256"],
                "outside_footprint": "every cell written as 0 (no NaN); grid fully finite",
            },
            "nan_file": {
                "path": srcs["gemsdoe32_nan"]["path"], "commit": srcs["gemsdoe32_nan"]["commit"],
                "sha256": srcs["gemsdoe32_nan"]["sha256"],
                "outside_footprint": "NaN",
            },
            "identical_inside_footprint": variant["identical_inside_footprint"],
            "positive_dots": counts["H33_2_B2"],
            "footprint_pixels": variant["footprint_pixels"],
        },
        "mechanism_verified": {
            "chain_D28_H27_B": {
                "D28_dots": counts["D28"], "H27_4_dots": counts["H27_4"], "H33_2_B2_dots": counts["H33_2_B2"],
                "removed_D28_to_H27_4": chain["removed_D28_to_H27"],
                "removed_H27_4_to_B": chain["removed_H27_to_B"],
                "removed_D28_to_B": chain["removed_D28_to_B"],
                "set_inclusion_holds": bool(chain["B_subset_of_H27"] and chain["H27_subset_of_D28"]),
            },
            "two_px_rule": {
                "text": "Exactly the D2.8 dots within 2 px of the restored catalogue are deleted; no other dot is removed.",
                "removed_dots_within_2px": claim["removed_dots_within_2px_of_catalogue"],
                "removed_dots_total": claim["removed_dots_total"],
                "claim_holds_exactly": claim["claim_holds_exactly"],
            },
            "distances_to_catalogue_px": {
                "removed_min": removed["min"], "removed_max": removed["max"],
                "kept_min": kept["min"],
                "kept_min_is_sqrt5": abs(kept["min"] - 5 ** 0.5) < 1e-6,
            },
            "radius_ladder_D28": {
                "text": "Deleting D2.8 dots within r px of the restored catalogue. r = 1 reproduces the H27-4 file; r = 2 reproduces the H33-2-B2 file (GEMSDOE32); r = 1.5 matches neither.",
                "removed_by_radius": {k: v["removed"] for k, v in ladder.items()},
                "kept_by_radius": {k: v["kept"] for k, v in ladder.items()},
                "reproduces_H27_4": ladder["1.0"]["equals_H27_4_file"],
                "reproduces_H33_2_B2": ladder["2.0"]["equals_H33_2_B2_file"],
            },
            "radius_3px_step_from_GEMSDOE32": {
                "dots_removed": v3["dots_removed_from_B"],
                "dots_remaining": v3["dots_remaining"],
                "share_within_3px_of_GEMSDOE32": v3["share_within_3px_of_GEMSDOE32"],
                "duplicate_by_70pct_rule": v3["duplicate_by_70pct_rule"],
                "meaning": "Any further pruning step of this family is a duplicate of GEMSDOE32 under the owner's rule.",
            },
            "dots_on_catalogue_pixels": f["dots_on_catalogue"],
            "interpretation": "INFERENCE: the official metric (alpha 0.2, beta 0.8) penalises dots that are not near "
                              "the test faults. Removing catalogue-adjacent dots lowers false-positive weight, but also "
                              "removes true-positive weight if a new fault lies within 300 m of a removed dot. "
                              "The +0.0178 user-reported gain over D2.8 (0.2600) is consistent with the first effect; "
                              "it is not measured here.",
        },
        "uniqueness_counting_bound": {
            "footprint_pixels": lattice["footprint_pixels"],
            "outside_3px_halo_pixels": lattice["outside_3px_halo"],
            "candidate_dots": lattice["candidate_dots"],
            "minimum_overlap_any_same_budget": lattice["minimum_overlap_any_same_budget"],
            "registered_control": r["registered_witness"]["path"],
            "registered_control_sha256": r["registered_witness"]["sha256"],
            "qualification": "COMPUTED counting bound for the 37,654-dot budget against the registered spacing-5 "
                             "control. This is a stop condition, not a bypass target; no exemption is applied.",
        },
        "prior_nine_site_claims_USER_REPORTED": rows,
        "focus_site_verification_source": "evidence/review_cc130eb1/focus_site_verification.json",
        "official_source_checks": SOURCE_CHECKS,
        "hypothesis_recheck": HYPOTHESIS_RECHECK,
    }


def _values_in_unit_interval(unique_values: list) -> bool:
    """True only if the complete set of finite values lies in [0, 1] (the forensic list keeps 5 entries)."""
    if len(unique_values) >= 5:
        raise SystemExit("unique-value list may be truncated; extend the forensic check before validating")
    return bool(unique_values) and min(unique_values) >= 0.0 and max(unique_values) <= 1.0


def run_card(data: dict) -> dict:
    """Protocol run card (PARALLEL-RUN PROTOCOL item 5). Negative verdict: no raster, no experiment."""
    f = load(FORENSICS)
    lat = load(LATTICE)
    g = data["gemsdoe32"]
    card = {
        "schema_version": 1,
        "session": SESSION,
        "date_utc": DATE_UTC,
        "lane": "none assigned (no method paragraph in this session's owner prompt)",
        "hypothesis": "No new hypothesis was tested. Candidates H-CC-A to H-CC-D and H48-E were re-checked against the repository only.",
        "mechanism": "Not applicable (no experiment). Verified mechanism for the 0.2778 claim: D2.8 with exactly the dots within 2 px of the restored catalogue deleted.",
        "non_fault_mimic": "Catalogue-proximity artifact: pruning dots near mapped faults lowers the false-positive term without finding any new fault.",
        "holdout_dti": {"value": None, "evidence_class": "NOT RUN",
                        "reason": "No feature stack and no method lane; HOLDOUT-DTI cannot be produced."},
        "user_reported_score_for_reference": {"value": 0.2778, "evidence_class": "USER-REPORTED", "organizer_receipt": None},
        "correlation_overlap_vs_registry": {
            "new_raster": None,
            "uniqueness_counting_bound": {
                "candidate_dots": lat["budget_dots"],
                "uncovered_pixels": lat["pixels_uncovered_by_radius"],
                "forced_minimum_overlap": lat["forced_minimum_overlap_for_budget"],
                "evidence_class": "COMPUTED counting bound; not a score",
            },
            "gemsdoe32_3px_pruned_variant_share_within_3px": data["mechanism_verified"]["radius_3px_step_from_GEMSDOE32"]["share_within_3px_of_GEMSDOE32"],
        },
        "raster_sha256": None,
        "referenced_rasters_sha256": {"GEMSDOE32_zeros": g["zeros_file"]["sha256"], "GEMSDOE32_nan": g["nan_file"]["sha256"]},
        "validator_output_referenced_GEMSDOE32": {
            "grid_shape": f["grids"]["gemsdoe32_nan"]["shape"],
            "crs": f["grids"]["gemsdoe32_nan"]["crs"],
            "transform": f["grids"]["gemsdoe32_nan"]["transform"],
            "dtype": f["grids"]["gemsdoe32_nan"]["dtype"],
            "nan_variant_outside_footprint_is_nan": f["variant_check"]["nan_variant_outside_footprint_is_nan"],
            "zeros_variant_nan_pixels": f["variant_check"]["zeros_variant_nan_pixels"],
            "zeros_variant_outside_footprint_values": f["variant_check"]["zeros_variant_outside_footprint_values"],
            "values_in_0_1": _values_in_unit_interval(f["grids"]["gemsdoe32_nan"]["values_unique_finite"]),
            "no_new_validator_run": True,
        },
        "submission_name": None,
        "note": "No submission: no new raster generated. DO NOT SUBMIT.",
        "note_chars": len("No submission: no new raster generated. DO NOT SUBMIT."),
        "ok_to_download_for_research": "study only; these files are already published by the owner",
        "ok_to_submit": False,
        "experiments_run": 0,
        "budget": "3 experiments or 2 hours; 0 experiments used",
        "leaderboard_estimate": {"value": None, "estimate_class": "not estimable",
                                 "reason": "No holdout-validated model and no organizer receipt."},
        "verdict": "negative",
    }
    if card["note_chars"] > 140:
        raise SystemExit("note exceeds 140 characters")
    return card


def main() -> int:
    data = build()
    text = json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n"
    card_text = json.dumps(run_card(data), indent=2, sort_keys=True, allow_nan=False) + "\n"
    if "--check" in sys.argv:
        ok = (OUT.is_file() and OUT.read_text(encoding="utf-8") == text
              and RUN_CARD.is_file() and RUN_CARD.read_text(encoding="utf-8") == card_text)
        if not ok:
            print("addendum or run card is stale; rerun scripts/build_session_addendum.py", file=sys.stderr)
            return 1
        print("addendum register and run card are current")
        return 0
    OUT.write_text(text, encoding="utf-8")
    RUN_CARD.parent.mkdir(parents=True, exist_ok=True)
    RUN_CARD.write_text(card_text, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} and {RUN_CARD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
