# Current project status — 2026-10-26

## PGR31 session update (2026-10-26 · branch `arena/71e9be2c-gemsdoe31`)

**Decision unchanged: no competition submission is approved.** A new lane (PGR31, Poisson
pseudo-gravity discordance) was preregistered (`knowledge/2026-10-26_pgr31_preregistration.md`,
SHA-256 `a161635f…`), run within the 3-experiment budget, and produced a unique research GeoTIFF:
[`gemsdoe31-pgr31-poisson-pseudograv-37654-20261026-zeros.tif`](../docs/downloads/gemsdoe31-pgr31-poisson-pseudograv-37654-20261026-zeros.tif)
(37,654 dots, SHA-256 `9dcc2e0c4da3f40c17796cfd4ab306cd6aa0ab218d98f83f3b5cbeb406d4b628`).
**DOWNLOAD FOR RESEARCH: YES · SUBMIT: NO** (`verdict: negative`, `ok_to_submit: false`;
`python scripts/verify_pgr31_run.py` reproduces the decision with no human inspector).

- Canary PASS (max two-sided AUC 0.5766). HOLDOUT-DTI (`gems57-pooled-hide-v2`, 2,778 withheld):
  candidate 0.0764 [0.0449, 0.1102] vs control 0.0761; paired Δ +0.0003 [−0.0202, +0.0240],
  2/4 quadrants; SGMC proxy Δ −0.0080 → screen **FAIL**; fresh confirmation (draw 52) gated off.
- Uniqueness (genuine-submission scope, 48 rasters incl. fetched nine-focus bests): surface
  max |ρ| 0.1506; final-dots max 3-px overlap 48.6% (33.2% vs H33-2-B2). The calibration-lattice
  degeneracy is disclosed in the run card, not exempted. Full record:
  `knowledge/2026-10-26_pgr31_executive_summary.md`, `evidence/pgr31/run_card.json`.
- Inputs were restored hash-verified from owner mirrors (`evidence/pgr31_data_restore_*.json`);
  DrivenData was not contacted; 0 slots spent; no ORGANIZER-CONFIRMED score exists.

## Decision

**No competition submission is currently approved.** No experiment, TIFF, upload, leaderboard access, or weekly slot was used in this review continuation. The only highlighted current artifact remains the existing MAGREST all-finite research TIFF, [downloadable for research only](../docs/downloads/gemsdoe31-magrest-concordant-37654-20261025-2c800a59ff-zeros.tif) and **NOT approved to submit**. Its machine decision receipt is [here](../docs/downloads/magrest-run-card.json).

The TIFF has passed local format checks against the owner-mirror sample template, but the exact file fails the active literal registry-overlap gate; format validity is not submission authorization, organizer acceptance, nor uniqueness. The registry witness covers every allowed cell, giving any nonempty in-footprint dot set 100% forward 3-pixel overlap, above the protocol's 70% stop threshold. The broader registry scan is not exhaustive, but that one valid witness is sufficient to fail the gate.

## Scientific and score status

- The highest supplied nine-site claim remains GEMSDOE32 H33-2-B2 at **USER-REPORTED 0.2778**; no organizer receipt is available. The claims 0.3195 and 0.4413 are likewise not independently verified here.
- Raster geometry shows H33-2-B2 is D2.8 support after removal of the 1–2-pixel catalogue-flank dots. A plausible metric mechanism is reduced false-positive budget spent near known faults, but the exact score cause cannot be inferred without competition truth.
- Current MAGREST paired screening did not pass its preregistered efficacy criteria; its HOLDOUT-DTI and paired interval are in [`registry/current_run.json`](../registry/current_run.json). These values are not leaderboard scores.
- Four future hypotheses are desk-only in [`knowledge/repo_review_2026-10-26.md`](repo_review_2026-10-26.md). No expected improvement is quantified.

## Verified checks this review

- Tests: 118 passed after restoring the two pinned small inputs; no skips.
- Ruff: passed.
- Fast/brute metric agreement: max absolute difference 4.441e-16 over 24 test grids; exact cases passed.
- Exact-run verifier: `verdict=negative`, `ok_to_download_for_research=true`, `ok_to_submit=false`; MAGREST SHA-256 `c101ceb7237df0890a0f650b4211cc501250b47c1ab9cfeca8ee4cb373eb48d9`.
- Generated site: 21 pages, 364 local links, site checks passed.

Full details and caveats: [`knowledge/repo_review_2026-10-26.md`](repo_review_2026-10-26.md), [`registry/review_passes.json`](../registry/review_passes.json).

## Blockers and next work

1. Resolve the omitted assigned-method paragraph and obtain a valid new-lane authorization before experimentation.
2. Resolve the literal dense-registry overlap degeneracy through explicit protocol ownership; do not add an ad hoc exemption.
3. Reproduce a relevant incumbent with the unchanged shared evaluator and authorized spatial holdouts; the private competition labels remain unavailable.
4. Obtain organizer-authenticated sample/template/rules/score receipts through permitted access. Do not scrape or submit automatically.
5. Only after those gates: preregister one candidate, run feature-only leakage canaries, validate on blocked holdout, conduct fresh confirmation, and have a separate selector decide slot eligibility.
