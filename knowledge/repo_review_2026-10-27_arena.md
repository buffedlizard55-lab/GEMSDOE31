# Repository review — 2026-10-27 (Arena session `arena/74acc325-gemsdoe31`)

## Decision first

**No TIFF is cleared to submit. No new TIFF, fit, submission-slot selection, upload, or leaderboard access was performed.** The protocol's required single-method paragraph is absent; the currently binding literal registry check stops a 37,654-dot candidate before placement (see the registered-lattice bound below). Inventing a new lane or writing a new GeoTIFF would contradict the parallel-run rules and would not make the artifact proven unique or high-scoring.

The existing site already exposes a prominent no-submit release status, a download-for-research-only TIFF, a manual-submission guide, and the requested nine-site comparison. The executive table is prior-art analysis, not a recommendation to upload those historical files. The output estimated score for every site/new candidate is **unavailable**: there is no validated cross-family estimate and no organizer receipt for the supplied scores.

## Nine-site executive summary

The figures are the highest relevant values present in the supplied history, classified **USER-REPORTED** (not `ORGANIZER-CONFIRMED`). The repository's pinned comparison marks the historical candidate fields as prior art, with >70% final-dot proximity to the H33 raster for the chosen records. That is not proof of uniqueness against every possible private or changed raster; it is sufficient to say these are not novel submissions. No score estimate for a new submission is validated.

| Site | Highest listed historical artifact | Listed result | Unique new submission? | New-entry score estimate | Action |
|---|---|---:|---|---|---|
| GEMSDOE24 | H25-1 dotted H19-5 D1.5 | 0.2477 — USER-REPORTED | No; prior-art field overlaps H33 above the configured stop | Unavailable | Do not resubmit |
| GEMSDOE25 | dotted H19-5 D2.8 | 0.2600 — USER-REPORTED | No; prior-art field overlaps H33 above the configured stop | Unavailable | Do not resubmit |
| GEMSDOE27 | topo-gap-closure T-v2 on D1.5 | 0.2449 — USER-REPORTED | No; prior-art field overlaps H33 above the configured stop | Unavailable | Do not resubmit |
| GEMSDOE28 | H36-1 rung30 blind R1 | 0.2710 — USER-REPORTED | No; prior-art field overlaps H33 above the configured stop | Unavailable | Do not resubmit |
| GEMSDOE30 | D28 Poisson300m offcat 44090 | 0.2600 — USER-REPORTED | No; D2.8 lineage / overlapping prior art | Unavailable | Do not resubmit |
| GEMSDOE31 | H27-4 solo D28 | 0.2708 — USER-REPORTED | No; historical reference, not a new submission | Unavailable | Do not resubmit |
| GEMSDOE32 | H33-2-B2 | 0.2778 — USER-REPORTED | No; existing reference raster, not a new submission | Unavailable | Do not resubmit |
| GEMSDOE33 | H33D analog tip-stepover R30 | 0.2632 — USER-REPORTED | No; prior-art field overlaps H33 above the configured stop | Unavailable | Do not resubmit |
| GEMSDOE36 | Anderson geothermal PINN 38854 | 0.2750 — USER-REPORTED | No; H33-family overlap in the pinned comparison | Unavailable | Do not resubmit |

Details, pinned artifact links, and the scope of the comparison are maintained at [`docs/executive-summary.html#focus-sites`](../docs/executive-summary.html#focus-sites) and [`registry/focus_review.json`](../registry/focus_review.json). The user-supplied 0.3195 and 0.4413 figures are inconsistent with the 0.2778 list as dated/attributed in the request and remain unverified; they are not used as a target or score estimate. This is a static site, not an automatically refreshed live leaderboard feed. Repository policy prohibits automated DrivenData monitoring/submission without prior written permission.

## Why H33-2-B2 may have been the strongest supplied result

**Observed geometry (from the pinned owner-mirror comparison, not an organizer receipt):** H33-2-B2 is a sparse D2.8 point field with a two-pixel known-catalogue-flank exclusion. It removes detections close to already catalogued faults rather than merely adding more pixels. That can improve a kernel-based Tversky score if the removed locations would otherwise contribute false-positive mass while enough true fault support remains elsewhere. The finite-radius kernel also makes redundant nearby predictions less valuable than coverage of new fault neighborhoods.

**Mechanistic plausibility, not established causality:** the D2.8 spacing and catalogue-flank pruning may trade some local recall for lower false-positive cost and less redundant support. No hidden competition truth or exact organizer receipt links the reported 0.2778 to these bytes in the evidence available here. Therefore we cannot prove why the private score was high, call 0.2778 an organizer-confirmed score, or promise to beat it. Pixel-set forensics describe the construction, not the hidden score's causal explanation.

For context, the repo's independently tested finite-change DTI algebra says an addition improves fixed-truth-count score only when its weighted true-positive gain exceeds its weighted false-positive cost. The 0.0588 figure shown in older documentation is an algebra illustration after substituting the **USER-REPORTED** 0.2778; it is not a measured DTI, score, or forecast. See [`scripts/check_marginal_dti.py`](../scripts/check_marginal_dti.py) and [`evidence/marginal_dti_audit_20261026.json`](../evidence/marginal_dti_audit_20261026.json).

## Ranked geological ideas — desk proposals only

These are candidate research questions, not newly assigned lanes, not claims of literature-wide novelty, and not numerical DTI forecasts. Local source review found no implementation of each *specific fitted operator* below; broader family novelty is not claimed. Every candidate is blocked from fitting until the method paragraph and registry rule are resolved. Ranking is qualitative expected value vs. implementation cost; all gains could be negative.

| Rank | Layers and physical signature | Why it may find unmapped faults | Difference from current implementations | Main non-fault mimic / validation concern | Expected benefit / cost |
|---:|---|---|---|---|---|
| 1 | B12 DEM and B13 isostatic gravity: fit local constant-elevation shoreline arcs, then measure residual from that shoreline null together with an independent cross-front gravity step | Buried range-front continuation may leave structural depth contrast even where no clear young surface scarp is preserved; explicit shoreline rejection could reduce a major geomorphic confound | H31-X detects slope-break geometry; this proposal tests whether a candidate line is better explained as an equipotential shoreline before accepting it, rather than just changing the slope threshold | Paleoshoreline/shoreline benches, tilted lake margins, lithologic contacts; controls must be elevation-matched, and horizontal real faults must not be automatically vetoed | Potential precision gain, unquantified / medium CPU |
| 2 | B2 RTP magnetic field and B13 gravity: segment paired contacts and estimate signed along-strike phase displacement, testing a reciprocal cross-field offset against an unbroken-contact null | A transverse concealed fault can offset basement contacts without a detectable surface scarp | MAGREST restores/compares magnetic texture and XFCOH tests edge coherence; this instead tests along-chain signed displacement and a specific no-offset null | Pluton margins, lithologic boundaries, flight-line/leveling seams; require reciprocal displacement and spatially held-out survey blocks | Potential specificity gain, lower confidence / high CPU |
| 3 | B12 DEM: paired drainage catchments across candidate traces; compare channel-steepness residuals conditional on drainage area and relief, requiring a cross-trace contrast stable to leave-one-channel-out checks | Differential uplift can affect drainage organization after direct scarps degrade, potentially exposing unmapped splays | Existing terrain/knickpoint descriptors are not a matched-catchment difference-in-differences test; this must be validated as a distinct operator, not a renamed curvature feature | Stream capture, alluvial avulsion, and rock-erodibility contrasts; 100 m resolution may limit channel-scale signal | Possible robustness gain, low confidence / high CPU |

The top-ranked hypothesis cannot be validated in this session: the required single-method paragraph is missing, no new lane authorization exists, and there is no `data/` or `.cache/` production feature stack in this checkout. The cached stack/evaluator/writer must be used unchanged once a lane is assigned. No new external layer is necessary for these desk candidates if the competition feature bundle is restored from the authorized competition data page; current credentials are not available here. No claim is made that any data host outside the allowed GitHub/PyPI hosts was checked or that the full current external dataset is downloadable without login.

## Hard duplicate preflight and submission decision

The current machine front door is [`registry/release_status.json`](../registry/release_status.json), with full reasoning in [`knowledge/2026-10-26_release_review_bf9d261d.md`](2026-10-26_release_review_bf9d261d.md). Its pinned spacing-5 lattice leaves 6,649 of 5,167,373 template-footprint cells outside a three-pixel halo. **COMPUTED counting bound, not a score:** with 37,654 distinct dots, at least 31,005 (82.3418%) must lie within that halo. The requested strict rule stops above 70%; therefore a candidate at that reference budget cannot pass the literal any-registry uniqueness condition even before feature placement. This bound is specific to that dot budget and does not assert that every possible nonempty raster is impossible.

Existing H31-X passes the local format/range/grid validation but fails the current literal registry gate; it is for research only. Re-encoding, changing the name, sampling points outside the scientific support, or copying a historical raster would not make a scientifically valid unique submission. **There is no file in this review that is OK to download and submit.** The current site clearly separates research download from upload permission.

## Three-pass repository review and verification

### Pass 1 — implementation/state audit

- Read the full README, including the preserved owner prompt; `AGENTS.md`; `registry/release_status.json`; the release/protocol reviews; `registry/current_run.json`; `registry/review_passes.json`; and the frozen MAGREST preregistration.
- Confirmed current branch `arena/74acc325-gemsdoe31`; no pre-existing working-tree changes at start.
- Confirmed the canonical release decision is negative, there is no assigned method paragraph, and all nine site scores on the summary are labelled USER-REPORTED. Existing README/site material preserves historical promotions; the top-of-page current decision and current machine release status explicitly supersede them.
- Restored only the two small ignored validation inputs through the repository verifier. Full `data/` production inputs and `.cache/` are absent; no fit or TIFF generation was attempted.

### Pass 2 — bugs, assumptions, and edge review

- Initial test attempt exposed two environment/input failures: `pytest` was initially absent from system Python, then H31-J/H31-S integration tests failed because `data/sample_submission.tif` and `data/labels.tif` had not been restored. Created ignored `.venv/`, installed pinned dependencies, and restored the two small inputs using `scripts/verify_current_run.py --restore-small-inputs`; this was a test-environment repair, not a data experiment.
- Rechecked decision artifacts after restoration: `scripts/build_release_status.py --check` confirms `verdict=negative`, `ok_to_submit=false`, and the strict duplicate bound. `scripts/verify_current_run.py --restore-small-inputs` returned `ok_to_download_for_research=true`, `ok_to_submit=false`, `verdict=negative` for the historical MAGREST artifact.
- Confirmed no leaderboard retrieval, organizer contact, weekly cap check, or submission was performed. Official non-GitHub websites cannot be freshly checked from this network allowlist; their stored links remain for manual review. Current source/page claims are not promoted to freshly verified facts.
- `scripts/collect_evidence.py` and site generation changed only the generated timestamp in `docs/downloads/readiness.json`; this incidental timestamp-only diff is not part of the review and is discarded.

### Pass 3 — whole-request and final verification

- `python -m pytest -q`: **202 passed** after restoring the pinned small inputs.
- Ruff: passed. Compileall for `src/`, `scripts/`, and `tests/`: passed.
- `scripts/check_metric.py`: max absolute fast-vs-brute DTI difference `4.441e-16` over the registered random-grid checks; exact cases and 300 m kernel offset checks passed. This is COMPUTED implementation verification, not a score.
- `scripts/build_release_status.py --check`: passed; `scripts/collect_evidence.py`: completed; `scripts/build_site.py`: 22 pages; `scripts/check_site.py`: 22 pages and 513 local links, all passing.
- No new GeoTIFF was made, so no new raster hash, candidate-specific holdout, leakage canary, before/after placement uniqueness run, or run card exists. Requirements for those deliverables are explicitly unfulfilled rather than fabricated.

## Official/source links for manual review

These are persistent reference URLs, **not freshly retrieved or re-verified in this review**. The runtime network allowlist does not include their hosts; no authentication, polling, or automatic submission occurred.

- [DrivenData problem description and format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData competition rules](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Competition data page (login may be required)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Official reference-solution repository](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN data](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [GDR/INGENIOUS submission 1391](https://gdr.openei.org/submissions/1391)
- [EPSG:32611 definition](https://epsg.io/32611)
- [DOE/NLR GEMS report PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [Competition leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) — static link only; no leaderboard data accessed.

## Remaining blockers and recommended next session

1. Obtain/record the exact single-method paragraph and resolve the strict any-registry lattice rule through explicit protocol-owner authorization. Do not self-assign an idea or exempt a control.
2. Restore the full permitted competition feature stack and shared cache, verify pinned hashes, and establish provenance/access permissions. Keep data and caches out of Git.
3. Refresh all nine site inventories at pinned commits if and when source access is permitted; current pinned snapshots are not proof of a complete or live inventory.
4. Only after authorization, preregister at most three experiments / two hours; run feature-alone leakage canaries first; then buffered whole-segment hide/recover with visible-only catalogue features and exact masking; compare paired pooled HOLDOUT-DTI/CI to a same-run retrained incumbent; keep a separate untouched confirmation.
5. On any eligible candidate, apply full before-placement and final-dot registry checks and exact file validation; create the required run card only from actual outputs. A separate selector must check weekly quota. A HOLDOUT-DTI or projection is never an organizer-confirmed score.
6. Preserve the current static site policy unless written permission authorizes automated DrivenData access. Attach exact-byte organizer receipts before any historical result is reclassified as ORGANIZER-CONFIRMED.
