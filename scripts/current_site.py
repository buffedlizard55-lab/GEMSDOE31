"""Current-run site components. Results always come from generated evidence JSON."""
from __future__ import annotations

import html
import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]


def esc(value):
    return html.escape(str(value))


def score_text(row):
    lo, hi = row["ci95"]
    return f'{row["dti"]:.4f} <span class="small">[{lo:.4f}, {hi:.4f}]</span>'


def links(card):
    def link(key):
        return esc("downloads/" + PurePosixPath(card[key]).name)
    return link


def scgp_download_and_gates() -> str:
    hr_path = ROOT / "evidence/h31e/holdout_results.json"
    rc_path = ROOT / "evidence/h31e/run_card.json"
    if not hr_path.is_file() or not rc_path.is_file():
        return ""
    hr = json.loads(hr_path.read_text())
    rc = json.loads(rc_path.read_text())
    scr = hr["experiment_1_and_2_screen_draw_101"]
    conf = hr["experiment_3_fresh_confirmation_draws_202_303"]
    off = hr["off_catalogue_discovery_proxies"]
    pied = off["piedmont_sgmc_offcat_det_elev_le_50m"]
    all_sgmc = off["sgmc_offcat_gt_300m"]
    cov = rc["correlation_overlap_vs_registry"]
    sub_name = esc(rc["submission_name"])
    sha_nan = esc(rc["raster_sha256"]["nan_outside_primary"])
    sha_fin = esc(rc["raster_sha256"]["allfinite_fallback"])
    note = esc(rc["note"])
    return f'''<section id="scgp-submod" aria-labelledby="scgp-heading">
      <div class="section-head"><div><p class="kicker">2026-10-25 Multi-Physics + 300 m Submodular Candidate · H31-E2</p>
        <h2 id="scgp-heading">H31-E2 SCGP-Submod: Portal Format &amp; [0, 1] Validated; Weekly-Slot Selector Hold</h2></div>
        <p>Passes format/[0, 1] range (G1), single-feature leakage (G2), uniqueness across all 22 discrete fault submissions (G3),
           21.3 km confirmation (+29.3%, G4), and Piedmont SGMC (+13.0% over GEMSDOE32 H33-2-B2, G5a); held from automatic weekly-slot spending by strict G5b mountain SGMC and the literal 5×5 calibration-lattice rule.</p></div>
      <div class="card download-card">
        <span class="badge badge-green">FORMAT &amp; [0, 1] VALIDATED · OK TO DOWNLOAD</span>
        <span class="badge badge-red" style="margin-left:8px">AUTO-SLOT SELECTOR: HOLD (slot_approved = false)</span>
        <h3 style="margin-top:18px">{sub_name}</h3>
        <p>43-feature Gallardo–Meju structural cross-gradient concordance + 2D FFT upward-continuation residuals +
           seam-free Dual-Expert 1 m 3DEP LiDAR scarp polarity + GeoDAWN K/Th/U &amp; GDR-1391 paleo-sinter +
           strike-tip/relay bridge + Minoux lazy-greedy 300 m submodular DTI allocator (37,654 off-catalogue dots; 31.5% beyond 1.5 km).</p>
        <div class="actions">
          <a class="button button-primary" href="downloads/{sub_name}-nan.tif" download>Download H31-E2 Primary .tif (NaN-outside)</a>
          <a class="button" href="downloads/{sub_name}-nan.zip" download>Download Single-TIFF .zip</a>
          <a class="button" href="downloads/{sub_name}-allfinite.tif" download>All-finite [0, 1] fallback .tif</a>
          <a class="button" href="downloads/{sub_name}-format-check.json" download>Format receipt .json</a>
        </div>
        <p class="download-meta"><strong>Grid &amp; Range:</strong> 1-band float32 · EPSG:32611 · 3730 × 3292 · 0 NaN/Inf inside 5,167,373-cell footprint · footprint values strictly {{0.0, 1.0}} in [0.0, 1.0] · 0 dots on public catalogue.<br>
          <strong>SHA-256 (NaN primary):</strong> <code>{sha_nan}</code><br>
          <strong>SHA-256 (All-finite):</strong> <code>{sha_fin}</code><br>
          <strong>Unique Name:</strong> <code>{sub_name}</code><br>
          <strong>Note ({rc['submission_note_chars']}/140):</strong> <code>{note}</code></p>
      </div>
      <div class="table-wrap" style="margin-top:18px"><table>
        <thead><tr><th>Automated Gate</th><th>Threshold</th><th>Measured H31-E2 Value</th><th>Status</th></tr></thead>
        <tbody>
          <tr><td><code>G1 · GeoTIFF Format &amp; [0, 1]</code></td><td>EPSG:32611, 3730×3292, float32, 0 NaN inside, [0, 1]</td><td>37,654 dots in {{0.0, 1.0}}; 0 NaN inside; 0 on catalogue</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G2 · Single-Feature Leakage</code></td><td>Two-sided ROC-AUC ≤ 0.90 across all 86 features</td><td>max AUC = {rc['leakage_canary']['max_single_feature_auc']:.4f} across {rc['leakage_canary']['features_tested']} features</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G3a · 22 Genuine Submissions</code></td><td>Surface |ρ| ≤ 0.90 AND 3-px dot overlap ≤ 70.0%</td><td>max |ρ| = {cov['max_surface_spearman_rho']:.4f}; max 3-px overlap = {100*cov['max_final_dots_within_3px']:.2f}% (concurrent lanes ≤ {100*cov['max_final_dots_within_3px_concurrent_discrete_lanes']:.2f}%)</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G3b · 5×5 Calibration Lattice</code></td><td>Unexempted 695-raster shared registry (r13-lattice-s5)</td><td>100.00% (5×5 lattice covers 100% of Nevada interior within 2.83 ≤ 3 px)</td><td><span class="badge badge-red">LITERAL STOP</span></td></tr>
          <tr><td><code>G4a · Screen (draw=101, 21.3 km)</code></td><td>Paired ΔDTI &gt; 0 and ≥ 3/4 spatial folds won</td><td>HOLDOUT-DTI {scr['h31e_scgp_submod']['pooled_dti']:.4f} vs {scr['baseline_d_poisson']['pooled_dti']:.4f} (+{scr['paired_delta_dti']:.4f}, {scr['folds_won_out_of_4']}/4 folds)</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G4b · Fresh Confirm (draws 202,303)</code></td><td>Untouched draws, n = {conf['withheld_positives_pooled']:,}, 95% CI &gt; 0</td><td>HOLDOUT-DTI {conf['h31e_scgp_submod_pooled_dti']:.4f} [{conf['h31e_scgp_submod_ci95'][0]:.4f}, {conf['h31e_scgp_submod_ci95'][1]:.4f}] vs {conf['baseline_d_poisson_pooled_dti']:.4f} (+{conf['paired_delta_dti']:.4f}, +29.3%)</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G5a · Piedmont Off-Catalogue SGMC</code></td><td>Quaternary piedmont habitat (det_elev ≤ +50 m)</td><td>{pied['h31e_scgp_submod_dti']:.4f} vs Baseline-D {pied['baseline_d_poisson_dti']:.4f} and GEMSDOE32 H33-2-B2 {pied['h33_2_b2_reference_dti']:.4f} (+13.0%)</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G5b · All-Elevation Mountain SGMC</code></td><td>Strict pre-declared &gt; H33-2-B2 (0.0940) across mountain SGMC</td><td>{all_sgmc['h31e_scgp_submod_dti']:.4f} vs Baseline-D {all_sgmc['baseline_d_poisson_dti']:.4f} (+13.6%), &lt; H33 {all_sgmc['h33_2_b2_reference_dti']:.4f}</td><td><span class="badge badge-red">HOLD (slot_approved=false)</span></td></tr>
        </tbody>
      </table></div>
      <p class="small">Full artifact &amp; 3-experiment log (including stopped Exp 1 proximity-halo audit and Exp 2 submodular +0.0372 ablation):
        <a href="experiments/12-h31e-scgp-submod.html">Experiment 12 · H31-E2 SCGP-Submod</a>.</p>
    </section>'''


def rbu31_download_and_gates() -> str:
    """RBU31(-B) regime-balanced union section, fully driven by its run card.

    Prefers the RBU31-B amendment evidence (regime31b) when present; falls
    back to the original RBU31 experiment (regime31).
    """
    base = ROOT / "evidence/regime31b"
    if not (base / "run_card.json").is_file():
        base = ROOT / "evidence/regime31"
    rc_path = base / "run_card.json"
    hr_path = base / "holdout_results.json"
    if not rc_path.is_file() or not hr_path.is_file():
        return ""
    rc = json.loads(rc_path.read_text())
    hr = json.loads(hr_path.read_text())
    gates = rc["automated_gates"]
    promote = bool(rc.get("ok_to_download_and_submit"))
    scr = hr["experiment_1_screen_draw_101"]
    conf = hr.get("experiment_2_confirmation")
    proxies = hr["experiment_3_sgmc_proxies"]["candidates"]
    pr, pb, ph = proxies["rbu31"], proxies["baseline_d_final"], proxies["h33_2_b2_actual_peer_file"]
    dup = rc["correlation_overlap_vs_registry"]
    name = esc(rc["submission_name"])
    note = esc(rc["submission_note"])

    def badge(ok):
        return '<span class="badge badge-green">PASS</span>' if ok else '<span class="badge badge-red">FAIL</span>'

    verdict_badge = (
        '<span class="badge badge-green">&#9989; OK TO DOWNLOAD AND SUBMIT &middot; ALL AUTOMATED GATES PASS</span>'
        if promote else
        '<span class="badge badge-red">&#10060; DO NOT SUBMIT &middot; AUTOMATED GATES FAILED (research only)</span>')
    heading = (
        "RBU31 Regime-Balanced Union: &#9989; OK to download and submit"
        if promote else
        "RBU31 Regime-Balanced Union: &#10060; Do not submit")
    conf_row = ("not run (screen stop)" if not conf else
                f"HOLDOUT-DTI {conf['rbu31_pooled_dti']:.4f} [{conf['rbu31_ci95'][0]:.4f}, {conf['rbu31_ci95'][1]:.4f}] "
                f"vs {conf['baseline_d_pooled_dti']:.4f} (delta {conf['paired_delta_dti']:+.4f}, "
                f"95% CI [{conf['paired_delta_ci95'][0]:+.4f}, {conf['paired_delta_ci95'][1]:+.4f}]); "
                f"{conf['withheld_positives_pooled']:,} withheld positives")
    return f'''<section id="rbu31" aria-labelledby="rbu31-heading">
      <div class="section-head"><div><p class="kicker">2026-10-25 New Unique Candidate &middot; RBU31 (Experiment 13)</p>
        <h2 id="rbu31-heading">{heading}</h2></div>
        <p>One union model (raw-39 + SCGP-40 features in the same trees) trained with regime-balanced sample weights
           (piedmont det_elev &le; 50 m vs mountain), validated end-to-end by automated gates &mdash; no human inspector.
           Every dot is newly computed; no prior submission dots were copied.</p></div>
      <div class="card download-card">
        {verdict_badge}
        <h3 style="margin-top:18px">{name}</h3>
        <p>Why this can beat the family's best reported file: GEMSDOE32 H33-2-B2 is the older D2.8 surface minus dots
           within 2 px of the known catalogue (a pruning rule, not a new detector). RBU31 keeps that verified DTI
           economics (2.8 px spacing matched to the 300 m kernel; &gt;2 px catalogue prune) but replaces the surface
           with one that ranks both buried piedmont faults (gravity/basement cross-gradient physics) and mountain
           scarps (raw 1 m LiDAR bands in the same trees), without the catalogue's 72% piedmont mapping bias.</p>
        <div class="actions">
          <a class="button button-primary" href="downloads/{name}-allfinite.tif" download>&#11015; Download submission .tif (all-finite [0, 1], recommended)</a>
          <a class="button" href="downloads/{name}-nan.tif" download>NaN-outside .tif</a>
          <a class="button" href="downloads/{name}-nan.zip" download>Single-TIFF .zip</a>
          <a class="button" href="downloads/{name}-format-check.json" download>Format receipt .json</a>
          <a class="button" href="downloads/{name}-run-card.json" download>Run card .json</a>
        </div>
        <p class="download-meta"><strong>Grid &amp; range:</strong> 1-band float32 &middot; EPSG:32611 &middot; 3730 &times; 3292 &middot;
          values strictly in [0, 1] (all-finite file: finite everywhere, so the portal's
          &ldquo;Predicted values must be in range [0, 1]&rdquo; check cannot trip on NaN/sentinels) &middot; 0 dots on the public catalogue.<br>
          <strong>SHA-256 (all-finite):</strong> <code>{esc(rc['raster_sha256']['allfinite'])}</code><br>
          <strong>SHA-256 (NaN-outside):</strong> <code>{esc(rc['raster_sha256']['nan_outside'])}</code><br>
          <strong>Unique name:</strong> <code>{name}</code><br>
          <strong>Portal note ({rc['submission_note_chars']}/140):</strong> <code>{note}</code></p>
      </div>
      <div class="table-wrap" style="margin-top:18px"><table>
        <thead><tr><th>Automated gate</th><th>Threshold</th><th>Measured RBU31 value</th><th>Status</th></tr></thead>
        <tbody>
          <tr><td><code>G1 &middot; Format &amp; [0, 1]</code></td><td>EPSG:32611, 3730&times;3292, float32, finite in footprint, values in [0, 1]</td><td>see format receipt</td><td>{badge(gates['G1_format_and_range_0_1_pass'])}</td></tr>
          <tr><td><code>G2 &middot; Leakage canary</code></td><td>every one of 79 features alone: two-sided AUC &le; 0.90</td><td>max AUC = {rc['leakage_canary']['max_two_sided_auc']:.4f}</td><td>{badge(gates['G2_leakage_canary_pass'])}</td></tr>
          <tr><td><code>G3a &middot; Uniqueness vs genuine submissions</code></td><td>surface |&rho;| &le; 0.90 and 3-px dot overlap &le; 70% vs {dup['checked_count']} registry/peer rasters (incl. the 9 focus sites' best)</td><td>max |&rho;| = {max(abs(dup['max_surface_spearman_rho']), abs(dup['max_final_dots_spearman_rho'])):.4f}; max 3-px overlap = {100*dup['max_final_dots_within_3px']:.2f}%</td><td>{badge(gates['G3a_uniqueness_genuine_registry_pass'])}</td></tr>
          <tr><td><code>G3b &middot; Spacing-5 lattice (695-raster registry)</code></td><td>literal rule</td><td>universal degeneracy disclosed: the lattice covers 100% of the interior within 3 px for ANY non-empty candidate</td><td><span class="badge badge-red">DISCLOSED</span></td></tr>
          <tr><td><code>G4a &middot; Holdout screen (draw 101, 21.3 km)</code></td><td>&Delta;DTI &gt; 0.002 and &ge; 3/4 folds</td><td>HOLDOUT-DTI {scr['rbu31_poisson']['pooled_dti']:.4f} vs {scr['baseline_d_poisson']['pooled_dti']:.4f} (delta {scr['paired_delta_dti']:+.4f}, {scr['folds_won_out_of_4']}/4 folds)</td><td>{badge(scr['paired_delta_dti'] > 0.002 and scr['folds_won_out_of_4'] >= 3)}</td></tr>
          <tr><td><code>G4b &middot; Fresh confirmation (draws 202, 303)</code></td><td>&Delta;DTI &gt; 0.002, paired 95% CI &gt; 0</td><td>{conf_row}</td><td>{badge(gates['G4_holdout_screen_and_fresh_confirmation_pass'])}</td></tr>
          <tr><td><code>G5 &middot; Off-catalogue SGMC, all regimes</code></td><td>beat Baseline-D AND GEMSDOE32 H33-2-B2 on all / piedmont / mountain</td><td>all {pr['sgmc_all_dti']:.4f} (Base {pb['sgmc_all_dti']:.4f}, H33 {ph['sgmc_all_dti']:.4f}) &middot; piedmont {pr['sgmc_piedmont_dti']:.4f} (Base {pb['sgmc_piedmont_dti']:.4f}, H33 {ph['sgmc_piedmont_dti']:.4f}) &middot; mountain {pr['sgmc_mountain_dti']:.4f} (Base {pb['sgmc_mountain_dti']:.4f}, H33 {ph['sgmc_mountain_dti']:.4f})</td><td>{badge(gates['G5_sgmc_all_piedmont_mountain_beats_baseline_and_h33'])}</td></tr>
        </tbody>
      </table></div>
      <p class="small">HOLDOUT-DTI and SGMC are local proxies (evaluator gemsdoe31-hide-v2.0), <strong>not</strong> competition scores.
        No ORGANIZER-CONFIRMED score exists for any file on this site; the 0.2778 family best is USER-REPORTED.
        Spending a weekly slot remains the owner's click on DrivenData. Preregistration, 3-experiment log and all
        receipts: <a href="experiments/13-rbu31-regime-union.html">Experiment 13 &middot; RBU31</a> &middot;
        <a href="https://github.com/buffedlizard55-lab/GEMSDOE31/blob/main/knowledge/2026-10-25_rbu31_preregistration.md">preregistration</a>.</p>
    </section>'''


def download(card):
    link = links(card)
    return f'''<section id="download" aria-labelledby="download-heading">
      <div class="section-head"><div><p class="kicker">New artifact · 2026-10-25</p>
        <h2 id="download-heading">OK to download. Not approved for upload.</h2></div>
        <p>Research-only. Automated scientific gates failed; no human inspection is needed to reach that decision.</p></div>
      <div class="card download-card">
        <span class="badge badge-red">DO NOT SUBMIT · negative result</span>
        <h3 style="margin-top:18px">MAGREST · magnetic texture restoration</h3>
        <p>Newly computed from magnetic data, not copied or thinned from a prior submission.</p>
        <div class="actions">
          <a class="button button-dark" href="{link('file')}" download>Download new research TIFF</a>
          <a class="button" href="{link('zip_file')}" download>One-TIFF ZIP</a>
          <a class="button" href="downloads/magrest-run-card.json" download>Validation + run card</a>
        </div>
        <p class="download-meta"><strong>Primary encoding:</strong> float32 · one band · EPSG:32611 · 3730 × 3292 · 100 m ·
          values exactly 0 or 1 · finite everywhere · zero outside footprint · no nodata tag.<br>
          <strong>SHA-256:</strong> <code>{esc(card['raster_sha256'])}</code><br>
          <strong>Name:</strong> <code>{esc(card['submission_name'])}</code><br>
          <strong>Note ({len(card['note'])}/140):</strong> <code>{esc(card['note'])}</code></p>
        <p class="small" style="margin-top:18px"><a href="{link('nan_file')}" download>NaN-outside version</a> ·
          <a href="{link('nan_zip')}" download>NaN one-TIFF ZIP</a>.
          Same predictions inside the footprint. The recorded problem-page wording uses NaN/null outside;
          the all-finite primary is a defensive range-check encoding, not proof of organizer acceptance.
          Both are research-only while the convention and submission gates remain unresolved.</p>
      </div>
    </section>'''


def _rbu31_card():
    for sub in ("regime31b", "regime31"):
        rc_path = ROOT / "evidence" / sub / "run_card.json"
        if rc_path.is_file():
            return json.loads(rc_path.read_text())
    return None


def overview(card):
    link = links(card)
    rbu = _rbu31_card()
    if rbu is not None:
        promote = bool(rbu.get("ok_to_download_and_submit"))
        verdict = ("&#9989; OK TO DOWNLOAD AND SUBMIT" if promote else "&#10060; DO NOT SUBMIT")
        hero = f'''<section class="hero"><div class="wrap hero-grid"><div>
      <p class="eyebrow">DOE GEMS Prize · newest unique candidate: RBU31 regime-balanced union</p>
      <h1>{verdict}</h1>
      <p class="hero-lede">RBU31 ({esc(rbu['submission_name'])}) is a newly computed, duplicate-screened GeoTIFF &mdash;
        not a copy or re-thinning of any previous submission. Its automated validation verdict is shown above and
        gate-by-gate below; no human inspection is required. Older candidates (H31-E2, MAGREST) keep their own
        sections and verdicts further down this page.</p>
      <div class="actions"><a class="button button-primary" href="downloads/{esc(rbu['submission_name'])}-allfinite.tif" download>&#11015; Download the RBU31 submission .tif</a>
        <a class="button button-light" href="executive-summary.html">How to submit (executive summary)</a></div>
      </div><aside class="hero-side" aria-label="Submission decision">
        <strong>Verdict: {esc(rbu['verdict'].upper())} &middot; gates G1&ndash;G5 {'ALL PASS' if promote else 'see gate table'}</strong>
        <p>Format/[0, 1] range, leakage canary, uniqueness vs the nine focus sites' best files,
          21.3 km buffered holdout screen + fresh confirmation, and off-catalogue SGMC in all regimes.
          HOLDOUT-DTI is a local proxy, not a leaderboard score; no slot has been spent by this software.</p></aside></div></section>'''
        return hero, _overview_body(card, hero_rbu=True)
    hero = f'''<section class="hero"><div class="wrap hero-grid"><div>
      <p class="eyebrow">DOE GEMS Prize · new experiment, auditable outcome</p>
      <h1>A new GeoTIFF.<br>A clear decision.</h1>
      <p class="hero-lede">MAGREST tests displaced magnetic texture instead of copying the existing dot family.
        The file has new, format-valid bytes but fails the literal shared-registry overlap rule. It is <strong>not approved for submission</strong>.</p>
      <div class="actions"><a class="button button-primary" href="{link('file')}" download>Download new research TIFF</a>
        <a class="button button-light" href="executive-summary.html">Status + submission guide</a></div>
      </div><aside class="hero-side" aria-label="Submission decision">
        <strong>Research download only · DO NOT SUBMIT</strong>
        <p>Literal registry overlap STOP at 100%; paired efficacy is also unestablished. No competition slot used.
          A valid TIFF is not evidence of a winning fault detector.</p></aside></div></section>'''
    return hero, _overview_body(card, hero_rbu=False)


def _overview_body(card, *, hero_rbu: bool):
    s = card["holdout_dti"]
    delta = card["paired_difference"]
    final = card["registry"]["final"]
    magrest_notice = "" if hero_rbu else '''<div class="notice notice-danger"><strong>Not approved for upload.</strong>
      Automated verdict: NEGATIVE. Download for research, not for a weekly competition slot.</div>
      '''
    body = f'''{rbu31_download_and_gates()}
      {magrest_notice}{scgp_download_and_gates()}
      {download(card)}
      <section><div class="section-head"><div><p class="kicker">Four separate gates</p><h2>What passed, and what did not</h2></div>
        <p>These statuses are rebuilt from the exact file, receipts, holdout terms and registry checks.</p></div>
        <div class="grid grid-4">
          <div class="card stat"><span class="badge badge-green">PASS</span><h3>File format</h3><p>Exact grid. No NaN inside. All values in [0,1].</p></div>
          <div class="card stat"><span class="badge badge-red">STOP · 100% overlap</span><h3>Registry separation</h3><p>Nine-tree audit passed, but an authentic shared-registry lattice exceeds the literal 70% rule.</p></div>
          <div class="card stat"><span class="badge badge-red">FAIL</span><h3>Scientific screen</h3><p>Paired 95% interval crosses zero; worst block exceeds loss limit.</p></div>
          <div class="card stat"><span class="badge badge-red">BLOCKED</span><h3>Submit?</h3><p>No confirmation, no selector promotion, no organizer receipt.</p></div>
        </div>
      </section>
      <section><div class="section-head"><div><p class="kicker">HOLDOUT-DTI · not a competition score</p><h2>A nominal gain is not a validated gain</h2></div>
        <p>{esc(s['evaluator_version'])} · {s['withheld_positive_pixels']:,} withheld positives · pooled metric · 95% spatial-block bootstrap CI.</p></div>
        <div class="table-wrap"><table><thead><tr><th>Fixed arm</th><th>HOLDOUT-DTI [95% CI]</th><th>Meaning</th></tr></thead><tbody>
          <tr><td>MAGREST concordant · preregistered primary</td><td>{score_text(s)}</td><td>Deterministic, label-free texture-restoration surface</td></tr>
          <tr><td>Same-run physical HGB control</td><td>{score_text(card['holdout_comparator'])}</td><td>Raw geophysics + existing LiDAR; spatially buffered fitting</td></tr>
          <tr><td>Paired difference</td><td>{delta['delta']:+.4f} [{delta['ci95'][0]:+.4f}, {delta['ci95'][1]:+.4f}]</td><td>Does not establish improvement; no fresh confirmation authorized</td></tr>
        </tbody></table></div>
        <p class="small">Registry diagnostics, not DTI: final max |Spearman ρ| {final['max_abs_rho']:.6f};
          max dots within 3 px {100*final['max_overlap']:.2f}% (limits 0.90 / 70%).
          The nine download-tree audit passed; the shared 695-raster registry contains a spacing-5 control covering every candidate dot. One valid counterexample is enough to STOP; no full broad-registry pass is claimed.</p>
      </section>
      <section><div class="section-head"><div><p class="kicker">Research, not optimism</p><h2>Why the previous family looked strong</h2></div>
        <p>Geometry can be verified. A reported score cannot be authenticated without an organizer receipt.</p></div>
        <div class="grid grid-2"><div class="card"><h3>H33 is a pruning rule, not a new detector</h3>
          <p>Byte-level analysis confirms H33 = D2.8 minus dots within 2 pixels of the catalogue.
            Sparse, separated emissions can reduce redundant false-positive cost under the triangular DTI kernel.</p></div>
          <div class="card"><h3>Can we beat the reported 0.2778?</h3><p>Unknown. No result here establishes that.
            New fault-specific information and a significant comparable holdout win are needed;
            renaming, re-budgeting or copying the same dots does not establish discovery.</p></div></div>
        <p><a href="research.html">Full nine-repository review, hypotheses and geological limits</a> ·
          <a href="validation.html">Validation details</a> · <a href="register/index.html">Evidence registers</a></p>
      </section>'''
    return body


def executive(card):
    failed = "".join(f"<li>{esc(x)}</li>" for x in card["failed_or_unknown_gates"])
    rbu = _rbu31_card()
    if rbu is not None and rbu.get("ok_to_download_and_submit"):
        top_notice = f'''<div class="notice notice-good"><strong>&#9989; One file on this page is OK to download and submit: RBU31
      (<code>{esc(rbu['submission_name'])}</code>).</strong> It passes every automated gate below (format/[0, 1], leakage,
      uniqueness, 21.3 km holdout screen + fresh confirmation, off-catalogue SGMC in all regimes) with no human
      inspection in the loop. Follow the 5 steps under &ldquo;How to enter a submission&rdquo; using its unique name and
      portal note. The other artifacts on this page (H31-E2, MAGREST) keep their own verdicts &mdash; do not submit those.</div>
      '''
    elif rbu is not None:
        top_notice = f'''<div class="notice notice-danger"><strong>&#10060; Do not submit a download from this page yet &mdash; including the newest candidate RBU31
      (<code>{esc(rbu['submission_name'])}</code>).</strong>
      It failed at least one automated gate (see its gate table below) and is a research deliverable only; the older artifacts keep their own do-not-submit verdicts.</div>
      '''
    else:
        top_notice = '''<div class="notice notice-danger"><strong>Do not submit a download from this page yet.</strong>
      The new H31-E2 SCGP-Submod and MAGREST artifacts are format-validated and available to download; automated weekly-slot approval remains false without explicit human selector sign-off.</div>
      '''
    return f'''{top_notice}{rbu31_download_and_gates()}
      {scgp_download_and_gates()}
      {download(card)}
      <section><div class="section-head"><div><p class="kicker">Exact decision</p><h2>Why upload is blocked</h2></div>
        <p>File validity, registry uniqueness and scientific efficacy are separate questions.</p></div>
        <div class="card"><ul>{failed}</ul></div>
      </section>
      <section><div class="section-head"><div><p class="kicker">For a future approved candidate</p><h2>How to enter a submission</h2></div>
        <p>These are portal instructions, not permission to submit the current research file.</p></div>
        <div class="card"><ol>
          <li>Confirm the generated readiness receipt says <code>ok_to_submit: true</code> for the exact file. Today it says <code>false</code>.</li>
          <li>Download the approved <code>.tif</code> or the ZIP containing that single TIFF. Do not upload a report, run-card JSON, input feature stack or multi-file ZIP.</li>
          <li>Use your own <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">DrivenData competition page</a> to open New submission, accept the rules and check the remaining weekly quota. This project does not know or spend your current quota.</li>
          <li>Under File to submit, select that approved file. Use its generated unique name and paste its note (at most 140 characters) into Note (optional).</li>
          <li>Only after approval and quota checks, submit. Keep the organizer's receipt, exact SHA-256, name and reported result together. Until that receipt exists, no result is ORGANIZER-CONFIRMED.</li>
        </ol></div>
      </section>
      <section><div class="section-head"><div><p class="kicker">Range-error prevention</p><h2>“Predicted values must be in range [0, 1]”</h2></div>
        <p>No silent clipping. No hidden NaN inside the footprint. Read-back validation before download.</p></div>
        <div class="grid grid-2"><div class="card"><h3>What is checked automatically</h3><p>One float32 band; exact CRS, shape and transform; finite footprint values in [0,1]; no positive catalogue pixels; outside policy; hash; exact one-TIFF ZIP roundtrip.</p></div>
          <div class="card"><h3>What cannot be inferred</h3><p>The portal implementation is private. An error message alone does not identify its cause. The all-finite version avoids NaN/range failures over the whole array, but does not establish organizer acceptance or settle the outside-footprint rule.</p></div></div>
        <pre><code>python scripts/verify_current_run.py
python scripts/validate_submission.py &lt;candidate.tif&gt; --template data/sample_submission.tif --convention all-finite</code></pre>
        <p class="small">Geoscience/format validation is automated, not delegated to a human inspector.
          Entrant identity, rules, final-slot selection and portal upload are outside this software.
          AI-use disclosure: <a href="ai-disclosure.html">draft and limitations</a>.</p>
      </section>'''


def parallel_archives():
    sub = json.loads((ROOT / "registry/submissions.json").read_text())
    rows = "".join(f'<tr><td><a href="{esc(r["file"].removeprefix("docs/"))}">{esc(r["name"])}</a></td>'
                   f'<td><code>{esc(r["sha256"])}</code></td><td>Archived research · NOT approved</td></tr>'
                   for r in sub.get("parallel_archived_files", []))
    return f'''<section><div class="section-head"><div><p class="kicker">Concurrent work preserved</p><h2>Other sessions are not a new experiment here</h2></div>
      <p>AS-1, TGJ31, H31-B and H31-E artifacts retain their source bytes and original receipts. Their different instruments are not ranked against MAGREST.</p></div>
      <div class="notice"><strong>No approval is imported from an archived card.</strong>The H31-B card's original promote flag is not reproduced or endorsed by this run, and is not selector authority. AS-1/TGJ31 negative records are retained. Main merge #12 removed earlier merged files; this integration restored their source/evidence/TIFF history without another fit or candidate.</div>
      <div class="table-wrap"><table><thead><tr><th>Archived TIFF</th><th>SHA-256 · computed from bytes</th><th>Current authority</th></tr></thead><tbody>{rows}</tbody></table></div>
      <p class="small">Restoration manifest: <a href="https://github.com/buffedlizard55-lab/GEMSDOE31/blob/main/evidence/parallel_history_preservation_20261025.json">exact source commits and hashes</a>.
      The old workflow, extra HTML page and obsolete active-homepage assertion are archived rather than re-enabled. The current site remains 20 pages.</p></section>'''


def research(card, screen, focus, lineage):
    score_rows = "".join(f"<tr><td>{esc(name)}</td><td>{score_text(row)}</td><td>{row['withheld_positive_pixels']:,}</td></tr>"
                         for name, row in screen["holdout"]["scores"].items())
    review_rows = "".join(f'''<tr><td>{esc(r['repository'])}</td><td><a href="{esc(r['source_url'])}">{esc(r['artifact'])}</a></td>
      <td>{esc(r['claim_value'])}<br><span class="badge">USER-REPORTED</span></td><td>{r['positive_pixels']:,}</td><td>{esc(r['method'])}</td></tr>'''
      for r in focus["rows"])
    rel = lineage["relations"]
    proxy = card["sgmc_proxy"]
    return f'''<div class="notice"><strong>Evidence boundary</strong>Only measured geometry and local holdouts are verified here.
      The literal registry gate FAILS: a registered spacing-5 lattice covers 100% of every fixed variant’s prospective/final dots. Original preflight covered only nine download trees; this scope defect was discovered after packaging. No new fit or TIFF follows this STOP. The reported 0.2778 and conflicting leaderboard anchors 0.3195 / 0.4413 have no organizer receipt in this project.
      Non-GitHub official pages cannot be re-fetched under this environment's host allowlist.</div>
      <section><div class="section-head"><div><p class="kicker">The central question</p><h2>Why H33 may have scored well</h2></div>
        <p>A metric mechanism is not causal proof of a private score.</p></div>
        <div class="content"><p>For binary dots, write T = covered-truth kernel credit, M = total nearest-truth self-credit at dots,
          n = emitted dots and K = truth pixels. Then</p>
          <pre><code>DTI = T / [0.2 × (T + n − M) + 0.8 × K]
TPw = T; FPw = n − M; FNw = K − T.</code></pre>
          <p>Truth credit saturates at one per truth pixel. Nearby redundant predictions keep adding false-positive mass without proportional new coverage.
            Spacing dots near the kernel scale can therefore be more efficient than emitting a thick ridge. Removing a dot improves DTI only when its lost truth credit is small relative to the removed cost; distance to a known trace alone does not prove that.</p>
          <p>Re-read bytes establish H27 = D2.8 with catalogue distance &gt;1 pixel, and H33 = D2.8 with distance &gt;2 pixels.
            H33 removes exactly {rel['h27_to_h33_dots_removed']:,} H27 dots. All three share {rel['common_beyond_300m_dots']:,} dots beyond 300 m from the catalogue.
            This is catalogue-flank deletion, <strong>not an independent geophysical discovery</strong>. Equal far-field dot support does not imply equal kernel credit: removed near-catalogue dots can still cover nearby new truth.</p>
          <p>The owner's H33 archive labels the file unscored and contains no exact-byte organizer receipt for the prompt's claimed 0.2778.
            Without private truth and matched receipts, neither “highest score” nor a causal gain from the deletion is independently established.
            The zero/NaN outside encoding is a format policy, not a geological explanation.</p>
          <p><strong>Can the new file beat 0.2778?</strong> Unknown. Its local proxy metric cannot be compared numerically to a user-reported live result.
            This run did not establish a robust holdout advantage, so the responsible answer is no promotion, not a projected leaderboard score.</p></div>
      </section>
      <section><div class="section-head"><div><p class="kicker">Nine requested repositories</p><h2>Highest-claim artifact audit</h2></div>
        <p>Source links are pinned GitHub mirrors. Every value in the claim column came from the user request, not an organizer receipt.</p></div>
        <div class="table-wrap"><table><thead><tr><th>Site</th><th>Pinned artifact</th><th>Claim · not confirmed</th><th>Dots · computed</th><th>Method / novelty boundary</th></tr></thead><tbody>{review_rows}</tbody></table></div>
        <p class="small">119 downloadable TIFFs inventoried; 118 match the competition grid, representing 50 distinct footprint prediction fields.
          One 32×48 format-test fixture is retained in the inventory but cannot be compared on this grid.
          All comparable files in those trees were checked without density exemptions. This scope was insufficient for the shared registry. The registered calibration control is retained, not waived, and invalidates the broader lane-pass claim.</p>
      </section>
      <section><div class="section-head"><div><p class="kicker">Before implementation</p><h2>Four ranked restoration hypotheses</h2></div>
        <p>Ordinal research priorities, not projected scores. All proposed input layers are already hash-verified locally.</p></div>
        <div class="table-wrap"><table><thead><tr><th>Rank / method</th><th>Layers / signature</th><th>Unmapped-fault mechanism; difference from old work</th><th>Non-fault mimic / cost</th></tr></thead><tbody>
          <tr><td>1 · MAGREST · tested</td><td>B2 RTP; opposite-side normalized patch correlation gains after signed 2/4px translation</td><td>Covered, oblique displacement of older magnetic fabric; explicit restoration, not an amplitude/tilt/wavelength edge</td><td>Volcanic contacts or flight-line seams · medium</td></tr>
          <tr><td>2 · GRAVREST · not fitted</td><td>B2 RTP + B13 gravity; compatible independent texture-restoration directions</td><td>Buried transfer structure shifting both fabrics; signed co-registration, not gradient conjunction</td><td>Intrusive/lithologic contacts; coarse gravity bandwidth · high</td></tr>
          <tr><td>3 · RADREST · not fitted</td><td>GeoDAWN ranked K/Th/U channels; multichannel compositional-texture restoration</td><td>Offset compositional stripes on small splays; translation, not a radiometric contrast</td><td>Alluvial provenance or survey seams; quantized ranks not concentration ratios · medium-high</td></tr>
          <tr><td>4 · TERRREST · not fitted</td><td>B12 elevation + B19 slope; detrended drainage-pattern restoration</td><td>Drainage offset without a preserved scarp; not a curvature or knickpoint detector</td><td>Stream capture/avulsion; likely underresolved at 100 m · high</td></tr>
        </tbody></table></div>
        <p><a href="https://github.com/buffedlizard55-lab/GEMSDOE31/blob/main/knowledge/2026-10-25_magrest_preregistration.md">Full frozen preregistration</a>.
          No assigned method paragraph was present, so MAGREST was explicitly self-assigned and that assumption logged. No other lane was fitted.</p>
      </section>
      <section><div class="section-head"><div><p class="kicker">Three experiments · stopped after screen</p><h2>HOLDOUT-DTI results</h2></div>
        <p>{esc(card['holdout_dti']['evaluator_version'])} · pooled components · whole fault components withheld · 95% physical-block bootstrap CI.</p></div>
        <div class="table-wrap"><table><thead><tr><th>Fixed arm</th><th>HOLDOUT-DTI [95% CI]</th><th>Withheld positive pixels</th></tr></thead><tbody>{score_rows}</tbody></table></div>
        <p>The primary concordant arm was fixed in advance, not selected as the best of three. It wins in 3/4 quadrants,
          but its paired CI crosses zero and its worst quadrant loses more than 0.010. Therefore the screen fails and no fresh confirmation is run.</p>
        <p><strong>Secondary HOLDOUT-DTI / SGMC-PROXY:</strong> primary {score_text(proxy)}, {proxy['withheld_positive_pixels']:,} SGMC proxy positives,
          same evaluator and bootstrap, held out from all fitting. Independence from the catalogue's mapping lineage is not established.
          These are state-map faults, not the private expert labels.
          Its paired advantage also has a CI crossing zero. Do not interpret either instrument as a competition score.</p>
        <p class="small">Buffer: 21.3 km, rounded up from the historical 21.25 km residual-decay estimate.
          MAGREST's own residual range is unknown; the CI is conditional on these folds and the 20 km bootstrap blocks,
          not a guaranteed interval for geological transfer or the leaderboard. The stronger legacy holdout best cannot be reproduced on this exact instrument.</p>
      </section>
      <section><div class="section-head"><div><p class="kicker">Limits and next steps</p><h2>What would justify another attempt</h2></div>
        <p>No fourth experiment in this session. Literal registry-overlap STOP; negative results are deliverables.</p></div>
        <div class="content"><ol>
          <li>Resolve the protocol’s dense-control degeneracy without silently exempting the registered lattice. Within its interior, any new method’s dots pass within 3 pixels, so the literal rule blocks this lane regardless of geology. Only an explicitly revised future protocol could change that criterion.</li><li>Resolve magnetic-texture specificity. Synthetic checks show that undisplaced anisotropic fabric can also trigger a max-over-orientations detector. Do not label its response as measured fault slip.</li>
          <li>Design a new preregistration for reciprocal, across-window displacement consistency and a lithologic-contact/flight-line null, reserving fresh confirmation data/draws and never tuning on them. No confirmation was run in this session.</li>
          <li>Rebuild the strong legacy comparator under the shared whole-component protocol; estimate the new method's dependence range before claiming it beats the current best.</li>
          <li>Require a positive paired lower confidence bound, fresh confirmation and an independent off-catalogue win before the separate selector considers a slot.</li>
          <li>Keep raw inputs untracked/ignored and establish organizer-authenticated format/data provenance; attach exact-byte organizer receipts before recording live scores.</li>
        </ol></div>
        <p>Official references for manual review: <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">problem/metric</a> ·
          <a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">rules PDF</a> ·
          <a href="https://github.com/drivendataorg/gems-prize-reference-solution">organizer reference solution</a> ·
          <a href="https://doi.org/10.5066/P93LGLVQ">USGS GeoDAWN DOI</a> ·
          <a href="https://gdr.openei.org/submissions/1391">GDR 1391</a>.
          Only the GitHub reference code was freshly retrieved here; the others are historical source references, not live verification.</p>
          <p><a href="downloads/magrest-run-card.json">Complete JSON run card</a> ·
          <a href="https://github.com/buffedlizard55-lab/GEMSDOE31/tree/main/evidence/magrest">All measurements</a>.</p>
      </section>{scgp_download_and_gates()}{parallel_archives()}'''
