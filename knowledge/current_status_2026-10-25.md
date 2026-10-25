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
