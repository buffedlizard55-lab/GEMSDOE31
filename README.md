# GEMSDOE31 — auditable GEMS Prize fault-mapping research

> **Current decision (2026-10-25): no file is cleared for submission.** The lane's unique-bytes candidate
> `gemsdoe31-as1-lidar-antislope-38000dots-20261025-9b3afbc8` is format-valid but **BLOCKED**: it failed the preregistered
> holdout gate (E3) and duplicates 14 registry rasters under the lane overlap rule. It is downloadable for inspection only;
> the gate receipts say so in machine-readable form. The 2026-10-04 incumbent (`gemsdoe31-h27-4-solo-d28-...`, owner-reported 0.2708)
> is not a new submission: its geometry was already scored. No organizer receipt exists for any score in this repository.

> Parallel finding from the session reviewed in [the session review](knowledge/session_review_2026-10-25.md): GEMSDOE32's H33-2-B2 prior-art TIFF exceeds the
> duplicate-correlation and overlap limits against the local H27-4 raster (run stopped and logged), and the prompt's 0.2778 claim stays USER-REPORTED because the
> inspected owner-mirror archive labels the artifact UNSCORED. The older H27-4 and union files are audit/format-reference only; **none is approved for a weekly slot.**

**Arena core values for this project: Maximize P(Win) · Own the Outcome.**

## Start here

| what | where |
| --- | --- |
| Reference TIFF download + upload status | [site home](docs/index.html) · [executive summary](docs/executive-summary.html) |
| Why the 0.2708 geometry scores, and what would beat it | [research](docs/research.html) |
| Buffer derivation, collar control, metric proof, truth proxies | [validation](docs/validation.html) |
| Inputs, score claims, irregularities, review passes | [register](docs/register/index.html) |
| Experiment log (11 experiments, including the stopped one) | [experiments](docs/experiments/index.html) |
| Lane run card, E1-E3, instrument calibration, ranked hypotheses | [lane](docs/lane.html) · [`knowledge/2026-10-25_lane_hypotheses.md`](knowledge/2026-10-25_lane_hypotheses.md) · [`evidence/run_card_lane_as1.json`](evidence/run_card_lane_as1.json) |
| Machine-readable state | [`feed.json`](docs/feed.json) · [`registry/`](registry/) · [`evidence/`](evidence/) |
| Latest status / score audit | [Current status](knowledge/current_status_2026-10-25.md) · [2026-10-25 review](knowledge/session_review_2026-10-25.md) · [irregularity register](registry/irregularities.json) |
| AI-use disclosure draft for the narrative | [ai-disclosure](docs/ai-disclosure.html) |

GitHub Pages serves [`docs/`](docs/index.html); the root [`index.html`](index.html) redirects there.

## Session prompt — reread this before doing anything

This repository is the project. Read this README, then `AGENTS.md`, then `registry/review_passes.json` before
starting substantive work. The charter below is the recurring brief; the "Current verified state" section is the
measured starting point. Nothing in this repository may claim a score, an organizer acceptance, or a geological
finding that a file here does not support.

## Session brief 2026-10-25 (the user's prompt, condensed without losing requirements)

**Goal.** Maximize the probability of a top finish in the DrivenData DOE GEMS Prize (competition 306). Study why GEMSDOE32
`h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` scored 0.2778 (highest among GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, 36) and whether a
submission can beat it. Anchors quoted in the prompt: "GEMSDOE high score 0.4413" and "highest score right now 0.3195" (they conflict; 0.4413 equals a
GEMSDOE32 *local proxy*, so it is probably mislabelled, see `registry/irregularities.json`). All score numbers in the prompt are stored in
[`registry/user_reported_scores.json`](registry/user_reported_scores.json) as USER-REPORTED.

**Highest urgency: a UNIQUE TIF.** Not a copy of a registry submission (copying is for learning only). It must be obvious whether the file is OK to download
and submit; the download must be easy to find; validation must run without a human. Required checks: values in [0,1] (the owner hit "Predicted values must be in
range [0, 1]"), CRS/shape/geotransform match, single band, NaN outside the footprint. A submission needs a unique name and a note of at most 140 characters. A file
must pass the high-scoring validation gates before being declared unique and submittable (`scripts/submission_gate.py`, `src/gemsdoe31/gate.py`).

**Hypotheses.** Generate 3-5 new geological hypotheses before implementing; each names layers, physical signature, why it would catch faults missing from the
USGS/INGENIOUS catalogue, and how it differs from the repo; rank by expected DTI gain and cost; validate the top one on the spatially blocked holdout before using
a slot; any new external data needs a named free official source whose availability is checked.

**Parallel-run lane protocol (binding).** Stay in your method lane. Overlap limits: rank-correlation > 0.90 with any registry raster, or > 70 percent of dots within 3 px of
one registry raster; if exceeded, log a duplicate and stop; check on the surface before placement and on the final dots. Reuse the template's cached feature stack,
`evaluate_holdout.py` and `submission_writer.py`. Hold-out is hide-and-recover (withhold fault segments with a buffer, catalogue features from visible faults only,
mask visible faults pixel-exactly, pooled DTI with alpha 0.2, beta 0.8, 300 m triangular kernel). Fix shared tools once in the template, no private forks. Label every number
HOLDOUT-DTI (evaluator version, withheld positives, 95% CI) or ORGANIZER-CONFIRMED; projections are never scores. Leakage canary: each feature alone, AUC > 0.90 means leakage.
End with one JSON run card (hypothesis, mechanism, mimicking non-fault process, holdout DTI + CI, overlap vs registry, raster sha256, validator output, name + note <= 140,
verdict promote/negative). Negative results are deliverables. Budget: 3 experiments or 2 hours. Do not pick submissions for slots.

**Research and data.** Deep research on geothermal and fault discovery from official sources, looking for overlooked data; store knowledge in `knowledge/` with links for
manual review; work autonomously; flag irregularities; no hallucinations. DrivenData data needs login, so the hash-pinned owner mirror is used:
`bash scripts/download_competition_data.sh`, then `python scripts/prepare_data.py`.

**Site and delivery.** GitHub Pages site, clean UI, the TIF download at the very top, an executive-summary subpage on exactly how to submit, a data table with official links,
limitations and needed access. Three review passes (implement and verify; bug/assumption review; whole-request recheck), PR merged to main, remaining work and limitations
stated. Reread this README every session. Core values: Maximize P(Win), Own the Outcome.

**Reference links.** [Competition](https://www.drivendata.org/competitions/306/competition-doe-gems/) ([problem description, page 967](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)) ·
[reference solution](https://github.com/drivendataorg/gems-prize-reference-solution) · [NLR rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf) ·
[GDR submission 1391](https://gdr.openei.org/submissions/1391) ·
[USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) ·
[INGENIOUS](https://gbcge.org/current-projects/ingenious/) · [EPSG:32611](https://epsg.io/32611) · [Tversky index](https://en.wikipedia.org/wiki/Tversky_index)

### Result of this session in four lines

1. E1-E3 are all negative or inconclusive; the preregistered E3 gate failed (`evidence/lane_e3.json`, `PROMOTE_TO_SELECTOR = false`).
2. The candidate is a lane duplicate (14 registry rasters) and sits in the family of LiDAR-scarp files that scored 0.038-0.159 live (USER-REPORTED): `evidence/instrument_calibration.json`.
3. Uniqueness and live validation conflict: the only geometry with live scores near 0.27 is the D28 family and anything derived from it fails the uniqueness rule.
4. Next: one owner decision on a live-slot experiment for the catalogue-shadow idea (H4) in `knowledge/2026-10-25_lane_hypotheses.md`; the gate will report the uniqueness waiver explicitly.

## Standing project charter — full active scope

The charter preserves the complete active scope and acceptance criteria as a faithful consolidated restatement of
the project request. It is the recurring project prompt: reread this section, the current evidence registers and the
status record before each substantive continuation. It is not represented as a verbatim quote where the session
handoff condensed the original wording.

### Objective and decision principles

Build a scientifically rigorous, reproducible and auditable GEMS Prize project that **maximizes the probability of a
valid, high-performing submission** and **owns the outcome**. “Maximize P(Win)” and “Own the Outcome” mean
prioritizing evidence and genuine geological signal over optimistic claims, reporting failed tests plainly, and
spending a weekly slot only when the candidate has passed the registered gates.

The task is to predict geological faults — not geothermal favorability, vents, or merely the public known-fault
inventory. Treat competition truth as incomplete and potentially inaccurate. Distinguish official sources,
owner/user-reported claims, computed evidence, and inference at every point. Provide source links and flag
irregularities; do not invent results or imply that a proxy score is a competition score.

### Scientific hypotheses and validation

1. Review earlier submissions, code, hypotheses, and outcomes before proposing new work. Do not relabel H26–H30
   experiments as new evidence.
2. Nominate **3–5 genuinely distinct geological hypotheses**. For each, document input layers, physical signature, why
   it could reveal faults missing from existing maps, what is novel relative to this repository, uncertain expected
   spatial-holdout DTI gain, implementation cost, data provenance/access, and validation status. Rank candidates
   before implementation.
3. Preregister the selected candidate's features, model, folds, draws/seeds, metric, analysis, buffer rule, and
   promotion gate before fitting. Compare it to a comparable same-run incumbent on a spatially blocked holdout. A
   screen pass alone is not sufficient; use fresh confirmation draws without tuning on them.
4. Derive the spatial collar empirically from out-of-fold residual semivariograms along known fault traces. Report
   the fitted range and uncertainty. Do not assume a generic 4–5-pixel buffer; if the range is not identifiable,
   report it as unknown and stop.
5. Do not use a weekly submission slot unless the candidate beats the current comparable spatial-holdout best,
   passes fresh confirmation, and passes the exact-file audit. A proxy DTI or modelled expectation is never a
   leaderboard score.
6. If data needed for a candidate cannot be accessed, identify and check a free official source, record what
   coverage/metadata/binaries were actually verified, and describe the blocker rather than inventing evidence.

### The core question this project must answer

Why did `h27-4-r1-solo-d2-8` score 0.2708 — the best of the owner-mirror GEMSDOE28 set — and can a submission beat
it, and beat the 0.3195 top-of-leaderboard anchor? The measured answer so far (details in
[research](docs/research.html)): the file is a **thinned dot set**, not a probability field — 40,199 isolated 100 m
cells at ≈283 m spacing, none on the public catalogue, each earning ≈0.135 off-catalogue proxy credit per pixel
against ~0.02 for a thresholded detector field. Under `DTI = TPw/(TPw + 0.2·FPw + 0.8·FNw)` the denominator charges
0.2 per emitted pixel, so precision pays and volume does not. Re-budgeting the same dots cannot reach 0.3195 (the
one exactly-controlled live thinning step cost 0.031 credit per removed dot, below the ≈0.055 break-even); the only
direction with headroom is **more genuine detections**.

### Submission artifact, site, and user instructions

1. Build a clean GitHub Pages site with a prominent, easy-to-find single-band GeoTIFF download and a clear
   executive-summary subpage explaining exactly how to submit. Make the current artifact's status unmistakable;
   never label an unconfirmed legacy file as the active submission. Site budget: 20 pages, no pictograms in the
   chrome, tables over paragraphs, per-claim evidence classes, links so any single claim can be checked.
2. For any candidate GeoTIFF, verify the organizer's CRS, grid, dimensions, geotransform/bounds, single-band float32
   type, and valid footprint. All footprint predictions must be finite and in `[0,1]`; values outside the footprint
   must be null/NaN as the official page specifies. No silent clipping or zero-filling. Include a regression test
   that catches the “Predicted values must be in range [0, 1]” class of error reported by the owner.
3. Include a unique submission name, a concise optional comment, and exact manual instructions for uploading on
   DrivenData. Clearly mark reserved metadata versus an actual submitted file. Explain that AI use must be disclosed
   in the narrative as required by the official rules.
4. Explain the prior D2.8 score history and why it may have scored as it did, separating user/owner-reported
   leaderboard claims from organizer receipts. The 0.2600 D2.8 claim remains unresolved against the pinned
   owner-mirror record — see `registry/irregularities.json` and
   [`knowledge/prior_submission_audit.md`](knowledge/prior_submission_audit.md).

### Source, access, and integrity rules

- Use official or primary sources for contest rules, data specifications, and third-party products. Preserve them in
  `registry/sources.json` with retrieval date, verified claims, and limits.
- DrivenData Terms of Use prohibit robot/spider/automatic access “for any purpose, including monitoring or copying”
  and prohibit manual monitoring/copying without prior written consent. Do **not** build a leaderboard scraper,
  periodic feed, or automatic submission. A static official leaderboard link for manual review is acceptable.
- Owner-mirror hashes prove byte identity to that mirror only; they do not prove organizer authenticity, acceptance,
  or score.
- Do not commit large competition inputs, LAZ files, or regenerable caches. Keep provenance hashes and only the small
  evidence artifacts required for audit.
- New data acquisition is allowed only through official, no-account sources; label what each new layer adds, its
  format, and whether it is obtainable without credentials.

### Review, reporting, and delivery

Perform cumulative review passes: (1) implement and verify against sources and preregistration; (2) inspect and fix
bugs, assumptions, leakage and edge cases; (3) re-check the full result against this charter and report remaining
limits. Record each pass in `registry/review_passes.json`. Keep the site and README current, flag irregularities, and
make the remaining work clear. Prepare a pull request and merge it to `main` if repository permissions and checks
allow; report a PR, merge, deployment, official score, or organizer acceptance only when there is a verifiable
status/receipt.

## Current verified state (2026-10-04)

- **Inputs:** all 11 hash-pinned owner-mirror inputs restore and verify (`evidence/data_restore.json`,
  `all_verified: true`; `scripts/prepare_data.py --verify-only` re-checks grid/CRS/shape/dtype). Grid: EPSG:32611,
  3730×3292, 100 m, 5,167,373-cell footprint, 7,111,787 cells outside it.
- **Metric:** `src/gemsdoe31/metric.py` implements the published sums; `scripts/check_metric.py` reports a maximum
  |ΔDTI| of 4.4e-16 against a literal brute-force transcription over 24 random grids plus two exact cases, and
  asserts `TPw + FNw = |G|`. 29 lattice offsets fall inside the 300 m kernel.
- **Buffer:** the empirical decay range of out-of-fold residuals along known fault traces is **21.25 km** (peak
  20.75 km, populated support 26.75 km); the adopted collar is 21.25 km — not 4–5 pixels. Fitted practical ranges:
  spherical 12.97 km, exponential 30.56 km (excluded, extrapolates), gaussian 6.74 km. The withdrawn 94.3 km
  pilot rule is recorded on the register. Collar sensitivity 0–30 km changes no arm ordering.
- **Arm results (fold-blocked, both proxies):** on the catalogue-gap holdout the LiDAR+radiometric arm leads
  (0.1355 at p≥0.4); on the off-catalogue discovery proxy the incumbent dot set leads by ~2× (0.0938 vs 0.0781
  best full-coverage arm). The two instruments disagree — that disagreement is why the catalogue-gap holdout cannot
  be used to promote arms.
- **Filtering is refuted; adding works:** every corroboration-filter quantile lowers both proxies; the best
  catalogue-dropping union is the **LiDAR arm at p≥0.60** → 106,138 dots, off-catalogue proxy **0.0999**
  (+0.0060), catalogue-gap proxy 0.0948 (`evidence/union_results.json`). The radiometric union at p≥0.70 gives
  +0.0017. Both files are built, format-validated and labelled research-only; neither is slot-approved.
- **Submissions present:** primary `gemsdoe31-h27-4-solo-d28-20261004-8acb75e1` (40,199 px, sha256
  `07b6db44…`), research unions
  `gemsdoe31-union-b-p060-20261004-8acb75e1` (106,138 px, sha256 `a4b8ffa5…`) and
  `gemsdoe31-add-arm-d28-20261004-8acb75e1` (55,304 px, sha256 `5987d505…`), plus the legacy D2.8 reference. All
  pass the `nan-outside` and `all-finite` format conventions; none has organizer acceptance.
- **Honesty limits:** no organizer receipt exists for any score; 0.2708 and 0.2600 are owner-reported. The arm
  sweeps' trainer is not in this snapshot (outputs and the fold-OOF probability maps are pinned instead); the
  off-catalogue proxy is SGMC state-map faults, a proxy for the hidden truth, not the hidden truth.

## Reproducibility and code

Python 3.11; pinned versions in [`requirements.txt`](requirements.txt).

```bash
git clone https://github.com/buffedlizard55-lab/GEMSDOE31.git && cd GEMSDOE31
python -m pip install -r requirements.txt
bash scripts/download_competition_data.sh      # restore + SHA-256 verify the 12 hash-pinned inputs (incl. TIGER road distance)
python scripts/prepare_data.py --verify-only   # hash/grid re-check (drop the flag to build features.f32)
python scripts/check_metric.py                 # metric vs brute force        -> evidence/metric_check.json
python scripts/derive_buffer.py                # residual semivariogram       -> evidence/buffer_derivation.json
python scripts/run_union.py                    # filter + union experiments   -> evidence/union_results.json
python scripts/build_raster_registry.py       # clone owner repos (git only), cache 364 MB of dot rasters in data/registry_rasters/ (gitignored)
python scripts/run_lane_e1.py && python scripts/run_lane_e2.py && python scripts/run_lane_e3.py   # lane experiments -> evidence/lane_e*.json
python scripts/calibrate_instruments.py        # proxies vs user-reported live scores -> evidence/instrument_calibration.json
python scripts/build_lane_candidate.py         # emit the frozen AS-1 candidate into docs/downloads/blocked/
python scripts/submission_gate.py <tif> --convention all-finite --name <name> --note "<=140 chars" --json-out <receipt>   # all gates, exit 0/3/2
python scripts/write_run_card.py               # evidence/run_card_lane_as1.json
python scripts/collect_evidence.py             # inventory artifacts, rebuild registry/*.json
python scripts/build_submission.py --dots <tif> --name <unique-name>
python scripts/build_site.py && python scripts/check_site.py
python -m pytest -q
```

`scripts/run_h31.py` remains intentionally fail-closed: it requires the fixed Arena branch, a clean worktree, the
pinned GEMSDOE25 sibling checkout, hash-matching mirror inputs/caches, and an empty output directory. It never
contacts DrivenData and never writes a submission GeoTIFF. See [`AGENTS.md`](AGENTS.md) for the ongoing scientific
and execution guardrails, and `registry/review_passes.json` for what the three review passes actually found.
