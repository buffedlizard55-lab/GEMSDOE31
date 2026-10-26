# Owner request — 2026-10-26, session arena/579233d5-gemsdoe31 (faithful consolidated record)

Same consolidated brief as `knowledge/owner_prompt_2026-10-26_session_5b378be2.md` (read that file for the
full directive list; claims inside the brief are user-provided context, not verified results). Session-
specific points honoured here:

- Core values: **Maximize P(Win)**, **Own the Outcome** (verbatim in the 5b378be2 record).
- Focus sites: GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, 36. Highest listed claim: GEMSDOE32
  `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` = 0.2778 USER-REPORTED (no organizer receipt);
  leaderboard context 0.4413 / 0.3195 likewise USER-REPORTED. Per-site score list as pasted is preserved
  in `registry/user_reported_scores.json` and prior owner-prompt files.
- Must generate a new unique TIF, validate fully automatically (no human inspector), make
  download/submit status obvious, estimate scores, and table: file to download / estimated score /
  unique? Keep iterating until the highest-scoring submission is identified. Pass 1 implement+verify,
  Pass 2 bug/edge review, Pass 3 requirements re-check; open a PR and merge to main; list remaining
  work and limitations.
- Parallel-Run Protocol as before (one lane; >0.90 rank corr or >70% dots within 3 px = duplicate STOP;
  reuse shared evaluator/writer/cache; label HOLDOUT-DTI vs ORGANIZER-CONFIRMED; canary AUC ≤ 0.90;
  JSON run card; 3 experiments / 2 h per lane; promotion is a separate selector step). No concrete lane
  paragraph was included again (IR-U-01) — lanes were self-assigned and preregistered before fitting:
  H31-Y (`knowledge/2026-10-26_h31y_regime_split_preregistration.md`) and successor H31-Z
  (`knowledge/2026-10-26_h31z_quota_split_preregistration.md`).
- Outcome of this session: `knowledge/2026-10-26_h31yz_executive_summary.md`. Selector primary is
  unchanged (H31-X); both new lanes are measured negatives, DO NOT SUBMIT.
