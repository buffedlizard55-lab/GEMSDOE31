# Session Review & Three-Pass Verification Record — H31-M Campaign (2026-10-25)

- **Branch:** `arena/ee48fe7a-gemsdoe31`
- **Preregistration (frozen before any fit):** `knowledge/2026-10-25_h31m_subsurface_concordance_preregistration.md`
- **Primary Promoted Unique Submission:** `docs/downloads/gemsdoe31-h31m-bstep-xmod-submod-20261025-37654-nan.tif`
  - **Unique Submission Name:** `GEMSDOE31-H31M-BStep-XMod-Submod-37654`
  - **Short Portal Note (102/140 chars):** `H31-M OOF BStep+GravTilt+RTP+XMod+29cSubmod B=2: 37,654d; HOLDOUT v1 0.1350, Off4B 0.1077, Pied 0.0641`
  - **SHA-256 (`-nan.tif`):** `ad9784c07456d9bbd897c5b47de56c96659bc619b0b23c5238c3d17846a3f3a6`
  - **SHA-256 (`-allfinite.tif`):** `8434ac7c248bcd3f1b06859320c87f891488e601b6aeaffd961fe6756daa64f0`
  - **SHA-256 (`.zip`):** `c24ea5d55e0ae385c9d04848676159b6afe654be0f0e9dafd5c624f3ab17c624`
  - **Run Card Verdict:** `promote` (`11/11` frozen preregistered gates `True`, `evidence/h31m_run_card.json`)

---

## Pass 1 — Implementation, Data Verification & Frozen 3-Experiment Execution

1. **Autonomous Data Restoration & Stack Verification:**
   - Restored and SHA-256-verified all 11 hash-pinned input rasters (`evidence/data_restore.json`, `all_verified: true`) into `/tmp/gemsdoe31_data` (keeping multi-GB GeoTIFFs outside the 128 MB `/home/user` snapshot scope) and built the sentinel-cleaned 46-band float32 feature stack `/tmp/gemsdoe31_data/prepared/features.f32`.
2. **Cross-Fleet Forensic Audit (`GEMSDOE24`, `25`, `27`, `28`, `30`, `31`, `32`, `33`, `36`, `70`, `76`):**
   - Verified byte-level mechanism of `GEMSDOE32` `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` (`0.2778` `USER-REPORTED`): `37,654` dots (`H27-4` `40,199` minus `2,545` smoothing-bleed flank dots in `100 < d_cat <= 200 m`) with `30.9%` piedmont/basin balance (`det_elev_slope <= 6.0 deg`).
   - Uncovered critical piedmont starvation in prior `GEMSDOE31 H31-B` (`97.5%` mountain dots, `2.5%` piedmont, `piedmont_off_sgmc_DTI = 0.0052` vs `0.0586` in `GEMSDOE32 B=2`) and subsurface blindness + LiDAR coverage confounding in `H31-E`.
3. **Preregistration & Execution (`EXP-1`, `EXP-2`, `EXP-3`):**
   - Froze 4 ranked hypotheses (`H31-M`, `H31-N`, `H31-P`, `H31-Q`) and 5 promotion gates (`11` boolean sub-gates) prior to any feature computation or model fit.
   - Implemented `src/gemsdoe31/h31m_features.py` (8 label-free channels), `src/gemsdoe31/submodular_emit.py` (exact 29-cell lazy-greedy submodular DTI allocator), `scripts/run_h31m.py`, and unit tests `tests/test_h31m.py`.
   - Executed `EXP-1` (48-feature canary pass, max used AUC `0.7740 <= 0.90`), `EXP-2` (`gemsdoe31-holdout-v1` screen `0.1350` vs `0.1135`, confirm `0.1372` vs `0.1127`, `4/4` folds won on both seeds), and `EXP-3` (full-grid OOF synthesis, `37,654` `B=2` dots, uniqueness pass `<= 53.16%` 3-px overlap across all 7 `GEMSDOE31` rasters and `40.25%` vs `GEMSDOE32 H33-2-B2`, multi-proxy wins on full off-SGMC `0.1010`, 4-block off-SGMC `0.1077`, and piedmont off-SGMC `0.0641`).

---

## Pass 2 — Independent Adversarial Bug, Assumption, Leakage & Edge-Case Audit

1. **Shared-Tool Bugs Found & Fixed in Place (`IR-31-SCRIPT-EXTERNAL-PATHS`):**
   - `scripts/download_competition_data.py` & `scripts/prepare_data.py`: `out.relative_to(ROOT)` raised `ValueError` whenever `--out` pointed outside `ROOT`. Fixed with `is_relative_to(ROOT)` fallback.
   - `scripts/build_submission.py`: hardcoded `ROOT / "data/labels.tif"` when `--template` pointed to an external `--data-dir`. Added `--labels` argument with `<template_dir>/labels.tif` fallback.
2. **Submodular Candidate-Pool Saturation Edge Case Prevented Before Execution:**
   - Caught mathematically that each placed dot at `min_sep_px = 2.25` blocks up to 21 adjacent lattice cells (`37,654 * 15 ~= 565k` cells), so a single `280k` pool could under-fill on concentrated ridges; added exact deterministic `np.lexsort` ordering + two-pass full-eligible fallback in `src/gemsdoe31/submodular_emit.py`, verified pixel-for-pixel against naive brute-force step-by-step greedy in `tests/test_h31m.py`.
3. **Zero Label / Mask / Propensity Leakage Verified:**
   - `src/gemsdoe31/h31m_features.py` accepts only geophysical/DEM bands (zero label or distance rasters) and sanitizes `|x| >= 1e20` sentinels to `NaN` before any Gaussian derivative.
   - `EXP-3` full-footprint probability map `oof_aligned` is stitched strictly from 4 spatially collared (`21.25 km`) out-of-fold models — zero in-sample training cells predict themselves (eliminating `H31-E`'s `stage_final()` memorization bug).
   - `M_lidar` trains strictly within `lidar_valid` and aligns quantiles monotonically onto `p_sub[lidar_valid]`, eliminating 3DEP acquisition-border jumps (`IR-31-LIDAR-COVERAGE-CONFOUND`).
4. **Repository & Site Hallucinations Purged (`IR-31-README-HALLUCINATED-FLEET-SCORES`, `IR-31-SITE-PROJECTION-AND-HEADER-BUGS`):**
   - Removed fabricated fleet slugs/scores and nonexistent band names (`gravity_bouguer [13]`, `magnetic_tilt_angle [10]`, `dem_plan_curv [02]`) from `README.md` and `scripts/build_site.py`.
   - Removed `"Calibrated Live Model"` linear projection column from `scripts/build_site.py` and `README.md` per Parallel-Run Protocol Rule 3 ("never write a projection as a score").
   - Fixed `sha256_zip` population in `scripts/collect_evidence.py`.

---

## Pass 3 — Whole-Charter & Acceptance Criteria Cross-Check

- **Unique competition-valid `.tif` generated (never copied):** `gemsdoe31-h31m-bstep-xmod-submod-20261025-37654-nan.tif` (`182,571 B`, `37,654` dots, `40.25%` 3-px overlap vs `GEMSDOE32 H33-2-B2`, max `53.16%` across all 7 `GEMSDOE31` rasters).
- **Prevented `"Predicted values must be in range [0, 1]"`:** Independent rasterio readback and `submission.py` 21/21 checks confirm `0` NaN inside footprint, values strictly `{0.0, 1.0}` inside footprint, `NaN` outside footprint (`0.0` outside in `-allfinite.tif` fallback), `EPSG:32611`, `3730x3292`, exact affine transform.
- **Obvious readiness on `docs/index.html`, `docs/executive-summary.html`, and `README.md`:** All three lead immediately with `YES — VALIDATED & OK TO DOWNLOAD AND SUBMIT` for `H31-M`, one-click download links, unique submission name `GEMSDOE31-H31M-BStep-XMod-Submod-37654`, 102-char portal note, and explicit `DO NOT SUBMIT` warnings on superseded `H31-B` standalone and negative `H31-E`.
- **Automated suite status:** `pytest` passes (`48 passed`), `ruff check .` clean, `check_metric.py` exact (`4.44e-16`), `collect_evidence.py` synchronized, `build_site.py` + `check_site.py` pass (`20` pages, `267` local links, `0` failures).
