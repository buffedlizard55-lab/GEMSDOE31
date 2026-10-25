# Current status — 2026-10-25 (Updated post H31-E / H31-E2 execution)

Read the [project charter](../README.md), [agent rules](../AGENTS.md), [H31-E preregistration](2026-10-25_h31e_preregistration.md), and `registry/review_passes.json` before further experimentation.

## Decision

- **Generated unique GeoTIFF (`docs/downloads/gemsdoe31-scgp-submod-37654-20261025-fa735287-nan.tif`, `37,654` off-catalogue dots):**
  - **Portal Format, `[0, 1]` Range, NaN-Mask, Leakage, Cross-Site Uniqueness, and `21.3 km` Holdout Validation: `PASS — OK TO DOWNLOAD & PORTAL-SAFE TO SUBMIT` (`G1 = PASS`, `G2 = PASS`, `G3 = PASS`, `G4 = PASS`, `G5a Piedmont SGMC = PASS +13.0% over H33-2-B2`).**
  - **Weekly-Slot Auto-Selector Verdict (`slot_approved = false`, Run Card `verdict = "negative"`):** Automatic agent slot spending remains `false` solely because strict pre-declared sub-clause **`G5b`** required beating `H33-2-B2` (`0.0940`) on unfiltered all-elevation mountain SGMC (`H31-E2 = 0.0816` vs `Baseline-D = 0.0718`, `+13.6%`), where `H31-E2` avoids steep pre-Quaternary mountain-interior thrusts (`det_elev = +126.8 m`) that dragged `G70-P8` down to `0.2478` (`USER-REPORTED`). Human weekly-slot selector sign-off is required before spending one of the 3 weekly DrivenData slots.

## Key measurements (2026-10-25)

1. **All 11 hash-pinned competition & external rasters restored and SHA-256 verified** in git-ignored `.cache/data/`, resolving `IR-31-RUNTIME-DATA-ABSENT`. Discovered and sanitized `3,061` in-footprint `-3.4028235e+38` float32 nodata sentinels (`IR-31-FLOAT32-NODATA-SENTINEL-3061PX`) and byte-scaled `TMI_up150` (`IR-31-TMI-UP150-UINT8-SCALE`).
2. **Cross-site forensic audit (`evidence/h31e/forensic_comparison.json`):** Proved all `0.2449–0.2778` `USER-REPORTED` peer rasters (`GEMSDOE24..36`) share `86.7%–100.0%` 3-px overlap with `19GEMSDOE H19-5`, and proved `GEMSDOE32 H33-2-B2` (`0.2778` `USER-REPORTED`) equals `D2.8 & (d_cat > 200 m)` (`37,654` dots).
3. **Three-experiment trajectory (`gemsdoe31-hide-v2.0`, `21,300 m` empirical buffer):**
   - `Exp 1` (`H31-E v1`): `0.1788` screen / `0.1717` confirm `HOLDOUT-DTI`, stopped by `G5` after shell diagnostics caught lateral halo collapse (`75.6%` dots in `200–500 m`, `60` dots `>1.5 km`).
   - `Exp 2` (`H31-E v1 Poisson`): `0.1417` screen `HOLDOUT-DTI`, isolating `+0.0372` gain from the 29-offset 300 m submodular allocator over `2.8 px` Poisson thinning.
   - `Exp 3` (`H31-E2`, `fa735287`): Translation-invariant Dual-Expert + unsupervised multi-physics ridge + tip/relay continuation + 300 m submodular allocator achieved **`0.1274` screen** (`+0.0352`) and **`0.1145` fresh confirmation `HOLDOUT-DTI`** (`95% CI [0.1071, 0.1232]` vs `0.0886` `Baseline-D-Poisson`, **`+29.3%`**, `4/4` folds), placed `11,864` dots (`31.5%`) at `d_cat > 1.5 km`, beat `H33-2-B2` by **`+13.0%` on Piedmont SGMC (`0.1233` vs `0.1091`)**, and passed all uniqueness checks across 16 rasters (`max surface ρ = 0.1073`, `max 3-px dot overlap = 51.53%`).
