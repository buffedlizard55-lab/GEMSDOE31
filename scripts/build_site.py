#!/usr/bin/env python3
"""Generate the public audit site from frozen, typed evidence (never hand-copy scores)."""
from __future__ import annotations

import html
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
REPO = "https://github.com/buffedlizard55-lab/GEMSDOE31"
GH = REPO + "/blob/main/"
HISTORY = [
    ("01-arms", "Original same-family feature arms", "evidence/arm_results.json"),
    ("02-operating-points", "Historical operating-point experiment", "evidence/operating_point.json"),
    ("03-collar-sensitivity", "Catalogue-collar sweep", "evidence/collar_sweep.json"),
    ("04-incumbent-filter", "Historical incumbent filtering", "evidence/incumbent_filter_results.json"),
    ("05-addition-arm", "Historical LiDAR union", "evidence/union_results.json"),
    ("06-buffer-derivation", "Inherited residual buffer", "evidence/buffer_derivation.json"),
    ("07-oof-maps", "Historical quantized OOF maps", "evidence/oof_quantisation.json"),
    ("08-h31a-pilot", "Stopped H31-A pilot", "evidence/h31_a/pilot/results.json"),
    ("09-pilot-variogram", "Historical H31-A variogram", "evidence/h31_a/pilot/posthoc_variogram_diagnostics.json"),
    ("10-submission-format", "Historical format checks", "registry/submissions.json"),
    ("11-score-claims", "Historical score/source audit", "knowledge/score_and_prior_art_review_2026-10-03.md"),
]



def read(path):
    return json.loads((ROOT / path).read_text())


def e(value):
    return html.escape("Not recorded" if value is None else str(value), quote=True)


def link(url, title):
    return f'<a href="{e(url)}">{e(title)}</a>'


def local(page, target):
    return os.path.relpath(DOCS / target, (DOCS / page).parent).replace(os.sep, "/")


def table(headers, rows):
    return '<div class="table-scroll"><table><thead><tr>' + ''.join(f'<th scope="col">{e(h)}</th>' for h in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in row) + '</tr>' for row in rows) + '</tbody></table></div>'


def main():
    card = read("evidence/tgj31/run_card.json")
    decision = read("evidence/tgj31/decision.json")
    holdout = read("evidence/tgj31/holdout.json")
    forensic = read("evidence/h33_forensics_20261025.json")
    register = read("registry/submissions.json")
    sources = read("registry/sources.json")
    inventory = read("registry/prior_raster_snapshot.json")
    if card["safe_to_submit"] or decision["safe_to_submit"] or decision["verdict"] != "negative":
        raise ValueError("This site's active artifact is a closed negative run; never silently turn it into a submission")
    data_dir = DOCS / "data/tgj31"
    data_dir.mkdir(parents=True, exist_ok=True)
    for p in sorted((ROOT / "evidence/tgj31").glob("*.json")):
        shutil.copyfile(p, data_dir / p.name)
    shutil.copyfile(ROOT / "evidence/h33_forensics_20261025.json", DOCS / "data/h33-forensics.json")
    shutil.copyfile(ROOT / "registry/submissions.json", DOCS / "data/submissions.json")
    shutil.copyfile(ROOT / "evidence/data_restore_20261025.json", DOCS / "data/input-restoration.json")
    score = card["holdout_dti"]
    scope = 'HOLDOUT-DTI · ' + e(score["evaluator_version"]) + f' · {score["withheld_positive_pixels"]:,} withheld positive pixels · 95% spatial-cluster CI'
    shared_ref = card["lineage"]["shared_template_ref"]
    template_url = 'https://github.com/buffedlizard55-lab/57GEMSDOE/tree/' + shared_ref
    health_sources = [{"repo": 'buffedlizard55-lab/' + row["repo"], "pin": row["ref"]}
                      for row in forensic["requested_site_comparison"]]
    health_sources.append({"repo": "drivendataorg/gems-prize-reference-solution", "pin": "aebe92f7c8a990f0e3443451b7a825d9afd6336b"})
    feed = {
        "schema_version": 2, "last_scientific_run_utc": card["date_utc"],
        "scientific_run_closed": True, "update_policy": "Browser automatically checks public GitHub source status, at most once per hour. Frozen scientific results do not change. No leaderboard polling or uploads.",
        "status": "negative; DO NOT SUBMIT; no organizer receipt", "safe_to_submit": False,
        "slot_approved": False, "organizer_confirmed_score": None, "current_weekly_cap_verified": False,
        "submission_name": card["submission_name"], "files": card["files"], "sha256": card["raster_sha256"],
        "holdout": score, "decision": decision, "public_sources": health_sources,
    }
    (DOCS / "feed.json").write_text(json.dumps(feed, indent=1, allow_nan=False) + "\n")

    def href(page, target, title):
        return link(local(page, target), title)

    def source(path, title):
        return link(GH + path, title)

    def alert():
        return '<aside class="decision-banner" role="note"><strong>DO NOT SUBMIT</strong><span>Newly generated research artifact. Local format checks pass; scientific and literal uniqueness gates fail. Zero competition slots used.</span></aside>'

    def downloads(page):
        return f'''<div class="download-row">{link(local(page, card['files']['tif'].removeprefix('docs/')), 'Download submission TIFF (audit only)').replace('<a ', '<a download ', 1)}{link(local(page, card['files']['zip'].removeprefix('docs/')), 'Download single-TIFF ZIP').replace('<a ', '<a download ', 1)}</div><p class="small">These files are safe to download for research, <strong>not approved to upload</strong>. Both contain the same new continuous surface, not copied predictions.</p>'''

    def write(page, title, body, active=""):
        nav = [("index.html", "Overview"), ("executive-summary.html", "Download & decision"),
               ("research.html", "Research"), ("validation.html", "Validation"),
               ("register/index.html", "Artifacts"), ("sources.html", "Sources"), ("feed.html", "Status feed")]
        navigation = ''.join(f'<a href="{e(local(page, p))}"' + (' aria-current="page"' if p == active else '') + f'>{e(t)}</a>' for p, t in nav)
        out = DOCS / page
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="New GEMS fault-mapping research, reproducible evidence and an honest submission decision."><title>{e(title)} · GEMS31</title><link rel="stylesheet" href="{e(local(page, 'assets/site.css'))}"></head>
<body data-safe-to-submit="false"><a class="skip" href="#main">Skip to content</a><header><div class="masthead"><a class="brand" href="{e(local(page, 'index.html'))}">GEMS<span>31</span><small>FAULT MAPPING RESEARCH</small></a><span class="header-status">Scientific run closed · {e(card['date_utc'])}</span></div><nav aria-label="Main">{navigation}</nav></header>
<main id="main">{body}</main><footer><strong>Maximize P(Win). Own the Outcome.</strong><p>Preserve negative evidence. Protect scarce submission slots. Format validity is not scientific approval.</p><div>{href(page, 'experiments/index.html', 'Research archive')} · {href(page, 'ai-disclosure.html', 'AI disclosure')} · {link(REPO, 'Repository')} · {href(page, 'data/tgj31/run_card.json', 'JSON run card')} · {href(page, 'feed.json', 'Machine-readable feed')}</div><p class="small">Pinned public-owner mirrors are not organizer authentication. No organizer-confirmed score or live leaderboard claim is made.</p></footer></body></html>\n''')

    prereg = (ROOT / "knowledge/2026-10-25_transfer_preregistration.md").read_text()
    ranked_rows = []
    for line in prereg.splitlines():
        if line.startswith("| "):
            cells = [c.strip().replace("**", "").replace("`", "") for c in line.strip("| ").split("|")]
            if cells[0] in ("1", "2", "3", "4"):
                ranked_rows.append([e(c) for c in cells])
    if len(ranked_rows) != 4:
        raise ValueError("frozen preregistration must supply the four ranked hypotheses")
    ranked_table = table(["Expected-benefit rank", "Exact layers / hypothesis", "Physical signature", "Difference from reviewed code", "Nonfault mimic", "Cost / availability"], ranked_rows)

    results_rows = []
    names = {"TGJ31": "TGJ31 transfer jumps (new)", "amplitude_control": "Same-input amplitude control", "H33_as_is_noncomparable": "H33 as-is (not fold-fair; descriptive only)"}
    for key, result in holdout["scores"].items():
        results_rows.append([e(names[key]), f'{result["dti"]:.6f}', f'[{result["ci95"][0]:.6f}, {result["ci95"][1]:.6f}]', f'{result["withheld_positive_pixels"]:,}'])
    result_table = f'<p class="eyebrow">{scope}</p>' + table(["Artifact / control", "Pooled DTI", "95% CI", "Withheld positives"], results_rows)
    delta = holdout["paired_differences"]["amplitude_control"]
    delta_text = f'<p><strong>Paired HOLDOUT-DTI difference vs amplitude control: {delta["delta"]:.6f}</strong> (95% CI [{delta["ci95"][0]:.6f}, {delta["ci95"][1]:.6f}]; {e(score["evaluator_version"])}, {score["withheld_positive_pixels"]:,} withheld positives). Wins {decision["quadrants_won_against_amplitude_control"]}/4 quadrants. No same-run current-best reproduction or fresh confirmation.</p>'
    limitations = '<p class="callout">The control has different confidence mass; this is not a matched-mass causal comparison. Intervals are conditional on public proxy labels, the fixed split and parameters, not leaderboard intervals. The 21.3 km buffer was inherited from historical residuals, not re-estimated from this operator. SGMC is a secondary diagnostic only.</p>'

    page = "index.html"
    write(page, "An honest decision, a new TIFF", f'''<section class="hero"><p class="eyebrow">GEOTHERMAL CONTEXT. FAULT-MAPPING TARGET.</p><h1>A new TIFF.<br>An honest decision.</h1><p class="lede">One gravity–magnetic hypothesis. One whole-segment holdout test. A new TIFF that did not earn a submission slot.</p></section>{alert()}{downloads(page)}<div class="metric-grid"><article><span>LOCAL FORMAT</span><h2>PASS</h2><p>Single float32 band. Finite [0,1]. Exact template grid. ZIP checked.</p></article><article><span>SCIENTIFIC RESULT</span><h2>NEGATIVE</h2><p>Lower pooled holdout DTI than the same-input control.</p></article><article><span>PROTOCOL UNIQUENESS</span><h2>FAIL</h2><p>A dense prior forces 100% literal overlap. No exemption applied.</p></article></div><section><h2>What was actually measured</h2>{result_table}{delta_text}{limitations}{href(page, 'validation.html', 'Read the full automated gate report')}</section><section class="split"><div><p class="eyebrow">WHY H33 CHANGED THE GEOMETRY</p><h2>Pruning, not a new detector.</h2><p>H33 is exactly H27 with 2,545 catalogue-flank pixels removed: 40,199 → 37,654 predictions. It adds no new detector information. Its reported organizer result has no receipt here.</p>{href(page, 'research.html', 'Read the H33 forensic explanation')}</div><div><p class="eyebrow">WHAT COMES NEXT</p><h2>Resolve gates before another experiment.</h2><p>Complete the registry, obtain an owner-assigned lane and authentic submission-page evidence, and reproduce the best incumbent with visible-only features. Then preregister a different hypothesis. No tuning of this closed negative lane.</p>{source('knowledge/2026-10-25_next_session.md', 'Prioritized next-session plan')}</div></section>''', page)

    page = "executive-summary.html"
    write(page, "Download & submission decision", f'''<p class="eyebrow">EXECUTIVE SUMMARY</p><h1>Download is ready.<br>Submission is blocked.</h1>{alert()}{downloads(page)}<h2>Exact new file and note</h2><dl><dt>Submission name</dt><dd><code class="wrap">{e(card['submission_name'])}</code></dd><dt>Short comment · {card['note_characters']} / 140 characters</dt><dd><code class="wrap">{e(card['note'])}</code></dd><dt>SHA-256 · TIFF</dt><dd><code class="wrap">{e(card['raster_sha256'])}</code></dd></dl><p>{href(page, 'data/tgj31/run_card.json', 'Download the JSON run card')} · {href(page, 'data/tgj31/decision.json', 'Read the machine decision')}</p><h2>How to enter an approved future file</h2><p><strong>Do not perform these upload steps with today's file.</strong> They describe the submission form supplied by the owner, not a verified current cap or an authorization.</p><ol class="steps"><li>Wait for an automated research promotion: format, canary, complete literal registry scan, comparable incumbent improvement and fresh spatial confirmation must all pass.</li><li>A separate selector must authorize a real slot against the current weekly cap shown on the authenticated submission page. This project used no slots and does not operate the portal.</li><li>Open {link('https://www.drivendata.org/competitions/306/competition-doe-gems/', 'the official DrivenData competition')}, sign in and choose <strong>New submission</strong>.</li><li>In <strong>File to submit</strong>, choose the selector-approved single-band <code>.tif</code>, or its <code>.zip</code> containing exactly one TIFF. Do not select a JSON report or an old copied reference.</li><li>Paste that artifact's unique name and at-most-140-character note. Submit once, save the submission-page receipt and exact file SHA-256. Only a receipt can establish ORGANIZER-CONFIRMED performance or acceptance.</li></ol><h2>The range error is guarded automatically</h2><p>The shared writer rejects nonfinite or out-of-range footprint values before casting or serialization; it does not clip them into compliance. Both validators re-read the actual on-disk TIFF. The ZIP is unpacked and checked against the same bytes. This file's measured range is [{card['validator_output']['range'][0]:.1f}, {card['validator_output']['range'][1]:.9f}], with zero NaN or Inf anywhere and zeros outside the footprint.</p><p>A local preflight cannot promise portal acceptance or a high score. {href(page, 'validation.html', 'See the exact grid and all gates.')}</p>''', page)

    page = "validation.html"
    gate_names = {"format": "On-disk grid, dtype, finite values and [0,1]", "leakage_canary": "Each individual feature canary", "literal_registry": "Full literal registry uniqueness", "paired_metric_improvement": "Paired lower CI above zero vs same-input control", "three_quadrant_wins": "Improvement in at least 3/4 quadrants", "current_best_reproduced": "Comparable current-best reproduction", "fresh_confirmation": "Independent fresh confirmation", "owner_assigned_lane": "Owner-assigned method paragraph", "organizer_template_authenticated": "Organizer-authenticated sample/template"}
    gates_table = table(["Automated gate", "Result"], [[e(gate_names[k]), '<strong class="' + ('pass' if v else 'fail') + '">' + ('PASS' if v else 'BLOCKED / FAILED') + '</strong>'] for k, v in decision["gates"].items()])
    v = card["validator_output"]
    checks = [["Band / dtype", "1 / float32"], ["CRS", "EPSG:32611"], ["Rows × columns", "3730 × 3292"], ["Transform", "(100, 0, 243350, 0, -100, 4508550)"], ["Footprint", "5,167,373 finite template cells"], ["NaN inside / anywhere", f'{v["nan_inside_footprint"]} / {v["nan_anywhere"]}'], ["Measured range", e(v["range"])], ["Outside footprint", "All zero"], ["ZIP", "Exactly one byte-identical TIFF"], ["Organizer upload acceptance", "NOT VERIFIED"]]
    overlap = card["correlation_overlap_vs_registry"]
    write(page, "Automated validation", f'''<p class="eyebrow">AUTOMATED, FAIL-CLOSED</p><h1>Format is not approval.</h1>{alert()}{gates_table}<p>{href(page, 'data/tgj31/decision.json', 'Machine-readable decision')} · {href(page, card['files']['writer_receipt'].removeprefix('docs/'), 'Shared validator')} · {href(page, 'data/tgj31/independent_format_validation.json', 'Independent validator')}</p><h2>Exact output contract</h2>{table(['Check', 'Measured result'], checks)}<p class="callout">Outside encoding is an explicit local policy, not verified portal conformity. The mandated shared writer uses finite zeros outside the footprint. A concurrent historical audit notes that the recorded official page describes null/NaN outside bounds; that convention has not been re-authenticated here. Both local validators pass the declared all-finite policy, not every possible organizer convention. No encoding retuning or upload is authorized.</p><h2>Hide-and-recover, not random patches</h2><p>Unchanged {link(template_url, 'shared57 evaluator and submission writer')}; {e(score['evaluator_version'])} and <code>label-blind-quadrants-v2</code>. Whole connected fault components are withheld across quadrant boundaries; 213 px exclusion buffer. Catalogue-derived predictors are absent. Visible catalogue pixels are masked exactly, never by a scoring dilation. Pooled DTI uses alpha 0.2, beta 0.8 and a 300 m triangular kernel. Bootstrap: 1,000 paired 30 km spatial clusters, seed 20261025.</p>{result_table}{delta_text}{limitations}<h2>Leakage canary</h2><p>All six feature-alone probes were tested on every eligible holdout. Maximum symmetric AUC {card['leakage_canary']['max_symmetric_auc']:.6f}, below the 0.90 alarm threshold. Passing a canary is not proof of no leakage. {href(page, 'data/tgj31/leakage_canary.json', 'All feature-level canaries')}.</p><h2>Both literal registry checks</h2><p>The mandatory nine-site audit indexed 87 byte-distinct rasters; 86 matched the grid. One explicit GEMSDOE36 format-test raster is off-grid and remains a recorded failure, not silently excluded. Highest observed Spearman correlation across the surface/final checks: {overlap['required_nine_max_spearman']:.6f}. Maximum forward 3 px overlap: {overlap['required_nine_surface_max_overlap']:.6%} before the exact catalogue mask; {overlap['required_nine_final_max_overlap']:.6%} on final continuous support.</p><p><strong>Extended universal blocker:</strong> a pinned GEMSDOE48 continuous prior is positive on every one of the 5,167,373 eligible cells. Every nonempty candidate therefore has 100% forward overlap under the owner's literal finite &gt; 0, 3 px rule and fails the 70% gate. There is no density exemption. The generated file is new content, but <strong>not protocol-unique</strong>.</p><p>No discrete dot placement or subsequent tuning occurred. The file packages the frozen continuous response for a negative audit only. The STOP verdict is not waived to satisfy the download requirement.</p><p>{href(page, 'data/tgj31/registry_surface.json', 'Surface audit')} · {href(page, 'data/tgj31/registry_final_support.json', 'Final-support audit')} · {href(page, 'data/tgj31/registry_universal_blocker.json', 'Saturation certificate')}</p><h2>Reproduce and verify</h2><pre>python -m venv .venv\n.venv/bin/pip install -r requirements.txt\n.venv/bin/python scripts/verify_tgj31.py\n# Optional: restore hash-pinned inputs, then prove exact surface reproduction\n.venv/bin/python scripts/download_competition_data.py\n.venv/bin/python scripts/prepare_shared_cache.py\n.venv/bin/python scripts/verify_tgj31.py --rebuild-surface\n.venv/bin/python -m pytest -q\n.venv/bin/python scripts/collect_evidence.py\n.venv/bin/python scripts/build_site.py\n.venv/bin/python scripts/check_site.py</pre><p>The original one-shot runner refuses to re-open this closed experiment. Exact reconstruction verifies hashes and output pixels, not a new trial. Historical supervised training is not claimed reproducible; its original trainer is absent.</p>''', page)

    page = "research.html"
    comparison = table(["Requested source", "Named artifact", "Measured positive cells", "Evidence"], [[link(r['source_url'], r['repo']), e(r['requested_artifact']), f"{r['positive_pixels']:,}" if 'positive_pixels' in r else 'Unavailable', 'Raster measurement; no organizer receipt'] for r in forensic['requested_site_comparison']])
    write(page, "Research & H33 forensics", f'''<p class="eyebrow">PHYSICS FIRST. EVIDENCE BEFORE PROMOTION.</p><h1>What explains H33?<br>What did we test?</h1><h2>H33: a precise geometric explanation, not private-truth causation</h2><p>Byte-pinned comparisons establish H33 = H27 with predictions at catalogue distance ≤ 2 px removed. H27 itself equals D2.8 with predictions at distance ≤ 1 px removed. H33 adds zero predictions and deletes 2,545 from H27, leaving 37,654. The closest retained catalogue distance is √5 px; minimum dot-to-dot spacing is about 283 m, median 300 m.</p><p><strong>Mechanistic inference:</strong> thinning limits redundant distance-kernel coverage; deleting catalogue-flank predictions can remove false-positive penalty while preserving credit to off-catalogue truth. But it can also delete useful private-truth detections. The condition is quantitative, not a promise:</p><pre>S = T / (0.2 T + 0.2 F + 0.8 K + epsilon)\nA deletion improves S iff:\nlost_T &lt; [0.2 S / (1 - 0.2 S)] × removed_F</pre><p>T is truth-weighted maximum credit, F is prediction mass minus nearest-truth self-credit, and K is truth count. Private truth is unavailable, so the inequality cannot be established for the live competition from these rasters.</p><p><strong>USER-REPORTED, NOT ORGANIZER-CONFIRMED:</strong> H33's 0.2778 and the conflicting claimed leaderboard highs 0.3195 / 0.4413 are quarantined context. The source's calibrated projection is not a score. GEMSDOE32's symmetric/calibrated LM instrument is not this pooled max-credit evaluator; its numbers are not comparable. There is no evidence-based forecast that this new file beats any of those reported values.</p><p>{href(page, 'data/h33-forensics.json', 'Exact H33 measurements and requested-source pins')} · {source('knowledge/2026-10-25_scientific_review.md', 'Scientific interpretation and metric-instrument audit')}</p><h2>Nine requested high-performing sources</h2>{comparison}<p>The complete list in the owner's recurring prompt remains in README. Automated retrieval covered 101 pinned repository trees; the broader inventory contains {inventory.get('unique_rasters', len(inventory.get('rasters', []))):,} byte-distinct restored rasters and 286 unavailable paths. It is not an organizer-complete registry. {source('registry/prior_raster_snapshot.json', 'Full inventory and missing paths')}.</p><h2>Four hypotheses ranked before implementation</h2><p>Ranks are qualitative expected proxy-improvement per cost, not performance projections. Availability is limited to already hash-verified inputs; no unverified external source was needed. "Untried" means not found in the indexed accessible prior code, not universal novelty.</p>{ranked_table}<p>{source('knowledge/2026-10-25_transfer_preregistration.md', 'Frozen preregistration, exact layers, assumptions and ranking')} · {source('registry/shared_template.json', 'Unchanged source hashes')}</p><h2>TGJ31 mechanism and negative outcome</h2><p>Median/IQR-normalized RTP and gravity are regionally detrended. A regularized local gravity-on-magnetics coefficient is transformed with arctan; its gradient must persist at both 3 and 7 px scales, weighted by coupling strength. A 110 px valid-data halo avoids sentinel and missing-data edges. There is no catalogue or SGMC predictor, no supervised fitting and no inherited prediction input. This is a bounded physical response, not a calibrated probability or a source inversion.</p>{result_table}{delta_text}{limitations}<p>The result rejects promotion of this frozen implementation; it does not prove that the underlying geology lacks faults or that all transfer methods must fail. A contact/source-depth confounder and confidence/mass mismatch remain. Scientific work stopped after one experiment. The target is fault labels; geothermal relevance motivates the work but vents are not the evaluated target.</p>''', page)

    page = "register/index.html"
    art_rows = []
    for row in register['files']:
        file = row.get('file_allfinite')
        art_rows.append([e(row['name']), e(row['role']), link(GH + file, 'TIFF (historical; not approved)') if file and row['id'] != 'tgj31-new-negative-audit' else (href(page, card['files']['tif'].removeprefix('docs/'), 'New TIFF · audit only') if file else 'No file'), '<strong class="fail">NOT APPROVED</strong>'])
    write(page, 'Artifact register', f'<p class="eyebrow">PROVENANCE, NOT A SELECTION LIST</p><h1>Every file has a status.</h1>{alert()}<p>The active artifact is the new TGJ31 continuous response. Historical files are retained for education and forensic comparison, not offered as new submissions. No row consumes or authorizes a slot.</p>{table(["Unique name", "Role", "File", "Submission status"], art_rows)}<p>{href(page, "data/submissions.json", "Submission register JSON")} · {source("registry/experiments.json", "Evidence inventory")}</p>', 'register/index.html')

    page = "sources.html"
    source_rows = [[e(r['publisher']), link(r['url'], r['title']), e(r.get('accessed_utc', 'Not recorded')), e(r.get('current_session_status', 'Historical source record; not re-authenticated in this session'))] for r in sources['sources']]
    write(page, 'Sources & data audit', f'''<p class="eyebrow">CLAIMS HAVE A SOURCE AND A LIMIT</p><h1>Keep provenance visible.</h1><p>Official references, owner mirrors, measured artifacts and scientific inference are not interchangeable. Current-session internet access allows GitHub and package registries, not DrivenData, government data portals, Dropbox or the rules PDF host. We do not claim to have re-opened those pages today.</p><h2>Current-session verifications</h2>{table(['Item', 'What was checked', 'Limit / evidence'], [
['Competition inputs', '11 frozen TGJ31 inputs verified; expanded 12-input manifest restored and hash/grid checked after PR #11', href(page, 'data/input-restoration.json', 'Frozen TGJ31 restoration receipt') + ' · ' + source('evidence/data_restore_integration_20261025.json', 'Expanded manifest receipt') + '; mirror identity is not organizer authenticity'],
['Official reference solution', link('https://github.com/drivendataorg/gems-prize-reference-solution/tree/aebe92f7c8a990f0e3443451b7a825d9afd6336b', 'Pinned administrator-owned repository and U-Net notebook'), 'Reference training example, not the official hidden-truth scoring implementation'],
['Shared evaluation/cache/writer', link(template_url, 'Pinned unchanged owner-published template57'), source('registry/shared_template.json', '24 exact source-file hashes') + '; not an organizer-authenticated scorer'],
['Nine focus projects', 'Pinned code and TIFFs measured; H33 pruning identities verified', href(page, 'data/h33-forensics.json', 'Source URLs, SHA-256s and limits')],
['Broader prior registry', '101 pinned trees, 1,005 byte-distinct restored rasters; 286 missing raster paths', source('registry/prior_raster_snapshot.json', 'Inventory, pins and failures') + '; incomplete and not an official registry'],
['Template discrepancy', 'Owner-mirror sample finite-cell values contain the catalogue rather than total absence', source('knowledge/2026-10-25_scientific_review.md', 'Flagged; no organizer authentication or submission approval')]
])}<h2>Historical official and literature source records</h2><p>Access dates below belong to earlier repository evidence. They are preserved, not presented as fresh current-session verification. Current cap, live scores and private fault labels remain unverified.</p>{table(['Publisher', 'Source', 'Recorded access', 'Current status'], source_rows)}<p>{source('registry/data_manifest.json', 'Hash-pinned data manifest')} · {source('registry/data_provenance.json', 'Detailed data provenance')} · {source('knowledge/2026-10-25_scientific_review.md', 'Line-by-line claim/limitation review')}</p><h2>Operational limits</h2><p>3.8 GiB RAM, CPU-only scientific run; large raw inputs and caches are excluded from Git and restored from compact hash-pinned manifests. No hidden labels, authenticated DrivenData data/receipts, submission selector, current weekly-cap receipt or assigned lane paragraph are available. No automatic portal login or upload is attempted.</p>''', page)

    page = "experiments/index.html"
    write(page, 'Research archive', '<p class="eyebrow">PRESERVE HISTORY, DO NOT PROMOTE IT</p><h1>Research archive.</h1><p>These older OOF, proxy and stopped-run artifacts are preserved for learning. They lack the new run\'s common hide-and-recover comparison and must not be quoted as current HOLDOUT-DTI or organizer scores.</p><ul>' + ''.join(f'<li>{href(page, "experiments/" + slug + ".html", title)}</li>' for slug, title, _ in HISTORY) + '<li>' + href(page, 'lane.html', 'Concurrent AS-1 audit — separate lane, blocked') + '</li></ul><p>' + source('knowledge/', 'All historical research notes') + '</p>', page)
    for slug, title, path in HISTORY:
        target = ROOT / path
        if not target.exists():
            path = 'evidence/h31/' if slug.startswith('h31') else 'knowledge/'
        write('experiments/' + slug + '.html', title, f'<p class="eyebrow">ARCHIVAL · NOT SUBMISSION-APPROVED</p><h1>{e(title)}</h1><p>This historical material is retained for education and provenance. Its old proxy figures are not comparable to the new whole-segment pooled HOLDOUT-DTI and are not organizer-confirmed.</p><p>{source(path, "Open the preserved source artifact")}</p><p>{href("experiments/" + slug + ".html", "research.html", "Current preregistered research and honest outcome")}</p>')

    page = "ai-disclosure.html"
    write(page, 'AI-use disclosure', '<p class="eyebrow">TRANSPARENT CONTRIBUTIONS</p><h1>AI-use disclosure.</h1><p>An Arena.ai coding agent reviewed repository code, gathered public pinned sources, proposed and preregistered four hypotheses, implemented the TGJ31 operator and adapters, ran CPU evaluation and validation, and generated the website and written analysis. The feature cache, evaluator and submission writer were vendored unchanged from the explicitly credited owner template.</p><p>The new file is AI-assisted computational research, not a geologist-confirmed fault map. The run produced a negative finding. No competition upload, hidden-label access, organizer acceptance or prize-level performance was established. AI assistance and its actual scope should be disclosed in any eventual competition narrative, subject to the current official rules.</p><p>No model trained for geothermal vent discovery or claim of confirmed new vents is made. No copied prior prediction was an input to the new operator.</p>')
    page = "feed.html"
    write(page, 'Audit status feed', f'''<p class="eyebrow">FROZEN RESULTS. AUTOMATIC SOURCE-STATUS CHECKS.</p><h1>Know what is current.</h1>{alert()}<p>Scientific snapshot: {e(card['date_utc'])}, one experiment, closed. The browser checks public GitHub source metadata automatically and caches it for one hour. A scheduled Pages workflow also publishes a dated metadata snapshot twice daily, used when browser queries fail. This never changes predictions, opens experiments, polls the leaderboard or spends slots. Failures stay visible rather than becoming verified claims.</p><p id="feed-status" role="status" aria-live="polite">Checking public source metadata…</p><div id="source-health"></div><p>{href(page, 'feed.json', 'Raw feed JSON')} · {link(REPO + '/actions', 'Automated CI runs')}</p><script defer src="{e(local(page, 'assets/feed.js'))}"></script>''', page)
    page = "lane.html"
    as1 = read("evidence/lane_candidate_build.json")
    write(page, "Concurrent AS-1 archive", f'''<p class="eyebrow">PRESERVED PARALLEL RESEARCH · NOT THE CURRENT LANE</p><h1>AS-1 archive.<br>Blocked, not selected.</h1><aside class="decision-banner"><strong>DO NOT SUBMIT</strong><span>This separate session's LiDAR antislope candidate and negative evidence are retained. It is not a TGJ31 experiment, comparable incumbent, current recommendation or authorized slot.</span></aside><p>Upstream PR #11 contributed its frozen candidate, E1/E2/E3 evidence, calibration, gates, tests and raster/claim registries. No AS-1 experiment was run or retuned during TGJ31. Its <code>LANE-EVAL-1</code> instrument is not the unchanged shared57 instrument; do not compare their values as if they were common holdout results. No organizer receipt exists.</p><h2>Preserved source evidence</h2><ul><li>{source('knowledge/2026-10-25_lane_hypotheses.md', 'Hypotheses and other-session results, with current caveats')}</li><li>{source('knowledge/upstream_AS1_README_2026-10-25.md', 'Original concurrent README preserved')}</li><li>{source('evidence/run_card_lane_as1.json', 'Separate AS-1 negative run card')}</li><li>{source('evidence/lane_e1.json', 'E1 evidence')} · {source('evidence/lane_e2.json', 'E2 evidence')} · {source('evidence/lane_e3.json', 'E3 evidence')}</li><li>{source('evidence/instrument_calibration.json', 'User-reported calibration, not organizer verification')}</li></ul><p>Archived candidate: <code class="wrap">{e(as1['name'])}</code></p><p>{href(page, as1['files']['allfinite'].removeprefix('docs/'), 'Archived AS-1 TIFF — audit only, DO NOT SUBMIT')} · {href(page, as1['files']['zip_allfinite'].removeprefix('docs/'), 'Archived single-TIFF ZIP')}</p><p class="callout">The older suggestions to test a live slot or waive uniqueness are not current instructions. User-reported results do not authenticate portal acceptance or establish a risk-free probe. No slot, waiver or new experiment is authorized. The current full-support literal registry witness blocks every nonempty eligible candidate.</p>''')
    print(f"Generated {len(list(DOCS.rglob('*.html')))} evidence-backed pages; active artifact is negative, safe_to_submit=false")


if __name__ == "__main__":
    main()
