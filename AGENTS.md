# Current review/permission front door (2026-10-26 bf9d261d)

Read `registry/release_status.json` and `knowledge/2026-10-26_release_review_bf9d261d.md` first.
No file is approved. `registry/current_run.json` is historical MAGREST evidence, not the latest release decision.
Run `python scripts/build_release_status.py --check` after restoring small inputs. Never use the legacy
`submission_gate.py` diagnostic to approve a slot. It cannot implement the binding two-stage literal registry gate.
Preserve historical run cards; do not interpret their promotion flags as current authorization.

# GEMSDOE31 agent instructions

Before changing this repository, read the entire `README.md` (including the preserved owner prompt), the latest status, `registry/current_run.json`, `registry/review_passes.json`, and `knowledge/2026-10-25_magrest_preregistration.md`. H31-A remains a historical STOP, not an active experiment. Keep the README as the recurring project charter; update the status record at the end of substantive work.

## Scientific and evidence rules

- Separate **OFFICIAL**, **OWNER-MIRROR**, **COMPUTED**, **INFERENCE** and **USER-REPORTED** claims. A hash proves byte identity to a mirror, not organizer authenticity; owner-reported leaderboard scores are not verified without an official receipt.
- Do not scrape, poll, automatically access, or manually monitor/copy DrivenData leaderboard material without prior written permission. A static official leaderboard link is permitted. Never submit/upload automatically.
- Preregister candidate physics, model, holdout, metric, buffer, seeds, and promotion gates before any fit. Do not use a weekly slot unless the candidate beats the same-run incumbent on an empirically buffered spatial holdout and passes fresh confirmation. A positive screen alone is insufficient.
- Derive the spatial collar from out-of-fold residual semivariograms on known fault traces. Never substitute an arbitrary pixel buffer or report the temporary pilot collar as an empirical range.
- The owner's 2026-10-25 highest-priority instruction supersedes the old blanket ban on packaging negative experiments: a genuinely new, duplicate-screened research TIFF is a deliverable even after a failed efficacy screen. Never package after a duplicate/leakage STOP. Final MAGREST review discovered a broader registered lattice only after packaging; the literal overlap is 100% and the lane is STOP. Retain the already-created research bytes with this disclosed ordering defect; do not generate any new TIFF or silently exempt dense controls. Label research download permission separately from submission permission; a failed/unconfirmed experiment is NOT approved for upload. Keep legacy D2.8/H27 files audit-only; never copy their dots or rename them as new work.
- MAGREST used exactly three fixed experiments; do not add a fourth or tune after this negative screen. Its 21.3 km collar is inherited from historical residual evidence, not a measured MAGREST range. No claim of beating the global holdout best is established. A fresh scientific continuation needs a new preregistration and lane assignment/assumption disclosure.
- Reuse the pinned shared template in `vendor/gems57` unchanged, including `evaluate_holdout.py`, `submission_writer.py` and `cache_bands`. All 19 band-cache hashes must match the template receipt. Report a shared-tool defect upstream, never hide a private evaluator fork.
- Duplicate scope includes ALL comparable downloadable TIFFs in the nine pinned sites AND the shared registry/other-path controls; do not repeat the original narrow-preflight defect. The pinned 695-raster template manifest contains a verified spacing-5 counterexample that already forces STOP. No dense/sparse, calibration or matched-budget exemptions. Check full-footprint ranks and three-pixel positive-support overlap before placement and on final dots; stop above |rho|=0.90 or overlap=0.70. State the scope, not global uniqueness.
- Validate a submission GeoTIFF against the sample template: EPSG:32611, exact shape/transform, one float32 band,
  all footprint values finite in `[0,1]`, and NaN outside the footprint (an all-finite variant is written too and
  validated under its own convention). No silent clipping or zero-filled outside area. `tests/test_submission.py`
  keeps the regression test for the "Predicted values must be in range [0, 1]" error class.
- Report **both** truth proxies on every arm: the catalogue-gap holdout and the off-catalogue (SGMC) discovery proxy.
  They disagree, and the catalogue-based one must never be used to promote an arm; state the proxy's limits whenever
  a number from it is quoted.
- Never quote a proxy DTI as a competition score. Owner-reported scores carry the file's SHA-256 and the
  `USER-REPORTED` class; an organizer receipt is required before anything is reported as a score.

## Execution / Git rules

- Work only on the Arena branch attached to the current session (read the current session instructions, never an older hard-coded branch ID);
  never switch, create or push another branch.
- Keep large input rasters and regenerable caches out of Git. Pin hashes and provenance in `registry/`.
- Run the full local check set before any PR: `python -m pytest -q`, `python -m ruff check .`,
  `python scripts/check_metric.py`, `python scripts/verify_current_run.py --restore-small-inputs`,
  `python scripts/collect_evidence.py`, `python scripts/build_site.py`, `python scripts/check_site.py`.
  The verifier re-reads TIFF/ZIP bytes and reproduces pooled DTI/CI and denial gates without a human inspector.
  `scripts/recheck_magrest.py` repeats only the original nine-download-tree comparison and requires the ignored `.cache/magrest/responses.npy`; it does not test the broad 695-raster registry. On a clean checkout that cache is unavailable and must not be recreated after the registered STOP. `scripts/verify_current_run.py --restore-small-inputs` instead re-derives the served raster's literal overlap STOP against the pinned registered counterexample.
  Update `registry/review_passes.json` with what each pass actually found.
- Regenerate the site from the registers; never hand-edit `docs/*.html`. If a number on the site is wrong, fix the
  artifact or the generator, not the HTML.
- Do not claim a live leaderboard score, organizer acceptance, PR, merge, or deployment without a verifiable receipt/status.

## Amendment 2026-10-26 (selector session arena/5b378be2)

Owner-directed rescope IR-U-02 (see `knowledge/2026-10-26_h31u_preregistration.md`): uniqueness for
upload choice is judged against discrete peer submissions (9 focus sites + local downloads, twins
deduplicated), while the literal 695-raster reading is still computed and disclosed on every card
(it fails for any nonempty raster: the spacing-5 lattice covers 99.87% of the footprint within
3 px). `registry/selector_decision_20261026.json` records the only upload-cleared file (H31-T;
alternates H31-J/H31-M). Lane run cards keep their original `slot_approved=false` verdicts. If a
future owner instruction restores the literal reading, all promotions revert to STOP. Nothing else
in the rules above is relaxed: no DrivenData contact, no unlabelled numbers, fail-closed gates.

## Amendment 2026-10-26 (session arena/9883b598) — current protocol

The current owner prompt restores the literal any-registry check before placement AND on final dots.
This supersedes IR-U-02 for current permissions. No current file is approved. Do not run the historical
selector or choose a slot. Read `knowledge/2026-10-26_protocol_review_9883b598.md` and
`evidence/review_9883b598/run_card.json`. Run `python scripts/verify_protocol_review.py` after restoring
small inputs. The lattice gives a counting bound for the stated budget, NOT every nonempty raster.
Preserve historic receipts; do not present cited holdouts as freshly reproduced. A method paragraph
is absent, so no new scientific lane was assigned in this review.

## Amendment 2026-10-26 (H31-YR/H31-Z session arena/579233d5, merged after the reviews above)

Two preregistered regime-split lanes ran in parallel under IR-U-02-era semantics; both are research-only
negatives under the current release STOP — do not refit or slot them: **H31-YR** (ROUTE blend; SGMC
0.1312 but 92.4% dots within 3 px of H31-X) and **H31-Z** (SPLIT50 quota; discrete-unique but SGMC
0.0749 < H33). Measured conclusion: potential-field corroboration helps in the 3–9° transition band;
forcing flat-piedmont quotas starves discovery. Lane-id collision rule: two parallel sessions
self-assigned "H31-Y" (KIN-PIED vs regime-split) — before self-assigning any lane id, fetch
origin/main and check for collisions; regime-split artifacts live under `*_regimesplit` paths.
IR-U-03 (chronological duplicate priority in the disabled historical selector) is recorded in
`registry/selector_decision_20261026_regimesplit_579233d5.json` as research ranking evidence only.
Tooling rule: never edit the same file from parallel tool calls in one block (edits raced twice in
that session; verify with `git diff` before launching processes).
