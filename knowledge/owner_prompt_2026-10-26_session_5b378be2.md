# Owner request — 2026-10-26, session arena/5b378be2-gemsdoe31 (faithful consolidated record)

This is a consolidated record of this session's brief (not a verbatim transcript; claims inside
the brief are user-provided context, not verified results). Reread with `README.md` + `AGENTS.md`
at the start of every continuation, per the brief itself.

## Core values (verbatim from brief)

- **Maximize P(Win)** — "Maximize the Probability of Winning": weigh tradeoffs, assess risk, choose the path that maximizes the probability of success; set emotions aside; put the project first.
- **Own the Outcome** — own results end to end; act without waiting for permission when you have the means; treat failure and success as signals; stay accountable to the final outcome.

## Directives (consolidated)

1. Review the repo; focus on the highest-scoring submissions from GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, 36.
   Produce an executive summary per site making it obvious which submission is best, unique, and submittable.
2. MUST generate a unique TIF submission (never copy a previous submission except for learning).
   It must be obvious whether the file is OK to download and submit. Validation must be automated
   through the project (no human inspector). Keep iterating/testing until the highest-scoring
   submission is identified. Estimate scores; table must list file to download, estimated score,
   and uniqueness vs the other GEMSDOE sites.
3. Parallel-Run Protocol: stay in one lane (rank-corr >0.90 or >70% of dots within 3 px of a
   registry raster = duplicate, stop; check surface + final dots); reuse cached features,
   `evaluate_holdout.py`, `submission_writer.py`; hide-and-recover holdout (whole segments +
   buffer, visible-only catalogue features, pixel-exact masking, pooled DTI α=0.2 β=0.8 300 m
   triangular); label every number HOLDOUT-DTI (evaluator, withheld n, 95% CI) or
   ORGANIZER-CONFIRMED (receipt only); leakage canary per feature (AUC >0.90 = leakage);
   end with one JSON run card; budget 3 experiments / 2 h; promotion is a separate selector step.
   NOTE: no concrete lane paragraph was included (IR-U-01 in the H31-U preregistration).
4. Study why GEMSDOE32 `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` = 0.2778 (USER-REPORTED in
   brief) leads; can we beat it? Brief also cites leaderboard context 0.4413 and 0.3195
   (both USER-REPORTED here; no receipts). Full per-site score list as pasted in the brief is
   preserved in `registry/user_reported_scores.json` and prior owner-prompt files.
5. Before implementing: propose 3–5 untried geological hypotheses (layers, physical signature,
   why catalogue-missing, novelty, ranked by expected DTI gain × cost); validate the top one on
   the spatial holdout before any weekly slot; external data only from free official sources,
   verified obtainable first. Deep scientific research on geothermal fault discovery; contrarian
   but grounded; store knowledge for reuse.
6. Competition: DrivenData 306 DOE GEMS. Submission = single-band GeoTIFF matching sample CRS/
   shape/geotransform; portal error seen: "Predicted values must be in range [0, 1]"; give the
   file a unique name + a short distinguishing note. Executive-summary subpage must explain
   exactly how to submit. Site (GitHub Pages) must be clean, obvious, one-click download.
7. Data access: no DrivenData auth available to the agent (login-walled); brief supplies mirror/
   Dropbox links; standing blocker text: run `bash scripts/download_competition_data.sh` into
   `data/`, then `python scripts/prepare_data.py` — "you need to complete the above task by
   yourself" (done this session via hash-verified GitHub mirrors; DrivenData never contacted).
8. Work in 3 passes (implement+verify; bug/edge review; full re-check), line-by-line verification
   from official sources with links, flag irregularities, no hallucinations, no manual input.
9. Put this prompt in the repo README as the recurring starting point (charter preserved there;
   this file is the dated session record).
10. Finish: create a pull request, merge to main, suggest remaining work and limitations.

## Official links named in the brief

- Leaderboard (static link only): https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- Competition: https://www.drivendata.org/competitions/306/competition-doe-gems/ (pages 967/968, data tab)
- Reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
- Rules PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf
- GDR 1391: https://gdr.openei.org/submissions/1391
- USGS GeoDAWN: https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and
- INGENIOUS: https://gbcge.org/current-projects/ingenious/
- EPSG:32611: https://epsg.io/32611 · Tversky: https://en.wikipedia.org/wiki/Tversky_index
