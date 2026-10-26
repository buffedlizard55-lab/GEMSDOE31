# Repository review — Arena branch `arena/e40c3412-gemsdoe31` — 2026-10-26

## Executive decision

**No new experiment or TIFF was generated; no TIFF is approved for competition submission.** The current documented H31-S file remains a research artifact, and its exact-file verifier reports `verdict=negative`, `ok_to_download_for_research=true`, `ok_to_submit=false`, and `slot_approved=false`. This review did not use a weekly slot, access the live leaderboard, or upload anything.

This is the only protocol-compliant decision for this continuation:

- The requested assigned-method paragraph is absent; the prompt has only an unexpanded placeholder. The earlier H31-S preregistration discloses that it self-declared a lane rather than receiving an assigned paragraph.
- H31-S already used the allowed three experiments. Its frozen card records `experiments_run=3` and `max_experiments=3` (843.1 seconds; the experiment-count limit was reached).
- The literal broad-registry rule has a measured counterexample: H31-S has 99.931% 3-pixel overlap with the registered spacing-5 lattice, exceeding the 70% stop threshold. Do not waive this by treating a dense or calibration raster as exempt.
- During PR preparation, the concurrent update to `origin/main` added a CSDU raster. We preserved that commit rather than discarding concurrent work, then independently rechecked its bytes against the pinned sample. Both CSDU encodings fail exact-footprint validation; its holdout, leakage canary and registry comparisons were not run. It is not a candidate to submit or promote.
- Consequently, new hypotheses below are desk-only research proposals. They are not an authorization to compute features, fit a model, emit a raster, or select a submission.

## What H33-2-B2's reported 0.2778 does and does not tell us

The score `0.2778` is **USER-REPORTED**, not organizer-confirmed in this repository. The exact scored submission bytes and an organizer receipt are unavailable, so its private score cannot be causally attributed or independently reproduced here.

Existing pixel forensics identify H33-2-B2 as the D2.8 support after removing dots within two pixels of the public catalogue; it adds no new detector support relative to D2.8. This is consistent with a plausible DTI-economics mechanism: reducing redundant or already-mapped coverage can lower false-positive cost faster than it lowers credit on withheld faults. It does **not** prove every removed point was false positive, and it does not prove a score gain. The metric's exact finite-change condition is recorded in `evidence/marginal_dti_audit_20261026.json`; substituting a user-reported leaderboard value into that algebra is not a score projection.

The nine requested sites and their highest supplied historical claims are indexed in `docs/executive-summary.html#focus-sites` and `registry/focus_review.json`. These claims remain USER-REPORTED; their best historical files are prior art, not unique new recommendations. The repo's measured overlaps and known duplicate-family relationships are in `evidence/nine_site_forensic_audit.json` and `evidence/h33_forensics_20261025.json`.

| Site | Highest supplied historical claim | Current interpretation |
|---|---:|---|
| GEMSDOE24 | 0.2477 | H25-1 D1.5; prior art / duplicate family |
| GEMSDOE25 | 0.2600 | Dotted H19-5 D2.8; prior art / duplicate family |
| GEMSDOE27 | 0.2449 | Topo-gap-closure T-v2; prior art / duplicate family |
| GEMSDOE28 | 0.2710 | H36-1 rung30; prior art / duplicate family |
| GEMSDOE30 | 0.2600 | D28 Poisson; prior art / duplicate family |
| GEMSDOE31 | 0.2708 | H27-4; user claim conflicts with pinned owner-page `UNSCORED` status |
| GEMSDOE32 | 0.2778 | H33-2-B2; highest supplied claim, not organizer-confirmed |
| GEMSDOE33 | 0.2632 | H33D analogue tip/stepover; prior art / high H33 overlap |
| GEMSDOE36 | 0.2750 | Anderson geothermal PINN; prior art / high H33 overlap |

These are not estimates of a future submission score. There is no supported way to claim that a new candidate will exceed 0.2778, 0.3195, or 0.4413 from the available evidence.

## Ranked desk hypotheses (not implemented or run)

The request asks for 3–5 geological hypotheses before implementation. Three refinements are listed because the latest repository review already identifies them as plausible gaps; they are **not asserted to be globally novel or untried across every sibling site**. Rankings are qualitative research priority under present evidence, not expected numeric DTI. A numeric expected DTI is not defensible without the missing production stack, authorized lane, and preregistered holdout. All require renewed authorization before work.

| Rank | Hypothesis; layers/signature | Why it could add missing faults; difference from repository work | Qualitative DTI expectation | Cost / data / status |
|---:|---|---|---|---|
| 1 | **Reciprocal magnetic texture restoration:** B2 RTP magnetic texture; estimate forward and reverse patch displacements and score cycle-closure error rather than only same-sign restoration gain at selected offsets. | A buried fault may offset magnetic texture even where no mapped scarp is visible; reciprocal closure could reject one-way matches caused by texture repetition. Differs from MAGREST's same-sign multi-offset restoration statistic, but is a method refinement, not a new established detector. | Unknown; no score projection. Mechanistically plausible, highly uncertain. | Medium CPU if pinned B2 cache is restored. Local layer only; no new external source required. Not runnable now: full feature/cache stack absent, lane unspecified, experiment budget exhausted. Nulls: volcanic flow contacts and flight-line/texture repetition. |
| 2 | **Joint radiometric–magnetic displacement agreement:** GeoDAWN K/Th/U channels plus B2 RTP; independently estimate compositional and magnetic displacement vectors and require sign/uncertainty agreement. | A concealed fault might offset both magnetic and alteration-related compositional fabric without a LiDAR scarp. Differs from simple K/Th amplitude or edge conjunction and from MAGREST-only magnetic restoration. | Unknown; no score projection. Plausible but depends on geologic context and radiometric quality. | High CPU / data QA. The repo cites USGS GeoDAWN DOI `10.5066/P9P36HQ6` in `registry/sources.json`; current session did not fetch its host or verify fresh availability. Existing raster/cache may be used only after hash restoration. Mimics: lithologic contacts, alluvial provenance boundaries, acquisition seams. Not runnable now. |
| 3 | **Gravity–magnetic reciprocal co-restoration:** B2 RTP magnetics and B13 isostatic gravity; compare independently estimated displacement/restoration solutions with uncertainty weighting. | Basement transfer faults under cover could displace both density and magnetic textures; cross-field agreement may separate a structural break from a single-field intrusive/contact edge. Differs from the repo's gravity/magnetic gradient or depth concordance by testing displacement consistency. | Unknown; no score projection. Lower confidence because gravity resolution may be too coarse for a 300 m scoring kernel. | High CPU / geophysical QA; local feature bands, no new external source required. Not runnable now: production stack absent and authorization/budget gates block execution. Mimic: intrusive lithologic boundary affecting both fields. |

**Selection decision:** none can be ranked by expected numerical DTI, and none is viable to execute under the current lane. If a future authorized run supplies one of these methods as its single assigned paragraph, test feature-alone leakage first, then the unchanged shared hide-and-recover evaluator with whole-segment withholding/buffer, exact visible-only catalogue features, pooled DTI, spatial CI, and a same-instrument incumbent. Stop on the first duplicate, leakage or failed efficacy gate. No weekly submission slot is to be used in this research step.

For manual source review, the repository's source register links the [official DrivenData problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), [official rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf), [DrivenData reference-solution repository](https://github.com/drivendataorg/gems-prize-reference-solution), [USGS GeoDAWN data release](https://doi.org/10.5066/P9P36HQ6), and [GDR/INGENIOUS compilation](https://gdr.openei.org/submissions/1391). These links are carried forward from `registry/sources.json`; this review did not fetch or re-verify external non-GitHub hosts, and the source registry records their retrieval dates and scope limits.

## Review finding fixed in this continuation

The site generator had stale status text:

- The executive-summary hero said “newest candidate RBU31 failed”, even though the latest recorded candidate is H31-S.
- The overview hero overstated H31-S's H31-M screen result as 4/4 quadrant wins. Its card records only 1/4 quadrants against H31-M on screen seed 41; the fresh seed-42 confirmation is 4/4, but that later confirmation does not erase the failed preregistered screen criterion.
- The overview's generic “latest” description and internal-page notice were keyed to the old MAGREST/RBU31 history, not the current H31-S receipt.

Updated the generator (`scripts/build_site.py`, `scripts/current_site.py`) to show the current H31-S status accurately and added a presentation regression test. Regenerated Pages from the source. No H31-S or historical TIFF, score receipt, or scientific result was changed. The concurrent CSDU files from the advancing `origin/main` were preserved, then explicitly marked as failed audit artifacts; their bytes were not repaired or regenerated.

## Concurrent CSDU artifact audit

The exact-file run card for `gemsdoe31-csdu-stepover-8cf9dc27` says its holdout and registry comparisons were not run. Its generator script writes a synthetic approximate ellipse footprint and synthetic all-zero labels, while its own local validation sets `require_competition_grid=False`. Treating its original format receipt as validation against the real sample would therefore be a false claim. The generator is now quarantined: its CLI exits before writing files, and a regression test protects that guard.

Using the pinned owner-mirror `data/sample_submission.tif` (SHA-256 `2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc`; not organizer-authenticated), ran the shared `validate_submission` on the exact committed CSDU bytes:

| CSDU file | Pinned sample check | Result |
|---|---|---|
| `...-allfinite.tif` | footprint finite/range: PASS; exact sample mask has 5,167,373 pixels; 2,101 dots inside and 1,899 outside, violating the all-finite zero-outside rule | **FAIL**, `outside_footprint_zero` |
| `...-nan.tif` | 2,610,312 NaN/Inf cells inside the true footprint; 4,387,799/7,111,787 outside cells are NaN, so outside mask also mismatches | **FAIL**, footprint finiteness/range/outside/mask |

Thus the CSDU files do not meet the exact-footprint submission gate even before science or uniqueness. The audit is recorded in `evidence/csdu_owner_mirror_validation_20261026.json`, and `IR-31-CSDU-SYNTHETIC-FOOTPRINT-FAIL` flags it. Do not upload, silently repair, or call the file unique: no registry comparison or HOLDOUT-DTI exists. The all-finite and NaN twins remain only for forensic reproducibility.

## Validation performed in this checkout

- Installed the pinned `requirements.txt` into ignored `.venv/` from the configured package index; no dependency or cache artifact is added to Git.
- Restored the two small hash-pinned validation rasters and the pinned registry witness via `python scripts/verify_current_run.py --restore-small-inputs`. Full feature data/cache is still absent.
- `python scripts/verify_h31s_run.py`: PASS exact-byte check; H31-S remains research-only, negative, and `ok_to_submit=false`.
- `python scripts/verify_current_run.py --restore-small-inputs`: PASS exact-byte check; MAGREST remains research-only, negative, and `ok_to_submit=false`.
- `python scripts/check_metric.py`: maximum fast/brute DTI difference `4.441e-16` over 24 grids; two exact cases checked; 29 offsets inside the 300 m kernel. This verifies implementation arithmetic, not leaderboard performance.
- `.venv/bin/python -m ruff check .`: PASS.
- `.venv/bin/python -m compileall -q src scripts tests`: PASS.
- `.venv/bin/python scripts/build_site.py` and `scripts/check_site.py`: PASS, 22 pages and 445 local links.
- The first full test pass before restoring small validation fixtures produced **133 passed, 7 skipped, 2 failures** because the small TIFF prerequisites were missing, plus one new test setup failure from calling the overview without its run card. Restored the inputs and fixed the test to supply the actual card. Final `.venv/bin/python -m pytest -q`: **145 passed**. Repeated the CI restore/verifier/test sequence locally under Python 3.11; all steps passed.
- Remote Actions run `40358930573` on commit `5895788` failed in the `Unit, leakage, metric, writer and regression tests` step. GitHub annotations expose only the step exit code; `gh run view --log-failed` returned EOF while fetching the log, so the exact remote failure is unknown. Do not merge until diagnosed or a new remote run passes.

## Three cumulative passes

1. **Pass 1 — inspect and correct:** read the complete README/embedded owner prompt, agent instructions, current status, run cards, preregistration, executive page, shared protocols and registry. Confirmed the no-new-experiment stop. Fixed current site status and corrected H31-S seed-41 screen wording.
2. **Pass 2 — bug/edge review:** restored only the small pinned validation fixtures (not the full competition feature stack), ran exact-file verification, checked the literal 695-raster STOP and H31-S efficacy gate remain fail-closed, and added a regression test against stale RBU31/latest and false 4/4 wording.
3. **Pass 3 — whole-request cross-check:** regenerated the site from its Python source; rechecked the nine-site table and labels, score provenance, download/submit distinction, optional note, holdout evidence and data limits. No unsupported score projection, experiment, TIFF, upload, or slot selection was added.

## Remaining work and limitations

1. Supply the missing assigned-method paragraph and explicitly authorize a new experiment before any candidate feature computation.
2. Resolve the literal dense-lattice uniqueness rule with the protocol owner; retain the existing STOP until documented resolution.
3. Restore and hash-verify the full production feature/cache stack and confirm exhaustive registry coverage before attempting a new holdout or global uniqueness conclusion.
4. Reconcile `registry/current_run.json` (historical MAGREST) with the separately authoritative `registry/h31s_current_run.json` without deleting historical verifiers or evidence.
5. Obtain organizer-authenticated receipts for exact scored bytes and current rules/template through authorized access; no score in this review is ORGANIZER-CONFIRMED.
6. The repo is a static site, not a current leaderboard feed. Do not automate DrivenData access or upload; the project records the terms/access limits in `registry/sources.json`.
7. After a separately authorized candidate beats a comparable same-protocol holdout incumbent and fresh confirmation, a distinct selector—not this review—must decide whether any weekly slot is used.
