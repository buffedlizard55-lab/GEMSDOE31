# Repository review — 2026-10-25 (Arena branch review)

## Executive result

**No fresh experiment or new GeoTIFF was produced in this review.** The local checkout has no `data/` input directory or prepared feature stack; `scripts/prepare_data.py --verify-only` reports `all_hashes_match: false` for the 11-file manifest. Therefore a new candidate cannot be responsibly fitted, evaluated with the required hide-and-recover protocol, or emitted from this checkout. Existing H31-B TIFFs were not modified or re-labeled as newly generated work.

This review found and fixed one deterministic packaging/UI defect: the generated home page printed a blank SHA-256 for the primary submission ZIP although the ZIP existed. The evidence collector now hashes the archive and records its size; the site displays the hash and its link checker fails if it disappears. Tests also assert each registered ZIP digest and that each archive contains exactly one readable `.tif` member.

## Findings and limitations

1. **Missing local training inputs (blocking for new modeling).** `data/` and the prepared cache are absent. The manifest and historic evidence refer to owner mirrors; they do not establish organizer authenticity. No current feature-alone canary or new spatial holdout can be run without restoring and hash-checking the inputs first.
2. **Existing download artifacts versus a new submission.** The repository contains H31-B TIFFs from prior work, but this review did not create them. Their prior JSON receipts say they passed template checks; this checkout lacks the sample template/input rasters needed to independently repeat exact template-footprint comparison now. A standalone read of the H31-B primary file confirms one float32 band, EPSG:32611, shape 3730×3292, 100 m affine transform, values `{0,1}` across finite cells and NaN elsewhere; its SHA-256 remains `ff1b736337d53d9966248302b6cba0ffbd64bfcfe81a9d0695ef3364e6c53ebb`. This check is not organizer acceptance and does not revalidate its scientific gates.
3. **Submission selection remains separate.** `registry/submissions.json` intentionally has `slot_approved: false`; a locally valid file and a holdout proxy are not evidence of a competition score or organizer approval. Do not auto-upload or claim acceptance.
4. **GEMSDOE32 score provenance.** The `0.2778` claim remains `USER-REPORTED` in the records inspected; there is no organizer receipt in `registry/score_claims.json`. The documented annulus/pruning explanation is an inference supported by the mirrored raster comparisons, not proof of an organizer score.
5. **Parallel repository work must be reconciled.** On review, GitHub showed open PR #14, from a different Arena branch, whose description reports a separate broader registry/uniqueness audit and a no-submit outcome. It is not part of this checkout or this change. Do not infer its artifacts are merged, and do not silently combine its lane with this one. Before any future promotion, compare exact output support against the complete applicable registry and reconcile the findings with that PR's verified evidence. This review does not merge or push another branch.
6. **ZIP digest defect (fixed here).** `scripts/collect_evidence.py` previously copied the ZIP path from a receipt but omitted its digest and byte size. The generated home page therefore rendered an empty ZIP hash. Fixed by hashing the actual archive and storing `sha256_zip`/`bytes_zip`; a regression check now verifies the hash, byte count, archive integrity, and single-TIFF member constraint.

## Verified locally in this review

- Full unit suite: **46 passed**.
- Ruff: clean.
- Metric audit: maximum absolute difference against brute-force reference `4.441e-16` over 24 test grids; 29 kernel offsets in support.
- Site generation/check: 20 pages and 274 local links pass; primary ZIP hash is populated.
- H31-B primary TIFF byte digest and raster header/range/mask were inspected with Rasterio. The pre-existing receipt records 21/21 format checks; current check is not a replacement for missing template data.

## Next actions, in order

1. Reconcile the open parallel PR #14 against this branch's promotion/download language before claiming any existing file meets the complete fleet-wide uniqueness rule.
2. Restore the 11 manifested inputs from an approved, reachable source and verify every SHA-256; do not substitute the owner mirrors for official organizer provenance.
3. Read the active preregistration first, then run no more than its experiment/time budget. Test every candidate feature alone; fail closed above the AUC leakage threshold. Use whole-segment hide-and-recover, visible-only catalogue-derived features, exact masking, the empirically derived collar, pooled DTI, and uncertainty intervals.
4. Only after a candidate beats the same-run incumbent and fresh confirmation, compare continuous surface rank-correlation and final-dot overlap against the complete registry. Record any failed/duplicate result as a negative deliverable; do not use a weekly slot as a test.
5. Revalidate the exact final TIFF and its ZIP against the sample template; include the unique portal name and ≤140-character note. Keep any organizer receipt separate from proxy metrics.
6. Keep the public site honest about what is currently downloadable, format-valid, scientifically promoted, and organizer-confirmed. These are four distinct statuses.

## Sources and scope note

The task-provided official references remain in [`registry/sources.json`](../registry/sources.json), including the DrivenData problem/rules links, DOE GDR and USGS sources, and EPSG:32611. This review did not query the DrivenData data or submission endpoints, attempt an upload, or freshly verify changing external pages. It used local files/tests and GitHub PR metadata only.
