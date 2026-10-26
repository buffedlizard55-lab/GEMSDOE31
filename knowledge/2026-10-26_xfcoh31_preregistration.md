# XFCOH31 preregistration (2026-10-26, before any fit in this lane)

Lane (assigned method): **Cross-field gravity–magnetic edge-transfer coherence.**
Layers: `rtp`, `tmi`, `iso_grav_anom`, `depth_to_base_surf` (+ the 19-band base stack as control context).
Physical signature: a buried fault juxtaposes basement units, so the magnetic (RTP) edge and the
isostatic-gravity edge are *coherent but laterally offset by 1–3 px and share gradient orientation*,
with edge terminations/step-overs. Features: gradient magnitudes at sigma 1.5/3 px for RTP/gravity/
basement-depth; same-pixel min-gradient coherence; offset coherence = max over the 8 shifts at
distance 2 px of min(z-grad RTP shifted, z-grad gravity) minus same-pixel coherence (clipped >= 0);
orientation agreement |cos(delta gradient angle)|; RTP x depth coherence.
Why catalogue-missing faults: a fault with no topographic scarp and no mapped trace can still offset
basement density/magnetisation; catalogue traces were mapped mainly from surface/geologic evidence.
Named non-fault mimic: unfaulted pluton margins / basin-fill lithologic contacts shared by both fields;
survey levelling seams. 
Novelty vs repo: prior arms used scalar amplitude/derivative/tilt products, unions and submodular
selection on existing surfaces (H31-M/H31-E/HVDC/MAGREST/TGJ31). No prior arm used *shifted cross-field
edge-offset coherence* as features. Not a copy of any D28/H27/H33 dot field: dots are emitted de novo
from the fitted surface.
Control: same HGB, folds, sampling and emitter, 19 base bands only.
Holdout: `gemsdoe31.holdout.fold_split` (whole components, quadrants, 21.25 km inherited collar —
disclosed, not re-derived), visible faults masked pixel-exactly, pooled DTI alpha=0.2 beta=0.8
300 m triangular kernel (`gemsdoe31.metric`), paired block bootstrap.
Canary: every novel feature alone, AUC vs withheld truth per fold pooled by sampling; AUC > 0.90 = STOP.
Uniqueness gate (vs genuine submissions only): Spearman |rho| <= 0.90 on the pre-placement surface and
<= 70% of final dots within 3 px of any one genuine focus-site submission raster
(GEMSDOE24/25/27/28/30/31/32/33/36 best files, pinned in evidence/nine_site_forensic_audit.json).
Irregularity disclosed in advance: the registry also contains a spacing-5 *calibration lattice*
(non-submission control) that covers the interior so any dot is within 3 px of it; applying the literal
rule to calibration controls is degenerate (documented in registry/submissions.json as
UNIVERSAL_DEGENERACY_DISCLOSED). It is reported separately, not used as a submission comparator.
Emission: ridge NMS + score-ordered Poisson thinning, min separation 2.8 px, budget 37,654 dots,
catalogue pixels and their 2-px halo excluded (mechanism learned from the b2 natural experiment;
dots themselves are new). Budget: <= 3 experiments (canary+holdout counts as EXP-1/2, final fit EXP-3).
Promotion gate: candidate HOLDOUT-DTI must beat the same-run base control (paired CI reported);
otherwise verdict=negative and the TIFF is labelled DO NOT SUBMIT. A format pass alone never promotes.
Primary file: all-finite zeros-outside float32 (fixes the "Predicted values must be in range [0, 1]"
class: no NaN/sentinel anywhere); NaN-outside twin also written for the official-wording convention.
