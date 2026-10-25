# Preregistration — H31-E surface-expression lane (2026-10-25, frozen before any fit)

Session lane for the parallel-run protocol. This file was written **before** any feature
construction or model fit for H31-E. Deviations must be logged as irregularities, not silently
absorbed. Budget: 3 experiments (EXP-1 canary/screen, EXP-2 model holdout, EXP-3 emission/build).

## Why the fleet best (H33-2-B2, USER-REPORTED 0.2778) is not this lane

Locally verified geometry (`evidence/h27_geometry.json`, recomputed lineage): the GEMSDOE25 D2.8
dot set (44,090 dots, USER-REPORTED 0.2600) → delete dots within 100 m of the public catalogue =
H27-4 (40,199 dots, USER-REPORTED 0.2708) → delete dots within 200 m = H33-2-B2 (37,654 dots,
USER-REPORTED 0.2778, no organizer receipt; the GEMSDOE32 archive itself labels it UNSCORED — see
`knowledge/session_review_2026-10-25.md`). Each step deletes low-credit catalogue-flank dots from
the **same** H19-5-family surface; under DTI = TPw/(TPw + 0.2·FPw + 0.8·FNw) a dot whose marginal
credit is below break-even (≈0.055 live units; the one controlled thinning step measured 0.031)
lowers the score by existing, so pruning raises it. H33-2-B2 is a strict subset of the local H27-4
raster (Spearman 0.9676, 100% of dots within 3 px) → duplicate by the parallel-run protocol.
Pruning has a hard ceiling: it adds no detections. Beating 0.2778 requires **new genuine
detections** at above-break-even credit per dot, from a different physical signature. That is this
lane's question. (All fleet scores here are USER-REPORTED; no organizer receipt exists in this repo.)

## Ranked candidate hypotheses (generated before implementation)

| Rank | Hypothesis | Layers | Physical signature | Why a catalogue-missing fault shows it | Difference from this repo / occupied lanes | Expected ΔDTI (planning prior, not a result); cost; data status |
|---:|---|---|---|---|---|---|
| **1 — H31-E, selected** | **Surface-expression conjunction**: piedmont flexure + radiometric juxtaposition + LiDAR dipole | `det_elev`, `det_elev_slope` (competition 19-band); LiDAR scarp u8 (12 bands, USGS 3DEP-derived); GeoDAWN radiometrics K/Th/U/TC + ratios ThK/UK/UTh | (a) multi-scale morphological top-hat + Laplacian flexure of det_elev (buried range-front flexures with no discrete scarp); (b) gradient-ridge of radiometric **ratios** (lithologic juxtaposition / alteration along a fault); (c) signed upface−downface LiDAR dipole (one-sided scarp asymmetry) | Catalogue compilation favours mapped Quaternary traces with clear scarps. A fault buried under piedmont alluvium can still flex the detrended surface and juxtapose radiometrically distinct units at bedrock/alluvium contacts, without ever being drawn as a trace | This repo used these bands only as raw HGB scalars (arms B/C/D). The top-hat/flexure, ratio-**gradient-ridge**, and dipole transforms are not implemented here. Deliberately **excludes magnetics/gravity gradients and all catalogue-derived features**, so it is not the H19-5/H27-4/H33 lane (24/25-old/28/30/32), not GEMSDOE25's 2026-10-25 blind-magnetics lane, not GEMSDOE36's Anderson-orientation lane, not GEMSDOE27's strain/conductivity corridor | Planning Δ vs same-run base: 0.000 to +0.010 catalogue-gap; standalone proxy unknown. ~0.5 day. **Data restored & hash-verified this session** (`evidence/data_restore.json: all_verified=true`) → viable now |
| 2 — H31-F | Scarp-degradation age-bank matched filter | 1 m bare-earth DEM tiles | Cross-strike error-function profiles at several diffusion widths; score profile-shape match, not step amplitude | Old degraded scarps are broad/low-amplitude and missed by amplitude detectors and by mappers | Not implemented anywhere in the fleet repos inspected; existing LiDAR channels are step/Laplacian aggregates at 100 m | Unknown. 2–4 days after data access. **Not viable in this sandbox**: needs the competition `1m_DEM_links.csv` (DrivenData login-gated, <https://www.drivendata.org/competitions/306/competition-doe-gems/data/>) or USGS 3DEP 1 m via The National Map (<https://www.usgs.gov/3d-elevation-program>); sandbox egress is GitHub/PyPI/npm only, so obtainability here = **no**. Named free official source exists for an unrestricted machine |
| 3 — H31-G | Quaternary-vent alignment axes | GDR volcanics raster (restored) + det_elev/LiDAR lineaments | Oriented lineament continuity through ≥2 young vents (angular coherence), not isotropic vent distance | Young vents localize on active structures; the connecting structure may be unmapped as a fault | This repo has only `dist_vent_km` (isotropic). Fleet GEMSDOE85 vent-bridge scored USER-REPORTED 0.1110 — adjacent, weak precedent | 0.000 to +0.004. 1–2 days. Data in hand (GDR 1391, CC-BY 4.0, <https://gdr.openei.org/submissions/1391>) |
| 4 — H31-H | Depth-resolved MT conductance-boundary persistence | GDR 1391 / USGS conductance maps (DOI 10.5066/P9TWT2LU) | Cross-depth persistence of conductivity-gradient orientation | Concealed fault/fluid pathway persists at depth without surface trace | Repo has only `cond_surf` + `depth_to_base_surf` scalars; GEMSDOE27's conductivity corridor failed its gate 2026-10-25 | 0.000 to +0.005. 2–4 days. **Not viable here**: product binaries are not on a GitHub mirror and the sandbox cannot reach USGS/GDR hosts; free official source named for an unrestricted machine |

## Frozen H31-E design

### Feature channels (label-free transforms computed from the restored stack; exact list)

Base surface-expression channels (raw stack bands): `det_elev`, `det_elev_slope`, LiDAR
`ex_max, ex_mean, step_max, lapneg_max, lappos_max, downface_max, upface_max, cross_max, relief,
coh100, strike, valid`, radiometric `K, Th, U, TC, ThK, UK, UTh, mean_k_500m, th_minus_k`,
stack-derived `upface_minus_downface`.

New transform channels (the hypothesis; computed in `src/gemsdoe31/surface_features.py`):

1. `tophat_det_3`, `tophat_det_7`, `tophat_det_15` — |white top-hat| + |black top-hat| of
   `det_elev` with flat square structuring elements of half-width 3/7/15 px, invalid cells
   nearest-filled for filtering then re-masked to NaN.
2. `flex_det_2`, `flex_det_5` — |Laplacian-of-Gaussian| of `det_elev` at σ = 2 and 5 px
   (scipy `gaussian_laplace`), same fill/re-mask rule.
3. `ratio_grad_thk`, `ratio_grad_uth`, `ratio_grad_uk` — gradient magnitude of the σ = 1
   Gaussian-smoothed ThK / UTh / UK bands (NaN-aware: fill 0 after standardisation by in-footprint
   median/IQR, re-mask), plus `ratio_ridge_gm` = geometric mean of the three percentile-clipped
   (99th) gradient fields.
4. `dipole_coh` — |upface_minus_downface| × coh100 / 255.

**Forbidden channels**: any catalogue-derived feature (`dist_cat_km`), any SGMC-derived feature
(`dist_sgmc_km` — SGMC is a scoring proxy), magnetics/gravity/strain/seismicity bands (other
lanes), `TMI_up150`. `dist_vent_km`/`dist_probe_km` are excluded to keep the hypothesis test clean.

### Holdout (hide-and-recover; evaluator id `gemsdoe31-holdout-v1`)

- Catalogue = `labels.tif == 1` (60,988 px; 3,199 8-connected components, computed 2026-10-25).
- Folds = 4 quadrants (`raster.quadrant_blocks`, NW/NE/SW/SE).
- For fold *q*: scoring domain = quadrant *q* ∩ footprint, eroded by 12 px (metric-neighbourhood
  guard, per the H31 preregistration). Withheld truth = whole components whose centroid lies in
  the domain; truth pixels = those components' pixels inside the domain. Components straddling
  the domain boundary with centroid outside are excluded from both training positives and truth.
- **Buffer/collar**: training samples (positive and negative) within **21.25 km** of any withheld
  truth pixel are excluded — the empirical residual-semivariogram collar in
  `evidence/buffer_derivation.json`, not an assumed pixel count.
- Visible faults are masked **pixel-exactly** in scoring: predictions on all non-withheld
  catalogue pixels are set to 0 before scoring; predictions outside the domain are 0.
- Scoring = `src/gemsdoe31/metric.py` (α = 0.2, β = 0.8, 300 m triangular kernel, brute-force
  verified ×4.4e-16 in `evidence/metric_check.json`), pooled over folds by summing TPw/FPw/FNw.
- 95% CI: paired spatial-block bootstrap (20 km blocks over the pooled domains, 1,000 resamples,
  seed 20261025) on pooled DTI and on paired Δ vs controls.
- **Leakage canary (EXP-1, before any model result is trusted)**: AUC of every new channel alone,
  withheld-truth vs sampled domain background. AUC > 0.90 ⇒ leakage until proven otherwise ⇒ stop.
- Controls scored identically: (C1) same-run base = HGB on base channels only (new transforms
  removed); (C2) incumbent H27-4 dot set (fixed file; note it was built with full-catalogue
  knowledge, so it is an optimistic catalogue-gap comparator and is never the sole gate);
  (C3) pinned OOF-B surface (`evidence/oof/oof_B_19_plus_lidar_u16.npz`) through the same emitter.
- Second proxy (mandatory per AGENTS.md): off-catalogue SGMC (>300 m from catalogue, 61,664 px)
  scored for candidate and controls on the full footprint. The catalogue-gap holdout alone can
  never promote; a candidate must not lose to the incumbent on the discovery proxy to be
  promote-eligible.

### Model and emitter (frozen)

- `HistGradientBoostingClassifier`: max_iter 100, learning_rate 0.12, max_leaf_nodes 31,
  min_samples_leaf 50, l2_regularization 1.0, class_weight {0:1, 1:5}, no early stopping
  (repo-pinned sibling parameters). NaNs passed natively (HGB handles them).
- Training sample per fold: all eligible catalogue positives; negatives = uniform random
  in-footprint non-catalogue pixels outside (domain ∪ collar ∪ excluded components), cap 300,000,
  seed 20261025 (screen) / 20261026 (confirmation rerun with identical design).
- Emitter (`src/gemsdoe31/emission.py`): Gaussian σ = 1 smoothing → 3×3 ridge NMS (cell must be
  ≥ all 8 neighbours) → score-ordered greedy Poisson thinning, min separation 2.8 px → top-K with
  K = round(domain_pixels × 40199 / 5167373) (incumbent density, fixed a priori). Binary dots
  emitted at value 1.0 (probability-valued emission is not used; the fleet's measured economics
  favour binary dots and it keeps the [0,1] contract trivially satisfiable).

### Uniqueness gates (parallel-run protocol; check surface AND final dots)

- Surface: Spearman rank correlation of the candidate full-footprint surface vs OOF-B and OOF-D
  surfaces (1,000,000-cell seeded sample) must be ≤ 0.90.
- Final dots: fraction of candidate dots within 3 px of any positive cell of **each** registry
  raster (H27-4, union-B P060, add-arm-D, D2.8 reference) must be ≤ 70%, and binary-raster
  Spearman vs H27-4 ≤ 0.90. Exceeding either ⇒ log as duplicate and stop.

### Promotion gates (all required for verdict `promote`)

1. Canary pass (no channel AUC > 0.90).
2. HOLDOUT-DTI: candidate beats same-run base C1 pooled, paired Δ 95% CI excludes 0, candidate
   better in ≥ 3/4 folds, worst fold Δ ≥ −0.010; confirmation seed reproduces the sign.
3. Discovery proxy: candidate off-catalogue DTI ≥ incumbent off-catalogue DTI (0.09385).
4. Uniqueness gates pass. 5. Exact-file format audit passes (`submission.py`, both conventions).
Failure of any gate ⇒ verdict `negative`; the TIFF, if built, is a research artifact labelled
NOT OK TO SUBMIT. Promotion never spends a slot by itself — slot choice is the selector's step.

### Named non-fault mimics (must be reported with results)

Lake Lahontan paleo-shorelines and alluvial-fan lobe boundaries (top-hat/flexure);
lithologic contacts and drainage heavy-mineral concentration (radiometric ratio steps);
roads, canals, mine disturbance, terrace risers (LiDAR dipole).

## Submission identity (reserved at preregistration)

- Name: `gemsdoe31-h31e-surfexpr-20261025-<sha8>` (sha8 from the final `-nan.tif`).
- Portal note (≤140 chars, finalized after dot count known):
  `H31-E surface-expression: det_elev flexure + radiometric ratio ridges + lidar dipole; dotted d2.8; no magnetics/catalogue feats`
