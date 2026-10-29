# Operative owner prompt — 29 October 2026 (`arena/a5caa430-gemsdoe31`)

This is a structured restatement of the current request, not a verbatim transcript of its repeated historical score lists. The original long-form request remains in the conversation; this file and the README carry the durable operating requirements for later sessions. At each session start, read this file, the entire `README.md`, `AGENTS.md`, `registry/release_status.json`, `registry/current_run.json`, `registry/review_passes.json`, and the frozen MAGREST preregistration before making changes.

## Objective and values

Build a rigorous, reproducible, auditable project for the DOE GEMS fault-mapping competition. Work toward a competitive valid submission, but do not claim a competition score, geological discovery, uniqueness, or organizer acceptance without the evidence that supports it. Keep Arena's core values central:

- **Maximize P(Win)**: choose evidence-backed work that increases the chance of a valid, high-performing entry; do not trade scientific or submission integrity for an optimistic claim.
- **Own the Outcome**: report failures, fix verified defects, preserve negative evidence, and make every release decision reproducible without a human inspector.

The scientific target is faults absent from the public USGS/INGENIOUS catalogue—not geothermal favorability by itself. Preserve official-source links, evidence classes, data provenance, irregularities, limitations, and a useful static project-status feed. Never build a DrivenData leaderboard scraper/poller or automated uploader.

## Required focus-site review

Review the highest reported files from **GEMSDOE24, GEMSDOE25, GEMSDOE27, GEMSDOE28, GEMSDOE30, GEMSDOE31, GEMSDOE32, GEMSDOE33, and GEMSDOE36**. The executive summary must identify, for every site:

1. A pinned file link for study (not an upload recommendation).
2. The reported result and its provenance class.
3. A new-file score estimate only if supported by a validated, comparable method; otherwise write **unavailable / not estimable**, not a projection.
4. Computed uniqueness against the other focus sites, with the scope and rule stated.
5. Explicit download and submission permissions.

Analyze the GEMSDOE32 H33-2-B2 `0.2778` claim from exact artifact lineage, the official metric description recorded in the source register, and known limitations. Keep geometry separate from score causality. The user-supplied `0.3195` and `0.4413` leaderboard claims conflict and are not organizer receipts. Do not access or monitor the leaderboard; provide only its static manual-review URL.

## Hypothesis research before any experiment

Before implementing a scientific method, nominate and rank three to five hypotheses not already tested in this repository. For each state:

- exact input layer(s) and any required free, official external data;
- the physical signature/transform;
- why it could detect a fault missing from the existing catalogue rather than merely recover a known fault;
- what is genuinely new relative to code already present (including prior thermal, gravity, magnetic, seismicity, strain, and LiDAR work);
- the named non-fault mimic and principal resolution/leakage risks;
- qualitative expected holdout-DTI upside and implementation cost (no fabricated numeric gain); and
- whether the required source/product, coverage, license, and access were actually checked.

A source URL alone does not establish that a dataset is freely downloadable, licensed for the challenge, or sufficiently resolved. If access or license is unverified, mark the idea blocked rather than viable.

## Parallel-run protocol (binding)

1. **Lane:** work only in the explicitly assigned single method paragraph. Do not self-assign a lane if the paragraph is absent. Before placement and on final dots, compare against the complete scoped registry. Stop and record a duplicate if absolute rank correlation exceeds `0.90` or more than `70%` of candidate dots are within `3 px` of any one registry raster. No registry/control exemptions or density workarounds.
2. **Reuse:** use the pinned shared template's cached feature stack, `evaluate_holdout.py`, and `submission_writer.py`; do not fork the evaluator. Hide whole fault segments with an evidence-based buffer; build catalogue-derived features only from visible faults; mask visible faults pixel-exactly; score pooled DTI with alpha `0.2`, beta `0.8`, and the `300 m` triangular kernel.
3. **Provenance:** label every number with its evidence class. A holdout result is **HOLDOUT-DTI** plus evaluator version, withheld-positive count, and 95% CI. A competition score is **ORGANIZER-CONFIRMED** only when copied from an exact-file submission receipt. A model projection is never reported as a score.
4. **Leakage:** test each feature alone against the holdout before trusting results. AUC above `0.90` is leakage until disproven.
5. **Run card:** record hypothesis, mechanism, a named non-fault mimic, HOLDOUT-DTI and CI (or null with reason), pre-placement/final registry correlation and overlap, raster SHA-256, automated validator output (no NaN inside footprint, values in `[0,1]`, CRS/shape/transform), submission name and note (maximum 140 characters), and verdict `promote` or `negative`. Negative results are deliverables.
6. **Budget and promotion:** stop after three experiments or two hours, whichever comes first. A weekly slot is not used unless the candidate beats the same-run incumbent on the blocked holdout and passes the separate selector/confirmation process. Do not pick a slot in a research lane.

## Deliverables, verification, and access

Keep a clean GitHub Pages site with a prominent download/status decision and an executive-summary submission guide. A local validator must re-read output bytes and check one-band float32, exact sample-template CRS/shape/transform, finite footprint values in `[0,1]`, and the correct outside-footprint convention. A format pass alone never grants scientific, uniqueness, eligibility, or upload approval. State whether an artifact is research-download-only or actually cleared; do not label prior bytes as a new submission.

Use free, official/primary sources where available and link them for manual review. Mark what was fetched in the current environment versus what is only a prior repository citation. DrivenData private data is login-gated in the recorded evidence; no credentials are available in this task. No upload, account action, or leaderboard inspection is authorized here.

Run three cumulative passes: (1) implement and verify; (2) independently review for bugs, omissions, assumptions, leakage, provenance, and edge cases; (3) cross-check the complete request and rerun final checks. Record all passes, current blockers, exact verification outcomes, and next steps. Work only on the fixed active Arena branch supplied for this session; open and merge a PR only with verifiable GitHub status.
