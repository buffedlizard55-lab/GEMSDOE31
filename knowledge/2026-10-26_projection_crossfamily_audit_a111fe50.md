# Projection audit — why the 0.355 estimate for H31-X must be withdrawn (2026-10-26)

All numbers COMPUTED this session by `scripts/cross_family_calibration.py` from
`evidence/instrument_calibration.json` (87 matched rasters; live values USER-REPORTED, no
organizer receipt). Full per-row output: `evidence/cross_family_calibration_20261026.json`.

## The old method (M1)

Earlier sessions estimated a candidate's live score as
`PROJECTION = 0.9275 · SGMC_TPw / (10694.6 + 0.2·n_dots)`, fitting the single scale on eleven
anchors (GEMSDOE24/25/27/28×4/30/32/33/36). Every anchor is a descendant of one surface family
(H19-5 → D1.5/D2.8 dots → catalogue-flank prunes); their SGMC-DTI spans only 0.0919–0.0996.
Within that family the formula is excellent (LOO RMSE 0.0028) — because it only has to explain
dot-budget arithmetic among near-identical dot fields.

## Out-of-family test (this audit)

Applied with frozen constants to the 67 other matched submissions with 10k–130k dots
(excluding the literal SGMC/geologic-map rasters), M1 fails:

| Model | n | LOO/frozen RMSE | MAE | Bias |
|---|---:|---:|---:|---:|
| M1 selector formula (frozen) | 67 | **0.1963** | 0.1355 | **+0.1350** |
| M2 live ~ SGMC credit/dot | 67 | 0.0947 | 0.0846 | +0.0014 |
| M3 live ~ credit + coverage + log dots | 67 | 0.0897 | 0.0783 | +0.0022 |
| M0 predict-the-mean | 67 | 0.0917 | 0.0813 | 0 |
| M1 on zero-catalogue-dot subset | 62 | 0.2022 | 0.1395 | +0.1390 |
| M3 on zero-catalogue-dot subset | 62 | 0.0928 | 0.0824 | +0.0025 |

Named counterexamples (M1 projection vs USER-REPORTED live):

| Submission | SGMC-DTI | M1 projection | Live (USER-REPORTED) |
|---|---:|---:|---:|
| GEMSDOE46 r12-scarp-rad-concordance | 0.1636 | 0.484 | 0.0843 |
| GEMSDOE41 h42-submission-primary | 0.1254 | 0.362 | 0.0245 |
| GEMSDOE49 gate_ortho_w0.25-40k | 0.1328 | 0.384 | 0.2376 |
| GEMSDOE63 cvarlw-thin-s3p17 | 0.1295 | 0.340 | 0.2303 |
| GEMSDOE29 sgmc-off-catalogue-44k (excluded literal proxy) | 0.5598 | 1.672 | 0.0512 |
| 16GEMSDOE h18-4-usgs-geologic-map (excluded literal proxy) | 0.9161 | 2.344 | 0.0360 |

## Interpretation (INFERENCE, grounded in the computed facts above)

1. M1 assumes live kernel credit is a fixed multiple (0.9275) of SGMC kernel credit. That ratio
   is a property of the H19-5 family's fault-population mix, not a universal constant. SGMC
   traces are geologic-map faults of all ages, concentrated in bedrock ranges (median slope
   13.5°); the hidden expert set is newly mapped faults absent from the USGS Quaternary
   database (official problem page, fetched this session), i.e. population-wise much closer to
   the catalogue (median slope 5.6°) than to SGMC. A dot field can therefore earn large SGMC
   credit in the ranges while earning little live credit.
2. Even the best cross-family linear calibration (M3) barely beats predicting the mean
   (RMSE 0.0897 vs 0.0917). **No combination of SGMC credit, coverage, dot count, or fixed-dot
   catalogue-gap DTI in this repository can estimate a new family's live score to better than
   about ±0.09 RMSE.** Intervals like H31-X's "0.355 [0.349, 0.360]" describe only in-family
   dot-budget arithmetic and must not be presented as score estimates.
3. What the proxies *can* do: rank within a family, and (for label-free surfaces re-emitted per
   fold) test whether a surface recovers withheld catalogue faults — the population closest to
   the hidden expert set. That catalogue hide-and-recover HOLDOUT-DTI is therefore the primary
   promotion instrument; SGMC is a secondary discovery sanity check; neither is a score.

## Consequence for this repository's claims

- H31-X's selector promotion rested on G4 (SGMC ≥ H33) and G6 (M1 projection ≥ 0.2778). G6 as
  constructed is invalid cross-family and is **retired**. H31-X's genuine evidence is its
  catalogue HOLDOUT-DTI 0.1661 [0.1499, 0.1821] vs same-run controls (paired CIs exclude 0,
  confirmed on an untouched component split) — that part stands and is the strongest in-repo
  holdout result. Its live score is **unknown within roughly ±0.09–0.20** depending on how much
  in-family structure one is willing to assume; "expected to beat 0.2778" is not established.
- All selector-audit projections for the other lanes (H31-B 0.409, H31-T 0.317, H31-J 0.312,
  H31-M 0.296, …) inherit the same defect and are withdrawn as score estimates. Their SGMC and
  holdout measurements themselves are unaffected.
- Honest estimation going forward (frozen in the H31-YM preregistration as executed under the name H31-Y, amended G6): report
  (a) M1 in-family value labelled "upper-bound diagnostic if the candidate behaved exactly like
  the H19-5 family", (b) M3 cross-family central estimate with ±2·LOO-RMSE interval,
  (c) catalogue HOLDOUT-DTI with CI. Never a single-point "estimated score" without (b)'s width.
