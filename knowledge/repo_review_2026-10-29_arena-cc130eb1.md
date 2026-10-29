# Repository review, nine-site duplicate audit, and decision — 2026-10-29 (arena/cc130eb1-gemsdoe31)

**Decision: no file is cleared to submit. Do not upload any TIFF from this review.**
Download links below are for study and learning only. Nothing here is a leaderboard claim.

- No new TIFF was generated. No experiment was run (budget 0 of 3). No slot is approved (`ok_to_submit=false`, `slot_approved=false`).
- Scores quoted are **USER-REPORTED**. None has an organizer receipt, so none is ORGANIZER-CONFIRMED.
- Holdout DTI: **not run**. The feature stack is not restored and no method lane is assigned.
- Machine-readable register: `registry/session_cc130eb1_decision.json`. Run card: `evidence/review_cc130eb1/run_card.json`. Verification: `evidence/review_cc130eb1/focus_site_verification.json`.
- Hypotheses (ranked, all untested and blocked): `knowledge/hypotheses_2026-10-29_arena-cc130eb1.md`.
- AI-use statement (required by the official rules §3.2 for any submission narrative): this review was produced with an AI coding agent. Every number above was computed by a script and re-read from a file. Every official claim was checked against a fetched page and is quoted in the register with its URL. No claim was taken from memory.

## 1. Is it OK to download and submit a file?

**No, for all nine focus-site files and for every file in the repository.** The reasons are these:

1. The official rules allow one final submission per entity, with up to three scored submissions per week (rules §1.1 "a single entry"; §3.2; §3.4). Only one submission counts for both prize phases (§3.5).
2. Every focus-site file duplicates the other eight. The minimum pairwise overlap across all 36 pairs is 0.9731 (either direction, 3 px). The minimum Spearman rank correlation is 0.8498 (5 px blocks). The repository's own duplicate rule is overlap > 0.70 or rank > 0.90 (`src/gemsdoe31/gate.py`).
3. The literal registry rule still stands: no file is cleared, and the uniqueness gate fails for the current H31-CC file (see `registry/release_status.json`).
4. The official text requires data outside the bounds to be **null or nan**. The repository's `-zeros` variants write 0 outside the footprint. See IR-CC130-01.

## 2. Nine-site executive table

Verified from the GitHub files at the pinned commits. Each file's SHA-256 was re-computed and matches the registry. Each file has the same grid (EPSG:32611, 3730 × 3292, 100 m), values in [0, 1], and NaN outside the 5,167,373-pixel footprint (7,111,787 NaN pixels). Source: `registry/session_cc130eb1_decision.json`.

| Site | USER-REPORTED top score | File (study download only) | Positive pixels | SHA-256 match | Max overlap vs other focus files | Duplicates | Unique? | New-file estimate |
|---|---|---|---|---|---|---|---|---|
| GEMSDOE24 | 0.2477 | [gems24-h25-1-dotted-h19-5-d1-5-20261002-…](https://github.com/buffedlizard55-lab/GEMSDOE24/blob/544fe988df1b8a1b16f249a28be3fc3b3ff378a0/docs/downloads/gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif) | 60,069 | True | 1.0000 vs GEMSDOE25 | 8 of 8 | No | not estimable |
| GEMSDOE25 | 0.2600 | [gems25-dotted-h19-5-d2-8-20261002-e56ea3…](https://github.com/buffedlizard55-lab/GEMSDOE25/blob/2a279dd0d2a4319c1022567876eb4c97553e2d13/docs/downloads/gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif) | 44,090 | True | 1.0000 vs GEMSDOE24 | 8 of 8 | No | not estimable |
| GEMSDOE27 | 0.2449 | [gems27-topo-gap-closure-t-v2-on-d1-5-202…](https://github.com/buffedlizard55-lab/GEMSDOE27/blob/c79609503619559b5a2c53116e87fce646bc4235/docs/downloads/gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif) | 61,328 | True | 1.0000 vs GEMSDOE24 | 8 of 8 | No | not estimable |
| GEMSDOE28 | 0.2710 | [gems28-h36-1-rung30-blind-r1-20261003-b5…](https://github.com/buffedlizard55-lab/GEMSDOE28/blob/178c65378e1adaaabe45d944fd63b7cd284bff4f/docs/downloads/gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif) | 37,660 | True | 1.0000 vs GEMSDOE24 | 8 of 8 | No | not estimable |
| GEMSDOE30 | 0.2600 | [gemsdoe30-d28-poisson300m-offcat-44090-2…](https://github.com/buffedlizard55-lab/GEMSDOE30/blob/ccc5e4e35b76d2fbe66c25782d9a3c805d796dbb/docs/downloads/gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca-nanoutside.tif) | 44,090 | True | 1.0000 vs GEMSDOE24 | 8 of 8 | No | not estimable |
| GEMSDOE31 | 0.2708 | [gemsdoe31-h27-4-solo-d28-20261004-8acb75…](https://github.com/buffedlizard55-lab/GEMSDOE31/blob/4371416853904713760b86db0dccd9afe50d776f/docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif) | 40,199 | True | 1.0000 vs GEMSDOE24 | 8 of 8 | No | not estimable |
| GEMSDOE32 | 0.2778 | [gemsdoe32-h33-h33-2-b2-20261004T220000Z-…](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/9863c82a7c7dc283c615b711bab941debaff0ec4/docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-nan.tif) | 37,654 | True | 1.0000 vs GEMSDOE24 | 8 of 8 | No | not estimable |
| GEMSDOE33 | 0.2632 | [GEMSDOE33-h33d-analog-tip-stepover-r30-2…](https://github.com/buffedlizard55-lab/GEMSDOE33/blob/f618cc54773bd9b4d6c2b3ebf78103a05cc10cb6/docs/downloads/GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e-nanoutside.tif) | 41,865 | True | 0.9998 vs GEMSDOE32 | 8 of 8 | No | not estimable |
| GEMSDOE36 | 0.2750 | [gemsdoe36-anderson-geothermal-pinn-38854-2026…](https://github.com/buffedlizard55-lab/GEMSDOE36/blob/c9ad59ec6f969ed931d089a03044c1567a633e84/docs/downloads/gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-nan.tif) | 38,854 | True | 1.0000 vs GEMSDOE32 | 8 of 8 | No | not estimable |

Why "estimable" is "not estimable": no model was validated on a spatially blocked holdout, and organizer receipts are absent. Any number I wrote would be a projection presented as a score. The repository never does that.

Note on the 1.0000 entries: "vs GEMSDOE24" is one tied partner. Every site duplicates all eight others (column "Duplicates"). GEMSDOE25 and GEMSDOE30 are pixel-identical (IR-CC130-03).

## 3. Why did GEMSDOE32 (H33-2-B2, 0.2778) score highest, and can >0.2778 be reached?

**The 0.2778 value itself is unverified.** It is USER-REPORTED, and no organizer receipt exists in the repository. The rules also say that public-leaderboard scores may differ from the private ones (rules §3.2). So "highest" means "highest of the user-reported values".

### 3a. What the official metric rewards (verified against the fetched official page)

The official DTI is `DTI = TPw / (TPw + α·FPw + β·FN w + ε)`, with α = 0.2 and β = 0.8. Source: the DrivenData problem page, fetched 2026-10-29. The page also says that the test set is "newly identified faults … not included in the existing USGS fault database".

Consequences, all derived from that formula (INFERENCE where marked):
- **Recall is weighted four times precision.** A missed truth unit costs 0.8. A false-positive unit costs 0.2.
- **Dots on already-mapped faults earn no credit, unless a new fault lies within the 300-m kernel.** Under the stated test definition, such a dot is a false positive (cost ≈ 0.2 each). INFERENCE: this is the reason pruning can help.
- **Redundant dots are cheap to remove if their neighbours already cover the same truth.** INFERENCE: removing them lowers FPw with little loss of TPw.
- **The final round can reward new discoveries.** The problem page says experts add verified new faults to the label set after reviewing every team's submission, and "predictions that helped experts identify previously-unmapped faults can score higher here than in the Initial Prize Round". INFERENCE: the best public-leaderboard file and the best final-round file may differ. Choosing one final file blind to private scores (§3.5–§3.6.2) is therefore a robustness decision, not a public-score contest.

### 3b. What the repository's own record shows

From `docs/data/h33-forensics.json`:
- H33 (37,654 dots) = H27 (40,199 dots) with dots within 2 px of the public catalogue removed. It removed **2,545** dots and added **none**.
- H33 has **0** dots on the public catalogue. Its nearest dot is 2.236 px (≈224 m) from a catalogue pixel.
- H27 = D28 (44,090) pruned at 1 px.

The user-reported ladder is 0.2600 (44,090 dots) → 0.2708 (40,199) → 0.2778 (37,654), so each pruning step raised the reported score. Across all nine focus files, the Spearman rank correlation between dot count and reported score is **−0.983** (n = 9).

This is consistent with the mechanism in 3a. It is not proof. The repository has no measured truth set, so the pattern could also come from other differences between the files.

### 3c. Is >0.2778 achievable?

**Unknown, and nothing here shows it.** No file in this repository has a validated holdout DTI above 0.2778, and no candidate was built. Three things would be needed:
1. A method lane, and a restored feature stack, to validate on a spatially blocked holdout.
2. A duplicate-clean raster. The registered spacing-5 lattice covers 99.87% of the footprint within 3 px at 37,654 dots, so any raster at that density has at least 82.3% overlap with it. That is the STOP.
3. An organizer receipt, which can only come from a submission.

The mechanism in 3a points to two untested directions. The first is catalogue-aware pruning with a continuous (calibrated-probability) output, rather than binary dots. The second is a precision model for dots that are likely not new faults. Both are hypotheses only. They are ranked in `knowledge/hypotheses_2026-10-29_arena-cc130eb1.md`.

### 3d. Conflicting leaderboard anchors

- **0.4413** and **0.3195** are cited by the user and appear in third-party repositories. Neither has a receipt in this repository or in the README. A sibling repo attributes 0.3195 to a different site (GEMSDOE49) with a different file name, which is a conflict (IR-CC130-09).
- The register records 0.4413 and 0.3195 as USER-REPORTED anchors, unverified.
- **GEMSDOE92 at 0.2784** (USER-REPORTED, in a third-party file) is higher than the nine-site maximum. It is outside the nine requested sites and is not verified.

## 4. Official facts used (fetched 2026-10-29)

| Fact | Source |
|---|---|
| Single GeoTIFF, single float32 layer, 100 m, values 0–1, outside bounds null or nan, EPSG:32611 | [DrivenData problem page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) |
| DTI formula and α = 0.2, β = 0.8 | same page |
| Test set = new faults not in the USGS database | same page |
| Single entry; three submissions per week; public vs private scores can differ; generative-AI disclosure required | [GEMS Prize Official Rules (NLR), §1.1, §3.2](https://docs.nlr.gov/docs/fy26osti/96647.pdf) |
| Labels: USGS Quaternary Fault and Fold Database plus newly identified faults | same rules, §2 |
| Metric: distance-weighted Tversky with triangular kernel, R = 300 m, α = 0.2, β = 0.8; TP over truth, FP over predictions, FN over truth | same page, "Performance metric" and "Mathematical representation" |
| External data allowed only if licensed for use in the challenge and shareable with the sponsor for evaluation | same page, "External datasets" |
| The GeoDAWN region is split into a public and a private test set; Final round re-scores on the expanded label set, which adds verified new faults | same page, "Competition structure" |
| Reference solution uses alpha 0.2 and beta 0.8 in its Tversky training loss | [reference solution](https://github.com/drivendataorg/gems-prize-reference-solution) |
| Up to three submissions per week for scoring; exactly one final submission chosen before the deadline, without knowledge of private-set scores; public-leaderboard score covers the public test subset only (§3.4–§3.6.2) | same PDF |
| Phase 1 uses a privately withheld subset of the new fault dataset; Phase 2 re-scores on the full revised set (§1, §1.1) | same PDF |
| Training labels come from the INGENIOUS Great Basin Regional Dataset Compilation, DOI 10.15121/1881483 (§3.3, footnote 4) | same PDF; [DOI](https://doi.org/10.15121/1881483) |
| Calendar deadlines are not in the text; they are at gems.drivendata.org (§1.2). Deadline is 5:00 p.m. ET (Appendix A.1). Eligibility requirements apply (§1.3). | same PDF |

Quotations and their normalisation are in `registry/session_cc130eb1_decision.json` (`official_sources`).

## 5. Irregularities (flagged, not resolved)

- **IR-CC130-01 (format risk).** Official text: "data outside the bounds is null or nan". The repo's `-zeros` files write 0 outside the 5,167,373-pixel footprint. The organizer sample mirror (below) uses NaN outside. Zeros files must not be uploaded without organizer confirmation.
- **IR-CC130-02 (sample mismatch).** The owner-mirror `data/sample_submission.tif` has 60,988 pixels equal to 1. The official page says the sample "predicts total fault absence". The mirror is not organizer-authenticated, so either the mirror or the description is wrong.
- **IR-CC130-03 (duplicate bytes).** GEMSDOE25 and GEMSDOE30 have identical pixel values, NaN masks and grids (reported 0.2600 each). Their bytes differ. GEMSDOE30's filename tag `91eae1ca` is the first 8 hex digits of GEMSDOE25's SHA-256.
- **IR-CC130-04 (one dot family).** All nine focus top files duplicate each other (minimum pairwise overlap 0.9731).
- **IR-CC130-05 (wrong front door).** The site generator reads `registry/current_run.json` (historical MAGREST), while AGENTS.md names `registry/release_status.json` (H31-CC) as canonical.
- **IR-CC130-06 (gate quirk).** `gate.py` sets chance-adjusted overlap to 0 when the other raster covers every random point. An identical dense raster can therefore pass the chance-adjusted rule. The verifier adds a conservative raw-overlap flag (`duplicate_by_raw_overlap_conservative`). The gate was not changed.
- **IR-CC130-07 (truth definition).** The official page says the test set is new faults. A third-party README says catalogue pixels are "masked out of evaluation". Both cannot be true for the same truth set. Unverified, and it matters for 3a. Needs organizer text.
- **IR-CC130-08 (access).** The shell cannot reach drivendata.org or most data hosts. The problem page and rules were read with the fetch tool. The repo's `src/gemsdoe31/metric.py` matches the page's definitions (kernel max(1 − d/R, 0), R = 300 m, α = 0.2, β = 0.8, DTI form). The page's worked example gives TP 3.00, FP 1.89, FN 2.00, which yields 0.6027 (displayed as 0.60). That is a formula check only; the example raster is an image and was not reproduced.
- **IR-CC130-09 (leaderboard anchors).** 0.3195 and 0.4413 conflict, and neither has a receipt. GEMSDOE92 (0.2784) is higher than the nine-site maximum (USER-REPORTED).
- **Earlier open issues from the repo.** GEMSDOE27 is 0.2250 in `focus_unique_2026.json` and 0.2449 in `focus_review.json`. This conflict is unresolved; it needs the registry bytes, which were not read this session.

## 6. Limitations and needed access

| Needed | Why | Status |
|---|---|---|
| Organizer text on truth definition (catalogue masking?) | decides whether pruning catalogue dots helps (IR-CC130-07) | not available |
| Organizer-authenticated sample submission | resolves IR-CC130-02 and the NaN convention | not available |
| Restored feature stack and labels (login-gated data tab; owner mirror) | prerequisite for any holdout DTI | not restored in this session; restore needs owner authorization under the current STOP |
| A written method paragraph and assigned lane | required before any experiment | missing |
| Organizer receipt for any submission | only source of a leaderboard score | none; no submission made |
| Licences permitting use in the challenge and sharing with the sponsor (problem page, "External datasets") for every external source | WSM is CC BY 4.0 (permits sharing, not yet checked against the challenge terms); NBMG, SMU and INGENIOUS are unchecked | not verified |
| Eligibility confirmation by the registered competitor (rules §1.3) | a precondition for any prize; not verified here | not verified; not claimed |
| Calendar deadlines (gems.drivendata.org, rules §1.2) | not in the fetched text | not verified |
| Live leaderboard | not scraped by policy; static official link only | not used |

Not claimed: any score, any uniqueness pass, any rank, any slot approval.

## 7. Free official data sources (for the hypotheses; links verified by search, licence stated where checked)

- World Stress Map Database Release 2025 (GFZ Data Services, DOI 10.5880/WSM.2025.001, CC BY 4.0, 100,842 records): https://dataservices.gfz-potsdam.de/wsm/showshort.php?id=a23de1c9-1f73-11f0-914a-f12b0080820d
- Nevada Bureau of Mines and Geology geothermal site descriptions (named hot springs and thermal wells): https://nbmg.unr.edu/geothermal/sitedescriptions.html
- NBMG cadastral positions for permitted wells are accurate to the quarter-quarter section (from the NGDS paper): https://publications.mygeoenergynow.org/grc/1030316.pdf
- SMU Geothermal Laboratory heat-flow database (NGDS node; licence not verified): http://search.geothermaldata.org/dataset/115609c8-6f52-49fe-a0af-9d379d516340
- USGS ComCat earthquake API (free; the repo's H5 note says epicentre error is km-scale, not re-measured here): https://earthquake.usgs.gov/fdsnws/event/1/

## 8. Verification log (this session)

| Check | Result |
|---|---|
| `scripts/verify_focus_sites.py` | exit 0; 9 sites; 36 pairs; all SHA-256 match; grid and [0,1] range pass |
| `tests/test_focus_sites.py` | 3 passed |
| `scripts/build_session_register.py` | wrote the register from the verified JSON |
| `scripts/build_site.py` then `scripts/check_site.py` | build exit 0; check passed (22 pages, budget 22) |
| pre-restore pytest | rewrote the H31-AA receipt; reverted with git checkout before the restore check |
| `verify_current_run --restore-small-inputs`, `verify_protocol_review`, `verify_h31cc_run --check`, `build_release_status --check`, `verify_h31j`, `verify_h31t`, `verify_h31aa_run --check` | all passed (see the status note) |
| full pytest, ruff, compileall, `check_metric.py`, `check_marginal_dti.py` | see the status note |

## 9. Remaining work

1. Read `registry/focus_unique_2026.json`, `registry/review_passes.json` (partly read), `registry/submissions.json`, `registry/user_reported_scores.json` and the three latest `knowledge/*.md` files, to settle the GEMSDOE27 conflict.
2. Obtain organizer text on the truth definition (IR-CC130-07) and the sample file (IR-CC130-02).
3. Decide with the owner whether the data restore is authorized. That is the only route to any holdout DTI.
4. Write a method paragraph and assign one lane before any experiment.
5. Resolve the zeros versus NaN format convention (IR-CC130-01) with the organizer before any upload.
6. Fix the front-door source mismatch (IR-CC130-05) in `scripts/build_site.py`.
