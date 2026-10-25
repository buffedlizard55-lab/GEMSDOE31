# GEMSDOE31 — Auditable DOE GEMS Prize Fault-Mapping Research & Promoted H31-M Submission

> **SUBMISSION READINESS STATUS: YES — VALIDATED & OK TO DOWNLOAD AND SUBMIT (`verdict: "promote"`, 11/11 frozen gates `True`).**
> - **Primary Unique Submission (`H31-M`):** [`docs/downloads/gemsdoe31-h31m-bstep-xmod-submod-20261025-37654-nan.tif`](docs/downloads/gemsdoe31-h31m-bstep-xmod-submod-20261025-37654-nan.tif) (`.zip`: [`gemsdoe31-h31m-bstep-xmod-submod-20261025-37654-nan.zip`](docs/downloads/gemsdoe31-h31m-bstep-xmod-submod-20261025-37654-nan.zip), defensive all-finite fallback: [`gemsdoe31-h31m-bstep-xmod-submod-20261025-37654-allfinite.tif`](docs/downloads/gemsdoe31-h31m-bstep-xmod-submod-20261025-37654-allfinite.tif))
>   - **Unique Submission Name:** `GEMSDOE31-H31M-BStep-XMod-Submod-37654`
>   - **Short Portal Note (102/140 chars):** `H31-M OOF BStep+GravTilt+RTP+XMod+29cSubmod B=2: 37,654d; HOLDOUT v1 0.1350, Off4B 0.1077, Pied 0.0641`
>   - **SHA-256 (`-nan.tif`):** `ad9784c07456d9bbd897c5b47de56c96659bc619b0b23c5238c3d17846a3f3a6`
>   - **SHA-256 (`-allfinite.tif`):** `8434ac7c248bcd3f1b06859320c87f891488e601b6aeaffd961fe6756daa64f0`
>   - **SHA-256 (`.zip`):** `c24ea5d55e0ae385c9d04848676159b6afe654be0f0e9dafd5c624f3ab17c624`
>   - **Automated Format & Portal Safety (`21/21` checks PASS):** Single-band `float32`, `EPSG:32611`, `3730×3292` at `100 m`, values strictly `{0.0, 1.0}` inside footprint (`0` NaN inside footprint — eliminating `"Predicted values must be in range [0, 1]"`), `NaN` outside footprint (`37,654` positive pixels; `0` within `200 m` of the public catalogue).
>   - **Leakage Canary (`PASS`):** All 48 input/engineered features pass `ROC-AUC <= 0.90` on spatially collared holdout (`max_used_unsigned_AUC = 0.7740`, `max_new_H31M_AUC = 0.6139`; `dist_cat_km` and `dist_sgmc_km` flagged > `0.99` and strictly excluded).
>   - **Parallel-Run Uniqueness Gate (`PASS`):** Pre-placement continuous surface Spearman `max |r_s| = 0.7204 <= 0.90`; post-placement 3-px (`300 m`) dot overlap `<= 53.16% <= 70.0%` across all 7 registered `GEMSDOE31` rasters and **`40.25%`** against `GEMSDOE32 H33-2-B2` (`1,102 / 37,654` exact shared dots).
>   - **Multi-Instrument Holdout & Habitat Validation (`PASS`):**
>     - `HOLDOUT-DTI (gemsdoe31-holdout-v1, 58,625 withheld positives, 21.25 km collar)`: screen **`0.1350`** (`95% CI [0.1163, 0.1566]`, paired delta vs base `[+0.0064, +0.0380]`, **4/4 folds won**); confirm **`0.1372`** (`95% CI [0.1191, 0.1580]`, paired delta `[+0.0107, +0.0392]`, **4/4 folds won**).
>     - `HOLDOUT-DTI (evaluator_v2.0_protocol_v1_buffer21250m, 50,470 off-catalogue SGMC positives)`: **`0.1077`** (`95% CI [0.0902, 0.1336]`, `3/4` folds > `GEMSDOE32 B=2` `0.0984`).
>     - `Full-Footprint Off-Catalogue SGMC DTI (61,664 positives)`: **`0.1010`** vs `GEMSDOE32 H33-2-B2` `0.0940` (`+7.4%`) and `H27-4` `0.0938` (`+7.7%`).
>     - `Piedmont/Basin Off-Catalogue SGMC DTI (det_elev_slope <= 6 deg, 11,573 positives)`: **`0.0641`** (`37.2%` piedmont dot balance) vs `GEMSDOE32 H33-2-B2` `0.0586` (`+9.4%`), `H27-4` `0.0584`, `H31-E` `0.0481`, and `H31-B` `0.0052` (`12.3x`).
> - **Prior Archive Warning (`DO NOT SUBMIT AS PRIMARY`):**
>   - `gemsdoe31-h31b-scarp-hessian-20261025-37654-nan.tif` (`H31-B` standalone): **Superseded archive** (`IR-31-H31B-PIEDMONT-STARVATION` — placed `97.5%` of dots in steep mountains, starving piedmont faults to `0.0052`).
>   - `gemsdoe31-h31e-surfexpr-20261025-8817f551-nan.tif` (`H31-E` surface-expression): **Negative verdict — DO NOT SUBMIT** (`off_sgmc = 0.0712 < 0.0938`).

**Arena Core Values for this project: Maximize P(Win) · Own the Outcome.**
- **Maximize P(Win):** Build an end-to-end, geophysically grounded, leakage-free fault-mapping system that maximizes the probability of winning the DOE GEMS Prize on genuinely unmapped Nevada range-front piedmont, intrabasinal, and bedrock faults rather than gaming unbuffered or habitat-skewed local proxies.
- **Own the Outcome:** Verify every claim line by line from official or hash-pinned sources, fix shared tooling bugs in place, audit and disclose repository irregularities (`registry/irregularities.json`), enforce automated format and uniqueness gates without human intervention, publish negative lanes (`H31-A`, `H31-E`, superseded `H31-B` piedmont audit) plainly on the record, and strictly separate `HOLDOUT-DTI` from `USER-REPORTED` and `ORGANIZER-CONFIRMED` claims.

## Start here

| What | Where |
| --- | --- |
| One-click submission download + 5-step upload guide | [site home (`docs/index.html`)](docs/index.html) · [executive summary (`docs/executive-summary.html`)](docs/executive-summary.html) |
| PhD forensic proof of `0.2778`, 4 ranked hypotheses, and `H31-M` science | [research (`docs/research.html`)](docs/research.html) · [`knowledge/2026-10-25_h31m_subsurface_concordance_preregistration.md`](knowledge/2026-10-25_h31m_subsurface_concordance_preregistration.md) |
| H31-M Run Card (`verdict: "promote"`) & full results JSON | [`evidence/h31m_run_card.json`](evidence/h31m_run_card.json) · [`evidence/h31m_results.json`](evidence/h31m_results.json) |
| Nine-site byte-level annulus audit (`GEMSDOE24..36`) | [`evidence/nine_site_forensic_audit.json`](evidence/nine_site_forensic_audit.json) |
| Buffer derivation (`21.25 km`), collar control, metric exactness (`4.44e-16`) | [validation (`docs/validation.html`)](docs/validation.html) · [`evidence/buffer_derivation.json`](evidence/buffer_derivation.json) |
| Hash-pinned inputs, score claims, irregularities, 3-pass review logs | [register (`docs/register/index.html`)](docs/register/index.html) · [`registry/irregularities.json`](registry/irregularities.json) |
| Experiment log (11 experiment pages) & machine-readable feed | [experiments (`docs/experiments/index.html`)](docs/experiments/index.html) · [`docs/feed.json`](docs/feed.json) |
| AI-use disclosure draft for the competition narrative | [ai-disclosure (`docs/ai-disclosure.html`)](docs/ai-disclosure.html) |

GitHub Pages serves [`docs/`](docs/index.html); the root [`index.html`](index.html) redirects there.

---

## Parallel-Run Protocol & Standing Project Charter

Every session in this repository operates under the **Standing Project Charter** and **Parallel-Run Protocol**:

1. **Mission & Competition Target:** Predict hidden expert-mapped Quaternary/structural faults across the West-Central Nevada GeoDAWN study area (`EPSG:32611`, `3730×3292` cells at `100 m`, `5,167,373` in-footprint cells) that are **not** contained in the public USGS/INGENIOUS training catalogue (`labels.tif`), scored under the official Distance-Weighted Tversky Index ($\alpha = 0.2$, $\beta = 0.8$, $R = 300\text{ m}$ linear triangular kernel). Never substitute geothermal favorability for fault presence, never scrape/poll DrivenData, and never upload submissions automatically.
2. **Stay in One Novel Lane & Enforce the Uniqueness Gate:** Check `registry/submissions.json` before running. Verify uniqueness **both** on the pre-placement continuous surface (`Spearman |r_s| <= 0.90` against prior surfaces and registry rasters) **and** on the final emitted dots (`<= 70%` of dots within `3 px / 300 m` of any registered raster's dots, plus sibling benchmark `GEMSDOE32 H33-2-B2`). If either threshold is exceeded, log duplicate and stop.
3. **Reuse Shared Tools & Fix Bugs in Place:** Import evaluators, metric, emitters, and validators from `src/gemsdoe31/` and `scripts/` rather than creating private forks; fix shared bugs in place (`IR-31-STACK-SENTINEL`, `IR-31-SCRIPT-EXTERNAL-PATHS`).
4. **Label Every Number:** Every quantitative score must carry its exact provenance tag:
   - `HOLDOUT-DTI` (with evaluator ID, withheld positive count, and 95% confidence interval),
   - `USER-REPORTED` / `OWNER-MIRROR` (when reported by the user or sibling repo without an attached official DrivenData organizer receipt), or
   - `ORGANIZER-CONFIRMED` (only when backed by an official organizer score receipt in `registry/score_claims.json`).
   Never write a linear projection or calibrated formula as an actual competition score.
5. **Single-Feature Leakage Canary:** Test every input feature and engineered channel alone on the spatially blocked holdout before trusting any multi-feature model (`ROC-AUC > 0.90` = leakage until proven otherwise).
6. **Experiment Budget & Run Card:** Cap each campaign at **<= 3 experiments** and **<= 2 hours** of runtime, concluding with one machine-readable JSON Run Card (`promote` or `negative`).

---

## PhD-Level Forensic Analysis: Why `GEMSDOE32` (`h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros`) Scored `0.2778` (`USER-REPORTED`) — and How `H31-M` Beats Its Offline & Habitat Benchmarks

### 1. Byte-Verified Nine-Repository Annulus & Proxy Table (`GEMSDOE24..36`)

All 10 focus GeoTIFFs across `GEMSDOE24`, `GEMSDOE25`, `GEMSDOE27`, `GEMSDOE28`, `GEMSDOE30`, `GEMSDOE31`, `GEMSDOE32`, `GEMSDOE33`, and `GEMSDOE36` were SHA-256-verified in `evidence/nine_site_forensic_audit.json` (plus sibling diagnostic `GEMSDOE70` in `registry/score_claims.json`):

| Site & Verified Artifact Slug | Live Score (`USER-REPORTED`) | Dots $|P|$ | $d=0$ (On Cat) | $(0,1]\text{ px}$ ($0\text{–}100\text{ m}$) | **$(1,2]\text{ px}$ ($100\text{–}200\text{ m}$)** | $(2,3]\text{ px}$ ($200\text{–}300\text{ m}$) | $>3\text{ px}$ ($>300\text{ m}$) | Full Off-SGMC DTI | 4-Block Off-SGMC `HOLDOUT-DTI` (95% CI) | SHA-256 Prefix |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **GEMSDOE27** `topo-gap-closure-t-v2-on-d1-5` | `0.2449` | 61,328 | 0 | 5,413 | **3,462** | 3,312 | 49,141 | `0.0996` | `0.1021` (`[0.0842, 0.1188]`) | `33003374335d…` |
| **GEMSDOE24** `h25-1-dotted-h19-5-d1-5` | `0.2477` | 60,069 | 0 | 5,355 | **3,414** | 3,169 | 48,131 | `0.0984` | `0.1015` (`[0.0835, 0.1179]`) | `68d0e2e4fcc5…` |
| **GEMSDOE25 / 30** `d28-poisson300m-offcat-44090` | `0.2600` | 44,090 | 0 | 3,891 | **2,545** | 2,171 | 35,483 | `0.0927` | `0.0968` (`[0.0785, 0.1135]`) | `8cf893ead566…` |
| **GEMSDOE33** `h33d-analog-tip-stepover-r30` | `0.2632` | 41,865 | 0 | 1,377 | **2,517** | 2,130 | 35,841 | `0.0943` | `0.0987` (`[0.0804, 0.1157]`) | `87f857d505e2…` |
| **GEMSDOE28** `h32-1-prethin-tip-euler-d2-8` | `0.2649` | 42,294 | 0 | 1,542 | **3,095** | 2,179 | 35,478 | `0.0933` | `0.0977` (`[0.0793, 0.1146]`) | `04d31922f5c1…` |
| **GEMSDOE28** `h38-1-hf-euler-r30-r1` | `0.2707` | 37,860 | 0 | 0 | **2,353** | 2,043 | 33,464 | `0.0921` | `0.0964` (`[0.0784, 0.1130]`) | `81d5b87bc842…` |
| **GEMSDOE28 / 31** `h27-4-r1-solo-d2-8` (`B=1`) | `0.2708` | 40,199 | 0 | 0 | **2,545** | 2,171 | 35,483 | `0.0938` | `0.0981` (`[0.0796, 0.1151]`) | `07b6db446ca2…` |
| **GEMSDOE28** `h36-1-rung30-blind-r1` | `0.2710` | 37,660 | 0 | 0 | **2,353** | 2,024 | 33,283 | `0.0919` | `0.0962` (`[0.0782, 0.1128]`) | `5556aa1438fd…` |
| **GEMSDOE36** `anderson-geothermal-pinn-38854` | `0.2750` | 38,854 | 0 | 0 | **0** | 2,281 | 36,573 | `0.0954` | `0.0998` (`[0.0808, 0.1173]`) | `e15891020b9c…` |
| **GEMSDOE32** `h33-h33-2-b2-...-zeros` (`B=2`) | **`0.2778`** | **37,654** | **0** | **0** | **0** | **2,171** | **35,483** | **`0.0940`** | **`0.0984`** (`[0.0797, 0.1159]`) | `c55bafc47005…` |

*(External leaderboard anchors from user prompt / `GEMSDOE32` owner mirror: public `#1 = 0.4413` `USER-REPORTED` read 2026-10-25; earlier anchor `0.3195` `USER-REPORTED`.)*

### 2. Three Coupled Physical & Mathematical Reasons `GEMSDOE32` (`0.2778`) Topped the Fleet

1. **Tversky Kernel Economics & Marginal Break-Even ($\tau_{\text{live}} = 0.0556\text{ TP}_w/\text{dot}$):**
   Under $\text{DTI} = \text{TP}_w / (0.8\,|G_{\text{test}}| + 0.2\,\text{FP}_w + 0.2\,\text{TP}_w)$, a continuous fault trace pays $0.2$ denominator penalty on *every* cell while neighboring cells within the 29-cell $R = 300\text{ m}$ triangular kernel $k(d) = \max(1 - d/300\text{ m}, 0)$ redundantly cover the same $\max_{x} p(x)k(d(x,g))$ truth credit. Thinning `H19-5` (`121,131` px, `0.1922` `OWNER-MIRROR`) to ~283 m Poisson dots (`D2.8`, `44,090` px, `0.2600` `USER-REPORTED`) eliminated self-overlapping false positives. Differentiating DTI at `0.2778` gives the exact break-even threshold $\tau_{\text{live}} = \frac{0.2\,\text{DTI}}{1 - 0.2\,\text{DTI}} = 0.0556$ live $\text{TP}_w$/dot.
2. **Deletion of the `100–200 m` Smoothing-Bleed Flank Halo (`B=2` Prune: `+0.0070` over `H27-4`):**
   Because the organizer masks out the public USGS/INGENIOUS catalogue $C$ pixel-by-pixel from $G_{\text{test}}$, and because `H19-5` smoothed catalogue-correlated ridges with a $\sigma = 100\text{ m}$ Gaussian filter, public traces leaked high values 200 m outward into fault-parallel flanks. Removing $0 < d(C) \le 100\text{ m}$ (`3,891` dots) gave `H27-4` (`40,199` dots, `0.2708` `USER-REPORTED`), and removing the remaining **`2,545` smoothing-halo dots in $100 < d(C) \le 200\text{ m}$** gave `GEMSDOE32 H33-2-B2` (`37,654` dots, `0.2778` `USER-REPORTED`) because those flank dots earned only `~0.0040` live $\text{TP}_w$/dot ($14\times$ below `0.0556`). **Paired natural-experiment proof:** `GEMSDOE28 H36-1` emitted `37,660` dots (within 6 dots of `37,654`) while retaining `2,353` dots in `100–200 m` and scored only **`0.2710` (`USER-REPORTED`)** (`+0.0068` difference at identical budget). Similarly, `GEMSDOE36` (`38,854` dots, `0.2750` `USER-REPORTED`) regressed `-0.0028` by adding `1,200` diffuse thermal halo dots earning `~0.0125` live $\text{TP}_w$/dot.
3. **Piedmont/Basin Habitat Balance (`30.9%` Piedmont Dots vs Mountain-Only Proxy Trap):**
   In the competition data, `52.6%` of real public-catalogue Quaternary fault cells (`60,988` px, median `det_elev_slope = 5.56 deg`, median `depth_to_base_surf = 321.6 m`) lie in low-slope piedmont aprons and basin floors (`det_elev_slope <= 6 deg`), whereas unstratified `off_sgmc` (`61,664` px, median `det_elev_slope = 13.50 deg`) is `81.2%` steep pre-Quaternary mountain bedrock. In `GEMSDOE70`/`GEMSDOE76` (`OWNER-MIRROR`), `P8-OOF38k` beat `H33` by `+39.8%` on mountain-heavy `SGMC \ cat` (`0.1311 vs 0.0938`) yet dropped `-10.8%` live (`0.2478 vs 0.2778` `USER-REPORTED`) because its piedmont fault recovery fell `-10.1%`. Likewise, prior standalone `GEMSDOE31 H31-B` placed `97.5%` of its dots on steep mountains (`2.5%` piedmont, `piedmont_off_sgmc_DTI = 0.0052`). `GEMSDOE32 H33-2-B2` succeeded because its `H19-5` root preserved `30.9%` piedmont/basin coverage (`piedmont_off_sgmc_DTI = 0.0586`).

### 3. Why `0.2778` Can Be Beaten — and How `H31-M` Solves Both Detection & Allocation

At `37,654` dots and $|G_{\text{live}}| \approx 13,368$ px, `0.2778` recovers only ~23% kernel-weighted recall of hidden faults (compared with the `0.4413` `USER-REPORTED` public ceiling, ~45% recall). `H33-2-B2` leaves substantial DTI on the table because:
1. It lacks explicit **subsurface basement-step, amplitude-invariant Miller-Singh gravity phase-tilt, shallow RTP bandpass crest, and cross-modality surface-to-subsurface strike concordance** operators needed to detect concealed range-front piedmont and intrabasinal faults without triggering on pluvial Lake Lahontan shorelines;
2. Single-head classifiers suffer **3DEP LiDAR coverage confounding** (`62.1%` footprint coverage vs `72.1%` on catalogue; `44.4%` in `NE` vs `85.4%` in `SW`) and cross-quadrant positive-prior shift (`NW` holds `48.9%` of withheld positives);
3. Isotropic Poisson-disk thinning ignores the anisotropic **29-cell $R = 300\text{ m}$ triangular DTI kernel**, wasting dots in low-contrast interiors instead of maximizing exact marginal kernel coverage $\sum_u W(u)\max_{i \in S} K(\|u - i\|)$.

---

## Pre-Implementation Ranked Candidate Geological Hypotheses

Frozen in [`knowledge/2026-10-25_h31m_subsurface_concordance_preregistration.md`](knowledge/2026-10-25_h31m_subsurface_concordance_preregistration.md) before any `H31-M` feature or model was computed:

| Rank & ID | Specific Layers & Physical Signature / Transform | Why It Catches Faults Missing from USGS/INGENIOUS Catalogue | Named Non-Fault Mimic & Physical Suppression | Difference vs Prior `GEMSDOE31` Lanes | Expected DTI Gain & Cost | Verified Official Data Sources |
| --- | --- | --- | --- | --- | --- | --- |
| **1 · `H31-M`** *(Selected, Implemented & PROMOTED)* | Competition bands `depth_to_base_surf` [01], `iso_grav_anom_slope` [08], `iso_grav_anom_vg` [09], `rtp` [11], `cond_surf` [00], `det_elev` [02], `det_elev_slope` [03] + 3DEP/GeoDAWN stack: fractional throw $|\nabla Z_b|/(Z_b+150\text{ m})$, Miller-Singh tilt $\arctan(\partial_z g / |\nabla_h g|)$ zero-crossing, shallow RTP bandpass (`100–800 m`) gradient crest, $|\nabla \sigma_{\text{surf}}|$, 300 m structure-tensor coherence, piedmont flexure ridge, and strike concordance $\cos^2(\theta_{\text{surf}}-\theta_{\text{sub}})$ + deconfounded dual-head Bayes OOF HGB + exact 29-cell lazy-greedy submodular DTI emitter. | Concealed range-front piedmont faults and intrabasinal graben step-overs buried under Holocene alluvial fans/playas lack crisp aerial-photo scarps omitted by Qfaults, but juxtapose dense resistive footwall bedrock against basin fill and clay/brine fault gouge co-axially with subtle piedmont slope breaks. | **(a)** Pluvial Lake Lahontan shorelines & fluvial terrace risers ($\nabla_{\text{sub}} \approx 0 \implies \text{xmod\_strike\_concordance} \to 0$); **(b)** Circular pluton margins & calderas (suppressed by 300 m linear tensor coherence); **(c)** Flat conductive playas (zeroed by $|\nabla\sigma_{\text{surf}}|$); **(d)** 3DEP LiDAR tile borders (eliminated by within-`lidar_valid` dual-head quantile alignment). | Replaces `H31-E` (subsurface-blind, LiDAR-confounded, in-sample final fit, Poisson emitter) and `H31-B` (`97.5%` mountain bias, raw `cond_surf` Hessian, mislabeled `tc`). | `+0.008` to `+0.025` `HOLDOUT-DTI` (**measured `+0.0215 / +0.0245`**) · ~25 min on 2 CPUs · 100% in-hand SHA-256-verified data. | [DrivenData GEMS Problem Page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) · [USGS GeoDAWN ScienceBase DOI 10.5066/P93LGLVQ](https://www.sciencebase.gov/catalog/item/657e1d85d34e23d3533209f7) · [USGS 3DEP](https://www.usgs.gov/3d-elevation-program/about-3dep-products-services) |
| **2 · `H31-N`** *(Untried In-Hand Add-On)* | `external/gdr_thermal.tif` (`temp2m_anom_c`, `dist_vent_km`, `dist_sinter_km`, `dist_pal_km`) + `heatflow` [06], `strain_dilation` [15], `strain_max_shear` [16]: directional anisotropic step-over saddle bridge along local Kostrov principal shear strike. | Dilational fault step-overs and relay ramps fracture into breccia pipes channeling 2 m temperature anomalies and sinter/travertine mounds without forming a continuous surface scarp in Qfaults. | Lateral outflow thermal plumes & circular volcanic vents (`GEMSDOE36` failure mode); suppressed by restricting emission to narrow inter-tip corridors aligned with principal shear strike. | Never used in `H31-A`, `H31-B`, or `H31-E` (`gdr_thermal.tif` unused in active models). | `+0.002` to `+0.006` DTI (~5% footprint coverage) · ~35 min CPU · In-hand data. | [DOE GDR Submission 1391 (DOI 10.15121/1881483, CC-BY 4.0)](https://gdr.openei.org/submissions/1391) |
| **3 · `H31-P`** *(External CI Candidate)* | Raw 1 m 3DEP bare-earth DEM tiles (`1m_DEM_links.csv`): cross-strike Hanks (2000) morphologic diffusion-age matched filter $z(x) = \frac{H}{2}\operatorname{erf}(x/\sqrt{4\kappa t}) + bx$ across $\sqrt{4\kappa t} \in \{4, 8, 16, 32\}\text{ m}$. | Late-Pleistocene piedmont scarps degraded over 15–130 ka into 15–40 m wide S-curves are invisible on 100 m DEMs and missed by 3 m finite differences in `lidar_scarp.tif`, while retaining diagnostic symmetric convex-concave curvature doublets. | Incised V-shaped alluvial-fan gullies & road/canal embankments; rejected by odd-symmetry residual penalty + $\ge 400\text{ m}$ strike continuity. | Uses analytical diffusion-age template $R^2$ rather than `H31-B`/`H31-E` 3 m step summary rasters. | `+0.008` to `+0.018` DTI inside 62.1% 3DEP area · 1–2 days via GitHub Actions CI (sandbox allowlist blocks `usgs.gov`). | [USGS 3DEP Products](https://www.usgs.gov/3d-elevation-program/about-3dep-products-services) · [USGS TNM Access API](https://tnmaccess.nationalmap.gov/api/v1/docs) |
| **4 · `H31-Q`** *(External CI Candidate)* | 3D Great Basin / INGENIOUS magnetotelluric resistivity depth slices (`0.5, 1.5, 3.0, 6.0 km`) vs single surface `cond_surf` [00]: vertical persistence product $\prod_z |\nabla_h \log_{10}\sigma(x,y,z)|^{1/4}$. | Crustal-scale extensional fault conduits cut sub-vertically from brittle upper crust through >5 km depth, whereas surficial clay playas terminate above 500 m. | Closed-basin conductive smectite/evaporite playas (<400 m thick); rejected when vertical gradient coherence vanishes below 1.5 km. | Desk-noted previously (`H32-1`) but never formulated as multi-slice vertical phase-tensor persistence. | `+0.005` to `+0.012` DTI at 5–15 km MT spacing · 2–3 days via CI runner (sandbox blocks `gdr.openei.org` / `sciencebase.gov`). | [DOE GDR Submission 1391](https://gdr.openei.org/submissions/1391) · [USGS ScienceBase MT Compilation](https://www.sciencebase.gov/catalog/item/5fb70a32d34eb413d5e14873) |

---

## H31-M Three-Experiment Campaign Results (`evidence/h31m_results.json`)

### 1. `EXP-1`: Single-Feature Leakage Canary (`48` Used Features + Excluded Known Leaks)

All 29 full-coverage subsurface/surface bands, 11 3DEP LiDAR bands, and 8 newly engineered `H31-M` channels pass `ROC-AUC <= 0.90` on both `gemsdoe31-holdout-v1` (`58,625` withheld positives) and `off_sgmc` (`max_used_unsigned_AUC = 0.7740`, `max_new_H31M_AUC = 0.6139`). Known leak bands `dist_cat_km` and `dist_sgmc_km` were audited by the same canary, flagged > `0.99`, and strictly excluded. Unsupervised single-channel holdout DTI peaked on `rtp_bandpass_crest` (`0.0722`), `surf_piedmont_ridge` (`0.0610`), `grav_tilt_zero` (`0.0470`), and `xmod_strike_concordance` (`0.0454`).

### 2. `EXP-2`: Spatially Blocked Hide-and-Recover Holdout (`gemsdoe31-holdout-v1`, `21.25 km` Collar, `58,625` Withheld Positives)

| Run & Seed | Arm | NW | NE | SW | SE | Pooled `HOLDOUT-DTI` | Paired Block-Bootstrap 95% CI vs `base_C1` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Screen (`20261025`)** | `base_C1_poisson` (29 sub + 11 LiDAR, Poisson `d=2.8`) | `0.1053` | `0.1350` | `0.1046` | `0.1178` | `0.1135` | — |
| **Screen (`20261025`)** | `h31m_poisson` (`+8` H31-M channels, Poisson `d=2.8`) | `0.1077` | `0.1356` | `0.1146` | `0.1277` | `0.1177` (`4/4` folds > base) | `[+0.0005, +0.0102]` |
| **Screen (`20261025`)** | **`h31m_submod` (`+8` H31-M channels + 29-cell submodular)** | **`0.1111`** | **`0.1667`** | **`0.1332`** | **`0.1678`** | **`0.1350` (`4/4` folds > base)** | **`[+0.0064, +0.0380]`** |
| **Confirm (`20261026`)** | `base_C1_poisson` | `0.1058` | `0.1313` | `0.1036` | `0.1172` | `0.1127` | — |
| **Confirm (`20261026`)** | `h31m_poisson` | `0.1069` | `0.1316` | `0.1052` | `0.1251` | `0.1147` (`4/4` folds > base) | `[-0.0009, +0.0064]` |
| **Confirm (`20261026`)** | **`h31m_submod` (`+8` H31-M channels + 29-cell submodular)** | **`0.1133`** | **`0.1687`** | **`0.1378`** | **`0.1676`** | **`0.1372` (`4/4` folds > base)** | **`[+0.0107, +0.0392]`** |

### 3. `EXP-3`: Multi-Proxy Discovery, Piedmont Habitat Balance & Uniqueness (`37,654` Dots)

| Candidate / Benchmark | Dots $|P|$ | $d \le 200\text{ m}$ Cat Dots | Piedmont % (`slope <= 6 deg`) | `gemsdoe31-holdout-v1` `HOLDOUT-DTI` | 4-Block Off-SGMC `HOLDOUT-DTI` (95% CI) | Full Off-SGMC DTI | **Piedmont Off-SGMC DTI** | Max 3-px Overlap vs Registry | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **`H31-M` Primary Unique (`gemsdoe31-h31m-bstep-xmod-submod-20261025-37654`)** | **37,654** | **0** | **37.2%** | **`0.1350` / `0.1372`** | **`0.1077`** (`[0.0902, 0.1336]`) | **`0.1010`** | **`0.0641`** | **`53.16%`** (`40.25%` vs `G32`) | **PROMOTE — YES, OK TO SUBMIT** |
| **`GEMSDOE32 H33-2-B2`** (`0.2778` `USER-REPORTED`) | 37,654 | 0 | 30.9% | — | `0.0984` (`[0.0797, 0.1159]`) | `0.0940` | `0.0586` | `100.0%` vs `H27-4` | Sibling Prior-Art Benchmark |
| **`GEMSDOE28/31 H27-4`** (`0.2708` `USER-REPORTED`) | 40,199 | 2,545 | 30.8% | `0.1297` | `0.0981` (`[0.0796, 0.1151]`) | `0.0938` | `0.0584` | `100.0%` (self) | Baseline Archive |
| **`H31-B` Standalone** (superseded) | 37,654 | 0 | **2.5%** | `0.1171` | `0.1380` (`[0.1169, 0.1683]`) | `0.1391` | **`0.0052`** | — | **SUPERSEDED (Piedmont-Starved)** |
| **`H31-E` Surface-Expression** | 40,199 | 2,866 | 40.1% | `0.0884` (full) | `0.0773` (`[0.0598, 0.0879]`) | `0.0712` | `0.0481` | — | **NEGATIVE — DO NOT SUBMIT** |

---

## Limitations & Prioritized Next Steps

1. **No Organizer Score Receipt Attached:** All historical live scores (`0.4413`, `0.3195`, `0.2778`, `0.2750`, `0.2710`, `0.2708`, `0.2600`, `0.2478`) remain `USER-REPORTED` or `OWNER-MIRROR` (`registry/score_claims.json`), and all `H31-M` figures are local `HOLDOUT-DTI` / discovery-proxy measurements. If the human entrant submits `gemsdoe31-h31m-bstep-xmod-submod-20261025-37654-nan.tif`, attach the resulting portal receipt to `registry/score_claims.json`.
2. **Proxy Structural Limits:** Off-catalogue USGS SGMC faults (`61,664` px) are 1:500k state-map structures of mixed Cenozoic/Mesozoic age rather than the organizer's hidden Quaternary fault panel, which is why `H31-M` required simultaneous wins across `gemsdoe31-holdout-v1`, full `off_sgmc`, 4-block `off_sgmc`, and low-slope `piedmont_off_sgmc`.
3. **Next High-Leverage Technical Steps:**
   - **Next in-hand lane (`H31-N`):** Test directional hydrothermal step-over saddle bridges using `external/gdr_thermal.tif` constrained by Kostrov principal shear strike.
   - **Next CI-runner external data lanes (`H31-P` & `H31-Q`):** Fetch raw 1 m 3DEP DEM tiles (`1m_DEM_links.csv`) for Hanks morphologic diffusion-age scarp template matching (`H31-P`) and 3D MT resistivity depth slices from DOE GDR 1391 (`H31-Q`) via GitHub Actions where `usgs.gov` and `gdr.openei.org` egress is available.
   - **2D Anisotropic CNN / U-Net Head:** Train a 4-quadrant spatially collared CPU U-Net (building on the official DrivenData reference architecture [`drivendataorg/gems-prize-reference-solution`](https://github.com/drivendataorg/gems-prize-reference-solution)) over the 8 `H31-M` channels to capture multi-kilometer trace continuity before 29-cell submodular emission.

---

## Reproducibility and Verification Commands

Python 3.11+; pinned dependencies in [`requirements.txt`](requirements.txt).

```bash
git clone https://github.com/buffedlizard55-lab/GEMSDOE31.git && cd GEMSDOE31
python -m pip install -r requirements.txt
python scripts/download_competition_data.py --data-dir /tmp/gemsdoe31_data
python scripts/prepare_data.py --data-dir /tmp/gemsdoe31_data --out-dir /tmp/gemsdoe31_data/prepared
python scripts/check_metric.py                                   # metric vs brute force        -> evidence/metric_check.json
python scripts/run_h31m.py --data-dir /tmp/gemsdoe31_data all    # EXP-1 canary + EXP-2 screen/confirm + EXP-3 OOF submodular TIFF & Run Card
python scripts/collect_evidence.py                               # inventory artifacts, rebuild registry/*.json
python scripts/build_site.py && python scripts/check_site.py     # regenerate & verify 20-page GitHub Pages site
PYTHONPATH=src python -m pytest -q && python -m ruff check .     # run full unit/regression test suite & linter
```
