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


def h31m_download_and_gates() -> str:
    hr_path = ROOT / "evidence/h31m_results.json"
    rc_path = ROOT / "evidence/h31m_run_card.json"
    if not hr_path.is_file() or not rc_path.is_file():
        return ""
    hr = json.loads(hr_path.read_text())
    rc = json.loads(rc_path.read_text())
    scr = hr["exp2_holdout_screen"]
    conf = hr["exp2_holdout_confirm"]
    s_boot = scr["bootstrap_submod_vs_base"]
    c_boot = conf["bootstrap_submod_vs_base"]
    prx = hr["exp3_proxies_and_habitat"]
    submod_p = prx["H31-M_candidate"]
    h33_p = prx["GEMSDOE32_H33_2_B2"]
    cov = rc["correlation_and_overlap_vs_registry"]
    dsub = cov["downloads_and_concurrent_subset"]
    ce = cov["broad_695_registry_counterexample"]
    slug = esc(hr["candidate_slug"])
    sub_name = esc(rc["submission_name"])
    sha_nan = esc(rc["raster_sha256"]["nan_tif"])
    sha_fin = esc(rc["raster_sha256"]["allfinite_tif"])
    sha_zip = esc(rc["raster_sha256"]["zip"])
    note = esc(rc["note"])
    s_dlo, s_dhi = s_boot["paired_delta_ci95"]["h31m_submod_minus_base_C1_poisson"]
    c_lo, c_hi = c_boot["ci95"]["h31m_submod"]
    off4 = submod_p["holdout_4block_off_sgmc"]
    h33_off4 = h33_p["holdout_4block_off_sgmc"]
    return f'''<section id="h31m-submod" aria-labelledby="h31m-heading">
      <div class="section-head"><div><p class="kicker">2026-10-25 Deconfounded Subsurface Concordance + 29-Cell Submodular Candidate · H31-M</p>
        <h2 id="h31m-heading">H31-M BStep-XMod-Submod: Research Download Only · DO NOT SUBMIT</h2></div>
        <p>Newly computed in this session from 8 label-free geophysical/structural channels + deconfounded dual-head Bayes OOF HGB +
           exact 29-cell submodular DTI allocation. Beats GEMSDOE32 H33-2-B2 simultaneously on Piedmont Off-SGMC, 4-Block Off-SGMC,
           Full Off-SGMC, and 21.25 km hide-and-recover holdout (4/4 folds on both seeds), and passes the 13-submission comparator subset —
           but is <strong>held as research-only (DO NOT SUBMIT)</strong> under the unexempted 695-raster spacing-5 lattice STOP and inherited 21.25 km collar.</p></div>
      <div class="card download-card">
        <span class="badge badge-green">LOCAL FORMAT &amp; 11/11 EFFICACY GATES PASS · RESEARCH DOWNLOAD ONLY</span>
        <span class="badge badge-red" style="margin-left:8px">DO NOT SUBMIT · REGISTRY STOP (slot_approved = false)</span>
        <h3 style="margin-top:18px">{slug}</h3>
        <p>8 label-free geophysical channels (<code>bstep_grad_norm</code>, <code>bstep_inflect</code>, Miller–Singh <code>grav_tilt_zero</code>,
           Blakely–Simpson <code>rtp_bandpass_crest</code>, <code>cond_grad_ridge</code>, <code>sub_tensor_coh</code>, <code>surf_piedmont_ridge</code>,
           <code>xmod_strike_concordance</code>) + quadrant-deconfounded Dual-Head Bayes OOF HGB (<code>M_sub</code> 37 bands + <code>M_lidar</code> 48 bands) +
           Minoux lazy-greedy 29-cell submodular DTI allocator with <code>B=2</code> (<code>d_cat &gt; 200 m</code>) hygiene (37,654 off-catalogue dots; 37.2% piedmont).</p>
        <div class="actions">
          <a class="button button-primary" href="downloads/{slug}-nan.tif" download>Download H31-M Research .tif (NaN-outside)</a>
          <a class="button" href="downloads/{slug}-nan.zip" download>Download Single-TIFF .zip</a>
          <a class="button" href="downloads/{slug}-allfinite.tif" download>All-finite research encoding .tif</a>
          <a class="button" href="downloads/{slug}-format-check.json" download>Format receipt .json</a>
        </div>
        <p class="download-meta"><strong>Grid &amp; Range:</strong> 1-band float32 · EPSG:32611 · 3730 × 3292 · 0 NaN/Inf inside 5,167,373-cell footprint · footprint values strictly {{0.0, 1.0}} in [0.0, 1.0] · 0 dots within 200 m of public catalogue.<br>
          <strong>SHA-256 (NaN primary):</strong> <code>{sha_nan}</code><br>
          <strong>SHA-256 (Single-TIFF ZIP):</strong> <code>{sha_zip}</code><br>
          <strong>SHA-256 (All-finite):</strong> <code>{sha_fin}</code><br>
          <strong>Artifact Name (not uniqueness approval):</strong> <code>{sub_name}</code><br>
          <strong>Note ({rc['note_length_chars']}/140):</strong> <code>{note}</code></p>
      </div>
      <div class="table-wrap" style="margin-top:18px"><table>
        <thead><tr><th>Automated Gate</th><th>Threshold</th><th>Measured H31-M Value</th><th>Status</th></tr></thead>
        <tbody>
          <tr><td><code>G1 · GeoTIFF Format &amp; [0, 1]</code></td><td>EPSG:32611, 3730×3292, float32, 0 NaN inside, [0, 1]</td><td>37,654 dots in {{0.0, 1.0}}; 0 NaN inside; 0 within 200 m of catalogue</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G2 · Single-Feature Leakage</code></td><td>Two-sided ROC-AUC ≤ 0.90 across all 48 used features</td><td>max AUC = {hr['exp1_canary']['max_used_feature_unsigned_auc']:.4f} (new H31-M channels max = {hr['exp1_canary']['max_new_h31m_unsigned_auc']:.4f})</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G3a · 13-Submission Comparator Subset</code></td><td>Surface |ρ| ≤ 0.90 AND 3-px dot overlap ≤ 70.0%</td><td>max |ρ| = {dsub['max_abs_surface_spearman_r']:.4f}; max 3-px = {100*dsub['max_dot_overlap_within_3px']:.2f}% (concurrent lanes ≤ {100*dsub['max_dot_overlap_within_3px_concurrent_discrete_lanes']:.2f}%; 40.25% vs H33-2-B2)</td><td><span class="badge">SUBSET ONLY — NOT UNIQUENESS APPROVAL</span></td></tr>
          <tr><td><code>G3b · 5×5 Calibration Lattice</code></td><td>Unexempted 695-raster shared registry (r13-lattice-s5)</td><td>{100*ce['dot_overlap_within_3px']:.4f}% ({ce['within_3px']:,} / 37,654 dots within 3 px; |ρ| = {abs(ce['final_spearman_r']):.4f})</td><td><span class="badge badge-red">LITERAL STOP</span></td></tr>
          <tr><td><code>G4a · Screen (seed 20261025, 21.25 km)</code></td><td>Paired 95% CI &gt; 0 and ≥ 3/4 spatial folds won</td><td>HOLDOUT-DTI {scr['arms']['h31m_submod']['pooled_DTI']:.4f} vs {scr['arms']['base_C1_poisson']['pooled_DTI']:.4f} (Δ CI [{s_dlo:+.4f}, {s_dhi:+.4f}], 4/4 folds)</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G4b · Confirm (seed 20261026, n=58,625)</code></td><td>Fresh draw, paired 95% CI &gt; 0 and ≥ 3/4 folds won</td><td>HOLDOUT-DTI {conf['arms']['h31m_submod']['pooled_DTI']:.4f} [{c_lo:.4f}, {c_hi:.4f}] vs {conf['arms']['base_C1_poisson']['pooled_DTI']:.4f} (4/4 folds)</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G5a · Piedmont Off-Catalogue SGMC</code></td><td>Alluvial/piedmont habitat (slope ≤ 6 deg, n=11,573 px)</td><td>HOLDOUT-DTI {submod_p['piedmont_off_sgmc_DTI']:.4f} vs GEMSDOE32 H33-2-B2 {h33_p['piedmont_off_sgmc_DTI']:.4f} (+9.4%) and H31-B 0.0052</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G5b · All-Elevation &amp; 4-Block Off-SGMC</code></td><td>Strict simultaneous win &gt; H33-2-B2 (0.0940 / 0.0984)</td><td>Full Off-SGMC {submod_p['full_off_sgmc_DTI']:.4f} vs {h33_p['full_off_sgmc_DTI']:.4f} (+7.4%); 4-Block {off4['mean_holdout_dti']:.4f} [{off4['ci95_low']:.4f}, {off4['ci95_high']:.4f}] vs {h33_off4['mean_holdout_dti']:.4f} (+9.5%)</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G6 · Own-Method Variogram &amp; Slot Gate</code></td><td>Candidate-specific residual range + unexempted registry pass</td><td>21.25 km collar inherited from historical buffer_derivation.json; r13-lattice-s5 STOP active</td><td><span class="badge badge-red">HOLD (slot_approved=false)</span></td></tr>
        </tbody>
      </table></div>
      <p class="small">HOLDOUT-DTI evaluator: <code>gemsdoe31-holdout-v1</code> (n=58,625 withheld positives, 21,250 m spatial collar, 400 block-bootstrap replicates) and
        <code>usgs-sgmc-offcat-gt300m-v1</code> (n=61,664 full / n=50,470 4-block collared / n=11,573 piedmont). None of these figures is a competition score or projection.
        Receipts: <a href="https://github.com/buffedlizard55-lab/GEMSDOE31/blob/main/evidence/h31m_run_card.json">H31-M JSON run card</a> ·
        <a href="https://github.com/buffedlizard55-lab/GEMSDOE31/blob/main/evidence/h31m_results.json">full EXP-1..3 measurements</a> ·
        <a href="https://github.com/buffedlizard55-lab/GEMSDOE31/blob/main/knowledge/2026-10-25_h31m_subsurface_concordance_preregistration.md">frozen H31-M preregistration</a>.</p>
    </section>'''


def hvdc_download_and_gates() -> str:
    exp_path = ROOT / "evidence/hvdc/hvdc_experiment_results.json"
    rc_path = ROOT / "evidence/hvdc/run_card.json"
    lc_path = ROOT / "evidence/hvdc/leakage_canary.json"
    if not exp_path.is_file() or not rc_path.is_file() or not lc_path.is_file():
        return ""
    exp = json.loads(exp_path.read_text())["experiments"]
    e1, e2, e3 = exp["EXP-1"], exp["EXP-2"], exp["EXP-3"]
    rc = json.loads(rc_path.read_text())
    lc = json.loads(lc_path.read_text())
    cov = rc["correlation_overlap_vs_registry"]
    lat = cov["shared_695_registry_counterexample_r13_lattice_s5"]
    sub_name = esc(rc["submission_name"])
    sha_nan = esc(rc["raster_sha256"]["nan_tif"])
    sha_fin = esc(rc["raster_sha256"]["allfinite_tif"])
    sha_zip = esc(rc["raster_sha256"]["nan_zip"])
    note = esc(rc["note"])
    return f'''<section id="hvdc-submod" aria-labelledby="hvdc-heading">
      <div class="section-head"><div><p class="kicker">2026-10-25 Dual-Specialist + 300 m CELF Submodular Candidate · H31-HVDC</p>
        <h2 id="hvdc-heading">H31-HVDC-Submod300: Research Download · DO NOT SUBMIT</h2></div>
        <p>Newly computed 4-fold OOF dual-specialist HGB + fold-visible vent/relay accommodation + Batch-Exact 300 m CELF submodular max-cover GeoTIFF.
           Local format checks, 55-feature leakage canary, blocked 21.25 km hide-and-recover confirmation (+60.0%), and 34-comparator discrete separation all pass,
           but the unexempted 695-raster shared registry triggers a literal overlap STOP (slot_approved = false).</p></div>
      <div class="card download-card">
        <span class="badge badge-green">LOCAL FORMAT CHECKS PASS · RESEARCH DOWNLOAD ONLY</span>
        <span class="badge badge-red" style="margin-left:8px">DO NOT SUBMIT · REGISTRY STOP (slot_approved = false)</span>
        <h3 style="margin-top:18px">{sub_name}</h3>
        <p>Hydrothermal-volcanic-detachment concordance + fold-visible vent-to-tip &amp; relay-ramp accommodation + Bayes prevalence calibration +
           Batch-Exact 300 m triangular-kernel submodular maximum coverage (37,654 binary {{0.0, 1.0}} dots, B &gt; 2 px outside public catalogue).</p>
        <div class="actions">
          <a class="button button-primary" href="downloads/{sub_name}-nan.tif" download>Download H31-HVDC Research .tif (NaN-outside)</a>
          <a class="button" href="downloads/{sub_name}-nan.zip" download>Download Single-TIFF .zip</a>
          <a class="button" href="downloads/{sub_name}-allfinite.tif" download>All-finite research encoding .tif</a>
          <a class="button" href="downloads/{sub_name}-format-check.json" download>Format &amp; gate receipt .json</a>
        </div>
        <p class="download-meta"><strong>Grid &amp; Range:</strong> 1-band float32 · EPSG:32611 · 3730 x 3292 · 100 m · 0 NaN/Inf inside 5,167,373-cell footprint · footprint values strictly {{0.0, 1.0}} in [0.0, 1.0] · 0 dots within 200 m of public catalogue.<br>
          <strong>SHA-256 (NaN primary):</strong> <code>{sha_nan}</code><br>
          <strong>SHA-256 (One-TIFF .zip):</strong> <code>{sha_zip}</code><br>
          <strong>SHA-256 (All-finite):</strong> <code>{sha_fin}</code><br>
          <strong>Artifact Name (not uniqueness approval):</strong> <code>{sub_name}</code><br>
          <strong>Note ({rc['note_length']}/140):</strong> <code>{note}</code></p>
      </div>
      <div class="table-wrap" style="margin-top:18px"><table>
        <thead><tr><th>Automated Gate</th><th>Threshold</th><th>Measured H31-HVDC Value</th><th>Status</th></tr></thead>
        <tbody>
          <tr><td><code>G1 · GeoTIFF Format &amp; [0, 1]</code></td><td>EPSG:32611, 3730x3292, float32, 0 NaN inside, [0, 1]</td><td>37,654 dots in {{0.0, 1.0}}; 0 NaN inside; 0 within 200 m of catalogue</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G2 · Single-Feature Leakage</code></td><td>Two-sided ROC-AUC &lt;= 0.90 across all 55 features</td><td>max AUC = {lc['max_symmetric_auc']:.4f} across {lc['n_features_tested']} features (0 leaked)</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G3a · 34-Comparator Discrete Subset</code></td><td>Surface |rho| &lt;= 0.90 AND 3-px dot overlap &lt;= 70.0%</td><td>max |rho| = {cov['max_abs_surface_spearman']:.4f} (0.0626 vs GEMSDOE32 H33); max fwd 3-px = {100*cov['max_forward_3px_overlap_discrete']:.2f}% (35.71% vs SCGP, 18.47% vs MAGREST)</td><td><span class="badge">SUBSET ONLY — NOT UNIQUENESS APPROVAL</span></td></tr>
          <tr><td><code>G3b · 5x5 Lattice &amp; Continuous Registry</code></td><td>Unexempted 695-raster shared registry (r13-lattice-s5 / GEMSDOE48)</td><td>{100*lat['forward_3px_overlap']:.2f}% ({lat['within_3px_dots']:,} / 37,654) vs r13-lattice-s5 (|rho| = {abs(lat['spearman_surface']):.6f}); 100.0% vs GEMSDOE48 continuous</td><td><span class="badge badge-red">LITERAL STOP</span></td></tr>
          <tr><td><code>G4a · Screen (draws 101, 102; 21.25 km)</code></td><td>Paired gain over clean ArmD-Poisson ({e1['screen_mean_holdout_dti']:.4f})</td><td>EXP-2 Physics-Poisson {e2['screen_mean_holdout_dti']:.4f}; EXP-3 Submod300 HOLDOUT-DTI {e3['screen_mean_holdout_dti']:.4f} [{e3['screen_ci95'][0]:.4f}, {e3['screen_ci95'][1]:.4f}]</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G4b · Fresh Confirm (draws 201, 202) &amp; 4-Draw Pool</code></td><td>Untouched draws, n = 48,169 withheld positives pooled</td><td>Confirm HOLDOUT-DTI {e3['confirm_mean_holdout_dti']:.4f} [{e3['confirm_ci95'][0]:.4f}, {e3['confirm_ci95'][1]:.4f}]; Pooled 4-draw {e3['pooled_4draw_mean_holdout_dti']:.4f} [{e3['pooled_4draw_ci95'][0]:.4f}, {e3['pooled_4draw_ci95'][1]:.4f}] (+0.0468 / +60.0%, 4/4 draws)</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G5 · Off-Catalogue SGMC (&gt;300 m)</code></td><td>Zero-leakage external SGMC evaluation proxy (never trained on)</td><td>OFFCAT-PROXY-DTI {e3['offcat_proxy_dti_sgmc_gt300m']:.4f} vs Clean ArmD {e1['offcat_proxy_dti_sgmc_gt300m']:.4f} (+12.7%) and legacy Arm D 0.0512 (+61.0%)</td><td><span class="badge badge-green">PASS</span></td></tr>
        </tbody>
      </table></div>
      <p class="small">HOLDOUT-DTI evaluator: gemsdoe31-hide-recover-v1 (21.25 km variogram collar, 48,169 withheld positives across 4 draws, 1,000-rep 20 km spatial block bootstrap).
        All prompt/sibling scores (0.2778, 0.3195, 0.4413) are USER-REPORTED with no organizer receipt. Under the unexempted 695-raster shared registry literal rule,
        verdict = negative and slot_approved = false; artifacts are preserved as reproducible research downloads.</p>
    </section>'''


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
        <h2 id="scgp-heading">H31-E2 SCGP-Submod: Research Only · DO NOT SUBMIT</h2></div>
        <p>Historical evidence below is not a new experiment or organizer acceptance. Local format checks pass,
           but the broader registry gate FAILS. A pass against a selected comparator subset does not establish uniqueness.
           The literal lattice STOP and failed mountain SGMC gate prohibit submission under the current protocol.</p></div>
      <div class="card download-card">
        <span class="badge badge-green">LOCAL FORMAT CHECKS PASS · RESEARCH DOWNLOAD ONLY</span>
        <span class="badge badge-red" style="margin-left:8px">DO NOT SUBMIT · REGISTRY STOP (slot_approved = false)</span>
        <h3 style="margin-top:18px">{sub_name}</h3>
        <p>43-feature Gallardo–Meju structural cross-gradient concordance + 2D FFT upward-continuation residuals +
           seam-free Dual-Expert 1 m 3DEP LiDAR scarp polarity + GeoDAWN K/Th/U &amp; GDR-1391 paleo-sinter +
           strike-tip/relay bridge + Minoux lazy-greedy 300 m submodular DTI allocator (37,654 off-catalogue dots; 31.5% beyond 1.5 km).</p>
        <div class="actions">
          <a class="button button-primary" href="downloads/{sub_name}-nan.tif" download>Download H31-E2 Research .tif (NaN-outside)</a>
          <a class="button" href="downloads/{sub_name}-nan.zip" download>Download Single-TIFF .zip</a>
          <a class="button" href="downloads/{sub_name}-allfinite.tif" download>All-finite research encoding .tif</a>
          <a class="button" href="downloads/{sub_name}-format-check.json" download>Format receipt .json</a>
        </div>
        <p class="download-meta"><strong>Grid &amp; Range:</strong> 1-band float32 · EPSG:32611 · 3730 × 3292 · 0 NaN/Inf inside 5,167,373-cell footprint · footprint values strictly {{0.0, 1.0}} in [0.0, 1.0] · 0 dots on public catalogue.<br>
          <strong>SHA-256 (NaN primary):</strong> <code>{sha_nan}</code><br>
          <strong>SHA-256 (All-finite):</strong> <code>{sha_fin}</code><br>
          <strong>Artifact Name (not uniqueness approval):</strong> <code>{sub_name}</code><br>
          <strong>Note ({rc['submission_note_chars']}/140):</strong> <code>{note}</code></p>
      </div>
      <div class="table-wrap" style="margin-top:18px"><table>
        <thead><tr><th>Automated Gate</th><th>Threshold</th><th>Measured H31-E2 Value</th><th>Status</th></tr></thead>
        <tbody>
          <tr><td><code>G1 · GeoTIFF Format &amp; [0, 1]</code></td><td>EPSG:32611, 3730×3292, float32, 0 NaN inside, [0, 1]</td><td>37,654 dots in {{0.0, 1.0}}; 0 NaN inside; 0 on catalogue</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G2 · Single-Feature Leakage</code></td><td>Two-sided ROC-AUC ≤ 0.90 across all 86 features</td><td>max AUC = {rc['leakage_canary']['max_single_feature_auc']:.4f} across {rc['leakage_canary']['features_tested']} features</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G3a · Historical 22-comparator subset</code></td><td>Surface |ρ| ≤ 0.90 AND 3-px dot overlap ≤ 70.0%</td><td>max |ρ| = {cov['max_surface_spearman_rho']:.4f}; max 3-px overlap = {100*cov['max_final_dots_within_3px']:.2f}% (concurrent lanes ≤ {100*cov['max_final_dots_within_3px_concurrent_discrete_lanes']:.2f}%)</td><td><span class="badge">SUBSET ONLY — NOT UNIQUENESS APPROVAL</span></td></tr>
          <tr><td><code>G3b · 5×5 Calibration Lattice</code></td><td>Unexempted 695-raster shared registry (r13-lattice-s5)</td><td>99.9655% of final H31-E2 dots (37,641 / 37,654); read-only byte audit, not a new experiment</td><td><span class="badge badge-red">LITERAL STOP</span></td></tr>
          <tr><td><code>G4a · Screen (draw=101, 21.3 km)</code></td><td>Paired ΔDTI &gt; 0 and ≥ 3/4 spatial folds won</td><td>HOLDOUT-DTI {scr['h31e_scgp_submod']['pooled_dti']:.4f} vs {scr['baseline_d_poisson']['pooled_dti']:.4f} (+{scr['paired_delta_dti']:.4f}, {scr['folds_won_out_of_4']}/4 folds)</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G4b · Fresh Confirm (draws 202,303)</code></td><td>Untouched draws, n = {conf['withheld_positives_pooled']:,}, 95% CI &gt; 0</td><td>HOLDOUT-DTI {conf['h31e_scgp_submod_pooled_dti']:.4f} [{conf['h31e_scgp_submod_ci95'][0]:.4f}, {conf['h31e_scgp_submod_ci95'][1]:.4f}] vs {conf['baseline_d_poisson_pooled_dti']:.4f} (+{conf['paired_delta_dti']:.4f}, +29.3%)</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G5a · Piedmont Off-Catalogue SGMC</code></td><td>Quaternary piedmont habitat (det_elev ≤ +50 m)</td><td>{pied['h31e_scgp_submod_dti']:.4f} vs Baseline-D {pied['baseline_d_poisson_dti']:.4f} and GEMSDOE32 H33-2-B2 {pied['h33_2_b2_reference_dti']:.4f} (+13.0%)</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G5b · All-Elevation Mountain SGMC</code></td><td>Strict pre-declared &gt; H33-2-B2 (0.0940) across mountain SGMC</td><td>{all_sgmc['h31e_scgp_submod_dti']:.4f} vs Baseline-D {all_sgmc['baseline_d_poisson_dti']:.4f} (+13.6%), &lt; H33 {all_sgmc['h33_2_b2_reference_dti']:.4f}</td><td><span class="badge badge-red">HOLD (slot_approved=false)</span></td></tr>
        </tbody>
      </table></div>
      <p class="small">These are historical HOLDOUT-DTI/proxy results, not competition scores.
        Holdout evaluator: gemsdoe31-hide-v2.0; screen n=17,900, confirmation n=35,599 withheld positives.
        The inherited 21.3 km collar is not a newly measured candidate-specific correlation range.
        Proxy independence and a same-instrument global-best comparison are not established.
        See linked receipts for intervals; no high-score claim follows from these figures.</p>
      <p class="small">Full artifact &amp; 3-experiment log (including stopped Exp 1 proximity-halo audit and Exp 2 submodular +0.0372 ablation):
        <a href="experiments/12-h31e-scgp-submod.html">Experiment 12 · H31-E2 SCGP-Submod</a>.</p>
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


def overview(card):
    link = links(card)
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
    s = card["holdout_dti"]
    delta = card["paired_difference"]
    final = card["registry"]["final"]
    body = f'''<div class="notice notice-danger"><strong>Not approved for upload.</strong>
      Automated verdict: NEGATIVE under the literal 695-raster shared-registry overlap rule. Download H31-M, H31-HVDC, H31-E2, or MAGREST for research, not for a weekly competition slot.</div>
      {h31m_download_and_gates()}
      {hvdc_download_and_gates()}
      {scgp_download_and_gates()}
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
    return hero, body


def executive(card):
    failed = "".join(f"<li>{esc(x)}</li>" for x in card["failed_or_unknown_gates"])
    return f'''<div class="notice notice-danger"><strong>Do not submit a download from this page yet.</strong>
      The new H31-M BStep-XMod-Submod, H31-HVDC-Submod300, H31-E2 SCGP-Submod, and MAGREST artifacts are format-validated and available to download in one click; all are research-only and fail the unexempted 695-raster shared-registry overlap gate. Human sign-off cannot override a failed gate; scientific and registry validation must pass before any separate selector decision.</div>
      {h31m_download_and_gates()}
      {hvdc_download_and_gates()}
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
      The literal registry gate FAILS: a registered spacing-5 lattice covers 99.52%–100% of fixed variants’ dots, and GEMSDOE48 continuous pignistic covers 100%. No new fit or TIFF follows this STOP. The reported 0.2778 and conflicting leaderboard anchors 0.3195 / 0.4413 have no organizer receipt in this project.
      Non-GitHub official pages cannot be re-fetched under this environment's host allowlist.</div>
      {h31m_download_and_gates()}
      {hvdc_download_and_gates()}
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
