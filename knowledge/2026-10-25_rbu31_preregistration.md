# RBU31 preregistration — regime-balanced union detector (2026-10-25)

Frozen **before any candidate fit**. Written after (a) byte-level forensics on
existing submissions only (`evidence/h33_forensics_20261025.json`,
`evidence/regime31/regime_forensics.json`, COMPUTED this session) and
(b) restoration of the hash-pinned owner-mirror inputs
(`evidence/data_restore_20261025_regime.json`; byte identity to the mirror,
**not** organizer authentication). No DrivenData contact; no leaderboard
access; no automatic submission.

Claim classes used below: **OFFICIAL** (organizer/USGS/NASA source),
**OWNER-MIRROR**, **COMPUTED** (reproduced from files in this repo),
**USER-REPORTED** (owner-supplied leaderboard values, no receipt),
**INFERENCE** (reasoning, not measurement).

---

## 1. Why did `h33-h33-2-b2-…-zeros` (GEMSDOE32) get the family's best reported value?

Reported value **0.2778 is USER-REPORTED** — no organizer receipt exists in
any repo reviewed, so it is never used as a target or called a score here.
What *can* be verified line-by-line (COMPUTED,
`evidence/h33_forensics_20261025.json`):

1. H27-4 (40,199 dots, this repo) = D2.8 (44,090 dots) with every dot at
   catalogue distance ≤ 1 px removed. H33-2-B2 (37,654 dots) = the same D2.8
   surface with every dot at distance ≤ 2 px removed (min distance √5 px).
   H33 adds **zero** new dots vs H27; it deletes 2,545 near-catalogue dots.
2. The metric (OFFICIAL problem page; α = 0.2, β = 0.8, triangular kernel
   R = 300 m) is `DTI = T / (0.2·T + 0.2·F + 0.8·K)`. Deleting a set of dots
   improves DTI iff `lost_T < 0.2·S/(1 − 0.2·S) · removed_F` at current score
   S — at S ≈ 0.27 the exchange rate is ≈ 0.059. Dots hugging *known*
   catalogue faults are the dots least likely to sit within 300 m of a
   *hidden* (off-catalogue) truth fault, so their lost_T ≈ 0 while their
   removed_F is maximal. Pruning them is almost free DTI.
3. The parent surface is a catalogue-trained detector thinned to ≈ 2.8 px
   (280–300 m) minimum spacing. Because TPw takes a **max** over predictions
   within 300 m of each truth pixel, a second dot near the same truth adds
   FPw but no TPw. Kernel-matched sparse emission is therefore worth more
   than surface probability mass — confirmed in-repo by the H31-E ablation
   (Poisson 2.8 px 0.12765 vs submodular 0.12736, screen draw 101).

**INFERENCE:** H33's edge is DTI economics (pruning + spacing) applied to a
strong parent surface, not new geological detection. Any candidate that
keeps those two emission rules but ranks *off-catalogue* pixels better than
D2.8 should, in expectation, exceed it — but this cannot be established
without the private truth. The only honest pre-submission evidence is
dominance on **both** independent-ish proxies available: the buffered
catalogue hide-and-recover holdout **and** off-catalogue SGMC, in **both**
geomorphic regimes.

## 2. Regime forensics that motivate this lane (COMPUTED)

`evidence/regime31/regime_forensics.json` (existing files only; regime:
piedmont `det_elev ≤ 50 m`, mountain `> 50 m` — same split as H31-E G5a/G5b):

| quantity | piedmont | mountain |
|---|---|---|
| footprint share | 68.0% | 32.0% |
| public catalogue share | **72.4%** | 27.6% |
| off-catalogue SGMC truth share | 37.5% | **62.5%** |

| candidate (37,654 dots) | SGMC-all | SGMC-piedmont | SGMC-mountain | piedmont dot share |
|---|---|---|---|---|
| H33-2-B2 (reconstructed, byte-verified identity) | 0.0940 | 0.1091 | 0.0654 | 64.4% |
| H31-E2 SCGP-Submod | 0.0816 | **0.1233** | 0.0372 | 68.8% |
| H31-B scarp-Hessian (hand rank-blend, no hide-v2 holdout) | 0.1391 | 0.1432 | 0.1095 | 52.7% |

SGMC TPw per emitted dot, mountain regime: H31-E2 **0.122** vs H33 0.188 vs
H31-B 0.239. H31-E2's failure is *placement quality in mountains*, not only
allocation: its physics experts never saw the raw 39-band stack (raw LiDAR
scarp bands included) inside the same trees, and no model in this repo has
ever been trained with regime-balanced risk. The catalogue's 72/28 regime
mix is a mapping-survey artifact (range-front scarps are mapped first);
training empirical risk on it while the deployment truth regime mix is
unknown (SGMC says 38/62 the other way) is a textbook covariate-shift
exposure. **Named non-fault mimic:** Pleistocene Lake Lahontan shoreline
terraces and unfaulted volcanic-flow/erosional scarps — concentrated in
exactly the piedmont band where the catalogue-trained risk is highest.

## 3. Candidate hypotheses considered (ranked before fitting)

| # | hypothesis | layer(s) / signature | why it should find *missing* faults | difference vs this repo | expected ΔDTI | cost |
|---|---|---|---|---|---|---|
| **H-A (SELECTED)** | **RBU31: single union HGB (raw-39 ∪ SCGP-40) trained with regime-balanced sample weights** | All cached bands; tree interactions between raw LiDAR scarp (`step_max`, `lappos/lapneg_max`, `relief`) and Gallardo–Meju cross-gradient / tilt / upward-continuation physics; regime gate `det_elev ≤ 50 m` used only for sample weights | Balanced risk removes the catalogue's piedmont mapping bias; cross-gradient/gravity-basement features rank *buried* piedmont faults with no scarp, raw scarp bands rank mountain faults the physics-only experts missed | H31-E kept raw and physics features in *separate* experts with fixed 0.45/0.55 blends + unsupervised ridge + tip/relay multipliers; Baseline-D has no SCGP features; H31-B is a hand-weighted rank blend over historical OOF maps with no hide-v2 holdout; no prior model uses regime-balanced weights | highest (directly targets the measured G5b mountain failure while retaining the measured piedmont physics gain) | low–medium (reuses cached stacks + shared evaluator) |
| H-B | Down-to-basin scarp-polarity consistency: sign LiDAR dipole by 1 km regional topographic gradient | LiDAR `upface/downface_max` × Gaussian gradient of `det_elev` (σ = 10 px) | Normal-fault scarps face the basin; shoreline/terrace scarps face along-contour — polarity rejects the named mimic | `lidar_signed_polarity_abs` exists but is unsigned w.r.t. *regional* slope | medium | medium (new directional channels, seam risks) |
| H-C | Lahontan shoreline negative-expert hard gate | Absolute-elevation band + contour-parallelism of scarp strike | Removes the dominant piedmont false-positive process directly | Only one soft feature (`scgp_lahontan_mimic_score`) exists; no trained mimic model | medium, uncertain | medium–high (needs absolute DEM level audit) |
| H-D | Drainage deflection / χ disequilibrium corridors | Flow routing on 100 m `det_elev` | Active normal faults deflect/knickpoint drainages crossing the range front | Not in this repo; tried fleet-wide (GEMSDOE60, USER-REPORTED 0.0351) with weak result | low | high (routing on 12.3 Mpx, pit-filling) |
| H-E | InSAR creep discontinuities (NASA OPERA DISP-S1) | LOS displacement gradient discontinuities | Aseismic creep localises on active faults invisible to magnetics/topography | Wholly new data type in fleet | unknown | **not viable this session**: free OFFICIAL source exists (registry `nasa-opera-disp-s1`) but requires Earthdata access outside this sandbox's host allowlist; named, checked, deferred |

## 4. Frozen candidate specification (H-A, exactly one candidate)

- **Features (79):** prepared-stack indices 0–38 (19 competition + 12 LiDAR
  + 8 GeoDAWN raw bands, sentinel-cleaned) **plus** H31-E static
  translation-invariant set (`EXP3_LIDAR_INDICES`: 32 full-footprint SCGP
  physics + 8 LiDAR-derived). No catalogue-distance, SGMC, or coordinate
  features; the SCGP level trio (`raw_det_elev`, `piedmont_apron_index`,
  `log_depth_to_base`) stays excluded exactly as in H31-E2. Prepared-band
  `det_elev` **is** one of the raw-39 Baseline-D columns and remains in the
  union on exactly Baseline-D's terms; additionally (disclosed, new) its
  values assign each training sample's regime weight and each evaluation
  pixel's regime.
- **Model:** `HistGradientBoostingClassifier` with the H31-E `HGB_CONFIG`
  (max_iter 200, lr 0.07, leaves 31, min_leaf 60, L2 2.0, no early stop),
  `class_weight` removed for the candidate and replaced by explicit
  `sample_weight`: for class c ∈ {0,1} and regime r ∈ {piedmont, mountain},
  `w = (0.5 · W_c) / n_{c,r}`, with class totals W_1 = 2·W_0 (same 2:1
  positive emphasis as Baseline-D/H31-E), then normalised to mean 1.
  Samples with non-finite `det_elev` get their class-average regime weight.
  Baseline-D comparator is retrained unchanged (class_weight {0:1, 1:2}).
- **Folds/training:** identical to `scripts/evaluate_holdout.py`
  (`gemsdoe31-hide-v2.0`): median-split quadrants, 213 px (21.3 km) buffer,
  whole 8-connected components touching quadrant+buffer excluded from
  training, same sample_ids (rng 5000+q, 120 k negative cap) for both arms.
- **Emission:** `poisson_disk_emit`, min_dist 2.8 px, per-quadrant budget
  `37,654 / 5,167,373 × quadrant pixels`, valid = evaluation domain with
  visible-fault distance > 2 px (the verified H33 pruning rule, learned —
  no prior dots are copied; every dot comes from the new surface).
  Final: cosine-buffer-weighted OOF blend of the 4 fold models (as H31-E),
  valid = footprint with full-catalogue distance > 2 px, budget **37,654**.
- **No** unsupervised-ridge blend, **no** tip/relay multiplier, **no**
  submodular emitter, **no** post-hoc tuning. One mechanism, clean ablation
  attribution vs Baseline-D (features) and vs H31-E2 saved numbers (design).

## 5. Experiments (budget: exactly 3, then stop)

1. **Screen, draw 101:** RBU31 vs same-run Baseline-D, pooled DTI + paired
   component-bootstrap CI (shared `pooled_dti_and_bootstrap_ci`), plus
   single-feature two-sided AUC canary over all 79 union features
   (STOP if any AUC > 0.90). Pass: ΔDTI > 0.002 and ≥ 3/4 folds won.
2. **Fresh confirmation, draws 202 + 303** (only if Exp 1 passes): same
   frozen models, untouched hidden segments. Pass: pooled ΔDTI > 0.002 and
   paired 95% CI lower bound > 0.
3. **Final emission + dual-proxy + uniqueness + format:** SGMC off-catalogue
   DTI overall, piedmont-only, and mountain-only for RBU31 vs Baseline-D
   final dots vs reconstructed H33; duplicate canary (surface Spearman
   |ρ| ≤ 0.90 **and** 3-px dot overlap ≤ 70%) vs all local registry TIFFs
   and the nine focus sites' top rasters (GEMSDOE24/25/27/28/30/31/32/33/36,
   fetched hash-verified where the forensic manifest pins a hash);
   GeoTIFF validation via shared `submission_writer.py`.

**Promotion gates (all required for "OK to submit"):**
G1 format/range [0,1] · G2 leakage canary · G3a uniqueness vs genuine
submissions (the spacing-5 lattice in the 695-raster shared registry covers
100% of the interior within 3 px *by construction* and therefore blocks
every non-empty candidate under a literal reading — G3b is reported as a
disclosed universal degeneracy, exactly as in H31-E2/MAGREST, never silently
exempted) · G4 Exp 1 + Exp 2 holdout beats Baseline-D · G5 SGMC beats
**both** Baseline-D and H33 on all-elevation **and** piedmont **and**
mountain. Any failure ⇒ verdict `negative`, TIFF labelled DO NOT SUBMIT
(research deliverable only). Passing all gates ⇒ verdict `promote`:
"OK TO DOWNLOAD AND SUBMIT — automated validation complete, no human
inspector in the loop; spending the weekly slot remains the owner's click."

## 6. Sources (OFFICIAL, for manual review)

- Metric/format: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Official rules PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf
- Reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
- GeoDAWN (USGS ScienceBase 657e1d85d34e23d3533209f7): https://www.sciencebase.gov/catalog/item/657e1d85d34e23d3533209f7
- INGENIOUS / GDR 1391: https://gdr.openei.org/submissions/1391
- USGS SGMC: https://mrdata.usgs.gov/geology/state/
- EPSG:32611: https://epsg.io/32611 · Tversky index: https://en.wikipedia.org/wiki/Tversky_index
- Gallardo & Meju (2003) cross-gradients: https://doi.org/10.1029/2003GL017370
- Spatial CV: Roberts et al. (2017) https://doi.org/10.1111/ecog.02881

*Arena core values for this project: Maximize P(Win) · Own the Outcome.*
