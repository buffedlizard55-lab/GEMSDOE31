#!/usr/bin/env python3
"""Byte-level forensics for the 0.2778 GEMSDOE32 file (research audit only; no score is computed here).

The owner's leaderboard list names ``gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros``. The
registry row (``registry/focus_review.json``) names the ``-nan`` sibling. This script:

1. fetches both GEMSDOE32 variants at the commits that last changed them (pinned, hash-checked),
   the GEMSDOE25 D2.8 parent raster (pinned commit, hash-checked), the local H27-4 raster, and the
   restored catalogue ``data/labels.tif`` (hash-checked against ``registry/data_manifest.json``);
2. checks the dot-set chain D2.8 (44,090) -> H27-4 (40,199) -> H33-2-B2 (37,654) by set inclusion;
3. measures how far each removed dot lies from the catalogue, testing the registry claim
   "D2.8 with <=2 px catalogue-flank dots deleted";
4. checks that the two GEMSDOE32 variants are identical inside the footprint and differ only outside it.

Evidence class: COMPUTED from pinned bytes. Scores are USER-REPORTED and are copied, never computed.
Run: ``python scripts/verify_gemsdoe32_forensics.py``. Writes
``evidence/review_48c411be/gemsdoe32_forensics.json``.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from download_competition_data import _download  # noqa: E402

CACHE = ROOT / ".cache" / "focus-sites" / "forensics"
OUT = ROOT / "evidence" / "review_48c411be" / "gemsdoe32_forensics.json"
SCHEMA_VERSION = 1

# Pinned sources. Each entry: (label, repo, commit, repo path, sha256 expected).
REMOTE = {
    "gemsdoe32_zeros": (
        "buffedlizard55-lab/GEMSDOE32",
        "c39ee46ea79812d8de7de9c037685a709ba2aa87",  # last commit touching the -zeros file (2026-10-04)
        "docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif",
        "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9",
    ),
    "gemsdoe32_nan": (
        "buffedlizard55-lab/GEMSDOE32",
        "9863c82a7c7dc283c615b711bab941debaff0ec4",  # registry source_ref for the -nan row
        "docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-nan.tif",
        "baeae3219bba6a19bc8cfe79224e28555c50184b7c1ca65c2a822f54807c77dd",
    ),
    "gemsdoe25_d28": (
        "buffedlizard55-lab/GEMSDOE25",
        "2a279dd0d2a4319c1022567876eb4c97553e2d13",  # registry source_ref for the GEMSDOE25 D2.8 row
        "docs/downloads/gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif",
        "91eae1ca42ec845eaa8c2ba32da49806e24751743459b8a10017c479bbe639b8",
    ),
}
LOCAL = {
    "h27_4_local": ROOT / "docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif",
    "labels_local": ROOT / "data/labels.tif",
}
LABELS_SHA256 = "7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093"
TWO_PX = 2.0
OVERLAP_PX = 3.0


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch(label: str) -> Path:
    repo, commit, remote, expected = REMOTE[label]
    dest = CACHE / f"{label}.tif"
    if not (dest.is_file() and sha256_file(dest).startswith(expected[:16])):
        dest.parent.mkdir(parents=True, exist_ok=True)
        partial = dest.with_name(dest.name + ".partial")
        partial.unlink(missing_ok=True)
        _download(repo, commit, remote, partial)
        partial.replace(dest)
    digest = sha256_file(dest)
    if not digest.startswith(expected[:16]):
        raise ValueError(f"{label}: sha256 {digest} does not match pinned prefix {expected[:16]}")
    return dest


def read_dots(path: Path) -> tuple[np.ndarray, np.ndarray, dict]:
    with rasterio.open(path) as ds:
        values = ds.read(1).astype(np.float64)
        meta = {"crs": ds.crs.to_string(), "shape": list(ds.shape), "dtype": ds.dtypes[0],
                "transform": list(ds.transform)[:6], "nodata": ds.nodata}
    finite = np.isfinite(values)
    dots = np.nan_to_num(values, nan=0.0) > 0
    meta.update({"finite_pixels": int(finite.sum()), "nan_pixels": int((~finite).sum()),
                 "dot_pixels": int(dots.sum()),
                 "values_unique_finite": [float(v) for v in np.unique(values[finite])][:5]})
    return dots, finite, meta


def dist_stats(values: np.ndarray) -> dict:
    if values.size == 0:
        return {"n": 0}
    return {"n": int(values.size), "min": float(values.min()), "median": float(np.median(values)),
            "max": float(values.max()), "share_le_2px": float((values <= TWO_PX + 1e-9).mean())}


def main() -> int:
    labels_path = LOCAL["labels_local"]
    if sha256_file(labels_path) != LABELS_SHA256:
        raise ValueError("data/labels.tif does not match registry/data_manifest.json sha256")
    labels = rasterio.open(labels_path).read(1)
    catalogue = np.nan_to_num(labels.astype(np.float64), nan=0.0) > 0

    h27_path = LOCAL["h27_4_local"]
    paths = {key: fetch(key) for key in REMOTE}
    rasters = {key: read_dots(path) for key, path in paths.items()}
    rasters["h27_4_local"] = read_dots(h27_path)
    rasters["h27_4_local"][2]["sha256"] = sha256_file(h27_path)

    z_dots, z_fin, z_meta = rasters["gemsdoe32_zeros"]
    n_dots, n_fin, n_meta = rasters["gemsdoe32_nan"]
    a_dots, a_fin, a_meta = rasters["gemsdoe25_d28"]
    h_dots, h_fin, h_meta = rasters["h27_4_local"]

    # Distance (px, Euclidean) from every pixel to the nearest catalogue pixel. The transform input
    # is True where the pixel is NOT a catalogue pixel, so the result is the distance to the catalogue.
    dist_to_cat = distance_transform_edt(~catalogue)

    removed_a_minus_b = a_dots & ~n_dots
    removed_a_minus_h = a_dots & ~h_dots
    removed_h_minus_b = h_dots & ~n_dots

    chain = {
        "B_subset_of_H27": bool(np.all(h_dots[n_dots])),
        "H27_subset_of_D28": bool(np.all(a_dots[h_dots])),
        "B_subset_of_D28": bool(np.all(a_dots[n_dots])),
        "removed_D28_to_B": int(removed_a_minus_b.sum()),
        "removed_D28_to_H27": int(removed_a_minus_h.sum()),
        "removed_H27_to_B": int(removed_h_minus_b.sum()),
    }

    d_removed = dist_to_cat[removed_a_minus_b]
    d_kept = dist_to_cat[n_dots]
    d_all_d28 = dist_to_cat[a_dots]
    d_removed_h = dist_to_cat[removed_a_minus_h]

    claim_check = {
        "registry_claim": "D2.8 with <=2 px catalogue-flank dots deleted",
        "d28_dots_within_2px_of_catalogue": int((d_all_d28 <= TWO_PX + 1e-9).sum()),
        "removed_dots_within_2px_of_catalogue": int((d_removed <= TWO_PX + 1e-9).sum()),
        "removed_dots_total": int(d_removed.size),
        "claim_holds_exactly": bool(np.array_equal(
            a_dots & (dist_to_cat > TWO_PX + 1e-9), n_dots)),
    }

    dots_on_catalogue = {
        "B_dots_on_catalogue": int((n_dots & catalogue).sum()),
        "D28_dots_on_catalogue": int((a_dots & catalogue).sum()),
        "H27_dots_on_catalogue": int((h_dots & catalogue).sum()),
    }

    variant = {
        "identical_inside_footprint": bool(np.array_equal(z_dots[n_fin], n_dots[n_fin])
                                           and np.array_equal(z_fin, np.ones_like(z_fin, dtype=bool))),
        "zeros_variant_nan_pixels": int(z_meta["nan_pixels"]),
        "zeros_variant_outside_footprint_values": sorted({float(v) for v in
                                                          np.unique(z_dots[~n_fin].astype(np.float64))}),
        "nan_variant_outside_footprint_is_nan": bool(np.all(~n_fin[~n_fin])),
        "footprint_pixels": int(n_fin.sum()),
    }

    # Radius ladder: delete D2.8 dots within r px of the catalogue and compare with the repo files.
    ladder = {}
    for radius in (1.0, 1.5, 2.0, 3.0):
        removed_r = a_dots & (dist_to_cat <= radius + 1e-9)
        kept_r = a_dots & ~removed_r
        ladder[str(radius)] = {
            "removed": int(removed_r.sum()),
            "kept": int(kept_r.sum()),
            "equals_H27_4_file": bool(np.array_equal(kept_r, h_dots)),
            "equals_H33_2_B2_file": bool(np.array_equal(kept_r, n_dots)),
        }
    # Overlap of the hypothetical 3 px variant with the GEMSDOE32 dots (same 3 px rule as the gate).
    v_dots = n_dots & ~(dist_to_cat <= 3.0 + 1e-9)
    vr, vc = np.nonzero(v_dots)
    br, bc = np.nonzero(n_dots)
    tree_b = cKDTree(np.column_stack([br, bc]).astype(np.float32))
    dist_v, _ = tree_b.query(np.column_stack([vr, vc]).astype(np.float32), distance_upper_bound=OVERLAP_PX + 1e-6)
    radius3_variant = {
        "dots_removed_from_B": int(n_dots.sum() - v_dots.sum()),
        "dots_remaining": int(v_dots.sum()),
        "share_within_3px_of_GEMSDOE32": float((dist_v <= OVERLAP_PX).mean()),
        "duplicate_by_70pct_rule": bool((dist_v <= OVERLAP_PX).mean() > 0.70),
    }

    out = {
        "schema_version": SCHEMA_VERSION,
        "evidence_class": "COMPUTED from pinned bytes; scores are USER-REPORTED (not copied into this file as scores)",
        "scope": "Audit of the GEMSDOE32 0.2778 claim. No new raster, no experiment, no submission, no leaderboard contact.",
        "sources": {
            "gemsdoe32_zeros": {"repo": REMOTE["gemsdoe32_zeros"][0], "commit": REMOTE["gemsdoe32_zeros"][1],
                                "path": REMOTE["gemsdoe32_zeros"][2], "sha256": sha256_file(paths["gemsdoe32_zeros"])},
            "gemsdoe32_nan": {"repo": REMOTE["gemsdoe32_nan"][0], "commit": REMOTE["gemsdoe32_nan"][1],
                              "path": REMOTE["gemsdoe32_nan"][2], "sha256": sha256_file(paths["gemsdoe32_nan"])},
            "gemsdoe25_d28": {"repo": REMOTE["gemsdoe25_d28"][0], "commit": REMOTE["gemsdoe25_d28"][1],
                              "path": REMOTE["gemsdoe25_d28"][2], "sha256": sha256_file(paths["gemsdoe25_d28"])},
            "h27_4_local": {"path": str(h27_path.relative_to(ROOT)), "sha256": sha256_file(h27_path)},
            "labels_local": {"path": "data/labels.tif", "sha256": LABELS_SHA256,
                             "note": "restored from owner mirror by verify_current_run.py --restore-small-inputs"},
        },
        "grids": {"gemsdoe32_zeros": z_meta, "gemsdoe32_nan": n_meta, "gemsdoe25_d28": a_meta,
                  "h27_4_local": h_meta},
        "dot_counts": {"D28": int(a_dots.sum()), "H27_4": int(h_dots.sum()), "H33_2_B2": int(n_dots.sum())},
        "chain": chain,
        "catalogue_pixels": int(catalogue.sum()),
        "dots_on_catalogue": dots_on_catalogue,
        "removed_distance_to_catalogue_px_D28_to_B": dist_stats(d_removed),
        "removed_distance_to_catalogue_px_D28_to_H27": dist_stats(d_removed_h),
        "kept_distance_to_catalogue_px_B": dist_stats(d_kept),
        "claim_check": claim_check,
        "variant_check": variant,
        "radius_ladder_D28": ladder,
        "radius_3px_variant_of_GEMSDOE32": radius3_variant,
        "reported_scores_USER_REPORTED_not_verified": {
            "GEMSDOE32": "0.2778 (leaderboard list; file named -zeros)",
            "note": "Copied from the owner list only. No organizer receipt exists.",
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"chain": chain, "claim_check": claim_check, "variant_check": variant}, indent=2))
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
