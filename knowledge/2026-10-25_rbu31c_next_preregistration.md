# RBU31-C preregistration — for the NEXT session (not run, 2026-10-25)

Frozen design, written after the negative RBU31/RBU31-B session
(`knowledge/session_review_2026-10-25_rbu31.md`) and **before** any RBU31-C
fit. The next session must not edit this file's gates or coefficients; any
change requires a new dated preregistration written before fitting.

## Rationale in one paragraph

H31-E2's surface (screen HOLDOUT-DTI 0.1274, Poisson ablation 0.1276) beats
RBU31-B (0.0991) by +0.028 on the identical draw/folds. The only components
H31-E2 has that RBU31-B lacks are: (a) a LiDAR-coverage expert blended by
quantile-matching (0.45/0.55), (b) a label-free multi-physics ridge vector
blended at 0.28, and (c) a visible-fault tip/relay multiplier
`1 + 0.65·tip + 0.55·relay`. Which of these carries the gain — and whether
any of it transfers off-catalogue (H31-E2 SGMC-mountain 0.0372 says most of
it does not) — is unknown because they were never ablated one at a time on
untouched draws.

## Candidate (single)

RBU31-B surface exactly as frozen in
`knowledge/2026-10-25_rbu31b_amendment_preregistration.md` (union-79,
regime-balanced weights, masked 12 km local standardization, Poisson
2.8 px, >2 px prune, budget 37,654), with the ranking surface multiplied
per fold by `1 + 0.65·vis_tip_continuation + 0.55·vis_relay_bridge`
computed **only** from that fold's visible faults via the shared
`compute_visible_structural_features` (coefficients copied from H31-E2,
not tuned), clipped to [0, 1], *before* local standardization. No lidar
expert, no unsupervised ridge blend — one added component.

## Experiments (3, in order; stop rules binding)

1. **Surface lane check (pre-placement, no fit beyond fold models):**
   rank-correlation and top-N 3-px overlap of the C surface vs H31-E2's
   packaged dots and vs the nine focus peers. If |ρ| > 0.90 or top-N/final
   overlap > 70% vs any genuine submission → duplicate STOP, no emission.
2. **First evaluation on untouched draws 202 + 303** (draw 101 is a burned
   development draw and must not be used): pooled HOLDOUT-DTI vs same-run
   Baseline-D and vs RBU31-B rerun identically. Pass: Δ vs Baseline-D
   > 0.002 with paired 95% CI > 0, ≥ 3/4 folds in each draw, AND pooled
   DTI > RBU31-B's on the same draws.
3. **Final emission + G1/G2/G3a/G5 exactly as before**, including SGMC
   all/piedmont/mountain vs Baseline-D and the actual H33-2-B2 peer file.
   Promote only if every gate passes; otherwise negative and stop.

## Named mimic

Tip/relay lobes also fire at drainage-aligned segment ends and shoreline
arc terminations; the SGMC-mountain gate is the arbiter. If C wins the
catalogue holdout but loses SGMC, the component is catalogue-geometry
overfitting and must be rejected for discovery use.
