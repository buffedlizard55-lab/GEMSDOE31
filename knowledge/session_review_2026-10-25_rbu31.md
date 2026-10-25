# Session review 2026-10-25 — RBU31 / RBU31-B (negative results, delivered)

Branch `arena/84287da3-gemsdoe31`. Three passes were run: Pass 1 implemented
and screened RBU31; Pass 2 diagnosed the failure, fixed a shared-tool defect
and edited the site generators (recovering two edit-race corruptions, see
below); Pass 3 ran the preregistered amendment (RBU31-B), independently
re-verified every packaged byte, rebuilt the site/registers and shipped.

## Question the owner asked: why 0.2778, and can we beat it?

`h33-h33-2-b2-…-zeros` (GEMSDOE32) is **USER-REPORTED 0.2778**; no organizer
receipt exists, here or in any focus repo. Byte-verified geometry
(`evidence/h33_forensics_20261025.json`, re-fetched hash-verified this
session in `evidence/regime31/peer_fetch.json`): H33 = D2.8 surface with all
dots ≤ 2 px from the public catalogue deleted (37,654 dots, zero new dots
vs H27-4). Under DTI = T/(0.2T + 0.2F + 0.8K), deleting dots helps iff
lost_T < 0.2S/(1−0.2S)·removed_F (≈ 0.059·removed_F at S = 0.27);
catalogue-hugging dots have lost_T ≈ 0 against an off-catalogue truth, so
pruning is almost free. Kernel-matched 2.8 px spacing matters for the same
reason (TPw is a max over the 300 m disk). **Conclusion:** the family's best
number is DTI economics on a strong parent surface, not new detection.
Beating it requires a better *off-catalogue ranking* at the same emission
economics — which neither candidate below achieved on both proxies. No
result this session establishes that 0.2778 (or the also-unverified 0.3195 /
0.4413 figures in the prompt) can be exceeded.

## Regime forensics (existing files only, before any fit)

`evidence/regime31/regime_forensics.json`: piedmont (`det_elev ≤ 50 m`) is
68.0% of the footprint and **72.4% of the catalogue** but only **37.5% of
off-catalogue SGMC truth**. H31-E2 beats H33 on piedmont SGMC (0.1233 vs
0.1091) but collapses in mountains (0.0372 vs 0.0654; TPw/dot 0.122 vs
0.188). H31-B's hand rank-blend is the only in-repo surface dominating SGMC
everywhere (0.1391/0.1432/0.1095) but was never tested on the hide-v2
catalogue holdout and leans on historical OOF maps.

## Experiments (budget respected: 3 hypothesis experiments, then stop)

| exp | candidate | screen HOLDOUT-DTI (draw 101, n=17,900) | SGMC all/pied/mtn | gates |
|---|---|---|---|---|
| 1 | RBU31 union-79 + regime-balanced weights | 0.0955 vs 0.0922, Δ+0.0034 [−0.0084,+0.0147], **1/4 folds** | 0.0736/0.1122/0.0324 | G1✓ G2✓ G3a✗ (surface top-N 75.3%) G4✗ G5✗ |
| 2 | RBU31-B = RBU31 + masked 12 km local standardization (σ=120, w=0.65, frozen from H31-B) | 0.0991 [0.0840,0.1165] vs 0.0922, Δ+0.0069 [−0.0065,+0.0192], **2/4 folds** | 0.0801/0.1236/0.0343 | G1✓ G2✓ G3a✓ G4✗ G5✗ |
| 3 | fresh confirmation (draws 202/303) | **not run** — both screens failed the preregistered ≥3/4-fold gate | — | — |

Baseline-D reproduced the H31-E session's 0.0921712554276685 *exactly* in
both runs (same folds/samples/seeds) — the harness is verified, the
candidates are simply not strong enough. Both verdicts: **negative, DO NOT
SUBMIT**. Both TIFF sets are retained as labelled research deliverables
(`docs/downloads/gemsdoe31-rbu31-…1788ff29*`,
`…rbu31b-localunion-…b7585935*`), each with an all-finite [0,1] variant whose
values are finite in [0,1] over the whole array (immune to the portal's
"Predicted values must be in range [0, 1]" class), a NaN-outside variant, a
single-TIFF ZIP, a format receipt and a JSON run card. Independent
byte-level recomputation of hashes, format, SGMC proxies and peer overlaps:
`evidence/regime31{b}/independent_verification.json` (all checks pass).

Useful negative knowledge: (i) putting raw-39 and SCGP-40 in the same trees
does **not** reproduce H31-E2's dual-expert gain (0.1274 screen with Poisson
ablation 0.1276); the missing mass must come from its lidar-expert blend,
label-free ridge blend and/or visible tip/relay multiplier — never cleanly
ablated. (ii) 12 km local standardization improves both proxies and drops
surface overlap (75.3% → 65.5%) but cannot rebalance regimes that are
contiguous at ≫12 km scale (piedmont dot share 75% → 77%). (iii) Mountain
SGMC rewards bedrock slope/relief expression that catalogue-trained risk
suppresses; treat G5-mountain as a biased instrument, not ground truth.

## Shared-tool defect found and fixed once (Protocol Rule 2)

`build_static_h31e_stack` read retired prepared bands
`dist_probe_km`/`dist_vent_km` and crashed. Fixed in
`src/gemsdoe31/scgp_features.py` by computing both from the GDR-1391
external rasters with the same EDT-km semantics as the neighbouring
paleo band. Report: `evidence/regime31/shared_tool_defect.json`.

## Irregularities / process failures (flagged, fixed)

1. Two sets of **parallel edits to the same file raced** and silently lost /
   corrupted text (`scripts/run_rbu31.py` lost edits; `scripts/build_site.py`
   gained a truncated string + duplicated experiment entry). Both were
   detected by `py_compile`/`git diff` review, restored verbatim from HEAD
   where needed, and re-applied sequentially with read-back checks. No
   corrupted text shipped.
2. G3b spacing-5 lattice degeneracy persists (blocks any candidate under a
   literal 70%/3 px reading); disclosed on site and run cards, not exempted.
3. Draw 101 was reused as a disclosed development draw for RBU31-B after
   Exp 1; the untouched draws 202/303 remain untouched.

## Limitations (unchanged in kind)

Owner-mirror inputs are hash-pinned but not organizer-authenticated; no
ORGANIZER-CONFIRMED score exists for any file; SGMC/catalogue proxies are
biased in opposite directions and neither is the private truth; the
21.3 km collar is inherited; live portal behaviour, outside-mask convention
and weekly quota were not freshly verified (host allowlist). No slot was
spent; no DrivenData access was made.

## Next session

`knowledge/2026-10-25_rbu31c_next_preregistration.md` freezes a
component-isolation design (tip/relay + label-free ridge on the RBU31-B
surface, first evaluation on untouched draws 202/303, surface-overlap stop
vs H31-E2). Do not re-run RBU31/RBU31-B variants, do not submit either TIFF,
and do not spend a slot on H31-E2 without the separate selector decision
its run card requires.
