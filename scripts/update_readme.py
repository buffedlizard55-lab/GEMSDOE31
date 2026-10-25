#!/usr/bin/env python3
"""Generate the README's current decision and retain the entire standing owner brief."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def content():
    # This generator belongs to the archived TGJ31 release. Never replace the
    # integrated current README with an older lane's status or owner prompt.
    active = ROOT / "registry/current_run.json"
    if active.exists():
        current = json.loads(active.read_text())
        archived = json.loads((ROOT / "evidence/tgj31/run_card.json").read_text())
        if current.get("submission_name") != archived.get("submission_name"):
            raise ValueError("Archived TGJ31 README generator cannot overwrite the active integrated README")
    card = json.loads((ROOT / "evidence/tgj31/run_card.json").read_text())
    decision = json.loads((ROOT / "evidence/tgj31/decision.json").read_text())
    s = card["holdout_dti"]
    delta = decision["paired_metric_result"]
    prompt = (ROOT / "knowledge/owner_request_2026-10-25.md").read_text()
    site_pages = len(list((ROOT / "docs").rglob("*.html")))
    return f'''# GEMS31 — new fault-mapping research, an honest submission decision

**Read this README, the previous next steps, and the complete standing owner prompt below at the start of every session.** Maximize P(Win). Own the Outcome. Preserve negative evidence rather than spend scarce slots on unsupported claims.

## Download first — DO NOT SUBMIT

A **genuinely newly computed TIFF** exists. It was generated from RTP and gravity, not copied predictions. **It passes automated local format checks but fails scientific and literal protocol-uniqueness gates. It is NOT approved for competition upload.** Downloading the negative artifact is safe; submitting it is not authorized. No human TIFF inspection is required to reach this automated decision.

- **[Download the new TIFF — audit only]({card['files']['tif']}?raw=1)**
- [Single-TIFF ZIP — audit only]({card['files']['zip']}?raw=1)
- [Research site](https://buffedlizard55-lab.github.io/GEMSDOE31/) · [Executive summary / exact upload conditions](docs/executive-summary.html)
- [One JSON run card](evidence/tgj31/run_card.json) · [Automated gate decision](evidence/tgj31/decision.json) · [Frozen preregistration](knowledge/2026-10-25_transfer_preregistration.md)

**Unique name:** `{card['submission_name']}`

**Note ({card['note_characters']}/140):** `{card['note']}`

**TIFF SHA-256:** `{card['raster_sha256']}`

| Decision component | Automated outcome |
|---|---|
| Declared local on-disk format | PASS — 1 float32 band, EPSG:32611, 3730×3292, exact transform, finite [0,1], explicit zero outside; ZIP verified. Historical official null/NaN outside convention remains unverified; not portal conformity. |
| Range regression | Reject invalid inputs, no silent clipping; two independent on-disk format checks |
| Each-feature leakage canary | PASS; max symmetric AUC {card['leakage_canary']['max_symmetric_auc']:.6f}, below 0.90; not proof of no leakage |
| New content vs copied submission | Generated from raw features; TIFF SHA differs from all 1,005 restored prior hashes |
| Literal lane uniqueness | FAIL — full-support GEMSDOE48 witness gives every nonempty raster 100% forward overlap under the unchanged 3 px/70% rule |
| Scientific improvement | FAIL — lower pooled holdout DTI than same-input amplitude control; only {decision['quadrants_won_against_amplitude_control']}/4 quadrant wins |
| Current-best reproduction / fresh confirmation | Missing; historical H33 is not a fold-fair incumbent |
| Assigned lane / organizer sample authenticity | Missing; declared lane is not an assignment and owner-mirror hashes are not organizer authentication |
| Real weekly slot | NOT APPROVED; current weekly cap unverified; zero slots used |

**HOLDOUT-DTI ({s['evaluator_version']}, {s['withheld_positive_pixels']:,} withheld positives, 95% spatial-cluster CI): {s['dti']:.8f} [{s['ci95'][0]:.8f}, {s['ci95'][1]:.8f}].** Paired difference vs same-input amplitude control: **{delta['delta']:.8f} [{delta['ci95'][0]:.8f}, {delta['ci95'][1]:.8f}]**, same evaluator, positives and confidence level. The control has different confidence mass; this is not a matched-mass causal ablation. Public-fault/SGMC proxy intervals are not private-leaderboard intervals.

## What explains the reported H33 result?

[Exact forensics](evidence/h33_forensics_20261025.json) establish **H33 = H27 minus predictions at catalogue distance ≤2 px**: 40,199 → 37,654 cells, 2,545 deleted and none added. H27 = D2.8 with distance ≤1 px removed. This is a catalogue-flank pruning change, not a new geological detector. Sparse spacing and less false-positive mass can help a distance-tolerant metric **if** little hidden-truth credit is lost; that condition is not verifiable without private truth.

The owner's **0.2778**, and conflicting claimed current highs **0.3195 / 0.4413**, remain **USER-REPORTED-NOT-AUTHENTICATED**, not ORGANIZER-CONFIRMED. No receipt exists. GEMSDOE32's symmetric/calibrated LM instrument is arithmetically different from the shared pooled max-credit evaluator. No verified forecast of beating those values is supportable. See [scientific interpretation, source ledger and counterexample](knowledge/2026-10-25_scientific_review.md).

## What was completed, and what remains blocked

- Reviewed the previous next steps first; **restored and hash-verified all 11 declared raw/external inputs autonomously**. [Restoration receipt](evidence/data_restore_20261025.json), [grid/hash receipt](evidence/data_preparation_20261025.json), [19-band shared cache receipt](evidence/shared_feature_cache.json). Data placement is no longer the blocker in this workspace.
- Ranked four hypotheses before implementation. Selected exactly one: **TGJ31 multiscale local gravity–magnetic transfer-coefficient jumps**, with unfaulted lithologic/intrusive contacts as its explicit confounder. It used no catalogue/SGMC predictor, prior prediction, supervised training or GPU.
- Reused unchanged template57 cache preparation, evaluator, splitter and writer, [pinned at source](registry/shared_template.json), including original evaluator regression tests. Whole-component hide-and-recover, exact visible-pixel masking, pooled alpha .2 / beta .8 / triangular 300 m DTI, six feature canaries and 1,000 paired 30 km cluster resamples.
- Executed one frozen negative audit, stopped scientific work, and generated a new finite TIFF/ZIP with both local validators. No discrete dot placement or subsequent tuning. [Exact surface reconstruction](evidence/tgj31_exact_reconstruction_20261025.txt) reproduced the raw surface hash and every delivered pixel.
- Audited the nine requested sources and a broader **101-tree snapshot / 1,005 byte-distinct restored rasters**. **286 missing raster paths** and one off-grid focus format-test remain explicit errors. This is not an organizer-complete registry; the full-support witness independently proves the literal overlap failure.
- Rebuilt the {site_pages}-page site from evidence, removed the stale copied-incumbent "Submit it" recommendation, separated format/science/slot status, retained research and added an automatic public-GitHub source-status feed with a dated, twice-daily scheduled Pages snapshot fallback. The feed never claims live leaderboard access or re-validates changed upstream science.
- Concurrent main PR #11 was integrated without running its AS-1 lane. All candidate/evidence/code/registries and its separate negative run card are preserved in a [clearly blocked archive page](docs/lane.html). The expanded 12-input manifest was restored and hash/grid verified; the original TGJ31 still uses only its frozen inputs. Its suggestions for live probes/uniqueness waivers are not adopted.
- Historical supervised training is **not** claimed ready: the original arm trainer is absent and old OOF maps are not a comparable current best. The quoted older "GPU/data-only blocker" wording in the owner prompt below is superseded by this finding. Direct organizer authentication, private truth, receipts, current cap and an explicit lane assignment are still unavailable.

[Three cumulative review passes and tests](knowledge/2026-10-25_three_pass_review.md) · **[Prioritized next-session work](knowledge/2026-10-25_next_session.md)** · [Historical README preserved](knowledge/README_2026-10-04_archive.md) · [Full research archive](knowledge/)

## Reproduce the closed result; do not start a new lane

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/verify_tgj31.py        # committed TIFF/ZIP/format/hash/negative-decision checks
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .

# Optional exact physical reconstruction, not a new experiment:
.venv/bin/python scripts/download_competition_data.py
.venv/bin/python scripts/prepare_shared_cache.py
.venv/bin/python scripts/verify_tgj31.py --rebuild-surface

# Rebuild only presentation/registries, without touching scientific predictions:
.venv/bin/python scripts/collect_evidence.py
.venv/bin/python scripts/build_site.py
.venv/bin/python scripts/update_readme.py
.venv/bin/python scripts/check_site.py
```

Large rasters/caches remain ignored; compact pinned manifests make them restorable. The original one-shot runner refuses to re-open the closed experiment. Optional browser smoke checks use `scripts/smoke_site.cjs` with Playwright and packaged Chromium in an ignored local cache. CI verifies the small committed deliverable without restoring hundreds of MB.

## Standing owner prompt — reread every session

The full current owner brief follows. Its leaderboard numbers, previous assertions and access descriptions are **quoted requirements/context, not verified current findings**. Current evidence and limitations above govern scientific claims. Preserve the prompt and research when updating the project.

<details>
<summary>Expand the complete standing owner request (2026-10-25)</summary>

{prompt}
</details>
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    expected = content()
    if args.check:
        if (ROOT / "README.md").read_text() != expected:
            raise SystemExit("README is stale; run scripts/update_readme.py")
        print("README matches frozen evidence and preserves the complete owner prompt")
    else:
        (ROOT / "README.md").write_text(expected)
        print("Updated README decision and standing prompt")


if __name__ == "__main__":
    main()
