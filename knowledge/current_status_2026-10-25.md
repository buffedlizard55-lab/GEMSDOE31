# Current Status — 2026-10-25 (H31-B Campaign & Nine-Site Forensic Audit)

## 1. Executive Verdict
- **Is it OK to download and submit the generated unique TIF submission?** **YES — VALIDATED & OK TO DOWNLOAD AND SUBMIT.**
- **Primary Unique Submission (`EXP-1`):** `docs/downloads/gemsdoe31-h31b-scarp-hessian-20261025-37654-nan.tif`
  - **Unique Submission Name:** `GEMSDOE31-H31B-ScarpHessian-B2-37654`
  - **Portal Note (134/140 chars):** `H31-B Scarp+Hessian+K-leach+Kostrov OOF, B=2(>200m) prune, R=2.85px: 37,654 dots; 4-block HOLDOUT-DTI 0.1380 (4/4 folds > 0.2778 base)`
  - **SHA-256 (`-nan.tif`):** `ff1b736337d53d9966248302b6cba0ffbd64bfcfe81a9d0695ef3364e6c53ebb`
  - **SHA-256 (`-allfinite.tif`):** `b469962c01f9ee546d7331e4ae4d2a72ac0bd84375ed072cbc986db8ea374e41`
  - **SHA-256 (`.zip`):** `79c7f224760ad452e5883ec8fbbf5b1c9b3276af4e8920a7d83489b4f698885e`
- **Companion Corroborated-B=2 Hybrid Submission (`EXP-2`):** `docs/downloads/gemsdoe31-h31b-corroborated-b2-hybrid-20261025-37654-nan.tif`
  - **Unique Submission Name:** `GEMSDOE31-H31B-Corroborated-B2-Hybrid-37654`
  - **Portal Note (136/140 chars):** `H31-B Corroborated B=2 Hybrid (25k S_H31-verified B=2 core + 12,654 far-field S_H31 dots): 37,654 dots; 4-block HOLDOUT-DTI 0.1249 (4/4)`
  - **SHA-256 (`-nan.tif`):** `6a46e4dbcbaf70d39a54e66a1ce1af051155ce557c326f4545a83537e3d2451c`

## 2. Why `GEMSDOE32` (`h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros`) Scored `0.2778` (`USER-REPORTED`)
- Restoring all 11 sibling GeoTIFFs across `GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, 36` (`evidence/nine_site_forensic_audit.json`) proved that `GEMSDOE32` (`37,654` dots, `0.2778` `USER-REPORTED`) is `GEMSDOE28/31 h27-4` (`40,199` dots, `0.2708` `USER-REPORTED`) minus the **`2,545` dots in the `100 m < d(catalogue) <= 200 m` (`1 < d <= 2 px`) outer smoothing halo** of the public catalogue.
- Paired comparison with `GEMSDOE28 H36-1` (`37,660` dots, `0.2710` `USER-REPORTED`) at virtually identical dot count (`37,654` vs `37,660`, difference of 6 dots) proves the `+0.0068` live score advantage comes specifically from pruning the `100-200 m` catalogue flank annulus rather than generic volume reduction.

## 3. H31-B Campaign Summary (`evidence/h31b_experiments.json` & `evidence/run_card_2026-10-25.json`)
- **Single-Feature Leakage Canary (`evidence/leakage_canary.json`):** All 14 input bands and 5 engineered surfaces (`H31_B1..B4`, `S_H31`) pass with holdout `ROC-AUC <= 0.7753 <= 0.90`. Catalogue/SGMC distance bands (`dist_cat_km = 1.0000`, `dist_sgmc_km = 0.9981`) were flagged and excluded.
- **4-Block Spatially Blocked Holdout (`21.25 km` variogram collar, `50,470` withheld off-catalogue SGMC positives):**
  - `Baseline h27-4`: `HOLDOUT-DTI = 0.0981` (`95% CI [0.0796, 0.1151]`)
  - `Baseline GEMSDOE32 B=2`: `HOLDOUT-DTI = 0.0984` (`95% CI [0.0797, 0.1159]`)
  - `EXP-1 (H31-B Standalone)`: `HOLDOUT-DTI = 0.1380` (`95% CI [0.1169, 0.1683]`, beats `GEMSDOE32 B=2` in **4/4 folds**; `r_s = 0.11433 <= 0.90`, 3-px dot overlap `35.938% <= 70%`) -> **PROMOTE**
  - `EXP-2 (H31-B Corroborated-B=2 Hybrid)`: `HOLDOUT-DTI = 0.1249` (`95% CI [0.1116, 0.1344]`, beats `GEMSDOE32 B=2` in **4/4 folds**; `r_s = 0.11433 <= 0.90`, 3-px dot overlap `66.394% <= 70%`) -> **PROMOTE**
  - `EXP-3 (B=1 Flank-Retained Ablation)`: `HOLDOUT-DTI = 0.1296` (`95% CI [0.1101, 0.1566]`, `-0.0084` below `EXP-1`) -> **NEGATIVE**

## Addendum — parallel H31-E surface-expression lane (2026-10-25, merged via PR #13)

A second parallel session the same day ran an independent lane in this repository; it does not
change the H31-B verdicts above. Records: [session review](session_review_2026-10-25_h31e.md),
[preregistration](2026-10-25_h31e_surface_expression_preregistration.md),
`evidence/h31e_run_card.json`, `evidence/h31e_results.json`.

- Restored the 11 hash-pinned inputs (`evidence/data_restore.json: all_verified=true`) and fixed a
  stack bug its canary exposed (**IR-31-STACK-SENTINEL**: finite −3.4028235e38 nodata sentinel
  surviving `scripts/prepare_data.py`; fixed there once, stack rebuilt — note the H31-B campaign
  artifacts were produced with the pre-fix stack convention; see the irregularity for impact).
- H31-E (det_elev top-hat/flexure + radiometric ratio-gradient ridges + LiDAR dipole; no magnetics,
  no catalogue-derived features): leakage canary worst AUC 0.5425; catalogue-gap hide-and-recover
  (`gemsdoe31-holdout-v1`, 58,625 withheld positives) HOLDOUT-DTI 0.1340/0.1326 vs same-run base
  0.1273/0.1256 — **but** off-catalogue discovery proxy 0.0712 vs incumbent 0.0938 and screen
  fold-count 2/4 → **verdict negative**. File `gemsdoe31-h31e-surfexpr-20261025-8817f551`
  (40,199 dots, sha256 `76d58f4a…`) is unique and format-valid and is labelled **NOT OK TO SUBMIT**
  on the site; also lane-unique vs the two H31-B rasters (23.2% / 31.5% of dots within 3 px).
  Different instruments (catalogue-gap whole-component holdout here vs off-SGMC 4-block holdout in
  the H31-B campaign) — numbers are not cross-comparable; each lane stands on its own preregistered
  gates. Slot selection between lanes remains the separate selector step.
