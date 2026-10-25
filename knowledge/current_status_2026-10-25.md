# Current status — 2026-10-25

Read the [project charter](../README.md), [agent rules](../AGENTS.md), [active preregistration](2026-10-04_h31_hypotheses_preregistration.md), [latest review](session_review_2026-10-25.md), and `registry/review_passes.json` before further experimentation.

## Decision

**Negative / stop. No unique submission GeoTIFF was generated; no weekly slot was touched.** The GEMSDOE32 H33-2-B2 prior-art TIFF triggers the duplicate canary against the local H27-4 raster, and this checkout has no local `data/` inputs or prepared feature stack from which a different candidate can be fit and validated.

## New findings

- The public GEMSDOE32 repository archive was inspected at commit `012e17b2a115c3c0d5e7885bea625bf9657c99fc`. Its H33-2-B2 artifact is described as a catalogue-flank deletion on the H27-4-style dot set; this is prior art, not a distinct detection mechanism. Its archived score metadata says `UNSCORED`. The user-provided `0.2778` claim remains USER-REPORTED and has no organizer receipt tied to exact bytes in the inspected archive.
- Locally computed duplicate-canary diagnostics against the H27-4 `allfinite` registry raster: Spearman rank correlation `0.967587`, H33 positives within three pixels `100.0000%`, exact shared positive cells `37,654`. The method is recorded as `IR-31-H33-2-B2-DUPLICATE` and rejected. These are duplicate diagnostics, not DTI scores.
- The inspected GEMSDOE32 H33 holdout path appears to construct its catalogue-flank deletion using full labels before evaluating a fixed mask against hidden components. That is not fold-visible catalogue processing under this project's protocol; an irregularity is registered and the owner holdout is not accepted as promotion evidence.
- The model/holdout remains blocked. `data/` does not exist in this checkout, the 11 pinned manifest inputs are absent, and cached OOF probabilities are insufficient for feature-alone leakage canaries or a new hide-and-recover model fit.
- Four distinct, unfit desk hypotheses and their official-source/access limits are documented in the session audit. The first-ranked scarp-degradation profile bank is conditional only; its input coverage is inaccessible here, so it is not marked viable.
- The H31 runner previously hard-coded a prior Arena session branch ID. It now accepts an `arena/*` session branch by default and supports an exact `GEMSDOE31_BRANCH` override. Tests cover both cases.
- The generated home page and executive summary now state prominently that currently downloadable rasters are reference/research-only and not approved for upload. No submission name or portal note is reserved.

## Verification performed

- `.venv/bin/python -m pytest -q`: **33 passed** after all code/UI changes.
- `.venv/bin/python -m ruff check .`: passed after all code changes; `.venv/bin/python -m compileall -q src scripts tests` also passed.
- `.venv/bin/python scripts/check_metric.py`: maximum absolute difference from the brute-force metric transcription `4.441e-16`; exact cases and 300 m kernel geometry verified.
- `.venv/bin/python scripts/prepare_data.py --verify-only`: all 11 manifest inputs absent, `all_hashes_match=false`. Its generated failure report was restored to the committed historical evidence receipt to avoid replacing prior successful-run evidence with an ephemeral environment result; present absence is captured in the audit.
- `scripts/collect_evidence.py`, `scripts/build_site.py`, and `scripts/check_site.py` passed; 20 pages and 255 local links checked. The home page and executive summary now explicitly label downloads as not approved for upload.
- No new holdout, AUC/leakage canary, DTI/CI, TIFF validator receipt, or organizer-confirmed score exists for this session.

## Outstanding gates

1. Restore permitted, hash-verified competition/runtime rasters and the required cached feature stack, including the authorized sample submission template; document exact provenance.
2. Preregister a genuinely distinct geological candidate, then test each feature alone for leakage, withhold whole fault segments plus empirical spatial buffer, and evaluate pooled DTI with alpha 0.2 / beta 0.8 / 300 m triangular kernel.
3. Require a comparable same-run incumbent, fresh confirmation, confidence interval, duplicate checks both before placement and on the final dots, and exact GeoTIFF format audit before any selector/promotion action.
4. Keep organizer score claims separate from user/owner reports; do not access or automate DrivenData pages absent permission.
5. Reimplement the absent four-arm trainer so previously reported OOF and union measurements can be independently regenerated.
