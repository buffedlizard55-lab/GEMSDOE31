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
    support = registry_support_summary()
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
           but is <strong>held as research-only (DO NOT SUBMIT)</strong>: its {100*ce['dot_overlap_within_3px']:.4f}% candidate-specific overlap with r13-lattice-s5 exceeds the literal 70% limit; separately, the GEMSDOE48 continuous field is a full-support witness under finite-value &gt; 0 semantics, and the inherited 21.25 km collar precedes own-method range estimation.</p></div>
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
          <tr><td><code>G3b · r13-lattice-s5 candidate overlap</code></td><td>Unexempted 695-raster shared registry; no calibration/density exemption</td><td>{100*ce['dot_overlap_within_3px']:.4f}% ({ce['within_3px']:,} / 37,654 dots within 3 px of r13; |ρ| = {abs(ce['final_spearman_r']):.4f}); separately, GEMSDOE48 support is {support['continuous_positive_pixels']:,}/{support['continuous_allowed_pixels']:,} allowed cells under {esc(support['support_definition'])}</td><td><span class="badge badge-red">LITERAL STOP</span></td></tr>
          <tr><td><code>G4a · Screen (seed 20261025, 21.25 km)</code></td><td>Paired 95% CI &gt; 0 and ≥ 3/4 spatial folds won</td><td>HOLDOUT-DTI {scr['arms']['h31m_submod']['pooled_DTI']:.4f} vs {scr['arms']['base_C1_poisson']['pooled_DTI']:.4f} (Δ CI [{s_dlo:+.4f}, {s_dhi:+.4f}], 4/4 folds)</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G4b · Confirm (seed 20261026, n=58,625)</code></td><td>Fresh draw, paired 95% CI &gt; 0 and ≥ 3/4 folds won</td><td>HOLDOUT-DTI {conf['arms']['h31m_submod']['pooled_DTI']:.4f} [{c_lo:.4f}, {c_hi:.4f}] vs {conf['arms']['base_C1_poisson']['pooled_DTI']:.4f} (4/4 folds)</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G5a · Piedmont Off-Catalogue SGMC</code></td><td>Alluvial/piedmont habitat (slope ≤ 6 deg, n=11,573 px)</td><td>HOLDOUT-DTI {submod_p['piedmont_off_sgmc_DTI']:.4f} vs GEMSDOE32 H33-2-B2 {h33_p['piedmont_off_sgmc_DTI']:.4f} (+9.4%) and H31-B 0.0052</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G5b · All-Elevation &amp; 4-Block Off-SGMC</code></td><td>Strict simultaneous win &gt; H33-2-B2 (0.0940 / 0.0984)</td><td>Full Off-SGMC {submod_p['full_off_sgmc_DTI']:.4f} vs {h33_p['full_off_sgmc_DTI']:.4f} (+7.4%); 4-Block {off4['mean_holdout_dti']:.4f} [{off4['ci95_low']:.4f}, {off4['ci95_high']:.4f}] vs {h33_off4['mean_holdout_dti']:.4f} (+9.5%)</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G6 · Own-Method Variogram &amp; Slot Gate</code></td><td>Candidate-specific residual range + unexempted registry pass</td><td>21.25 km collar inherited from historical buffer_derivation.json; r13 candidate-overlap STOP and distinct GEMSDOE48 full-support witness; own-method range not estimated</td><td><span class="badge badge-red">HOLD (slot_approved=false)</span></td></tr>
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


def registry_support_summary() -> dict:
    correction = json.loads((ROOT / "evidence/registry_overlap_claim_correction_2026-10-26.json").read_text())
    lattice, continuous = correction["corrected_facts"]
    return {
        "lattice_footprint_coverage_pct": 100 * lattice["three_pixel_halo_footprint_coverage"],
        "continuous_repo": continuous["source_repo"],
        "continuous_positive_pixels": continuous["positive_support_pixels"],
        "continuous_allowed_pixels": continuous["allowed_pixels"],
        "support_definition": continuous["support_definition"],
        "correction_path": "evidence/registry_overlap_claim_correction_2026-10-26.json",
    }


def public_failed_gate_messages(card: dict) -> list[str]:
    """Apply additive attribution corrections without rewriting the frozen run card."""
    support = registry_support_summary()
    final = card.get("registry", {}).get("final", {})
    lattice_overlap = final.get("counterexample_overlap")
    if lattice_overlap is None:
        lattice_text = "The frozen run's measured candidate-specific overlap with r13-lattice-s5 remains above the literal 70% threshold."
    else:
        lattice_text = (
            f"The frozen MAGREST variants have {100 * lattice_overlap:.2f}% candidate-specific overlap with r13-lattice-s5; "
            f"that lattice's 3-px halo covers {support['lattice_footprint_coverage_pct']:.4f}% of the footprint, not universally 100%."
        )
    witness = (
        f"A separate {support['continuous_repo']} continuous raster has positive support on "
        f"{support['continuous_positive_pixels']:,}/{support['continuous_allowed_pixels']:,} allowed cells under "
        f"{support['support_definition']} semantics; this is the distinct full-support witness."
    )
    corrected = (
        "Literal registry-overlap STOP remains. " + lattice_text + " " + witness
        + " No density/calibration exemption; historical run-card text is preserved. "
        + "See evidence/registry_overlap_claim_correction_2026-10-26.json"
    )
    messages = []
    for message in card.get("failed_or_unknown_gates", []):
        if message.startswith("Literal registry-overlap STOP: 100% of primary dots within 3 px of a registered spacing-5 lattice"):
            messages.append(corrected)
        else:
            messages.append(message)
    return messages


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
    # This is an archived experiment, never the active run or a selector approval.
    scr = hr["experiment_1_screen_draw_101"]
    conf = hr.get("experiment_2_confirmation")
    proxies = hr["experiment_3_sgmc_proxies"]["candidates"]
    pr, pb, ph = proxies["rbu31"], proxies["baseline_d_final"], proxies["h33_2_b2_actual_peer_file"]
    dup = rc["correlation_overlap_vs_registry"]
    support = registry_support_summary()
    name = esc(rc["submission_name"])
    note = esc(rc["submission_note"])

    def badge(ok):
        return '<span class="badge badge-green">PASS</span>' if ok else '<span class="badge badge-red">FAIL</span>'

    verdict_badge = '<span class="badge badge-red">&#10060; RESEARCH DOWNLOAD ONLY &middot; DO NOT SUBMIT</span>'
    heading = "Historical RBU31 research artifact: &#10060; DO NOT SUBMIT"
    conf_row = ("not run (screen stop)" if not conf else
                f"HOLDOUT-DTI {conf['rbu31_pooled_dti']:.4f} [{conf['rbu31_ci95'][0]:.4f}, {conf['rbu31_ci95'][1]:.4f}] "
                f"vs {conf['baseline_d_pooled_dti']:.4f} (delta {conf['paired_delta_dti']:+.4f}, "
                f"95% CI [{conf['paired_delta_ci95'][0]:+.4f}, {conf['paired_delta_ci95'][1]:+.4f}]); "
                f"{conf['withheld_positives_pooled']:,} withheld positives")
    return f'''<section id="rbu31" aria-labelledby="rbu31-heading">
      <div class="section-head"><div><p class="kicker">Historical research artifact &middot; RBU31 (Experiment 13)</p>
        <h2 id="rbu31-heading">{heading}</h2></div>
        <p>Archived union model (raw-39 + SCGP-40 features) with regime-balanced sample weights. Its automated results are
           historical and negative; they do not make the artifact current, globally unique, or approved for upload.</p></div>
      <div class="card download-card">
        {verdict_badge}
        <h3 style="margin-top:18px">{name}</h3>
        <p><b>Historical hypothesis, not a score projection:</b> RBU31 attempted to combine buried-piedmont geophysics
           and mountain scarps. Its local holdout and SGMC results below are negative/inconclusive and do not establish
           an improvement over any organizer score or a global-best submission.</p>
        <div class="actions">
          <a class="button button-primary" href="downloads/{name}-allfinite.tif" download>&#11015; Download RBU31 research TIFF — DO NOT SUBMIT</a>
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
          <strong>Artifact name (not uniqueness or upload approval):</strong> <code>{name}</code><br>
          <strong>Reserved portal note; do not upload ({rc['submission_note_chars']}/140):</strong> <code>{note}</code></p>
      </div>
      <div class="table-wrap" style="margin-top:18px"><table>
        <thead><tr><th>Automated gate</th><th>Threshold</th><th>Measured RBU31 value</th><th>Status</th></tr></thead>
        <tbody>
          <tr><td><code>G1 &middot; Format &amp; [0, 1]</code></td><td>EPSG:32611, 3730&times;3292, float32, finite in footprint, values in [0, 1]</td><td>see format receipt</td><td>{badge(gates['G1_format_and_range_0_1_pass'])}</td></tr>
          <tr><td><code>G2 &middot; Leakage canary</code></td><td>every one of 79 features alone: two-sided AUC &le; 0.90</td><td>max AUC = {rc['leakage_canary']['max_two_sided_auc']:.4f}</td><td>{badge(gates['G2_leakage_canary_pass'])}</td></tr>
          <tr><td><code>G3a &middot; Uniqueness vs genuine submissions</code></td><td>surface |&rho;| &le; 0.90 and 3-px dot overlap &le; 70% vs {dup['checked_count']} registry/peer rasters (incl. the 9 focus sites' best)</td><td>max |&rho;| = {max(abs(dup['max_surface_spearman_rho']), abs(dup['max_final_dots_spearman_rho'])):.4f}; max 3-px overlap = {100*dup['max_final_dots_within_3px']:.2f}%</td><td>{badge(gates['G3a_uniqueness_genuine_registry_pass'])}</td></tr>
          <tr><td><code>G3b &middot; Shared-registry support (695-raster audit)</code></td><td>literal rule; no calibration/density exemption</td><td>Separate {support['continuous_repo']} continuous raster: positive support on {support['continuous_positive_pixels']:,}/{support['continuous_allowed_pixels']:,} allowed cells under {esc(support['support_definition'])}. The r13 spacing-5 lattice is distinct; its 3-px halo covers {support['lattice_footprint_coverage_pct']:.4f}% of the footprint, not 100% universally.</td><td><span class="badge badge-red">STOP / NOT APPROVED</span></td></tr>
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
    submit_approved = card.get("ok_to_submit") is True and card.get("slot_approved") is True
    research_download = card.get("ok_to_download_for_research") is True
    if submit_approved:
        status = "APPROVED FOR SUBMISSION"
        button = "Download approved current-run TIFF"
        note = "Follow the exact-byte receipt and verify the weekly quota before upload."
        badge_class = "badge-green"
        portal_note_label = "Portal note"
    elif research_download:
        status = "RESEARCH DOWNLOAD ONLY · DO NOT SUBMIT"
        button = "Download current research TIFF — DO NOT SUBMIT"
        note = "The active run is negative/inconclusive and the literal duplicate gate is STOPPED; no submission slot is approved."
        badge_class = "badge-red"
        portal_note_label = "Reserved note (do not upload unless separately approved)"
    else:
        status = "NOT CLEARED FOR SUBMISSION"
        button = "Download current-run artifact"
        note = "No verified submission approval is recorded. Do not upload this file."
        badge_class = "badge-red"
        portal_note_label = "Reserved note (not approved for upload)"
    return f'''<section id="download" aria-labelledby="download-heading">
      <div class="section-head"><div><p class="kicker">Active run · exact file from registry/current_run.json</p>
        <h2 id="download-heading">{status}</h2></div>
        <p>{note}</p></div>
      <div class="card download-card">
        <span class="badge {badge_class}">{status} · slot_approved={str(bool(card.get('slot_approved'))).lower()}</span>
        <h3 style="margin-top:18px">{esc(card['submission_name'])}</h3>
        <p>Active MAGREST artifact; newly computed from magnetic data, not copied or thinned from a prior submission.</p>
        <div class="actions">
          <a class="button button-dark" href="{link('file')}" download>{button}</a>
          <a class="button" href="{link('zip_file')}" download>One-TIFF ZIP</a>
          <a class="button" href="downloads/magrest-run-card.json" download>Validation + run card</a>
        </div>
        <p class="download-meta"><strong>Primary encoding:</strong> float32 · one band · EPSG:32611 · 3730 × 3292 · 100 m ·
          values exactly 0 or 1 · finite everywhere · zero outside footprint · no nodata tag.<br>
          <strong>SHA-256:</strong> <code>{esc(card['raster_sha256'])}</code><br>
          <strong>Artifact name:</strong> <code>{esc(card['submission_name'])}</code><br>
          <strong>{portal_note_label} ({len(card['note'])}/140):</strong> <code>{esc(card['note'])}</code></p>
        <p class="small" style="margin-top:18px"><a href="{link('nan_file')}" download>NaN-outside version</a> ·
          <a href="{link('nan_zip')}" download>NaN one-TIFF ZIP</a>.
          Same predictions inside the footprint. The recorded problem-page wording uses NaN/null outside;
          the all-finite primary is a defensive range-check encoding, not proof of organizer acceptance.
          Both variants inherit the active run's approval status; format validation alone never approves upload.
          The downloadable run card is the original frozen receipt; the additive registry correction explains its older lattice-attribution wording.</p>
      </div>
    </section>'''


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
    _sgmc = h3.get('holdout_off_catalogue_sgmc', {}) or {}
    _gap = h3.get('holdout_catalogue_gap', {}).get('H3-lidar-scarp-unique', {}) or {}
    dti_sgmc = _sgmc.get('HOLDOUT_DTI')
    dti_gap = _gap.get('HOLDOUT_DTI')
    canary_sgmc = h3.get('canary', {}).get('auc_off_catalogue_sgmc', 0) or 0
    canary_cat = h3.get('canary', {}).get('auc_catalogue', 0) or 0
    sgmc_cell = f"HOLDOUT-DTI {dti_sgmc:.4f} (61,664 proxy truth cells)" if dti_sgmc is not None else "Not reported"
    gap_cell = f"HOLDOUT-DTI {dti_gap:.4f} vs D28 incumbent 0.0435" if dti_gap is not None else "Not reported"
    return f'''
<section id="h3-download" aria-labelledby="h3-heading">
  <div class="section-head"><div><p class="kicker">Historical research artifact · H3 LiDAR scarp · 2026-10-25</p>
    <h2 id="h3-heading">Research download only. NOT approved for upload.</h2></div>
    <p>Its holdout proxies disagree, and the original run lacked a broad registry check. Later registered evidence includes a separate full-support GEMSDOE48 continuous raster under finite-value &gt; 0 semantics; this archived H3 file is not submission-approved.</p></div>
  <div class="card download-card">
    <span class="badge badge-red">RESEARCH ONLY · verdict = negative · not promoted</span>
    <h3 style="margin-top:18px">{esc(name)}</h3>
    <p>LiDAR generic scarp (ex_max percentile rank, gaussian 0.8px) at 2.8px Poisson-disk spacing.
       {dots:,} dots, {on_cat} dots on the public catalogue. New dots — not copied from any prior submission.</p>
    <div class="actions">
      <a class="button button-dark" href="downloads/{name}-nan.tif" download>Download H3 Research .tif (NaN-outside)</a>
      <a class="button" href="downloads/{name}-allfinite.tif" download>All-finite research encoding .tif</a>
      <a class="button" href="downloads/{name}-nan.zip" download>One-TIFF .zip</a>
      <a class="button" href="../evidence/h3_unique_submission.json" download>Run card .json</a>
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
        <tr><td>Holdout DTI — off-catalogue SGMC</td><td>{sgmc_cell}</td></tr>
        <tr><td>Holdout DTI — catalogue-gap (seed 1)</td><td>{gap_cell}</td></tr>
        <tr><td>Format validation (NaN)</td>
            <td><span class="badge {'badge-green' if ok_nan else 'badge-red'}">{'PASS' if ok_nan else 'FAIL'}</span></td></tr>
        <tr><td>Format validation (all-finite)</td>
            <td><span class="badge {'badge-green' if ok_fin else 'badge-red'}">{'PASS' if ok_fin else 'FAIL'}</span></td></tr>
        <tr><td>Historical broad-registry gate</td>
            <td><span class="badge badge-red">NOT APPROVED — original preflight incomplete; separate full-support witness blocks under the recorded support rule</span></td></tr>
        <tr><td>Submission approval</td>
            <td><span class="badge badge-red">NOT APPROVED — do not upload</span></td></tr>
      </tbody>
    </table>
  </div>
</section>
'''


def overview(card):
    # Render the active run from registry/current_run.json, never an older experiment card.
    link = links(card)
    submit_approved = card.get("ok_to_submit") is True and card.get("slot_approved") is True
    research_download = card.get("ok_to_download_for_research") is True
    name = esc(card["submission_name"])
    if submit_approved:
        status = "APPROVED FOR SUBMISSION"
        cta = "Download approved current-run TIFF"
        lede = f"The active run ({name}) is explicitly marked okay to submit and has selector approval. Verify the exact receipt and quota before upload."
    elif research_download:
        status = "RESEARCH DOWNLOAD ONLY · DO NOT SUBMIT"
        cta = "Download MAGREST research TIFF — DO NOT SUBMIT"
        lede = f"The active run ({name}) is a research-only artifact. Its efficacy screen is negative/inconclusive and the literal duplicate gate is STOPPED; no submission slot is approved."
    else:
        status = "NOT CLEARED FOR SUBMISSION"
        cta = "Download current-run artifact"
        lede = f"The active run ({name}) has no verified submission approval. Do not upload it."
    hero = f'''<section class="hero"><div class="wrap hero-grid"><div>
      <p class="eyebrow">DOE GEMS Prize · active run · {name}</p>
      <h1>{status}</h1>
      <p class="hero-lede">{lede}</p>
      <div class="actions"><a class="button button-primary" href="{link('file')}" download>{cta}</a>
        <a class="button button-light" href="executive-summary.html">Status + submission guide</a></div>
      </div><aside class="hero-side" aria-label="Submission decision">
        <strong>{status}</strong>
        <p>Format validity is separate from efficacy, registry uniqueness, selector approval, organizer acceptance, and weekly quota.
          No local HOLDOUT-DTI or SGMC proxy is a competition score.</p></aside></div></section>'''
    return hero, _overview_body(card)


def _overview_body(card):
    s = card["holdout_dti"]
    delta = card["paired_difference"]
    final = card["registry"]["final"]
    support = registry_support_summary()
    r13_coverage = support["lattice_footprint_coverage_pct"]
    body = f'''<div class="notice notice-danger"><strong>Active status: RESEARCH DOWNLOAD ONLY — DO NOT SUBMIT.</strong>
      MAGREST is the current run. RBU31, H31-M, H31-HVDC, H31-E2, and H3 are archived research artifacts with their own negative or blocked records; none is a recommended upload.</div>
      {download(card)}
      {rbu31_download_and_gates()}
      {h31m_download_and_gates()}
      {hvdc_download_and_gates()}
      {scgp_download_and_gates()}
      {h3_download_and_gates()}
      <section><div class="section-head"><div><p class="kicker">Separate gates</p><h2>What passed, and what did not</h2></div>
        <p>These statuses come from the active run card, exact-file receipts, holdout terms, and registered overlap evidence.</p></div>
        <div class="grid grid-4">
          <div class="card stat"><span class="badge badge-green">PASS</span><h3>File format</h3><p>Exact grid; finite in-footprint values in [0,1]. Local validation is not organizer acceptance.</p></div>
          <div class="card stat"><span class="badge badge-red">STOP · 100% candidate overlap</span><h3>Registry separation</h3><p>The r13 lattice's 3-px halo overlaps all MAGREST dots; a separate full-support continuous raster is the universal witness under the current &gt;0 rule.</p></div>
          <div class="card stat"><span class="badge badge-red">NEGATIVE / INCONCLUSIVE</span><h3>Scientific screen</h3><p>The paired 95% interval crosses zero; this is not evidence of a competition-score gain.</p></div>
          <div class="card stat"><span class="badge badge-red">BLOCKED</span><h3>Submit?</h3><p>No selector approval or organizer receipt. The research download is not approved for submission.</p></div>
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
          MAGREST final dots within 3 px of the r13 spacing-5 lattice: {100*final['max_overlap']:.2f}%.
          The lattice's own 3-px halo covers {r13_coverage:.4f}% of the footprint, not 100% universally. Separately, a registered {support['continuous_repo']} continuous raster has positive support on all {support['continuous_allowed_pixels']:,} allowed cells under the {esc(support['support_definition'])} interpretation; that distinct full-support witness yields 100% forward overlap. No calibration/density exemption applies. The nine-tree subset audit is not a broad-registry pass.</p>
      </section>
      <section><div class="section-head"><div><p class="kicker">Research, not optimism</p><h2>Why the previous family looked strong</h2></div>
        <p>Geometry can be measured. A reported score's cause cannot be authenticated without exact-byte organizer evidence.</p></div>
        <div class="grid grid-2"><div class="card"><h3>H33 is plausibly a pruning rule, not a new detector</h3>
          <p>The repository's pixel audit finds H33 support matches D2.8 with dots within 2 pixels of the public catalogue.
            This geometry may reduce redundant false-positive cost under the triangular DTI kernel, but it does not prove why the user-reported 0.2778 occurred.</p></div>
          <div class="card"><h3>Can we beat the reported 0.2778?</h3><p>Unknown. No result here establishes that.
            A new candidate needs validated fault-specific information and a significant comparable holdout win;
            none would establish an organizer score without a receipt.</p></div></div>
        <p><a href="research.html">Full nine-repository review, hypotheses and geological limits</a> ·
          <a href="validation.html">Validation details</a> · <a href="register/index.html">Evidence registers</a></p>
      </section>'''
    return body


def focus_site_summary() -> str:
    """Show the highest owner-reported artifact per requested site, never as upload advice."""
    path = ROOT / "registry/focus_review.json"
    if not path.is_file():
        return ""
    rows = json.loads(path.read_text()).get("rows", [])
    best = {}
    for row in rows:
        try:
            score = float(row["claim_value"])
        except (KeyError, TypeError, ValueError):
            continue
        site = row.get("repository")
        if site and (site not in best or score > best[site][0]):
            best[site] = (score, row)

    site_order = ["GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28",
                  "GEMSDOE30", "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"]
    rendered = []
    for site in site_order:
        result = best.get(site)
        if result is None:
            rendered.append(f"<tr><td>{esc(site)}</td><td colspan=\"4\">No pinned candidate record in the current audit.</td></tr>")
            continue
        score, row = result
        overlap = row.get("fraction_within_3px_of_h33")
        overlap_text = "not available" if overlap is None else f"{100 * overlap:.1f}% of dots within 3 px of H33"
        artifact = esc(row["artifact"])
        url = esc(row["source_url"])
        method = esc(row.get("method", "Not established in the current audit"))
        sha = esc(row.get("sha256", ""))
        rendered.append(
            f'<tr><td><strong>{esc(site)}</strong></td>'
            f'<td><a href="{url}" target="_blank" rel="noopener">{artifact}</a>'
            f'<br><span class="small">SHA-256 <code>{sha[:12]}…</code></span></td>'
            f'<td>{score:.4f}<br><span class="badge">USER-REPORTED · no organizer receipt</span></td>'
            f'<td>{method}</td><td>{overlap_text}</td></tr>'
        )
    return f'''<section id="focus-sites"><div class="section-head"><div>
      <p class="kicker">Nine requested repositories · highest claim per site</p>
      <h2>Prior-art comparison — not a list of upload recommendations</h2></div>
      <p>Scores below are the claims supplied by the owner and pinned to repository artifacts where available.
        They are not organizer-confirmed scores. The highest listed claim is GEMSDOE32 H33-2-B2 (0.2778),
        but H33 is a D2.8 catalogue-distance prune, not a new detector, and is not eligible as a unique new submission.</p></div>
      <div class="notice notice-danger"><strong>Decision: none of these historical files is cleared to submit as a new unique candidate.</strong>
        The selected files are prior art; each has &gt;70% of its positive dots within 3 px of the pinned H33 raster
        (the reference itself is 100%). Do not copy or rename them. Every score in this table remains USER-REPORTED.</div>
      <div class="table-wrap"><table><thead><tr><th>Site</th><th>Highest listed artifact (pinned mirror)</th>
        <th>Claimed score</th><th>Method / interpretation</th><th>Measured relation to H33</th></tr></thead>
        <tbody>{''.join(rendered)}</tbody></table></div>
      <p class="small">The table shortens each SHA-256 for readability; full digests and evidence classes are in the <a href="register/index.html">submission register</a> and <code>registry/focus_review.json</code>.</p>
      <p class="small"><strong>GEMSDOE31 irregularity:</strong> the user-listed 0.2708 H27-4 claim conflicts with the pinned owner-page status
        recorded in <code>registry/irregularities.json</code> (listed as unscored); exact organizer receipt-to-file attribution is absent.
        This table is a forensic index, not a live leaderboard snapshot or a recommendation to spend a slot.</p>
    </section>'''


def executive(card):
    failed = "".join(f"<li>{esc(x)}</li>" for x in public_failed_gate_messages(card))
    focus_summary = focus_site_summary()
    submit_approved = card.get("ok_to_submit") is True and card.get("slot_approved") is True
    active_status = "APPROVED FOR SUBMISSION" if submit_approved else "RESEARCH DOWNLOAD ONLY · DO NOT SUBMIT"
    return f'''<div class="notice notice-danger"><strong>Active run: {active_status}.</strong>
      MAGREST is the active run card and is available for research download only. RBU31, H31-M, H31-HVDC, H31-E2, and H3 are archived research records; none is a submission recommendation. A valid TIFF, local HOLDOUT-DTI, or SGMC proxy is not organizer acceptance or a competition score. No human or selector approval overrides a failed hard gate.</div>
      {download(card)}
      {focus_summary}
      {rbu31_download_and_gates()}
      {h31m_download_and_gates()}
      {hvdc_download_and_gates()}
      {scgp_download_and_gates()}
      {h3_download_and_gates()}
      <section><div class="section-head"><div><p class="kicker">Exact active-run decision</p><h2>Why upload is blocked</h2></div>
        <p>File validity, registry uniqueness, scientific efficacy, selector approval, and organizer acceptance are separate questions.</p></div>
        <div class="card"><ul>{failed}</ul></div>
      </section>
      <section><div class="section-head"><div><p class="kicker">For a future approved candidate</p><h2>How to enter a submission</h2></div>
        <p>These are portal instructions, not permission to submit the current research file.</p></div>
        <div class="card"><ol>
          <li>Confirm the generated readiness receipt says <code>ok_to_submit: true</code> and a separate selector approval exists for the exact file. Today they do not.</li>
          <li>Download the approved <code>.tif</code> or the ZIP containing that single TIFF. Do not upload a report, run-card JSON, input feature stack or multi-file ZIP.</li>
          <li>Use your own <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">DrivenData competition page</a> to open New submission, accept the rules and check the remaining weekly quota. This project does not know or spend your current quota.</li>
          <li>Under File to submit, select that approved file. Use its generated name and paste its note (at most 140 characters) into Note (optional).</li>
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
      The old workflow, extra HTML page and obsolete active-homepage assertion are archived rather than re-enabled. The current site remains within the 21-page budget.</p></section>'''


def research(card, screen, focus, lineage):
    score_rows = "".join(f"<tr><td>{esc(name)}</td><td>{score_text(row)}</td><td>{row['withheld_positive_pixels']:,}</td></tr>"
                         for name, row in screen["holdout"]["scores"].items())
    review_rows = "".join(f'''<tr><td>{esc(r['repository'])}</td><td><a href="{esc(r['source_url'])}">{esc(r['artifact'])}</a></td>
      <td>{esc(r['claim_value'])}<br><span class="badge">USER-REPORTED</span></td><td>{r['positive_pixels']:,}</td><td>{esc(r['method'])}</td></tr>'''
      for r in focus["rows"])
    rel = lineage["relations"]
    proxy = card["sgmc_proxy"]
    return f'''<div class="notice"><strong>Evidence boundary</strong>Only measured geometry and local holdouts are verified here.
      The literal registry gate FAILS. The r13 spacing-5 lattice's 3-px halo covers 99.8713% of the footprint (not universally 100%) and overlaps specific frozen candidates by 99.52%–100%. A distinct GEMSDOE48 continuous raster has positive support on all 5,167,373 allowed cells under finite-value &gt; 0 semantics; this is the separate universal witness. No new fit or TIFF follows this STOP. The 0.2778 and conflicting 0.3195 / 0.4413 anchors remain USER-REPORTED without organizer receipts. No official external page was freshly fetched in this review.</div>
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
      <section><div class="section-head"><div><p class="kicker">Desk-only · not authorized for execution</p><h2>Four untried geological hypotheses</h2></div>
        <p>Rank is a qualitative prior on potential DTI benefit relative to cost, not a measured effect. Absolute ΔDTI is unknown for every proposal; none is a competition-score projection.</p></div>
        <div class="table-wrap"><table><thead><tr><th>Rank / qualitative DTI upside</th><th>Specific layers</th><th>Physical signature / unmapped-fault mechanism</th><th>How it differs from reviewed code</th><th>Non-fault mimic</th><th>Cost / data status</th></tr></thead><tbody>
          <tr><td>1 · Acquisition-seam-aware magnetic lineament persistence — potentially highest relative upside; very uncertain</td><td><code>rtp</code>, <code>mag_anom</code>, optionally GeoDAWN <code>TMI_up150</code></td><td>Directional spectral anisotropy and lineament-edge persistence across scales; test whether fault-related magnetic boundaries continue across inferred acquisition/leveling seams.</td><td>Existing magnetic arms use gradients/tilt/Euler or MAGREST patch-texture restoration; this explicitly models a stripe/seam null plus cross-scale persistence.</td><td>Volcanic/lithologic contact, residual leveling seam, or real structures parallel to flight lines.</td><td>Medium. Owner-mirror band hashes are registered; production stack is not restored here and flight-line metadata is absent. Absolute ΔDTI: unknown.</td></tr>
          <tr><td>2 · Multiscale gravity–magnetic edge-transfer coherence — medium-to-high relative upside; high uncertainty</td><td><code>rtp</code>, <code>iso_grav_anom</code>, <code>iso_grav_anom_slope</code>, <code>depth_to_base_surf</code></td><td>Scale-space edge transfer: compare polarity, tangent, termination and lateral displacement across magnetic, gravity and basement-depth fields to detect buried structures under cover.</td><td>Prior reviewed combinations mainly fuse scalar strengths/unions or local textures; this tests cross-field edge displacement/termination with a lithologic-contact null.</td><td>Pluton margin or basin-fill / lithologic contact shared across fields.</td><td>Medium-high. Bands are in the hash-pinned owner manifest, but the production stack/cache is absent here. Absolute ΔDTI: unknown.</td></tr>
          <tr><td>3 · Piedmont drainage-deflection asymmetry — lower/uncertain upside; high cost</td><td>High-resolution USGS 3DEP DEM-derived channel network plus 100 m <code>det_elev</code></td><td>Blind-corridor lateral channel/tributary deflection or paired incision asymmetry after conditioning on regional slope and fan direction; could detect displacement without a preserved scarp.</td><td>Existing LiDAR modules quantify local scarps/relief; this tests network-scale drainage geometry instead.</td><td>Avulsion, fan-lobe switching, lithologic permeability boundary, irrigation or human diversion.</td><td>High and not data-ready. Exact official tiles, metadata and in-footprint coverage were not fetched/checked under this runtime's host allowlist. Do not call viable until hashed. Absolute ΔDTI: unknown.</td></tr>
          <tr><td>4 · Radiometric channel edge displacement — low-to-medium relative upside; uncertain</td><td>GeoDAWN <code>K</code>, <code>Th</code>, <code>U</code>, <code>TC</code> plus <code>rtp</code></td><td>Repeatable, signed but laterally displaced K/Th/U transition edges across channels/scales; potential compositional expression of concealed structure rather than ratio extrema.</td><td>Earlier radiometric work uses contrast/rank features; this tests channel-wise edge geometry and offset consistency.</td><td>Alluvial provenance, weathering, volcanic-unit margin or acquisition seam.</td><td>Medium. Registered owner-mirror bands are quantized/coverage-limited and production files are not restored. Absolute ΔDTI: unknown.</td></tr>
        </tbody></table></div>
        <p class="small">These are repo-local hypotheses not identified as implemented in the source/evidence reviewed; that is not a claim of global scientific novelty. Resolve the missing assigned-method paragraph, literal full-support duplicate STOP, exhausted experiment budget, and data authorization before choosing any. See the <a href="https://github.com/buffedlizard55-lab/GEMSDOE31/blob/main/knowledge/repo_review_2026-10-26_continuation.md">ranked desk-review record</a>.</p>
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
          <li>Resolve the literal overlap STOP through an explicit protocol-owner decision about the inherited positive-support definition. The r13 lattice's 3-px halo covers 99.8713% of the footprint and overlaps the frozen candidates above threshold; separately, the continuous GEMSDOE48 field is full-support under finite-value &gt; 0 semantics. Do not misattribute the witnesses or add a private exemption.</li><li>Resolve magnetic-texture specificity. Synthetic checks show that undisplaced anisotropic fabric can also trigger a max-over-orientations detector. Do not label its response as measured fault slip.</li>
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
          These are source references only; no official or external non-GitHub page was freshly fetched in this review.</p>
          <p><a href="downloads/magrest-run-card.json">Complete JSON run card</a> ·
          <a href="https://github.com/buffedlizard55-lab/GEMSDOE31/tree/main/evidence/magrest">All measurements</a>.</p>
      </section>{scgp_download_and_gates()}{parallel_archives()}'''
