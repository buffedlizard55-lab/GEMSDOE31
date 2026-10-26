# Executive summary — focus sites, best submissions, and the new XFCOH31 candidate (2026-10-26)

All leaderboard numbers below are **USER-REPORTED** (typed in owner prompts / sibling repos; no organizer
receipt exists in any repo). HOLDOUT-DTI numbers are computed here and are never leaderboard scores.

## Best submission per focus site (clear answer)

| Site | Best submission to submit (USER-REPORTED) | Score | Dots |
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

**Single best across all focus sites: GEMSDOE32 h33-2-b2 (0.2778).** Hash-verified this session:
fetched bytes match `evidence/nine_site_forensic_audit.json` for all 11 focus rasters
(`evidence/xfcoh31_focus_fetch.json`).

## Why h33-2-b2 scored 0.2778 (mechanism, COMPUTED + INFERENCE)

b2 = H27-4/D28 thinned ridge field (40,199 dots, catalogue distance >1 px) with the 2,545 dots in the
100–200 m catalogue halo deleted → 37,654 dots. The paired natural experiment vs GEMSDOE28 H36-1
(37,660 dots, 0.2710) isolates the effect at constant budget: deleting halo dots lost only ~10.3 live
TPw (0.0040/dot, far below the 0.0556 break-even at s=0.2778) because hidden truth is depleted near the
public catalogue (scored faults are *new* faults), while each deleted dot also removes its α=0.2 FP
charge. Keeping full 2.828 px far-field density preserved real off-catalogue coverage. Full algebra:
`evidence/nine_site_forensic_audit.json:live_anchor_inversion`.

## Ranked hypotheses not previously tried (this session)

1. **XFCOH31 cross-field edge-transfer coherence** (RTP×gravity offset/orientation coherence + basement
   depth) — buried basement-offset faults invisible at surface. Mimic: pluton/basin contacts. **RUN.**
2. Radiometric channel-specific edge displacement (GeoDAWN K/Th/U offset edges) — not run (budget).
3. Drainage-deflection asymmetry on piedmont (needs USGS 3DEP channel extraction; source:
   https://www.usgs.gov/3d-elevation-program — official, free, not fetched this session).
4. Flight-line seam persistence null (needs GeoDAWN survey metadata; https://doi.org/10.5066/P93LGLVQ).
5. Seismicity alignments (USGS ComCat FDSN https://earthquake.usgs.gov/fdsnws/event/1/ — km location
   error ≫ 300 m kernel; low expected gain).

## XFCOH31 result (EXP-1 canary, EXP-2 holdout, EXP-3 final fit)

- Leakage canary: max single-feature AUC **0.562** (< 0.90, PASS).
- HOLDOUT-DTI (evaluator `gemsdoe31-holdout-v1`, 58,625 withheld positives, pooled, 1000-draw paired
  block bootstrap): candidate **0.04588 [0.04118, 0.05112]** vs same-run base-19 control
  **0.04812 [0.04361, 0.05298]**; paired Δ **−0.00224 [−0.00483, +0.00012]**. **Gate FAIL.**
- Uniqueness vs genuine focus submissions: max surface Spearman **0.087**, max 3-px dot overlap
  **30.7%** (PASS; calibration-lattice degeneracy disclosed in the run card).
- Validator: both encodings pass all hard checks; values exactly {0,1} ⊂ [0,1], no NaN inside footprint,
  EPSG:32611 / 3730×3292 / exact transform. This fixes the "Predicted values must be in range [0, 1]"
  class (sentinel/NaN leakage); the zeros file has no NaN anywhere.

## Download / submit decision (obvious, automated — no human inspection)

- **OK TO DOWNLOAD (research): YES** —
  `docs/downloads/gems31-xfcoh31-xfield-coherence-37654-20261026-zeros.tif`
  SHA-256 `857dd662430c0130c46f920666d70dae5df6148951ad76d42d31a8d540c32972`
- **OK TO SUBMIT: NO — DO NOT SUBMIT.** It did not beat its same-run control on holdout; spending a
  weekly slot would violate the preregistered gate. Verdict: **negative** (a deliverable per protocol).
- If a future candidate passes: upload the **-zeros.tif** (or its .zip) at
  https://www.drivendata.org/competitions/306/competition-doe-gems/ with name
  `gems31-xfcoh31-xfield-coherence-37654-20261026` and the ≤140-char note in the run card; disclose AI
  use per competition rules.

## Can we beat 0.2778?

Not demonstrated. No candidate in this repo has beaten a same-run control *and* the D28-family live
evidence simultaneously; local proxies are known to invert across families (instrument calibration,
Spearman ≈ +0.32 SGMC / +0.11 catalogue-gap vs live). The only live-measured positive lever remains
catalogue-halo pruning of a strong ridge field — which is not unique. Honest next step: a fresh lane
combining a *new* surface that first beats base-19 on holdout, then applies halo pruning, with fresh
confirmation draws. XFCOH31's features do not provide that surface.

Sources for manual review: competition https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/ ·
rules PDF https://docs.nlr.gov/docs/fy26osti/96647.pdf · reference solution
https://github.com/drivendataorg/gems-prize-reference-solution · GeoDAWN https://doi.org/10.5066/P93LGLVQ ·
grid https://epsg.io/32611 · Tversky https://en.wikipedia.org/wiki/Tversky_index
