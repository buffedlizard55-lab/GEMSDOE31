# Current project status — 2026-10-26

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
