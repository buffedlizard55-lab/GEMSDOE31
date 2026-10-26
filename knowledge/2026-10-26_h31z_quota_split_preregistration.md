# H31-Z preregistration — hard quota split only (successor lane to H31-Y)

Frozen **before any H31-Z fitting** in session `arena/579233d5-gemsdoe31` (2026-10-26), after H31-Y EXP-1/EXP-2
were measured and before H31-Y EXP-3/packaging completed. No DrivenData contact; no leaderboard access; no
automatic submission. Claim classes as in the H31-Y preregistration. No ORGANIZER-CONFIRMED score exists.

## Why this is a new lane, and what is already known (full disclosure)

H31-Y (`knowledge/2026-10-26_h31y_regime_split_preregistration.md`) froze three candidate geometries
{SPLIT50, SPLIT35, ROUTE} with winner = highest pooled HOLDOUT-DTI. Measured EXP-1 (COMPUTED,
`evidence/h31y/exp1_screen.json`, `gems57-pooled-hide-v2`, 60,988 withheld): ROUTE 0.1626 won —
but EXP-2's uniqueness audit measured **92.4% of ROUTE's final dots within 3 px of the H31-X dot field**,
a duplicate-lane STOP under the owner's rule (Parallel-Run Protocol §1: >70% ⇒ drifted lane, log as
duplicate and stop). Mechanism of the failure (INFERENCE from the measured ranks): in the slope-routed
log-blend, top JUNC values in the mountains still outrank top PIED values in the piedmont across most of
the footprint, so the score-ordered emission reproduces the JUNC dot set. A blended surface therefore
cannot be both JUNC-competitive and unique in this repository. H31-Y is being completed exactly as
preregistered and will carry verdict `negative` on G5; its TIFF is research-only.

H31-Z is the successor lane that this measured failure points to: **hard quota allocation is the only
geometry in the Y screen whose dot set is structurally forced away from the JUNC dot set** (a JUNC quota
of q·37,654 bounds the guaranteed-identical share at q). What is already known and **not** re-discovered
here: the Y EXP-1 screen numbers for the shared arms (SPLIT50 0.1473, SPLIT35 0.1349, JUNC 0.1661,
PIED 0.0705, CTRL 0.0671, SLOPE 0.0488; JUNC reproduced H31-X's 0.166133 exactly). H31-Z EXP-1 re-runs the
identical deterministic screen for its own arms as a replication receipt; it is disclosed in advance that
the SPLIT50/SPLIT35 ranking is expected to replicate. The evidence that can still kill this lane — and has
**not** been measured for any split arm — is: (a) final-dot uniqueness of the split emission (the PIED
half may still land within 3 px of H31-X/D1.5 dots and push the total over 70%), (b) the untouched
random-component confirmation, and (c) the off-catalogue SGMC discovery proxy / projection. Those are
this lane's real tests. No parameter of the split arms is changed from H31-Y: same lines (reused cache
`data/h31y/lines.f32`, formulas frozen in the Y preregistration), same quotas, same emission order,
same piedmont restriction. ROUTE and every blended surface are excluded. SPLIT65 remains excluded a
priori (65% guaranteed-identical share already risks the 70% rule vs H31-X).

## Lane paragraph (single method — stay inside it)

**H31-Z "hard regime quota split".** Two label-free specialists with a fixed dot quota each, emitted
jointly with one shared 2.8 px Poisson exclusion and B2 catalogue-flank pruning: **JUNC** quota
(H31-X X1 piedmont-junction line verbatim, recomputed in H31-Y and reused from its cache) emitted first,
unrestricted by regime; then **PIED** quota (geometric mean × second-line gate of ASIG analytic-signal,
BASE basement/conductance gradients, GRAV gravity-HG ranks — frozen in the Y preregistration) restricted
to slope ≤ 6°, excluding every pixel within 2.8 px of a JUNC-quota dot. Shortfall top-up rule identical to
H31-Y (recorded in every receipt). Candidate arms: **SPLIT50** (50% JUNC / 50% PIED) and **SPLIT35**
(35% / 65%). No prior dots or peer rasters enter the candidate.

Named non-fault mimics: as H31-Y (pediment edges / Lahontan shorelines / lava snouts for JUNC; basalt-flow
margins, unfaulted volcanic contacts, playa conductance edges, magnetic seams for PIED).

## Frozen experimental plan (≤3 experiments)

Same evaluator protocol as H31-X/H31-Y: `spatial.folds(buffer_px=213)`, `gems57-pooled-hide-v2`, per-fold
visible-B2 emission, 37,654 dots, pooled paired CIs (2,000 draws, seed 520810).

- **EXP-1 (canary citation + screen replication).** Canary values are cited from `evidence/h31y/canary.json`
  (same lines, same code; re-running identical AUCs is not an experiment). Screen arms
  {SPLIT50, SPLIT35, JUNC, PIED, CTRL, SLOPE}; winner = highest pooled HOLDOUT-DTI among {SPLIT50, SPLIT35}.
  JUNC replication vs 0.166133 is re-checked; failure to reproduce any shared-arm number from Y EXP-1
  within 5e-3 = STOP and diagnose.
- **EXP-2 (one ablation + uniqueness).** Winner with PIED piedmont restriction ON vs OFF; keep the better
  on pooled holdout. Final emission on the full catalogue. Uniqueness: exact final-dot 3-px overlap and
  Spearman vs every discrete peer (nine focus sites hash-verified + all local downloads incl. H31-X and
  H31-Y); ROUTE blend of the same lines as disclosed audit-surface proxy for Spearman/top-K only.
  Final-dot overlap > 0.70 or |Spearman| > 0.90 vs any discrete peer = duplicate STOP. Literal
  695-lattice reading recomputed and disclosed (IR-U-02).
- **EXP-3 (untouched confirmation + packaging, zero tuning).** Random whole-component split confirmation,
  **seed 3105** (3103 used by H31-X, 3104 by H31-Y; 3105 is untouched by any lane design). Full/quadrant/
  regime off-catalogue SGMC vs H33-2-B2 and H31-X final dots recomputed same code; anchor-inversion
  PROJECTION (eleven anchors, LOO RMSE); vendor `submission_writer`; both local validators.

## Frozen promotion gates — identical G1–G6 to H31-Y / the selector

G1 format (float32 EPSG:32611 3730×3292, [0,1], {0,1}, 0 on catalogue, exactly 37,654 dots, ≥2.8 px);
G2 canary ≤ 0.90 (cited); G3 pooled HOLDOUT-DTI beats CTRL and SLOPE with paired CI > 0, ≥3/4 quadrants
≥ CTRL, seed-3105 confirmation delta vs CTRL CI > 0; G4 full SGMC ≥ H33 recomputed same day;
G5 final-dot overlap ≤ 0.70 and |Spearman| ≤ 0.90 vs every discrete peer (literal lattice disclosed);
G6 PROJECTION ≥ 0.2778. Verdict `promote` only if all pass, else `negative` (research only). Primary-file
choice between promoted lanes remains the separate selector step (`scripts/selector_audit.py` re-run with
H31-Y and H31-Z added). No fourth experiment; a negative result is a deliverable.

## Data

No new data. Cached 42-band stack and H31-Y line cache reused (formulas frozen in the Y preregistration).
