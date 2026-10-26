# Repository review — 2026-10-26 Arena continuation

## Decision

**No file is approved to submit.** The latest documented candidate is H31-S (`UDAP-SSLIC`), a research-download artifact whose preregistered same-instrument screen and literal broad-registry uniqueness gates fail. No experiment, TIFF, upload, leaderboard access, or weekly slot was used in this continuation. The assigned-method paragraph is absent and the H31-S budget is exhausted.

The highest supplied nine-site claim remains GEMSDOE32 H33-2-B2 at **0.2778 (USER-REPORTED; no organizer receipt)**. Repository geometry is consistent with D2.8 thinning and a 2-pixel public-catalogue flank prune. This is a plausible false-positive-budget explanation, not proof of causal score improvement or private-score attribution. No leaderboard access or upload was performed.

## Three review passes

### Pass 1 — current-state and artifact audit

- Read `AGENTS.md`, the complete README/owner prompt, current status, `registry/h31s_current_run.json`, `registry/review_passes.json`, and the H31-S preregistration/run card. Confirmed the branch is `arena/aa4c2098-gemsdoe31` and the checkout began clean.
- Audited H31-S using its active run receipt and ran `python scripts/verify_h31s_run.py`: verdict negative; research download permitted; `ok_to_submit=false`; `slot_approved=false`; name `gemsdoe31-h31s-udap-sslic-37654-20261026-9355f21d9f`; all-finite TIFF SHA-256 `186d35d8c671cb36c9e3afb0b365c47c2962727248b0acaa8196d6b767f03ffd`.
- H31-S **HOLDOUT-DTI**, evaluator `gems57-pooled-hide-v2`: screen seed 41, 2,820 withheld positives, `0.09478` [0.06120, 0.12925]; paired delta vs same-instrument H31-M `+0.02345` [-0.02042, +0.06979], 1/4 quadrants. Untouched confirmation seed 42, 2,823 withheld positives, `0.09796` [0.07280, 0.12485]; paired delta vs H31-M `+0.02620` [+0.00010, +0.05441], 4/4 quadrants. The preregistration required success on both seeds, so screen failure remains negative.
- Uniqueness receipt: max surface `|Spearman|=0.16294`; discrete final 3-px overlap max 66.503%; broad-registry spacing-5 witness overlap 99.931% (dense baseline 100%). Both broad and discrete uniqueness gates fail; registry scan is not exhaustive.
- Discovered an important name/source mismatch: `registry/h31s_current_run.json` / `docs/downloads/h31s-run-card.json` describe H31-S; generic `registry/current_run.json` / `scripts/verify_current_run.py` still describe the older MAGREST artifact. The generic verifier also denies submission, but is not the latest candidate receipt.

### Pass 2 — independent consistency and edge review; correction

- Found competing README headers identifying XFCOH31, CONCORD31, H31-S and MAGREST as “latest” across different snapshots. Main's current-status record and H31-S receipt identify H31-S as latest; generic `current_run.json` is a legacy MAGREST record.
- Corrected README so H31-S is the sole current candidate, its holdout/uniqueness failures are explicit, its download is marked research-only, and MAGREST generic receipt is identified as legacy. The older CONCORD31 page is explicitly marked as a historical snapshot superseded by current status. Historical narrative and the complete owner prompt remain preserved.
- Regression suite caught dropped H31-J exact-file hashes/name/note and required hard-stop language; restored those audit references without implying approval.
- Kept the literal duplicate rule: the registered 99.931% overlap witness fails the threshold. No density exemption and no global uniqueness claim.

### Pass 3 — whole-request cross-check

- The requested current status, complete owner prompt, nine-site summary link, automated validator, research-only download and official-source review links are present. The exact H31-S verification is automated and needs no human inspector to decide the current no-submit status.
- No new candidates were fit or TIFFs generated: the assigned method paragraph is missing, three-experiment cap exhausted, and broad-registry STOP remains. Additional hypotheses cannot be called “untried” without a broader prior-art audit; no unsupported novelty or improvement estimates are asserted.
- No live leaderboard access, organizer receipt, slot selection, or upload. The static competition link is for manual review only; automated monitoring is not done.

## Verification

- `.venv/bin/python -m pytest -q`: **136 passed**.
- Ruff and `compileall`: passed.
- Metric proof: maximum fast/brute absolute difference `4.441e-16` over 24 grids; exact cases passed; 29 kernel offsets inside 300 m.
- `scripts/verify_h31s_run.py`: negative; research download allowed; submission denied; H31-S TIFF hashes reproduced.
- `scripts/verify_current_run.py --restore-small-inputs`: negative/no-submit for the older MAGREST receipt. Do not confuse it with the latest H31-S run.
- Site build/check: 22 pages, 439 local links; all checks passed. Evidence collection: 155 artifacts inventoried, 13 files registered.

## Limitations and next work

1. Obtain a valid assigned-method paragraph and new explicit lane authorization before any new fit.
2. Resolve the literal broad-registry comparator policy through documented owner/selector protocol; do not silently exempt the registered control.
3. Normalize the generic `registry/current_run.json`/verifier pointer to avoid confusion with H31-S, while retaining the archived MAGREST receipt and its verifier coverage.
4. Restore production data/cache from permitted pinned sources; this checkout lacks the full inputs.
5. Require candidate-specific leakage canaries, buffered whole-segment hide-and-recover HOLDOUT-DTI with CI, same-run incumbent comparisons, untouched confirmation, and exact-file uniqueness checks before selector consideration.
6. Obtain organizer-authenticated exact-byte score receipts. Never present a proxy or projection as an organizer score.

## Claim classes and source links

- **COMPUTED (owner-mirror/template-based):** H31-S receipts and tests in `registry/h31s_current_run.json`, `docs/downloads/h31s-run-card.json`, and `scripts/verify_h31s_run.py`. Hashes prove local byte identity only, not organizer authenticity.
- **USER-REPORTED:** 0.2778 and the other leaderboard values supplied in the prompt; no organizer receipt is present.
- **INFERENCE:** D2.8 thinning and catalogue-flank pruning plausibly reduce redundant false-positive budget; causality is unverified.
- **Official/primary source links for manual review:** DrivenData [overview](https://www.drivendata.org/competitions/306/competition-doe-gems/), [problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), [DOE GEMS rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf), [reference solution](https://github.com/drivendataorg/gems-prize-reference-solution), and [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and). This continuation did not newly fetch these sources; the links are provided for review, not claimed as freshly verified.
