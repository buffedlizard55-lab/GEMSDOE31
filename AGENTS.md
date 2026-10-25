# GEMSDOE31 agent instructions

Before changing this repository, read the entire `README.md`, `knowledge/2026-10-25_transfer_preregistration.md`, the historical H31 preregistration, and `knowledge/current_status_2026-10-25.md` plus `knowledge/2026-10-25_next_session.md`. Keep the README as the recurring project charter; update the status record at the end of substantive work.

## Scientific and evidence rules

- Separate **OFFICIAL**, **OWNER-MIRROR**, **COMPUTED**, **INFERENCE** and **USER-REPORTED** claims. A hash proves byte identity to a mirror, not organizer authenticity; owner-reported leaderboard scores are not verified without an official receipt.
- Do not scrape, poll, automatically access, or manually monitor/copy DrivenData leaderboard material without prior written permission. A static official leaderboard link is permitted. Never submit/upload automatically.
- Preregister candidate physics, model, holdout, metric, buffer, seeds, and promotion gates before any fit. Do not use a weekly slot unless the candidate beats the same-run incumbent on an empirically buffered spatial holdout and passes fresh confirmation. A positive screen alone is insufficient.
- For a trained-model comparison, derive the spatial collar from fold-fair residual semivariograms on known fault traces. The closed no-fit TGJ31 audit explicitly inherited 213 px from historical residual analysis; never present it as a newly estimated TGJ31 range or report a temporary pilot collar as empirical.
- The 2026-10-25 request requires a newly computed TIFF even for a negative result. It may be published ONLY as an audit artifact with `safe_to_submit=false`; do not copy a previous prediction, label it slot-approved, or resume scientific work after a literal duplicate gate fires. Keep all legacy files historical/reference-only.
- Active TGJ31 output uses the unchanged shared writer: one float32 band, exact template CRS/shape/transform,
  finite `[0,1]` everywhere, explicit zeros outside the finite template footprint, `nodata=None`.
  Re-read the actual TIFF and single-TIFF ZIP; reject invalid values before casting, never silently clip.
  Historical NaN-outside variants remain reference-only and are tested under their own convention.
- Main instrument is pooled hide-and-recover HOLDOUT-DTI with whole fault components, buffer and exact visible-pixel mask.
  Derive every catalogue feature from visible faults only; no SGMC predictor. Report the SGMC off-catalogue diagnostic
  separately, never as independent hidden truth. Neither proxy alone establishes organizer performance or authorizes a slot.
- Label new performance numbers HOLDOUT-DTI (evaluator version, withheld-positive count, 95% CI) or
  ORGANIZER-CONFIRMED (requires receipt). Preserve historical records as archival, not comparable new results.
- Never quote a proxy DTI as a competition score. Owner-reported scores carry the file's SHA-256 and the
  `USER-REPORTED` class; an organizer receipt is required before anything is reported as a score.

## Execution / Git rules

- Work only on the branch this session is attached to (`arena/94fc8374-gemsdoe31` at the time of writing);
  never switch, create or push another branch.
- Keep large input rasters and regenerable caches out of Git. Pin hashes and provenance in `registry/`.
- Run the full local check set before any PR: `python -m pytest -q`, `python -m ruff check .`,
  `python scripts/check_metric.py`, `python scripts/collect_evidence.py`, `python scripts/build_site.py`,
  `python scripts/verify_tgj31.py`, `python scripts/update_readme.py --check`, `python scripts/check_site.py`. Update `registry/review_passes.json` with what each pass actually found.
- Regenerate the site from the registers; never hand-edit `docs/*.html`. If a number on the site is wrong, fix the
  artifact or the generator, not the HTML.
- Do not claim a live leaderboard score, organizer acceptance, PR, merge, or deployment without a verifiable receipt/status.

## Closed current lane

TGJ31-v1 is negative and scientifically stopped. Do not alter its frozen preregistration, feature implementation or runner to improve a result. `scripts/verify_tgj31.py --rebuild-surface` is exact integrity reconstruction, not a new experiment. Resolve the universal literal-overlap blocker, lane assignment, organizer provenance and comparable-best reproduction before a new authorized preregistration.
