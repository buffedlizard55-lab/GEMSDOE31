# Current project status — 2026-10-26

## Current Arena integration status — `arena/e40c3412-gemsdoe31`

The current branch preserves the concurrent `origin/main` CSDU artifacts and independently records that both fail exact-footprint validation against the pinned owner-mirror sample. They remain forensic files, **DO NOT SUBMIT**; holdout-DTI, leakage canaries, and registry uniqueness remain untested. H31-S remains negative and not slot-approved. No experiment, TIFF generation, upload, leaderboard access, or slot use occurred.

Latest local validation after merge conflict resolution: **145 pytest tests passed**, Ruff and compileall passed, CSDU/H31-S/current-run exact-file verifiers retain their negative verdicts, and the generated site check passed (22 pages, 445 local links). The `origin/main` integration at `784d3ae` was committed and pushed to this branch as `5895788`. PR #40 remains open and unmerged. Three remote Actions runs (`40358930573`, `40359503361`, `40360022522`) failed in the unit/regression-test step; GitHub's log download returned EOF, so the specific failing assertion is unknown. The same restore/verifier/test sequence passes locally under Python 3.11. Meanwhile, `main` advanced to `8e91d82` and GitHub now reports PR #40 as conflicting. Do not merge until remote CI is diagnosed/passes and the newer base changes are reviewed. See [branch review](repo_review_2026-10-26_arena_e40c3412.md).

## Historical audit continuation (`arena/1028355f-gemsdoe31`)

See [metric and release review](2026-10-26_metric_and_release_review.md).
Zero new geological experiments, TIFFs or slots in this continuation. Corrected marginal DTI prose
and unsupported confirmed-score/causal claims. Revalidated MAGREST, H31-S, H31-J and H31-T;
none is slot-approved. Current validation: **142 tests pass**, Ruff/compileall pass, 22 pages and
439 local links pass. The earlier H31-S review below is preserved, not a new experiment here.
`registry/current_run.json` remains the historical MAGREST card; `registry/h31s_current_run.json`
identifies the separately preserved H31-S artifact. Neither authorizes submission.

## Executive decision

**No competition submission is approved. Do not upload any repository TIFF.** The latest fully automated candidate is H31-S (`UDAP-SSLIC`). It is a genuinely generated, downloadable research artifact—not a copy—but its run-card verdict is **negative**, `slot_approved=false`, and `ok_to_submit=false`.

- Research download: [`gemsdoe31-h31s-udap-sslic-37654-20261026-9355f21d9f-zeros.tif`](../docs/downloads/gemsdoe31-h31s-udap-sslic-37654-20261026-9355f21d9f-zeros.tif)
- Machine run card: [`registry/h31s_current_run.json`](../registry/h31s_current_run.json)
- Exact-file verifier: `python scripts/verify_h31s_run.py`
- Unique name: `gemsdoe31-h31s-udap-sslic-37654-20261026-9355f21d9f`
- Portal note (92/140 characters): `H31-S UDAP+HZAD+SSLIC 37654d B2 | HOLDOUT-DTI s41=0.0948 s42=0.0980 | research-only 9355f21d`

The all-finite TIFF passes local range validation; the exact cause of the prior portal rejection is unknown: it is single-band float32, finite everywhere, and every value is in `[0,1]`. Passing format validation does **not** establish scientific efficacy, uniqueness against every possible private submission, organizer acceptance, or permission to spend a weekly slot.

## H31-S measured result

All numbers below are **HOLDOUT-DTI**, evaluator `gems57-pooled-hide-v2`; none is a leaderboard score.

| Evaluation | Withheld positives | H31-S | 95% CI | Comparator | Paired delta (95% CI) | Gate |
|---|---:|---:|---:|---:|---:|---|
| Screen seed 41 | 2,820 | 0.0948 | [0.0612, 0.1292] | Physical-HGB 0.0591 | +0.0357 [0.0082, 0.0659] | 3/4 quadrants; pass comparator gate |
| Screen seed 41 | 2,820 | 0.0948 | [0.0612, 0.1292] | H31-M 0.0713 | +0.0235 [-0.0204, 0.0698] | 1/4 quadrants; **fail** |
| Fresh confirmation seed 42 | 2,823 | 0.0980 | [0.0728, 0.1249] | Physical-HGB 0.0544 | +0.0436 [0.0179, 0.0695] | 4/4 quadrants; pass |
| Fresh confirmation seed 42 | 2,823 | 0.0980 | [0.0728, 0.1249] | H31-M 0.0718 | +0.0262 [0.0001, 0.0544] | 4/4 quadrants; pass |

The preregistered rule required success against both comparators on both seeds. The seed-41 H31-M comparison failed, so the efficacy gate failed despite a positive fresh confirmation. Leakage canaries passed (maximum two-sided value AUC 0.6479, below 0.90).

## Uniqueness and validator status

- H31-S contains 37,654 positive pixels and zero dots on the public catalogue.
- SHA-256, all-finite TIFF: `186d35d8c671cb36c9e3afb0b365c47c2962727248b0acaa8196d6b767f03ffd`.
- Exact validator result: CRS EPSG:32611; shape 3730×3292; 100 m transform; one float32 band; finite values `[0,1]`; 37,654 binary dots.
- Against discrete focus-site competitors, H31-S is below the 70% overlap stop threshold (for example, 47.4% within 3 px of H33).
- Against the literal shared 695-raster registry it fails: a registered spacing-5 calibration lattice is within 3 px of 99.93% of H31-S dots, and a dense registered baseline reaches 100%. The protocol provides no exemption for controls, so this is a hard STOP. This also demonstrates that the literal broad-registry rule is degenerate for nearly any nonempty raster; only the protocol owner can rescope it.

## Focus-site executive answer

The highest supplied nine-site historical claim remains GEMSDOE32 H33-2-B2 at **0.2778 USER-REPORTED**. No organizer receipt is present, so it is not `ORGANIZER-CONFIRMED`. Forensics show H33 is primarily D2.8 support with 1–2 pixel catalogue-flank dots removed. Its plausible advantage is false-positive-budget pruning near already mapped faults, not demonstrated discovery of new faults. Hidden competition truth is unavailable, so the exact causal reason for 0.2778 and any claim that a new file will beat it cannot be verified.

The complete nine-site table is on [`docs/index.html`](../docs/index.html). Historical 0.3195 and 0.4413 figures are also user-reported and must not be represented as verified leaderboard targets. The best file to submit **today is none**: historical leaders violate the duplicate-lane rule, while H31-S fails preregistered efficacy and literal-registry gates.

## Three-pass review completed

1. **Implementation pass:** confirmed the generated H31-S TIFF, ZIP, receipt, run card, home-page warning, unique name, short note, nine-site table, and automated `DO NOT SUBMIT` state.
2. **Bug/edge pass:** restored the two pinned small validation inputs with `scripts/verify_h31j.py --restore-small-inputs`; reran exact H31-S validation; checked the site and local links; confirmed the all-finite artifact cannot contain NaN/Inf or out-of-range values.
3. **Requirements pass:** reconciled this status page with the latest H31-S run, retained evidence labels, did not invent an organizer score, did not use a submission slot, and stopped because the three-experiment budget is exhausted and no assigned method paragraph was supplied.

Verification on 2026-10-26:

- `python -m pytest -q`: **136 passed**.
- `ruff check .`: **passed**.
- `python scripts/check_site.py`: **22 pages, 439 local links, passed**.
- `python scripts/verify_h31s_run.py`: `ok_to_download_for_research=true`, `ok_to_submit=false`, `slot_approved=false`, `verdict=negative`.

## Blockers and next work

1. Obtain an explicit assigned-method paragraph before another experiment; the prompt omitted it, and the three-experiment H31-S budget is exhausted.
2. Ask the protocol owner to decide whether calibration lattices and dense continuous controls belong in the 3-pixel registry comparison. Do not silently exempt them.
3. Have a separate selector decide promotion only after a candidate passes every preregistered efficacy and uniqueness gate.
4. Obtain organizer-authenticated score receipts and rules/template provenance through permitted access. Local validation is not organizer acceptance.
5. Do not automate a DrivenData upload or spend a weekly slot from this repository.


## Arena continuation — branch aa4c2098, 2026-10-26

This continuation did **not** fit a model, run a geological experiment, generate a TIFF, use a slot, access the live leaderboard, or upload. It reconciled the README to current H31-S status and reviewed the marginal-DTI correction and desk-only hypothesis refinements from the latest release audit.

- Latest candidate: H31-S, dedicated verifier `scripts/verify_h31s_run.py` returns `verdict=negative`, `ok_to_download_for_research=true`, `ok_to_submit=false`, `slot_approved=false`. Its screen vs H31-M was 1/4 quadrants with paired CI crossing zero; later confirmation was positive but does not repair the failed preregistered screen.
- The broad-registry spacing-5 witness gives 99.931% 3-px overlap, above the literal 70% gate. The full registry comparison is not exhaustive.
- `registry/current_run.json` is a legacy MAGREST receipt; H31-S is identified by `registry/h31s_current_run.json` and its dedicated verifier. Both receipts deny submission. Follow-up should normalize this pointer without removing historical verification.
- Final checks in this continuation: 142 tests passed; Ruff/compileall passed; metric proof max fast/brute difference `4.441e-16` on 24 grids; marginal DTI audit passed 10,000 sign checks; four exact-file verifiers deny slot approval; site check passed 22 pages/439 local links.
- Remaining blockers: no assigned method paragraph; experiment budget exhausted; broad-registry stop; no organizer-authenticated score receipt; no full production data/cache or exhaustive registry proof.

## Arena continuation — branch `arena/e40c3412-gemsdoe31`, 2026-10-26

This review fixed stale public-facing status text and verified the existing denial; it did not run a geological experiment, generate a TIFF, use a slot, access the live leaderboard, or upload. H31-S remains the latest documented candidate and is still negative. Its original three-experiment cap is reached; no assigned method paragraph was supplied in the current request.

- Fixed the generated site hero that incorrectly said RBU31 was newest and overstated H31-S as 4/4 quadrants versus H31-M on its seed-41 screen. The corrected text states H31-S seed 41 has 1/4 quadrants versus H31-M and seed 42 confirmation has 4/4; the preregistered efficacy result stays negative.
- Current site is regenerated from `scripts/build_site.py` and `scripts/current_site.py`; local validation passes at 22 pages and 439 links.
- Installed pinned requirements in ignored `.venv/`, restored only the small test rasters and registered-lattice witness, verified H31-S and legacy MAGREST exact-file denials, ran the metric proof, Ruff, compileall and the full test suite. See [session review](repo_review_2026-10-26_arena_e40c3412.md) for final counts and exact outcomes.
- Three desk hypotheses are recorded in that review. They are not assigned to the current lane, have no numeric DTI forecast, and are not authorized to run.
- Full production feature/cache stack, live organizer receipts, and exhaustive global registry proof remain unavailable. No current file is approved to submit.

## Arena branch integration and CSDU audit — `arena/e40c3412-gemsdoe31`, 2026-10-26

During PR preparation, `origin/main` advanced and contained a concurrent CSDU stepover raster. It was preserved in the integration, but not treated as this review's candidate or experiment. A read-only exact-footprint audit against the pinned owner-mirror `data/sample_submission.tif` found both CSDU variants fail:

- The all-finite file has 1,899 positive cells outside the true footprint (`outside_footprint_zero` fails).
- The NaN-outside twin has 2,610,312 NaNs inside the actual footprint and fails footprint finiteness/range/mask checks.
- The originating script uses an approximate synthetic ellipse and synthetic zero-label raster; its own receipt reports 5,281,049 footprint cells, while the pinned sample has 5,167,373. The sample is an owner mirror, not organizer-authenticated.
- CSDU HOLDOUT-DTI, feature-alone leakage canaries, and registry similarity are not run. “New geometry” or zero copied dots by construction does not prove the protocol's registry uniqueness.

The new exact-mask audit is `evidence/csdu_owner_mirror_validation_20261026.json`; `IR-31-CSDU-SYNTHETIC-FOOTPRINT-FAIL` is in `registry/irregularities.json`. The original generator is quarantined and exits before writing. CSDU remains audit-only; **DO NOT SUBMIT**. No re-masking, regenerated TIFF, or CSDU experiment was performed. H31-S remains the latest fully evaluated candidate, but it too is negative and not approved.

PR #40 remains open and unmerged. The `origin/main` integration commit `5895788` and status follow-ups are pushed on the fixed Arena branch, preserving the incoming artifact and surfacing its failures. Local checks pass; three remote Actions runs failed in the unit/regression-test step, and their exact failure is not available from the log endpoint. `main` has since advanced to `8e91d82`, and GitHub reports the PR as conflicting. Do not merge pending CI diagnosis and review of the newer main changes.
