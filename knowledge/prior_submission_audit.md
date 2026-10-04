# Prior-submission audit: GEMSDOE25 D2.8 and the reported 0.2600

**Audit date:** 2026-10-04 (UTC)
**Evidence boundary:** no DrivenData page, leaderboard, submission endpoint, or user account was accessed. Claims about competition scores below are USER-REPORTED or OWNER-MIRROR claims, never independently verified official results. The pinned sibling is an owner-controlled public repository, not an organizer record.

## Executive finding

The active request describes a GEMSDOE25 D2.8 result of **0.2600**. That figure is recorded here as a user-reported claim because it appears in the request, but it is **not present in the pinned GEMSDOE25 score-claim audit or D2.8 artifact record**. At commit `c185edd8b09e19846cf34c16050e6cf891ecc2d0`, the owner-mirror `registry/submissions.json` marks D2.8 `unscored; not slot-approved`; the related score-audit says no D2.8 score was reported. The mirror calls its separate H19-5 D1.5 result **0.2477**, also unverified. No organizer receipt links 0.2600 to the D2.8 file. **Therefore this audit cannot assert why the exact 0.2600 was awarded, or even that the score belongs to this raster.** Do not resolve the discrepancy by checking the live leaderboard; the Terms of Use prohibit automated monitoring/copying and manual monitoring/copying without prior written consent.

## What the D2.8 raster is locally

The pinned owner-mirror registry and local byte/pixel checks describe D2.8 as a deterministic sparse-emission transform of H19-5, not a newly trained geological model:

- H19-5 parent: 121,131 positive pixels; owner-reported score **0.1922** (unverified).
- H19-5 D1.5 raster: 60,069 positive pixels; owner-reported score **0.2477** (unverified), 49.6% of the parent count.
- D2.8 raster: 44,090 positive pixels (36.4% of the parent count); it is pixel-for-pixel equal to `dot_thin(H19-5, min_dist=2.4 px)` in the pinned sibling. The sibling's D2.8 file uses a different TIFF byte layout from this repository's reference file, so **pixel identity is not byte identity**.
- The sibling's geometry analysis estimated that D1.5 retained 85.3% and D2.8 retained 75.9% of the parent's triangular-kernel credit under its assumed truth geometry. Those are computed geometric diagnostics under a model assumption, not measured credit against private test faults.

The label “D2.8” is a historical artifact name, not proof of an exact 2.8-pixel minimum spacing: on this raster's discrete grid the sibling reports the same pixel set for `min_dist=2.4` and `min_dist=2.8`.

## Mechanistic explanation—plausible, not verified

The official metric is distance-weighted Tversky with a 300 m triangular kernel and `alpha=0.2` for false positives, `beta=0.8` for false negatives. A prediction close to a true fault can receive more credit and a smaller distance-weighted false-positive penalty than a distant prediction. Removing nearby/redundant emitted dots can therefore raise DTI **if** the removed dots contributed little unique true-positive credit relative to their false-positive mass. Removing dots that uniquely cover fault segments can instead increase false negatives and lower DTI. The optimal tradeoff depends on the hidden truth geometry; it cannot be recovered from the output raster alone.

The D2.8 thinning reduces output count from 60,069 to 44,090 (about 26.6% fewer than D1.5) while retaining a modeled 75.9% of the parent’s geometric kernel credit. That pattern makes a modest improvement over D1.5 **plausible under the owner's assumed geometry**. It does not prove an official gain. The 2.4-pixel spacing is still less than the 6-pixel diameter of a 300 m support kernel at 100 m cells, so it does not eliminate overlap or establish an optimal spacing.

## What the owner-mirror models say—and do not say

The pinned GEMSDOE25 evidence includes a first-order emission model that uses only the owner-reported 0.1922 and 0.2477 anchors. It estimates D2.8 at DTI **0.2553**, with a sensitivity band **0.2500–0.2613** when assumed geometric retention is varied. The user-stated 0.2600 lies within that sensitivity band, but that is not an independent prediction interval, test result, or confirmation: both score anchors are unverified, the truth distribution is assumed, and the model is calibrated to those same claims. A separate owner package summary reports another conditional estimate around **0.251** (rough range 0.247–0.255); the difference between these model summaries is itself a reminder that they are assumption-sensitive, not a verified score.

The spatially blocked H28 holdout is not a confirmation of D2.8's live score: its frozen comparator reproduction failed (`0.149667509` recomputed versus `0.152003389` frozen), and its best arm had paired gain only `+0.000699` with 4/8 positive cells. Separately, H30's preregistered relay × terrain screen passed but fresh-draw confirmation failed (mean paired change `−0.001275`, 1/4 positive folds). These are owner-mirror catalogue-gap proxies, not hidden competition truth; they authorize no weekly slot. No local run establishes the D2.8 score.

## Claim ledger

| Claim | Evidence class | What is actually verified | Status |
|---|---|---|---|
| D2.8 scored 0.2600 | USER-REPORTED (from the current request) | No organizer receipt or D2.8 score row in the pinned mirror was found; live board intentionally not accessed | **Unverified; file-to-score attribution unresolved** |
| H19-5 scored 0.1922 | OWNER-MIRROR / user-owner claim | The sibling's score-audit labels it unverified; local parent raster exists in the owner's registry | **Unverified** |
| H19-5 D1.5 scored 0.2477 | OWNER-MIRROR / user-owner claim | The sibling's audit labels it unverified; local raster is pixel-identifiable as D1.5 thinning | **Unverified** |
| D2.8 has 44,090 positives and is a deterministic H19-5 thinning | COMPUTED against OWNER-MIRROR rasters | Local D2.8 reference is pixel-identical to the sibling D2.8 raster; see artifact hashes/format receipt | **Verified locally, not organizer-authenticated** |
| D2.8's conditional modeled DTI is ~0.255 | COMPUTED owner-mirror model | Reproduced only from unverified anchors and assumed fault geometry | **Model output, not competition score** |
| Current official score or rank | OFFICIAL | Not accessed; no receipt supplied or recorded | **Unknown** |

## Submission history relevant to the comparison

| Variant | Local identity | Reported score status | Interpretation |
|---|---|---|---|
| H19-4 | 123,779 positive pixels in sibling audit | 0.1894 owner-reported, unverified | Earlier dense surface; not a verified score |
| H19-5 | 121,131 positive pixels | 0.1922 owner-reported, unverified | Parent of the D1.5 and D2.8 dot-thinned variants |
| H19-5 D1.5 | 60,069 isolated positive dots | 0.2477 owner-reported, unverified | Stronger reported metric result; no organizer receipt in this audit |
| H19-5 D2.8 | 44,090 dots, deterministic thinning | 0.2600 user-reported in this request; marked unscored in the pinned sibling | Mechanistic explanation is plausible, but exact claim and file identity are unresolved |
| H30-1 P+S | No competition raster produced | No competition score | Proxy screen passed, fresh confirmation failed; stopped |

The table is a selected forensic comparison, not an independently verified leaderboard reconstruction. Historical score details and model assumptions are in the pinned owner's `registry/submissions.json`, `evidence/score_claim_audit.json`, `evidence/emission_model.json`, and `knowledge/07_findings_2026-10-02.md` at [GEMSDOE25 commit `c185edd8b09e19846cf34c16050e6cf891ecc2d0`](https://github.com/buffedlizard55-lab/GEMSDOE25/tree/c185edd8b09e19846cf34c16050e6cf891ecc2d0).

## Next evidence needed (manual/authorized only)

1. If the owner has an organizer-generated receipt for 0.2600, add a non-sensitive copy or its cryptographic digest and exact submission ID manually; no credentials are needed or requested.
2. Otherwise keep 0.2600 labelled user-reported/unverified. Do not poll, scrape, or manually monitor/copy the leaderboard without prior written consent.
3. Do not spend a weekly slot on D2.8 or H31-A until the new candidate beats the same-run, empirically buffered spatial holdout incumbent, passes fresh confirmation, and its exact TIFF passes the strict template/range audit.

## Official sources

- DrivenData [GEMS problem description, metric and format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/).
- DOE/NLR [GEMS Prize Official Rules](https://docs.nlr.gov/docs/fy26osti/96647.pdf).
- DrivenData [Terms of Use](https://www.drivendata.org/termsofuse/).
