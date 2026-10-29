# Active owner brief — 29 October 2026

This is a structured restatement of the active request and standing constraints for branch `arena/9f242e65-gemsdoe31`. The Arena request itself remains the source of truth; this file is maintained so later sessions do not lose scope or treat historical banners as current.

## Objective and requested comparison

- Maximize the probability of winning the DOE GEMS competition and own the outcome. Research performance, submission permission, and organizer-confirmed performance are separate.
- Compare the requested sites GEMSDOE24, GEMSDOE25, GEMSDOE27, GEMSDOE28, GEMSDOE30, GEMSDOE31, GEMSDOE32, GEMSDOE33 and GEMSDOE36.
- Maintain a clear per-site executive table with the pinned file to inspect/download, evidence-qualified reported score, whether the artifact is unique, and a new-file score estimate only if a calibrated estimate exists.
- Explain the reported GEMSDOE32 H33-2-B2 value of 0.2778, while keeping private-truth causation explicitly labelled as inference.
- Propose 3–5 distinct, ranked geological hypotheses. Rank expected DTI benefit and implementation cost qualitatively unless measured data support numerical estimates. Name a non-fault mimic and identify source/access uncertainty.
- Validate any explicitly authorized candidate on spatially blocked holdout before a slot is considered. Automatically validate GeoTIFFs; do not delegate scientific or format validation to a human inspector.
- Keep the submission guide, README charter, evidence-qualified project feed, source links for manual review, and three review passes current. Open/merge a PR if permitted, and report only verifiable GitHub status.

## Evidence and score language

- Distinguish `OFFICIAL`, `OWNER-MIRROR`, `COMPUTED`, `INFERENCE`, `HOLDOUT-DTI` and `USER-REPORTED` evidence.
- The nine historical values are user-reported; no organizer receipt currently ties them to exact bytes. The user-supplied 0.3195 and 0.4413 leaderboard anchors conflict and remain unverified.
- Never present a holdout result, proxy, projection, or user-supplied value as a competition score. A score becomes `ORGANIZER-CONFIRMED` only with an exact submission-page receipt.
- A new-file leaderboard estimate is unavailable without a calibrated, validated cross-family model. Keep it null rather than inventing a number.

## Current execution gate

The current prompt supplies **no single assigned method paragraph**. Do not invent a lane, fit a model, build a feature cache, create another TIFF, select a slot, or upload. The production feature stack is absent. The canonical `registry/release_status.json` is negative and `ok_to_submit=false`.

The user's literal parallel-run protocol is binding before placement and after final placement: if any registered raster has absolute rank correlation greater than 0.90 or more than 70% of candidate dots within 3 px, STOP. Do not evade STOP by changing density. One valid hash-pinned counterexample is sufficient to stop; say explicitly when a registry scan is not exhaustive.

## Protocol for a later explicitly authorized experiment

- Reuse pinned shared `vendor/gems57` feature cache, `evaluate_holdout.py` and `submission_writer.py` unchanged; do not fork shared tools.
- Hide whole fault segments with a buffer. Derive catalogue features only from visible faults, and mask visible faults pixel-exactly.
- Use pooled DTI with alpha 0.2, beta 0.8, a 300 m triangular kernel. Test each feature alone; AUC above 0.90 is leakage until explained.
- Label metrics `HOLDOUT-DTI`; include evaluator version, withheld-positive count and 95% CI. Never imply a holdout is an organizer score.
- End a run with a JSON card containing hypothesis, mechanism, named non-fault mimic, holdout/CI, surface and final correlation/overlap, raster SHA-256, validator, name/note and promote/negative verdict.
- Stop at three experiments or two hours. Do not choose a weekly slot. Promotion is a separate selector step.

## Integrity, access and Git constraints

- Unique TIFF means a genuinely new, audited raster, not a renamed/copied prior file. Research download permission is not permission to submit.
- Validate one-band float32 GeoTIFFs against the pinned grid and require finite footprint values in `[0,1]`; provide an all-finite version where appropriate to avoid the reported range error. Submission name and note must be unique, with note no longer than 140 characters.
- Do not scrape or poll DrivenData, access its pages automatically, upload, or contact the organizer. Keep static links for manual review only. Do not request credentials.
- Stay on `arena/9f242e65-gemsdoe31`; never switch, create or push another branch. Do not claim a PR, merge, or deployment without a verifiable receipt.

## Current findings to preserve

- Existing H-STEO TIFF: exact format checks pass against the owner-mirror template, but the final 9,140 dots have 9,135 (99.945%) within 3 px of one hash-pinned registered lattice. The reconstructed pre-placement surface has 99.965% within 3 px. It fails the literal overlap STOP despite near-zero rank correlations; it is not unique or submit-ready.
- Existing CSDU TIFF: its archived generator used a synthetic ellipse footprint and an all-zero labels raster. On the actual pinned template, 1,899 of 4,000 dots are outside the real footprint; its NaN twin has 2,610,312 missing values inside the real footprint. It is not a valid competition-grid submission.
- Neither archived artifact has a HOLDOUT-DTI result or a defensible new-file leaderboard estimate. No TIFF, experiment, submission slot or DrivenData contact is authorized by this review.
- Full report: `knowledge/repo_review_2026-10-29_arena-9f242e65.md`; desk hypotheses: `knowledge/hypotheses_2026-10-29_arena-9f242e65.md`; machine card: `evidence/review_9f242e65/run_card.json`.

## Manual-review links

- Competition problem: <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/>
- Rules PDF: <https://docs.nlr.gov/docs/fy26osti/96647.pdf>
- Reference solution: <https://github.com/drivendataorg/gems-prize-reference-solution>
- INGENIOUS: <https://doi.org/10.15121/1881483>
- World Stress Map 2025: <https://dataservices.gfz-potsdam.de/wsm/showshort.php?id=a23de1c9-1f73-11f0-914a-f12b0080820d>
- NBMG geothermal descriptions: <https://nbmg.unr.edu/geothermal/sitedescriptions.html>
- SMU heat-flow record: <http://search.geothermaldata.org/dataset/115609c8-6f52-49fe-a0af-9d379d516340>
- USGS ComCat API: <https://earthquake.usgs.gov/fdsnws/event/1/>
- Static leaderboard link (manual only): <https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/>

No official page or leaderboard was freshly fetched in this session. The source links are for manual review; they do not prove current availability, score, quota or organizer acceptance.
