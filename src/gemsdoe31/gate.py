"""Automated submission gates: format, range, catalogue masking, uniqueness, evidence, provenance.

Legacy diagnostic only: its density-exempt, block-rank comparison is NOT the
current literal any-registry surface-and-final test. G8 fails closed, so this
entry point cannot issue upload permission. Historical receipts are unchanged.
Use registry/release_status.json for the current release decision. A local format
pass never verifies organizer acceptance or estimates a leaderboard score.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import numpy as np
import rasterio
from scipy.spatial import cKDTree
from scipy.stats import rankdata

from .submission import sha256_file, validate_submission

GATE_VERSION = "GATE-2-legacy-diagnostic-only"
DUPLICATE_OVERLAP = 0.70       # more than this share of candidate dots within OVERLAP_PX of one registry raster
OVERLAP_PX = 3.0
DUPLICATE_RHO = 0.90           # Spearman of 500 m block densities
VACUOUS_CHANCE = 0.50          # a registry raster this dense makes the raw overlap rule meaningless
BLOCK_PX = 5
NOTE_MAX = 140
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{7,119}$")


def read_dots(path: str | Path) -> np.ndarray:
    with rasterio.open(path) as src:
        values = src.read(1)
    return np.nan_to_num(values, nan=0.0) > 0


def block_density(dots: np.ndarray, block: int = BLOCK_PX) -> np.ndarray:
    h, w = dots.shape
    hb, wb = -(-h // block), -(-w // block)
    rows, cols = np.nonzero(dots)
    counts = np.bincount((rows // block) * wb + cols // block, minlength=hb * wb)
    return counts.reshape(hb, wb).astype(np.float32)


def spearman_blocks(a: np.ndarray, b: np.ndarray, domain: np.ndarray) -> float:
    x, y = rankdata(a[domain]), rankdata(b[domain])
    x, y = x - x.mean(), y - y.mean()
    denom = float(np.sqrt((x * x).sum() * (y * y).sum()))
    return float((x * y).sum() / denom) if denom else 0.0


def footprint_blocks(footprint: np.ndarray, block: int = BLOCK_PX) -> np.ndarray:
    h, w = footprint.shape
    hb, wb = -(-h // block), -(-w // block)
    rows, cols = np.nonzero(footprint)
    counts = np.bincount((rows // block) * wb + cols // block, minlength=hb * wb).reshape(hb, wb)
    return counts > (block * block) // 2


def match_scores(registry: list[dict], scores: list[dict]) -> tuple[dict[str, float], list[str], list[str]]:
    """Map registry ``cache_name`` -> USER-REPORTED live score by exact name fragment.

    A fragment matching several *distinct* dot sets is ambiguous and is skipped (never guessed).
    Returns (mapping, ambiguous_fragments, unmatched_fragments).
    """
    mapping: dict[str, float] = {}
    ambiguous, unmatched = [], []
    for ent in scores:
        frag = ent["fragment"].lower()
        hits = [e for e in registry if any(frag in n.lower() for n in [e["path"]] + [v.split(":", 1)[1] for v in e["variants"]])]
        if not hits:
            unmatched.append(ent["fragment"])
        elif len({h["dot_set_sha256"] for h in hits}) > 1:
            ambiguous.append(ent["fragment"])
        else:
            for h in hits:
                mapping[h["cache_name"]] = ent["score"]
    return mapping, ambiguous, unmatched


def uniqueness_report(dots: np.ndarray, registry: list[dict], cache_dir: Path, footprint: np.ndarray,
                      *, seed: int = 20261025, scores: dict[str, float] | None = None) -> dict:
    """Compare a dot set with every registry raster. Dot rasters are read from ``cache_dir`` by ``cache_name``."""
    rng = np.random.default_rng(seed)
    fr, fc = np.nonzero(footprint)
    pick = rng.choice(fr.size, size=min(200_000, fr.size), replace=False)
    chance_points = np.column_stack([fr[pick], fc[pick]]).astype(np.float32)
    rows, cols = np.nonzero(dots)
    cand_points = np.column_stack([rows, cols]).astype(np.float32)
    cand_density = block_density(dots)
    domain = footprint_blocks(footprint)
    exact_dot_hash = hashlib.sha256(np.flatnonzero(dots.ravel()).astype(np.uint32).tobytes()).hexdigest()
    report_rows, missing = [], []
    for entry in registry:
        path = cache_dir / entry["cache_name"]
        if not path.is_file():
            missing.append(entry["cache_name"])
            continue
        other = read_dots(path)
        orow, ocol = np.nonzero(other)
        if orow.size == 0:
            continue
        tree = cKDTree(np.column_stack([orow, ocol]).astype(np.float32))
        raw = float((tree.query(cand_points, distance_upper_bound=OVERLAP_PX + 1e-6)[0] <= OVERLAP_PX).mean())
        chance = float((tree.query(chance_points, distance_upper_bound=OVERLAP_PX + 1e-6)[0] <= OVERLAP_PX).mean())
        adjusted = (raw - chance) / (1.0 - chance) if chance < 1.0 else 0.0
        vacuous = chance >= VACUOUS_CHANCE
        rho = spearman_blocks(cand_density, block_density(other), domain)
        report_rows.append({
            "registry_file": entry["path"], "repo": entry["repo"], "registry_dots": int(orow.size),
            "user_reported_score": (scores or {}).get(entry["cache_name"]), "overlap_3px": raw, "chance_overlap_3px": chance,
            "adjusted_overlap": adjusted, "raw_rule_vacuous": bool(vacuous), "spearman_500m": rho,
            "duplicate_by_overlap": bool((adjusted if vacuous else raw) > DUPLICATE_OVERLAP),
            "duplicate_by_rank_correlation": bool(rho > DUPLICATE_RHO),
            "identical_dot_set": entry["dot_set_sha256"] == exact_dot_hash})
    nearest = sorted(report_rows, key=lambda r: -r["spearman_500m"])[:5]
    worst_overlap = sorted(report_rows, key=lambda r: -(r["adjusted_overlap"] if r["raw_rule_vacuous"] else r["overlap_3px"]))[:5]
    return {
        "registry_rasters_compared": len(report_rows), "registry_rasters_missing": len(missing),
        "dot_set_sha256": exact_dot_hash,
        "identical_dot_set_in_registry": any(r["identical_dot_set"] for r in report_rows),
        "duplicates_by_overlap": [r["registry_file"] for r in report_rows if r["duplicate_by_overlap"]],
        "duplicates_by_rank_correlation": [r["registry_file"] for r in report_rows if r["duplicate_by_rank_correlation"]],
        "max_spearman_500m": max((r["spearman_500m"] for r in report_rows), default=None),
        "max_overlap_3px_non_vacuous": max((r["overlap_3px"] for r in report_rows if not r["raw_rule_vacuous"]), default=None),
        "max_adjusted_overlap": max((r["adjusted_overlap"] for r in report_rows), default=None),
        "vacuous_raw_rule_registry_rasters": sum(r["raw_rule_vacuous"] for r in report_rows),
        "nearest_by_rank_correlation": nearest, "highest_overlap": worst_overlap,
        "rows": report_rows,
    }


MIN_NEIGHBOUR_RHO = 0.50


def neighbour_projection(report: dict, k: int = 5) -> dict:
    """Mean user-reported live score of the k most similar *scored* registry rasters. A PROJECTION, never a score.

    Only neighbours with block-density Spearman >= MIN_NEIGHBOUR_RHO count; below that there is no comparable
    scored file and the honest output is "no projection" (extrapolation).
    """
    scored = [r for r in report["rows"] if r["user_reported_score"] is not None and r["spearman_500m"] >= MIN_NEIGHBOUR_RHO]
    top = sorted(scored, key=lambda r: -r["spearman_500m"])[:k]
    if not top:
        return {"label": "NEIGHBOUR-PROJECTION (not a score)", "available": False,
                "reason": f"no scored registry raster with 500 m-block Spearman >= {MIN_NEIGHBOUR_RHO}: extrapolation, no projection"}
    return {"label": "NEIGHBOUR-PROJECTION (not a score)", "available": True, "k": len(top),
            "mean_user_reported_live_score_of_neighbours": float(np.mean([r["user_reported_score"] for r in top])),
            "neighbours": [{"file": r["registry_file"], "spearman_500m": r["spearman_500m"],
                            "user_reported_score": r["user_reported_score"]} for r in top],
            "caveat": "neighbours are chosen by block-density similarity only; the scores are USER-REPORTED and unreceipted"}


def _fmt(value) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def gate(name: str, ok: bool, detail: str, *, hard: bool = True) -> dict:
    return {"pass": bool(ok), "hard": hard, "detail": detail}


def run_gate(*, tif: Path, template: Path, labels: Path, registry_path: Path, cache_dir: Path, convention: str,
             name: str, note: str, evidence_path: Path | None, procedure_sha256: str | None,
             used_names: set[str], scores_path: Path | None = None) -> dict:
    gates: dict[str, dict] = {}
    fmt = validate_submission(tif, template, convention=convention)
    gates["G1_format_grid_footprint"] = gate("format", fmt["ok_to_upload_format_only"],
                                             f"convention={convention}; hard failures: {fmt['hard_failures'] or 'none'}")
    with rasterio.open(tif) as src:
        values = src.read(1)
        nodata = src.nodata
    with rasterio.open(template) as src:
        footprint = np.isfinite(src.read(1))
    inside = values[footprint]
    gates["G2_range_0_1_no_nan_inside"] = gate(
        "range", bool(np.isfinite(inside).all() and inside.min() >= 0.0 and inside.max() <= 1.0),
        f"footprint cells {inside.size:,}; min={float(np.nanmin(inside)):.6g}; max={float(np.nanmax(inside)):.6g}; "
        f"non-finite={int((~np.isfinite(inside)).sum())}; nodata tag={nodata}")
    if convention == "all-finite":
        gates["G2b_whole_array_finite_in_0_1"] = gate(
            "whole-array", bool(np.isfinite(values).all() and values.min() >= 0.0 and values.max() <= 1.0),
            "every one of the 12,279,160 cells is finite and within [0,1] (defends against a whole-raster range check)")
    with rasterio.open(labels) as src:
        catalogue = src.read(1) == 1
    dots = np.nan_to_num(values, nan=0.0) > 0
    on_cat = int((dots & catalogue).sum())
    gates["G3_no_emission_on_public_catalogue"] = gate("catalogue", on_cat == 0,
                                                       f"{on_cat} emitted cells on the 60,988 public-catalogue cells (masked by the organizer, pure waste)")
    n = int(dots.sum())
    gates["G3b_emission_size_sane"] = gate("size", 1_000 <= n <= 250_000, f"{n:,} positive cells (accepted range 1,000-250,000)")

    registry = json.loads(registry_path.read_text())["rasters"]
    score_map = {}
    if scores_path and scores_path.is_file():
        score_map, _, _ = match_scores(registry, json.loads(scores_path.read_text())["entries"])
    uniq = uniqueness_report(dots, registry, cache_dir, footprint, scores=score_map)
    sha = sha256_file(tif)
    file_hash_in_registry = any(e["sha256"] == sha for e in registry)
    gates["G4_not_a_byte_or_dot_set_duplicate"] = gate(
        "exact", not file_hash_in_registry and not uniq["identical_dot_set_in_registry"],
        f"file sha256 {'FOUND' if file_hash_in_registry else 'absent'} in registry; identical dot set {'FOUND' if uniq['identical_dot_set_in_registry'] else 'absent'}; "
        f"{uniq['registry_rasters_compared']} registry rasters compared ({uniq['registry_rasters_missing']} not restored)")
    gates["G5_unique_by_overlap_and_rank_correlation"] = gate(
        "unique", uniq["registry_rasters_compared"] > 0 and not uniq["duplicates_by_overlap"]
        and not uniq["duplicates_by_rank_correlation"] and uniq["registry_rasters_missing"] == 0,
        f"{uniq['registry_rasters_compared']} compared (an empty comparison fails closed); max 500 m-block Spearman {_fmt(uniq['max_spearman_500m'])} "
        f"(limit {DUPLICATE_RHO}); max non-vacuous 3 px overlap {_fmt(uniq['max_overlap_3px_non_vacuous'])} (limit {DUPLICATE_OVERLAP}); "
        f"max chance-adjusted overlap {_fmt(uniq['max_adjusted_overlap'])}; "
        f"duplicates by overlap {len(uniq['duplicates_by_overlap'])}, by correlation {len(uniq['duplicates_by_rank_correlation'])}")

    problems = []
    if not NAME_RE.match(name):
        problems.append("name must be 8-120 chars of letters, digits, '.', '_' or '-'")
    if name.lower() in {u.lower() for u in used_names}:
        problems.append("name already used by a registry file or submission")
    if len(note) > NOTE_MAX or not note.strip():
        problems.append(f"note must be 1-{NOTE_MAX} characters (is {len(note)})")
    gates["G6_unique_name_and_short_note"] = gate("provenance", not problems, "; ".join(problems) or f"name ok; note {len(note)}/{NOTE_MAX} characters")

    evidence_ok, evidence_detail = False, "no evidence file"
    if evidence_path and evidence_path.is_file():
        ev = json.loads(evidence_path.read_text())
        pre = ev.get("preregistered_gates", {})
        bound = procedure_sha256 is not None and ev.get("candidate_procedure_sha256") == procedure_sha256
        evidence_ok = pre.get("PROMOTE_TO_SELECTOR") is True and pre.get("leakage_canary_ok") is True and bound
        evidence_detail = (f"preregistered PROMOTE_TO_SELECTOR={pre.get('PROMOTE_TO_SELECTOR')}; leakage canary ok={pre.get('leakage_canary_ok')}; "
                           f"evidence bound to this emission procedure={bound}; evaluator {ev.get('evaluator')}")
    gates["G7_preregistered_holdout_evidence"] = gate("evidence", evidence_ok, evidence_detail, hard=False)

    gates["G8_literal_registry_protocol"] = gate(
        "protocol", False,
        "STOP: legacy density-exempt/block-rank diagnostics do not implement the current literal "
        "surface AND final registry gate; no selector authorization or weekly cap verification. "
        "See registry/release_status.json. This tool cannot approve uploads.")

    hard_fail = [k for k, v in gates.items() if v["hard"] and not v["pass"]]
    soft_fail = [k for k, v in gates.items() if not v["hard"] and not v["pass"]]
    verdict = "BLOCKED" if hard_fail else "FORMAT_VALID_NOT_PROMOTED"
    return {
        "gate_version": GATE_VERSION, "file": tif.name, "sha256": sha, "convention": convention, "submission_name": name,
        "submission_note": note, "positive_cells": n, "verdict": verdict, "submit_recommended": False,
        "hard_failures": hard_fail, "evidence_failures": soft_fail, "gates": gates,
        "uniqueness": {k: v for k, v in uniq.items() if k != "rows"},
        "neighbour_projection": neighbour_projection(uniq),
        "organizer_acceptance_verified": False,
        "score_class": "UNSCORED. No organizer receipt exists for this file; no number here is a leaderboard score.",
    }
