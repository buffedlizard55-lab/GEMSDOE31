# Executive summary — 2026-10-26 (CONCORD31 session)

> **Historical CONCORD31 snapshot, not the current run status.** This note records the earlier CONCORD31 session only. The later repository status and active run card supersede any “this session” or file-readiness wording below: [current status](current_status_2026-10-26.md), [current MAGREST run card](../registry/current_run.json), [latest repo review](repo_review_2026-10-26.md). No file is approved to submit.

## ⛔ BOTTOM LINE — read this first
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

## 2. Why H33-2-B2 (0.2778, USER-REPORTED) leads — PhD-level answer
Measured byte geometry (`docs/data/h33-forensics.json`): **H33 = D2.8 dots with every dot ≤2 px (≤200 m) from the public catalogue deleted; H27 = same prune at ≤1 px.** H33 adds 0 dots vs H27, removes 2,545 flank dots, keeps all 35,483 dots >300 m away. It is *pruning economics, not new fault discovery*: with DTI = T/(0.2T+0.2F+0.8K), a binary dot costs F≈1−(self kernel credit) whether or not it hits truth, while truth credit saturates via the 300 m triangular kernel's max. Deleting near-catalogue dots (whose kernel credit largely overlaps already-mapped — and in the hidden set likely masked/duplicate — traces) cuts F faster than T. Formally pruning improves DTI S iff `lost_T < [0.2S/(1−0.2S)]·removed_F`. Sparse (≥~300 m median spacing), thin, off-catalogue dots therefore beat every thick/dense/on-catalogue raster in the table (0.0009–0.19 range for dense ML fills). **Can we beat 0.2778?** Only by finding *new true* off-catalogue traces at the same sparse budget — every in-repo attempt (H31-E, HVDC, RBU31, MAGREST, TGJ31, CONCORD31 below) is either holdout-negative or holdout-unvalidated, so **no verified path above 0.2778 exists yet**; claiming one would be fabrication. The prompt's "leaderboard 0.3195 / 0.4413" figures are likewise USER-REPORTED with no exact-byte organizer receipt — flagged, not used as targets.

## 3. New unique TIF generated this session — CONCORD31 (experiment 1 of max 3)
- **Hypothesis/mechanism:** surface = min(B,D) of the two pinned OOF arms (LiDAR-only × LiDAR+radiometric) in `evidence/oof/`; two-domain concordance → Poisson-disk dots (2.8 px), **zero incumbent dots copied**. Non-fault mimic: coincident LiDAR artefact + radiometric playa/soil-moisture edge.
- **Result:** 28,115 dots; **registry gate PASS** (local scope): max surface |Spearman ρ| = 0.194 ≤ 0.90, max final 3-px overlap = **49.7%** (vs union-b) ≤ 70% — checked on surface AND final dots. Validator PASS both encodings (EPSG:32611, 3730×3292, float32, [0,1], 0 NaN in footprint). SHA-256 `e7463b56aedc30263a08e9318bd8f336ab424f2c236734017e5b5cba75b89882`.
- **Submission name:** `gemsdoe31-concord31-minbd-concordance-28115-20261026` · **Note (≤140):** "CONCORD31 min(B,D) concordance dots 37.6k, no incumbent dots; UNVALIDATED holdout - research only" (`evidence/concord31/run_card.json`).
- **Verdict: negative** (format+uniqueness pass; efficacy unproven). Full JSON run card: `evidence/concord31/run_card.json`.

## 4. Five ranked untried hypotheses (layer · signature · why catalogue-missing · what's new)
1. **CONCORD31 min(B,D)** (OOF arms B/D · min-concordance · two sensors agreeing implies real structure the single-sensor catalogue mapping missed · never emitted standalone) — DONE above, holdout blocked. Cost: done.
2. **Antislope LiDAR scarp × K–Th alteration edge** (upface/downface + GeoDAWN K,Th · uphill-facing scarp AND K-depletion edge · blind/young faults displace topography + host alteration without mappable trace · AS-1 used antislope alone) — needs GeoDAWN stack in `data/` (official USGS GeoDAWN, free, no account: https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and — obtainable, just not from this sandbox).
3. **Gravity tilt-zero × RTP bandpass crest** (iso_grav + rtp · basement-step lineament · basement reactivation under cover · H31-M bundled it with 6 others & hit registry STOP; minimal pair untested) — needs `data/` stack.
4. **GDR volcanics/probe-envelope edge** (GDR-1391 layers · dots at envelope edge where flow focuses · direct fluid evidence, often unmapped · unused as emission domain; free official: https://gdr.openei.org/submissions/1391) — needs stack restore.
5. **Relay-ramp/stepover dilation dots** (QF v2 + LiDAR curvature · between-segment jogs · catalogue maps traces, not jogs · untested) — needs stack + segment analysis. Highest cost, ranked last.

## 5. How to submit (only a future gate-passing file)
DrivenData competition 306 → Submit → single-band GeoTIFF or ZIP-of-one-TIFF matching sample CRS/shape/transform → use the **all-finite** file → paste the run card's name/note → disclose AI use per rules (https://docs.nlr.gov/docs/fy26osti/96647.pdf). Local validation ≠ organizer acceptance.

## Irregularities flagged
1. 0.2778/0.2708/0.3195/0.4413: all USER-REPORTED, zero organizer receipts; GEMSDOE31's own pinned page lists H27-4 as unscored.
2. `data/` truth/catalogue/SGMC rasters absent; Dropbox + DrivenData hosts unreachable from sandbox → HOLDOUT-DTI + leakage canary NOT RUN for CONCORD31 (named missing inputs: labels/existing_faults/SGMC + GeoDAWN stack via `scripts/download_competition_data.sh` on an unrestricted machine).
3. Shared-registry 5-px calibration lattice makes the literal >70%-within-3px rule fire on ANY dot set (repo-registered degeneracy) — CONCORD31 was screened against local submission rasters only; global uniqueness NOT proven.
4. pytest not installed in sandbox venv — repo test suite not re-run this session (validator + registry gates were run directly).
