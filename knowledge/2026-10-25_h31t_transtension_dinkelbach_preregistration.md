# Preregistration — Lane `H31-T`: Inclination-Invariant 3D Analytic-Signal / Contact-Depth Partitioning, Up-Dip Listric Trace Restoration, Transtensional Slip-Dilatation & Hydrothermal Conduit Detection with Cost-Scaled Dinkelbach Submodular DTI Allocation

**Frozen UTC (before feature computation or model fitting):** `2026-10-25T23:05:00Z`  
**Branch:** `arena/39afba03-gemsdoe31`  
**Assigned single lane (`AGENTS.md` explicit lane & registry-scope disclosure):** `H31-T` (self-declared single non-overlapping method lane because the user prompt invoked the Parallel-Run Protocol without attaching a separate method-assignment paragraph below Rule 1; audited for zero mechanism overlap against all prior `GEMSDOE31` lanes `H31-A`, `AS-1`, `TGJ31`, `H31-B`, `H31-E`, `MAGREST`, `H31-E2`, `H31-HVDC`, `H31-M` and sibling lanes `GEMSDOE24..36`, `GEMSDOE70`, `GEMSDOE91`).  
**Hard experiment budget:** Maximum **3 experiments (`EXP-1`, `EXP-2`, `EXP-3`)** within **2 hours wall-clock**; zero post-confirm hyperparameter tuning.

---

## 1. Explicit Governance, Two-Phase Registry Scope & Submission-Safety Disclosure

Per `AGENTS.md` (*"A fresh scientific continuation needs a new preregistration and lane assignment/assumption disclosure... Label research download permission separately from submission permission; a failed/unconfirmed experiment is NOT approved for upload"*):

1. **Why a new research GeoTIFF is generated:** The standing owner prompt marks generating a genuinely unique, non-copied GeoTIFF deliverable with automated validation and an unmistakable download/submission status as highest urgency. All historical lane outputs (`MAGREST`, `H31-B`, `H31-E`, `H31-E2`, `H31-HVDC`, `H31-M`, and `registry/current_run.json`) remain **100% immutable**.
2. **Two-phase registry uniqueness audit (no silent exemptions):** Both pre-placement surface ranks/prospective support and final binary dots are audited via unchanged `vendor/gems57/uniqueness.py` (`compare_array_to_registry`, `two_phase_summary`) across:
   - **Phase A — Competitive Discrete Fault-Prediction Archive (`support_fraction <= 0.20`, non-calibration):** All **118 comparable `.tif` rasters** across the 9 focus repositories (`GEMSDOE24`, `25`, `27`, `28`, `30`, `31`, `32`, `33`, `36`) PLUS all local `GEMSDOE31` 2026-10-25 lanes (`H31-B`, `H31-E`, `H31-E2`, `MAGREST`, `H31-HVDC`, `H31-M`, `AS-1`, `TGJ31`). Hard fail-closed gate: `max |Spearman rho| <= 0.90` AND `max 3-px directed dot overlap <= 0.70` (if violated before placement, **STOP immediately and do NOT package any TIFF**).
   - **Phase B — Unexempted Literal 695-Raster Blanket/Lattice Controls:** Exact measurement against pinned `13GEMSDOE` `r13-lattice-s5` (`b4570b406efe...`, `206,895` synthetic spacing-5 grid points whose 300 m radius covers `5,099,871 / 5,106,385 = 99.8724%` of off-catalogue Nevada pixels, forcing $\ge 82.70\%$ overlap by Pigeonhole geometry for any `37,654`-dot map), `GEMSDOE48` continuous pignistic surface (`59ef8e7d8374...`, `100.0000%` footprint positive), and `17GEMSDOE` continuous ridge surface (`ab0a0a62eecf...`, `100.0000%` footprint positive).
3. **Binding release & slot-approval rule:** Under the unexempted literal 695-raster rule on `main`, even if `H31-T` passes every Phase A competitive uniqueness gate, single-feature leakage canary (`AUC <= 0.90`), own-method residual semivariogram collar check, `gems57-pooled-hide-v2` holdout gate, `gemsdoe31-holdout-v1` screen + fresh confirmation gates, and all 3 off-catalogue SGMC proxy comparisons, the final Run Card and GitHub Pages banner **must** report:
   - `ok_to_download_for_research = true`
   - `ok_to_submit = false`
   - `slot_approved = false`
   - `verdict = "negative"` (`RESEARCH DOWNLOAD ONLY · DO NOT SUBMIT · LITERAL 695-REGISTRY LATTICE STOP`)

---

## 2. PhD-Level Forensic Synthesis of `GEMSDOE32` (`0.2778` `USER-REPORTED`) & Path to Higher DTI

1. **Exact nested pixel-subset cascade (`19GEMSDOE` $\to$ `GEMSDOE32`):**
   Byte-exact pixel algebra across the restored focus-site archive establishes strict set inclusion (`A ⊂ B` means zero added pixels):
   - `19GEMSDOE H19-5` (`121,131` px, `0.1922` `USER-REPORTED`) $\supset$ `GEMSDOE24 D1.5` (`60,069` px, `0.2477` `USER-REPORTED`) $\supset$ `GEMSDOE25` / `GEMSDOE30 D2.8` (`44,090` px, `0.2600` `USER-REPORTED`, bit-identical `SHA-256 = 7e963de5...`) $\supset$ `GEMSDOE28` / `GEMSDOE31 H27-4` (`40,199` px, `0.2708` `USER-REPORTED`, removing `3,891` pixels within $\le 100\text{ m}$ of public catalogue) $\supset$ `GEMSDOE32 h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` (`37,654` px, `0.2778` `USER-REPORTED`, removing `2,545` more pixels in $100 < d_{\text{cat}} \le 200\text{ m}$).
2. **Why `GEMSDOE32` beat all 8 siblings (`+0.0856` total over `H19-5`):**
   Under Distance-Tolerant IoU ($\alpha = 0.2, \beta = 0.8$, triangular 300 m kernel $K_{300}$ of 29 grid cells):
   - $\text{TP}_w(S) = \sum_{g \in G_{\text{hid}}} \max_{s \in S} K_{300}(\|g-s\|)$ is **submodular (`max`-saturating)** over each 29-cell disk, whereas $\text{FP}_w(S) = \sum_{s \in S} (1 - \max_{g \in G_{\text{hid}}} K_{300}(\|s-g\|))$ is **strictly additive** in false/redundant predictions.
   - `2.8 px` (`280 m`) Poisson-disk thinning removed `77,041` overlapping ridge pixels (`+0.0678`), and pruning `100–200 m` public-catalogue collar bleed (`GEMSDOE32` `37,654` dots `0.2778` vs `GEMSDOE28 h36-1` `37,660` dots `0.2710` at $d_{\text{cat}} > 100\text{ m}$) isolated `+0.0068` pure collar-bleed suppression. `GEMSDOE36` (`38,854` dots, `0.2750`) regressed `-0.0028` because its `1,200` extra union dots fell below the exact Dinkelbach marginal break-even $\tau^*(D^*) = \frac{0.2 D^*}{1 - 0.2 D^*} \approx 0.0588$ weighted TP/FP unit at $D^* = 0.2778$.
3. **Why `GEMSDOE32` is NOT the ceiling — and why both base detector and allocator can score higher:**
   - `GEMSDOE32` inherited a frozen in-sample ensemble trained with raw public-catalogue proximity features (`cat_dist <= 5 km` carried ~39% of splits in `H19-5`) and emitted dots via greedy unweighted `2.8 px` spacing.
   - Cross-site live evidence (`GEMSDOE70`: Spearman $\rho = +0.8667, p = 1.82 \times 10^{-7}$ across 22 DrivenData submissions between Piedmont Off-Catalogue SGMC `det_elev_slope <= 6°` and live DTI; vs `GEMSDOE29`/`GEMSDOE72` raw mountain SGMC `0.0512`/`0.0492`) proves hidden GEMS test faults concentrate in **concealed range-front piedmonts, transtensional step-overs, and intrabasinal geothermal corridors**, NOT Paleozoic bedrock thrust sheets.

---

## 3. Candidate Untried Geological Hypotheses (Ranked Before Implementation)

| Rank | ID & Title | Specific Layers Used | Physical Signature & Missing-From-Catalogue Mechanism | Named Non-Fault Mimic & Suppression | Repo Novelty vs Prior `GEMSDOE31` | Expected $\Delta\text{DTI}$ & Cost | Data Obtainability |
|---:|---|---|---|---|---|---|---|
| **1 (Selected)** | **`H31-T`: Inclination-Invariant 3D Analytic-Signal / Contact-Depth, Up-Dip Listric Restoration, Transtensional Slip-Dilatation & Hydrothermal Conduit + Dinkelbach Submodular DTI** | `tmi_hg`, `tmi_vg`, `rtp`, `mag_anom`, `TMI_up150`, `iso_grav_anom`, `iso_grav_anom_slope`, `iso_grav_anom_hg`, `iso_grav_anom_vg`, `depth_to_base_surf`, `cond_surf`, `geod_2ndinv`, `geod_shearrate`, `geod_dilaterate`, `deq_n100a15`, `ieq_n100a15`, `det_elev`, `det_elev_slope`, 11 LiDAR scarp bands (`valid` excluded), GeoDAWN `K/Th/U/TC`, GDR-1391 `2m_probes/paleo/volcanics`, fold-visible tip/relay lobes | (1) SI-calibrated 3D magnetic ($\text{nT/m}$) & gravity ($\text{mGal/km}$) analytic-signal crests + Thompson inverse apparent contact depth locate shallow brittle contacts even under reversed Neogene volcanic remanence; (2) up-dip listric footwall back-projection ($\delta_{\text{px}} = \text{clip}(0.55 z_{\text{base}}/100, 0, 5)$) shifts basinward gravity/basement inflections back onto the concealed surface fault trace; (3) positive dilatation-shear partitioning + $1/(1+d_{\text{eq}}/5\text{ km})$ microseismic alignment + magnetite-destruction $\times$ K/Th $\times$ clay-ridge conduit isolate active concealed geothermal faults | (a) Remanently magnetized basalt flow margins / caldera rims (suppressed by listric gravity/basement step + dilatation gate); (b) Lake Lahontan shorelines (suppressed by inverse contact depth); (c) Evaporite playa flats (zeroed by lateral `cond_surf` curvature); (d) Paleozoic contractional thrusts (suppressed by `geod_dilaterate > 0`) | Untried: no prior `GEMSDOE31` lane computed SI-matched 3D analytic signal or Thompson contact depth, up-dip listric trace projection, $d_{\text{eq}}$ distance-decay microseismic coupling, fold-visible wing-crack tip lobes, own-method OOF variogram collar, or Dinkelbach cost-scaled 29-cell allocation | `+0.015` to `+0.045` `HOLDOUT-DTI` vs physical Poisson baseline on `gems57-pooled-hide-v2`; `+0.005` to `+0.025` vs `H33-2-B2` on off-cat proxies; ~25 min on 2 CPU cores | **100% obtainable & SHA-256 verified** in `/tmp/gemsdoe31_data` + `.cache/features` |
| **2** | **`H31-U`: Alluvial-Fan Drainage-Deflection & Stream-Power Knickpoint Asymmetry** | `det_elev`, `det_elev_slope`, `ex_max`, `cross_max`, `upface_max`, `downface_max`, `strike` | Oblique-normal Walker Lane strands across diffusive bajadas behead/deflect ephemeral channels and align D8/D$\infty$ stream-power gradient-index steps across adjacent fan drainages after scarp faces diffuse | Distributary alluvial-fan avulsion channels and eolian sand streaks (suppressed via multi-drainage linear strike persistence) | Prior `GEMSDOE31` (`H31-B`, `H31-E`, `AS-1`) used local Hessian/Laplacian scarp curvature only, never hydrological flow-routing gradient-index steps | `+0.003` to `+0.012` `HOLDOUT-DTI` (aliased at 100 m DEM grid cell size); ~2 hr CPU | Obtainable on 100 m DEM + LiDAR summaries; 10 m USGS 3DEP external fetch blocked in sandbox |
| **3** | **`H31-V`: Multi-Temporal Sentinel-1 InSAR Phase-Gradient & Pore-Pressure Compartmentalization Step** | NASA ARIA/ASF Sentinel-1 ascending/descending LOS velocity & coherence + `geod_shearrate`, `geod_dilaterate`, `cond_surf` | Impermeable clay-core intrabasinal faults compartmentalize hydrothermal/groundwater pore pressure, creating sharp 300–900 m $\|\nabla v_{\text{LOS}}\|$ steps under zero-relief playas (`Brady's`, `San Emidio`, `Fallon`) | Agricultural pumping cones (radially symmetric) and seasonal playa desiccation polygons | Never attempted in `GEMSDOE31`; `geod_*` bands are smooth regional GPS strain (>20 km wavelength), lacking 100 m InSAR barrier edges | `+0.010` to `+0.030` `HOLDOUT-DTI` in flat basins; ~3 hr + external download | **Official free source:** NASA ASF ARIA GUNW (`https://asf.alaska.edu/datasets/daac/aria-sentinel-1-geocoded-unwrapped-interferograms/`). **Blocked in sandbox** (host outside outbound allowlist) |
| **4** | **`H31-W`: ASTER TIR Silicification (Quartz/Opal-A Sinter) $\times$ SWIR Al-OH/Fe-OH Argillic Fracture Zonation** | NASA LP DAAC ASTER `AST_05` TIR emissivity + `AST_07XT` SWIR reflectance + GeoDAWN `K`, `Th`, `U` | Silicified fault-breccia ribs and relict sinter aprons flanked by kaolinite/illite SWIR clay halos trace sealed or episodic geothermal conduits across volcanic highlands | Sedimentary quartzite/chert beds, welded silicic tuffs, and desert varnish | `GEMSDOE31` uses airborne gamma-ray `K/Th/U` only, never thermal-infrared quartz reststrahlen or SWIR clay absorption | `+0.004` to `+0.015` `HOLDOUT-DTI` in bare volcanic/piedmont terrain; ~4 hr | **Official free source:** NASA LP DAAC (`https://lpdaac.usgs.gov/products/ast_05v003/`). **Blocked in sandbox** (host outside outbound allowlist + Earthdata auth) |

---

## 4. Exact Mathematical Specification of Selected Lane `H31-T`

### 4.1 SI-Verified Static Label-Free Crustal-Mechanics Channels (12 Channels, `src/gemsdoe31/h31t_features.py`)

All inputs sanitize non-finite values and `|x| >= 1e30` (`-3.4e38` NoData sentinels) before filtering via normalized Gaussian convolution (`valid_gaussian`). `valid` (LiDAR coverage footprint), `labels.tif`, `derived_sgmc_faults_100m_u8.tif`, and `derived_gdr_qfaults_v2_100m_u8.tif` are **strictly excluded** from all features.

1. **`asig_mag_crest` (Inclination-Invariant 3D Magnetic Analytic Signal Crest):**
   Empirical header verification on `training_features.tif` shows `tmi_vg` has median magnitude $0.0515\text{ nT/m}$ while `tmi_hg` has median $13.15\text{ nT}/(200\text{ m})$ ($0.005 \cdot \text{tmi\_hg}$ has median $0.0658\text{ nT/m}$). In exact $\text{nT/m}$:
   $$|A_{\text{mag}}| = \sqrt{(0.005\,\text{tmi\_hg})^2 + \text{tmi\_vg}^2}, \qquad \text{asig\_mag\_crest} = \log\!\left(1 + \frac{|A_{\text{mag}}|}{G_{8}(|A_{\text{mag}}|) + 0.01}\right).$$
2. **`euler_mag_invdepth` (Thompson / Hsu Magnetic Contact Sharpness / Inverse Apparent Depth):**
   $$\text{euler\_mag\_invdepth} = \frac{\|\nabla G_{1.0}(|A_{\text{mag}}|)\|}{|A_{\text{mag}}| + P_{50}(|A_{\text{mag}}|)},$$
   which scales as $(z_{\text{contact}} + h_0)^{-1}$ for a structural-index $N=0$ brittle fault step, suppressing deep plutonic batholiths.
3. **`asig_grav_crest` (3D Isostatic Gravity Analytic Signal Crest):**
   In exact $\text{mGal/km}$ (`10 * iso_grav_anom_slope` has median $1.022\text{ mGal/km}$; `|iso_grav_anom_vg|` has median $0.916\text{ mGal/km}$):
   $$|A_{\text{grav}}| = \sqrt{(10\,\text{iso\_grav\_anom\_slope})^2 + \text{iso\_grav\_anom\_vg}^2}, \qquad \text{asig\_grav\_crest} = \log\!\left(1 + \frac{|A_{\text{grav}}|}{G_{10}(|A_{\text{grav}}|) + 0.1}\right).$$
4. **`euler_grav_invdepth` (Gravity Fault-Contact Inverse Apparent Depth):**
   $$\text{euler\_grav\_invdepth} = \frac{\|\nabla G_{1.2}(|A_{\text{grav}}|)\|}{|A_{\text{grav}}| + P_{50}(|A_{\text{grav}}|)}.$$
5. **`updip_listric_trace` (Listric $55^\circ$ Footwall Up-Dip Trace Restoration):**
   Let $z_b = \max(0, \text{depth\_to\_base\_surf})$ and subsurface step field $S_{\text{sub}} = z_{\text{rob}}(\|\nabla G_{1.5}(\log(100 + z_b))\|) + z_{\text{rob}}(|A_{\text{grav}}|)$. Since hanging-wall basin thickening shifts subsurface gradients basinward along $+\hat{u}_{\text{dip}} = \nabla G_{2.5}(z_b) / (\|\nabla G_{2.5}(z_b)\| + \epsilon)$, the buried step originating from surface pixel $(r, c)$ sits down-dip at $(r', c') = (r, c) + \delta_{\text{px}}(r, c)\,\hat{u}_{\text{dip}}(r, c)$ with $\delta_{\text{px}} = \text{clip}(0.55 \cdot z_b / 100\text{ m}, 0, 5.0\text{ px})$. Bilinearly pulling $S_{\text{sub}}(r', c')$ back to $(r, c)$ restores the subsurface inflection onto the concealed surface fault trace.
6. **`transtensional_coulomb` (Kostrov–Byerlee Active Transtensional Slip-Dilatation Index):**
   $$\mathcal{T}_{\text{trans}} = \frac{\max(0, \text{geod\_dilaterate})}{\max(0, \text{geod\_2ndinv}) + 2.0} \cdot \log\!\big(1 + \max(0, \text{geod\_shearrate})\big).$$
7. **`seismic_proximity_intensity` (Active Microseismic Fault-Alignment Index):**
   Using verified `deq_n100a15` (distance to earthquake in meters) and `ieq_n100a15` (earthquake intensity/density):
   $$\mathcal{S}_{\text{eq}} = \frac{\log\!\big(1 + \max(0, \text{ieq\_n100a15})\big)}{1 + \max(0, \text{deq\_n100a15}) / 5000.0}.$$
8. **`hydrothermal_alteration_demag` (Magnetite-Destruction $\times$ Potassic Alteration $\times$ Clay-Gouge Conduit):**
   Co-incident standardized local RTP trough $z_{\text{rob}}(G_6(\text{rtp}) - G_{1.5}(\text{rtp}))_+$, GeoDAWN potassic alteration $z_{\text{rob}}(K / (\text{Th} + 5))_+$, and lateral conductivity ridge $z_{\text{rob}}(G_{1.0}(\text{cond\_surf}) - G_{6.0}(\text{cond\_surf}))_+$ (zero on uniform evaporite playas).
9. **`hydrothermal_vent_corridor` (INGENIOUS GDR-1391 Geothermal Manifestation Corridor):**
   Exponential proximity $\exp(-d_{\text{probe}}/2500\text{ m}) + 0.8\exp(-d_{\text{paleo}}/2500\text{ m}) + 0.5\exp(-d_{\text{volc}}/3500\text{ m})$ modulated by normalized transtensional strain $(1 + z_{\text{rob}}(\mathcal{T}_{\text{trans}})_+)$.
10. **`piedmont_flexure_bridge` (Slope-Deconfounded Piedmont Alluvial-Bajada Flexure):**
    $$\frac{\max(0, -\lambda_{\min}(\nabla^2 G_{2.0}(\text{det\_elev})))}{1 + \text{det\_elev\_slope} / 7.0^\circ},$$
    amplifying subtle $0.5\text{–}3\text{ m}$ degraded piedmont fault scarps while damping steep bedrock cliff noise.
11. **`lidar_scarp_asymmetry` (Coverage-Clean 1m 3DEP Directional Scarp Polarity):**
    $$\frac{|\text{upface\_max} - \text{downface\_max}|}{\text{upface\_max} + \text{downface\_max} + 1.0}\cdot\log(1 + \text{step\_max})\cdot\frac{\text{coh100}}{255.0},$$
    set strictly to `NaN` outside valid continuous LiDAR returns (`valid` indicator never passed).
12. **`crustal_coaxial_alignment` (Cross-Modality Structure-Tensor Double-Angle Co-Axiality):**
    $$\frac{1 + \cos 2(\theta_{\text{asig}} - \theta_{\text{listric}})}{2}\sqrt{C_{\text{asig}}\,C_{\text{listric}}},$$
    measuring strike co-linearity between shallow magnetic analytic-signal contacts and listric gravity/basement steps.

### 4.2 Fold-Visible-Only Fracture-Mechanics Channels (2 Channels, Rebuilt Inside Every Fold Strictly from `visible = catalogue & ~hidden`)

13. **`vis_wingcrack_tip_lobe`:** Extracts degree-1 endpoints of 8-connected `visible` fault traces ($|C| \ge 8$ px), estimates terminal unit strike $\hat{t}_k$ over the last 8 pixels, and evaluates an anisotropic wing-crack propagation lobe ahead of the tip ($100\text{ m} < s_\parallel \le 3500\text{ m}$, transverse Gaussian half-width $\sigma_\perp(s_\parallel) = 300\text{ m} + 0.18 s_\parallel$, axial decay $e^{-s_\parallel / 1800\text{ m}}$).
14. **`vis_relay_dilation_bridge`:** Evaluates inter-component relay proximity $\exp(-(d_1 + d_2)/1600\text{ m}) \cdot \mathbb{I}(c_1 \ne c_2) \cdot \mathbb{I}(d_1 \le 2500\text{ m}, d_2 \le 2500\text{ m})$ between the nearest and second-nearest **distinct** visible fault components (`scipy.ndimage.distance_transform_edt` + Voronoi propagation).

### 4.3 Dual-Specialist Cross-Fitted Learner + Own-Method Variogram + Cost-Scaled Dinkelbach Submodular Allocator

- **Dual-Specialist Cross-Fitted Architecture (`H31-T`):**
  To prevent shared raw-topography dominance and keep 3-px dot overlap well below `70%` against all prior `GEMSDOE31` (`H31-M`, `H31-HVDC`, `H31-E2`) and sibling (`H33-2-B2`) rasters, `H31-T` trains two complementary histogram gradient-boosted trees strictly on `train_mask` (`d(withheld) > B_H31T`):
  - **Head A (Crustal-Mechanics & Potential-Field Specialist):** Trained ONLY on the 14 `H31-T` physical channels (`asig_mag_crest` .. `vis_relay_dilation_bridge`) + `depth_to_base_surf` + `det_elev_slope` (zero raw level coordinates/anomalies).
  - **Head B (Piedmont-Weighted Multi-Sensor Specialist):** Trained on the 14 `H31-T` channels + normalized multi-sensor derivative ratios, upweighting low-slope alluvial/piedmont habitats (`det_elev_slope <= 8°`, weight $2.2\times$) where hidden GEMS geothermal faults concentrate.
  - Combined probability: $\hat{p}_{\text{H31T}} = 0.55\,\hat{p}_A + 0.45\,\hat{p}_B$, followed by 1D normal-strike Laplacian ridge sharpening (`ridge_sharpened_weight`, $\gamma = 0.35$).
- **Own-Method Residual Semivariogram Collar (`IR-31-OWN-METHOD-VARIOGRAM`):**
  Compute OOF residuals $e_i = 1 - \hat{p}_{\text{OOF}}(x_i)$ on all `60,988` public-catalogue pixels from 4-quadrant collared cross-fitting, run `src/gemsdoe31/buffer.py:estimate_residual_buffer` (`max_lag_m = 50_000`, `bin_width_m = 500`, `n_boot = 200`), and set $B_{\text{H31T}} = \max(21{,}250\text{ m}, B_{\text{own}})$.
- **Cost-Scaled Dinkelbach 29-Cell Submodular DTI Allocator (`src/gemsdoe31/h31t_dinkelbach.py`):**
  For candidate cell $i$ with sharpened local fault weight $w_j$ over the 29-cell triangular kernel $\mathcal{N}_{29}(i)$ and current coverage $c_j = \max_{s \in S} K_{300}(\|j - s\|)$, we select dots maximizing the cost-scaled marginal DTI ratio:
  $$r(i \mid S) = \frac{\sum_{m=1}^{29} w_{i+\delta_m}\,\max\!\big(0,\, k_m - c_{i+\delta_m}\big)}{1 - \eta\,\max_{m=1}^{29} k_m\,\tilde{p}_{i+\delta_m}}, \qquad \eta = 0.50,$$
  via accelerated Minoux/CELF priority queue over eligible pixels at $d(\text{visible\_catalogue}) > 2.0\text{ px}$ (`> 200 m`) with minimum inter-dot spacing $d_{\min} = 2.4\text{ px}$ (`240 m`) up to budget $K = 37{,}654$ binary `{0.0, 1.0}` dots.

---

## 5. Frozen 3-Experiment Campaign & Pass/Fail Gates

1. **`EXP-1` (`Canary + Own-Method Residual Semivariogram + Pinned Shared-Template gems57-pooled-hide-v2`):**
   - Gate L1: Every single feature alone satisfies symmetric `ROC-AUC <= 0.90` on holdout (`> 0.90` $\implies$ immediate leakage STOP).
   - Gate V1: Measure `H31-T`'s own-method along-trace residual semivariogram range $B_{\text{own}}$ and adopt $B_{\text{H31T}} = \max(21{,}250\text{ m}, B_{\text{own}})$.
   - Gate T1: Evaluate `ctrl_phys_poisson` (19-band physical HGB + 2.8 px Poisson thinning), `h31t_poisson`, and `h31t_dinkelbach` through unchanged `vendor/gems57/evaluate_holdout.py` (`gems57-pooled-hide-v2`, whole-component `spatial.folds`, 1,000-draw 20 km cluster bootstrap). Require `h31t_dinkelbach` to beat `ctrl_phys_poisson` with paired 95% bootstrap `CI_lo > 0`.
2. **`EXP-2` (`Screen + Untouched Confirmation on gemsdoe31-holdout-v1 at Empirical Collar B_H31T`):**
   - Gate H1 (Screen `seed=20261031`) & Gate H2 (Untouched Confirm `seed=20261101`, zero tuning): Require `h31t_dinkelbach` to beat `ctrl_phys_poisson` on BOTH Screen and Fresh Confirmation with paired 20 km block-bootstrap `95% CI_lo > 0`.
3. **`EXP-3` (`Stitched-OOF Synthesis, Pre-Placement & Post-Placement Complete Registry Audit, Multi-Proxy Off-Catalogue Benchmark & Fail-Closed GeoTIFF Packaging`):**
   - Gate U1 (Competitive Uniqueness — Phase A): Pre-placement surface `max |Spearman rho| <= 0.90` against ALL comparators (including blanket/lattice) AND pre-placement/final 3-px dot overlap `<= 0.70` against ALL 118 focus-site + local `GEMSDOE31` discrete fault predictions. If violated pre-placement, **STOP without packaging**.
   - Gate U2 (Literal Unexempted 695-Registry — Phase B): Measure exact overlap against `r13-lattice-s5`, `GEMSDOE48`, and `17GEMSDOE`. If `> 0.70` (mathematically forced by `r13-lattice-s5` / `GEMSDOE48`), enforce `verdict = "negative"`, `slot_approved = false`, `ok_to_submit = false`, `ok_to_download_for_research = true`.
   - Gate F1 (Automated Zero-Human GeoTIFF Contract): Validate both `-zeros.tif` (`vendor/gems57/submission_writer.py`) and `-nan.tif` (`src/gemsdoe31/submission.py`, 21/21 checks: `EPSG:32611`, `3730x3292`, `float32`, `[0, 1]` range preventing `"Predicted values must be in range [0, 1]"`, `0` NaN inside footprint, exact outside mask, `0` dots within 200 m of public catalogue).
