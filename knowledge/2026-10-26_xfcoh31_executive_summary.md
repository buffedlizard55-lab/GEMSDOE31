# Historical executive summary — focus-site claim snapshot and XFCOH31 session (2026-10-26)

> **Archive/status correction:** XFCOH31 is not the current run. `registry/current_run.json` identifies MAGREST as active; its existing TIFF is downloadable for research only, not approved to submit, and its preregistered screen is negative. The literal shared-registry 3-pixel overlap STOP remains binding. This document preserves an earlier nine-site snapshot and must not be read as current upload guidance.

All leaderboard values below are **USER-REPORTED claims**, not organizer-confirmed scores; no exact-byte organizer receipt is linked here. HOLDOUT-DTI values are local evaluator outputs, never leaderboard scores.

## Archived snapshot: highest supplied score/file claim per focus site (not submission approval)

The table is a historical repository snapshot, not an exhaustive all-time ranking or organizer validation. “Best” means highest reported value among the files compared in that session only.

| Site | Highest supplied score/file claim in that snapshot (USER-REPORTED) | Claimed score | Dots |
|---|---|---:|---:|
| GEMSDOE24 | h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan | 0.2477 | 60,069 |
| GEMSDOE25 | dotted-h19-5-d2-8-20261002-e56ea318af89-nan | 0.2600 | 44,090 |
| GEMSDOE27 | topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan | 0.2449 | 61,328 |
| GEMSDOE28 | h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan | 0.2710 | 37,660 |
| GEMSDOE30 | d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca | 0.2600 | 44,090 |
| GEMSDOE31 | h27-4-solo-d28-20261004-8acb75e1-nan | 0.2708 | 40,199 |
| GEMSDOE32 | **h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros** | **0.2778** | 37,654 |
| GEMSDOE33 | h33d-analog-tip-stepover-r30-20261004-cb490425926e | 0.2632 | 41,865 |
| GEMSDOE36 | anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros | 0.2750 | 38,854 |

**Largest value in this historical nine-site table: GEMSDOE32 H33-2-B2 (0.2778, USER-REPORTED).** The local fetch receipt establishes byte identity for the compared rasters, not score authenticity, exhaustive global ranking, uniqueness, or approval to submit.

## H33 geometry and plausible metric mechanism (not causal proof)

Byte-level comparison shows H33-2-B2 has 37,654 dots and equals D2.8 support after removing 2,545 dots in the 100–200 m catalogue-distance band; no dots were added. This establishes raster lineage and geometry only. It cannot reveal the deleted dots' private-truth credit or prove why an unverified reported score changed. The file H36-1 is a separate candidate, so comparing its reported value is not a controlled intervention on H33.

For `DTI = T/(T + αF + βFN)` with `FN=N−T`, adding/removing a block is evaluated by comparing `ΔT/ΔF` to `αS/(1−αS)`. At `α=0.2`, `S=0.2778`, this ratio is about `0.05882`. In the simplified isolated-pixel case where `ΔT+ΔF=1`, the corresponding hit-credit threshold is `k>αS≈0.05556`. These are different ratios. The values of `ΔT` and `ΔF` for the 2,545 deletions are unknown without competition truth; the catalogue-pruning explanation is plausible, not established.

## Historical XFCOH31-session hypothesis queue (not the active backlog)

These were earlier desk ideas, not current authorization. The first was tested in the XFCOH31 session and produced a negative holdout result; the others were unrun. The active three-item desk backlog is summarized in the README, and no follow-up experiment is authorized here.

1. XFCOH31 cross-field edge-transfer coherence (RTP × gravity offset/orientation coherence + basement depth) — historical screen run; negative result below.
2. Radiometric channel-specific edge displacement (GeoDAWN K/Th/U offset edges) — not run.
3. Drainage-deflection asymmetry on piedmont (would require USGS 3DEP channel extraction; source lead: https://www.usgs.gov/3d-elevation-program).
4. Flight-line seam persistence null (would require GeoDAWN survey metadata; source lead: https://doi.org/10.5066/P93LGLVQ).
5. Seismicity alignments (source lead: https://earthquake.usgs.gov/fdsnws/event/1/; spatial uncertainty may be large relative to the kernel).

The links in this archived list are pointers, not sources re-verified during the current review.

## Historical XFCOH31 result (not the active run; not promoted)

- Leakage canary: max single-feature AUC **0.562** (< 0.90, PASS).
- HOLDOUT-DTI (evaluator `gemsdoe31-holdout-v1`, 58,625 withheld positives, pooled, 1000-draw paired
  block bootstrap): candidate **0.04588 [0.04118, 0.05112]** vs same-run base-19 control
  **0.04812 [0.04361, 0.05298]**; paired Δ **−0.00224 [−0.00483, +0.00012]**. **Gate FAIL.**
- Recorded pairwise focus-subset comparison: max surface Spearman **0.087**, max 3-px dot overlap **30.7%**. This subset statistic is not a broad-registry uniqueness pass; the registered spacing-5 witness triggers the literal STOP for any nonempty in-footprint candidate.
- The archived run record reports local format validation for both encodings (binary values, footprint, EPSG:32611, 3730×3292, exact transform). Local format validity is not organizer authentication, outside-mask convention approval, or permission to submit.

## Historical XFCOH31 artifact record (not current download guidance)

The archived XFCOH31 run card recorded its TIFF as research-download-only and **not approved to submit**, with SHA-256 `857dd662430c0130c46f920666d70dae5df6148951ad76d42d31a8d540c32972`. This file is not the active MAGREST artifact. The current site and current run card are authoritative for current download guidance; the shared-registry STOP blocks competition submission.

## Current experimental decision

No follow-up experiment is authorized. The assigned method paragraph is absent, the per-task experiment limit is exhausted, and the literal overlap STOP prevents a nonempty submission candidate. The three current desk-only hypotheses in the README are not authorization or score forecasts.

Source URLs preserved in the historical XFCOH31 record (not re-fetched during this current review): competition page, rules PDF, reference-solution repository, GeoDAWN, EPSG:32611, and the Tversky-index reference.
