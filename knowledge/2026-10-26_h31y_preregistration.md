# H31-Y preregistration — frozen BEFORE any fitting (2026-10-26, branch `arena/f4d7fb29-gemsdoe31`)

Labels used everywhere: **HOLDOUT-DTI** (evaluator, withheld positives, 95% CI) · **COMPUTED** (raster
measurement) · **USER-REPORTED** (owner-typed, no organizer receipt) · **PROJECTION** (estimate, never a score).
No ORGANIZER-CONFIRMED score exists in this repository. This repository never contacts DrivenData.

## Lane assignment disclosure (IR-U-01)

The prompt's Parallel-Run Protocol §1 says "Your lane is the single method paragraph below", but **no method
paragraph was supplied** (same omission recorded by H31-U and H31-X). Per the owner's overriding instruction
to generate and validate a unique submission autonomously, this session self-assigns and freezes the lane
paragraph below before touching predictors. The previous session's declared next step was
"KIN/TEX costed but not run; budget-split lane (junction + piedmont specialist) is the natural next step."
This lane is that KIN-PIED specialist. H31-X junction dots are **not** reused.

## Lane paragraph (single method — stay inside it)

**H31-Y "KIN-PIED: polarity-concordant LiDAR facing + intra-basin piedmont gravity lineaments".**
In the Basin and Range, synthetic range-bounding scarps face the hanging-wall basin; antithetic hanging-wall
scarps face the range. Isostatic gravity independently defines hanging-wall polarity: the basinward unit
vector is the direction of *decreasing* `iso_grav_anom` (sediment-filled basins are mass deficits). The
candidate surfaces are therefore:

1. **SYNTH** = `downface_max` × `max(0, û_down · û_basin)` on LiDAR-valid cells.
2. **ANTI**  = `downface_max` × `max(0, û_down · û_range)` on LiDAR-valid cells
   (`û_range = −û_basin`). This is the hanging-wall / intra-basin specialist.
3. **GRAVPIED** = `|iso_grav_anom_hg|` restricted to a soft piedmont window on `det_elev_slope`
   (full weight 0–5°, taper to 0 at 10°). Intra-basin buried faults lack QFFD scarps but still
   produce gravity horizontal-gradient ridges on the low-slope hanging wall.
4. **BASEPIED** = `|∇ depth_to_base_surf|` in the same piedmont window.

`û_down` is the downslope unit vector of smoothed `det_elev`. All lines are label-free from the cached
42-band stack. Emission reuses live-proven D2.8→H33 *geometry only* (score-ordered Poisson, min spacing
2.8 px, 37,654 dots, catalogue-flank pruning d > 2 px). **No prior dots, surfaces, or peer rasters enter
the candidate.** Peers are used only for the uniqueness audit and the SGMC / projection instruments.

## Why H33-2-B2 (0.2778 USER-REPORTED) leads, and what this lane can and cannot claim

From `evidence/h33_forensics_20261025.json`: H33 = H19-5 surface → D2.8 Poisson (44,090; 0.2600) →
delete dots ≤1 px from the catalogue (H27-4; 40,199; 0.2708) → delete dots ≤2 px (H33-2-B2; 37,654;
0.2778). Mechanism (INFERENCE, not a score): hidden expert truth is depleted beside already-mapped
faults, so catalogue-flank pruning is FP-budget economics under DTI α=0.2, β=0.8, 300 m triangular
kernel. H31-X already occupies the range-front *junction line* and was weak on the piedmont SGMC
slice (0.043 vs H33 0.059). H31-Y therefore refuses the junction and targets the complementary
regime: polarity-split LiDAR scarps and low-slope gravity/basement lineaments.

A projection is never a score. Beating 0.2778 live is **not claimed** before a holdout screen.

Official sources (for manual review; fetched previously or standard references, not re-scraped here):

- Competition problem: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- About / data notes: https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/
- Reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
- Tversky index: https://en.wikipedia.org/wiki/Tversky_index
- EPSG:32611: https://epsg.io/32611
- USGS GeoDAWN: https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and
- INGENIOUS: https://gbcge.org/current-projects/ingenious/
- GDR 1391: https://gdr.openei.org/submissions/1391
- NLR rules PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf

## Ranked hypotheses not yet run in this repository (label-free unless noted)

| Rank | ID | Layers / physical signature | Why it could catch a catalogue-missing fault | Difference from everything implemented here | Expected gain / cost |
|---|---|---|---|---|---|
| 1 | **Y1–Y4 (selected core, KIN-PIED)** | LiDAR `downface_max` polarity-split by gravity basinward vector; `iso_grav_anom_hg` and `depth_to_base_surf` in a ≤5° piedmont window | QFFD lists recognised Quaternary ruptures, mostly master range fronts. Antithetic hanging-wall faults and buried intra-basin structures appear on geologic maps (SGMC) and in expert labels without a QFFD scarp | AS-1 used antislope *without* gravity polarity and failed; H31-B used hessian magnitude; H31-X used 100 m DEM slope-break *junction* (no LiDAR facing, 82% of dots at slope >6°); H31-U SCARP was step/ex/cross geomean without polarity; MAGREST/PGR31/H31-N are magnetic, not LiDAR-polarity | complementary to H31-X; ~30–60 min |
| 2 | TEX (not run; costed) | RTP structure-tensor orientation/coherence discontinuity | Bedrock faults in volcanics truncate magnetic fabric without a gradient edge | all magnetic lanes here are gradient/phase/restoration | survey-seam mimic; ~45 min; deferred (budget) |
| 3 | Y-ENS (not run) | geometric mean of H31-X junction with GRAVPIED | budget-split range-front + piedmont | would likely fail uniqueness vs H31-X; not a new physical line | deferred |
| 4 | Lahontan paleoshoreline mask | highstand ~1330 m ASL wave-cut benches | suppress a named scarp mimic | `det_elev` is *detrended*; no ASL DEM in the 42-band cache. Official 3DEP exists but is not re-downloaded here. **Not viable without new external data** | blocked |
| 5 | InSAR LOS step | Sentinel-1 / NASA ASF | active strain without a QFFD scarp | ASF/Earthdata hosts are outside this sandbox allowlist | blocked |

Named non-fault mimics for the selected lane: Lake Lahontan shorelines and wave-cut benches (cannot be
elevation-masked with detrended DEM — disclosed), irrigation canals and road cuts, lava-flow snouts,
landslide toes, erosional pediment edges without a gravity step (suppressed by GRAVPIED gate on Y4),
airborne-survey seams (not used: no RTP tensor).

## Frozen experimental plan (≤3 experiments; stop afterwards)

- **EXP-1 (canary + screen).** Leakage canary: ROC-AUC of every line and Y-surface vs the catalogue and vs
  off-catalogue SGMC (200k negative sample); any two-sided value >0.90 = leakage STOP for that feature.
  Screen: arms {Y1=GRAVPIED, Y2=ANTI, Y3=SYNTH, Y4=GRAVPIED×ANTI (geomean × second-line gate),
  CTRL=rank(`tmi_hg`), SLOPE=rank(`det_elev_slope`)} dotted per fold with *visible-catalogue* B2 pruning
  only, vendor `spatial.folds(buffer_px=213)` + unchanged `gems57-pooled-hide-v2`, pooled paired CIs.
  Winner = highest pooled HOLDOUT-DTI among Y1–Y4. No peer raster is a predictor.
- **EXP-2 (one ablation + uniqueness).** If the winner is Y4, compare second-line gate ON vs OFF; keep
  the better on pooled holdout. Final emission on the full visible catalogue (B2). Surface Spearman and
  top-K / final-dot 3-px overlap against every discrete peer (nine focus-site rasters + all local
  GEMSDOE31 downloads, self excluded). |ρ| > 0.90 or overlap > 0.70 vs any discrete peer = duplicate STOP.
  Literal 695-raster spacing-5 lattice reading is recomputed and disclosed (IR-U-02), not exempted.
- **EXP-3 (independent confirmation + packaging, zero tuning).** Seeded random 50% split of whole
  catalogue components (seed 3104), visible half masked pixel-exactly and used for B2 pruning, hidden
  half scored with the same evaluator. Then full-footprint, per-quadrant and slope-regime
  (piedmont ≤6° / mountain >6°) off-catalogue SGMC DTI vs H33 recomputed same code same day,
  anchor-inversion PROJECTION (never a score), vendor `submission_writer.write_submission`, both
  validators.

## Frozen promotion gates (automated; no human inspector)

- **G1 format:** single-band float32, EPSG:32611, 3730×3292, exact transform, finite [0,1] inside the
  footprint, correct outside convention per file, {0,1} values, 0 dots on the catalogue, ≥2.8 px spacing.
- **G2 canary:** every used line/surface two-sided AUC ≤ 0.90 on both truths.
- **G3 efficacy:** pooled HOLDOUT-DTI beats CTRL **and** SLOPE with paired 95% CI excluding 0, ≥3/4
  quadrants ≥ CTRL, and the random-split confirmation paired delta vs CTRL also excludes 0.
- **G4 discovery proxy:** full-footprint off-catalogue SGMC DTI ≥ H33-2-B2's value recomputed the same day.
- **G5 uniqueness (discrete-peer scope, IR-U-02):** final-dot and top-K 3-px overlap ≤ 0.70 and
  |Spearman| ≤ 0.90 vs every discrete peer; literal lattice reading disclosed.
- **G6 projection:** anchor-inversion PROJECTION ≥ 0.2778 (never written as a score).
- Verdict `promote` only if G1–G6 all pass; otherwise `negative` (research download only, DO NOT SUBMIT).
  A negative result is a deliverable. No fourth experiment, no tuning after EXP-3.
  **This lane does not spend a weekly slot.** Selector promotion is a separate step.

## Data

Inputs restored hash-verified from owner mirrors (`scripts/download_competition_data.py`); 42-band cache
built by `scripts/prepare_data.py`. No new external data is required for Y1–Y4. TEX also needs no new
data (deferred). Lahontan and InSAR are blocked as named above.
