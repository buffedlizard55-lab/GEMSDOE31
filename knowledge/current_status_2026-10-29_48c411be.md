# Current status — 2026-10-29 (arena/48c411be-gemsdoe31)

## Decision

**No file is cleared to submit. DO NOT SUBMIT.** No new TIFF was generated, no experiment ran (0 of 3), no weekly slot is approved, and no leaderboard score is claimed. Every number taken from the leaderboard list is **USER-REPORTED** (no organizer receipt exists in this repository).

Why no new TIFF:

1. **No method lane.** The parallel-run protocol says "your lane is the single method paragraph below". No such paragraph follows it, so no experiment is authorised (AGENTS.md: "No new method paragraph is present").
2. **Feature stack not restored.** `registry/data_manifest.json` pins `training_features.tif` (418,912,844 bytes) to GitHub parts. AGENTS.md forbids restoring it under the current STOP without owner authorisation (IR-48C4-07).
3. **The uniqueness rule cannot be met at the competition budget.** The registered spacing-5 control leaves 6,649 footprint pixels outside its 3 px halo. A 37,654-dot file must therefore put at least 31,005 dots (82.34%) within 3 px of the control. The protocol stops any file above 70%. This was recomputed from the cached control (`scripts/verify_lattice_bound.py`). Bypassing it, for example by placing dots only in those 6,649 pixels, would be gaming the rule, and the repository rules forbid that. No bypass was made (IR-48C4-04).

## Answer: why GEMSDOE32's 0.2778 scored highest (verified in bytes)

Source: `evidence/review_48c411be/gemsdoe32_forensics.json` (`scripts/verify_gemsdoe32_forensics.py`). Scores are USER-REPORTED.

| Step | Dots | Verified fact |
|---|---|---|
| D2.8 parent (GEMSDOE25 file, commit `2a279dd0`) | 44,090 | user-reported 0.2600 (GEMSDOE25 and GEMSDOE30 family) |
| H27-4 (local `gemsdoe31-h27-4-solo-d28…-nan.tif`) | 40,199 | = D2.8 with every dot within **1 px** of the catalogue deleted (3,891 dots). User-reported 0.2708 |
| H33-2-B2 (GEMSDOE32, `-nan` at `9863c82a`; `-zeros` at `c39ee46e`) | 37,654 | = D2.8 with every dot within **2 px** of the catalogue deleted (6,436 dots). User-reported 0.2778 |

- Set inclusion holds: H33-2-B2 ⊂ H27-4 ⊂ D2.8.
- The deleted dots lie 1.0 to 2.0 px from the restored catalogue (`data/labels.tif`, SHA-256 checked). The kept dots are all at least √5 ≈ 2.236 px away. No GEMSDOE32 dot lies on the catalogue.
- A 1.5 px cut matches neither repo file.
- A 3 px cut would delete 2,171 more dots, leaving 35,483. **100% of those dots lie within 3 px of GEMSDOE32**, so that step is a duplicate by construction. The pruning ladder cannot be climbed inside the uniqueness rule.

**Interpretation (INFERENCE, not measured here).** The official metric (α = 0.2, β = 0.8, 300 m triangular kernel) penalises predicted mass that is not near the test faults. The test faults are new faults that are not in the USGS catalogue (official problem page). Deleting dots that sit next to mapped faults therefore lowers the false-positive term. It also lowers the true-positive term if a new fault lies within 300 m of a deleted dot. The user-reported gains (+0.0108 for 1 px, +0.0070 more for 2 px) are consistent with the first effect. They are not measured here.

**Can a file beat 0.2778?** Not by pruning this family, because the next step is a duplicate. A higher score needs a new dot family from an assigned method lane, validated on a spatially blocked holdout before any slot is used. No such family exists in this session.

### GEMSDOE32 has two files

| Name | Source | Outside the footprint |
|---|---|---|
| `…-zeros.tif` (219,065 bytes; the file named in the owner's leaderboard list) | commit `c39ee46e` (2026-10-04) | 0.0 in every cell. No NaN anywhere (12,279,160 finite cells). |
| `…-nan.tif` (355,443 bytes; the file in the registry row) | commit `9863c82a` | NaN (5,167,373-pixel footprint) |

Inside the footprint the two files are identical (37,654 dots at 1; everything else 0). The **official** text says "data outside the bounds is null or nan". The `-zeros` file complies only if "bounds" means the full grid extent. The `-nan` file complies under either reading. This is unresolved (IR-48C4-02). GEMSDOE32's `main` moved to `0ffda716` on 2026-10-29, after the pinned commits (IR-48C4-03).

## Uniqueness bound (recomputed)

`scripts/verify_lattice_bound.py` reads the hash-pinned cached control (`.cache/registry-scope/registered-lattice.tif`, SHA-256 `b4570b40…`). It finds 5,167,373 footprint pixels, 6,649 of them more than 3 px from every control dot, and a forced minimum overlap of 31,005 / 37,654 = 0.8234 at the 37,654-dot budget. All five checks match `registry/release_status.json`. The bound is a counting argument for this budget, not a claim about every nonempty raster.

## Hypotheses re-checked (none run)

| id | idea | in repo before this session? | status |
|---|---|---|---|
| H-CC-A | thermal-spring collinearity | no | untested. Position accuracy is the main risk (the cc130eb1 hypothesis text says quarter-quarter section; not verified here). |
| H-CC-B | World Stress Map SHmax prior | no | untested. WSM DOI resolves (GFZ record, 100,842 records); licence text not read here. |
| H-CC-C | seismicity nodal-plane alignment | **yes, as H5 (NOT RUN)** in `knowledge/2026-10-25_lane_hypotheses.md` | rescope of H5; expected gain low at 300 m (IR-48C4-09) |
| H-CC-D | heat-flow residual (SMU database) | archive notes only | blocked: SMU node could not be fetched on 2026-10-29; licence unverified |
| H48-E | catalogue-flank radius on the D2.8 family | 1 px and 2 px variants exist; 3 px is a duplicate | the ladder is exhausted under the uniqueness rule; a new family is needed |

Ranking by expected DTI gain and cost, with no validation done: (1) H-CC-B, if the WSM licence allows use (low–medium cost, CC BY 4.0 claimed in the register, not yet read); (2) H-CC-A (medium cost, positional risk); (3) H-CC-D (blocked); (4) H-CC-C (low expected gain at 300 m). Ranking is INFERENCE.

## Official and free sources checked on 2026-10-29

| Source | Result |
|---|---|
| DrivenData problem page https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/ | reachable; quotes verified: NaN outside bounds; values between 0 and 1; α = 0.2, β = 0.8; 300 m triangular kernel |
| DrivenData data tab | login-gated (earlier sessions); not requested again |
| WSM DOI https://doi.org/10.5880/WSM.2025.001 | resolves to GFZ Data Services; licence not read |
| NBMG site descriptions https://nbmg.unr.edu/geothermal/sitedescriptions.html | reachable; lists more than 200 sites; licence not checked |
| SMU heat-flow node http://search.geothermaldata.org/dataset/115609c8-6f52-49fe-a0af-9d379d516340 | **fetch failed**; unverified |
| USGS FDSN event service docs https://earthquake.usgs.gov/fdsnws/event/1/ | documentation reachable; no query issued |

Leaderboard: the static official link was not scraped or polled. Anchor scores (0.4413, 0.3195) remain conflicting USER-REPORTED values (IR-CC130-09).

## Checks run on the final tree

| Check | Result |
|---|---|
| `scripts/verify_current_run.py --restore-small-inputs` | run first (labels and sample restored; registered control cached) |
| `pytest -q` | see the final run below |
| `ruff check .` | see the final run below |
| `compileall -q src scripts tests` | see the final run below |
| `check_metric.py`, `verify_protocol_review.py`, `verify_h31cc_run.py --check`, `build_release_status.py --check`, `verify_h31j.py`, `verify_h31t.py`, `verify_h31aa_run.py --check`, `verify_focus_sites.py` | rc 0 |
| `audit_download.py` | rc 2 = verified denial (as documented) |
| `verify_gemsdoe32_forensics.py`, `verify_lattice_bound.py`, `build_session_addendum.py --check` | rc 0 |
| `collect_evidence.py`, `build_site.py`, `check_site.py` | rc 0; 22 pages and 555 local links checked |

## Irregularities (new this session)

IR-48C4-01 to IR-48C4-09 are in `registry/irregularities.json`. The main ones: two GEMSDOE32 files; the NaN-versus-zeros conflict; the GEMSDOE32 head changed today; the uniqueness rule conflicts with the budget; the pruning ladder is exhausted; the feature-stack authorisation; the test-order dependency; the H-CC-C and H-CC-D status.

## Owner decisions needed (in priority order)

1. **Uniqueness rule.** Keep the literal any-registry rule (no full-budget file can then be unique), or define the comparison set. This choice decides whether any new TIFF can be generated at all.
2. **Method lane.** Supply the single method paragraph (lane) that the protocol requires. Without it no experiment runs.
3. **Feature-stack restore.** Authorise restoring `training_features.tif` from the owner mirror. Without it no holdout DTI can be produced.
4. **Organizer text.** Ask whether "bounds" means the full grid or the valid footprint, and get the organizer sample or validator message (IR-48C4-02, IR-48C4-06).

## Next session (suggested)

- Once a lane and the feature stack are authorised: run a spatially blocked holdout for the best new family, with a buffered collar derived from out-of-fold residuals, and run the duplicate screen on the surface and on the final dots.
- Obtain the WSM licence text, and try the SMU node again. Verify NBMG's data licence before any use.
- Keep the executive summary and register regenerated from the evidence JSON. Do not hand-edit HTML.
