# GEMSDOE31 repository review — 2026-10-26

## Executive decision

**No new model fit, experiment, raster, upload, or submission slot was authorized or created.** The current MAGREST lane remains closed by its recorded three-experiment limit and the literal duplicate STOP; the prescribed method paragraph for a fresh lane is still absent. The existing MAGREST raster is **OK TO DOWNLOAD FOR RESEARCH ONLY — DO NOT SUBMIT**. A unique, competition-ready TIFF cannot be responsibly produced under the current lane/registry rules.

The executive summary now includes a generated nine-site prior-art matrix. It selects the highest score claim supplied for each requested site, links to the hash-pinned owner-mirror artifact, labels every value USER-REPORTED, and explicitly says none is upload-approved. This is an audit aid, not an authenticated current leaderboard.

## What the H33-2-B2 result does and does not establish

The supplied claim for GEMSDOE32 `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` is **USER-REPORTED: 0.2778; no organizer receipt is present**. The other prompt anchors `0.3195` and `0.4413` are also user-supplied and unverified here. They must not be treated as current official rankings or as comparable targets.

The pinned owner-mirror raster audit in `evidence/h33_forensics_20261025.json` measures 37,654 positive cells in H33-2-B2, exactly equal to H27-4 after removing 2,545 H27 cells in the 1–2 pixel catalogue-flank band. H27 itself is D2.8 pruned at the 1-pixel threshold. This is a reproducible support-geometry relationship, not evidence that H33 added a fault detector or geological information.

A plausible metric mechanism is that separated dots use the finite false-positive budget more efficiently than a thick ridge: deleting low-yield predictions near the known-catalogue halo may reduce false-positive mass while preserving much of the candidate support farther from the catalogue. This is an **INFERENCE**, not a causal attribution. The private competition truth is unavailable, and removed near-catalogue dots could still receive kernel credit from hidden nearby faults. Therefore the local byte comparison cannot prove why the reported score occurred.

**Can a new, unique raster be said to beat 0.2778? No.** No organizer-confirmed result or same-instrument comparison establishes that. Current MAGREST evidence is **HOLDOUT-DTI**, evaluator `gems57-pooled-hide-v2`, 2,901 withheld positives: `0.052972044857535226`, 95% CI `[0.04131136300815562, 0.06532899139157548]`. Its paired difference versus the same-run physical HGB control is **HOLDOUT-DTI** under that evaluator and the same 2,901 withheld positives: `+0.00467843602723389`, 95% CI `[-0.017864202465723577, +0.022933167391729445]`. This experiment failed its preregistered paired screen because the interval includes zero. A local holdout value is not a competition score or a projection.

## Highest listed artifact per requested site

Every listed score below is **USER-REPORTED / no organizer receipt**, not ORGANIZER-CONFIRMED. The artifact links in the executive summary are pinned commit URLs into owner-maintained mirrors, and the hashes are byte hashes of those mirror files. “Highest” means highest claim in the supplied list/audit for that repository, not a fresh leaderboard lookup.

| Site | Highest listed artifact | Claimed score | Evidence-based interpretation / caution |
|---|---|---:|---|
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5-20261002-989f59505db1` | USER-REPORTED 0.2477 | Sparse H19-5 D1.5 emission. Its positive support has 88.5% of dots within 3 px of H33; prior art, not a unique new submission. |
| GEMSDOE25 | `dotted-h19-5-d2-8-20261002-e56ea318af89` | USER-REPORTED 0.2600 | D2.8 sparse emission. The two pinned artifact byte hashes differ; this review makes no pixel-identity claim with other sites. H33-family overlap remains high. |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1` | USER-REPORTED 0.2449 | Owner-described topological gap-closure on D1.5; not refitted in this session. 86.7% within 3 px of H33. |
| GEMSDOE28 | `h36-1-rung30-blind-r1-20261003-b531dae0a36f` | USER-REPORTED 0.2710 | Highest supplied claim for site 28. Near-identical budget to H33, but 95.5% within 3 px of H33; overlap, not independent novelty. |
| GEMSDOE30 | `d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca` | USER-REPORTED 0.2600 | D2.8 replay/spacing variation, not evidence of an independent detector. 88.2% within 3 px of H33. |
| GEMSDOE31 | `h27-4-solo-d28-20261004-8acb75e1` | USER-REPORTED 0.2708 | H27/D2.8 prior reference. Irregularity: the pinned owner-page record marks the corresponding artifact unscored; exact score-to-bytes organizer attribution is unresolved. 95.4% within 3 px of H33. |
| GEMSDOE32 | `h33-h33-2-b2-20261004T220000Z-e5eb6e7e` | USER-REPORTED 0.2778 | Highest listed claim in the nine-site set. Exactly the D2.8 support pruned at the 2-pixel catalogue threshold; not a new detector and 100% self-overlap with the registered file. |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30-20261004-cb490425926e` | USER-REPORTED 0.2632 | Owner-described analogue-tip/stepover strategy; independent transfer is not established by the available evidence. 92.6% within 3 px of H33. |
| GEMSDOE36 | `anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6` | USER-REPORTED 0.2750 | Owner-described Anderson/orientation-constrained model. Existing audit describes it as H33 support plus 1,200 GDR thermal/step-over predictions; the score attribution remains unverified. 97.4% within 3 px of H33. |

The 3-pixel fractions above are computed against the pinned GEMSDOE32 H33 owner-mirror raster, not a proof of exhaustive global uniqueness. Each exceeds the owner's 70% duplicate threshold for that particular prior. These nine artifacts are therefore useful comparison points only; none meets the requested “unique, not a duplicate” standard.

## Stop gate and current TIFF

`evidence/tgj31/registry_universal_blocker.json` records one registered full-footprint positive-support witness: 5,167,373 of 5,167,373 allowed cells covered within 3 pixels. Under the active literal forward overlap definition (`candidate dot within 3 px of any prior positive`), any nonempty in-footprint dot set has 100% overlap against this witness and fails the 70% limit. The broader scan is explicitly not exhaustive, but one witness suffices to fail this gate. No dense/calibration exemption is authorized.

The already-generated MAGREST all-finite TIFF remains `docs/downloads/gemsdoe31-magrest-concordant-37654-20261025-2c800a59ff-zeros.tif`, SHA-256 `c101ceb7237df0890a0f650b4211cc501250b47c1ab9cfeca8ee4cb373eb48d9`. Its local validator records one float32 band, EPSG:32611, shape 3730×3292, transform `[100,0,243350,0,-100,4508550]`, footprint values finite in `[0,1]`, and zero outside. Those checks establish local format compatibility with the pinned mirror, not organizer acceptance. Its run card says `verdict=negative`, `ok_to_download_for_research=true`, `ok_to_submit=false`, `slot_approved=false`.

No new TIFF was emitted by this review. Do not rename this research TIFF or any prior artifact into a purported unique submission.

## Desk hypothesis ranking for a future authorized lane

These are 4 hypotheses not identified as implemented in the reviewed GEMSDOE31 source tree; that is a repo-local finding, not global novelty. No expected DTI effect is numerically estimable from available evidence, so the ordering below is a qualitative ranking of plausible discovery value against implementation/data cost, not a score projection. They are unfit proposals and cannot be run inside the closed lane. The absent assigned method paragraph must be resolved before selecting any one.

| Rank | Candidate / specific layers | Physical signature and why it may find missing faults | How it differs from reviewed code | Non-fault mimic | Cost / expected DTI |
|---|---|---|---|---|---|
| 1 | **Acquisition-seam-aware magnetic persistence** — RTP (`rtp`), magnetic anomaly (`mag_anom`), optionally upward-continued TMI. | Directional spectral anisotropy plus edge/lineament persistence across scale; tests whether a fault-related edge continues across likely leveling/flight-line seams rather than rewarding every linear artifact. Could reveal boundaries suppressed by acquisition corrections. | Existing magnetic gradients/tilt/Euler and MAGREST's local displaced-texture restoration do not explicitly fit an acquisition-seam null and cross-scale persistence test. | Volcanic/lithologic contact, residual leveling seam, or real structures aligned with flight lines. | Medium, since mirrored bands exist but flight-line metadata are not pinned. Expected DTI change: **unknown**. |
| 2 | **Multiscale gravity–magnetic edge-transfer coherence** — RTP (`rtp`), isostatic gravity (`iso_grav_anom` and slope), basement-depth surface. | Match edge position, polarity, tangent, and termination across scales/fields; look for consistent lateral edge offsets rather than amplitude co-location. Buried structures may juxtapose magnetic and density units where no topographic scarp exists. | Existing combinations largely use scalar fusion/unions or local patch restoration; this is an edge-displacement/termination test with explicit cross-field geometry. | Pluton margin or basin-fill/lithologic boundary shared by fields. | Medium-high; production input stack/cache is absent in this clean review checkout. Expected DTI change: **unknown**. |
| 3 | **Piedmont drainage-deflection asymmetry** — high-resolution 3DEP DEM-derived channel network plus 100 m `det_elev` context. | Blind-corridor lateral channel/tributary deflection or paired incision asymmetry conditioned on regional slope and fan direction; potentially captures displacement without a preserved scarp. | Current LiDAR modules quantify local scarp, relief and slope; this tests network-scale channel geometry. | Avulsion, fan-lobe switching, lithologic permeability, irrigation or human diversion. | High and not data-ready: the exact official free source required is [USGS 3DEP / The National Map](https://www.usgs.gov/3d-elevation-program). Exact in-footprint product and endpoint availability were not checked in this run; do not call it viable until tiles/metadata are obtained and hash-pinned. Expected DTI change: **unknown**. |
| 4 | **Radiometric channel edge displacement** — GeoDAWN K, Th, U and total-count bands with RTP context. | Seek repeatable but laterally displaced K/Th/U boundaries across channels/scales rather than ratio extrema; could flag compositional boundaries associated with unmapped structures. | Earlier radiometric contrast/alteration ranks do not test channel-wise edge geometry and signed offset consistency. | Alluvial provenance, weathering, volcanic unit margin, or acquisition seam. | Medium; mirrored bands exist but are quantized and coverage-limited. Expected DTI change: **unknown**. |

A future candidate would have to preregister its one method paragraph, data hashes, blocked hide-and-recover holdout, visible-only catalogue-derived features, pixel-exact masking, single-feature leakage canaries, same-instrument incumbent, pooled DTI with CI, explicit mimic/null, pre-placement and final uniqueness tests, and fresh confirmation. The shared full-support witness currently makes the literal 70% uniqueness gate impossible for any nonempty in-footprint candidate; none of these proposals can be validated for slot selection until that conflict is resolved by an explicit protocol owner decision. No source page outside the permitted host allowlist was freshly fetched for this review; the official source URL above is supplied for review, not claimed as newly verified retrieval.

## Three review passes and commands actually run

1. **Implementation / task pass:** read the recurring README charter, AGENTS, current run, review-pass register, MAGREST preregistration, current status and prior follow-up. Confirmed the lane STOP and experiment limit. Added the nine-site prior-art matrix to the generated executive summary without altering data, predictions, evaluation tools or TIFFs.
2. **Bug / assumption pass:** added regression tests to ensure all nine sites are present, highest claim is sourced and user-reported, and H33 overlap / no-upload cautions remain visible. The current checkout initially lacked Python scientific/test dependencies; installed the repository-pinned requirements into ignored `.venv`. The first plain test run had 110 passed and 6 expected skips until exact small-input restoration; `verify_current_run.py --restore-small-inputs` returned `ok_to_download_for_research=true`, `ok_to_submit=false`, `verdict=negative`, and the existing TIFF hash. After restoring the inputs, all 118 tests passed. The review also caught and removed an unsupported exact-byte-identity note between the GEMSDOE25 and GEMSDOE24 rows: their recorded TIFF SHA-256 values differ, so the site now explicitly makes no cross-site pixel-identity claim. `ruff check .` passed. `check_metric.py` reported maximum fast/brute DTI difference `4.441e-16`, 24 grids, and 29 kernel offsets.
3. **Whole-request / delivery pass:** `collect_evidence.py`, `build_site.py`, and `check_site.py` completed; generated output had 21 pages and 364 local links. The tracker detected 124 artifacts and 10 submission records. `collect_evidence.py` temporarily removed an ignored, unavailable `.npy` artifact from the regenerated experiment index; that unrelated generated churn and the verifier's timestamp-only readiness update were restored, leaving no unintended registry/data-result changes. The new executive summary table links to the existing pinned mirror records. It does not assert official score, exact current leaderboard ranking, organizer acceptance, or approval to submit.

## Limitations and next work

- The assigned single-method paragraph is not present in the owner prompt; the current protocol has no valid method assignment for a fresh experiment.
- The current active lane is exhausted/stopped. Resolve the universal dense-witness degeneracy only through an explicit protocol/selector owner decision; do not add a private exemption or bypass the literal threshold.
- Reproduce the strongest comparable incumbent with the unchanged shared evaluator and same holdout instrument before opening a new lane.
- Restore the complete pinned production cache/inputs and recover/verify registry raster paths; current broad registry scan is not exhaustive.
- Obtain organizer-authenticated sample/template and actual submission/score receipt via authorized access. No credentials were sought or stored; no leaderboard polling or upload was performed.
- The scientific proxies are not private competition truth and do not establish geothermal vents. Scores cannot be projected from local HOLDOUT-DTI.

## Sources / evidence index

- Competition rules and overview links, for review only: `registry/sources.json` and `docs/sources.html`.
- Nine-site pinned artifact claims, hashes, method notes and H33 overlap: `registry/focus_review.json`.
- Byte geometry of H27/H33: `evidence/h33_forensics_20261025.json`.
- User score claims and conflicts: `registry/score_claims.json`, `registry/irregularities.json`.
- Current negative run: `registry/current_run.json`, `evidence/magrest/run_card.json`, `evidence/tgj31/registry_universal_blocker.json`.
- Existing ranked desk hypotheses and their access limitations: `knowledge/repo_review_2026-10-25_arena_followup.md`.


## Independent verification continuation — 2026-10-26

This continuation re-ran the checks from `AGENTS.md` in a clean checkout after installing the pinned `requirements.txt` into ignored `.venv`. It did not change code, fit a model, create or modify a submission raster, inspect the DrivenData leaderboard, or use a slot.

- `python -m pytest -q`: **118 passed** after the exact-input verifier restored the two small pinned inputs; there were no remaining skips. The pre-restore run was 112 passed / 6 expected skips.
- `python -m ruff check .`: passed.
- `python scripts/check_metric.py`: maximum fast/brute pooled-DTI absolute difference **4.441e-16** across 24 grids; exact cases passed; 29 kernel offsets are inside the 300 m radius.
- `python scripts/verify_current_run.py --restore-small-inputs`: returned `verdict=negative`, `ok_to_download_for_research=true`, `ok_to_submit=false`; unchanged MAGREST all-finite raster SHA-256 `c101ceb7237df0890a0f650b4211cc501250b47c1ab9cfeca8ee4cb373eb48d9`.
- `python scripts/collect_evidence.py`, `build_site.py`, and `check_site.py`: reported 124 experiment artifacts, 10 submission records, and a passing generated site with 21 pages and 364 local links. The collector's unrelated generated changes to readiness/experiment registers were restored; they are not review findings.

The independent rerun confirms the prior decision, not the scientific validity of a competition score: no new TIFF is approved to submit. The all-finite research raster remains explicitly **OK TO DOWNLOAD FOR RESEARCH ONLY — DO NOT SUBMIT**. The lane still fails the literal 70% duplicate test against a registered full-footprint witness (100% forward overlap), the three-experiment cap is exhausted, and no newly assigned method paragraph is present. No user-reported leaderboard number was accessed or upgraded to ORGANIZER-CONFIRMED.
