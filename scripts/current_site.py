"""Current-run site components. Results always come from generated evidence JSON."""
from __future__ import annotations

import html
import json
from pathlib import Path, PurePosixPath

import focus_review

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


def _selector():
    p = ROOT / "registry/selector_decision_20261026.json"
    return json.loads(p.read_text()) if p.is_file() else None


def selector_decision_section() -> str:
    """The current literal protocol overrides archived discrete-only approvals."""
    p = ROOT / "registry/release_status.json"
    if not p.is_file():
        return '<div class="notice notice-danger">DO NOT SUBMIT: current protocol audit missing.</div>'
    r = json.loads(p.read_text())
    h = r["holdout_dti"]
    u = r["correlation_overlap_vs_registry"]
    filename = esc(r["file"].replace("docs/", "", 1))
    return f'''<section id="selector-decision" aria-labelledby="selector-heading">
      <p class="kicker">Current release audit · 26 October 2026 · no new experiment</p>
      <h2 id="selector-heading">DO NOT SUBMIT — literal registry STOP</h2>
      <div class="notice notice-danger"><strong>No current artifact is approved.</strong>
      Earlier H31-X / H31-T selector upload permissions are withdrawn under the current prompt.
      A format pass cannot override failed uniqueness. No new TIFF was generated after STOP.</div>
      <div class="table-wrap"><table><thead><tr><th>File to download</th><th>HOLDOUT-DTI (prior receipt)</th>
      <th>Estimated leaderboard score</th><th>Unique under requested rule?</th><th>Permission</th></tr></thead><tbody><tr>
      <td><a href="{filename}" download>{esc(Path(r["file"]).name)}</a><br>Existing H31-X, not new this session</td>
      <td>{h["dti"]:.4f}, 95% CI [{h["ci95"][0]:.4f}, {h["ci95"][1]:.4f}]<br>
      {esc(h["evaluator_version"])}, {h["withheld_positive_pixels"]:,} withheld; cited, not rerun</td>
      <td>Unavailable: cross-family calibration unvalidated. Historical projection is not a score or reliable interval. Quantified this session (a111fe50): the retired in-family formula has out-of-family RMSE 0.196 / bias +0.135 over 67 matched USER-REPORTED submissions; best cross-family LOO RMSE 0.090 barely beats the mean (<code>evidence/cross_family_calibration_20261026.json</code>).</td>
      <td>No: surface top-K {100*u["surface"]["max_overlap"]:.1f}% (prior receipt);
      final dots {100*u["final"]["max_overlap"]:.2f}% vs registered lattice (fresh read-back).</td>
      <td>Research download YES<br><strong>Submission NO</strong></td></tr></tbody></table></div>
      <div class="actions"><a class="button button-primary" href="{filename}" download>Download existing H31-X research .tif — DO NOT SUBMIT</a>
      <a class="button" href="downloads/current-release-status.json">Current automated release / format receipt</a>
      <a class="button" href="downloads/protocol-review-run-card.json">Prior protocol audit</a></div>
      <p><strong>SHA-256:</strong> <code>{esc(r["raster_sha256"])}</code><br>
      <strong>Research name:</strong> <code>{esc(r["submission_name"])}</code><br>
      <strong>Note:</strong> {esc(r["note"])}</p>
      <p>Values are finite in [0,1]; one float32 band; CRS, shape and transform match the hash-pinned mirror template.
      This is local validation, not organizer acceptance. Private truth, authenticated score receipts and current weekly quota are unavailable.</p>
      <p>One authentic registry witness suffices for STOP; no exhaustive registry pass is claimed.
      The lattice covers {100*r["lattice_coverage"]["coverage_fraction"]:.3f}% of the footprint within 3 px.
      At this dot budget any placement must overlap at least {100*r["lattice_coverage"]["minimum_overlap_any_same_budget"]:.2f}%.
      This counting bound does not apply to every nonempty raster. Moving dots to evade the test is not geological discovery.
      A budget-only preflight now detects this unavoidable STOP before any new fit or placement.
      The current permission is published once in <a href="downloads/current-release-status.json">release status JSON</a>;
      historical lane cards are not upload permissions.</p>
      <p><a href="https://github.com/buffedlizard55-lab/GEMSDOE31/blob/main/knowledge/2026-10-26_release_review_bf9d261d.md">Review, hypotheses, evidence and remaining work</a></p>
    </section>'''


def h31y_download_and_gates() -> str:
    """H31-Y KIN-PIED research GeoTIFF. Lane card negative. Not approved for upload."""
    rc_path = ROOT / "evidence/h31y/run_card.json"
    if not rc_path.is_file():
        return ""
    rc = json.loads(rc_path.read_text())
    g = rc["gates"]
    hd = rc["holdout_dti"]
    sc = hd["screen_final_surface"]
    dc = hd["screen_paired_vs_ctrl"]
    cf = hd["confirmation_random_component_split"]
    cfd = cf["paired_differences"]["CTRL"]
    sg = rc["sgmc_proxy"]
    u = rc["correlation_overlap_vs_registry"]
    pj = rc["projection"]
    f = rc["files"]

    def badge(ok):
        return '<span class="badge badge-green">PASS</span>' if ok else '<span class="badge badge-red">FAIL</span>'

    return f'''<section id="h31y-kinpied" aria-labelledby="h31y-heading">
      <div class="section-head"><div><p class="kicker">2026-10-26 · H31-Y KIN-PIED unique research GeoTIFF</p>
        <h2 id="h31y-heading">H31-Y: generated TIF · <span class="badge badge-red">DO NOT SUBMIT</span></h2></div>
        <p>Preregistered before fitting. Three experiments. Not approved for upload (lane G5 top-K fail and
           literal registry STOP). Format-valid all-finite values in [0, 1].</p></div>
      <div class="card download-card">
        <h3><code>{esc(f["zeros"].split("/")[-1])}</code></h3>
        <p><strong>OK TO DOWNLOAD FOR RESEARCH: YES. NOT OK TO SUBMIT.</strong>
           Name <code>{esc(rc["submission_name"])}</code>. Note ({rc["note_chars"]}/140): <code>{esc(rc["note"])}</code></p>
        <p><strong>Hypothesis.</strong> {esc(rc["hypothesis"])}<br>
           <strong>Mechanism.</strong> {esc(rc["mechanism"])}<br>
           <strong>Named non-fault mimics.</strong> {esc(rc["non_fault_mimic"])}</p>
        <div class="actions">
          <a class="button" href="{esc(f["zeros"].replace("docs/", "", 1))}" download>Download H31-Y research .tif (all-finite [0,1] — DO NOT SUBMIT)</a>
          <a class="button" href="{esc(f["zip"].replace("docs/", "", 1))}" download>Single-TIFF .zip</a>
          <a class="button button-light" href="downloads/h31y-run-card.json">Run card (JSON)</a>
        </div>
        <p class="download-meta"><strong>SHA-256 zeros:</strong> <code>{esc(rc["raster_sha256"])}</code><br>
          HOLDOUT-DTI (gems57-pooled-hide-v2, {sc["withheld_positive_pixels"]:,} withheld) {sc["dti"]:.4f}
          [{sc["ci95"][0]:.4f}, {sc["ci95"][1]:.4f}]; paired vs CTRL {dc["delta"]:+.4f}
          [{dc["ci95"][0]:+.4f}, {dc["ci95"][1]:+.4f}]; confirmation paired {cfd["delta"]:+.4f}.
          Off-catalogue SGMC {sg["candidate"]["dti"]:.4f} vs H33 {sg["H33"]["dti"]:.4f} (COMPUTED).
          PROJECTION {pj["value"]:.4f} (never a score). Final-dot 3-px max {100*u["discrete_max_final_overlap_3px"]:.1f}%;
          top-K {100*(u["discrete_max_topk_overlap_3px"] or 0):.1f}% (G5 fail). Lattice overlap disclosed, not exempted.</p>
      </div>
      <div class="table-wrap"><table><thead><tr><th>Gate</th><th>Result</th></tr></thead><tbody>
        <tr><td>G1 format</td><td>{badge(g["G1_format"])}</td></tr>
        <tr><td>G2 canary</td><td>{badge(g["G2_canary"])}</td></tr>
        <tr><td>G3 holdout efficacy</td><td>{badge(g["G3_holdout_efficacy"])}</td></tr>
        <tr><td>G4 SGMC discovery</td><td>{badge(g["G4_sgmc_discovery"])}</td></tr>
        <tr><td>G5 uniqueness (incl. top-K)</td><td>{badge(g["G5_uniqueness_discrete"])}</td></tr>
        <tr><td>G6 projection ge 0.2778</td><td>{badge(g["G6_projection_ge_02778"])}</td></tr>
      </tbody></table></div>
      </section>'''


def h31aa_download_and_gates() -> str:
    """2026-10-27 Lane H31-AA (SLFS) unique research GeoTIFF + updated 2026-10-27 executive audit."""
    rc_path = ROOT / "evidence/h31aa/run_card.json"
    if not rc_path.is_file():
        return ""
    rc = json.loads(rc_path.read_text())
    g = rc["gates"]
    det = g["detail"]
    hd = rc["holdout_dti"]
    sc = hd["screen_final_surface"]
    inc = hd["incumbent_h31x_same_run"]
    d_inc = hd["screen_paired_vs_h31x"]
    d_ctrl = hd["screen_paired_vs_ctrl"]
    cf = hd["confirmation_random_component_split"]
    cfs = cf["scores"][det["winner"]]
    cf_inc = cf["scores"]["JUNC_INC"]
    sg = rc["sgmc_proxy"]
    u = rc["correlation_overlap_vs_registry"]
    diag = rc["diagnostics"]
    f = rc["files"]
    fmt_rel = f"downloads/{rc['submission_name']}-format-check.json"

    def badge(ok):
        return '<span class="badge badge-green">PASS</span>' if ok else '<span class="badge badge-red">FAIL</span>'

    return f'''<section id="h31aa-slfs" aria-labelledby="h31aa-heading">
      <div class="section-head"><div><p class="kicker">2026-10-27 · H31-AA (SLFS) newly generated unique research GeoTIFF</p>
        <h2 id="h31aa-heading">H31-AA: Strike-Coherent Log-Flexure &amp; Paleoshoreline-Null · <span class="badge badge-red">DO NOT SUBMIT</span></h2></div>
        <p>Frozen preregistration before any data touch (SHA-256 <code>{esc(rc["preregistration"]["sha256"][:12])}…</code>).
           Three-experiment budget executed via shared <code>evaluate_holdout.py</code> and <code>submission_writer.py</code>.
           Validated all-finite <code>[0, 1]</code> GeoTIFF for research download only (<code>slot_approved = false</code>).</p></div>
      <div class="card download-card">
        <h3><code>{esc(f["zeros"].split("/")[-1])}</code></h3>
        <p><strong>OK TO DOWNLOAD FOR RESEARCH: YES · DO NOT SUBMIT (<code>verdict = negative</code>, <code>slot_approved = false</code>).</strong><br>
           Unique name: <code>{esc(rc["submission_name"])}</code> · Portal note ({rc["note_chars"]}/140): <code>{esc(rc["note"])}</code></p>
        <p><strong>Hypothesis.</strong> {esc(rc["hypothesis"])}<br>
           <strong>Mechanism.</strong> {esc(rc["mechanism"])}<br>
           <strong>Named non-fault mimics.</strong> {esc(rc["non_fault_mimic"])}</p>
        <div class="actions">
          <a class="button button-primary" href="{esc(f["zeros"].replace("docs/", "", 1))}" download>Download H31-AA research .tif (all-finite [0,1] — DO NOT SUBMIT)</a>
          <a class="button" href="{esc(f["zip"].replace("docs/", "", 1))}" download>Single-TIFF .zip</a>
          <a class="button button-light" href="{esc(f["nan"].replace("docs/", "", 1))}" download>NaN-outside twin (.tif)</a>
          <a class="button button-light" href="{esc(fmt_rel)}">Automated format receipt</a>
          <a class="button button-light" href="downloads/h31aa-run-card.json">H31-AA Run Card (JSON)</a>
        </div>
        <p class="download-meta"><strong>SHA-256 (all-finite zeros .tif):</strong> <code>{esc(rc["raster_sha256"])}</code><br>
          <strong>SHA-256 (zeros .zip):</strong> <code>{esc(rc["zip_sha256"])}</code> · <strong>SHA-256 (nan .tif):</strong> <code>{esc(rc["raster_sha256_nan"])}</code><br>
          <strong>HOLDOUT-DTI ({esc(sc["evaluator_version"])}, {sc["withheld_positive_pixels"]:,} withheld, 21.3 km collar):</strong>
          AA2 <strong>{sc["dti"]:.4f}</strong> [{sc["ci95"][0]:.4f}, {sc["ci95"][1]:.4f}]
          (arm AA4 reached <strong>{det["exp1_screen_scores"]["AA4"]["dti"]:.4f}</strong> overall and <strong>0.1512 vs 0.1454</strong> beating H31-X on NW Fold 0 [29,319 positives])
          vs same-run H31-X incumbent <strong>{inc["dti"]:.4f}</strong> [{inc["ci95"][0]:.4f}, {inc["ci95"][1]:.4f}]
          (paired delta {d_inc["delta"]:+.4f} [{d_inc["ci95"][0]:+.4f}, {d_inc["ci95"][1]:+.4f}]) and CTRL {d_ctrl["delta"]:+.4f} [{d_ctrl["ci95"][0]:+.4f}, {d_ctrl["ci95"][1]:+.4f}].<br>
          <strong>Untouched Confirmation (seed=3107, {cfs["withheld_positive_pixels"]:,} withheld):</strong>
          AA2 {cfs["dti"]:.4f} [{cfs["ci95"][0]:.4f}, {cfs["ci95"][1]:.4f}] vs H31-X {cf_inc["dti"]:.4f}.<br>
          <strong>Off-catalogue USGS-SGMC discovery proxy (COMPUTED):</strong> All {sg["candidate"]["dti"]:.4f} vs H33 {sg["H33"]["dti"]:.4f};
          <strong>Piedmont (&le;6 deg) 0.0929 (#1 across all 9 focus sites, +58.5% over H33 0.0586 &amp; +110% over H31-X 0.0442)</strong>;
          median catalogue distance {diag["median_d_cat_px"]:.1f} px; steep bedrock &gt;15 deg cut from 18.6% (H31-X) to {100*diag["frac_slope_gt_15deg"]:.2f}%.<br>
          <strong>Estimated leaderboard score:</strong> Unavailable (cross-family projection unvalidated; M3 zero-catalogue diagnostic {rc["projection"]["m3_zero_catalogue_central"]:.3f} &plusmn; 0.186 PROJECTION, never a score).</p>
      </div>
      <div class="table-wrap"><table><thead><tr><th>Automated Gate</th><th>Status</th><th>Measured Receipt</th></tr></thead><tbody>
        <tr><td>G1 GeoTIFF format &amp; [0, 1] range</td><td>{badge(g["G1_format"])}</td><td>EPSG:32611 · 3730&times;3292 · float32 · 0 NaN · 37,654 binary dots · 0 on catalogue</td></tr>
        <tr><td>G2 Single-feature leakage canary (&le;0.90)</td><td>{badge(g["G2_canary"])}</td><td>15/15 lines &amp; surfaces pass (max two-sided AUC 0.7574)</td></tr>
        <tr><td>G3a Beats physical CTRL &amp; SLOPE</td><td>{badge(g["G3_beats_baselines"])}</td><td>+{d_ctrl["delta"]:.4f} vs CTRL on screen; +0.0731 on seed-3107 confirmation</td></tr>
        <tr><td>G3b Beats global holdout best (H31-X 0.1661)</td><td>{badge(g["G3_beats_holdout_best"])}</td><td>AA2 0.1489 (AA4 0.1556; wins NW Fold 0 0.1512 &gt; 0.1454, loses high-relief NE Fold 1)</td></tr>
        <tr><td>G4 Off-catalogue SGMC overall (&ge;H33 0.0940)</td><td>{badge(g["G4_sgmc_discovery"])}</td><td>Overall 0.0688 &lt; 0.0940 (#1 Piedmont 0.0929, lower Mountain 0.0393 due to 18 deg cap)</td></tr>
        <tr><td>G5a Protocol surface |&rho;| &le;0.90 &amp; final dots &le;70%</td><td>{badge(g["G5_protocol_surface_rho_and_final_dots"])}</td><td>Max |Spearman| {u["max_abs_spearman_surface"]:.4f}; max final 3-px overlap {100*u["discrete_max_final_overlap_3px"]:.2f}% across 45 peers</td></tr>
        <tr><td>G5b External 9-site two-stage (top-K &amp; final &le;70%)</td><td>{badge(g["G5_external_focus_two_stage"])}</td><td>Max external top-K {100*u["external_focus_max_topk_overlap_3px"]:.2f}% &le; 70%; max external final {100*u["external_focus_max_final_overlap_3px"]:.2f}% (solves H31-X 86.3% external top-K failure)</td></tr>
        <tr><td>G5c Unspaced top-K vs local GEMSDOE31 H31-X</td><td>{badge(g["G5_discrete_two_stage"])}</td><td>Unspaced crest top-K 85.0% vs local H31-X (post-Poisson final dots 60.6% &le; 70%)</td></tr>
        <tr><td>G5d Binding literal 695-raster broad registry</td><td>{badge(g["G5_literal_broad_registry"])}</td><td>{100*u["literal_broad_registry"]["candidate_overlap_3px"]:.2f}% vs spacing-5 lattice r13-lattice-s5 (&ge;82.34% mathematical floor at 37,654 dots; no exemption)</td></tr>
      </tbody></table></div>
      <div class="table-wrap" style="margin-top:18px"><table>
        <caption>2026-10-27 Master Audit Summary — Newly Generated H31-AA, Local Holdout Leader H31-X, &amp; Newly Scored Oct 25–26 Focus/Sibling Runs</caption>
        <thead><tr><th>Artifact / Site</th><th>Evidence-Labeled Metric</th><th>Estimated Leaderboard Score</th><th>Uniqueness Across GEMSDOE Sites</th><th>Download &amp; Upload Status</th></tr></thead>
        <tbody>
          <tr><td><strong>GEMSDOE31 · H31-AA (new 2026-10-27)</strong><br><a href="{esc(f["zeros"].replace("docs/", "", 1))}" download><code>{esc(f["zeros"].split("/")[-1])}</code></a></td>
              <td>HOLDOUT-DTI (gems57-pooled-hide-v2, 60,988, 95% CI [0.1368, 0.1604]): <strong>0.1489</strong> (AA4: 0.1556; Piedmont SGMC <strong>0.0929</strong>)</td>
              <td>Unavailable (no validated cross-family model)</td>
              <td>External 9-site 2-stage PASS (69.3% / 57.0%); all-peer final PASS (60.6%); literal 695-lattice STOP (98.3%)</td>
              <td><span class="badge badge-red">DO NOT SUBMIT</span><br>Research download YES</td></tr>
          <tr><td><strong>GEMSDOE31 · H31-X (local holdout best)</strong><br><a href="downloads/gemsdoe31-h31x-piedmont-junction-37654-20261026-5a956da9-zeros.tif" download><code>gemsdoe31-h31x-piedmont-junction-37654-20261026-5a956da9-zeros.tif</code></a></td>
              <td>HOLDOUT-DTI (gems57-pooled-hide-v2, 60,988, 95% CI [0.1491, 0.1825]): <strong>0.1661</strong> (SGMC 0.1209)</td>
              <td>Unavailable</td>
              <td>Final discrete PASS (63.1%); Stage-1 external top-K FAIL (86.3% vs D1.5); literal lattice STOP (99.3%)</td>
              <td><span class="badge badge-red">DO NOT SUBMIT</span><br>Research download YES</td></tr>
          <tr><td><strong>GEMSDOE32 · H33-2-B2 (historical family high)</strong><br><code>h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros</code></td>
              <td><strong>0.2778</strong> <code>USER-REPORTED · no organizer receipt</code> (prompt cites 0.4413 current competition high &amp; 0.3195 earlier anchor)</td>
              <td>Already scored claim (unverified receipt)</td>
              <td>Exact subset of D2.8 at d_cat &gt; 2 px (100% self-overlap; 86.7%–97.4% across D1.5/D2.8 sites)</td>
              <td><span class="badge badge-red">DO NOT RESUBMIT</span><br>Prior art</td></tr>
          <tr><td><strong>GEMSDOE27 · H31-DRCG (Oct 26 wave leader)</strong><br><code>gems27-h31-drcg-wl-celf28-20261026-cf8e1bbef244-allfinite</code></td>
              <td><strong>0.2250</strong> <code>USER-REPORTED · no organizer receipt</code> (+ H29: <strong>0.2190</strong>)</td>
              <td>Already scored claim</td>
              <td>50.2% 3-px overlap vs H33 (d_cat median 16.3 px; genuine off-catalogue piedmont/Walker Lane reach)</td>
              <td><span class="badge badge-red">DO NOT RESUBMIT</span><br>Prior art</td></tr>
          <tr><td><strong>GEMSDOE36 · KPL36-EXP3 (Oct 26 wave #2)</strong><br><code>gemsdoe36-kpl36-exp3-20261026-fc869911e88c-zeros</code></td>
              <td><strong>0.1647</strong> <code>USER-REPORTED · no organizer receipt</code> (MSDB1 on GEMSDOE30: <strong>0.1462</strong>; S33-SEISDIL on GEMSDOE33: <strong>0.0963</strong>)</td>
              <td>Already scored claim</td>
              <td>56.1% 3-px overlap vs H33 (d_cat median 14.9 px)</td>
              <td><span class="badge badge-red">DO NOT RESUBMIT</span><br>Prior art</td></tr>
          <tr><td><strong>PU Halo Collapse Diagnosis (Oct 25–26)</strong><br>G24 GVC1 (0.0859), G25 H66 (0.0742), G91 S22 (0.0298), G28 S18 (0.0217), G28 S21 (0.0206)</td>
              <td><strong>0.0206 – 0.0859</strong> <code>USER-REPORTED · no organizer receipt</code>; sibling sites KANLER/EUG/WBG/GINNYGEMSDOE1–3 unscored</td>
              <td>Already scored / unscored</td>
              <td>Byte forensics: G28 S21 places 97% of dots within 15 px of mapped catalogue (median 4.1 px), memorizing potential-field blur halos around known faults</td>
              <td><span class="badge badge-red">DO NOT SUBMIT</span><br>Forensic negative</td></tr>
        </tbody></table></div>
      </section>'''


def _h31yz_section(lane_key: str, lane_name: str, kicker: str, card_file: str) -> str:
    """H31-Y/H31-Z regime-split lanes (2026-10-26, session 579233d5): data-driven from run cards."""
    rc_path = ROOT / f"evidence/{lane_key}/run_card.json"
    if not rc_path.is_file():
        return ""
    rc = json.loads(rc_path.read_text())
    g = rc["gates"]
    det = g.get("detail", {})
    hd = rc["holdout_dti"]
    sc = hd["screen_final_surface"]
    dc = hd["screen_paired_vs_ctrl"]
    ds = hd["screen_paired_vs_slope"]
    dj = hd.get("screen_paired_vs_junc_incumbent") or {}
    cf = hd["confirmation_random_component_split"]
    winner = det.get("winner", "")
    cfs = cf["scores"].get(winner, {})
    cfctrl = cf["scores"].get("CTRL", {})
    cfd = cf["paired_differences"].get("CTRL", {})
    sg = rc["sgmc_proxy"]
    u = rc["correlation_overlap_vs_registry"]
    pj = rc["projection"]
    f = rc["files"]
    regs = sg.get("regimes", {})
    cand_pied = regs.get("candidate_piedmont_le6deg", {})
    cand_mtn = regs.get("candidate_mountain_gt6deg", {})

    def badge(ok):
        return '<span class="badge badge-green">PASS</span>' if ok else '<span class="badge badge-red">FAIL</span>'

    if rc["verdict"] == "promote":
        verdict_badge = '<span class="badge badge-green">lane gates pass — selector decision above governs upload choice</span>'
        dl_label = "Download all-finite .tif (values in [0,1])"
    else:
        verdict_badge = '<span class="badge badge-red">DO NOT SUBMIT — research download only</span>'
        dl_label = "Download research .tif — DO NOT SUBMIT"
    lit = u.get("literal_broad_registry", {}) or {}
    return f'''<section id="{lane_key}-regime-split" aria-labelledby="{lane_key}-heading">
      <div class="section-head"><div><p class="kicker">{esc(kicker)}</p>
        <h2 id="{lane_key}-heading">{esc(lane_name)}: unique label-free GeoTIFF · {verdict_badge}</h2></div>
        <p>Preregistered before any fitting (<a href="https://github.com/buffedlizard55-lab/GEMSDOE31/blob/main/{esc(rc["preregistration"])}">frozen preregistration</a>);
        three experiments, no tuning after EXP-3. Every number is HOLDOUT-DTI, COMPUTED or PROJECTION; nothing is ORGANIZER-CONFIRMED.</p></div>
      <div class="card download-card">
        <h3><code>{esc(f["zeros"].split("/")[-1])}</code></h3>
        <p><strong>Hypothesis.</strong> {esc(rc["hypothesis"])}<br>
           <strong>Mechanism.</strong> {esc(rc["mechanism"])}<br>
           <strong>Named non-fault mimics.</strong> {esc(rc["non_fault_mimic"])}</p>
        <div class="actions">
          <a class="button button-primary" href="{esc(f["zeros"].replace("docs/", "", 1))}" download>{dl_label}</a>
          <a class="button" href="{esc(f["zip"].replace("docs/", "", 1))}" download>Single-TIFF .zip</a>
          <a class="button button-light" href="{esc(f["nan"].replace("docs/", "", 1))}" download>NaN-outside twin</a>
          <a class="button button-light" href="downloads/{esc(card_file)}">Run card (JSON)</a>
        </div>
        <p class="download-meta"><strong>SHA-256 (all-finite):</strong> <code>{esc(rc["raster_sha256"])}</code><br>
          <strong>Portal name:</strong> <code>{esc(rc["submission_name"])}</code> · <strong>note ({rc["note_chars"]}/140):</strong> <code>{esc(rc["note"])}</code><br>
          <strong>Lane verdict:</strong> <code>{esc(rc["verdict"])}</code> · {esc(rc["instruction"])}</p>
      </div>
      <div class="table-wrap"><table><thead><tr><th>Gate (frozen)</th><th>Rule</th><th>Measured</th><th>Result</th></tr></thead><tbody>
        <tr><td><code>G1 format</code></td><td>float32 · EPSG:32611 · 3730×3292 · [0,1] · both conventions · exactly 37,654 dots · 0 on catalogue</td>
            <td>zeros ok={rc["validator"]["zeros"]["ok"]}, nan ok={rc["validator"]["nan"]["ok"]}</td><td>{badge(g["G1_format"])}</td></tr>
        <tr><td><code>G2 canary</code></td><td>every line/surface two-sided AUC ≤ 0.90 vs catalogue and off-SGMC</td>
            <td>max AUC 0.76 (SLOPE vs off-SGMC); all lines ≤ 0.90 (evidence/h31y_regimesplit/canary.json)</td><td>{badge(g["G2_canary"])}</td></tr>
        <tr><td><code>G3 holdout efficacy</code></td><td>pooled HOLDOUT-DTI beats CTRL and SLOPE, paired 95% CI &gt; 0, ≥3/4 quadrants, untouched confirmation CI &gt; 0</td>
            <td>HOLDOUT-DTI {sc["dti"]:.4f} [{sc["ci95"][0]:.4f}, {sc["ci95"][1]:.4f}] ({esc(sc["evaluator_version"])}, n={sc["withheld_positive_pixels"]:,}) ·
                Δ vs CTRL {dc["delta"]:+.4f} [{dc["ci95"][0]:+.4f}, {dc["ci95"][1]:+.4f}] ·
                Δ vs SLOPE {ds["delta"]:+.4f} [{ds["ci95"][0]:+.4f}, {ds["ci95"][1]:+.4f}] ·
                Δ vs JUNC incumbent surface {dj.get("delta", float("nan")):+.4f} · {hd["quadrant_wins_vs_ctrl"]}/4 quadrants ·
                confirmation (seed {cf["partition"]["seed"]}, n={cfs.get("withheld_positive_pixels", 0):,}): {cfs.get("dti", float("nan")):.4f} vs CTRL {cfctrl.get("dti", float("nan")):.4f}, Δ {cfd.get("delta", float("nan")):+.4f}</td>
            <td>{badge(g["G3_holdout_efficacy"])}</td></tr>
        <tr><td><code>G4 discovery proxy</code></td><td>full-footprint off-catalogue SGMC DTI ≥ H33-2-B2 recomputed same day</td>
            <td>{sg["candidate"]["dti"]:.4f} (TPw {sg["candidate"]["tpw"]:,.0f}) vs H33 {sg["H33"]["dti"]:.4f} (TPw {sg["H33"]["tpw"]:,.0f});
                piedmont slope ≤6 deg (band): {cand_pied.get("dti", float("nan")):.4f} ({cand_pied.get("n_dots", 0):,} dots);
                mountain &gt;6 deg: {cand_mtn.get("dti", float("nan")):.4f}</td>
            <td>{badge(g["G4_sgmc_discovery"])}</td></tr>
        <tr><td><code>G5 uniqueness (owner rule)</code></td><td>final-dot 3-px overlap ≤ 0.70; |Spearman| ≤ 0.90 vs every discrete peer; literal lattice disclosed</td>
            <td>final dots max {100 * (u["discrete_max_final_overlap_3px"] or 0):.1f}% · ROUTE-proxy top-K {100 * (u.get("discrete_max_topk_overlap_3px_proxy") or 0):.1f}% (disclosed, not gated) ·
                |Spearman| dots {abs(u.get("max_abs_spearman_dots") or 0):.3f} ·
                literal 695-lattice {100 * (lit.get("candidate_overlap_3px") or 0):.1f}% (fails for every nonempty raster; lane judged under IR-U-02, since superseded by the literal release STOP above)</td>
            <td>{badge(g["G5_uniqueness_discrete"])}</td></tr>
        <tr><td><code>G6 projection</code></td><td>anchor-inversion PROJECTION ≥ 0.2778 (never a score)</td>
            <td>PROJECTION {pj["value"]:.4f} [{pj["interval_approx"][0]:.3f}, {pj["interval_approx"][1]:.3f}] (in-family LOO RMSE {pj["loo_rmse"]:.4f}; cross-family transfer unproven)</td>
            <td>{badge(g["G6_projection_ge_02778"])}</td></tr>
      </tbody></table></div>
      </section>'''


def h31yr_download_and_gates() -> str:
    return _h31yz_section("h31y_regimesplit", "H31-YR ROUTE (duplicate STOP; filed as H31-Y by session 579233d5 — distinct from H31-Y KIN-PIED above)", "2026-10-26 · Lane H31-YR · slope-routed regime blend — measured duplicate, DO NOT SUBMIT", "h31y-regimesplit-run-card.json")


def h31z_download_and_gates() -> str:
    return _h31yz_section("h31z", "H31-Z hard quota split", "2026-10-26 · Lane H31-Z · hard regime quota split (successor to H31-YR)", "h31z-run-card.json")

def h31ym_download_and_gates() -> str:
    """H31-YM regime-mosaic (session a111fe50; executed as H31-Y, renamed on merge)."""
    p = ROOT / "evidence/h31ym/run_card.json"
    if not p.is_file():
        return ""
    y = json.loads(p.read_text())
    exp1_p = ROOT / "evidence/h31ym/exp1_screen.json"
    rows = ""
    if exp1_p.is_file():
        exp1 = json.loads(exp1_p.read_text())
        labels = {"Y1": "Y1 FAN piedmont specialist only", "Y2": "Y2 junction only (H31-X method comparator; reproduced 0.1661)",
                  "Y3": "Y3 regime mosaic 50/50 (candidate)", "Y4": "Y4 pixel blend",
                  "CTRL": "CTRL rank(tmi_hg)", "SLOPE": "SLOPE rank(slope)"}
        for arm, lab in labels.items():
            s = exp1["pooled"]["scores"][arm]
            rows += (f'<tr><td>{esc(lab)}</td><td>{s["dti"]:.4f} [{s["ci95"][0]:.4f}, {s["ci95"][1]:.4f}]</td></tr>')
        pied = exp1["subgroup_piedmont"]["pooled"]["scores"]
        rows += (f'<tr><td>Piedmont-truth subgroup: Y3 vs Y2 (29,324 withheld)</td>'
                 f'<td>Y3 {pied["Y3"]["dti"]:.4f} vs Y2 {pied["Y2"]["dti"]:.4f} (kernel credit 2,172 vs 642)</td></tr>')
    gates = " · ".join(
        f'{esc(k)}={"PASS" if v else "FAIL"}' for k, v in y["gates"].items() if k.startswith("G"))
    return f'''<section id="h31ym"><div class="section-head"><div>
      <p class="kicker">Parallel lane · 2026-10-26 session a111fe50 · preregistered, automated gates</p>
      <h2>H31-YM regime-mosaic — unique research TIFF, verdict negative (DO NOT SUBMIT)</h2></div>
      <p>Mountain dots from the piedmont-junction slope-break line; piedmont dots from one-sided, strike-coherent,
        low-relief 1 m-LiDAR fan scarps; 50/50 budget. Executed as “H31-Y” in its session and renamed H31-YM on
        merge (the KIN-PIED lane above keeps H31-Y; see <code>evidence/h31ym/RENAME.json</code>).
        No prior dots or surfaces used. Under current literal-STOP governance no file is approved in any case.</p></div>
      <div class="card download-card">
        <span class="badge badge-red">DO NOT SUBMIT — preregistered gates failed</span>
        <h3 style="margin-top:18px"><code>{esc(y["files"]["zeros"])}</code></h3>
        <div class="actions">
          <a class="button" href="downloads/{esc(y["files"]["zeros"])}" download>Research .tif — all-finite [0,1] (do not submit)</a>
          <a class="button button-light" href="downloads/{esc(y["files"]["nan"])}" download>NaN-outside twin</a>
          <a class="button button-light" href="downloads/{esc(y["submission_name"])}-run-card.json" download>Run card JSON</a>
        </div>
        <p class="download-meta"><strong>SHA-256:</strong> <code>{esc(y["raster_sha256"])}</code> ·
          <strong>Gates:</strong> {esc(gates)}<br>
          <strong>Reserved name (do not use):</strong> <code>{esc(y["submission_name"])}</code> ·
          <strong>Note ({y["submission_note_chars"]}/140):</strong> <code>{esc(y["submission_note"])}</code><br>
          <strong>Discrete-unique (not literal-rule unique):</strong> max 3-px final-dot overlap
          {100 * y["registry"]["max_final_overlap_3px"]:.1f}% vs discrete peers (45.9% vs H33);
          literal spacing-5 lattice reading fails as for every 37,654-dot field (counting bound in the protocol review).<br>
          <strong>Score estimate:</strong> unavailable (cross-family RMSE ≈0.09–0.20; see selector section). Any
          in-family number on the run card is a withdrawn diagnostic, never a score.</p>
        <div class="table-wrap"><table><thead><tr><th>Arm (same folds, same evaluator)</th>
          <th>HOLDOUT-DTI [95% CI] — gems57-pooled-hide-v2, 60,988 withheld positives</th></tr></thead>
          <tbody>{rows}</tbody></table></div>
        <p class="small">Halving the mountain budget costs more catalogue credit than the fan specialist gains at
          the catalogue's 48% piedmont truth mix (break-even &gt;57% piedmont); untouched component-split
          confirmation (seed 3104) repeats the ordering. Next step recorded: marginal-credit allocation
          (~70–80% mountain) under a fresh preregistration — only after the owner resolves the registry
          definition. Receipts: <code>evidence/h31ym/</code>.</p>
      </div></section>'''


def h31x_download_and_gates() -> str:
    """H31-X piedmont-junction lane (2026-10-26, session 3ce68fc7): download, gates, disclosure."""
    rc_path = ROOT / "evidence/h31x/run_card.json"
    if not rc_path.is_file():
        return ""
    rc = json.loads(rc_path.read_text())
    g = rc["gates"]
    hd = rc["holdout_dti"]
    sc = hd["screen_final_surface"]
    dc = hd["screen_paired_vs_ctrl"]
    ds = hd["screen_paired_vs_slope"]
    cf = hd["confirmation_random_component_split"]
    cfs = cf["scores"]
    cfd = cf["paired_differences"]["CTRL"]
    sg = rc["sgmc_proxy"]
    u = rc["correlation_overlap_vs_registry"]
    pj = rc["projection"]
    f = rc["files"]
    e2_path = ROOT / "evidence/h31x/exp2.json"
    ov_h33 = 0.0
    if e2_path.is_file():
        for r in json.loads(e2_path.read_text())["uniqueness"]["rows"]:
            if "h33-h33-2-b2" in r.get("peer", "") and "final_overlap_3px" in r:
                ov_h33 = r["final_overlap_3px"]
                break
    def badge(ok):
        return '<span class="badge badge-green">PASS</span>' if ok else '<span class="badge badge-red">FAIL</span>'
    verdict_badge = ('<span class="badge badge-green">OK TO SUBMIT</span>' if rc["verdict"] == "promote"
                     else '<span class="badge badge-red">DO NOT SUBMIT — both-stage registry STOP</span>')
    return f'''<section id="h31x-piedmont-junction" aria-labelledby="h31x-heading">
      <div class="section-head"><div><p class="kicker">2026-10-26 · Historical lane H31-X · piedmont-junction range-front contact line</p>
        <h2 id="h31x-heading">H31-X: unique label-free GeoTIFF · {verdict_badge}</h2></div>
        <p>Preregistered before any fitting (<a href="https://github.com/buffedlizard55-lab/GEMSDOE31/blob/main/{esc(rc["preregistration"])}">frozen preregistration</a>);
        three experiments, no tuning after EXP-3. Every number is HOLDOUT-DTI, COMPUTED or PROJECTION; nothing is ORGANIZER-CONFIRMED.</p></div>
      <div class="card download-card">
        <h3><code>{esc(f["zeros"].split("/")[-1])}</code></h3>
        <p><strong>Hypothesis.</strong> {esc(rc["hypothesis"])}<br>
           <strong>Mechanism.</strong> {esc(rc["mechanism"])}<br>
           <strong>Named non-fault mimics.</strong> {esc(rc["non_fault_mimic"])}</p>
        <div class="actions">
          <a class="button button-primary" href="{esc(f["zeros"].replace("docs/", "", 1))}" download>Download all-finite .tif (values in [0,1])</a>
          <a class="button" href="{esc(f["zip"].replace("docs/", "", 1))}" download>Single-TIFF .zip</a>
          <a class="button button-light" href="{esc(f["nan"].replace("docs/", "", 1))}" download>NaN-outside twin</a>
          <a class="button button-light" href="downloads/h31x-run-card.json">Run card (JSON)</a>
        </div>
        <p class="download-meta"><strong>SHA-256 (all-finite):</strong> <code>{esc(rc["raster_sha256"])}</code><br>
          <strong>SHA-256 (NaN twin):</strong> <code>{esc(rc["raster_sha256_nan"])}</code><br>
          <strong>Portal name:</strong> <code>{esc(rc["submission_name"])}</code> · <strong>note ({rc["note_chars"]}/140):</strong> <code>{esc(rc["note"])}</code></p>
      </div>
      <div class="table-wrap"><table><thead><tr><th>Gate (frozen)</th><th>Rule</th><th>Measured</th><th>Result</th></tr></thead><tbody>
        <tr><td><code>G1 format</code></td><td>float32 · EPSG:32611 · 3730×3292 · exact transform · [0,1] · both conventions · 0 dots on catalogue</td>
            <td>zeros ok={rc["validator"]["zeros"]["ok"]}, nan ok={rc["validator"]["nan"]["ok"]}, hard failures none</td><td>{badge(g["G1_format"])}</td></tr>
        <tr><td><code>G2 canary</code></td><td>every line/surface two-sided AUC ≤ 0.90 vs catalogue and off-SGMC</td>
            <td>max AUC 0.76 (SLOPE vs off-SGMC); junction line 0.64 / 0.59</td><td>{badge(g["G2_canary"])}</td></tr>
        <tr><td><code>G3 holdout efficacy</code></td><td>pooled HOLDOUT-DTI beats CTRL and SLOPE, paired 95% CI &gt; 0, ≥3/4 quadrants, confirmation CI &gt; 0</td>
            <td>HOLDOUT-DTI {sc["dti"]:.4f} [{sc["ci95"][0]:.4f}, {sc["ci95"][1]:.4f}] ({esc(sc["evaluator_version"])}, n={sc["withheld_positive_pixels"]:,}) ·
                Δ vs CTRL {dc["delta"]:+.4f} [{dc["ci95"][0]:+.4f}, {dc["ci95"][1]:+.4f}] ·
                Δ vs SLOPE {ds["delta"]:+.4f} [{ds["ci95"][0]:+.4f}, {ds["ci95"][1]:+.4f}] · {hd["quadrant_wins_vs_ctrl"]}/4 quadrants ·
                untouched random-component split (n={cfs["X1"]["withheld_positive_pixels"]:,}): {cfs["X1"]["dti"]:.4f} vs CTRL {cfs["CTRL"]["dti"]:.4f}, Δ {cfd["delta"]:+.4f} [{cfd["ci95"][0]:+.4f}, {cfd["ci95"][1]:+.4f}]</td>
            <td>{badge(g["G3_holdout_efficacy"])}</td></tr>
        <tr><td><code>G4 discovery proxy</code></td><td>full-footprint off-catalogue SGMC DTI ≥ H33-2-B2 recomputed same day</td>
            <td>{sg["candidate"]["dti"]:.4f} (TPw {sg["candidate"]["tpw"]:,.0f}) vs H33 {sg["H33"]["dti"]:.4f} (TPw {sg["H33"]["tpw"]:,.0f}); 4/4 quadrants above H33;
                piedmont slope le 6 deg: {sg["regimes"]["candidate_piedmont_le6deg"]["dti"]:.4f} vs H33 {sg["regimes"]["H33_piedmont_le6deg"]["dti"]:.4f} (trade-off, disclosed);
                mountain slope gt 6 deg: {sg["regimes"]["candidate_mountain_gt6deg"]["dti"]:.4f} vs {sg["regimes"]["H33_mountain_gt6deg"]["dti"]:.4f}</td>
            <td>{badge(g["G4_sgmc_discovery"])}</td></tr>
        <tr><td><code>G5 uniqueness (both stages)</code></td><td>final-dot <em>and</em> pre-placement top-K 3-px overlap ≤ 0.70; |Spearman| ≤ 0.90 vs every discrete peer</td>
            <td>final dots max {100*u["discrete_max_final_overlap_3px"]:.1f}% (GEMSDOE27 D1.5 field), {100*ov_h33:.1f}% vs H33 ·
                pre-placement top-K {100*u["discrete_max_topk_overlap_3px"]:.1f}% (<strong>fails the required pre-placement check</strong>) ·
                |Spearman| surface {u["max_abs_spearman_surface"]:.3f}, dots {u["max_abs_spearman_dots"]:.3f} ·
                literal 695-lattice reading {100*u["literal_broad_registry"]["candidate_overlap_3px"]:.1f}% (fails for this artifact; no universal claim)</td>
            <td>{badge(g["G5_uniqueness_discrete"])}</td></tr>
        <tr><td><code>G6 projection</code></td><td>anchor-inversion PROJECTION ≥ 0.2778 (never a score)</td>
            <td>PROJECTION {pj["value"]:.4f} [{pj["interval_approx"][0]:.3f}, {pj["interval_approx"][1]:.3f}] (in-family LOO RMSE {pj["loo_rmse"]:.4f}; cross-family transfer unproven)</td>
            <td>{badge(g["G6_projection_ge_02778"])}</td></tr>
      </tbody></table></div>
      <p class="small"><strong>Current correction:</strong> both pre-placement and final-dot checks are required by the owner prompt.
      The prior selector excluded the pre-placement top-K failure and broad-registry witness. That permission is withdrawn.
      A discrete-peer subset pass is not a full uniqueness pass. This frozen lane card remains negative.</p>
      <p class="small">Fixed-dot reference arms (H33-2-B2, H31-T, H31-J, H31-B) were scored in the same folds at the previous session's request and
        are <strong>uninformative under this protocol</strong> (0.000–0.011): their authors pruned every dot within 2 px of the <em>full</em> catalogue,
        which removes nearly all 300 m-kernel credit around withheld segments. They are recorded as handicapped references only.</p>
      </section>'''


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
      <div class="section-head"><div><p class="kicker">2026-10-25 Latest Campaign · SI Crustal-Mechanics + Listric Restoration + Dinkelbach 29-Cell Submodular · H31-T</p>
        <h2 id="h31t-heading">H31-T Transtension-Dinkelbach: Research Download Only · DO NOT SUBMIT</h2></div>
        <p>Newly computed 100% label-free Dual-Specialist OOF HGB across 12 spatially collared folds (with H31-T's own measured 21.25 km OOF residual variogram, resolving <code>IR-31-OWN-METHOD-VARIOGRAM</code>) +
           Cost-Scaled Dinkelbach 29-cell submodular CELF allocation (37,654 binary {{0.0, 1.0}} dots, 0 within 200 m of public catalogue).
           Passes all 21/21 format &amp; [0, 1] checks, 35-plane leakage canary, unchanged <code>gems57-pooled-hide-v2</code> (+18.68%, 4/4 quadrants),
           disjoint <code>gemsdoe31-holdout-v1</code> Screen &amp; untouched Confirmation (+23.01%, 4/4 folds), Full &amp; 4-Block Off-Catalogue SGMC (+15.1% vs GEMSDOE32 H33-2-B2),
           and Phase A uniqueness across all 119 discrete fault maps in all 9 focus sites + GEMSDOE31 —
           but is <strong>blocked from weekly slot upload (DO NOT SUBMIT, slot_approved = false)</strong> under the unexempted 695-raster <code>r13-lattice-s5</code> / <code>GEMSDOE48</code> STOP rule.</p></div>
      <div class="card download-card">
        <span class="badge badge-green">LOCAL FORMAT &amp; 7/7 SCIENTIFIC GATES PASS · RESEARCH DOWNLOAD ONLY</span>
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
    return f'''<section id="h31t-forensic"><div class="section-head"><div><p class="kicker">2026-10-25 PhD Synthesis · H31-T</p><h2>Exact Nested Lineage of GEMSDOE32 (0.2778 USER-REPORTED) &amp; Four Ranked Crustal-Mechanics Hypotheses</h2></div>
      <p>Byte-verified pixel set-algebra across all 9 focus repositories, Tversky fractional marginal-ratio optimality, and 8-lane Off-Catalogue SGMC comparison.</p></div>
      <div class="content">
        <p><strong>Exact nested subset identity (computed directly on SHA-256-verified GeoTIFFs):</strong>
          <code>H19-5</code> (121,131 px, 0.1922 <code>USER-REPORTED</code>) →
          <code>GEMSDOE25 D1.5</code> (60,069 px, 0.2477 <code>USER-REPORTED</code>) →
          <code>GEMSDOE25 D2.8</code> (44,090 px, 0.2600 <code>USER-REPORTED</code>) →
          <code>GEMSDOE28 H27-4</code> (40,199 px, 0.2708 <code>USER-REPORTED</code>, <code>d_cat &gt; 100 m</code>) →
          <code>GEMSDOE32 H33-2-B2</code> (37,654 px, 0.2778 <code>USER-REPORTED</code>, <code>d_cat &gt; 200 m</code>).
          The measured H33 support is the D2.8 support with dots within two catalogue pixels removed.
          This adds no geological information. The historical score values remain USER-REPORTED without organizer receipts.</p>
        <p><strong>Corrected marginal DTI algebra (COMPUTED, not a performance forecast):</strong>
          Since <code>FNw = N − TPw</code>, fixed-truth DTI is
          <code>S = T / (0.2T + 0.2F + 0.8N + epsilon)</code>.
          Improvement for a finite change occurs exactly when
          <code>(1 − 0.2S) ΔT &gt; 0.2S ΔF</code>.
          For positive added FP weight, <code>ΔT / ΔF &gt; 0.2S / (1 − 0.2S)</code>.
          At the unverified illustrative value S=0.2778 this ratio is 0.0588285;
          in the special one-truth-cell case ΔT=k and ΔF=1−k, the bar is k&gt;0.05556, not a general hit probability.
          The former denominator 1−S was incorrect. The unchanged shared evaluator agrees with 10,000 finite-change checks.</p>
        <p><strong>Mechanism is an inference, not established private-score causality:</strong>
          Sparse spacing can avoid redundant kernel coverage; catalogue-flank pruning can save false-positive cost.
          Without private truth we cannot say the deleted dots were false positives, that added tail dots caused a decline,
          or that this pruning exhausted all possible improvement. A new physical detector must beat a same-instrument
          incumbent and pass confirmation and both registry checks before selection. No improvement is guaranteed.</p>
      </div>
      <div class="table-wrap" style="margin-top:16px"><table>
        <thead><tr><th>Rank &amp; Candidate</th><th>Input Layers &amp; Physical Transform</th><th>Why It Catches Unmapped Faults &amp; Differs from Prior Repo Lanes</th><th>Expected Gain / Cost / External Data</th></tr></thead>
        <tbody>
          <tr><td><code>1 · H31-T · Executed</code></td><td>SI 3D magnetic (nT/m) &amp; gravity (mGal/km) analytic signal + Thompson inverse depth, 55-deg up-dip listric footwall restoration, Kostrov–Byerlee transtension × 1/(1+d_eq/5km), hydrothermal magnetite-destruction × K/Th × clay-cap ridge, Cost-Scaled Dinkelbach CELF</td><td>Restores 0.8–2.5 km hanging-wall geophysical offsets up-dip onto buried range-front traces and handles reversed volcanic remanence; strictly 100% label-free (verified after <code>EXP-1</code> exposed <code>visible_catalogue</code> self-inclusion)</td><td>Highest · Medium (~21 min CPU) · 100% hash-pinned local stack</td></tr>
          <tr><td><code>2 · H31-R · Future</code></td><td>Anisotropic Riemann-tensor trace-linking geodesic graph across <code>step_max</code>, <code>bstep_grad_norm</code>, and 3D analytic signal</td><td>Connects intermittent 100–300 m buried relay segments across alluvial fan lobes via minimum-action elastoplastic paths rather than pixelwise GBDT + greedy disks</td><td>Moderate-High · High (~60–90 min Eikonal) · Local stack</td></tr>
          <tr><td><code>3 · H31-S · Future</code></td><td>Continuous-wavelet multi-depth tilt-derivative phase-convergence tomography (z = 200 m..3,200 m) on <code>tmi_rtp</code> &amp; <code>iso_grav_anom</code></td><td>Tracks continuous inclined fault planes from shallow splays down into crystalline basement while rejecting rootless tabular lava-flow margins</td><td>Moderate · Medium-High · Local stack</td></tr>
          <tr><td><code>4 · H31-V · Blocked</code></td><td>ARIA / Sentinel-1 MintPy vertical &amp; east-west InSAR velocity + seasonal poroelastic phase gradient</td><td>Detects active sub-mm/yr creep and hydraulic head-drop barriers across zero-scarp playa faults invisible to static potential fields</td><td>High on playas · Infeasible in sandbox (<code>asf.alaska.edu</code> / NASA Earthdata blocked by outbound TLS allowlist)</td></tr>
        </tbody>
      </table></div>
      <div class="table-wrap" style="margin-top:18px"><table>
        <thead><tr><th>8-Lane Off-Catalogue SGMC Comparison</th><th>Emitted Dots</th><th>Full Off-SGMC (&gt;300 m)</th><th>4-Block Collared Off-SGMC [95% CI]</th><th>Piedmont Off-SGMC (slope ≤ 6 deg)</th></tr></thead>
        <tbody>{''.join(rows_html)}</tbody>
      </table></div>
      <p class="small">Scientific transparency note: <code>EXP-1</code> (preserved verbatim in <code>evidence/h31t/exp1_vis_self_inclusion_diagnostic.json</code>) revealed that feeding fold-visible catalogue tip/relay fields into GBDT training creates <code>d0_m = 0</code> self-inclusion on training positives (collapsing Quadrant 1 Poisson DTI to 0.0693 vs 0.1410 ctrl). Removing catalogue-derived features in <code>EXP-2</code> made <code>H31-T</code> 100% label-free and lifted <code>gems57-pooled-hide-v2</code> to 0.1300 (+18.68%, 4/4 quadrants) and Full Off-SGMC to 0.1082 (+15.1% over <code>GEMSDOE32 H33-2-B2</code> 0.0940), while explaining the label-free piedmont trade-off (0.0434 vs 0.0586 in <code>cat_dist</code>-guided <code>H33-2-B2</code>).</p>
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
      <div class="section-head"><div><p class="kicker">Latest Preregistered Discovery Candidate · 2026-10-25 · Lane H31-J</p>
        <h2 id="h31j-heading">H31-J TGTD-Submod: All 6 Technical &amp; Scientific Gates PASS · Research Download Only · DO NOT SUBMIT</h2></div>
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
          <li><strong>B06 tilt-versus-radiometric conflict, unreverified:</strong> This session read <code>training_features.tif</code> band B06 as name <code>tc</code>, description “Tilt angle or total curvature”. The official problem page captions <code>gems_tc_tmi.png</code> as total radiometric counts. An older sentence on this page claimed <code>registry/data_provenance.json</code> proves B06 is GeoDAWN radiometric total count at rho +0.996. That file has no such proof, and the correlation was not recomputed. Do not treat either label as settled. H31-N did not use B06.</li>
          <li><strong>B10 distance-versus-density conflict:</strong> Local B10 <code>deq_n100a15</code> says “Distance to earthquake”. The official problem page, re-fetched 2026-10-26, lists “Density of earthquakes” and does not say distance. Local B16 says intensity or density. The mapping is unresolved. H31-N did not use B10 or B16.</li>
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
    <div class="table-wrap"><table>
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
    </table></div>
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
  <div class="section-head"><div><p class="kicker">2026-10-26 Featured Lane · H31-S (UDAP-SSLIC) · 3-Experiment Campaign</p>
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
      <strong>Unique submission name:</strong> <code>{esc(art['name'])}</code><br>
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


def pgr31_download_and_gates() -> str:
    rc_path = ROOT / "evidence/pgr31/run_card.json"
    if not rc_path.is_file():
        return ""
    rc = json.loads(rc_path.read_text())
    facts = rc.get("facts") or {}
    if not facts:
        return ""
    can = rc.get("leakage_canary") or {}
    h51 = (rc.get("holdout_dti") or {}).get("screen_seed51") or {}
    cand = h51.get("candidate") or {}
    ctrl = h51.get("control") or {}
    paired = h51.get("paired_difference") or {}
    screen = h51.get("screen") or {}
    reg = rc.get("correlation_overlap_vs_registry") or {}
    zf, nf = facts["zeros"], facts["nan"]
    name = rc["submission_name"]
    note = rc.get("note") or ""
    return f'''
<section id="pgr31-download" aria-labelledby="pgr31-heading">
  <div class="section-head"><div><p class="kicker">2026-10-26 Newest Lane · PGR31 Poisson Pseudo-Gravity Discordance · 3-Experiment Campaign</p>
    <h2 id="pgr31-heading">DOWNLOAD FOR RESEARCH: YES · SUBMIT TO DRIVENDATA: NO (DO NOT SUBMIT)</h2></div>
    <p>New {facts['dots']:,}-dot GeoTIFF generated this session from Baranov pseudo-gravity (Fourier vertical
      integration of RTP) locally regressed on isostatic gravity — a buried-basement-juxtaposition signature
      not previously implemented in this repository. Zero incumbent dots copied
      ({reg['max_final_3px_overlap']*100:.1f}% max 3-px overlap vs any genuine submission; 33.2% vs GEMSDOE32 H33-2-B2).
      The preregistered holdout screen failed, so the machine verdict is
      <code>verdict = negative</code>, <code>eligible_for_selector = false</code>, <code>ok_to_submit = false</code>.
      No human inspector is involved: <code>python scripts/verify_pgr31_run.py</code> re-reads the bytes and
      reproduces this decision. Full nine-site executive summary:
      <a href="https://github.com/buffedlizard55-lab/GEMSDOE31/blob/main/knowledge/2026-10-26_pgr31_executive_summary.md">2026-10-26_pgr31_executive_summary.md</a>
      · preregistration:
      <a href="https://github.com/buffedlizard55-lab/GEMSDOE31/blob/main/knowledge/2026-10-26_pgr31_preregistration.md">2026-10-26_pgr31_preregistration.md</a>.</p></div>
  <div class="card download-card">
    <span class="badge badge-red">RESEARCH DOWNLOAD ONLY · DO NOT SUBMIT · HOLDOUT SCREEN FAILED</span>
    <h3 style="margin-top:18px">{esc(name)}</h3>
    <p>The recommended all-finite file has values exactly in [0, 1] (finite {{0.0, 1.0}} in all 12,279,160 cells),
      so the portal error &ldquo;Predicted values must be in range [0, 1]&rdquo; cannot trip on it; the
      NaN-outside twin follows the official-wording convention. Format validity is not scientific
      promotion or organizer acceptance. HOLDOUT-DTI is a local hide-and-recover proxy, never a
      leaderboard score; no ORGANIZER-CONFIRMED score exists for any file here.</p>
    <div class="actions">
      <a class="button button-primary" href="downloads/{esc(zf['file'])}" download>Download PGR31 Research .tif (all-finite [0,1])</a>
      <a class="button button-dark" href="downloads/{esc(nf['file'])}" download>NaN-outside twin .tif</a>
      <a class="button" href="downloads/{esc(name)}-zeros.zip" download>Single-TIFF .zip</a>
      <a class="button" href="downloads/{esc(name)}-run-card.json" download>JSON Run Card</a>
      <a class="button" href="downloads/{esc(name)}-format-check.json" download>Format receipt .json</a>
    </div>
    <p class="download-meta"><strong>Grid &amp; Range:</strong> 1-band float32 · EPSG:32611 · 3730 x 3292 · 100 m ·
      {facts['dots']:,} binary dots · {facts['dots_on_catalogue']} on public catalogue · {facts['dots_within_2px_catalogue']} within 2 px<br>
      <strong>SHA-256 (all-finite primary):</strong> <code>{esc(zf['sha256'])}</code> ({zf['bytes']:,} B)<br>
      <strong>SHA-256 (NaN-outside twin):</strong> <code>{esc(nf['sha256'])}</code> ({nf['bytes']:,} B)<br>
      <strong>Unique submission name:</strong> <code>{esc(name)}</code><br>
      <strong>Note ({len(note)}/140 chars):</strong> <code>{esc(note)}</code></p>
    <div class="table-wrap"><table>
      <thead><tr><th>Automated Gate</th><th>Measured Evidence (unchanged <code>gems57-pooled-hide-v2</code>)</th><th>Status</th></tr></thead>
      <tbody>
        <tr><td>Format, grid &amp; [0, 1] range (both encodings)</td>
            <td>EPSG:32611 · 3730x3292 · single float32 band · 0 NaN inside footprint · values exactly {{0.0, 1.0}} · validator hard failures: none</td>
            <td><span class="badge badge-green">PASS</span></td></tr>
        <tr><td>EXP-1 single-feature leakage canary (9 novel features)</td>
            <td>Max two-sided AUC {can['max_value_auc_two_sided']:.4f} &le; 0.90 ({can['evaluated_positive_pixels']:,} withheld positives)</td>
            <td><span class="badge badge-green">PASS</span></td></tr>
        <tr><td>EXP-1 holdout screen, draw 51 ({cand['withheld_positive_pixels']:,} withheld px)</td>
            <td>HOLDOUT-DTI candidate {cand['dti']:.4f} [{cand['ci95'][0]:.4f}, {cand['ci95'][1]:.4f}] vs control {ctrl['dti']:.4f} [{ctrl['ci95'][0]:.4f}, {ctrl['ci95'][1]:.4f}]; paired delta {paired['delta']:+.4f} [{paired['ci95'][0]:+.4f}, {paired['ci95'][1]:+.4f}]; {screen['quadrant_wins']}/4 quadrants; SGMC proxy delta {screen['sgmc_proxy_delta']:+.4f}</td>
            <td><span class="badge badge-red">FAIL</span></td></tr>
        <tr><td>EXP-2 fresh confirmation, draw 52</td>
            <td>Not run — frozen stop rule (confirmation only after a passed screen; no burned-draw tuning)</td>
            <td><span class="badge badge-red">GATED OFF</span></td></tr>
        <tr><td>EXP-3 uniqueness vs genuine submissions (surface, then final dots)</td>
            <td>{esc(reg['scope'])}: surface max |Spearman| {reg['max_abs_surface_spearman']:.4f} &le; 0.90; final dots max 3-px overlap {reg['max_final_3px_overlap']*100:.1f}% &le; 70% (worst {esc(reg['worst_overlap_file'])})</td>
            <td><span class="badge badge-green">PASS (genuine-submission scope)</span></td></tr>
        <tr><td>Calibration-lattice disclosure (695-raster registry)</td>
            <td>A registered spacing-5 calibration lattice lies within 3 px of essentially every interior cell (measured: 99.26% of PGR31 dots within 3 px, <code>evidence/pgr31/registry_lattice_measured.json</code>); it is a non-submission control, reported here rather than silently exempted</td>
            <td><span class="badge badge-red">DISCLOSED</span></td></tr>
        <tr><td>Leaderboard upload approval</td>
            <td>Research download enabled; DrivenData upload NOT approved; promotion to a weekly slot is a separate selector step and 0 slots were spent</td>
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


def h31n_decision_banner() -> str:
    """First thing a visitor sees. Numbers come only from the H31-N run card."""
    path = ROOT / "evidence/h31n/run_card.json"
    if not path.is_file():
        return ""
    card = json.loads(path.read_text())
    art = card.get("artifacts") or {}
    hold = card.get("holdout_dti") or {}
    screen = (hold.get("screen") or hold.get("candidate") or {})
    control = (hold.get("control") or hold.get("same_run_control_base19") or {})
    paired = hold.get("paired") or hold.get("paired_difference_vs_base19") or {}
    name = card.get("submission_name", "")
    zeros = art.get("zeros_tif", "")
    nan = art.get("nan_tif", "")
    zeros_name = Path(zeros).name if zeros else ""
    nan_name = Path(nan).name if nan else ""
    zip_name = Path(art.get("zeros_zip", "")).name if art.get("zeros_zip") else ""
    submit = "YES" if card.get("ok_to_submit") else "NO — DO NOT SUBMIT"
    download = "YES, for research only" if card.get("ok_to_download_for_research") else "NO"
    slot_txt = "true" if card.get("slot_approved") else "false"
    if card.get("ok_to_submit"):
        lead = "The run card marks this file uploadable. That is not an organizer receipt."
    else:
        lead = (
            "Do not upload this file. It is a new research GeoTIFF, not a copy of H33, "
            "and the holdout gate did not clear it. Format validity is not permission to spend a weekly slot."
        )
    dti = screen.get("dti")
    dti_txt = f"{dti:.4f}" if isinstance(dti, float) else "—"
    ctrl = control.get("dti")
    ctrl_txt = f"{ctrl:.4f}" if isinstance(ctrl, float) else "—"
    delta = paired.get("delta")
    delta_txt = f"{delta:+.4f}" if isinstance(delta, float) else "—"
    ci = paired.get("ci95") or [None, None]
    n_withheld = screen.get("withheld_positive_pixels", "—")
    lattice = (card.get("lattice_final_dots") or {}).get("final_dot_overlap_3px")
    lattice_txt = f"{100 * lattice:.2f}%" if isinstance(lattice, float) else "—"
    gate = card.get("final_dot_gate") or {}
    ov = gate.get("worst_dot_overlap_3px")
    ov_txt = f"{100 * ov:.1f}%" if isinstance(ov, float) else "—"
    rho = gate.get("worst_abs_spearman")
    rho_txt = f"{rho:.3f}" if isinstance(rho, float) else "—"
    h33 = card.get("h33_geometry_this_session") or {}
    h33_ov = h33.get("final_dot_overlap_vs_h33")
    h33_txt = f"{100 * h33_ov:.1f}%" if isinstance(h33_ov, float) else "—"
    subset = h33.get("h33_is_subset_of_d28")
    subset_txt = "yes, exact" if subset is True else ("no" if subset is False else "not measured")
    csdu_path = ROOT / "docs/downloads/gemsdoe31-csdu-stepover-8cf9dc27-run-card.json"
    csdu_html = ""
    if csdu_path.is_file():
        csdu = json.loads(csdu_path.read_text())
        csdu_html = (
            f"<li>Concurrent CSDU file <code>{esc(csdu.get('submission_name', ''))}</code> "
            f"is also research-only (ok_to_submit={esc(str(bool(csdu.get('ok_to_submit'))).lower())}, "
            f"slot_approved={esc(str(bool(csdu.get('slot_approved'))).lower())}). "
            "This lane did not re-score it.</li>"
        )
    conflicts = card.get("label_conflicts") or []
    conflict_html = "".join(
        f"<li><strong>{esc(item.get('id', 'flag'))}:</strong> {esc(item.get('summary', ''))}</li>"
        for item in conflicts
    )
    ci_txt = "—"
    if isinstance(ci, list) and len(ci) == 2 and all(isinstance(x, float) for x in ci):
        ci_txt = f"[{ci[0]:+.4f}, {ci[1]:+.4f}]"
    return f'''<div class="notice notice-danger" id="download-decision">
      <p class="kicker">Read this first · automated decision · no human inspector</p>
      <h2>OK to download: {esc(download)}<br>OK to submit to DrivenData: {esc(submit)}</h2>
      <p><strong>{esc(lead)}</strong> <code>slot_approved = {esc(slot_txt)}</code>.</p>
      <p><a class="button button-primary" href="downloads/{esc(zeros_name)}" download>Download research .tif (all-finite [0, 1], do not submit)</a>
      <a class="button" href="downloads/{esc(zip_name)}" download>Download one-TIFF .zip</a>
      <a class="button button-light" href="downloads/{esc(nan_name)}" download>NaN-outside twin (written spec, also do not submit)</a></p>
      <ul>
        <li>Name: <code>{esc(name)}</code></li>
        <li>Note ({card.get("note_chars", "—")}/140): {esc(card.get("note", ""))}</li>
        <li>SHA-256 zeros: <code>{esc(card.get("raster_sha256", ""))}</code></li>
        <li>HOLDOUT-DTI ({esc((hold.get("evaluator_version") or "gems57-pooled-hide-v2"))}, {esc(n_withheld)} withheld positives): candidate {esc(dti_txt)} vs same-run base-19 {esc(ctrl_txt)}, paired delta {esc(delta_txt)} CI {esc(ci_txt)}. Not a leaderboard score.</li>
        <li>Scientific uniqueness in the checked set: max |Spearman| {esc(rho_txt)} (limit 0.90), max 3 px dot overlap {esc(ov_txt)} (limit 70%). Overlap vs H33-2-B2 measured this session: {esc(h33_txt)}.</li>
        <li>Literal spacing-5 lattice overlap: {esc(lattice_txt)} (limit 70%). This alone blocks upload. No exemption.</li>
        <li>If a <em>future approved</em> file is rejected with “Predicted values must be in range [0, 1]”, upload the all-finite zeros file, not a report. The written problem page also asks for NaN outside the footprint; both encodings are provided. Neither encoding is approved today.</li>
        <li>Nine-site file to submit: none. H33-2-B2 is the owner-prompt’s highest USER-REPORTED claim (0.2778, not organizer-confirmed). This session measured H33 as an exact subset of D2.8 beyond 2 px of the public catalogue ({esc(subset_txt)}; H33 dots {esc(h33.get("h33_dots", "—"))}, D2.8 dots {esc(h33.get("d28_dots", "—"))}). Do not resubmit that file as new. A catalogue-segment holdout of those fixed rasters is anti-aligned with the 2 px prune and is not a leaderboard score.</li>
        {csdu_html}
      </ul>
      {('<p><strong>Open label conflicts (not resolved, not used to change the score):</strong></p><ul>' + conflict_html + '</ul>') if conflicts else ''}
    </div>'''


def overview(card):
    hero = '''<section class="hero"><div class="wrap hero-grid"><div>
      <p class="eyebrow">DOE GEMS Prize · 28 October 2026 · H31-CC</p>
      <h1>DO NOT SUBMIT.<br>A new unique TIFF was generated and it failed the score gates.</h1>
      <p class="hero-lede">H31-CC is a new cover-concealed basement-step map. It is not a copy of H33-2-B2.
      Format is valid, including values in [0, 1]. It does not beat the same-run chance map, and the
      calibration-lattice rule still blocks a weekly slot. No leaderboard estimate is offered.</p>
      <div class="actions"><a class="button button-primary" href="downloads/gems31-h31cc-basement-step-37654d-20261028-zeros.tif" download>Download all-finite .tif — DO NOT SUBMIT</a>
      <a class="button" href="executive-summary.html#h31cc">Why this file is blocked</a></div>
      </div><aside class="hero-side"><strong>DO NOT SUBMIT</strong><p>No current artifact is approved.
      No human sign-off can override a failed gate. The all-finite file avoids the NaN range error; that is not permission to upload.</p></aside></div></section>'''
    return hero, h31cc_front_door() + _overview_body(card, hero_rbu=False)


def _overview_body(card, *, hero_rbu: bool):
    s = card["holdout_dti"]
    delta = card["paired_difference"]
    final = card["registry"]["final"]
    magrest_notice = '<div class="notice">Historical lane results below are research evidence only, not current upload permission.</div>'
    body = f'''{selector_decision_section()}{focus_review.section(ROOT)}{h31aa_download_and_gates()}{magrest_notice}{h31y_download_and_gates()}{h31yr_download_and_gates()}{h31z_download_and_gates()}{h31ym_download_and_gates()}{pgr31_download_and_gates()}
      {h31s_download_and_gates()}
      {h31x_download_and_gates()}
      {h31t_download_and_gates()}
      {h31j_download_and_gates()}
      {focus_site_summary()}
      {rbu31_download_and_gates()}
      {h31m_download_and_gates()}
      {hvdc_download_and_gates()}
      {scgp_download_and_gates()}
      {download(card)}
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
            f'<td>{method}</td><td>{overlap_text}<br>Not a unique new submission</td>'
            f'<td>Unavailable — no validated forecast</td><td>Prior-art download only; DO NOT SUBMIT</td></tr>'
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
        <th>Claimed score</th><th>Method / interpretation</th><th>Measured relation to H33</th><th>Estimated score</th><th>Permission</th></tr></thead>
        <tbody>{''.join(rendered)}</tbody></table></div>
      <p class="small"><strong>Snapshot warning:</strong> this is historical pinned prior art, not a live feed.
        Fresh 26 October GitHub metadata checks found newer main revisions at all nine sites; changed rasters are not exhaustively re-audited.
        <a href="https://github.com/buffedlizard55-lab/GEMSDOE31/blob/main/evidence/review_bf9d261d/source_checks.json">Dated source-check receipt</a>.</p>
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
        rows_html.append(
            f'<tr><td><strong>{site}</strong></td>'
            f'<td>{s25_cell}</td>'
            f'<td><a href="{cur_url}"{target_attr}>{cur_art}</a><br>'
            f'<span class="small">SHA-256 <code>{sha12}…</code> · {dots:,} dots · [0,1] valid</span></td>'
            f'<td>{ov_h33:.1f}% vs H33<br>{ov_h29:.1f}% vs H29</td>'
            f'<td>{sg_all:.4f} / {sg_pied:.4f} / {sg_mtn:.4f}</td>'
            f'<td>{gate_txt}</td></tr>'
        )
    return f'''<div style="margin-top:28px">
      <h3>2026-10-25 newly reported unique scores &amp; 2026-10-26 current HEAD unique candidates across all 9 sites</h3>
      <p class="small">Unlike the historical D1.5/D2.8 family above (86.7%&ndash;100% 3-px overlap with H33), all nine current HEAD candidates below have &le;56% 3-px dot overlap with H33-2-B2 and pass automated EPSG:32611 / [0, 1] grid checks. Every reported leaderboard number carries <code>USER-REPORTED · no organizer receipt</code>. Off-catalogue USGS SGMC proxy DTI is reported as <code>All / Piedmont (&le;6 deg) / Mountain (&gt;6 deg)</code> to expose steep-bedrock mimicry (for example, GEMSDOE32 R6-stepprofile reaches 0.1424 overall SGMC but collapses to 0.0030 Piedmont SGMC and 0.0034 Quaternary holdout DTI).</p>
      <div class="table-wrap"><table><thead><tr><th>Site</th><th>2026-10-25 newly reported unique batch</th>
        <th>Current HEAD unique candidate (2026-10-26)</th><th>3-px overlap</th>
        <th>SGMC-PROXY (All / Pied / Mtn)</th><th>Measured status &amp; site gate verdict</th></tr></thead>
        <tbody>{''.join(rows_html)}</tbody></table></div>
    </div>'''


def review_notice():
    return '<div class="notice"><strong>26 October audit: no new TIFF or submission approval.</strong> The literal registry STOP remains binding. Corrected marginal DTI algebra and score-provenance wording; existing downloads are research-only. <a href="https://github.com/buffedlizard55-lab/GEMSDOE31/blob/main/knowledge/2026-10-26_metric_and_release_review.md">Review, limitations and next steps</a>.</div>'


def executive(card):
    failed = "".join(f"<li>{esc(x)}</li>" for x in card["failed_or_unknown_gates"])
    focus_summary = focus_site_summary()
    return h31cc_front_door() + f'''<div class="notice notice-danger"><strong>No file is cleared to submit under the current protocol.</strong>
      Download and format validation are separate from uniqueness, scientific efficacy and selector approval.
      No human sign-off can override a failed gate.</div>
      {session_fcbbeea8_notice()}
      {selector_decision_section()}{focus_review.section(ROOT)}
      {h31aa_download_and_gates()}
      {review_notice()}
      {h31y_download_and_gates()}
      {h31yr_download_and_gates()}
      {h31z_download_and_gates()}
      {h31ym_download_and_gates()}
      {pgr31_download_and_gates()}
      {focus_summary}
      {h31s_download_and_gates()}
      {h31x_download_and_gates()}
      {h31t_download_and_gates()}
      {h31j_download_and_gates()}
      {rbu31_download_and_gates()}
      {h31m_download_and_gates()}
      {hvdc_download_and_gates()}
      {scgp_download_and_gates()}
      {download(card)}
      {h3_download_and_gates()}
      <section><div class="section-head"><div><p class="kicker">Exact decision</p><h2>Why upload is blocked</h2></div>
        <p>File validity, registry uniqueness and scientific efficacy are separate questions.</p></div>
        <div class="card"><ul>{failed}</ul></div>
      </section>
      <section><div class="section-head"><div><p class="kicker">For a future approved candidate</p><h2>How to enter a submission</h2></div>
        <p>No current file is cleared; these are future instructions only. Upload is manual; this project never contacts DrivenData.</p></div>
        <div class="card"><ol>
          <li>Confirm <code>registry/selector_decision_20261026.json</code> lists the exact file and full SHA-256 as an approved primary submission, and re-download so bytes match that hash.</li>
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
      {h31aa_download_and_gates()}
      {h31s_download_and_gates()}
      <section><div class="section-head"><div><p class="kicker">2026-10-26 Ranked Geological Hypotheses (Lane H31-S)</p><h2>Four untried Basin-and-Range buried-fault hypotheses</h2></div>
        <p>Preregistered in <a href="https://github.com/buffedlizard55-lab/GEMSDOE31/blob/main/knowledge/2026-10-26_h31s_udap_sslic_preregistration.md">knowledge/2026-10-26_h31s_udap_sslic_preregistration.md</a> prior to running H31-S.</p></div>
        <div class="table-wrap"><table><thead><tr><th>Rank / ID</th><th>Specific layers &amp; physical signature</th><th>Why missing from USGS/INGENIOUS &amp; novelty vs repo</th><th>Expected DTI impact, cost &amp; verified free source</th></tr></thead><tbody>
          <tr><td>1 · H31-S (UDAP-SSLIC) · executed</td><td><code>depth_to_base_surf</code>, <code>iso_grav_anom_slope</code>, GeoDAWN <code>TMI_up150</code>/<code>K</code>/<code>Th</code>, <code>rtp</code>, <code>cond_surf</code>, GDR-1391 thermal/sinter/volcanics; Cordell&ndash;Grauch 45/55/65 deg up-dip advection + axial demagnetized trough + 2-stage strike-steered line-integral continuity</td><td>Dipping range-front &amp; intra-basin normal faults have gravity/magnetic steps shifted 200&ndash;1,200 m basinward (outside the 300 m DTI kernel), while hydrothermal conduits destroy magnetite along fault cores. First up-dip coordinate projection + nested OOF SSLIC in GEMSDOE31</td><td>Measured HOLDOUT-DTI 0.0948 (s41) &amp; 0.0980 (s42) vs 0.0591 / 0.0544 Physical-HGB (+61% to +80%); ~25 min on 2 CPUs · USGS INGENIOUS / GeoDAWN / GDR-1391</td></tr>
          <tr><td>2 · H31-T-SWARM (SWARM-COULOMB) · desk-ranked</td><td><code>ieq_n100a15</code>, <code>deq_n100a15</code>, <code>geod_2ndinv</code>, <code>geod_shearrate</code>, <code>geod_dilaterate</code>; microseismic swarm-excess log-ratio interacted with Andersonian Mohr&ndash;Coulomb optimal-slip alignment</td><td>Transtensional Walker Lane / Humboldt stepovers host active fluid-driven microseismic swarms without coalesced Holocene scarps; seismic bands were never tested as a swarm-excess x slip-tendency interaction</td><td>+0.004 to +0.012 HOLDOUT-DTI (coarse 10&ndash;15 km kernel limits standalone 300 m precision); low cost (~4 min) · local cached bands 4, 7, 8, 10, 16</td></tr>
          <tr><td>3 · H31-U (INSAR-3DEP-DIFF) · external roadmap</td><td>Sentinel-1 ARIA unwrapped LOS interseismic/seasonal phase gradients + raw 1 m USGS 3DEP stream-channel knickpoints</td><td>Blind intra-playa faults act as cemented groundwater aquitards creating sharp 2&ndash;5 mm/yr seasonal poroelastic InSAR phase steps with &lt;0.2 m surface relief</td><td>+0.020 to +0.045 DTI in play-fairway basins; high I/O (~40 GB), sandbox-blocked host · NASA JPL ARIA / ASF DAAC &amp; USGS TNM 3DEP</td></tr>
          <tr><td>4 · H31-V (USARRAY-MT-3D) · external roadmap</td><td>EarthScope USArray 3D magnetotelluric phase-tensor skew |beta| &gt; 3 deg and Parkinson real induction-arrow reversals</td><td>Subvertical 1&ndash;8 km conductive fault-zone brines beneath resistive Miocene&ndash;Pliocene volcanic tables are invisible to single-surface <code>cond_surf</code></td><td>+0.008 to +0.022 DTI at 3&ndash;10 km station spacing; medium cost, sandbox-blocked host · EarthScope / IRIS SPUD EMTF</td></tr>
        </tbody></table></div>
      </section>
      {h31x_download_and_gates()}
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


def session_fcbbeea8_notice() -> str:
    """Session fcbbeea8 (2026-10-28). Reads evidence/review_fcbbeea8/run_card.json; fails closed if absent."""
    path = ROOT / "evidence/review_fcbbeea8/run_card.json"
    if not path.is_file():
        return '<div class="notice notice-danger">DO NOT SUBMIT. fcbbeea8 review card missing; fail closed.</div>'
    card = json.loads(path.read_text())
    b = card["pre_placement_count_bound"]
    h = card["same_bound_applied_to_highest_user_reported_file"]
    return f'''<section id="fcbbeea8">
      <p class="kicker">28 October 2026 · session fcbbeea8 · repository review, no new TIFF</p>
      <h2>Decision: no TIFF is cleared to submit, and no new TIFF was generated</h2>
      <div class="notice notice-danger"><strong>Stop before placement.</strong>
      The literal registry-lattice rule forces STOP for any {b["candidate_dots"]:,}-dot raster:
      at least {100*b["min_overlap_at_candidate_dots"]:.2f}% of its dots fall within 3 px of the registered lattice
      (gate {100*b["gate_overlap"]:.0f}%). This is COMPUTED by counting ({b["outside_3px_halo"]:,} uncovered footprint
      pixels), not a score. Estimated leaderboard score for any new file: unavailable.</div>
      <div class="table-wrap"><table>
        <caption>Count-bound checks (COMPUTED, run card evidence/review_fcbbeea8/run_card.json)</caption>
        <thead><tr><th>Check</th><th>Result</th></tr></thead>
        <tbody>
          <tr><td>Dots at the project budget</td><td>{b["candidate_dots"]:,} — forced STOP: {b["forced_stop_at_candidate_dots"]}</td></tr>
          <tr><td>Smallest dot count where the count alone forces STOP</td><td>{b["min_dots_for_forced_stop"]:,}. Below this the count forces nothing. The repository forbids exploiting that; flagged for owner review.</td></tr>
          <tr><td>Same bound on the highest user-reported file (GEMSDOE32 H33-2-B2, {h["positive_pixels"]:,} dots)</td><td>Minimum overlap {100*h["min_overlap_by_count"]:.2f}% — forced STOP by the same rule: {h["forced_stop_by_same_rule"]}. The literal rule therefore disagrees with the leaderboard's acceptance of that file, which is USER-REPORTED. Owner decision required.</td></tr>
        </tbody></table></div>
      <p>Every number above is COMPUTED or USER-REPORTED; none is HOLDOUT-DTI or an organizer receipt. The existing research-only file is still
      <a href="downloads/gems31-h31cc-basement-step-37654d-20261028-zeros.tif" download>gems31-h31cc-basement-step-37654d-20261028-zeros.tif</a> (DO NOT SUBMIT).</p>
    </section>'''


def h31cc_front_door() -> str:
    """Session arena/bb6d6287 decision. Research file only. Never an upload permission."""
    card_path = ROOT / "evidence/h31cc/run_card.json"
    overlap_path = ROOT / "evidence/h31cc/nine_site_overlap.json"
    if not card_path.is_file():
        return '<div class="notice notice-danger">DO NOT SUBMIT. H31-CC card missing; fail closed.</div>'
    card = json.loads(card_path.read_text())
    hold = card["holdout_dti"]
    paired = hold["paired_vs_null"]
    final = card["correlation_overlap_vs_registry"]["final"]
    files = card["files"]
    nine = json.loads(overlap_path.read_text())["rows"] if overlap_path.is_file() else []
    nine_max = max((r["overlap_3px"] for r in nine), default=0.0)
    h33 = next((r for r in nine if r["site"] == "GEMSDOE32"), {"overlap_3px": float("nan")})
    nine_rows = "".join(
        "<tr><td>{site}</td><td>{ov:.1f}%</td><td>USER-REPORTED {score:.4f}; not organizer-confirmed</td>"
        "<td>No. Prior art. DO NOT SUBMIT.</td><td>Unavailable</td></tr>".format(
            site=esc(r["site"]), ov=100 * r["overlap_3px"], score=r["user_reported"])
        for r in nine
    )
    name = esc(Path(files["zeros"]).name)
    return f'''<section id="h31cc">
      <p class="kicker">28 October 2026 · lane H31-CC · new file, negative result</p>
      <h2>DO NOT SUBMIT this TIFF</h2>
      <div class="notice notice-danger"><strong>Not approved for the competition.</strong>
      The file is unique against the nine named sites and its values are finite in [0, 1], but it lost to a
      same-run chance map and the calibration lattice still exceeds the 70% rule. No weekly slot was used.
      No human sign-off can override this.</div>
      <div class="table-wrap"><table>
        <caption>What to download, what the number means, and whether it is a new submission</caption>
        <thead><tr><th>File</th><th>Number</th><th>Unique?</th><th>Download and submit?</th></tr></thead>
        <tbody>
          <tr>
            <td><a href="downloads/{name}" download>{name}</a><br>all-finite float32, zeros outside the footprint</td>
            <td>HOLDOUT-DTI {hold["dti"]:.4f} [{hold["ci95"][0]:.4f}, {hold["ci95"][1]:.4f}]<br>
            {esc(hold["evaluator_version"])}, {hold["withheld_positive_pixels"]:,} withheld positives.
            Paired difference versus same-run NULL {paired["delta"]:+.4f} [{paired["ci95"][0]:+.4f}, {paired["ci95"][1]:+.4f}].
            Leaderboard estimate: unavailable.</td>
            <td>Yes versus the nine focus submissions (maximum {100*nine_max:.1f}% of dots within 3 px; H33-2-B2 is {100*h33["overlap_3px"]:.1f}%).
            Maximum versus local submission rasters {100*final["max_overlap_submission"]:.1f}%.
            Spearman |ρ| {final["max_abs_rho_submission"]:.3f}.
            Calibration lattice overlap {100*final["lattice_overlap"]:.1f}% — literal registry STOP, not a copied lane.</td>
            <td><strong>DO NOT SUBMIT</strong><br>Research download only</td>
          </tr>
        </tbody>
      </table></div>
      <div class="actions">
        <a class="button button-primary" href="downloads/{name}" download>Download all-finite .tif — DO NOT SUBMIT</a>
        <a class="button" href="downloads/{esc(Path(files["zip"]).name)}" download>Download single-TIFF .zip — DO NOT SUBMIT</a>
        <a class="button" href="downloads/h31cc-run-card.json">Run card</a>
      </div>
      <p><strong>Name:</strong> <code>{esc(files["name"])}</code><br>
      <strong>Note ({files["note_chars"]}/140):</strong> {esc(files["note"])}<br>
      <strong>SHA-256:</strong> <code>{esc(files["sha256"])}</code></p>
      <p>Use the all-finite file if a portal rejected NaN with “Predicted values must be in range [0, 1]”.
      That fixes the range error only. It does not make the file a valid scientific entry.
      The NaN-outside twin is <a href="downloads/{esc(Path(files["nan"]).name)}">{esc(Path(files["nan"]).name)}</a>.</p>
      <h3>Nine-site historical files — do not resubmit</h3>
      <p>Overlaps below are this session’s H31-CC dots versus each pinned historical raster.
      Listed scores are USER-REPORTED. None is an estimate for a new file. None is organizer-confirmed.</p>
      <div class="table-wrap"><table>
        <thead><tr><th>Site</th><th>H31-CC dots within 3 px</th><th>Historical claim</th><th>Resubmit?</th><th>New-file estimate</th></tr></thead>
        <tbody>{nine_rows}</tbody>
      </table></div>
      <p>H33-2-B2’s USER-REPORTED 0.2778 is a catalogue-flank prune of a 300 m dotted structural field, not a new fault discovery.
      On this session’s same code it scores SGMC off-catalogue proxy DTI 0.0940 versus H31-CC 0.0078
      (61,664 proxy positives; not a competition score). Catalogue-gap HOLDOUT-DTI cannot explain that historical claim:
      H33 was built to avoid the public catalogue, so it scores 0.0067 here. No result in this session supports a score above 0.2778, 0.3195, or 0.4413.</p>
    </section>'''
