# GEMSDOE31 Complete Forensic Autopsy, Ranked Hypotheses, and H31-HVDC Validation Report (2026-10-25)

## 1. Byte-Level Autopsy of All 9 Focus GEMSDOE Sites: Why GEMSDOE32 (`0.2778`) Won

Every champion GeoTIFF across `19GEMSDOE` and the nine focus sites (`GEMSDOE24`, `25`, `27`, `28`, `30`, `31`, `32`, `33`, `36`) was retrieved read-only via GitHub API, SHA-256-verified, and inspected pixel-by-pixel against `sample_submission.tif` (`5,167,373` in-footprint cells) and `labels.tif` (`60,988` public USGS/INGENIOUS catalogue fault cells). All prompt-quoted live leaderboard scores lack organizer portal receipts in the repository and are therefore strictly labeled **`USER-REPORTED`**.

| Site | Champion Raster | SHA-256 Prefix | Emitted Dots | Dots in `d_cat <= 200 m` | Outside Policy | Exact Relationship to Lineage | Score (`USER-REPORTED`) |
| --- | --- | --- | ---: | ---: | --- | --- | ---: |
| `19GEMSDOE` | `gems19-h19-5-corroboration-...` | `6e45e662b403` | `121,131` | `17,326` | `NaN` | Root 4-line OOF physical corroboration field | `0.1922` |
| `GEMSDOE24` | `gemsdoe24-d1.5-20261003T201124Z.tif` | `6bf8dc35ca2b` | `60,069` | `8,769` | `NaN` | `1.5 px` Poisson-disk thinning of `H19-5` | `0.2477` |
| `GEMSDOE27` | `topo-gap-closure-on-d1.5-...` | `54d0c597a723` | `61,328` | `8,875` | `NaN` | `D1.5` + `1,259` LiDAR gap-closure dots (`-0.0028` dilution) | `0.2449` |
| `GEMSDOE25` | `gemsdoe25-d2.8-20261003T212915Z.tif` | `53fa6455d172` | `44,090` | `6,436` | `NaN` | `2.8 px` (`280 m`) Poisson-disk thinning of `H19-5` | `0.2600` |
| `GEMSDOE30` | `gemsdoe30-d28-20261003T212915Z.tif` | `53fa6455d172` | `44,090` | `6,436` | `NaN` | **Bit-for-bit identical** to `GEMSDOE25` `D2.8` | `0.2600` |
| `GEMSDOE33` | `gemsdoe33-h33d-analog-...-zeros.tif` | `9a7d6d47ab62` | `41,865` | `3,894` | `0.0` | Partial collar + tip-analog re-thinning | `0.2632` |
| `GEMSDOE28` / `31` | `h27-4-r1-solo-d2-8-...` | `aa84b1bc0e05` | `40,199` | `2,545` | `NaN` | `(D2.8 > 0) & (EDT(~labels) > 1.0)` (`-3,891` dots at `<=100 m`) | `0.2708` |
| `GEMSDOE28` | `h36-1-s1-best-corrob-...` | `be2d9ec03198` | `37,660` | `2,353` | `NaN` | Pruned `2,539` lowest-corroboration dots (kept `100-200 m` ring) | `0.2710` |
| **`GEMSDOE32`** | `h33-h33-2-b2-...-zeros.tif` | `8781bf73df64` | **`37,654`** | **`0`** | `0.0` | **`(D2.8 > 0) & (EDT(~labels) > 2.0)` (`37,654/37,654` subset of `D2.8`)** | **`0.2778`** |
| `GEMSDOE36` | `gemsdoe36-anderson-geothermal-pinn-38854-...` | `3bb1c7b9d6c0` | `38,854` | `0` | `0.0` | `GEMSDOE32` (`37,654`) + `1,200` conduit dots (`-0.0028` dilution) | `0.2750` |

### Exact Three-Part Mechanism Behind `0.2778`
1. **Metric-Matched Sparse Binary Emission (`19GEMSDOE -> GEMSDOE25`: `0.1922 -> 0.2600`):** Under the official Distance-Weighted Tversky Index ($\alpha = 0.2$, $\beta = 0.8$, $k(d) = \max(1 - d/300\text{ m}, 0)$), `TPw` uses a **$\max$ operator** across all predicted pixels within `300 m`, while `FPw` sums $0.2\,p(x)\,[1 - \max_g k(d(x,g))]$ **additively** over every non-zero pixel. Thinning dense patches (`121,131 px`) to `280 m` (`2.8 px`) binary `{0, 1}` dots (`44,090 px`) removed `77,041` redundant denominator-penalized pixels (`-15,408` in $\alpha\,\text{FP}_w$) while retaining almost the entire `300 m` coverage envelope.
2. **Exact `B=2` (`200 m`) Catalogue Collar Deletion (`GEMSDOE25 -> GEMSDOE28 -> GEMSDOE32`: `0.2600 -> 0.2708 -> 0.2778`):** Because the organizer's hidden evaluation set $G_{\text{hidden}}$ consists of expert-mapped faults **absent** from `labels.tif`, dots placed at `d_cat <= 100 m` (`3,891` dots removed in `GEMSDOE28`, `+0.0108`) and in the `100 m < d_cat <= 200 m` annulus (`2,545` additional dots removed in `GEMSDOE32`, `+0.0070`) earn near-zero marginal `TPw` on unmapped segments (any branch intersecting a mapped fault is already covered from `d_cat = 224-300 m`) while paying the full `0.2` false-positive weight (`6,436 * 0.2 = 1,287.2` denominator units saved). Notably, `GEMSDOE32` (`37,654` dots, `0.2778`) beat `GEMSDOE28` `h36-1` (`37,660` dots, `0.2710`) at **virtually identical dot count (`6` dots apart)** solely because removing the `100-200 m` catalogue collar (`2,545` zero-return dots) is strictly superior to pruning off-catalogue dots (`2,539` real-return dots).
3. **Why `GEMSDOE36` (`0.2750`) Regressed by `-0.0028`:** Differentiating $\text{DTI}$ with respect to adding $\Delta N$ dots shows a new dot improves `DTI` if and only if its expected marginal kernel credit satisfies $\Delta\text{TP}_w / \Delta N > \tau^*(D) = \frac{0.2\,D}{1 + 0.8\,D}$ (`0.0454` at `D = 0.2778`; `0.0588` at `D = 0.368`). `GEMSDOE36`'s `1,200` appended dots yielded ~`0.025 TPw/dot < 0.0454`, diluting the denominator.

### How to Beat `0.2778`, `0.3195`, and Approach `0.4413`
Collar pruning on the `H19-5` surface is mathematically saturated at `B = 2` (`37,654` dots), and any subset/superset of `D2.8`/`H33` triggers the `>70%` 3-px overlap duplicate gate. Surpassing `0.2778 -> 0.3195 -> 0.4413` requires three orthogonal advances:
1. **Deconfounding the `24.63%` LiDAR Survey Gap & Removing the Leaked `valid` Feature:** Historical `GEMSDOE31` `Arm B`/`Arm D` passed the binary 3DEP survey mask (`valid`) directly to the classifier, depressing off-catalogue generalization (`Arm D DTI_ff = 0.0512` vs `Arm C = 0.0629`). Splitting inference into a `100%`-coverage full-footprint geophysical specialist + a coverage-normalized multi-sensor specialist eliminates survey-boundary artifacts across the `1,272,913` non-LiDAR footprint cells.
2. **Coupling Hydrothermal Upflow Physics (`GDR 1391` + Magnetite Destruction + `K/Th` Alteration) with Structural Accommodation (`Tip Splays + Voronoi Relay Bridges`):** Over `75%` of Great Basin geothermal systems sit on unmapped fault terminations, step-overs, and range-front intersections (Faulds et al., 2006, 2011) where ascending fluids destroy magnetite (`rtp` troughs) and enrich potassium (`K/Th`) even under alluvial cover.
3. **Bayes Prior-Shift Calibration + Exact `300 m` CELF Submodular Max-Cover:** Replacing ad-hoc `2.8 px` isotropic Poisson-disk thinning with King & Zeng (2001) prior-calibrated probabilities and exact `29`-offset `300 m` triangular-kernel lazy-greedy submodular optimization (`allocate_submodular_dots`) directly maximizes $\mathbb{E}[\text{TP}_w(S)]$ per `0.2` denominator cost.

---

## 2. Experimental Validation Results (`EXP-1`, `EXP-2`, `EXP-3`)

All 3 preregistered experiments (`knowledge/2026-10-25_h31_hvdc_preregistration.md`) completed in **`28.96 minutes`** (budget `<= 120 minutes`, `3 / 3` experiments) under `gemsdoe31-hide-recover-v1` (`21,250 m` empirical semivariogram collar, whole-component exclusion, pixel-exact visible fault masking, `37,654` binary `{0.0, 1.0}` dots outside `d_vis <= 2.0 px`, `1,000`-replicate `20 km x 20 km` spatial-tile cluster-bootstrap 95% CIs).

### Single-Feature Leakage Canary (`evidence/hvdc/leakage_canary.json`)
- **Status:** **PASSED** (`55 / 55` features cleanly `<= 0.90`; `0` flagged features).
- Highest static full-footprint feature: `hvdc_piedmont_belt_curv` (`ROC-AUC = 0.5922`, `99.94%` finite coverage — #1 of all 52 static features, ahead of every raw competition and LiDAR band).
- Fold-visible structural-hydrothermal accommodation features (strictly computed from `draw.visible`, evaluated on `draw.hidden` at `d_vis > 2.0 px`):
  - `vis_vent_tip_bridge`: **`ROC-AUC = 0.7606`**
  - `vis_relay_bridge`: **`ROC-AUC = 0.7413`**
  - `vis_tip_horsetail_lobe`: **`ROC-AUC = 0.6407`**

### Blocked Hide-and-Recover `HOLDOUT-DTI` Summary (`evidence/hvdc/hvdc_experiment_results.json`)

| Experiment | Screen `[101, 102]` `HOLDOUT-DTI` (95% CI) | Untuned Confirm `[201, 202]` `HOLDOUT-DTI` (95% CI) | Pooled 4-Draw `HOLDOUT-DTI` (95% CI) | Delta vs `EXP-1` (Pooled) | Live OOF `OFFCAT-PROXY-DTI` (`SGMC > 300 m`) | Duplicate Canary (`21` Rasters) |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `EXP-1` (`ArmD-Clean-Poisson`) | `0.0733` (`[0.0623, 0.0857]`) | `0.0826` (`[0.0682, 0.0994]`) | `0.0779` (`[0.0664, 0.0908]`) | `0.0000` | `0.0731` | PASS (`0.5562`) |
| `EXP-2` (`H31-HVDC-Physics-Poisson`) | `0.0782` (`[0.0669, 0.0896]`) | `0.0860` (`[0.0730, 0.1004]`) | `0.0821` (`[0.0713, 0.0936]`) | `+0.0042` (`4/4` draws) | `0.0701` | PASS (`0.5053`) |
| **`EXP-3` (`H31-HVDC-Submod300`)** | **`0.1202` (`[0.1078, 0.1332]`)** | **`0.1292` (`[0.1141, 0.1448]`)** | **`0.1247` (`[0.1128, 0.1381]`)** | **`+0.0468` (`+60.0%`, `4/4` draws)** | **`0.0824`** | **PASS (`0.4888`; `0.3689` vs `GEMSDOE32`)** |

### Per-Quadrant Spatial Consistency (`EXP-3` vs `EXP-1`, Mean Across Draws `[101, 102, 201, 202]`)
- **Q0 (NW):** `0.1202` vs `0.0607` (**`+0.0595`**, won `4/4` draws)
- **Q1 (NE):** `0.0870` vs `0.0696` (**`+0.0174`**, won mean & `2/2` confirm draws)
- **Q2 (SW):** `0.1595` vs `0.1151` (**`+0.0445`**, won `4/4` draws)
- **Q3 (SE):** `0.1419` vs `0.1023` (**`+0.0396`**, won `4/4` draws)

---

## 3. Limitations & Remaining High-Leverage Next Steps (Out-of-Sandbox)
1. **No Live DrivenData Receipt Yet:** All `HOLDOUT-DTI` figures are local blocked hide-and-recover measurements (`COMPUTED`), and all sibling scores (`0.2449-0.2778`, `0.3195`, `0.4413`) are `USER-REPORTED`. Weekly live slot allocation remains governed by the cross-lane selector (`slot_approved = false` in `registry/submissions.json`).
2. **1 m 3DEP Bare-Earth Scarp Diffusion (`H31-3DEP-DIFF`) & GDR 1391 3-D MT Resistivity Cubes:** Outbound access in this sandbox is restricted to GitHub/PyPI/npm, so raw USGS S3 1 m DEM tiles (`1m_DEM_links.csv`) and multi-depth MT resistivity slices (`gdr.openei.org/submissions/1391`) could not be fetched here. In a general-internet CI runner, adding nonlinear Hanks (2000) scarp-diffusion profile residuals over the `75.37%` LiDAR footprint + 10 m 3DEP (`USGS_13_*`) over the remaining `24.63%` gap is the single highest-ceiling next step toward `0.32-0.44`.
3. **Orthogonal Cross-Family Ensembling in the Selector:** Because `EXP-3` (`gemsdoe31-h31-hvdc-submod300-37654-20261025-43714168-nan.tif`) shares only `36.89%` 3-px dot overlap (`1,232 / 37,654` exact pixels, Spearman `0.0626`) with `GEMSDOE32` `H33`, `63.1%` of its predictions target genuinely distinct hydrothermal/relay/piedmont fault segments.
