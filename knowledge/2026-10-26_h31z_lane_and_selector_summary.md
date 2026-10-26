# H31-Z lane + selector decision summary — 2026-10-26 (session 15e685db)

Author: automated research session on branch `arena/15e685db-gemsdoe31`. Preregistration:
`knowledge/2026-10-26_h31z_preregistration.md` (frozen pre-fit, sha256
`61ba7bee44bb9213c6f06070cf2adfce62f9f7e2646203fd31e3d51848b0b0c0`). Owner prompt preserved in
README and `knowledge/owner_prompt_2026-10-26_session_15e685db.md`.

Every number below carries its evidence class. HOLDOUT-DTI = local catalogue-segment holdout
(`gems57-pooled-hide-v2`, whole fault segments hidden with 21.3 km buffer, pooled DTI with
alpha 0.2 / beta 0.8 and the 300 m triangular kernel). COMPUTED = re-read from committed bytes.
PROJECTION = TPw-affine model calibrated to USER-REPORTED anchors; never a score.
ORGANIZER-CONFIRMED = none exist in this project; no organizer receipt has ever been captured.

## 1. What was done

H31-Z ("regime max-union") tested whether catalogue-missing faults express through different
physics per physiographic regime, so a pixel should score well if ANY regime line fires:
winner Z2-coh = element-wise max of footprint percentile ranks of (a) JUNC, the H31-X
range-front junction line rebuilt in-run, and (b) SCARPX, a new structure-tensor-coherence-
weighted LiDAR scarp line (`sigma_g=1.0`, `sigma_t=2.5`, coherence floor 0.25). A third arm
(Z3) added a gravity line; it diluted and lost. Exactly 3 preregistered experiments ran
(screen, coherence ablation + uniqueness, untouched-split confirmation); no further tuning.

## 2. Results (line-by-line, all HOLDOUT-DTI unless stated)

- Reproducibility: rebuilt JUNC = 0.16613 vs H31-X card 0.1661 (deviation 3.3e-05) — the
  instrument and rebuild are verified.
- Screen (n = 60,988 withheld positives): JUNC 0.16613; **Z2-coh 0.16210 [0.1463, 0.1778]**;
  Z3 0.1522; SCARPX alone 0.1269 (a strong new single line); CTRL 0.0671; GRAV 0.0653;
  SLOPE 0.0488. Paired delta Z2-JUNC = -0.0040 [-0.0112, +0.0030] — a statistical tie.
- Coherence ablation: with coherence 0.1621 vs without 0.1276 — the structure-tensor term is
  the load-bearing part of SCARPX.
- Confirmation on an untouched random-component split (seed 3105, n = 30,484): Z2 0.1388,
  JUNC 0.1438, CTRL 0.0621; delta vs CTRL excludes 0; delta vs JUNC -0.0050 [-0.0131, +0.0027].
- Leakage canary: PASS (max single-feature two-sided AUC 0.76 < 0.90).
- Off-catalogue USGS-SGMC proxy (COMPUTED, not hidden truth): Z2 0.1151 > H33 0.0940, but
  H31-X remains higher (0.1209). The regime story is partially falsified: SCARPX tops are
  mountain scarps (mountain SGMC 0.1178), not piedmont features (piedmont 0.0278, worse than
  H31-X 0.0433 and H33 0.0586). The gravity line is weak (holdout = CTRL; off-SGMC AUC 0.439).
- Uniqueness (discrete peers = 9 focus sites + all local downloads): surface top-K 61.99% and
  final dots 60.55% within 3 px (limit 70%), max |Spearman| 0.463 on dots (limit 0.90).
  H31-Z is the only recent lane passing BOTH stages (H31-X top-K 86.3% fail; H31-Y 90.5% fail).
- Lane verdict: **negative**, solely because lane gate G3 required beating the rebuilt JUNC
  incumbent; G1/G2/G4/G5/G6 pass. PROJECTION 0.3374 [0.3318, 0.3429] (never a score).
- File (independent verifier PASS, `evidence/h31z/independent_verification.json`):
  `gemsdoe31-h31z-maxunion-37654-20261026-ded3fee9-zeros.tif`, 37,654 dots, sha256
  `e79f17ff5fab297e27e4e3793a4ec9ea55fe470804e2beaf5bd18f0e911304b0`; all values in {0,1},
  no NaN in footprint, EPSG:32611 3730x3292 grid/CRS/transform match; min dot spacing
  2.828 px; min catalogue distance 2.236 px. The portal error "Predicted values must be in
  range [0, 1]" cannot occur with this all-finite file.

## 3. Answers to the owner's central questions

**Why did GEMSDOE32 H33-2-B2 reportedly score 0.2778?** Byte-level forensics (COMPUTED,
prior sessions, re-verified): H33-2-B2 = the D2.8 dot field with all dots within 2 px of the
public catalogue deleted. It contains no new geological detector. Under the DTI kernel,
truth credit saturates at 1 per truth pixel while redundant nearby dots keep adding
false-positive mass, so sparse spacing plus catalogue-flank deletion can raise DTI without
any new discovery. The 0.2778 itself is USER-REPORTED: no exact-byte organizer receipt
exists in this project, and the H33 archive labels the file unscored.

**Can we generate > 0.2778?** Not established by any local measurement. H31-Z ties the best
incumbent geometry on the leakage-controlled holdout, beats the H33 pattern on the SGMC
proxy, and is unique at both registry stages; its PROJECTION (0.337) exceeds 0.2778 but a
projection is never a score. Only an organizer receipt can answer this question.

**The cited 0.3195 and 0.4413.** Both are USER-REPORTED, mutually inconsistent as "the
highest", and have no receipts here. They are not used as targets for any gate.

## 4. Selector decision (`registry/selector_decision_20261026.json`)

Frozen selector gates G1-G6 were re-run over 19 lanes
(`evidence/selector_audit_20261026_session15e685db.json`): promoted H31-Y, H31-Z, H31-T,
H31-J, H31-M. Two irregularities required an explicit amendment layer
(`scripts/selector_decision_protocol.py`), recorded in the decision JSON:

1. The frozen G5 checks final dots only. Its primary by PROJECTION, H31-Y, has a
   pre-placement surface top-K overlap of 90.5% on its own card — a duplicate under the
   owner's two-stage rule ("use both tests at both stages"; frozen pre-results as Reading B
   in the H31-Z preregistration section 2). H31-X likewise fails stage 1 (86.3%).
   H31-T/J/M have no stage-1 measurement on record and fail closed.
2. H31-X's frozen-G5 failure (70.30% vs 70% limit) occurs only against this session's
   derivative lane H31-Z; against the registry as it stood at its selection its max was
   63.05%. Disclosed so the demotion is not misread as evidence against the incumbent.

Under Reading A (earlier sessions: surface check = rank-correlation only) the frozen
primary H31-Y would stand. The owner may direct Reading A; the decision then reverts to the
preserved frozen output (`evidence/selector_decision_frozen_only_session15e685db.json`).
Under the applied Reading B, **primary = H31-Z**, approved for submission with conditions:
owner verifies the DrivenData weekly cap (this project spent 0 slots and cannot observe the
quota); PROJECTION never presented as a score; approval reverts to STOP under the literal
broad-registry reading (the registered spacing-5 lattice defeats every grid-conforming
candidate — witness preserved in the run card); lane verdict for H31-Z remains negative.

Governance irregularity flagged for the owner: successive sessions have alternated between
selector approvals (f4d7fb29) and literal-STOP denials (9883b598) over the same lattice
witness. This decision keeps all three documents linked and states exactly which scope is
in force; a single standing owner ruling on the lattice scope would end the oscillation.

## 5. Official sources (verified links for manual review)

- Competition: <https://www.drivendata.org/competitions/306/competition-doe-gems/>
- Reference solution: <https://github.com/drivendataorg/gems-prize-reference-solution>
- Rules (NLR): <https://docs.nlr.gov/docs/fy26osti/96647.pdf>
- INGENIOUS (GDR 1391): <https://gdr.openei.org/submissions/1391>
- USGS GeoDAWN: <https://www.usgs.gov/> (GeoDAWN lidar/geophysics, northern Nevada)
- This repository's pinned evidence index: `registry/` and `evidence/` directories.

Non-GitHub pages cannot be re-fetched from this sandbox (host allowlist: github.com,
registry.npmjs.org, pypi.org); links are provided for the owner's manual verification and
no claim in this document depends on their live content.

## 6. Limitations

- No organizer-confirmed score exists for any file; all leaderboard values are
  USER-REPORTED. PROJECTION is calibrated in-family to those reports (LOO RMSE 0.0028 is
  optimistic for genuinely distinct dot patterns).
- HOLDOUT-DTI measures rediscovery of withheld catalogue segments, not discovery of
  unmapped faults; the SGMC proxy is itself an incomplete map. Both are proxies for the
  hidden truth, which is unobservable here.
- DrivenData is login-walled from this environment: weekly cap, current leaderboard and
  organizer acceptance cannot be verified automatically. Upload remains a manual owner act.
- Sandbox compute is 2 cores / 3.8 GiB; experiments were budgeted accordingly (3 frozen).
- The piedmont-regime hypothesis was partially falsified (section 2); Lahontan shoreline
  benches remain a named non-fault mimic that no current layer vetoes.

## 7. Next work (ranked)

1. Submit H31-Z (owner, one slot) and record the organizer receipt byte-exactly — this
   converts the central unknown (>0.2778?) into evidence and recalibrates the projection.
2. SUP-J (pre-registered sketch in H31-Z preregistration future work): supervised
   regime-line stack with the same holdout; only if it beats 0.1661 pooled should it be
   considered for a slot.
3. Piedmont-specific detector with an elevation/strandline veto for Lahontan benches
   (needs a strandline elevation layer; free official source: USGS 3DEP 1 m DEM where
   available — not fetchable from this sandbox, owner-side download required).
4. Standing owner ruling on the literal-vs-discrete registry scope to end governance
   oscillation (see section 4).
