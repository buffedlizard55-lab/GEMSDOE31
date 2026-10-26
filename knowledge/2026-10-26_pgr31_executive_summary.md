# Executive summary — nine focus sites + new PGR31 candidate (2026-10-26, this session)

All leaderboard numbers are **USER-REPORTED** (owner prompts / sibling repos; **no organizer receipt
exists in this repository for any file**). HOLDOUT-DTI numbers are local hide-and-recover proxies,
never leaderboard scores. A projection is never written as a score.

## BOTTOM LINE — download / submit decision for the new file (obvious, machine-decided)

| Question | Answer |
|---|---|
| New unique TIF generated this session? | **YES** — `gemsdoe31-pgr31-poisson-pseudograv-37654-20261026` (PGR31), 37,654 de-novo dots, zero incumbent dots copied |
| OK to download? | **YES, for research** — [`docs/downloads/gemsdoe31-pgr31-poisson-pseudograv-37654-20261026-zeros.tif`](../docs/downloads/gemsdoe31-pgr31-poisson-pseudograv-37654-20261026-zeros.tif) (135,374 B, SHA-256 `9dcc2e0c4da3f40c17796cfd4ab306cd6aa0ab218d98f83f3b5cbeb406d4b628`); NaN-outside twin SHA-256 `e38fc198e87e2f9c3e3eeeb32ea2f21e1cbf8964e050a138e40b11d4cafed888` |
| OK to submit to DrivenData? | **NO — DO NOT SUBMIT** (`verdict: negative`, `eligible_for_selector: false`, `ok_to_submit: false`). No human inspector was involved: `python scripts/verify_pgr31_run.py` re-reads the bytes and reproduces this decision |
| Portal error "Predicted values must be in range [0, 1]"? | **Fixed for this file**: the recommended `-zeros.tif` is finite in **all 12,279,160 cells** with values exactly `{0.0, 1.0}` (verified by re-reading the file), single-band float32, EPSG:32611, 3730×3292, exact sample transform; validator hard failures `[]` under both conventions |
| Reserved name / note (for a *future* file that passes) | Name `gemsdoe31-pgr31-poisson-pseudograv-37654-20261026` · Note (109/140): `PGR31 Poisson pseudo-grav discordance 37654d \| HOLDOUT-DTI s51 0.0764 vs 0.0761 \| research-only DO NOT SUBMIT` |
| Why not submit? | Preregistered screen **failed**: HOLDOUT-DTI (gems57-pooled-hide-v2, 2,778 withheld positives) candidate **0.0764** [0.0449, 0.1102] vs same-run base-38 control **0.0761** [0.0440, 0.1122]; paired Δ **+0.0003** [−0.0202, +0.0240], 2/4 quadrants, worst −0.0365; off-catalogue SGMC proxy Δ **−0.0080**. Fresh confirmation (draw 52) was gated off by the frozen stop rule — no tuning on a burned draw |

## 1. The nine focus sites — highest claim each, and the clear submit verdict

"Best per site" below is the highest **USER-REPORTED** artifact in the owner prompt / pinned audit
(`evidence/nine_site_forensic_audit.json`). Every one is the same D2.8/H19-5 dot family
(**86.7–100% of its dots within 3 px of GEMSDOE32 H33** — measured, `registry/focus_review.json` /
`knowledge/2026-10-26_executive_summary_and_hypotheses.md`), so **none of them is submittable as a
new unique entry**: under the lane rule (>70% within 3 px = duplicate) they are one submission, not nine.

| Site | Highest USER-REPORTED artifact | Score | Dots | Within 3 px of H33 | Best *unique* scored file in the prompt (USER-REPORTED) | PGR31 dots within 3 px of this site's best (measured this session) | Verdict |
|---|---|---|---|---|---|---|---|
| GEMSDOE24 | h25-1-dotted-h19-5-d1-5-20261002-989f59505db1 | 0.2477 | 60,069 | 88.5% | GVC1 0.0859 | 40.3% | Historical = duplicate; do not resubmit |
| GEMSDOE25 | dotted-h19-5-d2-8-20261002-e56ea318af89 | 0.2600 | 44,090 | 88.2% | H66-MGD 0.0742 | 38.8% | duplicate |
| GEMSDOE27 | topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1 | 0.2449 | 61,328 | 86.7% | **H29-HPVC 0.2190** (best confirmed *unique* score in the fleet) | 41.8% | Historical = duplicate. The only unscored candidate whose own site records a holdout pass + peer uniqueness and awaits the owner-as-selector is GEMSDOE27 H29-1 D-refill (SECONDHAND: `registry/focus_unique_2026.json`, not re-gated here) |
| GEMSDOE28 | h36-1-rung30-blind-r1-20261003-b531dae0a36f | 0.2710 | 37,660 | 95.5% | S18-MXTP 0.0217 | 35.6% | duplicate |
| GEMSDOE30 | d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca | 0.2600 | 44,090 | 88.2% | MSDB1 0.1462 | 38.8% | duplicate (pixel-family replay of D2.8) |
| GEMSDOE31 | h27-4-solo-d28-20261004-8acb75e1 | 0.2708 | 40,199 | 95.4% | none reported | 36.1% | duplicate; this repo's newest unique file is PGR31 above (negative) |
| GEMSDOE32 | **h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros** | **0.2778** | 37,654 | 100% (itself) | none reported | 33.2% | **Single best claim overall** — it *is* the reference geometry; cannot be "submitted again" as new |
| GEMSDOE33 | h33d-analog-tip-stepover-r30-20261004-cb490425926e | 0.2632 | 41,865 | 92.6% | none reported | 37.4% | duplicate |
| GEMSDOE36 | anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros | 0.2750 | 38,854 | 97.4% | none reported | 33.6% | duplicate |

**Clear answer to "which best submission should I submit for a high score?": none of the nine
historical bests, and not PGR31.** Already-scored files have spent their slot; the nine historical
bests are one duplicate family; every unscored candidate in this repository, PGR31 included, is
either holdout-negative or blocked by the disclosed 695-registry lattice degeneracy. Spending a
weekly slot is the separate selector step (owner's click), and this session's gates authorise no file.

## 2. Why H33-2-B2 reached 0.2778 (USER-REPORTED) — and can we beat it?

Measured byte geometry (`docs/data/h33-forensics.json`, hashes verified): **H33 = the 44,090-dot
D2.8 field pruned at ≤1 px from the public catalogue (→ H27-4, 40,199 dots), then pruned again at
≤2 px (→ 37,654 dots; 2,545 dots removed, 0 added, all 35,483 dots beyond 300 m kept; min catalogue
distance 2.236 px).** It contains no new geological detection. The mechanism is DTI economics
(α=0.2 FP charge, β=0.8 FN charge, 300 m triangular kernel): at score S a dot only pays if its
expected truth credit exceeds `0.2S/(1−0.2S)` ≈ 0.0588 at S=0.2778. Hidden "new fault" truth is
depleted in the 100–200 m halo of already-mapped faults (the paired H36-1 natural experiment at
equal budget isolates the halo deletion as worth +0.0068 USER-REPORTED; `evidence/nine_site_forensic_audit.json`),
so deleting halo dots cuts F faster than T, while 2.828 px far-field spacing avoids redundant
kernel coverage. The whole fleet table is consistent: sparse thin off-catalogue dots score
0.24–0.28; dense/thick/on-catalogue fields score 0.0009–0.19.

**Can a submission beat 0.2778?** In principle only by placing the same sparse budget on *new true*
off-catalogue traces the D2.8 surface missed. **No verified instance exists yet**: fleet-wide, the
best genuinely-unique scored file is 0.2190 (GEMSDOE27 H29); this session's PGR31 adds a null
result (paired CI crosses 0, SGMC proxy negative). The prompt's 0.3195 / 0.4413 leaderboard figures
remain USER-REPORTED with no organizer receipt and are not used as targets.

## 3. What PGR31 tested (3-experiment budget, all frozen before fitting)

Preregistration `knowledge/2026-10-26_pgr31_preregistration.md` (SHA-256 `a161635f…`) ranks five
untried hypotheses; the selected lane is **Poisson pseudo-gravity discordance**: Baranov vertical
integration of RTP to pseudo-gravity (equalising derivative order with gravity — distinct from
XFCOH31's raw cross-field gradients and from analytic-signal contact depth), then local
(σ=6 px, footprint-masked) Poisson regression slope/correlation/residual-gradient features.
Named mimic: unfaulted pluton/caldera contacts and GeoDAWN survey seams.

| Gate | Result |
|---|---|
| EXP-1 leakage canary (9 novel features alone vs withheld truth) | **PASS** — max two-sided AUC 0.5766 ≤ 0.90 (`evidence/pgr31/canary_seed51.json`) |
| EXP-1 screen, draw 51 (gems57-pooled-hide-v2, 2,778 withheld) | **FAIL** — Δ +0.0003 [−0.0202, +0.0240], 2/4 quadrants (NW 0.0579 vs 0.0944; SW 0.1202 vs 0.0656), SGMC proxy candidate 0.0478 vs control 0.0558 |
| EXP-2 fresh confirmation, draw 52 | **Not run** — frozen gate (screen must pass first) |
| EXP-3 surface uniqueness (pre-placement) | PASS vs genuine submissions — max \|Spearman\| 0.1506 ≤ 0.90 (48 rasters) |
| EXP-3 final-dots uniqueness | PASS vs genuine submissions — max 3-px overlap **48.6%** ≤ 70% (worst: HVDC); 33.2% vs H33; max \|ρ\| 0.0739 |
| Format / [0,1] (automated, no human inspector) | PASS — 0 hard failures, both encodings; 0 dots on/within 2 px of catalogue |
| Calibration-lattice disclosure | The 695-raster registry's spacing-5 calibration lattice lies within 3 px of essentially every interior cell, so the *literal* all-registry 70% rule is degenerate for any non-empty candidate; measured for PGR31 specifically: **99.26%** of its dots lie within 3 px of the restored registered lattice (`evidence/pgr31/registry_lattice_measured.json`); reported, not exempted (run card) |
| Determinism | Final surface SHA-256 `70bfab89…` reproduced bit-identically on a second run |

Interpretation (INFERENCE): individual pseudo-gravity features carry weak signal (AUC 0.52–0.58;
SW fold +0.055) but the gain does not generalise across quadrants and reverses in NW and on the
SGMC proxy — consistent with the named pluton/contact mimic dominating in part of the map. The
hypothesis is **not refuted as physics** (the canary and SW fold show signal), but as a
*submission surface at this budget/emitter* it earns no slot. Negative results are deliverables.

## 4. How to submit (only a future file whose run card says `verdict: promote`)

1. Open https://www.drivendata.org/competitions/306/competition-doe-gems/ → Submit.
2. Upload the **all-finite `-zeros.tif`** (or its single-TIFF `.zip`) whose run card shows
   `verdict: promote` — no current file qualifies.
3. Paste that file's reserved name/note from its run card; disclose AI use in the narrative as the
   official rules require (https://docs.nlr.gov/docs/fy26osti/96647.pdf). Never upload automatically.
4. Local validation is not organizer acceptance; keep the submission-page receipt — it is the only
   thing that can upgrade a USER-REPORTED score to ORGANIZER-CONFIRMED.

## 5. Irregularities flagged (no hallucinations; line-by-line sources)

1. No assigned method paragraph exists in the prompt (protocol rule 1) — disclosed in the
   preregistration; the lane was self-assigned from the ranked list the same prompt required.
2. 0.2778 / 0.2708 / 0.3195 / 0.4413 and every table score: USER-REPORTED, zero organizer receipts.
3. The 21.3 km holdout collar is **inherited** (`evidence/buffer_derivation.json`), not re-derived
   from PGR31's own OOF residuals — PGR31's own-method spatial range is unknown.
4. Competition inputs are hash-pinned **owner mirrors** (`registry/data_manifest.json`,
   restored this session `all_verified: true`); a hash match is byte identity to the mirror,
   not organizer authentication. DrivenData was not contacted in any way.
5. Holdout truth (public catalogue) and SGMC are proxies; they disagreed for PGR31 (catalogue
   Δ +0.0003, SGMC Δ −0.0080), which by the frozen gate is itself a fail.
6. Full JSON run card: `evidence/pgr31/run_card.json` (copy beside the TIF in `docs/downloads/`).
