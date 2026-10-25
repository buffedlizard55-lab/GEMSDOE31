"""Literal, scoped registry canary. No dense-prior or matched-budget exemptions."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import rankdata

CORRELATION_LIMIT = .90
OVERLAP_LIMIT = .70


def standardized_ranks(values):
    v = np.asarray(values)
    if not np.isfinite(v).all():
        raise ValueError("ranking requires finite values")
    if v.size < 2 or np.min(v) == np.max(v):
        return None
    ranks = rankdata(v, method="average")
    ranks -= ranks.mean()
    length = np.linalg.norm(ranks)
    return ranks / length


def _digest(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def build_index(root: Path, inventory: dict, footprint: np.ndarray) -> dict:
    """Cache exact (float64) normalized ranks and packed 3-px support halos."""
    cache = root / "work/novelty"
    cache.mkdir(parents=True, exist_ok=True)
    entries, skipped, by_content = [], [], {}
    for item in inventory["records"]:
        if not item["path"].endswith(".tif"):
            continue
        path = root / item["cache_file"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError(f"prior bytes drifted: {path}")
        with rasterio.open(path) as ds:
            if ds.shape != footprint.shape or ds.count != 1 or str(ds.crs) != "EPSG:32611" or list(ds.transform)[:6] != [100., 0., 243350., 0., -100., 4508550.]:
                skipped.append(dict(source=item["source_url"], reason="different grid; NOT a comparable competition raster", shape=list(ds.shape)))
                continue
            a = ds.read(1)
        v = a[footprint]
        missing = int((~np.isfinite(v)).sum())
        # Missing pixels contain no positive prediction. Record this diagnostic
        # convention explicitly; this does NOT repair/validate a prior for upload.
        v = np.where(np.isfinite(v), v, 0).astype(np.float32)
        content = _digest(v)
        if content in by_content:
            by_content[content]["sources"].append(item["source_url"])
            continue
        stem = cache / content
        ranks = standardized_ranks(v)
        if ranks is not None:
            np.save(str(stem) + "-ranks.npy", ranks)
        support = np.zeros(footprint.shape, bool)
        support[footprint] = v > 0
        halo = distance_transform_edt(~support) <= 3 if support.any() else support
        np.save(str(stem) + "-halo.npy", np.packbits(halo.ravel()))
        entry = dict(content_sha256=content, sources=[item["source_url"]],
                     source_sha256=item["sha256"], nonfinite_inside_prior=missing,
                     positive_pixels=int(support.sum()), constant_ranks=ranks is None,
                     ranks_file=str(stem.relative_to(root)) + "-ranks.npy" if ranks is not None else None,
                     halo_file=str(stem.relative_to(root)) + "-halo.npy")
        by_content[content] = entry
        entries.append(entry)
    out = dict(schema_version=1, entries=entries, incomparable=skipped,
               byte_rasters=inventory["raster_count"], comparable_files=sum(len(e["sources"]) for e in entries),
               distinct_prediction_fields=len(entries),
               scope=inventory["scope"],
               prior_missing_convention="nonfinite prior cells rank as zero and do not count as dots; this is a diagnostic convention, not format repair",
               halo_radius_px=3, correlation="exact average-rank Spearman across full footprint; float64 normalized ranks")
    (root / "evidence/magrest_registry_index.json").write_text(json.dumps(out, indent=1) + "\n")
    return out


def audit(root: Path, surfaces: dict[str, np.ndarray], footprint: np.ndarray,
          supports: dict[str, np.ndarray], index: dict, *, phase: str) -> dict:
    """Check correlations on surfaces, overlap on supplied prospective/final support.

    Before placement supply the unplaced top-K cells. After placement supply the
    actual dots. The same literal thresholds are used; no changes to the registry.
    """
    fp = np.asarray(footprint, bool)
    ranked = {n: standardized_ranks(s[fp]) for n, s in surfaces.items()}
    points = {n: np.flatnonzero(np.asarray(supports[n], bool).ravel()) for n in surfaces}
    rows = {n: [] for n in surfaces}
    for prior in index["entries"]:
        r = np.load(root / prior["ranks_file"], mmap_mode="r") if prior["ranks_file"] else None
        packed = np.load(root / prior["halo_file"], mmap_mode="r")
        halo = np.unpackbits(packed, count=fp.size).astype(bool)
        for name in surfaces:
            rho = float(np.dot(ranked[name], r)) if r is not None and ranked[name] is not None else None
            count = len(points[name])
            covered = int(halo[points[name]].sum())
            overlap = covered / count if count else None
            # An empty emitted candidate is not eligible; undefined correlation
            # is not a positive demonstration of independence.
            duplicate = (rho is not None and abs(rho) > CORRELATION_LIMIT) or (overlap is not None and overlap > OVERLAP_LIMIT)
            rows[name].append(dict(prior_content_sha256=prior["content_sha256"],
                                   prior_sources=prior["sources"], spearman_rho=rho,
                                   overlap_within_3px=overlap, within_3px=covered,
                                   candidate_support_pixels=count, duplicate=bool(duplicate)))
        del halo, r
    arms = {}
    for name, records in rows.items():
        arms[name] = dict(pass_=bool(len(points[name]) and not any(r["duplicate"] for r in records)),
                          surface_footprint_sha256=_digest(np.asarray(surfaces[name][fp], dtype=np.float32)),
                          support_sha256=hashlib.sha256(np.packbits(np.asarray(supports[name], bool).ravel()).tobytes()).hexdigest(),
                          duplicate=any(r["duplicate"] for r in records),
                          max_abs_rho=max((abs(r["spearman_rho"]) for r in records if r["spearman_rho"] is not None), default=None),
                          max_overlap=max((r["overlap_within_3px"] for r in records if r["overlap_within_3px"] is not None), default=None),
                          comparisons=records)
    return dict(phase=phase, evidence_class="COMPUTED duplicate diagnostics, NOT DTI or a competition score",
                correlation_limit=CORRELATION_LIMIT, overlap_limit=OVERLAP_LIMIT,
                scope=index["scope"], incomparable=index["incomparable"],
                comparable_files=index["comparable_files"], distinct_prediction_fields=len(index["entries"]), arms=arms)


def prospective_support(surface, allowed, budget):
    a = np.asarray(surface)
    ids = np.flatnonzero(np.asarray(allowed, bool) & (a > 0))
    ids = ids[np.argsort(-a.ravel()[ids], kind="stable")[:budget]]
    mask = np.zeros(a.shape, bool)
    mask.ravel()[ids] = True
    return mask
