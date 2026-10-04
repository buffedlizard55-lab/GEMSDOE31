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
- Audited the D2.8 `0.2600` claim. GEMSDOE25 marks its D2.8 file unscored, while the later GEMSDOE28 page calls 0.2600 owner-reported; no organizer receipt is available. The subsequent H27-4 `0.2708` user claim conflicts with GEMSDOE28's UNSCORED status. See `knowledge/prior_submission_audit.md` and `knowledge/score_and_prior_art_review_2026-10-03.md`.
- Checked official source pages and data-access limits. H31-B remains blocked: the official TNM catalog lists a candidate LAZ product, but its binary download failed and no return attributes/full coverage were verified.
- Built static Pages source with overview, executive summary/manual upload guide, research, sources, and AI-disclosure draft. The prominent TIFF remains explicitly legacy/reference-only.

## Review addendum — score claim, prior art, and next hypotheses (2026-10-03 PDT / 2026-10-04 UTC)

- Read the user-supplied score history and inspected the public GEMSDOE28 owner page/repository at source HEAD `33cc5942220f1440531d7184889c5c6f5d2f0a3e`. The page labels H27-4 `UNSCORED`, while the request attributes 0.2708 to it. The page publishes local catalogue-gap gains (+0.00177 and +0.00176 on its own seed sets); these are not competition scores and were not independently rerun here. See [`knowledge/score_and_prior_art_review_2026-10-03.md`](score_and_prior_art_review_2026-10-03.md).
- The GEMSDOE28 page calls D2.8 `0.2600` owner-reported; the pinned GEMSDOE25 register marks its D2.8 artifact unscored. Both remain OWNER-MIRROR/USER-REPORTED claims with unresolved exact file attribution. The user-reported 0.3195 public-best value was not checked against the official leaderboard.
- Added a four-item desk shortlist—USGS ComCat focal-mechanism geometry, ASTER spectral alteration, age-conditioned fan scarps, and groundwater-head compartments—with layers, physics, prior-art boundary, planning ΔDTI ranges/cost, and source preflight limits. The ComCat API returned 618 moment-tensor records in a broad approximate envelope; ASTER CMR found at least one matching granule; USGS Water Data returned sample groundwater records. These are access leads only: **no candidate was fitted or holdout-validated**.
- Confirmed the current workspace lacks `data/` competition inputs and `/tmp/gemsdoe25-full`; the top candidate cannot be reproduced here. The H31-A range remains unknown, so no arbitrary buffer, new TIFF, or weekly slot was substituted.
- Fixed a branch guard defect: the instructions and runner hard-coded the prior session's `arena/01a104a9-gemsdoe31`; the active session uses `arena/01a1050e-gemsdoe31`. The runner now uses one `EXPECTED_BRANCH` constant and tests both acceptance and rejection paths.
- Added a site score-audit page and source links. The one-click TIFF remains explicitly legacy/reference-only. No automatic leaderboard feed or upload was added.

## Stop conditions and remaining evidence gaps

- **Do not run H31 screen draws 11–12 or confirmation draws 13–14 for this H31-A pilot.** The buffer cannot be measured and the metric gate failed; do not choose an arbitrary larger collar or use the unstable 24.964 km point-fit diagnostic as a range.
- No H31 candidate GeoTIFF exists. The same-run parent is not a reproduced current-best comparable incumbent, so that separate promotion gate has also not been satisfied.
- No official sample/template was independently obtained; local file validation used the SHA-pinned owner-mirror copy.
- Full-grid LiDAR/DEM coverage, raw LAZ attributes, and exact GDR 1501 overlap remain unchecked.
- No official DrivenData leaderboard page, private score page, or submission interface was accessed. The `0.2600` D2.8 and `0.2708` H27-4 claims remain USER-REPORTED/OWNER-MIRROR and unresolved against the relevant owner registries/pages.
- The AI narrative is a draft for entrant review, not submitted.

## Checks and delivery state

- Earlier H31-A post-pilot suite: 23 passed. Latest review suite: **25 passed**; Ruff: all checks passed; Python compileall: passed.
- All 11 checked JSON documents and 8 pilot JSONL rows parse; the latest 7-page HTML local-link/fragment audit has no broken references; score-claim classifications and the legacy TIFF SHA-256 were rechecked. The local legacy-format receipt remains a check against the owner mirror only.
- Added three cumulative reviews for this extension (implementation/source verification, independent assumption/link review, whole-charter cross-check) as passes 4–6 in `registry/review_passes.json`; earlier passes 1–3 remain historical.
- PR #1 merged to `main` at `18a9c4e9493192a21f2bb22ca0356d4a24be8d6c`; follow-up PR #2 merged at `d8b531025c63e9d56897f8b983bdfca284b33420`. GitHub reported no status checks for either PR. Pages is configured for `main` at `/` and reports `built`; the root `index.html` redirects into `docs/`. A cache-busted fetch of the public Pages URL followed the redirect and showed the current site/H31-A stop status. Changing the setting directly to `/docs` returned 403 `Resource not accessible by integration`; the root redirect workaround is live.
- This review extension was committed as `3cd7fbf` plus its PR-status record `51ee6dc` on `arena/01a1050e-gemsdoe31`, pushed only to that branch, and merged through [PR #4](https://github.com/buffedlizard55-lab/GEMSDOE31/pull/4) at `b93b7ae81c5cdd594ed55715a5e9f14ca3dc199c` (2026-10-04T04:18:01Z). GitHub Pages run [37176602101](https://github.com/buffedlizard55-lab/GEMSDOE31/actions/runs/37176602101) succeeded; the public root and score-audit page were fetched and showed the updated content. No official score, candidate, or organizer acceptance is implied.

## Recommended next work

1. Do not promote H31-A or create a submission TIFF from its failed pilot. Preserve the negative result.
2. The four new desk hypotheses are not preregistered or fitted. Select one only after product-level coverage/access, licensing, layer quality, and causal-confounder checks; separately define a defensible residual-range/buffer method before any new spatial holdout. Never use an arbitrary buffer.
3. Reproduce the actual current-best comparator on identical folds and buffer, then require a paired holdout win, fresh confirmation, and exact-file validation before considering a slot.
4. Resolve official-template provenance, authorized runtime/data access, and permitted LiDAR/ASTER inputs if a documented route becomes available. Keep the static official leaderboard link only; do not monitor or copy its content.

## Evidence labels

- **OFFICIAL:** contest/source pages and rules in `registry/sources.json`; official score/acceptance remains unverified.
- **OWNER-MIRROR:** inputs/caches and legacy reference pinned to GEMSDOE25, plus the later GEMSDOE28 owner-page reports/status; hashes/pages do not authenticate organizer provenance.
- **COMPUTED:** tests, local TIFF validation, runtime-context smoke, and H31-A pilot/variogram diagnostics.
- **USER-REPORTED:** supplied D2.8 `0.2600`, H27-4 `0.2708`, and claimed high `0.3195`; none has an organizer receipt here.
- **INFERENCE:** geological rationales and subjective ΔDTI planning ranges; not hidden-label findings, measured candidate results, or score forecasts.
