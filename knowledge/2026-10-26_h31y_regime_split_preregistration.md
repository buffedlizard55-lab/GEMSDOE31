# H31-Y preregistration — regime budget-split: piedmont-junction × buried-basement piedmont specialist

Frozen **before any fitting** in session `arena/579233d5-gemsdoe31` (2026-10-26). Written after reading
`AGENTS.md`, the README selector decisions, `registry/selector_decision_20261026.json`,
`evidence/selector_audit_20261026.json`, `evidence/h31x/run_card.json` and
`knowledge/2026-10-26_h31x_piedmont_junction_preregistration.md`. No DrivenData contact; no leaderboard
access; no automatic submission. Inputs restored hash-verified from owner mirrors this session
(`evidence/data_restore_20261026_session579233d5.json`, `all_verified=true`); a hash match proves byte
identity to the mirror, **not** organizer authenticity.

Claim classes: **OFFICIAL** · **OWNER-MIRROR** · **COMPUTED** · **USER-REPORTED** (owner-typed, no receipt) ·
**HOLDOUT-DTI** (evaluator, withheld positives, 95% CI) · **PROJECTION** (estimate, never a score).
No ORGANIZER-CONFIRMED score exists in this repository.

## Lane assignment disclosure (IR-U-01, again)

The Parallel-Run Protocol §1 says "Your lane is the single method paragraph below", but **no method
paragraph was supplied** in this session's prompt either (the same omission every prior session recorded).
Per the owner's overriding instruction to generate and validate a unique submission autonomously, this
session self-assigns and freezes the single lane paragraph below before touching data beyond restore/prepare.
The previous session's declared next step — *"a budget-split lane (junction + piedmont specialist) is the
natural next step"* (`knowledge/2026-10-26_h31x_executive_summary.md` §6) — is exactly this lane.

## Lane paragraph (single method — stay inside it)

**H31-Y "regime budget-split emission".** Two label-free specialists, each given a fixed share of the
37,654-dot budget, emitted jointly with one shared 2.8 px Poisson exclusion and the live-proven B2
catalogue-flank prune (`d(catalogue) > 2 px`):

1. **JUNC** — the H31-X X1 piedmont-junction line, byte-for-byte the same formula (directional concave-up
   slope break `J = max(0, −∇s·û)` from `det_elev`/`det_elev_slope`, σ = 1.5 px, soft slope window
   3°–15° full / 0 at 1° and 25°, **raw, no NMS** — the variant H31-X's preregistered ablation selected).
   It is recomputed from the cached stack, not copied from any prior surface or dot file.
2. **PIED** — a buried-basement piedmont specialist for terrain where a fault has little or no surface
   expression: the geometric mean (× second-line gate) of three potential-field/basement edge lines,
   footprint percentile ranks — **ASIG** `rank(√(tmi_hg² + tmi_vg²))` (analytic-signal amplitude,
   polarity-independent magnetic contact locator), **BASE** (H31-U definition verbatim: geometric mean of
   `rank(|∇ depth_to_base_surf|)`, `rank(|∇ cond_surf|)`, `rank(|iso_grav_anom_slope|)`, σ = 1.5 px),
   **GRAV** `rank(|iso_grav_anom_hg|)`. PIED dots are restricted to the piedmont regime
   (`det_elev_slope ≤ 6°`, the selector's regime definition) in the split arms.

Emission order (deterministic): JUNC quota first (unrestricted regime), then PIED quota with every pixel
within 2.8 px of a JUNC dot excluded (exact EDT), both via the shared `poisson_disk_emit`
(`max_pool=400_000`, as in `run_h31u.emit_dots`). Implementation rule frozen here: if either quota emits
fewer dots than its quota (pool exhaustion), the shortfall is topped up from the other surface under the
same exclusion, JUNC topping up PIED first; the emitted per-surface counts are recorded in every receipt
so any top-up is visible, never silent. No prior dots,
surfaces or peer rasters enter the candidate; peer rasters are used only for the uniqueness audit and the
SGMC/projection instruments (learning only).

## Why H33-2-B2 (0.2778 USER-REPORTED) leads, and the measured opening (COMPUTED facts only)

Lineage and metric economics are established work (`evidence/h33_forensics_20261025.json`,
`knowledge/2026-10-26_h31x_executive_summary.md` §3): H33 = D2.8 Poisson dots on the H19-5 surface with
dots ≤2 px from the catalogue deleted; under DTI (α = 0.2, β = 0.8, 300 m triangular kernel) a
non-redundant dot helps iff kernel credit `k > 0.2·S`; flank dots earn ≈0.004 TPw/dot vs the 0.0556 bar at
S = 0.2778. For a fixed 37,654-dot field the only remaining lever is **more hidden truth per far-field dot**.

The opening is regime complementarity, measured same-code in the selector audit
(`evidence/selector_audit_20261026.json`, off-catalogue USGS-SGMC DTI by slope regime, COMPUTED):

| Candidate | SGMC all | piedmont ≤6° | mountain >6° | Catalogue HOLDOUT-DTI (`gems57-pooled-hide-v2`) |
|---|---:|---:|---:|---:|
| H31-X (JUNC alone, current selector primary) | 0.1209 | 0.0634 | 0.1303 | 0.1661 [0.1499, 0.1821] |
| H31-B-standalone (scarp-Hessian) | 0.1391 | 0.0610 | 0.1563 | no paired CI on shared evaluator (G3 fail-closed) |
| H31-T (analytic-signal/listric) | 0.1082 | **0.0991** | 0.0940 | 0.1300 [0.1147, 0.1456] |
| H31-J | 0.1064 | 0.0871 | 0.0980 | pass (card) |
| H33-2-B2 (USER-REPORTED 0.2778) | 0.0940 | — | — | handicapped fixed-dot reference only |

Every mountain specialist is weak in the piedmont and vice versa; the two truth proxies themselves sample
different regimes (catalogue median slope 5.6°, off-catalogue SGMC median 13.5°, COMPUTED in the H31-X
session). H31-X's corroboration arms (geometric-mean gates X2/X3/X4: 0.1019/0.1222/0.1147 HOLDOUT-DTI) show
that **multiplying** lines dilutes the junction signal. A **quota split** does not multiply anything: it
replaces the bottom-ranked half of one specialist's dots (lowest marginal credit, by construction of the
score-ordered emission) with the top-ranked half of a specialist that covers *different* truth segments.
Under the kernel-max structure of TPw this union can exceed either full field when the specialists'
covered-truth sets are sufficiently disjoint — and can also lose if PIED's top half earns less than JUNC's
bottom half. That is the measured question of EXP-1, not an assumption.

**Uniqueness constraint that sizes the quotas (frozen reasoning):** a JUNC quota emitted from the same
surface reproduces the first dots of H31-X's own emission, so the within-3-px overlap vs the H31-X peer
raster is bounded below by roughly the JUNC share. A 65% JUNC quota therefore risks breaching the owner's
70% duplicate rule against H31-X even before PIED dots that happen to fall near H31-X dots are counted.
Eligible candidate arms are capped at a 50% JUNC share; a 65/35 split is scored as a **reference arm only**
(informative about the quota trade-off, never promotable from this lane).

## Ranked hypotheses not yet tried in this repository

| Rank | ID | Layers / physical signature | Why it should catch a catalogue-missing fault | Difference from everything implemented here | Expected gain / cost |
|---|---|---|---|---|---|
| 1 | **Y-SPLIT50 (selected candidate family)** | `det_elev(_slope)` JUNC line + `tmi_hg/tmi_vg` analytic signal, `depth_to_base_surf`, `cond_surf`, `iso_grav_anom(_hg/_slope)` PIED line; fixed 50/50 quota, PIED restricted to slope ≤6° | Buried piedmont faults are invisible in terrain (no slope break to rank) but offset magnetic basement and step basin thickness/conductance; experts adding them use exactly these subsurface edges. JUNC keeps the range-front population QFFD under-lists | All prior multi-line lanes *blend* surfaces (geometric mean / HGB / rank blend) before one emission; none allocate a hard per-regime dot quota between a terrain line and a potential-field line with a shared spacing exclusion. RBU31 balanced *training-sample weights* of a catalogue-trained HGB (failed mountain placement); this lane is label-free and balances *emission budget* | highest; ~20 min on cached stack |
| 2 | Y-ROUTE | Same lines; single surface `S = exp(w·ln JUNC + (1−w)·ln PIED)`, `w = clip((slope−3°)/6°, 0, 1)` | Same geology, soft version: lets a strong piedmont magnetic edge at 7° still win dots | Slope-dependent exponent routing has never been used here (fixed-weight blends only) | high; same cost |
| 3 | Y-SPLIT35 | Same lines; 35% JUNC / 65% PIED quota | Tests the catalogue-truth regime prior (catalogue is piedmont-dominated) at the cost of mountain coverage | As rank 1 | medium; same cost |
| 4 | KIN (costed, not run — carried from H31-X prereg) | LiDAR `downface_max`/`upface_max` facing agreement with the gravity-defined basinward vector (synthetic vs antithetic scarps) | Small scarps below QFFD compilers' threshold; facing *direction* separates fault scarps from shoreline/terrace mimics | Vector agreement, not scalar co-location; no lane uses scarp polarity vs a gravity vector | medium; ~30 min, LiDAR covers ~75% of footprint |
| 5 | TEX (costed, not run — carried from H31-X prereg) | RTP structure-tensor orientation/coherence discontinuity lines | Bedrock faults in volcanics truncate magnetic fabric without a gradient edge | All magnetic lanes here are gradient/phase based | low–medium; ~45 min, survey-seam mimic risk |

Named non-fault mimics: for JUNC — erosional pediment edges, Lahontan shorelines, fan-terrace risers,
lava-flow snouts; for PIED — tabular basalt-flow margins and caldera rims (analytic-signal highs with no
basement step: suppressed by the BASE/GRAV corroboration gate), lithologic contacts inside unfaulted
volcanic piles, conductive playa/evaporite edges (cond_surf gradients with no magnetic/gravity step),
survey-boundary seams in the magnetic compilation.

## Frozen experimental plan (≤3 experiments; stop afterwards)

Common protocol (identical to H31-X so numbers are comparable): vendor `spatial.folds(buffer_px=213)`,
unchanged `gems57-pooled-hide-v2` evaluator, per-fold emission with visible-catalogue B2 pruning, full
37,654-dot budget per fold, pooled paired CIs (`ev.pooled_summary`, 2,000 draws, seed 520810).

- **EXP-1 (canary + screen).** Leakage canary: ROC-AUC of every line (JUNC_RAW, ASIG, BASE, GRAV, PIED,
  CTRL, SLOPE) and the ROUTE surface alone vs catalogue and vs off-catalogue SGMC (200k negative sample);
  two-sided AUC > 0.90 = leakage STOP for that feature. Replication check: the JUNC arm must reproduce
  H31-X's X1-raw screen (HOLDOUT-DTI 0.1661 [0.1499, 0.1821], 60,988 withheld) to within floating-point
  tolerance; if it does not, STOP and diagnose before interpreting anything. Screen arms:
  {JUNC, PIED (unrestricted, specialist baseline), SPLIT50, SPLIT35, ROUTE, CTRL = rank(`tmi_hg`),
  SLOPE = rank(`det_elev_slope`), SPLIT65-REF (reference only)}. Candidate winner = highest pooled
  HOLDOUT-DTI among {SPLIT50, SPLIT35, ROUTE}. Paired deltas vs JUNC, CTRL and SLOPE are recorded for
  every arm.
- **EXP-2 (one ablation + uniqueness).** Winner with the piedmont restriction on the PIED quota OFF
  (for ROUTE: exponent routing replaced by fixed 50/50 log-blend) vs ON; keep the better on pooled holdout.
  Final emission on the full catalogue (B2). Uniqueness: final-dot 3-px overlap and Spearman vs every
  discrete peer dot field (nine focus sites hash-verified + all local GEMSDOE31 downloads, twins
  deduplicated); for split arms the audit surface is the ROUTE blend of the same lines (disclosed proxy —
  a quota emission has no single surface; the final-dot check is the owner's rule and is exact).
  |Spearman| > 0.90 or final-dot overlap > 0.70 vs any discrete peer = duplicate STOP for promotion.
  The literal 695-raster spacing-5-lattice reading is recomputed and disclosed (IR-U-02), never exempted.
- **EXP-3 (independent confirmation + packaging, zero tuning).** Untouched confirmation on a different
  partition of truth: seeded random 50% split of whole 8-connected catalogue components, **seed 3104**
  (H31-X used 3103; a new seed keeps this lane's confirmation untouched by its design), visible half masked
  pixel-exactly and used for B2 pruning, same evaluator terms and 20 km block paired bootstrap. Then
  full-footprint, per-quadrant and slope-regime off-catalogue SGMC DTI for the candidate vs H33-2-B2 and
  vs the H31-X final dots (fixed-dot full-footprint SGMC is not handicapped — SGMC truth is >3 px from the
  catalogue), anchor-inversion PROJECTION (eleven focus anchors, LOO RMSE), vendor
  `submission_writer.write_submission`, both local validators (all-finite and NaN-outside conventions).

## Frozen promotion gates (automated; no human inspector) — identical to the selector's G1–G6

- **G1 format:** single-band float32, EPSG:32611, 3730×3292, exact transform, finite [0,1] inside the
  footprint, correct outside convention per file, {0,1} values, 0 dots on the catalogue, ≥2.8 px spacing,
  exactly 37,654 dots.
- **G2 canary:** every used line/surface two-sided AUC ≤ 0.90 on both truths.
- **G3 efficacy:** pooled HOLDOUT-DTI beats CTRL **and** SLOPE with paired 95% CI excluding 0, ≥3/4
  quadrants ≥ CTRL, and the seed-3104 confirmation paired delta vs CTRL also excludes 0.
- **G4 discovery proxy:** full-footprint off-catalogue SGMC DTI ≥ H33-2-B2's value recomputed the same day.
- **G5 uniqueness (discrete-peer scope, IR-U-02):** final-dot 3-px overlap ≤ 0.70 and |Spearman| ≤ 0.90 vs
  every discrete peer; literal lattice reading disclosed. (Deliberately the owner's rule as written, not
  H31-X's stricter pre-placement top-K variant; the top-K number is still computed and reported.)
- **G6 projection:** anchor-inversion PROJECTION ≥ 0.2778 (never written as a score).
- Lane verdict `promote` only if G1–G6 all pass; otherwise `negative` (research download only,
  DO NOT SUBMIT). Whether a promoted H31-Y replaces H31-X as the selector primary is a **separate selector
  step** re-running `scripts/selector_audit.py` with H31-Y added under its frozen rules; this lane does not
  pick the submission. No fourth experiment, no tuning after EXP-3. A negative result is a deliverable.

## Data

No new external data is needed or used: the 42-band prepared stack (`scripts/prepare_data.py` over the
hash-verified owner mirrors: OFFICIAL-source GeoDAWN/USGS-3DEP-derived layers, OWNER-MIRROR competition
rasters) already contains every band named above. KIN also needs no new data; TEX needs none; InSAR
remains blocked (NASA ASF/Earthdata outside the sandbox host allowlist — named official source:
https://search.asf.Alaska.edu / NASA OPERA DISP-S1, checked in prior sessions, not obtainable here).

---
*Post-merge note (2026-10-26): lane id "H31-Y" collided with parallel session arena/f4d7fb29's
H31-Y KIN-PIED lane; this lane is cited as H31-YR and its code/evidence live under
`scripts/run_h31y_regimesplit.py` / `evidence/h31y_regimesplit/`. Permissions are governed by
`registry/release_status.json` (literal registry STOP): everything here is research-only.*
