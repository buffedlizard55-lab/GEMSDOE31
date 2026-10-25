# Scientific and source review — 2026-10-25

**Target: uncharted faults, not geothermal vents.** Geothermal relevance motivates the competition; neither the labels nor this experiment establish vent discovery, permeability, reservoir temperature or commercial prospectivity. The reported private leaderboard values are not available for verification here.

## What H33 actually changes

- [Pinned GEMSDOE32](https://github.com/buffedlizard55-lab/GEMSDOE32/tree/012e17b2a115c3c0d5e7885bea625bf9657c99fc), [GEMSDOE28](https://github.com/buffedlizard55-lab/GEMSDOE28/tree/78e724f95337a6528b1248be5c113c6d6d502891) and [GEMSDOE25](https://github.com/buffedlizard55-lab/GEMSDOE25/tree/0f73c51dc954306468875c02cf98634e64ac0751) supply the measured H33/H27/D2.8 files. `scripts/audit_h33.py` checks the masks, rather than believing their names.
- **RASTER-MEASUREMENT:** H33 has 37,654 positive pixels; H27 has 40,199; D2.8 has 44,090. H33 equals H27 with distance-to-catalogue ≤2 px removed, exactly. H27 equals D2.8 with distance ≤1 px removed, exactly. H33 removes 2,545 H27 pixels and adds zero. Nearest retained catalogue distance is √5 px, not exactly 2 px. Nearest predicted-dot spacing: minimum 282.84 m, median 300 m. These are geometry measurements, not performance scores.
- **INFERENCE:** A sparse representation limits redundant 300 m kernel coverage; catalogue-flank pruning may remove false-positive mass without losing much off-catalogue truth credit. No new detector or physical observation is introduced by this pruning.
- **Not identifiable from these files:** whether this caused the owner's claimed private-truth result, the live denominator/truth mass, or whether more pruning would help. An uncharted fault can lie within 200 m of a mapped one; catalogue distance is not a reliable geological absence label.

For the shared max-credit arithmetic, write `T=TPw`, `F=FPw`, `K=truth count`. Then `FNw=K−T` and `S=T/(0.2T+0.2F+0.8K+epsilon)`. Removing weighted truth credit `lost_T` and false-positive weight `removed_F` improves S iff

```
lost_T < [0.2 S/(1−0.2 S)] × removed_F.
```

This is an algebraic condition, not proof that it holds against unavailable private truth. It makes explicit the trade-off that a purely visual interpretation misses.

### Why the GEMSDOE32 calibrated proxy is not comparable

`src/gems32/live_mirror.py` at the pinned source describes its `official_dti` as official, but implements a symmetric average of truth-side and prediction-side credits with a different denominator. Its optional prevalence calibration substitutes 12,691 as an assumed hidden-truth count and averages quadrant values. That is not the unchanged shared57 pooled maximum-credit evaluator used here; a calibration fitted to owner-reported orderings does not create an organizer receipt.

`evidence/metric_instrument_audit_20261025.json` records execution of the original cached GEMSDOE32 function and the shared57 function on the same synthetic fixture (two adjacent unit predictions, one coincident truth). The arithmetic values differ (about 0.76923 vs 0.93750). **These are ARITHMETIC-UNIT-TEST outputs, not HOLDOUT-DTI, projections or organizer performance.** Source hashes and coordinates are recorded; no private metric fork is used to evaluate TGJ31.

The 0.2778, 0.3195 and 0.4413 values in the owner's request remain **USER-REPORTED-NOT-AUTHENTICATED**. The GEMSDOE32 source's calibrated projection is not an organizer-confirmed score. We cannot determine the current leaderboard high or forecast beating any of them.

## The sole new experiment: TGJ31-v1

Preregistered in commit `f6dde77` before feature implementation; implementation committed as `b9be6ef` before the run. Four exact ranked hypotheses and prior-art exclusions are preserved in `knowledge/2026-10-25_transfer_preregistration.md`. No supervised model was fitted, no old prediction was used as an input, and no other hypothesis was run.

The physical proposition is narrower than a fault detector theorem: a buried juxtaposition may change the local relation between density-sensitive gravity and susceptibility-sensitive magnetics, even without a topographic scarp or high standalone edge amplitude. RTP band 2 and isostatic-gravity-anomaly band 13 are verified against the raster's band descriptions. Median/IQR normalization is label-free. A sigma-20 regional trend is removed. Regularized local gravity-on-magnetic coefficients at sigma 3/7 px are transformed by arctan; both gradient descriptors must exceed the fixed 0.5 threshold, weighted by regularized coupling strength. The 110 px valid-data halo is conservative and leaves 3,107,957 supported output cells from 5,167,373 footprint cells. Unsupported cells predict zero but their truths are not removed from evaluation.

**Named nonfault mimic:** an unfaulted lithologic or intrusive contact; source-depth variations, remanent magnetization and survey leveling changes can also alter the observed relation. Gravity and magnetics are nonlocal potential fields. Robust normalization and local covariance do not invert for density/susceptibility, solve nonuniqueness or establish causation. The coupling descriptor is not a calibrated R-squared or fault probability. Broad smooth sources and a small confidence mass can dominate the result.

### Measured result, with its full label

**HOLDOUT-DTI (`gems57-pooled-hide-v2`, 60,988 withheld positive pixels, 95% spatial-cluster CI):** TGJ31 **0.0082809936 [0.0057409769, 0.0112344266]**. Same-input amplitude control **0.0258250764 [0.0162575600, 0.0350710906]**. Paired difference **−0.0175440828 [−0.0278254174, −0.0074018506]**, one quadrant won out of four.

The as-is H33 reference is not fold-fair: it was pruned using the full catalogue and the originating detector is not reconstructed. Its **HOLDOUT-DTI (`gems57-pooled-hide-v2`, 60,988 withheld positives, 95% spatial-cluster CI)** is **0.0066970418 [0.0058885216, 0.0074367701]**, descriptive only. It cannot satisfy the comparable-incumbent gate. The paired TGJ31−H33 interval spans zero; it supplies no evidence of private-test improvement.

Secondary diagnostic only: **HOLDOUT-DTI (`gems57-pooled-hide-v2`, 61,664 SGMC off-catalogue positives, 95% spatial-cluster CI)** is **0.0037140804 [0.0022246306, 0.0052217653]**. SGMC was never a predictor. Independent origin of a map does not make its overlapping fault labels independent geological ground truth.

All six individual feature canaries ran on every fold. Maximum symmetric AUC was 0.5712345, below the preregistered 0.90 alarm. A passing canary is necessary, not sufficient evidence of no leakage.

The controls have different confidence mass and are not a matched-mass causal ablation. The result rejects **promotion of the frozen operator**, not all coupling-based geophysics. No retuning or second experiment followed. CI resamples 30 km physical clusters 1,000 times with fixed seed 20261025; it is conditional on labels, split and parameters, not a leaderboard confidence interval. The 21.3 km buffer is inherited from historical residual analysis, not measured from a new TGJ31 residual fit. No same-run current-best reproduction or independent confirmation exists.

## New content is not a protocol-unique lane

The 101-tree pinned inventory restored 1,005 byte-distinct TIFF hashes; 286 raster paths remained unavailable. The mandatory-nine snapshot has 87 byte-distinct files; 86 have the expected grid. `GEMS36_FORMAT_TEST_NOT_SUBMISSION.tif` is off-grid and is retained as an explicit error. Neither inaccessible files nor an off-grid test are silently erased to make a passing report.

The observed mandatory-nine maximum Spearman rho across the two checks is 0.0092794. Forward overlap is at most 0.3369089 for the unplaced continuous surface and 0.3309426 after the exact catalogue-pixel mask. Those partial observations do not authorize uniqueness.

The unchanged shared `saturation_certificate` verifies that the pinned GEMSDOE48 continuous prior is positive at all **5,167,373 / 5,167,373** footprint cells. Under literal finite-value>0 dot support, every nonempty candidate in that domain has forward overlap 1.0 with this prior, failing the unchanged 0.70 limit. It is a universal mathematical blocker, not a failure of file byte uniqueness. No density exemption, ≥0.5 support threshold or reinterpretation of "dots" was applied.

The frozen continuous response was serialized as the preregistered **negative audit artifact**. There is no discrete placement stage, no coordinate optimization and no subsequent scientific attempt. Both surface and final support were checked. The new TIFF hash is absent from all 1,005 restored prior hashes, and no prior prediction entered the operator, but the file is explicitly **not protocol-unique or submission-approved**. This distinction cannot honestly be bypassed to promise a unique eligible submission.

## Claim-by-claim source ledger

| Claim | Verification / primary pointer | Limit |
|---|---|---|
| Input bytes and grid are available locally | `evidence/data_restore_20261025.json`, `evidence/data_preparation_20261025.json`, `registry/data_manifest.json` | Hash identity to public owner mirrors, not organizer authenticity. Large inputs stay out of Git. |
| Actual band order | `evidence/shared_feature_cache.json`, raster band descriptions | Interpretive metadata, not independent physical calibration. Selected RTP2/gravity13 are correctly identified. |
| Original reference solution exists | [DrivenData-owned pinned code](https://github.com/drivendataorg/gems-prize-reference-solution/tree/aebe92f7c8a990f0e3443451b7a825d9afd6336b) | A U-Net training example, not the official private evaluator. No GPU reference-model training was performed. |
| Whole segments, exact visible mask, pooled arithmetic | `vendor/gems57/spatial.py`, `evaluate_holdout.py`, `metric.py`; source hashes in `registry/shared_template.json` | Owner-published template, not organizer-authenticated evaluator. Source bytes remain unchanged. |
| Physics operator is label-free | `src/gemsdoe31/transfer.py:41–123`; implementation hashes in run card | Unlabeled whole-footprint normalization is transductive; no supervised training or source inversion. |
| H33 exact identity | `scripts/audit_h33.py`; `evidence/h33_forensics_20261025.json` | Does not identify private faults or verify 0.2778. |
| Finite [0,1], exact grid, single float32 band | Shared on-disk validator plus independent validator and ZIP receipt under `evidence/tgj31/` / `docs/downloads/` | A local preflight, not organizer acceptance. No clipping of invalid predictions. |
| Literal duplicate and STOP | `registry_surface.json`, `registry_final_support.json`, `registry_universal_blocker.json`, `STOP.json` | Incomplete registry cannot clear uniqueness; the full-support witness independently proves failure. |
| Automated negative decision | `evidence/tgj31/decision.json`, derived mechanically from frozen receipts | Research promotion and a separate slot selector remain distinct. No slots used. |
| Rules, government data and spatial-validation literature | Historical dated records in `registry/sources.json`: [official problem](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), [rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf), [GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and), [INGENIOUS](https://gdr.openei.org/submissions/1391), [Roberts et al.](https://doi.org/10.1111/ecog.02881), [Valavi et al.](https://doi.org/10.1111/2041-210X.13107) | Current egress permits GitHub/package registries only. These official hosts/PDF/papers were not re-opened this session; do not turn an old access date into fresh verification. |

## Limitations and next work

Read `knowledge/2026-10-25_next_session.md` in priority order. No private truth, receipt, live score, authenticated current cap or explicit assigned method paragraph is available. The older supervised arm trainer is missing; previous OOF artifacts do not prove a reproducible current best. Data placement is completed through hash-pinned public mirrors, not direct portal authentication. This CPU physical pipeline requires no GPU, but is not a trained version of the official reference U-Net.

A negative result with a real new finite GeoTIFF, exact provenance and a clear automated STOP is the honest outcome. It protects the probability of winning better than spending a weekly slot on a failed or mislabeled candidate.

## Concurrent upstream format review retained

Main PRs #8/#9 added an independent H33 duplicate/full-catalogue-processing audit while this run was in flight. Their full record is preserved as `knowledge/session_review_2026-10-25.md` and the earlier status as `knowledge/upstream_current_status_2026-10-25_pre_TGJ31.md`. Their missing-data conclusion describes a separate checkout, not the restored data here. Their H33 zero-outside warning is not discarded: historical official text describes null/NaN outside bounds, whereas the mandatory shared writer uses explicit all-finite zeros outside its footprint. The precise portal convention has not been re-authenticated. The new artifact's local PASS is limited to its declared all-finite validator policy; it is not organizer format acceptance. We did not change encoding after the duplicate STOP or generate another variant.
