# Repository review — 28 October 2026 (`arena/41e3ba3f-gemsdoe31`)

## Decision

**DO NOT SUBMIT. No artifact is approved.** This review generated **no TIFF**, ran **no scientific experiment**, selected **no candidate or weekly slot**, and did not access or submit to DrivenData. The newest existing scientific artifact is H31-CC from a prior session; it remains a research file only. Its scientific score receipt is cited, not replayed here, and its final dots independently reproduce a literal registered-raster STOP.

The requested single-method paragraph is absent. Do not self-assign another method lane. The current registered spacing-5 witness also fails the literal overlap rule for the existing 37,654-dot H31-CC file. No density change or comparator exemption is permitted. **A new-file leaderboard estimate is unavailable.**

This review found and corrected a status-presentation mismatch: the site front door showed H31-CC as the newest research artifact while the canonical release status still described the older H31-X review. The current release status now audits H31-CC's existing bytes and preserves the same negative decision; the previous H31-X status is archived byte-for-byte at [`evidence/release_status/release-status-2026-10-26-bf9d261d.json`](../evidence/release_status/release-status-2026-10-26-bf9d261d.json). The H31-X review and historical run cards remain unchanged.

## Current H31-CC artifact — exact-byte read-back

| Item | Verified result |
|---|---|
| Existing file | [`gems31-h31cc-basement-step-37654d-20261028-zeros.tif`](../docs/downloads/gems31-h31cc-basement-step-37654d-20261028-zeros.tif) — generated in the previous H31-CC session, not this review |
| SHA-256 | `0e82a9e8b80052d0bc61e8f550b2ac5204d012ab1f53fb2208051f285f10ad44` |
| Companion NaN-outside TIFF | `da2a1d708ee138e9586e59de9c5562756b793aa66cbd18e61c3f0b03049f0d11` |
| Single-TIFF ZIP | `912adee9ca4f98ff102bef72849a9e71ea4600cc9f17240d9ca0b7089a323505` |
| Grid and values | **COMPUTED, owner-mirror comparison:** one float32 band, EPSG:32611, 3730×3292, exact pinned affine transform; 37,654 binary positives; no positives on the pinned public catalogue; all-finite twin is finite in [0,1] and the companion is NaN outside the sample footprint |
| Spacing | **COMPUTED:** nearest emitted-dot spacing 2.828427 px, greater than the frozen 2.8 px minimum |
| Pair of ZIP/TIFF bytes | **COMPUTED:** ZIP contains exactly the all-finite TIFF; member bytes match; hashes match the frozen run card |
| Final registered-control test | **COMPUTED:** 37,508 / 37,654 dots lie within 3 px of the pinned registered spacing-5 control: **99.6123%**, above the literal 70% limit. This one hash-pinned registered owner-mirror witness is sufficient for STOP; the 695-raster inventory was not exhaustively replayed. |
| Binary final-dot Spearman vs that witness | **COMPUTED diagnostic:** −0.0000768. Low correlation does not erase the independently failing 3-px overlap condition. |
| Pre-placement peer metrics | **CITED** from H31-CC's frozen card: max surface |ρ| 0.1319 and max tested-peer support overlap 32.0%. They were not recomputed in this integrity review; the source scope was nine focus rasters plus local downloads, not a complete registry. |
| Scientific screen | **CITED HOLDOUT-DTI:** 0.0470699 [0.0332317, 0.0618164], `gems57-pooled-hide-v2`, 60,988 withheld positives. Paired difference versus the same-run NULL is −0.0096697 [−0.0234561, +0.0052007]. The paired interval crosses zero and the point estimate is negative. Not rerun here and not a leaderboard score. |
| Off-catalogue proxy | **CITED SGMC-PROXY-DTI:** H31-CC 0.007849 vs H33 0.093965 on the same proxy protocol in the prior session. This is not hidden-truth HOLDOUT-DTI or a leaderboard score; it was not rerun here. |
| New-file leaderboard estimate / upload | **Unavailable / DO NOT SUBMIT.** No organizer score receipt, current private truth, fresh confirmation, selector approval, or weekly-cap verification is present. |

The added [independent verification receipt](../evidence/h31cc/verification_receipt.json) and its public copy (`docs/downloads/h31cc-verification.json`) make the byte/format/ZIP/witness checks executable. This did not regenerate the raster or reproduce the historical holdout. The `HOLDOUT-DTI` and pre-placement surface numbers remain cited prior results.

## Nine-site historical comparison

All scores below are **USER-REPORTED** claims, not **ORGANIZER-CONFIRMED** receipts. The 3-px column is a **COMPUTED** comparison between the pinned artifact and H33-2-B2; it is not a complete uniqueness scan, a live leaderboard feed, or an estimate for a new file. New-file estimates are unavailable. Full paths, source revisions, hashes, and evidence classifications remain in [`registry/focus_review.json`](../registry/focus_review.json) and the generated [nine-site table](../docs/executive-summary.html#focus-sites).

| Site | Highest listed pinned artifact | Reported claim | Computed positive-dot overlap with H33 | Interpretation / action |
|---|---|---:|---:|---|
| GEMSDOE24 | H25-1 dotted H19-5 D1.5 | 0.2477 | 88.5% | Historical prior art; not a unique new entry |
| GEMSDOE25 | Dotted H19-5 D2.8 | 0.2600 | 88.2% | Historical prior art; not a unique new entry |
| GEMSDOE27 | Topographic gap-closure T-v2 | 0.2449 | 86.7% | Historical prior art; not a unique new entry |
| GEMSDOE28 | H36-1 rung30 blind R1 | 0.2710 | 95.5% | Historical prior art; not a unique new entry |
| GEMSDOE30 | D2.8 Poisson 300 m off-catalogue | 0.2600 | 88.2% | Historical prior art; not a unique new entry |
| GEMSDOE31 | H27-4 solo D2.8 | 0.2708 | 95.4% | **USER-REPORTED;** conflicts with a pinned owner-page “unscored” status; exact score-to-file attribution unresolved |
| GEMSDOE32 | H33-2-B2 | **0.2778** | 100.0% | Highest of these nine claims; same reference; do not copy, rename, or call a new discovery |
| GEMSDOE33 | H33D analog tip/stepover R30 | 0.2632 | 92.6% | Historical prior art; not a unique new entry |
| GEMSDOE36 | Anderson geothermal PINN | 0.2750 | 97.4% | Highest listed historical claim for this site; later lower KPL36 0.1647 does not supersede it |

The score register also contains newer, lower claims such as GEMSDOE27 0.2250, GEMSDOE36 0.1647, GEMSDOE33 0.0963, and GEMSDOE28 0.0206. They remain **USER-REPORTED** and do not change the historical high-water values above. The focus-site register explicitly says it is a pinned historical snapshot, not a live leaderboard feed. Conflicting prompt anchors **0.3195** and **0.4413** remain unverified; no organizer receipts were added.

### H33-2-B2: supported forensic interpretation and limits

The pinned byte-level record [`evidence/h33_forensics_20261025.json`](../evidence/h33_forensics_20261025.json) describes H33 as catalogue-flank pruning of an existing dotted structural field: the recorded lineage removes dots near the public catalogue and adds none. Under the supplied metric definition (α=0.2, β=0.8, 300 m triangular kernel), deleting redundant predictions can plausibly reduce false-positive weight while retaining nearby kernel coverage. This is **INFERENCE** about a possible metric mechanism, not proof that deleted dots were false positives, not a causal explanation of private organizer truth, and not evidence of newly discovered geology. Hidden-truth credit remains unavailable. No organizer receipt ties the 0.2778 claim to exact bytes. The repository also records inconsistent parent counts (40,199 vs 42,846); treat that lineage detail as unresolved.

## Ranked desk-only hypotheses for a later authorized lane

These candidates are ranked from the repository's existing preregistrations and run-card inventory; no claim of worldwide novelty is made. Their exact variants are recorded as unfit in this repository. The ranking is qualitative relative promise and cost, **not a DTI forecast**. H31-CC is tested and is not a future hypothesis. No candidate was selected or fitted in this review because the lane paragraph is absent and the literal pre-placement gate remains binding.

| Rank | Local candidate / specific signal | Geological rationale | Closest repo prior art and novelty qualification | Named non-fault mimic | Feasibility / uncertainty |
|---:|---|---|---|---|---|
| 1 | **H31-AD signed horst-flank conduit:** B17 `cond_surf` gradient against B15 `depth_to_base_surf` gradient, corroborated by GeoDAWN Th/K or U/K and earthquake-intensity B16 | A covered normal-fault horst flank could juxtapose basement and conductive hydrothermal clay, with alteration signal but little surface scarp | Exact signed-polarity plus K-metasomatism operator is listed unfit; H31-U/H31-YR/H31-M and H31-HVDC use related inputs or unsigned/general conjunctions. Novelty is incremental, not global. | Saline-playa evaporites, lacustrine clays, unfaulted lithologic contacts, survey seams | Medium relative promise, low confidence; low–medium cost. Coarse conductivity limits 300 m localization. |
| 2 | **H31-AB signed cross-field phase offset:** B2 RTP, B13 isostatic gravity, optionally `TMI_up150`; reciprocal signed lateral displacement across orthogonal transfer corridors, tested against an unbroken-contact null | Oblique transfer faults may laterally offset basement contacts without a continuous vertical scarp | MAGREST tested same-field texture restoration and XFCOH31 tested cross-field gradient coherence; this exact perpendicular signed-offset operator is listed unfit, but prior families make the novelty boundary narrow. | Pluton/caldera margins, volcanic lithologic contacts, magnetic/gravity survey seams | Low–medium relative promise, low confidence; medium cost. High risk of reproducing prior cross-field signal. |
| 3 | **H31-AC matched-catchment ksn difference-in-differences:** paired D8 catchments matched on area/relief; opposite-signed normalized channel-steepness residuals across a candidate corridor, leave-one-channel-out stability | Fault-related uplift may persist in drainage profiles after hillslope diffusion erases scarps | Distinct from local raster-curvature/scarp filters and recorded unfit. It is a catchment-level operator, not a pixel ridge detector. | Lithologic erodibility contrast, stream capture, avulsion, base-level change | Low–medium relative promise at 100 m and high cost. The preferred 10 m DEM coverage/access is not verified here; the high-resolution form is not ready. |

Manual next step for any of these: an authorized lane assignment, exact data/cache restoration and hashes, preregistration, leakage canaries, whole-segment hide/recover with data-derived buffer, paired pooled-DTI CI, a separate fresh confirmation, full-scope surface/final-dot uniqueness, then an independent selector decision. Do not infer that the historical list authorizes any of those steps.

## Release/site reconciliation and implementation

- Before changes, `registry/release_status.json` was a byte-checked 26 October H31-X negative review, while the site hero and leading artifact section displayed the 28 October H31-CC research TIFF. Both denied upload, but the canonical pointer was stale relative to the latest research artifact.
- Preserved the exact prior release-status JSON at `evidence/release_status/release-status-2026-10-26-bf9d261d.json` (SHA-256 `ce76d989c6ca20aced87c57b65827d990be3dd1475736392c69ebb3cb413fc16`).
- Added a deterministic H31-CC integrity verifier and CI check. It validates both existing TIFF encodings against hash-pinned owner-mirror inputs; checks card/prereg hashes, file and ZIP hashes, exact one-TIFF ZIP roundtrip, binary values, catalogue mask, dot count and spacing; and re-computes final-dot overlap against one hash-pinned registered owner-mirror raster. It does not fit, emit, or rescore.
- Rebuilt the canonical release status from the latest existing H31-CC artifact. The permission decision is still `negative`, `ok_to_submit=false`, `slot_approved=false`, `leaderboard_estimate=null`. The surface and HOLDOUT-DTI values are explicitly cited, not rerun. The broad registry inventory is explicitly incomplete; the single witness suffices only to prove STOP.
- Updated the site generator and optional browser smoke test so the front door and canonical status refer to the same existing artifact. The hero now distinguishes prior-session H31-CC generation from this review's read-only verification. README and AGENTS point to this current review, while older session artifacts remain historical.
- `registry/current_run.json` remains the historical MAGREST run; its scope is not rewritten. `registry/review_passes.json` retains the `DO NOT SUBMIT — literal registry STOP` decision and identifies H31-CC as the latest scientific artifact.
- Integrated the already-merged main update from PR #62 into this fixed Arena branch after GitHub identified a merge conflict. Preserved its prior count-bound review and regenerated the combined evidence inventory and site; this was repository maintenance, not a new scientific run.

## Three review passes

### Pass 1 — implementation and line-by-line verification

- Re-read the full README and preserved charter, `AGENTS.md`, release status, current run, pass register, H31-CC preregistration/run card, site generator, focus-site evidence, H33 forensic record, and relevant tests.
- Restored only the pinned small sample/labels and registered lattice witness for read-only checks. The production feature stack/cache remained absent and was not restored. Installed the pinned project requirements in ignored `.venv/` only.
- Ran the repository's existing current-run integrity check and confirmed the prior MAGREST artifact remains negative. Before release-status changes, `build_release_status.py --check` and `check_site.py` passed; the stale current artifact pointer was then documented and fixed.
- Read the H31-CC runner and its current unit test. Added an independent read-back verifier because the original test asserted format fields/dot count but did not bind the served TIFF/ZIP bytes to the frozen card or rederive the registered-control overlap.

### Pass 2 — independent bug, assumptions, and fail-closed gate review

- Re-read the final emitted H31-CC TIFF and NaN twin; reproduced byte hashes, format validators, catalogue exclusion, 37,654-dot count, 2.828427 px minimum spacing, ZIP contents, and 99.6123% overlap against the registered witness.
- Confirmed the run card's HOLDOUT-DTI remains negative against the same-run NULL; it is cited, not recomputed. SGMC values are labeled as proxy metrics, not competition scores.
- Confirmed surface/pre-placement statistics remain cited from the frozen prior card, and one registered witness is not an exhaustive 695-raster pass. No uniqueness claim was broadened beyond evidence.
- Reviewed the latest score values without organizer receipts, the GEMSDOE31 unscored-status irregularity, H27 lineage count discrepancy, and conflicting 0.3195 / 0.4413 anchors. No new score claim or projection was created.
- No canary or scientific experiment was run because no candidate lane or feature stack was authorized/available.

### Pass 3 — full-request acceptance and CI/site consistency

- Verified that README identifies the current branch, current no-submit decision, current review, current prompt, latest artifact, and pinned status. The generated site presents the same current H31-CC artifact in both its research-artifact section and release-status section.
- An initial full test run caught that embedding a second closing `<details>` tag changed the byte-exact preserved owner-prompt section. Moved the current prompt copy outside that immutable block; the preservation regression then passed.
- Ran the focused H31-CC verifier/test, full unit suite, lint, compile, metric check, release-status consistency check, evidence collection, deterministic site build, and static site/link check. Exact results are recorded in the review register and below.
- Did not fetch outside-allowlist DrivenData, USGS, GDR, DOE/NLR, EPSG, or other non-GitHub pages. No live leaderboard, quota, current competition rules, organizer receipt, PR status, or external upload was inferred from a link.

## Manual-review sources and access limitations

These links are provided for human review. They were **not fetched in this review** unless a prior repository receipt explicitly says otherwise; no fresh external verification is claimed.

- [DrivenData GEMS problem and metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) · [competition overview/rules](https://www.drivendata.org/competitions/306/competition-doe-gems/) · [manual public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) — do not scrape or monitor.
- [DOE/NLR rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf).
- [Organizer reference solution on GitHub](https://github.com/drivendataorg/gems-prize-reference-solution) — historical local note identifies a U-Net reference; not executed here.
- [USGS GeoDAWN DOI](https://doi.org/10.5066/P93LGLVQ) · [INGENIOUS GDR 1391](https://gdr.openei.org/submissions/1391) · [USGS 3DEP](https://www.usgs.gov/3d-elevation-program).
- [EPSG:32611](https://epsg.io/32611) · [Tversky index](https://en.wikipedia.org/wiki/Tversky_index).

## Limitations and next steps

1. Resolve the missing method paragraph and literal registry policy with the authorized protocol owner before any future experiment. Do not change dot density or exempt the lattice.
2. Restore the full pinned production stack/cache only if an authorized method lane is assigned; the read-only validation inputs are not enough to reproduce geological features.
3. Require exact-byte organizer receipts before upgrading any score from USER-REPORTED to ORGANIZER-CONFIRMED. Reconcile the GEMSDOE31 0.2708/unscored conflict and the H27 parent-count discrepancy.
4. Treat H31-AD, H31-AB, and H31-AC as desk-only and locally unfit, not selected or globally novel. Re-rank only after a current, complete prior-art and source-availability check.
5. Keep the site static; do not create an automated DrivenData leaderboard feed. The linked leaderboard is for permitted manual review only.
6. The 82.34% minimum-overlap bound is specific to 37,654 dots. The count alone forces STOP only at `N ≥ 22,164`; below that it proves nothing, and the repository forbids evading the literal gate by changing density.
7. The optional Playwright browser smoke was not run because ignored `.cache/browser/node_modules` is absent; static generation and link checks passed.
8. No current file is cleared to submit. A format-valid research TIFF and a high historical USER-REPORTED score do not establish scientific efficacy, uniqueness under the binding gate, or organizer acceptance.

## Local verification results

| Check | Result |
|---|---|
| `scripts/verify_current_run.py --restore-small-inputs` | Passed; historical MAGREST remains negative. Re-read existing bytes; no experiment. |
| `scripts/verify_protocol_review.py` | Passed; prior H31-X protocol audit remains negative; 82.34% minimum-overlap bound is budget-specific. |
| `scripts/verify_h31cc_run.py --check` | Passed; exact existing TIFF/ZIP checks and 99.6123% registered-witness overlap reproduced; `ok_to_submit=false`. |
| `scripts/build_release_status.py --check` | Passed; current status is H31-CC, negative, and points to verified bytes. |
| `scripts/verify_h31j.py`, `scripts/verify_h31t.py`, `scripts/verify_h31aa_run.py --check` | Passed; all remain not slot-approved. |
| `python -m pytest -q` | **214 passed**. |
| `python -m ruff check .` | All checks passed. |
| `python -m compileall -q src scripts tests` | Passed. |
| `python scripts/check_metric.py` | Maximum fast/brute DTI difference `4.441e-16` over 24 grids; 29 kernel offsets. |
| `python scripts/check_marginal_dti.py` | 10,000 fixed-truth sign checks passed; zero geological experiments. |
| `python scripts/collect_evidence.py` | 250 artifacts inventoried; 14 submission files registered; 0 legacy cache files copied. |
| `python scripts/build_site.py` / `python scripts/check_site.py` | 22 pages generated; 22 pages and 552 local links passed. |
| External source/leaderboard access | No web pages fetched; no DrivenData access; manual links provided with limitations. |
