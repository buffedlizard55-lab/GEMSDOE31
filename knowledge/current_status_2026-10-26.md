# Current project status — 2026-10-26

## Executive decision

**No competition submission is approved. Do not upload any repository TIFF.** The latest fully automated candidate is H31-S (`UDAP-SSLIC`). It is a genuinely generated, downloadable research artifact—not a copy—but its run-card verdict is **negative**, `slot_approved=false`, and `ok_to_submit=false`.

- Research download: [`gemsdoe31-h31s-udap-sslic-37654-20261026-9355f21d9f-zeros.tif`](../docs/downloads/gemsdoe31-h31s-udap-sslic-37654-20261026-9355f21d9f-zeros.tif)
- Machine run card: [`registry/h31s_current_run.json`](../registry/h31s_current_run.json)
- Exact-file verifier: `python scripts/verify_h31s_run.py`
- Unique name: `gemsdoe31-h31s-udap-sslic-37654-20261026-9355f21d9f`
- Portal note (92/140 characters): `H31-S UDAP+HZAD+SSLIC 37654d B2 | HOLDOUT-DTI s41=0.0948 s42=0.0980 | research-only 9355f21d`

The all-finite TIFF fixes the prior portal-range failure mechanically: it is single-band float32, finite everywhere, and every value is in `[0,1]`. Passing format validation does **not** establish scientific efficacy, uniqueness against every possible private submission, organizer acceptance, or permission to spend a weekly slot.

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


## Arena review continuation — 2026-10-26

This continuation made **no model fit, experiment, TIFF, upload, leaderboard access, or slot use**. It reconciled the competing README summaries to the H31-S current status and explicitly flagged the older generic `registry/current_run.json` MAGREST receipt as stale for identifying the latest run. Full findings: [`repo_review_2026-10-26_arena.md`](repo_review_2026-10-26_arena.md).

- H31-S screen `HOLDOUT-DTI` (`gems57-pooled-hide-v2`, seed 41, 2,820 withheld positives): `0.09478` (95% CI `[0.06120, 0.12925]`); paired delta vs H31-M `+0.02345` (95% CI `[-0.02042, +0.06979]`, 1/4 quadrant wins), so the preregistered same-instrument screen gate failed. Untouched confirmation seed 42: `0.09796` (95% CI `[0.07280, 0.12485]`, 2,823 withheld positives); this does not erase the screen failure.
- H31-S exact verifier: `verdict=negative`, `ok_to_download_for_research=true`, `ok_to_submit=false`, `slot_approved=false`; zeros TIFF SHA-256 `186d35d8c671cb36c9e3afb0b365c47c2962727248b0acaa8196d6b767f03ffd`.
- The final discrete-scope maximum is 66.503% 3-px overlap; the unexempted broad-registry spacing-5 witness gives 99.931% overlap and the dense baseline gives 100%, forcing the registered stop. The broad scan is not exhaustive.
- The prior generic MAGREST verifier also returns a negative/no-submit decision, but it validates a different, older artifact. H31-S is the latest status artifact; this naming divergence is logged for follow-up.
- Verification in this continuation: 136 tests passed; Ruff and compileall passed; metric max fast/brute difference `4.441e-16` over 24 grids; H31-S verifier passed its fail-closed checks; generated site 22 pages / 439 local links passed.
- Limitations remain: missing assigned method paragraph, exhausted 3-experiment budget, broad-registry gate failure, absent production data/cache in this checkout, no organizer score receipt, and no complete global scan. No candidate is approved to submit.
