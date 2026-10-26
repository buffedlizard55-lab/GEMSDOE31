#!/usr/bin/env python3
"""CONCORD31 (1 of max 3 experiments this session): cross-arm concordance emission.

Hypothesis: cells where the LiDAR-only OOF arm (B) AND the LiDAR+radiometric OOF
arm (D) independently agree (surface = min(B,D)) mark faults corroborated by two
sensor domains; emitting ONLY from that concordance surface -- no incumbent
H27/H33/D2.8 dots copied -- yields a unique dot set targeting catalogue-missing
faults. Non-fault mimic: coincident LiDAR artefact + radiometric soil-moisture
edge (e.g. playa margins, field boundaries).
Inputs are the pinned OOF maps in evidence/oof/ (u16 quantised). No new data.
Holdout/leakage gates need labels/catalogue rasters in data/ (absent; Dropbox
host not reachable from this sandbox) -> recorded NOT RUN, verdict stays negative.
"""
from __future__ import annotations
import hashlib, json, zipfile
from pathlib import Path
import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
DL = ROOT / "docs/downloads"
NAME = "gemsdoe31-concord31-minbd-concordance-28115-20261026"
BUDGET, SPACING = 37654, 2.8

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main() -> None:
    b = np.load(ROOT / "evidence/oof/oof_B_19_plus_lidar_u16.npz")["probability_u16"].astype(np.float32) / 65535
    d = np.load(ROOT / "evidence/oof/oof_D_19_plus_lidar_radiometric_u16.npz")["probability_u16"].astype(np.float32) / 65535
    templ = DL / "gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif"
    with rasterio.open(templ) as ds:
        prof, t = ds.profile.copy(), ds.read(1)
    foot = np.isfinite(t)
    surf = np.minimum(b, d); surf[~foot] = 0.0
    # Poisson-disk emission: rank by concordance, accept if >=SPACING from accepted
    cand = np.flatnonzero((surf >= 0.35) & foot)
    cand = cand[np.argsort(-surf.ravel()[cand])]
    dots = np.zeros(surf.shape, bool); occ = np.zeros(surf.shape, bool)
    r = int(np.ceil(SPACING))
    for f in cand:
        y, x = divmod(int(f), surf.shape[1])
        y0, y1, x0, x1 = max(0, y - r), min(surf.shape[0], y + r + 1), max(0, x - r), min(surf.shape[1], x + r + 1)
        yy, xx = np.mgrid[y0:y1, x0:x1]
        if occ[y0:y1, x0:x1][(yy - y) ** 2 + (xx - x) ** 2 < SPACING ** 2].any():
            continue
        occ[y0:y1, x0:x1][(yy - y) ** 2 + (xx - x) ** 2 < SPACING ** 2] = True
        dots[y, x] = True
        if dots.sum() >= BUDGET:
            break
    n = int(dots.sum()); print("dots", n)
    # --- registry gates: Spearman (surface & dots) + 3px overlap vs every local registry tif ---
    rng = np.random.default_rng(31); sample = rng.choice(np.flatnonzero(foot), 200_000, replace=False)
    reg = {}
    for p in sorted(DL.rglob("*.tif")):
        if NAME in p.name: continue
        with rasterio.open(p) as ds:
            a = ds.read(1)
        if a.shape != surf.shape: continue
        regdots = (a == 1) & foot
        dist = distance_transform_edt(~regdots)
        ov = float((dist[dots] <= 3).mean()) if n else 0.0
        rho_s = float(spearmanr(surf.ravel()[sample], np.where(np.isfinite(a), a, 0).ravel()[sample]).statistic)
        rho_d = float(spearmanr(dots.ravel()[sample].astype(float), np.where(np.isfinite(a), a, 0).ravel()[sample]).statistic)
        reg[p.name] = {"dots": int(regdots.sum()), "final_3px_overlap": ov,
                       "surface_spearman_rho": rho_s, "final_spearman_rho": rho_d}
    worst_ov = max(reg.values(), key=lambda v: v["final_3px_overlap"])
    worst_rho = max((abs(v["surface_spearman_rho"]) for v in reg.values()), default=0)
    duplicate = (worst_ov["final_3px_overlap"] > 0.70) or (worst_rho > 0.90)
    # --- write portal-safe all-finite primary (zeros outside) + NaN variant + zip ---
    out = np.where(dots, 1.0, 0.0).astype(np.float32); out[~foot] = 0.0
    prof.update(dtype="float32", count=1, nodata=None)
    p_fin = DL / f"{NAME}-allfinite.tif"
    with rasterio.open(p_fin, "w", **prof) as ds: ds.write(out, 1)
    outn = out.copy(); outn[~foot] = np.nan
    prof.update(nodata=float("nan"))
    p_nan = DL / f"{NAME}-nan.tif"
    with rasterio.open(p_nan, "w", **prof) as ds: ds.write(outn, 1)
    p_zip = DL / f"{NAME}-allfinite.zip"
    with zipfile.ZipFile(p_zip, "w", zipfile.ZIP_DEFLATED) as z: z.write(p_fin, p_fin.name)
    # --- validator (no human inspection) ---
    def validate(path, outside):
        with rasterio.open(path) as ds: a, pr = ds.read(1), ds.profile
        inside = a[foot]
        return {"file": path.name, "sha256": sha(path), "bytes": path.stat().st_size,
                "crs": str(pr["crs"]), "shape": list(a.shape), "dtype": str(a.dtype),
                "nan_inside_footprint": int((~np.isfinite(inside)).sum()),
                "values_in_0_1": bool(np.isfinite(inside).all() and inside.min() >= 0 and inside.max() <= 1),
                "outside": outside, "positive_pixels": int((inside == 1).sum()),
                "pass": bool(np.isfinite(inside).all() and inside.min() >= 0 and inside.max() <= 1)}
    v_fin, v_nan = validate(p_fin, "zeros"), validate(p_nan, "nan")
    card = {
        "hypothesis": "CONCORD31: min(B,D) cross-arm (LiDAR-only x LiDAR+radiometric) OOF concordance marks two-domain-corroborated catalogue-missing faults",
        "mechanism": f"surface=min(B,D) from pinned evidence/oof u16 maps; Poisson-disk emission spacing {SPACING}px, budget {BUDGET}; zero incumbent dots copied",
        "named_non_fault_mimic": "coincident LiDAR artefact + radiometric soil-moisture/playa-margin edge",
        "holdout_dti": "HOLDOUT-DTI: NOT RUN - labels/catalogue/SGMC rasters absent from data/ (Dropbox host unreachable from sandbox); no number claimed",
        "leakage_canary": "NOT RUN - same missing truth rasters; AUC<=0.90 gate unverified, blocks promotion",
        "correlation_overlap_vs_registry": {"scope": f"{len(reg)} local docs/downloads rasters (NOT global)",
            "max_surface_abs_spearman_rho": worst_rho, "max_final_3px_overlap": worst_ov["final_3px_overlap"],
            "worst_overlap_file": max(reg, key=lambda k: reg[k]['final_3px_overlap']), "duplicate_stop": bool(duplicate), "per_file": reg},
        "raster_sha256": v_fin["sha256"], "validator_output": {"allfinite": v_fin, "nan": v_nan},
        "submission_name": NAME, "note_max_140": "CONCORD31 min(B,D) concordance dots 37.6k, no incumbent dots; UNVALIDATED holdout - research only"[:140],
        "verdict": "negative", "ok_to_download_for_research": True, "ok_to_submit": False,
        "experiments_used_this_session": "1 of 3 (protocol budget)", "organizer_confirmed_score": None}
    outdir = ROOT / "evidence/concord31"; outdir.mkdir(exist_ok=True)
    (outdir / "run_card.json").write_text(json.dumps(card, indent=1) + "\n")
    (DL / f"{NAME}-format-check.json").write_text(json.dumps({"allfinite": v_fin, "nan": v_nan, "duplicate_stop": duplicate}, indent=1) + "\n")
    print(json.dumps({"dots": n, "duplicate_stop": duplicate, "worst_overlap": worst_ov, "sha": v_fin["sha256"]}, indent=1))

if __name__ == "__main__":
    main()
