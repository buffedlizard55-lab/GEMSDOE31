# GEMSDOE31 agent instructions

Before changing this repository, read the entire `README.md`, the active H31 preregistration in `knowledge/`, and the current outcome/status record. Keep the README as the recurring project charter; update the status record at the end of substantive work.

## Scientific and evidence rules

- Separate **OFFICIAL**, **OWNER-MIRROR**, **COMPUTED**, and **INFERENCE** claims. A hash proves byte identity to a mirror, not organizer authenticity; owner-reported leaderboard scores are not verified without an official receipt.
- Do not scrape, poll, automatically access, or manually monitor/copy DrivenData leaderboard material without prior written permission. A static official leaderboard link is permitted. Never submit/upload automatically.
- Preregister candidate physics, model, holdout, metric, buffer, seeds, and promotion gates before any fit. Do not use a weekly slot unless the candidate beats the same-run incumbent on an empirically buffered spatial holdout and passes fresh confirmation. A positive screen alone is insufficient.
- Derive the spatial collar from out-of-fold residual semivariograms on known fault traces. Never substitute an arbitrary pixel buffer or report the temporary pilot collar as an empirical range.
- Do not create a new candidate TIFF from a failed/unconfirmed experiment. Keep the legacy D2.8 reference file explicitly labeled as an owner-mirror benchmark, not a new or slot-approved candidate.
- Validate a submission GeoTIFF against the sample template: EPSG:32611, exact shape/transform, one float32 band, all footprint values finite in `[0,1]`, and NaN outside the footprint. No silent clipping or zero-filled outside area.

## Execution / Git rules

- Work only on `arena/01a104a9-gemsdoe31`; do not switch branches.
- Keep large input rasters and regenerable caches out of Git. Pin hashes and provenance in `registry/`.
- Run the test/lint suite, review every new claim and source link, and update `registry/review_passes.json` before PR submission.
- Do not claim a live leaderboard score, organizer acceptance, PR, merge, or deployment without a verifiable receipt/status.
