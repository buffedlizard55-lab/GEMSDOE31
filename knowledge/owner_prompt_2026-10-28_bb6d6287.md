# Owner prompt preserved 2026-10-28 — session arena/bb6d6287-gemsdoe31

Read this file and `README.md` at the start of work on this project. The text below is the operative charter for this session, condensed from the repeated owner message without dropping a rule. It is not an organizer document.

## Binding protocol

1. Lane. Stay inside one method. If rank-correlation with any registry raster exceeds 0.90, or more than 70% of dots fall within 3 px of one registry raster’s dots, log a duplicate and stop. Check the surface before placement and the final dots.
2. Reuse the template cache, `evaluate_holdout.py`, and `submission_writer.py`. Holdout hides whole fault segments with a buffer. Catalogue features come only from visible faults. Visible faults are masked pixel-exactly. Score pooled DTI, alpha 0.2, beta 0.8, 300 m triangular kernel.
3. Label every number HOLDOUT-DTI (evaluator, withheld positives, 95% CI) or ORGANIZER-CONFIRMED. A projection is not a score.
4. Leakage canary: test each feature alone. AUC above 0.90 is leakage until proven otherwise.
5. End with one JSON run card: hypothesis, mechanism, named non-fault mimic, holdout DTI and CI, correlation/overlap versus the registry, raster SHA-256, validator output, submission name and note of at most 140 characters, verdict promote or negative.
6. Stop after 3 experiments or 2 hours. Do not pick a weekly slot. Promotion is a separate selector step.

## Delivery rules

- Generate a unique TIFF. Do not copy a previous submission except for learning.
- Make it obvious whether the file may be downloaded and submitted. A format pass is not permission.
- Predicted values must be in [0, 1]. Provide an all-finite file so a portal does not reject NaN.
- Give a unique name and a note of at most 140 characters.
- Executive summary first: file, estimate, uniqueness versus GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, and 36.
- Do not treat inspection-only pages as a substitute for an automated validator.
- Do not invent organizer scores. 0.2778, 0.3195, and 0.4413 in the prompt are unverified and conflict.
- Official links for manual review: competition page, data page, reference solution, GeoDAWN, GDR 1391, EPSG:32611, Tversky index, rules PDF.
- No DrivenData login, scrape, or automatic upload.
- Maximize P(Win). Own the outcome. Negative results are deliverables.

## This session’s execution

The method paragraph was absent. The top new hypothesis, cover-concealed basement step, was preregistered and fit. The result is negative. See `knowledge/2026-10-28_h31cc_session_review.md`.
