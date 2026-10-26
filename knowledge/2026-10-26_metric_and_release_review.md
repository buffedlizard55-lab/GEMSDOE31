# Executive decision — review continuation, 26 October 2026

**DOWNLOAD EXISTING FILES FOR RESEARCH: YES. SUBMIT: NO. NEW TIFF THIS SESSION: NONE.**

This is an audit/repair continuation, not another geological lane. The prompt does not contain the
promised single-method paragraph. Previous experiments have already recorded a literal overlap STOP.
Making another file after that STOP would violate the requested parallel-run protocol. No competition
slot was used, no model trained, and no score improvement is asserted. This does **not** complete the
requested new, high-performing, submission-approved TIFF objective.

[Executive summary and existing downloads](../docs/executive-summary.html) ·
[Existing MAGREST research TIFF](../docs/downloads/gemsdoe31-magrest-concordant-37654-20261025-2c800a59ff-zeros.tif) ·
[Existing full run card](../registry/current_run.json).
These are existing artifacts, not newly generated submissions. Other preserved lanes remain separately
identified on the site. We re-ran the MAGREST, H31-S, H31-J and H31-T exact-file verifiers in this runtime;
all deny slot approval. A valid numeric range does not prove portal acceptance.

## Nine-site decision

The following are the highest **USER-REPORTED** historical claims supplied for each requested site,
not ORGANIZER-CONFIRMED scores. None is a recommendation to copy or resubmit an old prediction.
The source snapshots and hashes are in [focus_review.json](../registry/focus_review.json);
the [site matrix](../docs/executive-summary.html#focus-sites) links each pinned artifact.
No live leaderboard was accessed. The two reported global benchmarks are inconsistent; neither is verified.

| Site | Highest supplied historical claim | Artifact family | Decision under new-file requirement |
|---|---:|---|---|
| GEMSDOE24 | USER-REPORTED 0.2477 | H25-1 dotted D1.5 | Prior art only |
| GEMSDOE25 | USER-REPORTED 0.2600 | Dotted H19-5 D2.8 | Prior art only |
| GEMSDOE27 | USER-REPORTED 0.2449 | Topo gap closure T-v2 | Prior art only; newer H29 claim is not organizer-confirmed |
| GEMSDOE28 | USER-REPORTED 0.2710 | H36-1 rung30 blind R1 | Prior art only |
| GEMSDOE30 | USER-REPORTED 0.2600 | D28 Poisson300m | Prior art only |
| GEMSDOE31 | USER-REPORTED 0.2708 | H27-4 solo D28 | Prior art only; current research candidates remain blocked |
| GEMSDOE32 | USER-REPORTED 0.2778 | H33-2-B2 | Highest supplied nine-site claim, not a unique new candidate |
| GEMSDOE33 | USER-REPORTED 0.2632 | H33D analogue tip/stepover | Prior art only |
| GEMSDOE36 | USER-REPORTED 0.2750 | Anderson geothermal PINN | Prior art only |

## What H33 actually establishes

[Stored byte forensics](../evidence/h33_forensics_20261025.json) show that H33 removes catalogue-flank
pixels from D2.8; it does not add a new detector. Thinning may reduce redundant coverage cost and
pruning may remove false-positive weight. Without private truth, neither is a proven explanation
for the claimed competition improvement. The claimed GEMSDOE36 decline likewise does not prove
that every additional dot was unhelpful. We corrected overconfident causal wording in README and
in the generated research page.

The README and renderer had an incorrect gain/FP denominator, although the shared evaluator's
arithmetic was already correct. With fixed truth count N, T=TPw, F=FPw and FNw=N−T:

    S = T / ((1−beta)T + alpha F + beta N + epsilon)
    improvement iff (1−(1−beta)S) delta_T > alpha S delta_F

For positive delta_F and alpha=0.2, beta=0.8, the ratio threshold is
`0.2S/(1−0.2S)`, NOT `0.2S/(1−S)`. A COMPUTED algebra illustration using the unverified
claim S=0.2778 gives 0.0588285. In the special one-truth-cell nonredundant case the
kernel-credit threshold is 0.05556, not a general fault-hit probability. No private-score
projection follows. [Reproducible check](../scripts/check_marginal_dti.py) compares 10,000 finite
additions/removals to the unchanged shared evaluator, plus tests for zero-cost/no-op cases.
The [receipt](../evidence/marginal_dti_audit_20261026.json) pins the shared source hashes.

## Ranked future hypothesis refinements — NOT authorized or executed

These are desk proposals, not claims of unexplored global novelty. Existing local feature modules
and preregistrations already cover much of the requested physics. Rebranding those methods would
not meet the uniqueness requirement. The following operational refinements require a new lane
preregistration and complete prior-art search before implementation. The rank expresses qualitative
research priority, **not expected numeric DTI gain**; improvement for all three is unknown.

| Rank / hypothesis | Layers and physical signature | Why possibly off-catalogue; specific difference to existing implementation | Named non-fault mimic / null | Cost and access |
|---|---|---|---|---|
| 1. Reciprocal restoration consistency | B2 RTP magnetic texture; forward and reverse patch displacement maps with cycle-closure error | Concealed lateral displacement may preserve corresponding texture across a trace. MAGREST measures same-sign restoration gain at two offsets, not full forward/reverse cycle closure. This is a refinement of MAGREST, not permission to resume its stopped lane. | Separate volcanic flow contacts; test phase-randomized and flight-line-aligned nulls | Medium CPU; use shared cached B2 only after hash restoration; full feature stack not restored in this audit |
| 2. Compositional displacement corroboration | GeoDAWN K/Th/U channel ranks; one common displacement fitted to multichannel textures, then compare its sign to magnetic displacement | Small concealed splays might displace compositional fabric without a preserved scarp. Requires displacement agreement, not the already-used K/Th amplitude/edge conjunction. RADREST was previously proposed; this specific joint-sign test has no result here. | Alluvial provenance boundaries and radiometric acquisition seams | Higher cost; existing mirror provenance is recorded, but concentration calibration and missing-coverage controls are prerequisites |
| 3. Gravity–magnetic reciprocal co-restoration | B2 RTP and B13 isostatic gravity; separate displacement solutions with reciprocal consistency and uncertainty-weighted agreement | A basement transfer fault might displace both density and magnetic texture. Unlike existing gradient/depth concordance, test whether registered textures agree; GRAVREST itself is an earlier desk proposal, not a new discovery. | Intrusive lithologic contact; negative control is equally good unshifted fit | Higher cost and coarse-gravity resolution risk; existing shared bands, no new external input promised |

Do not execute any of these under the recorded STOP. No fresh external dataset was proposed as
obtainable. Official GeoDAWN metadata is linked in the existing source register, but its host is
outside this sandbox's network allowlist; current binary availability was not checked here.

## Binding limitations and next-session priorities

1. **Protocol:** resolve the missing lane and literal dense-control overlap rule explicitly. Do not
   silently drop calibration/dense rasters, change thresholds, or place dots outside their halos to
   manufacture novelty. Large overlap with a dense lattice is not scientific proof of copying, but
   it still fails the user's literal gate. One counterexample proves failure; it does not prove
   an exhaustive registry pass. [Pinned witness](../registry/shared_registry_57_pin.json).
2. **Validation:** compare a future candidate with the strongest reproducible incumbent on identical
   visible-only whole-segment folds, an empirically supported buffer, pooled shared DTI and paired
   spatial CI. Feature canaries precede trusting results. Fresh confirmation and independent discovery
   proxy evidence follow. Different evaluator populations cannot be ranked by headline DTI.
3. **Data/access:** only small owner-mirror validation inputs were restored here. No authenticated
   organizer template, hidden labels, score receipts or weekly quota are available. GitHub-hosted
   official reference documentation is accessible; other supplied official domains and Dropbox
   are outside the network allowlist. No request for credentials is needed.
4. **Official verification:** the [official reference README](https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/README.md)
   explicitly offers CPU training. The quoted blanket “GPU needed” statement is not a current
   requirement. [Retrieval receipt](../evidence/official_reference_review_20261026.json).
   This does not verify current rules, dates, leaderboard, quota or outside-footprint convention.
5. **Release:** the site is static, regenerated from evidence, not a live leaderboard feed. The nine-site
   highest-claim summary is now ahead of long per-lane download sections on the executive page.
   Upload instructions apply only to a future file whose exact-file receipt authorizes selection.

## Three cumulative passes

- **Pass 1:** read project charter/history, restore and revalidate small pinned inputs, reproduce existing
  release denial, audit shared formula, repair README and renderer without changing shared scoring code.
- **Pass 2:** add random finite-change and zero-cost/no-op regression tests; remove confirmed-score wording;
  distinguish gain/FP ratio from isolated kernel credit; preserve prompt and all TIFF bytes.
- **Pass 3:** run full tests, lint, metric check, marginal proof, all four exact-file verifiers, evidence
  collection, site regeneration and link checks. See current check counts in the review register.

The requested new approved submission remains blocked. Negative findings are delivered instead of
inventing a new score, bypassing the STOP, or claiming all user requirements are fulfilled.
