# Executive summary — 2026-10-26, session `arena/579233d5-gemsdoe31` (lanes H31-Y, H31-Z; selector re-run)

Labels: **HOLDOUT-DTI** (evaluator, withheld positives, 95% CI) · **COMPUTED** · **USER-REPORTED**
(owner-typed, no organizer receipt) · **PROJECTION** (estimate, never a score). No ORGANIZER-CONFIRMED
score exists in this repository. This repository never contacts DrivenData; uploading is a manual owner
action. Core values applied throughout: **Maximize P(Win)**, **Own the Outcome**.

## 1. The one answer: which file to download and submit

| | |
|---|---|
| **File (download this)** | [`docs/downloads/gemsdoe31-h31x-piedmont-junction-37654-20261026-5a956da9-zeros.tif`](../docs/downloads/gemsdoe31-h31x-piedmont-junction-37654-20261026-5a956da9-zeros.tif) — H31-X, unchanged this session (all-finite, every cell in [0,1]; single-TIFF zip and NaN-outside twin alongside) |
| **SHA-256** | `eff2b18e37378d0f0a2f5c8e22fc68e7c359ee161114502a985135e03dd217f9` |
| **Portal name / note (88/140)** | `gemsdoe31-h31x-piedmont-junction-37654-20261026-5a956da9` / `H31-X X1 piedmont-junction slope-break 37654d B2 \| HOLDOUT-DTI 0.1661 n=60988 \| 5a956da9` |
| **Verdict** | **OK TO DOWNLOAD AND SUBMIT** — re-confirmed primary by the uniform selector re-run this session (`scripts/selector_audit.py` with H31-Y/H31-Z added; `registry/selector_decision_20261026.json`). Gated alternates: H31-T (PROJECTION 0.317), H31-J (0.312), H31-M (0.296). Submit at most one file per weekly slot. |
| **This session's new files** | **Both are ⛔ DO NOT SUBMIT** (see table below). They are genuine, newly generated TIFFs with full run cards — valuable negative results, not submittable entries. |

How to submit: DrivenData → competition 306 → *New submission* → choose exactly the H31-X `.tif` above (or
its single-TIFF `.zip`) → paste the note → check the weekly quota → submit → keep the organizer receipt
next to the SHA-256. The all-finite encoding cannot trigger "Predicted values must be in range [0, 1]".
Validation here is automated and fail-closed (both conventions + vendor writer), not organizer acceptance,
and no human inspector is involved in any gate.

### Required table: file to download · estimated score · unique?

Estimated live score = anchor-inversion **PROJECTION** (eleven USER-REPORTED focus anchors, in-family LOO
RMSE 0.0028; cross-family transfer unproven) — never a score. Uniqueness = owner's rule on the submitted
dots (>70% within 3 px of one discrete peer, or |rank correlation| > 0.90 ⇒ duplicate), COMPUTED.

| File to download | Estimated score (PROJECTION) | Unique vs all other GEMSDOE sites/lanes? | OK to submit? |
|---|---:|---|---|
| **`gemsdoe31-h31x-piedmont-junction-37654-20261026-5a956da9-zeros.tif`** (H31-X, selector primary) | **0.355 [0.349, 0.360]** | **Yes** — max 67.0% dots within 3 px of any discrete peer in the re-run (worst peer is this session's H31-Z split; 63.1% vs pre-session peers, 57.0% vs H33); \|Spearman\| ≤ 0.13 | ✅ **YES — submit this one** |
| `gemsdoe31-h31t-transtension-dinkelbach-20261025-b37654-zeros.tif` (H31-T, alternate) | 0.317 | Yes — max 43.9%; 34.1% vs H33 | ✅ alternate only |
| `gemsdoe31-tgtd-submod-37654-20261025-ab35d4e8-zeros.tif` (H31-J, alternate) | 0.312 | Yes — max 49.9% | ✅ alternate only |
| `gemsdoe31-h31m-bstep-xmod-submod-20261025-37654-allfinite.tif` (H31-M, alternate) | 0.296 | Yes — max 59.9% | ✅ alternate only |
| `gemsdoe31-h31y-regimesplit-route-37654-20261026-8f16cb42-zeros.tif` (H31-Y, **new this session**) | 0.385 [0.380, 0.391] | **No — duplicate**: 92.4% of dots within 3 px of H31-X | ⛔ NO (G5 fail; research only) |
| `gemsdoe31-h31z-quotasplit-split50-37654-20261026-de0eae67-zeros.tif` (H31-Z, **new this session**) | 0.219 [0.213, 0.224] | Yes — max 54.1% (vs H31-X); 41.4% vs H33 | ⛔ NO (G4/G6 fail; research only) |
| Every historical nine-site best (H33 family, §2) | 0.2449–0.2778 USER-REPORTED | No — 86.7–100% within 3 px of H33 (one family) | ⛔ NO (already submitted / duplicate lane) |

Governance disclosures (unchanged + one clarification): promotions judge uniqueness against discrete peer
*submissions* (owner-directed rescope IR-U-02); the literal 695-raster reading fails for every nonempty
raster (registered spacing-5 lattice within 3 px of 99.87% of the footprint, COMPUTED) — under a literal
reading, submit nothing. **IR-U-03 (new this session, disclosed in `scripts/selector_audit.py`):**
duplicate status is chronological — a later lane that copies an earlier one (H31-Y copying H31-X) is the
duplicate and cannot retroactively demote the original; both directions of every overlap are recorded in
`evidence/selector_audit_20261026.json`.

## 2. Nine focus sites — best submission each, estimated score, unique?

COMPUTED from hash-verified fetched bytes (`evidence/nine_site_forensic_audit.json`, selector re-run);
claims USER-REPORTED. All nine are one nested family — none is submittable again as a unique entry.

| Site | File (best historical claim) | Estimated/reported score | Dots | Within 3 px of H33 | Unique / submittable? |
|---|---|---:|---:|---:|---|
| GEMSDOE32 | `gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` | 0.2778 USER-REPORTED | 37,654 | 100% (self) | already submitted — no |
| GEMSDOE36 | `gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif` | 0.2750 USER-REPORTED | 38,854 | 97.4% | duplicate lane — no |
| GEMSDOE28 | `gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif` (also h27-4 0.2708, h38-1 0.2707, h32-1 0.2649) | 0.2710 USER-REPORTED | 37,660 | 95.5% | duplicate lane — no |
| GEMSDOE31 (historical) | `gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-allfinite.tif` | 0.2708 USER-REPORTED | 40,199 | 95.4% | duplicate lane — superseded by H31-X |
| GEMSDOE33 | `GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif` | 0.2632 USER-REPORTED | 41,865 | 92.6% | duplicate lane — no |
| GEMSDOE25 | `gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif` | 0.2600 USER-REPORTED | 44,090 | 88.2% | duplicate lane — no |
| GEMSDOE30 | `gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif` | 0.2600 USER-REPORTED | 44,090 | 88.2% | duplicate — no |
| GEMSDOE24 | `gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif` | 0.2477 USER-REPORTED | 60,069 | 88.5% | duplicate lane — no |
| GEMSDOE27 | `gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif` | 0.2449 USER-REPORTED | 61,328 | 86.7% | duplicate lane — no |

The 0.3195 / 0.4413 leaderboard figures in the brief remain USER-REPORTED context; nothing in this
repository evidences reaching them (the highest gated PROJECTION is 0.355; the highest ungated,
H31-B-standalone 0.409, lacks a machine-verifiable paired holdout win and stays unpromoted fail-closed).

## 3. Why H33-2-B2 scored 0.2778 (USER-REPORTED) — and what this session proved about beating it

Established forensics (COMPUTED, `evidence/h33_forensics_20261025.json`): H33 = H19-5 surface → D2.8
Poisson dots (44,090; 0.2600) → delete dots ≤1 px from the catalogue (0.2708) → delete ≤2 px (37,654;
0.2778). Under DTI = TPw/(TPw + 0.2·FPw + 0.8·FNw) with a 300 m triangular kernel, a non-redundant dot
helps iff its kernel credit exceeds 0.2·S (0.0556 at S = 0.2778); catalogue-flank dots earn ≈0.004
TPw/dot because hidden expert truth is depleted beside already-mapped faults, so the B2 prune is pure
FP-budget economics. Beating it requires a surface whose far-field top-37,654 locations carry more hidden
truth per dot — at identical budget/geometry.

**This session's measured answer (all HOLDOUT-DTI `gems57-pooled-hide-v2`, 60,988 withheld, same folds):**

| Arm (label-free) | HOLDOUT-DTI | Off-cat SGMC DTI (COMPUTED) | PROJECTION | Final-dot overlap vs H31-X |
|---|---:|---:|---:|---:|
| JUNC alone (= H31-X surface, replicated exactly) | **0.1661** | 0.1209 | 0.355 | 100% (self) |
| ROUTE slope-routed JUNC×PIED blend (H31-Y) | 0.1626 | **0.1312** | 0.385 | **92.4% (duplicate)** |
| SPLIT65 reference (65% JUNC quota) | 0.1559 | not packaged (reference only) | — | — |
| SPLIT50 hard quota (H31-Z) | 0.1473 | 0.0749 | 0.219 | 54.1% (unique) |
| SPLIT35 hard quota | 0.1349 | not packaged | — | — |
| PIED potential-field specialist alone | 0.0705 | (line AUC vs SGMC 0.42) | — | — |
| CTRL rank(tmi_hg) / SLOPE rank(slope) | 0.0671 / 0.0488 | — | — | — |

Three line-by-line conclusions, each directly measured:

1. **Potential-field corroboration of junction dots carries real discovery signal — in the transition
   zone, not the flat piedmont.** ROUTE beats H31-X on the independent SGMC proxy (TPw 7,573 vs 6,971)
   at almost no catalogue-holdout cost (paired −0.0036 [−0.0061, −0.0012]). But its regime receipt
   corrects my own preregistered mechanism attribution: only **31** of its 37,654 dots lie at slope
   (band) ≤6°; the SGMC gain is in the mountain slice (0.1388 vs H31-X 0.1184, same code). The routed
   blend re-ranks junction segments at 3–9° slopes where magnetic/basement corroboration discriminates
   fault-bounded fronts — it does not add flat-basin faults. (INFERENCE about *where*, from COMPUTED
   regime dot counts.)
2. **Forcing budget into the flat piedmont via this PIED line destroys discovery credit.** SPLIT50's
   21,322 piedmont dots earn the same piedmont SGMC slice (0.0431) as H31-X's 6,449 (0.0433) — roughly
   3× less efficient per dot — while halving mountain coverage (SGMC 0.0749 overall). The
   ASIG+BASE+GRAV specialist as constructed does not locate geologic-map-style faults (its canary AUC
   vs off-SGMC was 0.42, below chance — measured before the screen and honoured as a warning, not tuned away).
3. **A blended surface cannot be both JUNC-competitive and unique here.** Any blend weak enough to keep
   JUNC's ranking reproduces ≥92% of its dots (duplicate STOP); any blend strong enough to move the dots
   (fixed 50/50: HOLDOUT-DTI 0.1063) or any quota large enough to force novelty (SPLIT50: SGMC 0.0749)
   loses on at least one proxy. The remaining route to >0.2778 is therefore a *genuinely different
   mountain/transition line* (next-lane candidates in §6), not a recombination of JUNC with PIED.

Pipeline integrity check: the JUNC arm reproduced H31-X's screen HOLDOUT-DTI **exactly**
(0.1661329569994631, |Δ| = 0.0, same 60,988 withheld) from recomputed lines — evaluator, folds and
emission are bit-stable across sessions.

## 4. This session's lanes (preregistered, 3 experiments each, gates automated)

### H31-Y — regime budget-split family; winner ROUTE → **negative (duplicate STOP)**
Preregistration `knowledge/2026-10-26_h31y_regime_split_preregistration.md`; card `evidence/h31y/run_card.json`;
file `gemsdoe31-h31y-regimesplit-route-37654-20261026-8f16cb42-zeros.tif` (SHA-256 `89a5fc01…`).
G1 format PASS · G2 canary PASS (max two-sided AUC 0.76) · G3 PASS (0.1626 [0.1470, 0.1780];
Δ vs CTRL +0.0955 [0.0690, 0.1217]; Δ vs SLOPE +0.1137 [0.0995, 0.1274]; confirmation seed 3104:
0.1464 vs CTRL 0.0573, Δ +0.0891 [0.0624, 0.1140]) · G4 PASS (SGMC 0.1312 ≥ H33 0.0940) ·
**G5 FAIL (92.4% dots within 3 px of H31-X; literal lattice 99.4%)** · G6 PASS (0.385).
Verdict `negative`, `ok_to_submit=false`. The file is retained as a research download only.

### H31-Z — hard quota split SPLIT50 → **negative (discovery-proxy fail)**
Preregistration `knowledge/2026-10-26_h31z_quota_split_preregistration.md`; card `evidence/h31z/run_card.json`;
file `gemsdoe31-h31z-quotasplit-split50-37654-20261026-de0eae67-zeros.tif` (SHA-256 `5a7e3b3e…`).
G1 PASS · G2 PASS (cited canary) · G3 PASS (0.1473 [0.1334, 0.1613]; Δ vs CTRL +0.0802 [0.0548, 0.1056];
Δ vs SLOPE +0.0984 [0.0853, 0.1114]; Δ vs JUNC −0.0189 [−0.0277, −0.0093]; confirmation seed 3105:
0.1266 vs CTRL 0.0621, Δ +0.0645 [0.0409, 0.0874]) · **G4 FAIL (SGMC 0.0749 < H33 0.0940)** ·
G5 PASS (max 54.1% vs H31-X; literal lattice 99.2% disclosed) · **G6 FAIL (PROJECTION 0.219 < 0.2778)**.
Verdict `negative`, `ok_to_submit=false`. Restriction ablation: ON 0.1473 vs OFF 0.1451 (kept ON).

## 5. Ranked hypotheses: status after this session

1. **Quota/routed regime splits (H31-Y/Z) — executed, both negative for different measured reasons** (§§3–4).
2. **Next lane candidate (highest value, unrun): transition-corroborated junction at kernel scale** —
   JUNC recomputed at σ = 3 px (300 m, the DTI kernel scale) with ASIG/BASE corroboration applied
   *only* in the 3–9° transition band as a rank multiplier bounded to actually move ≥30% of dots
   (uniqueness designed-in, checked on the surface before placement). Directly targets the measured
   ROUTE gain without reproducing its dot set. Cost ~20 min; needs its own preregistration + untouched
   confirmation seed.
3. **KIN** (LiDAR scarp facing vs gravity basinward vector) — costed, unrun (~30 min; LiDAR ~75% coverage).
4. **TEX** (RTP structure-tensor orientation discontinuities) — costed, unrun (~45 min; seam-mimic risk).
5. **H31-B-standalone paired re-test** — highest SGMC (0.1391) but no paired holdout CI on the shared
   evaluator; reconstructing its surface label-free per fold is the only honest route (its fixed dots are
   handicapped in hide-and-recover by construction); medium cost, complex surface.

No new external data was needed; InSAR (NASA OPERA/ASF) remains unreachable from this sandbox
(official source named in the preregistrations).

## 6. Remaining work and limitations

* Live transfer is unproven for every candidate: all live anchors are USER-REPORTED; the projection is
  calibrated on one dot family. The first ORGANIZER-CONFIRMED number will come from the owner's manual
  upload of H31-X — record the receipt against its SHA-256 immediately.
* H31-X's own lane card remains `verdict=negative` under its stricter pre-placement top-K G5; the
  selector (owner's rule) promotes it. If the owner prefers minimal overlap, H31-T (34.1% vs H33,
  PROJECTION 0.317) is the conservative alternate.
* Two regime definitions exist in-repo (selector: DEM-derived slope; lane receipts: `det_elev_slope`
  band) — never compare regime slices across instruments.
* Open irregularities unchanged: B10 label vs official "Density of earthquakes"; B06 tilt vs `tc`
  caption; sample submission byte-equals the catalogue.
* Budget respected: exactly 3 experiments per lane, no tuning after any EXP-3, no slots spent,
  DrivenData never contacted.
