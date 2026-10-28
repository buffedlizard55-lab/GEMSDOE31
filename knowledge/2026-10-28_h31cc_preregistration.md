# H31-CC preregistration — cover-concealed basement step

Frozen before any fit, uniqueness measurement, or holdout score. Session `arena/bb6d6287-gemsdoe31`. Date 2026-10-28.

## Lane assignment disclosure

The parallel-run prompt says the lane is “the single method paragraph below.” That paragraph is not in the prompt. The same prompt orders 3–5 new hypotheses and validation of the top one on the spatial holdout before any weekly slot. This file is that assignment. No other hypothesis will be fit in this session.

## Ranked hypotheses (not yet fit)

| Rank | Name | Layers | Signature | Why it can hit a catalogue-missing fault | Difference from this repo | Named mimic | Expected value / cost |
|---:|---|---|---|---|---|---|---|
| 1 | H31-CC cover-concealed basement step | B15 `depth_to_base_surf`, B19 `det_elev_slope`, B18 `iso_grav_anom_hg`, B8 `geod_dilaterate` | Horizontal gradient of basement depth, kept only where slope is below 4°, ranked with gravity horizontal-gradient magnitude, optionally requiring positive dilatation | Public Quaternary catalogues map scarps. A blind or alluvium-covered normal fault can still step basement depth and gravity without a ridge. Ridge, scarp, and piedmont-junction families require topographic expression. | H31-X uses a 3–15° slope-break window. This is the complement: slope < 4° and a basement step. Not tilt-worm, Euler, radiometric ratio, or catalogue dilation. | Depositional isopach pinch-out, lithologic density contact, gravity terrain residual, playa compaction | Selected. Medium official-score ceiling if hidden faults lack scarps; catalogue-gap holdout may be weak. Low cost: bands are in the pinned cache. |
| 2 | Signed cross-field texture offset | B2 RTP, B13 isostatic gravity | Coherent lateral offset between matched magnetic and gravity texture along a corridor | A transfer fault can offset a basement contact without a continuous scarp | Not MAGREST same-field restoration and not edge-orientation coherence | Flight-line seam, pluton contact | Higher ceiling, high cost. Not fit. No new external data required. |
| 3 | Computed magnetic tilt zero-contour under cover | B9 `tmi_vg`, B3 `tmi_hg`, B19 slope | `arctan(vg/hg)` near zero, slope < 4° | Magnetic contact under cover | Band `tc` is unsigned (about 3–89) and is not this operator. Tilt-worm submissions already exist (GEMSDOE76, USER-REPORTED 0.2343), so this is not claimed novel. | Flight-line gradient, cultural noise | Not selected. Prior art. |
| 4 | Conductivity–magnetic contact | B17 `cond_surf`, B3 `tmi_hg` | Conductivity gradient coincident with magnetic horizontal gradient, low slope | Hydrothermal clay along a concealed fault | Not the radiometric K-alteration family | Playa brine, clay-rich basin fill | Low expected value: conductivity percentiles are smooth. Not fit. |
| 5 | Channel deflection on the 100 m DEM | B12 `det_elev` | Abrupt, coherent channel-azimuth offset | A fault can deflect drainage after the scarp is buried | Not slope-break or gap-closure | Fan avulsion, canal, lithologic knickpoint | Viable later from the competition stack. High cost at 100 m. Not fit. |

No candidate needs a new external dataset. All five use the competition feature stack already mirrored in this repository.

## Frozen H31-CC operator

- Smooth `depth_to_base_surf` with Gaussian σ = 2.0 px, then horizontal gradient magnitude.
- Low-slope gate: `det_elev_slope` < 4.0. Prior lanes treated this band as degrees. This session does not re-estimate units.
- CC1 = rank of that gradient inside the footprint, zero outside the low-slope gate and outside the footprint.
- CC2 = geometric mean of CC1’s rank and the rank of absolute `iso_grav_anom_hg`, same gate.
- CC3 = CC2 where `geod_dilaterate` > 0, else 0. CC3 is the preregistered primary.
- NULL = the same low-slope gate with frozen random scores (`numpy` Generator seed 310031). Same budget, same spacing. This is the same-run chance incumbent.
- Emission: score-ordered Poisson disk, minimum distance 2.8 px, budget 37,654, only where the arm is positive and distance to **visible** catalogue faults is > 2 px. No retuning of spacing, budget, or slope after scores.
- Catalogue-derived features: none. No catalogue distance, density, or strike enters the surface.
- Holdout: `gems57.spatial.folds`, `buffer_px=80` (shared-template default, 8 km). Not a new variogram. Evaluator `gems57-pooled-hide-v2`, α=0.2, β=0.8, 300 m triangular kernel. Visible faults masked pixel-exactly by the shared evaluator.
- Confirmation, only if the primary’s screen paired 95% interval versus NULL is entirely above 0: the same `folds` function is not reused. Confirmation uses label-blind quadrants split at row `height//3` and column `width//3`, whole intersecting components withheld, buffer 80 px. Thresholds stay frozen.
- Leakage canary: each input feature alone, AUC on the screen holdout positives versus a frozen negative sample. AUC above 0.90 is leakage until proven otherwise and stops promotion of any arm that uses that feature.
- Uniqueness, before placement and on final dots: Spearman on the full footprint and fraction of dots within 3 px. Stop if |ρ| > 0.90 or overlap > 0.70 against any comparable submission raster in the nine focus sites or local `docs/downloads`. The spacing-5 calibration lattice is measured and disclosed. It is a degenerate control (3 px halo covers the interior of a 5 px grid), not a scientific lane. It is not silently exempted: `ok_to_submit` stays false if lattice overlap exceeds 0.70.
- Promotion to a downloadable research TIFF requires a pass against submission rasters and no leakage stop. It does not authorize a weekly slot. `ok_to_submit` also requires beating the same-run NULL and the same-instrument H31-X fixed reference, a passing confirmation, and a lattice overlap at or below 0.70. A projection is never a score.

## What this file does not claim

No organizer receipt exists here for 0.2778, 0.3195, or 0.4413. Those remain USER-REPORTED or prompt-supplied and conflicting. This operator is not a copy of H33-2-B2.
