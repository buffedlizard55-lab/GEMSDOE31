# Repository review continuation — 2026-10-26

## Decision and scope

**No model was fit, no experiment or candidate placement was run, no TIFF was generated, and no submission slot or upload was used.** This continuation fixes public-site and review-tool defects only. The active MAGREST run remains a negative research result and its existing TIFF remains **RESEARCH DOWNLOAD ONLY — DO NOT SUBMIT**. Exact bytes and decision: `docs/downloads/gemsdoe31-magrest-concordant-37654-20261025-2c800a59ff-zeros.tif`, SHA-256 `c101ceb7237df0890a0f650b4211cc501250b47c1ab9cfeca8ee4cb373eb48d9`, `verdict=negative`, `ok_to_submit=false`, `slot_approved=false`.

This pass followed the recurring brief and `AGENTS.md`, then rechecked the active run card, registry correction evidence, site sources, generated pages, static checker, and tests. The broader nine-site findings and first hypothesis review are in [`repo_review_2026-10-26.md`](repo_review_2026-10-26.md); this addendum records the follow-on corrections and validation.

## Findings fixed

| Severity | Finding | Correction |
|---|---|---|
| High | `scripts/current_site.py::overview()` preferred archived RBU31 evidence over `registry/current_run.json`, so the landing page could present RBU31 as the newest candidate and label an unapproved file a submission. `scripts/build_site.py` separately hardcoded RBU31 into homepage notices and the executive-summary hero. | The active page now reads the registry's current run card. It leads with the exact MAGREST artifact and an unmistakable research-only / DO NOT SUBMIT status. Archived RBU31 links stay in a lower historical section, always labelled research-only. |
| High | RBU31/H31-E2 historical copy attributed universal full-footprint overlap to the r13 spacing-5 lattice. | Added `evidence/registry_overlap_claim_correction_2026-10-26.json`; corrected README, AGENTS, active site/generators, current-status narrative, and derived `registry/submissions.json`. Historical experiment run cards and receipts were not rewritten. |
| Medium | H3 site generation emitted a Python `if dti_sgmc is not None` fragment into a table cell; overview and executive rendering each emitted H3 twice, creating duplicate `h3-download` and `h3-heading` IDs. | Optional metric strings are formatted before rendering; H3 appears once on each page. `scripts/check_site.py` parses every generated page for duplicate IDs and rejects unrendered conditional fragments. |
| Medium | The static site checks did not assert that the active run drives the hero or preserve a visible, untried-hypothesis list. | Added status, current-file, archived-RBU, overlap-attribution, and four-hypothesis checks; added regressions in `tests/test_presentation_safety.py`. The research page now displays four desk-only, untried hypotheses with their layers, mechanisms, mimics, cost/data limits, and explicit unknown DTI effects. |
| Medium | `scripts/audit_shared_registry_stop.py` restored its pinned TIFF only with the GitHub REST contents endpoint. That endpoint returned HTTP 403 rate-limit during this review even though the pinned Git object was reachable. | Reused the project's existing `download_competition_data._git_fetch_blob()` path first, retaining the API as fallback and enforcing the same SHA-256 before accepting bytes. The exact verifier then succeeded. |

## Overlap attribution: two separate rasters

The literal STOP is **unchanged**, but its evidence must not be conflated:

1. **GEMSDOE24 r13 spacing-5 lattice** — pinned SHA-256 `b4570b406efec198eb2f4d142ad8d0d6184b14b66f2f52b5c4d697f0647dc9b2`; the measured 3-pixel halo covers `0.9987132726822701` of the allowed footprint (`99.8713%`), not all possible candidate cells. It nevertheless overlaps the *specific* frozen MAGREST variants by `100%` of their candidate support. Other fixed examples have measured lattice overlap `99.6255%` (H31-M) and `99.52%` (H31-HVDC); these are candidate-specific measurements.
2. **GEMSDOE48 H58 continuous pignistic raster** — pinned owner-mirror SHA-256 `59ef8e7d8374e228bc1e41376f03fc67dd5b8a5e6804885a1ae802f399140b89`; registered in the shared snapshot; its recorded positive support is `5,167,373/5,167,373` allowed cells. Under the inherited `finite prediction > 0` support definition it is the *separate* universal 100% forward-overlap witness. It is a continuous field, not a sparse dot raster, so the conclusion is conditional on that recorded interpretation.

Both sources are owner-maintained mirrors, not organizer-authenticated registry/scoring evidence. The broad inventory is not exhaustive, but one registered witness suffices for this project's literal rule; no density/calibration exemption applies. Full sources, hashes, measurements, semantics and caveats are in the correction JSON.

## H33-2-B2 and the nine requested repositories

The supplied H33-2-B2 value **0.2778 is USER-REPORTED; no exact-byte organizer receipt was found**. The pinned support audit measures H33 as the D2.8 dot support after removing dots within two pixels of the public catalogue (2,545 dots removed relative to H27-4). A plausible explanation is metric-efficient pruning: removing low-yield near-catalogue dots can reduce false-positive mass while retaining off-catalogue support. That is an inference, not proof of the score's cause; the private truth is unavailable. Neither this explanation nor any local proxy predicts a leaderboard result.

| Site | Highest supplied claim | Evidence label |
|---|---:|---|
| GEMSDOE24 | 0.2477 | USER-REPORTED, no organizer receipt |
| GEMSDOE25 | 0.2600 | USER-REPORTED, no organizer receipt |
| GEMSDOE27 | 0.2449 | USER-REPORTED, no organizer receipt |
| GEMSDOE28 | 0.2710 | USER-REPORTED, no organizer receipt |
| GEMSDOE30 | 0.2600 | USER-REPORTED, no organizer receipt |
| GEMSDOE31 | 0.2708 | USER-REPORTED; pinned owner record marks the related artifact unscored |
| GEMSDOE32 | 0.2778 | USER-REPORTED, no organizer receipt |
| GEMSDOE33 | 0.2632 | USER-REPORTED, no organizer receipt |
| GEMSDOE36 | 0.2750 | USER-REPORTED, no organizer receipt |

These are the highest claims in the supplied repository records, not a live leaderboard lookup or ORGANIZER-CONFIRMED ranking. The existing `knowledge/repo_review_2026-10-26.md` links the pinned artifacts and discusses each method/overlap.

The active MAGREST **HOLDOUT-DTI** remains `0.052972044857535226` (evaluator `gems57-pooled-hide-v2`, 2,901 withheld positives, 95% CI `[0.04131136300815562, 0.06532899139172948]` as canonical in the run card). Its paired difference versus the same-run physical HGB control is `+0.00467843602723389`, 95% CI `[-0.017864202465723577, +0.022933167391729445]`, which crosses zero. This is a negative/inconclusive local holdout, not a competition score or projection.

## Four desk-only hypotheses for a separately authorized lane

These are repo-local ideas not identified in the reviewed GEMSDOE31 implementations; that is not a claim of global scientific novelty. Rank is a qualitative prior on potential DTI benefit versus cost, not a measured effect. Absolute ΔDTI is unknown for every proposal.

| Rank | Hypothesis / specific layers | Physical signature; why it may find missing faults | Difference from prior work | Non-fault mimic | Cost / access and expected effect |
|---|---|---|---|---|---|
| 1 | **Acquisition-seam-aware magnetic lineament persistence** — `rtp`, `mag_anom`, optionally GeoDAWN `TMI_up150`. | Directional anisotropy and lineament-edge persistence across scales; tests whether fault-related magnetic boundaries continue across inferred acquisition/leveling seams. | Existing arms use gradients/tilt/Euler or MAGREST patch-texture restoration; this explicitly models a stripe/seam null plus cross-scale persistence. | Volcanic/lithologic contact, residual leveling seam, or structure aligned with flight lines. | Medium. Owner-mirror band hashes are registered, but production stack is absent here and flight-line metadata is missing. Potentially highest relative upside, very uncertain; absolute ΔDTI **unknown**. |
| 2 | **Multiscale gravity–magnetic edge-transfer coherence** — `rtp`, `iso_grav_anom`, `iso_grav_anom_slope`, `depth_to_base_surf`. | Compare polarity, tangent, termination and lateral displacement across magnetic, gravity and basement-depth fields to detect buried structures under cover. | Prior work mainly fuses scalar strengths/unions or local textures; this tests cross-field edge displacement/termination with a contact null. | Pluton margin or basin-fill/lithologic contact shared across fields. | Medium-high. Bands are hash-pinned in the owner manifest, but production stack/cache is absent. Medium-to-high relative upside, high uncertainty; absolute ΔDTI **unknown**. |
| 3 | **Piedmont drainage-deflection asymmetry** — high-resolution USGS 3DEP DEM-derived channel network plus 100 m `det_elev`. | Blind-corridor channel/tributary deflection or paired incision asymmetry after conditioning on slope and fan direction; may detect displacement without a preserved scarp. | Existing LiDAR work quantifies local scarps/relief; this tests network-scale drainage geometry. | Avulsion, fan-lobe switching, lithologic permeability, irrigation or human diversion. | High and not data-ready: exact official tiles, metadata and in-footprint coverage were not fetched/checked under this runtime's host allowlist. Do not call viable until obtained and hash-pinned. Lower/uncertain relative upside; absolute ΔDTI **unknown**. |
| 4 | **Radiometric channel edge displacement** — GeoDAWN `K`, `Th`, `U`, `TC` plus `rtp`. | Seek repeatable, signed but laterally displaced channel transitions across scales; may expose compositional expressions of concealed structures. | Earlier radiometric work uses contrast/rank features; this tests channel-wise edge geometry and offset consistency. | Alluvial provenance, weathering, volcanic-unit margin or acquisition seam. | Medium. Registered bands are quantized/coverage-limited and production files are not restored. Low-to-medium relative upside, uncertain; absolute ΔDTI **unknown**. |

No hypothesis was fitted or scored; no external official endpoint was fetched. The full desk-only list also appears on the generated research page. The source URLs are references, not fresh availability verification.

## Validation actually completed

- Initial `verify_current_run.py --restore-small-inputs` attempt hit GitHub API HTTP 403 rate-limit while fetching the registered lattice. The existing blobless Git fetch returned the expected 1,706,456 bytes and SHA. After adding that shared-helper fallback, the same exact verifier succeeded: `ok_to_download_for_research=true`, `ok_to_submit=false`, `verdict=negative`; MAGREST TIFF SHA unchanged.
- `.venv/bin/python -m pytest -q`: **121 passed** after adding the public-copy attribution regression.
- `.venv/bin/ruff check .`: passed.
- `scripts/check_metric.py`: max fast/brute difference `4.441e-16` over 24 grids; closed forms passed; 29 kernel offsets.
- `scripts/collect_evidence.py`: 125 evidence artifacts inventoried; 10 submissions registered; generated RBU/H31-E2 public gate text uses the correction record.
- `scripts/build_site.py` + `scripts/check_site.py`: **21 pages / 356 local links passed**. Checks include duplicate HTML IDs, invalid conditional fragments, current-run precedence, active DO NOT SUBMIT status, corrected overlap attribution and four desk-only hypotheses.
- All small-input/registry-raster hashes are checked. Only the two small validation TIFFs and pinned registry control were restored to ignored workspace paths; no production feature stack/cache, model, candidate, or TIFF was produced.

Official non-GitHub pages and the live competition/leaderboard/quota were not fetched in this continuation; no scraping, polling, upload, or organizer-acceptance claim occurred.

## Review passes

1. **Implementation/evidence:** checked active status and exact artifact; traced generated home and executive pages back through `current_site.py` / `build_site.py`; verified the two registered witness sources and corrected their attribution without rewriting historical run cards.
2. **Bug/assumption:** added current-run/H3/overlap regressions and structural HTML checks; fixed the pinned-object restore fallback after the GitHub API limit; confirmed that all public status paths say research-only and no unique-submission approval.
3. **Whole-request/delivery:** reread the user goals and constraints, preserved H33 and nine-site caveats, published four untried desk hypotheses with data access/mimics/cost and unknown ΔDTI, then ran the full local check set. No experiment, slot, TIFF or upload was authorized.

## Remaining blockers

The assigned single-method paragraph remains missing; the MAGREST lane is stopped and its three-experiment budget is exhausted; the full-support witness blocks every nonempty in-footprint candidate under the inherited support rule; production feature data/cache is not restored; official template/score receipts are unavailable. Do not resume modeling or create another TIFF until the protocol owner explicitly resolves scope/support semantics, provides a method assignment and authorizes a new lane. No local proxy can establish that GEMSDOE31 beats 0.2778. Arena core values remain **Maximize P(Win) · Own the Outcome**: report the negative evidence directly and do not spend an unvalidated slot.
