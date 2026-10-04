# GEMSDOE31 — auditable GEMS fault-mapping research

> **Current decision: H31-A is stopped; no new submission is approved.** Its pilot missed the paired proxy gate and neither residual variogram identified a stable range, so the final buffer is unknown. The visible GeoTIFF is a legacy owner-mirror reference for inspection only. It passes local format checks against the pinned owner-mirror sample template, but is not organizer-authenticated, not an H31 candidate, and not approved for a weekly slot. No official score has been independently verified.

## Start here

- **GitHub Pages site:** [buffedlizard55-lab.github.io/GEMSDOE31](https://buffedlizard55-lab.github.io/GEMSDOE31/) (root entry redirects to [`docs/index.html`](docs/index.html); prominent legacy-reference download, status and project links).
- **Submission executive summary and manual upload guide:** [`docs/executive-summary.html`](docs/executive-summary.html).
- **Research hypotheses and current H31-A design:** [`docs/research.html`](docs/research.html) and the full [H31 preregistration](knowledge/2026-10-04_h31_hypotheses_preregistration.md).
- **Official and trusted source register:** [`docs/sources.html`](docs/sources.html) / [`registry/sources.json`](registry/sources.json).
- **Prior-submission forensic audit:** [`knowledge/prior_submission_audit.md`](knowledge/prior_submission_audit.md).
- **Data provenance and file-validation receipts:** [`registry/data_provenance.json`](registry/data_provenance.json) and [`registry/submissions.json`](registry/submissions.json).
- **Current outcome/status:** [`knowledge/current_status_2026-10-04.md`](knowledge/current_status_2026-10-04.md).
- **Latest result/score-claim audit:** [`knowledge/score_and_prior_art_review_2026-10-03.md`](knowledge/score_and_prior_art_review_2026-10-03.md) and the [one-page site review](docs/score-audit.html).

### Latest brief addendum — reread before each substantive task

The task is to improve **geological fault mapping**, not to predict geothermal favorability or vents as the competition target. The user-supplied values `0.2708` for GEMSDOE28 H27-4 and `0.3195` for the public leaderboard are unverified claims, not training labels or verified official scores. The rest of the historical score list supplied by the user is context only; its individual entries were not independently authenticated here and must not be represented as official results. The linked GEMSDOE28 owner page marks its H27-4 raster **UNSCORED** while reporting internal proxy gains; the pinned GEMSDOE25 registry marks its D2.8 file unscored, although GEMSDOE28 separately calls D2.8 `0.2600` owner-reported. Preserve this discrepancy; do not invent an attribution or promise a score above either number.

Before any new fit, review prior art across GEMSDOE25 and GEMSDOE28, propose 3–5 genuinely distinct fault-geology hypotheses with named layers, physical signal, novelty, uncertain holdout-DTI planning range, cost, and product-level access checks. Do not call a hypothesis viable merely because a catalog page exists. The current desk shortlist is in the [score/prior-art audit](knowledge/score_and_prior_art_review_2026-10-03.md); it is not a preregistration or result. The H31-A pilot failed and its same-trace residual range/final buffer are unknown, so **no new spatial holdout, TIFF, or weekly submission is authorized under that design**. Never replace the unknown measured buffer with 4–5 pixels or the unstable 24.964 km diagnostic.

The one-click `.tif` below is a **legacy reference only**, not a candidate to upload. A new file requires authorized inputs and template provenance, a stable out-of-fold residual variogram and measured buffer, a paired holdout win over a reproduced incumbent, fresh confirmation, and strict exact-file validation. No automatic DrivenData leaderboard/feed or upload is allowed under the documented Terms; use the static official link for manual review only. All score observations supplied by the user or reported on sibling project sites remain explicitly USER-REPORTED/OWNER-MIRROR unless an organizer receipt is available.

### Prominent download — legacy reference only

[**Download the format-checked legacy D2.8 reference GeoTIFF**](docs/downloads/gemsdoe31-reference-d28-offcat-44090-20261004-nan.tif) · [validation receipt](docs/downloads/gemsdoe31-reference-d28-offcat-44090-20261004-format-check.json) · SHA-256 `5f963b8bca5ec226ddc7caaadec239c6be6d28aa567f890033be04d04bfd5e32`.

This single-band float32 file contains 44,090 binary positive pixels and is pixel-identical (not byte-identical) to a D2.8 raster in the pinned GEMSDOE25 owner mirror. It is **not** a new submission, not an H31 result, and not slot-approved. The D2.8 0.2600 value is unresolved: the pinned GEMSDOE25 registry marks that artifact unscored, while the GEMSDOE28 owner page calls 0.2600 owner-reported. The user's H27-4 0.2708 claim conflicts with the GEMSDOE28 page, which marks that artifact unscored. Neither file-to-score link has an organizer receipt. Do not treat the reference download or local format receipt as proof of an official score or upload acceptance.

## Standing project charter — full active scope

The charter below preserves the complete active scope and acceptance criteria from the project request as a faithful consolidated restatement. It is the recurring project prompt: reread this section, the active preregistration, and the current outcome/status record before each substantive continuation. (It is not represented as a verbatim quote where the session handoff condensed the original wording.)

### Objective and decision principles

Build a scientifically rigorous, reproducible and auditable GEMS Prize project that **maximizes the probability of a valid, high-performing submission** and **owns the outcome**. Arena core values **“Maximize P(Win)”** and **“Own the Outcome”** mean prioritizing evidence and genuine geological signal over optimistic claims, reporting failed tests plainly, and spending a weekly slot only when the candidate has passed the registered gates.

The task is to predict geological faults—not geothermal favorability, vents, or merely the public known-fault inventory. Treat competition truth as incomplete and potentially inaccurate. Distinguish official sources, owner/user-reported claims, computed evidence, and inference at every point. Provide source links and flag irregularities; do not invent results or imply that a proxy score is a competition score.

### Scientific hypotheses and validation

1. Review earlier submissions, code, hypotheses, and outcomes before proposing new work. Do not relabel H26–H30 experiments as new evidence.
2. Nominate **3–5 genuinely distinct geological hypotheses**. For each, document input layers, physical signature, why it could reveal faults missing from existing maps, what is novel relative to this repository, uncertain expected spatial-holdout DTI gain, implementation cost, data provenance/access, and validation status. Rank candidates before implementation.
3. Preregister the selected candidate's features, model, folds, draws/seeds, metric, analysis, buffer rule, and promotion gate before fitting. Compare it to a comparable same-run incumbent on a spatially blocked holdout. A screen pass alone is not sufficient; use fresh confirmation draws without tuning on them.
4. Derive the spatial collar empirically from out-of-fold residual semivariograms along known fault traces. Report the fitted range and uncertainty, and use at least the upper fitted range. Do not assume a generic 4–5-pixel buffer; if the range is not identifiable, report it as unknown and stop.
5. Do not use a weekly submission slot unless the candidate beats the current comparable spatial-holdout best, passes fresh confirmation, and passes the exact-file audit. A proxy DTI or modelled expectation is never a leaderboard score.
6. If data needed for a candidate cannot be accessed, identify and check a free official source, record what coverage/metadata/binaries were actually verified, and describe the blocker rather than inventing evidence.

### Submission artifact, site, and user instructions

1. Build a clean GitHub Pages site with a prominent, easy-to-find single-band GeoTIFF download and a clear executive-summary subpage. Make the current artifact's status unmistakable; never label an unconfirmed legacy file as the active submission.
2. For any candidate GeoTIFF, verify the organizer's CRS, grid, dimensions, geotransform/bounds, single-band float32 type, and valid footprint. All footprint predictions must be finite and in `[0,1]`; values outside the footprint must be null/NaN as the official page specifies. No silent clipping or zero-filling. Include a regression test that catches the previous “Predicted values must be in range [0, 1]” class of error.
3. Include a unique submission name, a concise optional comment, and exact manual instructions for uploading on DrivenData. Clearly mark reserved metadata versus an actual submitted file. Explain that AI use must be disclosed in the narrative as required by the official rules.
4. Explain the prior GEMSDOE25/D2.8 and GEMSDOE28/H27-4 result history while separating user/owner claims from organizer receipts. The 0.2600 D2.8 and 0.2708 H27-4 claims remain unresolved; see [`knowledge/prior_submission_audit.md`](knowledge/prior_submission_audit.md) and the [new score/prior-art audit](knowledge/score_and_prior_art_review_2026-10-03.md).

### Source, access, and integrity rules

- Use official or primary sources for contest rules, data specifications, and third-party products. Preserve them in `registry/sources.json` with retrieval date, verified claims, and limits.
- DrivenData Terms of Use prohibit robot/spider/automatic access “for any purpose, including monitoring or copying” and prohibit manual monitoring/copying without prior written consent. Do **not** build a leaderboard scraper, periodic feed, or automatic submission. A static official leaderboard link for manual review is acceptable.
- Owner-mirror hashes prove byte identity to that mirror only; they do not prove organizer authenticity, acceptance, or score.
- Do not commit large competition inputs, LAZ files, or regenerable caches. Keep provenance hashes and only the small evidence artifacts required for audit.

### Review, reporting, and delivery

Perform cumulative review passes: (1) implement and verify against sources and preregistration; (2) inspect and fix bugs, assumptions, leakage and edge cases; (3) re-check the full result against this charter and report remaining limits. Record each pass in `registry/review_passes.json`. Keep the site and README current, flag irregularities, and make the remaining work clear. Prepare a pull request and merge it to `main` if repository permissions and checks allow; report a PR, merge, deployment, official score, or organizer acceptance only when there is a verifiable status/receipt.

## Current verified state

- H31-A's two-feature magnetic-scale design was frozen before fitting. Pilot draw 10 then failed its paired DTI screen and produced no stable same-trace residual range; **H31-A is stopped, the final buffer is unknown, and no further screen/confirmation is authorized**. See the [pilot report](knowledge/h31_a_pilot_2026-10-04.md) and its saved residual/variogram artifacts under `evidence/h31_a/pilot/`. H31-B has an official TNM Access API tile record within sampled owner-mirror footprint locations, but the LAZ binary download failed; no return attributes were inspected.
- **25 tests pass in the latest review**; Ruff, compileall, JSON syntax, HTML local-link/fragment, score-classification, and legacy-TIFF hash checks pass. The earlier 23-test count in the H31-A pilot record is historical. A production runtime-context smoke and the registered pilot both used the pinned sibling. Pilot metrics are local catalogue-gap proxy results, **not** competition scores; its unstable ~24.964 km point-fit diagnostic is not an operational range. There is no data-derived final buffer, H31 confirmation, slot-eligible candidate, or new submission.
- The owner-mirror sample template has CRS EPSG:32611, shape 3730×3292, 100 m transform, and 5,167,373 finite footprint cells. The legacy reference passes local exact-grid/range checks against that template. The original organizer template and organizer acceptance are not independently verified here.
- No official DrivenData leaderboard page, private score page, or submission interface was accessed. User-supplied scores and owner-mirror claims are classified and audited; no automatic leaderboard feed or submission tool exists. The H27-4 `0.2708` claim conflicts with the GEMSDOE28 page's `UNSCORED` status; the D2.8 `0.2600` value conflicts with the pinned GEMSDOE25 registry but is called owner-reported on GEMSDOE28.
- This checkout currently has no `data/` competition inputs and no `/tmp/gemsdoe25-full` sibling/cache tree. The H31 runner cannot be rerun from this workspace until a permitted, hash-verified data/runtime copy is available.
- The score/prior-art review was submitted as [PR #4](https://github.com/buffedlizard55-lab/GEMSDOE31/pull/4) from `arena/01a1050e-gemsdoe31` and merged to `main` at `b93b7ae81c5cdd594ed55715a5e9f14ca3dc199c` on 2026-10-04. GitHub Pages run [37176602101](https://github.com/buffedlizard55-lab/GEMSDOE31/actions/runs/37176602101) completed successfully; the public root and score-audit page were fetched after deployment. This verifies publication only, not any score, organizer acceptance, or candidate.

## Reproducibility and code

Python 3.11; pinned versions are in [`requirements.txt`](requirements.txt). Run checks with:

```bash
python -m pytest -q
ruff check .
```

The H31 runner is intentionally fail-closed: it requires the fixed Arena branch, a clean worktree, the pinned clean GEMSDOE25 sibling checkout, hash-matching mirror inputs/caches, and an empty output directory. It never contacts DrivenData and never writes a submission GeoTIFF. See [`AGENTS.md`](AGENTS.md) for ongoing scientific and execution guardrails.
