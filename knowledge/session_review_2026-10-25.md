> **Historical earlier same-date H31/source audit.** Current data/output state is superseded by [MAGREST review](session_review_2026-10-25_magrest.md) and [latest status](current_status_2026-10-25.md). The data were subsequently restored and a new negative research TIFF generated; do not reuse the old missing-data statement as present status.

# Session review — 2026-10-25

**Decision: NEGATIVE / STOP. No new submission TIFF was generated.** The requested priority artifact is blocked twice: the H33-2-B2 geometry from the referenced GEMSDOE32 owner mirror fails this repository's pre-placement duplicate canary against the existing H27-4 registry raster, and this checkout contains none of the competition/runtime inputs needed to validate a different geological hypothesis. No weekly slot is recommended or used.

## Evidence classes and source boundary

- **USER-REPORTED:** the prompt attributes a competition score of `0.2778` to `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros`. No DrivenData receipt linking that number to those exact bytes is in this checkout or in the inspected GEMSDOE32 archive. The archive's own submission metadata marks the artifact `UNSCORED`; it records a projected/modelled value, which is not an organizer score. Therefore the `0.2778` claim remains unverified and is not repeated as a confirmed score.
- **OWNER-MIRROR:** GEMSDOE32 main at commit [`012e17b2a115c3c0d5e7885bea625bf9657c99fc`](https://github.com/buffedlizard55-lab/GEMSDOE32/commit/012e17b2a115c3c0d5e7885bea625bf9657c99fc), files [`README.md`](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/012e17b2a115c3c0d5e7885bea625bf9657c99fc/README.md), [`h33_candidates.json`](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/012e17b2a115c3c0d5e7885bea625bf9657c99fc/evidence/h33_candidates.json), [`h33_validation.json`](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/012e17b2a115c3c0d5e7885bea625bf9657c99fc/evidence/h33_validation.json), and [`submission_build.json`](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/012e17b2a115c3c0d5e7885bea625bf9657c99fc/registry/submission_build.json). These are owner-maintained records, not organizer evidence.
- **COMPUTED / DUPLICATE-CANARY:** H33-2-B2 GeoTIFF bytes were read from that public owner repository solely for prior-art learning and overlap auditing. The TIFF itself was not copied into this repository or offered for submission. Pixel overlap and correlation were computed locally against the already registered GEMSDOE31 rasters.
- **OFFICIAL source references:** competition metric/submission rules are in [`registry/sources.json`](../registry/sources.json), including the official [problem page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) and [rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf). The DrivenData data tab remains login-gated according to the recorded access audit. No leaderboard, private submission page, or DrivenData service was contacted in this review.

## What the GEMSDOE32 artifact does, and why the apparent result is not causal proof

The owner-mirror build describes H33-2-B2 as its H27-4 / D2.8-style sparse dot emission after deleting all dots within a two-cell catalogue-flank distance (about 200 m at the 100 m grid). It is therefore a catalogue-distance *removal rule*, not an independent new geophysical detector. The owner's evidence reports improved internal fold-surrogate ordering after this removal, but also says the artifact had not received an organizer score at the archived repository revision. Its apparent score change, if later submitted as the user reports, cannot establish that the deletion rule caused the score without an exact-byte receipt and same-protocol controls.

**Holdout-protocol irregularity:** in the inspected owner code, `scripts/run_h33_validation.py` reads the full catalogue labels and calls `compute_h33_2_flank_sweep(base, labels, d_cat, ...)`; `compute_h33_2_flank_sweep` builds the pruning distance from those labels. The generic holdout then evaluates the resulting fixed candidate raster against hidden catalogue components. The checked code path does not rebuild this catalogue-distance removal using only each fold's visible faults. That violates this project's preregistered hide-and-recover rule for catalogue-derived processing. Because the effect on the held-out pixels could be conservative or optimistic depending on local geometry, do not call it an unbiased holdout or transfer its result to our evaluator. This is an owner-code audit, not a claim about the organizer's private scorer.

A plausible metric-level explanation for why such sparse emissions can perform well is that the official DTI penalizes false-positive mass with alpha 0.2 and false-negative truth with beta 0.8, using a 300 m triangular kernel. Isolated dots can cover spatially separated truth efficiently while limiting false-positive mass; removing redundant near-known-fault dots may improve precision if those pixels are masked or low value. This is a **mechanistic inference**, not evidence that the H33 score is verified, that the deleted collar is optimal, or that a similar rule will transfer to hidden faults. The site’s label `zeros` identifies an outside-footprint encoding convention, not a geological mechanism; no score advantage from zeros versus NaN was established here.

## Pre-placement duplicate canary — stop condition met

Compared the archived H33-2-B2 `-zeros.tif` values to all distinct registered GEMSDOE31 submission rasters over the finite footprint of the local H27-4 template. These are similarity diagnostics, not holdout DTIs or competition scores.

| Registered raster | Spearman rank correlation (in-footprint raster values) | H33-2-B2 positive cells within 3 pixels of registered positive cells | Exact positive-cell intersection |
|---|---:|---:|---:|
| `gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-allfinite.tif` | 0.967587 | 100.0000% | 37,654 |
| `gemsdoe31-reference-d28-offcat-44090-20261004-nan.tif` | 0.923555 | 100.0000% | 37,654 |
| `gemsdoe31-add-arm-d28-20261004-8acb75e1-nan.tif` | 0.823719 | 100.0000% | 37,654 |
| `gemsdoe31-union-b-p060-20261004-8acb75e1-nan.tif` | 0.591632 | 100.0000% | 37,654 |

The comparison crosses outside-footprint conventions only after masking to the finite H27-4 footprint. The H33 file has 37,654 positive cells; every one is already a positive cell in the local H27-4 raster. It exceeds both registered duplicate limits (>0.90 rank correlation and >70% within-three-pixel overlap), so **this method/artifact is logged as a duplicate and rejected. Stop; do not prune, rename, rewrite, or submit it as a new GEMSDOE31 candidate.** The computed correlation depends on the binary-valued file and in-footprint pixel domain; it is a duplicate screen, not geological validation.

SHA-256 of the inspected owner-mirror H33-2-B2 `-zeros.tif`: `c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9`. This hash identifies only the bytes in the inspected public GitHub archive; it does not authenticate a competition upload or receipt.

**Format irregularity:** the inspected `-zeros.tif` has a finite zero at every cell outside the locally recorded footprint, no NaNs, and no nodata tag. The official problem page cited in `registry/sources.json` specifies null/NaN outside the bounds. This owner-mirror file therefore does not follow the recorded official outside-footprint convention. The sample template is absent from this workspace, so an exact-format revalidation could not be performed here; the owner’s own byte receipt is not organizer acceptance. This is logged as `IR-31-H33-ZERO-OUTSIDE`.

## Candidate hypotheses to consider after runtime restoration

These are **desk-only, unfit hypotheses** already documented as prior-art boundaries in the GEMSDOE31 research register. They are not new results or approved slot ideas. Rank is value-for-effort, not a numerical score forecast. All candidate-derived channels must pass a feature-alone leakage canary and the exact holdout procedure before any emission is made.

| Rank | Hypothesis and layer(s) | Physical signature sought | Why it may reveal an unmapped fault | Difference from prior implementations here | Data/access status and cost |
|---:|---|---|---|---|---|
| 1 | Scarp-degradation age-bank matched filter; 1 m bare-earth DEM tiles referenced through the competition's `1m_DEM_links.csv` | Cross-strike error-function profiles spanning several diffusion/degradation widths; score profile-shape agreement, not peak step amplitude | Old, degraded scarps may be broad and low amplitude and thus missed by conventional mapping or single-threshold scarp detectors | Existing LiDAR channels emphasize step, Laplacian, relief, and coherence; this tests a multi-width profile-shape bank rather than a single scarp amplitude/dipole | Competition data tab is officially login-gated in this environment; DEM links and runtime/cache are absent here. **Not currently viable.** Moderate processing after authorized data restoration. Official review: [competition data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) and [USGS 3DEP](https://www.usgs.gov/3d-elevation-program). |
| 2 | Quaternary-vent-aligned fault search; INGENIOUS/USGS mapped vents or volcanic units plus DEM, magnetic, and LiDAR structural lineaments | Angular/oriented lineament continuity radiating from or connecting young vents, distinct from isotropic vent-distance decay | Young volcanic centers may occupy active structural corridors; a connected lineament may expose a fault not represented as a mapped fault trace | Existing project features use vent distance as a habitat/context covariate, not an oriented lineament-arrangement or emission mechanism | The prior register identifies the official INGENIOUS/GDR source family, but the raster binaries are not present in this checkout. Exact GEMS-area coverage and license must be confirmed from source metadata before testing. Low-to-moderate effort after restoration; **not currently viable**. |
| 3 | Depth-resolved conductivity-boundary persistence; GDR 1391 / USGS Great Basin electrical-conductance maps at multiple depths | Cross-depth persistence of coherent conductivity-gradient orientation, rather than surface conductivity or conductive-base depth alone | A concealed structure or fluid pathway can persist at depth without a mapped surface trace | Existing competition inputs provide surface conductivity and depth-to-base summaries; a multi-depth continuity transform is absent from the reviewed implementation | [Official GDR submission 1391](https://gdr.openei.org/submissions/1391) is identified in the preregistration; exact raster downloads, resolution, study-area overlap, and bytes are not present/verified in this checkout. Moderate-to-high effort; **not currently viable**. |
| 4 | Raw LiDAR return-attribute structure; official USGS 3DEP point-cloud (LPC/LAZ) returns | Ground/non-ground return density, intensity quantiles, and cross-strike texture discontinuity aggregated to the model grid | Material juxtaposition, damage-zone cover, or roughness may reveal subtle strands where a bare-earth elevation edge is weak | Existing LiDAR predictors are elevation-derived; raw return attributes are a different measurement family | Prior access audit found an official in-footprint catalogue product record but the exact LAZ binary download failed and its metadata endpoint was under maintenance; no return attributes or whole-footprint coverage have been confirmed. [USGS 3DEP](https://www.usgs.gov/3d-elevation-program). Moderate-to-high effort; **not currently viable**. |

**Selected next experiment:** none. The first-ranked hypothesis is only a conditional desk priority. It cannot be fitted in this workspace without the competition’s authorized DEM data and pinned feature/cache stack. No holdout positives, confidence interval, or feature-alone AUC exist for these candidates here. Do not write an expected DTI as though it were a result.

## Reproducibility and immediate blockers

- Current worktree initially had no `data/` directory. Re-running `.venv/bin/python scripts/prepare_data.py --verify-only` found all 11 manifest entries absent and reported `all_hashes_match: false`. The command rewrote `evidence/data_preparation.json`; that generated failure snapshot was restored to its original committed version so it cannot overwrite the repository’s historical successful preparation receipt. The absence is recorded here as a current workspace fact.
- The cached OOF probability files under `evidence/oof/` exist but are not the feature stack and cannot produce isolated feature rasters or train a new holdout model. `run_union.py` evaluates old OOF emissions against proxy truth; it is not the hide-whole-segments experiment requested for a new hypothesis.
- No HOLDOUT-DTI was produced in this session. There are no withheld positives, no evaluator-version receipt for a new arm, and no valid 95% interval to report.
- The exact competition sample template, labels, training features, prepared feature stack, reference checkout, and holdout runtime must be restored from the hash-pinned and authorized sources before experimentation. Keep the official data tab access limitation explicit; no credentials were used.
- No TIFF was generated. Hence there is no candidate TIFF validator receipt, submission name, or portal note. Existing downloadable files remain historical/reference or research-only; none becomes approved through this review.

## Review passes

1. **Pass 1 — implement and verify:** inspected the recurring README/preregistration/status, fetched the public GEMSDOE32 GitHub repository archive at the pinned commit, read its H33 candidate/evidence and submission receipt metadata, calculated the duplicate screen against local registered rasters, and reran tests/metric. The H33 geometry failed the project duplicate threshold; there is no local training/runtime input to validate another candidate.
2. **Pass 2 — adversarial review:** separated the prompt's score claim from the owner-mirror `UNSCORED` status; confirmed no owner-repository submission receipt is an organizer receipt; checked outside-footprint handling and exact dot subset identity; avoided copying the reference TIFF. Found the H31 runner's hard-coded prior-session branch ID would reject the current active Arena branch and fixed it to require an Arena branch, with optional exact pinning via `GEMSDOE31_BRANCH`.
3. **Pass 3 — charter cross-check:** no submission slot was spent, no unvalidated/duplicate TIFF was made, no live DrivenData access occurred, and the holdout/CI remain explicitly null. Full tests, lint, metric, generated site and artifact register checks are recorded in the session's final review record.

## Machine-readable run card

```json
{
  "hypothesis": "No candidate promoted; H33-2-B2 catalogue-flank deletion is prior art and fails the duplicate gate.",
  "mechanism": "The owner-mirror method deletes base-emission cells within 200 m of the public fault catalogue; similarity screening shows it reproduces a strict subset of the local H27-4 raster.",
  "named_non_fault_mimic": "Lithologic contacts, drainage incision, roads, and erosion can create lineaments or near-catalogue spatial associations without representing a fault; this is a rationale for future feature tests, not evidence against the already-pruned pixels.",
  "holdout_dti": null,
  "holdout_dti_ci95": null,
  "holdout_evaluator_version": null,
  "withheld_positive_count": null,
  "correlation_overlap_vs_registry": {
    "reference": "GEMSDOE31 H27-4 existing raster; within its finite footprint",
    "spearman_rho": 0.967587,
    "candidate_dots_within_3px": 1.0,
    "exact_intersection_cells": 37654,
    "duplicate_threshold_exceeded": true
  },
  "raster_sha256": "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9",
  "validator_output": {
    "no_nan_inside_footprint": null,
    "values_in_0_1": null,
    "crs_shape_transform_match": null,
    "reason": "No new candidate raster was written. The inspected prior-art TIFF is not treated as this project's candidate or passed through its official-template validator."
  },
  "submission_name": null,
  "submission_note": null,
  "verdict": "negative"
}
```
