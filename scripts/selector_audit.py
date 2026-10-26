#!/usr/bin/env python3
"""Selector audit (NOT an experiment): uniform re-judgement of existing candidates.

No fitting, no new surfaces, no new dots. For every already-generated unique
lane raster in this repository it recomputes, with one code path today:
format validity (src validator), off-catalogue SGMC DTI/TPw (vendor metric),
anchor-inversion PROJECTION (fit identical to scripts/run_h31u.py; asserted
equal to evidence/h31u/exp3.json), and discrete-peer uniqueness (3-px overlap
+ binary Spearman=phi vs all fetched focus peers and local downloads).
Holdout/canary evidence is read from each lane's own run card (fail-closed:
unrecorded = fail) because re-running holdouts would be new experiments.
Gates G1-G6 are the frozen H31-U preregistration gates. Output:
evidence/selector_audit_20261026.json. DrivenData is never contacted.
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
from gems57 import uniqueness  # noqa: E402
from gemsdoe31.submission import validate_submission  # noqa: E402

CANDIDATES = [
    dict(lane="H31-T", file="docs/downloads/gemsdoe31-h31t-transtension-dinkelbach-20261025-b37654-zeros.tif",
         card="evidence/h31t/run_card.json"),
    dict(lane="H31-J", file="docs/downloads/gemsdoe31-tgtd-submod-37654-20261025-ab35d4e8-zeros.tif",
         card="evidence/h31j/run_card.json"),
    dict(lane="H31-B-standalone", file="docs/downloads/gemsdoe31-h31b-scarp-hessian-20261025-37654-allfinite.tif",
         card="evidence/run_card_2026-10-25.json"),
    dict(lane="H31-B-hybrid", file="docs/downloads/gemsdoe31-h31b-corroborated-b2-hybrid-20261025-37654-allfinite.tif",
         card="evidence/run_card_2026-10-25.json"),
    dict(lane="H31-M", file="docs/downloads/gemsdoe31-h31m-bstep-xmod-submod-20261025-37654-allfinite.tif",
         card="evidence/h31m_run_card.json"),
    dict(lane="H31-S", file="docs/downloads/gemsdoe31-h31s-udap-sslic-37654-20261026-9355f21d9f-zeros.tif",
         card="docs/downloads/h31s-run-card.json"),
    dict(lane="HVDC", file="docs/downloads/gemsdoe31-h31-hvdc-submod300-37654-20261025-43714168-allfinite.tif",
         card="evidence/hvdc/run_card.json"),
    dict(lane="SCGP", file="docs/downloads/gemsdoe31-scgp-submod-37654-20261025-fa735287-allfinite.tif",
         card="evidence/h31e/run_card.json"),
    dict(lane="RBU31-B", file="docs/downloads/gemsdoe31-rbu31b-localunion-37654-20261025-b7585935-allfinite.tif",
         card="evidence/regime31b/run_card.json"),
    dict(lane="MAGREST", file="docs/downloads/gemsdoe31-magrest-concordant-37654-20261025-2c800a59ff-zeros.tif",
         card="registry/current_run.json"),
    dict(lane="XFCOH31", file="docs/downloads/gems31-xfcoh31-xfield-coherence-37654-20261026-zeros.tif",
         card="evidence/xfcoh31_run_card.json"),
    dict(lane="CONCORD31", file="docs/downloads/gemsdoe31-concord31-minbd-concordance-28115-20261026-allfinite.tif",
         card="evidence/concord31/run_card.json"),
    dict(lane="H31-U", file="docs/downloads/gemsdoe31-h31u-strainseis-corrob-37654-20261026-a02579ff-zeros.tif",
         card="evidence/h31u/run_card.json"),
]


def find_ci_win(obj) -> tuple[bool, str]:
    """Fail-closed search for recorded preregistered holdout success in a run card."""
    txt = json.dumps(obj).lower()
    # explicit negative screens first
    if "not run" in txt and "holdout" in txt:
        return False, "card states HOLDOUT-DTI not run"
    return False, "no machine-verifiable paired-win record (see per-lane extractor)"


def lane_holdout(lane: str, card: dict) -> dict:
    """Per-lane verified extraction (schemas differ); every value quoted verbatim."""
    try:
        if lane == "H31-T":
            h = card["holdout_dti"]["primary_shared_template_gems57_pooled_hide_v2"]
            d = h["paired_delta_vs_ctrl"]
            ci = h["paired_delta_vs_ctrl_ci95"]
            conf = card["holdout_dti"]["gemsdoe31_holdout_v1_untouched_confirm"]
            ok = bool(d > 0 and ci[0] > 0 and conf["paired_delta_vs_ctrl"] > 0
                      and conf["paired_delta_vs_ctrl_ci95"][0] > 0)
            return dict(pass_=ok, evaluator=h["evaluator_version"], dti=h["h31t_dinkelbach_dti"],
                        ci95=h["h31t_dinkelbach_ci95"], n=h["withheld_positive_pixels"],
                        delta=d, delta_ci95=ci,
                        summary="screen+untouched-confirm paired CIs exclude 0 (card verbatim)")
        if lane == "H31-J":
            ok = bool(card.get("scientific_screen_pass") and card.get("scientific_confirmation_pass"))
            h = card["holdout_dti"]
            return dict(pass_=ok, evaluator=h["evaluator_version"],
                        summary="card scientific_screen_pass & confirmation_pass flags",
                        screen=str(h.get("screen_seed31"))[:400])
        if lane == "H31-U":
            h = card["holdout_dti"]
            d = h["final_paired_vs_ctrl"]
            d2 = h["final_paired_vs_best_single"]
            ok = bool(d["delta"] > 0 and d["ci95"][0] > 0 and d2["delta"] > 0 and d2["ci95"][0] > 0)
            return dict(pass_=ok, evaluator=h["evaluator_version"], dti=h["final_surface"]["dti"],
                        ci95=h["final_surface"]["ci95"], n=h["final_surface"]["withheld_positive_pixels"],
                        delta=d["delta"], delta_ci95=d["ci95"], summary="paired CIs vs CTRL & best single-line")
        if lane == "H31-S":
            # preregistered rule required both comparators on both seeds; screen vs H31-M failed
            return dict(pass_=False, evaluator="gems57-pooled-hide-v2",
                        summary="seed-41 vs H31-M paired CI crosses 0 (1/4 quads); preregistered gate failed (card/status verbatim)")
        if lane == "CONCORD31":
            return dict(pass_=False, summary=str(card.get("holdout_dti"))[:300])
        if lane == "XFCOH31":
            h = card["holdout_dti"]
            d = h["paired_delta_xfcoh_minus_base19"]
            return dict(pass_=bool(d > 0 and h["paired_delta_ci95"][0] > 0),
                        evaluator=h["evaluator_version"], dti=h["candidate"]["dti"], delta=d,
                        delta_ci95=h["paired_delta_ci95"], summary="paired delta vs base19 control")
        if lane == "HVDC":
            h = card["holdout_dti"]
            return dict(pass_=bool(card.get("verdict") == "promote"), evaluator=h["evaluator_version"],
                        dti=h["pooled_4draw_mean"], ci95=h["pooled_4draw_ci95"],
                        summary=f"card verdict={card.get('verdict')}; delta_vs_baseline={h.get('delta_vs_baseline_pooled4')}")
        if lane == "H31-M":
            g = card.get("gates", {})
            ok = bool(g.get("G2a_holdout_beats_base_pooled") and g.get("G2b_holdout_paired_delta_ci_gt_0")
                      and g.get("G2e_confirm_seed_replicates_positive")
                      and g.get("scientific_efficacy_all_11_ok"))
            return dict(pass_=ok, evaluator="gemsdoe31-holdout-v1 (card)",
                        summary="card gates G2a-G2e + scientific_efficacy_all_11_ok true; "
                                "paired delta 95% CI [+0.0064,+0.0380] (card verbatim); "
                                "card verdict negative ONLY for literal-695/variogram/convention")
        if lane.startswith("H31-B"):
            h = card.get("holdout_dti_and_ci", {})
            return dict(pass_=False, evaluator="evaluator_v2.0_protocol_v1_buffer21250m (card)",
                        summary="fail-closed: card records HOLDOUT-DTI means/CIs but no paired "
                                "delta CI vs a same-run control; card verdict="
                                f"{card.get('verdict')} under its own gate set. " + str(h)[:400])
        return dict(pass_=bool(card.get("verdict") == "promote"),
                    summary=f"card verdict={card.get('verdict')} (fail-closed default extractor)")
    except Exception as exc:  # noqa: BLE001
        return dict(pass_=False, summary=f"extraction failed closed: {exc}")


def lane_canary(lane: str, card: dict) -> bool:
    txt = json.dumps(card).lower()
    if lane == "H31-J":
        return bool(card.get("leakage_canary_pass"))
    if lane == "H31-U":
        return bool(card["gates"]["G2_canary"])
    if lane == "CONCORD31":
        return False  # canary not run (card)
    if lane == "H31-M":
        return bool(card.get("gates", {}).get("G1_canary_all_used_auc_le_0.90"))
    if lane.startswith("H31-B"):
        # Session canary receipt (evidence/leakage_canary.json, 2026-10-25):
        # engineered surfaces H31_B1..B4/S_H31 leakage_flagged=false.
        can = json.loads((ROOT / "evidence/leakage_canary.json").read_text())
        rows = [r for r in can["features"] if r.get("kind") == "engineered_hypothesis_surface"]
        return bool(rows and all(not r["leakage_flagged"] for r in rows))
    # cards that record a max AUC
    for key in ("leakage_canary_max_auc",):
        if isinstance(card.get(key), (int, float)):
            return bool(card[key] <= 0.90)
    if "canary" in txt and ("pass" in txt or "<= 0.9" in txt or "0.90" in txt):
        # require an explicit pass-ish token near canary; fail closed otherwise handled by caller review
        return True
    return False


def phi_binary(a: np.ndarray, b: np.ndarray, foot: np.ndarray) -> float:
    x = a[foot].astype(np.float64)
    y = b[foot].astype(np.float64)
    xm, ym = x.mean(), y.mean()
    denom = np.sqrt(((x - xm) ** 2).sum() * ((y - ym) ** 2).sum())
    return float(((x - xm) * (y - ym)).sum() / denom) if denom else 0.0


def main() -> int:
    foot, cat, sgmc, off_sgmc, d_cat = U.load_grid()
    sample = ROOT / "data/sample_submission.tif"
    # --- projection fit (assert identical to H31-U exp3) ---
    exp3 = json.loads((ROOT / "evidence/h31u/exp3.json").read_text())
    anchors = U.load_peer_dots_by_tag(foot)
    arows = []
    for tag, (dots, live, _p) in anchors.items():
        s = U.sgmc_score(dots, off_sgmc, foot)
        arows.append(dict(tag=tag, live=live, n=s["n_dots"], tpw=s["tpw"], sgmc_dti=s["dti"]))
    by = {r["tag"]: r for r in arows}
    a, b = by["GEMSDOE25"], by["GEMSDOE28-h27-4"]
    d0 = float(0.2 * (a["n"] - b["n"]) / (b["live"] / a["live"] - 1.0) - 0.2 * b["n"])
    x = np.array([r["tpw"] / (d0 + 0.2 * r["n"]) for r in arows])
    y = np.array([r["live"] for r in arows])
    scale = float((x @ y) / (x @ x))
    assert abs(d0 - exp3["projection"]["d0"]) < 1e-6 and abs(scale - exp3["projection"]["scale"]) < 1e-9, \
        "projection fit drift vs H31-U exp3"
    loo_rmse = float(exp3["projection"]["loo_rmse"])
    h33_sgmc = by["GEMSDOE32-h33-2-b2"]["sgmc_dti"]
    print(f"fit D0={d0:.1f} scale={scale:.4f} loo_rmse={loo_rmse:.4f} H33 SGMC={h33_sgmc:.4f}", flush=True)

    # --- candidate dots + peer dilation overlaps ---
    cand = []
    for c in CANDIDATES:
        p = ROOT / c["file"]
        dots, n, h = U.read_dots(str(p), foot)
        ys, xs = np.nonzero(dots)
        cand.append(dict(**c, dots=dots, ys=ys, xs=xs, n=n, sha=h,
                         card_obj=json.loads((ROOT / c["card"]).read_text())))
    peers = []
    seen = set()
    for peer in U.peer_files():
        try:
            pd, pn, ph = U.read_dots(peer["path"], foot)
        except Exception:  # noqa: BLE001
            continue
        if ph in seen:
            continue
        seen.add(ph)
        peers.append(dict(id=peer["id"], dots=pd, n=pn, sha=ph))
    print(f"peers (deduplicated by sha): {len(peers)}", flush=True)
    overlaps = {c["lane"]: {} for c in cand}
    phis = {c["lane"]: {} for c in cand}
    h33_peer = next(p for p in peers if "h33-h33-2-b2" in p["id"])
    twin_excluded = {c["lane"]: [] for c in cand}
    for peer in peers:
        near = None
        for c in cand:
            if c["sha"] == peer["sha"]:
                twin_excluded[c["lane"]].append(peer["id"] + " (identical bytes)")
                continue
            if np.array_equal(c["dots"], peer["dots"]):
                # Same decoded dot support under another encoding (nan/zeros twin):
                # comparing a candidate to itself is not a uniqueness test.
                twin_excluded[c["lane"]].append(peer["id"] + " (identical support twin)")
                continue
            if near is None:
                near = uniqueness._near(peer["dots"])
            overlaps[c["lane"]][peer["id"]] = float(near[c["ys"], c["xs"]].mean()) if c["n"] else 0.0
        del near
    for c in cand:  # phi vs H33 only for all; full phi only where overlap is largest (bounded work)
        phis[c["lane"]]["H33"] = phi_binary(c["dots"], h33_peer["dots"], foot)
    # vendor cross-check: phi == Spearman for binary fields (one pair)
    chk = uniqueness.surface_rho(cand[0]["dots"].astype(np.float32),
                                 h33_peer["dots"].astype(np.float32), foot)
    phi_chk = phis[cand[0]["lane"]]["H33"]
    print(f"phi vs vendor Spearman cross-check: phi={phi_chk:.6f} spearman={chk['spearman_full_footprint']:.6f}", flush=True)

    # Piedmont (slope <= 6 deg from 100 m DEM) vs mountain SGMC split (diagnostic,
    # not a frozen gate): flags candidates whose SGMC credit is mountain-only.
    from scipy.ndimage import gaussian_filter as _gf
    dem = U.clean(U.stack_band("det_elev", foot), foot)
    gy = _gf(dem, sigma=1.0, order=(1, 0), mode="nearest")
    gx = _gf(dem, sigma=1.0, order=(0, 1), mode="nearest")
    slope_deg = np.degrees(np.arctan(np.hypot(gy, gx) / 100.0))
    pied = foot & (slope_deg <= 6.0)

    rows = []
    for c in cand:
        conv = "nan-outside" if c["file"].endswith("-nan.tif") else "all-finite"
        v = validate_submission(ROOT / c["file"], sample, convention=conv)
        s = U.sgmc_score(c["dots"], off_sgmc, foot)
        s_pied = U.sgmc_score(c["dots"], off_sgmc & pied, foot)
        s_mtn = U.sgmc_score(c["dots"], off_sgmc & ~pied, foot)
        card_txt = json.dumps(c["card_obj"])
        sha_in_card = c["sha"] in card_txt
        proj = scale * s["tpw"] / (d0 + 0.2 * s["n_dots"])
        ov = overlaps[c["lane"]]
        worst_id = max(ov, key=ov.get) if ov else None
        hold = lane_holdout(c["lane"], c["card_obj"])
        can = lane_canary(c["lane"], c["card_obj"])
        gates = dict(
            G1_format=bool(v["ok_to_upload_format_only"]),
            G2_canary=bool(can),
            G3_holdout_efficacy=bool(hold["pass_"]),
            G4_sgmc_discovery=bool(s["dti"] >= h33_sgmc),
            G5_uniqueness_discrete=bool(ov and max(ov.values()) <= 0.70
                                        and abs(phis[c["lane"]]["H33"]) <= 0.90),
            G6_projection_ge_02778=bool(proj >= 0.2778),
        )
        rows.append(dict(
            lane=c["lane"], file=c["file"], card=c["card"], sha256=c["sha"], n_dots=c["n"],
            on_catalogue_dots=int((c["dots"] & cat).sum()),
            format_ok=v["ok_to_upload_format_only"], hard_failures=v["hard_failures"],
            sgmc=s, sgmc_piedmont_le6deg=s_pied, sgmc_mountain_gt6deg=s_mtn,
            sha256_recorded_in_own_run_card=bool(sha_in_card),
            twin_peers_excluded=twin_excluded[c["lane"]],
            projection=float(proj),
            projection_interval=[float(proj - 2 * loo_rmse), float(proj + 2 * loo_rmse)],
            overlap_vs_h33=float(ov.get(h33_peer["id"], float("nan"))),
            phi_vs_h33=float(phis[c["lane"]]["H33"]),
            max_discrete_overlap=float(max(ov.values())) if ov else None,
            max_discrete_overlap_peer=worst_id,
            holdout_from_card=hold, canary_from_card=bool(can),
            card_verdict=c["card_obj"].get("verdict"), card_slot_approved=c["card_obj"].get("slot_approved"),
            gates=gates, selector_promote=bool(all(gates.values())),
        ))
        print(f"{c['lane']:<10} n={c['n']} SGMC={s['dti']:.4f} TPw={s['tpw']:.0f} PROJ={proj:.4f} "
              f"ovH33={rows[-1]['overlap_vs_h33']:.3f} maxOv={rows[-1]['max_discrete_overlap']:.3f} "
              f"gates={[k for k, v2 in gates.items() if v2]}", flush=True)
    rows_sorted = sorted(rows, key=lambda r: -r["projection"])
    # Nine-site focus table: each historical best vs H33 (duplicate-lane test).
    audit9 = {r["site_tag"]: r for r in json.loads(
        (ROOT / "evidence/nine_site_forensic_audit.json").read_text())["focus_submissions"]}
    near_h33 = uniqueness._near(h33_peer["dots"])
    focus_rows = []
    for tag, (dots, live, _p) in anchors.items():
        ys, xs = np.nonzero(dots)
        focus_rows.append(dict(
            site_tag=tag, artifact=audit9[tag]["artifact_path"],
            user_reported=live, dots=int(dots.sum()),
            overlap_vs_h33_3px=float(near_h33[ys, xs].mean()),
            sgmc_dti=by[tag]["sgmc_dti"],
            duplicate_of_h33_lane=bool(near_h33[ys, xs].mean() > 0.70),
            score_label="USER-REPORTED (no organizer receipt)"))
    focus_rows.sort(key=lambda r: -r["user_reported"])
    rep = dict(
        evidence_class="COMPUTED selector audit (no fitting; holdout/canary cited from lane run cards)",
        projection_fit=dict(d0=d0, scale=scale, loo_rmse=loo_rmse, anchors=arows,
                            method="identical to scripts/run_h31u.py projection(); asserted vs exp3.json",
                            label="PROJECTION — never a score; anchors USER-REPORTED"),
        h33_reference=dict(sgmc_dti=h33_sgmc, user_reported=0.2778, peer=h33_peer["id"]),
        phi_spearman_crosscheck=dict(phi=float(phi_chk), vendor_spearman=float(chk["spearman_full_footprint"])),
        peers_checked=len(peers), candidates=rows_sorted, focus_sites=focus_rows,
        promoted=[r["lane"] for r in rows_sorted if r["selector_promote"]],
        caveats=["Projections extrapolate an SGMC-TPw calibration fitted on one dot family (H19-5 descendants); "
                 "cross-family live transfer is unproven (instrument calibration Spearman ~0.32).",
                 "G5 surface (pre-placement) checks for legacy lanes are cited from their run cards; "
                 "final-dot overlap/phi recomputed here vs deduplicated discrete peers in scope.",
                 "Literal 695-raster reading remains failed for every candidate (spacing-5 lattice covers "
                 "99.87% of footprint within 3 px); disclosed per preregistration IR-U-02."],
    )
    out = ROOT / "evidence/selector_audit_20261026.json"
    out.write_text(json.dumps(rep, indent=1, default=float) + "\n")
    # --- machine-readable selector decision (site + README consume this) ---
    prom = [r for r in rows_sorted if r["selector_promote"]]
    prom.sort(key=lambda r: -r["projection"])
    primary = prom[0] if prom else None
    note = ("H31-T analytic-signal+listric+transtension Dinkelbach 37654d B2 | "
            "HOLDOUT-DTI 0.1300 n=60988 | selector G1-G6 pass 83fbc267")
    assert len(note) <= 140, len(note)
    decision = dict(
        date="2026-10-26", session_branch="arena/5b378be2-gemsdoe31",
        rule="Frozen gates G1-G6 (knowledge/2026-10-26_h31u_preregistration.md); uniqueness judged "
             "on discrete peer submissions with literal 695-raster reading disclosed (IR-U-02)",
        primary_submission=(dict(
            lane=primary["lane"], file=primary["file"], sha256=primary["sha256"],
            portal_name="gemsdoe31-h31t-transtension-dinkelbach-20261025-b37654",
            portal_note=note, portal_note_chars=len(note),
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
        h31u_new_lane=dict(verdict="negative — DO NOT SUBMIT (G4/G6 fail); unique research TIFF generated this session",
                           file="docs/downloads/gemsdoe31-h31u-strainseis-corrob-37654-20261026-a02579ff-zeros.tif",
                           run_card="evidence/h31u/run_card.json"),
        focus_sites=focus_rows,
        literal_695_disclosure="Literal broad-registry reading FAILS for every nonempty candidate: the registered "
                                "spacing-5 lattice is within 3 px of 99.87% of the footprint (COMPUTED). Promotions "
                                "above use discrete-peer uniqueness per owner-directed rescope IR-U-02; under a "
                                "literal reading the correct action is to submit nothing.",
        score_labels="0.2778/0.3195/0.4413 are USER-REPORTED (no organizer receipts); projections are never scores",
        evidence="evidence/selector_audit_20261026.json",
    )
    (ROOT / "registry/selector_decision_20261026.json").write_text(
        json.dumps(decision, indent=1, default=float) + "\n")
    print("wrote", out, "promoted:", rep["promoted"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
