#!/usr/bin/env python3
"""Independently re-verify the top artifact of each requested focus site (learning/audit only).

For the nine focus sites in ``registry/focus_review.json`` this script:

1. takes the highest USER-REPORTED row per site (the claim value is copied, never scored here),
2. fetches that exact published file at its pinned commit over github.com (reusing
   ``download_competition_data._download``; bytes go to the git-ignored ``.cache/focus-sites``),
3. checks SHA-256 against the registry, grid (EPSG:32611, 3730x3292, 100 m, template transform),
   dtype, band count, finite/NaN convention, and value range [0, 1],
4. recomputes the pairwise 3-px dot overlap (same rule as ``gate.uniqueness_report``: share of
   candidate dots within 3 px of any dot of the other raster) and the Spearman rank correlation of
   5-px block densities (same as ``gate.spearman_blocks``).

Writes ``evidence/review_cc130eb1/focus_site_verification.json``. Nothing here is a leaderboard
score: the only score-like numbers are the USER-REPORTED claims copied from the registry.
Run: ``python scripts/verify_focus_sites.py``.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from download_competition_data import _download  # noqa: E402
from gemsdoe31.gate import block_density, footprint_blocks, spearman_blocks  # noqa: E402

CACHE = ROOT / ".cache" / "focus-sites"
OUT = ROOT / "evidence" / "review_cc130eb1" / "focus_site_verification.json"
TEMPLATE = {
    "crs": "EPSG:32611",
    "shape": (3730, 3292),
    "transform": (100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0),
}
OVERLAP_PX = 3.0
VACUOUS_CHANCE = 0.50  # gate.py: a registry raster this dense makes the raw overlap rule meaningless
DUPLICATE_OVERLAP = 0.70
DUPLICATE_RHO = 0.90
REGISTRY_SHA_KEY = "sha256"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def top_rows(registry: dict) -> list[dict]:
    """Highest USER-REPORTED row per focus site (ties kept in registry order)."""
    best: dict[str, dict] = {}
    for row in registry["rows"]:
        value = float(row["claim_value"])
        current = best.get(row["repository"])
        if current is None or value > float(current["claim_value"]):
            best[row["repository"]] = row
    return [best[name] for name in sorted(best)]


def published_path(source_url: str, source_ref: str) -> str:
    marker = f"/blob/{source_ref}/"
    if marker not in source_url:
        raise ValueError(f"source_url does not pin {source_ref}: {source_url}")
    return source_url.split(marker, 1)[1]


def fetch(row: dict) -> Path:
    dest = CACHE / row["repository"] / Path(row["artifact"]).name
    if not (dest.is_file() and sha256_file(dest) == row[REGISTRY_SHA_KEY]):
        dest.parent.mkdir(parents=True, exist_ok=True)
        partial = dest.with_name(dest.name + ".partial")
        partial.unlink(missing_ok=True)
        _download(f"buffedlizard55-lab/{row['repository']}", row["source_ref"],
                  published_path(row["source_url"], row["source_ref"]), partial)
        partial.replace(dest)
    return dest


def describe(path: Path) -> dict:
    with rasterio.open(path) as src:
        values = src.read(1).astype(np.float64)
        info = {
            "shape": list(src.shape),
            "crs": src.crs.to_string() if src.crs else None,
            "transform": list(src.transform)[:6],
            "dtype": src.dtypes[0],
            "bands": src.count,
            "nodata_tag": src.nodata,
        }
    nan = np.isnan(values)
    finite = ~nan
    inside = finite
    info.update({
        "nan_pixels": int(nan.sum()),
        "finite_pixels": int(finite.sum()),
        "min_finite": float(values[finite].min()) if finite.any() else None,
        "max_finite": float(values[finite].max()) if finite.any() else None,
        "values_in_0_1": bool(finite.any() and values[finite].min() >= 0.0 and values[finite].max() <= 1.0),
        "positive_pixels": int(np.count_nonzero(np.nan_to_num(values, nan=0.0) > 0)),
        "nonzero_values_outside_finite": 0,
    })
    info["grid_matches_template"] = (
        info["crs"] == TEMPLATE["crs"]
        and tuple(info["shape"]) == TEMPLATE["shape"]
        and tuple(info["transform"]) == TEMPLATE["transform"]
    )
    dots = np.nan_to_num(values, nan=0.0) > 0
    return {"info": info, "dots": dots, "footprint": inside}


def chance_points(footprint: np.ndarray, seed: int = 20261029) -> np.ndarray:
    """Same random-footprint baseline as gate.uniqueness_report (200k points, fixed seed)."""
    rng = np.random.default_rng(seed)
    fr, fc = np.nonzero(footprint)
    pick = rng.choice(fr.size, size=min(200_000, fr.size), replace=False)
    return np.column_stack([fr[pick], fc[pick]]).astype(np.float32)


def directional(dots_a: np.ndarray, dots_b: np.ndarray, points: np.ndarray) -> dict:
    """Share of A's dots within 3 px of B's dots, raw and chance-adjusted (gate.uniqueness_report rule)."""
    rows, cols = np.nonzero(dots_a)
    orow, ocol = np.nonzero(dots_b)
    tree = cKDTree(np.column_stack([orow, ocol]).astype(np.float32))
    dist, _ = tree.query(np.column_stack([rows, cols]).astype(np.float32),
                         distance_upper_bound=OVERLAP_PX + 1e-6)
    raw = float((dist <= OVERLAP_PX).mean()) if rows.size else 0.0
    chance = float((tree.query(points, distance_upper_bound=OVERLAP_PX + 1e-6)[0] <= OVERLAP_PX).mean())
    adjusted = (raw - chance) / (1.0 - chance) if chance < 1.0 else 0.0
    vacuous = chance >= VACUOUS_CHANCE
    return {"raw": raw, "chance": chance, "adjusted": adjusted, "vacuous": vacuous,
            "decisive": adjusted if vacuous else raw}


def pairwise(name_a: str, a: dict, name_b: str, b: dict, domain: np.ndarray,
             points: np.ndarray) -> dict:
    """Both directions; a_in_b is the gate's raw share of A's dots within 3 px of B's dots."""
    ab = directional(a["dots"], b["dots"], points)
    ba = directional(b["dots"], a["dots"], points)
    rho = spearman_blocks(block_density(a["dots"]), block_density(b["dots"]), domain)
    decisive = max(ab["decisive"], ba["decisive"])
    raw_max = max(ab["raw"], ba["raw"])
    return {"a": name_a, "b": name_b,
            "overlap_3px_a_within_b": round(ab["raw"], 6),
            "chance_overlap_3px_of_b": round(ab["chance"], 6),
            "adjusted_overlap_3px": round(ab["adjusted"], 6),
            "raw_rule_vacuous": bool(ab["vacuous"]),
            "decisive_overlap": round(ab["decisive"], 6),
            "overlap_3px_b_within_a": round(ba["raw"], 6),
            "chance_overlap_3px_of_a": round(ba["chance"], 6),
            "adjusted_overlap_3px_b_within_a": round(ba["adjusted"], 6),
            "decisive_overlap_b_within_a": round(ba["decisive"], 6),
            "max_decisive_overlap_either_direction": round(decisive, 6),
            "max_raw_overlap_either_direction": round(raw_max, 6),
            "spearman_5px_blocks": round(rho, 6),
            "duplicate_by_overlap_rule": bool(decisive > DUPLICATE_OVERLAP),
            # Conservative companion: gate.py sets adjusted=0 when chance==1.0, so a raster that covers
            # every random point passes the chance-adjusted rule even if its dots are identical.
            "duplicate_by_raw_overlap_conservative": bool(raw_max > DUPLICATE_OVERLAP),
            "duplicate_by_rank_rule": bool(abs(rho) > DUPLICATE_RHO)}


def main() -> int:
    registry = json.loads((ROOT / "registry" / "focus_review.json").read_text())
    rows = top_rows(registry)
    results, loaded = [], {}
    for row in rows:
        path = fetch(row)
        fresh = describe(path)
        digest = sha256_file(path)
        loaded[row["repository"]] = fresh
        results.append({
            "site": row["repository"],
            "claim_value_USER_REPORTED": row["claim_value"],
            "score_evidence_class": "USER-REPORTED; NOT ORGANIZER-CONFIRMED",
            "artifact": row["artifact"],
            "source_url": row["source_url"],
            "sha256_recomputed": digest,
            "sha256_registry": row[REGISTRY_SHA_KEY],
            "sha256_match": digest == row[REGISTRY_SHA_KEY],
            "positive_pixels_recomputed": fresh["info"]["positive_pixels"],
            "positive_pixels_registry": row["positive_pixels"],
            "format": fresh["info"],
        })
    footprint = np.zeros(TEMPLATE["shape"], dtype=bool)
    for item in loaded.values():
        footprint |= item["footprint"]
    domain = footprint_blocks(footprint)
    names = [r["repository"] for r in rows]
    points = chance_points(footprint)
    matrix = []
    for i, na in enumerate(names):
        for nb in names[i + 1:]:
            matrix.append(pairwise(na, loaded[na], nb, loaded[nb], domain, points))
    worst = sorted(matrix, key=lambda m: -m["max_decisive_overlap_either_direction"])[:5]
    doc = {
        "schema_version": 1,
        "scope": "Top USER-REPORTED artifact per focus site (9 sites), re-fetched at pinned commits",
        "evidence_class": "COMPUTED from pinned GitHub bytes; scores are USER-REPORTED claims",
        "organizer_receipt": None,
        "overlap_rule": ("share of candidate dots within 3 px (Euclidean) of any dot of the other raster; "
                         "chance-adjusted (random footprint baseline) when the other raster covers >= 50% by chance"),
        "rank_rule": "Spearman over 5 px block densities on the union finite footprint",
        "thresholds": {"overlap": DUPLICATE_OVERLAP, "rho": DUPLICATE_RHO},
        "sites": results,
        "pairwise": matrix,
        "highest_pairwise": worst,
        "pairs_flagged_duplicate_by_overlap": sum(m["duplicate_by_overlap_rule"] for m in matrix),
        "pairs_flagged_duplicate_by_rank": sum(m["duplicate_by_rank_rule"] for m in matrix),
        "pairs_flagged_duplicate_by_raw_overlap_conservative": sum(
            m["duplicate_by_raw_overlap_conservative"] for m in matrix),
        "pairs_total": len(matrix),
        "all_sha256_match": all(r["sha256_match"] for r in results),
        "all_grid_match_template": all(r["format"]["grid_matches_template"] for r in results),
        "all_values_in_0_1": all(r["format"]["values_in_0_1"] for r in results),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(f"sites={len(results)} sha_match={doc['all_sha256_match']} grid={doc['all_grid_match_template']} "
          f"range01={doc['all_values_in_0_1']} pairs={len(matrix)} "
          f"dup_overlap={doc['pairs_flagged_duplicate_by_overlap']} dup_rank={doc['pairs_flagged_duplicate_by_rank']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
