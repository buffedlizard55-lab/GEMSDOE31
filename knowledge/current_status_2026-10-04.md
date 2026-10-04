# GEMSDOE31 current status — 2026-10-04 (post-pilot)

**Decision: H31-A STOP.** Its paired pilot metric gate failed, and neither residual variogram produced an identifiable range. The operational range and final buffer are **unknown**. No H31 screen, confirmation, new TIFF, weekly slot, official score, or organizer acceptance is authorized or verified. The home-page download remains a legacy owner-mirror reference, not a current submission candidate.

## Completed

- Preserved the active scope and “Maximize P(Win)” / “Own the Outcome” charter in `README.md`, with project-specific scientific/Git guardrails in `AGENTS.md`.
- Ranked four distinct geological hypotheses; froze H31-A's feature definitions, model, spatial folds, draw schedule, endpoint, residual variogram, buffer rule, and promotion gates before any model fit.
- Completed H31-A pilot draw 10 on GEMSDOE25 owner-mirror commit `c185edd8b09e19846cf34c16050e6cf891ecc2d0`, using the temporary 500 m collar only to obtain out-of-fold residuals. The full report is `knowledge/h31_a_pilot_2026-10-04.md`; full run artifacts are in `evidence/h31_a/pilot/`.
- Pilot metric result: mean paired block ΔDTI **−0.004009** (gate requires >+0.001), with only **1/4** blocks positive (gate requires ≥3/4). This is catalogue-gap proxy evidence, not a competition score.
- Residual diagnostics: 11,194 held-out pixels, 583 trace groups with pairs, 28 populated 500 m bins, but populated support only to 13.75 km. Provisional ~24.964 km point fits reached only 0.808 of modeled partial sill and failed the preregistered plateau criterion. No bootstrap interval was produced. The empirical range and final buffer remain **unknown**; the preregistered stop condition applies.
- Preserved full design and run hashes. The original run JSON is unchanged; `posthoc_variogram_diagnostics.json` supplements its failure record using the saved residual NPZ and unchanged frozen variogram functions. It does not retrain models or alter the decision rule.
- Added a regression test so future variogram failures retain empirical-bin diagnostics. Final suite after this fix: **23 tests passed** without warnings; Ruff and compileall passed.
- Validated the legacy 44,090-positive-pixel D2.8 TIFF against the hash-pinned owner-mirror sample: one float32 band, EPSG:32611, exact 3730×3292 grid/transform, finite footprint values in [0,1], and NaN outside. Organizer sample authenticity/acceptance remains unverified.
- Audited the user-reported D2.8 `0.2600` claim. The pinned owner mirror marks D2.8 unscored; no organizer receipt is available. See `knowledge/prior_submission_audit.md`.
- Checked official source pages and data-access limits. H31-B remains blocked: the official TNM catalog lists a candidate LAZ product, but its binary download failed and no return attributes/full coverage were verified.
- Built static Pages source with overview, executive summary/manual upload guide, research, sources, and AI-disclosure draft. The prominent TIFF remains explicitly legacy/reference-only.

## Stop conditions and remaining evidence gaps

- **Do not run H31 screen draws 11–12 or confirmation draws 13–14 for this H31-A pilot.** The buffer cannot be measured and the metric gate failed; do not choose an arbitrary larger collar or use the unstable 24.964 km point-fit diagnostic as a range.
- No H31 candidate GeoTIFF exists. The same-run parent is not a reproduced current-best comparable incumbent, so that separate promotion gate has also not been satisfied.
- No official sample/template was independently obtained; local file validation used the SHA-pinned owner-mirror copy.
- Full-grid LiDAR/DEM coverage, raw LAZ attributes, and exact GDR 1501 overlap remain unchecked.
- No DrivenData score/leaderboard was accessed; the `0.2600` D2.8 claim remains user-reported and unresolved.
- The AI narrative is a draft for entrant review, not submitted.

## Checks and delivery state

- `pytest`: 23 passed; Ruff: all checks passed; Python compileall: passed.
- All registry/receipt JSON parses; static HTML link audit has no broken local links; legacy-reference format checks pass against the owner mirror only.
- The initial project is committed on `arena/01a104a9-gemsdoe31`. PR/merge and GitHub Pages deployment are not yet verified.

## Recommended next work

1. Do not promote H31-A or create a submission TIFF from its failed pilot. Preserve the negative result.
2. If pursuing another experiment, preregister a distinct hypothesis or a defensible method to identify the residual sill/range before any new fit; retain the same no-arbitrary-buffer stop rule and reproduce the actual current-best comparator on the same folds/buffer.
3. Resolve official-template provenance and permitted LiDAR access if an authorized route becomes available.
4. Open and merge a PR only after checks; enable/verify Pages from the `docs/` folder. Keep the static official leaderboard link only and do not monitor or copy its content.

## Evidence labels

- **OFFICIAL:** contest/source pages and rules in `registry/sources.json`; official score/acceptance remains unverified.
- **OWNER-MIRROR:** inputs/caches and legacy reference pinned to GEMSDOE25; hashes do not authenticate organizer provenance.
- **COMPUTED:** tests, local TIFF validation, runtime-context smoke, and H31-A pilot/variogram diagnostics.
- **USER-REPORTED:** the D2.8 `0.2600` claim in the request; no receipt.
- **INFERENCE:** geological rationales and planning gains; not hidden-label findings.
