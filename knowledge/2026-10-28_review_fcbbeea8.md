# Repository review — 28 October 2026 (session `arena/fcbbeea8-gemsdoe31`)

## Decision

**DO NOT SUBMIT. No file is cleared to submit.** This session generated **no new TIFF** and placed **no dots**.

Why no new TIFF: the user's parallel-run protocol says that when a raster's overlap with a registry raster exceeds 70%, "log it as a duplicate and stop", and to check this **before placement**. The registered lattice's counting bound (re-derived below) forces that STOP for any 37,654-dot raster before placement. The repository's rules (`AGENTS.md`) forbid packaging a file after a duplicate STOP and forbid evading the gate by changing density. A new TIFF would therefore be a known duplicate, and it could not meet the "unique" requirement under the literal rule. The existing research-only file is still available for inspection, not submission:

- `docs/downloads/gems31-h31cc-basement-step-37654d-20261028-zeros.tif` (session bb6d6287), SHA-256 `0e82a9e8b80052d0bc61e8f550b2ac5204d012ab1f53fb2208051f285f10ad44`, **DO NOT SUBMIT**.

Estimated leaderboard score for any new file: **unavailable**. No organizer receipt exists in this repository.

## Verification run this session (all reproduced locally)

| Check | Command | Result |
|---|---|---|
| Pinned inputs restored | `scripts/verify_current_run.py --restore-small-inputs` | `data/sample_submission.tif` SHA-256 `2176d08e…35cbc`, `data/labels.tif` SHA-256 `7ba308cc…4093`: both match `registry/data_manifest.json` (owner-mirror pins, not organizer authenticated) |
| Full tests | `python -m pytest -q` | 213 passed (2 failures before input restore, both data-dependent; 0 failures after) |
| Lint | `python -m ruff check .` | passed |
| Metric | `python scripts/check_metric.py` | passed |
| Duplicate gate, count bound | `python scripts/verify_protocol_review.py` | verdict negative, `coverage_fraction` 0.99871, `outside_3px_halo` 6,649, `minimum_overlap_any_same_budget` 0.82342 |
| Release status | `python scripts/build_release_status.py --check` | verdict negative, `ok_to_submit` false, forced duplicate STOP true |
| H31-CC format read-back | `validate_submission` (repo validator) on both H31-CC files | all-finite file: CRS 32611, shape 3730×3292, float32, 0 NaN, values in [0,1], 37,654 ones. NaN twin: 7,111,787 NaN (equals the outside-footprint count), values in [0,1]. Both `ok_to_upload_format_only` = true. Format pass does **not** make a file submittable |
| Site build and check | `build_site.py`, `check_site.py` | 22 pages, 546 local links, all checks passed |

## The count bound, and its threshold

For a registered lattice whose 3 px halo leaves `u` footprint pixels uncovered, any raster with `N` dots has at least `N − u` dots within 3 px of that lattice. So `min_overlap(N) = (N − u)/N`, with `u = 6,649`.

- At `N = 37,654` (the project's budget): `min_overlap = 0.82342`. Forced STOP at the 70% gate.
- The count alone forces STOP only when `N ≥ 22,164`. Below that the count proves nothing.
- The repository forbids exploiting that threshold (it is a density change, and the rules say no density evasion). **Flagged for owner review, not acted on.**

Scope: this is a counting bound against one registered lattice. It is not a proof about every nonempty raster.

## Why the 0.2778 file is the highest user-reported number, and why the gate is inconsistent with it

Source: `evidence/h33_forensics_20261025.json` (RASTER-MEASUREMENT on the owner mirror).

- GEMSDOE32 `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` has 37,654 positives. Its SHA-256 is `c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9`.
- It equals GEMSDOE31's H27-4 raster after deleting 2,545 dots within about 2.24 px of the public catalogue. It adds 0 new pixels, and 0 of its dots sit on a catalogue pixel.
- H27-4 is itself a pruned version of the D2.8 300 m Poisson field.
- Mechanism (a hypothesis supported by the metric algebra, not proven for the leaderboard): under DTI with α = 0.2, β = 0.8, removing dots near known faults lowers false-positive weight and raises the score only if the removed dots were not hiding truth.

The same counting bound applied to this file gives `min_overlap = 0.82342`, so **the literal lattice rule would also stop the highest user-reported file.** The 0.2778 file was accepted by the leaderboard (USER-REPORTED, no receipt). The literal rule is therefore stricter than the competition's apparent acceptance. This is an owner decision, not something I should resolve by choosing a rule that suits the result.

Our internal proxies also do not reproduce the reported ordering. On the catalogue-gap holdout, the H33-2-B2 file scores HOLDOUT-DTI 0.0067 [0.0060, 0.0074] (`h33` rescore in `knowledge/2026-10-28_h31cc_session_review.md`). On the off-catalogue SGMC proxy it scores 0.0940. Neither is a competition score. This divergence is a limitation to report, not an excuse.

## Conflicting user-reported numbers (irregularity)

The prompt names 0.4413, 0.3195 and 0.2778 as "the highest". None is organizer-confirmed and no receipt exists here. The nine-site table uses only the values as the user listed them:

| Site | Best user-reported entry (as listed in prompt) | Value |
|---|---|---|
| GEMSDOE32 | h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros | 0.2778 |
| GEMSDOE36 | anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros | 0.2750 |
| GEMSDOE28 | h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan | 0.2710 |
| GEMSDOE31 | h27-4-solo-d28-20261004-8acb75e1-nan | 0.2708 |
| GEMSDOE33 | h33d-analog-tip-stepover-r30-20261004-cb490425926e | 0.2632 |
| GEMSDOE25 | dotted-h19-5-d2-8-20261002-e56ea318af89-nan | 0.2600 |
| GEMSDOE30 | d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca | 0.2600 |
| GEMSDOE24 | h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan | 0.2477 |
| GEMSDOE27 | topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan | 0.2449 |

## Three passes

1. **Implementation and verification.** Restored the two pinned small inputs. Re-ran the full test, lint, metric, release-status, current-run and site checks, plus the count bound. Wrote `scripts/session_fcbbeea8_gate.py` and `evidence/review_fcbbeea8/run_card.json`, which re-derive the bound and the H33 case. Added a site section (`scripts/current_site.py`, `session_fcbbeea8_notice`) that reads the card.
2. **Bug and assumption review.** Found and fixed one defect: `collect_evidence` wrote a stale `evidence/h31aa/verification_receipt.json` that said "skipped (sample not restored)" even with the sample present. It was restored to the committed bytes, which then verify fresh. Also renamed an ambiguous run-card key to `new_file_download_for_research_this_session`. Recorded that the count threshold is 22,164, not the 9,498 I first estimated (an arithmetic slip corrected before commit).
3. **Whole-request check.** The user asked for a new unique TIFF. Not delivered, for the protocol reason above. The user asked for an executive summary with a table of file, estimate and uniqueness. Delivered on the existing page, with the estimate column reading "unavailable". The user asked for three to five hypotheses. Not repeated here; prior hypotheses are in `knowledge/2026-10-28_h31cc_preregistration.md` and `knowledge/2026-10-25_unique_submission_hypotheses.md`. The user asked for links for manual review (below).

## Experiments and budget

- Experiments run this session: **0** (budget 3 experiments / 2 hours; none used).
- Dots placed: **0**. Slots used: **0**. DrivenData contacted: **no**. Leaderboard accessed: **no**.

## Limitations and what is needed

1. **Organizer access.** DrivenData login is required for the competition data and any official receipt. Not available in this sandbox (allowlist: github.com, codeload, api.github.com, registry.npmjs.org, pypi.org, files.pythonhosted.org). The owner-mirror pins in `registry/data_manifest.json` prove byte identity to a mirror only.
2. **Missing method paragraph.** The prompt's single method paragraph (the lane definition) is absent, so the lane was self-assigned in earlier sessions.
3. **Owner decision on the registry rule.** Options: (a) keep the literal rule, which means no ≥22,164-dot file can be submitted and the 0.2778 file would have been stopped too; (b) restate the rule with an owner-approved registry definition or budget; (c) allow sub-threshold budgets, which the repo currently forbids. Only the owner can choose.
4. **Proxy mismatch.** Internal proxies (catalogue-gap holdout and SGMC off-catalogue) do not reproduce the user-reported ordering, so no internal number is a leaderboard estimate.

## Sources for manual review

Links are given for manual review. **Those marked "not fetched" were not accessed in this session.**

- [Competition problem page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) — not fetched this session.
- [Competition about page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/) — not fetched this session.
- [Competition data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) — login required; not accessed.
- [Leaderboard (static link)](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) — not fetched; not scraped (AGENTS.md).
- [Reference solution](https://github.com/drivendataorg/gems-prize-reference-solution) — fetched in an earlier session (per `knowledge/2026-10-28_h31cc_session_review.md`); not re-fetched.
- [Submission format PDF, NLR](https://docs.nlr.gov/docs/fy26osti/96647.pdf) — not fetched this session.
- [EPSG:32611](https://epsg.io/32611) — not fetched this session; the grid check uses the repo's own pinned transform.
- [USGS GeoDAWN dataset](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) — not fetched this session.
- [Tversky index](https://en.wikipedia.org/wiki/Tversky_index) — not fetched this session.
- Owner-mirror pins: [`registry/data_manifest.json`](../registry/data_manifest.json) (SHA-256 per file; mirror provenance only).
