# Repository review — 2026-10-27 (branch `arena/56618cf9-gemsdoe31`)

## Decision

**No TIFF in this checkout is cleared for competition upload. Do not submit.** No new raster, model fit, experiment, slot selection, upload, or leaderboard retrieval was performed in this review. The request's mandatory protocol names a single-method paragraph, but the prompt contains no such paragraph. Earlier `H31-AA` work in this checkout cannot be treated as assignment authorization: its preregistration itself notes the absent paragraph and then self-selects a lane. The literal registry gate also remains failed. We must not use an invented lane or weaken the gate to satisfy a request for an uploadable result.

There is an existing H31-AA TIFF in `docs/downloads/`, labeled research-only. Its run card reports HOLDOUT-DTI `0.1488667` (evaluator `gems57-pooled-hide-v2`, 60,988 withheld positives, 95% CI `[0.1368349, 0.1603827]`) and paired difference against same-run H31-X `-0.0172663` (95% CI `[-0.0282642, -0.0062493]`). This is a negative relative to the incumbent. The card also records a literal-registry stop and explicitly sets `verdict=negative`, `ok_to_submit=false`, `slot_approved=false`. These are stored run-card results, not independently reproduced in this review. The purported leaderboard estimates remain unavailable; user-supplied site scores are not organizer-confirmed without exact-byte submission receipts.

## Review of repository state

- Current checked-out branch: `arena/56618cf9-gemsdoe31`; working tree was clean at review start. The documentation contains session banners for other Arena branches, including `arena/f5b2211b-gemsdoe31` and `arena/74acc325-gemsdoe31`. These are historical branches, not this branch. Treat their claims and review logs as repository evidence with provenance, not as proof that checks ran on this checkout.
- README already contains a large preserved owner prompt, recurring instruction to reread it, core values (“Maximize P(Win)” and “Own the Outcome”), and extensive historical session records. The top banner is stale for this branch and asserts specific prior-session deliverables; the current review record is linked from the README to prevent confusing that banner with this session.
- `registry/release_status.json` currently describes H31-X and is negative. The H31-AA run card is separately under `docs/downloads/h31aa-run-card.json`; `registry/current_run.json` refers to a MAGREST run. There are therefore multiple historical/current-looking artifacts. The release front door is negative; do not infer permission from an artifact's TIFF format check, prior README promotions, or research download link.
- The repository lacks `data/` and `.cache/` inputs. No new science can be reproduced without those authorized inputs and the shared cache.
- No source URLs outside the sandbox's allowed hosts were freshly accessed. Stored official links are useful for manual review, not evidence of current external status. The DrivenData leaderboard, submission cap, authentication, and receipts were not checked.

## Review of the nine focus sites

The summary in `knowledge/2026-10-27_h31aa_session_review.md` and `docs/executive-summary.html` captures the available pinned/user-supplied context, but its site scores are classified `USER-REPORTED`, not `ORGANIZER-CONFIRMED`. It also contains both older high scores and additional more recent entries. The “highest submission” should be selected from the complete per-site evidence and pinned artifacts, not copied from a prompt list alone. No reliable score estimate for a new raster is supported. In particular, H33-2-B2's reported `0.2778` does not establish causal reasons for its score and cannot establish that a new candidate can beat it; `0.3195` and `0.4413` are also unverified claims in this repository context.

A suitable research explanation is conditional, not causal: deleting redundant predictions near mapped traces can improve a distance-tolerant, FP-penalized metric if removed dots contributed false-positive mass more than weighted true-positive coverage. The hypothesized spacing/pruning mechanism is plausible from the raster geometry and scoring algebra. It is not proof of why hidden organizer truth yielded the reported number, nor a validated prediction of leaderboard performance.

## Protocol and experimental gates

The user-supplied task sets three experiments / two hours maximum, requires feature-alone leakage canaries, visible-only catalogue-derived features, whole-segment buffered hide-and-recover, exact visible-fault masks, pooled DTI and paired uncertainty, pre-placement and final-dot duplicate checks, plus a complete run card. This session did not run experiments because (a) the assigned lane paragraph is absent, (b) raw/cache data are missing, and (c) the binding registry gate is failed. This is the correct fail-closed behavior. Desk hypotheses in past review documents are not authorization to compute or emit a candidate. A negative result is recorded here; no projection is labeled as a score.

## Three-pass review

### Pass 1 — inventory

Inspected the repository layout, README banner and owner prompt pointers, historical review/preregistration records, `registry/current_run.json`, `registry/release_status.json`, H31-AA run card, validation scripts, tests, and current git branch/status. Confirmed current branch and absent `data/` directory. No competition data or slot was touched.

### Pass 2 — attempted checks and risk review

- `python -m pytest -q` could not start because the system Python has no pytest.
- System Python could not run release/run verification because NumPy was absent.
- Created ignored `.venv/` and installed pinned `requirements.txt` from the package index. This changed no tracked files.
- `scripts/build_release_status.py --check` then stopped because `data/sample_submission.tif` is absent. It did not validate or update the decision. No attempt was made to restore data from an unauthorized source.
- README's top dated banner refers to earlier branch sessions. This is a documentation provenance hazard; the current review link below records the branch actually reviewed.

### Pass 3 — available verification

- `.venv/bin/python scripts/check_site.py`: **22 pages, 534 local links checked; all passed**.
- `scripts/build_release_status.py --check`: **blocked**, missing `data/sample_submission.tif`.
- `.venv/bin/python -m pytest -q`: **196 passed, 10 skipped, 2 failed**. The failures are `test_h31j_end_to_end_artifact_and_gate_integrity` and `test_h31s_packaged_deliverables_and_run_card_pass_automated_validation`; both stop because `data/sample_submission.tif` (and for H31-J, `data/labels.tif`) is missing. The skipped cases likewise document missing small-input restoration.
- Release-status recomputation and independent raster verification: **blocked** by the same missing pinned sample template. Do not claim a full CI pass.
- No new TIFF was generated, so no new raster hash, independent holdout, feature leakage canary, surface/final uniqueness run, or validator receipt exists.

## Ranked desk hypotheses for a future authorized lane

These ideas are suggestions only, not a claim of broad novelty and not permission to execute. They use existing competition stack layers where available; no external data was fetched.

| Rank | Candidate research idea | Layers / signature | Why it might detect an unmapped fault | Repo distinction and non-fault mimic | Cost / expected benefit |
|---:|---|---|---|---|---|
| 1 | Matched cross-front drainage-profile contrast | DEM, slope, drainage-area derivatives; compare normalized channel-steepness residuals in paired catchments across candidate traces | Persistent differential uplift may survive after the surface scarp has degraded | Distinct from pointwise curvature if implemented as matched catchment difference-in-differences; stream capture, lithologic erodibility, and alluvial avulsion mimic it. High compute; unquantified benefit. | High / potentially modest |
| 2 | Signed transverse displacement of paired geophysical contacts | RTP magnetic and isostatic gravity gradients; detect reciprocal lateral contact offsets | Concealed strike-slip/oblique faults can offset basement contacts without a clear vertical scarp | Distinct from magnetic restoration or edge-coherence alone; pluton boundaries, caldera margins, and survey seams mimic offsets. High compute and careful null testing needed. | High / uncertain |
| 3 | Shoreline-null residual on terrain flexure | DEM and gravity/basement layers; compare along-strike elevation constancy against subsurface edge corroboration | Helps distinguish low-relief fault-front continuations from abandoned lake benches | Must be a prespecified null comparison, not a post-hoc threshold variant; paleoshorelines and tilted lake margins are key mimics. Moderate compute. | Medium / uncertain |

None is currently eligible: no assigned paragraph, data/cache, confirmed registry scope, or same-run incumbent setup. For the catchment idea at finer resolution, the official free source to investigate is USGS 3DEP (https://www.usgs.gov/3d-elevation-program); it was not checked for availability in this sandbox and is not treated as viable input until access/license/projection are verified. Other two proposals need no new external source if the authorized feature stack contains the stated bands.

## Next steps and limitations

1. Obtain the actual assigned method paragraph and owner resolution of the any-registry/3-px/70% rule. Do not self-assign a lane or exempt a registered raster.
2. Reconcile the branch-specific README front matter with this checkout; preserve historical branch content but make current branch/session provenance explicit.
3. Restore authorized, hash-pinned competition inputs and shared cache, then run `scripts/verify_protocol_review.py`, `scripts/build_release_status.py --check`, full tests, lint, compile checks, and TIFF validation. Without the data, the release gate and scientific pipeline cannot be verified here.
4. Refresh nine-site and wider registry inventories at immutable commits, and distinguish complete scan scope from unscanned artifacts. Verify exact-byte organizer receipts before reclassifying any reported score.
5. After authorization only, preregister and evaluate a maximum of three ideas using the unchanged shared evaluator. Compare against a retrained same-run incumbent, run leakage canaries first, preserve a separate confirmation split, and enforce surface and emitted-dot uniqueness.
6. Keep the current research-only TIFF visibly marked **DO NOT SUBMIT**. Format validity does not imply scientific merit, uniqueness, organizer acceptance, or slot permission. A separate authorized selector must check weekly quota before any submission.

## Official links (stored for manual review, not freshly checked)

- [DrivenData problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Competition rules](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Competition data page (login may be required)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN data](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [USGS 3DEP](https://www.usgs.gov/3d-elevation-program)
- [GDR/INGENIOUS submission 1391](https://gdr.openei.org/submissions/1391)
- [EPSG:32611](https://epsg.io/32611)
- [DOE/NLR GEMS report](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [Leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) (not accessed in this session)
