# H31-N preregistration — Poisson pseudogravity residual edge

Frozen before any fit in this lane (2026-10-26). Do not edit coefficients, seeds, scales, or gates after looking at holdout numbers. A change requires a new dated preregistration.

## Lane assignment

The parallel-run prompt said the lane was "the single method paragraph below" and did not inject a distinct paragraph. This session therefore adopts one method and does not wander:

**Label-free Baranov / Poisson pseudogravity residual of isostatic gravity against reduced-to-pole magnetics, emitted on the residual's horizontal-gradient ridges.**

GitHub code search on 2026-10-26 for `pseudogravity` and `baranov` in `buffedlizard55-lab` returned 0 hits. That is not proof of absence. Raster rank-correlation and 3 px dot overlap against pinned peer files are the collision test.

This is not H31-K (geodetic pull-apart saddle; still unfitted), not catalogue tip/relay, not tilt, not phase congruency, not a radiometric ratio, not XFCOH31 cross-field offset coherence, not MAGREST texture shift, and not a copy of H33 dots.

## Hypothesis

A fault that juxtaposes non-magnetic density (carbonate or metamorphic basement against basin fill) produces an isostatic-gravity edge that is not explained by the RTP magnetic field. Basaltic flows and magnetic lithologic contacts do the opposite. The Poisson relation (Baranov 1957; Blakely 1995, *Potential Theory in Gravity and Magnetic Applications*) says a uniformly magnetized body's gravity-like field is the RTP anomaly filtered by `|k|^{-1}`. The local residual of observed isostatic gravity after regression on that pseudogravity is the density contrast magnetization does not explain. Its horizontal-gradient ridges are the candidate fault traces.

## Layers

Shared template cache bands only (no new external download):

- Band 02 `rtp` — reduced-to-pole magnetic anomaly (pseudogravity source)
- Band 13 `iso_grav_anom` — isostatic gravity anomaly (regression target)
- Band 03 `tmi_hg` — magnetic horizontal gradient (quiet-edge weight only)

Control arm uses all 19 cached bands and none of the novel features.

## Physical signature (frozen)

1. Subtract the footprint mean of RTP, zero outside the footprint, taper the outer 20 px, FFT.
2. Pseudogravity spectrum = RTP spectrum / `|k|` with `|k|` in rad/m (`2π` times cycles/m). DC bin set to 0. Scale is arbitrary because the next step regresses it out.
3. Local regression at Gaussian `σ = 30` px (3 km) and `σ = 12` px (1.2 km), footprint-normalized:
   `residual = grav - (a + b * pseudogravity)`.
4. Features, each robust-z on the footprint and clipped to [-8, 8], zero where the pixel is within 15 px of the footprint boundary (FFT-boundary mimic):
   - `pg_resid_s30`
   - `pg_resid_hg_s30` (horizontal gradient of the σ=30 residual)
   - `pg_resid_hg_s12`
   - `pg_quiet_edge` = `pg_resid_hg_s30` multiplied by `1 - rank_cdf(tmi_hg)` on the footprint

No catalogue, SGMC, or distance-to-fault array enters the feature function.

## Why this can hit a fault missing from the USGS/INGENIOUS catalogue

The public catalogue and the H19-5/H33 family are dominated by traces with topographic or magnetic expression. A non-magnetic density step under cover has no scarp requirement and is not a magnetic worm. Expert-labeled competition faults are, by the problem statement, faults absent from the public USGS database ([problem page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)). This transform is aimed at that gap. It can still fail the catalogue-segment holdout if withheld catalogue strands are magnetically expressed scarps.

## Named non-fault mimic

Non-magnetic granitoid or pluton roofs, and FFT survey-boundary leakage. The 15 px boundary mask is the preregistered boundary control. Pluton roofs remain a residual mimic; SGMC-versus-catalogue disagreement is reported, not treated as truth.

## Holdout (frozen)

- Shared template `vendor/gems57/holdout.py:buffered_component_draw` and `vendor/gems57/evaluate_holdout.py` (`gems57-pooled-hide-v2`).
- Seeds: screen `41`, confirmation `42` only if the screen gate passes. `hide_frac=0.20`. Quadrant erosion 12 px.
- Training exclusion collar for the scored run: 25 km (250 px), chosen before the fit as a conservative superset of previously measured residual ranges in this repo (largest adopted 21.3 km). It is **not** reported as this method's empirical range.
- After the screen OOF, compute this method's residual semivariogram with `gemsdoe31.variogram`. If the bootstrap upper 95% practical range exceeds 25 km, the screen number is not a valid HOLDOUT-DTI and the lane stops without a second fit.
- Visible faults masked pixel-exactly. Catalogue features: none.
- Emission inside each fold: ridge NMS + score-ordered Poisson thinning, minimum separation 2.8 px, budget `round(37654 * domain_pixels / footprint_pixels)`, dots on visible-catalogue pixels and their 2 px halo excluded. The 2 px halo uses **visible** faults only.
- Pooled DTI, alpha 0.2, beta 0.8, 300 m triangular kernel, paired spatial-block bootstrap (`block_side=200`, 1000 draws, seed 520810).
- Same-run control: identical HGB and emitter on the 19 cached bands only.
- Screen pass (required before confirmation): candidate DTI > control DTI, paired 95% CI lower bound > 0, and at least 3 of 4 quadrants won.
- SGMC off-catalogue (>300 m from the public catalogue) is a second proxy, labeled HOLDOUT-PROXY-SGMC, never a competition score, never a promotion criterion by itself.

## Model (frozen)

`HistGradientBoostingClassifier(max_iter=100, learning_rate=0.08, max_leaf_nodes=31, min_samples_leaf=50, l2_regularization=1.0, early_stopping=False)`.
Positives: all allowed catalogue pixels. Negatives: 150,000 footprint pixels, seed 31026. Same for every arm.

## Leakage canary

Each novel feature alone, AUC vs catalogue on a 400,000-pixel footprint sample (seed 31026), and AUC vs withheld vs visible-domain negatives inside the screen folds. Symmetric AUC above 0.90 is leakage until the feature code is shown not to read labels. If the code reads no labels and AUC still exceeds 0.90, stop and do not treat it as a pass.

## Uniqueness

Before final placement: full-footprint Spearman of the submission surface vs each compared raster. After placement: fraction of dots within 3 px (Euclidean) of that raster's positive pixels.

Stop and do not package if any **scientific** compared raster has `|ρ| > 0.90` or overlap `> 0.70`.

Compared set (not a complete 695-raster scan): all `docs/downloads/*.tif` in this repo, plus the peer files downloaded into `data/prior_audit/peers/` (H33-2-B2, H29, Anderson, D2.8, H36-1, H27-4, H33D, and the same-day strain-saddle / graben-pair / blind-basin / tilt-coherence files). Scope is stated on the run card. Incomplete scan cannot promote.

The spacing-5 calibration lattice `r13-lattice-s5` was measured this session: **99.871%** of footprint pixels lie within 3 px of a lattice dot (`evidence` receipt written by the runner). Under the literal rule that is a universal overlap failure. It is reported separately. `ok_to_submit` stays false. No density exemption is invented. Packaging a scientifically non-duplicate research TIFF is still required by the owner prompt; the banner must say DO NOT SUBMIT.

## Emission for the file

Full-catalogue fit (legal at submission time: public faults are known; hidden test faults are not in that raster). Poisson 2.8 px, budget 37,654, delete dots on the public catalogue and within 2 px. Values exactly `{0, 1}` inside the footprint.

Two encodings, both validated:

- `*-zeros.tif`: all finite, 0 outside. This is the file to upload if the portal returns `Predicted values must be in range [0, 1]`.
- `*-nan.tif`: NaN outside, matching the written problem-page sentence that data outside the bounds is null or NaN. Not claimed to be the file the portal accepted.

## Promotion

`slot_approved` only if screen pass, confirmation pass on seed 42 with the same rule, peer uniqueness pass, leakage pass, validator pass, and the literal lattice overlap does not fire. The lattice measurement already shows it will fire. Expected verdict before the fit: research file at best, not a weekly slot.

## Experiments (maximum 3)

1. Canary + lattice coverage measurement. Leakage or a feature that reads labels → stop, no model.
2. Screen holdout + variogram. Collar insufficient or peer-surface `|ρ| > 0.90` before placement → stop, no TIFF.
3. Confirmation only if the screen gate passes; otherwise final fit, peer dot-overlap check, SGMC proxy, and packaging only if peer uniqueness passes. Verdict negative if the screen gate fails.
