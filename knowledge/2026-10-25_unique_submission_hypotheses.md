# GEMSDOE31 — 3–5 Untried Geological Hypotheses for a Unique TIF Submission

**Session:** 2026-10-25 · Branch `arena/ad2e4792-gemsdoe31` · Lane: new unique-submission lane
**Goal:** Generate a unique GeoTIFF submission distinct from every raster in the 716-entry shared registry,
beating the GEMSDOE32 H33-2-B2 user-claimed 0.2778 (USER-REPORTED, no organizer receipt).
**Constraint:** Parallel-Run Protocol — stop if rank-correlation > 0.90 or > 70% of dots within 3 px of any
registry raster. AUC > 0.90 on any single feature = leakage STOP.

---

## How the current best (H33-2-B2, 0.2778 user-claimed) likely works

Forensic analysis (`evidence/nine_site_forensic_audit.json`, `pass-13-2026-10-25-prior-art-and-hypothesis-gate`)
shows H33-2-B2 (37,654 dots) = H27-4 D2.8 (40,199 dots) minus 2,545 flank dots in the 100 m < d(catalogue) <= 200 m
annulus — i.e. D2.8 dotted ridges with catalogue-flank pruning. The metric rewards nonredundant 300 m triangular-kernel
coverage, not thick rerendered predictions. Thin dots on off-catalogue fault traces therefore outperform thick,
redundant, on-catalogue fills. The 0.2778 figure remains USER-REPORTED with no organizer receipt linked to exact
bytes; GEMSDOE32 owner metadata says UNSCORED. It is an analytical target, not a verified baseline.

---

## Hypothesis 1 (Rank 1 — top candidate): Antislope LiDAR scarp + radiometric K–Th alteration edge

**Layers:** `upface_max`, `downface_max` (LiDAR, 12 bands); `K`, `Th` (GeoDAWN radiometric, u8)
**Physical signature:** Coincidence of (a) an uphill-facing topographic scarp (fault-face antislope signature, road-cut/terrace-riser mimic suppressed because anthropogenic steps face downslope) AND (b) a potassium-thorium contrast edge (hydrothermal clay alteration halo around a fault, visible as K depletion / Th enrichment at the fault margin). Dot emission on pixels strong in both domains, >2 px from visible catalogue faults.
**Why it catches catalogue-missing faults:** The USGS/INGENIOUS catalogue maps faults from surface geologic expression. Blind, young, or poorly exposed geothermal faults may show no mappable geologic trace but still displace topography subtly (antislope scarp) and host alteration halos (K–Th contrast). A fault needs only one strong domain plus moderate support in the other, so neither LiDAR gaps (24.6% no coverage) nor radiometric smoothing alone kills it.
**How it differs from repo:** AS-1 lane uses LiDAR antislope alone (`knowledge/2026-10-25_lane_hypotheses.md`, E1/E2). H31-M uses 8 geophysical channels but fails the 695-raster registry STOP. HVDC uses a 38-band HGB. No existing lane fuses exactly two low-cost layers (antislope + K–Th edge) into a thin dotted emission. Nothing in the 716-raster registry is this exact two-domain conjunction.
**Expected ΔDTI:** +0.02 to +0.06 over the AS-1 antislope-only surface on the holdout (conservative); implementation cost: LOW (~100 lines, all data already restored, no new downloads).
**Validation:** Run single-feature leakage canary (K–Th edge and antislope separately, AUC must be <= 0.90), then pooled holdout DTI vs AS-1 incumbent on the same folds/buffer.

---

## Hypothesis 2 (Rank 2): Gravity-tilt-zero lineament + Curie-depth edge (basement fault reactivation)

**Layers:** `iso_grav_anom`, `iso_grav_anom_hg`, `iso_grav_anom_slope`, `rtp` (magnetic); `depth_to_base_surf`
**Physical signature:** Zero-contour of gravity tilt derivative (basement step / density contrast) intersecting a RTP magnetic bandpass edge (magnetite destruction at hydrothermal alteration front); depth-to-base gradient marks brittle-ductile transition reactivation.
**Why it catches catalogue-missing faults:** Catalogue faults are upper-crustal, surface-mapped. Basement-involved reactivation faults may not break young cover but localize geothermal flow at depth; gravity tilt-zero + RTP edge marks the subsurface structure directly.
**How it differs:** H31-M tested gravity tilt-zero + RTP bandpass as part of an 8-channel bundle that failed registry STOP. This hypothesis uses only those two channels in a minimal conjunction, keeping the dot set small and spatially distinct from the dense lattice controls.
**Expected ΔDTI:** uncertain (+0.01 to +0.04); cost: MEDIUM (requires directional derivative computation, no new data).
**Validation:** Canary first; holdout only if canary passes.

---

## Hypothesis 3 (Rank 3): Hydrothermal sinter / spring proximity via GDR volcanics + 2 m probe density

**Layers:** `derived_gdr_volcanics_100m_u8`, `derived_gdr_2m_probes_100m_u8`, `derived_gdr_paleo_100m_u8` (GDR 1391)
**Physical signature:** Proximity to mapped Quaternary volcanics and geothermal gradient probes (direct fluid-path markers); dots placed at the *edge* of the probe/volcanic envelope (not the center), where faults focus flow to the surface.
**Why it catches catalogue-missing faults:** GDR volcanics/probes record where geothermal fluid actually reached the surface — direct evidence of active fault permeability. Many such structures are unmapped in the USGS catalogue because they are young, small, or concealed by alluvium.
**How it differs:** No existing lane uses GDR volcanics/probes as the primary emission domain. GDR layers exist in the restored data but were not used as a fault-emission hypothesis in any executed lane.
**Expected ΔDTI:** uncertain (+0.00 to +0.03); cost: LOW (data restored, simple distance transform).
**Data check:** All three GDR layers restored and verified (`data_restore.json all_verified=True`). Viable without new downloads.
**Validation:** Canary + holdout on available proxies.

---

## Hypothesis 4 (Rank 4): Quaternary fault (SGMC v2) stepover / relay-ramp dilation zones

**Layers:** `derived_gdr_qfaults_v2_100m_u8` (GDR Quaternary faults); `step_max`, `lappos_max` (LiDAR curvature)
**Physical signature:** Dilational stepovers and relay ramps between Quaternary fault segments (high curvature, positive Laplacian) — structural sites where geothermal fluids pond and surface expressions cluster.
**Why it catches catalogue-missing faults:** The catalogue maps fault *traces*, not the dilational *jogs between* traces. Relay-ramp damage zones are high-permeability geothermal conduits often absent from regional fault maps.
**How it differs:** Existing lanes dot on fault traces (D2.8, H33) or scarps (AS-1). No lane targets the *between-segment* structural dilation zones specifically.
**Expected ΔDTI:** uncertain (+0.00 to +0.02); cost: MEDIUM (requires segment-gap analysis).
**Data check:** GDR QF faults restored; LiDAR curvature bands available.

---

## Hypothesis 5 (Rank 5): Topographic openness × radiometric TMI-up150 conjugate pair

**Layers:** `geod_2ndinv` (DEM second invariant / openness), `TMI_up150` (total magnetic intensity upward continued 150 m)
**Physical signature:** Convex-up topographic openness (ridge/crest) co-located with deep-sourced magnetic anomaly (basement fault offsetting magnetic basement); the conjugate pair suppresses shallow non-fault topography and shallow magnetic noise.
**Why it catches catalogue-missing faults:** Deep magnetic basement offsets mark faults that may not break cover; openness filters to ridge crests where fault-related uplift is expressed. The combination is label-free and uses bands no lane has paired.
**How it differs:** `geod_2ndinv` and `TMI_up150` exist in the 42-band stack but have not been paired as a two-band emission surface in any executed lane.
**Expected ΔDTI:** uncertain (+0.00 to +0.02); cost: LOW.
**Validation:** Canary + holdout.

---

## Selection for this session

**Top candidate: Hypothesis 1 (antislope scarp + K–Th alteration edge).**
Reason: lowest implementation cost, all data already restored, clean novelty boundary vs AS-1, and the two-domain conjunction is the most likely to produce a spatially distinct dot set (low registry overlap) while targeting faults the catalogue misses.

**Decision rule:** Proceed to holdout validation only if (a) single-feature canary AUC <= 0.90 for both layers, and (b) the combined surface's holdout DTI beats the AS-1 antislope-only incumbent on the same spatial folds. If either fails, record a negative run card (negative results are deliverables) and do not touch a submission slot.

---

## Run card fields to complete after validation

- hypothesis: H1-antislope-KTh-edge
- mechanism: antislope LiDAR scarp AND K–Th radiometric contrast edge conjunction
- non_fault_mimic: road cuts / terrace risers (antislope), dry-lake-playa mineral crusts (K–Th)
- holdout_dti: HOLDOUT-DTI (evaluator, withheld positives, 95% CI)
- correlation/overlap_vs_registry: max |rho|, max 3-px overlap vs 716-raster registry
- raster_sha256: of the generated TIF
- validator_output: no NaN inside footprint, values in [0,1], CRS/shape/transform match
- submission_name + note (<=140 chars)
- verdict: promote / negative