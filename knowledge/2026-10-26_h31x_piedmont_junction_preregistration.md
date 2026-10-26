# H31-X preregistration — frozen BEFORE any fitting (2026-10-26, branch `arena/3ce68fc7-gemsdoe31`)

Labels used everywhere: **HOLDOUT-DTI** (evaluator, withheld positives, 95% CI) · **COMPUTED** (raster
measurement) · **USER-REPORTED** (owner-typed, no organizer receipt) · **PROJECTION** (estimate, never a score).
No ORGANIZER-CONFIRMED score exists in this repository. This repository never contacts DrivenData.

## Lane assignment disclosure (IR-U-01 again)

The prompt's Parallel-Run Protocol §1 says "Your lane is the single method paragraph below", but **no method
paragraph was supplied** (the full prompt was read twice; every earlier session recorded the same omission).
Per the owner's overriding instruction to generate and validate a unique submission autonomously, this session
self-assigns and freezes the lane paragraph below before touching data. The previous session's declared next
step ("paired hide-and-recover test of H31-B-standalone vs H31-T on the shared evaluator") is executed inside
EXP-1/EXP-3 as fixed-dot reference arms, with its handicap stated (see below).

## Lane paragraph (single method — stay inside it)

**H31-X "piedmont-junction range-front contact line".** In the Basin and Range, the master range-bounding
normal fault sits at or just basinward of the bedrock–alluvium contact, which in the terrain is the
*piedmont junction*: the sharp, concave-up slope break where steep bedrock slopes (≳10°) give way to the
gently sloping piedmont (≲5°). The candidate surface is therefore the **directional slope-break line**:
`J = max(0, −∇s·û)` where `s` is the detrended-elevation slope (`det_elev_slope`, degrees), `û` is the
local downslope unit vector of smoothed `det_elev`, computed label-free from the cached 42-band stack at
σ = 1.5 px, restricted to the transition regime by a soft slope window (full weight 3°–15°, tapering to zero
at 1° and 25°), and thinned to a one-pixel crest by non-maximum suppression along `û`. Corroboration gates
(tested as arms, not tuned): the radiometric lithologic-contrast edge (|∇| of smoothed GeoDAWN `TC` and
`ThK`), and the gravity basin-edge (`iso_grav_anom_hg` rank) that distinguishes a fault-bounded front from an
erosional pediment edge. Emission reuses the live-proven D2.8→H33 geometry *as geometry only* (score-ordered
Poisson thinning, min spacing 2.8 px, 37,654 dots, catalogue-flank pruning d > 2 px); **no prior dots,
surfaces or peer rasters enter the candidate**. Peer rasters are used only for the uniqueness audit and the
SGMC proxy / projection (learning only).

## Why H33-2-B2 (0.2778 USER-REPORTED) leads and what can beat it (pre-analysis, COMPUTED facts only)

From `evidence/h33_forensics_20261025.json` / `evidence/nine_site_forensic_audit.json`: H33 = H19-5
surface → D2.8 Poisson dots (44,090; 0.2600) → delete dots ≤1 px from the catalogue (H27-4; 40,199;
0.2708) → delete dots ≤2 px (H33-2-B2; 37,654; 0.2778). With `DTI = T/(0.2T + 0.2F + 0.8K)` a
non-redundant dot helps iff its kernel credit `k > 0.2·S` (0.0556 at S = 0.2778, i.e. within ≈283 m of
uncovered truth). Anchor inversion over the eleven in-family rasters implies ≈13.4k hidden-truth pixels and
≈0.004 TPw per catalogue-flank dot: hidden expert truth is depleted beside already-mapped faults, so flank
pruning is pure FP-budget economics. For a fixed 37,654-dot binary field the score is ≈ `T/(0.2n + 0.8K)`;
0.2778 ⇒ T ≈ 5.1k (≈38 % recall), 0.44 (USER-REPORTED leaderboard top) ⇒ T ≈ 8.0k (≈60 % recall).
**The only lever is a surface whose top 37,654 far-field locations carry more hidden truth.** Proxy facts
(COMPUTED this session): off-catalogue USGS-SGMC faults have median slope 13.5° (bedrock ranges) while the
QFFD catalogue has median slope 5.6° (piedmont/range front); the two truth proxies therefore sample different
regimes and a robust candidate must not regress on either.

## Ranked hypotheses not yet tried in this repository (all label-free, all runnable from the local cache)

| Rank | ID | Layers / physical signature | Why it should catch a catalogue-missing fault | Difference from everything implemented here | Expected gain / cost |
|---|---|---|---|---|---|
| 1 | **X1 (selected core)** | `det_elev`, `det_elev_slope`: directional concave-up slope-break line (`−∇s·û` in the 3°–15° regime, NMS-thinned) | QFFD only lists faults with recognised Quaternary displacement; range-bounding faults on eroded or fan-buried fronts are still drawn on geologic maps and added by experts as range-front structures (the classic Great Basin geothermal setting) | H31-B ranked slope *magnitude* (steepness ⇒ bedrock interiors); H31-E/SCGP used top-hat/Laplacian flexure of `det_elev` with no downslope directionality or slope-regime window; H31-T restored basement offsets up-dip; no lane here places dots on the junction *line* | highest on both proxies; ~10 min |
| 2 | X3 | X1 × gravity basin-edge (`iso_grav_anom_hg` rank, geometric mean, second-line gate) | A gravity step across the junction separates a fault-bounded front from an erosional pediment edge | gravity HG used before only symmetrically (rings both basin flanks); here it gates a terrain-defined line | + precision, same cost |
| 3 | X2 | X1 × radiometric lithologic-contrast edge (|∇| smoothed `TC`, `ThK` ranks) | Bedrock/alluvium juxtaposition across a contact fault shows as a K/Th/TC step | ratio-gradient ridges were used alone (ALT line, H31-U) never as a contact gate on a junction line | + precision in bare terrain |
| 4 | X4 | X1 × X2 × X3 (three-line geometric mean, second-line gate) | maximum corroboration | tests dilution by the weakest line | unknown |
| 5 | KIN (not run; costed) | LiDAR `downface_max`/`upface_max` facing agreement with the gravity-defined basinward vector (synthetic vs antithetic scarps) | small LiDAR-visible scarps below QFFD compilers' threshold | vector (direction) agreement rather than scalar co-location | LiDAR covers 75 % of footprint; ~30 min; deferred (budget) |
| 6 | TEX (not run; costed) | RTP structure-tensor orientation/coherence discontinuity lines (magnetic fabric truncation) | bedrock faults in volcanics truncate anomaly fabric without a gradient edge | all magnetic lanes here are gradient/phase based | survey-seam mimic risk; ~45 min; deferred |

Named non-fault mimics for the selected lane: erosional pediment edges and inactive range fronts (no gravity
step ⇒ suppressed by X3), Lahontan highstand shorelines and wave-cut benches, alluvial-fan terrace risers,
lava-flow snouts (steep front, concave base; no gravity step), landslide toes, road/canal cuts. The slope
window removes canyon walls (>25°) and flat playas (<1°).

## Frozen experimental plan (≤3 experiments; stop afterwards)

- **EXP-1 (canary + screen).** Leakage canary: ROC-AUC of every line and surface alone vs the catalogue and vs
  off-catalogue SGMC (200k negative sample); any value >0.90 (two-sided) = leakage STOP for that feature.
  Screen: arms {X1, X2, X3, X4, CTRL = rank(`tmi_hg`) (same control as H31-U), SLOPE = rank(`det_elev_slope`)
  (steepness baseline = H31-B's dominant B1 term)} dotted per fold with visible-catalogue B2 pruning only,
  vendor `spatial.folds(buffer_px=213)` + unchanged `gems57-pooled-hide-v2` evaluator, pooled paired CIs.
  Fixed-dot reference arms H33-2-B2, H31-T, H31-J, H31-B-standalone are scored in the same folds as the
  previous session's requested comparison — **handicapped references only** (their B2 prune used the FULL
  catalogue, so dots within 2 px of withheld segments were deleted before scoring); never a promotion
  comparator. Winner = highest pooled HOLDOUT-DTI among X-arms.
- **EXP-2 (one ablation + uniqueness).** Winner with NMS thinning OFF vs ON; keep the better on pooled
  holdout. Final emission on the full visible catalogue (B2). Surface Spearman and top-K / final-dot 3-px
  overlap against every discrete peer dot field (nine focus-site rasters fetched hash-verified + all local
  GEMSDOE31 downloads); |ρ| > 0.90 or overlap > 0.70 vs any discrete peer = duplicate STOP. The literal
  695-raster reading (spacing-5 lattice) is recomputed and disclosed (IR-U-02), not exempted.
- **EXP-3 (independent confirmation + packaging, zero tuning).** Because label-free arms are
  buffer-invariant on quadrant evaluators (disclosed by H31-U), the untouched confirmation is a *different
  partition of truth*: a seeded random 50 % split of whole catalogue components (seed 3103, components, not
  pixels), visible half masked pixel-exactly and used for B2 pruning, hidden half scored with the same
  evaluator terms (20 km block paired bootstrap). Then full-footprint, per-quadrant and slope-regime
  (piedmont ≤6° / mountain >6°) off-catalogue SGMC DTI vs H33/H27 recomputed same code same day, anchor-inversion
  PROJECTION (eleven focus anchors, LOO RMSE), vendor `submission_writer.write_submission`, both validators.

## Frozen promotion gates (automated; no human inspector)

- **G1 format:** single-band float32, EPSG:32611, 3730×3292, exact transform, finite [0,1] inside the
  footprint, correct outside convention per file, {0,1} values, 0 dots on the catalogue, ≥2.8 px spacing.
- **G2 canary:** every used line/surface two-sided AUC ≤ 0.90 on both truths.
- **G3 efficacy:** pooled HOLDOUT-DTI beats CTRL **and** SLOPE with paired 95 % CI excluding 0, ≥3/4 quadrants
  ≥ CTRL, and the random-split confirmation paired delta vs CTRL also excludes 0.
- **G4 discovery proxy:** full-footprint off-catalogue SGMC DTI ≥ H33-2-B2's value recomputed the same day.
- **G5 uniqueness (discrete-peer scope, IR-U-02):** final-dot and top-K 3-px overlap ≤ 0.70 and |Spearman| ≤ 0.90
  vs every discrete peer; literal lattice reading disclosed.
- **G6 projection:** anchor-inversion PROJECTION ≥ 0.2778 (never written as a score).
- Verdict `promote` only if G1–G6 all pass; otherwise `negative` (research download only, DO NOT SUBMIT).
  A negative result is a deliverable. No fourth experiment, no tuning after EXP-3.

## Data

Inputs restored hash-verified from owner mirrors this session (`evidence/data_restore_20261026_session3ce68fc7.json`,
`all_verified = true`); 42-band cache built by `scripts/prepare_data.py` (`evidence/data_preparation.json`
byte-identical to the committed receipt). No new external data is needed for X1–X4. KIN/TEX also need no new
data; InSAR (H31-V) remains blocked (ASF/NASA Earthdata outside the sandbox allowlist).
