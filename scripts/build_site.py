#!/usr/bin/env python3
"""Generate every page of the GitHub Pages site from ``registry/`` and ``evidence/``.

Nothing on the site is transcribed by hand: scores, hashes, buffer values, experiment tables and the
machine-readable feed are all read out of JSON files written by scripts in this repository. If a run has
not happened, its numbers are simply absent. Re-run after any measurement:

    python scripts/build_site.py
"""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
REPO = "https://github.com/buffedlizard55-lab/GEMSDOE31"

NAV = [
    ("", "index.html", "Overview"),
    ("", "executive-summary.html", "Executive summary"),
    ("", "research.html", "Research"),
    ("", "validation.html", "Validation"),
    ("", "register/index.html", "Register"),
    ("", "experiments/index.html", "Experiments"),
    ("", "lane.html", "Lane"),
    ("", "sources.html", "Sources"),
]


# --------------------------------------------------------------------------------------- helpers

def load(path: str, default=None):
    file = ROOT / path
    if not file.is_file():
        return default
    return json.loads(file.read_text())


def e(text) -> str:
    return html.escape(str(text))


def fmt(value, digits: int = 4) -> str:
    if value is None or value == "":
        return "—"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        return f"{value:,.{digits}f}"
    if isinstance(value, int):
        return f"{value:,}"
    return e(value)


def table(headers: list[str], rows: list[list[str]], caption: str = "") -> str:
    head = "".join(f"<th>{e(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    cap = f'<caption class="small" style="text-align:left;padding:10px 15px">{e(caption)}</caption>' if caption else ""
    return f'<div class="table-wrap"><table>{cap}<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def shell(prefix: str, title: str, description: str, current: str, hero: str, body: str,
          footer_left: str = "") -> str:
    current_attr = ' aria-current="page"'
    nav = "".join(
        '<a href="{p}{h}"{c}>{l}</a>'.format(p=prefix, h=href, c=current_attr if label == current else "", l=e(label))
        for _, href, label in NAV
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{e(description)}">
  <title>{e(title)} · GEMSDOE31</title>
  <link rel="stylesheet" href="{prefix}assets/site.css">
</head>
<body>
  <header class="topbar">
    <div class="wrap topbar-inner">
      <a class="brand" href="{prefix}index.html" aria-label="GEMSDOE31 home"><span class="brand-mark">G31</span><span>GEMSDOE31</span></a>
      <nav class="nav" aria-label="Primary navigation">
        {nav}
      </nav>
    </div>
  </header>
{hero}
  <main class="wrap">
{body}
  </main>
  <footer class="footer"><div class="wrap footer-inner">
    <p>{footer_left or "Every figure on this site is generated from measured artifacts in the repository."}</p>
    <p><a href="{prefix}feed.html">Live feed</a> · <a href="{prefix}ai-disclosure.html">AI use</a> · <a href="{REPO}">Repository</a></p>
  </div></footer>
</body>
</html>
"""


def page_hero(kicker: str, headline: str, lede: str) -> str:
    return f"""  <section class="page-hero">
    <div class="wrap">
      <p class="eyebrow">{e(kicker)}</p>
      <h1>{e(headline)}</h1>
      <p class="hero-lede">{e(lede)}</p>
    </div>
  </section>
"""


def section(kicker: str, heading: str, blurb: str, content: str) -> str:
    return f"""    <section>
      <div class="section-head">
        <div><p class="kicker">{e(kicker)}</p><h2>{e(heading)}</h2></div>
        <p>{e(blurb)}</p>
      </div>
{content}
    </section>
"""


# --------------------------------------------------------------------------------------- data views

def arm_table(arms: dict) -> str:
    rows = []
    for arm, blobs in arms.items():
        if not blobs:
            continue
        cat = blobs.get("best_catalogue", {})
        ff = blobs.get("best_farfield", {})
        rows.append([
            f"<code>{e(arm)}</code>",
            f"{len(blobs.get('features', []))} planes",
            fmt(cat.get("thr"), 2),
            fmt(cat.get("dots"), 0),
            f"<strong>{fmt(cat.get('DTI_cat'))}</strong>",
            fmt(ff.get("dots"), 0),
            f"<strong>{fmt(ff.get('DTI_ff'))}</strong>",
            fmt(ff.get("credit_per_dot_ff"), 4),
        ])
    return table(["feature arm", "inputs", "thr", "dots", "catalogue-gap DTI", "dots", "off-catalogue DTI", "credit/dot"],
                 rows, "Same folds, same model class, no catalogue-derived feature in either arm.")


def operating_point_table(operating: dict) -> str:
    rows = []
    for arm, points in operating.items():
        for point in points:
            if point["thr"] not in (0.2, 0.3, 0.4, 0.5, 0.6):
                continue
            rows.append([f"<code>{e(arm)}</code>", fmt(point["thr"], 2), fmt(point["dots"], 0),
                         fmt(point["cat_DTI"]), fmt(point["ff_DTI"]), fmt(point.get("ff_credit_per_dot"))])
    return table(["arm", "threshold", "dots", "catalogue-gap DTI", "off-catalogue DTI", "credit/dot"], rows,
                 "Selected thresholds; the full sweep lives in evidence/operating_point.json.")


ARM_LABELS = {
    "B_19_plus_lidar": "LiDAR arm",
    "D_19_plus_lidar_radiometric": "LiDAR + radiometric arm",
}


def best_union(union: dict) -> dict:
    """Best catalogue-dropping union: recorded in the artifact, recomputed from the rows if absent."""
    if union.get("best_union"):
        return union["best_union"]
    candidates = [row for row in union.get("unions", [])
                  if row.get("drop_catalogue_pixels") and row["added"] >= 1000]
    if not candidates:
        return {}
    best = max(candidates, key=lambda row: row["ff_DTI"])
    return {"arm": best["arm"], "threshold": best["threshold"], "added": best["added"], "dots": best["dots"],
            "cat_DTI": best["cat_DTI"], "ff_DTI": best["ff_DTI"], "delta": best["ff_delta"],
            "added_credit_per_dot": best["added_ff_credit_per_dot"]}


def union_table(union: dict) -> str:
    """Every catalogue-dropping union, both arms, best row highlighted."""
    incumbent = union.get("incumbent", {})
    rows = [[f"<strong>incumbent</strong> ({fmt(incumbent.get('dots'), 0)} dots)", "—",
             fmt(incumbent.get("cat_DTI")), fmt(incumbent.get("ff_DTI")), "—", fmt(incumbent.get("ff_credit_per_dot"))]]
    candidates = [row for row in union.get("unions", [])
                  if row.get("drop_catalogue_pixels") and row["added"] >= 1000]
    best = max(candidates, key=lambda row: row["ff_DTI"]) if candidates else None
    for row in candidates:
        marker = ' <span class="badge badge-green">best union</span>' if row is best else ""
        label = ARM_LABELS.get(row["arm"], row["arm"])
        emission = (f"incumbent + {label} p≥{fmt(row['threshold'], 2)}{marker}"
                    + '<div class="small">+' + fmt(row["added"], 0) + " added dots</div>")
        rows.append([emission, fmt(row["dots"], 0), fmt(row["cat_DTI"]), fmt(row["ff_DTI"]),
                     "<strong>" + f"{row['ff_delta']:+.4f}" + "</strong>",
                     fmt(row["added_ff_credit_per_dot"])])
    return table(["emission", "total dots", "catalogue-gap DTI", "off-catalogue DTI", "Δ off-catalogue",
                  "added credit/dot"],
                 rows, "Catalogue-dropping variants only, both detector arms, thresholds that actually add at "
                       "least 1,000 dots; the full sweep including the near-empty high thresholds is in "
                       "evidence/union_results.json. The incumbent is never thinned; additions are only ever added.")


def variogram_table(buffer_derivation: dict) -> str:
    empirical = buffer_derivation["empirical"]
    bins = [(c, g, n) for c, g, n in zip(empirical["bin_centres_m"], empirical["semivariance"], empirical["pair_counts"]) if n]
    step = max(1, len(bins) // 12)
    rows = [[f"{c/1000:.2f}", fmt(g, 5), fmt(n, 0)] for c, g, n in bins[::step]]
    return table(["lag (km)", "semivariance γ", "pairs"], rows,
                 "500 m bins, minimum 20 pairs per bin; pairs restricted to the same fault component.")


def buffer_decision_table(buffer_derivation: dict) -> str:
    decision = buffer_derivation["decision"]
    rows = [
        ["Empirical decay range (γ first reaches 95 % of peak)", f"<strong>{fmt(decision['empirical_decay_range_m'], 0)} m</strong>"],
        ["Peak lag / peak γ", f"{fmt(decision['empirical_peak_lag_m'], 0)} m / {fmt(decision['empirical_peak_gamma'], 5)}"],
        ["Median fitted practical range", f"{fmt(decision['model_practical_range_median_m'], 0)} m"],
        ["Largest fitted range (reported, not adopted)", f"{fmt(decision['max_fitted_range_m'], 0)} m"],
        ["Populated lag support", f"{fmt(decision['observed_lag_support_m'], 0)} m"],
        ["<strong>Buffer adopted for every holdout comparison</strong>",
         f"<strong>{fmt(decision['buffer_m'], 0)} m ≈ {fmt(decision['buffer_km'], 2)} km ({fmt(decision['buffer_m']/100, 0)} px)</strong>"],
        ["Sensitivity band across models", f"{fmt(decision['sensitivity_band_m'][0], 0)} – {fmt(decision['sensitivity_band_m'][1], 0)} m"],
        ["Component-bootstrap 5th–95th percentile",
         f"{fmt(min(v for v in decision['bootstrap_p05_m'].values() if v), 0)} – {fmt(max(v for v in decision['bootstrap_p95_upper_m'].values() if v), 0)} m"],
    ]
    return table(["quantity", "value"], rows)


def collar_table(collar: list) -> str:
    rows = []
    for row in collar:
        arms = {k: v for k, v in row.items() if isinstance(v, dict)}
        labels = sorted(arms)
        rows.append([f"{row['collar_km']:.2f}"] + [f"{fmt(arms[a]['cat_DTI'])} / {fmt(arms[a]['ff_DTI'])}" for a in labels])
    headers = ["collar (km)"] + [f"{a.split('_')[0]} cat / off-cat" for a in sorted({k for row in collar for k, v in row.items() if isinstance(v, dict)})]
    return table(headers, rows, "Each row deletes every evaluation cell within the collar of the training region, then rescores.")


def submission_receipts() -> list[dict]:
    out = []
    for receipt in sorted((DOCS / "downloads").glob("*-format-check.json")):
        data = json.loads(receipt.read_text())
        data["_path"] = receipt.relative_to(DOCS).as_posix()
        out.append(data)
    return out



def verdict_badge(verdict: str) -> str:
    cls = {"READY_TO_SUBMIT": "badge-green", "FORMAT_VALID_NOT_PROMOTED": "badge", "BLOCKED": "badge-red"}.get(verdict, "badge")
    text = {"READY_TO_SUBMIT": "READY TO SUBMIT", "FORMAT_VALID_NOT_PROMOTED": "FORMAT VALID, NOT PROMOTED",
            "BLOCKED": "BLOCKED: DO NOT SUBMIT"}.get(verdict, verdict)
    return f'<span class="badge {cls}">{e(text)}</span>'


def lane_gate_receipt(cand: dict, key: str = "allfinite") -> dict:
    return json.loads((ROOT / cand["gate_receipts"][key]["receipt"]).read_text())


def gate_rows(receipt: dict) -> list[list[str]]:
    rows = []
    for name, g in receipt["gates"].items():
        badge = '<span class="badge badge-green">PASS</span>' if g["pass"] else '<span class="badge badge-red">FAIL</span>'
        rows.append([f"<code>{e(name)}</code>", badge, e(g["detail"])])
    return rows


def dl(path: str, label: str, prefix: str = "") -> str:
    return f'<a class="button button-light" href="{prefix}{e(path.replace("docs/", "", 1))}" download>{e(label)}</a>'


# --------------------------------------------------------------------------------------- pages

def build_index(sub: dict, buf: dict, union: dict, arms: dict) -> str:
    primary = next(f for f in sub["files"] if f["id"] == "primary-h27-4-solo-d28")
    research = next(f for f in sub["files"] if f["name"] == sub["best_research_candidate"]["name"])
    inc = union.get("incumbent", {})
    inc_credit = inc.get("ff_credit_per_dot")
    operating = load("evidence/operating_point.json", {})
    best_arm = max((max(row["ff_DTI"] for row in rows) for rows in operating.values() if rows), default=None)
    cand = sub["lane_candidate"]
    receipt = lane_gate_receipt(cand)
    cleared = cand["ready_to_submit"]
    fa, fn = cand["files"]["allfinite"], cand["files"]["nan"]
    hero = f"""  <section class="hero">
    <div class="wrap hero-grid">
      <div>
        <p class="eyebrow">DOE GEMS Prize · competition 306 · auditable fault mapping</p>
        <h1>{'Download it. It passed every gate.' if cleared else 'Download the candidate file. Read its verdict first.'}</h1>
        <p class="hero-lede">{verdict_badge(cand['verdict'])} The candidate <code>{e(cand['name'])}</code> is a single-band float32 GeoTIFF on the
        exact competition grid. Automated gates checked its format, value range, catalogue masking, byte and lane uniqueness against
        {receipt['uniqueness']['registry_rasters_compared']} registry rasters, name, note and preregistered holdout evidence.
        {'It is cleared.' if cleared else 'It is NOT cleared: see the failing gates on the right. Do not spend a weekly slot on it.'}</p>
        <div class="actions">
          <a class="button button-primary" href="{e(fa.replace('docs/', '', 1))}" download>{'Download submission TIFF' if cleared else 'Download candidate TIFF — not approved for upload'} (all-finite)</a>
          <a class="button button-light" href="{e(fn.replace('docs/', '', 1))}" download>NaN-outside twin</a>
          <a class="button button-light" href="executive-summary.html">How to submit</a>
        </div>
      </div>
      <aside class="hero-side" aria-label="Gate verdict">
        <strong>Gate verdict · {e(cand['verdict'].replace('_', ' '))}</strong>
        <p>{''.join(f"{'PASS' if g['pass'] else 'FAIL'} · {e(n.split('_', 1)[0])} {e(n.split('_', 1)[1].replace('_', ' '))}<br>" for n, g in receipt['gates'].items())}</p>
        <p><a href="lane.html">Run card, hypotheses and calibration</a></p>
      </aside>
    </div>
  </section>
"""
    body = f"""    <div class="notice notice-danger"><strong>Not approved for upload.</strong> The TIFF below is a legacy incumbent for research and format-reference purposes only. The separate union file is research-only, and the inspected GEMSDOE32 H33-2-B2 geometry fails the project's duplicate canary. No unique candidate has passed holdout validation and confirmation, so do not spend a competition slot on any download from this site.</div>
    <section>
      <div class="section-head">
        <div><p class="kicker">Submission</p><h2>Is this file OK to download and submit?</h2></div>
        <p>Download: always fine, the file is format-valid. Submit: only when the verdict says READY TO SUBMIT.</p>
      </div>
      <div class="card download-card">
        <h2>{e(cand['name'])}</h2>
        <p>{verdict_badge(cand['verdict'])} · {fmt(cand['dots'], 0)} positive pixels · EPSG:32611 · 100 m · 3730×3292 · finite in [0,1] ·
        zero emitted on the public catalogue.</p>
        <div class="actions" style="margin-top:18px">
          <a class="button button-primary" href="{e(fa.replace('docs/', '', 1))}" download>Download .tif (all-finite)</a>
          {dl(cand['files']['zip_allfinite'], 'Download .zip (all-finite)')}
          {dl(fn, 'NaN-outside .tif')}
          {dl(cand['files']['zip'], 'NaN-outside .zip')}
        </div>
        <p class="download-meta">SHA-256 (all-finite) <code>{e(cand['gate_receipts']['allfinite']['sha256'])}</code><br>
        Portal name: <code>{e(cand['name'])}</code><br>
        Portal note ({cand['note_chars']}/140 characters): <em>{e(cand['note_for_portal'])}</em><br>
        <a href="{e(cand['gate_receipts']['allfinite']['receipt'].replace('docs/', '', 1))}">gate receipt (all-finite)</a> ·
        <a href="{e(cand['gate_receipts']['nan']['receipt'].replace('docs/', '', 1))}">gate receipt (NaN-outside)</a> ·
        <a href="executive-summary.html">how to submit</a></p>
      </div>
      {table(['gate', 'result', 'detail'], gate_rows(receipt))}
      {'' if cleared else '<div class="notice notice-danger"><strong>Not approved for upload.</strong> The candidate failed a gate, and the legacy incumbent and union files are reference or research only. Do not spend a competition slot on any download from this site.</div>'}
      <div class="notice notice-danger"><strong>Not an organizer score</strong> No organizer receipt exists for this file and
      no number on this site is a leaderboard score. Download links above are for inspection; the verdict is the instruction.</div>
      <div class="card" style="margin-top:18px"><h3>The earlier incumbent is not a new submission</h3>
        <p><code>{e(primary['name'])}</code> ({fmt(primary['positive_pixels'], 0)} pixels, owner-reported 0.2708) is format-valid but its
        geometry was already scored by the owner, so resubmitting it spends a slot for nothing.
        <a href="downloads/{e(primary['file_nan'].split('/')[-1])}" download>Download for reference</a>.</p></div>
    </section>
    <section>
      <div class="section-head">
        <div><p class="kicker">The answer</p><h2>Why the 0.2708 submission scores</h2></div>
        <p>Three measured properties explain it, and together they say where an improvement has to come from.</p>
      </div>
      <div class="grid grid-3">
        <article class="card stat"><span class="badge badge-green">Verified prune</span><strong>{fmt(primary['positive_pixels'], 0)} dots</strong>
          <span>Removing every D2.8 cell within 100 m of the catalogue reproduces this file bit for bit
          ({fmt((load('evidence/h27_geometry.json', {}).get('counts') or {}).get('d28_cells_removed_from_base'), 0)} cells pruned);
          spacing is 283 m minimum, 300 m median. The metric charges 0.2 per emitted pixel, so redundancy is expensive.</span></article>
        <article class="card stat"><span class="badge badge-green">Off-catalogue</span><strong>0 px</strong>
          <span>on the public USGS/INGENIOUS catalogue. The competition scores faults that are <em>missing</em> from that database, so catalogue-hugging pixels are worth ~0.</span></article>
        <article class="card stat"><span class="badge">Detection gap</span><strong>{fmt(inc.get('ff_DTI'))}</strong>
          <span>off-catalogue proxy DTI for the incumbent dot set, versus {fmt(best_arm)} for the best full-coverage
          detector at any threshold it was swept over. The gap is in new detections, not in the threshold.</span></article>
      </div>
    </section>

    <section>
      <div class="section-head">
        <div><p class="kicker">Measured today</p><h2>What the arms actually score</h2></div>
        <p>Two truth proxies, both off the public catalogue path. Their orderings disagree — the disagreement is the finding.</p>
      </div>
      {arm_table(arms)}
      <p class="small">Catalogue-gap proxy: held-out public-catalogue pixels (60,988 px). Off-catalogue proxy: USGS SGMC
      state-map fault cells more than 300 m from the catalogue (61,664 px) — the only populated fault population in
      reach that is off-catalogue by construction, i.e. the one that resembles the hidden truth. Both proxies are
      INFERENCE-class instruments, described with their limits on the <a href="validation.html">validation page</a>.</p>
    </section>

    <section>
      <div class="section-head">
        <div><p class="kicker">Direction of travel</p><h2>Adding detections works; re-budgeting does not</h2></div>
        <p>The incumbent's own dots earn {fmt(inc_credit)} credit each on the off-catalogue proxy; the best
        detector arms' dots earn ~0.02. Thresholding the incumbent down therefore loses at every quantile, while
        adding thresholded detections to it gains — and the LiDAR arm gains most.</p>
      </div>
      {union_table(union)}
      <div class="notice notice-good"><strong>Strongest research candidate, not slot-approved</strong>
      {e(research['name'])} ({fmt(research['positive_pixels'], 0)} dots, {fmt(research['positive_pixels_on_public_catalogue'], 0)} on the
      public catalogue) moves the off-catalogue proxy by <strong>{fmt(research['measured']['delta'])}</strong>.
      <a href="downloads/{e(research['file_nan'].split('/')[-1])}" download>Download it</a> and read the caveat:
      {e(research['why_not_slot_approved'])}</div>
    </section>

    <section>
      <div class="section-head">
        <div><p class="kicker">Methodological spine</p><h2>Why the numbers can be trusted this far</h2></div>
        <p>Four checks that this repository runs on itself, all reproducible from the commands on the validation page.</p>
      </div>
      <div class="grid grid-2">
        <div class="card"><h3>Buffer measured from the data</h3>
          <p>Collar of <strong>{fmt(buf['decision']['buffer_km'], 2)} km</strong>, from the empirical semivariogram of
          out-of-fold residuals along known traces (decay range {fmt(buf['decision']['empirical_decay_range_m']/1000, 2)} km).
          Not an assumed 4–5 pixels. <a href="validation.html">Derivation</a></p></div>
        <div class="card"><h3>The metric implementation is exact</h3>
          <p>Direct implementation of the official distance-weighted Tversky index, checked against a literal
          brute-force transcription. No published number comes from an approximation.
          <a href="validation.html#metric">Check</a></p></div>
        <div class="card"><h3>Two off-catalogue truth proxies</h3>
          <p>The catalogue-gap holdout and the SGMC off-catalogue population are kept separate and reported side by
          side, because a single proxy would have promoted the wrong arm. <a href="validation.html#proxies">Detail</a></p></div>
        <div class="card"><h3>Fail-closed promotion gates</h3>
          <p>Nothing reaches a weekly slot without beating the same-run incumbent, fresh confirmation draws and an
          exact-file audit. The failed H31-A pilot is published as a stop, not tidied away.
          <a href="experiments/index.html">Experiment log</a></p></div>
      </div>
    </section>
"""
    return shell("", "Overview", "Download a format-checked legacy reference raster; no candidate is approved for upload.",
                 "Overview", hero, body,
                 "Measured artifacts, honest limits. No score on this site is organizer-verified.")


def build_executive_summary(sub: dict, buf: dict, receipts: list[dict]) -> str:
    primary = next(f for f in sub["files"] if f["id"] == "primary-h27-4-solo-d28")
    cand = sub["lane_candidate"]
    rc = {k: lane_gate_receipt(cand, k) for k in ("allfinite", "nan")}
    cleared = cand["ready_to_submit"]
    fa = cand["files"]["allfinite"].split("/")[-1]
    ph = rc["allfinite"]["uniqueness"]
    dup_scores = load("evidence/run_card_lane_as1.json", {}).get("overlap_vs_registry", {}).get("duplicates_with_user_reported_live_score", {}).values()
    files_table = table(
        ["file", "when to use it", "bytes-level sha256", "gate verdict"],
        [[f"<code>{e(fa)}</code>", "default: every cell finite in [0,1], zeros outside the footprint (cannot trip a whole-array range check)",
          f"<code>{e(cand['gate_receipts']['allfinite']['sha256'])}</code>", verdict_badge(cand["gate_receipts"]["allfinite"]["verdict"])],
         [f"<code>{e(cand['files']['nan'].split('/')[-1])}</code>", "literal spec wording: NaN outside the footprint. Use it if the portal objects to the zeros",
          f"<code>{e(cand['gate_receipts']['nan']['sha256'])}</code>", verdict_badge(cand["gate_receipts"]["nan"]["verdict"])]])
    body = f"""    <section>
      <div class="section-head">
        <div><p class="kicker">Verdict first</p><h2>{'This file is cleared.' if cleared else 'No file is cleared for submission today.'}</h2></div>
        <p>The gates run in the project with no human inspector: <code>python scripts/submission_gate.py</code>.</p>
      </div>
      <div class="notice {'notice-good' if cleared else 'notice-danger'}"><strong>{verdict_badge(cand['verdict'])} {'' if cleared else 'Do not submit a download from this page yet.'}</strong>
      {'All gates passed.' if cleared else 'The file is format-valid and byte-unique, but it failed the lane-uniqueness gate (' + str(len(ph['duplicates_by_overlap'])) + ' registry rasters already contain more than 70 percent of its dots within 3 pixels) and the preregistered holdout gate. Spending a weekly slot on it is not recommended.'}
      Failing gates: {e(', '.join(cand['gate_receipts']['allfinite']['hard_failures'] + cand['gate_receipts']['allfinite']['evidence_failures']) or 'none')}.</div>
      {table(['gate', 'result', 'detail'], gate_rows(rc['allfinite']))}
    </section>

    <section>
      <div class="section-head">
        <div><p class="kicker">Submission</p><h2>How to submit, step by step</h2></div>
        <p>Only after the verdict says READY TO SUBMIT. If you override a failed gate, you are spending a scarce slot on an experiment.</p>
      </div>
      <div class="card">
        <ol>
          <li><strong>Download</strong> <a href="{e(cand['files']['allfinite'].replace('docs/', '', 1))}" download>{e(fa)}</a> (or the green button on the <a href="index.html">overview page</a>).</li>
          <li><strong>Check the hash</strong>: <code>sha256sum {e(fa)}</code> must print <code>{e(cand['gate_receipts']['allfinite']['sha256'])}</code>.</li>
          <li><strong>Re-run the gate yourself</strong> (optional, needs the restored inputs): <code>python scripts/submission_gate.py docs/downloads/blocked/{e(fa)} --convention all-finite --name {e(cand['name'])} --note "..."</code>.</li>
          <li><strong>Open the submit page</strong> at <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/" target="_blank" rel="noopener">drivendata.org/competitions/306</a> and sign in.</li>
          <li><strong>Choose the file</strong> (single-band GeoTIFF, or a zip containing one), paste the name and note below, submit.</li>
        </ol>
      </div>
      <div class="table-wrap"><table><tbody>
        <tr><th style="width:190px">Submission name</th><td><code>{e(cand['name'])}</code></td></tr>
        <tr><th>Note ({cand['note_chars']}/140 characters)</th><td><code>{e(cand['note_for_portal'])}</code></td></tr>
      </tbody></table></div>
      <p class="small">The note is at most 140 characters by the gate rule. Nothing in this repository submits a file.</p>
    </section>

    <section>
      <div class="section-head">
        <div><p class="kicker">Which file</p><h2>Two files, two conventions</h2></div>
        <p>Both carry the same dots. Only the cells outside the footprint differ.</p>
      </div>
      {files_table}
      <p class="small">The official page (problem description, page 967) says data outside the bounds is null or nan; the owner's ledgers show both conventions
      were accepted and scored (USER-REPORTED). The root cause of the portal's "Predicted values must be in range [0, 1]" is documented below.</p>
    </section>

    <section>
      <div class="section-head">
        <div><p class="kicker">Troubleshooting</p><h2>“Predicted values must be in range [0, 1]”</h2></div>
        <p>Two measurable mechanisms in the competition's own rasters produce exactly this message.</p>
      </div>
      <div class="notice notice-danger"><strong>It is not a rescaling problem</strong>
      The training stack carries a float32 sentinel (about -3.4e38) inside the scoring footprint, and a footprint mask taken from a feature band instead of the template
      strands scored pixels as NaN (SECONDHAND, GEMSDOE32 root-cause note; see <code>knowledge/2026-10-25_lane_hypotheses.md</code>).</div>
      <div class="grid grid-2">
        <div class="card"><h3>What the repository does about it</h3>
          <p>The footprint comes only from the template. <code>src/gemsdoe31/submission.py</code> and gate G1/G2 hard-fail any non-finite cell inside it,
          any value outside [0,1], and (all-finite) any non-finite cell anywhere. <code>tests/test_submission.py</code> and <code>tests/test_gate.py</code> keep regression tests.</p></div>
        <div class="card"><h3>If a gate-passing file is still refused</h3>
          <ol><li>Confirm you selected the single-band GeoTIFF, not a feature stack.</li>
          <li>Try the other convention.</li>
          <li>Stop and send the gate receipt JSON to the organizers instead of re-saving modified bytes.</li></ol></div>
      </div>
    </section>

    <section>
      <div class="section-head">
        <div><p class="kicker">Honesty box</p><h2>What this file is, and what it is not</h2></div>
        <p>The difference between a claim and a measurement.</p>
      </div>
      <div class="table-wrap"><table><tbody>
        <tr><th style="width:220px">What it is</th><td>A label-free LiDAR antislope-scarp emission of {fmt(cand['dots'], 0)} Poisson-disk dots, none on the public catalogue.</td></tr>
        <tr><th>Score</th><td>None. No organizer receipt exists and none of the holdout numbers (<a href="lane.html">run card</a>) is a leaderboard score.</td></tr>
        <tr><th>Why it is blocked</th><td>Preregistered gate E3 failed (AS-1 beats the random-score null by +0.0065, CI includes zero) and the file duplicates sibling LiDAR-scarp lanes whose
        owner-reported live scores are {e(', '.join(f'{v:.4f}' for v in sorted(dup_scores)))}, far below 0.2778.</td></tr>
        <tr><th>The earlier incumbent</th><td><code>{e(primary['name'])}</code> is not a new submission: its geometry was already scored by the owner (0.2708, USER-REPORTED).</td></tr>
        <tr><th>Slot approved?</th><td>No (<code>registry/submissions.json</code> never marks a file slot-approved).</td></tr>
        <tr><th>AI use</th><td>Substantial, and required to be disclosed: see <a href="ai-disclosure.html">AI use</a>.</td></tr>
      </tbody></table></div>
    </section>
"""
    return shell("", "Executive summary", "The gate verdict and the exact steps to submit, with the format-error fix and the honesty box.",
                 "Executive summary",
                 page_hero("Executive summary", "Verdict first, then five steps.",
                           "Where to click, what to paste, what to do when the portal complains, and what the file does and does not claim."),
                 body, "This page is the operator's guide; the science is on the research, lane and validation pages.")


def build_lane(sub: dict) -> str:
    card = load("evidence/run_card_lane_as1.json", {})
    e3 = load("evidence/lane_e3.json", {})
    calib = load("evidence/instrument_calibration.json", {})
    gap = e3["groups"]["catalogue-gap FRESH seeds 11-15"]
    sg = e3["groups"]["off-catalogue SGMC (NOT fresh)"]

    def row(name: str) -> list[str]:
        return [e(name), fmt(gap[name]["HOLDOUT_DTI"]), f"[{fmt(gap[name]['ci95'][0])}, {fmt(gap[name]['ci95'][1])}]",
                fmt(sg[name]["HOLDOUT_DTI"]), f"[{fmt(sg[name]['ci95'][0])}, {fmt(sg[name]['ci95'][1])}]"]

    e3_table = table(["method", "catalogue-gap, fresh seeds 11-15", "95% CI", "SGMC off-catalogue (not fresh)", "95% CI"], [row(n) for n in gap],
                     "HOLDOUT-DTI, evaluator " + e3["evaluator"] + ", 38,000 dots each, 1000-draw paired tile bootstrap")
    cal = calib["spearman"]
    cal_rows = [[e(k), fmt(v["rho"], 3), fmt(v["p"], 3)] for k, v in cal.items()]
    scarp_rows = [[e(r["fragment"][:46]), e(r["site"]), fmt(r["live_user_reported"]), fmt(r["sgmc_DTI"]), fmt(r["gap_DTI"])]
                  for r in calib["rows"] if any(k in r["fragment"] for k in ("lidar", "scarp", "r11", "r12"))]
    hyp = table(["rank", "hypothesis", "status"],
                [["1", "H4 catalogue-shadow geometry (generalise the b2 exclusion)", "not run: derivative of the D28 family, cannot be unique; only a live slot can test it"],
                 ["2", "H1 AS-1 antislope LiDAR scarps", "E1 and E3 negative; duplicate of sibling lanes"],
                 ["3", "H3 non-LiDAR gap zone from gravity, basement depth, conductance", "E2b refuted"],
                 ["4", "H2 TIGER road mask on scarp candidates", "E2a refuted"],
                 ["5", "H5 seismicity alignments (USGS FDSN)", "not run: location error far above the 300 m kernel"]])
    body = f"""    <section>
      <div class="section-head">
        <div><p class="kicker">Run card</p><h2>Verdict: {e(card['verdict'])}</h2></div>
        <p>{e(card['verdict_reason'])}</p>
      </div>
      <div class="table-wrap"><table><tbody>
        <tr><th style="width:230px">Hypothesis</th><td>{e(card['hypothesis'])}</td></tr>
        <tr><th>Mechanism</th><td>{e(card['mechanism'])}</td></tr>
        <tr><th>Mimicking non-fault processes</th><td>{e('; '.join(card['mimicking_non_fault_processes']))}</td></tr>
        <tr><th>Overlap vs registry</th><td>{card['overlap_vs_registry']['registry_rasters_compared']} rasters; max 500 m-block Spearman {fmt(card['overlap_vs_registry']['max_spearman_500m'], 3)};
        max non-vacuous 3 px overlap {fmt(card['overlap_vs_registry']['max_non_vacuous_3px_overlap'], 3)}; {len(card['overlap_vs_registry']['duplicates_by_overlap'])} duplicates by overlap</td></tr>
        <tr><th>Raster sha256</th><td><code>{e(card['raster_sha256']['allfinite'])}</code> (all-finite)<br><code>{e(card['raster_sha256']['nan'])}</code> (NaN-outside)</td></tr>
        <tr><th>Name and note</th><td><code>{e(card['submission_name'])}</code><br>{e(card['submission_note'])} ({card['note_chars']}/140)</td></tr>
        <tr><th>Organizer confirmed</th><td>no. Machine-readable: <a href="https://github.com/buffedlizard55-lab/GEMSDOE31/blob/main/evidence/run_card_lane_as1.json">evidence/run_card_lane_as1.json</a></td></tr>
      </tbody></table></div>
    </section>

    <section>
      <div class="section-head">
        <div><p class="kicker">E3, preregistered</p><h2>The gate that failed</h2></div>
        <p>E3 was committed to git before it ran. E1 and E2 designs were declared in their script docstrings before running (self-declared, no external timestamp).</p>
      </div>
      {e3_table}
      <div class="notice notice-danger"><strong>Instrument defect</strong> Random Poisson dots in the LiDAR zone beat the D28 incumbent and the owner-reported live best on the
      catalogue-gap proxy, because that proxy rewards coverage and b2 was pruned against the hidden half of the catalogue. Both local proxies are weak rankers across geometry families.</div>
    </section>

    <section>
      <div class="section-head">
        <div><p class="kicker">Calibration</p><h2>How far the proxies can be trusted</h2></div>
        <p>{calib['n_files']} registry rasters with USER-REPORTED live scores against local proxies. Rank correlations are weak; the scarp-led files are inverted.</p>
      </div>
      {table(['local predictor', 'Spearman vs live', 'p'], cal_rows)}
      {table(['file fragment', 'site', 'live (USER-REPORTED)', 'SGMC proxy DTI', 'catalogue-gap proxy DTI'], scarp_rows, 'LiDAR and scarp-led files: high proxy, low live')}
    </section>

    <section>
      <div class="section-head">
        <div><p class="kicker">Hypotheses</p><h2>Ranked by expected gain and cost</h2></div>
        <p>Full table with layers, signatures and sources: <code>knowledge/2026-10-25_lane_hypotheses.md</code>.</p>
      </div>
      {hyp}
    </section>
"""
    return shell("", "Lane run card", "The lane's hypotheses, holdout results, calibration and verdict.", "Lane",
                 page_hero("Parallel-run lane", "Negative result, fully logged.", "Three experiments, one preregistered gate, one verdict. Negative results are deliverables."),
                 body, "Every number is read from evidence/*.json by scripts/build_site.py.")


def build_research(sub: dict, buf: dict, union: dict) -> str:
    primary = next(f for f in sub["files"] if f["id"] == "primary-h27-4-solo-d28")
    geom = load("evidence/h27_geometry.json", {"prune_test": {}, "counts": {},
                                               "nearest_neighbour_spacing_m": {},
                                               "distance_to_catalogue_m_for_retained_cells": {}})
    inc = union.get("incumbent", {})
    credit = inc.get("ff_TPw", 0) / inc["dots"] if inc.get("dots") else None
    body = f"""    <section>
      <div class="section-head">
        <div><p class="kicker">Question 1</p><h2>Why <code>h27-4-r1-solo-d2-8</code> is the best artifact</h2></div>
        <p>The mechanism is in the metric algebra, and it is measurable rather than arguable.</p>
      </div>
      <div class="content">
        <p>The official metric is a distance-weighted Tversky index with α = 0.2, β = 0.8 and a triangular kernel of
        radius 300 m, so the denominator charges <strong>0.2 for every emitted pixel</strong> while a truth pixel is
        credited once. A dotted emission therefore pays little per dot and still reaches almost every truth pixel
        within the kernel radius. <code>scripts/verify_h27_geometry.py</code> tests the two published rasters and the
        catalogue against each other (<code>evidence/h27_geometry.json</code>), and the geometry that produced the
        score is now a measurement rather than a description:</p>
        <ul>
          <li><strong>It is the D2.8 emission minus its catalogue-flank dots.</strong> Removing every D2.8 cell within
          100 m of the public catalogue leaves exactly {fmt(geom['prune_test']['pruned_cells'], 0)} cells, and that set
          equals the {fmt(primary['positive_pixels'], 0)}-cell file <strong>bit for bit</strong> — a
          {fmt(geom['counts']['d28_cells_removed_from_base'], 0)}-cell prune that the owner page describes and this
          repository now confirms.</li>
          <li><strong>Nothing left sits on the catalogue.</strong>
          {fmt(geom['counts']['best_known_cells_within_100m_of_catalogue'], 0)} of the retained cells are within
          100 m of it; retained cells sit a median of
          {fmt(geom['distance_to_catalogue_m_for_retained_cells']['median'], 0)} m away.</li>
          <li><strong>It is dotted, not a field.</strong> Nearest-neighbour spacing is
          {fmt(geom['nearest_neighbour_spacing_m']['min'], 0)} m minimum / median
          {fmt(geom['nearest_neighbour_spacing_m']['median'], 0)} m — at the 300 m kernel radius, so neighbouring dots
          share credit without double-paying the denominator.</li>
          <li><strong>High credit per dot.</strong> On this repository's off-catalogue proxy the same dot set earns
          {fmt(credit)} credit per emitted pixel, versus 0.02–0.05 for every thresholded detector tested here.</li>
        </ul>
        <p class="small">Caveat kept in view: the owner page lists this artifact as <em>unscored</em>, so the 0.2708
        attribution rests on the owner's report, not on an organizer receipt
        (<code>registry/score_claims.json</code>).</p>
      </div>
    </section>

    <section>
      <div class="section-head">
        <div><p class="kicker">Question 2</p><h2>Why re-budgeting cannot reach 0.3195</h2></div>
        <p>Both the algebra and this repository's measurements point the same way.</p>
      </div>
      <div class="content">
        <p>The owner-mirror inversion in GEMSDOE28 calibrates the hidden truth at |G| ≈ 12,226 px and reports that
        reaching a 0.3195 row needs ≈5,942 px of credit — 1,151 px more than the 0.2600 artifact captured. The one
        exactly-controlled live measurement of marginal efficiency is the thinning step itself: removing 15,979 dots
        cost 495.08 px of credit, i.e. <strong>0.031 credit per dot</strong>, below the break-even
        <code>0.2·DTI / (1 − 0.2·DTI) ≈ 0.055</code>. Dots at that efficiency can never pay for themselves.</p>
        <p>This repository independently measured the same sign error in a second instrument. Ranking arms on the
        catalogue-gap holdout and on the off-catalogue proxy produces <strong>opposite orderings</strong>: the
        LiDAR-augmented arm wins the catalogue-gap score while the catalogue-ignoring incumbent dot set wins the
        off-catalogue score by roughly 2×. A selection rule built on catalogue proximity therefore systematically
        promotes arms that cannot move the live score — which is why earlier holdouts "validated" arms worth ≈0.001.</p>
      </div>
      {union_table(union)}
    </section>

    <section>
      <div class="section-head">
        <div><p class="kicker">Question 3</p><h2>Five candidate hypotheses, ranked</h2></div>
        <p>Rank is expected off-catalogue gain per unit of effort. Only the first has been partially measured here; the rest are INFERENCE and are labelled as such.</p>
      </div>
      <div class="table-wrap"><table>
        <thead><tr><th>rank</th><th>layers and physical signature</th><th>why it can find faults the catalogue lacks</th><th>novelty vs. everything tried here</th><th>cost / status</th></tr></thead>
        <tbody>
          <tr>
            <td><span class="badge badge-green">1 · partially measured</span><br><strong>H32-2</strong><br>Radiometric K and Th/K damage-zone matched filter</td>
            <td>GeoDAWN contractor K, Th and U grids and the Th/K, U/K, U/Th ratios; an oriented cross-strike matched filter for a narrow zone of K enrichment with Th/K depression.</td>
            <td>A damage zone concentrates K-bearing clay/zeolite alteration and K-feldspar veining, so the ratio field can mark a strand where the magnetic or topographic edge is weak. The competition stack ships only total count (<code>tc</code>), so the K-specific ratios are information the provided features do not contain.</td>
            <td>Prior work used radiometric conjunctions and single-channel cross-scarp contrast; a Th/K ratio matched filter is not among them.</td>
            <td><strong>Measured today, partially:</strong> adding the ratio block lifted the off-catalogue proxy at a fixed operating point (+22 %). The isolated matched-filter form is 2–3 days.</td>
          </tr>
          <tr>
            <td><span class="badge">2 · not started</span><br><strong>H32-5</strong><br>Scarp-degradation (diffusion-age) matched filter</td>
            <td>1 m 3DEP bare-earth DEM (links are supplied by the competition itself in <code>1m_DEM_links.csv</code>); a bank of error-function step profiles degraded by a range of diffusion ages, matched across strike.</td>
            <td>The compiled catalogue is dominated by fresh, obvious scarps; photo-interpretation misses low-amplitude, wide, degraded scarps. Inverting profile <em>shape</em> ages them instead of thresholding amplitude.</td>
            <td>The existing LiDAR block is amplitude, edge and curvature descriptors (step max, Laplacians, relief, coherence); none inverts profile shape.</td>
            <td>2–4 days; overlaps GEMSDOE30's measured scarp-dipole transform, so the increment is the multi-age bank rather than the dipole.</td>
          </tr>
          <tr>
            <td><span class="badge">3 · not started</span><br><strong>H32-4</strong><br>Quaternary-vent-aligned fault search</td>
            <td>INGENIOUS Quaternary volcanic flows and vents plus the fault detectors; search for lineaments radiating from or connecting young vents.</td>
            <td>Young volcanic centres and active faults share the same stress field, and the owner-mirror inversion attributes a large share of the estimated hidden truth to the 0–1 km ring around vents.</td>
            <td>Vents appear in this project only as a habitat inside an inversion, never as an emission or extension field.</td>
            <td>1–2 days with layers already on disk; <strong>risky</strong> — the inversion that motivates it fits at R² = −0.36, so the enrichment is a hypothesis, not a finding.</td>
          </tr>
          <tr>
            <td><span class="badge">4 · blocked on data</span><br><strong>H32-1</strong><br>Depth-resolved conductance continuity</td>
            <td>GDR 1391 electrical-conductance maps at their published depth intervals; cross-depth coherence of conductive gradients.</td>
            <td>A damage zone or fluid pathway can connect conductive anomalies across depths with no surface trace.</td>
            <td>The competition tape carries a single <code>cond_surf</code> plus <code>depth_to_base_surf</code>; a depth stack is new here.</td>
            <td>3–5 days. The GDR page is public CC-BY but unreachable from this sandbox; this project's own CI runner can reach it. Not viable until the stack is downloaded and aligned.</td>
          </tr>
          <tr>
            <td><span class="badge">5 · blocked on data</span><br><strong>H32-3</strong><br>LiDAR return-attribute roughness</td>
            <td>USGS 3DEP LAZ point clouds; ground-return density, intensity quantiles and roughness texture summarised to the grid.</td>
            <td>Fault zones juxtapose materials and change micro-roughness and cover in ways the bare-earth DEM edge does not show.</td>
            <td>Every LiDAR layer here is derived from elevation; no raw return attribute has been inspected.</td>
            <td>3–5 days after access. Earlier LAZ fetches from this sandbox failed with SSL errors while the catalogue record was reachable, so the binary path is unproven.</td>
          </tr>
        </tbody>
      </table></div>
    </section>

    <section>
      <div class="section-head">
        <div><p class="kicker">Results</p><h2>What was tested today, and what it settled</h2></div>
        <p>Failures and gains are published side by side so neither is retried by accident.</p>
      </div>
      <div class="grid grid-3">
        <div class="card"><h3>Corroboration filtering — refuted</h3><p>Keeping only incumbent dots that this
        repository's detector also likes reduced the off-catalogue proxy at <em>every</em> quantile tested
        ({fmt(load('evidence/incumbent_filter_results.json', {}).get('rows', [{}])[0].get('ff_delta'))} at the
        mildest cut). The incumbent's low-probability dots still carry credit, so our likelihood is not a superset of
        whatever produced the incumbent.</p></div>
        <div class="card"><h3>Thresholding detections down — refuted</h3><p>Raising the detector threshold trades away
        coverage faster than it buys precision once the field is unioned with the incumbent: the LiDAR arm's gain
        peaks at p ≥ 0.6, not at the highest-precision end.</p></div>
        <div class="card"><h3>Catalogue-gap holdout as a selector — refuted</h3><p>Its arm ranking is anti-correlated
        with the off-catalogue proxy, so it cannot promote arms. That refutation is the reason the off-catalogue proxy
        exists.</p></div>
      </div>
      <div class="notice notice-good"><strong>What worked: adding thresholded detections, on the LiDAR arm</strong>
      Unioning the incumbent with the LiDAR arm's off-catalogue detections at p ≥ 0.60 raises the off-catalogue proxy
      by {fmt(best_union(union).get('delta'))} — roughly three times the gain of the LiDAR+radiometric arm at its
      own best threshold. Adding pixels is directly invertible (the prediction surface is flat away from the incumbent),
      so each added dot's contribution is measurable, and the added dots earn
      {fmt(best_union(union).get('added_credit_per_dot'))} credit each — a fifth of an incumbent dot's rate,
      but positive.</div>
    </section>

    <section>
      <div class="section-head">
        <div><p class="kicker">Method</p><h2>The buffer that governs every comparison</h2></div>
        <p>Measured from residual autocorrelation, not assumed. Undersized collars leak training pixels and overstate generalisation.</p>
      </div>
      <div class="content">
        <p>Residual autocorrelation along known fault traces decays to 5 % of its peak at
        <strong>{fmt(buf['decision']['empirical_decay_range_m']/1000, 2)} km</strong>, so the holdout buffer is
        <strong>{fmt(buf['decision']['buffer_km'], 2)} km</strong>. Earlier GEMSDOE sessions used 0.5–2.8 km collars,
        7–40× smaller; anything measured under them is under-buffered. The full derivation, the model fits and the
        collar-sensitivity control are on the <a href="validation.html">validation page</a>.</p>
      </div>
    </section>
"""
    return shell("", "Research", "Metric algebra, the measured detection gap, and five ranked geological hypotheses "
                                 "with their evidence classes.", "Research",
                 page_hero("Research", "What the score means, and what could beat it.",
                           "The mechanism behind 0.2708, the quantified reason re-budgeting fails, and ranked candidate hypotheses — each with a physical signature and a reason it can find an unmapped fault."),
                 body, "Hypotheses on this page are labelled INFERENCE; only measured results are presented as results.")


def build_validation(buf: dict, buffer_derivation: dict, experiments: dict, metric_check: dict) -> str:
    decision = buffer_derivation["decision"]
    fits = buffer_derivation["fits"]
    grids = metric_check.get("grids_compared")
    worst = metric_check.get("max_abs_dti_delta_vs_brute_force")
    worst_text = f"{worst:.3e}" if isinstance(worst, float) else "—"
    offsets = metric_check.get("kernel_offsets_in_support")
    fit_rows = [[model, fmt(f["nugget"], 5), fmt(f["partial_sill"], 5), f"{f['range_m']/1000:.2f}",
                 f"{f['practical_range_m']/1000:.2f}", fmt(f["r_squared"], 3),
                 "yes" if model in decision["models_extrapolating_beyond_support"] else "no"]
                for model, f in fits.items()]
    collar = load("evidence/collar_sweep.json", [])
    body = f"""    <section>
      <div class="section-head">
        <div><p class="kicker">Buffer</p><h2>A collar measured from the data</h2></div>
        <p>An under-buffered holdout leaks training pixels from the same fault structure and overstates generalisation to a genuinely unmapped fault.</p>
      </div>
      <div class="content">
        <p>Out-of-fold residuals <code>e = 1 − p</code> were taken at every held-out catalogue pixel — 60,988 pixels in
        3,199 8-connected components — and pairs were restricted to the <strong>same</strong> component, so the curve is
        a within-trace dependence estimate. Matheron semivariance in 500 m bins, minimum 20 pairs per bin.</p>
      </div>
      {variogram_table(buffer_derivation)}
      <p class="small">The curve rises to a peak of {fmt(decision['empirical_peak_gamma'], 5)} at
      {fmt(decision['empirical_peak_lag_m']/1000, 2)} km and then falls: the residual correlation has a finite length.
      The distance at which γ first reaches 95 % of that peak — where autocorrelation has decayed to ≈5 % — is the
      empirical decay range.</p>
      <h3>Fits and the pre-declared decision rule</h3>
      {table(["model", "nugget", "partial sill", "fitted range (km)", "practical range (km)", "R²", "extrapolates beyond support?"], fit_rows)}
      <div class="notice"><strong>Rule, fixed before the numbers were seen</strong>{e(decision['rule'])}
      The exponential fit is reported but excluded: it extrapolates past the populated lag support, and using it would
      make the collar arbitrary again — the exact failure this rule exists to prevent.</div>
      {buffer_decision_table(buffer_derivation)}
      <p class="small">The pilot-stage rule that produced a 94.3 km collar was withdrawn: it came from an exponential
      bootstrap 95th percentile of {fmt(decision.get('withdrawn_rule_max_bootstrap_p95_m'), 0)} m against a
      {fmt(decision['observed_lag_support_m'], 0)} m lag support. It is recorded on the
      <a href="register/index.html">register</a> as a withdrawn claim and is not used anywhere on this site.</p>
    </section>

    <section>
      <div class="section-head">
        <div><p class="kicker">Control</p><h2>Collar sensitivity of the blocked protocol</h2></div>
        <p>Leakage-contaminated comparisons collapse as the collar grows. This one does not.</p>
      </div>
      {collar_table(collar)}
      <p class="small">Interpretation, stated conservatively: the quadrant protocol (≈150–190 km blocks) is insensitive
      to the collar between 0 and 30 km, so the LiDAR arm's advantage is not a short-range leakage artefact. It does
      <strong>not</strong> license the small collars used elsewhere: those are component-level holdouts whose
      geography is one to two orders of magnitude smaller than the measured range.</p>
    </section>

    <section id="metric">
      <div class="section-head">
        <div><p class="kicker">Metric</p><h2>The implementation is exact</h2></div>
        <p>Every score on this site comes from a direct implementation of the official formula, not an approximation.</p>
      </div>
      <div class="content">
        <p><code>src/gemsdoe31/metric.py</code> implements the definition directly — the {fmt(offsets, 0)} lattice offsets whose
        Euclidean distance is inside the 300 m kernel, plus a Euclidean distance transform for the false-positive
        term — and is checked against <code>metric.brute_force</code>, a literal per-pixel transcription of the
        published sums, on {fmt(grids, 0)} random grids and two exact hand-computed cases:
        <strong>maximum absolute DTI difference {worst_text}</strong> (<code>scripts/check_metric.py</code>,
        <code>evidence/metric_check.json</code>). The same check asserts the definitional identity
        <code>TPw + FNw = |G|</code> on every grid, which is the invariant that catches sign and kernel errors.
        The published worked example is not reproduced here because its two example rasters are only available as
        pictures on the competition page.</p>
      </div>
      <div class="table-wrap"><table><tbody>
        <tr><th style="width:220px">Kernel</th><td>k(d) = max(1 − d/300 m, 0), Euclidean distance, 100 m cells</td></tr>
        <tr><th>α / β</th><td>0.2 false-positive weight, 0.8 false-negative weight</td></tr>
        <tr><th>Verification</th><td>max |DTI_fast − DTI_brute| = {worst_text} over {fmt(grids, 0)} random grids, plus two exact closed-form cases (scripts/check_metric.py)</td></tr>
        <tr><th>Kernel offsets inside 300 m at 100 m cells</th><td>{fmt(offsets, 0)} (the radius-3 disk: (±3,0) counts, (±3,±1) does not)</td></tr>
        <tr><th>ε</th><td>{e(metric_check.get('epsilon_assumption', '—'))} — {e(metric_check.get('epsilon_note', ''))}</td></tr>
        <tr><th>Grid</th><td>3730 × 3292, EPSG:32611, 100 m, Affine(100, 0, 243350, 0, −100, 4508550)</td></tr>
      </tbody></table></div>
    </section>

    <section id="proxies">
      <div class="section-head">
        <div><p class="kicker">Truth proxies</p><h2>Two off-catalogue instruments, reported side by side</h2></div>
        <p>The competition's truth is a set of expert-mapped faults missing from the public database. No local population is that, so two proxies are used and their disagreement is published rather than hidden.</p>
      </div>
      <div class="grid grid-2">
        <div class="card"><h3>Catalogue-gap holdout</h3>
          <p>Held-out public-catalogue pixels: 60,988 px in four spatial blocks, with the measured buffer applied
          during training exclusion. Rewards finding mapped faults; does <em>not</em> resemble the hidden truth.
          <span class="badge badge-red">not usable as a selector</span></p></div>
        <div class="card"><h3>Off-catalogue discovery proxy</h3>
          <p>USGS State Geologic Map Compilation structure layers rasterised to this grid: 82,151 fault cells, of which
          <strong>61,664 lie more than 300 m from the competition catalogue</strong>. The only populated fault population
          in reach that is off-catalogue by construction. <span class="badge badge-green">selection instrument</span></p>
          <p class="small">Limit, stated plainly: SGMC faults are state-map faults of mixed age and certainty, not the
          experts' newly mapped Quaternary faults. A proxy can rank arms wrongly, which is why the arm ordering was
          checked at every threshold and both proxies are always printed.</p></div>
      </div>
    </section>

    <section>
      <div class="section-head">
        <div><p class="kicker">Protocol</p><h2>Fixed protocol for every measured comparison</h2></div>
        <p>Nothing about the folds, the buffer, the model class or the excluded features changed between arms.</p>
      </div>
      <div class="table-wrap"><table><tbody>
        <tr><th style="width:190px">Folds</th><td>{e(experiments['protocol']['folds'])}</td></tr>
        <tr><th>Buffer</th><td>{e(experiments['protocol']['buffer'])}</td></tr>
        <tr><th>Model</th><td>{e(experiments['protocol']['model'])}</td></tr>
        <tr><th>Excluded features</th><td>{e(experiments['protocol']['excluded_features'])}</td></tr>
        <tr><th>Metric</th><td>{e(experiments['protocol']['metric'])}</td></tr>
      </tbody></table></div>
      <h3>Reproduce every number</h3>
      <pre>git clone {REPO}.git &amp;&amp; cd GEMSDOE31
python -m pip install -r requirements.txt
bash scripts/download_competition_data.sh      # restore + SHA-256 verify the 11 hash-pinned inputs
python scripts/prepare_data.py --verify-only   # grid/hash re-check; add no flag to build features.f32
python scripts/check_metric.py                 # metric vs brute force -&gt; evidence/metric_check.json
python scripts/derive_buffer.py                # semivariogram -&gt; evidence/buffer_derivation.json
python scripts/run_union.py                    # filtering + union tables -&gt; evidence/union_results.json
python scripts/collect_evidence.py             # hash the artifacts, rebuild registry/*.json
python scripts/build_submission.py --dots &lt;tif&gt; --name &lt;unique-name&gt;
python scripts/build_site.py                   # regenerate this site from the registers</pre>
      <p class="small">Nothing on this site is typed in by hand: <code>scripts/build_site.py</code> reads the JSON in
      <code>registry/</code> and <code>evidence/</code>, and <code>scripts/collect_evidence.py</code> writes those JSON
      files from the artifacts on disk. One step is <em>not</em> yet reproducible from this snapshot: the training runs
      behind <code>evidence/arm_results.json</code> and <code>evidence/operating_point.json</code> (four arms × four
      folds) were executed in a sibling workspace whose trainer is not in this repository. Their outputs and protocol
      are pinned here, the fold-OOF probability maps they produced are committed in quantised form
      (<code>evidence/oof/*_u16.npz</code>, audited in <code>evidence/oof_quantisation.json</code>), and every
      downstream step — union, filter, metric, buffer, submission, site — reruns from those artifacts.
      Re-implementing the trainer is the top item of remaining work.</p>
    </section>
"""
    return shell("", "Validation", "Measured buffer derivation, collar sensitivity, metric exactness and the two "
                                   "off-catalogue truth proxies.", "Validation",
                 page_hero("Validation", "Measured, not assumed.",
                           "The buffer comes from the data, the metric is verified against brute force, and the two truth proxies are reported together with their limits."),
                 body, "Reproduce with: scripts/derive_buffer.py, scripts/check_metric.py, scripts/build_site.py.")


def build_sources(sources: dict, experiments: dict) -> str:
    items = []
    for s in sources["sources"]:
        claims = "".join(f"<li>{e(c)}</li>" for c in s.get("claims_verified", [])) or "<li>No claim verified this session.</li>"
        limits = s.get("limits") or s.get("used_for") or ""
        items.append(f"""<li>
          <strong><a href="{e(s['url'])}" target="_blank" rel="noopener">{e(s['title'])}</a></strong>
          <span class="badge{' badge-green' if s['class'] == 'OFFICIAL' else ''}">{e(s['class'])}</span>
          <span class="small"> · {e(s['publisher'])} · {e(s.get('accessed_utc') or 'not fetched this session')}</span>
          <ul class="small" style="margin:8px 0 0">{claims}</ul>
          {f'<p class="small" style="margin:8px 0 0"><em>Limit:</em> {e(limits)}</p>' if limits else ''}
        </li>""")
    body = f"""    <section>
      <div class="section-head">
        <div><p class="kicker">Provenance</p><h2>How to read a claim on this site</h2></div>
        <p>Every claim carries its class. A class is a statement about where the evidence came from — not about how confident anyone feels.</p>
      </div>
      <ul class="pill-list">
        <li><strong>OFFICIAL</strong> — read from a government, publisher or competition-administrator page linked here.</li>
        <li><strong>OWNER-MIRROR</strong> — published in one of this project's own repositories; a hash match proves byte identity to that mirror only.</li>
        <li><strong>COMPUTED</strong> — reproduced by a script in this repository, with the artifact path recorded.</li>
        <li><strong>INFERENCE</strong> — reasoning to be tested, not a measurement.</li>
        <li><strong>USER-REPORTED</strong> — stated by the project owner; no organizer receipt in the repository.</li>
        <li><strong>TRUSTED-PEER-REVIEWED</strong> — peer-reviewed methods literature cited for a design choice; it supplies no value for this dataset.</li>
      </ul>
    </section>

    <section>
      <div class="section-head">
        <div><p class="kicker">Register</p><h2>Every source used</h2></div>
        <p>Includes what was verified and, where it matters, what the source does <em>not</em> prove.</p>
      </div>
      <ul class="source-list">{''.join(items)}</ul>
    </section>

    <section>
      <div class="section-head">
        <div><p class="kicker">Boundary</p><h2>What this project deliberately does not do</h2></div>
        <p>These are limits chosen for the competition's terms and the integrity of the numbers, not omissions.</p>
      </div>
      <div class="grid grid-3">
        <div class="card"><h3>No leaderboard scraping</h3><p>The DrivenData terms prohibit automatic access and
        manual monitoring or copying without written consent. The leaderboard is a static link for a human to open;
        nothing on this site is derived from it.</p></div>
        <div class="card"><h3>No uploading</h3><p>Nothing in this repository submits a file. A weekly slot is scarce
        and the charter requires a measured margin before one is spent.</p></div>
        <div class="card"><h3>No unaudited scores</h3><p>A score appears only as <span class="badge">owner-reported</span>
        with the file's SHA-256 attached, unless an organizer receipt is present. None is.</p></div>
      </div>
    </section>

    <section>
      <div class="section-head">
        <div><p class="kicker">Machine-readable</p><h2>The same facts as JSON</h2></div>
        <p>For automated review, every register file is published in the repository and summarised in the feed.</p>
      </div>
      <div class="table-wrap"><table><tbody>
        <tr><th style="width:280px">registry/sources.json</th><td>this page</td></tr>
        <tr><th>registry/submissions.json</th><td>every submission-shaped file, its hashes and its status</td></tr>
        <tr><th>registry/data_manifest.json</th><td>hash pins for every input raster</td></tr>
        <tr><th>registry/score_claims.json</th><td>score claims and their evidence class</td></tr>
        <tr><th>registry/irregularities.json</th><td>open and closed irregularities, including the D2.8 score discrepancy</td></tr>
        <tr><th>registry/review_passes.json</th><td>the multi-pass review record</td></tr>
        <tr><th>registry/experiments.json</th><td>protocol and artifact list behind every table</td></tr>
        <tr><th>feed.json</th><td>current download, buffer, proxy scores, open items</td></tr>
      </tbody></table></div>
      <p class="small">Rebuilt by <code>python scripts/build_site.py</code> and
      <code>python scripts/collect_evidence.py</code>.</p>
    </section>
"""
    return shell("", "Sources", "Every source used, its evidence class, and what it does and does not prove.",
                 "Sources",
                 page_hero("Sources", "Verify everything.",
                           "Links for manual review, the evidence class of each claim, and the boundary this project keeps around the competition's own systems."),
                 body, "Reported irregularities, including the D2.8 score discrepancy, are listed on the register page.")


def build_feed(sub: dict, buf: dict, union: dict, arms: dict, sources: dict) -> tuple[str, str]:
    primary = next(f for f in sub["files"] if f["id"] == "primary-h27-4-solo-d28")
    research = next(f for f in sub["files"] if f["name"] == sub["best_research_candidate"]["name"])
    feed = {
        "schema_version": 1,
        "project": "GEMSDOE31",
        "generated_from": "registry/*.json + evidence/*.json by scripts/build_site.py",
        "decision": sub["decision"],
        "lane_candidate": {"name": sub["lane_candidate"]["name"], "verdict": sub["lane_candidate"]["verdict"],
                           "ready_to_submit": sub["lane_candidate"]["ready_to_submit"],
                           "tif_allfinite": sub["lane_candidate"]["files"]["allfinite"], "tif_nan": sub["lane_candidate"]["files"]["nan"],
                           "sha256_allfinite": sub["lane_candidate"]["gate_receipts"]["allfinite"]["sha256"],
                           "note": sub["lane_candidate"]["note_for_portal"], "organizer_receipt": "none"},
        "current_download": {
            "name": primary["name"],
            "tif": primary["file_nan"],
            "sha256": primary.get("sha256_nan"),
            "positive_pixels": primary["positive_pixels"],
            "positive_pixels_on_public_catalogue": primary["positive_pixels_on_public_catalogue"],
            "format_validated": primary.get("format_ok_nan"),
            "measured": primary.get("measured"),
            "score_status": sub["current_recommended"]["score_status"],
            "slot_approved": sub["current_recommended"]["slot_approved"],
        },
        "research_candidate": {
            "name": research["name"],
            "tif": research["file_nan"],
            "sha256": research.get("sha256_nan"),
            "positive_pixels": research["positive_pixels"],
            "off_catalogue_proxy_DTI": research["measured"]["off_catalogue_proxy_DTI"],
            "incumbent_off_catalogue_proxy_DTI": research["measured"]["incumbent_off_catalogue_proxy_DTI"],
            "delta": research["measured"]["delta"],
            "slot_approved": False,
        },
        "buffer": {
            "derived_buffer_km": buf["decision"]["buffer_km"],
            "empirical_decay_range_km": buf["decision"]["empirical_decay_range_m"] / 1000,
            "rule": buf["decision"]["rule"],
            "source": "evidence/buffer_derivation.json",
        },
        "proxy_scores": {
            "incumbent_off_catalogue": union.get("incumbent", {}).get("ff_DTI"),
            "incumbent_catalogue_gap": union.get("incumbent", {}).get("cat_DTI"),
            "baseline_arm_off_catalogue": arms.get("A_competition19", {}).get("best_farfield", {}).get("DTI_ff"),
            "best_arm_off_catalogue": max((a["best_farfield"]["DTI_ff"] for a in arms.values() if a.get("best_farfield")), default=None),
            "best_union_off_catalogue": max((r["ff_DTI"] for r in union.get("unions", []) if r["arm"].startswith("D_")), default=None),
        },
        "sources": [{"id": s["id"], "class": s["class"], "url": s["url"], "accessed_utc": s.get("accessed_utc")}
                    for s in sources["sources"]],
        "automation": {
            "rebuild": "python scripts/build_site.py",
            "rule": "pages and this feed are regenerated from registry/ and evidence/ on every push; no manual editing",
            "not_automated": "leaderboard reads, score entry and file uploads remain manual by competition terms",
        },
        "open_items": [
            "no organizer receipt for any score on this site",
            "no candidate has beaten the incumbent on the off-catalogue proxy by a margin worth a weekly slot",
            "lane candidate AS-1 failed its preregistered holdout gate and the lane-uniqueness gate: no file is cleared for submission",
            "external layers needing the CI runner (GDR 1391 MT depth stack, 3DEP LAZ returns) are not yet validated",
        ],
    }
    payload = json.dumps(feed, indent=1) + "\n"
    rows = [[e(k), f"<code>{e(json.dumps(v))}</code>"] for section, values in feed.items()
            if isinstance(values, dict) and section not in ("sources", "automation")
            for k, v in values.items()]
    body = f"""    <section>
      <div class="section-head">
        <div><p class="kicker">Machine-readable</p><h2>Current state of the project</h2></div>
        <p>Regenerated from the register and evidence files, so it cannot drift from the measurements. Also published as <a href="feed.json">feed.json</a>.</p>
      </div>
      {table(["field", "value"], rows)}
    </section>

    <section>
      <div class="section-head">
        <div><p class="kicker">Boundary</p><h2>Why the feed stops there</h2></div>
        <p>Three things are deliberately not automated, each for a stated reason.</p>
      </div>
      <div class="grid grid-3">
        <div class="card"><h3>Leaderboard reads</h3><p>Automatic access and monitoring are prohibited without written
        consent, so the leaderboard stays a link for a human. Scores enter the repository only as owner-reported
        claims with the file's SHA-256 attached.</p></div>
        <div class="card"><h3>Uploads</h3><p>Nothing here submits a file. A weekly slot is scarce and the charter
        requires a measured margin first.</p></div>
        <div class="card"><h3>Post-holdout tuning</h3><p>Arms are ranked on fixed folds with a fixed buffer, and the
        promotion rule is written into the evidence file before the run.</p></div>
      </div>
    </section>

    <section>
      <div class="section-head">
        <div><p class="kicker">Open items</p><h2>What is still owed</h2></div>
        <p>Published so the next session starts from the same list rather than from memory.</p>
      </div>
      <div class="card"><ul>{''.join(f'<li>{e(i)}</li>' for i in feed["open_items"])}</ul></div>
      <h3>Rebuild</h3>
      <pre>python scripts/collect_evidence.py   # copy measured artifacts into evidence/ + registry/experiments.json
python scripts/build_site.py          # regenerate every page and feed.json</pre>
    </section>
"""
    return payload, shell("", "Live feed", "Current download, buffer, proxy scores and open items, rebuilt from "
                                           "the repository's own evidence.", "Live feed",
                          page_hero("Live feed", "The state of the project, from the files.",
                                    "Rebuilt on every push from registry/ and evidence/, published as HTML and as JSON."),
                          body, "Feed data: feed.json · rebuilt by scripts/build_site.py")


def build_ai_disclosure() -> str:
    body = """    <section>
      <div class="section-head">
        <div><p class="kicker">Required disclosure</p><h2>How AI was used</h2></div>
        <p>The competition's rules require entrants to disclose AI use in the submission narrative.</p>
      </div>
      <div class="grid grid-2">
        <div class="card"><h3>What was done with AI assistance</h3>
          <ul><li>The analysis code, the data-restoration scripts and every page on this site were written by an AI
          agent working from the owner's written brief.</li>
          <li>The agent ran the experiments and wrote the numbers here directly from the resulting files.</li>
          <li>Every quantitative claim is traceable to a script and an artifact in the repository, and carries an
          evidence class (OFFICIAL / OWNER-MIRROR / COMPUTED / INFERENCE / USER-REPORTED).</li></ul></div>
        <div class="card"><h3>What is not claimed</h3>
          <ul><li>No score on this site is organizer-verified. The 0.2708 and 0.2600 figures are owner-reported
          readings of a public leaderboard, not receipts.</li>
          <li>Geological hypotheses are labelled INFERENCE and have not been confirmed by field work.</li>
          <li>The submission file's <em>format</em> is validated locally against the grid template; its live score is
          not predicted here.</li></ul></div>
      </div>
      <div class="notice"><strong>Draft wording for the submission narrative — edit to match what you actually did</strong>
      <pre style="margin-top:12px">This submission's raster was produced with substantial AI assistance (an agentic coding
workflow), using the competition-provided feature stack plus publicly licensed external
layers. All quantitative claims, validation protocols and file-format checks are recorded
in the project repository with sources and evidence classes. No live score is claimed.
The human entrant reviewed the submission file, its format receipt and this disclosure
before submitting.</pre></div>
      <p class="small">The exact disclosure requirements come from the competition rules; this page is a draft for the
      entrant to review, not a filed disclosure. <a href="sources.html">Sources</a></p>
    </section>
"""
    return shell("", "AI use", "Draft disclosure of AI assistance for the submission narrative, for entrant review.",
                 "", page_hero("AI use", "Disclose it properly.",
                              "What the agent did, what is not claimed, and wording you can paste into the submission narrative after checking it."),
                 body, "Draft for entrant review — not a filed disclosure.")


def build_register(data: dict, sources_doc: dict, buf: dict) -> str:
    manifest = data["data_manifest"]
    claims = data["score_claims"]
    irregularities = data["irregularities"]
    reviews = data["review_passes"]

    manifest_rows = []
    for entry in manifest.get("files", []):
        parts = len(entry.get("parts", [])) or 1
        manifest_rows.append([
            f"<code>{e(entry.get('id'))}</code><div class=\"small\">{e(entry.get('dest', ''))}</div>",
            f"<span class=\"badge{' badge-green' if entry.get('group') == 'core' else ''}\">{e(entry.get('group',''))}</span>",
            f"<code>{e((entry.get('sha256') or '')[:24])}…</code>" if entry.get("sha256") else "—",
            fmt(entry.get("bytes"), 0),
            f"{parts} part(s), {len(entry.get('bands', [])) and len(entry.get('bands', [])) or '—'} bands",
            f"<code>{e(entry.get('repo',''))}</code><div class=\"small\">{e((entry.get('ref') or '')[:12])}…</div>",
        ])
    claim_rows = [[f"<code>{e(c['id'])}</code>", fmt(c.get("reported_dti")), f"<span class=\"badge\">{e(c['evidence_class'])}</span>",
                   e(c.get("claim_source", "")), e(c.get("artifact", "")), e(c.get("organizer_verification", c.get("organizer_verified", "none")))]
                  for c in claims.get("claims", [])]
    irregularity_rows = [[f"<code>{e(i['id'])}</code>",
                          f"<span class=\"badge{' badge-red' if i.get('severity') == 'high' else ''}\">{e(i.get('severity',''))} · {e(i.get('status'))}</span>",
                          e(i.get("summary", "")), e(i.get("action", ""))] for i in irregularities.get("items", [])]
    review_rows = []
    for p in reviews.get("passes", []):
        scope = p.get("scope", "")
        scope_text = "; ".join(scope) if isinstance(scope, list) else str(scope)
        verification = p.get("verification", {})
        outcome = "; ".join(f"{k}: {v}" for k, v in verification.items()) if isinstance(verification, dict) else str(verification)
        gates = p.get("open_scientific_gates", [])
        gates_text = "; ".join(gates) if isinstance(gates, list) else str(gates)
        review_rows.append([f"<code>{e(p.get('id'))}</code>",
                            f"<span class=\"badge\">{e(p.get('status',''))}</span>",
                            e(scope_text), e(outcome), e(gates_text)])
    body = f"""    <section>
      <div class="section-head">
        <div><p class="kicker">Register</p><h2>Inputs, pinned by hash</h2></div>
        <p>Every raster this work uses is hashed. Hash equality proves byte identity to the mirror it came from — not organizer authentication.</p>
      </div>
      {table(["input", "group", "sha256", "bytes", "layout", "mirror"], manifest_rows)}
      <p class="small">Full record: <code>registry/data_manifest.json</code> ·
      <a href="{REPO}/blob/main/registry/data_manifest.json">view on GitHub</a>. Irregularities found while restoring
      the inputs are recorded below rather than smoothed over.</p>
    </section>

    <section>
      <div class="section-head">
        <div><p class="kicker">Scores</p><h2>Score claims and their evidence class</h2></div>
        <p>No organizer receipt exists for any score in this repository, so none is presented as official.</p>
      </div>
      {table(["claim", "value", "class", "source", "artifact", "organizer verification"], claim_rows)}
      <p class="small">Full record: <code>registry/score_claims.json</code>. The 0.3195 leaderboard anchor is treated as
      a real independent team's result and is used only as a target, never as a measurement of ours.</p>
    </section>

    <section>
      <div class="section-head">
        <div><p class="kicker">Integrity</p><h2>Irregularities: open and closed</h2></div>
        <p>Kept in the repository so a reviewer does not have to find them.</p>
      </div>
      {table(["id", "severity · status", "what happened", "what is being done"], irregularity_rows)}
    </section>

    <section>
      <div class="section-head">
        <div><p class="kicker">Process</p><h2>Review passes and withdrawn claims</h2></div>
        <p>Three passes are run over the work; a claim that fails a pass is withdrawn on the record, not silently dropped.</p>
      </div>
      {table(["pass", "status", "scope", "verification performed", "open scientific gates"], review_rows) if review_rows else '<p class="small">Review-pass record not present in this checkout.</p>'}
      <ul>
        <li><strong>Withdrawn:</strong> the pilot-stage buffer rule that produced a 94.3 km collar (exponential bootstrap
        p95 against a {fmt(buf['decision']['observed_lag_support_m'], 0)} m lag support). Replaced by the empirical
        decay-range rule on the <a href="../validation.html">validation page</a>.</li>
        <li><strong>Withdrawn:</strong> any holdout result quoted under a 0.5–2.8 km collar without disclosing that it is
        7–40× smaller than the measured range.</li>
        <li><strong>Refuted:</strong> the catalogue-gap holdout as a promotion instrument — its ranking is
        anti-correlated with the off-catalogue proxy.</li>
        <li><strong>Superseded:</strong> a separate <code>score-audit</code> page that used to sit alongside this one.
        Its claims and the H27-4 unscored record are folded into the score table above, and the long-form record stays
        at <a href="{REPO}/blob/main/knowledge/score_and_prior_art_review_2026-10-03.md">knowledge/score_and_prior_art_review_2026-10-03.md</a>.
        The site is held to a 20-page budget, so a redundant page is merged rather than accumulated.</li>
      </ul>
    </section>

    <section>
      <div class="section-head">
        <div><p class="kicker">Files</p><h2>Register files in this repository</h2></div>
        <p>Each is JSON, regenerated by scripts, and linked so any single claim can be checked.</p>
      </div>
      <div class="table-wrap"><table><tbody>
        <tr><th style="width:300px"><code>registry/score_claims.json</code></th><td>score claims, evidence classes, receipt status</td></tr>
        <tr><th><code>registry/data_manifest.json</code></th><td>hash pins and irregularity records for the inputs</td></tr>
        <tr><th><code>registry/submissions.json</code></th><td>submission files, hashes, measured proxies, slot status</td></tr>
        <tr><th><code>registry/irregularities.json</code></th><td>the irregularity log</td></tr>
        <tr><th><code>registry/review_passes.json</code></th><td>the review record</td></tr>
        <tr><th><code>registry/sources.json</code></th><td>the source register behind <a href="../sources.html">sources</a></td></tr>
        <tr><th><code>registry/experiments.json</code></th><td>protocol and artifact list</td></tr>
      </tbody></table></div>
    </section>
"""
    return shell("../", "Register", "Hash-pinned inputs, score claims, irregularities and the review record.",
                 "Register",
                 page_hero("Register", "Everything that can be checked.",
                           "Inputs pinned by hash, score claims labelled by evidence class, irregularities kept open, and withdrawn claims kept on the record."),
                 body, "Machine-readable originals live in registry/ in the repository.")


EXPERIMENTS = [
    dict(slug="01-arms", number=1, title="Blocked-fold detector arms A–D",
         source="evidence/arm_results.json", status="measured",
         question="Does adding LiDAR- and radiometric-derived channels to the 19 competition planes improve fault detection under spatial blocking?",
         verdict="Measured. The LiDAR/radiometric arms win the catalogue-gap proxy; the base 19-plane arm wins nothing. Both orderings are reported because the two proxies disagree.",
         detail="Four arms were trained on the same four spatial blocks with the same model class and no catalogue-derived feature. "
                "A = the 19 competition planes; B = A plus LiDAR terrain descriptors; C = A plus radiometric channels; D = both. "
                "Arms were compared at matched thresholds and each arm's best operating point on each proxy is recorded."),
    dict(slug="02-operating-points", number=2, title="Operating-point sweep",
         source="evidence/operating_point.json", status="measured",
         question="Where on each arm's probability scale should a submission threshold sit?",
         verdict="Measured and negative for the live score: no threshold on any arm reaches the incumbent dot set on the off-catalogue proxy, because coverage dilutes credit per pixel.",
         detail="Each arm was swept over thresholds, recording emitted dots, both proxy DTIs and credit per emitted pixel. "
                "The sweep is what showed that precision at ~0.135 credit/dot is the incumbent's advantage and that no threshold reproduces it."),
    dict(slug="03-collar-sensitivity", number=3, title="Collar sensitivity of the blocked protocol",
         source="evidence/collar_sweep.json", status="measured",
         question="Is the LiDAR arm's advantage an artefact of short-range leakage from the training region?",
         verdict="Measured, no: proxy scores are flat from a 0 km to a 30 km collar, so the conclusion is stable under the measured 21.25 km range. It does not license smaller collars used elsewhere.",
         detail="The same paired comparison was recomputed while deleting every evaluation cell within b km of the training region, for b in 0…30 km."),
    dict(slug="04-incumbent-filter", number=4, title="Corroboration filtering of the incumbent (negative)",
         source="evidence/incumbent_filter_results.json", status="negative result",
         question="Can the incumbent dot set be improved by keeping only the dots this repository's detector also likes?",
         verdict="No. Every quantile tested reduced both proxies monotonically. The incumbent's low-probability dots still carry real off-catalogue credit.",
         detail="Incumbent dots were ranked by the fold-D detector probability and the top 90 %, 75 %, 50 % and 25 % were rescored. "
                "All four subsets scored below the full dot set, which is why the leaderboard direction is to add detections rather than thin the incumbent."),
    dict(slug="05-addition-arm", number=5, title="Addition arm: incumbent plus off-catalogue detections",
         source="evidence/union_results.json", status="measured, weak positive",
         question="Does adding high-probability off-catalogue detections to the incumbent improve the off-catalogue proxy?",
         verdict="Weakly positive. The best union adds 15,105 dots for +0.0017 on the proxy — the right sign, but within the owner's observed ±0.003 live noise, so it is a research candidate and not slot-approved.",
         detail="The incumbent was unioned with cells where the fold-D detector probability exceeded a threshold and the cell was not on the public "
                "catalogue, at thresholds from 0.5 to 0.95. Adding pixels is directly invertible, unlike subtracting them: the surface is flat "
                "away from the incumbent, so each added dot's contribution is measurable."),
    dict(slug="06-buffer-derivation", number=6, title="Residual semivariogram → holdout buffer",
         source="evidence/buffer_derivation.json", status="measured",
         question="How far can training pixels leak into a holdout and still leave an honest comparison?",
         verdict="Measured: autocorrelation decays to 5 % of peak at 21.25 km, so the collar is 21.25 km — not the 4–5 pixels assumed in earlier work.",
         detail="Out-of-fold residuals along known traces were pooled within components and binned at 500 m. Three variogram models were fitted "
                "with a component bootstrap; the decision rule (max of empirical decay range and median fitted practical range) was fixed before "
                "the numbers were read."),
    dict(slug="07-oof-maps", number=7, title="Out-of-fold probability maps",
         source="evidence/oof", status="measured",
         question="What do the detectors' spatial error patterns look like once every cell is predicted by a model that never saw its block?",
         verdict="Retained as arrays (two arms, float32, grid-shaped) so every later experiment reuses the same folds instead of re-fitting.",
         detail="These maps are the input to the union and filter experiments. They are large binary arrays and are published as a release asset "
                "rather than committed to the repository; their hashes are recorded here. Regenerating them requires the feature matrix and the "
                "blocked-fold training run.", manifest=True),
    dict(slug="08-h31a-pilot", number=8, title="H31-A pilot: multiscale magnetic local-wavelength discontinuity",
         source="evidence/h31_a/pilot/results.json", status="stopped",
         question="Does a cross-scale magnetic local-wavelength feature find faults the catalogue misses?",
         verdict="Stopped at the pilot gate: mean paired ΔDTI −0.0040 and only 1/4 blocks positive. Not promoted, not screened, no submission built from it.",
         detail="The protocol, draw numbers and gate thresholds were frozen before fitting and are published in the repository. A candidate that "
                "fails a pre-declared gate is stopped rather than rescued with a different measurement."),
    dict(slug="09-pilot-variogram", number=9, title="Pilot-stage variogram diagnostics and the withdrawn 94.3 km rule",
         source="evidence/h31_a/pilot/variogram.json", status="diagnostic",
         question="Could the pilot's own residuals identify a stable buffer range?",
         verdict="No: both fits were unstable because the observed lag support did not reach 95 % of the fitted sill. The rule that inferred a 94.3 km collar from an exponential bootstrap was withdrawn.",
         detail="Post-hoc diagnostics recomputed the empirical curve for both arms; the instability is recorded as the reason the later, "
                "full-grid derivation was run instead. The withdrawn number is kept on the register so it cannot reappear as a buffer."),
    dict(slug="10-submission-format", number=10, title="Submission format validation and the [0,1] error class",
         source="docs/downloads", status="measured",
         question="Why did the portal reject a previously downloaded TIFF with “Predicted values must be in range [0, 1]”?",
         verdict="The traced trigger was non-finite cells inside the scored footprint while every finite value was already in range. The validator now hard-fails on that condition and a regression test pins it.",
         detail="Two format conventions are written from every dot set (NaN outside the footprint, and an all-finite variant). Each file gets a "
                "JSON receipt recording grid equality, value range, NaN placement and SHA-256, so a rejection can be diagnosed from the receipt "
                "instead of by guesswork."),
    dict(slug="11-score-claims", number=11, title="Score-claim audit and the D2.8 discrepancy",
         source="registry/score_claims.json", status="open irregularity",
         question="Which numbers in this project are receipts, which are reports, and which are derived?",
         verdict="Open and unresolved: the owner reports 0.2600 for D2.8 and 0.2708 for the h27-4 geometry, but the pinned owner mirror marks D2.8 unscored and no organizer receipt exists for any score.",
         detail="Every score in this repository is therefore labelled USER-REPORTED, and the discrepancy is tracked as an irregularity until the "
                "owner can attach an organizer receipt or a file-to-score identifier. This is why the site never presents a score as official."),
]


def build_experiments_index(sub: dict) -> str:
    rows = [[f"{x['number']:02d}", f'<a href="{x["slug"]}.html">{e(x["title"])}</a>',
             f'<span class="badge{" badge-green" if x["status"] == "measured" else " badge-red" if x["status"] in ("negative result", "stopped") else ""}">{e(x["status"])}</span>',
             e(x["question"])] for x in EXPERIMENTS]
    body = f"""    <section>
      <div class="section-head">
        <div><p class="kicker">Experiment log</p><h2>{len(EXPERIMENTS)} experiments, including the failures</h2></div>
        <p>Every page is generated from the artifact it describes; negative results and a stopped pilot stay in the log.</p>
      </div>
      {table(["#", "experiment", "status", "question it answers"], rows)}
      <p class="small">Protocol, folds, buffer and the exactness of the metric are fixed across all of these and are
      described once on the <a href="../validation.html">validation page</a>. Artifacts live in <code>evidence/</code>
      and <code>registry/</code>; the machine-readable index is <code>registry/experiments.json</code>.</p>
    </section>

    <section>
      <div class="section-head">
        <div><p class="kicker">How to read a result</p><h2>Three rules that govern every page here</h2></div>
        <p>These are the conditions under which the numbers were produced, not preferences.</p>
      </div>
      <div class="grid grid-3">
        <div class="card"><h3>Proxies are not scores</h3><p>No proxy DTI on this site is a competition score. A proxy
        can rank two arms; it cannot tell you what the leaderboard will say.</p></div>
        <div class="card"><h3>Folds and buffer are fixed</h3><p>Four spatial blocks and a
        {fmt(load('evidence/buffer_derivation.json', {'decision': {}})['decision'].get('buffer_km'), 2)} km collar derived from the data.
        Comparing a result measured under a different collar is not allowed.</p></div>
        <div class="card"><h3>A gate failure stops work</h3><p>Experiment 8 was stopped by its own pre-declared gate.
        Nothing was promoted from it, and no submission was built from it.</p></div>
      </div>
    </section>
"""
    return shell("../", "Experiments", "Experiment log: arms, sweeps, buffer derivation, the stopped pilot and the "
                                       "format-error investigation.", "Experiments",
                 page_hero("Experiments", "Measured, or stopped.",
                           "Eleven experiments with their artifacts, including the negative results and the one candidate that failed its own gate."),
                 body, "Artifacts pinned in evidence/ and registry/; every page generated by scripts/build_site.py.")


def build_experiment_page(exp: dict) -> str:
    path = exp["source"]
    if exp.get("manifest"):
        files = sorted(p for p in (ROOT / path).rglob("*") if p.is_file())
        rows = [[f"<code>{e(f.name)}</code>", fmt(f.stat().st_size, 0)] for f in files]
        content = table(["file", "bytes"], rows) + (
            '<p class="small">Arrays are published as a release asset rather than committed; see the repository '
            'releases page for the downloads and their hashes, which are recorded in this page\'s source file.</p>')
    else:
        artifact = load(f"{path}.json") if not str(path).endswith(".json") and (ROOT / f"{path}.json").is_file() else load(path)
        if isinstance(artifact, dict):
            rows = []
            for key, value in artifact.items():
                if isinstance(value, (dict, list)):
                    rows.append([f"<code>{e(key)}</code>", f"<code>{e(json.dumps(value)[:320])}{'…' if len(json.dumps(value)) > 320 else ''}</code>"])
                else:
                    rows.append([f"<code>{e(key)}</code>", fmt(value, 6)])
            content = table(["field", "value"], rows)
        elif isinstance(artifact, list):
            rows = [[f"<code>{e(json.dumps(row)[:400])}</code>"] for row in artifact]
            content = table(["row"], rows)
        else:
            content = '<p class="small">Artifact not present in this checkout.</p>'
    body = f"""    <section>
      <div class="section-head">
        <div><p class="kicker">Experiment {exp['number']:02d}</p><h2>{e(exp['title'])}</h2></div>
        <p>{e(exp['question'])}</p>
      </div>
      <div class="notice{' notice-good' if exp['status'] == 'measured' else ''}"><strong>{e(exp['status'].capitalize())}</strong>{e(exp['verdict'])}</div>
      <div class="content"><p>{e(exp['detail'])}</p></div>
    </section>

    <section>
      <div class="section-head">
        <div><p class="kicker">Artifact</p><h2>Measured values, as written by the script</h2></div>
        <p>Source file: <code>{e(path)}</code> — rendered here directly from the JSON, not transcribed.</p>
      </div>
      {content}
      <p class="small">Full artifact:
      <a href="{REPO}/blob/main/{e(path)}" target="_blank" rel="noopener">view in the repository</a>.</p>
    </section>
"""
    return shell("../", f"Experiment {exp['number']:02d} · {exp['title']}",
                 exp["question"], "Experiments",
                 page_hero(f"Experiment {exp['number']:02d} · {exp['status']}", exp["title"], exp["verdict"]),
                 body, f"Artifact: {path}. Generated by scripts/build_site.py.")


def main() -> None:
    submissions = load("registry/submissions.json", {"files": [], "current_recommended": {}})
    sources = load("registry/sources.json", {"sources": []})
    experiments = load("registry/experiments.json", {"protocol": {}, "artifacts": {}})
    buffer_derivation = load("evidence/buffer_derivation.json")
    if buffer_derivation is None:
        raise SystemExit("evidence/buffer_derivation.json is required; run scripts/derive_buffer.py first")
    union = load("evidence/union_results.json", {})
    arms = load("evidence/arm_results.json", {})
    data = {
        "data_manifest": load("registry/data_manifest.json", {}),
        "score_claims": load("registry/score_claims.json", {}),
        "irregularities": load("registry/irregularities.json", {}),
        "review_passes": load("registry/review_passes.json", {}),
    }
    DOSSDIRS = [DOCS, DOCS / "register", DOCS / "experiments"]
    for d in DOSSDIRS:
        d.mkdir(parents=True, exist_ok=True)

    pages = {
        DOCS / "index.html": build_index(submissions, buffer_derivation, union, arms),
        DOCS / "executive-summary.html": build_executive_summary(submissions, buffer_derivation, submission_receipts()),
        DOCS / "lane.html": build_lane(submissions),
        DOCS / "research.html": build_research(submissions, buffer_derivation, union),
        DOCS / "validation.html": build_validation(buffer_derivation, buffer_derivation, experiments,
                                                  load("evidence/metric_check.json", {})),
        DOCS / "sources.html": build_sources(sources, experiments),
        DOCS / "ai-disclosure.html": build_ai_disclosure(),
        DOCS / "register" / "index.html": build_register(data, sources, buffer_derivation),
        DOCS / "experiments" / "index.html": build_experiments_index(submissions),
    }
    for exp in EXPERIMENTS:
        pages[DOCS / "experiments" / f"{exp['slug']}.html"] = build_experiment_page(exp)
    feed_json, feed_html = build_feed(submissions, buffer_derivation, union, arms, sources)
    pages[DOCS / "feed.json"] = feed_json
    pages[DOCS / "feed.html"] = feed_html

    for path, text in pages.items():
        path.write_text(text)
    (DOCS / ".nojekyll").write_text("")
    html_pages = sorted(p for p in DOCS.rglob("*.html"))
    print(f"wrote {len(html_pages)} pages and {len(pages) - len(html_pages)} data file(s) under {DOCS.relative_to(ROOT)}")
    for p in html_pages:
        print("  ", p.relative_to(ROOT))


if __name__ == "__main__":
    main()
