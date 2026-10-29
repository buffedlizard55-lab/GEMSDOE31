# Current status — 2026-10-29 (`arena/eebfaae2-gemsdoe31`)

## Decision

**Negative. No new TIFF generated. No file approved to submit. No experiment or weekly submission slot used.**

## Evidence and actions

- Executive summary and the per-site comparison are available in `docs/executive-summary.html`; detailed review: `knowledge/repo_review_2026-10-29_arena-eebfaae2.md`.
- Machine-readable run card: `evidence/review_eebfaae2/run_card.json`.
- Canonical H31-CC release exact artifact check: SHA-256 `0e82a9e8b80052d0bc61e8f550b2ac5204d012ab1f53fb2208051f285f10ad44`; research-only, `ok_to_submit=false`; its cited HOLDOUT-DTI is 0.047069900074 (gems57-pooled-hide-v2, 60,988 withheld, 95% CI [0.03323168323881463, 0.06181643961343269]). This is a prior result, not rerun in this session.
- A later-dated H-STEO research TIFF also exists (9,140 dots; SHA-256 `aadbcd5398fccfc402c8358c5b87ba0d922b6eeb90f4932b5bbdf4fde0e18e89`). We independently revalidated both encodings against the hash-pinned owner-mirror sample; format passes only. Its holdout is null and novelty evidence is limited to one lattice (full registry check unavailable). It is not submission-ready.
- Existing strict registry witness comparison: final 3-pixel overlap 0.9961225898974877 (>0.70), correlation 0.00008201247921201492; enough to trigger STOP against that witness, not an exhaustive registry scan. No candidate surface or final placement exists this session.
- Focus-site pairwise findings are inherited from the pinned previous audit: 36/36 pairs exceed the overlap limit, minimum 0.97313. Scores are USER-REPORTED, not organizer-confirmed. The nine-site sources were not re-fetched in this session.
- Data restoration was limited to hash-pinned public owner-mirror sample grid, catalogue labels and one witness for automated format/release verification. This is not an organizer-authenticated data download; the full feature stack/cache is absent.
- Source checks: USGS FDSN API documentation fetched successfully. NBMG geothermal page returned HTTP 502; GFZ WSM record returned HTTP 500; SMU NGDS fetch failed. No event or external dataset query was made; coverage/licensing is unresolved.

## Verification

- First `pytest -q`: 3 failures, 245 passed, 11 skipped due missing small validation inputs. The inputs were restored using the documented hash-pinned GitHub owner-mirror path. Second `pytest -q`: 259 passed; after adding three fail-closed review-record regression tests, final `pytest -q`: 262 passed.
- Ruff: passed. `compileall`: passed. Metric test: maximum fast/brute discrepancy 4.441e-16.
- Metric check: maximum fast/brute discrepancy 4.441e-16; marginal-DTI algebra check passed 10,000 cases with all signs agreeing.
- Protocol review and H31-CC/release verifiers: negative decision reproduced; no upload approval.
- H31-J, H31-T, H31-AA verifiers: passed their historical artifact checks; each remains unapproved.
- Evidence collection: passed with 259 artifacts inventoried. Static site: 22 pages, 559 local links, passed.

## Open gates

1. Restore/hash-verify competition features for any scientifically authorized holdout; comply with the owner's data authorization.
2. Assign one method lane / provide the method paragraph missing from the prompt before any experiment.
3. Resolve strict registry duplicate STOP before candidate surface or placement; do not generate after a STOP.
4. Obtain organizer confirmation for score/source and mask/format ambiguities; no score receipt or live leaderboard data is available.
5. Verify external-source availability, coverage and challenge sharing licences before any use.
6. Any real slot selection remains a separate, authorized selector decision under the competition's current cap.
