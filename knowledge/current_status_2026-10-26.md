# Current project status — 2026-10-26

## Decision

**No competition submission is currently approved.** No experiment, TIFF, upload, leaderboard access, or weekly slot was used in this review continuation. The only highlighted current artifact remains the existing MAGREST all-finite research TIFF, [downloadable for research only](../docs/downloads/gemsdoe31-magrest-concordant-37654-20261025-2c800a59ff-zeros.tif) and **NOT approved to submit**. Its machine decision receipt is [here](../docs/downloads/magrest-run-card.json).

The TIFF has passed local format checks against the owner-mirror sample template, but the exact file fails the active literal registry-overlap gate; format validity is not submission authorization, organizer acceptance, nor uniqueness. The registry witness covers every allowed cell, giving any nonempty in-footprint dot set 100% forward 3-pixel overlap, above the protocol's 70% stop threshold. The broader registry scan is not exhaustive, but that one valid witness is sufficient to fail the gate.

## Scientific and score status

- The highest supplied nine-site claim remains GEMSDOE32 H33-2-B2 at **USER-REPORTED 0.2778**; no organizer receipt is available. The claims 0.3195 and 0.4413 are likewise not independently verified here.
- Raster geometry shows H33-2-B2 is D2.8 support after removal of dots within 2 pixels of the public catalogue. A plausible metric mechanism is reduced false-positive budget spent near known faults, but the exact score cause cannot be inferred without competition truth.
- Current MAGREST paired screening did not pass its preregistered efficacy criteria; its HOLDOUT-DTI and paired interval are in [`registry/current_run.json`](../registry/current_run.json). These values are not leaderboard scores.
- Three hypotheses in the current README are desk-only; no expected score improvement is quantified and none is authorized for implementation.

## Prior MAGREST verification receipts

These receipts were recorded before the current documentation/site-source reconciliation; they are **not** verification of the edits now in progress.

- Prior suite: 118 passed after restoring the two pinned small inputs; no skips.
- Prior Ruff and metric checks: passed; fast/brute maximum absolute difference 4.441e-16 over 24 grids, with exact cases passing.
- Prior exact-run verifier: `verdict=negative`, `ok_to_download_for_research=true`, `ok_to_submit=false`; MAGREST SHA-256 `c101ceb7237df0890a0f650b4211cc501250b47c1ab9cfeca8ee4cb373eb48d9`.
- Prior generated site: 21 pages, 364 local links, checks passed.

## Current reconciliation verification

README, archived knowledge summaries, registers, and the site generator now distinguish the active MAGREST run from historical parallel lanes; classify score claims as USER-REPORTED absent exact organizer receipts; limit pairwise comparator results to their checked subsets; and preserve the literal shared-registry STOP. The H33 metric explanation states the distinct general ratio (`0.05882`) and isolated-dot threshold (`0.05556`) without claiming private-score causation. The three current hypotheses—GRAVREST, RADREST, TERRREST—remain desk-only, unscored, and unauthorized. Archived H31-S preregistration bytes were preserved unchanged (SHA-256 `fe9464365d34d84ea2205579c50a3960ba0dc4c843c66d0519ae355e19f8de03`).

Fresh verification on the current edits completed:
- `scripts/verify_current_run.py --restore-small-inputs`: negative decision reproduced; research download remains allowed; submission denied; MAGREST raster SHA-256 unchanged (`c101ceb7237df0890a0f650b4211cc501250b47c1ab9cfeca8ee4cb373eb48d9`). Restored the two small pinned inputs and one registered witness through the project verifier; these ignored research inputs are not tracked.
- `scripts/verify_h31j.py` and `scripts/verify_h31t.py`: both returned verified with `slot_approved = false`.
- `pytest`: **136 passed**; full `ruff check .` and `compileall -q src scripts tests`: passed.
- `scripts/check_metric.py`: maximum absolute fast/brute DTI difference **4.441e-16** over 24 grids; both exact cases passed; 29 kernel offsets within 300 m.
- `scripts/collect_evidence.py`: refreshed registers from 155 evidence artifacts and 13 submission records; archived RBU31 named-peer results are now explicitly subset-only, not broad uniqueness.
- `scripts/build_site.py` and `scripts/check_site.py`: generated 22 pages; all site checks passed across **438 local links**. `docs/data/submissions.json` and `docs/feed.json` now identify MAGREST as the research-only active artifact, with no recommended/submittable file.
- `git ls-files .cache data work .venv` is empty; generated caches and restored inputs remain ignored.

No experiment, TIFF, upload, leaderboard access, or weekly slot was used. This verification confirms integrity, presentation, and denial status—not competition performance, global uniqueness, organizer acceptance, or the truth of any reported score. Full review history and remaining gates: [`knowledge/repo_review_2026-10-26.md`](repo_review_2026-10-26.md), [`registry/review_passes.json`](../registry/review_passes.json).

## Blockers and next work

1. Resolve the omitted assigned-method paragraph and obtain a valid new-lane authorization before experimentation.
2. Resolve the literal dense-registry overlap degeneracy through explicit protocol ownership; do not add an ad hoc exemption.
3. Reproduce a relevant incumbent with the unchanged shared evaluator and authorized spatial holdouts; the private competition labels remain unavailable.
4. Obtain organizer-authenticated sample/template/rules/score receipts through permitted access. Do not scrape or submit automatically.
5. Only after those gates: preregister one candidate, run feature-only leakage canaries, validate on blocked holdout, conduct fresh confirmation, and have a separate selector decide slot eligibility.
