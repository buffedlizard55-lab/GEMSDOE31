# Executive summary — selector decision 2026-10-26 (session arena/5b378be2-gemsdoe31)

Labels: **HOLDOUT-DTI** (evaluator, withheld positives, 95% CI) · **USER-REPORTED** (owner-typed,
no organizer receipt) · **COMPUTED** (raster measurement) · **PROJECTION** (estimate, never a score).
No ORGANIZER-CONFIRMED score exists in this repository. No upload, slot, or leaderboard access occurred.

## The decision (automated gates, no human inspector)

| Action | File (download this exact `.tif`) | Estimated live DTI (PROJECTION) | Unique vs discrete peers? |
|---|---|---|---|
| ✅ **SUBMIT (primary)** | `docs/downloads/gemsdoe31-h31t-transtension-dinkelbach-20261025-b37654-zeros.tif` (SHA-256 `83fbc267…`) | **0.317** [0.312, 0.323 in-family LOO; cross-family wider] | Yes — max 43.9% within 3 px; 34.1% vs H33; all \|ρ\| ≤ 0.90 |
| ✅ Alternate 1 | `docs/downloads/gemsdoe31-tgtd-submod-37654-20261025-ab35d4e8-zeros.tif` (H31-J) | 0.312 | Yes — max 49.9% |
| ✅ Alternate 2 | `docs/downloads/gemsdoe31-h31m-bstep-xmod-submod-20261025-37654-allfinite.tif` (H31-M) | 0.296 | Yes — max 59.9% |
| ⛔ Research only (new) | `docs/downloads/gemsdoe31-h31u-strainseis-corrob-37654-20261026-a02579ff-zeros.tif` (H31-U) | 0.205 | Yes — max 37.7% (but SGMC/projection gates fail) |
| ⛔ Research only | H31-B-standalone/hybrid, H31-S, HVDC, SCGP, RBU31-B, XFCOH31, MAGREST, CONCORD31 (see audit) | 0.18–0.41 (see caveats) | Yes, but efficacy/discovery gates fail |

Portal name `gemsdoe31-h31t-transtension-dinkelbach-20261025-b37654`; note (123/140)
`H31-T analytic-signal+listric+transtension Dinkelbach 37654d B2 | HOLDOUT-DTI 0.1300 n=60988 | selector G1-G6 pass 83fbc267`.
Steps: DrivenData → New submission → choose the exact `.tif` (or single-TIFF zip) → paste note →
check weekly quota → submit → keep organizer receipt with the SHA-256. The all-finite file is finite
in [0,1] at every cell, so it cannot trigger "Predicted values must be in range [0, 1]".

**Governance condition (IR-U-02).** The literal 695-raster overlap rule fails for *every* nonempty
candidate: the registered spacing-5 lattice lies within 3 px of 99.87% of the footprint (COMPUTED,
`evidence/h31u/exp2.json`). Promotions judge uniqueness against discrete peer *submissions* (the
population the rule exists to deduplicate), with the literal reading disclosed — owner-directed
rescope frozen in `knowledge/2026-10-26_h31u_preregistration.md`. If you require the literal reading,
the correct action is to submit nothing. Lane run cards keep `slot_approved=false`; only the
selector decision (`registry/selector_decision_20261026.json`) clears upload choice.

## Why did H33-2-B2 get 0.2778 (USER-REPORTED), and can we beat it?

COMPUTED lineage (`evidence/h33_forensics_20261025.json`): H19-5 four-line corroborated surface →
D2.8 Poisson dots (44,090; 0.2600) → delete dots ≤1 px from catalogue (H27-4; 40,199; 0.2708) →
delete dots ≤2 px (H33-2-B2; 37,654; 0.2778). Under DTI (α=0.2, β=0.8, 300 m triangular kernel),
an added dot helps iff marginal credit/FP-weight > 0.2S/(1−0.2S) (0.0588 at S=0.2778; isolated-dot
break-even kernel credit 0.0556 ≈ within ~283 m of uncovered truth). Anchor inversion over the
11 focus rasters (recomputed; LOO RMSE 0.0028 in-family) implies ~13.4k hidden-truth pixels and
that catalogue-flank dots earn ≈0.004 TPw/dot — hidden expert-mapped truth is depleted beside
already-mapped faults, so flank dots pay 0.2 FP-weight for almost no credit. Deleting 2,545 of them
is the entire 0.2708→0.2778 gain; the equal-budget H36-1 comparison (0.2710) proves it is *which*
dots were removed, not the count. Sparse 2.8 px spacing prevents 300 m-kernel redundancy.

**Beating it** therefore requires higher far-field (>200 m from catalogue) credit per dot at the
same budget/geometry — a better surface, not new emission. H31-T/J/M each beat H33 on the
independent off-catalogue SGMC discovery proxy at equal dots (H31-T TPw 6,236 vs H33 5,400,
COMPUTED) while also winning preregistered hide-and-recover holdouts — hence projections
0.30–0.32. This is evidence, not proof: the projection calibrates SGMC TPw on one dot family and
cross-family live transfer is unproven (historical cross-family Spearman ≈0.32). Nothing in this
repository evidences reaching the brief's 0.4413 figure (USER-REPORTED context).

## Nine focus sites — best historical file each (all USER-REPORTED; overlaps COMPUTED 2026-10-26)

| Site (tag) | Best file | Claim | Dots | Within 3 px of H33 | Unique-submittable? |
|---|---|---:|---:|---:|---|
| GEMSDOE32 | h33-h33-2-b2-…-zeros | 0.2778 | 37,654 | 100% (itself) | No — it is the reference/spent |
| GEMSDOE36 | anderson-geothermal-pinn-38854 | 0.2750 | 38,854 | 97.4% | No — duplicate lane |
| GEMSDOE28 | h36-1-rung30-blind-r1 | 0.2710 | 37,660 | 95.5% | No — duplicate lane |
| GEMSDOE31 (=28) | h27-4-solo-d28 | 0.2708 | 40,199 | 95.4% | No — duplicate lane |
| GEMSDOE28 | h38-1-hf-euler-r30-r1 | 0.2707 | 37,860 | 95.0% | No — duplicate lane |
| GEMSDOE28 | h32-1-prethin-tip-euler | 0.2649 | 42,294 | 91.6% | No — duplicate lane |
| GEMSDOE33 | h33d-analog-tip-stepover | 0.2632 | 41,865 | 92.6% | No — duplicate lane |
| GEMSDOE25 / 30 | dotted-h19-5-d2-8 (= D2.8) | 0.2600 | 44,090 | 88.2% | No — duplicate lane |
| GEMSDOE24 | h25-1-dotted-h19-5-d1-5 | 0.2477 | 60,069 | 88.5% | No — duplicate lane |
| GEMSDOE27 | topo-gap-closure-t-v2-on-d1-5 | 0.2449 | 61,328 | 86.7% | No — duplicate lane |

All eleven are one H19-5 geometry family; resubmitting any as "new" violates the duplicate rule.
Newer unique batches on those sites (USER-REPORTED 2026-10-25: GEMSDOE27 H29-HPVC 0.2190 is the
highest) and each site's current unscored candidate are tabulated in the README nine-site matrix
(prior COMPUTED audit, 2026-10-26) — none is cleared here; only GEMSDOE31 candidates were gated.

## This session's new lane H31-U (negative result — deliverable)

Preregistered (`knowledge/2026-10-26_h31u_preregistration.md`): five ranked hypotheses
(U1 strain+seismic+tilt+scarp corroboration; U4 tilt+scarp+alteration; U2 tilt alone;
U5 six-line; U3 basement+conductance), three experiments, frozen gates G1–G6. Data: local cache
only (no new external source needed). Results (HOLDOUT-DTI, `gems57-pooled-hide-v2`, n=60,988):
U5 six-line geometric mean won the screen (0.0952 [0.080, 0.109] final; +0.0281 [0.0052, 0.0508]
vs generic-ridge control; +0.0270 vs best single line; canaries ≤0.61 two-sided; discrete
uniqueness max 37.7%, max |ρ| 0.085). But off-catalogue SGMC reached only 0.0703 vs H33 0.0940
and PROJECTION 0.205 < 0.2778 → G4/G6 fail → `negative`, DO NOT SUBMIT
(`evidence/h31u/run_card.json`). Interpretation: strain/seismicity fronts recover *catalogue-like*
faults yet miss the SGMC/expert-style discovery population — the two proxies genuinely disagree,
and the frozen rule correctly refuses to spend a slot on a one-proxy win. Mimics observed in
design: GPS block-model strain artifacts and diffuse seismicity fronts plausibly dilute far-field
precision at 300 m scale.

## Ranked hypotheses status & next work

Executed: U1–U5 (U5 selected, negative on discovery proxy). Untried but costed in preregistration
lineage: paired-CI confirmation for H31-B-standalone (highest SGMC 0.1391/PROJECTION 0.409 but
fail-closed on G3 and proxy-selection risk — a preregistered hide-and-recover paired test vs H31-T
on the shared evaluator is the single highest-value next experiment); InSAR creep lines (blocked:
ASF/NASA Earthdata outside sandbox allowlist); organizer-authenticated receipts (owner uploads
generate the first ORGANIZER-CONFIRMED numbers — record them against SHA-256 immediately).

## Limitations (what I cannot do here)

No DrivenData authentication (cannot upload, check quota, or read the live leaderboard — by design
and by AGENTS.md); competition inputs are owner-mirror bytes (hash-verified to the mirror, not
organizer-authenticated); hidden truth is private, so all live expectations are PROJECTIONs;
2 CPU / 3.8 GB sandbox (full-grid CPU pipelines only). Free official sources already mirrored:
USGS GeoDAWN + 3DEP, GDR-1391 (DOI 10.15121/1881483), USGS SGMC — see `registry/sources.json`.

## Manual-review links

Competition <https://www.drivendata.org/competitions/306/competition-doe-gems/> ·
problem <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/> ·
reference solution <https://github.com/drivendataorg/gems-prize-reference-solution> ·
NLR rules <https://docs.nlr.gov/docs/fy26osti/96647.pdf> ·
GDR-1391 <https://gdr.openei.org/submissions/1391> ·
GeoDAWN <https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and> ·
INGENIOUS <https://gbcge.org/current-projects/ingenious/> · EPSG:32611 <https://epsg.io/32611> ·
Tversky index <https://en.wikipedia.org/wiki/Tversky_index>
