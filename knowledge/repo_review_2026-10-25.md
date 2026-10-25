# Repository review — 2026-10-25 (current integration)

## Executive result

**No new experiment or GeoTIFF was produced by this review.** I fixed the ZIP-hash display/metadata defect in the active submission-register collector, added ZIP-integrity regression checks, and documented the review in the README. During this work, upstream `main` advanced when PR #14 was merged; this branch has now integrated that commit. The resulting canonical project state is the negative MAGREST research release described below, not the earlier H31-B green download page.

**Current submission decision: research download only; DO NOT SUBMIT.** The just-merged audit found a literal 100% within-3-pixel overlap between the MAGREST support and a registered spacing-5 lattice, and the preregistered screen failed its paired-loss gate. The file is preserved as a negative research artifact; no selector approval, weekly slot, or organizer score exists. Do not relabel or reuse the historic H31-B TIFF as a new candidate.

## Findings

1. **Bulk modeling inputs unavailable in this working checkout.** The current-run verifier restored the pinned `labels.tif` and `sample_submission.tif` plus its registered control from the permitted GitHub mirror, then independently verified the current negative artifact. The other manifest inputs and prepared feature stack are still absent: `scripts/prepare_data.py --verify-only` returned `all_hashes_match: false` and `all_grids_match: false` for the 11-file manifest. That blocks new feature construction/fitting/holdout work here.
2. **The reported GEMSDOE32 `0.2778` is not organizer-confirmed.** It remains a user/owner claim without an organizer receipt. The documented H27→H33 pruning geometry is useful forensic evidence, but cannot establish a live score, a competition win, or that a new predictor generalizes to the private truth.
3. **Existing H31-B/H31-E files are historical artifacts, not this review's output.** The H31-B primary file was reopened before upstream integration: one float32 band, EPSG:32611, 3730×3292, 100 m grid, finite values `{0,1}` and NaN elsewhere; its digest was `ff1b736337d53d9966248302b6cba0ffbd64bfcfe81a9d0695ef3364e6c53ebb`. Its older template receipt records format checks, but this review did not recreate it or re-run scientific gates from source inputs.
4. **Current MAGREST artifact is explicitly negative.** The merged run card reports `HOLDOUT-DTI` under `gems57-pooled-hide-v2`, 2,901 withheld positives, 0.052972 (95% CI [0.041311, 0.065329]); paired Δ against its same-run physical control is +0.004678 (95% CI [-0.017864, +0.022933]). These are local holdout results, not competition scores. The distinct registry-overlap STOP is sufficient to block uniqueness regardless of the screen result.
5. **ZIP metadata/UI defect (fixed by this change).** The register collector previously recorded ZIP paths without their SHA-256 or size, causing a blank archive digest on the old H31-B home page. It now hashes extant ZIPs and records size; tests verify matching digest/size and a readable archive containing exactly one TIFF. The site checker verifies each registered ZIP receipt against the archive bytes. The merged main page's no-upload wording remains intact.
6. **Merged parallel work.** GitHub reports PR #14 merged to `main` as commit `3e8854d6b487f7cf65fac853e4333778cb0f061e` during this review. This branch integrated that commit rather than carrying an out-of-date green H31-B site forward. Its exact scientific claims and limitations are recorded in `knowledge/session_review_2026-10-25_magrest.md`, `knowledge/current_status_2026-10-25.md`, and the cited evidence/run cards.

## Verification performed

- Full integrated suite: **90 passed**; Ruff clean.
- Metric check: maximum fast-vs-brute difference `4.441e-16` over 24 grids; 29 in-support kernel offsets. This is a numerical implementation check, not a competition score.
- `scripts/verify_current_run.py --restore-small-inputs` independently returned `ok_to_download_for_research=true`, `ok_to_submit=false`, `verdict=negative` for the current artifact and exact digest.
- Site build/check: 20 pages and 281 local links passed. `scripts/prepare_data.py --verify-only` remains a fail-closed incomplete-input result for the full 11-file manifest.
- No DrivenData endpoint was contacted, no submission was uploaded, and no live leaderboard or weekly cap was checked.

## Next actions, in order

1. Follow [`knowledge/2026-10-25_next_session.md`](2026-10-25_next_session.md): do not reopen a stopped lane or emit another TIFF under an unresolved registry gate.
2. Resolve the dense-control/registry policy without waiving the literal overlap rule; recover missing registry paths and preserve hashes/error records.
3. Restore inputs from an authorized source and verify every SHA-256 and grid before new modeling. The working copy currently lacks the inputs; upstream history's restoration receipt does not change that.
4. Reconstruct a same-protocol current-best baseline before proposing a new preregistration; use the shared hide-and-recover evaluator, per-feature leakage canaries, exact visible-fault masking, empirical buffer, pooled DTI and paired spatial confidence intervals.
5. Keep every candidate's surface and final-dot uniqueness checks against the complete applicable raster registry. Any duplicate or failed scientific gate remains a negative result; the weekly selector is separate.
6. Keep format validity, unique support, scientific promotion, organizer acceptance, and leaderboard score as distinct statuses. Only an organizer receipt can make a score `ORGANIZER-CONFIRMED`.

## Source/scope note

The source register is [`registry/sources.json`](../registry/sources.json); the official competition rules and data endpoints were not freshly queried here. The review used local artifacts/tests and GitHub PR metadata. Owner mirrors are not organizer-authenticated, and no assumption is made about a live score or upload result.
