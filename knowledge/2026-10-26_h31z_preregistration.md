# H31-Z preregistration — frozen BEFORE any fitting (2026-10-26, branch `arena/15e685db-gemsdoe31`)

Labels used everywhere: **HOLDOUT-DTI** (evaluator version, withheld positives, 95% CI) ·
**COMPUTED** (raster measurement) · **USER-REPORTED** (owner-typed, no organizer receipt) ·
**PROJECTION** (estimate, never a score) · **ORGANIZER-CONFIRMED** (submission-page receipt only).
No ORGANIZER-CONFIRMED score exists in this repository. This repository never contacts DrivenData.
Core values (owner charter): **Maximize P(Win)** and **Own the Outcome** — respect failed gates
rather than promise a score.

## 1. Lane assignment disclosure (irregularity IR-U-01, repeated)

The prompt's Parallel-Run Protocol §1 says "Your lane is the single method paragraph below", but
**no method paragraph was supplied** (full prompt read; every earlier session recorded the same
omission). Per the owner's overriding instruction to generate and validate a unique submission
autonomously, this session self-assigns and freezes the single lane paragraph in §4 before
building any line, canary or holdout. This disclosure is part of the frozen record; the lane must
not be widened after seeing results.

## 2. Registry-scope disclosure (IR-U-02, as established by H31-U/H31-X/H31-Y)

Uniqueness for the upload decision is judged against **discrete submission-like peer dot fields**:
the nine focus sites' hash-verified downloadable submissions present under
`data/prior_audit/**/downloads/` plus every local GEMSDOE31 file under `docs/downloads/*.tif`,
byte-identical twins measured once, representation class `dot_field` only. Thresholds (owner rule,
Parallel-Run Protocol §1): duplicate iff |Spearman ρ| > 0.90 **or** > 70% of dots within 3 px of
one peer's dots — checked on the pre-placement surface top-K support **and** on final dots.

The literal 695-raster template-registry reading is additionally **computed and disclosed** via
the registered spacing-5 lattice witness (206,895 dots; ~99.9% of the footprint lies within 3 px
of it, so at a 37,654-dot budget the counting bound forces ≥ ~82% overlap for *any* placement;
see `evidence/review_9883b598/`). That witness is a calibration control, not a submission; the
owner's duplicate rule is written about lane/submission rasters ("you have drifted into another
lane"). Treating calibration lattices as peers makes a unique submission mathematically
impossible and nullifies the owner's primary instruction. The lattice number is therefore a
disclosed diagnostic, never silently exempted: it appears on the run card, and **if a future
owner instruction restores the literal reading, every promotion in this session reverts to STOP**
(AGENTS.md amendment 2026-10-26). If the discrete-peer check fails, this lane STOPS (duplicate),
packages nothing as submittable, and says so.

## 3. Why H33-2-B2 leads the nine focus sites (COMPUTED facts; full analysis in the executive summary)

From `evidence/h33_forensics_20261025.json` (byte-level, COMPUTED): the nine sites' best files are
one nested family — H19-5 surface (0.1922 USER-REPORTED) → D1.5 dots 60,069 (0.2477) → D2.8
Poisson dots 44,090 (0.2600) → delete dots ≤1 px from the public catalogue (H27-4, 40,199,
0.2708) → delete dots ≤2 px (H33-2-B2, 37,654, **0.2778 USER-REPORTED**, no organizer receipt).
H33 adds zero dots; it deletes 2,545 catalogue-flank dots. With
`DTI = T / (0.2·T + 0.2·F + 0.8·K)` (α=0.2, β=0.8, 300 m triangular kernel), a non-redundant dot
helps iff its kernel credit `k > α·S` (0.0556 at S=0.2778, i.e. within ≈283 m of uncovered truth);
anchor inversion over the eleven in-family rasters implies ≈13.4k hidden-truth pixels and
≈0.004 TPw per flank dot — hidden expert truth is depleted beside mapped faults, so flank pruning
is FP-budget economics, not new geology. For fixed n=37,654, S≈T/(0.2n+0.8K): 0.2778⇒T≈5.1k
(≈38% hidden recall); 0.44⇒T≈8.0k. **The only remaining lever is a surface whose top 37,654
far-field locations carry more hidden truth per dot.** The current holdout best in this repo is
H31-X's piedmont-junction line: HOLDOUT-DTI 0.1661 [0.1499, 0.1821] (`gems57-pooled-hide-v2`,
60,988 withheld). Its disclosed weakness: 82% of dots at slope >6°; piedmont (≤6°) off-catalogue
SGMC slice 0.0433 vs H33 0.0586 (COMPUTED). H31-X's own executive summary names the next step:
cover the piedmont/intra-basin regime the junction starves. Owner-listed leaderboard context
(0.3195 and 0.4413 both appear in the prompt) is mutually inconsistent as "the" top value; both
figures are USER-REPORTED, unverified, and used as targets for nothing (irregularity flagged).

## 4. Lane paragraph (single method — stay inside it)

**H31-Z "regime-complementary max-union".** Basin-and-Range faults missing from the Quaternary
catalogue express in three different physiographic regimes with three different physical
signatures, and every prior lane in this repo combined such lines *multiplicatively*
(geometric-mean × second-line gate), which systematically dilutes the strongest line
(H31-X: J alone 0.166 vs J×gravity 0.122 vs J×radiometric 0.102, HOLDOUT-DTI same instrument).
H31-Z instead forms the candidate surface as the **element-wise maximum of footprint percentile
ranks** of regime-specific label-free lines — a union, not a conjunction — so each regime's best
locations survive into the shared 37,654-dot budget without needing corroboration from a line
that is physically silent in that regime: (i) **JUNC**, the H31-X directional concave-up
slope-break line at the bedrock–alluvium piedmont junction, reused *exactly* (same code, σ=1.5 px,
soft slope window 1°/3°–15°/25°, raw no-NMS form that won H31-X's ablation) as both component and
same-run incumbent comparator; (ii) **SCARPX**, a new LiDAR scarp-*coherence* line: 1 m-derived
scarp-step strength (`step_max`, `max(downface_max, upface_max)`) weighted by the 100 m-grid
structure-tensor linear coherence of the step field across cells (gradient σ=1.0 px, tensor
smoothing σ=2.5 px, weight 0.25+0.75·coherence), targeting sub-catalogue metre-scale scarps on
fans and range fronts that form *continuous lineaments* rather than isolated steps; (iii)
**GRAV**, `rank(|iso_grav_anom_hg|)`, the gravity basin-edge/step line that remains expressive on
flat piedmont/playa where both terrain lines are silent. Emission reuses the live-proven geometry
as geometry only: score-ordered Poisson thinning, min spacing 2.8 px, 37,654 dots, catalogue-flank
pruning d>2 px. **No prior dots, surfaces or peer rasters enter the candidate**; peers are used
only for uniqueness, the SGMC proxy and the projection (learning only). No catalogue-derived
feature is used anywhere (the catalogue enters only via per-fold visible-only B2 pruning and
pixel-exact visible masking inside the shared evaluator).

Named non-fault mimics: Lahontan paleoshoreline benches/terraces and fan-terrace risers (JUNC,
SCARPX — linear and coherent, the hardest mimic; no elevation veto is possible on the detrended
DEM), road/canal cuts and field boundaries (SCARPX linearity), lava-flow snouts and landslide
toes (JUNC), erosional pediment edges and inactive fronts (JUNC without GRAV step), lithologic
gravity contacts without fault offset and pluton margins (GRAV), airborne-survey seams (GRAV/CTRL).

## 5. Ranked hypotheses considered (3–5 required; all frozen before fitting)

| Rank | ID | Layers / physical signature | Why it should catch a catalogue-missing fault | Difference from everything implemented in this repo | Expected gain / cost |
|---|---|---|---|---|---|
| 1 | **Z-UNION (selected)** | `det_elev`/`det_elev_slope` (JUNC) + LiDAR `step_max`/`downface_max`/`upface_max`/`valid` (SCARPX coherence) + `iso_grav_anom_hg` (GRAV); max-of-ranks union | Experts/geologic maps carry range-front, fan-scarp and buried basin-edge faults that QFFD omits for lack of recognised Quaternary offset; each regime's signature is silent in the others, so a union covers all three populations at one budget | Every multi-line lane here (H31-U/X/Y, SCGP) used multiplicative gating; RBU31 was a *supervised* regime-weighted HGB; SCARPX's cross-cell structure-tensor coherence on the LiDAR step field is new (H31-U SCARP was an unweighted step/ex/cross geomean; H31-Y used gravity-polarity facing; H31-B a Hessian hand blend; `coh100` is within-cell 1 m coherence, not cross-cell line coherence) | Highest P(beat JUNC 0.166): directly attacks JUNC's measured piedmont starvation without diluting its tops; ~30 min |
| 2 | SUP-J | Per-fold HistGradientBoosting on raw 42-band stack **plus** JUNC/SCARPX/GRAV as spatial-context features; visible-only training | Learns regime-dependent line weighting (trust LiDAR on fans, JUNC at fronts, magnetics in volcanics) instead of a hand union rule | Prior HGB lanes never received directional/spatial-operator features (per-pixel trees cannot compute ∇s·û); RBU31/H31-E feature sets exclude junction/coherence lines | Possibly largest gain, but 2–3 h on 2 CPU cores, heaviest memory, highest duplicate risk vs the H19-5 supervised family; deferred to a future preregistration |
| 3 | TEX | `rtp`/`tmi`: structure-tensor orientation-discontinuity lines \|∇θ\| weighted by two-sided coherence (magnetic fabric truncation) | Buried bedrock faults in volcanics truncate/offset anomaly fabric without a gradient-magnitude edge or scarp | All magnetic lanes here are amplitude/phase based (HG, tilt, analytic signal, pseudogravity, MAGREST patch restoration); none uses orientation-field discontinuity. Costed in H31-X preregistration, never run | Low–moderate alone (magnetic-only lanes here ≤0.075 HOLDOUT-DTI); survey-seam mimic risk; ~45 min |
| 4 | LAHO-NULL | `det_elev` + `iso_grav_anom`: equipotential-contour shoreline null — veto junction segments that are contour-parallel over long strike with no cross-front gravity step | Removes the dominant piedmont false-positive process (Lahontan benches) from the junction line | No lane fits an explicit shoreline null model (H31-E had one soft mimic feature inside a supervised stack) | Precision gain uncertain; detrended DEM destroys absolute-elevation shoreline test; veto-of-J design has high duplicate risk vs H31-X dots; ~40 min |
| 5 | DRAIN | Paired-catchment channel-steepness (χ) difference-in-differences across candidate traces | Differential uplift across an unmapped splay leaves opposite-signed steepness residuals in matched basins even where scarps have diffused | No fitted matched-basin detector exists in this repo | **Not viable in this sandbox**: flow routing on detrended `det_elev` is invalid; the free official source (USGS 3DEP 10 m DEM, https://www.usgs.gov/3d-elevation-program) is outside this sandbox's host allowlist (github/PyPI only) — checked, not obtainable here. NASA OPERA DISP-S1 InSAR creep lines fail the same allowlist test (Earthdata). Named, checked, deferred |

No new external data is needed for the selected lane: every input is in the hash-pinned cached
stack restored this session (`evidence/data_restore_20261026_session15e685db.json`, all_verified).

## 6. Frozen implementation constants

- Grid: EPSG:32611, 3730×3292, transform (100, 0, 243350, 0, −100, 4508550), footprint 5,167,373 px.
  Inputs: `data/prepared/features.f32` (42-band stack from `scripts/prepare_data.py`).
- Lines stored as float32 memmap `data/h31z/lines.f32`, order
  `[JUNC, S0, SCARPX, GRAV, CTRL, SLOPE]`, each a footprint percentile rank in [0,1]
  (`run_h31u.rank01`, ties averaged; zeros outside support tie at the bottom).
  - `JUNC = rank01(run_h31x.junction_line(det_elev, det_elev_slope, foot, nms=False))` — exact reuse.
  - `S0`: `geomean_rank([rank01(where(lidar_ok, step_max, 0)), rank01(where(lidar_ok, max(downface,upface), 0))])`,
    zeroed where not `lidar_ok` (LiDAR `valid`>0, finite), then `rank01`. NaN inputs → 0 before ranks.
  - `SCARPX`: coherence of the pre-final-rank S0 field: gradients via Gaussian σ=1.0 derivatives,
    tensor `[[gx², gx·gy],[gx·gy, gy²]]` Gaussian-smoothed σ=2.5 px (mode nearest),
    `coh = (λmax−λmin)/(λmax+λmin+1e-12)` (closed-form 2×2 eigenvalues, clipped to [0,1]);
    raw `= S0_field × (0.25 + 0.75·coh)`, zeroed off-`lidar_ok`/off-footprint, then `rank01`.
    (0.25 floor frozen: coherence is a soft weight, never a veto, so short genuine scarps survive.)
  - `GRAV = rank01(|clean(iso_grav_anom_hg)|)`, `CTRL = rank01(clean(tmi_hg))`,
    `SLOPE = rank01(clean(det_elev_slope))` (`clean` = `run_h31u.clean` winsorise/median-fill).
- Arms (candidate surface = element-wise max of the named rank lines; single-line arms are the line):
  candidates `SCARPX`, `GRAV`, `Z2=max(JUNC,SCARPX)`, `Z3=max(JUNC,SCARPX,GRAV)`;
  comparators `JUNC` (same-run holdout-best rebuild), `CTRL`, `SLOPE`.
- Emission: `poisson_disk_emit(surf, allowed, 37654, min_dist_px=2.8, max_pool=400000)`;
  per fold `allowed = foot & (d_visible > 2 px) & (surf > 0)`; final `d_catalogue > 2 px`.
- Holdout: vendor `spatial.folds(catalogue, foot, buffer_px=213)` + unchanged
  `gems57-pooled-hide-v2` (`vendor/gems57/evaluate_holdout.py`, α=0.2, β=0.8, 300 m triangular
  kernel), pooled terms, paired 20 km-block bootstrap (2000 draws, seed 520810 via
  `run_h31u.pooled`). Whole-component hiding and pixel-exact visible masking are properties of
  the shared tools, reused unchanged.
- Confirmation: seeded random 50% split of whole 8-connected catalogue components, **seed 3105**
  (3103/3104 were consumed by H31-X/H31-Y), visible half used for B2 pruning only.
- SGMC proxy: off-catalogue USGS-SGMC faults (`d_catalogue > 3 px`, 61,664 px), same
  `sgmc_score`/regime code as H31-X/Y; piedmont = slope ≤6°, mountain >6° (single frozen regime
  definition for this lane; other sessions' `det_elev ≤50 m` split is *not* used or mixed).
- Projection: unchanged anchor-inversion code (`run_h31u.projection`, 11 USER-REPORTED anchors,
  LOO RMSE). Labelled PROJECTION, never a score; in-family calibration caveat carried verbatim.

## 7. Frozen experimental plan (≤3 experiments, ≤2 h compute; stop afterwards)

- **EXP-1 (canary + screen).** Leakage canary first: ROC-AUC of every line and candidate surface
  alone vs catalogue and vs off-SGMC (`run_h31u.auc_for`, 200k negatives); two-sided AUC >0.90 ⇒
  leakage STOP for that feature (lane stops if JUNC/SCARPX/GRAV/Z-surfaces are implicated).
  Screen: all 7 arms dotted per fold (visible-B2 only) on buffer-213 quadrant folds.
  Winner = highest pooled HOLDOUT-DTI among candidates {SCARPX, GRAV, Z2, Z3}.
  Reproducibility check R1 (not a gate): rebuilt JUNC pooled DTI should match H31-X's raw-final
  0.1661 within ±0.01; larger deviation is flagged as an irregularity before any interpretation.
- **EXP-2 (one ablation + uniqueness, pre-placement).** If winner uses SCARPX: ablated variant
  replaces SCARPX with S0 (coherence off) in the identical combination; both variants + JUNC +
  CTRL + SLOPE re-scored on the same folds; keep the higher pooled DTI (tie ⇒ keep coherence ON).
  If winner is GRAV alone: no ablation, final = GRAV. Final dots emitted on the full catalogue
  (B2). Uniqueness audit (surface top-K + final dots, Spearman full-footprint) vs every discrete
  peer (§2 scope) + literal lattice witness. Duplicate (>0.70 or |ρ|>0.90 vs any discrete peer,
  either stage) ⇒ STOP: log duplicate, no submittable package.
- **EXP-3 (confirmation + packaging, zero tuning).** Random-component confirmation (seed 3105)
  for {final variant, JUNC, CTRL}; SGMC full/quadrant/regime vs H33/H27 recomputed same day;
  anchor PROJECTION; package via vendor `submission_writer.write_submission` (all-finite zeros
  primary + NaN-outside twin + single-TIFF zips); validate both conventions
  (`gemsdoe31.submission.validate_submission`). Packaging a research TIFF after a failed
  *efficacy* gate is required by the owner's highest-priority instruction; packaging after a
  *duplicate/leakage* STOP is forbidden.

## 8. Frozen promotion gates (automated; no human inspector)

- **G1 format:** single-band float32, EPSG:32611, 3730×3292, exact transform, finite [0,1] inside
  footprint under its stated convention, values ⊆ {0,1}, 37,654 dots, 0 dots on/within 2 px of
  catalogue, ≥2.8 px spacing. The recommended upload file is the **all-finite** encoding (every
  cell finite in [0,1]), which cannot trigger the portal error "Predicted values must be in
  range [0, 1]"; the NaN twin is provided for the official null-outside wording.
- **G2 canary:** every used line/surface two-sided AUC ≤0.90 on both truths.
- **G3 efficacy (must beat the current holdout best):** final variant pooled HOLDOUT-DTI beats
  **JUNC, CTRL and SLOPE** with paired 95% CI excluding 0, ≥3/4 quadrants ≥ JUNC, and
  confirmation-split paired Δ vs JUNC also excludes 0. Beating CTRL but not JUNC ⇒ G3 FAIL.
- **G4 discovery proxy:** full-footprint off-catalogue SGMC DTI ≥ H33-2-B2 recomputed same day.
- **G5 uniqueness (§2 discrete scope):** final-dot and top-K 3-px overlap ≤0.70 and
  |Spearman| ≤0.90 (surface and dots) vs every discrete peer; lattice reading disclosed.
- **G6 projection:** anchor-inversion PROJECTION ≥0.2778 (never written as a score).
- Lane verdict `promote` only if G1–G6 all pass; otherwise `negative` (research download only,
  DO NOT SUBMIT). Negative results are deliverables. No fourth experiment, no post-hoc tuning.

## 9. Selector step (separate from this lane, per Protocol §6)

After the lane card, a separate selector decision re-judges the upload choice among
{H31-Z final (if packaged), H31-X, H31-T, H31-J, H31-M} under uniform gates using each lane's own
card plus fresh same-day re-reads (format, SGMC, pairwise overlap) for the top two. It names at
most one primary file (owner uploads manually; this repo never contacts DrivenData), records
alternates, and states that the live weekly cap shown on the submission page is **unverified**
from this sandbox. Lane verdicts are never rewritten by the selector; disagreements (e.g. H31-X's
lane-level top-K failure vs selector final-dot rule) are disclosed, not resolved silently.

## 10. Known limitations declared in advance

Label-free arms are buffer-invariant on quadrant evaluators (buffer changes only the unused train
mask) — the independent-truth checks are therefore the component-split confirmation and SGMC.
Fixed peer dot files are handicapped in hide-and-recover (pruned against the full catalogue) and
are never promotion comparators. SGMC is a geologic-map proxy, not hidden truth. The projection
is calibrated on one dot family (H19-5 descendants); cross-family transfer is unproven. All
0.24–0.28 anchors and the 0.3195/0.4413 leaderboard figures are USER-REPORTED with no receipt.
CANARY/HOLDOUT numbers from earlier lanes that used different instruments
(`gemsdoe31-holdout-v1`, seed-variant screens) are not pooled with `gems57-pooled-hide-v2`.
