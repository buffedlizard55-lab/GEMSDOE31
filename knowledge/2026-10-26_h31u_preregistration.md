# H31-U preregistration — frozen BEFORE any fitting (2026-10-26, branch arena/5b378be2-gemsdoe31)

## Lane assignment disclosure (Irregularity IR-U-01)

The session prompt's Parallel-Run Protocol §1 says "Your lane is the single method paragraph below",
but **no method paragraph was supplied** in the prompt (verified by reading the full prompt; earlier
sessions recorded the same omission). Per the owner's overriding instruction to generate and validate a
unique submission autonomously, this session **self-assigns and freezes** the lane paragraph below
before touching data. This is disclosed here, not hidden.

## Lane paragraph (single method — stay inside it)

**H31-U "strain–seismic corroborated potential-field ridges".** Buried, catalogue-missing
Basin-and-Range faults that are still tectonically/hydrothermally active should simultaneously
(a) localize present-day geodetic strain (gradient ridges of dilatation/shear strain-rate),
(b) align microseismicity-density fronts, (c) offset magnetic/gravity basement (tilt-derivative /
horizontal-gradient ridges of RTP magnetics and isostatic gravity), and (d) where cover is thin,
express a LiDAR/DEM scarp step. No single line is trusted: the candidate surface is the
geometric mean of per-line footprint percentile ranks multiplied by the second-highest line rank
(a ≥2-line corroboration gate), computed **label-free** from the cached 42-band stack only.
Emission reuses the live-proven geometry of the D2.8→H33 family *as geometry only* (score-ordered
Poisson thinning, min spacing 2.8 px, 37,654-dot budget, catalogue-flank pruning d>2 px) — **no
prior dots, surfaces, or peer rasters enter the candidate**. Peer rasters are used only for the
uniqueness audit and proxy scoring (learning only).

## Why H33-2-B2 (0.2778 USER-REPORTED) leads, and what could beat it (pre-analysis)

COMPUTED forensics already in repo (`evidence/h33_forensics_20261025.json`,
`evidence/nine_site_forensic_audit.json`): H33 = H19-5 surface → D2.8 dotted (44,090) → delete
d≤1 px catalogue flank (H27-4, 40,199, 0.2708) → delete d≤2 px flank (37,654, 0.2778). At
DTI S, an added dot helps iff marginal truth credit/FP weight > 0.2·S/(1−0.2·S) (=0.0588 at
S=0.2778; isolated-dot break-even kernel credit k>0.0556 ≈ within ~283 m of uncovered truth).
Catalogue-flank dots earn ~0.004 TPw/dot (anchor inversion) because hidden expert-mapped truth is
depleted next to already-mapped faults, so deleting 2,545 of them raised DTI. Sparse 2.8 px
spacing avoids 300 m-kernel redundancy. **Therefore the only remaining lever is a better
far-field surface ranking (higher TPw/dot >200 m from catalogue) at the same budget/geometry.**
Supervised catalogue-trained models have repeatedly collapsed live (USER-REPORTED 0.019–0.042)
because hidden truth ≠ catalogue distribution; hence this lane is unsupervised and label-free.

## Ranked hypotheses (all use only the restored local cache; no new external data)

| Rank | ID | Layers / transform | Why catalogue-missing | Novelty vs this repo | Cost |
|---|---|---|---|---|---|
| 1 | **U1** | 4-line corroboration: STRAIN (|∇| dilat/shear/2nd-inv), SEIS (|∇| log seismicity density), TILT (RTP tilt + mag/grav HG), SCARP (LiDAR step/ex/cross) | Active buried faults strain + seismogenic + basement-offsetting even with no mappable trace | Strain & seismicity bands never used as primary unsupervised ridge lines here (only as HGB inputs); H19-5 used neither | Low |
| 2 | U4 | 3-line corroboration: TILT × SCARP × ALT (radiometric ThK/UK edges) | Classic buried-fault triad without strain/seismic | Ablation isolating whether novel lines help | Low |
| 3 | U2 | TILT alone (multi-field potential-field ridge) | Basement offsets under cover | cf. sibling tiltworm 0.2343 USER-REPORTED; never run pure here | Low |
| 4 | U5 | 6-line corroboration (U1 + BASE + ALT) | Maximum corroboration | Tests dilution by weak lines | Low |
| 5 | U3 | BASE alone (|∇| depth-to-basement × |∇| conductance × grav slope) | Range-front basement steps | Sibling basement-step failed live (0.0009); low prior, cheap falsification | Low |

Non-fault mimics (named per protocol): STRAIN—GPS interpolation/block-model artifacts;
SEIS—quarry blasts & aftershock clusters; TILT—volcanic flow margins & survey-line seams;
SCARP—Lahontan shorelines, roads, terrace risers; BASE—basin-margin depositional pinch-outs;
ALT—playa evaporite crusts. The ≥2-line gate is the mimic defence.

## Frozen experimental plan (≤3 experiments)

- **EXP-1 (canary + screen).** Leakage canary: AUC of every line and surface alone vs catalogue
  and vs off-catalogue SGMC on holdout regions; AUC>0.90 = leakage STOP for that feature.
  Screen: arms {U1,U2,U3,U4,U5, CTRL=rank(tmi_hg)} dotted per fold (visible-catalogue B2 only),
  vendor `spatial.folds(buffer_px=213)` + `evaluate_holdout` pooled DTI. Winner = highest pooled
  HOLDOUT-DTI among U-arms (tie-break: off-SGMC DTI). H27-4 incumbent dots scored as handicapped
  reference only (their B1 prune used the full catalogue; caveat stated wherever quoted).
- **EXP-2 (one ablation + uniqueness pre-check).** Winner with gate OFF (plain geometric mean)
  vs gate ON; keep better on pooled holdout. Surface Spearman + top-K/final-dot 3-px overlap vs
  all discrete peer dot-fields (9 focus sites fetched hash-verified + all local GEMSDOE31
  downloads). |ρ|>0.90 or overlap>0.70 vs any discrete peer = duplicate STOP.
- **EXP-3 (confirmation + packaging, zero tuning).** Re-score frozen winner with
  `buffer_px=80` folds (sensitivity), full-footprint + per-quadrant off-SGMC DTI, anchor-inversion
  PROJECTION (refit on 11 focus anchors, LOO error reported). Package with vendor
  `submission_writer.write_submission`; validate with both validators/conventions. Run card JSON.

## Frozen promotion gates (automated; no human inspector)

- G1 format: single-band float32, EPSG:32611, 3730×3292, exact transform, finite [0,1] in
  footprint, correct outside convention, {0,1} values, 0 dots on catalogue, min spacing ≥2.8 px.
- G2 canary: every used line/surface AUC ≤0.90 on both truths.
- G3 efficacy: pooled HOLDOUT-DTI (gems57-pooled-hide-v2) beats CTRL **and** best single-line
  arm with paired 95% CI excluding 0, and ≥3/4 quadrants ≥ CTRL. Confirmation (buffer 80) must
  not reverse the sign vs CTRL.
- G4 discovery proxy: full-footprint off-SGMC DTI ≥ H33's recomputed value (same code, same day).
- G5 uniqueness (discrete peers): max 3-px overlap ≤0.70 and max |Spearman| ≤0.90 on surface
  AND final dots vs every discrete dot-field peer in scope.
- G6 projection: anchor-inversion point PROJECTION ≥0.2778 (USER-REPORTED anchor; projection is
  never called a score). All of G1–G6 pass ⇒ verdict `promote` ("OK to download and submit";
  owner uploads manually — this repo never contacts DrivenData). Any failure ⇒ `negative`,
  DO NOT SUBMIT, research download only.

### Literal 695-raster reading (Irregularity IR-U-02, disclosed decision)

The inherited literal registry rule compares against *every* registered raster including a
spacing-5 calibration lattice and dense continuous surfaces whose "dots" cover ~100% of the
footprint; any nonempty candidate then has ~100% 3-px overlap (measured 99.93–100% for every
prior candidate), making the literal gate unsatisfiable by construction. This session reports
the literal reading as a disclosed diagnostic (with the lattice witness recomputed) and judges
uniqueness on **discrete peer submissions** — the population the duplicate rule exists for —
using the shared template's own two-phase distinction (`vendor/gems57/uniqueness.py`). Nothing
is silently exempted: both readings appear in the run card and executive summary, and the
protocol owner may overrule this rescope, in which case the verdict reverts to STOP.

## Score labels

Every number is HOLDOUT-DTI (evaluator gems57-pooled-hide-v2, withheld positives, 95% CI),
USER-REPORTED (owner-typed, no organizer receipt — includes 0.2778/0.3195/0.4413), COMPUTED
(raster measurement), or PROJECTION (anchor inversion; never a score). No ORGANIZER-CONFIRMED
score exists in this repository.
