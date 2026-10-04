# GEMSDOE31 current status — 2026-10-04 (pre-fit snapshot)

**Decision:** no new H31 TIFF, no weekly slot, and no official score are authorized or verified. The home-page download is explicitly a legacy reference raster, not a current submission candidate.

## Completed

- Preserved the full active project scope as a recurring README charter; added project-specific scientific/Git guardrails in `AGENTS.md`.
- Ranked four new geological hypotheses and froze H31-A's features, model, folds, draws, metric, variogram, buffer rule, and promotion gates before any H31 model fit. The H31-B source-access update is documented separately and does not change H31-A.
- Implemented first-pass H31-A feature construction, same-run paired analysis, residual variogram fitting/bootstrap/buffer selection, strict GeoTIFF validation, mirror/runtime verification, and pilot/screen/confirmation runner. Screen buffer retries are capped at three and must chain from the immediately prior passing-metric, buffer-unstable screen result.
- Re-ran checks after cleanup: **22 tests passed** with no warnings; `ruff check .`: **all checks passed**; Python `compileall`, all seven JSON documents, static HTML local-link audit, and `git diff --check` also passed.
- Ran a no-model-fit production-context smoke against GEMSDOE25 commit `c185edd8b09e19846cf34c16050e6cf891ecc2d0`: all **7/7** pinned raw inputs and **6/6** derived caches verified; 3730×3292 footprint and H31 feature columns built; four-fold holdout collar is passed as the temporary 5 px pilot setting. This tests context construction, not a model or variogram.
- Validated the legacy 44,090-positive-pixel D2.8 reference against the pinned owner-mirror sample TIFF: one float32 band, EPSG:32611, exact 3730×3292 grid/transform/bounds, finite footprint values in `[0,1]`, no infinities, and NaNs exactly outside the mirrored footprint. Receipt: `docs/downloads/gemsdoe31-reference-d28-offcat-44090-20261004-format-check.json`; `organizer_acceptance_verified=false`.
- Investigated the request's D2.8 `0.2600` claim. It is user-reported but absent from the pinned owner-mirror D2.8 score record, which says unscored. A local conditional emission model brackets a plausible range but is not a leaderboard result; see `knowledge/prior_submission_audit.md`.
- Queried the official USGS TNM Access API. A LAZ tile record is located inside the owner-mirror footprint at 49/49 sampled bbox locations; the exact binary download failed with `SSL_ERROR_SYSCALL`, and the XML endpoint was under maintenance. No LAZ header or point-return attributes were checked; H31-B remains blocked.

## Not done / evidence still unavailable

- The full `scripts/run_h31.py` pilot has **not** run. No production variogram range, data-derived final buffer, H31 model result, screen, confirmation, current-incumbent win, or slot decision exists.
- No new candidate GeoTIFF has been generated. The legacy reference is not H31, not slot-approved, and its score is not organizer-verified.
- The original organizer sample/template has not been independently obtained; local validation used the SHA-pinned owner-mirror copy.
- Full-grid LiDAR/DEM tile coverage, raw LAZ attributes, and the GDR 1501 full-footprint overlap remain unchecked.
- GitHub Pages has not been deployed; PR/merge have not yet occurred.

## Next sequence

1. Finish code/source review and commit the frozen preregistered implementation on `arena/01a104a9-gemsdoe31` so the fail-closed runner can execute from a clean worktree.
2. Run only pilot draw 10 with the temporary 500 m collar. If residual variograms are unstable or do not support a range, stop with buffer unknown; do not invent a final distance.
3. If the pilot yields a stable buffer, run registered screen draws 11–12 using at least the data-derived upper range. Run fresh confirmation draws 13–14 only if the screen passes. Compare against the required same-run incumbent before considering any artifact or weekly slot.
4. Complete source, code, and full-charter review passes; update this file and `registry/review_passes.json`; push only the fixed Arena branch; open and merge a PR only if checks and GitHub permissions permit.

## Evidence labels

- **OFFICIAL:** contest/source pages and rules identified in `registry/sources.json`; official score/acceptance remains unverified.
- **OWNER-MIRROR:** inputs/caches and D2.8 reference pinned to a public owner sibling; hashes do not authenticate organizer provenance.
- **COMPUTED:** tests, local TIFF validation, feature/context smoke, hashes, and any future local proxy outcomes.
- **USER-REPORTED:** the D2.8 `0.2600` score claim in the request; no receipt.
- **INFERENCE:** geological rationales and conditional score mechanisms; not hidden-label findings.
