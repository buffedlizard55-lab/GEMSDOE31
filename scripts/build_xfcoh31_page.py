#!/usr/bin/env python3
"""Generate the XFCOH31 decision page from its run card and exact-file audit."""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD_PATH = ROOT / "evidence/xfcoh31_run_card.json"
AUDIT_PATH = ROOT / "evidence/xfcoh31_registry_stop_audit.json"


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def pct(value: float) -> str:
    return f"{100 * value:.4f}%"


def build_page(card: dict | None = None, audit: dict | None = None) -> str:
    if card is None:
        card = json.loads(CARD_PATH.read_text())
    if audit is None:
        audit = json.loads(AUDIT_PATH.read_text())

    holdout = card["holdout_dti"]
    candidate = holdout["candidate"]
    control = holdout["same_run_control_base19"]
    focus = card["correlation_overlap_vs_registry"]
    within = audit["overlap"]["candidate_dots_within_3px_of_witness"]
    dots = audit["overlap"]["candidate_dots"]
    overlap = audit["overlap"]["fraction_within_3px"]
    delta_ci = holdout["paired_delta_ci95"]
    note_len = card.get("note_length", len(card["note"]))
    filename = Path(audit["candidate"]["path"]).name
    stem = filename.removesuffix("-zeros.tif")
    witness = audit["registry_witness"]["witness"]
    candidate_ci = candidate["ci95"]
    control_ci = control["ci95"]

    focus_rows = "".join(
        "<tr>"
        f"<td>{esc(row['site'])}</td>"
        f"<td>{row['score_user_reported']:.4f}</td>"
        f"<td>{row['surface_spearman_sample']:.4f}</td>"
        f"<td>{pct(row['dot_overlap_within_3px'])}</td>"
        "</tr>"
        for row in card["correlation_overlap_vs_registry"]["rows"]
    )

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="XFCOH31 final decision: research download only, DO NOT SUBMIT; fails HOLDOUT-DTI and literal shared-registry overlap gates.">
<title>XFCOH31 — final download decision · GEMSDOE31</title>
<link rel="stylesheet" href="assets/site.css"></head><body>
<header class="topbar"><div class="wrap topbar-inner"><a class="brand" href="index.html"><span class="brand-mark">G31</span><span>GEMSDOE31</span></a>
<nav class="nav" aria-label="Primary navigation"><a href="index.html">Overview</a><a href="executive-summary.html">Executive summary</a><a href="research.html">Research</a></nav></div></header>
<section class="page-hero"><div class="wrap"><p class="eyebrow">2026-10-26 · XFCOH31 final exact-file review</p>
<h1>Research download only.<br>DO NOT SUBMIT.</h1>
<p class="hero-lede">The existing TIFF passes local format checks, but its recorded HOLDOUT-DTI result is negative and its final dots fail the literal shared-registry overlap limit. No uniqueness or organizer acceptance is claimed.</p></div></section>
<main class="wrap">
<section class="notice notice-danger" role="alert">
<strong>DOWNLOAD FOR RESEARCH: YES · SUBMISSION: NO · DO NOT SUBMIT.</strong>
This is an already-existing research artifact, not an approved submission. The exact final TIFF has {within:,}/{dots:,} dots ({pct(overlap)}) within 3 px of the pinned <code>r13-lattice-s5</code> witness, exceeding the 70% STOP threshold. The holdout also fails against the same-run base-19 control. <strong>No new experiment, placement, or TIFF was made after this STOP.</strong>
</section>
<section><div class="section-head"><div><p class="kicker">Research-only file</p><h2>Exact artifact and separate permissions</h2></div>
<p>A local format pass is not a uniqueness pass, organizer acceptance, slot approval, or permission to submit.</p></div>
<div class="card download-card"><div class="actions">
<a class="button button-primary" href="downloads/{esc(filename)}" download>Download existing XFCOH31 research TIFF</a>
<a class="button" href="downloads/{esc(stem)}-zeros.zip" download>Single-TIFF ZIP</a>
<a class="button" href="downloads/{esc(stem)}-run-card.json" download>Complete run card</a>
<a class="button" href="downloads/{esc(stem)}-registry-audit.json" download>Exact registry audit JSON</a>
<a class="button" href="downloads/{esc(stem)}-format-check-all-finite.json" download>All-finite format receipt</a>
</div>
<div class="table-wrap"><table><tbody>
<tr><th>File</th><td><code>{esc(filename)}</code></td></tr>
<tr><th>SHA-256</th><td><code>{esc(card['raster_sha256'])}</code></td></tr>
<tr><th>Submission name (identity only)</th><td><code>{esc(card['submission_name'])}</code></td></tr>
<tr><th>Note</th><td><code>{esc(card['note'])}</code> ({note_len}/140 characters; not approval)</td></tr>
<tr><th>Local format validation</th><td>PASS, format-only; organizer acceptance not verified; no uniqueness implication</td></tr>
<tr><th>Download permission</th><td><strong>YES — research only</strong></td></tr>
<tr><th>Submit / promote / weekly slot</th><td><strong>NO — NEGATIVE — DO NOT SUBMIT; <code>slot_approved = false</code></strong></td></tr>
<tr><th>Separate run records</th><td>H31-S remains in <code>registry/h31s_current_run.json</code>; MAGREST remains in <code>registry/current_run.json</code>. Neither is this XFCOH31 file.</td></tr>
</tbody></table></div>
</div></section>
<section><div class="section-head"><div><p class="kicker">HOLDOUT-DTI · not a competition score</p><h2>Negative against the same-run control</h2></div>
<p>Evaluator <code>{esc(holdout['evaluator_version'])}</code> · {candidate['withheld_positive_pixels']:,} withheld positives · pooled DTI · 1,000 spatial-block bootstrap resamples over 186 blocks.</p></div>
<div class="table-wrap"><table><thead><tr><th>Arm / contrast</th><th>HOLDOUT-DTI</th><th>95% CI</th><th>Interpretation</th></tr></thead><tbody>
<tr><td>XFCOH31</td><td>{candidate['dti']:.7f}</td><td>[{candidate_ci[0]:.7f}, {candidate_ci[1]:.7f}]</td><td>Candidate</td></tr>
<tr><td>Same-run base-19 control</td><td>{control['dti']:.7f}</td><td>[{control_ci[0]:.7f}, {control_ci[1]:.7f}]</td><td>Control scores higher</td></tr>
<tr><td>Paired XFCOH31 minus base-19</td><td>{holdout['paired_delta_xfcoh_minus_base19']:+.7f}</td><td>[{delta_ci[0]:+.7f}, {delta_ci[1]:+.7f}]</td><td><strong>Preregistered efficacy gate failed</strong></td></tr>
</tbody></table></div>
<p class="small">These are HOLDOUT-DTI values from the recorded run, not leaderboard scores or projections. The committed result JSON retains pooled scores and bootstrap summaries but not per-block sufficient statistics needed to independently replay the paired CI. See the protocol-compliance notes in the run card.</p>
</section>
<section><div class="section-head"><div><p class="kicker">Literal shared registry</p><h2>Exact final-dot overlap triggers STOP</h2></div>
<p>One verified registered counterexample is enough to fail this existential rule; no exhaustive registry pass is claimed.</p></div>
<div class="table-wrap"><table><tbody>
<tr><th>Registry manifest</th><td><code>{esc(audit['registry_witness']['manifest'])}</code>; SHA-256 <code>{esc(audit['registry_witness']['manifest_sha256'])}</code>; {audit['registry_witness']['registered_rasters_in_manifest']} rasters pinned</td></tr>
<tr><th>Witness</th><td><code>r13-lattice-s5</code>; SHA-256 <code>{esc(witness['sha256'])}</code>; authenticated source <a href="{esc(witness['source_url'])}">pinned repository file</a></td></tr>
<tr><th>Rasters examined</th><td>{audit['registry_witness']['rasters_examined']} of {audit['registry_witness']['registered_rasters_in_manifest']} (not exhaustive)</td></tr>
<tr><th>Full-footprint Spearman rho</th><td>{audit['correlation']['spearman_rho']:.10f} (absolute limit {audit['correlation']['limit']:.2f}; PASS)</td></tr>
<tr><th>Final dots within 3 px</th><td>{within:,} / {dots:,} = {pct(overlap)} (limit {100*audit['overlap']['limit']:.0f}%; <strong>FAIL / STOP</strong>)</td></tr>
<tr><th>Global uniqueness decision</th><td><strong>NOT ESTABLISHED; literal overlap STOP</strong></td></tr>
<tr><th>Pre-placement shared-registry surface check</th><td>Not performed for this existing run; no broad surface search or new placement was run after the final-dot STOP.</td></tr>
</tbody></table></div>
<p>The witness is a calibration raster, but the standing rule applies to every shared-registry raster. No density, calibration, or “non-submission control” exemption is applied. The measured overlap is not a byte-identity finding.</p>
</section>
<section><div class="section-head"><div><p class="kicker">Limited comparator subset</p><h2>Focus-site separation is not global uniqueness</h2></div>
<p>The earlier comparison covers named genuine GEMSDOE24/25/27/28/30/31/32/33/36 files only. Its pass cannot override the shared-registry witness.</p></div>
<div class="table-wrap"><table><thead><tr><th>Named comparator</th><th>USER-REPORTED score</th><th>Surface Spearman sample</th><th>Final-dot 3-px overlap</th></tr></thead><tbody>{focus_rows}</tbody></table></div>
<p><strong>Subset-only result:</strong> max surface Spearman {focus['max_surface_spearman']:.4f}; max 3-px overlap {pct(focus['max_dot_overlap_within_3px'])}. Scores are USER-REPORTED, not organizer-confirmed. This table is not a full-registry uniqueness approval.</p>
</section>
<section><div class="section-head"><div><p class="kicker">Validation provenance</p><h2>Format checks and workflow limits</h2></div>
<p>Review separates the file’s technical format from the scientific, registry, and governance gates.</p></div>
<div class="grid grid-2"><div class="card"><h3>Technical format</h3><p>One float32 band · EPSG:32611 · 3730 × 3292 · exact 100 m transform · {dots:,} positive dots · zero NaN/Inf in the footprint · all values in [0,1]. Local all-finite hard failures: {len(audit['format_validation']['hard_failures'])}. Organizer acceptance: <strong>not verified</strong>.</p><p><a href="downloads/{esc(stem)}-format-check-all-finite.json">All-finite receipt</a> · <a href="downloads/{esc(stem)}-format-check-nan-outside.json">NaN-outside receipt</a>.</p></div>
<div class="card"><h3>Recorded protocol deviations</h3><ul>
<li>Fresh feature memmap instead of the template cached stack.</li>
<li>Direct holdout module calls rather than the requested <code>evaluate_holdout.py</code> wrapper.</li>
<li>Direct TIFF/ZIP writing rather than the requested shared <code>submission_writer.py</code>.</li>
<li>Feature-only canary against visible catalogue labels, not the preregistered fold-pooled withheld-truth canary.</li>
<li>Fixed 21.25 km collar inherited from the shared template, not re-estimated for this lane.</li>
</ul><p>No rerun is authorized: the experiment budget is spent and this exact final file fails the literal registry gate.</p></div></div>
</section>
<section><div class="section-head"><div><p class="kicker">No leaderboard scraping or submission</p><h2>Sources and independent confirmation</h2></div><p>No organizer-confirmed score or acceptance receipt is recorded.</p></div>
<ul>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">Official competition page</a> (not freshly fetched here).</li>
<li><a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">Competition rules PDF</a> (not freshly fetched here).</li>
<li><a href="https://github.com/drivendataorg/gems-prize-reference-solution">Organizer reference solution</a>.</li>
<li><a href="https://doi.org/10.5066/P93LGLVQ">USGS GeoDAWN</a> and <a href="https://epsg.io/32611">EPSG:32611</a> reference pages (not freshly fetched here).</li>
</ul>
<p class="small">No DrivenData leaderboard access, upload, score submission, or organizer contact occurred. Official-source links are references only; non-GitHub hosts were not freshly retrieved under this environment’s host restrictions.</p>
<p>Detailed summary: <a href="https://github.com/buffedlizard55-lab/GEMSDOE31/blob/main/knowledge/2026-10-26_xfcoh31_executive_summary.md">nine-site executive summary and ranked hypotheses</a> · <a href="https://github.com/buffedlizard55-lab/GEMSDOE31/blob/main/knowledge/session_review_2026-10-26_xfcoh31.md">three-pass review</a>.</p>
</section>
</main><footer class="footer"><div class="wrap footer-inner"><p>Maximize P(Win) · Own the Outcome · negative results preserved.</p><p><a href="index.html">Home</a> · <a href="executive-summary.html">Submission workflow</a></p></div></footer>
</body></html>
"""


def main() -> None:
    page = build_page()
    (ROOT / "docs/xfcoh31.html").write_text(page)
    print("wrote docs/xfcoh31.html")


if __name__ == "__main__":
    main()
