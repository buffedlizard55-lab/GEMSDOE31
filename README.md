# GEMSDOE31 — Auditable Fault-Mapping Research, 9-Site Forensic Audit & H31-HVDC Submission

**Live GitHub Pages Site & One-Click Download:** `docs/index.html` and `docs/executive-summary.html` (published via GitHub Pages at `https://buffedlizard55-lab.github.io/GEMSDOE31/`).

---

## Core Values & Standing Project Charter

1. **Maximize `P(Win)`:** Every technical decision is anchored to the exact mathematical objective of the U.S. Department of Energy / DrivenData **Geologic Enhanced Mapping System (GEMS) Prize** (Competition `306`): maximizing the official **Distance-Weighted Tversky Index (`DTI`, `alpha = 0.2`, `beta = 0.8`, linear `300 m` triangular kernel `k(d) = max(1 - d/300 m, 0)`)** on expert-mapped Quaternary/structural faults **absent** from the public USGS/INGENIOUS compilation. We never copy a prior submission, never spend a weekly DrivenData slot without passing strict spatially buffered holdout + duplicate + format gates, and never substitute hand-waving or projections for measured out-of-fold (`OOF`) results.
2. **Own the Outcome:** Every dataset byte, SHA-256 digest, irregularity, negative experiment, and validation check is audited end-to-end, fail-closed in code, and labeled by evidence class (`OFFICIAL`, `OWNER-MIRROR`, `COMPUTED`, `INFERENCE`, `USER-REPORTED`, `TRUSTED-PEER-REVIEWED`). No `Predicted values must be in range [0, 1]` error can slip past `scripts/submission_writer.py` or `src/gemsdoe31/submission.py`.
3. **Parallel-Run Discipline (`H31-HVDC` Single Lane):**
   - **Duplicate Gate (Pre-Placement & Post-Placement):** Checked against all `21` local + sibling focus-site GeoTIFFs (`|Spearman rho| <= 0.90` on score surface AND `<= 70%` 3-px dot overlap).
   - **Shared Spatially Blocked Evaluator (`gemsdoe31-hide-recover-v1`):** `4` spatial quadrants (`row 1851`, `col 1639`) + empirical **`21,250 m` (`21.25 km`, `213 px`)** OOF residual-variogram spatial collar + whole-component exclusion + `20%` whole-component hiding (`screen=[101, 102]`, `confirm=[201, 202]`), pixel-exact visible fault masking, and `1,000`-replicate `20 km x 20 km` cluster-bootstrap 95% CIs.
   - **Single-Feature Leakage Canary:** Every feature (`55 / 55`) tested solo on holdout (`max(AUC, 1-AUC) <= 0.90`) prior to trusting any model fit.
   - **Strict Compute Budget:** `3 / 3` preregistered experiments completed in **`28.96 minutes`** (`<= 3 experiments`, `<= 2 hours`).

---

## Promoted Unique Deliverable & Programmatic Validation Status

- **Programmatic Gate Verdict:** **`PASS — UNIQUE & COMPETITION-VALID GEOTIFF (OK TO DOWNLOAD FOR WEEKLY SLOT SELECTION)`** (`evidence/hvdc/submission_validation_receipt.json`)
- **Primary GeoTIFF (Official `NaN`-Outside Convention):** [`docs/downloads/gemsdoe31-h31-hvdc-submod300-37654-20261025-43714168-nan.tif`](docs/downloads/gemsdoe31-h31-hvdc-submod300-37654-20261025-43714168-nan.tif)
  - **SHA-256:** `2851825a2a33b3a7539aff02131d7a1d59becb5c2e89d1b9a0212652e1e8b1b2` (`185,198` bytes)
  - **Zipped Archive:** [`docs/downloads/gemsdoe31-h31-hvdc-submod300-37654-20261025-43714168-nan.zip`](docs/downloads/gemsdoe31-h31-hvdc-submod300-37654-20261025-43714168-nan.zip) (`995d01e3ab88ba983e126d18846a371063389cfd4fbcd57f60279b4a727a5506`, `134,964` bytes)
  - **All-Finite Portal Fallback (`0.0` Outside):** [`docs/downloads/gemsdoe31-h31-hvdc-submod300-37654-20261025-43714168-allfinite.tif`](docs/downloads/gemsdoe31-h31-hvdc-submod300-37654-20261025-43714168-allfinite.tif) (`1cce914c6daa274ce84cfe215540cdb03bef88f880c952e528807378b826262d`, `141,056` bytes)
- **Unique Submission Name:** `gemsdoe31-h31-hvdc-submod300-37654-20261025-43714168-nan.tif`
- **Portal Note (`115` chars `<= 140`):** `GEMSDOE31 H31-HVDC dual-specialist + vent/relay OOF + 300m CELF submod (37654 {0,1} dots, B>2px; HOLDOUT-DTI 0.1247)`
- **Automated Contract & Uniqueness Verification (`10 / 10` Hard Checks Passed):**
  - `CRS`: `EPSG:32611` (`match = True`), `Shape`: `3730 x 3292` (`match = True`), `Transform`: `(100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)` (`match = True`), `dtype`: `float32`, `bands`: `1`
  - `In-footprint finite`: `5,167,373 / 5,167,373` (`0` NaN, `0` Inf inside footprint; strictly binary `{0.0, 1.0}` within `[0, 1]`)
  - `Outside-footprint NaN`: `7,111,787 / 7,111,787` exact match to `sample_submission.tif`
  - `Emitted dots`: `37,654` (`0` within `<= 200 m` of public catalogue `labels.tif`)
  - `Duplicate canary (`21` registry rasters)`: **PASSED** — max `|Spearman|` = `0.1473` (`0.0626` vs `GEMSDOE32` `H33`; ceiling `0.90`); max `3-px` dot overlap = `0.4888` (`0.3689` vs `GEMSDOE32` `H33`, only `1,232 / 37,654` exact shared pixels; ceiling `0.70`).
  - *Selector Note (Protocol Rule 6):* `slot_approved` in `registry/submissions.json` remains `false` until the cross-lane weekly selector allocates one of the 3 weekly DrivenData upload slots; Run Card `verdict = "promote"` certifies that all 6 local promotion gates passed.

---

## Summary of Findings

### 1. Why `GEMSDOE32` (`h33-h33-2-b2`, `0.2778` `USER-REPORTED`) Scored Highest Across the 9 Focus Sites
Byte-level inspection of all 14 sibling GeoTIFFs (`knowledge/2026-10-25_h31_hvdc_results_and_audit.md`) proved that **every** focus-site submission from `0.2449` to `0.2778` descends from `19GEMSDOE`'s 4-line OOF physical corroboration surface (`H19-5`, `121,131` px, `0.1922` `USER-REPORTED`):
- `GEMSDOE24` (`D1.5`, `60,069` px -> `0.2477` `USER-REPORTED`) and `GEMSDOE25` / `GEMSDOE30` (`D2.8`, `44,090` px, SHA-256-identical -> `0.2600` `USER-REPORTED`) monetized `280 m` sparse binary `{0, 1}` dot spacing so adjacent dots stop paying duplicate `0.2` false-positive weight inside the `300 m` `max` kernel.
- `GEMSDOE28` / `GEMSDOE31` (`H27-4`, `40,199` px -> `0.2708` `USER-REPORTED`) deleted `3,891` dots at `d_cat <= 100 m`.
- **`GEMSDOE32` (`h33-h33-2-b2`, `37,654` px -> `0.2778` `USER-REPORTED`) is bitwise `(D2.8 > 0) & (EDT(~labels) > 2.0)`** — deleting the remaining `2,545` zero-marginal-credit dots in the `100 m < d_cat <= 200 m` catalogue annulus (`6,436` total collar dots removed from `D2.8`, saving `1,287.2` denominator units).
- `GEMSDOE36` (`38,854` px -> `0.2750` `USER-REPORTED`) is `GEMSDOE32` plus `1,200` conduit dots whose marginal efficiency fell below the break-even inclusion threshold $\tau^*(0.2778) = 0.0454\text{ TP}_w/\text{dot}$.

### 2. Ranked Untried Geological Hypotheses (`knowledge/2026-10-25_h31_hvdc_preregistration.md`)
1. **Rank 1 (Implemented & Validated — `PROMOTE`): `H31-HVDC`** — *Hydrothermal-Vent & Dilational Accommodation Conduit Network with Coverage-Deconfounded Dual-Specialist OOF & Exact 300 m CELF Submodular Max-Cover* (`GDR 1391` volcanic vents + 2 m thermal probes + paleo-sinter mounds + magnetite-destruction `rtp` troughs x `K/Th` potassic alteration + `cond_surf` boundaries + fold-visible PCA horsetail tip splays & Voronoi relay bridges).
2. **Rank 2 (Integrated as Full-Footprint Sub-Component): `H31-PCBC`** — *Piedmont Concealment-Belt Curvature & Coverage-Deconfounded Dual-Specialist* (`det_elev` multi-scale DoG + negative Hessian crest curvature over intermediate `det_elev_slope` above buried `depth_to_base_surf`; achieved `#1` zero-shot static feature `ROC-AUC = 0.5922` across `99.94%` of footprint).
3. **Rank 3 (Integrated Subsurface Channel): `H31-BGS`** — *Phase-Aligned Conductive-Basement & Isostatic-Gravity Horizontal-Gradient Step* (`|\nabla depth_to_base_surf| x |iso_grav_anom_hg|` + Kostrov transtensional strain-seismicity coupling).
4. **Rank 4 (Out-of-Sandbox Next Frontier): `H31-3DEP-DIFF`** — *Nonlinear Scarp-Diffusion Profile Residual Bank on Raw 1 m / 10 m USGS 3DEP Bare-Earth DEMs* (`1m_DEM_links.csv` + `USGS_13_*`; blocked in sandbox by network host whitelist, top priority for general-internet CI runner).

### 3. Preregistered 3-Experiment Results (`gemsdoe31-hide-recover-v1`, `21.25 km` Collar, `37,654` Dots)

| Arm | Model & Emitter | Screen `[101, 102]` `HOLDOUT-DTI` (95% CI) | Confirm `[201, 202]` `HOLDOUT-DTI` (95% CI) | Pooled 4-Draw `HOLDOUT-DTI` (95% CI) | `OFFCAT-PROXY-DTI` (`SGMC > 300 m`) | Duplicate Canary |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `EXP-1` | `ArmD-Clean-Poisson` (38 clean sensor bands, no `valid`) | `0.0733` (`[0.0623, 0.0857]`) | `0.0826` (`[0.0682, 0.0994]`) | `0.0779` (`[0.0664, 0.0908]`) | `0.0731` | PASS |
| `EXP-2` | `H31-HVDC-Physics-Poisson` (Dual-Specialist + HVDC physics) | `0.0782` (`[0.0669, 0.0896]`) | `0.0860` (`[0.0730, 0.1004]`) | `0.0821` (`[0.0713, 0.0936]`) | `0.0701` | PASS |
| **`EXP-3`** | **`H31-HVDC-Submod300` (+ fold-visible conduit OOF + 300 m CELF)** | **`0.1202` (`[0.1078, 0.1332]`)** | **`0.1292` (`[0.1141, 0.1448]`)** | **`0.1247` (`[0.1128, 0.1381]`)** | **`0.0824`** | **PASS (`0.4888` max)** |

*(Every holdout score above is `HOLDOUT-DTI` (`COMPUTED`) with mean `12,042` withheld positive pixels per draw across `640` hidden components; `EXP-3` wins `4 / 4` draws and all `4 / 4` spatial quadrants `NW, NE, SW, SE`.)*

---

## Audited Official & Mirror Sources (`registry/sources.json`)

| Source | Class | Official / Canonical Link | Verified Role |
| --- | --- | --- | --- |
| DrivenData GEMS Problem & Metric Spec | `OFFICIAL` | <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/> | Official DTI formula (`alpha=0.2, beta=0.8, R=300 m`), EPSG:32611 100 m GeoTIFF `[0, 1]` contract |
| DOE / NLR Official Rules (FY26 OSTI 96647) | `OFFICIAL` | <https://docs.nlr.gov/docs/fy26osti/96647.pdf> | 3 submissions/week cap, single-band 100 m GeoTIFF rule, AI-disclosure mandate |
| DrivenData GEMS Reference Solution | `OFFICIAL` | <https://github.com/drivendataorg/gems-prize-reference-solution> | Prof. John Lipor Monte Carlo U-Net CV benchmark (`aebe92f7c8a9`) |
| DrivenData Terms of Use | `OFFICIAL` | <https://www.drivendata.org/termsofuse/> | Prohibits automated scraping/polling; enforced strictly |
| USGS / GDR 1501 GeoDAWN LiDAR | `OFFICIAL` | <https://gdr.openei.org/submissions/1501> | CC-BY-4.0 EarthMRI LiDAR coverage (`75.37%` of GEMS footprint) |
| USGS ScienceBase GeoDAWN Rad/Mag | `OFFICIAL` | <https://www.sciencebase.gov/catalog/item/657e1d85d34e23d3533209f7> | Public-domain airborne `K, Th, U, TC, ThK, UK, UTh, TMI_up150` grids (`DOI:10.5066/P93LGLVQ`) |
| DOE GDR 1391 INGENIOUS Great Basin | `OFFICIAL` | <https://gdr.openei.org/submissions/1391> | CC-BY-4.0 Quaternary volcanic vents, 2 m thermal probes, paleo-sinter mounds |
| USGS SGMC State Geologic Map Compilation | `OFFICIAL` | <https://mrdata.usgs.gov/geology/state/> | Public-domain bedrock fault lines used strictly as zero-training-leakage `OFFCAT-PROXY-DTI` (`61,664` cells `>300 m` from catalogue) |
| Sibling GEMSDOE Focus Repositories | `OWNER-MIRROR` | <https://github.com/buffedlizard55-lab/GEMSDOE32> | Hash-verified audit of `19GEMSDOE` & `GEMSDOE24/25/27/28/30/32/33/36/70` |

---

## Reproducing Everything from Scratch

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/download_competition_data.py --data-dir /tmp/gems_data
.venv/bin/python scripts/prepare_data.py --data-dir /tmp/gems_data --out-dir /tmp/gems_data/prepared
.venv/bin/python scripts/check_metric.py
.venv/bin/python scripts/run_arms.py --data-dir /tmp/gems_data --prepared-dir /tmp/gems_data/prepared --cache-dir /tmp/gems_data/hvdc_cache
.venv/bin/python scripts/evaluate_holdout.py docs/downloads/gemsdoe31-h31-hvdc-submod300-37654-20261025-43714168-nan.tif --data-dir /tmp/gems_data
.venv/bin/python scripts/build_site.py && .venv/bin/python scripts/check_site.py
.venv/bin/python -m pytest -q && .venv/bin/python -m ruff check .
```
