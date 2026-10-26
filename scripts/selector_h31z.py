#!/usr/bin/env python3
"""Selector step for session arena/15e685db (separate from the H31-Z lane).

Re-judges every already-generated candidate under the SAME frozen selector
gates G1-G6 as the historical selector audit (H31-U preregistration gates;
gate definitions imported/copied verbatim from `scripts/selector_audit.py`,
whose own entry point remains disabled by the 9883b598 session). No fitting,
no new surfaces, no new dots: format, SGMC, projection and discrete-peer
overlaps are recomputed from TIFF bytes today; holdout/canary verdicts are
read fail-closed from each lane's own run card.

Governance (preregistration H31-Z section 2 / IR-U-02): uniqueness judged on
discrete peer submissions; the literal 695-raster lattice reading is computed
in lane cards and disclosed in the decision -- under that reading the correct
action is to submit nothing. Primary = highest PROJECTION among promoted
(never a score). DrivenData is never contacted; owner uploads manually and
must check the live weekly cap on the submission page (unverified here).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))

import run_h31u as U  # noqa: E402
import selector_audit as SA  # noqa: E402
from gems57 import uniqueness  # noqa: E402
from gemsdoe31.submission import validate_submission  # noqa: E402

SESSION = "arena/15e685db-gemsdoe31"
H31Z_CARD = ROOT / "evidence/h31z/run_card.json"
H31Z = dict(lane="H31-Z", card="evidence/h31z/run_card.json")


def h31z_holdout(card: dict) -> dict:
    """X/Y-style extractor for the H31-Z card schema (fail-closed)."""
    h = card["holdout_dti"]
    d = h["screen_paired_vs_ctrl"]
    d2 = h["screen_paired_vs_slope"]
    c = h["confirmation_random_component_split"]["paired_differences"]["CTRL"]
    exp2 = json.loads((ROOT / "evidence/h31z/exp2.json").read_text())
    pf = exp2["ablation"]["per_fold"]
    fk = exp2["ablation"]["final_variant"]
    qwins_ctrl = sum(1 for a, b in zip(pf[fk], pf["CTRL"]) if a["dti"] >= b["dti"])
    ok = bool(d["delta"] > 0 and d["ci95"][0] > 0 and d2["delta"] > 0 and d2["ci95"][0] > 0
              and c["delta"] > 0 and c["ci95"][0] > 0 and qwins_ctrl >= 3)
    return dict(pass_=ok, evaluator=h["evaluator_version"], dti=h["screen_final_surface"]["dti"],
                ci95=h["screen_final_surface"]["ci95"],
                n=h["screen_final_surface"]["withheld_positive_pixels"],
                delta=d["delta"], delta_ci95=d["ci95"],
                confirmation_delta=c["delta"], confirmation_delta_ci95=c["ci95"],
                quadrant_wins_vs_ctrl=qwins_ctrl,
                paired_vs_junc_screen=h["screen_paired_vs_junc"],
                summary="paired CIs vs CTRL & SLOPE + untouched random-component confirmation "
                        "vs CTRL (card verbatim); NOTE lane G3 additionally required beating "
                        "JUNC (H31-X rebuild) and failed: delta vs JUNC recorded verbatim")


def main() -> int:
    zcard = json.loads(H31Z_CARD.read_text())
    zfile = zcard["files"]["zeros"]
    candidates = [dict(c) for c in SA.CANDIDATES] + [dict(H31Z, file=zfile)]
    foot, cat, sgmc, off_sgmc, d_cat = U.load_grid()
    sample = ROOT / "data/sample_submission.tif"
    # --- projection fit (assert identical to H31-U exp3, as historical selector) ---
    exp3u = json.loads((ROOT / "evidence/h31u/exp3.json").read_text())
    anchors = U.load_peer_dots_by_tag(foot)
    arows = []
    for tag, (dots, live, _p) in anchors.items():
        s = U.sgmc_score(dots, off_sgmc, foot)
        arows.append(dict(tag=tag, live=live, n=s["n_dots"], tpw=s["tpw"], sgmc_dti=s["dti"]))
    by = {r["tag"]: r for r in arows}
    a, b = by["GEMSDOE25"], by["GEMSDOE28-h27-4"]
    d0 = float(0.2 * (a["n"] - b["n"]) / (b["live"] / a["live"] - 1.0) - 0.2 * b["n"])
    xs = np.array([r["tpw"] / (d0 + 0.2 * r["n"]) for r in arows])
    ys = np.array([r["live"] for r in arows])
    scale = float((xs @ ys) / (xs @ xs))
    assert abs(d0 - exp3u["projection"]["d0"]) < 1e-6 and abs(scale - exp3u["projection"]["scale"]) < 1e-9, \
        "projection fit drift vs H31-U exp3"
    loo_rmse = float(exp3u["projection"]["loo_rmse"])
    h33_sgmc = by["GEMSDOE32-h33-2-b2"]["sgmc_dti"]
    print(f"fit D0={d0:.1f} scale={scale:.4f} loo_rmse={loo_rmse:.4f} H33 SGMC={h33_sgmc:.4f}", flush=True)

    cand = []
    for c in candidates:
        dots, n, h = U.read_dots(str(ROOT / c["file"]), foot)
        ys_, xs_ = np.nonzero(dots)
        cand.append(dict(**c, dots=dots, ys=ys_, xs=xs_, n=n, sha=h,
                         card_obj=json.loads((ROOT / c["card"]).read_text())))
    peers, seen = [], set()
    for peer in U.peer_files():
        try:
            pd_, pn, ph = U.read_dots(peer["path"], foot)
        except Exception:  # noqa: BLE001
            continue
        if ph in seen:
            continue
        seen.add(ph)
        peers.append(dict(id=peer["id"], dots=pd_, n=pn, sha=ph))
    print(f"peers (deduplicated by sha): {len(peers)}", flush=True)
    overlaps = {c["lane"]: {} for c in cand}
    twin_excluded = {c["lane"]: [] for c in cand}
    h33_peer = next(p for p in peers if "h33-h33-2-b2" in p["id"])
    for peer in peers:
        near = None
        for c in cand:
            if c["sha"] == peer["sha"]:
                twin_excluded[c["lane"]].append(peer["id"] + " (identical bytes)")
                continue
            if np.array_equal(c["dots"], peer["dots"]):
                twin_excluded[c["lane"]].append(peer["id"] + " (identical support twin)")
                continue
            if near is None:
                near = uniqueness._near(peer["dots"])
            overlaps[c["lane"]][peer["id"]] = float(near[c["ys"], c["xs"]].mean()) if c["n"] else 0.0
        del near
    phis = {c["lane"]: SA.phi_binary(c["dots"], h33_peer["dots"], foot) for c in cand}
    from scipy.ndimage import gaussian_filter as _gf
    dem = U.clean(U.stack_band("det_elev", foot), foot)
    gy = _gf(dem, sigma=1.0, order=(1, 0), mode="nearest")
    gx = _gf(dem, sigma=1.0, order=(0, 1), mode="nearest")
    slope_deg = np.degrees(np.arctan(np.hypot(gy, gx) / 100.0))
    pied = foot & (slope_deg <= 6.0)
    del dem, gy, gx, slope_deg

    rows = []
    for c in cand:
        conv = "nan-outside" if c["file"].endswith("-nan.tif") else "all-finite"
        v = validate_submission(ROOT / c["file"], sample, convention=conv)
        s = U.sgmc_score(c["dots"], off_sgmc, foot)
        s_pied = U.sgmc_score(c["dots"], off_sgmc & pied, foot)
        s_mtn = U.sgmc_score(c["dots"], off_sgmc & ~pied, foot)
        proj = scale * s["tpw"] / (d0 + 0.2 * s["n_dots"])
        ov = overlaps[c["lane"]]
        worst_id = max(ov, key=ov.get) if ov else None
        if c["lane"] == "H31-Z":
            hold = h31z_holdout(c["card_obj"])
            can = bool(c["card_obj"]["gates"]["G2_canary"])
        else:
            hold = SA.lane_holdout(c["lane"], c["card_obj"])
            can = SA.lane_canary(c["lane"], c["card_obj"])
        gates = dict(
            G1_format=bool(v["ok_to_upload_format_only"]),
            G2_canary=bool(can),
            G3_holdout_efficacy=bool(hold["pass_"]),
            G4_sgmc_discovery=bool(s["dti"] >= h33_sgmc),
            G5_uniqueness_discrete=bool(ov and max(ov.values()) <= 0.70 and abs(phis[c["lane"]]) <= 0.90),
            G6_projection_ge_02778=bool(proj >= 0.2778),
        )
        rows.append(dict(
            lane=c["lane"], file=c["file"], card=c["card"], sha256=c["sha"], n_dots=c["n"],
            on_catalogue_dots=int((c["dots"] & cat).sum()),
            format_ok=v["ok_to_upload_format_only"], hard_failures=v["hard_failures"],
            sgmc=s, sgmc_piedmont_le6deg=s_pied, sgmc_mountain_gt6deg=s_mtn,
            sha256_recorded_in_own_run_card=bool(c["sha"] in json.dumps(c["card_obj"])),
            twin_peers_excluded=twin_excluded[c["lane"]],
            projection=float(proj),
            projection_interval=[float(proj - 2 * loo_rmse), float(proj + 2 * loo_rmse)],
            overlap_vs_h33=float(ov.get(h33_peer["id"], float("nan"))),
            phi_vs_h33=float(phis[c["lane"]]),
            max_discrete_overlap=float(max(ov.values())) if ov else None,
            max_discrete_overlap_peer=worst_id,
            holdout_from_card=hold, canary_from_card=bool(can),
            card_verdict=c["card_obj"].get("verdict"),
            card_slot_approved=c["card_obj"].get("slot_approved"),
            gates=gates, selector_promote=bool(all(gates.values())),
        ))
        print(f"{c['lane']:<18} n={c['n']} SGMC={s['dti']:.4f} TPw={s['tpw']:.0f} PROJ={proj:.4f} "
              f"ovH33={rows[-1]['overlap_vs_h33']:.3f} maxOv={rows[-1]['max_discrete_overlap']:.3f} "
              f"promote={rows[-1]['selector_promote']}", flush=True)

    rows_sorted = sorted(rows, key=lambda r: -r["projection"])
    audit9 = {r["site_tag"]: r for r in json.loads(
        (ROOT / "evidence/nine_site_forensic_audit.json").read_text())["focus_submissions"]}
    near_h33 = uniqueness._near(h33_peer["dots"])
    focus_rows = []
    for tag, (dots, live, _p) in anchors.items():
        ys_, xs_ = np.nonzero(dots)
        ov_h33 = float(near_h33[ys_, xs_].mean())
        focus_rows.append(dict(site_tag=tag, artifact=audit9[tag]["artifact_path"],
                               user_reported=live, dots=int(dots.sum()), overlap_vs_h33_3px=ov_h33,
                               sgmc_dti=by[tag]["sgmc_dti"], duplicate_of_h33_lane=bool(ov_h33 > 0.70),
                               score_label="USER-REPORTED (no organizer receipt)"))
    focus_rows.sort(key=lambda r: -r["user_reported"])
    rep = dict(
        evidence_class="COMPUTED selector audit (no fitting; holdout/canary cited from lane run cards)",
        session_branch=SESSION,
        projection_fit=dict(d0=d0, scale=scale, loo_rmse=loo_rmse, anchors=arows,
                            method="identical to scripts/run_h31u.py projection(); asserted vs exp3.json",
                            label="PROJECTION — never a score; anchors USER-REPORTED"),
        h33_reference=dict(sgmc_dti=h33_sgmc, user_reported=0.2778, peer=h33_peer["id"]),
        peers_checked=len(peers), candidates=rows_sorted, focus_sites=focus_rows,
        promoted=[r["lane"] for r in rows_sorted if r["selector_promote"]],
        caveats=["Projections extrapolate an SGMC-TPw calibration fitted on one dot family (H19-5 "
                 "descendants); cross-family live transfer is unproven.",
                 "Selector G5 implements the owner's duplicate rule on final submitted dots; lane-level "
                 "pre-placement top-K readings stay on lane cards (H31-X 86.3% FAIL, H31-Y 90.5% FAIL, "
                 "H31-Z 62.0% PASS) and are disclosed in the decision.",
                 "Literal 695-raster reading remains failed for every candidate (spacing-5 lattice "
                 "covers 99.87% of footprint within 3 px); disclosed per IR-U-02."],
    )
    out = ROOT / "evidence/selector_audit_20261026_session15e685db.json"
    out.write_text(json.dumps(rep, indent=1, default=float) + "\n")
    prom = sorted((r for r in rows_sorted if r["selector_promote"]), key=lambda r: -r["projection"])
    primary = prom[0] if prom else None
    if primary and primary["lane"] == "H31-T":
        portal_name = "gemsdoe31-h31t-transtension-dinkelbach-20261025-b37654"
        note = ("H31-T analytic-signal+listric+transtension Dinkelbach 37654d B2 | "
                "HOLDOUT-DTI 0.1300 n=60988 | selector G1-G6 pass 83fbc267")
    elif primary:
        card_obj = next(c["card_obj"] for c in cand if c["lane"] == primary["lane"])
        portal_name = card_obj["submission_name"]
        note = card_obj["note"]
    else:
        portal_name, note = None, "no promoted candidate"
    assert len(note) <= 140, len(note)
    zrow = next(r for r in rows_sorted if r["lane"] == "H31-Z")
    xrow = next(r for r in rows_sorted if r["lane"] == "H31-X")
    decision = dict(
        date="2026-10-26", session_branch=SESSION,
        rule="Frozen selector gates G1-G6 (H31-U preregistration; same definitions as historical "
             "selector_audit); uniqueness on discrete peer submissions with literal 695-raster "
             "reading disclosed (IR-U-02, H31-Z preregistration section 2). Primary = highest "
             "PROJECTION among promoted. Supersedes the 9883b598 literal-STOP decision for upload "
             "choice only; that decision is preserved at "
             "evidence/selector_decision_superseded_9883b598.json and its lattice facts are "
             "unchanged and restated below.",
        primary_submission=(dict(
            lane=primary["lane"], file=primary["file"], sha256=primary["sha256"],
            portal_name=portal_name, portal_note=note, portal_note_chars=len(note),
            holdout_dti=primary["holdout_from_card"], sgmc=primary["sgmc"],
            projection=primary["projection"], projection_interval=primary["projection_interval"],
            overlap_vs_h33=primary["overlap_vs_h33"],
            max_discrete_overlap=primary["max_discrete_overlap"],
            verdict="OK TO DOWNLOAD AND SUBMIT (owner uploads manually; repo never contacts DrivenData)",
        ) if primary else None),
        alternates=[dict(lane=r["lane"], file=r["file"], sha256=r["sha256"],
                         projection=r["projection"], sgmc_dti=r["sgmc"]["dti"],
                         overlap_vs_h33=r["overlap_vs_h33"]) for r in prom[1:]],
        promoted_lanes=[r["lane"] for r in prom],
        not_promoted=[dict(lane=r["lane"], failed_gates=[k for k, v in r["gates"].items() if not v],
                           projection=r["projection"]) for r in rows_sorted if not r["selector_promote"]],
        h31x_lane=dict(
            lane_card_verdict=xrow["card_verdict"], selector_promote=xrow["selector_promote"],
            discrepancy_explanation=(
                "H31-X lane card is verdict=negative under its own STRICTER G5 (pre-placement top-K "
                "86.3% vs D1.5 fields). Selector G5 uses final submitted dots (63.1% max, recomputed "
                "today in this audit's candidate rows). Both readings disclosed; lane card unchanged."),
            file=xrow["file"], run_card="evidence/h31x/run_card.json"),
        h31z_new_lane=dict(
            lane_card_verdict=zrow["card_verdict"], selector_promote=zrow["selector_promote"],
            discrepancy_explanation=(
                "H31-Z lane card is verdict=negative SOLELY because its preregistered G3 required "
                "beating the rebuilt H31-X junction (paired delta vs JUNC -0.0040 [-0.0112,+0.0030] "
                "screen; -0.0050 confirmation). Selector G3 (frozen precedent: paired wins vs CTRL/"
                "SLOPE + confirmation vs CTRL) passes. H31-Z is the only recent lane passing BOTH "
                "uniqueness stages (final 60.5%, top-K 62.0%). Lane card unchanged; selector governs "
                "upload choice only."),
            file=zrow["file"], run_card="evidence/h31z/run_card.json"),
        focus_sites=focus_rows,
        literal_695_disclosure="Literal broad-registry reading FAILS for every nonempty candidate: "
                                "the registered spacing-5 lattice is within 3 px of 99.87% of the "
                                "footprint (COMPUTED). Promotions above use discrete-peer uniqueness "
                                "per IR-U-02; under a literal reading the correct action is to "
                                "submit nothing.",
        score_labels="0.2778/0.3195/0.4413 are USER-REPORTED (no organizer receipts); projections are never scores",
        weekly_cap="UNVERIFIED from this sandbox; owner must check the cap on the submission page",
        evidence="evidence/selector_audit_20261026_session15e685db.json",
    )
    (ROOT / "registry/selector_decision_20261026.json").write_text(
        json.dumps(decision, indent=1, default=float) + "\n")
    (ROOT / "registry/selector_decision_20261026_session15e685db.json").write_text(
        json.dumps(decision, indent=1, default=float) + "\n")
    print("wrote", out, "promoted:", rep["promoted"], "primary:", primary["lane"] if primary else None,
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
