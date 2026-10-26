# GEMSDOE31 PhD-Level Forensic Review, Nine-Site Audit & H31-S (`UDAP-SSLIC`) Campaign (`2026-10-26`)

- **Repository / Branch:** `buffedlizard55-lab/GEMSDOE31` · `arena/34f326b4-gemsdoe31`
- **Review & Execution Date:** `2026-10-26`
- **Featured 2026-10-26 Unique Research Deliverable:**
  - Primary all-finite `[0, 1]` GeoTIFF: [`docs/downloads/gemsdoe31-h31s-udap-sslic-37654-20261026-9355f21d9f-zeros.tif`](../docs/downloads/gemsdoe31-h31s-udap-sslic-37654-20261026-9355f21d9f-zeros.tif) (`143,032` B, SHA-256 `186d35d8c671cb36c9e3afb0b365c47c2962727248b0acaa8196d6b767f03ffd`)
  - Official-wording NaN-outside twin: [`docs/downloads/gemsdoe31-h31s-udap-sslic-37654-20261026-9355f21d9f-nan.tif`](../docs/downloads/gemsdoe31-h31s-udap-sslic-37654-20261026-9355f21d9f-nan.tif) (`188,437` B, SHA-256 `665619b452553b25e7474ebe24cd466764550662744b36e0e7395f980ea241c1`)
  - Single-TIFF ZIP: [`docs/downloads/gemsdoe31-h31s-udap-sslic-37654-20261026-9355f21d9f-zeros.zip`](../docs/downloads/gemsdoe31-h31s-udap-sslic-37654-20261026-9355f21d9f-zeros.zip) (`108,160` B, SHA-256 `862d4971202580540a33b6eb2d913eea49376fe9a0918150f021238afa0bc07e`)
  - JSON Run Card: [`docs/downloads/h31s-run-card.json`](../docs/downloads/h31s-run-card.json) / [`evidence/h31s/run_card.json`](../evidence/h31s/run_card.json)
  - Unmistakable Status: **`DOWNLOAD FOR RESEARCH: YES · SUBMIT TO DRIVENDATA: NO (DO NOT SUBMIT, slot_approved = false)`**

---

## 1. Executive Summary Across All Nine Requested Sites (`GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, 36`)

Every leaderboard score quoted in the owner prompt is labeled **`USER-REPORTED; NOT ORGANIZER-CONFIRMED`** (no authenticated organizer submission receipt exists inside these repositories). All dot counts, `[0, 1]` range checks, 3-px overlaps, and off-catalogue USGS SGMC (`1:500k` bedrock geology `>300 m` off `labels.tif`) proxy metrics below were computed directly from commit-pinned GeoTIFF bytes on `2026-10-26`.

### 1.1 Historical Highest Claims (`0.2449`–`0.2778` USER-REPORTED) — Why None Is Eligible as a New Unique Submission

| Site | Historical Top-Claimed File | Claimed Score (`USER-REPORTED`) | Dots | 3-px Overlap vs `H33-2-B2` | Status |
| --- | --- | --- | ---: | ---: | --- |
| `GEMSDOE32` | `gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` | `0.2778` | `37,654` | `100.0%` | Already submitted reference; `D2.8` minus `<=2 px` catalogue halo |
| `GEMSDOE36` | `gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif` | `0.2750` | `38,854` | `97.4%` | Duplicate of `D2.8/H33` family (`>70%`) |
| `GEMSDOE28` | `gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif` | `0.2710` | `37,660` | `95.5%` | Duplicate of `D2.8/H33` family (`>70%`) |
| `GEMSDOE31` | `gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif` | `0.2708` | `40,199` | `95.4%` | Duplicate of `D2.8/H33` family (`>70%`); also flagged in `registry/irregularities.json` |
| `GEMSDOE33` | `GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e-nanoutside.tif` | `0.2632` | `41,865` | `92.6%` | Duplicate of `D2.8/H33` family (`>70%`) |
| `GEMSDOE25` | `gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif` | `0.2600` | `44,090` | `88.2%` | Duplicate of `D2.8/H33` family (`>70%`) |
| `GEMSDOE30` | `gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca-nanoutside.tif` | `0.2600` | `44,090` | `88.2%` | Duplicate of `D2.8/H33` family (`>70%`) |
| `GEMSDOE24` | `gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif` | `0.2477` | `60,069` | `88.5%` | Duplicate of `D2.8/H33` family (`>70%`) |
| `GEMSDOE27` | `gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif` | `0.2449` | `61,328` | `86.7%` | Duplicate of `D2.8/H33` family (`>70%`) |

### 1.2 Newly Reported `2026-10-25` Unique Batch & Current `2026-10-26` `HEAD` Unique Candidates Across All 9 Sites

| Site (`HEAD` commit) | `2026-10-25` Newly Reported Unique Score (`USER-REPORTED`) | Current `HEAD` Unscored Unique Candidate (`2026-10-26`) | Dots & `[0,1]` | 3-px Overlap (`vs H33 / vs H29`) | Off-Cat SGMC (`All / Pied / Mtn`) | Site Verdict & Forensic Assessment |
| --- | --- | --- | --- | --- | --- | --- |
| **`GEMSDOE24`** (`bb1a82cf`) | `gems24-gvc1-...-abe8e51c719d-zeros.tif` -> **`0.0859`** (`36.6%` vs H33) | [gems24-rshg1-regime-hydro-hgb-20261025-98f69d77e868-zeros.tif](https://github.com/buffedlizard55-lab/GEMSDOE24/blob/bb1a82cfc9ec0a1a52abfd3e83d5962de215499a/docs/downloads/gems24-rshg1-regime-hydro-hgb-20261025-98f69d77e868-zeros.tif) | `37,722` · PASS | `42.8% / 40.3%` | `0.0785 / 0.0719 / 0.0686` | `DOWNLOAD YES / SUBMIT NO` |
| **`GEMSDOE25`** (`5d46f06b`) | `gems25-h66-mgd-flank-...-da617550a0e9-zeros.tif` -> **`0.0742`** (`30.4%` vs H33) | [gems25-h36-spigm-subsurface-submod300-20261025-3937b96ce366-zeros.tif](https://github.com/buffedlizard55-lab/GEMSDOE25/blob/5d46f06b420cc688894eb517228546950c9fa3b2/docs/downloads/gems25-h36-spigm-subsurface-submod300-20261025-3937b96ce366-zeros.tif) | `37,654` · PASS | `24.0% / 19.6%` | `0.0679 / 0.0717 / 0.0572` | `testing only — DO NOT SUBMIT` |
| **`GEMSDOE27`** (`927322ea`) | **`gems27-h29-hydrothermal-piedmont-celf-...-511898747886-allfinite.tif` -> `0.2190`** (**highest user-reported newer-batch claim; subset novelty only**, `56.1%` vs H33) | [gems27-h29-1-drefill-b2-38k-20261025-c24b6371179c-allfinite.tif](https://github.com/buffedlizard55-lab/GEMSDOE27/blob/927322eadbee909f0b006732d9c09d6e10b57239/docs/downloads/research/gems27-h29-1-drefill-b2-38k-20261025-c24b6371179c-allfinite.tif) | `38,000` · PASS | `40.9% / 36.9%` | `0.0897 / 0.0553 / 0.0838` | `H29-1` passed GEMSDOE27 holdout (`+0.0022`) & 12-peer uniqueness; awaits owner selector (`H30` failed holdout) |
| **`GEMSDOE28`** (`712570c5`) | `gems28-s18-mxtp-...-3e95505c011a-allfinite.tif` -> **`0.0217`** (`11,082` dots, budget-starved) | [gems28-s19-ascp-20261026-dc717c1ab13b-allfinite.tif](https://github.com/buffedlizard55-lab/GEMSDOE28/blob/712570c5711530e07ae00795471b08d1aa122ffd/docs/downloads/gems28-s19-ascp-20261026-dc717c1ab13b-allfinite.tif) | `37,654` · PASS | `22.5% / 19.1%` | `0.1457 / 0.0275 / 0.1569` | `DO NOT SUBMIT` (`S19` failed 1.5 km holdout `0.0808` vs `0.1417`) |
| **`GEMSDOE30`** (`781eea04`) | `gems30-MSDB1-edge44090-...-e7856ec3f14a.tif` -> **`0.1462`** (`44,090` dots, `39.2%` vs H33) | [GEMSDOE30-nearslay-annulus-d3-offcat-20261025T235837Z-662af003-nan.tif](https://github.com/buffedlizard55-lab/GEMSDOE30/blob/781eea04fb1d46056631c7fb37900f2508295325/docs/downloads/GEMSDOE30-nearslay-annulus-d3-offcat-20261025T235837Z-662af003-nan.tif) | `40,000` · PASS | `22.3% / 22.1%` | `0.0649 / 0.0846 / 0.0507` | `NOT cleared to submit` (pure `300m–1.5km` catalogue annulus) |
| **`GEMSDOE31`** (`arena/34f326b4`) | none reported | [`gemsdoe31-h31s-udap-sslic-37654-20261026-9355f21d9f-zeros.tif`](../docs/downloads/gemsdoe31-h31s-udap-sslic-37654-20261026-9355f21d9f-zeros.tif) (plus prior `H31-M` SGMC `0.1010 / 0.0641 / 0.0947`) | `37,654` · PASS | `47.4% / 55.7%` | `0.0837 / 0.0400 / 0.0784` | `RESEARCH ONLY · DO NOT SUBMIT` (`HOLDOUT-DTI` `0.0948` s41 & `0.0980` s42; blocked by literal 695-lattice STOP & s41 H31-M quad gate) |
| **`GEMSDOE32`** (`15a5fce9`) | none reported (`H33-2-B2` = `0.2778`) | [gemsdoe32-r6-stepprofile-b2-37654-20261026T002502Z-23fbbb51-zeros.tif](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/15a5fce9498fa0da87f81e80b97e2acdeeb068a7/docs/downloads/gemsdoe32-r6-stepprofile-b2-37654-20261026T002502Z-23fbbb51-zeros.tif) | `37,654` · PASS | `19.1% / 14.8%` | `0.1424 / 0.0030 / 0.1678` | Self-marked `PROMOTE` on SGMC (`0.1424`), **SEVERE RISK:** `0.0030` Piedmont SGMC & `0.0034` Quaternary holdout DTI in `round6_run_card.json` |
| **`GEMSDOE33`** (`c9a24250`) | none reported | [gemsdoe33-a33-l1-analog-transfer-research-37654-20261025-85c94a805a34-zeros.tif](https://github.com/buffedlizard55-lab/GEMSDOE33/blob/c9a24250af4a7227ba6f24921e0a2146c5013514/docs/downloads/gemsdoe33-a33-l1-analog-transfer-research-37654-20261025-85c94a805a34-zeros.tif) | `37,654` · PASS | `37.1% / 32.7%` | `0.0916 / 0.0517 / 0.0857` | `NOT OK TO SUBMIT` (lost to regional comparator) |
| **`GEMSDOE36`** (`1f92ee9c`) | none reported | [gemsdoe36-lane36-supgbm-68302-20261026T002651Z-f35cb3e4-zeros.tif](https://github.com/buffedlizard55-lab/GEMSDOE36/blob/1f92ee9c68df2a753a6e77daed2368da10b940e6/docs/downloads/gemsdoe36-lane36-supgbm-68302-20261026T002651Z-f35cb3e4-zeros.tif) | `68,302` · PASS | `33.8% / 30.1%` | `0.0746 / 0.0803 / 0.0637` | `Lane36` passed internal segment holdout (`0.1777` vs `0.1615`, `68,302` dots); repo top banner remains `NOT APPROVED` |

---

## 2. PhD-Level Forensic Analysis: Why `GEMSDOE32 H33-2-B2` Scored `0.2778` (`USER-REPORTED`), Why the `2026-10-25` Unique Submissions Separated (`0.0217`–`0.2190`), and What It Takes to Exceed `0.2778` / `0.3195` / `0.4413`

### 2.1 Exact DTI Economics of `H19-5` (`0.1922`) -> `D1.5` (`0.2477`) -> `D2.8` (`0.2600`) -> `H27-4` (`0.2708`) -> `H33-2-B2` (`0.2778`)

Under the organizer's Distance-Tolerant Intersection metric ($\alpha = 0.2$, $\beta = 0.8$, $R = 300\text{ m}$ triangular 29-cell kernel $K$, total hidden truth pixels $N_T$):

$$\text{DTI} = \frac{T}{T + 0.2\,F + 0.8\,N_T} = \frac{T}{0.2\,(T + n - M) + 0.8\,N_T}$$

Differentiating with respect to a candidate dot block $(\Delta T, \Delta F)$ around operating score $S = \text{DTI}$ shows that adding or retaining dots increases DTI if and only if:

$$\frac{\Delta T}{\Delta F} > \frac{\alpha S}{1 - \alpha S} = \frac{0.2 \times 0.2778}{1 - 0.2 \times 0.2778} = \mathbf{0.0588}$$

Byte-for-byte inspection of the `D1.5 -> D2.8 -> H27-4 -> H33-2-B2` chain reveals **three cumulative metric-alignment steps on a single supervised detector surface** (`H19-5`):
1. **Discrete `2.8 px` Poisson-disk packing (`0.1922 -> 0.2600`):** Because $\text{TP}_w$ saturates at `1.0` per truth pixel via $\min(1, \cdot)$ while $\text{FP}_w$ sums linearly across every dot without nearby truth, continuous ribbons pay `5–10x` redundant false-positive mass along the same fault trace. Spacing binary `{0, 1}` dots at `2.8 px` (`280 m`, matching $R = 300\text{ m}$) maximizes distinct trace coverage per unit $\text{FP}_w$.
2. **`B = 2` (`>200 m`) near-catalogue halo pruning (`44,090 -> 40,199 -> 37,654` dots, `0.2600 -> 0.2708 -> 0.2778`):** `H33-2-B2` is **pixel-for-pixel identical** to `D2.8` beyond `200 m` from `labels.tif` (`37,654` shared dots), deleting `6,436` near-catalogue dots (`3,891` in `(0, 100 m]` for `H27-4`, plus `2,545` in `(100, 200 m]` for `H33-2-B2`). Gaussian-smoothed features bleed `100–200 m` orthogonally across already-mapped traces where known faults are masked from truth credit, so those `6,436` flank dots yielded $\Delta T / \Delta F < 0.0588$.
3. **Why `0.2778` also marks the ceiling of pruning `D2.8`:** Further pruning (`>300 m`) begins deleting real unmapped fault-tip continuations and en-echelon relays. No reorganization of `D2.8` dots can pass the `<=70%` 3-px uniqueness rule or reach `0.3195` / `0.4413`.

### 2.2 Empirical Lesson from the Five Newly Reported `2026-10-25` Unique Submissions (`0.0217` to `0.2190` `USER-REPORTED`)

The `2026-10-25` leaderboard batch supplies a controlled natural experiment across five genuinely unique (`17.1%–56.1%` overlap with `H33`) methods:
1. **`GEMSDOE28 S18-MXTP` (`0.0217`):** Emitted only `11,082` dots (`29%` of optimal budget); under $\beta = 0.8$, starving $T$ leaves $0.8\,N_T$ dominating the denominator.
2. **`GEMSDOE25 H66-MGD` (`0.0742`) & `GEMSDOE24 GVC1` (`0.0859`):** Unsupervised geophysical/lineament heuristics. Notably, `H66` achieved **higher** raw SGMC (`0.0959`) than `H33-2-B2` (`0.0940`) yet scored `0.0742` on the leaderboard — proving that **unsupervised bedrock/pluton edges match pre-Quaternary 1:500k SGMC contacts rather than Quaternary/geothermal competition truth**.
3. **`GEMSDOE30 MSDB1` (`0.1462`):** Supervised multiscale decision-boundary classifier (`44,090` dots) — **doubling** the unsupervised arms (`0.1462` vs `0.0742–0.0859`), slightly diluted by `+6,436` unpruned tail dots.
4. **`GEMSDOE27 H29-HPVC` (`0.2190` — highest user-reported newer-batch claim; subset novelty only):** Combined **supervised OOF fault probabilities** + **hydrothermal/piedmont physics** + **exact 29-cell CELF submodular `B=2` cover at `K = 37,654`**, recovering **`78.8%` of `H33-2-B2`'s score (`0.2190 / 0.2778`) with zero copied dots (`56.1%` 3-px overlap)**.
5. **Diagnostic warning on `GEMSDOE32 R6-stepprofile` (`unscored`):** Although `R6-stepprofile` reaches `0.1424` overall SGMC (`0.1678` Mountain SGMC), our multi-regime audit shows its **Piedmont SGMC collapses to `0.0030` (`0.3%`)**, corroborating `GEMSDOE32`'s own `round6_run_card.json` where its Quaternary holdout DTI was **`0.00338`**. Unsupervised topographic step detectors overwhelmingly fire on steep bedrock canyon rims and volcanic table ledges.

### 2.3 Are We Able to Beat `0.2778` (and Close the Gap Toward `0.3195` / `0.4413`)?

- **Honest scientific answer:** No local holdout proxy (`HOLDOUT-DTI` or `SGMC-PROXY`) is numerically commensurate with private leaderboard DTI, so **no candidate may claim to beat `0.2778` before an organizer receipt exists**.
- **Physical & mathematical pathway:** Closing the gap from `GEMSDOE27 H29` (`0.2190`) to `0.2778+` requires solving the exact failure modes of raw-coordinate trees:
  1. **Dip-migration error in alluvial basins (`200–1,200 m` > `300 m` DTI kernel):** Projecting buried hanging-wall gravity HGM, basement-step, and upward-continued magnetic gradients **up-dip** back onto the surface fault subcrop (`UDAP`).
  2. **Hydrothermal magnetite destruction (`HZAD`):** Detecting axial `RTP`/`TMI_up150` troughs (`+\nabla^2_\perp`) co-located with `K/Th` potassic alteration and shallow clay-cap conductivity anomalies rather than only positive magnetic steps.
  3. **Bayes prevalence-prior calibration + 2-Stage Strike-Steered Line-Integral Continuity (`SSLIC`):** Converting class-weighted tree outputs (`62.5%` effective training prior) back to true spatial prevalence (`~1.55%`) so 2D diffuse lithologic blobs (`11.49` kernel sum) cannot out-integrate sharp 1D fault strands (`~3.0` line kernel sum) during 29-cell submodular allocation.

---

## 3. Execute-and-Verify Summary: `H31-S` (`UDAP-SSLIC`) 3-Experiment Campaign

Preregistered before execution in [`knowledge/2026-10-26_h31s_udap_sslic_preregistration.md`](2026-10-26_h31s_udap_sslic_preregistration.md) (`SHA-256 fe9464365d34d84ea2205579c50a3960ba0dc4c843c66d0519ae355e19f8de03`), reusing unchanged `vendor/gems57/evaluate_holdout.py` (`gems57-pooled-hide-v2`), `vendor/gems57/holdout.py:buffered_component_draw`, and `vendor/gems57/submission_writer.py`.

1. **Candidate-Specific OOF Residual Semivariogram (`evidence/h31s/buffer_derivation.json`):**
   - Computed from `39,992` `H31-S` OOF catalogue residuals (`2,248` 8-connected components, `500 m` bins to `60 km`, `80` component-bootstrap draws):
   - Fitted practical ranges: `exponential = 19.33 km`, `spherical = 11.41 km`, `gaussian = 5.97 km` (all three reach `>=80%` sill within the `26.25 km` populated lag support; `0` extrapolating models).
   - Non-parametric `95%`-of-peak empirical decay range: **`20.75 km` (`20,750 m`)** -> adopted `buffer_px = 213` (`21.3 km`), honoring both `H31-S`'s own measured range and the `21.3 km` `MAGREST` floor.
2. **Single-Feature & Missingness Leakage Canaries (`evidence/h31s/canaries_*.json`):**
   - Stage-1 (`50/50` features): max two-sided value AUC = **`0.6479 <= 0.90`**, max missingness AUC = **`0.5000 <= 0.90`** (`PASS`).
   - Stage-2 `SSLIC` (`7/7` features): max two-sided value AUC = **`0.6251 <= 0.90`**, max missingness AUC = **`0.5000 <= 0.90`** (`PASS`).
   - Deliberately excluded `distance_to(visible)` features (`catalogue_features_used = False`) after code inspection of `vendor/gems57/holdout.py:296` showed `visible = cat & ~(edt(~hidden) <= buffer_px)` creates an artificial `21.3 km` hole around hidden truth in holdout.
3. **3-Experiment Pooled `HOLDOUT-DTI` Progression (`gems57-pooled-hide-v2`):**

| Arm | Screen `seed=41` (`2,820` withheld px) | Screen `SGMC-PROXY` (`16,785` px) | Untouched Confirmation `seed=42` (`2,823` withheld px) |
| --- | --- | --- | --- |
| `EXP-1a: Control-Physical-HGB` (`MAGREST` baseline) | `0.05908` `[0.03507, 0.08231]` | `0.04530` `[0.02255, 0.08136]` | `0.05440` `[0.03399, 0.07976]` |
| `EXP-1b: Incumbent-H31M-Submod` (same-instrument in-repo ref) | `0.07133` `[0.04476, 0.09685]` | `0.05113` `[0.02372, 0.09150]` | `0.07176` `[0.04724, 0.09574]` |
| `EXP-2: H31-S Stage-1 (UDAP+HZAD+Nulls)` | `0.08036` `[0.05154, 0.10339]` | `0.05188` `[0.02660, 0.08676]` | *(screen-only per budget)* |
| **`EXP-3: H31-S Full (2-Stage Nested OOF SSLIC)`** | **`0.09478` `[0.06120, 0.12925]`** | **`0.06260` `[0.04094, 0.09424]`** | **`0.09796` `[0.07280, 0.12485]`** |
| Paired $\Delta$ vs `Control-Physical-HGB` | **`+0.03569` `[+0.00821, +0.06590]`** (`3/4` quads, **PASS**) | `+0.01730` `[-0.00967, +0.04287]` | **`+0.04356` `[+0.01791, +0.06951]`** (`4/4` quads, **PASS**) |
| Paired $\Delta$ vs `Incumbent-H31M-Submod` | `+0.02345` `[-0.02042, +0.06979]` (`1/4` quads, mixed) | `+0.01147` `[-0.02468, +0.04788]` | **`+0.02620` `[+0.00010, +0.05441]`** (`4/4` quads, **PASS**) |

4. **Shared-Tool & Presentation Bugs Fixed in This Session:**
   - **`scripts/audit_shared_registry_stop.py`:** Replaced raw `gh api` REST blob fetch (which failed under shared REST rate-limit exhaustion HTTP 403) with `download_competition_data._download` (git-fetch blob fallback over `https://github.com`), restoring deterministic offline/CI execution of `verify_current_run.py --restore-small-inputs`.
   - **`scripts/current_site.py`:** Fixed missing `f`-string prefix on line 389 (which leaked literal Python code `if dti_sgmc is not None else` into rendered HTML), removed duplicate consecutive `h3_download_and_gates()` sections on `index.html` and `executive-summary.html`, and removed HTML pictogram entities.

---

## 4. Official & Verified Sources for Manual Review

- **Competition overview & submission portal:** <https://www.drivendata.org/competitions/306/competition-doe-gems/>
- **Problem description & DTI metric specification:** <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/>
- **Official DOE GEMS Prize rules PDF (NREL/OSTI):** <https://docs.nlr.gov/docs/fy26osti/96647.pdf>
- **Organizer reference solution repository:** <https://github.com/drivendataorg/gems-prize-reference-solution> (verified commit `aebe92f7`)
- **USGS INGENIOUS Great Basin dataset (OpenEI GDR #1467):** <https://gdr.openei.org/submissions/1467>
- **OpenEI GDR #1391 Great Basin Play Fairway (2 m probes, paleogeothermal, volcanics):** <https://gdr.openei.org/submissions/1391>
- **USGS GeoDAWN airborne radiometric & magnetic data release:** <https://doi.org/10.5066/P9P36HQ6> / <https://doi.org/10.5066/P93LGLVQ>
- **Nine focus repositories (`2026-10-26` audited `HEAD`s):**
  - `GEMSDOE24` (`bb1a82cf`): <https://github.com/buffedlizard55-lab/GEMSDOE24>
  - `GEMSDOE25` (`5d46f06b`): <https://github.com/buffedlizard55-lab/GEMSDOE25>
  - `GEMSDOE27` (`927322ea`): <https://github.com/buffedlizard55-lab/GEMSDOE27>
  - `GEMSDOE28` (`712570c5`): <https://github.com/buffedlizard55-lab/GEMSDOE28>
  - `GEMSDOE30` (`781eea04`): <https://github.com/buffedlizard55-lab/GEMSDOE30>
  - `GEMSDOE31` (`arena/34f326b4-gemsdoe31`): <https://github.com/buffedlizard55-lab/GEMSDOE31>
  - `GEMSDOE32` (`15a5fce9`): <https://github.com/buffedlizard55-lab/GEMSDOE32>
  - `GEMSDOE33` (`c9a24250`): <https://github.com/buffedlizard55-lab/GEMSDOE33>
  - `GEMSDOE36` (`1f92ee9c`): <https://github.com/buffedlizard55-lab/GEMSDOE36>

---

## 5. Remaining Limitations & Next-Session Priorities

1. **Literal 695-Raster Lattice Degeneracy (`r13-lattice-s5` / `GEMSDOE48`):** Under `AGENTS.md`, dense continuous surfaces and spacing-5 calibration grids in the historical 695-raster manifest are not silently exempted, causing `99.93%–100%` 3-px overlap for any nonempty Nevada prediction. An explicit owner/selector protocol amendment scoping uniqueness to discrete submission candidates (`<= 100,000` dots, where `H31-S` already passes at `max = 66.5%` final-dot overlap across all 9 sites and concurrent local lanes including `XFCOH31` `40.8%`, `CONCORD31` `42.0%`, `H31-T` `46.9%`, `H31-J` `54.8%`) is required before flipping `ok_to_submit` to `true`.
2. **Stabilizing `NW/SW/SE` Fold Gains vs `H31-M`:** While `H31-S` won `4/4` quadrants against both `Physical-HGB` and `H31-M` on untouched confirmation `seed=42` (`+0.0262`, CI `[+0.0001, +0.0544]`), its `+0.0235` pooled gain over `H31-M` on `seed=41` was concentrated in `NE` (`0.1375` vs `0.0341`) with minor `-0.005` to `-0.012` deltas in the other three quadrants. Combining `H31-S`'s `UDAP + SSLIC` features with `H31-M`'s multi-scale regional magnetic/gravity tilt concordance in a future preregistered run should lift piedmont & mountain stability across all quadrants.
3. **External InSAR (`H31-U`) & 3D USArray MT (`H31-V`) Ingestion:** When running in an environment with outbound access to NASA ASF DAAC (`asf.alaska.edu`) and EarthScope/IRIS (`ds.iris.edu`), ingesting Sentinel-1 ARIA seasonal phase-gradient barriers and MT phase-tensor skew $|\beta|$ offers the strongest independent physical signal for zero-relief intra-playa geothermal faults.

---

## Prior Independent Verification Continuation — 2026-10-26 (Preserved from `main`)

This continuation re-ran the checks from `AGENTS.md` in a clean checkout after installing the pinned `requirements.txt` into ignored `.venv`. It did not change code, fit a model, create or modify a submission raster, inspect the DrivenData leaderboard, or use a slot.

- `python -m pytest -q`: **118 passed** after the exact-input verifier restored the two small pinned inputs; there were no remaining skips. The pre-restore run was 112 passed / 6 expected skips.
- `python -m ruff check .`: passed.
- `python scripts/check_metric.py`: maximum fast/brute pooled-DTI absolute difference **4.441e-16** across 24 grids; exact cases passed; 29 kernel offsets are inside the 300 m radius.
- `python scripts/verify_current_run.py --restore-small-inputs`: returned `verdict=negative`, `ok_to_download_for_research=true`, `ok_to_submit=false`; unchanged MAGREST all-finite raster SHA-256 `c101ceb7237df0890a0f650b4211cc501250b47c1ab9cfeca8ee4cb373eb48d9`.
- `python scripts/collect_evidence.py`, `build_site.py`, and `check_site.py`: reported 124 experiment artifacts, 10 submission records, and a passing generated site with 21 pages and 364 local links. The collector's unrelated generated changes to readiness/experiment registers were restored; they are not review findings.

The independent rerun confirms the prior decision, not the scientific validity of a competition score: no new TIFF is approved to submit. The all-finite research raster remains explicitly **OK TO DOWNLOAD FOR RESEARCH ONLY — DO NOT SUBMIT**. The lane still fails the literal 70% duplicate test against a registered full-footprint witness (100% forward overlap), the three-experiment cap is exhausted, and no newly assigned method paragraph is present. No user-reported leaderboard number was accessed or upgraded to ORGANIZER-CONFIRMED.
