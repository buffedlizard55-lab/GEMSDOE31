# Untested geological hypotheses — 2026-10-29 (arena/cc130eb1-gemsdoe31)

**Status of every hypothesis: NOT TESTED. Holdout validation is BLOCKED.**
Blockers: the feature stack and labels are not restored in this checkout; no method paragraph assigns a lane; the literal registry STOP stands; and no organizer receipt exists. No experiment ran. No slot is requested.

Ranking uses three criteria, in order: expected gain under the official DTI (INFERENCE from the metric; see the review, §3a), cost to build, and whether the idea is already in the repository. Each entry names its own failure mode, which the holdout must test.

## Method for any future test (applies to all four)

1. **Spatially blocked holdout.** Partition the footprint into blocks of at least 2 km, and withhold entire blocks, not random pixels. Score only on withheld blocks. A random-pixel split leaks along the same fault and inflates the score.
2. **Fixed-truth comparison.** Compare the candidate with the best existing dot family, on the same withheld blocks, using the repository's DTI code (`src/gemsdoe31/metric.py`, which matches the official formula).
3. **Non-fault mimic.** Build the mimic from the same features with the geological signal removed, and score it the same way. If the mimic scores close to the candidate, the candidate is not evidence of faulting.
4. **Duplicate gate.** Overlap and rank against every registered raster, before placement and on final dots. Stop if overlap is above 0.70 or rank is above 0.90.
5. **Budget.** At most 3 experiments and 2 hours. Promotion to a slot is a separate selector step.

## Ranked hypotheses

### Rank 1 — H-CC-A: thermal-spring collinearity (fault-controlled upflow)

- **Layer.** Nevada Bureau of Mines and Geology hot-spring and thermal-well inventory (positions and temperatures). Source: https://nbmg.unr.edu/geothermal/sitedescriptions.html
- **Signature.** Three or more thermal sites within 300 m of a common line, with that line's azimuth within a stated tolerance of the regional fault trend.
- **Why it might catch catalogue-missing faults.** Springs and wells can localise on permeable faults that have no mapped trace. This is an assumption to test, not a finding.
- **Difference from the repository.** No spring-alignment statistic exists (keyword search: zero hits for "hot spring" as a feature). The repository uses groundwater and conductivity context only.
- **Non-fault mimic.** Aquifer or playa-margin outflow; clusters of drill sites; mislocated wells. NBMG positions are accurate only to the quarter-quarter section (source: https://publications.mygeoenergynow.org/grc/1030316.pdf), which is comparable to the 300-m kernel.
- **Failure mode to test.** The spring count is small. Location error could make the alignment statistic noise.
- **Cost.** Medium.
- **Status.** Not tested. Blocked (data not restored; no lane).

### Rank 2 — H-CC-B: stress-orientation prior (World Stress Map)

- **Layer.** World Stress Map Database Release 2025: SHmax azimuths, quality A–C records. DOI 10.5880/WSM.2025.001, CC BY 4.0. Source: https://dataservices.gfz-potsdam.de/wsm/showshort.php?id=a23de1c9-1f73-11f0-914a-f12b0080820d
- **Signature.** Local lineament azimuth (from the strike and gradient-tensor features in `src/gemsdoe31/h31m_features.py` and related feature modules) agreeing with the azimuth expected from SHmax, weighted by record quality.
- **Why it might catch catalogue-missing faults.** Buried faults that share the regional orientation are the ones an azimuth prior can rank up. This is an expected relationship in an extensional setting, but it must be measured on the known faults in the holdout, not assumed.
- **Difference from the repository.** Zero keyword hits for "World Stress" or SHmax in `knowledge/`, `registry/`, `scripts/`, `src/`.
- **Non-fault mimic.** Dike swarms and topographic grain that also align with stress.
- **Failure mode to test.** The prior may only re-rank existing dots rather than add new truth. Because it is a weighting, it may not change the duplicate picture at all.
- **Cost.** Low to medium. The data licence is verified (CC BY 4.0).
- **Status.** Not tested. Blocked.

### Rank 3 — H-CC-C: seismicity nodal-plane alignment (re-scoped H5)

- **Layer.** USGS ComCat events with moment-tensor nodal planes (free). Source: https://earthquake.usgs.gov/fdsnws/event/1/
- **Signature.** Clusters of focal-plane strikes consistent with a fault segment that is absent from the catalogue.
- **Why it might catch catalogue-missing faults.** Seismogenic faults are often unmapped.
- **Difference from the repository.** The repository's H5 (in `knowledge/2026-10-25_lane_hypotheses.md`) was **not run**. Its stated objection is that epicentre location error is in kilometres against a 300-m kernel (the repo's own note, not re-measured here). That objection applies to epicentres. Focal-plane orientation may be less affected, but this is untested.
- **Non-fault mimic.** Induced seismicity from geothermal production; quarry blasts.
- **Failure mode to test.** Most events may be too few or too imprecise to resolve 300 m.
- **Cost.** Medium to high. Expected gain at 300 m is low.
- **Status.** Not tested. Blocked.

### Rank 4 — H-CC-D: heat-flow residual (SMU database)

- **Layer.** SMU Geothermal Laboratory heat-flow database (NGDS node). Source: http://search.geothermaldata.org/dataset/115609c8-6f52-49fe-a0af-9d379d516340. **Licence not verified.**
- **Signature.** Heat-flow residual against a regional conduction model, interpolated.
- **Why it might catch catalogue-missing faults.** Thermal upflow can mark active faults.
- **Difference from the repository.** Heat flow appears in archive notes only, not as a feature.
- **Non-fault mimic.** Radiogenic granite; sedimentary-basin thermal blanketing.
- **Failure mode to test.** Well spacing is coarse relative to 300 m, so the interpolated field cannot localise a fault. This is the weakest candidate on expected gain.
- **Cost.** Medium. Licence check needed first.
- **Status.** Not tested. Blocked.

## What was not proposed

- Any variant of catalogue pruning (already implemented as H33 / H31-AA families) and any density change: both are covered by the duplicate STOP.
- Any new TIFF. No raster is proposed for slot use.

## Validation decision

No candidate reaches the holdout stage. The top candidate (H-CC-A) is marked **untested and blocked**. It cannot move to a slot until: (a) the owner authorizes the data restore, (b) a method paragraph assigns one lane, (c) its holdout DTI with a 95% CI beats the non-fault mimic and the current best family on the same blocks, and (d) it passes the duplicate gate on surface and on final dots.
