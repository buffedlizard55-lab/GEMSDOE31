# Executive release review — 26 October 2026

## Download and decision first

**RESEARCH DOWNLOAD: YES. COMPETITION SUBMISSION: NO. No current file is approved.**

- [Existing H31-X all-finite TIFF — DO NOT SUBMIT](../docs/downloads/gemsdoe31-h31x-piedmont-junction-37654-20261026-5a956da9-zeros.tif)
- [Current release status / JSON run card](../registry/release_status.json) · [public copy](../docs/downloads/current-release-status.json)
- [Nine-site executive summary, artifact links and submission instructions](../docs/executive-summary.html#focus-sites)

This continuation audits existing bytes, not a new scientific lane. **No new unique submission TIFF is delivered.**
The prompt's instruction to stop at a registry duplicate takes precedence over continuing to package after that STOP.
No fit, new raster, upload, leaderboard access or weekly slot was used. A changed filename or encoding is not a new discovery.
The single method paragraph referenced in the parallel protocol is absent; no lane was silently self-assigned.

## Highest listed claim at each requested site

These values are **USER-REPORTED**, not ORGANIZER-CONFIRMED, not new HOLDOUT-DTI, and not estimates.
They index the largest historical claim in the supplied prompt for each site. Exact TIFF filenames, full hashes,
commit-pinned GitHub artifact links and overlap measurements are in [the focus register](../registry/focus_review.json).
Every row is prior art, not an upload recommendation. **Validated new-entry leaderboard estimates are unavailable.**

| Site | Highest listed historical artifact | USER-REPORTED result | Unique new entry? | Download / submit action | Validated new-entry estimate |
|---|---|---:|---|---|---|
| GEMSDOE24 | H25-1 dotted H19-5 D1.5 | 0.2477 | No; existing H33-related dot family | Prior-art study only / do not submit | Unavailable |
| GEMSDOE25 | dotted H19-5 D2.8 | 0.2600 | No; existing H33-related dot family | Prior-art study only / do not submit | Unavailable |
| GEMSDOE27 | topo-gap-closure T-v2 on D1.5 | 0.2449 | No; existing H33-related dot family | Prior-art study only / do not submit | Unavailable |
| GEMSDOE28 | H36-1 rung30 blind R1 | 0.2710 | No; existing H33-related dot family | Prior-art study only / do not submit | Unavailable |
| GEMSDOE30 | D28 Poisson300m offcat 44090 | 0.2600 | No; existing D2.8 lineage | Prior-art study only / do not submit | Unavailable |
| GEMSDOE31 | H27-4 solo D28 | 0.2708 | No; legacy reference | Existing H31-X research link above / do not submit | Unavailable |
| GEMSDOE32 | H33-2-B2 | 0.2778 | No; already existing D2.8 prune | Prior-art study only / do not submit | Unavailable |
| GEMSDOE33 | H33D analog tip-stepover R30 | 0.2632 | No; existing H33-related dot family | Prior-art study only / do not submit | Unavailable |
| GEMSDOE36 | Anderson geothermal PINN 38854 | 0.2750 | No; existing H33-related dot family | Prior-art study only / do not submit | Unavailable |

These are not fresh website maxima. All nine current main HEADs differ from the older raster-inventory pins:
[fresh GitHub metadata receipt](../evidence/review_bf9d261d/source_checks.json). A HEAD lookup does not validate changed
rasters; no exhaustive current uniqueness pass is claimed. Unscored GEMSDOE27 H31-DRCG-WL cannot be ranked as a scored winner.
The prompt's conflicting 0.3195 and 0.4413 claims do not establish a verified current leaderboard target.
This PR changes GEMSDOE31 only, not the other eight repositories.

## Why GEMSDOE32 may have performed well — and what is not known

**COMPUTED historical geometry, cited rather than reconstructed this session:**
[H33 forensics](../evidence/h33_forensics_20261025.json) and [lineage](../evidence/prior_lineage_20261025.json)
identify H33-2-B2 as the D2.8 support with a two-pixel public-catalogue exclusion.
Sparse, spaced predictions may reduce redundant false-positive cost under a finite-radius kernel;
catalogue-flank pruning may avoid predictions near already mapped faults. Neither mechanism identifies
which removed points were false positives on private truth. The reported score alone cannot prove causality.

For fixed truth count N, `S = T / ((1-beta)T + alpha*F + beta*N + epsilon)`.
With positive denominators, improvement requires
`[1-(1-beta)S]*delta_T > alpha*S*delta_F`.
This favors added nonredundant true coverage relative to its FP cost, not arbitrary densification.
[Independent algebra regression](../scripts/check_marginal_dti.py) verifies the finite-change criterion.
This is an algebraic result, not a score projection.

Can a different detector exceed the reported 0.2778? **Unknown.** Prior H31-X evidence is
**HOLDOUT-DTI 0.166133, 95% CI [0.149858, 0.182107], `gems57-pooled-hide-v2`, 60,988 withheld positives**,
cited from its original card, not retrained/reproduced in this session. It is not directly comparable to a private
leaderboard score. Its win against its own control does not establish a win over a same-run retrained global incumbent.
The fixed prior dot files had been pruned against the full catalogue and are handicapped as hide-and-recover comparators.
Cross-family forecasts from the related H33/D2.8 anchors are unvalidated; the current estimate is **null**, not an optimistic number.

## Fresh automated findings

1. **Format/range:** common validator re-reads H31-X and the hash-pinned sample mirror. One float32 band;
   EPSG:32611; shape 3730 × 3292; exact 100 m affine transform; zero NaN/Inf in the footprint; values in [0,1];
   zeros outside for the explicitly named all-finite encoding. No hard format failures. This handles the reported
   range-error class locally, not proof of portal acceptance or the cause of the earlier rejection.
2. **Literal registry STOP:** final-dot overlap against the hash-pinned registered spacing-5 lattice is **99.344%**;
   absolute full-footprint rank correlation **0.000910** (COMPUTED diagnostics, not scores).
   Prior surface diagnostics remain **CITED**: top-K overlap **86.310%**, absolute rank correlation **0.125451**.
   The original surface array is absent. No full surface replay or full-registry pass is claimed.
3. **Before-fit counting preflight:** the lattice halo leaves **6,649** cells outside on a **5,167,373**-cell footprint.
   For N distinct dots, overlap is at least `max(0,N-6649)/N`. For **37,654** dots this is **82.3418%**,
   already above the literal 70% limit. The new utility uses integer arithmetic for the strict boundary and is
   exhaustively checked against every subset on small footprints. This is a necessary-only bound, not a claim that
   every nonempty raster is impossible or proof of actual copying. Do not relocate points merely to evade the test.
4. **Permission conflict repaired:** `registry/review_passes.json` still called H31-X promoted, while the selector
   and site denied it. That text is preserved as history. `registry/release_status.json` is now the versioned current
   review/permission front door; scientific cards remain immutable history. The top download, feed JSON and feed HTML
   now identify the same artifact and cited evidence. MAGREST stays explicitly historical.
5. **Legacy approval bypass repaired:** `submission_gate.py` / `gemsdoe31.gate` could emit `READY_TO_SUBMIT` from
   weaker, density-exempt block-rank diagnostics and a promote flag. They now fail a hard protocol gate and cannot
   issue upload permission. Historical receipts are not rewritten. This is a local release-tool defect, not a
   discovered defect in or a private fork of the shared scientific evaluator/writer; those files remain unchanged.
6. **Scientific focus:** fault mapping is the competition output. Geothermal vents/favorability are possible
   corroborating context, not a substitute for fault truth. No new geological discovery is established by this audit.

## Ranked unimplemented hypotheses — carried-forward desk work, not new lanes

The three proposals below were already documented in the previous protocol review and remain unexecuted. Reusing them
is deliberate: the next step was protocol resolution, not inventing another lane. Local code review did not find the
specific fitted null/matched-pair operators described below. This is not a global literature novelty claim.
Expected improvement is qualitative judgment, **not predicted DTI points**; any could be negative.
All use existing manifest-listed layers, so no new external data are necessary for a pilot. This review restores only
small validation inputs; it does not claim a freshly restored production feature stack. No viable new-data claim is made.

| Rank / expected value / cost | Layers and signature | Why missing faults, rather than only mapped faults? | Difference from implemented methods | Named non-fault null / test |
|---|---|---|---|---|
| 1 / possible precision improvement; uncertain / medium CPU | B12 DEM + B13 isostatic gravity: fit constant-elevation shoreline arcs to scarp chains, test residual geometry plus independent cross-front gravity step | Buried range-front continuation could show structural depth contrast without a preserved mapped scarp | H31-X uses slope breaks; it does not fit an explicit equipotential-shoreline null before accepting the chain | Tilted paleoshorelines and lithologic contacts; matched elevation controls, no automatic veto of horizontal true faults |
| 2 / possible specificity improvement; lower confidence / high CPU | B2 RTP + B13 gravity: signed along-strike phase displacement of segmented contacts with reciprocal cross-field agreement | An unmapped transverse fault may offset basement contacts even with no surface scarp | MAGREST matches local magnetic textures; this tests an unbroken-contact null along chains across both fields | Intrusive boundaries / survey seams; reciprocal displacement and held-out survey-block controls |
| 3 / possible robustness gain; resolution limited / high CPU | B12 DEM: matched drainage-basin pairs; channel-steepness residuals conditional on area and relief; opposite-signed cross-trace contrast | Differential uplift can survive in drainage organization after local scarps disappear | A fitted matched-basin difference-in-differences operator is not the existing curvature/knickpoint descriptor | Stream capture, avulsion, erodibility; area/relief matching and leave-one-channel-out sensitivity |

**Top candidate validation status: NOT RUN.** It cannot be honestly labelled validated or promoted after the current
STOP and without an assigned method. Once authorized, freeze nulls and features; restore/hash-check the shared cache;
run each feature's canary first; hide whole components with an empirically justified buffer; derive catalogue features
from visible faults only; exact-mask visible pixels; reuse the shared pooled DTI and writer; compare against a retrained
same-run incumbent with paired spatial CI, discovery proxy and untouched confirmation. Stop on duplicate/leakage,
at three experiments or two hours. No weekly slot until a separate permitted selector verifies all gates and quota.

## Sources and limitations

Fresh official source: [organizer reference README, pinned commit](https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/README.md),
[archived bytes](../evidence/review_bf9d261d/official_reference_README.md) and checksum in the source receipt.
It explicitly supports CPU-only execution; a GPU is faster, not mandatory. The prompt's GPU-required assertion is incorrect.
Owner repositories/rasters are **OWNER-MIRROR**, not official organizer-authenticated data.

Official review links, **not retrieved here** because their hosts are outside the network allowlist:
[problem/format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/),
[rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf),
[GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and),
[GDR 1391](https://gdr.openei.org/submissions/1391),
[leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/).
No authentication attempt, leaderboard monitoring, automated submission or quota verification occurred.
Exact-file organizer receipts, official template provenance and current rules remain needed; credentials must not be placed in chat or Git.

## Next work in order

1. Explicit protocol-owner resolution of the dense registered control and assignment of one method paragraph.
   No silent registry exclusion. This is an authorization ambiguity, not something more compute can fix.
2. Refresh the complete nine-site raster inventory at fixed new commits; compare all registry fields at both stages.
3. Restore/hash-check the production stack/cache and authenticate template/rules provenance through authorized access.
4. Preregister one hypothesis, reproduce the strongest comparable same-run incumbent and run canaries, screen and fresh
   confirmation with the shared tools. No projection-driven promotion.
5. Only a separate selector can approve a weekly slot after evidence, uniqueness, provenance and quota gates pass.

## Three-pass audit

Pass 1 implemented the canonical status, reconciled the stale register/feed and added a counting preflight.
Pass 2 found and blocked the legacy approval bypass, checked strict thresholds/invalid inputs, and preserved historical
scientific claims as cited rather than fresh evidence. Pass 3 reruns full tests, metric proofs, byte checks, deterministic
site build and browser download checks. Actual receipts and results are in `registry/review_passes.json` and
`evidence/review_bf9d261d/`; passing code checks does not fulfil the blocked new-submission requirement.


### Integration / portability follow-up

Integrated concurrent main PR #47 without losing its no-submit clarification, navigation warning or regression test.
Final local suite: **202 tests passed** (including its inherited test and a new BLAS-drift test).
The first GitHub verify run failed; REST log retrieval was temporarily rate-limited. During investigation a
last-bit BLAS/thread-count correlation serialization difference was reproduced locally. The canonical report now
rounds only the displayed final rank correlation to 12 decimals **after** the verifier evaluates unrounded gates.
`--check` passes with OpenBLAS thread counts 1, 2 and 4; no overlap/score, threshold or permission is rounded or relaxed.
Historical shared evaluator/writer code remains unchanged. GitHub CI/merge status is reported separately, not assumed.
