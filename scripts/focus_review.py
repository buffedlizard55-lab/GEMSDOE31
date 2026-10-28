"""Fail-closed nine-site historical comparison. No network, fits, selection or TIFF writing."""
from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITES = (24, 25, 27, 28, 30, 31, 32, 33, 36)


def build(root=ROOT):
    root = Path(root)
    source = root / 'evidence/h33_forensics_20261025.json'
    forensic = json.loads(source.read_text())
    historical = json.loads((root / 'evidence/nine_site_forensic_audit.json').read_text())
    rows = []
    for site in SITES:
        name = f'GEMSDOE{site}'
        matches = [r for r in forensic['requested_site_comparison'] if r['repo'] == name]
        if len(matches) != 1:
            raise ValueError(f'expected exactly one historical focus artifact for {name}')
        r = matches[0]
        # These are historical user claims, not authenticated scores or predictions.
        if r['receipt_exists'] or r['organizer_confirmed_score'] is not None:
            raise ValueError('receipt schema changed: review provenance before publishing')
        prefix = f'data/prior_audit/{name}/'
        if not r['file'].startswith(prefix):
            raise ValueError('unexpected artifact provenance path')
        artifact = r['file'][len(prefix):]
        if artifact not in r['published_paths_matching_request']:
            raise ValueError('artifact not among pinned published files')
        holdouts = [h for h in historical['focus_submissions']
                    if h['site_tag'].split('-')[0] == name
                    and r['requested_artifact'] in h['artifact_path']]
        if len(holdouts) > 1:
            raise ValueError('ambiguous holdout evidence')
        proxy = holdouts[0].get('holdout_off_sgmc_4block') if holdouts else None
        rows.append(dict(site=name, historical_file=artifact, sha256=r['sha256'],
                         source_url=f"https://github.com/buffedlizard55-lab/{name}/blob/{r['ref']}/{artifact}",
                         reported_result=r['reported_value_quarantined'],
                         result_class='USER-REPORTED; not organizer-confirmed',
                         estimated_leaderboard_score=None,
                         estimate_reason='No validated cross-family calibration or organizer receipt',
                         sgmc_proxy_dti=proxy,
                         sgmc_proxy_provenance='CITED historical SGMC proxy; not rerun; not a hide-and-recover holdout',
                         unique_new_submission=False, ok_to_submit=False,
                         permission='PRIOR ART — learning only; do not resubmit'))
    return dict(review_id='20261027-3b1ed545', scope='Nine focus artifacts at pinned historical revisions; not a live or exhaustive site ranking',
                evidence_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                best_reported_site=max(rows, key=lambda r: r['reported_result'])['site'],
                selection_performed=False, new_tif_generated=False, submission_slots_used=0, rows=rows)


def section(root=ROOT):
    report = build(root)
    esc = html.escape
    rows = []
    for r in report['rows']:
        proxy = r['sgmc_proxy_dti']
        proxy_text = ('Not available for this exact artifact' if proxy is None else
                      f"COMPUTED SGMC-PROXY-DTI {proxy['mean_holdout_dti']:.4f}; 95% CI "
                      f"[{proxy['ci95_low']:.4f}, {proxy['ci95_high']:.4f}]; "
                      f"{proxy['withheld_positives_total']:,} proxy-positive pixels; "
                      f"{esc(proxy['evaluator_version'])}. Historical, cited, not rerun; not a hide-and-recover holdout.")
        rows.append(f'''<tr><td>{esc(r['site'])}</td><td><a href="{esc(r['source_url'])}">{esc(Path(r['historical_file']).name)}</a><br>
          <small>SHA-256: {esc(r['sha256'])}</small></td><td>{r['reported_result']:.4f} USER-REPORTED<br>Estimate: unavailable</td>
          <td>{proxy_text}</td><td>No — prior submission. DO NOT SUBMIT.</td></tr>''')
    return '''<section id="nine-site-decision"><h2>Nine focus sites: historical best reported entries, not upload recommendations</h2>
      <p><strong>Best historical claim: GEMSDOE32 (0.2778 USER-REPORTED). Approved new submission: NONE.</strong>
      Links below open pinned prior-art files for learning, not a new submission download. No organizer receipts exist in this evidence.
      These historical snapshots are not a current feed; later files and private submissions are not covered.</p>
      <div class="table-wrap"><table><thead><tr><th>Site</th><th>Historical file / pinned source</th><th>Reported result / estimated score</th>
      <th>Cited proxy evidence</th><th>Unique new file / permission</th></tr></thead><tbody>''' + ''.join(rows) + '''</tbody></table></div>
      <p>H33 removes 2,545 near-catalogue dots from H27 and adds zero, according to the frozen raster audit.
      This supports a pruning mechanism, not proof of why the private score improved. Hidden truth credit is unavailable.
      Historical inverse-score calculations do not establish causal discovery or forecast performance.</p>
      <p>The broad lattice witness independently blocks the usual dot budget. No selector was run and no weekly slot was used.
      A new experiment also lacks the single-method lane paragraph required by the prompt. No TIFF was generated in this review.</p></section>'''


if __name__ == '__main__':
    print(json.dumps(build(), indent=2, allow_nan=False))
