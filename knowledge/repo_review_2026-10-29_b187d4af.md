# Three-pass review — 29 October 2026

**DO NOT SUBMIT. No newly generated TIFF is approved.** This session performed no experiment, placement, selector step, or competition upload. The request describes a single method paragraph but does not actually supply one. The literal any-registry duplicate rule is binding; the pinned spacing-5 control prevents promotion of the existing H31-CC file. It is not safe to pretend a new method or a policy exemption was authorized.

## Pass 1 — repository and release audit

Read the full README, repository instructions, release registers, and previous review. Restored only hash-pinned small validation inputs and the registered witness using the repository verifier. `verify_current_run`, `verify_protocol_review`, `verify_h31cc_run --check`, and `build_release_status --check` passed, all retaining the negative decision. H31-CC's [existing all-finite research TIFF](../docs/downloads/gems31-h31cc-basement-step-37654d-20261028-zeros.tif) is **not approved for submission**; its SHA-256 is `0e82a9e8b80052d0bc61e8f550b2ac5204d012ab1f53fb2208051f285f10ad44`. Local format validation passed against the pinned owner-mirror sample; that is not proof of organizer acceptance. The prior H31-CC HOLDOUT-DTI was not rerun.

## Pass 2 — safety defect and correction

The reusable `selector_permission` helper previously accepted an internally contradictory uniqueness record with `pass_=true`, `duplicate=false`, and nonempty or missing failures. No actual release was approved by this review or by this defect. It now requires an explicit empty failures list; malformed uniqueness and scientific-gate inputs fail closed. Malformed stage records are also treated as missing evidence rather than raising an attribute error. Regression tests cover these cases. This is local release-policy code, not a change to the shared holdout or submission writer.

## Pass 3 — recheck and limitations

- `pytest`: 219 passed; `ruff` and `compileall`: passed; `check_metric`: fast/brute maximum absolute difference 4.441e-16 on the script's test grids.
- Evidence collection and site regeneration completed; site checker passed 22 pages and 552 local links. Timestamp-only readiness drift was discarded.
- The H31-CC final-dot comparison was independently recomputed: 99.6123% within three pixels of **one** registered control. It exceeds the 70% STOP. This is not an exhaustive registry scan and does not establish literal copying. Surface comparisons and scientific results are cited from the prior card, not replayed.
- At 37,654 dots, the independently checked witness supplies an 82.34% minimum-overlap counting bound; this is specific to that budget, not all possible rasters. Do not lower density to evade the policy.
- The nine requested historical site comparisons, pinned sources, score qualifications and three ranked desk-only hypotheses are in the [prior comprehensive review](repo_review_2026-10-28_arena-41e3ba3f.md) and [executive summary](../docs/executive-summary.html#focus-sites). Their scores are **USER-REPORTED**, not organizer-confirmed. The supplied 0.3195 and 0.4413 leaderboard claims conflict and were not verified. H33 pruning may reduce redundant predictions under the stated metric, but private-truth causation and outperformance cannot be established from these data.
- No newly validated leaderboard estimate exists. A holdout statistic is not an organizer score. The full feature cache was not restored and no fresh leakage canary or holdout was run. The network environment restricts external hosts, and no DrivenData login, live leaderboard, weekly cap, or organizer receipt was accessed or verified. User-provided Dropbox links could not be tested here. The earlier claim that data placement is the only blocker is therefore insufficient: lane assignment, literal duplicate feasibility, complete registry coverage, validation and separate slot authorization also matter.

## Next steps

A protocol owner must specify the missing method lane and resolve the literal registry overlap conflict without silently exempting controls. If an authorized, feasible lane results, preregister it, restore and hash-check the pinned feature stack, execute leakage canaries and spatial holdout on the shared tools, and compare against the complete registry at both required stages. Only a later authorized selector, fresh efficacy confirmation and verified weekly cap could permit a real submission. Never use a competition slot for this review.

Sources for manual review: [organizer reference solution](https://github.com/drivendataorg/gems-prize-reference-solution), [competition description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), [competition data](https://www.drivendata.org/competitions/306/competition-doe-gems/data/), [USGS GeoDAWN](https://doi.org/10.5066/P93LGLVQ), [INGENIOUS](https://gdr.openei.org/submissions/1391). Non-GitHub pages were not freshly checked in this environment.

[Machine-readable review card](../evidence/review_b187d4af/run_card.json) · [current release status](../registry/release_status.json) · [existing H31-CC independent verification](../evidence/h31cc/verification_receipt.json).
