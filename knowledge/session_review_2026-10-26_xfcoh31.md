# XFCOH31 three-pass review — 2026-10-26

**Repository:** `buffedlizard55-lab/GEMSDOE31`
**Working branch:** `arena/f167d617-gemsdoe31`
**Decision:** the existing XFCOH31 TIFF is **research-download-only; DO NOT SUBMIT**. No experiment, model fit, placement, TIFF, upload, leaderboard access, or weekly slot was used after the exact-file STOP.

This review is an audit of the existing run and bytes, not a rerun. The experiment budget is spent. The exact numeric audit is in [`evidence/xfcoh31_registry_stop_audit.json`](../evidence/xfcoh31_registry_stop_audit.json); the decision page is [`docs/xfcoh31.html`](../docs/xfcoh31.html); the nine-site summary and ranked hypotheses are in [`knowledge/2026-10-26_xfcoh31_executive_summary.md`](2026-10-26_xfcoh31_executive_summary.md).

## Pass 1 — charter, provenance, and experiment-workflow review

Read the repository README including its complete owner prompt, `AGENTS.md`, the XFCOH31 preregistration, run card/results, existing source registry, run implementation, shared holdout/metric code, and the separate MAGREST and H31-S run records. The exact file under review is the XFCOH31 all-finite TIFF with SHA-256 `857dd662430c0130c46f920666d70dae5df6148951ad76d42d31a8d540c32972`.

Findings:

- `registry/current_run.json` remains the MAGREST technical receipt; `registry/h31s_current_run.json` remains H31-S; XFCOH31 is a separate run card and exact-file audit. Their data and decisions were kept distinct.
- The supplied GEMSDOE32 H33-2-B2 `0.2778` and other competition values remain **USER-REPORTED**, not ORGANIZER-CONFIRMED. No organizer receipt was located.
- The run used the shared `gemsdoe31.holdout` and metric functions with whole fault components, pixel-exact masking of visible faults, the shared pooled DTI (alpha 0.2, beta 0.8, 300 m triangular kernel), and a 21.25 km fixed collar. The collar was inherited, not re-estimated specifically for XFCOH31.
- Material workflow deviations were found and recorded in the run card: `run_xfcoh31.py` builds a fresh feature memmap rather than using the template cache; directly calls holdout module functions rather than the requested `evaluate_holdout.py` workflow; directly writes TIFF/ZIP rather than using the requested `submission_writer.py`; and tests individual features against visible catalogue labels rather than the preregistration’s described fold-pooled withheld truth. The saved results do not retain per-block sufficient statistics needed to independently replay the paired confidence interval.
- The recorded canary maximum, 0.5620 AUC, is a feature-only association diagnostic—not DTI and not a complete proof that the requested leakage protocol was met. It remains below the user’s 0.90 stop threshold, but the protocol mismatch is not waived.

No code was changed to rerun or retrofit the experiment. A private-fork workaround would not repair those provenance gaps; the 3-experiment cap and exact-file STOP remain binding.

## Pass 2 — independent exact-file, grid, and duplicate-stop audit

Added `scripts/audit_xfcoh31_registry_stop.py` to re-read the exact TIFF, template, pinned manifest, and witness, validate local format, calculate full-footprint average-tie Spearman rho, and test final-dot distance to the witness. The script is read-only for model/TIFF bytes; `--check-record` recomputes and compares the committed JSON receipt.

**Local format-only result:** one float32 band; EPSG:32611; 3730 × 3292; exact 100 m template transform; 5,167,373 footprint pixels; 37,654 positive dots; zero nonfinite footprint pixels; all values in [0,1]; outside pixels zero. The local validator reports no hard failures under the all-finite convention. This is not organizer acceptance.

**HOLDOUT-DTI** (`gemsdoe31-holdout-v1`, 58,625 withheld positives; pooled DTI; 1,000 spatial-block bootstrap resamples over 186 blocks):

- XFCOH31: `0.0458814`, 95% CI `[0.0411819, 0.0511205]`.
- Same-run base-19 control: `0.0481217`, 95% CI `[0.0436109, 0.0529829]`.
- Paired XFCOH31 minus base-19: `-0.0022403`, 95% CI `[-0.0048284, 0.0001154]` — negative efficacy result.

**Exact final-dot shared-registry result:**

- Pinned manifest `registry/shared_registry_57_snapshot.json`, SHA-256 `846eddb9459f0e5b67f33da519bbd62c966bf5f539545ba3dad262fbfbc308c2`, contains 695 rasters.
- Examined one authenticated witness, `r13-lattice-s5`, SHA-256 `b4570b406efec198eb2f4d142ad8d0d6184b14b66f2f52b5c4d697f0647dc9b2`.
- Full-footprint Spearman rho `0.0004222482` (absolute limit 0.90: pass).
- Dots within 3 px: `37,560 / 37,654 = 99.7504%` (limit 70%: fail).
- **Literal result: STOP; no global uniqueness approval; DO NOT SUBMIT.** A calibration label does not exempt a raster under the standing “any registry raster” rule. This is not a byte-identity finding.

This is one witness, not an exhaustive 695-raster scan. The broad pre-placement surface check was not performed for this existing run. One authentic final-dot counterexample is sufficient to stop; no full-registry pass is claimed and no follow-on placement was run. The focus-site comparator table (maximum sampled rho 0.0870, maximum 3-px overlap 30.6528%) remains a limited subset only.

## Pass 3 — full acceptance, reporting, and reproducibility checks

Updated the XFCOH31 evidence card to include confidence intervals, literal registry audit, protocol deviations, decision fields, and explicit subset scope. Rebuilt the XFCOH31 page, home page, executive summary, research page, machine-readable feed and submission registry so the active reviewed lane is XFCOH31 while H31-S and MAGREST remain separate. Added an open irregularity entry, current status, README pointers, and regression tests. The existing TIFF bytes were not rewritten.

Final local checks:

- `scripts/verify_current_run.py --restore-small-inputs`: MAGREST remains negative, research-download-only, not approved to submit; SHA-256 `c101ceb7237df0890a0f650b4211cc501250b47c1ab9cfeca8ee4cb373eb48d9`.
- `scripts/verify_h31j.py` and `scripts/verify_h31t.py`: both verified their separate existing records; neither result is attributed to XFCOH31.
- `scripts/audit_xfcoh31_registry_stop.py --check-record`: exact TIFF/hash/witness receipt matches; literal overlap STOP reproduced.
- `pytest`: **145 passed** after rebasing onto current `origin/main`.
- Ruff: passed; `compileall`: passed.
- `scripts/check_metric.py`: maximum fast/brute DTI difference `4.441e-16` over 24 grids; 29 triangular-kernel offsets inside 300 m.
- `scripts/collect_evidence.py`: 159 evidence artifacts inventoried; 13 submission-register files; `active_review_lane` identifies XFCOH31 separately from the MAGREST technical current run.
- `scripts/build_site.py`: 22 pages and 5 data files generated.
- `scripts/check_site.py`: 22 pages, 466 local links; passed. Site checks also enforce the active XFCOH31 stop, explicit no-submit status, and separate H31-S/MAGREST run references.
- Ignored competition inputs/caches are not tracked; `git diff --check` passed.

No non-GitHub official page was freshly retrieved in this environment. Official-source URLs remain references, and no DrivenData page or leaderboard was accessed. No submission, score entry, organizer contact, or selector action occurred.

## Acceptance matrix and next permitted action

| Requirement | Review outcome |
|---|---|
| Nine-site summary and H33-2-B2 claim | Present; all competition values labeled USER-REPORTED absent receipts. |
| Three-to-five ranked novel hypotheses | Five hypotheses retained; only XFCOH31 was run, with a negative verdict. |
| Spatial holdout and feature canary reporting | Results and evaluator/count/CI are shown; workflow/canary provenance gaps are explicitly disclosed. |
| Exact file and automated format validation | Existing file hash and local format checks reverified. |
| Registry uniqueness | Literal exact-file overlap STOP; focus-site subset is not global approval. |
| Download-versus-submit decision | Research download YES; submit NO; slot not approved. |
| New file or further experiment after STOP | None. |
| Official scores/organizer acceptance | None claimed. |

Next work is blocked until the protocol owner resolves the literal registry rule in writing and explicitly authorizes a future method lane. Do not scrape DrivenData, make a density/calibration exemption, run a fourth XFCOH31 experiment, place new dots, generate a new TIFF, or spend a slot under the current decision.
