# Preregistration: Lane H31-J (`TGTD-Submod`) — Tabular Gravity-Tensor Dimensionality, Advective Geothermometer Disequilibrium, and Piedmont-Toe Flexure OOF Submodular Allocation

- **Date (UTC):** `2026-10-25`
- **Branch:** `arena/6fef25ef-gemsdoe31` (branched from `main` at `ecdf391d955e1ae199e12f9537026b65aa5ddb7e`)
- **Status:** Frozen **before** model training, holdout evaluation, or candidate raster emission
- **Method lane:** Single lane only — **`H31-J · TGTD-Submod`**
- **Experiment budget:** Strictly `<= 3` frozen model/allocation variants (`H31-J1`, `H31-J2`, `H31-J3`), `<= 2` hours total compute, `0` live DrivenData submission slots consumed (`slot_approved = false`)

---

## 1. Forensic Diagnosis Motivating `H31-J` (Why `0.2778` Won in Focus Siblings & Why `H31-E2` / `MAGREST` Fell Short)

1. **Exact lineage of `GEMSDOE32` `0.2778` (`USER-REPORTED`):**
   - `19GEMSDOE` `H19-5` continuous 4-line potential-field + topographic ridge (`121,131` px, `0.1922` `USER-REPORTED`)
   - $\rightarrow$ `GEMSDOE31` `D2.8` greedy `d >= 2.8 px` sparse dot thinning (`44,090` dots, `0.2600` `USER-REPORTED`, `+0.0678` from eliminating redundant 29-cell 300-m triangular kernel self-overlap)
   - $\rightarrow$ `GEMSDOE27` `H27-4` `1 px` (`100 m`) known-fault exclusion collar (`40,199` dots, `0.2708` `USER-REPORTED`)
   - $\rightarrow$ `GEMSDOE32` `H33-2-B2` (`h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros`, `37,654` dots, `0.2778` `USER-REPORTED`, `+0.0070` from widening the dead-zone collar to `d_vis > 2.0 px` = `200 m` and preserving **`58.4%` (`21,989` dots) in the far field `> 1.5 km`** from `labels.tif`).
2. **Why `H31-E2` (`SCGP-Submod`) failed its far-field proxy gate (`G5b` All-Elevation `SGMC > 300 m`: `0.0816 < 0.0940`):**
   - `H31-E2` injected four visible-catalogue geometry features (`vis_d1`, `vis_tip_2k`, `vis_relay_4k`, `vis_belt_annulus`) directly into its `HistGradientBoostingClassifier` and emitted its submission from a **full-catalogue in-sample refit** rather than stitched spatial OOF predictions.
   - Because severed holdout traces sit close to remaining visible strands under `r_min <= 21.3 km` splits, trees heavily weighted `vis_d1` (`68.5%` of emitted dots crowded within `<= 1.5 km` of `labels.tif`, leaving only `31.5%` beyond `1.5 km`). Sibling live natural experiments (`GEMSDOE76` `0.2343 -> 0.1555` `USER-REPORTED` when catalogue-tip continuation was added; `GEMSDOE91` `0.1823` `USER-REPORTED`) confirm that hidden test faults lie in genuinely unmapped basins and range fronts rather than `<= 1.5 km` splays of `labels.tif`.
3. **Why `MAGREST` (`0.0530` on `gems57-pooled-hide-v2` `seed=31`) failed its screen gate:**
   - Unsupervised potential-field ridge hand-crafting alone could not separate true tectonic fault offsets from circular volcanic/intrusive anomalies (`paired delta +0.0047`, `95% CI [-0.0155, +0.0241]` crossing zero vs `physical_hgb = 0.0483`), and `physical_hgb` suffered from unstandardized regional level drift across quadrants plus raw LiDAR coverage-boundary effects.
4. **Irregularities verified before coding (zero hallucinations):**
   - **Owner prompt lane-letter omission:** The owner prompt's candidate lane menu lists `Lane A, B, C, D, E, G, H, I` (`Lane F` was omitted in the prompt numbering). Disclosed explicitly.
   - **`training_features.tif` band header mislabeling (`IR-B06`, `IR-B10`, `IR-B18`):**
     - `B06` (`tc`) is labeled *"Tilt angle or total curvature - magnetic field derivative"* in the TIFF metadata, but direct pixel correlation against `geodawn_rad_u8.tif` band 4 (`TC`) is `r = 0.99714` (`range [2.95, 88.57]`): `B06` is **radiometric Total Count**, not magnetic tilt angle! `H31-J` computes true magnetic Miller–Singh tilt angle $\arctan2(\text{RTP}_z, \text{RTP}_H)$ directly from upward-continued `B02` (`rtp`).
     - `B10` (`deq_n100a15`) is labeled *"Distance to earthquake"*, but takes values in `[0, 4.96e6]` (median `623`): it is **declustered earthquake density**, not distance.
     - `B18` (`iso_grav_anom_hg`) takes signed values in `[-15.4, +12.9]`, whereas `B05` (`iso_grav_anom_slope`, `[0.00138, 0.652]`) is the positive horizontal gradient magnitude.
   - **External CSV leakage column (`IR-WELLSPRING-COL`):** `data/external/gdr_wellspring_in_footprint.csv` contains a precomputed column `dist_known_fault_px` measured against full `labels.tif`. `H31-J` **strictly excludes `dist_known_fault_px` at CSV read time** (`usecols = ["row", "col", "temp_c", "geothermquartz_c", "geothermchalc_c", "geothermcat_c"]`) and enforces a unit-test ban against loading that column.

---

## 2. Five Ranked Untried Candidate Geological Hypotheses (Evaluated Before Coding)

| Rank | Candidate Hypothesis | Physical Layers Used | Blind/Unmapped Fault Signature & Non-Fault Mimic Suppressed | Novelty vs `GEMSDOE31` & Focus Fleet | Expected `HOLDOUT-DTI` Gain vs `physical_hgb` (`0.0483`) | Compute Cost | Verified Open Data Availability |
|---|---|---|---|---|---|---|---|
| **1 (SELECTED: `H31-J`)** | **Tabular Gravity-Tensor Dimensionality (`TGTD`) + Advective Geothermometer Upflow Disequilibrium (`GDR-1391`) + Piedmont-Toe Concave Flexure (`PTCF`), Dual-Regime Stitched OOF + 300 m Ridge-Submodular** | Pinned 19-band `vendor/gems57` cache (`B01..B19`), GDR #1391 `gdr_wellspring_in_footprint.csv` (`temp_c`, `geothermquartz_c`, `geothermchalc_c`, `geothermcat_c` ONLY), `geodawn_rad_u8.tif`, `geodawn_extensions_u8.tif`, `derived_gdr_2m_probes_100m_u8.tif`, `derived_gdr_volcanics_100m_u8.tif`, interior-feathered `lidar_scarp_features_u8.tif` | **(a)** Pedersen–Rasmussen (1990) / Beiki (2010) 3-D Laplace gravity/magnetic gradient tensor invariant $\mathcal{T}_{2\text{D}} = 1 - \lvert -3\sqrt{6}\det(\mathbf{T}_G)/\|\mathbf{T}_G\|_F^3\rvert \to 1$ isolates elongated 2-D basement fault steps while suppressing **circular 3-D calderas/plutons** ($\mathcal{T}_{2\text{D}} \to 0$). **(b)** Fournier (1977) silica/Na-K-Ca disequilibrium $\Delta T_{\text{diseq}} = T_{\text{geotherm}} - T_{\text{outlet}}$ channeled strictly onto 1-D tabular gravity steps & smectite/K-metasomatic corridors catches blind amagmatic upflow conduits (e.g., Beowawe `6.2 km` off-catalogue, Alkali `6.9 km` off-catalogue) while suppressing **shallow lateral outflow plumes**. **(c)** Piedmont-toe concave flexure + one-sided relief asymmetry + Hurst roughness break catches washed-out Holocene fan-toe faults while suppressing **symmetric V-shaped mountain canyons**. | **100% untried in `GEMSDOE31`**: `gdr_wellspring_in_footprint.csv`, Pedersen–Rasmussen $\det(\mathbf{T}_G)$ dimensionality invariant, `PTCF` + V-canyon suppressor + Hurst jump, `60 km` seam-free regional standardization, and zero-catalogue dual-regime stitched OOF submodular emission have never been run in `GEMSDOE31` (`H31-A`, `TGJ31`, `AS-1`, `H31-B`, `H31-E`, `MAGREST`, `H31-E2`). | `+0.030` to `+0.065` `HOLDOUT-DTI` on `gems57-pooled-hide-v2` (`seed=31` & `seed=32`), plus positive gains on both All-Elevation and Piedmont `SGMC > 300 m` off-catalogue proxies | Low (`~10 min` CPU for all 3 frozen experiments) | **VERIFIED** locally & hash-pinned (`training_features.tif` + 19 cached bands + `gdr_wellspring_in_footprint.csv` `sha256: 122718e6...`, CC-BY-4.0 DOE GDR #1391, DOI `10.15121/1881483`) |
| **2 (Deferred)** | **Anisotropic Geophysical-Strike Riemannian Eikonal Relay Bridge (`Eikonal-Geodesic`)** | `B05` (`iso_grav_anom_slope`), `B07` (`geod_shearrate`), `B17` (`cond_surf`), `lidar_scarp_features_u8.tif` (`strike`, `coh100`) | Label-free anisotropic Fast-Marching geodesics aligned with gravity/LiDAR strike connect en-echelon fault stepovers across Holocene fan lobes while penalizing cross-strike excursion. | Untried (`H31-B` ran isotropic Dijkstra between *known catalogue tips*, leaking `labels.tif`). | `+0.015` to `+0.030` | Moderate (`~35 min` PDE solve) | **VERIFIED** in `registry/data_manifest.json` |
| **3 (Deferred)** | **Multi-Continuation 3-D Euler Deconvolution Contact-Index (`N=0`) vs Basement Depth (`Euler-SI0`)** | `B13` (`iso_grav_anom`), `B02` (`rtp`), `B15` (`depth_to_base_surf`) | Reid et al. (1990) structural-index $N=0$ contact solutions whose inferred Euler depth $z_0$ matches `depth_to_base_surf` (`B15`) isolate intrabasinal basement-offsetting faults beneath deep valley fill. | Untried in `GEMSDOE31` (Menu Lane C). | `+0.010` to `+0.025` | Moderate (`~20 min` windowed SVD) | **VERIFIED** in `registry/data_manifest.json` |
| **4 (Deferred standalone; core invariant folded into Block 5 of `H31-J`)** | **Kostrov Transtensional Strain-Style × Declustered Microseismic Moment Partitioning (`Kostrov-Seismo`)** | `B04` (`geod_2ndinv`), `B07` (`geod_shearrate`), `B08` (`geod_dilaterate`), `B10` (`deq_n100a15`), `B16` (`ieq_n100a15`), `B15` (`depth_to_base_surf`) | Oblique Walker Lane / CNSB transfer zones exhibit coupled high shear × positive dilatation and elevated declustered seismicity along steep sediment-thickness margins despite subdued range-front scarps. | Untried as a dedicated lane in `GEMSDOE31`. | `+0.005` to `+0.015` standalone (`25–50 km` GPS wavelength requires fine structural localization) | Low (`~5 min`) | **VERIFIED** in `registry/data_manifest.json` |
| **5 (Deferred standalone; sparse auxiliary folded into Block 3 of `H31-J`)** | **Shallow 2-m Temperature Probe + Syn-Extensional Volcanic Vent Dike Alignment (`ShallowThermal-Vent`)** | `derived_gdr_2m_probes_100m_u8.tif`, `derived_gdr_volcanics_100m_u8.tif`, `B02` (`rtp`), `B17` (`cond_surf`) | Shallow 2 m thermal anomalies (Kratt/Coolbaugh surveys) and Quaternary/Neogene vent alignments trace blind dilational conduits in Carson Sink / Humboldt structural zone. | Untried in `GEMSDOE31` (`78 KB` raster never modeled). | `+0.003` to `+0.010` standalone (`< 1%` areal probe coverage) | Low (`~4 min`) | **VERIFIED** in `registry/data_manifest.json` |

---

## 3. Frozen Mathematical & Engineering Specification of `H31-J`

### 3.1 Strict Anti-Leakage Architecture
1. **Zero catalogue-proximity features in model training or inference:** No distance-to-catalogue, tip-density, relay-corridor, or belt-annulus feature derived from `labels.tif` (neither full nor fold-visible) is ever computed or passed to any classifier. Every feature in `src/gemsdoe31/tgtd_features.py` is 100% label-free!
2. **Banned inputs:**
   - `derived_gdr_qfaults_v2_100m_u8.tif` (`99.95%` duplicate of `labels.tif`) — banned and asserted unread.
   - `derived_sgmc_faults_100m_u8.tif` — report-only off-catalogue evaluation proxy, never imported or read by feature engineering, model training, calibration, or emission.
   - `derived_gdr_paleo_100m_u8.tif` — excluded from features because paleoseismic trenches are human excavations sited on mapped Quaternary scarps.
   - `dist_known_fault_px` column in `gdr_wellspring_in_footprint.csv` — dropped at CSV parser column-selection level (`usecols`) and asserted absent.
3. **Single-feature + missingness leakage canary (`Rule 4`):**
   - Before trusting any model score, every feature column $j$ (and its non-finite indicator) is evaluated **alone** on the pinned `gems57-pooled-hide-v2` holdout (`seed=31`, `buffer_px=213`).
   - Hard gate: $\max(\text{AUC}_j, 1 - \text{AUC}_j) \le 0.90$ and missingness $\text{AUC}_j \le 0.90$. Any violation triggers an immediate `STOP`.

### 3.2 Physics Feature Stack (`src/gemsdoe31/tgtd_features.py`)
- **Pinned Base Bands (19 features):** Unchanged `.cache/features/band-01.npy .. band-19.npy` built by `vendor/gems57/prepare_data.py::cache_bands` (`all 19 SHA-256 hashes verified against registry/template_pins.json`).
- **Regional Background De-Trending (`60 km` = `600 px` smooth label-free local standardization):** Removes regional Basin-and-Range baseline level shifts across NW/NE/SW/SE quadrants (`det_elev`, `iso_grav_anom`, `rtp`, `depth_to_base_surf`, `cond_surf`, `geod_*`) with $C^\infty$ spatial continuity (zero quadrant-boundary seams).
- **Block 1 — 3-D Laplace Spectral Gravity Gradient Tensor & Tabular Dimensionality (`TGTD`):**
  - Exact 2-D FFT upward continuation ($z_1 = 300\text{ m}$, $z_2 = 1000\text{ m}$) + 3-D harmonic tensor $\mathbf{T}_G = [g_{\alpha\beta}]$ on tapered/inpainted `B13` (`iso_grav_anom`).
  - Pedersen–Rasmussen / Beiki 2-D tabular index $\mathcal{T}_{2\text{D}}^G(z) = 1 - \lvert -3\sqrt{6}\det(\mathbf{T}_G)/(\|\mathbf{T}_G\|_F^3 + \epsilon)\rvert$ (where $3\sqrt{6} = \sqrt{54}$ is the exact sharp upper-bound normalizer for trace-free symmetric $3\times 3$ harmonic tensors with axisymmetric 3-D spectrum $(-1, -1, 2)$), gravity Miller–Singh tilt $\theta_G(z) = \arctan2(g_z, g_H)$, tabular tilt-zero crest score $\mathcal{S}_{\text{TGTD}}(z) = \mathcal{T}_{2\text{D}}^G(z) g_H(z) e^{-(\theta_G(z)/0.35)^2}$, multi-scale worm persistence $\sqrt{\mathcal{S}_{\text{TGTD}}(300\text{m}) \mathcal{S}_{\text{TGTD}}(1000\text{m})}$, and horizontal curvature ridge $-g_{nn}(300\text{m})$.
- **Block 2 — Spectral RTP Magnetic Tensor & Hydrothermal Demagnetization:**
  - True magnetic Miller–Singh tilt $\theta_{\text{RTP}}(300\text{m})$ from upward-continued `B02` (`rtp`), magnetic 2-D tabular index $\mathcal{T}_{2\text{D}}^{\text{mag}}(300\text{m})$, upward-continued vertical second derivative $\text{RTP}_{zz}(300\text{m})$, hydrothermal magnetite-destruction index $\max(-\text{RTP}_{zz}, 0) \cdot \text{cond\_surf}$, and gravity–magnetic strike co-alignment $\cos^2(\phi_G - \phi_{\text{RTP}}) \cdot \mathcal{T}_{2\text{D}}^G \cdot \mathcal{T}_{2\text{D}}^{\text{mag}}$.
- **Block 3 — Channeled Geothermometer Upflow Disequilibrium (`GDR-1391`):**
  - Per-cell max chemical disequilibrium $\Delta T_{\text{diseq}} = \max(\max(T_{\text{quartz}}, T_{\text{chalc}}, T_{\text{Na-K-Ca}}) - \max(T_{\text{outlet}}, 15^\circ\text{C}), 0)$ and outlet thermal excess $\Delta T_{\text{outlet}} = \max(T_{\text{outlet}} - 20^\circ\text{C}, 0)$.
  - Multi-scale Gaussian advective potentials ($\sigma = 1.5\text{ km}, 4.5\text{ km}$) **multiplied by 1-D structural conduit gates** ($\mathcal{S}_{\text{TGTD}}(300\text{m})$ and $\text{cond\_surf} \cdot \text{K/Th}$) plus shallow 2 m probe / Quaternary-Neogene vent structural alignment, preventing circular IDW thermal halos.
- **Block 4 — Piedmont-Toe Concave Flexure (`PTCF`) + One-Sided Relief Asymmetry + Hurst Break:**
  - Concave-upward toe flexure $\max(\nabla^2_\sigma z_{\text{det}}, 0)$ ($\sigma = 300\text{ m}, 800\text{ m}, 1600\text{ m}$), cross-strike one-sided relief step $|z_+ - z_-| / (|z_+ - z_0| + |z_- - z_0| + 1)$ (suppressing symmetric V-shaped mountain canyons), multi-scale topographic Hurst exponent gradient $|\nabla H_{\text{topo}}|$, and basement-cover thickness gradient $|\nabla G_{300\text{m}}(\text{B15})|$.
- **Block 5 — Crustal Transtension & GeoDAWN Radiometric Alteration:**
  - Kostrov transtensional strain ratio $\text{B07}\cdot\max(\text{B08}, 0)/(\text{B04}^2 + 1)$, seismic clustering contrast $\log(1 + \text{B10}) - \log(1 + \text{B16})$, potassium metasomatism `K / (Th + 1)`, uranium redox mobilization `U / (Th + 1)`, and aeromagnetic `TMI_up150` gradient.
- **Block 6 — Seam-Free Interior-Feathered 1 m 3DEP LiDAR Scarp Polarity (Specialist B only):**
  - `upface_minus_downface` polarity, `step_max / (relief + 5)` normalized fault step, `coh100` scarp linearity, `lapneg_max`, and LiDAR–gravity strike alignment $\cos^2(\phi_{\text{lidar}} - \phi_G)$, blended ONLY inside the `1.5 km`-eroded interior of valid 3DEP coverage with smooth cosine feathering $w_{\text{lidar}}(\mathbf{x}) \in [0, 0.40]$ after rank-matching Specialist B to Specialist A inside the LiDAR interior.

### 3.3 Exact 3 Frozen Experiments (`<= 3` Budget Lock)

All three variants are evaluated on the **unchanged `vendor/gems57` holdout evaluator** (`gems57-pooled-hide-v2`, `buffered_component_draw` with `hide_frac=0.20`, `buffer_px=213` = `21.3 km`, `boundary_px=213`, `1,000`-draw `20 km` physical-block paired bootstrap, `alpha=0.2, beta=0.8, 300 m` triangular kernel) at matched operating density $\rho_0 = 37,654 / N_{\text{allowed}}$ (`37,654` final dots on full submission, matching `GEMSDOE32` `0.2778` and `MAGREST` / `H31-E2` dot budget for exact apples-to-apples comparison) and `d_vis > 2.0 px` (`200 m`) visible-catalogue dead-collar exclusion:

1. **Experiment 1 (`H31-J1 · Subsurface-TGTD-Geotherm-OOF`):**
   - Pure subsurface + radiometric/crustal specialist (`Blocks 1–3 + non-topographic B01..B11, B13..B18 + Block 5`, **zero LiDAR, zero `det_elev`/`det_elev_slope`**) + 300 m ridge-submodular allocator (`gamma=2.0`, `min_dist_px=2.4`). Tests pure blind subsurface + geothermometer skill without any topographic scarp cue.
2. **Experiment 2 (`H31-J2 · TGTD-Geotherm-PTCF-DualOOF-Poisson`):**
   - Full `H31-J` Dual-Regime stitched 4-quadrant OOF probability surface (Specialist A Full-Footprint `Blocks 1–5` + interior-feathered Specialist B `Blocks 1–6`) + standard greedy Poisson-disk thinning (`min_dist_px=2.8`, `d_vis > 2.0 px`). Isolates the contribution of the `H31-J` physics OOF surface under the exact `D2.8 + B2` emitter geometry of `GEMSDOE32`.
3. **Experiment 3 (`H31-J3 · TGTD-Geotherm-PTCF-DualOOF-Submod`, Primary Preregistered Candidate):**
   - Exact same `H31-J` Dual-Regime stitched 4-quadrant OOF surface emitted via **1D Ridge-Localized Lazy-Greedy 300 m Submodular Cover** (`ridge_sharpened_weight(gamma=2.0, flank_px=2.0)` + `submodular_dti_emit(min_dist_px=2.4)`), emitted for the final raster strictly from **stitched 4-quadrant OOF predictions** (every quadrant scored by models that never saw a single label in that quadrant — **zero in-sample refit memorization**!).

---

## 4. Promotion Gates, Controls, & Validation Suite

1. **Gate G1 — Data & Shared Cache Integrity:** All 11 GeoTIFFs in `registry/data_manifest.json`, all 19 `.cache/features/band-01..19.npy` hashes in `registry/template_pins.json`, and `gdr_wellspring_in_footprint.csv` (`sha256: 122718e65bdf55aab0ee12ad20d80062f0deb1de957225a61ad880dd5dc196ea`) match byte-for-byte.
2. **Gate G2 — Single-Feature & Missingness Leakage Canary (`seed=31`):** Every feature column satisfies $\max(\text{AUC}, 1-\text{AUC}) \le 0.90$ and missingness $\text{AUC} \le 0.90$.
3. **Gate G3 — Dual-Stage Uniqueness Canary (Continuous Pre-Placement Surface AND Final Emitted Dots):**
   - **`G3a` (All Discrete/Actionable Submissions Across `GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, 36, 70` + All Local `GEMSDOE31` Lanes including `MAGREST` & `H31-E2`):** `|Spearman rho| <= 0.90` AND `3-px overlap <= 0.70` on both pre-placement surface (`prospective top-37,654`) and final `37,654` dots.
   - **`G3b` (Literal Un-Amended Shared Registry `57GEMSDOE` including `r13-lattice-s5` 5×5 Calibration Lattice & `GEMSDOE48` Full-Footprint Surface):** Reported verbatim without silent exemptions; because `r13-lattice-s5` places a dot every 500 m across 100% of $\mathbb{Z}^2$ (`max distance sqrt(8) <= 3 px`), any raster has literal `100%` 3-px overlap against that lattice, which is disclosed transparently on `docs/index.html`, `docs/executive-summary.html`, and the JSON Run Card alongside `slot_approved = false`.
4. **Gate G4 — Primary `gems57-pooled-hide-v2` Buffered Holdout Screen (`seed=31`, `2,901` withheld positives, `buffer_px=213` = `21.3 km`) + Untouched Fresh Confirmation (`seed=32`, `buffer_px=213`):**
   - Compare `H31-J3` directly on the **exact same `gems57-pooled-hide-v2` instrument** against:
     1. `physical_hgb` (`0.048294` on `seed=31`),
     2. `MAGREST` (`0.052972` on `seed=31`),
     3. Fold-fair `GEMSDOE32 H33-2-B2` rule (`H19-5` continuous score + `d=2.8` + `d_vis > 2.0 px` on fold-visible catalogue).
   - Screen pass requires: `pooled DTI > physical_hgb`, `1,000`-draw `20 km` block paired bootstrap `95% CI lower > 0` vs `physical_hgb`, `>= 3/4` spatial quadrant wins, and worst quadrant delta `>= -0.010`.
   - Confirmation pass requires: **zero code/hyperparameter changes** on untouched `seed=32` achieving `pooled DTI > physical_hgb` and paired `95% CI lower > 0`.
5. **Gate G5 — Own-Method OOF Residual Semivariogram Range Audit (`src/gemsdoe31/variogram.py`):**
   - Estimate empirical Matheron semivariogram & exponential practical range ($95\%$ sill) on `H31-J3`'s own hidden-component OOF residuals and verify whether the `21,300 m` (`213 px`) collar exceeds `H31-J3`'s own practical range (closing the open limitation from `MAGREST`).
6. **Gate G6 — Off-Catalogue `SGMC > 300 m` Proxy Audit (Both All-Elevation AND Piedmont-Low-Relief + Far-Field `> 1.5 km` Share):**
   - Report full-footprint (`> 300 m` from `labels.tif`) AND piedmont (`det_elev < 100 m`, `> 300 m` from `labels.tif`) `SGMC` proxy DTI (`HOLDOUT-PROXY-SGMC`, never treated as organizer DTI) against `GEMSDOE32 H33-2-B2` (`37,654` dots) and `H31-E2` (`37,654` dots), plus verify far-field (`> 1.5 km`) dot share `>= 45%` (preventing near-catalogue starvation).
7. **Gate G7 — Automated Submission Format & `[0, 1]` Range Regression Lock:**
   - Emit both `-zeros.tif` (`all-finite float32 in [0.0, 1.0]` across all `12,279,160` grid cells, immune to any whole-array `[0, 1]` portal check) and `-nan.tif` (`finite float32 in [0.0, 1.0]` on all `5,167,373` footprint cells, `NaN` outside footprint matching `sample_submission.tif`), plus single-TIFF `.zip` archives and automated format receipts.
