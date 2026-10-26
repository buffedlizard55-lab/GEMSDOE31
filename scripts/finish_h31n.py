#!/usr/bin/env python3
"""Finish H31-N packaging from the preregistered full-catalogue fit.

The screen holdout already ran. This does not refit folds and does not tune.
The submission model uses seed 31026 directly (the screen had already advanced
that stream, so this fit is the explicitly seeded submission model, not a
continuation). A TIFF is written only if final Poisson dots pass the scientific
70% / 0.90 gates. The lattice gate cannot be passed; ok_to_submit stays false.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "vendor"), str(ROOT / "scripts")]

from gems57.submission_writer import write_submission  # noqa: E402
from gemsdoe31.emission import emit_dots  # noqa: E402
from gemsdoe31.h31n_pseudogravity import FEATURE_NAMES, pseudogravity_features  # noqa: E402
from run_h31n import (  # noqa: E402
    BUDGET,
    SEED,
    SEPARATION_PX,
    compare,
    fit_hgb,
    load_band,
    load_grid,
    log,
    predict_surface,
    sha256_file,
    stack_rows,
    train_indices,
)


def main() -> int:
    grid = load_grid()
    fp, cat = grid.footprint, grid.catalogue
    novel_map = pseudogravity_features(load_band(2), load_band(13), load_band(3), fp)
    novel = [novel_map[name] for name in FEATURE_NAMES]
    bands = [load_band(i) for i in range(1, 20)]
    rng = np.random.default_rng(SEED)
    idx = train_indices(cat, fp & ~cat, rng)
    model = fit_hgb(stack_rows(bands, novel, list(range(23)), idx), cat.ravel()[idx].astype(np.int8))
    surface = predict_surface(model, bands, novel, list(range(23)), fp.shape)
    d_cat = distance_transform_edt(~cat)
    valid = fp & (d_cat > 2.0)
    dots = emit_dots(surface, valid, max_dots=BUDGET, min_distance_px=SEPARATION_PX)
    log(f"emitted {int(dots.sum())} dots, on catalogue {int((dots & cat).sum())}")
    final = compare(surface, dots, fp)
    ranked = sorted(
        [r for r in final["rows"] if r.get("dot_overlap_3px") is not None],
        key=lambda r: r["dot_overlap_3px"], reverse=True,
    )
    for row in ranked[:8]:
        log(f"  overlap {row['dot_overlap_3px']:.3f} rho {row['abs_spearman']} {row['file']}")
    card_path = ROOT / "evidence/h31n/run_card.json"
    card = json.loads(card_path.read_text())
    card["submission_model"] = {
        "seed": SEED,
        "note": "Explicit seed 31026. Not the RNG state left after the screen folds.",
    }
    card["final_dot_gate"] = {
        "worst_abs_spearman": final["worst_abs_spearman"],
        "worst_dot_overlap_3px": final["worst_dot_overlap_3px"],
        "scientific_duplicate": final["scientific_duplicate"],
        "top": ranked[:8],
    }
    (ROOT / "evidence/h31n/uniqueness_rows.json").write_text(json.dumps(final["rows"], indent=1) + "\n")
    if final["scientific_duplicate"]:
        card["verdict"] = "negative"
        card["stop"] = "scientific duplicate on final Poisson dots"
        card["ok_to_download_for_research"] = False
        card["ok_to_submit"] = False
        card["slot_approved"] = False
        card_path.write_text(json.dumps(card, indent=1, allow_nan=False) + "\n")
        log("DUPLICATE STOP — no TIFF")
        return 3
    array_hash = hashlib.sha256(np.packbits(dots.ravel()).tobytes()).hexdigest()[:8]
    name = f"gemsdoe31-h31n-pseudograv-37654-20261026-{array_hash}"
    screen = card["holdout_dti"]["screen"]["dti"]
    base = card["holdout_dti"]["control"]["dti"]
    note = (
        f"H31-N pseudogravity residual 37654d | HOLDOUT-DTI {screen:.4f} vs base {base:.4f} | "
        f"DO NOT SUBMIT {array_hash}"
    )
    zeros = np.where(fp, dots.astype(np.float32), 0.0).astype(np.float32)
    path = ROOT / "docs/downloads" / f"{name}-zeros.tif"
    receipt = write_submission(
        path, zeros, ROOT / "data/sample_submission.tif", fp,
        note=note, name=name, catalogue=cat,
        metadata={"lane": "H31-N", "slot_approved": False},
    )
    nan_path = path.with_name(f"{name}-nan.tif")
    nan_values = np.where(fp, zeros, np.nan).astype(np.float32)
    with rasterio.open(ROOT / "data/sample_submission.tif") as sample:
        profile = sample.profile.copy()
    profile.update(dtype="float32", count=1, nodata=None, compress="deflate")
    with rasterio.open(nan_path, "w", **profile) as dst:
        dst.write(nan_values, 1)
    card.update({
        "verdict": "negative",
        "stop": None,
        "ok_to_download_for_research": True,
        "ok_to_submit": False,
        "slot_approved": False,
        "submission_name": name,
        "note": note,
        "note_chars": len(note),
        "raster_sha256": receipt["sha256"],
        "validator": receipt["validator"],
        "artifacts": {
            "zeros_tif": str(path.relative_to(ROOT)),
            "zeros_zip": str(path.with_suffix(".zip").relative_to(ROOT)),
            "zeros_sha256": receipt["sha256"],
            "nan_tif": str(nan_path.relative_to(ROOT)),
            "nan_sha256": sha256_file(nan_path),
            "dots": int(dots.sum()),
            "dots_on_catalogue": int((dots & cat).sum()),
        },
        "why_not_submit": [
            "HOLDOUT-DTI did not beat the same-run base-19 control (paired CI includes 0 and is negative).",
            "Variogram for this method was unstable, so the 25 km collar is not an empirical range.",
            "Literal spacing-5 lattice covers 99.871% of the footprint within 3 px; overlap gate cannot pass.",
            "No organizer receipt. No weekly slot is authorized.",
        ],
    })
    card_path.write_text(json.dumps(card, indent=1, allow_nan=False) + "\n")
    (ROOT / "docs/downloads" / f"{name}-run-card.json").write_text(json.dumps(card, indent=1, allow_nan=False) + "\n")
    log(f"wrote {path.name} sha {receipt['sha256']} ok_to_submit=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
