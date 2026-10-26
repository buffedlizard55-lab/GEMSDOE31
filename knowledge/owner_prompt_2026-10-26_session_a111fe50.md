# Owner prompt record — session `arena/a111fe50-gemsdoe31` (2026-10-26)

Session instruction record (faithful condensation kept with the repo as the owner directed;
the recurring full charter remains in `README.md`). The owner directed, in substance:

1. Review the repo; focus on the highest-scoring submissions from GEMSDOE24, 25, 27, 28, 30, 31,
   32, 33, 36; produce an executive summary making it obvious which single file to submit.
2. The submission must be **unique** (not a copy of any earlier GEMSDOE file), downloadable as a
   single GeoTIFF with a unique name and a ≤140-character note; estimate its score; provide a
   table: file to download · estimated score · unique or not.
3. Explain, with PhD-level analysis verified line by line (no hallucinations), why GEMSDOE32
   `h33-h33-2-b2-…-zeros` scored 0.2778 (USER-REPORTED) and whether a higher score is achievable
   (owner-cited leaderboard context values 0.3195 / 0.4413, USER-REPORTED).
4. Parallel-Run Protocol: stay in one self-contained method lane; rank-correlation >0.90 or >70%
   of dots within 3 px of a registry raster = duplicate STOP (check surface and final dots);
   reuse the shared template/evaluator/writer; label every number HOLDOUT-DTI or
   ORGANIZER-CONFIRMED (projections are never scores); leakage canary AUC >0.90 = stop; end with
   one JSON run card; budget ≤3 experiments; do not spend a submission slot from the lane.
   NOTE: as in every earlier session, no distinct "single method paragraph" lane assignment was
   actually supplied in the prompt text — recorded as irregularity IR-U-01 in the preregistration
   (`knowledge/2026-10-26_h31y_preregistration.md`), which self-assigns the lane before fitting.
5. Generate 3–5 new geological hypotheses (layers, physical signature, why catalogue-missing,
   novelty), rank by expected DTI gain/cost, validate the top candidate on the spatially blocked
   holdout before any weekly slot; name free official sources for anything needing external data.
6. Fix the portal failure class “Predicted values must be in range [0, 1]”; make the site's first
   screen an obvious single download decision with an executive-summary subpage explaining
   exactly how to submit; validation must be automated (no human inspector).
7. Preserve this prompt in the repo; keep Arena core values (Maximize P(Win); Own the Outcome);
   verify line by line from official sources; run three cumulative review passes; open and merge
   a PR to `main` if checks/permissions allow, reporting only verifiable receipts.

How this session answered each item: `knowledge/2026-10-26_h31y_executive_summary.md` (§1–§8),
`knowledge/2026-10-26_h31y_projection_audit.md`, `evidence/h31y/run_card.json`,
`registry/selector_update_20261026_a111fe50.json`, regenerated `docs/`.
