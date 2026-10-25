# RBU31-B amendment preregistration — locally-standardized union surface (2026-10-25)

Frozen before any RBU31-B fit or emission. This amendment is informed by
(1) the completed RBU31 Experiment 1 (negative, below) and (2) forensic
evidence that existed in this repo **before** RBU31 was run
(`evidence/h31b_experiments.json`, `src/gemsdoe31/h31b_discover.py`,
`evidence/regime31/regime_forensics.json`). No parameter below was fitted to
any evaluation in this session: σ = 120 px and local weight 0.65 are copied
exactly from the pre-existing H31-B `local_survey_invariant_score`.

## What Experiment 1 established (COMPUTED, evaluator `gemsdoe31-hide-v2.0`)

- RBU31 (union-79, regime-balanced weights, Poisson emission): screen
  HOLDOUT-DTI **0.0955** vs same-run Baseline-D **0.0922** (Δ +0.0034,
  95% CI [−0.0084, +0.0147], folds won **1/4** — NW +0.047, NE/SW/SE losses).
  Baseline-D reproduced the H31-E session's 0.09217 exactly, verifying the
  harness. Leakage canary PASS (max two-sided AUC 0.6118 over 79 features).
- Final-dot SGMC proxies: all 0.0736 / piedmont 0.1122 / mountain 0.0324 —
  below H33-2-B2 (0.0940 / 0.1091 / 0.0654) overall and in mountains.
  Piedmont dot share 75.1% despite regime-balanced weights.
- Duplicate canary: final dots PASS (max 3-px overlap 53.2%, max |ρ| 0.151)
  but the unthinned top-N surface overlaps H31-E2 by 75.3% within 3 px —
  the global-probability surface is too close to the H31-E lane.
- Verdict: **negative**. The v1 TIFFs are retained as a labelled research
  deliverable (`evidence/regime31/v1/`), never to be submitted.

Diagnosis: global top-budget emission on calibrated probabilities starves
regions whose absolute scores run low (mountain bedrock, survey-sparse
west), exactly where off-catalogue SGMC truth concentrates (62.5%
mountain). H31-B's hand-built surface — the only in-repo artifact beating
H33 on SGMC-mountain (0.1095) — differs from every HGB surface here chiefly
by its **12 km local standardization**, which ranks each pixel against its
local neighbourhood and thereby forces budget into every district. Under
DTI's β = 0.8 false-negative weight, covering more distinct truth segments
is worth more than concentrating on the globally highest probabilities.

Rejected alternative: re-adding H31-E2's unsupervised-ridge blend and
tip/relay multiplier. That moves the surface *toward* H31-E2 (already 75.3%
top-N overlap) — lane drift under Parallel-Run Rule 1, and it does not
address the mountain starvation mechanism.

## Frozen RBU31-B specification (single change vs RBU31)

Identical folds, sample_ids, features (79), model config, regime-balanced
sample weights, seeds, comparator (Baseline-D retrained in-run), budgets
and emission (Poisson 2.8 px, > 2 px catalogue prune) as
`knowledge/2026-10-25_rbu31_preregistration.md`. **One change:** the
candidate ranking surface (in every fold evaluation, before emission, and
on the final OOF surface) is replaced by its masked locally-standardized
rank:

```
mean  = G_σ(s·m) / G_σ(m)                 σ = 120 px (12 km), m = prediction-domain mask
z     = (s − mean) / sqrt(G_σ((s−mean)²·m) / G_σ(m) + 1e-6)
blend = 0.65·z + 0.35·rank_CDF(s | m)
out   = rank_CDF(blend | m)
```

Fold mask m = that quadrant's eroded prediction domain; final mask =
footprint. Masking (vs H31-B's unmasked full-grid form) is required for
honest fold evaluation and is disclosed as the one deviation from the
H31-B implementation; σ and 0.65 are unchanged. Baseline-D is **not**
locally standardized (single-mechanism attribution); the H31-E2 and H33
comparators enter only through SGMC proxies and the duplicate canary.

## Experiment accounting and gates (session budget: 3 hypothesis experiments)

- Exp 1 = RBU31 screen (done, negative). Its final emission/SGMC were
  packaging diagnostics, disclosed as informing this amendment.
- **Exp 2 = RBU31-B screen, draw 101** (now a disclosed development draw).
  Same pass rule: ΔDTI > 0.002 and ≥ 3/4 folds vs Baseline-D.
- **Exp 3 = RBU31-B fresh confirmation, draws 202 + 303**, run only if
  Exp 2 passes: ΔDTI > 0.002 with paired 95% CI > 0. These draws are
  untouched by any design decision (identical protocol draws to H31-E2's
  confirmation, never used for selection in this session).
- Final emission + gates exactly as RBU31 §5: G1 format/[0,1]; G2 leakage
  (union features; the standardization is a fixed label-free transform);
  G3a uniqueness on **standardized** surface and final dots vs local +
  nine-site peer rasters (H31-B's own TIFFs included); G3b lattice
  degeneracy disclosed; G4 = Exp 2 + Exp 3; G5 = SGMC beats Baseline-D and
  H33 on all **and** piedmont **and** mountain. All pass ⇒ `promote`
  ("OK TO DOWNLOAD AND SUBMIT"); any failure ⇒ `negative`, stop, no
  further experiments this session.

## Named mimic / risk

Local standardization can promote isolated noise in quiet districts
(survey seams, Lahontan shoreline arcs, volcanic flow margins) — the
canary/SGMC/holdout gates are the arbiters. If RBU31-B wins the catalogue
holdout but loses SGMC-mountain, the mechanism is rejected, not retuned.
