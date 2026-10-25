# Lane hypotheses, E1-E3 results, calibration and the b2 question (2026-10-25)

Claim classes: **HOLDOUT-DTI** = computed here by evaluator `LANE-EVAL-1` on owner-mirror inputs. **USER-REPORTED** = a leaderboard
number the project owner typed into a prompt (no organizer receipt). **SECONDHAND** = read from a sibling owner repository, not verified.
**PROJECTION** is never a score. No file in this repository has an ORGANIZER-CONFIRMED score.

## 0. Bottom line

* **No file is cleared for submission today.** The lane candidate (AS-1) is format-valid and byte-unique, but it failed its preregistered
  holdout gate (E3) *and* it is a protocol duplicate of 14 registry rasters (>70 % of its dots within 3 px of one of them).
  Verdict: **negative**. Receipts: `docs/downloads/blocked/*-gate-*.json`, run card `evidence/run_card_lane_as1.json`.
* **Uniqueness and live validation pull in opposite directions.** Every geometry family with a live score at or above ~0.26 is the D28 family
  (a thinned ridge/geophysics lattice) and its descendants. Anything that is *unique* under the lane rule is, by construction, outside that
  family and has no live evidence. The local proxies cannot bridge that gap (section 4).
* **LiDAR-scarp-led files have already been tried by siblings and score badly live** (section 4): 0.038 to 0.159 USER-REPORTED, against 0.2778
  for the live best. AS-1 sits on top of that family: three of its 14 duplicate rasters have live scores, 0.1589 (r11f), 0.1352 (h30 arrangement-matched habitat) and 0.0843 (r12).

## 1. Why did h33-2-b2 score 0.2778 (USER-REPORTED, GEMSDOE32)?

SECONDHAND (GEMSDOE32 `docs/research/`): b2 is the 0.2708 D28 base with every dot within 2 px of the public catalogue deleted (37,654 dots).
Our own measurement agrees on the direction: the registered D28 file earns more per dot than any detector arm, and the score ladder across the D28
family (USER-REPORTED) is monotone in thinning: 60,069 dots 0.2477, 44,090 dots 0.2600, 40,199 dots 0.2708, 37,654 dots 0.2778.
Mechanism that fits all of it (INFERENCE): the hidden truth is depleted near the public catalogue (experts labelled *new* faults), and the metric
charges 0.2 per emitted pixel, so dots that sit where truth is unlikely cost more than they can earn. A dot at distance d from a scored truth pixel
only pays if its kernel credit exceeds 0.2 s / (1 - 0.2 s) (at s = 0.2778 that is about 0.0588, i.e. within about 280 m).

**Can a submission beat it?** Not shown. The honest statement is: the only lever with a live-measured positive slope is *fewer, better-placed
dots in the D28 geometry*, and the sibling STRAINBREAK/BREAKLINE/PRUNE variants already explore it. Beyond that the evidence is silent.

## 2. Ranked hypotheses (expected DTI gain x cost, before running anything)

| Rank | Id | Layers | Physical signature | Why it could find faults missing from the catalogue | Differs from the repo how | Cost | Status |
|---|---|---|---|---|---|---|---|
| 1 | H4 catalogue-shadow geometry | `labels.tif`, D28 emission | truth is depleted near the catalogue (b2) | a generalised exclusion shape (radius, one-sided, along-strike) removes dots with negative expected credit | derivative of D28, so it **cannot** be unique under the lane rule | very low | NOT RUN: no proxy can score it (proxies are built from the same catalogue); only a live slot tests it |
| 2 | H1 AS-1 antislope scarps | 12 LiDAR bands (3DEP) | up-facing facets, asymmetric step | 1-10 m scarps are invisible at 100 m | label-free LiDAR percentile surface | low (data in hand) | **E1, E3 negative**; duplicate of sibling lanes |
| 3 | H3 gap-zone geophysics | gravity, basement depth, conductance, `tmi_hg` in the 24.6 % non-LiDAR zone | gradient lineaments | covers the zone LiDAR cannot | gap-only surfaces | low | **E2b refuted** |
| 4 | H2 road mask | TIGER/Line 2024 roads (free official source, verified, restored) | cultural lineaments mimic scarps | removes road cuts | mask on top of H1 | low | **E2a refuted** (paired CI excludes 0, on both proxies the mask lowers or does not change DTI) |
| 5 | H5 seismicity alignments | USGS ComCat via FDSN | epicentre alignments, nodal planes | seismogenic faults are often unmapped | uses focal mechanisms, not the 100 m density band already provided | medium | NOT RUN. Expected gain low: location error (km) is far above the 300 m kernel. Source is official and documented; the endpoint is blocked from this sandbox (the page was readable, the download was not tested) |

Data source checks: TIGER road distance was built from the GEMSDOE24 owner mirror (sha256 `e5350423...2988`), the originating dataset is the
Census TIGER/Line 2024 roads. FDSN documentation fetched 2026-10-25: https://earthquake.usgs.gov/fdsnws/event/1/ . The competition's own
description (page 967, fetched 2026-10-25) already lists a *density of earthquakes* band among the provided features, so seismicity is not an
overlooked source, only a coarse one.

## 3. Experiments (budget: 3)

Label: E1 and E2 designs were declared in their script docstrings before running (no external timestamp, so this is **self-declared**); E3 was
**committed to git before it ran** (`c1a6284`). Procedure hash added to `evidence/lane_e3.json` afterwards as provenance only (the re-run was
bit-identical apart from that field).

* **E1** (`evidence/lane_e1.json`): leakage canary max AUC 0.77 (< 0.90). Best surface differs by proxy (SGMC: generic `ex_max` 0.147;
  catalogue-gap: antislope-dominant 0.093). Proxy DTI keeps rising with budget to 50k dots, so budget does not transfer.
* **E2** (`evidence/lane_e2.json`): road mask refuted, gap-fill refuted (no gap surface beats the incumbent's 0.170 credit per dot).
* **E3** (`evidence/lane_e3.json`, preregistered): fresh seeds 11-15, 152,681 withheld pixels. AS-1 0.0755 [0.060, 0.090] vs random-score null
  0.0688: paired difference +0.0065 [-0.0055, +0.0185]. **Gate failed.** AS-1 vs generic scarp S0: +0.0156 [0.0085, 0.0227] on the gap proxy but
  -0.0049 on SGMC, so the antislope-over-generic claim is not confirmed. b2 scores 0.0058 on this proxy only because it was pruned against the full
  catalogue including the hidden half: the comparison is structurally unfair to b2 and also shows the proxy cannot see the live mechanism.

## 4. Calibration: how far can these instruments be trusted? (`evidence/instrument_calibration.json`)

87 registry rasters with USER-REPORTED live scores (1 ambiguous fragment skipped, 23 fragments not found in the registry).
Spearman of local proxy vs live: SGMC DTI +0.32 (p 0.003), catalogue-gap DTI +0.11 (p 0.32), 3 px coverage +0.40, dot count +0.11.
Reading: weak, and **inverted across families**. Examples (live USER-REPORTED vs SGMC DTI): `r11f-scarp-radiometric-fusion` 0.1589 vs 0.167;
`h59-sharpened-scarp-scatter-90k` 0.0764 vs 0.249; the D28 family 0.26-0.2778 vs 0.093. Nine scarp/LiDAR-led files range 0.038-0.159 live.
So a candidate that wins on SGMC (AS-1: 0.142) is exactly the profile of files that lost live. This is the strongest argument against spending a
slot on any LiDAR-scarp candidate, and it is the reason the gate's evidence rule is preregistered rather than proxy-ranked.

## 5. Format root cause (SECONDHAND, GEMSDOE32 `docs/research/range-error-root-cause-2026-10-03.md`, official wording re-read here)

Page 967 (fetched 2026-10-25): single layer, float32, values between 0 and 1, same CRS/resolution/bounds, "data outside the bounds is null or nan".
The training stack has float32 sentinel (-3.4028e38) pixels inside the scoring footprint (3,061 per band, SECONDHAND) and a footprint mask taken
from a feature band strands 3,061 scored pixels as NaN. Either produces "Predicted values must be in range [0, 1]". Our builder derives the
footprint **only** from the template, hard-fails non-finite inside, and ships both conventions. The owner ledgers show both `-nan` and `-zeros` files
scored, so both are accepted by the portal (USER-REPORTED). Default: all-finite (zeros outside) is the one that cannot trip a whole-array range check.

## 6. Irregularities flagged

1. The prompt's 0.4413 equals GEMSDOE32's local proxy `R2-safe-zeroTPp` (0.44127926). Probably a mislabelled proxy, and it conflicts with 0.3195.
2. The prompt's method paragraph is missing.
3. The organizer `sample_submission` non-zero cells (60,988) are exactly the public catalogue. Only its footprint may be used.
4. 7GEMSDOE README lists the LiDAR ridge top2pct file as unscored; the user reports 0.1461.
5. The raw lane-overlap rule is vacuous against dense rasters (a 120k-dot raster covers most of the footprint within 3 px). The gate reports raw,
   chance and chance-adjusted overlap; 21 of the 715 compared registry rasters have chance overlap >= 0.5.
6. `registry/raster_registry.json` previously inherited scores by loose fragment (b2 variants inherited 0.2778). Fixed: exact fragments, ambiguous skipped.

## 7. Next session (ordered)

1. Decide whether to spend **one** live slot as an experiment on H4 (a generalised catalogue-shadow) from the D28 family. It is the only idea with a live-measured
   slope. It is not unique, so it needs an explicit owner decision to waive the uniqueness gate; the gate will say so.
2. Obtain the organizer's real scoring behaviour for NaN vs zero outside (one portal test with a template-identical all-zero file is free of risk).
3. Build a paleoshoreline mask (Lake Lahontan) before any further LiDAR-scarp work: it is the mimic most likely to fool scarp detectors in the Great Basin, and it was not tested.
4. Register the 23 unmatched score fragments by fetching the missing files (they are not in the cloned repositories).

## 8. Links for manual review

* Competition: https://www.drivendata.org/competitions/306/competition-doe-gems/ (problem description page 967, fetched)
* Reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
* NLR rules PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf
* GDR submission 1391: https://gdr.openei.org/submissions/1391
* USGS GeoDAWN: https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and
* INGENIOUS: https://gbcge.org/current-projects/ingenious/
* EPSG:32611: https://epsg.io/32611 · Tversky index: https://en.wikipedia.org/wiki/Tversky_index
* USGS FDSN event service (fetched): https://earthquake.usgs.gov/fdsnws/event/1/
* Forum thread on masking known faults (SECONDHAND via GEMSDOE32): https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516
