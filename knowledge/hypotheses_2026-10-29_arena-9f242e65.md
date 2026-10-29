# Untested, ranked geological leads — 29 October 2026

**Decision: no candidate is presently viable to implement.** The user-provided prompt contains no assigned method paragraph, the production feature stack is absent, and the literal any-registry STOP is binding. No holdout, canary, fit, or experiment was run. These are desk hypotheses, not numerical forecasts or permission to start a lane.

The ranking below is qualitative and ordered by *plausible* DTI benefit, then build cost and novelty relative to the current branch. The official DTI weights false positives at 0.2 and false negatives at 0.8. No numeric improvement is estimated: there is no calibrated mapping from these external layers to private competition truth, and no competition score receipt.

| Rank | Hypothesis | Expected DTI upside (qualitative only) | Implementation cost | Current viability |
|---|---|---|---|---|
| 1 | **Thermal-site / structural-axis alignment** | Medium potential, very high uncertainty; sparse sites might supply high-precision independent evidence, but positional error and tiny sample size can erase the gain. | Medium–high; first establish a machine-readable inventory and coordinates. | **Not viable yet:** NBMG link is identified, but this session did not verify a downloadable point table, coordinate precision, full-footprint coverage, or reuse terms. |
| 2 | **World Stress Map orientation prior** | Low–medium potential; useful mainly to re-rank lineaments, not necessarily add true fault detections. | Medium; data processing and spatial interpolation. | **Not viable yet:** official DOI/link is identified, but no source files were retrieved or coverage checked in this session. License/metadata assertions are inherited from earlier repository notes, not freshly re-verified here. |
| 3 | **Focal-mechanism nodal-plane alignment** | Low potential at the 300 m kernel; orientation may help even where epicentres are imprecise, but event density is unknown. | Medium–high; parse mechanisms, quality, depth and uncertainty. | **Not viable yet:** ComCat endpoint is identified; no events were retrieved or coverage/error assessed. The concept is distinct from the earlier unrun epicentre-density idea, but still untested. |
| 4 | **Heat-flow residual against a regional conduction model** | Very low potential at 300 m; measurement spacing and interpolation likely smear the target. | High; source licensing and harmonization first. | **Not viable:** the SMU/NGDS link is identified, but no data were retrieved and its license remains unverified. |

## Hypothesis specifications and failure tests

### 1. Thermal-site / structural-axis alignment

- **Layer:** Nevada Bureau of Mines and Geology geothermal site descriptions: <https://nbmg.unr.edu/geothermal/sitedescriptions.html>.
- **Signature:** if a source-quality check finds at least three independently located hot-spring or thermal-well records, estimate a quality-weighted local axis; test whether the axis aligns with a mapped-independent geophysical lineament within a preregistered azimuth tolerance. Do not rasterize the public catalogue itself as a predictor.
- **Mechanism:** geothermal discharge can exploit permeable faults that are absent from a regional fault catalogue. This is a physical rationale, not an established result for these sites.
- **Named non-fault mimics:** aquifer or playa-margin outflow, clustered drilling, and location/geocoding error.
- **Prior-art search:** no thermal-site alignment statistic was found in the current branch's `src/` or `scripts/` at review time. The repository does contain groundwater and conductivity context. This is a scoped source-code search, not a search of every sibling repository.
- **Source gate:** the linked page is not evidence that a georeferenced, machine-readable product is obtainable. Verify the product and accuracy before calling the lane viable.

### 2. World Stress Map orientation prior

- **Layer:** World Stress Map Database Release 2025, DOI 10.5880/WSM.2025.001: <https://dataservices.gfz-potsdam.de/wsm/showshort.php?id=a23de1c9-1f73-11f0-914a-f12b0080820d>.
- **Signature:** compare a lineament's local gradient-tensor/strike azimuth with the quality-weighted SHmax-derived normal-fault orientation; require an explicit angular tolerance and test the feature alone.
- **Mechanism:** faults compatible with the current regional stress may be more likely to remain mechanically active or permeable. Do not assume every old mapped lineament shares that stress field.
- **Named non-fault mimics:** dike swarms and topographic or lithologic grain that also follows regional structure.
- **Prior-art search:** no WSM/SHmax orientation feature was found in the current branch's `src/` or `scripts/`.
- **Source gate:** no WSM product was downloaded here. The repository's earlier CC BY 4.0 note is not a fresh license/product verification.

### 3. Focal-mechanism nodal-plane alignment

- **Layer:** USGS ComCat FDSN event service: <https://earthquake.usgs.gov/fdsnws/event/1/>.
- **Signature:** cluster quality-screened nodal-plane strikes and test whether they support an independently detected lineament absent from the public catalogue. Use the preferred solution and both-plane ambiguity explicitly; do not treat epicentre density as a fault trace.
- **Mechanism:** focal-plane orientation can provide an independent kinematic constraint on seismogenic structures.
- **Named non-fault mimics:** induced geothermal seismicity, quarry blasts, and unrelated overlapping event sequences.
- **Prior-art boundary:** a previous desk note considered epicentre alignments and flagged kilometre-scale location error; the focal-plane-orientation hypothesis is different, but the current branch has no focal-mechanism feature in `src/` or `scripts/`.
- **Source gate:** the API URL is identified, but event count, magnitude completeness, location uncertainty and focal-mechanism coverage were not measured.

### 4. Heat-flow residual

- **Layer:** SMU Geothermal Laboratory / NGDS catalog record: <http://search.geothermaldata.org/dataset/115609c8-6f52-49fe-a0af-9d379d516340>.
- **Signature:** remove a preregistered broad regional conduction trend, then test whether residual anomalies localize independently of known fault labels.
- **Mechanism:** fault-controlled fluid flow can perturb local heat transport.
- **Named non-fault mimics:** radiogenic granite and sedimentary-basin thermal blanketing.
- **Prior-art search:** no heat-flow raster/feature was found in the current branch's `src/` or `scripts/`; heat flow appears only in historical notes.
- **Source gate:** dataset contents, spatial precision, license and availability remain unverified. Coarse well spacing may make a 300 m localization impossible even if the source can be downloaded.

## Required test protocol if a future prompt assigns one lane

1. First verify the exact official product, license, spatial coverage, coordinates/uncertainty and checksum. A link alone is not proof of availability.
2. Reuse the pinned `vendor/gems57` evaluator/writer/cache unchanged. Use pooled **HOLDOUT-DTI** with alpha 0.2, beta 0.8, and the 300 m triangular kernel. Hide whole fault segments with a buffer; derive catalogue features only from visible faults and mask visible faults pixel-exactly.
3. Test each feature alone. AUC above 0.90 is leakage until explained. Name and test a non-fault mimic.
4. Before placement and on final dots, compare against the full available registry. Stop if any comparable raster has absolute rank correlation above 0.90 or more than 70% of candidate dots within 3 px. Do not change density to evade the gate.
5. Record evaluator version, withheld-positive count and 95% interval. A holdout result is **HOLDOUT-DTI**, never a competition score. Only an exact organizer receipt may be labelled **ORGANIZER-CONFIRMED**.
6. Stop at three experiments or two hours. Do not choose a weekly slot; promotion is a separate selector action.

## Manual source review

- Official problem and format: <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/>.
- Official rules PDF: <https://docs.nlr.gov/docs/fy26osti/96647.pdf>.
- Official reference solution: <https://github.com/drivendataorg/gems-prize-reference-solution>.
- INGENIOUS dataset: <https://doi.org/10.15121/1881483>.
- Static leaderboard page (manual link only; do not scrape or poll): <https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/>.

No pages were freshly fetched in this review; the external hosts are outside this execution environment's outbound allowlist. Use the links for manual review, not as evidence that a product or live score was checked.
