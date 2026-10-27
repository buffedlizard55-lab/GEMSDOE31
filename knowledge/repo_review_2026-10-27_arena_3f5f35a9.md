# Repository review — 2026-10-27 (active Arena branch `arena/3f5f35a9-gemsdoe31`)

## Decision first

**Do not upload any file from this review.** This review generated no TIFF, ran no new geological experiment, used no competition submission slot, and did not access or upload to DrivenData. The latest documented candidate is H31-AA (SLFS), a *research-only* TIFF from the preceding session. Its fixed holdout result failed to beat the same-run holdout incumbent, and its file fails the binding literal shared-registry uniqueness gate. The repeatable release gate is negative (`ok_to_submit=false`, `slot_approved=false`). No human override is implied.

The request's 2026-10-27 prompt contains more than one claimed leaderboard maximum (`0.2778`, `0.3195`, and `0.4413`). None is backed by an organizer receipt in this repository. Treat all user-supplied leaderboard values below as **USER-REPORTED**, not verified scores; no live leaderboard was accessed. A leaderboard-score estimate for a new candidate is **unavailable**, not a projected HOLDOUT-DTI.

## Nine-site executive comparison

The artifact identity, pinned owner-mirror URL, SHA-256, score label, and H33 proximity are taken from `registry/focus_review.json`, `registry/focus_unique_2026.json`, and `evidence/nine_site_forensic_audit.json`. The similarity metric is fraction of the artifact's positive dots that lie within 3 pixels of GEMSDOE32 H33-2-B2. Every row exceeds the protocol's 70% overlap stop threshold. This establishes failure against H33 for each row; it is **not** an exhaustive pairwise comparison of every site raster or proof of global uniqueness/non-uniqueness beyond the stated pinned artifacts.

| Site | Highest listed artifact (pinned mirror) | Reported score | Within 3 px of H33 | Unique under the stated threshold? | Estimated leaderboard score for a new file | Recommendation |
|---|---|---:|---:|---|---|---|
| GEMSDOE24 | `gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif` | 0.2477 USER-REPORTED | 88.48% | No — exceeds 70% vs H33 | Unavailable | Prior art; do not resubmit |
| GEMSDOE25 | `gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif` | 0.2600 USER-REPORTED | 88.17% | No — exceeds 70% vs H33 | Unavailable | Prior art; do not resubmit |
| GEMSDOE27 | `gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif` | 0.2449 USER-REPORTED | 86.72% | No — exceeds 70% vs H33 | Unavailable | Prior art; do not resubmit |
| GEMSDOE28 | `gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif` | 0.2710 USER-REPORTED | 95.47% | No — exceeds 70% vs H33 | Unavailable | Prior art; do not resubmit |
| GEMSDOE30 | `gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca-nanoutside.tif` | 0.2600 USER-REPORTED | 88.17% | No — exceeds 70% vs H33 | Unavailable | Prior art; do not resubmit |
| GEMSDOE31 | `gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif` | 0.2708 USER-REPORTED | 95.39% | No — exceeds 70% vs H33 | Unavailable | Prior art; do not resubmit |
| GEMSDOE32 | `gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-nan.tif` | 0.2778 USER-REPORTED | 100.00% | No — reference raster itself | Unavailable | Prior art; do not resubmit |
| GEMSDOE33 | `GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e-nanoutside.tif` | 0.2632 USER-REPORTED | 92.64% | No — exceeds 70% vs H33 | Unavailable | Prior art; do not resubmit |
| GEMSDOE36 | `gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-nan.tif` | 0.2750 USER-REPORTED | 97.40% | No — exceeds 70% vs H33 | Unavailable | Prior art; do not resubmit |

**Important ranking correction:** later low-scoring entries in the prompt do not replace each site's highest listed historical result. For example, GEMSDOE36's `KPL36` is listed at 0.1647, but the earlier Anderson artifact is listed at 0.2750; GEMSDOE28's newer S18/S21 values (0.0217/0.0206) are below the earlier H36-1 value (0.2710). GEMSDOE27's later H31-DRCG is 0.2250, below its listed 0.2449 result. All of those scores remain user-reported unless an organizer receipt is added.

The site already has the requested visible summary and upload instructions: [`docs/executive-summary.html`](../docs/executive-summary.html), with a current no-submit banner and no authorized download presented as upload-ready. For repeatable file generation/format checks, see `scripts/build_submission.py`, `scripts/validate_submission.py`, and the current release register; format validity alone does not establish score, uniqueness, organizer acceptance, or authorization to submit.

## Why H33-2-B2 may have scored highest in the supplied list

The strongest evidence-based explanation is a **candidate mechanism**, not proven causality. Byte-level comparison records H33-2-B2 as the D2.8 point field after removal of predictions in the public-catalogue flank through 2 pixels (approximately 200 m on the 100 m grid). Its surviving 37,654 dots are a subset of the D2.8 field; the forensic record reports zero added points. Removing dots close to known catalogue faults can reduce false-positive penalty while retaining many predictions farther from mapped faults. With the competition's finite-radius tolerance kernel and stronger false-negative weight, this pruning can improve the reported score if those removed flank dots add little hidden-truth coverage.

The independent comparisons in `evidence/nine_site_forensic_audit.json` also record that H36-1 had nearly the same dot count (37,660) but retained many catalogue-flank dots and used wider far-field spacing; its listed score was 0.2710 versus H33's 0.2778. The repo's forensic arithmetic attributes the difference primarily to catalogue-halo pruning rather than simply reducing the dot budget. GEMSDOE36's Anderson result is recorded as adding 1,200 thermal/step-over predictions to the 37,654-dot H33 base and scoring 0.2750; this is consistent with added diffuse predictions increasing false-positive cost more than true-positive benefit. These are reconstructions based on pinned raster bytes, reported scores, and proxy/evaluator calculations—not direct observation of the competition's private truth.

**What cannot be concluded:** no exact organizer receipt ties these score claims to their TIFF bytes; hidden competition labels are unavailable; there is no causal experiment against the private truth. Therefore the analysis does not prove why H33 achieved 0.2778, that it is the current leaderboard leader, or that any new raster will score higher. The claimed 0.3195 and 0.4413 leaderboard values are unverified and inconsistent as a single “current maximum” within the supplied prompt.

## Latest tested candidate and scientific status

The preceding H31-AA preregistration contains four ranked hypotheses and the frozen SLFS test. That experiment is complete; it is not permission to start a new lane. The applicable run card is `evidence/h31aa/run_card.json` and the detailed review is [`knowledge/2026-10-27_h31aa_session_review.md`](2026-10-27_h31aa_session_review.md).

- H31-AA/AA2 screen: **HOLDOUT-DTI** (evaluator `gems57-pooled-hide-v2`, 60,988 withheld positives, 95% CI `[0.1368, 0.1604]`) = **0.1489**.
- Same-run H31-X incumbent: **HOLDOUT-DTI** (same evaluator and 60,988 withheld positives, 95% CI `[0.1491, 0.1825]`) = **0.1661**. Paired difference AA2 − H31-X: **HOLDOUT-DTI** (same evaluator, 60,988 withheld positives, 95% CI `[-0.0283, -0.0062]`) = **-0.0173**.
- Untouched AA2 confirmation: **HOLDOUT-DTI** (evaluator `gems57-pooled-hide-v2`, 31,346 withheld positives, 95% CI `[0.1181, 0.1424]`) = **0.1302**, below H31-X's 0.1517 on that same split.
- AA4 scored 0.1556 on the screen, but the preregistered selection did not make it the selected uniqueness-cleared arm; it does not repair AA2's failure against H31-X or the literal registry stop.
- The 2026-10-27 audit reports external-focus uniqueness passing the two-stage discrete check for AA2 (69.27% pre-placement top-K overlap; 57.03% final dots) but local discrete top-K uniqueness and literal broad-registry checks failing. All overlap values are computed against the specified pinned raster scope; they are not proof against private/unseen rasters.
- The latest package is downloadable for research, not for competition submission: `gemsdoe31-h31aa-slfs-flexure-37654-20261027-fdb34746-zeros.tif`, SHA-256 `d272d5babb9523a70f77e76ad6843830d67a9eabaaa60f8c3f46ca57bde9a1ef`. Do not submit it.

No fresh geological hypothesis was fitted in this review. The requested method paragraph is absent; the H31-AA three-experiment budget was already consumed; and the repository's literal broad-registry rule remains a binding STOP. The previous four desk candidates and their layer/physics/mimic/cost details are documented in `knowledge/2026-10-27_h31aa_preregistration.md` and `knowledge/repo_review_2026-10-27_arena.md`. Do not claim these are exhaustive literature novelty searches.

## Submission choice, validator status, and blockers

- **Best historical listed score:** GEMSDOE32 H33-2-B2 at 0.2778 USER-REPORTED; not a unique new field.
- **Best submission to download and upload now:** none.
- **New candidate score estimate:** unavailable. HOLDOUT-DTI and SGMC proxy values are not calibrated leaderboard estimates, and projection audits found no defensible cross-family point prediction.
- **Current release state:** negative, `ok_to_submit=false`, `slot_approved=false`; validator passage cannot override scientific/uniqueness failure.
- **Critical literal-registry issue:** a pinned spacing-5 calibration lattice covers 99.8713% of the template footprint within 3 px. At the stated 37,654-dot budget, a counting lower bound forces at least 31,005 / 37,654 = 82.3418% of dots inside that halo, above the 70% rule. This is a computed combinatorial bound specific to the footprint, halo, and dot budget; it is not evidence of copying or a claim about every possible nonempty raster. The registered continuous surface is another literal-rule collision. No control exemption is authorized.
- **Data and access:** this review found no tracked production `data/` or `.cache/` stack at its start. Small validation inputs were restored through the repo verifier. DrivenData-hosted training data and current leaderboard data were not fetched; the official data page requires the permitted entrant access route. No automatic site monitoring, organizer contact, or submission occurred.

### Recommended work order

1. Resolve the uniqueness rule with the protocol owner in writing; do not silently exempt the calibration lattice or dense surfaces.
2. Supply/record the actual assigned method paragraph and confirm a fresh experiment budget. Freeze 3–5 distinct hypotheses, mimics, metrics, and gates before fitting; reuse `vendor/gems57` evaluator, writer and cached feature stack without a private fork.
3. Restore permitted competition inputs, verify pinned hashes and source provenance; do not place data/caches into Git.
4. For an authorized candidate, run each single-feature leakage canary first, then whole-segment spatial hide-and-recover with a buffer derived from OOF residuals, visible-fault-only features and exact visible-label masking. Report pooled HOLDOUT-DTI with evaluator, withheld-positive count and CI, plus a truly untouched confirmation.
5. Compute uniqueness on the continuous surface before placement and final dots against the complete authorized registry scope; validate exact CRS, shape, transform, band count, finiteness and `[0,1]` range. Negative candidates remain research-only.
6. Use the separate selector only after all gates pass and the weekly cap is checked by an authorized entrant. Never automate upload. Obtain organizer receipts before promoting a score claim to ORGANIZER-CONFIRMED.

## Official and primary-source links for manual review

These links are recorded for review; **they were not fetched from their non-allowlisted hosts in this session**. Repository mirrors and hashes establish byte identity to the pinned mirror, not official-source authenticity.

- [DrivenData DOE GEMS problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData competition rules](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [DrivenData competition data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [DrivenData leaderboard — static link only; not accessed](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [Official DrivenData reference-solution repository](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN airborne magnetic and radiometric surveys](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [GDR/INGENIOUS submission 1391](https://gdr.openei.org/submissions/1391)
- [EPSG:32611 definition](https://epsg.io/32611)
- [DOE/NLR GEMS report PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)

## Three-pass review record

1. **Pass 1 — Review and source/claim inventory:** read `AGENTS.md`, the complete README (including the preserved charter/prompt), current release status, current-run and review registers, H31-AA preregistration/run card, focus-site score/raster registers, and the existing executive summary. Confirmed no pre-existing working-tree changes. Identified the active branch `arena/3f5f35a9-gemsdoe31`.
2. **Pass 2 — Assumptions, edge cases, and independent gates:** the first direct system-Python check failed because NumPy/dependencies were absent. Created ignored `.venv/`, installed pinned requirements, restored only small verifier inputs, then reran checks. Confirmed the three claimed leaderboard highs are not authenticated here; differentiated the GEMSDOE36 historical leader from the lower KPL36 later result; distinguished file-format validity from uniqueness and permission; and confirmed literal broad-registry STOP. No TIFF or score projection was created.
3. **Pass 3 — Whole-request and code-quality cross-check:** full test suite passed (208 tests); Ruff and compileall passed; DTI implementation check max fast-vs-brute error was `4.441e-16` over 24 test grids; release-status check returned negative; exact current-run verifier returned research-download true / submit false / negative; generated site passed with 22 pages and 534 local links. No live DrivenData access or upload occurred. The run-card artifacts below are the previous H31-AA experiment, not a new experiment in this review.

## Existing H31-AA run card (previous session; included to satisfy traceability)

```json
{
  "hypothesis": "H31-AA SLFS: strike-coherent logarithmic slope flexure, screened against a paleoshoreline null and corroborated by subsurface edges",
  "mechanism": "AA2 crest-filtered LFLEX_SHORE; 37,654 dots, 2.8 px Poisson spacing, catalogue distance > 2 px",
  "named_non_fault_mimic": "Pleistocene Lake Lahontan wave-cut shorelines; additional mimics include cliff/talus breaks, canyon mouths, fan terraces, and volcanic flow toes",
  "holdout_dti": {
    "class": "HOLDOUT-DTI",
    "evaluator": "gems57-pooled-hide-v2",
    "withheld_positive_pixels": 60988,
    "dti": 0.14886666599413936,
    "ci95": [0.13683485419346192, 0.1603826679811272]
  },
  "registry_comparison": {
    "scope": "45 pinned discrete peers plus literal 695-raster witness/bound; not exhaustive/global",
    "max_abs_spearman_surface": 0.11399814751949117,
    "max_abs_spearman_final_dots": 0.05443126538084839,
    "external_focus_topk_overlap": 0.6927285281776172,
    "external_focus_final_overlap": 0.5702979763106177,
    "local_discrete_topk_overlap": 0.8497636373293674,
    "local_discrete_final_overlap": 0.6055930312848569,
    "literal_lattice_final_overlap": 0.9828437881765549,
    "literal_lattice_lower_bound_at_37654_dots": 0.8234184947150369
  },
  "raster_sha256": "d272d5babb9523a70f77e76ad6843830d67a9eabaaa60f8c3f46ca57bde9a1ef",
  "validator": {
    "all_finite_tif": "PASS: 0 NaN/Inf in footprint; all values in [0,1]; EPSG:32611; shape 3730x3292; transform matches; float32 one-band",
    "format_validity_is_not_submission_permission": true
  },
  "submission_name": "gemsdoe31-h31aa-slfs-flexure-37654-20261027-fdb34746",
  "submission_note": "H31-AA AA2 SLFS log-flexure+shoreline-null 37654d B2 | HOLDOUT-DTI 0.1489 n=60988 | fdb34746",
  "verdict": "negative; research-download only; DO NOT SUBMIT",
  "slot_approved": false
}
```
