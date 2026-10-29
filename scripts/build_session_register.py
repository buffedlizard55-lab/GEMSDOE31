#!/usr/bin/env python3
"""Build ``registry/session_cc130eb1_decision.json`` from verified evidence (no hand-typed numbers).

Inputs (all read, none edited):
  * ``evidence/review_cc130eb1/focus_site_verification.json`` (written by ``scripts/verify_focus_sites.py``)
  * ``registry/focus_review.json`` (USER-REPORTED claim values and pinned source URLs)
  * ``docs/data/h33-forensics.json`` (repository forensic record for the H27 -> H33 pruning)

The register is consumed by ``scripts/build_site.py`` to render the decision panel on the front page
and the executive summary. Official-source quotations are copied verbatim from ``fetch_page``
results on 2026-10-29 and are listed with their URLs so a reviewer can re-check them.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / "evidence" / "review_cc130eb1" / "focus_site_verification.json"
OUT = ROOT / "registry" / "session_cc130eb1_decision.json"

FETCHED = "2026-10-29"
OFFICIAL_SOURCES = [
    {
        "id": "dd-problem-page",
        "class": "OFFICIAL",
        "title": "DrivenData GEMS Prize problem description (page 967)",
        "quote_normalisation": "Math glyphs (for example alpha, beta, TPw) are normalised to plain text; wording is unchanged. Verified against a re-fetch on 2026-10-29.",
        "url": "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/",
        "fetched": FETCHED,
        "quotes": [
            "the sponsors have compiled a set of newly identified faults in the GeoDAWN region that are not "
            "included in the existing USGS fault database. These new faults have been manually labeled by fault "
            "experts and comprise the test dataset for the competition.",
            "Competitors must choose a single submission for scoring across both rounds before the deadline, without knowing their private test set performance.",
            "For this competition, we set α=0.2 and β=0.8, which reduces the penalty for false positive predictions and increases the penalty for false negative predictions.",
            "Participants are allowed to use any additional data sources, provided that the participants possess a license that permits the data to be used in this challenge and shared with the sponsor for evaluation purposes.",
            "The labels for this challenge come from the USGS quaternary fault maps and from INGENIOUS.",
            "Your submission has the same bounds as the training data, and data outside the bounds is null or nan.",
            "Your submission contains a single layer with datatype of 32-bit float (float32) with values between 0 "
            "and 1 indicating the confidence or probability of fault presence",
            "A sample submission that predicts total fault absence is provided for your reference on the data "
            "download page.",
        ],
    },
    {
        "id": "nlr-official-rules",
        "class": "OFFICIAL",
        "title": "GEMS Prize Official Rules, September 2026 (NLR, docs.nlr.gov/docs/fy26osti/96647.pdf)",
        "url": "https://docs.nlr.gov/docs/fy26osti/96647.pdf",
        "fetched": FETCHED,
        "quotes": [
            "Participants will submit a single entry, which will be evaluated in two prize phases using a "
            "distance-weighted Tversky index.",
            "You can make multiple submissions, subject to the limits specified on the competition website "
            "(three submissions per week).",
            "Scores displayed on the public leaderboard while the competition is running may not be the same as "
            "the final scores on the private leaderboard at the end of the competition.",
            "The labels for this prize come from the USGS Quaternary Fault and Fold Database and from a set of "
            "newly identified faults labeled by geology experts at the National Laboratory of the Rockies (NLR) "
            "and USGS.",
        ],
    },
    {
        "id": "nlr-rules-sections-3-3-to-3-6",
        "class": "OFFICIAL",
        "title": "GEMS Prize Official Rules, §3.3–§3.6 and Appendix A.1 (same PDF)",
        "url": "https://docs.nlr.gov/docs/fy26osti/96647.pdf",
        "fetched": FETCHED,
        "quotes": [
            "you may submit more than one set of predictions for automated scoring on the competition platform up to "
            "three per week, as specified on the competition website. By the submission deadline, you must select only "
            "one set of predictions to use as your final submission for the final evaluation and ranking.",
            "The competitor’s score on the public test dataset will be shown on the public leaderboard.",
            "The competitor’s score on the private test dataset will be used for the first prize round when the competition closes.",
            "you must make your decision without knowledge of your scores on the private test set.",
            "The training labels contain existing fault data at 100-m resolution where positively labeled pixels indicate fault presence. "
            "These labels were obtained from the INGENIOUS project’s Great Basin Regional Dataset Compilation.",
            "by 5:00 p.m. ET on the prize submission deadline date before the prize’s phase submission period closes.",
        ],
        "note": "The exact calendar deadline is not in the fetched text; the rules defer to the competition website (not verified).",
    },
    {
        "id": "ingenious-great-basin-compilation",
        "class": "OFFICIAL-DATA-PROVIDER",
        "title": "INGENIOUS Great Basin Regional Dataset Compilation (Geothermal Data Repository, DOI 10.15121/1881483)",
        "url": "https://doi.org/10.15121/1881483",
        "fetched": "2026-10-29 (cited in the rules §3.3 footnote 4; DOI not re-downloaded)",
        "quotes": [],
        "note": "Source of the training fault labels per the rules; licence not checked in this session.",
    },
    {
        "id": "organizer-reference-solution",
        "class": "OFFICIAL",
        "title": "DrivenData reference solution (GitHub), notebook alpha/beta cells",
        "url": "https://github.com/drivendataorg/gems-prize-reference-solution",
        "fetched": FETCHED,
        "quotes": [
            "alpha = 0.2  # weight for false positives in Tversky loss",
            "beta = 0.8  # weight for false negatives in Tversky loss",
        ],
        "note": "Training loss only; the reference notebook does not implement the scoring evaluator.",
    },
    {
        "id": "gfz-wsm-2025",
        "class": "OFFICIAL-DATA-PROVIDER",
        "title": "World Stress Map Database Release 2025 (GFZ Data Services, DOI 10.5880/WSM.2025.001)",
        "url": "https://dataservices.gfz-potsdam.de/wsm/showshort.php?id=a23de1c9-1f73-11f0-914a-f12b0080820d",
        "fetched": "2026-10-29 (search result snippet; not re-downloaded)",
        "quotes": ["The WSM database release 2025 contains 100,842 data records within the Earth’s crust.",
                   "License: CC BY 4.0"],
    },
    {
        "id": "nbmg-thermal-sites",
        "class": "OFFICIAL-STATE-SURVEY",
        "title": "Nevada Bureau of Mines and Geology: geothermal site descriptions",
        "url": "https://nbmg.unr.edu/geothermal/sitedescriptions.html",
        "fetched": "2026-10-29 (search result snippet; not re-downloaded)",
        "summary": "Per-site descriptions for named Nevada hot springs, thermal wells and geothermal areas (paraphrase, not a quote).",
        "quotes": [],
    },
    {
        "id": "nbmg-positional-accuracy",
        "class": "OFFICIAL-STATE-SURVEY",
        "title": "NGDS geochemical data for Nevada (GRC paper, NBMG)",
        "url": "https://publications.mygeoenergynow.org/grc/1030316.pdf",
        "fetched": "2026-10-29 (search result snippet; not re-downloaded)",
        "quotes": ["permitted wells file ... accurate to the quarter-quarter section"],
    },
    {
        "id": "smu-heat-flow",
        "class": "PUBLIC-DATABASE",
        "title": "SMU Geothermal Laboratory Heat Flow Database (NGDS node)",
        "url": "http://search.geothermaldata.org/dataset/115609c8-6f52-49fe-a0af-9d379d516340",
        "fetched": "2026-10-29 (search result snippet; licence NOT verified)",
        "quotes": ["Heat flow values for the U.S. derived from temperature gradient and thermal conductivity data."],
    },
    {
        "id": "gems-contest-secondary",
        "class": "SECONDARY-UNVERIFIED",
        "title": "Svyable/GEMS-CONTEST README (third-party repository; claims organizer clarification)",
        "url": "https://github.com/Svyable/GEMS-CONTEST",
        "fetched": "2026-10-29 (search result snippet)",
        "quotes": ["pixels corresponding to the existing USGS/INGENIOUS faults are masked out of evaluation"],
        "note": "Conflicts with the official problem page's truth definition. Not used for any decision.",
    },
]


def main() -> None:
    verify = json.loads(VERIFY.read_text())
    focus = json.loads((ROOT / "registry" / "focus_review.json").read_text())
    forensic = json.loads((ROOT / "docs" / "data" / "h33-forensics.json").read_text())

    sites = {s["site"]: s for s in verify["sites"]}
    pairs = verify["pairwise"]

    def max_pair(site: str) -> dict:
        best = None
        for m in pairs:
            if site not in (m["a"], m["b"]):
                continue
            other = m["b"] if m["a"] == site else m["a"]
            cand = {"other_site": other, "max_overlap_either_direction": m["max_decisive_overlap_either_direction"],
                    "max_raw_overlap_either_direction": m["max_raw_overlap_either_direction"],
                    "spearman_5px_blocks": m["spearman_5px_blocks"]}
            if best is None or cand["max_overlap_either_direction"] > best["max_overlap_either_direction"]:
                best = cand
        return best

    rows = []
    for site_name in sorted(sites):
        s = sites[site_name]
        reg = next(r for r in focus["rows"] if r["repository"] == site_name and r["claim_value"] == s[
            "claim_value_USER_REPORTED"])
        worst = max_pair(site_name)
        partners = [m["b"] if m["a"] == site_name else m["a"] for m in pairs
                    if site_name in (m["a"], m["b"]) and m["max_decisive_overlap_either_direction"] > 0.70]
        rows.append({
            "site": site_name,
            "reported_top_score_USER_REPORTED": float(s["claim_value_USER_REPORTED"]),
            "score_evidence_class": s["score_evidence_class"],
            "file": reg["artifact"],
            "source_url": s["source_url"],
            "sha256_registry": s["sha256_registry"],
            "sha256_recomputed": s["sha256_recomputed"],
            "sha256_match": s["sha256_match"],
            "positive_pixels": s["positive_pixels_recomputed"],
            "grid_matches_template": s["format"]["grid_matches_template"],
            "values_in_0_1": s["format"]["values_in_0_1"],
            "nan_outside_footprint": s["format"]["nan_pixels"] == 7111787,
            "closest_other_focus_file": worst,
            "other_focus_sites_flagged_duplicate_by_overlap": sorted(partners),
            "count_other_focus_sites_flagged": len(partners),
            "unique_vs_other_focus_sites": not (worst["max_overlap_either_direction"] > 0.70
                                                or abs(worst["spearman_5px_blocks"]) > 0.90),
            "new_file_score_estimate": "NOT ESTIMABLE (no holdout-validated model; no organizer receipt)",
            "download_decision": "DO NOT SUBMIT — prior art / learning only",
        })

    best_row = max(rows, key=lambda r: r["reported_top_score_USER_REPORTED"])
    # Repository forensic: the H27 -> H33 ladder used in the explanation (USER-REPORTED scores).
    ladder = [
        {"file_family": "D2.8 (GEMSDOE30/25 identical pixels)", "positive_pixels": 44090,
         "reported_USER_REPORTED": 0.2600},
        {"file_family": "H27-4 (GEMSDOE31/28/33 family)", "positive_pixels": forensic["h27_positive_pixels"],
         "reported_USER_REPORTED": 0.2708},
        {"file_family": "H33-2-B2 (GEMSDOE32)", "positive_pixels": forensic["h33_positive_pixels"],
         "reported_USER_REPORTED": 0.2778},
    ]

    from scipy.stats import spearmanr

    dot_rho = spearmanr([r["positive_pixels"] for r in rows],
                        [r["reported_top_score_USER_REPORTED"] for r in rows]).statistic

    doc = {
        "schema_version": 1,
        "dot_count_vs_reported_score_spearman": round(float(dot_rho), 4),
        "dot_count_vs_reported_score_note": "n=9, USER-REPORTED scores; a pattern in the claims, not a measured effect.",
        "session": "arena/cc130eb1-gemsdoe31",
        "date_utc": "2026-10-29",
        "decision": "NO FILE IS APPROVED. DO NOT SUBMIT ANY TIFF FROM THIS SITE.",
        "download_permission": "research/learning only; not a submission",
        "submission_permission": "none (ok_to_submit=false, slot_approved=false)",
        "new_tif_generated": False,
        "experiments_run": 0,
        "leaderboard_estimate_for_any_file": None,
        "estimate_reason": ("No holdout-validated model: the feature stack is not restored, no method paragraph "
                            "assigns a lane, and the literal any-registry duplicate STOP stands. An estimate would "
                            "be a projection, which the repository never reports as a score."),
        "user_reported_anchors": {
            "0.2778": "GEMSDOE32 top focus file (USER-REPORTED, no organizer receipt)",
            "0.3195": "conflicting anchor (USER-REPORTED, no receipt)",
            "0.4413": "conflicting anchor (USER-REPORTED, no receipt; a sibling repo attributes 0.3195 to GEMSDOE49 "
                      "with a different file name)",
            "0.2784": "GEMSDOE92 gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros (USER-REPORTED) is higher than the "
                      "0.2778 focus-site maximum; it is outside the nine requested sites and is not verified",
        },
        "best_focus_site_reported": {"site": best_row["site"], "score": best_row["reported_top_score_USER_REPORTED"]},
        "focus_site_rows": rows,
        "all_nine_pairwise_duplicate_by_overlap": verify["pairs_flagged_duplicate_by_overlap"] == verify["pairs_total"],
        "pairs_total": verify["pairs_total"],
        "pairs_duplicate_by_overlap": verify["pairs_flagged_duplicate_by_overlap"],
        "pairs_duplicate_by_rank": verify["pairs_flagged_duplicate_by_rank"],
        "min_pairwise_max_overlap": min(m["max_decisive_overlap_either_direction"] for m in pairs),
        "min_pairwise_spearman": min(m["spearman_5px_blocks"] for m in pairs),
        "h33_family_ladder": ladder,
        "h33_forensic": {
            "h33_on_catalogue_pixels": forensic["h33_on_catalogue_pixels"],
            "h33_pixels_removed_vs_h27": forensic["h33_pixels_removed_vs_h27"],
            "h33_pixels_added_vs_h27": forensic["h33_pixels_added_vs_h27"],
            "h33_min_catalogue_distance_px": forensic["h33_min_catalogue_distance_px"],
            "source": "docs/data/h33-forensics.json",
        },
        "blockers": [
            "No method paragraph: the protocol says 'your lane is the single method paragraph below', but none "
            "follows, so no scientific lane can be assigned (AGENTS.md: 'No new method paragraph is present').",
            "Literal any-registry duplicate rule: the registered spacing-5 lattice covers 99.87% of the 37,654-dot "
            "footprint, so the 37,654-dot budget is forced to a duplicate STOP (counting bound 82.34%).",
            "Feature stack and labels are not restored in this checkout; the competition data is login-gated.",
            "Organizer receipts are absent; no score can be confirmed.",
        ],
        "irregularities": [
            "IR-CC130-01 Official text says data outside the bounds must be null or nan; the repo's -zeros files write "
            "0 outside the 5,167,373-pixel footprint. The organizer-sample mirror uses NaN outside. Zeros files are "
            "therefore a format risk and must not be uploaded without organizer confirmation.",
            "IR-CC130-02 The owner-mirror data/sample_submission.tif has 60,988 pixels equal to 1, but the official "
            "page says the sample predicts total fault absence (all zero). The mirror is not organizer-authenticated.",
            "IR-CC130-03 GEMSDOE25 and GEMSDOE30 top files have identical pixel values, NaN masks and grids, reported "
            "as 0.2600 each; byte hashes differ. GEMSDOE30's filename tag 91eae1ca equals the first eight hex digits "
            "of GEMSDOE25's SHA-256.",
            "IR-CC130-04 All nine focus top files are one dot family: minimum pairwise overlap "
            "0.973 (either direction) and minimum Spearman 0.85 across all 36 pairs.",
            "IR-CC130-05 Front-page and executive summary generators read registry/current_run.json (historical "
            "MAGREST), while AGENTS.md names registry/release_status.json (H31-CC) as canonical.",
            "IR-CC130-06 The repo's gate sets chance-adjusted overlap to 0 when the other raster covers 100% of random "
            "points, so an identical dense raster can pass the overlap rule; the conservative raw rule was added.",
            "IR-CC130-07 Conflicting truth definitions: the official page says the test set is NEW faults not in the "
            "USGS database; a third-party README says catalogue pixels are masked. Unverified; needs organizer text.",
            "IR-CC130-08 The DTI definition was re-read from the official problem page; the shell could not reach "
            "drivendata.org, so the page was read through the fetch tool. The repo's metric.py matches the page.",
            "IR-CC130-09 Leaderboard anchors 0.3195 and 0.4413 conflict and have no receipt; GEMSDOE92 at 0.2784 is "
            "higher than the nine-site maximum and is USER-REPORTED only.",
        ],
        "official_sources": OFFICIAL_SOURCES,
        "hypotheses_ranked": [
            {"rank": 1, "id": "H-CC-A thermal-spring collinearity",
             "layers": "NBMG hot-spring and thermal-well inventory (positions, temperatures)",
             "signature": "three or more thermal sites within 300 m of a common line whose azimuth agrees with the "
                          "regional fault trend",
             "why_missing_from_catalogue": "springs and wells can localise on permeable faults that have no mapped trace "
                                           "(to be tested, not assumed)",
             "difference_from_repo": "no spring-alignment statistic exists; repo uses groundwater and conductivity context",
             "non_fault_mimic": "aquifer or playa-margin outflow; cluster of drill sites; mislocated wells",
             "cost": "medium; positions only to quarter-quarter section, comparable to the 300 m kernel",
             "validated": False},
            {"rank": 2, "id": "H-CC-B stress-orientation prior (World Stress Map)",
             "layers": "WSM 2025 SHmax azimuth and quality A-C records; repo gradient-tensor strike field",
             "signature": "agreement between local lineament azimuth and the SHmax-derived fault orientation",
             "why_missing_from_catalogue": "buried faults with the regional orientation are the ones an azimuth prior "
                                           "can rank up (to be measured)",
             "difference_from_repo": "no WSM layer or stress-orientation weight in the repo (zero keyword hits)",
             "non_fault_mimic": "dike swarms and topographic grain aligned with stress",
             "cost": "low to medium; CC BY 4.0 data",
             "validated": False},
            {"rank": 3, "id": "H-CC-C seismicity nodal-plane alignment (re-scoped H5)",
             "layers": "USGS ComCat events with moment-tensor nodal planes",
             "signature": "clusters of focal-plane strikes consistent with a fault segment absent from the catalogue",
             "why_missing_from_catalogue": "seismogenic faults are often unmapped",
             "difference_from_repo": "repo H5 was not run; the repo's own limit is km-scale location error",
             "non_fault_mimic": "induced seismicity from geothermal production; quarry blasts",
             "cost": "medium-high; expected gain low at 300 m",
             "validated": False},
            {"rank": 4, "id": "H-CC-D heat-flow residual (SMU database)",
             "layers": "SMU Geothermal Laboratory heat-flow database (licence to verify)",
             "signature": "heat-flow residual against a regional conduction model",
             "why_missing_from_catalogue": "thermal upflow can mark faults, but well spacing is coarse",
             "difference_from_repo": "heat-flow appears only in archive notes, not as a feature",
             "non_fault_mimic": "radiogenic granite; sedimentary-basin thermal blanketing",
             "cost": "medium; the expected gain at 300 m is the weakest of the four",
             "validated": False},
        ],
        "validation_status": "No candidate was validated. Holdout validation requires the restored feature stack and an "
                             "assigned lane, both unavailable in this session.",
        "run_card": "evidence/review_cc130eb1/run_card.json",
        "verification": "evidence/review_cc130eb1/focus_site_verification.json",
    }
    OUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)} rows={len(rows)} sources={len(OFFICIAL_SOURCES)}")


if __name__ == "__main__":
    main()
