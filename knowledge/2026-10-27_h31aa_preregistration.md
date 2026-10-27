# Preregistration — Lane `H31-AA` (`SLFS`): Strike-Coherent Logarithmic Piedmont Flexure with Equipotential Paleoshoreline Rejection and Subsurface Basin-Edge Corroboration

- **Date (UTC):** `2026-10-27`
- **Session branch:** `arena/f5b2211b-gemsdoe31` (branched from `main`, fast-forwarded to `fbebc01703a39a99528432892b7c11b716ca5ab3`)
- **Lane ID:** `H31-AA` (`SLFS`) — checked against `origin/main` and all open PRs (`#31, #38, #40, #42, #51`) for zero lane-ID collision
- **Status at creation:** FROZEN BEFORE ANY FEATURE COMPUTATION, CANARY, OR HOLDOUT EVALUATION

---

## 1. Governance & Protocol Disclosure (Read First)

1. **Missing Method Paragraph (`IR-U-01`):** The composite owner prompt instructs *"MUST GENERATE A UNIQUE TIF SUBMISSION FOR THE COMPETITION"* and *"Before implementing, generate 3–5 candidate geological hypotheses we haven't tried yet... Validate the top candidate on our spatially-blocked holdout set"*, while Protocol §1 references *"the single method paragraph below"* which is absent from the prompt text. Rather than fabricating an external assignment or leaving the scientific requirement unexecuted, this document explicitly preregisters the top-ranked unimplemented hypothesis (`H31-AA`) before any data touch.
2. **Dual Uniqueness Reporting (`literal-registry-20261026-9883b598` vs `vendor/gems57/uniqueness.py` two-phase reading):**
   - **Binding Literal Broad-Registry Gate (`G5_literal_broad_registry`):** Under the literal support rule (`prediction > 0`), the pinned 695-raster snapshot (`registry/shared_registry_57_snapshot.json`) contains a continuous probability surface (`17GEMSDOE_E-proba-multiscale`, `ab0a0a62eecf`, positive on all `5,167,373` footprint cells; `0` cells outside halo) and a uniform synthetic spacing-5 grid (`13gems_20261001_r13-lattice-s5_v2_nan-outside.tif`, `b4570b406efe`, covering `5,160,724 / 5,167,373 = 99.871%` of the footprint within 3 px; `6,649` boundary cells outside halo). At the `37,654`-dot operating budget, `overlap_budget_preflight` proves a minimum overlap of `(37,654 - 6,649) / 37,654 = 82.3418% > 70%` before any fit. No silent density or calibration-lattice exemption is applied; therefore `slot_approved = false`, `ok_to_submit = false`, and `verdict = "negative"` under the binding repository release policy (`registry/release_status.json`), and promotion to a weekly slot remains reserved to an owner-authorized selector step (Protocol §6).
   - **Two-Stage Discrete Geological-Peer Gate (`G5_discrete_two_stage`):** Simultaneously, `H31-AA` enforces the strict two-stage `|Spearman ρ| <= 0.90` AND `3-px overlap <= 0.70` threshold on **both** the pre-placement continuous surface (`top-37,654` support) **and** the final emitted dots against all discrete geological submission rasters across the nine focus sites (refreshed at `2026-10-27` HEAD commits, including the 2026-10-25 and 2026-10-26 scored waves) plus all local `GEMSDOE31` discrete lanes. Notably, the prior holdout leader `H31-X` (`0.1661`) failed Stage-1 pre-placement discrete overlap (`86.3% > 70%` vs `GEMSDOE24/27 D1.5`). `H31-AA` is designed from first principles to pass **both** stages of discrete-peer uniqueness while testing whether improved piedmont physics beats `H31-X` on the identical `gems57-pooled-hide-v2` holdout.
3. **Deliverable Policy:** Per `AGENTS.md` and Protocol §5 (*"Negative results are deliverables"*), a genuinely new, zero-copy research GeoTIFF screened for leakage and discrete-peer duplication is packaged with `ok_to_download_for_research = true`, `ok_to_submit = false`, `slot_approved = false`, and validated under both `all-finite` (`zeros`) and `nan-outside` conventions with zero human intervention.

---

## 2. Four Candidate Unimplemented Geological Hypotheses (Ranked Before Any Fit)

All expected improvements are qualitative structural-geology / metric-geometry judgments, **never predicted DTI scores** (any experiment can be negative).

| Rank | ID & Name | Specific Layers (Pinned Stack) | Targeted Physical Signature | Why It Catches Unmapped Faults (vs Mapped Catalogue) | Named Non-Fault Mimics & Falsification | How It Differs from Repo & Focus-Site Prior Art | Expected Value / Compute Cost |
|---:|---|---|---|---|---|---|---|
| **1 (Selected)** | **`H31-AA` (`SLFS`)** Strike-Coherent Log-Flexure + Paleoshoreline Null + Subsurface Corroboration | `det_elev` (B12), `det_elev_slope` (B19), `iso_grav_anom_hg` (B18), `depth_to_base_surf` (B15), `tmi_hg`/`tmi_vg` (B3/B9), `step_max`/`downface_max`/`valid` (LiDAR) | Multi-scale ($\sigma \in \{1.5, 3.0\}$ px) downslope derivative of **logarithmic** slope $-\nabla \ln(s_\sigma + 1.5^\circ)\cdot\hat{\mathbf{u}}_{\text{down}}$ windowed to piedmont-to-lower-front slopes ($0.8^\circ\text{–}18^\circ$, flat peak $2^\circ\text{–}11^\circ$), steered along local contour-strike tangent ($L=4$ px), damped by an explicit **equipotential paleoshoreline null** (low along-strike $\delta z$ + weak subsurface gravity/basement step), extracted on strict 1-px cross-strike crests | Degraded pre-Holocene piedmont scarps, relay ramps, and fan-draped range fronts have modest absolute $\Delta s$ ($3^\circ\text{–}6^\circ$) missed by field mapping and unnormalized $-\nabla s$, but strong fractional slope ratio $-\nabla \ln(s+1.5^\circ)$ and subsurface density/basement steps | Pleistocene Lake Lahontan wave-cut benches (~1,335 m, strictly horizontal with no basement step), intra-range cliff/talus breaks ($>18^\circ$), V-valley canyon mouths (short strike persistence) | `H31-X` used unnormalized $-\nabla s$ at single $\sigma=1.5$ up to $25^\circ$ (putting 19% of dots in $>15^\circ$ bedrock and failing Stage-1 top-K at 86.3%), with no strike steering or shoreline null; 100% label-free unlike `G27-H29`/`H31-DRCG`/`KPL36` HGB ensembles | Highest expected precision/recall gain on piedmont & relay fronts / ~15–25 min CPU |
| 2 | `H31-AB` Cross-Field Signed Phase-Offset Transverse Detector | `rtp` (B2), `TMI_up150` (ext), `iso_grav_anom` (B13) | Segmented magnetic tilt-phase contours tested for reciprocal signed lateral cross-correlation offset across orthogonal transfer corridors in both `rtp` and `iso_grav_anom` against an unbroken-contact null | Concealed strike-slip / oblique accommodation-zone transfer faults (Walker Lane / Humboldt zone) offset basement contacts laterally with zero vertical surface scarp | Pluton margins, caldera ring contacts, GeoDAWN survey-block seams | `MAGREST` restored 1D magnetic patches only; `XFCOH31` measured colinear gradient alignment rather than orthogonal lateral offset | Moderate specificity in volcanic basins / ~60–90 min CPU |
| 3 | `H31-AC` Matched-Catchment $k_{sn}$ Difference-in-Differences | `det_elev` (B12), `relief` (LiDAR), `iso_grav_anom_slope` (B5) | Paired D8 drainage basins matched on area and relief across candidate traces; opposite-signed normalized channel-steepness residuals stable under leave-one-channel-out jackknife | Footwall uplift persists in fluvial longitudinal profiles after diffusive hillslope creep erases surface fault scarps | Lithologic erodibility contrasts, stream capture, alluvial avulsion | Existing terrain curvatures are local pixel filters, not paired-catchment DiD estimators; high-res extension requires USGS 3DEP 10 m DEMs (official public source `https://www.usgs.gov/3d-elevation-program`, unreachable under sandbox allowlist) | Lower SNR at 100 m grid / ~60 min CPU |
| 4 | `H31-AD` Conductance–Basement Horst-Flank Conduit Detector | `cond_surf` (B17), `depth_to_base_surf` (B15), `ThK`/`UK` (GeoDAWN), `ieq_n100a15` (B16) | Anti-parallel lateral gradients $\nabla \text{cond\_surf} \cdot (-\nabla \text{depth\_to\_base\_surf}) > 0$ along smectite-clay-cap / resistive-horst boundaries corroborated by low `Th/K` potassium metasomatism | Blind geothermal upflow faults (Dixie Valley / McGinness Hills style) sit at the horst-flank boundary beneath conductive argillic alteration caps with no surface scarp | Saline playa evaporites and lacustrine basin-center clays | `H31-U` / `H31-YR` combined isotropic gradient magnitudes rather than signed horst-flank polarity + K-metasomatism | Coarse `cond_surf` limits 300 m kernel localization / ~20 min CPU |

---

## 3. Exact Mathematical Specification of `H31-AA` (Frozen)

All operations are **100% label-free** (no fault catalogue labels or SGMC faults ever enter feature construction). Missing values are median-imputed inside the footprint after `[0.1, 99.9]` percentile winsorization and masked outside the footprint.

1. **Multi-Scale Logarithmic Piedmont Flexure (`LFLEX_RAW`):**
   - For each scale $\sigma \in \{1.5, 3.0\}$ px ($150\text{ m}$ and $300\text{ m}$):
     - Smooth elevation $z_\sigma = G_\sigma * z$ and slope $s_\sigma = G_\sigma * s$.
     - Downslope unit vector $\hat{\mathbf{u}}_{\text{down},\sigma} = -\nabla z_\sigma / (\|\nabla z_\sigma\| + 10^{-6})$ and local contour-strike tangent $\hat{\mathbf{u}}_{\text{strike},\sigma} = (-\hat{u}_{\text{down},\sigma,x},\; \hat{u}_{\text{down},\sigma,y})$.
     - Logarithmic slope field $\ell_\sigma = \ln(\max(s_\sigma, 0) + s_0)$ with $s_0 = 1.5^\circ$.
     - Concave-up relative flexure $\phi_\sigma = \max(0,\; -\nabla \ell_\sigma \cdot \hat{\mathbf{u}}_{\text{down},\sigma}) \cdot W_{\text{pied}}(s_\sigma)$, where $W_{\text{pied}}(s)$ rises linearly from $0$ at $0.8^\circ$ to $1$ at $2.0^\circ$, equals $1$ on $[2.0^\circ, 11.0^\circ]$, falls linearly from $1$ at $11.0^\circ$ to $0$ at $18.0^\circ$, and equals $0$ above $18.0^\circ$.
   - **Steered Along-Strike Integration:** For each $\sigma \in \{1.5, 3.0\}$, sample $\phi_\sigma$ at offsets $k \in \{-4, -3, -2, -1, 0, 1, 2, 3, 4\}$ px along $\hat{\mathbf{u}}_{\text{strike},\sigma}$ (nearest-grid steered indexing clipped to bounds, zero outside footprint) with Gaussian weights $w_k \propto \exp(-0.5 (k / 2.5)^2)$, yielding $\bar{\phi}_\sigma$.
   - Combine scales via geometric mean: $F_{\text{flex}} = \sqrt{\bar{\phi}_{1.5} \cdot \bar{\phi}_{3.0}}$.

2. **Equipotential Paleoshoreline Null Suppressor (`w_shore`):**
   - Along-strike elevation RMS variation over $\pm 6$ px ($600\text{ m}$) along $\hat{\mathbf{u}}_{\text{strike}, 3.0}$:
     $$\delta z_{\text{strike}}(x) = \sqrt{\frac{1}{4}\sum_{k \in \{-6, -3, +3, +6\}} \big(z_{1.5}(x + k\,\hat{\mathbf{u}}_{\text{strike},3.0}) - z_{1.5}(x)\big)^2}$$
   - Subsurface basin-edge rank $S_{\text{sub}}(x) = \text{geomean}\big(\text{rank}(|\text{iso\_grav\_anom\_hg}|),\; \text{rank}(\|\nabla_{2.0}\text{depth\_to\_base\_surf}\|),\; \text{rank}(\sqrt{\text{tmi\_hg}^2 + \text{tmi\_vg}^2})\big)$.
   - Equipotential-shoreline score: $p_{\text{hor}}(x) = 1 - \text{rank}(\delta z_{\text{strike}}(x))$ (high when the contour is nearly horizontal over $1.2\text{ km}$).
   - Shoreline mimic indicator: $m_{\text{shore}}(x) = \text{clip}((p_{\text{hor}}(x) - 0.60)/0.40,\; 0,\; 1) \cdot \text{clip}((0.55 - S_{\text{sub}}(x))/0.55,\; 0,\; 1)$.
   - Shoreline survival weight: $w_{\text{shore}}(x) = 1.0 - 0.65\,m_{\text{shore}}(x) \in [0.35, 1.0]$.
   - Shoreline-filtered flexure field: $F_{\text{shore}} = F_{\text{flex}} \cdot w_{\text{shore}}$.

3. **Strict 1-Pixel Cross-Strike Crest Extraction (`crest1px`):**
   - Along integer-rounded $\hat{\mathbf{u}}_{\text{down}, 1.5} = (\Delta y, \Delta x)$, a pixel is on the cross-strike directional crest iff $F(r,c) > 0$, $F(r,c) \ge F(r+\Delta y, c+\Delta x)$, and $F(r,c) > F(r-\Delta y, c-\Delta x)$ (strict inequality on the upslope side breaks ties deterministically to 1 pixel!).
   - Non-crest pixels retain $0.05 \cdot F(r,c)$ so full-footprint rank ordering stays continuous and non-degenerate while the top-$37,654$ pixels lie strictly on 1-pixel-thin fault-toe crests.

4. **Corroborating Lines & Candidate Arms (`EXP-1`):**
   - `LFLEX_COH` = `rank01(crest1px(F_flex))`
   - `LFLEX_SHORE` = `rank01(crest1px(F_shore))`
   - `SUB_EDGE` = $S_{\text{sub}}$
   - `LIDAR_TOE`: inside `valid > 0`, geometric mean of within-LiDAR percentile ranks of `step_max` and `downface_max`; outside `valid > 0`, exact neutral value `0.50`.
   - **Four Frozen Candidate Arms:**
     - `AA1`: `LFLEX_COH`
     - `AA2`: `LFLEX_SHORE`
     - `AA3`: `rank01(crest1px(F_shore * (0.65 + 0.35 * SUB_EDGE)))`
     - `AA4`: `rank01(crest1px(F_shore * (0.55 + 0.25 * SUB_EDGE + 0.20 * LIDAR_TOE)))`
   - **Same-Run Comparators (rebuilt and scored on identical folds/emission):**
     - `JUNC_INC`: `H31-X` winning `X1` (`JUNC_RAW`, global `GEMSDOE31` holdout best `0.166133`)
     - `CTRL`: `rank01(tmi_hg)`
     - `SLOPE`: `rank01(det_elev_slope)`

---

## 4. Validation Protocol, Gates, and 3-Experiment Budget

- **Shared Evaluator & Buffer:** `vendor/gems57/evaluate_holdout.py` (`gems57-pooled-hide-v2`), whole-component hiding (`spatial.folds(cat, foot, buffer_px=213)`, `60,988` withheld positives across 4 quadrants), fold-visible `d_vis > 2.0 px` exclusion, exact `masked_known` masking of visible faults, score-ordered `2.8 px` Poisson-disk emission at `37,654` dots (`α=0.2, β=0.8, 300 m` triangular kernel).
- **Stage 0 — Single-Feature Leakage Canary & Pre-Placement Uniqueness:**
  - Every individual line (`LFLEX_COH`, `LFLEX_SHORE`, `SUB_EDGE`, `LIDAR_TOE`, `JUNC_INC`, `CTRL`, `SLOPE`) and every arm (`AA1..AA4`) must satisfy $\max(\text{AUC}, 1-\text{AUC}) \le 0.90$ on both `cat` and `off_sgmc` (`G2_canary`).
  - Pre-placement surface check on `AA1..AA4` against all refreshed 9-site discrete peers + all local `GEMSDOE31` discrete lanes: requires `|Spearman ρ| <= 0.90` AND `top-37,654 3-px overlap <= 0.70`.
- **`EXP-1` (4-Arm Screen):** Score `AA1..AA4`, `JUNC_INC`, `CTRL`, `SLOPE` on the 213-px quadrant folds. Winner = highest pooled `HOLDOUT-DTI` among `AA1..AA4` passing Stage-0 pre-placement discrete uniqueness.
- **`EXP-2` (Crest-Thinning Ablation + Final Emission + Full Uniqueness Audit):** Compare `EXP-1` winner (`crest1px`) against its unthinned counterpart (`no_crest`) on the 213-px holdout and two-stage discrete uniqueness; retain the variant passing two-stage discrete uniqueness with higher holdout DTI. Emit `37,654` binary dots on `foot & (d_cat > 2.0)` and audit both discrete-peer uniqueness and the literal `r13-lattice-s5` / continuous-surface registry witnesses.
- **`EXP-3` (Untouched Confirmation Split `seed=3107` + Off-Catalogue SGMC Proxy + Updated `n=71+` Cross-Family Score Audit):** Zero parameter changes. Evaluate on `random_component_split(cat, foot, seed=3107)` vs `JUNC_INC`, `CTRL`, `SLOPE`; score off-catalogue SGMC (`d_cat > 3 px`) full, slope regimes, and quadrants vs `H33-2-B2` and `H31-X`.
- **Hard Gates:**
  - `G1_format`: both `zeros` and `nan` GeoTIFFs pass `gemsdoe31.submission.validate_submission` (`EPSG:32611`, `3730×3292`, `float32`, finite `[0,1]`, `37,654` dots, `0` on catalogue).
  - `G2_canary`: all single lines and candidate surfaces have two-sided AUC $\le 0.90$.
  - `G3_beats_holdout_best`: beats `CTRL`, `SLOPE`, **and same-run rebuilt `JUNC_INC` (`H31-X`, `0.166133`)** with paired 95% bootstrap CI $> 0$ on screen AND untouched confirmation (`seed=3107`).
  - `G4_sgmc_discovery`: off-catalogue SGMC DTI $\ge$ `H33-2-B2` (`0.0940`).
  - `G5_discrete_two_stage`: both pre-placement `top-37,654` 3-px overlap $\le 0.70$ AND final-dot 3-px overlap $\le 0.70$, plus $|\rho| \le 0.90$, across all refreshed discrete peers.
  - `G5_literal_broad_registry`: literal 695-raster check including `r13-lattice-s5` (expected `FAIL` due to `82.34%` mathematical floor at `37,654` dots; never exempted). Because `G5_literal_broad_registry` is binding for repository upload permission (`registry/release_status.json`), `ok_to_submit` and `slot_approved` remain `false` unless an owner-authorized selector explicitly adopts discrete-peer gating.
