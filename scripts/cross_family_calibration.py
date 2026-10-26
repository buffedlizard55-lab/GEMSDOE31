#!/usr/bin/env python3
"""Cross-family calibration audit for live-score estimation (diagnostic, not an experiment).

The selector projection used by earlier sessions fits live = scale * SGMC_TPw / (D0 + 0.2 n)
on eleven anchors that are all descendants of one surface family (H19-5 -> D2.8 -> prunes).
This script tests that formula out-of-family against every matched USER-REPORTED live value in
evidence/instrument_calibration.json, and fits simple leave-one-out linear calibrations on the
same cross-family rows. Output: evidence/cross_family_calibration_20261026.json.

Mechanical exclusions (applied to the cross-family evaluation set, listed in the output):
dots outside [10k, 130k]; submissions whose fragment names the SGMC/geologic-map proxy itself
(their SGMC-DTI is not a predictor but the embedded raster).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import LeaveOneOut, cross_val_predict

ROOT = Path(__file__).resolve().parents[1]
D0 = 10694.644444444453      # selector_audit_20261026.json projection_fit
SCALE = 0.9275488479808367   # ibid.


def metrics(y: np.ndarray, p: np.ndarray) -> dict:
    e = y - p
    return dict(n=int(len(y)), rmse=float(np.sqrt(np.mean(e**2))), mae=float(np.mean(np.abs(e))),
                bias=float(np.mean(p - y)), max_abs_err=float(np.max(np.abs(e))),
                frac_within_0p02=float(np.mean(np.abs(e) <= 0.02)))


def loo_linear(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, dict]:
    pred = cross_val_predict(LinearRegression(), x, y, cv=LeaveOneOut())
    full = LinearRegression().fit(x, y)
    coef = dict(intercept=float(full.intercept_), coef=[float(c) for c in full.coef_])
    return pred, coef


def main() -> None:
    cal = json.loads((ROOT / "evidence/instrument_calibration.json").read_text())
    rows = cal["rows"]
    excluded, keep = [], []
    for r in rows:
        frag = r["fragment"].lower()
        if not (10_000 <= r["dots"] <= 130_000):
            excluded.append(dict(fragment=r["fragment"], reason="dots outside [10k,130k]"))
        elif "sgmc" in frag or "geologic-map" in frag:
            excluded.append(dict(fragment=r["fragment"], reason="literal SGMC/geologic-map proxy raster"))
        else:
            keep.append(r)
    y = np.array([r["live_user_reported"] for r in keep])
    n_dots = np.array([r["dots"] for r in keep], float)
    sgmc_tpw = np.array([r["sgmc_credit_per_dot"] * r["dots"] for r in keep])

    # M1: selector in-family formula, applied out-of-family with its frozen constants
    p_m1 = SCALE * sgmc_tpw / (D0 + 0.2 * n_dots)

    # M2/M3: LOO linear calibrations on cross-family rows
    feats = {
        "M2_credit_per_dot": np.array([[r["sgmc_credit_per_dot"]] for r in keep]),
        "M3_credit_coverage_logdots": np.array(
            [[r["sgmc_credit_per_dot"], r["coverage_3px"], np.log(r["dots"])] for r in keep]),
        "M4_credit_coverage_gap_logdots": np.array(
            [[r["sgmc_credit_per_dot"], r["coverage_3px"], r["gap_DTI"], np.log(r["dots"])]
             for r in keep]),
    }
    out_models = {"M1_selector_formula_frozen": dict(coef=dict(d0=D0, scale=SCALE),
                                                     **metrics(y, p_m1))}
    preds = {"M1_selector_formula_frozen": p_m1}
    for name, x in feats.items():
        p, coef = loo_linear(x, y)
        preds[name] = p
        out_models[name] = dict(coef_loo_fullfit=coef, **metrics(y, p))
    out_models["M0_mean"] = metrics(y, np.full_like(y, y.mean()))

    # zero-catalogue-dots subset (comparable dotted fields), same M1 test + M3 LOO
    sub = [i for i, r in enumerate(keep) if r["dots_on_catalogue"] == 0]
    ys = y[sub]
    p_sub_m3, coef_sub = loo_linear(feats["M3_credit_coverage_logdots"][sub], ys)
    subset = dict(n=len(sub),
                  M1=metrics(ys, p_m1[sub]),
                  M3=dict(coef_loo_fullfit=coef_sub, **metrics(ys, p_sub_m3)))

    # named counterexamples (M1 projection vs USER-REPORTED live)
    want = ("gate_ortho", "sgmc-off-catalogue", "h18-4", "cvarlw", "h42-submission", "r12-scarp")
    counter = []
    for i, r in enumerate(keep):
        if any(w in r["fragment"] for w in want):
            counter.append(dict(fragment=r["fragment"], site=r["site"], dots=r["dots"],
                                sgmc_dti=r["sgmc_DTI"], live_user_reported=r["live_user_reported"],
                                m1_projection=float(p_m1[i]),
                                m3_loo=float(preds["M3_credit_coverage_logdots"][i])))
    # also the excluded literal-proxy rows under M1 (reductio ad absurdum)
    reductio = []
    for r in rows:
        frag = r["fragment"].lower()
        if ("sgmc" in frag or "geologic-map" in frag) and 10_000 <= r["dots"] <= 130_000:
            tpw = r["sgmc_credit_per_dot"] * r["dots"]
            reductio.append(dict(fragment=r["fragment"], live_user_reported=r["live_user_reported"],
                                 m1_projection=float(SCALE * tpw / (D0 + 0.2 * r["dots"]))))

    out = dict(
        evidence_class="COMPUTED diagnostic on USER-REPORTED live values; not an experiment; "
                       "every output is a PROJECTION, never a score",
        source_rows="evidence/instrument_calibration.json",
        n_rows_total=len(rows), n_kept=len(keep), excluded=excluded,
        models=out_models, zero_catalogue_subset=subset,
        counterexamples=counter, reductio_literal_proxy_rows=reductio,
        per_row=[dict(fragment=r["fragment"], site=r["site"], dots=r["dots"],
                      live_user_reported=r["live_user_reported"],
                      sgmc_credit_per_dot=r["sgmc_credit_per_dot"], coverage_3px=r["coverage_3px"],
                      gap_dti=r["gap_DTI"],
                      **{k: float(v[i]) for k, v in preds.items()})
                 for i, r in enumerate(keep)],
        use="For a new candidate with (credit_per_dot, coverage_3px, log dots), the honest central "
            "estimate is the zero-catalogue-subset M3 full-fit prediction; the honest interval is "
            "+/- 2 x its LOO RMSE. The M1 in-family value is an upper-bound diagnostic only.",
    )
    dest = ROOT / "evidence/cross_family_calibration_20261026.json"
    dest.write_text(json.dumps(out, indent=1) + "\n")
    for name, m in out_models.items():
        print(f"{name:32s} n={m['n']} RMSE={m['rmse']:.4f} MAE={m['mae']:.4f} bias={m['bias']:+.4f}")
    print("zero-cat subset:", json.dumps({k: subset[k] for k in ("n",)}, indent=0),
          "M1 RMSE", round(subset["M1"]["rmse"], 4), "M3 RMSE", round(subset["M3"]["rmse"], 4))
    for c in counter + reductio:
        print("counterexample:", c)
    print("wrote", dest.relative_to(ROOT))


if __name__ == "__main__":
    main()
