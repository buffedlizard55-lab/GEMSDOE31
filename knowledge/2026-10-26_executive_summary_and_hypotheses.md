# Historical executive summary — 2026-10-26 (CONCORD31 session)

> **Archive/status note:** this is a report from a separate CONCORD31 session, not the current run. The authoritative active run is MAGREST in [`registry/current_run.json`](../registry/current_run.json), downloadable for research only and not approved to submit. CONCORD31's local subset check did not establish broad/global uniqueness; the shared spacing-5 witness remains a binding STOP. See [`knowledge/current_status_2026-10-26.md`](current_status_2026-10-26.md) for current blockers and status.

## Historical session decision — read as an archive
**NO file — old or new — is OK TO SUBMIT this session.** Automated gates, not a human inspector, decide this.
- ✅ **OK to download for research (portal-safe encoding):** `docs/downloads/gemsdoe31-concord31-minbd-concordance-28115-20261026-allfinite.tif` — values strictly {0,1} ⊂ [0,1], 0 NaN inside footprint, zeros outside (this all-finite encoding is the fix for the portal error *"Predicted values must be in range [0, 1]"*: a NaN-outside file read whole-raster contains NaN ∉ [0,1]).
- ❌ **DO NOT SUBMIT it:** its HOLDOUT-DTI and leakage canary are **NOT RUN** (truth/catalogue rasters absent, see Irregularities). Protocol: never spend a weekly slot on an idea that hasn't beaten the holdout best.
- ❌ **DO NOT submit any of the 9 historical "best" files below as a "new" entry:** each is >86% within 3 px of H33 (duplicate lane, §2).

## 1. The 9 focus sites — highest listed claim each (all USER-REPORTED, no organizer receipt exists for any)
| Site | Highest artifact | Claim | Dots | vs H33 (3-px) | Verdict |
|---|---|---|---|---|---|
| GEMSDOE32 | h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros | **0.2778** | 37,654 | 100% (itself) | Best *claim*; NOT unique-submittable (it IS the reference) |
| GEMSDOE36 | anderson-geothermal-pinn-38854 | 0.2750 | 38,854 | 97.4% | Duplicate of H33 lane |
| GEMSDOE28 | h36-1-rung30-blind-r1 (also h27-4 0.2708) | 0.2710 | 37,660 | 95.5% | Duplicate |
| GEMSDOE31 | h27-4-solo-d28 | 0.2708 | 40,199 | 95.4% | Duplicate; also conflicts with pinned page "unscored" (`registry/irregularities.json`) |
| GEMSDOE33 | h33d-analog-tip-stepover-r30 | 0.2632 | 41,865 | 92.6% | Duplicate |
| GEMSDOE25 | dotted-h19-5-d2-8 | 0.2600 | 44,090 | 88.2% | Duplicate |
| GEMSDOE30 | d28-poisson300m-offcat-44090 | 0.2600 | 44,090 | 88.2% | Duplicate (D2.8 replay) |
| GEMSDOE24 | h25-1-dotted-h19-5-d1-5 | 0.2477 | 60,069 | 88.5% | Duplicate |
| GEMSDOE27 | topo-gap-closure-t-v2-on-d1-5 | 0.2449 | 61,328 | 86.7% | Duplicate |
Source: `docs/data/h33-forensics.json`, `evidence/nine_site_forensic_audit.json` (measured in-repo). **"Best submission to submit for a high score" = none of these** — resubmitting any is a duplicate, not a strategy.

## 2. H33 geometry and a plausible metric mechanism (not causal proof)

Byte geometry in `docs/data/h33-forensics.json` records the raster relation: H33 equals D2.8 after deleting dots within 2 px (200 m) of the public catalogue; H27 uses a 1-px collar. H33 adds no dots to H27 and removes 2,545 in the 100–200 m band. This is **not new fault discovery**. Under `DTI = T/(T+αF+βFN)`, a pruning change improves a measured score only when the deleted block's truth-credit loss is small enough relative to removed false-positive cost. For an added block the general threshold is `ΔT/ΔF > αS/(1−αS)`; at `α=0.2`, `S=0.2778`, this is about `0.05882`. In the simplified isolated-pixel case `ΔT+ΔF=1`, the equivalent credit threshold is `ΔT>αS≈0.05556`. These thresholds do not reveal the deleted dots' private-truth credit. No organizer receipt authenticates the supplied `0.2778` claim, so the raster comparison cannot establish why that claimed score changed. The `0.3195` and `0.4413` values are also USER-REPORTED, with no exact-byte organizer receipt. No local holdout or SGMC proxy in this repo is numerically comparable to the private leaderboard.

## 3. Historical CONCORD31 research TIF record — local subset checks only
- **Hypothesis/mechanism:** surface = min(B,D) of the two pinned OOF arms (LiDAR-only × LiDAR+radiometric) in `evidence/oof/`; two-domain concordance → Poisson-disk dots (2.8 px), **zero incumbent dots copied**. Non-fault mimic: coincident LiDAR artefact + radiometric playa/soil-moisture edge.
- **Result:** 28,115 dots; the archived local/pairwise comparison against the checked submission subset recorded max surface |Spearman ρ| = 0.194 and max final 3-px overlap = 49.7% vs union-b. This is **not** broad-registry uniqueness: the literal shared spacing-5 witness blocks any nonempty in-footprint prediction. Local validators passed both encodings (EPSG:32611, 3730×3292, float32, [0,1], 0 NaN in footprint). SHA-256 `e7463b56aedc30263a08e9318bd8f336ab424f2c236734017e5b5cba75b89882`.
- **Historical artifact identifier (not an approved submission name):** `gemsdoe31-concord31-minbd-concordance-28115-20261026` · archived note: "CONCORD31 min(B,D) concordance dots 37.6k, no incumbent dots; UNVALIDATED holdout - research only" (`evidence/concord31/run_card.json`).
- **Verdict: negative** (format passed locally; broad uniqueness STOP; efficacy untested). Full JSON run card: `evidence/concord31/run_card.json`.

## 4. Historical hypothesis notes (not the active backlog or experiment authorization)

The first item below was run as CONCORD31 and lacked holdout evidence; the other ideas remain speculative and unvalidated. The current README's three-item desk backlog is the relevant present summary. The source URLs below were not re-fetched during this current review.

1. **CONCORD31 min(B,D)** (OOF arms B/D · min-concordance hypothesis · two sensor domains might agree on structure not represented by the mapping catalogue · never emitted standalone) — run above; holdout blocked. Cost: historical run completed.
2. **Antislope LiDAR scarp × K–Th alteration edge** (upface/downface + GeoDAWN K,Th · candidate signature: uphill-facing scarp and K-depletion edge · possible blind/young-fault signal; AS-1 used antislope alone) — would require GeoDAWN stack in `data/` (source lead: https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and).
3. **Gravity tilt-zero × RTP bandpass crest** (iso_grav + rtp · possible basement-step lineament · H31-M tested a broader bundle; a minimal pair was not tested) — requires restoring `data/` stack.
4. **GDR volcanics/probe-envelope edge** (GDR-1391 layers · possible dots at envelope edges) — speculative, not validated; source lead: https://gdr.openei.org/submissions/1391.
5. **Relay-ramp/stepover dilation dots** (QF v2 + LiDAR curvature · possible between-segment jogs) — speculative, needs stack and segment analysis; highest historical effort estimate.

## 5. How to submit (only a future gate-passing file)
DrivenData competition 306 → Submit → single-band GeoTIFF or ZIP-of-one-TIFF matching sample CRS/shape/transform → use the **all-finite** file → paste the run card's name/note → disclose AI use per rules (https://docs.nlr.gov/docs/fy26osti/96647.pdf). Local validation ≠ organizer acceptance.

## Irregularities flagged
1. 0.2778/0.2708/0.3195/0.4413: all USER-REPORTED, zero organizer receipts; GEMSDOE31's own pinned page lists H27-4 as unscored.
2. `data/` truth/catalogue/SGMC rasters absent; Dropbox + DrivenData hosts unreachable from sandbox → HOLDOUT-DTI + leakage canary NOT RUN for CONCORD31 (named missing inputs: labels/existing_faults/SGMC + GeoDAWN stack via `scripts/download_competition_data.sh` on an unrestricted machine).
3. Shared-registry 5-px calibration lattice makes the literal >70%-within-3px rule fire on ANY dot set (repo-registered degeneracy) — CONCORD31 was screened against local submission rasters only; global uniqueness NOT proven.
4. pytest not installed in sandbox venv — repo test suite not re-run this session (validator + registry gates were run directly).
