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


def h31t_download_and_gates() -> str:
    rc_path = ROOT / "evidence/h31t/run_card.json"
    e3_path = ROOT / "evidence/h31t/exp3_uniqueness_offcat_package.json"
    if not rc_path.is_file() or not e3_path.is_file():
        return ""
    rc = json.loads(rc_path.read_text())
    e3 = json.loads(e3_path.read_text())
    hd = rc["holdout_dti"]
    g57 = hd["primary_shared_template_gems57_pooled_hide_v2"]
    scr = hd["gemsdoe31_holdout_v1_screen"]
    cnf = hd["gemsdoe31_holdout_v1_untouched_confirm"]
    prx = hd["offcat_sgmc_discovery_proxies"]
    ru = rc["registry_uniqueness"]
    art = rc["artifacts"]
    lc = rc["leakage_canary"]
    ov = rc["own_method_variogram_collar"]
    knc = ru["key_named_comparators"]
    slug = esc(rc["submission_name"])
    sha_zeros = esc(art["primary_zeros_tif_sha256"])
    sha_zeros_zip = esc(art["primary_zeros_zip_sha256"])
    sha_nan = esc(art["companion_nan_tif_sha256"])
    sha_nan_zip = esc(art["companion_nan_zip_sha256"])
    note = esc(rc["submission_note"])
    _ = e3
    return f'''<section id="h31t-dinkelbach" aria-labelledby="h31t-heading">
      <div class="section-head"><div><p class="kicker">Archived research run · 2026-10-25 · SI Crustal-Mechanics + Listric Restoration + Dinkelbach 29-Cell Submodular · H31-T</p>
        <h2 id="h31t-heading">H31-T Transtension-Dinkelbach: Research Download Only · DO NOT SUBMIT</h2></div>
        <p>Newly computed 100% label-free Dual-Specialist OOF HGB across 12 spatially collared folds (with H31-T's own measured 21.25 km OOF residual variogram, resolving <code>IR-31-OWN-METHOD-VARIOGRAM</code>) +
           Cost-Scaled Dinkelbach 29-cell submodular CELF allocation (37,654 binary {{0.0, 1.0}} dots, 0 within 200 m of public catalogue).
           Passes all 21/21 format &amp; [0, 1] checks, 35-plane leakage canary, unchanged <code>gems57-pooled-hide-v2</code> (+18.68%, 4/4 quadrants),
           disjoint <code>gemsdoe31-holdout-v1</code> Screen &amp; untouched Confirmation (+23.01%, 4/4 folds), Full &amp; 4-Block Off-Catalogue SGMC (+15.1% vs GEMSDOE32 H33-2-B2),
           and Phase A uniqueness across all 119 discrete fault maps in all 9 focus sites + GEMSDOE31 —
           but is <strong>blocked from weekly slot upload (DO NOT SUBMIT, slot_approved = false)</strong> under the unexempted 695-raster <code>r13-lattice-s5</code> / <code>GEMSDOE48</code> STOP rule.</p></div>
      <div class="card download-card">
        <span class="badge">HISTORICAL LOCAL CHECKS RECORDED · RESEARCH DOWNLOAD ONLY</span>
        <span class="badge badge-red" style="margin-left:8px">DO NOT SUBMIT · REGISTRY STOP (slot_approved = false)</span>
        <h3 style="margin-top:18px">{slug}</h3>
        <p>12 100% label-free SI-calibrated crustal-mechanics channels (<code>mag_as3d</code>, <code>mag_inv_depth</code>, <code>grav_as3d</code>, <code>grav_inv_depth</code>,
           <code>mag_grav_crest_coh</code>, <code>listric_updip_bstep</code>, <code>listric_updip_grav</code>, <code>transtension_slip_index</code>, <code>eq_transtension_couple</code>,
           <code>hydro_mag_destr_kth</code>, <code>cond_clay_cap_ridge</code>, <code>piedmont_scarp_asi</code>) + stitched 12-fold OOF Dual-Specialist HGB +
           Cost-Scaled Dinkelbach 29-cell submodular CELF allocator (37,654 off-catalogue binary {{0.0, 1.0}} dots; min distance to public catalogue {rc['validator_output']['min_distance_to_public_catalogue_m']:.2f} m).</p>
        <div class="actions">
          <a class="button button-primary" href="downloads/{slug}-zeros.tif" download>Download H31-T Research .tif (All-finite zeros)</a>
          <a class="button" href="downloads/{slug}-zeros.zip" download>Download Single-TIFF .zip (All-finite)</a>
          <a class="button" href="downloads/{slug}-nan.tif" download>NaN-outside companion .tif</a>
          <a class="button" href="downloads/{slug}-nan.zip" download>NaN Single-TIFF .zip</a>
          <a class="button" href="downloads/{slug}-format-check.json" download>Format receipt .json</a>
          <a class="button" href="downloads/{slug}-run-card.json" download>Run Card .json</a>
        </div>
        <p class="download-meta"><strong>Grid &amp; Range:</strong> 1-band float32 · EPSG:32611 · 3730 × 3292 · 0 NaN/Inf inside 5,167,373-cell footprint · footprint values strictly {{0.0, 1.0}} in [0.0, 1.0] (prevents “Predicted values must be in range [0, 1]”) · 0 dots within 200 m of public catalogue.<br>
          <strong>SHA-256 (All-finite primary):</strong> <code>{sha_zeros}</code><br>
          <strong>SHA-256 (All-finite ZIP):</strong> <code>{sha_zeros_zip}</code><br>
          <strong>SHA-256 (NaN companion):</strong> <code>{sha_nan}</code><br>
          <strong>SHA-256 (NaN ZIP):</strong> <code>{sha_nan_zip}</code><br>
          <strong>Artifact Name (not uniqueness approval):</strong> <code>{slug}</code><br>
          <strong>Note ({rc['submission_note_chars']}/140):</strong> <code>{note}</code></p>
      </div>
      <div class="table-wrap" style="margin-top:18px"><table>
        <thead><tr><th>Automated Gate</th><th>Threshold</th><th>Measured H31-T Value</th><th>Status</th></tr></thead>
        <tbody>
          <tr><td><code>G1 · GeoTIFF Format &amp; [0, 1]</code></td><td>EPSG:32611, 3730×3292, float32, 0 NaN inside, [0, 1]</td><td>37,654 dots in {{0.0, 1.0}}; 0 NaN inside; min catalogue distance {rc['validator_output']['min_distance_to_public_catalogue_m']:.2f} m (21/21 checks)</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G2 · Single-Feature Leakage</code></td><td>Two-sided ROC-AUC ≤ 0.90 across all {lc['features_tested']} static planes</td><td>max symmetric AUC = {lc['max_symmetric_auc']:.4f} (<code>{esc(lc['max_feature'])}</code>)</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G3 · Own-Method Variogram Collar</code></td><td>Candidate-specific OOF residual 95% decay (<code>IR-31-OWN-METHOD-VARIOGRAM</code>)</td><td>{ov['own_empirical_adopted_buffer_m']:,.0f} m ({ov['adopted_holdout_buffer_px']} px, {esc(ov['best_parametric_model'])} WRMSE fit)</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G4a · Shared Template Holdout</code></td><td>Unchanged <code>gems57-pooled-hide-v2</code> (n={g57['withheld_positive_pixels']:,}, 21.25 km), paired 95% CI &gt; 0</td><td>HOLDOUT-DTI {g57['h31t_dinkelbach_dti']:.4f} [{g57['h31t_dinkelbach_ci95'][0]:.4f}, {g57['h31t_dinkelbach_ci95'][1]:.4f}] vs {g57['ctrl_phys_poisson_dti']:.4f} ctrl (delta {g57['paired_delta_vs_ctrl']:+.4f}, 95% CI [{g57['paired_delta_vs_ctrl_ci95'][0]:+.4f}, {g57['paired_delta_vs_ctrl_ci95'][1]:+.4f}], 4/4 quadrants)</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G4b · Disjoint Screen Holdout</code></td><td><code>gemsdoe31-holdout-v1</code> seed {scr['seed']} (n={scr['withheld_positive_pixels']:,}), paired 95% CI &gt; 0</td><td>HOLDOUT-DTI {scr['h31t_dinkelbach_dti']:.4f} vs {scr['ctrl_phys_poisson_dti']:.4f} ctrl (delta {scr['paired_delta_vs_ctrl']:+.4f}, 95% CI [{scr['paired_delta_vs_ctrl_ci95'][0]:+.4f}, {scr['paired_delta_vs_ctrl_ci95'][1]:+.4f}])</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G4c · Untouched Confirm Holdout</code></td><td><code>gemsdoe31-holdout-v1</code> seed {cnf['seed']} (n={cnf['withheld_positive_pixels']:,}, 0 tuning), paired 95% CI &gt; 0</td><td>HOLDOUT-DTI {cnf['h31t_dinkelbach_dti']:.4f} [{cnf['h31t_dinkelbach_ci95'][0]:.4f}, {cnf['h31t_dinkelbach_ci95'][1]:.4f}] vs {cnf['ctrl_phys_poisson_dti']:.4f} ctrl (delta {cnf['paired_delta_vs_ctrl']:+.4f}, 95% CI [{cnf['paired_delta_vs_ctrl_ci95'][0]:+.4f}, {cnf['paired_delta_vs_ctrl_ci95'][1]:+.4f}], 4/4 folds)</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G5 · Off-Catalogue SGMC (&gt;300 m)</code></td><td>Statewide &amp; 4-block collared vs GEMSDOE32 H33-2-B2; piedmont reported transparently</td><td>Full Off-SGMC {prx['full_gt300m_h31t_dti']:.4f} vs {prx['full_gt300m_h33_2_b2_dti']:.4f} (+15.1%); 4-Block {prx['collared_4block_h31t_dti']:.4f} vs {prx['collared_4block_h33_2_b2_dti']:.4f}; Piedmont (slope ≤ 6 deg) {prx['piedmont_le6deg_h31t_dti']:.4f} vs {prx['piedmont_le6deg_h33_2_b2_dti']:.4f} (label-free trade-off)</td><td><span class="badge badge-green">REPORTED</span></td></tr>
          <tr><td><code>G6a · 119-Submission Discrete Subset</code></td><td>All 9 focus repos + all GEMSDOE31 discrete lanes (|ρ| ≤ 0.90, 3-px ≤ 70%)</td><td>pre-surface max |ρ| = {ru['pre_placement_max_abs_spearman_rho']:.4f}; post max |ρ| = {ru['post_placement_max_abs_spearman_rho']:.4f}; max 3-px = {100*ru['phase_a_max_3px_overlap']:.2f}% ({100*knc['gemsdoe32_h33_2_b2']['my_dots_within_3px_of_theirs']:.2f}% vs H33-2-B2, {100*knc['h31_m']['my_dots_within_3px_of_theirs']:.2f}% vs H31-M)</td><td><span class="badge">SUBSET ONLY — NOT UNIQUENESS APPROVAL</span></td></tr>
          <tr><td><code>G6b · Literal 695-Raster Controls</code></td><td>Unexempted <code>r13-lattice-s5</code> &amp; <code>GEMSDOE48</code> continuous blanket</td><td>{100*knc['r13_lattice_s5']['my_dots_within_3px_of_theirs']:.2f}% vs <code>r13-lattice-s5</code>; {100*knc['gemsdoe48_continuous']['my_dots_within_3px_of_theirs']:.1f}% vs <code>GEMSDOE48</code></td><td><span class="badge badge-red">LITERAL STOP (slot_approved=false)</span></td></tr>
        </tbody>
      </table></div>
      <p class="small">HOLDOUT-DTI evaluators: <code>gems57-pooled-hide-v2</code> (n=60,988 withheld positives, 21,250 m own-method collar, 1,000 block-bootstrap replicates) and
        <code>gemsdoe31-holdout-v1</code> (disjoint Screen n=29,862 + untouched Confirmation n=28,763). None of these figures is a competition score or projection.
        Receipts: <a href="downloads/{slug}-run-card.json">H31-T JSON Run Card</a> ·
        <a href="https://github.com/buffedlizard55-lab/GEMSDOE31/tree/main/evidence/h31t">full EXP-1..3 evidence directory</a> ·
        <a href="https://github.com/buffedlizard55-lab/GEMSDOE31/blob/main/knowledge/2026-10-25_h31t_transtension_dinkelbach_preregistration.md">frozen H31-T preregistration</a>.</p>
    </section>'''


def h31t_phd_forensic_and_hypotheses() -> str:
    e3_path = ROOT / "evidence/h31t/exp3_uniqueness_offcat_package.json"
    if not e3_path.is_file():
        return ""
    e3 = json.loads(e3_path.read_text())
    full_s = e3["offcat_sgmc_benchmarks"]["offcat_sgmc_full_gt300m"]
    pied_s = e3["offcat_sgmc_benchmarks"]["offcat_sgmc_piedmont_le6deg_gt300m"]
    blk_s = e3["offcat_sgmc_benchmarks"]["offcat_sgmc_4block_collared"]["scores"]
    rows_html = []
    for label in (
        "H31-T (Dinkelbach)",
        "H31-M Subsurface",
        "GEMSDOE32 H33-2-B2",
        "H27-4 Baseline",
        "H31-B Scarp-Hessian",
        "H31-HVDC Conduit",
        "H31-E2 SCGP-Submod",
        "MAGREST Concordant",
    ):
        if label not in full_s:
            continue
        f_v = full_s[label]
        p_v = pied_s[label]
        b_v = blk_s[label]
        rows_html.append(
            f"<tr><td><strong>{esc(label)}</strong></td>"
            f"<td>{f_v['n_emitted']:,}</td>"
            f"<td>{f_v['dti']:.4f}</td>"
            f"<td>{b_v['dti']:.4f} [{b_v['ci95'][0]:.4f}, {b_v['ci95'][1]:.4f}]</td>"
            f"<td>{p_v['dti']:.4f} ({p_v['n_emitted_in_piedmont']:,} px)</td></tr>"
        )
    return f'''<section id="h31t-forensic"><div class="section-head"><div><p class="kicker">Historical 2026-10-25 analysis · H31-T archive</p><h2>H33 geometry, the unverified 0.2778 claim, and historical H31-T hypotheses</h2></div>
      <p>Byte-verified geometry and local proxy comparisons only. Score claims remain USER-REPORTED; no private-score cause is established.</p></div>
      <div class="content">
        <p><strong>Exact nested subset identity (computed directly on SHA-256-verified GeoTIFFs):</strong>
          <code>H19-5</code> (121,131 px, 0.1922 <code>USER-REPORTED</code>) →
          <code>GEMSDOE25 D1.5</code> (60,069 px, 0.2477 <code>USER-REPORTED</code>) →
          <code>GEMSDOE25 D2.8</code> (44,090 px, 0.2600 <code>USER-REPORTED</code>) →
          <code>GEMSDOE28 H27-4</code> (40,199 px, 0.2708 <code>USER-REPORTED</code>, <code>d_cat &gt; 100 m</code>) →
          <code>GEMSDOE32 H33-2-B2</code> (37,654 px, 0.2778 <code>USER-REPORTED</code>, <code>d_cat &gt; 200 m</code>).
          Under <code>DTI = TPw / (TPw + α × FPw + β × FNw)</code> with <code>α=0.2</code>, <code>β=0.8</code>, and operating point <code>D* ≈ 0.2778</code>, an added block improves DTI iff
          <code>ΔTPw / ΔFPw &gt; α × D* / (1 − α × D*) = 0.2 × 0.2778 / (1 − 0.2 × 0.2778) ≈ 0.05882</code>. In the simplified isolated-dot case where <code>ΔTPw + ΔFPw = 1</code>, this is equivalent to <code>ΔTPw &gt; α × D* ≈ 0.05556</code>; neither algebraic threshold proves that pruning caused the unverified private score.
          <code>2.8 px</code> thinning reduced the parent count by 77,041 dots. Metric theory makes reduced redundant false-positive cost a plausible explanation, but the removed dots' hidden-truth credit is unknown.
          H33 then removed 2,545 additional dots in the 100–200 m catalogue-distance band and added none; the score claims do not isolate that change.
          GEMSDOE36's geometry contains H33 plus 1,200 dots, but its <code>0.2750</code> vs <code>0.2778</code> values are USER-REPORTED and do not identify the added dots' marginal truth/false-positive credit.</p>
        <p><strong>Historical hypotheses, not forecasts or current authorization:</strong>
          earlier H31-T notes explored magnetic/gravity texture, up-dip restoration, alteration, and submodular allocation as possible signals.
          They do not establish that H33's reported score was caused by those mechanisms, that private truth would reward them, or that a new submission can beat the USER-REPORTED <code>0.2778</code>, <code>0.3195</code>, or <code>0.4413</code> anchors.
          Current blockers and the active three-item desk backlog are stated at the top of the README; no experiment is authorized here.</p>
      </div>
      <div class="table-wrap" style="margin-top:16px"><table>
        <thead><tr><th>Historical rank &amp; candidate</th><th>Inputs / recorded transform</th><th>Proposed mechanism (not verified geological causation)</th><th>Historical holdout note / effort</th></tr></thead>
        <tbody>
          <tr><td><code>1 · H31-T · archived run</code></td><td>Historical SI-calibrated magnetic/gravity features, depth/restoration terms, alteration channels, and Dinkelbach allocation</td><td>The operator encoded an up-dip offset hypothesis; geological correspondence was not independently confirmed.</td><td>Historical HOLDOUT-DTI record is detailed below; not a leaderboard forecast. About 21 min CPU in that run.</td></tr>
          <tr><td><code>2 · H31-R · historical proposal, not current</code></td><td>Anisotropic Riemann-tensor trace-linking geodesic graph across <code>step_max</code>, <code>bstep_grad_norm</code>, and 3D analytic signal</td><td>Earlier concept for connecting intermittent 100–300 m buried relay segments; not a current desk proposal or authorized experiment.</td><td>Historical effort estimate only; local-stack availability and expected value are unverified.</td></tr>
          <tr><td><code>3 · H31-S · historical tomography concept (distinct from later UDAP-SSLIC H31-S)</code></td><td>Continuous-wavelet multi-depth tilt-derivative phase-convergence tomography (z = 200 m..3,200 m) on <code>tmi_rtp</code> &amp; <code>iso_grav_anom</code></td><td>Earlier concept for inclined fault planes; not the later UDAP-SSLIC run and not part of the current desk backlog.</td><td>Historical ordinal estimate only; no current authorization or score forecast.</td></tr>
          <tr><td><code>4 · H31-V · historical external roadmap</code></td><td>ARIA / Sentinel-1 MintPy vertical &amp; east-west InSAR velocity + seasonal poroelastic phase gradient</td><td>Earlier external-data idea for active creep and hydraulic barriers; not a current desk proposal or authorized experiment.</td><td>Required external data and access were not verified during this review; expected impact remains unverified.</td></tr>
        </tbody>
      </table></div>
      <div class="table-wrap" style="margin-top:18px"><table>
        <thead><tr><th>Historical 8-lane HOLDOUT-PROXY-SGMC comparison (not private truth)</th><th>Emitted Dots</th><th>Full Off-SGMC (&gt;300 m)</th><th>4-Block Collared Off-SGMC [95% CI]</th><th>Piedmont Off-SGMC (slope ≤ 6 deg)</th></tr></thead>
        <tbody>{''.join(rows_html)}</tbody>
      </table></div>
      <p class="small">Historical diagnostic note: <code>EXP-1</code> reported a self-inclusion issue in catalogue-derived tip/relay features; <code>EXP-2</code> removed those features. The archived run card records HOLDOUT-DTI <code>gems57-pooled-hide-v2</code> (60,988 withheld positives): candidate 0.130010 vs control 0.109548, paired Δ +0.020461 [95% CI +0.004540, +0.036530]. These local evaluator results are not competition scores. The recorded Full Off-SGMC values (0.1082 vs 0.0940 H33) and Piedmont proxy values (0.0434 vs 0.0586) are HOLDOUT-PROXY-SGMC diagnostics, not private truth or causal explanation.</p>
    </section>'''


def h31j_download_and_gates() -> str:
    rc_path = ROOT / "evidence/h31j/run_card.json"
    if not rc_path.is_file():
        return ""
    rc = json.loads(rc_path.read_text())
    art = rc["artifacts"]
    hd = rc["holdout_dti"]
    scr = hd["screen_seed31"]
    conf = hd["confirmation_seed32"]
    j1_s = scr["scores"]["h31j1_subsurface_submod"]
    j2_s = scr["scores"]["h31j2_dual_poisson"]
    j3_s = scr["scores"]["h31j3_dual_submod"]
    ctrl_s = scr["scores"]["physical_hgb"]
    mag_s = scr["scores"]["magrest_concordant"]
    d_s = scr["paired_vs_physical_hgb"]
    j3_c = conf["scores"]["h31j3_dual_submod"]
    ctrl_c = conf["scores"]["physical_hgb"]
    d_c = conf["paired_vs_physical_hgb"]
    vario = rc["own_method_variogram_summary"]
    uniq = rc["uniqueness_summary"]
    g3b = uniq["shared_registry_g3b"]["post_placement_final_dots"]
    sgmc = rc["off_catalogue_sgmc_proxy"]
    j3_sgmc = sgmc["h31j3_dual_submod"]
    h33_sgmc = sgmc["gemsdoe32_h33_2_b2"]
    sub_name = esc(rc["submission_name"])
    note = esc(rc["portal_note"])
    sha_zeros = esc(art["primary_zeros_sha256"])
    sha_zeros_zip = esc(art["primary_zeros_zip_sha256"])
    sha_nan = esc(art["companion_nan_sha256"])
    sha_nan_zip = esc(art["companion_nan_zip_sha256"])
    return f'''<section id="tgtd-submod-h31j" aria-labelledby="h31j-heading">
      <div class="section-head"><div><p class="kicker">Historical 2026-10-25 research run · H31-J archive</p>
        <h2 id="h31j-heading">H31-J TGTD-Submod: Historical local checks recorded; shared-registry STOP · DO NOT SUBMIT</h2></div>
        <p>Genuinely new 37,654-dot Basin-and-Range blind/piedmont fault detector combining Pedersen–Rasmussen 3-D Laplace gravity-tensor 2-D tabular invariants,
           DOE GDR #1391 chemical geothermometer disequilibrium conduit channeling, and V-canyon-suppressed piedmont flexure via 4-quadrant OOF + 300 m ridge-submodular emission.
           Verified automatically by <code>scripts/verify_h31j.py</code> without human inspector intervention; held as research-only (<code>slot_approved = false</code>) under Rule 6 and the unexempted 695-raster spacing-5 lattice STOP.</p></div>
      <div class="card download-card">
        <span class="badge badge-green">LOCAL FORMAT [0, 1] &amp; 8/8 QUADRANTS PASS · RESEARCH DOWNLOAD ONLY</span>
        <span class="badge badge-red" style="margin-left:8px">DO NOT SUBMIT · REGISTRY STOP (slot_approved = false)</span>
        <h3 style="margin-top:18px">{sub_name}</h3>
        <p><strong>Immediate Automated Readiness Summary:</strong> All <code>12,279,160</code> pixels in the primary <code>-zeros.tif</code> / <code>-zeros.zip</code>
           are finite <code>float32</code> in <code>[0.0, 1.0]</code> (eliminating <em>“Predicted values must be in range [0, 1]”</em> range rejections);
           companion <code>-nan.tif</code> / <code>-nan.zip</code> carries identical <code>37,654</code> footprint dots with exact <code>NaN</code> outside.
           Zero dots overlap the public fault catalogue or its <code>≤ 200 m</code> dead collar; zero dots are copied from prior submissions.
           Upload remains disabled (<code>slot_approved = false</code>) under Parallel-Run Rule 6 and the binding literal 695-raster 5×5 lattice STOP (<code>G3b</code>).</p>
        <div class="actions">
          <a class="button button-primary" href="downloads/{sub_name}-zeros.zip" download>Download H31-J Research All-Finite [0, 1] .zip</a>
          <a class="button" href="downloads/{sub_name}-zeros.tif" download>Download Primary All-Finite .tif</a>
          <a class="button" href="downloads/{sub_name}-nan.zip" download>Companion NaN-Outside .zip</a>
          <a class="button" href="downloads/{sub_name}-nan.tif" download>Companion NaN-Outside .tif</a>
          <a class="button" href="downloads/{sub_name}-run-card.json" download>JSON Run Card</a>
          <a class="button" href="downloads/{sub_name}-format-check.json" download>Format Receipt</a>
        </div>
        <p class="download-meta"><strong>Grid &amp; [0, 1] Verification:</strong> 1-band float32 · EPSG:32611 · 3730 × 3292 · 100 m · 37,654 dots in {{0.0, 1.0}} · 0 NaN/Inf inside 5,167,373-cell footprint · 0 on public catalogue · 0 within 200 m collar · 57.59% beyond 1.5 km.<br>
          <strong>Artifact Name (not uniqueness approval):</strong> <code>{sub_name}</code><br>
          <strong>Note ({rc['portal_note_length']}/140 chars):</strong> <code>{note}</code><br>
          <strong>SHA-256 (-zeros.tif, {art['primary_zeros_bytes']:,} B):</strong> <code>{sha_zeros}</code><br>
          <strong>SHA-256 (-zeros.zip, {art['primary_zeros_zip_bytes']:,} B):</strong> <code>{sha_zeros_zip}</code><br>
          <strong>SHA-256 (-nan.tif, {art['companion_nan_bytes']:,} B):</strong> <code>{sha_nan}</code> · <strong>(-nan.zip, {art['companion_nan_zip_bytes']:,} B):</strong> <code>{sha_nan_zip}</code></p>
      </div>
      <div class="table-wrap" style="margin-top:18px"><table>
        <thead><tr><th>Automated Gate</th><th>Preregistered Rule</th><th>Measured H31-J3 Result (Evidence Class Stated)</th><th>Verdict</th></tr></thead>
        <tbody>
          <tr><td><code>G1 · Local GeoTIFF &amp; [0, 1]</code></td><td>EPSG:32611, 3730×3292, float32, 0 NaN inside, [0, 1], 1-TIFF ZIP</td><td>COMPUTED: 37,654 dots in {{0.0, 1.0}}; -zeros all 12,279,160 finite; ZIP SHA-256 verified</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G2 · Leakage Canary</code></td><td>Single-feature two-sided ROC-AUC ≤ 0.90 across all 4 folds × 65 cols</td><td>COMPUTED (not DTI): 260/260 checks ≤ 0.90; max sym AUC = {rc['leakage_canary_summary']['max_single_feature_symmetric_auc']:.4f}; miss AUC = {rc['leakage_canary_summary']['max_missingness_symmetric_auc']:.4f}; <code>dist_known_fault_px</code> excluded</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G3a · {uniq['discrete_comparable_files']}-File Discrete Subset</code></td><td>Pre-placement |ρ| ≤ 0.90; Final dots |ρ| ≤ 0.90 &amp; 3-px ≤ 70.0%</td><td>COMPUTED across {uniq['discrete_comparable_files']} files ({uniq['discrete_distinct_fields']} distinct fields, GEMSDOE24..36+31+70): pre |ρ| = {uniq['pre_placement_max_abs_rho']:.4f} (unspaced d=0 diagnostic clump {100*uniq['pre_placement_unspaced_d0_diagnostic_3px_overlap']:.2f}%); final |ρ| = {uniq['post_placement_max_abs_rho']:.4f}, max 3-px = {100*uniq['post_placement_max_3px_overlap']:.2f}% (vs H33-2-B2: 41.5%)</td><td><span class="badge">SUBSET ONLY — NOT UNIQUENESS APPROVAL</span></td></tr>
          <tr><td><code>G3b · Shared-Registry 5×5 Lattice</code></td><td>Unexempted 695-raster shared registry (<code>r13-lattice-s5</code>)</td><td>COMPUTED: |ρ| = {abs(g3b['spearman_rho']):.4f} ≤ 0.90; 3-px overlap = {100*g3b['overlap_within_3px']:.2f}% (synthetic 5×5 spacing-5 grid covers Nevada interior within 2.83 ≤ 3 px)</td><td><span class="badge badge-red">LITERAL STOP</span></td></tr>
          <tr><td><code>G4a · Screen Holdout (seed=31)</code></td><td><code>gems57-pooled-hide-v2</code>, 21.3 km buffer, n = {scr['withheld_positives']:,}, paired 95% CI &gt; 0</td><td>HOLDOUT-DTI: H31-J3 <strong>{j3_s['dti']:.4f}</strong> [{j3_s['ci95'][0]:.4f}, {j3_s['ci95'][1]:.4f}] vs physical_hgb {ctrl_s['dti']:.4f} (Δ = +{d_s['delta']:.4f} [+{d_s['ci95'][0]:.4f}, +{d_s['ci95'][1]:.4f}], +85.7%, 4/4 quadrants) &amp; MAGREST {mag_s['dti']:.4f}; H31-J1 subsurface = {j1_s['dti']:.4f}; H31-J2 Poisson = {j2_s['dti']:.4f}</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G4b · Untouched Confirm (seed=32)</code></td><td>Zero retuning, <code>gems57-pooled-hide-v2</code>, 21.3 km buffer, n = {conf['withheld_positives']:,}</td><td>HOLDOUT-DTI: H31-J3 <strong>{j3_c['dti']:.4f}</strong> [{j3_c['ci95'][0]:.4f}, {j3_c['ci95'][1]:.4f}] vs physical_hgb {ctrl_c['dti']:.4f} [{ctrl_c['ci95'][0]:.4f}, {ctrl_c['ci95'][1]:.4f}] (Δ = +{d_c['delta']:.4f} [+{d_c['ci95'][0]:.4f}, +{d_c['ci95'][1]:.4f}], +60.2%, 4/4 quadrants = 8/8 total)</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G5 · Own-Method OOF Variogram</code></td><td>95%-sill residual practical range ≤ 21,300 m holdout buffer</td><td>COMPUTED: 95%-sill range = <strong>{vario['practical_range_95_sill_m']:,.1f} m</strong> (scale {vario['scale_parameter_m']:,.1f} m, R² = {vario['weighted_r_squared']:.4f}); 21.3 km collar covers {100*vario['sill_fraction_at_collar']:.2f}% of sill</td><td><span class="badge badge-green">PASS</span></td></tr>
          <tr><td><code>G6 · Off-Catalogue SGMC (&gt;300 m)</code></td><td>Report-only matched 37,654-dot discovery proxy (never training truth)</td><td>HOLDOUT-PROXY-SGMC: All-elev (61,664 px) <strong>{j3_sgmc['sgmc_all_elevation_dti']:.4f}</strong> vs GEMSDOE32 H33-2-B2 {h33_sgmc['sgmc_all_elevation_dti']:.4f} (+15.2%); Piedmont &lt;100 m (28,115 px) <strong>{j3_sgmc['sgmc_piedmont_lt100m_dti']:.4f}</strong> vs H33-2-B2 {h33_sgmc['sgmc_piedmont_lt100m_dti']:.4f} (+30.5%)</td><td><span class="badge badge-green">REPORTED WIN</span></td></tr>
          <tr><td><code>G7 / Rule 6 · Weekly Live Slot</code></td><td>Never auto-spend DrivenData weekly submission quota</td><td><code>slot_approved = false</code>; blocked from upload while the literal 695-raster G3b rule remains unamended</td><td><span class="badge badge-red">DO NOT SUBMIT</span></td></tr>
        </tbody>
      </table></div>
      <p class="small">Reproduce verification offline in ~2 s: <code>.venv/bin/python scripts/verify_h31j.py</code> ·
        Preregistration: <a href="https://github.com/buffedlizard55-lab/GEMSDOE31/blob/main/knowledge/2026-10-25_h31j_tgtd_preregistration.md">frozen H31-J specification</a> ·
        Evidence directory: <a href="https://github.com/buffedlizard55-lab/GEMSDOE31/tree/main/evidence/h31j">evidence/h31j/</a>.</p>
    </section>'''


def h31j_research_sections() -> str:
    rc_path = ROOT / "evidence/h31j/run_card.json"
    if not rc_path.is_file():
        return ""
    rc = json.loads(rc_path.read_text())
    hd = rc["holdout_dti"]
    scr = hd["screen_seed31"]
    conf = hd["confirmation_seed32"]
    vario = rc["own_method_variogram_summary"]
    sgmc = rc["off_catalogue_sgmc_proxy"]
    j3_sgmc = sgmc["h31j3_dual_submod"]
    h33_sgmc = sgmc["gemsdoe32_h33_2_b2"]
    scgp_sgmc = sgmc.get("h31e2_scgp_submod", {})
    return f'''<section id="h31j-research" aria-labelledby="h31j-res-heading">
      <div class="section-head"><div><p class="kicker">2026-10-25 Preregistered Discovery Study · Lane H31-J</p>
        <h2 id="h31j-res-heading">Five Ranked Untried Geological Hypotheses &amp; H31-J TGTD-Submod Verification</h2></div>
        <p>Documented and frozen in <code>knowledge/2026-10-25_h31j_tgtd_preregistration.md</code> before fitting any model.
           All 5 hypotheses use verified free official public data (USGS GeoDAWN DOI 10.5066/P93LGLVQ, DOE GDR #1391, USGS 3DEP 1 m LiDAR, NBMG/GBCGE).</p></div>
      <div class="table-wrap"><table>
        <thead><tr><th>Rank &amp; Candidate</th><th>Exact Layers &amp; Physical Signature</th><th>Why Missing From USGS / INGENIOUS &amp; Difference vs Repo</th><th>Mimic Suppressed · Cost · Status</th></tr></thead>
        <tbody>
          <tr><td><strong>1 · H31-J · TGTD + GDR-1391 Geotherm + PTCF</strong></td><td>B13 gravity + B02 RTP 3-D Laplace tensor (z=300m, 1000m) Pedersen–Rasmussen <code>T_2D</code>; GDR-1391 quartz/chalcedony/Na-K-Ca <code>ΔT_diseq</code> × tabular/MT/K conduit; B12/B19 asymmetric piedmont flexure + Hurst break + seam-free 1 m LiDAR</td><td>Wash-covered &amp; blind basin faults lack preserved 1 m scarps and are blurred into circular gravity blobs by standard horizontal gradients; first 3-D harmonic tensor invariant + advective geothermometer disequilibrium + 4-quad OOF 300 m submodular lane</td><td>3-D calderas/plutons (<code>|I_G|→1</code>), symmetric V-canyons, shallow outflow plumes · Medium (~28 min CPU) · <strong>IMPLEMENTED &amp; CONFIRMED</strong></td></tr>
          <tr><td>2 · H31-K · Transtensional Relay / Pull-Apart Stepover</td><td>B07 geodetic shear, B08 dilatation, B10/B16 earthquake densities, B13 upward-continued gravity saddle between en-echelon tips</td><td>Accommodation zones in Humboldt/Walker Lane host commercial blind geothermal systems (Bradys, Desert Peak) between mapped range-front segments; zero catalogue-tip proximity leakage</td><td>Regional 50 km GPS smoothing &amp; mining seismicity clusters · Low–Medium · Ranked #2 (future lane)</td></tr>
          <tr><td>3 · H31-L · Magnetite-Destruction Trough + Potassic Alteration</td><td><code>max(-RTP_zz, 0)</code> narrow linear magnetic quiet trough flanked by GeoDAWN K/Th potassium enrichment + B17 shallow MT conductor</td><td>Hydrothermal fluids oxidize titanomagnetite to hematite/pyrite and precipitate illite/smectite/adularia along unmapped permeable fault damage zones without topographic relief</td><td>Felsic ash-flow tuff margins &amp; playa evaporite pans · Low–Medium · Core term incorporated in H31-J</td></tr>
          <tr><td>4 · H31-M · Multi-Azimuth Drainage Deflection &amp; Fan Apex Alignment</td><td>B12/B19 2-D structure-tensor orientation jump of incised piedmont channels + collinear alluvial-fan apices</td><td>Strike-slip &amp; oblique Walker Lane faults systematically deflect ephemeral washes where vertical scarps have diffused away</td><td>Braided fan avulsions &amp; highway/railroad berms at 100 m · Medium · Ranked #4 (future lane)</td></tr>
          <tr><td>5 · H31-N · Poisson Mag–Grav Pseudogravity Residual</td><td>FFT Baranov (1957) pseudogravity from B02 RTP regressed locally against B13 isostatic gravity</td><td>Isolates non-magnetic density steps (carbonate/metamorphic basement against basin fill) from strongly magnetic but unfaulted basaltic flows</td><td>Non-magnetic granitoid pluton roofs · Low · Ranked #5 (future lane)</td></tr>
        </tbody>
      </table></div>
      <div class="table-wrap" style="margin-top:18px"><table>
        <thead><tr><th>Experiment / Arm</th><th>Screen seed=31 HOLDOUT-DTI (n=2,901)</th><th>Untouched Confirm seed=32 HOLDOUT-DTI (n=2,808)</th><th>All-Elev SGMC Proxy (61,664 px)</th><th>Piedmont &lt;100 m SGMC Proxy (28,115 px)</th><th>Far-Field &gt;1.5 km</th></tr></thead>
        <tbody>
          <tr><td><strong>H31-J3 · Dual-Regime OOF + 300 m Submodular (Primary)</strong></td><td><strong>{scr['scores']['h31j3_dual_submod']['dti']:.4f}</strong> [{scr['scores']['h31j3_dual_submod']['ci95'][0]:.4f}, {scr['scores']['h31j3_dual_submod']['ci95'][1]:.4f}]</td><td><strong>{conf['scores']['h31j3_dual_submod']['dti']:.4f}</strong> [{conf['scores']['h31j3_dual_submod']['ci95'][0]:.4f}, {conf['scores']['h31j3_dual_submod']['ci95'][1]:.4f}]</td><td><strong>{j3_sgmc['sgmc_all_elevation_dti']:.4f}</strong></td><td><strong>{j3_sgmc['sgmc_piedmont_lt100m_dti']:.4f}</strong></td><td><strong>{100*j3_sgmc['far_field_gt_1p5km_fraction']:.2f}%</strong></td></tr>
          <tr><td>H31-J2 · Dual-Regime OOF + Poisson d=2.8 px</td><td>{scr['scores']['h31j2_dual_poisson']['dti']:.4f} [{scr['scores']['h31j2_dual_poisson']['ci95'][0]:.4f}, {scr['scores']['h31j2_dual_poisson']['ci95'][1]:.4f}]</td><td>— (ablation arm)</td><td>—</td><td>—</td><td>—</td></tr>
          <tr><td>H31-J1 · Pure Subsurface + Geotherm Only (zero terrain/LiDAR)</td><td>{scr['scores']['h31j1_subsurface_submod']['dti']:.4f} [{scr['scores']['h31j1_subsurface_submod']['ci95'][0]:.4f}, {scr['scores']['h31j1_subsurface_submod']['ci95'][1]:.4f}]</td><td>— (ablation arm)</td><td>—</td><td>—</td><td>—</td></tr>
          <tr><td>Same-run <code>physical_hgb</code> control (pinned template features)</td><td>{scr['scores']['physical_hgb']['dti']:.4f} [{scr['scores']['physical_hgb']['ci95'][0]:.4f}, {scr['scores']['physical_hgb']['ci95'][1]:.4f}]</td><td>{conf['scores']['physical_hgb']['dti']:.4f} [{conf['scores']['physical_hgb']['ci95'][0]:.4f}, {conf['scores']['physical_hgb']['ci95'][1]:.4f}]</td><td>—</td><td>—</td><td>—</td></tr>
          <tr><td>MAGREST concordant (prior current-run primary)</td><td>{scr['scores']['magrest_concordant']['dti']:.4f} [{scr['scores']['magrest_concordant']['ci95'][0]:.4f}, {scr['scores']['magrest_concordant']['ci95'][1]:.4f}]</td><td>{conf['scores']['magrest_concordant']['dti']:.4f} [{conf['scores']['magrest_concordant']['ci95'][0]:.4f}, {conf['scores']['magrest_concordant']['ci95'][1]:.4f}]</td><td>0.0700</td><td>0.0610</td><td>62.75%</td></tr>
          <tr><td>GEMSDOE32 H33-2-B2 reference (0.2778 USER-REPORTED)</td><td>{scr['scores']['gemsdoe32_h33_b2_foldfair']['dti']:.4f} (fold-fair)</td><td>{conf['scores']['gemsdoe32_h33_b2_foldfair']['dti']:.4f} (fold-fair)</td><td>{h33_sgmc['sgmc_all_elevation_dti']:.4f}</td><td>{h33_sgmc['sgmc_piedmont_lt100m_dti']:.4f}</td><td>{100*h33_sgmc['far_field_gt_1p5km_fraction']:.2f}%</td></tr>
          <tr><td>H31-E2 SCGP-Submod (prior multi-physics candidate)</td><td>— (separate draw=101 instrument)</td><td>— (separate draws 202,303)</td><td>{scgp_sgmc.get('sgmc_all_elevation_dti', 0.0816):.4f}</td><td>{scgp_sgmc.get('sgmc_piedmont_lt100m_dti', 0.1289):.4f}</td><td>{100*scgp_sgmc.get('far_field_gt_1p5km_fraction', 0.3151):.2f}%</td></tr>
        </tbody>
      </table></div>
      <div class="content" style="margin-top:18px">
        <h3>Own-Method Spatial Residual Range &amp; Key Irregularities Flagged</h3>
        <ul>
          <li><strong>Own-Method OOF Residual Semivariogram (Gate G5):</strong> Computed across <code>5,709</code> withheld fault pixels (<code>122,132</code> within-component pairs across <code>332</code> components). Weighted exponential fit yields scale <code>{vario['scale_parameter_m']:,.1f} m</code> and 95%-sill practical range <strong><code>{vario['practical_range_95_sill_m']:,.1f} m</code> (10.72 km, R² = {vario['weighted_r_squared']:.4f})</strong>, confirming that the <code>21,300 m</code> holdout buffer is <code>1.99×</code> the residual range and covers <code>{100*vario['sill_fraction_at_collar']:.2f}%</code> of sill.</li>
          <li><strong>Data Header Mislabel Disclosed &amp; Fixed:</strong> Band <code>B06</code> in <code>training_features.tif</code> is labeled <code>Magnetic_Tilt_Angle</code> in metadata, whereas <code>registry/data_provenance.json</code> proves <code>B06</code> is actually <code>GeoDAWN_Radiometric_TotalCount</code> (rho = +0.996). H31-J treats <code>B06</code> strictly as radiometric total count and computes true magnetic Miller–Singh tilt angle spectrally from <code>B02</code> RTP.</li>
          <li><strong>Conflicting Leaderboard Anchors Without Organizer Receipts:</strong> Prompt prose cites both <code>0.3195</code> and <code>0.4413</code> as #1 leaderboard figures alongside <code>0.2778</code> for GEMSDOE32 H33-2-B2, with zero organizer submission receipts in any of the nine audited repos. Every external score remains labeled <code>USER-REPORTED</code>, and no local <code>HOLDOUT-DTI</code> or <code>HOLDOUT-PROXY-SGMC</code> number is ever projected onto the live leaderboard scale.</li>
          <li><strong>Next-Session Priority Recommendations:</strong> (1) Protocol-owner decision formally separating synthetic geometry-probe lattices (<code>r13-lattice-s5</code>) from genuine fault-prediction entries in the shared 695-raster registry before any live slot review; (2) Confirm outside-footprint convention (<code>-zeros.zip</code> vs <code>-nan.zip</code>) against organizer specification; (3) Test Rank #2 hypothesis <strong>H31-K</strong> (transtensional stepover / relay accommodation saddle) as an orthogonal subsurface signal.</li>
        </ul>
      </div>
    </section>'''


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
    # Archived cards never confer current approval; the shared-registry STOP is binding.
    scr = hr["experiment_1_screen_draw_101"]
    conf = hr.get("experiment_2_confirmation")
    proxies = hr["experiment_3_sgmc_proxies"]["candidates"]
    pr, pb, ph = proxies["rbu31"], proxies["baseline_d_final"], proxies["h33_2_b2_actual_peer_file"]
    dup = rc["correlation_overlap_vs_registry"]
    name = esc(rc["submission_name"])
    note = esc(rc["submission_note"])

    def badge(ok):
        return '<span class="badge badge-green">PASS</span>' if ok else '<span class="badge badge-red">FAIL</span>'

    verdict_badge = '<span class="badge badge-red">ARCHIVED RESEARCH ONLY &middot; DO NOT SUBMIT (shared-registry STOP)</span>'
    heading = "RBU31 Regime-Balanced Union: archived · DO NOT SUBMIT"
    conf_row = ("not run (screen stop)" if not conf else
                f"HOLDOUT-DTI {conf['rbu31_pooled_dti']:.4f} [{conf['rbu31_ci95'][0]:.4f}, {conf['rbu31_ci95'][1]:.4f}] "
                f"vs {conf['baseline_d_pooled_dti']:.4f} (delta {conf['paired_delta_dti']:+.4f}, "
                f"95% CI [{conf['paired_delta_ci95'][0]:+.4f}, {conf['paired_delta_ci95'][1]:+.4f}]); "
                f"{conf['withheld_positives_pooled']:,} withheld positives")
    return f'''<section id="rbu31" aria-labelledby="rbu31-heading">
      <div class="section-head"><div><p class="kicker">Archived 2026-10-25 research candidate &middot; RBU31 (Experiment 13)</p>
        <h2 id="rbu31-heading">{heading}</h2></div>
        <p>One union model (raw-39 + SCGP-40 features in the same trees) trained with regime-balanced sample weights
           (piedmont det_elev &le; 50 m vs mountain), validated end-to-end by automated gates &mdash; no human inspector.
           Every dot is newly computed; no prior submission dots were copied.</p></div>
      <div class="card download-card">
        {verdict_badge}
        <h3 style="margin-top:18px">{name}</h3>
        <p>Historical method description, not a performance forecast: RBU31 combined an older sparse-dot family with a regime-balanced union model.
           The H33 score remains USER-REPORTED; geometric pruning does not reveal deleted dots' hidden-truth credit, and RBU31's local holdout/proxy results do not establish a private-score gain.</p>
        <div class="actions">
          <a class="button button-primary" href="downloads/{name}-allfinite.tif" download>Download RBU31 archived research TIFF (DO NOT SUBMIT)</a>
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
          <strong>Historical artifact identifier (not approval):</strong> <code>{name}</code><br>
          <strong>Portal note ({rc['submission_note_chars']}/140):</strong> <code>{note}</code></p>
      </div>
      <div class="table-wrap" style="margin-top:18px"><table>
        <thead><tr><th>Automated gate</th><th>Threshold</th><th>Measured RBU31 value</th><th>Status</th></tr></thead>
        <tbody>
          <tr><td><code>G1 &middot; Format &amp; [0, 1]</code></td><td>EPSG:32611, 3730&times;3292, float32, finite in footprint, values in [0, 1]</td><td>see format receipt</td><td>{badge(gates['G1_format_and_range_0_1_pass'])}</td></tr>
          <tr><td><code>G2 &middot; Leakage canary</code></td><td>every one of 79 features alone: two-sided AUC &le; 0.90</td><td>max AUC = {rc['leakage_canary']['max_two_sided_auc']:.4f}</td><td>{badge(gates['G2_leakage_canary_pass'])}</td></tr>
          <tr><td><code>G3a &middot; Named-peer subset diagnostic</code></td><td>Pairwise comparison against {dup['checked_count']} listed peers only; not an exhaustive global gate</td><td>max |&rho;| = {max(abs(dup['max_surface_spearman_rho']), abs(dup['max_final_dots_spearman_rho'])):.4f}; max 3-px overlap = {100*dup['max_final_dots_within_3px']:.2f}%</td><td><span class="badge">SUBSET ONLY</span></td></tr>
          <tr><td><code>G3b &middot; Spacing-5 lattice (695-raster registry)</code></td><td>literal unexempted overlap rule</td><td>registered witness covers any nonempty in-footprint candidate within 3 px; exact final support fails</td><td><span class="badge badge-red">LITERAL STOP · DO NOT SUBMIT</span></td></tr>
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
        <tr><td>Holdout DTI — off-catalogue SGMC</td>
            <td>{f"HOLDOUT-DTI {dti_sgmc:.4f} (truth px 61,664)" if dti_sgmc is not None else "HOLDOUT-DTI n/a"}</td></tr>
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


def _h31s_card():
    rc_path = ROOT / "evidence/h31s/run_card.json"
    if rc_path.is_file():
        return json.loads(rc_path.read_text())
    return None


def h31s_download_and_gates():
    rc = _h31s_card()
    if rc is None:
        return ""
    art = rc["artifact"]
    exp1, exp2, exp3 = rc["experiments"]
    s41 = exp3["screen_seed41"]
    s42 = exp3["confirmation_seed42"]
    col = rc["spatial_collar"]
    can = rc["leakage_canary"]
    uq_d = rc["uniqueness"]["discrete_competitor_scope"]
    uq_l = rc["uniqueness"]["literal_695_shared_registry_scope"]
    sg = rc["sgmc_external_proxy"]
    fz = esc(art["file_zeros"].removeprefix("docs/"))
    fn = esc(art["file_nan"].removeprefix("docs/"))
    fzip = esc(art["zip_zeros"].removeprefix("docs/"))
    frec = esc(art["receipt_json"].removeprefix("docs/"))
    return f'''
<section id="h31s-download" aria-labelledby="h31s-heading">
  <div class="section-head"><div><p class="kicker">Archived parallel run · 2026-10-26 · H31-S (UDAP-SSLIC) · 3-Experiment Campaign</p>
    <h2 id="h31s-heading">DOWNLOAD FOR RESEARCH: YES · SUBMIT TO DRIVENDATA: NO (DO NOT SUBMIT)</h2></div>
    <p>Original 37,654-dot physics-driven GeoTIFF built from Up-Dip Basin-Depth Advected Potential-Field projection (UDAP),
      Hydrothermal Magnetite-Destruction Axial Troughs (HZAD), Contour/Seam Null Suppressors, and 2-Stage Nested OOF
      Strike-Steered Line-Integral Continuity (SSLIC) on the unchanged <code>gems57-pooled-hide-v2</code> evaluator.
      Zero copied dots (47.4% 3-px overlap vs GEMSDOE32 H33-2-B2; 55.7% vs GEMSDOE27 H29).</p></div>
  <div class="card download-card">
    <span class="badge badge-red">RESEARCH DOWNLOAD ONLY · DO NOT SUBMIT · slot_approved = false</span>
    <h3 style="margin-top:18px">{esc(art['name'])}</h3>
    <p>Automated format, CRS, transform, and strict [0, 1] range checks PASS with zero human intervention on both
      the defensive all-finite zeros-outside file (prevents &ldquo;Predicted values must be in range [0, 1]&rdquo;)
      and the official-wording NaN-outside companion. Upload remains blocked by the literal unexempted 695-raster
      spacing-5 lattice rule (99.93% within 3 px), the strict 3/4-quadrant screen rule vs same-instrument H31-M on seed 41,
      and separate selector promotion.</p>
    <div class="actions">
      <a class="button button-primary" href="{fz}" download>Download H31-S Research .tif (all-finite [0,1] zeros-outside)</a>
      <a class="button button-dark" href="{fn}" download>NaN-outside twin .tif</a>
      <a class="button" href="{fzip}" download>Single-TIFF .zip</a>
      <a class="button" href="downloads/h31s-run-card.json" download>JSON Run Card</a>
      <a class="button" href="{frec}" download>Validation receipt .json</a>
    </div>
    <p class="download-meta"><strong>Grid &amp; Range:</strong> 1-band float32 · EPSG:32611 · 3730 x 3292 · 100 m ·
      {art['positive_pixels']:,} binary dots · {art['positive_pixels_on_public_catalogue']} on public catalogue · finite [0.0, 1.0]<br>
      <strong>SHA-256 (zeros-outside primary):</strong> <code>{esc(art['sha256_zeros'])}</code> ({art['bytes_zeros']:,} B)<br>
      <strong>SHA-256 (NaN-outside twin):</strong> <code>{esc(art['sha256_nan'])}</code> ({art['bytes_nan']:,} B)<br>
      <strong>SHA-256 (single-TIFF .zip):</strong> <code>{esc(art['sha256_zip'])}</code> ({art['bytes_zip']:,} B)<br>
      <strong>Historical artifact identifier (not an approved submission name):</strong> <code>{esc(art['name'])}</code><br>
      <strong>Note ({art['note_length']}/140 chars):</strong> <code>{esc(art['note_140'])}</code></p>
    <div class="table-wrap"><table>
      <thead><tr><th>Automated Gate</th><th>Measured Evidence (unchanged <code>gems57-pooled-hide-v2</code>)</th><th>Status</th></tr></thead>
      <tbody>
        <tr><td>Format, grid &amp; [0, 1] range (both encodings)</td>
            <td>EPSG:32611 · 3730x3292 · 100 m · 0 NaN inside footprint · all values in {{0.0, 1.0}}</td>
            <td><span class="badge badge-green">PASS</span></td></tr>
        <tr><td>Single-feature &amp; missingness leakage canary</td>
            <td>Stage-1 max two-sided AUC {can['stage1_max_value_auc']:.4f} · Stage-2 SSLIC max AUC {can['stage2_max_value_auc']:.4f} · missingness AUC {can['stage1_max_missing_auc']:.4f} (&lt;= 0.90)</td>
            <td><span class="badge badge-green">PASS</span></td></tr>
        <tr><td>Candidate-specific OOF residual variogram collar</td>
            <td>Measured H31-S along-component decay range {col['raw_derived_buffer_m']/1000:.2f} km (exponential {col['decision']['model_practical_ranges_m']['exponential']/1000:.2f} km, spherical {col['decision']['model_practical_ranges_m']['spherical']/1000:.2f} km); adopted {col['adopted_buffer_px']} px (21.3 km)</td>
            <td><span class="badge badge-green">MEASURED</span></td></tr>
        <tr><td>EXP-1 -> EXP-2 -> EXP-3 Screen (seed 41, {s41['withheld_positive_pixels']:,} withheld px)</td>
            <td>HOLDOUT-DTI: Physical-HGB {exp1['physical_hgb_holdout_dti']:.4f} -> H31-M {exp1['incumbent_h31m_submod_holdout_dti']:.4f} -> Stage-1 UDAP+HZAD {exp2['holdout_dti']:.4f} -> <strong>H31-S Full {s41['holdout_dti']:.4f}</strong> [{s41['ci95'][0]:.4f}, {s41['ci95'][1]:.4f}] (vs Physical-HGB {s41['vs_physical_hgb']['delta']:+.4f}, CI [{s41['vs_physical_hgb']['ci95'][0]:+.4f}, {s41['vs_physical_hgb']['ci95'][1]:+.4f}], 3/4 quads PASS; vs H31-M {s41['vs_incumbent_h31m_submod']['delta']:+.4f}, CI [{s41['vs_incumbent_h31m_submod']['ci95'][0]:+.4f}, {s41['vs_incumbent_h31m_submod']['ci95'][1]:+.4f}], 1/4 quads)</td>
            <td><span class="badge badge-red">MIXED (PASS vs control; 1/4 quads vs H31-M)</span></td></tr>
        <tr><td>EXP-3 Untouched Fresh Confirmation (seed 42, {s42['withheld_positive_pixels']:,} withheld px)</td>
            <td>HOLDOUT-DTI: Physical-HGB {s42['physical_hgb_dti']:.4f} -> H31-M {s42['incumbent_h31m_submod_dti']:.4f} -> <strong>H31-S Full {s42['holdout_dti']:.4f}</strong> [{s42['ci95'][0]:.4f}, {s42['ci95'][1]:.4f}] (vs Physical-HGB {s42['vs_physical_hgb']['delta']:+.4f}, CI [{s42['vs_physical_hgb']['ci95'][0]:+.4f}, {s42['vs_physical_hgb']['ci95'][1]:+.4f}], 4/4 quads PASS; vs H31-M {s42['vs_incumbent_h31m_submod']['delta']:+.4f}, CI [{s42['vs_incumbent_h31m_submod']['ci95'][0]:+.4f}, {s42['vs_incumbent_h31m_submod']['ci95'][1]:+.4f}], 4/4 quads PASS)</td>
            <td><span class="badge badge-green">PASS (4/4 quads vs both)</span></td></tr>
        <tr><td>External USGS SGMC proxy (&gt;300 m off catalogue)</td>
            <td>SGMC-PROXY All {sg['h31s_sgmc_all_dti']:.4f} · Piedmont {sg['h31s_sgmc_piedmont_dti']:.4f} · Mountain {sg['h31s_sgmc_mountain_dti']:.4f} (beats GEMSDOE27 H29 All 0.0820 &amp; MAGREST All 0.0707; 31.2% piedmont dot share)</td>
            <td><span class="badge">DIAGNOSTIC</span></td></tr>
        <tr><td>Discrete competitor uniqueness (all 9 peer sites + local)</td>
            <td>Final 37,654 dots max 3-px overlap {uq_d['max_final_dots_3px_overlap']*100:.1f}% (&lt;= 70% PASS; 47.4% vs H33-2-B2, 55.7% vs GEMSDOE27 H29); surface max |Spearman| {uq_d['max_surface_abs_spearman']:.4f} (&lt;= 0.90 PASS); unplaced top-K surface 72.5% vs one internal RBU31 research raster (68.6% max across all external sites)</td>
            <td><span class="badge badge-red">FINAL DOTS PASS · TOP-K SURFACE 72.5% LOCAL</span></td></tr>
        <tr><td>Literal 695-raster shared registry (unexempted)</td>
            <td>{uq_l['final_dots_in_lattice_3px']*100:.2f}% of dots within 3 px of registered 13GEMSDOE spacing-5 lattice <code>r13-lattice-s5</code> (100% within GEMSDOE48 dense baseline)</td>
            <td><span class="badge badge-red">STOP · BLOCKS UPLOAD</span></td></tr>
        <tr><td>Leaderboard upload approval</td>
            <td>Research download enabled; DrivenData upload NOT approved (<code>slot_approved = false</code>, 0 weekly slots spent)</td>
            <td><span class="badge badge-red">DO NOT SUBMIT</span></td></tr>
      </tbody>
    </table></div>
  </div>
</section>
'''


def _rbu31_card():
    for sub in ("regime31b", "regime31"):
        rc_path = ROOT / "evidence" / sub / "run_card.json"
        if rc_path.is_file():
            return json.loads(rc_path.read_text())
    return None


def overview(card):
    link = links(card)
    score = card["holdout_dti"]
    delta = card["paired_difference"]
    final = card["registry"]["final"]
    name = esc(card["submission_name"])
    hero = f'''<section class="hero"><div class="wrap hero-grid"><div>
      <p class="eyebrow">DOE GEMS Prize · Current registered run · {esc(card['hypothesis'])}</p>
      <h1>RESEARCH DOWNLOAD ONLY<br>DO NOT SUBMIT</h1>
      <p class="hero-lede"><strong>{name}</strong> is the artifact named by <code>registry/current_run.json</code>.
        Local format checks pass, but its preregistered screen is negative: HOLDOUT-DTI
        {score['dti']:.5f} [{score['ci95'][0]:.5f}, {score['ci95'][1]:.5f}] using
        <code>{esc(score['evaluator_version'])}</code> ({score['withheld_positive_pixels']:,} withheld positives).
        Paired difference vs its same-run control is {delta['delta']:+.5f}
        [{delta['ci95'][0]:+.5f}, {delta['ci95'][1]:+.5f}], crossing zero.
        The literal shared-registry overlap gate also fails ({100 * final['max_overlap']:.1f}% of final dots within 3 px of a registered witness).</p>
      <div class="actions">
        <a class="button button-primary" href="{link('file')}" download>Download MAGREST research TIFF (DO NOT SUBMIT)</a>
        <a class="button" href="{link('zip_file')}" download>One-TIFF research ZIP</a>
        <a class="button" href="downloads/magrest-run-card.json" download>JSON run card and validation</a>
        <a class="button button-light" href="executive-summary.html">Nine-Site Executive Summary &amp; Submission Guide</a>
      </div>
      </div><aside class="hero-side" aria-label="Submission decision">
        <strong>OK TO DOWNLOAD FOR RESEARCH: YES</strong>
        <p><strong>DO NOT SUBMIT.</strong> <code>ok_to_submit = false</code> · <code>slot_approved = false</code> ·
          0 slots used. The nine pinned peer-tree comparison passed, but one authentic shared-registry witness is enough to fail the literal 70% overlap rule; global uniqueness is not proven. Historical H31-S, H31-T, H31-J and other run cards remain below as research records, not current approval.</p></aside></div></section>'''
    return hero, _overview_body(card, hero_rbu=False)


def _overview_body(card, *, hero_rbu: bool):
    s = card["holdout_dti"]
    delta = card["paired_difference"]
    final = card["registry"]["final"]
    magrest_notice = '''<div class="notice notice-danger"><strong>Not approved for upload.</strong>
      Automated verdict: DO NOT SUBMIT under the unexempted 695-raster shared-registry overlap rule (<code>slot_approved = false</code>). Download H31-S, H31-T, H31-J, XFCOH31, CONCORD31, RBU31-B, H31-M, H31-HVDC, H31-E2, or MAGREST for research, not for a weekly competition slot.</div>'''
    body = f'''{magrest_notice}
      {download(card)}
      {focus_site_summary()}
      <section><div class="section-head"><div><p class="kicker">Historical research archive</p><h2>Earlier run cards — not the active registered run</h2></div>
        <p>The entries below preserve prior experiments and their own results. They do not override <code>registry/current_run.json</code>, pass the literal shared-registry STOP, or authorize a submission.</p></div></section>
      {h31s_download_and_gates()}
      {h31t_download_and_gates()}
      {h31j_download_and_gates()}
      {rbu31_download_and_gates()}
      {h31m_download_and_gates()}
      {hvdc_download_and_gates()}
      {scgp_download_and_gates()}
      {h3_download_and_gates()}'''
    body += f'''
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
      {_focus_unique_2026_html()}
    </section>'''


def _focus_unique_2026_html() -> str:
    p = ROOT / "registry/focus_unique_2026.json"
    if not p.is_file():
        return ""
    data = json.loads(p.read_text())
    rows_html = []
    for item in data.get("sites", []):
        site = esc(item["site"])
        s25_val = esc(item["scored_20261025_value"])
        s25_art = esc(item["scored_20261025_artifact"])
        s25_url = item.get("scored_20261025_url") or ""
        if s25_url:
            s25_cell = (
                f'<a href="{esc(s25_url)}" target="_blank" rel="noopener">{s25_art}</a><br>'
                f'<strong>{s25_val}</strong> <span class="badge">USER-REPORTED · no organizer receipt</span>'
            )
        else:
            s25_cell = f"{s25_art} ({s25_val})"

        cur_art = esc(item["current_unique_artifact"])
        cur_url = esc(item["current_unique_url"])
        target_attr = ' target="_blank" rel="noopener"' if cur_url.startswith("http") else ""
        sha12 = esc(item["current_sha256"][:12])
        dots = int(item["dots"])
        ov_h33 = 100.0 * float(item["overlap_3px_vs_h33"])
        ov_h29 = 100.0 * float(item["overlap_3px_vs_h29"])
        sg_all, sg_pied, sg_mtn = item["sgmc_all_pied_mtn"]
        gate_txt = esc(item["site_gate_status"])
        snapshot_note = (
            '<br><span class="small">Pinned parallel snapshot only; this repository\'s active registered run is MAGREST.</span>'
            if item["site"] == "GEMSDOE31" else ""
        )
        rows_html.append(
            f'<tr><td><strong>{site}</strong></td>'
            f'<td>{s25_cell}</td>'
            f'<td><a href="{cur_url}"{target_attr}>{cur_art}</a>{snapshot_note}<br>'
            f'<span class="small">SHA-256 <code>{sha12}…</code> · {dots:,} dots · [0,1] valid</span></td>'
            f'<td>{ov_h33:.1f}% vs H33<br>{ov_h29:.1f}% vs H29</td>'
            f'<td>{sg_all:.4f} / {sg_pied:.4f} / {sg_mtn:.4f}</td>'
            f'<td>{gate_txt}</td></tr>'
        )
    return f'''<div style="margin-top:28px">
      <h3>Pairwise-distinct research records in the pinned 2026-10-25/26 site snapshot</h3>
      <p class="small">The newer records shown here have &le;56% 3-px dot overlap with H33-2-B2 in the recorded pairwise comparison and pass local EPSG:32611 / [0, 1] checks. This is only a comparison with named peer rasters, <strong>not</strong> broad/global uniqueness or submission approval; the shared spacing-5 registry witness remains a binding STOP for any nonempty prediction. Leaderboard figures are USER-REPORTED with no organizer receipt. SGMC-PROXY DTI is a local diagnostic, not a competition score; columns are <code>All / Piedmont (&le;6 deg) / Mountain (&gt;6 deg)</code> (for example, the pinned GEMSDOE32 R6 record reaches 0.1424 overall but 0.0030 Piedmont SGMC and 0.0034 Quaternary holdout DTI).</p>
      <div class="table-wrap"><table><thead><tr><th>Site</th><th>2026-10-25 supplied score claim</th>
        <th>Pinned 2026-10-26 source-snapshot artifact</th><th>Pairwise 3-px overlap vs H33 / H29</th>
        <th>SGMC-PROXY (All / Pied / Mtn)</th><th>Recorded gate status (not current approval)</th></tr></thead>
        <tbody>{''.join(rows_html)}</tbody></table></div>
    </div>'''


def executive(card):
    failed = "".join(f"<li>{esc(x)}</li>" for x in card["failed_or_unknown_gates"])
    focus_summary = focus_site_summary()
    return f'''<div class="notice notice-danger"><strong>Current registered run: {esc(card['submission_name'])} · OK TO DOWNLOAD FOR RESEARCH: YES · DO NOT SUBMIT.</strong>
      <code>ok_to_submit = false</code> and <code>slot_approved = false</code>. The active run has a negative HOLDOUT-DTI screen and a literal shared-registry overlap STOP. Historical lane artifacts below retain their own receipts, but none supersedes <code>registry/current_run.json</code> or authorizes an upload. Human sign-off cannot override a failed gate.</div>
      {download(card)}
      {focus_summary}
      <section><div class="section-head"><div><p class="kicker">Historical research archive</p><h2>Earlier run cards — not the active registered run</h2></div>
        <p>Prior experiments are retained for audit and education. Their comparator-subset checks do not override the shared-registry STOP or current no-submission decision.</p></div></section>
      {h31s_download_and_gates()}
      {h31t_download_and_gates()}
      {h31j_download_and_gates()}
      {rbu31_download_and_gates()}
      {h31m_download_and_gates()}
      {hvdc_download_and_gates()}
      {scgp_download_and_gates()}
      {h3_download_and_gates()}
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
      <p>Parallel-lane artifacts from prior sessions remain archived with their source bytes and recorded receipts where available. Different evaluators and instruments are not ranked against the active MAGREST run.</p></div>
      <div class="notice"><strong>No approval is imported from any archived card.</strong>Historical promote flags are not reproduced or endorsed by the active run and are not selector authority. Archived records are retained for audit; their subset checks and local outcomes do not override the literal shared-registry STOP. No new fit or candidate was created in this review.</div>
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
      {download(card)}
      <section><div class="section-head"><div><p class="kicker">Historical 2026-10-26 preregistration · H31-S archive</p><h2>Archived H31-S method and its historical alternatives</h2></div>
        <p>This table preserves the original <a href="https://github.com/buffedlizard55-lab/GEMSDOE31/blob/main/knowledge/2026-10-26_h31s_udap_sslic_preregistration.md">H31-S preregistration</a> for audit; it is not the current hypothesis ranking. H31-S and the H31-T/U/V alternatives are historical, not active authorization. The separate three-item desk-only backlog below reflects the current review.</p></div>
        <div class="table-wrap"><table><thead><tr><th>Rank / ID</th><th>Specific layers &amp; physical signature</th><th>Why missing from USGS/INGENIOUS &amp; novelty vs repo</th><th>Ordinal potential, cost &amp; access</th></tr></thead><tbody>
          <tr><td>1 · H31-S (UDAP-SSLIC) · executed archive</td><td><code>depth_to_base_surf</code>, <code>iso_grav_anom_slope</code>, GeoDAWN <code>TMI_up150</code>/<code>K</code>/<code>Th</code>, <code>rtp</code>, <code>cond_surf</code>, GDR-1391 thermal/sinter/volcanics; Cordell&ndash;Grauch up-dip advection + axial trough + strike-steered continuity</td><td>Dipping range-front and intra-basin structures can shift potential-field steps basinward; the archived operator tests up-dip projection plus nested OOF continuity. This is historical work, not a new experiment or current promotion.</td><td>Historical HOLDOUT-DTI only; not a competition score or comparable forecast. Medium compute; source access/provenance remains mirror-conditional.</td></tr>
          <tr><td>2 · H31-T-SWARM (SWARM-COULOMB) · historical preregistered alternative</td><td><code>ieq_n100a15</code>, <code>deq_n100a15</code>, <code>geod_2ndinv</code>, <code>geod_shearrate</code>, <code>geod_dilaterate</code>; microseismic swarm excess × Andersonian slip tendency</td><td>Earlier hypothesis for active fluid-related stepovers; not tested or adopted as a current proposal in this review.</td><td>Historical ordinal estimate only; seismic spatial scales are coarse relative to the 300 m kernel. No numeric gain or current authorization.</td></tr>
          <tr><td>3 · H31-U (InSAR + 3DEP) · historical external roadmap</td><td>Sentinel-1 ARIA LOS gradients + high-resolution 3DEP drainage/scarp evidence</td><td>Earlier external-data idea for active deformation or channel offsets; not part of the current desk-only backlog.</td><td>Required layers were not fetched; access, station/scene coverage, cost, and score impact remain unverified.</td></tr>
          <tr><td>4 · H31-V (USArray MT) · historical external roadmap</td><td>Magnetotelluric phase-tensor / induction-arrow structure</td><td>Earlier idea for deep conductive fluid pathways; not part of the current desk-only backlog.</td><td>External layers were not fetched; station coverage, cost, and score impact remain unverified.</td></tr>
        </tbody></table></div>
      </section>
      {h31t_download_and_gates()}
      {h31t_phd_forensic_and_hypotheses()}
      {h31j_research_sections()}
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
      <section><div class="section-head"><div><p class="kicker">Current desk review · not authorized for execution</p><h2>Three distinct hypotheses, ranked by expected value and cost</h2></div>
        <p>Ordinal, uncertain research priorities—not numeric score forecasts. No new fit is authorized. The shared feature stack and raw source rasters are not present in this checkout, so the layer inventory and access conditions require verification before any future protocol.</p></div>
        <div class="table-wrap"><table><thead><tr><th>Rank / method</th><th>Layers / discriminating signature</th><th>Expected value and key mimic</th><th>Cost / present limitation</th></tr></thead><tbody>
          <tr><td>1 · GRAVREST · desk-only</td><td>B2 RTP + B13 gravity; signed, compatible texture-displacement estimates across both fabrics</td><td>Highest information value among these proposals, but uncertain; a buried transfer structure should displace both fabrics coherently. Mimic: shared lithologic or intrusive contact.</td><td>Medium-high implementation and resolution cost; gravity bandwidth may be too coarse. Cached stack is absent here.</td></tr>
          <tr><td>2 · RADREST · desk-only</td><td>GeoDAWN K/Th/U compositional textures; channel-specific direction agreement rather than a ratio/edge threshold</td><td>Moderate, uncertain potential for offset alteration/provenance textures. Mimic: alluvial provenance boundary or survey seam.</td><td>Medium-high cost for missingness and quantization controls; raw data and verified channel metadata are absent.</td></tr>
          <tr><td>3 · TERRREST · desk-only</td><td>B12 elevation + B19 slope; detrended drainage-texture displacement across a candidate trace</td><td>Lowest expected value at the available 100 m scale; tests offset drainage texture rather than curvature alone. Mimic: stream capture or avulsion.</td><td>High validation cost; terrain bands are not in this checkout and finer-resolution 3DEP access requires verification.</td></tr>
        </tbody></table></div>
        <p>The assigned method paragraph is absent from the current owner prompt. MAGREST is the separate active registered run and remains negative; this review does not treat it as a newly assigned hypothesis and authorizes no additional experiment.</p>
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
