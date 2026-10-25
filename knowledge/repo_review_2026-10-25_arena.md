# Repository review — Arena continuation, 2026-10-25

## Executive decision

**No new TIFF, model fit, experiment, or competition upload was made in this review.** The method lane's frozen broad-registry STOP remains controlling. The existing MAGREST GeoTIFF is downloadable for research only; the exact-file verifier returns `ok_to_submit: false`. Creating another file or modifying the old one after the STOP would violate the lane and budget rules, not improve the project.

This review independently reran the exact-file denial verifier. It reproduced the current GeoTIFF SHA-256 `c101ceb7237df0890a0f650b4211cc501250b47c1ab9cfeca8ee4cb373eb48d9`, `ok_to_download_for_research=true`, `ok_to_submit=false`, `verdict=negative`. The literal broad-registry counterexample remains a registered spacing-5 lattice with 100% of the candidate dots inside the three-pixel neighborhood. The original nine-download-tree test is not equivalent to the broad registry. No dense/calibration exemption is applied.

The reported H33-2-B2 value `0.2778` remains **USER-REPORTED**, not ORGANIZER-CONFIRMED. The repository's exact-byte geometry analysis supports a plausible explanation based on removing near-catalogue predictions and thus improving precision under a distance-weighted metric; it cannot establish why the private organizer score changed or predict that a new detector will beat it. The prompt's `0.3195` and `0.4413` are also not verified receipts. No competition score is claimed in this review.

## Review passes

### Pass 1 — inspect and verify

- Read the full README and owner prompt, `AGENTS.md`, current status, current run card, all review-pass records, and the frozen MAGREST preregistration before assessing work.
- Installed the pinned environment from `requirements.txt`. Before restoring the two small validation inputs, pytest reported **92 passed, 6 skipped**; after restore, the complete final suite reported **98 passed, 0 skipped**. The skips were limited to checks requiring the two pinned small inputs and did not indicate test failures.
- Ruff passed; `compileall` passed; the metric cross-check's maximum absolute fast-vs-brute difference was `4.441e-16` across 24 random grids and two exact cases.
- `verify_current_run.py --restore-small-inputs` passed and correctly returned a negative/no-submit decision for the served TIFF. Site regeneration and `check_site.py` passed for 20 pages and 296 local links.

### Pass 2 — adversarial consistency review and fixes

- Found `AGENTS.md` overstated `scripts/recheck_magrest.py` as a full scoped-registry check. The code only repeats the original nine-download-tree screen, and needs the ignored `.cache/magrest/responses.npy`, which is absent from this clean checkout. It does not test the broad 695-entry registry. Corrected the instruction: the clean-checkout broad STOP is reproduced by `verify_current_run.py` against the pinned registered counterexample; do not re-fit or recreate the stopped response cache.
- Clarified the README command comments to separate the optional original-nine-tree repeat from the current exact-file/broad-counterexample verifier.
- The evidence collector's console summary called an old proxy-based union the “best research candidate” without identifying its historical proxy scope. Changed its output label to “best historical proxy research candidate (not slot-approved).” This is only a label; the generated registry already kept `current_recommended.name` null and denied slot approval.
- Found a presentation ambiguity: the archived H31-E2 card emphasized earlier narrow-scope PASS badges before its broad-registry STOP and executive summary implied a human selector could still decide. Updated the generated page source and site checker to mark the archived TIFF DO NOT SUBMIT, identify its 100% registry STOP, and state that no human selector can waive a hard gate. Updated the README's first card to call H31-E2 archived/research-only. The current MAGREST artifact remains the separate active run, also DO NOT SUBMIT.

### Pass 3 — full charter and action cross-check

- The owner prompt requires a unique TIFF, but also mandates stopping on overlap above 70% or rank-correlation above 0.90 and forbids more experiments after the three-run/two-hour budget. The project has already recorded an authentic registry counterexample and a literal 100% overlap STOP. The only compliant choice is **not to generate another TIFF**. The previous MAGREST artifact remains a disclosed research deliverable, not approved for competition submission.
- No organizer leaderboard, submission page, quota, or receipt was queried. Non-GitHub official pages are outside this environment's network allowlist; the results in this note rely on pinned local artifacts and owner-mirror evidence, not fresh external authentication.
- The prior session's evidence records successful restoration of all 11 inputs, but this clean runtime started without `data/` or the original feature cache. The exact-file verifier restored only its two small pinned validation inputs and the registry witness. The 42-band production cache/full inputs are not present now; no claim that they were restored in this runtime is made. This does not authorize a new fit after the STOP.

## Candidate hypotheses: backlog only, not authorized in this lane

The repo's existing frozen MAGREST preregistration already names three unfit restoration hypotheses. They are recorded here for the next-session selector, not as new experiments, score forecasts, or approval to widen the active lane. Expected DTI gain is **unknown** for each; the relative ranks below are qualitative scientific priority/cost, not numerical predictions.

| Rank (qualitative) | Hypothesis / existing layers | Target signature | Why it might expose an unmapped fault | Difference from implemented work | Effort / data status / non-fault mimic |
|---:|---|---|---|---|---|
| 1 | **GRAVREST co-restoration**: cached RTP magnetic texture and `iso_grav_anom` gravity texture | Independently estimate signed cross-flank texture restoration and require compatible displacement directions | A buried transfer structure may affect magnetic fabric and basin-density texture where surface scarp relief is weak | Existing work tests magnetic restoration alone and has gravity–magnetic amplitude/concordance features; no paired signed-restoration operator was fit | Medium-high; requires original ignored feature/cache restoration. Gravity's coarser bandwidth is a major resolution risk. Mimic: a shared intrusive or lithologic contact. |
| 2 | **RADREST compositional texture**: GeoDAWN K, Th, U ranked channels | Multichannel rank-correlation restoration of offset compositional stripes, with common signed displacement | Alteration or juxtaposed lithologies may form a discontinuity along a fault not represented in mapped traces | Existing radiometric contrasts/edges are not reciprocal multichannel texture registration | Medium; historical mirror bands exist but current full inputs are absent; validate coverage and missingness before use. Mimic: alluvial-fan provenance boundary or acquisition seam. |
| 3 | **TERRREST drainage-pattern restoration**: detrended elevation and elevation slope | Cross-trace matching of local drainage texture with consistent signed channel offsets | A short fault may offset drainage without preserving a sharp scarp | Existing terrain predictors focus on relief, curvature, step, and scarp texture, not signed drainage-texture restoration | High for defensible resolution; current grid is 100 m, likely too coarse for many offsets, and the full-resolution DEM source would need authorized, verified coverage. Mimic: stream capture or alluvial avulsion. |

These three ideas come from the prior preregistration and are **not being repreregistered or fit here**. The sole present-session method lane is closed by the duplicate STOP. No candidate can be said to beat the current holdout best until a future protocol explicitly resolves the lane/registry degeneracy, restores inputs, performs feature-alone leakage canaries, and runs whole-segment spatial holdout with the shared evaluator. A new lane needs its own preregistration and selection decision; no weekly slot is selected.

## Current limitations and next actions

1. Keep all extant TIFFs with their current evidence class and explicit download/submission status; do not rename, prune, or repackage a stopped raster.
2. Before any new experiment, resolve the literal 70% dense-control ambiguity prospectively without exemptions, and record the allowed registry scope and comparator selection before placement.
3. Restore the full authorized data/cache only if a new protocol and lane are approved; current `data/` lacks the production stack. Preserve owner-mirror versus organizer provenance distinctions.
4. Rebuild the strongest relevant comparator using the pinned shared evaluator and same folds/buffer; estimate the candidate method's own dependence range; use fresh confirmation and a second off-catalogue corroboration instrument.
5. Verify organizer instructions, outside-mask convention, current quota, and any score only from authorized organizer pages/receipts. Do not automate or scrape the leaderboard.
6. Keep the static evidence feed. An automatic live leaderboard feed would conflict with the repository's recorded DrivenData terms review absent written permission.

## Links and evidence trail

- Frozen protocol and alternatives: [`2026-10-25_magrest_preregistration.md`](2026-10-25_magrest_preregistration.md).
- Current exact-file decision: [`registry/current_run.json`](../registry/current_run.json), [`docs/downloads/readiness.json`](../docs/downloads/readiness.json), and [`scripts/verify_current_run.py`](../scripts/verify_current_run.py).
- Broad-registry correction and witness pin: [`evidence/magrest/registry_scope_correction.json`](../evidence/magrest/registry_scope_correction.json), [`registry/shared_registry_57_pin.json`](../registry/shared_registry_57_pin.json).
- Local validation/metric code: [`src/gemsdoe31/submission.py`](../src/gemsdoe31/submission.py), [`scripts/check_metric.py`](../scripts/check_metric.py), [`vendor/gems57/evaluate_holdout.py`](../vendor/gems57/evaluate_holdout.py).
- Official/manual-review URLs are indexed in [`registry/sources.json`](../registry/sources.json). Fresh external verification of non-GitHub URLs was not possible in this runtime.

## Machine-readable run card

```json
{
  "hypothesis": "No new candidate authorized; retain the existing MAGREST restoration raster as a negative research result.",
  "mechanism": "Previously preregistered cross-flank magnetic-texture restoration; no new inference or fit in this review.",
  "named_non_fault_mimic": "Volcanic-flow/lithologic contacts or magnetic survey-line seams.",
  "holdout_dti": {
    "evidence_class": "HOLDOUT-DTI",
    "evaluator_version": "gems57-pooled-hide-v2",
    "value": 0.052972044857535226,
    "ci95": [0.04131136300815562, 0.06532899139157548],
    "withheld_positive_pixels": 2901,
    "scope": "Existing MAGREST run, not a score produced by this repository review."
  },
  "correlation_overlap_vs_registry": {
    "surface_and_final_checked": true,
    "max_abs_rank_correlation": 0.01014651673592438,
    "max_dot_overlap_within_3px": 1.0,
    "witness": "registered spacing-5 lattice; literal overlap STOP",
    "scope": "Nine pinned downloads trees plus one authentic registered counterexample; not exhaustive over all 695 rasters."
  },
  "raster_sha256": "c101ceb7237df0890a0f650b4211cc501250b47c1ab9cfeca8ee4cb373eb48d9",
  "validator_output": {
    "no_nan_inside_footprint": true,
    "values_in_0_1": true,
    "crs_shape_transform_match": true,
    "format_only_pass": true,
    "literal_uniqueness_gate": false,
    "ok_to_download_for_research": true,
    "ok_to_submit": false
  },
  "submission_name": "gemsdoe31-magrest-concordant-37654-20261025-2c800a59ff",
  "submission_note": "MAGREST reciprocal magnetic texture restoration; 2/4px same-sign concordance; independent dots; research-only, not slot-approved",
  "verdict": "negative"
}
```
