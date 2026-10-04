# GEMSDOE31 — auditable GEMS Prize fault-mapping research

> **Current decision: download the incumbent, do not spend the weekly slot yet.** The one-click file is
> `gemsdoe31-h27-4-solo-d28-20261004-8acb75e1` — the re-emitted, re-validated geometry behind the owner-reported
> 0.2708 row (40,199 pixels, none on the public catalogue). Two research candidates that *add* detector
> detections beat it on the off-catalogue discovery proxy (best: +0.0060) but are **not** slot-approved: the gain is
> measured on a proxy, never live, and no organizer receipt exists for any score in this repository.

**Arena core values for this project: Maximize P(Win) · Own the Outcome.**

## Start here

| what | where |
| --- | --- |
| One-click submission download + how to submit | [site home](docs/index.html) · [executive summary](docs/executive-summary.html) |
| Why the 0.2708 geometry scores, and what would beat it | [research](docs/research.html) |
| Buffer derivation, collar control, metric proof, truth proxies | [validation](docs/validation.html) |
| Inputs, score claims, irregularities, review passes | [register](docs/register/index.html) |
| Experiment log (11 experiments, including the stopped one) | [experiments](docs/experiments/index.html) |
| Machine-readable state | [`feed.json`](docs/feed.json) · [`registry/`](registry/) · [`evidence/`](evidence/) |
| AI-use disclosure draft for the narrative | [ai-disclosure](docs/ai-disclosure.html) |

GitHub Pages serves [`docs/`](docs/index.html); the root [`index.html`](index.html) redirects there.

## Session prompt — reread this before doing anything

This repository is the project. Read this README, then `AGENTS.md`, then `registry/review_passes.json` before
starting substantive work. The charter below is the recurring brief; the "Current verified state" section is the
measured starting point. Nothing in this repository may claim a score, an organizer acceptance, or a geological
finding that a file here does not support.

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
bash scripts/download_competition_data.sh      # restore + SHA-256 verify the 11 hash-pinned inputs
python scripts/prepare_data.py --verify-only   # hash/grid re-check (drop the flag to build features.f32)
python scripts/check_metric.py                 # metric vs brute force        -> evidence/metric_check.json
python scripts/derive_buffer.py                # residual semivariogram       -> evidence/buffer_derivation.json
python scripts/run_union.py                    # filter + union experiments   -> evidence/union_results.json
python scripts/collect_evidence.py             # inventory artifacts, rebuild registry/*.json
python scripts/build_submission.py --dots <tif> --name <unique-name>
python scripts/build_site.py && python scripts/check_site.py
python -m pytest -q
```

`scripts/run_h31.py` remains intentionally fail-closed: it requires the fixed Arena branch, a clean worktree, the
pinned GEMSDOE25 sibling checkout, hash-matching mirror inputs/caches, and an empty output directory. It never
contacts DrivenData and never writes a submission GeoTIFF. See [`AGENTS.md`](AGENTS.md) for the ongoing scientific
and execution guardrails, and `registry/review_passes.json` for what the three review passes actually found.
