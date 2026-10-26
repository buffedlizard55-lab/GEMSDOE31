# Executive summary — 2026-10-26, session `arena/3ce68fc7-gemsdoe31` (lane H31-X)

Labels: **HOLDOUT-DTI** (evaluator, withheld positives, 95% CI) · **COMPUTED** · **USER-REPORTED** (owner-typed,
no organizer receipt) · **PROJECTION** (estimate, never a score). No ORGANIZER-CONFIRMED score exists in this
repository. This repository never contacts DrivenData; uploading is a manual owner action.

## 1. The one answer: which file to download and submit

| | |
|---|---|
| **File** | [`docs/downloads/gemsdoe31-h31x-piedmont-junction-37654-20261026-5a956da9-zeros.tif`](../docs/downloads/gemsdoe31-h31x-piedmont-junction-37654-20261026-5a956da9-zeros.tif) (all-finite, every cell in [0,1]; single-TIFF zip and NaN-outside twin alongside) |
| **SHA-256** | `eff2b18e37378d0f0a2f5c8e22fc68e7c359ee161114502a985135e03dd217f9` |
| **Portal name / note (88/140)** | `gemsdoe31-h31x-piedmont-junction-37654-20261026-5a956da9` / `H31-X X1 piedmont-junction slope-break 37654d B2 \| HOLDOUT-DTI 0.1661 n=60988 \| 5a956da9` |
| **Verdict** | **OK TO DOWNLOAD AND SUBMIT** by the uniform selector (`scripts/selector_audit.py`, re-run this session with H31-X added; `registry/selector_decision_20261026.json`). Alternates passing the same gates: H31-T (PROJECTION 0.317), H31-J (0.312), H31-M (0.296). Submit at most one file per weekly slot. |
| **Disclosure** | The H31-X *lane card* (`evidence/h31x/run_card.json`) says `verdict=negative` because its own preregistered G5 was stricter than the owner's duplicate rule (it also tests pre-placement top-K overlap; see §4). The selector's rules predate this lane and implement the owner's rule literally; they govern the upload choice (same governance as IR-U-02). Nothing was relaxed after the fact. |

How to submit: DrivenData → competition 306 → *New submission* → choose exactly this `.tif` (or its single-TIFF
`.zip`) → paste the note → check the weekly quota (3/week) → submit. The all-finite encoding cannot trigger
"Predicted values must be in range [0, 1]". Validation here is automated and fail-closed (`src/gemsdoe31/submission.py`
both conventions + vendor `gems57.submission_writer`), not organizer acceptance.

## 2. Nine focus sites — best submission each, estimated score, unique?

Scores are USER-REPORTED (owner's leaderboard notes); overlap is COMPUTED (fraction of dots within 3 px of
GEMSDOE32 H33-2-B2). Source: `evidence/nine_site_forensic_audit.json`, `evidence/selector_audit_20261026.json`.

| Site | File to download (best claim) | Estimated score | Dots | Within 3 px of H33 | Unique / submittable again? |
|---|---|---:|---:|---:|---|
| GEMSDOE32 | `gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` | 0.2778 USER-REPORTED | 37,654 | 100% (self) | already submitted — do not resubmit |
| GEMSDOE36 | `gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif` | 0.2750 USER-REPORTED | 38,854 | 97.4% | duplicate lane of H33 — no |
| GEMSDOE28 | `gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif` (also h27-4 0.2708, h38-1 0.2707, h32-1 0.2649) | 0.2710 USER-REPORTED | 37,660 | 95.5% | duplicate lane of H33 — no |
| GEMSDOE31 (this repo, historical) | `gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-allfinite.tif` (= GEMSDOE28 h27-4 re-emission) | 0.2708 USER-REPORTED | 40,199 | 95.4% | duplicate lane — superseded by **H31-X** |
| GEMSDOE33 | `GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif` | 0.2632 USER-REPORTED | 41,865 | 92.6% | duplicate lane of H33 — no |
| GEMSDOE25 | `gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif` | 0.2600 USER-REPORTED | 44,090 | 88.2% | duplicate lane of H33 — no |
| GEMSDOE30 | `gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif` | 0.2600 USER-REPORTED | 44,090 | 88.2% (same support as GEMSDOE25) | duplicate — no |
| GEMSDOE24 | `gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif` | 0.2477 USER-REPORTED | 60,069 | 88.5% | duplicate lane of H33 — no |
| GEMSDOE27 | `gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif` | 0.2449 USER-REPORTED | 61,328 | 86.7% | duplicate lane of H33 — no |
| **New, this session** | **`gemsdoe31-h31x-piedmont-junction-37654-20261026-5a956da9-zeros.tif`** | **PROJECTION 0.355 [0.349, 0.360] — never a score**; HOLDOUT-DTI 0.1661 [0.1499, 0.1821] | 37,654 | 57.0% (max vs any discrete peer 63.1%) | **unique by the owner's rule; selector-promoted** |

All nine historical "best" files are members of one nested family (H19-5 surface → Poisson dots → catalogue-flank
prunes); none can be resubmitted as a new unique entry. The 0.3195 / 0.4413 leaderboard figures are USER-REPORTED
context only; nothing here evidences reaching 0.4413.

## 3. Why H33-2-B2 scored 0.2778 and whether it can be beaten (PhD-level, COMPUTED facts)

* **Lineage (exact bytes):** H19-5 (121,131 px, 0.1922) → D1.5 dots (60,069, 0.2477) → D2.8 Poisson dots (44,090,
  0.2600) → delete dots ≤1 px from the public catalogue (H27-4: 40,199, 0.2708) → delete ≤2 px (H33-2-B2: 37,654,
  0.2778). H33 is a strict subset of D2.8 (`evidence/h33_forensics_20261025.json`).
* **Metric economics:** DTI = TPw/(TPw + 0.2·FPw + 0.8·FNw) with a 300 m triangular kernel. For a fixed binary dot
  field of n dots and K hidden-truth pixels, S ≈ T/(0.2n + 0.8K). A dot is worth adding iff its expected kernel credit
  k > 0.2·S (0.0556 at S = 0.2778, i.e. it must lie within ≈283 m of uncovered truth). Anchor inversion over eleven
  in-family rasters gives K ≈ 13.4k and ≈0.004 TPw per catalogue-flank dot: the hidden expert truth is depleted next
  to already-mapped faults, so deleting 2,545 flank dots raised 0.2708 → 0.2778 (pure FP-budget economics).
* **Why binary 2.8-px-spaced dots:** the kernel saturates at 300 m, so dense support wastes FP weight; sparse maxima
  capture most of the credit at a fifth of the FP cost. 0.2778 ⇒ T ≈ 5.1k (≈38% hidden recall); 0.44 ⇒ T ≈ 8.0k.
* **Lever that remains:** a surface whose top 37,654 far-field locations carry more hidden truth per dot. H31-X attacks
  this by placing dots on the *piedmont junction line* (concave-up slope break at the bedrock–alluvium contact), the
  position of the master range-bounding fault, which QFFD only lists where Quaternary displacement was recognised but
  which experts and geologic maps carry much more completely. On both independent proxies it beats the H33 bytes:
  catalogue hide-and-recover (0.1661 vs H31-T's 0.1300 on the same evaluator and folds) and off-catalogue USGS-SGMC
  faults (0.1209 vs 0.0940, 4/4 quadrants; TPw 6,971 vs 5,400). The in-family PROJECTION is 0.355 (±0.006 LOO) — an
  estimate from one dot family's calibration; cross-family transfer is unproven, so it is never written as a score.
* **Regime trade-off (disclosed):** 82% of H31-X dots sit at slope > 6° (range front / mountain side); on the piedmont
  (≤6°) SGMC slice it is 0.0433 vs H33's 0.0586. If the hidden truth is dominated by intra-basin piedmont faults,
  H31-X under-covers them; the catalogue holdout (median slope 5.6°) nevertheless favours it strongly.

## 4. H31-X results (all preregistered: `knowledge/2026-10-26_h31x_piedmont_junction_preregistration.md`)

| Gate | Measured | Lane verdict | Selector verdict |
|---|---|---|---|
| G1 format | float32 EPSG:32611 3730×3292, [0,1], both conventions valid, 0 dots on catalogue, 37,654 dots, min spacing 2.8 px | PASS | PASS |
| G2 canary | max two-sided AUC 0.76 (SLOPE vs off-SGMC); junction line 0.64 (catalogue) / 0.59 (off-SGMC) | PASS | PASS |
| G3 holdout | HOLDOUT-DTI **0.1661 [0.1499, 0.1821]** (`gems57-pooled-hide-v2`, 60,988 withheld, buffer 213); Δ vs CTRL rank(tmi_hg) **+0.0991 [+0.0720, +0.1258]**; Δ vs SLOPE baseline **+0.1173 [+0.1024, +0.1314]**; 4/4 quadrants; untouched random-component split (29,965 withheld, seed 3103): 0.1462 vs CTRL 0.0659, Δ +0.0804 [+0.0536, +0.1081] | PASS | PASS |
| G4 SGMC proxy | 0.1209 vs H33 0.0940 (COMPUTED same code same day); quadrants 0.135/0.112/0.113/0.111 vs 0.102/0.095/0.108/0.074 | PASS | PASS |
| G5 uniqueness | final dots: max 63.1% within 3 px (GEMSDOE27 D1.5 60k field), 57.0% vs H33; \|Spearman\| surface 0.125, dots 0.050; **pre-placement raw top-K 86.3%** (lane-only stricter test); literal 695-lattice reading 99.3% (fails for every nonempty raster; disclosed IR-U-02) | **FAIL (top-K)** | PASS (owner rule: final dots ≤70%, \|ρ\| ≤0.90) |
| G6 projection | PROJECTION 0.3548 [0.349, 0.360] | PASS | PASS |
| **Verdict** | | **negative** (lane card, as frozen) | **promote — primary** |

Screen arms (same folds, HOLDOUT-DTI): X1 junction 0.1655 · X3 junction×gravity 0.1222 · X4 three-line 0.1147 ·
X2 junction×radiometric 0.1019 · CTRL 0.0671 · SLOPE 0.0488. NMS ablation: raw 0.1661 vs NMS 0.1655 → raw kept
(preregistered rule). Fixed-dot references (H33, H31-T, H31-J, H31-B) scored 0.000–0.011 in these folds — uninformative
under this protocol (their authors pruned within 2 px of the *full* catalogue), recorded as handicapped references only.

Post-hoc diagnostics (`evidence/h31x/exp2_posthoc_diagnostics.json`, not a gate): 29% of the raw top-K pixels lie
within 2 px of the catalogue and are pruned before emission; after pruning the top-K overlap is still 0.82 vs D1.5
fields and 0.79 vs H33 — i.e. the junction surface and the catalogue-trained H19-5 family rank the same range fronts
highly, while the emitted dot sets differ at 43% of locations. A uniform random field scores 0.16–0.17 on the same test.

## 5. Ranked new hypotheses (frozen before fitting; see preregistration for layers, mimics, novelty, cost)

1. **X1 piedmont-junction slope-break line** — run; HOLDOUT-DTI 0.1661 (best in repository).
2. X3 junction × gravity basin-edge gate — run; 0.1222 (gate dilutes the terrain signal).
3. X2 junction × radiometric contact edge — run; 0.1019.
4. X4 three-line corroboration — run; 0.1147.
5. KIN: LiDAR scarp facing-direction agreement with the gravity basinward vector (synthetic vs antithetic) — costed
   (~30 min, LiDAR covers 75% of footprint), not run (budget).
6. TEX: RTP structure-tensor fabric-truncation lines — costed (~45 min; survey-seam mimic risk), not run.

No new external data was needed. Blocked external ideas remain documented with official sources (InSAR/ASF, ASTER
LP DAAC, 1 m 3DEP tiles) — unreachable from this sandbox.

## 6. Remaining work and limitations

* Live transfer is unproven: all 0.2xxx anchors are USER-REPORTED; the projection calibration is in-family (H19-5
  descendants); H31-X is a different family. The only way to learn its live value is the owner's manual upload.
* The lane's stricter pre-placement top-K check failed; the selector's final-dot rule passed. Both are disclosed; the
  owner can choose H31-T (34% vs H33, more conservative novelty) if a lower-overlap entry is preferred.
* Piedmont regime trade-off (§3). A natural next lane is a *budget split* (e.g. 70% junction / 30% piedmont-specialist
  dots from H33's piedmont slice) — requires its own preregistration and holdout.
* Open irregularities unchanged: B10 label vs official page; B06 tilt vs `tc`; sample submission equals catalogue.
* KIN and TEX hypotheses remain untested; the H31-B paired test could not be reproduced exactly (OOF geometry).
