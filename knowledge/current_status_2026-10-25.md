# Current status — 2026-10-25 (H31-E2 SCGP-Submod + MAGREST integrated record)

Read the complete owner prompt at the end of README, AGENTS, [H31-E preregistration](2026-10-25_h31e_preregistration.md), the frozen MAGREST preregistration, this record and `registry/review_passes.json` before continuing.

## Submission-safety correction (current review)

No artifact is approved for submission. H31-E2's 22-comparator PASS is a historical subset result,
not a broad-registry uniqueness pass. Literal registry STOP is binding, not merely an automatic-selector
hold that a human can override. See [review](review_2026-10-25_submission_safety.md).
No new experiment or TIFF is permitted in this stopped lane.

## Clean-runtime repository review (Arena continuation)

The local clean checkout lacked the full ignored production input/cache despite prior-session restore receipts. The exact-file verifier restored the two small inputs and registered witness, then passed; no new fit, TIFF, or slot followed. Final checks after integrating concurrent submission-safety fixes: pytest 101 passed, Ruff and compileall passed, metric equivalence max absolute difference 4.441e-16, and site check 20 pages/296 links passed. Updated review: [`repo_review_2026-10-25_arena.md`](repo_review_2026-10-25_arena.md).

## Historical integrated lane (H31-E2 SCGP-Submod · `gemsdoe31-scgp-submod-37654-20261025-fa735287`)

- **Primary NaN-outside GeoTIFF:** `docs/downloads/gemsdoe31-scgp-submod-37654-20261025-fa735287-nan.tif` (`d5ae3715c4ee727195ec6c023d5c852497538c3e60ff559997984f397b4d2fa8`); all-finite fallback `88860b14b2808e910ad72544996e41ccb59a80e2e190cda1467d7f0eb16a2ed6`; `37,654` off-catalogue binary dots (`31.5%` beyond `1.5 km`).
- **Automated validation gates (`evidence/h31e/run_card.json`):** `G1` Format & `[0, 1]` Range **PASS** (`0` NaN inside footprint); `G2` Single-Feature Leakage **PASS** (`max AUC = 0.7624 <= 0.90`); `G3a` Uniqueness across all 22 genuine submissions **PASS** (`max surface |ρ| = 0.1073 <= 0.90`, `max 3-px overlap = 51.53% <= 70.0%`); `G4a` Screen (`draw=101`, `21.3 km` buffer) **PASS** (`0.1274` vs `0.0922`, `+0.0352`, `4/4` quadrants); `G4b` Fresh Untouched Confirmation (`draws=[202, 303]`, `n=35,599`) **PASS** (`0.1145 [0.1071, 0.1232]` vs `0.0886`, `+0.0259`, `+29.3%`); `G5a` Piedmont SGMC **PASS** (`0.1233` vs `GEMSDOE32 H33-2-B2 = 0.1091`, `+13.0%`).
- **Weekly-slot auto-selector verdict (`slot_approved = false`, Run Card `verdict = "negative"`):** Held from automatic agent slot spending by strict pre-declared `G5b` all-elevation mountain SGMC (`0.0816 < 0.0940`, though `+13.6%` vs `Baseline-D = 0.0718`) and the unexempted `57GEMSDOE` `r13-lattice-s5` 5×5 calibration-lattice rule (`100.0%` interior coverage).

## Concurrent MAGREST decision

**Newly computed research TIFF exists. Literal registry-overlap STOP. OK TO DOWNLOAD FOR RESEARCH. DO NOT SUBMIT.**

- Primary: `docs/downloads/gemsdoe31-magrest-concordant-37654-20261025-2c800a59ff-zeros.tif`.
- SHA-256: `c101ceb7237df0890a0f650b4211cc501250b47c1ab9cfeca8ee4cb373eb48d9`.
- A one-TIFF ZIP and explicitly named NaN-outside counterpart are alongside it. Both use the same new predictions.
- Independent 37,654-dot emitter used no old dot field. All 118 comparable files in the nine pinned download trees pass the surface and final-support thresholds. One 32×48 test fixture is grid-incomparable. That original preflight scope was insufficient. Final review found an authentic registered spacing-5 lattice outside those download trees; surface/prospective and final overlaps are 100% for all three variants. The literal shared-registry rule FAILS. No dense/calibration exemption and no exhaustive 695-raster pass claimed. See `evidence/magrest/registry_scope_correction.json`.
- HOLDOUT-DTI `gems57-pooled-hide-v2`, **2,901 withheld positives**, **0.052972044857535226**, 95% CI **[0.04131136300815562, 0.06532899139157548]**.
- Same-run physical HGB control: HOLDOUT-DTI under that evaluator/n, **0.048293608830301336**, 95% CI **[0.029921573594205237, 0.06850647563703088]**.
- Paired Δ **+0.00467843602723389**, 95% CI **[-0.017864202465723577, +0.022933167391729445]**. Three quadrant wins; southwest loss **-0.01822816838479043**, exceeding the permitted .010 loss. **Screen failed.**
- Three frozen variants exhausted the experiment budget before the registry scope defect was discovered. No new fit/tuning/TIFF after the STOP. Already-generated genuinely new bytes are retained per the highest-priority output request, not promoted as a lane-approved unique submission. No confirmation, no fourth experiment, no selector action, no weekly slot. A format pass is not science approval or organizer acceptance.

## Resolved engineering blockers

- Eleven manifest inputs restored and hash/grid-verified; no manual placement needed.
- All nineteen regenerated raw feature-cache bands exactly match the pinned shared 57GEMSDOE receipt. `prepare_template_cache.py` reuses them and calls the unchanged shared builder only if absent.
- Whole 8-connected fault components withheld with an inherited 213-pixel collar; visible faults masked pixel-exactly. Active predictors use no catalogue/SGMC features or coordinate planes.
- 136 feature/missingness leakage tests pass; highest bidirectional AUC .8048414150943396. Synthetic label-copy regression demonstrates the leakage STOP.
- Shared evaluator, grid, mask, inference and writer files are unchanged and hash-pinned. The separate old local writer no longer clips invalid input, repairs footprint NaN or substitutes an unverified grid.
- The older common data preparer no longer caches full-catalogue/SGMC distances; Float32-min sentinel cleaning and verify-only failure semantics were repaired. No historical result is rewritten.
- Exact-file verification reopens both TIFFs, checks ZIP membership/bytes, template/catalogue hashes, spacing, supports, code/prereg pins, independent registry thresholds and frozen pooled DTI/CI/paired delta; re-derives the literal 100% overlap STOP and `ok_to_submit=false`. CI restores two small competition inputs plus that registered control.
- README contains the complete normalized current owner prompt. Site home/executive show the new download and DO NOT SUBMIT; historical pages are scoped as archives.

## Findings about the reported winner

H27 equals D2.8 pruned at catalogue distance >1 pixel; H33 equals D2.8 pruned at >2 pixels. H33 removes 2,545 H27 dots and retains the same 35,483 dots farther than 300 m. This is geometry/pruning, not evidence of new fault discovery. Equal far support does not imply equal kernel credit: removed near-catalogue dots can still cover off-catalogue truth. Reported .2778, .3195 and .4413 values remain user reports without exact-byte organizer receipts. See the 12-artifact, nine-site claim-separated review and lineage receipt.

## Remaining scientific/access limits

- A global same-protocol current-best comparison is not established; the stronger historical holdout best uses a different truth/buffer instrument and its older full trainer is unavailable.
- MAGREST's own residual correlation range is unknown. The inherited 21.3 km collar and 20 km bootstrap blocks do not prove independence or transfer.
- The negative result does not establish a valuable fault-slip map. Volcanic contacts, undisturbed anisotropic magnetic fabric and flight-line seams are named mimics.
- Only GitHub/package hosts are reachable. Official organizer reference code was freshly retrieved and pinned; official non-GitHub rule/data pages, the live leaderboard, submission page/quota and outside-mask convention were not freshly verified. Mirrors are not organizer-authenticated.
- No human inspection or external manual input is needed to get the present decision: it is already automatically negative. Scientific/data/access shortcomings are not delegated to an inspector.

## Next session

Keep this negative release immutable. First resolve the dense-control degeneracy explicitly in a future protocol; this session cannot waive the literal 70% rule. Start a new preregistration only after the lane is clarified or an explicit assumption is documented. Priorities: reciprocal across-window consistency and explicit contact/seam nulls; own-method residual-range estimation; shared-protocol reproduction of the strongest available control; independent off-catalogue corroboration and fresh confirmation; exact-file organizer receipt and convention verification before any separate selector approval. Never reuse this negative TIFF as a new submission under another name.

PR/deployment outcome is recorded in the session's final response and GitHub history; do not infer a deployment from an earlier Pages `built` response.

## Concurrent integration

Main advanced to `6b3ec48` during this run. Preserve H31-B source/TIFFs/receipts and restore the 121 earlier merged AS-1/TGJ31 files removed by that later merge. Colliding/obsolete workflow, extra page and homepage assertion are archived, not re-enabled; one legacy value-test fixture is adapted to the stricter grid contract. Current tests cover all retained scientific modules without a new fit. Original H31-B promote metadata is archived evidence, not reproduced or imported approval. All parallel TIFFs have current research-only/no-submit register entries. See `evidence/parallel_history_preservation_20261025.json`.

Main then advanced to `7619b61` (H31-E / PR #13); its code, tests, TIFFs, preregistration, results and negative card are preserved in the same integration. None is a new experiment by this session or a same-instrument MAGREST comparison. Source sentinel fix is reconciled with the already stricter local preparer; active shared-template hashes remain unchanged.

## Verified release delivery

PR #14 merged at 21:57:39Z as `3e8854d6b487f7cf65fac853e4333778cb0f061e`; push/PR/main CI and the Pages deployment succeeded. Fresh GitHub API retrieval of all four TIFF/ZIP blobs at that merge matches the reviewed bytes, and the published current run card is identical and denies upload. `evidence/magrest_delivery_release14_20261025.json` records the commit-specific API proof and limitations (public Pages HTTP and CI logs unavailable under the host allowlist). 89 local tests, 20 pages/281 local links, and 15 local browser viewport checks/six exact downloads passed.

A final wording-only follow-up removes an incorrect “failed confirmation” phrase (confirmation was never run), and withdraws “independent” from the SGMC proxy description because mapping-lineage independence is not established. No data, metric, TIFF or negative/STOP decision changes. The separate selector still has no candidate/slot authorization.

## Arena follow-up review (2026-10-25)

No new experiment or TIFF was authorized. The review's ranked four-hypothesis shortlist is desk-only; the active lane remains closed by the universal full-footprint overlap witness, missing assigned method paragraph, and exhausted three-experiment budget. The existing MAGREST raster remains **OK TO DOWNLOAD FOR RESEARCH ONLY — DO NOT SUBMIT**.

Final clean-runtime verification after restoring the two small pinned input files: 112 pytest tests passed; Ruff passed; DTI fast/brute maximum absolute difference was 4.441e-16; exact-run verifier returned `verdict=negative`, `ok_to_submit=false`; site build/check passed 20 pages and 320 local links. Report: [`knowledge/repo_review_2026-10-25_arena_followup.md`](repo_review_2026-10-25_arena_followup.md). Three current review-pass records are appended to `registry/review_passes.json`.

## 2026-10-26 review continuation

No new experiment, TIFF, or slot was used. Added a generated nine-site highest-claim matrix to the executive summary, with pinned artifact links, hashes, USER-REPORTED labels, and explicit prior-art/no-upload wording. Corrected an unsupported statement that the GEMSDOE25 and GEMSDOE24 TIFFs were exact same bytes; hashes differ and no cross-site pixel identity is now asserted. Full review and limitations: [`repo_review_2026-10-26.md`](repo_review_2026-10-26.md).

Verification after restoring the two exact small inputs: 118 pytest tests passed; Ruff passed; `verify_current_run.py --restore-small-inputs` returned `verdict=negative`, `ok_to_download_for_research=true`, `ok_to_submit=false` for the unchanged MAGREST hash; fast/brute DTI maximum difference `4.441e-16` over 24 grids; regenerated site check passed 21 pages and 364 local links. Initial tests before small-input restoration had 6 documented skips; those were rerun after restore. The full evidence collector reported 124 experiment artifacts and 10 submission records. Its temporary registry/readiness churn was restored where unrelated to this review.

The executive matrix ranks the highest supplied claim at GEMSDOE32 H33-2-B2 (`0.2778`, USER-REPORTED), but does not establish an official rank or score. The active duplicate witness, missing assigned method paragraph, exhausted experiment budget and non-authenticated competition inputs remain blockers. No upload or leaderboard access occurred.
