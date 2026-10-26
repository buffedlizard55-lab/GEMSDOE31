# H31-Y preregistration — frozen BEFORE any fitting (2026-10-26, branch `arena/a111fe50-gemsdoe31`)

Labels everywhere: **HOLDOUT-DTI** (evaluator, withheld positives, 95% CI) · **COMPUTED** ·
**USER-REPORTED** (owner-typed, no organizer receipt) · **PROJECTION** (estimate, never a score).
No ORGANIZER-CONFIRMED score exists in this repository. This repository never contacts DrivenData.

## Lane assignment disclosure (IR-U-01, repeated)

The prompt's Parallel-Run Protocol §1 says "Your lane is the single method paragraph below", but
**no distinct method paragraph was supplied** in this session's prompt either (same omission every
earlier session recorded). This session self-assigns and freezes the lane paragraph below before
touching candidate data. Data actually inspected before freezing: band inventory, band percentiles,
footprint/catalogue slope-regime fractions, and all previously committed evidence. No candidate
surface, dot set, holdout score, or proxy score for H31-Y existed before this file.

## Lane paragraph (single method — stay inside it)

**H31-Y "regime-mosaic dual-specialist emission".** Basin-and-Range normal faults occupy two
geomorphic regimes that require different detectors: (i) range-front / mountain regime
(smoothed `det_elev_slope` > 6°), where the master fault sits at the concave-up piedmont-junction
slope break (H31-X's label-free junction line, re-derived here from `det_elev`/`det_elev_slope`
at σ = 1.5 px — method reused for learning, **no H31-X dots or surface files enter**); and
(ii) piedmont / alluvial-fan regime (slope ≤ 6°), where a Quaternary fault crossing a smooth fan
appears in 1 m LiDAR derivatives as a one-sided, strike-coherent step on otherwise low-relief
ground: `FAN = geomean_rank(step_max, |upface_max − downface_max|, coh100, relief-inverse)`,
computed label-free from the cached 42-band stack, soft-restricted to the piedmont slope window
(full weight 0.5–6°, tapering to zero at 0.1° and 10°); where LiDAR is invalid the junction rank
is the frozen fallback so the piedmont budget can still be spent. Emission reuses only the
live-proven *geometry* (score-ordered Poisson thinning, min spacing 2.8 px, 37,654 dots,
catalogue-flank pruning d > 2 px from the *visible* catalogue per fold). The candidate arm
**Y3** spends the budget as a regime mosaic: 50% of dots emitted from the junction ranking inside
the mountain regime, 50% from the FAN ranking inside the piedmont regime (mountain emitted first;
piedmont emission excludes the 2.8 px neighbourhoods of mountain dots, so global spacing holds).
Peer rasters are used only for uniqueness/proxy audits (learning only), never as candidate inputs.

Named non-fault mimics: fluvial terrace risers and fan-lobe boundaries (one-sided LiDAR steps on
fans), Lahontan shoreline benches, canal/road cuts, and erosional pediment edges (junction line
without a fault). The relief-inverse term suppresses rugged bedrock texture; coherence suppresses
unorganised roughness. Neither removes terrace risers — that residual mimic risk is inherent and
is why the piedmont-truth subgroup holdout (below) is a gate, not a diagnostic.

## Why this lane, ranked hypotheses (frozen)

| Rank | ID | Layers / signature | Why it may catch catalogue-missing faults | Novelty vs this repo | Cost |
|---|---|---|---|---|---|
| 1 | **Y3 mosaic (selected)** | junction line (mountain) + FAN LiDAR dipole/coherence/step (piedmont), 50/50 budget | Experts' new faults are Quaternary structures; QFFD is most incomplete on fans where scarps are subtle in 100 m data but visible in 1 m LiDAR derivatives; H31-X spends 82% of dots at slope > 6° and is weakest exactly there (selector audit regime slices) | No lane here ever allocated the dot budget **by geomorphic regime with regime-specific rankings**; LiDAR channels were HGB scalars (H31-E/B) or a global antislope surface (AS-1/H1), never a piedmont-restricted specialist in a mosaic | ~30 min |
| 2 | Y4 blend | single geomean surface `sqrt(JUNC_rank · FAN_rank_global)` | same physics, tests whether mosaic allocation beats pixel blending | — | same |
| 3 | Y1 FAN-only | FAN surface, global emission | upper bound on piedmont-specialist value; expected to fail overall holdout | — | same |
| 4 | KIN facing-agreement | LiDAR facing vs gravity basinward vector | costed in H31-X prereg, never run; facing-band semantics (`upface/downface` azimuth reference) are **not documented in this repo**, so it cannot be implemented without guessing → deferred, recorded as blocked-by-documentation, not silently approximated | — | blocked |
| 5 | TEX fabric truncation | RTP structure-tensor orientation discontinuities | costed in H31-X prereg, never run; survey-seam mimic risk; deferred under the 3-experiment budget | — | deferred |

External-data candidates (InSAR, 1 m DEM erf-bank, drainage networks) remain blocked in this
sandbox (non-GitHub egress); official free sources already named in earlier preregistrations
(USGS 3DEP https://www.usgs.gov/3d-elevation-program; ASF DAAC) — not re-proposed as viable here.

## Frozen experimental plan (≤3 experiments; stop afterwards)

- **EXP-1 (lines + canary + screen).** Build lines {JUNC, FAN, CTRL=rank(`tmi_hg`), SLOPE=rank(`det_elev_slope`)}.
  Leakage canary: ROC-AUC of every line/surface alone vs catalogue and vs off-catalogue SGMC,
  overall and inside the piedmont regime; any two-sided AUC > 0.90 = leakage STOP for that feature.
  Screen arms {Y1, Y2=JUNC-only (method comparator), Y3, Y4, CTRL, SLOPE} with vendor
  `spatial.folds(buffer_px=213)` + unchanged `gems57-pooled-hide-v2`, per-fold visible-B2 emission,
  pooled paired CIs. Report overall pooled DTI **and** truth-regime subgroups (withheld positives
  split by smoothed slope at the truth pixel ≤ 6° / > 6°) for Y2 vs Y3.
- **EXP-2 (uniqueness + final emission of the frozen candidate Y3).** Regardless of screen ranking,
  the packaged candidate is Y3 if and only if it passes the gates below; no post-screen arm
  substitution (that would be tuning). Surface Spearman (mosaic ranking field) and final-dot 3-px
  overlap vs every discrete peer (nine focus rasters hash-verified this session + all local
  downloads incl. H31-X); |ρ| > 0.90 or overlap > 0.70 = duplicate STOP. Literal 695-raster
  lattice reading recomputed and disclosed (IR-U-02), not exempted.
- **EXP-3 (confirmation + proxies + packaging, zero tuning).** Untouched seeded random 50%
  whole-component split (seed 3104, never used before), visible half for B2 pruning only, same
  evaluator terms. Off-catalogue SGMC DTI full + slope-regime slices vs H33/H31-X recomputed same
  code same day. Score estimation uses the **corrected cross-family calibration** in
  `knowledge/2026-10-26_h31y_projection_audit.md` (in-family anchor projection reported only as an
  upper-bound diagnostic). Package both encodings via vendor `submission_writer`; validate with
  both validators.

## Frozen promotion gates (automated; no human inspector)

- **G1 format:** single-band float32, EPSG:32611, 3730×3292, exact transform, finite [0,1] inside
  footprint, {0,1} values, 0 dots on catalogue, ≥2.8 px global spacing, both encodings valid.
- **G2 canary:** every used line/surface two-sided AUC ≤ 0.90 on both truths (overall + piedmont).
- **G3 efficacy:** Y3 pooled HOLDOUT-DTI paired 95% CI vs CTRL excludes 0 **and** Y3 does not lose
  to Y2 (junction comparator) overall (paired CI lower bound > −0.005) **and** Y3 beats Y2 on the
  piedmont-truth subgroup (point estimate > Y2) **and** confirmation-split paired Δ vs CTRL CI
  excludes 0.
- **G4 discovery proxy:** full-footprint off-catalogue SGMC DTI ≥ H33-2-B2 same-day value.
  (Reported as a proxy gate only; the projection audit shows SGMC must never be converted to a
  live score by the in-family scale.)
- **G5 uniqueness (discrete-peer scope, IR-U-02):** final-dot 3-px overlap ≤ 0.70 and
  |Spearman| ≤ 0.90 vs every discrete peer; literal lattice reading disclosed.
- **G6 honest estimate (amended pre-fit, same day, after the calibration audit completed and
  before EXP-1 ran):** the audit (`knowledge/2026-10-26_h31y_projection_audit.md`) shows the best
  cross-family calibration has LOO RMSE 0.0897 — barely better than the mean — so *no* central
  live estimate ≥ 0.26 is attainable for any new family and such a threshold would be theatre.
  G6 therefore requires only that all three labelled estimates be reported (M1 in-family
  upper-bound diagnostic; M3 cross-family central ± 2·LOO-RMSE; catalogue HOLDOUT-DTI + CI) and
  that the M3 interval's upper end exceed 0.2778 (candidate not ruled out as competitive).
  Promotion rests on G1–G5; the old in-family point-projection gate is **retired as invalid**.
- Verdict `promote` only if G1–G6 pass; otherwise `negative` (research download only, DO NOT
  SUBMIT). A negative result is a deliverable. No fourth experiment, no tuning after EXP-3.

## Data

Inputs restored hash-verified this session (`evidence/data_restore_20261026_session_a111fe50.json`,
all_verified=true); 42-band cache rebuilt (`scripts/prepare_data.py`); nine focus peer rasters
fetched hash-verified (`evidence/regime31/peer_fetch.json`, learning only). No new external data.
