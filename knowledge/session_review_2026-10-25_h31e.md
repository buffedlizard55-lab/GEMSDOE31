# Session review — H31-E surface-expression lane (2026-10-25, second session of the day)

**Verdict: NEGATIVE (preregistered gates failed). A unique, format-valid TIFF was generated and is
labelled NOT OK TO SUBMIT everywhere it appears. No weekly slot is recommended or used.**
Machine-readable run card: [`evidence/h31e_run_card.json`](../evidence/h31e_run_card.json);
full results: [`evidence/h31e_results.json`](../evidence/h31e_results.json); design frozen before
fitting in [`2026-10-25_h31e_surface_expression_preregistration.md`](2026-10-25_h31e_surface_expression_preregistration.md).
Budget used: 3/3 experiments, ~1 hour. This session supersedes the earlier 2026-10-25 stop only in
that the runtime-input blocker was removed (the 11 hash-pinned inputs were restored from the owner
GitHub mirrors and SHA-256-verified, `evidence/data_restore.json: all_verified=true`); that
session's H33-2-B2 duplicate rejection stands unchanged.

## The question, answered: why 0.2778, and what beating it requires

All fleet scores below are **USER-REPORTED / OWNER-MIRROR**; no organizer receipt exists in this
repository for any of them. The geometry, by contrast, is **COMPUTED** here and in sibling repos
from the actual bytes:

1. **The top of the fleet is one nested family, one surface.** H19-5 (121,131 dots, 0.1922) ⊃
   D2.8 (44,090, 0.2600) ⊃ H27-4 solo (40,199, 0.2708) ⊃ H33-2-B2 (37,654, 0.2778). Each step was
   verified pixel-exactly: H27-4 = D2.8 minus dots within 100 m of the public catalogue
   (`evidence/h27_geometry.json`); H33-2-B2 = H27-4 minus its 2,545 dots within 200 m
   (GEMSDOE32's own round-5 forensic note, fetched 2026-10-25 from
   <https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html>, agrees; the earlier session
   here measured Spearman 0.9676 and 100% within-3px overlap vs the local H27-4 raster — a strict
   subset, hence a duplicate lane for us).
2. **Why pruning scores.** With DTI = TPw/(TPw + 0.2·FPw + 0.8·FNw), a dot is worth emitting only
   if its kernel-weighted credit exceeds break-even k ≈ 0.2·DTI (≈0.0556 at DTI 0.2778). The
   scorer masks known catalogue pixels, so catalogue-flank dots earn ~0.006–0.016 (owner-mirror
   measurement) while always paying α — they are below break-even by construction. The sparse
   dotted geometry itself (283–300 m spacing) matches the 300 m triangular kernel: maximal truth
   coverage per unit of α-cost. H33-2-B2 was simply the first file with **zero** dots inside
   200 m of the catalogue. The `-zeros` suffix is an outside-footprint encoding, not a mechanism;
   no score advantage of zeros-vs-NaN has been established (see IR-31-H33-ZERO-OUTSIDE).
3. **The family's ceiling is visible.** GEMSDOE36's "Anderson PINN" (0.2750) reportedly contains
   all 37,654 champion dots plus 1,200 more — and scored *lower* (−0.0028): additions to the
   champion earned below break-even live. Pruning cannot go much further either (the removable
   below-break-even mass is nearly exhausted). Beating 0.2778 therefore needs **better-placed
   dots, not re-budgeted ones**: at a fixed 37,654-dot budget, +8% mean credit/dot reaches ≈0.30;
   the user-reported public #1 (0.4413; the prompt's other anchor 0.3195 is stale — see
   IR-31-LEADERBOARD-ANCHORS) needs ≈+59% credit/dot. That requires a detector whose new dots
   land on real hidden faults at >0.056 live credit each — a detection-quality problem, not an
   emission-geometry problem. Every novel standalone lane measured across the fleet so far
   (including GEMSDOE32's three 2026-10-25 lanes and this session's H31-E) has failed to beat the
   champion on a fair instrument; that is the honest state of the art in this programme.

## Focus-site high scorers (24/25/27/28/30/31/32/33/36), USER-REPORTED

| Site | Highest reported file | Score | What it actually is (owner-mirror evidence) |
|---|---|---:|---|
| GEMSDOE32 | h33-h33-2-b2-…-zeros | 0.2778 | H27-4 minus 200 m catalogue flank (37,654 dots); archive itself says UNSCORED; site now says submitted — no receipt |
| GEMSDOE36 | anderson-geothermal-pinn-38854-…-zeros | 0.2750 | Champion dot set + 1,200 dots (per GEMSDOE32 forensics) — same family |
| GEMSDOE31 (this repo) | h27-4-solo-d28 | 0.2708 | D2.8 minus 100 m flank (40,199 dots), re-emitted here |
| GEMSDOE28 | h36-1-rung30-blind-r1 / h27-4-r1-solo-d2-8 | 0.2710 / 0.2708 | Same H19-5 surface, rung variants |
| GEMSDOE33 | h33d-analog-tip-stepover-r30 | 0.2632 | Tip/stepover additions on the family surface |
| GEMSDOE25 / GEMSDOE30 | dotted-h19-5-d2-8 / d28-poisson300m-offcat-44090 | 0.2600 | The D2.8 emission itself (44,090 dots) |
| GEMSDOE24 | h25-1-dotted-h19-5-d1-5 | 0.2477 | Denser (d=1.5) thinning of the same surface — denser is worse, confirming the α economics |
| GEMSDOE27 | topo-gap-closure-t-v2-on-d1-5 | 0.2449 | Gap-closure edits on the d1.5 emission |

Pattern: **every** score ≥0.24 in the fleet derives from the single H19-5 surface. Independent
detectors (all other lanes, all sites) sit at ≤0.19. A scientist should read that as: the H19-5
detector found a real, large set of hidden-fault-proximal locations, and nobody's alternative
detector has yet found a comparably credit-dense set.

## What this session did (EXP-1 → EXP-3, all numbers COMPUTED)

- Restored the 11 hash-pinned inputs; rebuilt the 46-band feature stack after fixing a real bug
  the canary caught (**IR-31-STACK-SENTINEL**: the −3.4028235e38 nodata sentinel survived
  `prepare_data.py`'s non-finite-only conversion and poisoned derived channels; fixed once in the
  shared tool, stack rebuilt, sentinel count now exactly matches the NaN count 7,113,308).
- Implemented the shared tools this repo lacked: `src/gemsdoe31/holdout.py` (evaluator
  `gemsdoe31-holdout-v1`), `src/gemsdoe31/emission.py`, `src/gemsdoe31/surface_features.py`,
  public `per_truth_credit`/`fp_weights` in `metric.py` (both asserted to sum to the exact
  metric's TPw/FPw), and `scripts/run_h31e.py`. A paired-bootstrap block-alignment bug was found
  by a crash, fixed, and regression-tested (`tests/test_h31e.py`, 7 tests).
- **EXP-1 canary/screen:** worst new-channel AUC 0.5425 (dipole_coh) — no leakage (stop >0.90).
  Single-channel catalogue-gap HOLDOUT-DTI: dipole_coh 0.0886, flex_det_2 and ratio_grad_uth
  0.0860, vs same-protocol controls C3 OOF-B 0.1256 and C2 incumbent 0.0484.
- **EXP-2 holdout** (hide whole components by quadrant, 21.25 km empirical collar, visible faults
  masked pixel-exactly, pooled DTI α0.2/β0.8/R300 m, 58,625 withheld positive pixels):
  candidate **HOLDOUT-DTI 0.1340** (95% CI 0.1240–0.1443) vs same-run base 0.1273, paired Δ CI
  [+0.0001, +0.0136]; confirmation seed **0.1326** vs 0.1256, Δ CI [+0.0013, +0.0128], 4/4 folds.
  Screen folds: NW −0.0001, NE +0.0245, SW −0.0048, SE +0.0141 → the preregistered ≥3/4-fold
  sub-gate **fails on the screen** (2/4) even though confirmation is 4/4. Goalposts were not moved.
- **Discovery proxy (decisive):** candidate off-catalogue SGMC DTI **0.0712** vs incumbent
  **0.0938** — below the incumbent, so promotion is barred by this repo's own rule that the
  catalogue-gap instrument can never promote alone. (For the selector only: candidate∪incumbent
  proxy = 0.1253 at 78,759 dots; the candidate's dots are complementary on the proxy but a union
  is a different, duplicate-lane artifact and was not built. Fleet precedent warns proxy-union
  gains do not transfer automatically: GEMSDOE36's live additions *cost* score.)
- **EXP-3 emission/build:** final model on all data → 40,199 dots (1,485 on the public catalogue,
  reported, not surgically removed post hoc). Uniqueness: surface Spearman 0.528 (OOF-B) / 0.518
  (OOF-D) ≤0.90 ✓; dots within 3 px of registry rasters 38.0–43.7% ≤70% ✓ — genuinely lane-unique.
  File `gemsdoe31-h31e-surfexpr-20261025-8817f551` (note, 125 chars, ends "DO NOT SUBMIT"):
  `-nan.tif` sha256 `76d58f4a…`, `-allfinite.tif` sha256 `825b6719…`; both pass the strict
  validator (no NaN inside footprint, values exactly {0,1} ⊂ [0,1], EPSG:32611/shape/transform
  match, hard_failures []) — the owner's "Predicted values must be in range [0, 1]" error class
  cannot occur in these bytes. Format-validity is not organizer acceptance and not a score.

## Interpretation (INFERENCE)

The surface-expression transforms carry real, leak-free signal for *catalogue-like* faults
(catalogue-gap win over a same-run base that already contains the raw bands, replicated across
seeds), but the resulting standalone dot set is *less* aligned with the off-catalogue population
than the H19-5 family's dots. Two non-exclusive readings: (a) topo/radiometric surface expression
is what mappers already used, so it preferentially recovers catalogue-*style* faults — the ones
least likely to be missing; (b) the SGMC proxy itself is state-map compilation with its own
biases, and neither proxy is the hidden expert truth. Either way, under this repo's preregistered
rules the answer is the same: **do not submit**. The candidate's value to the programme is as a
validated, complementary, lane-unique detection set whose union behaviour a future selector can
weigh — with eyes open about the GEMSDOE36 live counterexample.

## Limitations / what I could not do

- Sandbox egress is GitHub/PyPI/npm only: no DrivenData (login-gated; also prohibited without
  permission), no USGS TNM 1 m DEM/LAZ, no GDR MT binaries. Hence H31-F (scarp-degradation
  age-bank) and H31-H (MT depth stack) remain desk hypotheses with named free official sources
  in the preregistration. The most promising untested direction for a machine without egress
  limits is 1 m DEM scarp-profile work (the hidden truth is expert mapping largely from such
  data; the fleet's 100 m aggregates are lossy).
- No organizer receipt can be produced from here; every score claim stays USER-REPORTED.
- Prior OOF/arm evidence was produced with the pre-fix stack (sentinel present outside the
  footprint and at 3,061 fringe cells); training/scored samples were in-footprint so the impact
  is expected negligible, but exact equivalence was not re-derived (the arm trainer is still
  absent — IR-31-TRAINER-NOT-IN-SNAPSHOT).

## Review passes

1. **Pass 1 — implement & verify:** preregistered, restored+verified data, built channels →
   canary caught the sentinel bug → fixed shared tool → EXP-1/2/3 → TIFF + strict validation.
2. **Pass 2 — adversarial:** independent rasterio re-read of both TIFFs (dtype/CRS/transform/
   range/NaN-placement/sha re-derived outside the repo validator; dots bitwise equal to the
   experiment array); metric re-verified vs brute force (4.4e-16); leakage audit (no catalogue-
   or SGMC-derived channel; collar/quadrant/component rules unit-tested); bootstrap alignment
   bug fixed + regression test; fold-count gate left strictly as preregistered despite the
   attractive confirmation result.
3. **Pass 3 — charter cross-check:** README/site/registers rebuilt from artifacts; verdict
   obvious at first glance on the site home page and executive summary; full local check set
   (pytest, ruff, check_metric, collect_evidence, build_site, check_site) rerun after final edits
   — results recorded in `registry/review_passes.json`.

## Run card

See [`evidence/h31e_run_card.json`](../evidence/h31e_run_card.json) (single JSON, protocol §5).
Verdict: **negative**. Submission name reserved for file identity only:
`gemsdoe31-h31e-surfexpr-20261025-8817f551` — **DO NOT SUBMIT**.
