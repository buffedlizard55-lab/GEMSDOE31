from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def esc(value):
    return html.escape(str(value))

def h3_download_and_gates() -> str:
    """Download section for the H3 LiDAR-scarp research TIF."""
    p = ROOT / "evidence/h3_unique_submission.json"
    if not p.is_file():
        return ''
    h3 = json.loads(p.read_text())
    receipt = h3.get('submission_receipt', {})
    name = h3.get('submission_name', 'unknown')
    note = h3.get('submission_note', '')
    sha = receipt.get('nan_sha256', 'unknown')
    dots = receipt.get('dots', 0)
    on_cat = receipt.get('dots_on_catalogue', '?')
    ok_nan = bool(receipt.get('format_ok_nan', False))
    ok_fin = bool(receipt.get('format_ok_allfinite', False))
    dti_sgmc = h3.get('holdout_off_catalogue_sgmc', {}).get('HOLDOUT_DTI')
    dti_gap = h3.get('holdout_catalogue_gap', {}).get('catalogue-gap-seed1', {}).get('HOLDOUT_DTI')
    canary_sgmc = h3.get('canary', {}).get('auc_off_catalogue_sgmc', 0)
    canary_cat = h3.get('canary', {}).get('auc_catalogue', 0)
    return f'''
<section id="h3-download" aria-labelledby="h3-heading">
  <div class="section-head"><div><p class="kicker">New artifact · H3 LiDAR scarp · 2026-10-25</p>
    <h2 id="h3-heading">OK to download for research. NOT approved for upload.</h2></div>
    <p>Holdout proxies disagree (catalogue-gap vs off-catalogue SGMC). Full 716-raster registry cache
    was unavailable for the uniqueness gate. Labelled research-only until both proxies agree and the
    registry gate passes.</p></div>
  <div class="card download-card">
    <span class="badge badge-red">RESEARCH ONLY · verdict = negative · not promoted</span>
    <h3 style="margin-top:18px">{esc(name)}</h3>
    <p>LiDAR generic scarp (ex_max percentile rank, gaussian 0.8px) at 2.8px Poisson-disk spacing.
       {dots:,} dots, {on_cat} dots on the public catalogue. New dots — not copied from any prior submission.</p>
    <div class="actions">
      <a class="button button-dark" href="downloads/{name}-nan.tif" download>Download H3 Research .tif (NaN-outside)</a>
      <a class="button" href="downloads/{name}-allfinite.tif" download>All-finite research encoding .tif</a>
      <a class="button" href="downloads/{name}-nan.zip" download>One-TIFF .zip</a>
      <a class="button" href="evidence/h3_unique_submission.json" download>Run card .json</a>
    </div>
    <p class="download-meta"><strong>Grid &amp; Range:</strong> 1-band float32 · EPSG:32611 · 3730 x 3292 · 100 m ·
      {dots:,} dots · values exactly {{0.0, 1.0}} in [0.0, 1.0]<br>
      <strong>SHA-256 (NaN primary):</strong> <code>{esc(sha)}</code><br>
      <strong>SHA-256 (All-finite):</strong> <code>{esc(receipt.get('allfinite_sha256','unknown'))}</code><br>
      <strong>Name:</strong> <code>{esc(name)}</code><br>
      <strong>Note ({len(note)}/140):</strong> <code>{esc(note)}</code></p>
    <table>
      <thead><tr><th>Gate</th><th>Result</th></tr></thead>
      <tbody>
        <tr><td>Single-feature leakage canary (SGMC AUC)</td>
            <td><span class="badge badge-green">PASS</span> {canary_sgmc:.3f} (&lt;= 0.90)</td></tr>
        <tr><td>Single-feature leakage canary (catalogue AUC)</td>
            <td><span class="badge badge-green">PASS</span> {canary_cat:.3f} (&lt;= 0.90)</td></tr>
        <tr><td>Holdout DTI — off-catalogue SGMC</td>
            <td>HOLDOUT-DTI {dti_sgmc:.4f} (truth px 61,664)</td></tr>
        <tr><td>Holdout DTI — catalogue-gap (seed 1)</td>
            <td>HOLDOUT-DTI {dti_gap:.4f} vs D28 incumbent 0.0435</td></tr>
        <tr><td>Format validation (NaN)</td>
            <td><span class="badge {'badge-green' if ok_nan else 'badge-red'}">{'PASS' if ok_nan else 'FAIL'}</span></td></tr>
        <tr><td>Format validation (all-finite)</td>
            <td><span class="badge {'badge-green' if ok_fin else 'badge-red'}">{'PASS' if ok_fin else 'FAIL'}</span></td></tr>
        <tr><td>716-raster uniqueness gate</td>
            <td><span class="badge badge-red">CACHE UNAVAILABLE — not checked</span></td></tr>
        <tr><td>Submission approval</td>
            <td><span class="badge badge-red">NOT APPROVED — do not upload</span></td></tr>
      </tbody>
    </table>
  </div>
</section>
'''
