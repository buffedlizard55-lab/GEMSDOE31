# Executive repository review — 29 October 2026

Branch: `arena/a668bcb6-gemsdoe31`. **No file is approved to submit. No new TIFF, geological experiment, selector choice, slot or upload in this review.** A negative deliverable is required by the parallel protocol; creating another file after a duplicate STOP would violate it.

## Actionable decision

The existing [H31-CC all-finite research TIFF](../docs/downloads/gems31-h31cc-basement-step-37654d-20261028-zeros.tif) remains available for research only, **DO NOT SUBMIT**. Its exact-byte read-back passes local format checks, not organizer acceptance. It is not a new file or a recommendation from this session.

- SHA-256: `0e82a9e8b80052d0bc61e8f550b2ac5204d012ab1f53fb2208051f285f10ad44`.
- **CITED HOLDOUT-DTI**: 0.0470699, 95% CI [0.0332317, 0.0618164], evaluator `gems57-pooled-hide-v2`, 60,988 withheld positives. Paired versus same-run NULL: −0.0096697 [−0.0234561, +0.0052007]. Historical result, not retrained here; not a leaderboard estimate.
- **COMPUTED this review**: final dots within 3 px of the pinned registered spacing-5 witness: 37,508/37,654 = 99.6123%, failing the literal 70% gate. Binary-dot rank correlation ≈−0.0000768 does not negate the failing overlap. Only one registered witness rechecked, not an exhaustive scan. Surface results are cited from the frozen card, not rerun.
- **COMPUTED format validation** against pinned owner-mirror sample: one float32 band, EPSG:32611, 3730×3292, exact affine transform, all values finite in [0,1] for the zero-outside twin; no NaN inside the footprint. ZIP matches the single TIFF. Organizer authentication and acceptance remain unavailable.
- New-candidate leaderboard estimate: **unavailable**. The missing single-method paragraph, literal STOP, negative scientific evidence and absent selector/quota approvals prohibit claiming submission readiness.

[Canonical status](../registry/release_status.json) · [automated exact-byte verifier](../scripts/verify_h31cc_run.py) · [frozen scientific card](../evidence/h31cc/run_card.json) · [generated executive guide](../docs/executive-summary.html).

## Nine-site executive comparison

These are the highest **USER-REPORTED** values supplied for the focus sites, not ORGANIZER-CONFIRMED receipts or current live standings. Links open commit-pinned prior-art downloads through the existing table. All are old submissions, not unique new deliverables. No file here is selected for upload.

| Site | Highest supplied historical file identity | USER-REPORTED claim | New-file estimate | Unique new / submit? |
|---|---|---:|---|---|
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan` | 0.2477 | Unavailable | No / No |
| GEMSDOE25 | `dotted-h19-5-d2-8-20261002-e56ea318af89-nan` | 0.2600 | Unavailable | No / No |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan` | 0.2449 | Unavailable | No / No |
| GEMSDOE28 | `h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan` | 0.2710 | Unavailable | No / No |
| GEMSDOE30 | `d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca` | 0.2600 | Unavailable | No / No |
| GEMSDOE31 | `h27-4-solo-d28-20261004-8acb75e1-nan` | 0.2708 | Unavailable | No / No; unscored-page conflict unresolved |
| GEMSDOE32 | `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` | **0.2778** | Unavailable | No / No; highest of nine supplied claims |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30-20261004-cb490425926e` | 0.2632 | Unavailable | No / No |
| GEMSDOE36 | `anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros` | 0.2750 | Unavailable | No / No |

Exact source filenames sometimes have site prefixes/aliases. Use the **full paths, SHA-256 and pinned URLs** in the [executive table](../docs/executive-summary.html#nine-site-decision) and [focus register](../registry/focus_review.json), not an alias to identify download bytes. The separate newer GEMSDOE92 0.2784 claim in this prompt is USER-REPORTED, outside the nine-site focus, and exceeds 0.2778; therefore H33 is not the highest supplied claim across all sites. Conflicting 0.3195/0.4413 leaderboard anchors remain unverified.

**Freshness irregularity:** GitHub metadata was actually fetched this review: all nine focus repository HEADs differ from the pinned artifact revisions. This establishes drift, not that files or results changed. Current remote raster inventories and score receipts were not re-audited. See [timestamped source receipt](../evidence/review_a668bcb6/source_access.json). No DrivenData contact or leaderboard retrieval occurred.

## Why H33 may work, without invented private-truth attribution

The pinned [H33 forensic evidence](../evidence/h33_forensics_20261025.json) reports pruning of near-catalogue dots from an older dotted field, not an independent new geological detector. Under the supplied α=0.2, β=0.8, 300 m triangular-kernel metric, redundant predictions may add false-positive cost without adding nearby truth coverage. Removing them may improve DTI. This is a plausible **INFERENCE**, not proof of which private positives were hit, a causal score explanation, or a guaranteed route beyond 0.2778.

For fixed truth mass N, `S=T/(0.2*T+0.2*F+0.8*N+epsilon)`. With positive denominators, the exact finite-change improvement condition is `(1−0.2*S)*delta_T > 0.2*S*delta_F`. This algebra is **COMPUTED**, not a calibrated prediction. Existing sign tests independently check it. Further catalogue pruning can also remove true hidden-fault coverage; blindly copying/tuning H33 is neither a new lane nor justified by the metric.

The actual competition target is fault mapping, not direct vent detection. Geothermal-process covariates can inform hypotheses but must not substitute geothermal favorability for the evaluated fault label.

## Ranked hypotheses — desk-only, not new fits or assigned lanes

These exact variants remain unfit in the checked local runner/evidence inventory. They refine prior proposed directions rather than claiming global novelty. Expected DTI benefit is a **qualitative planning judgment**, not a forecast; no numeric improvement is supportable before validation. No external dataset is asserted obtainable when it was not fetched.

| Rank / expected benefit / cost | Layers and exact physical signature | Why potentially off-catalogue / difference from implemented work | Named non-fault mimic / feasibility |
|---|---|---|---|
| 1 / moderate relative potential, low confidence / medium | B17 `cond_surf`, B15 `depth_to_base_surf`, GeoDAWN K/Th; signed opposing gradients across a horst flank, with a conductivity-boundary and alteration coincidence | Buried basement/alteration juxtaposition without a mapped scarp; adds signed polarity/alteration conditioning rather than H31-CC's low-slope unsigned basement/gravity conjunction or HVDC's broader fusion | Saline playa clay, evaporites, depositional pinch-out. Coarse conductivity may not localize at kernel scale. Pinned mirrored inputs exist in the manifest but production cache is absent here; official provenance not newly authenticated. |
| 2 / low–moderate relative potential, low confidence / medium–high | RTP magnetics B2 and isostatic gravity B13; reciprocal signed lateral offsets across an orthogonal corridor, with unbroken-contact null | Concealed transfer-fault displacement rather than simple gradient strength; differs from MAGREST same-field restoration and XFCOH31 gradient coherence | Pluton/caldera margins, volcanic contacts, survey seams. Use existing layer family only; no new external data assumed. Exact signed cross-field phase operator is not an executed runner. |
| 3 / low–moderate relative potential, low confidence / high | Existing 10 m DEM: paired catchments matched on drainage area/relief; difference-in-differences of normalized channel steepness, leave-one-channel-out consistency | Relative uplift across an unrecorded structure, not merely H31-X piedmont slope-break, H31-AA flexure or single scarp magnitude | Lithologic erosion contrast, fan incision, paleolake base-level change. Existing DEM mirror metadata is documented; do not call this runnable until tiles/cache and coverage pass. Additional tiles would require USGS 3DEP, outside current network allowlist, so acquisition-dependent implementation is blocked, not viable now. |

References for these unfit directions and prior-art boundaries: [previous ranked review](repo_review_2026-10-28_arena-41e3ba3f.md), `scripts/run_h31cc.py`, `scripts/run_magrest.py`, `scripts/run_xfcoh31.py`, `scripts/run_h31x.py`, and `scripts/run_h31aa.py`. These are hypotheses, not verified geological discoveries. No top candidate is validated or selected because the prompt does not assign its promised method lane and the literal STOP remains binding. Do not spend a weekly slot.

## Concrete bugs fixed

1. **False approval:** `scripts/submission_writer.py::write_validated_submission_variants` previously set `ok_to_download_and_submit` directly from two format checks. That omits scientific efficacy, two-stage uniqueness, provenance, fresh confirmation, selector authorization and current weekly cap. Both legacy wrapper receipts now explicitly deny upload/slot approval and label format-only versus research download separately.
2. **Packaging after STOP:** the common local legacy builder and both local wrappers now consult `registry/release_status.json` before writing output, reject absent/malformed policy, missing lane, incomplete diagnostics, duplicate stages and inconsistent decisions. No CLI/environment bypass is introduced. CLI paths stop before reading missing production inputs. Scientific negatives may still be research-packaged after authorized two-stage uniqueness passes; no positive efficacy result is required for a research file.
3. **Unsupported quota/human dependency:** removed the legacy writer's unverified fixed weekly-cap claim and “human selector” language. A separate selector/current-cap check is still required, but human inspection is not a substitute for software validation.

These are **legacy local-wrapper fixes**, not a private fork of the pinned template. `vendor/gems57/evaluate_holdout.py` and `vendor/gems57/submission_writer.py` remain unchanged. The pinned upstream writer is a format serializer, not a canonical policy consumer; other historical runners that directly use it remain archival, not authorized entry points. This change does not claim an OS-level ban on arbitrary raster writes. Use canonical authorization and the pinned shared tools only for a future assigned lane.

## Three review passes and limitations

**Pass 1:** read recurring README/AGENTS and existing release/scientific evidence; restored only hash-pinned small sample/catalogue/witness inputs; reran existing H31-CC exact-byte validator; fetched official reference README and nine owner HEAD metadata; fixed local-writer false approval and STOP bypass. No feature stack restoration or fits.

**Pass 2:** synthetic tests cover malformed/missing registers, strict booleans, each stage's threshold failures, exact threshold equality, incomplete registry coverage, stale decisions, valid negative-research semantics, no output before STOP, and caller-supplied promote flags not granting upload. An initial metadata collection used the wrong schema key (`repo` instead of `repository`); corrected it and consolidated repeated site rows before publication. No failed collection was described as complete. No synthetic TIFF was generated by the new tests.

**Pass 3:** full tests, Ruff, compile, metric/marginal checks, small-input/historical verifiers, canonical release check, evidence collection, deterministic site build and local link checks. Final exact check counts are in the session run card/review register. Canonical H31-CC scientific status and existing TIFF/ZIP bytes remain unchanged. Main changes from PRs #64 and #65 are integrated on this session branch; no other branch was checked out. The first merge attempt was rejected after parallel PR #65 landed during CI. README/session records were both preserved, the artifact inventory and site regenerated, and the integrated suite passed 255 tests. The inherited `audit_download.py` command returned exit 2 (VERIFIED_DENIAL), not an approval. Static checks passed on 22 pages and 552 local links.

**Not fulfilled / blocked:** no new unique submission-ready TIFF; no fresh geological screen or canaries; no calibrated leaderboard estimate; no organizer-authenticated receipt, quota or acceptance; no exhaustive current nine-site/broad-registry raster audit. Static source links do not establish current source availability. The registered-control count bound is budget-specific (82.34% minimum at 37,654 dots), not impossibility for all nonempty rasters; density changes must not evade it.

## Sources actually verified versus links for later review

- **OFFICIAL, fetched:** [organizer reference README at exact commit](https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/README.md); [stored bytes](../evidence/review_a668bcb6/official-reference-README.md), SHA-256 in the source receipt. It specifies CPU-only as an option and GPU as faster, contradicting the blanket “GPU needed” claim in the preserved prompt. The notebook was not trained here.
- **OWNER-MIRROR metadata, fetched:** nine owner repository HEADs plus Pages API configuration/status, timestamped in the receipt. At retrieval Pages was building from `main` root; this is not proof this branch's update was deployed.
- **Not fetched / outside allowed hosts:** [official problem/metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), [rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf), [GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and), [INGENIOUS GDR1391](https://gdr.openei.org/submissions/1391), [USGS 3DEP](https://www.usgs.gov/3d-elevation-program), [EPSG:32611](https://epsg.io/32611). No fresh official-data availability claim is made.

## Next-session priority order

1. Resolve the absent method paragraph and dense-control definition with the protocol owner. Do not silently exempt a registry raster or alter density. This policy conflict cannot be solved by another fit.
2. Refresh and hash-pin the nine-site and broad-registry rasters; all focus repository HEADs have drifted. Keep scores USER-REPORTED until exact-file organizer receipts exist. Resolve GEMSDOE31's unscored attribution and H27 lineage count discrepancy.
3. Only after authorization, restore/hash-check shared cache; preregister one method with candidate-specific empirical dependence/buffer; run single-feature canaries; compare same-run incumbent using whole-segment visible-only holdout, pooled DTI and spatial CI; require untuned confirmation and discovery evidence. Stop by the three-experiment/two-hour budget.
4. Independently audit all historical direct-to-template packaging entry points before future reuse; canonical release/selector remain the only permission sources. Never use a format receipt to select a slot.
5. A separate selector verifies exact file, rules, current quota and account eligibility. The project does not auto-upload or scrape/poll the leaderboard. Retain organizer receipts for later calibration instead of pretending proxy-to-leaderboard extrapolations are validated.

Maximize P(Win): don't consume scarce slots on duplicate or negative evidence. Own the Outcome: fix false approvals and make automated denial reproducible, while stating clearly that the desired winning TIFF is not yet delivered.
