# Current repository and artifact review — 29 October 2026

**Branch:** `arena/9f242e65-gemsdoe31`
**Decision: DO NOT SUBMIT.** No new TIFF or experiment was generated; no slot was used; no DrivenData page was accessed, polled, or contacted. The current method paragraph is absent, the production feature stack is not restored, and the canonical release register is negative. The two pre-existing CSDU/H-STEO archive artifacts were audited read-only. One is invalid on the actual template; the other fails the literal 3-pixel registry gate.

This review uses the owner-mirror bytes pinned by this project. Hashes prove identity to those mirrors only, not organizer authentication. One hash-pinned registry counterexample suffices for the literal STOP but does not establish a global uniqueness pass.

## Decision at a glance

| Item | Evidence-qualified result | Decision |
|---|---|---|
| New experiment in this review | 0 | None authorized or run |
| New TIFF in this review | No | No file created |
| Current canonical release status | `registry/release_status.json`: negative; `ok_to_submit=false`; `slot_approved=false`; no assigned method lane | Remains binding |
| H-STEO archive | Format check passes against the pinned mirror template; 9,135/9,140 (99.9453%) final dots are within 3 px of one hash-pinned registered lattice. Pre-placement hard-mask support overlap is 99.9650%. | Literal overlap STOP; not unique, not submit-ready |
| CSDU archive | Generator used a synthetic ellipse footprint and all-zero labels; actual-template checks fail for both encodings. | Invalid as a competition-grid artifact; uniqueness not evaluated |
| Holdout / leakage canary | Neither H-STEO nor CSDU has a valid HOLDOUT-DTI/95% CI or single-feature canary in this review. | Not run; no score estimate |
| New-file leaderboard estimate | None supported | `null`; do not invent one |
| Submission / organizer score | No upload, slot or receipt | None; no organizer-confirmed score |

Machine-readable details: [`evidence/review_9f242e65/run_card.json`](../evidence/review_9f242e65/run_card.json). The card distinguishes the two archive files from work performed in this review (`experiments_run_in_this_review=0`, `new_tif_generated_in_this_review=false`).

## Nine requested site comparison

The table below carries forward the pinned nine-site audit. Scores are **USER-REPORTED**, not organizer-confirmed. Each file is linked at the exact owner-repository commit used by the audit; the link is for study, not submission. The historical audit found all 36 pairwise comparisons duplicate by the >70% 3-px-overlap rule (minimum pairwise maximum overlap 0.97313); no site file is unique under that comparison. New-file estimates are unavailable.

| Site | Highest reported value in the pinned focus register | Pinned file to inspect · direct download (research/prior-art only) | Unique? | New-file estimate |
|---|---:|---|---|---|
| GEMSDOE24 | 0.2477 | [gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif](https://github.com/buffedlizard55-lab/GEMSDOE24/blob/544fe988df1b8a1b16f249a28be3fc3b3ff378a0/docs/downloads/gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif) · [direct download](https://github.com/buffedlizard55-lab/GEMSDOE24/raw/544fe988df1b8a1b16f249a28be3fc3b3ff378a0/docs/downloads/gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif) | No; overlaps all 8 other focus files | Unavailable |
| GEMSDOE25 | 0.2600 | [gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif](https://github.com/buffedlizard55-lab/GEMSDOE25/blob/2a279dd0d2a4319c1022567876eb4c97553e2d13/docs/downloads/gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif) · [direct download](https://github.com/buffedlizard55-lab/GEMSDOE25/raw/2a279dd0d2a4319c1022567876eb4c97553e2d13/docs/downloads/gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif) | No; overlaps all 8 other focus files | Unavailable |
| GEMSDOE27 | 0.2449 | [gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif](https://github.com/buffedlizard55-lab/GEMSDOE27/blob/c79609503619559b5a2c53116e87fce646bc4235/docs/downloads/gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif) · [direct download](https://github.com/buffedlizard55-lab/GEMSDOE27/raw/c79609503619559b5a2c53116e87fce646bc4235/docs/downloads/gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif) | No; overlaps all 8 other focus files | Unavailable |
| GEMSDOE28 | 0.2710 | [gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif](https://github.com/buffedlizard55-lab/GEMSDOE28/blob/178c65378e1adaaabe45d944fd63b7cd284bff4f/docs/downloads/gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif) · [direct download](https://github.com/buffedlizard55-lab/GEMSDOE28/raw/178c65378e1adaaabe45d944fd63b7cd284bff4f/docs/downloads/gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif) | No; overlaps all 8 other focus files | Unavailable |
| GEMSDOE30 | 0.2600 | [gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca-nanoutside.tif](https://github.com/buffedlizard55-lab/GEMSDOE30/blob/ccc5e4e35b76d2fbe66c25782d9a3c805d796dbb/docs/downloads/gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca-nanoutside.tif) · [direct download](https://github.com/buffedlizard55-lab/GEMSDOE30/raw/ccc5e4e35b76d2fbe66c25782d9a3c805d796dbb/docs/downloads/gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca-nanoutside.tif) | No; overlaps all 8 other focus files | Unavailable |
| GEMSDOE31 | 0.2708 | [gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif](https://github.com/buffedlizard55-lab/GEMSDOE31/blob/4371416853904713760b86db0dccd9afe50d776f/docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif) · [direct download](https://github.com/buffedlizard55-lab/GEMSDOE31/raw/4371416853904713760b86db0dccd9afe50d776f/docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif) | No; overlaps all 8 other focus files | Unavailable |
| GEMSDOE32 | 0.2778 | [gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-nan.tif](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/9863c82a7c7dc283c615b711bab941debaff0ec4/docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-nan.tif) · [direct download](https://github.com/buffedlizard55-lab/GEMSDOE32/raw/9863c82a7c7dc283c615b711bab941debaff0ec4/docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-nan.tif) | No; overlaps all 8 other focus files | Unavailable |
| GEMSDOE33 | 0.2632 | [GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e-nanoutside.tif](https://github.com/buffedlizard55-lab/GEMSDOE33/blob/f618cc54773bd9b4d6c2b3ebf78103a05cc10cb6/docs/downloads/GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e-nanoutside.tif) · [direct download](https://github.com/buffedlizard55-lab/GEMSDOE33/raw/f618cc54773bd9b4d6c2b3ebf78103a05cc10cb6/docs/downloads/GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e-nanoutside.tif) | No; overlaps all 8 other focus files | Unavailable |
| GEMSDOE36 | 0.2750 | [gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-nan.tif](https://github.com/buffedlizard55-lab/GEMSDOE36/blob/c9ad59ec6f969ed931d089a03044c1567a633e84/docs/downloads/gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-nan.tif) · [direct download](https://github.com/buffedlizard55-lab/GEMSDOE36/raw/c9ad59ec6f969ed931d089a03044c1567a633e84/docs/downloads/gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-nan.tif) | No; overlaps all 8 other focus files | Unavailable |

The values and file pins are in `registry/session_cc130eb1_decision.json` and `evidence/review_cc130eb1/focus_site_verification.json`. The 0.2449 GEMSDOE27 row is a pinned historical claim; other repository notes have different GEMSDOE27 claims, so attribution remains unresolved. GEMSDOE25's 0.2600 and GEMSDOE31's 0.2708 also have owner-record conflicts. None has an organizer receipt.

### Why H33-2-B2 is reported at 0.2778

A later hash-pinned byte-forensics audit integrated from `evidence/review_48c411be/gemsdoe32_forensics.json` establishes the raster lineage: H33-2-B2 is exactly the D2.8 raster after removing 6,436 catalogue-adjacent dots (all within 2 px), leaving 37,654 dots from 44,090; its zero and NaN variants have identical in-footprint dots. A 1 px prune exactly matches the H27-4 file (40,199 dots); 1.5 px produces an unregistered 38,998-dot raster; 3 px leaves 35,483 dots, all within 3 px of H33-2-B2. This is **COMPUTED from pinned raster bytes** and does not verify any score.

The plausible performance explanation is that removing low-marginal-credit catalogue-adjacent cells reduced false-positive cost while retaining most triangular-kernel credit. Under the reported asymmetric metric (0.2 false-positive weight, 0.8 false-negative weight), that can improve DTI if saved false-positive cost exceeds lost kernel credit. This is **INFERENCE**, not evidence that those cells were false positives on private truth or that pruning caused the reported value. The 0.2778 remains USER-REPORTED; H33 is prior art, not a unique or submit-ready file. The conflicting 0.3195 and 0.4413 user anchors remain unverified. See [`registry/session_48c411be_addendum.json`](../registry/session_48c411be_addendum.json) for the additional audit record.

## Archived artifact integrity findings

### H-STEO — format-valid, but duplicate STOP and scientific label overstated

- File: [`gemsdoe31-h-steo-offcatalogue-stepper-20261029T164949Z-4bbba08696ed-nan.tif`](../docs/downloads/gemsdoe31-h-steo-offcatalogue-stepper-20261029T164949Z-4bbba08696ed-nan.tif), SHA-256 `aadbcd5398fccfc402c8358c5b87ba0d922b6eeb90f4932b5bbdf4fde0e18e89`.
- The existing NaN-outside and all-finite twins pass local shape/CRS/transform, float32, range and footprint validation against the pinned **owner-mirror** sample. The `.zip` roundtrip is byte-checked. These are format-only facts, not organizer acceptance.
- Read-only replay exactly reproduces 9,140 final dots from the pinned public catalogue and template. The reconstructed pre-placement mask contains 465,907 pixels; 465,744 are within 3 px of the registered control (99.9650%). Before the exact-lattice filter, 9,534 7×7 grid candidates include 394 exact spacing-5 intersections; after filtering, final support has zero exact intersections but 9,135/9,140 (99.9453%) are still within 3 px.
- Full-footprint pixel and 5-px-block Spearman correlations are small (absolute maxima 0.0031 for the pre-placement mask and 0.0086 for final dots). They do not override the literal >70% overlap STOP.
- The control is `GEMSDOE24@07345ea0604953d7efb858d9cfbc21e20c7aca0b:inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif`, SHA-256 `b4570b406efec198eb2f4d142ad8d0d6184b14b66f2f52b5c4d697f0647dc9b2`. It is one hash-pinned member of a 695-raster owner-mirror manifest. This is enough for STOP; coverage is not exhaustive and no global uniqueness pass is claimed.
- The old run card's `spacing_5_lattice_overlap: 0.0` describes exact shared cells only, not the required 3-px buffer. The claimed 7×7 offset alone does not mathematically avoid a 5×5 lattice: the original code explicitly removed 394 exact intersections. The 22,000-dot cap was below a budget-specific counting bound; that density choice does not establish uniqueness and cannot waive the measured 3-px STOP.
- Method-label issue: the preserved generator dilated/eroded the public catalogue mask and placed dots on a 7×7 grid. It did not test for two strands, use an independent geophysical/topographic layer, or construct a stepover-specific feature. `min_separation_px` was not used. The “stepover” mechanism is not demonstrated.
- No HOLDOUT-DTI, withheld-positive count, CI, leakage canary or new-file score estimate exists. `scripts/generate_unique_submission.py` is now an explicit no-write retired stub so the archive cannot be regenerated or density-tuned after STOP.

### CSDU — synthetic, invalid on the actual submission footprint

- Archived file stem: `gemsdoe31-csdu-stepover-8cf9dc27` (originally described as four thousand concealed stepover dots).
- The historical generator code created a synthetic ellipse approximating the competition footprint ratio and an all-zero catalogue. It did not use the pinned `sample_submission.tif` or public `labels.tif`. The historical CSDU run card's `dots_on_public_catalogue: 0` is therefore a statistic of synthetic all-zero labels, not the actual public catalogue.
- Rechecking the existing bytes against the actual pinned template finds 4,000 total positive cells, 2,101 inside the true footprint and **1,899 outside**. The all-finite twin fails the actual-template outside-zero check. The NaN-outside twin has **2,610,312 NaN/Inf cells inside** the true footprint and 2,723,988 finite cells outside it; it fails multiple hard checks. Neither format convention passes.
- The card's uniqueness-by-construction claim is unsupported: no registry comparison was run. Because the raster is not a valid candidate footprint, uniqueness was not measured in this review.
- `scripts/run_unique_stepover_submission.py` is now an explicit no-write retired stub. Existing synthetic bytes are retained with a warning for provenance; do not repair them, resubmit them, or treat their grid metadata as competition-grid validity.

## Untested geological hypotheses

Four distinct desk leads are ranked in [`knowledge/hypotheses_2026-10-29_arena-9f242e65.md`](hypotheses_2026-10-29_arena-9f242e65.md): (1) thermal-site/structural-axis alignment, (2) World Stress Map stress-orientation prior, (3) focal-mechanism nodal-plane alignment, and (4) SMU heat-flow residual. Each names a non-fault mimic, novelty boundary, qualitative expected gain, cost, source link and failure mode. The source layers were **not obtained or re-verified** in this session; none is presently viable. The external hosts are outside the allowed outbound network path. No experiment ran because no method paragraph was assigned and the duplicate STOP remains.

If a future prompt authorizes a lane, it must follow the shared-evaluator protocol in the hypothesis note and active owner brief: whole-segment buffered hide-and-recover, catalogue features from visible faults only, exact masking of visible faults, pooled DTI alpha 0.2/beta 0.8 with the 300 m triangular kernel, per-feature leakage canary, a named non-fault mimic, 95% CI and pre-/post-placement literal uniqueness gate. Do not choose a slot; stop at three experiments or two hours.

## Source/access boundary

Manual-review links are maintained in `README.md`, `knowledge/owner_prompt_2026-10-29_arena-9f242e65.md`, and the hypotheses note: DrivenData problem/rules, official reference solution, INGENIOUS, WSM 2025, NBMG geothermal descriptions, SMU heat-flow record, USGS ComCat, and the static leaderboard. **No web page was freshly fetched in this session.** Repository GitHub byte pins and local raster checks were used; non-GitHub source availability, license, live leaderboard, organizer receipts and weekly quota were not newly verified. Do not scrape/poll the leaderboard or upload.

## Three review passes

1. **Implementation / evidence pass:** read the current project instructions, README/charter, current release register, historical `current_run`, and prior review/focus registers. Restored only pinned small validation inputs and the one registered lattice witness. Added a deterministic read-only audit and reproduced the H-STEO mask exactly; revalidated both H-STEO twins and both CSDU twins against the real pinned template. No production stack, feature cache, TIFF, fit or holdout was generated.
2. **Independent assumptions / defect pass:** checked the 7×7 versus 5×5 congruence claim, exact versus 3-px overlap, method specificity, density-bound interpretation, saved run-card claims, synthetic CSDU input generation and real-footprint counts. Confirmed that a single registered witness is enough for literal STOP but not an exhaustive uniqueness pass. Disabled both unsafe legacy generators with regression tests. Rechecked that no official source/leaderboard/organizer receipt was accessed.
3. **Whole-request acceptance pass:** reconciled the nine-site comparison, H33 explanation, four ranked hypotheses, source links, score evidence classes, release status, guide/README, site/feed and automated gates. No new-file estimate or submission approval is supported. Tests and generated-site checks are recorded in `registry/review_passes.json` after completion.

## Current verified decision and next step

`registry/release_status.json` remains the canonical negative release card for H31-CC; `registry/current_run.json` is a historical MAGREST record. Neither is permission to submit. The new archive review only adds evidence that H-STEO also fails the literal overlap gate and CSDU is invalid on the actual footprint. Keep all archived outputs research/audit-only.

Next step is not a new run. First obtain an explicit assigned method paragraph and an authorized, hash-pinned feature stack; verify the external source product and terms; preregister one lane; run the shared evaluator and writer only after a complete pre-placement uniqueness gate passes. A fresh positive blocked holdout with confirmation and a separate selector decision would still be required before any slot. Keep all work on `arena/9f242e65-gemsdoe31`; any PR/merge status is reported only after GitHub confirms it.
