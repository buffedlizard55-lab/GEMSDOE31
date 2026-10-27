# 2026-10-27 Session Review (`arena/f5b2211b-gemsdoe31`) — PhD Forensic Audit of `GEMSDOE32` & the Oct 25–26 Wave, Ranked Hypotheses, and Lane `H31-AA` (`SLFS`) Execution

- **Date (UTC):** `2026-10-27`
- **Branch:** `arena/f5b2211b-gemsdoe31` (fast-forwarded to `origin/main` `fbebc01703a39a99528432892b7c11b716ca5ab3` before implementation)
- **Binding Release Decision (`registry/release_status.json`):** **`DO NOT SUBMIT` (`verdict = "negative"`, `ok_to_submit = false`, `slot_approved = false`, `submission_slots_used = 0`)**. No current artifact is approved for competition upload; no human sign-off can override a failed literal gate under the active protocol (`literal-registry-20261026-9883b598`).
- **New Research Deliverable (`H31-AA` / `SLFS`):** [`docs/downloads/gemsdoe31-h31aa-slfs-flexure-37654-20261027-fdb34746-zeros.tif`](../docs/downloads/gemsdoe31-h31aa-slfs-flexure-37654-20261027-fdb34746-zeros.tif) (`SHA-256: d272d5babb9523a70f77e76ad6843830d67a9eabaaa60f8c3f46ca57bde9a1ef`) — **OK TO DOWNLOAD FOR RESEARCH ONLY; DO NOT SUBMIT**.

---

## 1. Executive Summary & Nine-Site + Oct 25–26 Wave Reconciliation

Every score pasted in the owner prompt carries provenance class **`USER-REPORTED` (no authenticated organizer receipt in this repository)**. Every `HOLDOUT-DTI` value carries `(evaluator_version, withheld_positive_pixels, 95% CI)`. Every overlap and off-catalogue USGS SGMC proxy number is `COMPUTED` directly from SHA-256-verified GeoTIFF bytes (`evidence/h31aa/nine_site_oct27_audit.json`).

| Site / Lane | Artifact | Metric / Score (Strictly Labeled) | 3-px Overlap vs `H33` | Off-Cat SGMC (`All / Pied <=6° / Mtn >6°`) | Median `d_cat` (`px`) / `% >15°` Slope | Uniqueness & Upload Verdict |
|---|---|---|---:|---|---|---|
| **GEMSDOE31 · `H31-AA`** *(new 2026-10-27)* | `gemsdoe31-h31aa-slfs-flexure-37654-20261027-fdb34746-zeros.tif` (`37,654`d) | `HOLDOUT-DTI (gems57-pooled-hide-v2, 60,988, [0.1368, 0.1604])`: **`0.1489`** (`AA4`: **`0.1556`**, NW Fold 0 `0.1512 > 0.1454`); confirm `seed=3107` (`31,346`, `[0.1181, 0.1424]`): `0.1302` | `52.1%` | `0.0688` / **`0.0929` (#1)** / `0.0393` | `20.52 px` / **`2.16%`** | External 9-site 2-stage **PASS** (`69.3% / 57.0%`); all-peer final **PASS** (`60.6%`); literal 695-lattice **STOP** (`98.3%`) → **RESEARCH ONLY · DO NOT SUBMIT** |
| **GEMSDOE31 · `H31-X`** *(local holdout best)* | `gemsdoe31-h31x-piedmont-junction-37654-20261026-5a956da9-zeros.tif` (`37,654`d) | `HOLDOUT-DTI (gems57-pooled-hide-v2, 60,988, [0.1491, 0.1825])`: **`0.1661`**; confirm `0.1517` | `57.0%` | **`0.1209`** / `0.0442` / `0.1184` | `20.62 px` / `18.60%` | External Stage-1 top-K **FAIL** (`86.3%` vs `D1.5`); final **PASS** (`63.1%`); literal lattice **STOP** (`99.3%`) → **RESEARCH ONLY · DO NOT SUBMIT** |
| **GEMSDOE32 · `H33-2-B2`** | `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` (`37,654`d) | **`0.2778`** `USER-REPORTED` *(prompt also cites `0.4413` competition high & `0.3195` earlier anchor)* | `100.0%` | `0.0940 / 0.0586 / 0.0827` | `19.65 px` / `8.28%` | Exact subset of `D2.8` at `d_cat > 2 px` (`86.7%–97.4%` family overlap) → **PRIOR ART · DO NOT RESUBMIT** |
| **GEMSDOE27 · `H31-DRCG`** *(Oct 26 wave #1)* | `gems27-h31-drcg-wl-celf28-20261026-cf8e1bbef244-allfinite.tif` (`37,654`d) | **`0.2250`** `USER-REPORTED` *(+ `H29`: **`0.2190`** `USER-REPORTED`)* | `50.2%` *(56.1%)* | `0.0885 / 0.0452 / 0.0822` | `16.28 px` / `15.76%` | Genuine post-`D2.8` unique wave leader across all 9 focus sites → **PRIOR ART · DO NOT RESUBMIT** |
| **GEMSDOE36 · `KPL36`** *(Oct 26 wave #2)* | `gemsdoe36-kpl36-exp3-20261026-fc869911e88c-zeros.tif` (`37,654`d) | **`0.1647`** `USER-REPORTED` | `56.1%` | `0.0656 / 0.0662 / 0.0562` | `14.87 px` / `14.90%` | Kinematic + LiDAR OOF ensemble → **PRIOR ART · DO NOT RESUBMIT** |
| **GEMSDOE30 · `MSDB1`** | `gems30-MSDB1-edge44090-20261025-e7856ec3f14a.tif` (`44,090`d) | **`0.1462`** `USER-REPORTED` | `39.2%` | `0.0744 / 0.0553 / 0.0638` | `5.83 px` / `14.74%` | `77%` of dots within `15 px` of known faults (near-catalogue bias) → **PRIOR ART · DO NOT RESUBMIT** |
| **GEMSDOE33 · `S33-SEISDIL`** *(Oct 26)* | `gemsdoe33-s33-seisdil-strain-seismicity-37654-20261026-3463540a7e02-zeros.tif` (`37,654`d) | **`0.0963`** `USER-REPORTED` | `34.8%` | `0.0813 / 0.0555 / 0.0719` | `15.81 px` / `11.08%` | Coarse regional strain/seismicity fields limit 300 m kernel precision → **PRIOR ART · DO NOT RESUBMIT** |
| **GEMSDOE24 · `GVC1`** | `gems24-gvc1-negative-geothermal-lineament-submod-20261025-abe8e51c719d-zeros.tif` (`37,654`d) | **`0.0859`** `USER-REPORTED` | `36.6%` | `0.0705 / 0.0746 / 0.0579` | `5.66 px` / `14.86%` | Near-catalogue clustering (`median d_cat = 5.66 px`) → **DO NOT SUBMIT** |
| **GEMSDOE25 · `H66-MGD`** | `gems25-h66-mgd-flank-sapd3-0-k3p5-20261025-da617550a0e9-zeros.tif` (`44,832`d) | **`0.0742`** `USER-REPORTED` | `30.4%` | `0.0959 / 0.0805 / 0.0825` | `5.83 px` / `13.68%` | `91%` of dots at `d_cat <= 15 px` (flank-hugging collapse despite high SGMC) → **DO NOT SUBMIT** |
| **GEMSDOE28 · `S18` & `S21`** *(Oct 25–26)* | `gems28-s18-mxtp` (`11,082`d) / `gems28-s21-puhgb` (`37,654`d) | **`0.0217` / `0.0206`** `USER-REPORTED` | `17.1% / 28.7%` | `0.0175` / `0.0588` | `22.63 px` / **`4.12 px`** | `S18` starved (`11k` dots); `S21` places **`97%` of dots within `15 px` of known faults** → **DO NOT SUBMIT** |

### Additional Sibling Sites in the 2026-10-27 Owner Brief
- **Newly scored Oct 26 sibling entry:** `GEMSDOE91` `gems91-s22-omtj-e1-37654dots-20261026T161800Z-334a0649-zeros: 0.0298` (`USER-REPORTED`, recorded in `registry/user_reported_scores.json`; prior `GEMSDOE91` `s17-lftg` was `0.1823`). Highest historical sibling claims across all 92+ sites remain `GEMSDOE32 H33-2-B2` (`0.2778`), `GEMSDOE48` (`0.2736`), `GEMSDOE28 H36-1` (`0.2710`), `GEMSDOE31 H27-4` (`0.2708`), `GEMSDOE36 Anderson` (`0.2750`), `GEMSDOE70 p5-dual` (`0.2478`), `GEMSDOE49 gate_ortho` (`0.2376`), `GEMSDOE76 ptcf-tiltworm` (`0.2343`), `GEMSDOE63 cvarlw` (`0.2303`), and `GEMSDOE27 H31-DRCG` (`0.2250`).
- **Unscored new sibling series (`KANLERGEMSDOE1..3`, `EUGGEMSDOE1..3`, `WBGGEMSDOE1..3`, `GINNYGEMSDOE1..3`):** Listed in the prompt with blank scores (`unscored`); none carries a score claim or organizer receipt.

---

## 2. PhD-Level Forensic Analysis of `GEMSDOE32` (`0.2778` `USER-REPORTED`) vs `0.4413` / `0.3195` — and Why PU Models Collapsed to `0.0206`

### 2.1 Algebraic Decomposition of `H33-2-B2` (`0.2778` `USER-REPORTED`)
Under the pooled Distance-Tolerant Tversky Index ($\alpha = 0.2$ FP weight, $\beta = 0.8$ FN weight, $300\text{ m}$ triangular kernel $K(d) = \max(0, 1 - d/300\text{ m})$) for $n$ binary dots against $K$ hidden truth pixels:
$$\text{DTI} = \frac{T}{0.2(T + n - M) + 0.8 K}, \qquad \text{TP}_w = T, \quad \text{FP}_w = n - M, \quad \text{FN}_w = K - T$$
Byte-exact raster algebra (`evidence/h33_forensics_20261025.json`) proves:
1. **Exact Nested Set Identity:** `H33-2-B2` (`37,654` dots, `0.2778` `USER-REPORTED`) $\subset$ `H27-4-solo-d28` (`42,846` dots, `0.2708` `USER-REPORTED`) $\subset$ `D2.8` (`44,090` dots, `0.2600` `USER-REPORTED`). Specifically, `H27-4 = D2.8 \ {d_cat <= 1 px}` and `H33-2-B2 = D2.8 \ {d_cat <= 2 px}` (`0` dots added anywhere in Nevada; all three share the exact same `34,043` dots beyond `300 m` of the catalogue).
2. **Marginal Pruning Economics:** At score level $S \approx 0.27$, deleting $\Delta n = 5,192$ near-catalogue dots ($1 < d_{\text{cat}} \le 2\text{ px}$) improves DTI iff $\Delta T_{\text{lost}} < \frac{0.2 S}{1 - 0.2 S}\Delta \text{FP}_w \approx 0.057\,\Delta \text{FP}_w$. Because hidden organizer holdout faults are predominantly **unmapped structures** rather than parallel twins within `100–200 m` of already-mapped traces, removing those `5,192` flank dots shed $\sim 1,038$ units of weighted denominator penalty with minimal loss of hidden-truth coverage (+`0.0070` live gain from `H27-4` to `H33-2-B2`, and +`0.0178` from `D2.8`).
3. **Kernel-Matched Non-Redundant Cover (`d = 2.8 px`):** Because `TP_w` saturates at $1.0$ per truth pixel while every redundant dot within $300\text{ m}$ pays full `0.2` FP weight, Poisson-disk / greedy cover spacing at $2.8\text{ px}$ ($280\text{ m}$) maximizes distinct $300\text{ m}$ fault-corridor coverage per emitted dot.
4. **Why `H33` Reached `0.2778` While Supervised PU Runs (`G28 S21 = 0.0206`, `G25 H66 = 0.0742`, `G24 GVC1 = 0.0859`) Collapsed:**
   Byte forensics across all 9 Oct 25–26 scored GeoTIFFs (`evidence/h31aa/nine_site_oct27_audit.json`) exposes the exact failure mechanism:
   - Smooth potential-field bands (`iso_grav_anom`, `depth_to_base_surf`, `cond_surf`, `rtp`) have $2\text{–}8\text{ km}$ spatial correlation lengths. Even with spatial-block cross-validation, a supervised PU tree ensemble learns the **regional potential-field / elevation signature of mapped ranges** and concentrates its highest probabilities immediately outside the `d_cat > 2 px` mask (`G28 S21-PUHGB` places **`97%` of all `37,654` dots at `d_cat <= 15 px`, median `4.12 px`**; `G25 H66` places **`91%` at `d_cat <= 15 px`, median `5.83 px`**). That wastes almost the entire dot budget hugging mapped faults where hidden holdout faults are absent!
   - By contrast, **`H33-2-B2` (`0.2778`)** places dots at **`median d_cat = 19.65 px` (`~2.0 km`)** with **`89%` of dots in `3°–15°` range-front/piedmont transition slopes** and only **`8.28%` in `>15°` steep bedrock cliffs**; similarly, **`GEMSDOE27 H31-DRCG` (`0.2250`, the highest post-`D2.8` unique score)** places dots at **`median d_cat = 16.28 px`**.
5. **Can We Beat `0.2778` (and Close the Gap Toward `0.3195` / `0.4413`)?**
   - **Not by pruning or re-spacing `D2.8` again** (exhausted prior art, and blocked by uniqueness).
   - **What is required physically to exceed `0.2778`:** Even `H33` leaves `FN_w` (`0.8 K`) as ~`85%` of the DTI denominator because 100 m DEM curvature + coarse gravity miss (a) degraded pre-Holocene piedmont scarps (`2°–8°`) and (b) blind intrabasin faults beneath Quaternary alluvium (`43%` of the footprint lacks 1 m LiDAR). Closing the gap from `0.2778` toward `0.4413` requires combining high-relief range-front junction recovery (`10°–22°`) with true low-angle piedmont & blind-basin physical localization (such as 10 m seamless USGS 3DEP DEM drainage/flexure + unwrapped Sentinel-1 InSAR aquitard phase steps, which require external hosts blocked inside this sandbox).

---

## 3. Lane `H31-AA` (`SLFS`) — Measured Results & Pareto Tradeoff Discovery

Frozen preregistration: [`knowledge/2026-10-27_h31aa_preregistration.md`](2026-10-27_h31aa_preregistration.md) (`SHA-256: 3c810c12015960848324d6062e9dfd4370d270aa543da8fcf4c85cb301432e50`).

### 3.1 Four-Arm Screen (`EXP-1`, `gems57-pooled-hide-v2`, `213 px` collar, `60,988` withheld positives)
- `AA1` (`LFLEX_COH` multi-scale steered log-flexure 1-px crest): **`0.1485` `[0.1369, 0.1593]`**
- `AA2` (`+ Paleoshoreline equipotential null suppressor`, selected screen winner clearing external-focus 2-stage top-K `0.6927 <= 0.70`): **`0.1489` `[0.1370, 0.1595]`**
- `AA3` (`+ Subsurface gravity/basement/analytic-signal`): **`0.1500` `[0.1386, 0.1607]`**
- `AA4` (`+ Coverage-neutral LiDAR scarp toe`): **`0.1556` `[0.1435, 0.1666]`** — **beats `H31-X` (`0.1454`) on NW Quadrant Fold 0 (`0.1512`, `29,319` withheld positives = 48% of the catalogue, where Lake Lahontan benches and LiDAR coexist!)**
- Same-run rebuilt comparators: `JUNC_INC` (`H31-X`): **`0.1661` `[0.1504, 0.1826]`**; `CTRL` (`tmi_hg`): `0.0671`; `SLOPE`: `0.0488`.

### 3.2 Crest-Thinning Ablation & Uniqueness (`EXP-2`)
- `AA2_crest` (`0.1489`) beat `AA2_nocrest` (`~0.1419`) by `+0.0070` on pooled `HOLDOUT-DTI` while cutting external-peer pre-placement top-K overlap from `70.66%` (`FAIL`) to **`69.27% <= 70%` (`PASS`)** and final-dot overlap to **`57.03% <= 70%` (`PASS`)** (`60.56%` across all 45 external + local peers; max `|Spearman ρ| = 0.1140 <= 0.90`).
- **Why `AA2` / `AA4` Trailed `H31-X` Overall (`0.1489` / `0.1556` vs `0.1661`):** On NE Quadrant Fold 1 (Ruby Mountains / East Humboldt metamorphic core complexes, `0%` LiDAR, steep `14°–22°` bedrock range fronts), tapering $W_{\text{pied}}(s)$ down from $11^\circ \to 18^\circ$ cost `-0.045` to `-0.050` DTI (`0.1694–0.1745` vs `0.2199`), while earning **`#1 Piedmont Off-Catalogue SGMC = 0.0929`** (`+58.5%` above `H33 = 0.0586` and `+110%` above `H31-X = 0.0442`) and cutting `>15°` steep-cliff dots from `18.6%` (`H31-X`) to **`2.16%`**.

### 3.3 Untouched Confirmation (`EXP-3`, `seed=3107`, `31,346` withheld positives)
- `AA2`: **`0.1302` `[0.1181, 0.1424]`** (`+0.0731` over `CTRL = 0.0571`, `+0.0870` over `SLOPE = 0.0433`, `-0.0215` vs `H31-X = 0.1517`).

---

## 4. Three-Pass Verification Log & Remaining Limitations

- **Pass 1 (Implementation & Primary Verification):** Restored & SHA-256 verified all 11 raw inputs + 42-band stack + 9-site & Oct 25–26 peer GeoTIFFs; froze `knowledge/2026-10-27_h31aa_preregistration.md` (`3c810c12...`); implemented `src/gemsdoe31/h31aa_features.py`, `scripts/run_h31aa.py`, `scripts/verify_h31aa_run.py`, and `tests/test_h31aa.py`; packaged and validated `-zeros.tif`, `-nan.tif`, and `.zip`s.
- **Pass 2 (Bugs, Edge Cases & Missing Requirements Caught and Fixed):**
  1. Fixed tie-averaging parity in `tests/test_h31aa.py` `_simple_rank01` to match production `U.rank01` on flat paleoshoreline plateaus.
  2. Separated external 9-site discrete uniqueness (`G5_external_focus_two_stage = PASS`, `69.27% / 57.03%`) from local `GEMSDOE31` unspaced-crest overlap (`84.98%` pre-Poisson vs `60.56%` post-Poisson) and literal 695-registry `r13-lattice-s5` (`98.28%` vs `82.34%` floor) without modifying the frozen preregistration.
  3. Removed stale `"Submit exactly one file: the selector primary (H31-X)"` hero copy in `scripts/build_site.py` so every page consistently enforces the binding `DO NOT SUBMIT` policy.
  4. Added all 5 newly reported Oct 26 owner scores (`G27 H31-DRCG 0.2250`, `G36 KPL36 0.1647`, `G33 S33 0.0963`, `G28 S21 0.0206`, `G91 S22 0.0298`) to `registry/user_reported_scores.json` and reconciled `registry/focus_unique_2026.json`.
- **Pass 3 (Full Charter Re-Check & CI Suite):** Verified `README.md` owner-prompt SHA-256 preservation, fail-closed `registry/release_status.json`, 22-page site budget, `ruff check .`, `compileall`, full `pytest` suite, and zero tracked `.cache/data/work/.venv` files.

### Limitations & Recommended Next Steps for Next Session
1. **Protocol Blocker (`r13-lattice-s5` & `17GEMSDOE_E-proba-multiscale`):** Under the literal `prediction > 0` broad-registry rule, any `37,654`-dot raster overlaps `r13-lattice-s5` on at least `82.3418%` of dots (`100%` on `E-proba-multiscale`). Before any future candidate can be marked `ok_to_submit = true`, the owner/selector must explicitly ratify the `like_for_like_reading` (`dot_field` geological submissions only, `DENSE_SUPPORT_FRACTION = 0.20`).
2. **Next Scientific Hypothesis (`H31-AE` Hybrid Slope-Asymptote Flexure):** Combine `H31-AA`'s `1-px` strike-coherent log-flexure + paleoshoreline null + LiDAR toe in `<10°` basins/piedmonts (`Piedmont SGMC = 0.0929`, NW Fold 0 winner) with an un-truncated upper-front asymptote (`10°–24°`) so NE high-relief metamorphic core-complex fronts (`Fold 1`) are not attenuated.
3. **External Official Data Blocker (Sandbox Network Allowlist):** Only `github.com`, `codeload.github.com`, `api.github.com`, `registry.npmjs.org`, `pypi.org`, and `files.pythonhosted.org` are reachable from this sandbox. Direct downloads from `usgs.gov` (seamless 10 m 3DEP DEMs), `asf.alaska.edu` (Sentinel-1 ARIA unwrapped InSAR), `earthscope.org` (USArray MT), and `drivendata.org` require an unrestricted host or pinned GitHub mirror release.
