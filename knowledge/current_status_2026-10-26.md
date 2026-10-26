# Current project status — 2026-10-26 (XFCOH31 final review)

## Decision

**No competition submission is approved.** The active lane reviewed here is XFCOH31. Its existing GeoTIFF remains **OK TO DOWNLOAD FOR RESEARCH: YES · SUBMIT: NO — DO NOT SUBMIT**. No experiment, model fit, placement, TIFF, upload, leaderboard access, or weekly slot was used after the exact-file registry STOP.

- Existing TIFF: [`docs/downloads/gems31-xfcoh31-xfield-coherence-37654-20261026-zeros.tif`](../docs/downloads/gems31-xfcoh31-xfield-coherence-37654-20261026-zeros.tif)
- SHA-256: `857dd662430c0130c46f920666d70dae5df6148951ad76d42d31a8d540c32972`
- Decision page: [`docs/xfcoh31.html`](../docs/xfcoh31.html)
- Machine run card: [`evidence/xfcoh31_run_card.json`](../evidence/xfcoh31_run_card.json)
- Exact-file audit: [`evidence/xfcoh31_registry_stop_audit.json`](../evidence/xfcoh31_registry_stop_audit.json)
- Three-pass review: [`knowledge/session_review_2026-10-26_xfcoh31.md`](session_review_2026-10-26_xfcoh31.md)

## Independent reasons for the negative verdict

1. **HOLDOUT-DTI efficacy gate failed.** Under `gemsdoe31-holdout-v1`, with 58,625 withheld positives, XFCOH31 scored `0.0458814` (95% CI `[0.0411819, 0.0511205]`) versus the same-run base-19 control `0.0481217` (95% CI `[0.0436109, 0.0529829]`). Paired Δ was `-0.0022403` (95% CI `[-0.0048284, 0.0001154]`). These are HOLDOUT-DTI values, not competition scores.
2. **Literal shared-registry uniqueness gate failed.** Exactly 37,560 of 37,654 final dots (99.7504%) fall within 3 px of the pinned `r13-lattice-s5` raster. Full-footprint Spearman rho is `0.0004222482`, which passes its 0.90 limit; overlap fails the 70% limit. The witness is one authenticated raster in a pinned 695-raster manifest. This is sufficient for STOP but is not an exhaustive scan. No density/calibration exemption is applied.
3. **Requested workflow compliance is incomplete.** The recorded script built a fresh feature memmap rather than reusing the cached stack, wrote TIFF/ZIP directly rather than via `submission_writer.py`, called holdout module functions instead of the requested `evaluate_holdout.py` wrapper, and used a feature-only canary against visible catalogue labels rather than the preregistration’s described fold-pooled withheld-truth canary. The fixed 21.25 km collar was inherited, not re-estimated for XFCOH31. The saved results do not contain per-block statistics needed to independently replay the confidence interval. No private fork or post-cap rerun is authorized.

**Format status is separate:** the existing all-finite GeoTIFF passes local grid, datatype, range, and outside-zero checks. This proves neither uniqueness, promotion eligibility, nor organizer acceptance. The previous focus-site subset result (max 0.087 Spearman; max 30.65% 3-px overlap) is scoped only to those named genuine submissions and is not global uniqueness approval.

## Distinct records — do not conflate

- `registry/h31s_current_run.json` and `evidence/h31s/run_card.json` describe the separate H31-S (UDAP-SSLIC) run; its own research-only status remains unchanged. The prior H31-S review and measured results remain documented in [`knowledge/repo_review_2026-10-26.md`](repo_review_2026-10-26.md) and its dedicated run card.
- `registry/current_run.json` and `docs/downloads/magrest-run-card.json` describe the separate MAGREST run; its own negative decision remains unchanged.
- `evidence/xfcoh31_run_card.json` and `evidence/xfcoh31_registry_stop_audit.json` describe XFCOH31 only. Its scores, raster hash, and STOP are not attributed to H31-S or MAGREST.

## Score claims and scientific status

GEMSDOE32 H33-2-B2 at `0.2778` remains **USER-REPORTED**; no organizer receipt is present. The nine-site summary, including GEMSDOE24/25/27/28/30/31/32/33/36 and ranked future hypotheses, is in [`knowledge/2026-10-26_xfcoh31_executive_summary.md`](2026-10-26_xfcoh31_executive_summary.md). It treats the score as an unverified claim and distinguishes it from HOLDOUT-DTI.

The XFCOH31 run used three experiments (feature canary, holdout, final fit). The experiment cap is spent. **Do not add a fourth experiment, re-place dots, or create another TIFF in this lane.** The final audit wrote a JSON receipt only.

## Verification and next work

The three review passes and their automated checks are recorded in [`registry/review_passes.json`](../registry/review_passes.json). The exact-file audit is reproducible with:

```sh
python scripts/verify_current_run.py --restore-small-inputs
python scripts/audit_xfcoh31_registry_stop.py --check-record
python -m pytest -q
python -m ruff check .
python scripts/collect_evidence.py
python scripts/build_site.py
python scripts/check_site.py
```

Future research is blocked pending written protocol-owner resolution of the literal overlap rule and explicit method-lane authorization. Obtain organizer-authenticated template/rules/score receipts only through permitted access; do not scrape DrivenData, upload automatically, spend a weekly slot, or treat a local proxy as a competition score. H31-S and MAGREST remain separate historical run records while this lane’s decision is negative.
