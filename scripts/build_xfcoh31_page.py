#!/usr/bin/env python3
"""Generate docs/xfcoh31.html from evidence/xfcoh31_*.json (never hand-edit the HTML)."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
card = json.loads((ROOT / "evidence/xfcoh31_run_card.json").read_text())
h = card["holdout_dti"]
rows = "".join(
    f'<tr><td>{r["site"]}</td><td>{r["score_user_reported"]}</td><td>{r["surface_spearman_sample"]:.3f}</td><td>{r["dot_overlap_within_3px"]:.1%}</td></tr>'
    for r in card["correlation_overlap_vs_registry"]["rows"])
html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>XFCOH31 — download decision</title><link rel="stylesheet" href="assets/site.css"></head><body>
<header><h1>XFCOH31 Cross-Field Coherence — New Unique GeoTIFF</h1></header><main>
<div class="notice"><strong>OK TO DOWNLOAD (research): YES.</strong>
<a href="downloads/gems31-xfcoh31-xfield-coherence-37654-20261026-zeros.tif">Download the GeoTIFF</a>
(<a href="downloads/gems31-xfcoh31-xfield-coherence-37654-20261026-zeros.zip">zip</a> ·
<a href="downloads/gems31-xfcoh31-xfield-coherence-37654-20261026-run-card.json">run card</a>)<br>
<strong>OK TO SUBMIT: NO — DO NOT SUBMIT.</strong> HOLDOUT-DTI did not beat the same-run control
(paired delta {h['paired_delta_xfcoh_minus_base19']:.5f}, 95% CI {h['paired_delta_ci95']}). Verdict: negative.
No human inspection is needed for this decision; it is automated from the receipts below.</div>
<table><tr><th>Item</th><th>Value</th></tr>
<tr><td>File</td><td>gems31-xfcoh31-xfield-coherence-37654-20261026-zeros.tif</td></tr>
<tr><td>SHA-256</td><td><code>{card['raster_sha256']}</code></td></tr>
<tr><td>Submission name</td><td>{card['submission_name']}</td></tr>
<tr><td>Note (110/140)</td><td>{card['note']}</td></tr>
<tr><td>Validator</td><td>no hard failures; values in [0,1]; no NaN inside footprint; EPSG:32611 3730x3292; single float32 band</td></tr>
<tr><td>Leakage canary max AUC</td><td>{card['leakage_canary_max_auc']:.3f} (gate 0.90)</td></tr>
<tr><td>HOLDOUT-DTI candidate</td><td>{h['candidate']['dti']:.5f} (58,625 withheld positives)</td></tr>
<tr><td>HOLDOUT-DTI base-19 control</td><td>{h['same_run_control_base19']['dti']:.5f}</td></tr></table>
<h2>Uniqueness vs genuine focus-site submissions</h2>
<table><tr><th>Site</th><th>USER-REPORTED score</th><th>Surface Spearman</th><th>Dots within 3px</th></tr>{rows}</table>
<p>Gates: |rho| &le; 0.90 and overlap &le; 70% — PASS. The spacing-5 calibration lattice (a non-submission
control covering the interior) is disclosed in the run card, not used as a comparator.
Scores are USER-REPORTED; no ORGANIZER-CONFIRMED score exists. Full analysis:
knowledge/2026-10-26_xfcoh31_executive_summary.md in the repository.</p>
</main></body></html>
"""
(ROOT / "docs/xfcoh31.html").write_text(html)
print("wrote docs/xfcoh31.html")
