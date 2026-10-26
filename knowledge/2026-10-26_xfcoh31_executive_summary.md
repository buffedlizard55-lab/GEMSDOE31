# Executive summary — nine-site claims and the XFCOH31 final decision (2026-10-26)

## Decision first

**DOWNLOAD FOR RESEARCH: YES. SUBMIT: NO — DO NOT SUBMIT.** The existing XFCOH31 all-finite TIFF is locally format-valid, but its recorded HOLDOUT-DTI result is negative against the same-run control and a read-only exact-file audit finds **37,560 of 37,654 dots (99.7504%) within 3 pixels** of one authentic pinned shared-registry raster. The user’s literal 70% rule therefore triggers STOP. The older focus-site comparator table is a limited subset, not global uniqueness approval. No new experiment, placement, TIFF, upload, or weekly slot followed this audit.

The TIFF remains downloadable only as a research artifact:

- File: [`docs/downloads/gems31-xfcoh31-xfield-coherence-37654-20261026-zeros.tif`](../docs/downloads/gems31-xfcoh31-xfield-coherence-37654-20261026-zeros.tif)
- SHA-256: `857dd662430c0130c46f920666d70dae5df6148951ad76d42d31a8d540c32972`
- Machine run card: [`evidence/xfcoh31_run_card.json`](../evidence/xfcoh31_run_card.json)
- Exact-file audit: [`evidence/xfcoh31_registry_stop_audit.json`](../evidence/xfcoh31_registry_stop_audit.json)
- Generated decision page: [`docs/xfcoh31.html`](../docs/xfcoh31.html)

This is not the H31-S file or the MAGREST file. Their separate evidence and prior decisions remain unchanged: H31-S is in `registry/h31s_current_run.json`; MAGREST is in `registry/current_run.json`.

## Nine-site best-claim summary

Every competition score below is **USER-REPORTED**; no exact-byte organizer receipt is present in this repository. The ranking is a summary of supplied claims, not an organizer-confirmed leaderboard result.

| Site | Best supplied artifact / claim | USER-REPORTED score | Dots |
|---|---|---:|---:|
| GEMSDOE24 | h25-1-dotted-h19-5-d1-5 | 0.2477 | 60,069 |
| GEMSDOE25 | dotted-h19-5-d2-8 | 0.2600 | 44,090 |
| GEMSDOE27 | topo-gap-closure-t-v2-on-d1-5 | 0.2449 | 61,328 |
| GEMSDOE28 | h36-1-rung30-blind-r1 | 0.2710 | 37,660 |
| GEMSDOE30 | d28-poisson300m-offcat-44090 | 0.2600 | 44,090 |
| GEMSDOE31 | h27-4-solo-d28 | 0.2708 | 40,199 |
| GEMSDOE32 | h33-h33-2-b2 | **0.2778** | 37,654 |
| GEMSDOE33 | h33d-analog-tip-stepover-r30 | 0.2632 | 41,865 |
| GEMSDOE36 | anderson-geothermal-pinn | 0.2750 | 38,854 |

The highest supplied claim is GEMSDOE32 H33-2-B2 at **USER-REPORTED 0.2778**, not ORGANIZER-CONFIRMED. The nine-site bytes and lineage are documented in `evidence/nine_site_forensic_audit.json` and `evidence/xfcoh31_focus_fetch.json`.

### What the H33-2-B2 geometry suggests — not a score explanation

Byte-level set algebra identifies H33-2-B2 as the D2.8 sparse-dot geometry after removing the catalogue-flank halo, leaving 37,654 dots. The official metric’s 300 m triangular kernel can make that pruning economically plausible: redundant dots still incur false-positive cost while adding little new truth coverage. This is a **COMPUTED geometric mechanism hypothesis**, not proof of why the hidden competition result was 0.2778; the hidden truth and an organizer score receipt are not available here.

## Ranked novel hypotheses

These are research hypotheses, not score projections. No expected score gain is assigned.

1. **XFCOH31 cross-field edge-transfer coherence — executed; negative.** Align RTP magnetic and gravity/depth gradient magnitudes, orientation, and small lateral offsets to find buried basement-displacement faults. Named non-fault mimic: unfaulted pluton or basin-fill contacts shared by both fields, plus survey-levelling seams. The holdout and global registry gates below fail.
2. **Radiometric channel-specific edge displacement — not run.** Compare offset K/Th/U edges with gravity/magnetic contacts to test hydrothermal alteration along concealed damage zones. Mimics: lithologic boundaries and radiometric survey seams.
3. **Piedmont drainage-deflection asymmetry — not run.** Extract channel bends and fan-apex alignments from USGS 3DEP elevation data to find faults without preserved scarps. Mimics: avulsion, roads, canals, and natural fan-lobe boundaries.
4. **Flight-line seam persistence null — not run.** Test whether apparent cross-field edges persist across independent survey lines before interpreting them as faults. Mimic: levelling seams and acquisition-line offsets.
5. **Seismicity alignment — not run.** Test whether independent earthquake alignments add support to concealed traces. Mimics: mining seismicity and location error larger than the scoring kernel.

## XFCOH31 HOLDOUT-DTI and canary evidence

**HOLDOUT-DTI** (`gemsdoe31-holdout-v1`, 58,625 withheld positive pixels; pooled DTI, alpha 0.2, beta 0.8, 300 m triangular kernel; 1,000 spatial-block bootstrap resamples over 186 blocks):

| Arm | HOLDOUT-DTI | 95% CI |
|---|---:|---:|
| XFCOH31 | 0.0458814 | [0.0411819, 0.0511205] |
| Same-run base-19 control | 0.0481217 | [0.0436109, 0.0529829] |
| Paired XFCOH31 minus base-19 | -0.0022403 | [-0.0048284, 0.0001154] |

The candidate did not beat its same-run control; the preregistered efficacy gate is negative. These are HOLDOUT-DTI values, not a competition score or projection.

The recorded feature-only canary maximum is **AUC 0.5620** (nine novel features, each tested individually against visible catalogue labels on one 400,000-pixel footprint sample; not DTI). This is below the 0.90 stop threshold, but it is **not** the preregistration’s described per-fold withheld-truth canary and is not sufficient to claim that the requested leakage protocol was satisfied.

The spatial evaluator does use the shared `gemsdoe31.holdout` and `gemsdoe31.metric` code: whole 8-connected fault components are assigned by quadrant, a fixed 21.25 km collar is applied, visible catalogue pixels are masked pixel-exactly, and pooled DTI uses the shared metric. The collar was inherited from the shared template rather than re-estimated specifically for XFCOH31. Review of `scripts/run_xfcoh31.py` also found these workflow deviations:

- It reads `training_features.tif` and constructs a fresh `.cache/xfcoh_X.f32` stack instead of reusing the template’s cached stack.
- It calls holdout module functions directly rather than the requested `evaluate_holdout.py` workflow wrapper.
- It writes the TIFF and ZIP directly through Rasterio/`zipfile`, bypassing the requested shared `submission_writer.py`.
- It tests the nine feature-only canaries against visible catalogue labels, not the preregistration’s stated fold-pooled withheld truth.
- The committed result JSON retains pooled values and bootstrap summaries, but not per-block sufficient statistics needed to independently replay the paired confidence interval.

These compliance gaps are recorded rather than repaired by a private fork. The experiment budget is spent and the final-file registry STOP is binding; no rerun is authorized.

## Exact-file shared-registry audit

The check used the exact final TIFF and the pinned 695-raster manifest `registry/shared_registry_57_snapshot.json` (manifest SHA-256 `846eddb9459f0e5b67f33da519bbd62c966bf5f539545ba3dad262fbfbc308c2`). One authenticated manifest entry is sufficient to trigger the existential STOP; this was **one witness examined, not an exhaustive 695-raster scan**.

- Witness: `r13-lattice-s5`, SHA-256 `b4570b406efec198eb2f4d142ad8d0d6184b14b66f2f52b5c4d697f0647dc9b2`.
- Exact full-footprint Spearman rho: `0.0004222482` (absolute limit 0.90, so correlation passes).
- Final dots within 3 px: `37,560 / 37,654 = 99.7504%` (limit 70%, so overlap fails).
- Result: **literal registry STOP; global uniqueness is not established; DO NOT SUBMIT.**
- The broad pre-placement surface check was not performed. The existing final-dot failure suffices; no new surface search or placement followed.

The witness is a calibration raster, but the standing project rule applies to **any** registry raster. No density, calibration, or “non-submission control” exemption is used. This is not a byte-identity finding: it is a measured 3-pixel overlap stop.

## Format validation is a separate question

The existing all-finite TIFF is one-band float32 on EPSG:32611, shape 3730×3292, exact 100 m template transform, with 37,654 positive dots, zero nonfinite cells, and values in [0,1]. The local all-finite format receipt has no hard failures. Its NaN-outside twin also has a separate local format receipt. **Neither receipt is organizer acceptance, uniqueness approval, nor submission permission.**

- Submission name: `gems31-xfcoh31-xfield-coherence-37654-20261026`
- Existing note: 110/140 characters (research identification only)
- Research download: **YES**
- Submission/promotion/weekly slot: **NO / NEGATIVE / DO NOT SUBMIT**

## Sources and verification limits

Official-source links recorded for manual review include the DrivenData competition page (`https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/`), the NLR rules PDF (`https://docs.nlr.gov/docs/fy26osti/96647.pdf`), the organizer reference-solution GitHub repository (`https://github.com/drivendataorg/gems-prize-reference-solution`), USGS GeoDAWN (`https://doi.org/10.5066/P93LGLVQ`), and EPSG:32611 (`https://epsg.io/32611`). Non-GitHub hosts were not freshly fetched in this restricted environment; URLs are retained as source references, not claimed as newly verified. No DrivenData leaderboard access, score submission, or organizer contact occurred.
