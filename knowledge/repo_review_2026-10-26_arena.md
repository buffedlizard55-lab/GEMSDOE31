# Repository review — 2026-10-26 Arena continuation

## Decision

**No file is approved to submit.** The latest documented candidate is H31-S (`UDAP-SSLIC`), research-download only. Its preregistered screen against H31-M and literal broad-registry uniqueness gate fail. This continuation performed no fit, geological experiment, TIFF generation, upload, live leaderboard access, or weekly-slot use. The assigned-method paragraph is absent and the experiment budget is exhausted.

The highest supplied nine-site claim remains GEMSDOE32 H33-2-B2 at **0.2778 (USER-REPORTED; no organizer receipt)**. Byte forensics show catalogue-flank pruning from the D2.8 support. That may reduce redundant false-positive weight, but does not establish causal improvement or private score attribution. The separate [metric and release review](2026-10-26_metric_and_release_review.md) corrects the mathematical explanation and lists three desk-only refinements; none is an authorized experiment or numeric DTI forecast.

## Three review passes

### Pass 1 — current-state and artifact audit

- Read `AGENTS.md`, the complete README/owner prompt, current status, H31-S run card, `registry/review_passes.json`, and its preregistration. Confirmed branch `arena/aa4c2098-gemsdoe31`.
- `scripts/verify_h31s_run.py`: `verdict=negative`, `ok_to_download_for_research=true`, `ok_to_submit=false`, `slot_approved=false`; name `gemsdoe31-h31s-udap-sslic-37654-20261026-9355f21d9f`; all-finite TIFF SHA-256 `186d35d8c671cb36c9e3afb0b365c47c2962727248b0acaa8196d6b767f03ffd`.
- **HOLDOUT-DTI** (`gems57-pooled-hide-v2`): screen seed 41, 2,820 withheld positives, `0.09478` [0.06120, 0.12925]; paired delta vs H31-M `+0.02345` [-0.02042, +0.06979], only 1/4 quadrant wins. Untouched confirmation seed 42, 2,823 withheld positives, `0.09796` [0.07280, 0.12485]; paired delta vs H31-M `+0.02620` [+0.00010, +0.05441], 4/4 quadrants. Since the preregistered screen criterion failed, positive confirmation alone does not make the overall verdict positive.
- Uniqueness receipt: max surface `|Spearman|=0.16294`; discrete final 3-px overlap max 66.503%; broad-registry witness overlap 99.931% and dense baseline 100%. Both broad and discrete uniqueness gates fail; the broad scan is not exhaustive.
- Identified `registry/current_run.json` and `scripts/verify_current_run.py` as older MAGREST scope, while `registry/h31s_current_run.json` and `scripts/verify_h31s_run.py` identify H31-S. Both deny submission; README now labels the mismatch rather than implying MAGREST is current.

### Pass 2 — independent consistency, math and edge review

- Reconciled competing README session banners to the H31-S status, and explicitly labeled CONCORD31 material as historical. Kept the full owner prompt and exact historical artifacts/hashes.
- Reviewed the newly merged DTI marginal-gain correction: with fixed truth count `N`, `S=T/((1-beta)T+alpha F+beta N+epsilon)`. Improvement requires `(1-(1-beta)S) ΔT > alpha S ΔF`; for positive `ΔF`, the ratio threshold is `alpha*S/(1-(1-beta)*S)`. At the unverified `S=0.2778`, the arithmetic example is 0.0588285; this is algebra only, not a score projection. The shared evaluator was not modified.
- The former denominator `1-S` and general interpretation as an isolated-dot hit probability were corrected in README/rendered research text. The one-cell special case threshold is separately labeled.
- Merged an independently checkable `scripts/check_marginal_dti.py` and tests from main; verified 10,000 finite addition/removal sign checks. No TIFF or historic metric was changed.
- Kept the literal broad duplicate rule. No calibration-density exemption or global uniqueness claim was added.

### Pass 3 — whole-request cross-check

- The latest release review provides three ranked future hypothesis refinements (reciprocal magnetic restoration, joint radiometric/magnetic displacement, and gravity–magnetic co-restoration), named mimics, costs, prior-art limits and sources. They are desk-only, expected DTI gains unknown, and not authorized under the exhausted/stopped lane. They should not be described as globally novel without a wider prior-art audit.
- No live leaderboard access, organizer receipt, weekly selection, or upload. Static official/source links remain for manual review. The site is not a live competition feed; automated monitoring remains prohibited by repository policy absent written permission.
- Local status and exact-file receipts clearly distinguish “download for research” from “approved to submit.”

## Verification

- `.venv/bin/python -m pytest -q`: **142 passed**.
- Ruff and `compileall`: passed.
- `scripts/check_metric.py`: max fast/brute absolute difference `4.441e-16` over 24 grids; 29 offsets within 300 m.
- `scripts/check_marginal_dti.py`: 10,000 finite-change sign checks pass.
- Exact verifiers for H31-S, H31-J, H31-T and legacy MAGREST deny slot approval. H31-S permits research download only.
- Evidence collection/site generation/check: 22 pages, 439 local links; all checks passed.

## Remaining blockers

1. Obtain a valid assigned-method paragraph and new lane authorization before any new fit.
2. Resolve the literal broad-registry comparator policy through documented owner/selector protocol; do not silently exempt the registered dense witness.
3. Normalize the generic MAGREST `current_run.json`/verifier pointer without dropping historic coverage; current H31-S has a dedicated receipt/verifier.
4. Restore full production data/cache from permitted pinned sources; this clean checkout lacks them.
5. Require feature-alone leakage canaries, buffered whole-segment hide-and-recover HOLDOUT-DTI with CI, same-run incumbent comparisons, untouched confirmation, and exact-file uniqueness before selector review.
6. Obtain organizer-authenticated exact-byte score receipts. Never present a proxy or projection as an organizer score.

Official and primary manual-review links are indexed in `registry/sources.json`; the latest [`metric and release audit`](2026-10-26_metric_and_release_review.md) records access limits and the official-reference review.
