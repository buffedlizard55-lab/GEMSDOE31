# Repository review — 2026-10-25 (current integration)

## Executive result

**No new experiment or TIFF was produced by this review.** The current artifact remains the newly computed MAGREST research raster from merged PR #14; it is **OK TO DOWNLOAD FOR RESEARCH, DO NOT SUBMIT**. Its preregistered screen and the complete-registry overlap check fail; the site and machine-readable readiness record both deny submission. Do not rename or reuse it as a competition submission.

The review fixed missing ZIP SHA-256/byte-count metadata in the submission register collector, added ZIP integrity regression tests, and linked this review from README. The PR's original branch was brought forward to the then-current main (including PR #14) instead of carrying its stale green H31-B download page forward. PR #15 has since been merged.

## Findings and resolutions

1. **Inputs and stack now restored locally.** The 11 manifest files were fetched from the repository's pinned public GitHub owner mirrors and rechecked. `evidence/data_restore_review_2026-10-25.json` records `all_verified=true`; `evidence/data_preparation_review_2026-10-25.json` records all SHA-256 and grid checks true. `scripts/prepare_data.py` built the 42-band float32 stack (`2,062,898,880` bytes) at `data/prepared/features.f32`; the stack and source rasters remain ignored local data, not Git assets. These are **COMPUTED owner-mirror provenance checks**, not organizer-authenticated competition downloads. This removes the local data-placement blocker but does not justify a new fit under the closed experiment/duplicate-stop policy.
2. **Current TIFF must not be submitted.** `scripts/verify_current_run.py` independently returned `ok_to_download_for_research=true`, `ok_to_submit=false`, `verdict=negative` for `docs/downloads/gemsdoe31-magrest-concordant-37654-20261025-2c800a59ff-zeros.tif` (SHA-256 `c101ceb7237df0890a0f650b4211cc501250b47c1ab9cfeca8ee4cb373eb48d9`). The exact literal registry check reports 100% within-3-pixel overlap with a registered spacing-5 lattice; the paired screen also fails its predeclared loss criterion. This is a research download, not a competition-ready unique TIFF.
3. **MAGREST HOLDOUT-DTI (not a competition score).** Under evaluator `gems57-pooled-hide-v2`, with 2,901 withheld positives, candidate `HOLDOUT-DTI` is 0.052972 (95% CI [0.041311, 0.065329]); same-run control `HOLDOUT-DTI` is 0.048294 (95% CI [0.029922, 0.068506]); paired `HOLDOUT-DTI` delta is +0.004678 (95% CI [-0.017864, +0.022933]). The paired CI includes zero and a quadrant loss exceeds the allowed margin. The independent registry-overlap STOP is decisive regardless of this proxy metric.
4. **GEMSDOE32 score provenance.** The reported `0.2778` remains USER-REPORTED: no organizer score receipt is in the repository. H27→H33 annulus/pruning analysis is a useful geometric explanation of the mirrored dot sets, not proof of the competition's private score or a guarantee of transfer.
5. **Historical H31-B/H31-E files are not this review's output.** H31-B's primary raster was reopened before upstream integration and found to be one float32 band, EPSG:32611, 3730×3292, 100 m grid, finite `{0,1}` values and NaN elsewhere; SHA-256 `ff1b736337d53d9966248302b6cba0ffbd64bfcfe81a9d0695ef3364e6c53ebb`. Its prior receipt is historical validation only. The merged current page does not represent it as an approved current submission.
6. **ZIP metadata/UI defect fixed.** The collector previously recorded ZIP paths without SHA-256/size. It now hashes every extant registered ZIP, including the current negative artifact. Tests verify digest, size, archive integrity, and exactly one TIFF member; `check_site.py` compares every registered archive against its stored digest/size.
7. **PR #14 integration.** GitHub merged PR #14 during the review. Its literal registry STOP and explicit no-submit outcome are now the canonical main state, recorded in `knowledge/current_status_2026-10-25.md`, `knowledge/session_review_2026-10-25_magrest.md`, and the frozen run card. PR #15 (ZIP audit/review) is also merged. No other branch was merged by this session.

## Three-pass review

- **Pass 1 — implementation and evidence:** inspected the full README charter, active preregistration, current outcome records, submission register, current run card, site generator/checker, existing GeoTIFFs and ZIPs. Restored and hash-checked inputs, built the shared feature stack, fixed ZIP receipt metadata and added regression coverage.
- **Pass 2 — edge cases and consistency:** found the pre-merge site incorrectly presented the older H31-B raster as ready, and found a blank primary ZIP hash. Integrated the newer PR #14 negative verdict; confirmed the sample/template and labels via the pinned restoration path; ensured the current-run verifier reproduces the no-submit result. Confirmed ZIPs have one readable TIFF.
- **Pass 3 — final validation:** full tests, lint, metric check, current-run verifier, site build/check, source hash/grid check, and feature-stack build were rerun. No model fit, fourth experiment, candidate promotion, upload, or leaderboard lookup was performed.

## Final local verification

- Tests: **90 passed**; Ruff clean.
- `scripts/check_metric.py`: maximum fast-vs-brute DTI difference `4.441e-16` over 24 grids; 29 in-support kernel offsets. Numerical implementation test, not a score.
- `scripts/verify_current_run.py --restore-small-inputs`: negative status independently reproduced; no human review needed to determine the current file is not submit-ready.
- Site: 20 generated pages and 281 local links pass; download button is explicitly research-only and paired with DO NOT SUBMIT.
- Data verification: all 11 owner-mirror hashes and grid matches true; 42 prepared bands. The 2.06 GB stack and input rasters are ignored local files.
- No DrivenData endpoint was contacted; no file was uploaded; no live leaderboard or weekly cap was checked.

## Next actions

Follow [`knowledge/2026-10-25_next_session.md`](2026-10-25_next_session.md). Resolve the literal dense-control/registry degeneracy and confirm the assigned method lane before any new preregistration. Rebuild a comparable incumbent with the shared evaluator; do per-feature leakage canaries, whole-fault-component holdout, visible-only catalogue context, exact masking, empirical buffer, pooled DTI and paired spatial confidence intervals. Do not run more fits or emit a new TIFF until the current stop/budget is formally resolved. A future candidate must beat the same-protocol incumbent, pass fresh confirmation and the complete registry uniqueness check. Organizer receipts—not proxy metrics—are required for any ORGANIZER-CONFIRMED score.

## Source/scope note

See [`registry/sources.json`](../registry/sources.json) and the official-source audit in `evidence/official_reference_audit_20261025.json`. This review used the pinned GitHub owner mirrors and local project artifacts. Mirror byte identity is not organizer authentication; official non-GitHub competition pages, live scores, submission quota and portal acceptance were not freshly queried.
