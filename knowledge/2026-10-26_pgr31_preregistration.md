# PGR31 preregistration — frozen 2026-10-26 before any PGR31 feature, fit, holdout score or TIFF

Status at freeze: **no PGR31 feature, prediction, holdout number, or TIFF has been computed.**
Inputs were restored and hash-verified only (`evidence/pgr31_data_restore_core.json`,
`evidence/pgr31_data_restore_external.json`; `all_verified: true` in both). A hash match proves byte
identity to the owner mirrors in `registry/data_manifest.json`, not organizer authenticity.

## Lane-assignment irregularity (disclosed, not hidden)

The owner prompt says *"Your lane is the single method paragraph below"*, but the prompt as received
contains **no single assigned method paragraph** (the same omission recorded in
`knowledge/2026-10-25_next_session.md` and `registry/review_passes.json` `remaining_work`).
The same prompt also orders this session to *"generate 3–5 candidate geological hypotheses we haven't
tried yet … Rank them … Validate the top candidate on our spatially-blocked holdout"*. This session
therefore self-assigns exactly one lane from its own ranked list below (the XFCOH31/H31-S precedent in
this repository), discloses that assumption here, and does **not** pick a weekly slot: promotion to a
real slot remains a separate selector step (protocol rule 6).

## Ranked untried hypotheses (layer · signature · why a catalogue-missing fault · what is new)

Ranking is ordinal (expected HOLDOUT-DTI gain × implementation cost). No figure below is a
projection written as a score. "Untried" was checked by text search of this repository's
`knowledge/`, `src/` and `scripts/` on 2026-10-26 (e.g. `pseudograv*` / `pseudo-gravity`: zero hits
outside Poisson-disk thinning).

| Rank | Hypothesis | Layers (verified band descriptions, see below) | Physical signature | Why it can catch a fault missing from the USGS/INGENIOUS catalogue | Difference from anything in this repo | Cost / data check |
|---|---|---|---|---|---|---|
| **1 — SELECTED: PGR31 Poisson pseudo-gravity discordance** | `rtp` (training band 2) Fourier vertically integrated to pseudo-gravity (Baranov 1957; Poisson relation), locally regressed against `iso_grav_anom` (band 13); `depth_to_base_surf` (band 15) only as base-stack context | Pseudo-gravity gradient; local (σ=6 px masked-Gaussian) Pearson correlation, regression slope (a magnetization-to-density-ratio proxy), slope-field gradient, and local-regression residual gradient between pseudo-gravity and observed gravity | A buried normal fault juxtaposes basement blocks with different density/magnetization ratios under alluvial cover: no scarp to map (catalogue traces come mainly from surface/geologic evidence; ~39% of known Great Basin geothermal systems are blind and up to ~75% of resources are estimated blind — Faulds & Hinz 2015), but the Poisson slope/residual still steps across the fault | XFCOH31 compared *raw* RTP vs gravity gradients (mismatched derivative order / dipolar RTP); SCGP cross-gradients used gradient-direction products; H31-T used analytic-signal contact depth. No prior arm vertically integrated RTP to pseudo-gravity (equalising derivative order so the two potentials are commensurable) nor used a *local Poisson regression slope/residual* as features | Low–moderate (one FFT + Gaussian moments on restored, hash-verified inputs; no new external data) |
| 2 — RADISP radiometric flank-displacement | GeoDAWN `K,Th,U` + `ThK,UK,UTh` (external u8 stacks) | Cross-flank patch-correlation gain at ±2/4 px shifts of the radiometric ternary ratios (the MAGREST operator applied to radiometrics, not magnetics) | A fault laterally offsets surficial provenance units even where its scarp is buried/eroded | MAGREST restored displaced *magnetic* texture only; radiometrics entered prior arms as raw pixel values | Moderate; inputs restored + hash-verified this session — not run (one-lane budget) |
| 3 — SEISALIGN seismicity/strain anisotropy | `ieq_n100a15` (16), `deq_n100a15` (10), `geod_shearrate` (7), `geod_dilaterate` (8) | Anisotropic (structure-tensor) ridge of earthquake-intensity × shear:dilatation partitioning | Actively creeping/seismogenic blind faults align microseismicity before a trace is mapped | Prior arms used these four bands only as unoriented scalars | Low, but band descriptions state 100 km / 15° smoothing parameters, so 100 m localisation is expected to be poor — ranked down on that verified metadata |
| 4 — HINGE basement-depth hinge line | `depth_to_base_surf` (15), `iso_grav_anom_vg` (11) | Cross-strike curvature sign-change of basement depth phase-locked to gravity vertical-gradient zero crossings | Listric rollover over a buried pediment fault warps basement depth without a surface scarp | Overlaps H31-M's `bstep_inflect` and the unrun H31-BGF sketch — low novelty, ranked down for lane-drift risk | Low; not run |
| 5 — INSAR phase discontinuity | Sentinel-1 ARIA (NASA ASF DAAC, https://asf.alaska.edu) | Line-of-sight phase-gradient barriers across creeping traces | Aseismic creep on an unmapped fault breaks InSAR phase continuity | No InSAR layer exists in this repo | **Not viable this session:** ASF requires Earthdata account access and the host is outside this sandbox's allowlist (github/pypi only); named here as the specific free official source for an unrestricted runner, per protocol |

## Frozen PGR31 design (no tuning after this file)

### Inputs (all hash-pinned owner mirrors; band identity read from the files this session)

- `data/training_features.tif` — 19 float32 bands; descriptions verified 2026-10-26:
  1 `mag_anom`, 2 `rtp`, 3 `tmi_hg`, 4 `geod_2ndinv`, 5 `iso_grav_anom_slope`, 6 `tc`,
  7 `geod_shearrate`, 8 `geod_dilaterate`, 9 `tmi_vg`, 10 `deq_n100a15`, 11 `iso_grav_anom_vg`,
  12 `det_elev`, 13 `iso_grav_anom`, 14 `tmi`, 15 `depth_to_base_surf`, 16 `ieq_n100a15`,
  17 `cond_surf`, 18 `iso_grav_anom_hg`, 19 `det_elev_slope`.
- `data/external/lidar_scarp_features_u8.tif` — 12 uint8 bands
  (`ex_max, ex_mean, step_max, lapneg_max, lappos_max, downface_max, upface_max, cross_max, relief,
  coh100, strike, valid`); **`valid` (band 12) is excluded** (coverage-leakage precedent in this repo).
- `data/external/geodawn_rad_u8.tif` (`K, Th, U, TC`) and `geodawn_extensions_u8.tif`
  (`ThK, UK, UTh, TMI_up150`). uint8 value 0 is the files' nodata → treated as missing (NaN).
- `data/labels.tif` (public catalogue, training labels / holdout truth only — never a feature),
  `data/sample_submission.tif` (footprint/template), `data/external/derived_sgmc_faults_100m_u8.tif`
  (off-catalogue SGMC proxy truth only — never a feature or training label).
- No catalogue-derived feature (no distance-to-catalogue, tip, or relay features) is used by either arm,
  so the fold-visible-catalogue leakage channel documented in H31-S cannot occur. The ≤2 px catalogue
  exclusion below is an **emission-domain rule only**, applied with the fold's `masked_known` in holdout.

### Base stack (identical in both arms; 38 features)

19 training bands (invalid = non-finite or ≤ −1e30 → NaN; robust z `(x−median)/(1.4826·MAD)` over
finite footprint cells, clipped [−8, 8], NaN preserved) + 11 lidar bands + 8 radiometric bands
(each `u8/255`, 0 → NaN).

### Novel features (candidate arm only; 9 features, all label-free and deterministic)

Let `R` = band 2 (rtp) footprint-finite field. Pseudo-gravity (Baranov vertical integration of RTP):
fill non-finite/outside-footprint cells with the finite-footprint median, subtract the
finite-footprint mean, then `PG = irfft2( rfft2(R) / |k| )` with `|k|` the angular wavenumber
magnitude (rad/px) and the `k = 0` coefficient set to 0. `pg` = robust-z(PG) over the footprint,
clipped [−8, 8]; `g` = robust-z(band 13) likewise. Local moments use **footprint-masked Gaussian
normalised convolution** at σ = 6 px: for fields a, `mean(a) = G(m·a)/G(m)` with `m` the footprint
mask (and `a` finite), `cov`, `var` analogously. Features:

1. `pg_z` = pg
2. `pg_grad_s15` = |∇ G₁.₅(pg)|
3. `pg_grad_s30` = |∇ G₃(pg)|
4. `grav_grad_s15` = |∇ G₁.₅(g)|
5. `pg_grav_mincoh` = min( robust-z(pg_grad_s15), robust-z(grav_grad_s15) )
6. `pg_grav_localcorr6` = cov₆(pg, g) / sqrt(var₆(pg)·var₆(g)) (0 where either variance ≤ 1e-12)
7. `pg_grav_slope6` = cov₆(pg, g) / var₆(g), clipped [−8, 8] (0 where var₆(g) ≤ 1e-12)
8. `pg_slope_grad` = |∇ G₁.₅(pg_grav_slope6)|
9. `pg_resid_grad` = |∇ G₁.₅(pg − (mean₆(pg) + pg_grav_slope6·(g − mean₆(g))))|

All nine are forced finite inside the footprint (asserted) and 0 outside it. Named non-fault mimic:
**unfaulted pluton margins / caldera ring contacts**, where magnetization-to-density ratio changes
without brittle offset, and GeoDAWN survey-block levelling seams (the survey was flown in blocks with
different specifications — USGS GeoDAWN data release, DOI 10.5066/P93LGLVQ).

### Model, emitter, holdout (identical for candidate and control; only the feature set differs)

- Model: `HistGradientBoostingClassifier(max_iter=100, learning_rate=0.12, max_leaf_nodes=31,
  min_samples_leaf=50, l2_regularization=1.0, early_stopping=False)`, sample weight 5 for positives
  (the MAGREST physical-control configuration already used in this repo).
- Holdout instrument: unchanged shared template `vendor/gems57/holdout.py:buffered_component_draw`
  + `vendor/gems57/evaluate_holdout.py` (`gems57-pooled-hide-v2`, α=0.2, β=0.8, 300 m triangular
  kernel): whole 8-connected components withheld (hide_frac=0.20), `buffer_px=boundary_px=213`
  (21.3 km — the inherited empirical collar, `evidence/buffer_derivation.json`; disclosed as
  inherited, **not** re-derived for PGR31, so PGR31's own-method range is unknown and this alone
  blocks any claim beyond this instrument). Visible faults are masked pixel-exactly via
  `masked_known`; pooled DTI (never mean-fold DTI); paired 20 km spatial-block bootstrap
  (`pooled_summary`, 1000 draws).
- Per fold (quadrant q of the draw): train on `footprint & quad≠q & EDT(quad≠q)>213 & ~hidden_all`;
  positives = all `visible` catalogue pixels in that mask; negatives = seeded sample (seed
  `51000+100·draw_seed+fold`) of 120,000 from `train & ~catalogue & dist_to_catalogue>3 px`
  (hidden pixels are in neither class). Predict the fold quadrant; emit with the shared
  `gemsdoe31.magrest.spaced_dots` (score-ordered, min separation 2.8 px) under
  `allowed = footprint & region & ~masked_known & dist_to_masked_known>2 px` at budget
  `round(37654 · footprint(region)/footprint(all))`.
- Both truth proxies are reported per arm: catalogue hide-and-recover **and** the off-catalogue
  SGMC proxy (`sgmc & dist_to_catalogue>3 px`). SGMC is a 1:500k state-map proxy, not hidden truth.

### Experiments (max 3, in order; stop rules binding)

1. **EXP-1 — leakage canary + screen (draw seed 51).** Each of the 9 novel features alone:
   ROC-AUC vs withheld truth (positives = withheld pixels in the scored regions; negatives = seeded
   200,000 sample from scored regions & ~catalogue). Symmetric AUC = max(AUC, 1−AUC) **> 0.90 on any
   feature = leakage STOP: no holdout trust, no TIFF.** Otherwise run both arms on draw 51.
2. **EXP-2 — fresh confirmation (draw seed 52)**, run **only if** EXP-1 screen passes the promotion
   screen below. If EXP-1 fails, EXP-2 is skipped (burned-draw tuning is prohibited).
3. **EXP-3 — final surface + registry gates + packaging.** Fit the candidate on the full footprint
   (positives = all 60,988 catalogue pixels; negatives = seeded 200,000 as above; seed 51099).
   *Pre-placement surface gate:* Spearman ρ between the continuous candidate surface and every
   registry raster (200,000 seeded footprint sample) must satisfy |ρ| ≤ 0.90.
   Emit 37,654 dots (`dist_to_catalogue>2 px`); *final-dots gate:* ≤ 70% of dots within 3 px of any
   one registry raster's positive support, and final-dots |ρ| ≤ 0.90. Registry scope = every
   `docs/downloads/**/*.tif` already in this repo **plus** the fetched nine-focus-site best files
   (hash-checked against `evidence/nine_site_forensic_audit.json`). Package with the unchanged
   template writer `vendor/gems57/submission_writer.py` (primary all-finite file) and write the
   NaN-outside twin; validate both with `gemsdoe31.submission.validate_submission`.
   **Duplicate/leakage STOP at any gate = no new TIFF is packaged** (the surface/dots are logged and
   the run card records the stop).
   The registered spacing-5 *calibration lattice* degeneracy (any non-empty dot set is ~100% within
   3 px of it; `evidence/tgj31/registry_universal_blocker.json`) is **reported separately and not
   silently exempted**: it is a non-submission control, so the lane gate above is applied to genuine
   submission rasters and the lattice result is disclosed in the run card exactly as XFCOH31 did.
   No global uniqueness is claimed beyond the stated scope.

### Promotion screen (per draw; all must hold on EXP-1 and, if run, EXP-2)

Candidate (base38+novel9) vs control (base38): pooled HOLDOUT-DTI Δ > +0.002 with paired 95% CI
lower bound > 0; candidate wins ≥ 3/4 quadrant folds; worst fold Δ ≥ −0.010; and candidate SGMC-proxy
pooled Δ > 0 on the same draw (the catalogue proxy alone never promotes — `AGENTS.md`).
Verdict **promote** (eligible for the separate selector step) requires canary pass + both registry
gates pass + the screen passed on **both** draws 51 and 52. Anything else is verdict **negative**:
the TIFF (if not stopped for duplicate/leakage) is a research-only download, `ok_to_submit: false`.

### Sources (verified 2026-10-26; for manual review)

- Competition + metric: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
  · rules PDF https://docs.nlr.gov/docs/fy26osti/96647.pdf
- Pseudo-gravity / Poisson relation: Baranov (1957) via SEG Wiki "Dictionary:Pseudogravity"
  https://wiki.seg.org/wiki/Dictionary:Pseudogravity ("vertical integration of reduced-to-the-pole
  magnetic data"); Fedi et al. (1989), *Terra Nova*, DOI 10.1111/j.1365-3121.1989.tb00433.x.
- GeoDAWN airborne magnetic/radiometric data: USGS data release, DOI 10.5066/P93LGLVQ,
  https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and
- Blind Great Basin geothermal systems: Faulds & Hinz (2015), Proc. World Geothermal Congress,
  https://www.osti.gov/servlets/purl/1724082 (~39% of known systems blind; up to ~75% of resources
  estimated blind; step-overs/relay ramps the most favourable host setting).
- INGENIOUS: https://gbcge.org/current-projects/ingenious/ · GDR 1391 https://gdr.openei.org/submissions/1391
- Grid CRS: https://epsg.io/32611 · Tversky index: https://en.wikipedia.org/wiki/Tversky_index

No DrivenData page was scraped, polled or submitted to. All scores quoted anywhere in this session
remain **USER-REPORTED** unless copied from an organizer receipt (none exists in this repo).
