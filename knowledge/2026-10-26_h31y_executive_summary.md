# Executive summary — nine focus sites, best file to submit, and the new H31-Y lane (2026-10-26, session a111fe50)

Every leaderboard-style number is **USER-REPORTED** (owner-typed; no organizer receipt exists in any
repo) unless labelled **HOLDOUT-DTI** (computed locally, never a leaderboard score) or **PROJECTION**
(an estimate, never a score). No ORGANIZER-CONFIRMED score exists. This repo never contacts DrivenData.

## 1. The one obvious answer

| Decision | File | Hash / portal note | Evidence (labelled) | Estimated live score |
|---|---|---|---|---|
| **SUBMIT THIS** | `docs/downloads/gemsdoe31-h31x-piedmont-junction-37654-20261026-5a956da9-zeros.tif` | SHA-256 `eff2b18e…17f9`; name `gemsdoe31-h31x-piedmont-junction-37654-20261026-5a956da9`; note (88/140) in §5 | HOLDOUT-DTI **0.1661 [0.1499, 0.1821]** (gems57-pooled-hide-v2, 60,988 withheld), independently reproduced this session (arm Y2 = 0.1661); SGMC 0.1209 vs H33 0.0940 (COMPUTED); unique: 57.0% of dots within 3 px of H33, max vs any discrete peer 63.1% (limit 70%) | **UNKNOWN.** Old 0.355 withdrawn (§3). Corrected PROJECTION: M3 cross-family central **0.125**, interval **[−0.061, 0.311]**; M1 in-family diagnostic 0.355 (upper bound only if it behaved exactly like the H19-5 family) |
| **DO NOT SUBMIT** (new this session) | `docs/downloads/gemsdoe31-h31y-regime-mosaic-37654-20261026-66162f1f-zeros.tif` | SHA-256 `41f1e63a…901e`; reserved note (101/140) ends `DO-NOT-SUBMIT` | HOLDOUT-DTI 0.1550 [0.1401, 0.1701]; beats CTRL/SLOPE (CIs exclude 0), **loses to junction comparator** −0.0112 [−0.0191, −0.0024]; piedmont subgroup 0.0684 vs 0.0203; SGMC 0.0873 < H33 0.0940; unique: max 59.4% (vs H31-X), 45.9% vs H33, \|ρ\| 0.135 | PROJECTION: M3 central 0.125, interval [−0.061, 0.311]; M1 diagnostic 0.255. Verdict **negative** (gates G3/G4 fail) — research download only |
| Gated alternates (earlier selector audit, estimates withdrawn) | H31-T `…h31t-transtension-dinkelbach-20261025-b37654-zeros.tif`; H31-J `…tgtd-submod-37654-20261025-ab35d4e8-zeros.tif`; H31-M `…h31m-bstep-xmod-submod-20261025-37654-allfinite.tif` | hashes in `registry/selector_decision_20261026.json` | Passed the earlier uniform gate audit on format/canary/holdout/SGMC/uniqueness; H31-T 34.1% vs H33 (lowest overlap alternate) | UNKNOWN (their 0.317/0.312/0.296 M1 values withdrawn as score estimates, §3) |

Submit at most one file per weekly slot (competition allows 3/week; see rules in §5). If the owner
prefers maximum distance from H33 over maximum holdout margin, H31-T is the conservative alternate.

## 2. Nine focus sites — best historical submission each: file, estimated score, unique?

Source: `evidence/nine_site_forensic_audit.json` + `evidence/selector_audit_20261026.json`; peer bytes
re-fetched hash-verified this session (`evidence/regime31/peer_fetch.json`, all `hash_ok=true`).
Overlap = fraction of dots within 3 px of GEMSDOE32 H33-2-B2 (COMPUTED).

| Site | Best historical file (do not resubmit) | Estimated score | Dots | Within 3 px of H33 | Unique new submission? |
|---|---|---:|---:|---:|---|
| GEMSDOE32 | `gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` | **0.2778 USER-REPORTED** | 37,654 | 100% (self) | No — already submitted |
| GEMSDOE36 | `gemsdoe36-anderson-geothermal-pinn-38854-…-9b9ea4e6-zeros.tif` | 0.2750 USER-REPORTED | 38,854 | 97.4% | No — H33 + 1,200 dots |
| GEMSDOE28 | `gems28-h36-1-rung30-blind-r1-…-b531dae0a36f-nan.tif` (also h27-4 0.2708, h38-1 0.2707, h32-1 0.2649) | 0.2710 USER-REPORTED | 37,660 | 95.5% | No — same family |
| GEMSDOE31 (historical) | `gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-allfinite.tif` | 0.2708 USER-REPORTED | 40,199 | 95.4% | No — re-emission of GEMSDOE28 h27-4; superseded by H31-X above |
| GEMSDOE33 | `GEMSDOE33-h33d-analog-tip-stepover-r30-…-cb490425926e.tif` | 0.2632 USER-REPORTED | 41,865 | 92.6% | No — same family |
| GEMSDOE25 | `gems25-dotted-h19-5-d2-8-…-e56ea318af89-nan.tif` | 0.2600 USER-REPORTED | 44,090 | 88.2% | No — D2.8 parent |
| GEMSDOE30 | `gemsdoe30-d28-poisson300m-offcat-44090-…-91eae1ca.tif` | 0.2600 USER-REPORTED | 44,090 | 88.2% | No — identical support to GEMSDOE25 |
| GEMSDOE24 | `gems24-h25-1-dotted-h19-5-d1-5-…-989f59505db1-nan.tif` | 0.2477 USER-REPORTED | 60,069 | 88.5% | No — D1.5 parent |
| GEMSDOE27 | `gems27-topo-gap-closure-t-v2-on-d1-5-…-5512495c6bd1-nan.tif` | 0.2449 USER-REPORTED | 61,328 | 86.7% | No — D1.5 derivative |

All nine are one nested dot family (H19-5 surface → Poisson thinning → catalogue-flank pruning).
The owner's 0.3195 / 0.4413 leaderboard context values are USER-REPORTED; nothing in this repo
evidences reaching them. 0.44 would require ≈8.0k live kernel credit vs H33's ≈5.1k (§4).

## 3. CRITICAL AUDIT FINDING — the previous score estimates were invalid (new this session)

The selector's projections (H31-X 0.355 ±0.006, H31-B 0.409, H31-T 0.317 …) came from fitting
`live ≈ 0.9275·SGMC_TPw/(10694.6+0.2n)` on eleven anchors from the single H19-5 family. Tested
out-of-family on all 67 other matched submissions (`scripts/cross_family_calibration.py` →
`evidence/cross_family_calibration_20261026.json`):

- Selector formula (frozen constants): **RMSE 0.196, bias +0.135** — e.g. GEMSDOE46
  r12 (SGMC-DTI 0.164) projected 0.484, actual USER-REPORTED 0.0843; gate_ortho projected
  0.384, actual 0.2376; literal SGMC rasters project to 1.67–2.34 (impossible), actual 0.036–0.051.
- Best cross-family calibration (M3: SGMC credit/dot + coverage + log dots, LOO): RMSE **0.090**,
  barely better than predicting the mean (0.092).
- **Conclusion: no local proxy can estimate a new family's live score tighter than ≈±0.09.**
  SGMC faults are geologic-map traces concentrated in bedrock ranges (median slope 13.5°); the
  hidden expert set is newly mapped faults missing from the USGS Quaternary database (official
  problem page, §6) — a different population. All M1 projections are withdrawn as score estimates;
  promotion now rests on catalogue hide-and-recover + uniqueness + format evidence. Full audit:
  `knowledge/2026-10-26_h31y_projection_audit.md`.

## 4. Why H33-2-B2 scored 0.2778 (USER-REPORTED), and what beating it requires

Exact-byte lineage (COMPUTED, `evidence/h33_forensics_20261025.json`): H19-5 surface (121,131 px,
0.1922) → D1.5 dots (60,069, 0.2477) → D2.8 Poisson dots (44,090, 0.2600) → delete dots ≤1 px from
the public catalogue (H27-4, 40,199, 0.2708) → delete dots ≤2 px (H33-2-B2, 37,654, 0.2778).
Metric economics: DTI = TPw/(TPw+0.2·FPw+0.8·FNw), 300 m triangular kernel (official page, §6).
For sparse binary dots, score ≈ T/(0.2n+0.8K); a dot pays iff its expected kernel credit
k > 0.2·S = 0.0556 at S=0.2778 (within ≈283 m of uncovered truth). Anchor inversion gives
K ≈ 13.4k hidden pixels and ≈0.004 TPw per catalogue-flank dot — hidden truth is depleted beside
already-mapped faults (the test set is by construction *new* faults), so flank pruning is pure
FP-budget savings: deleting 2,545 halo dots cost ≈10 live TPw and gained +0.0070. The paired
control H36-1 (37,660 dots, 0.2710) shows it is *which* dots, not how many. 0.2778 ⇒ T≈5.1k
(≈38% recall); 0.44 ⇒ T≈8.0k. The remaining lever is purely a better far-field ranking surface.

## 5. How to submit the primary file (exact steps)

1. Download `gemsdoe31-h31x-piedmont-junction-37654-20261026-5a956da9-zeros.tif` from the site
   banner (or its single-TIFF `.zip`). Verify SHA-256
   `eff2b18e37378d0f0a2f5c8e22fc68e7c359ee161114502a985135e03dd217f9`.
2. DrivenData competition 306 → **New submission** → File to submit: that exact file.
   It is single-band float32, EPSG:32611, 3730×3292, values exactly {0,1} ⊂ [0,1], finite
   everywhere — it cannot trigger “Predicted values must be in range [0, 1]”
   (that error class comes from NaN/sentinel/out-of-range values; both encodings are validated
   by `scripts/validate_submission.py`, run this session on H31-Y and previously on H31-X).
3. Note (optional, 88/140): `H31-X X1 piedmont-junction slope-break 37654d B2 | HOLDOUT-DTI 0.1661 n=60988 | 5a956da9`
4. Check weekly quota (rules: up to 3/week; one final selection must serve both prize rounds),
   submit, keep the organizer receipt with the SHA-256. Disclose AI use as the rules require
   (`AI_DISCLOSURE.md`). Until a receipt exists, no score is ORGANIZER-CONFIRMED.

## 6. Official sources (fetched/verified this session)

- Problem description & metric & format: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
  (hidden test = expert-identified faults **not** in the public USGS database; public/private split;
  DTI α=0.2, β=0.8, R=300 m; EPSG:32611, 100 m, float32 in [0,1], null/NaN outside bounds).
- Official rules (prize structure, 3/week, one submission for both rounds, updated test set in round 2):
  https://docs.nlr.gov/docs/fy26osti/96647.pdf
- Reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
- GeoDAWN data: https://doi.org/10.5066/P93LGLVQ · INGENIOUS/GDR 1391: https://doi.org/10.15121/1881483
- Grid: https://epsg.io/32611 · Tversky index: https://en.wikipedia.org/wiki/Tversky_index

## 7. H31-Y run card (JSON, protocol §5 — full card in `evidence/h31y/run_card.json`)

```json
{
  "hypothesis": "Regime-mosaic: mountain faults via piedmont-junction slope-break line, piedmont fan faults via one-sided strike-coherent low-relief LiDAR scarps; 50/50 budget beats either specialist alone",
  "mechanism": "18,827 dots JUNC rank (slope>6°) + 18,827 dots FAN geomean-rank(step_max, |upface-downface|, coh100, relief-inverse) (slope<=6°, JUNC fallback off-LiDAR); Poisson 2.8px; d(catalogue)>2px; NO prior dots/surfaces",
  "non_fault_mimic": "fluvial terrace risers / fan-lobe boundaries; Lahontan shoreline benches; erosional pediment edges",
  "holdout_dti": "HOLDOUT-DTI (gems57-pooled-hide-v2, 60988 withheld): Y3 0.1550 [0.1401, 0.1701]; paired vs CTRL +0.0879 [0.0620, 0.1144], vs junction Y2 -0.0112 [-0.0191, -0.0024]; confirmation seed 3104 (30424 withheld): Y3 0.1406, Y2 0.1501, CTRL 0.0573",
  "correlation_overlap_vs_registry": "discrete peers: max final overlap 0.5939 (H31-X), vs H33 0.459, max |surface Spearman| 0.135, max |dots Spearman| 0.508; diagnostic top-K overlap vs H31-X 0.930 disclosed; literal 695-lattice 0.990 (fails for any nonempty raster, IR-U-02)",
  "raster_sha256": "41f1e63a803950db1f621321d5a26c5d3fbbfcc3999923035f0de8a253f7901e",
  "validator": "both encodings pass all hard checks (vendor submission_writer + local validate_submission, re-run independently): single-band float32 EPSG:32611 3730x3292 exact transform, values {0,1} in [0,1], no NaN inside footprint, min spacing >=2.8px, 0 dots on catalogue",
  "submission_name": "gemsdoe31-h31y-regime-mosaic-37654-20261026-66162f1f",
  "submission_note_101_of_140": "H31-Y Y3 regime-mosaic junc+FAN 50/50 37654d B2 | HOLDOUT-DTI 0.1550 n=60988 | 66162f1f DO-NOT-SUBMIT",
  "verdict": "negative"
}
```

## 8. Limitations and next steps (ranked)

1. **Allocation by marginal credit (next lane, needs fresh preregistration):** Y3's subgroup terms
   imply the optimal mountain:piedmont split is ≈70–80:20–30, not 50:50 (50:50 wins only if hidden
   truth is >57% piedmont vs catalogue 48%). A marginal-credit allocator estimated per fold from
   visible catalogue only could plausibly beat Y2 overall *and* keep most of the 3.4× piedmont gain.
2. **No live feedback yet:** every 0.2xxx anchor is USER-REPORTED and no candidate from this repo's
   recent lanes has an organizer receipt. One manual upload of H31-X (within quota) is worth more
   information than another offline lane: a single labelled live point for a non-H19-5 family would
   anchor the cross-family calibration that currently has RMSE 0.09.
3. KIN (LiDAR facing-direction) remains blocked on undocumented `upface/downface` azimuth semantics;
   TEX (RTP fabric truncation) and drainage-deflection remain costed-but-unrun; InSAR/1 m erf-bank
   remain sandbox-blocked (official free sources named in earlier preregistrations).
4. Final-round caution: round 2 rescoring uses an expert-updated label set (rules §3.6); a single
   submission must serve both rounds. Catalogue-flank pruning optimizes round 1 (new faults only);
   whether round-2 labels include public-catalogue faults is not stated unambiguously in the fetched
   official text — flagged for manual review before the final-selection deadline.
5. Irregularities unchanged: B10 distance-vs-density, B06 tilt-vs-radiometric, sample submission =
   catalogue raster, literal-695 lattice scope (IR-U-02), lane paragraph still absent from the prompt.
