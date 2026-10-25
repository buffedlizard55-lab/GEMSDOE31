"""1D ridge-localized submodular 300 m DTI kernel allocator and duplicate canary (H31-E).

Reuses the exact 29-offset 300 m triangular kernel ``_offsets`` from ``gemsdoe31.metric`` so there is
a single source of truth for kernel geometry across metric evaluation and submodular allocation.
"""

from __future__ import annotations

import hashlib
import heapq
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt, gaussian_filter
from scipy.stats import spearmanr

from .metric import CELL_M, RADIUS_M, _offsets


def ridge_sharpened_weight(
    prob_grid: np.ndarray,
    footprint: np.ndarray,
    d_vis_px: np.ndarray | None = None,
    *,
    flank_px: float = 2.0,
    gamma: float = 2.0,
) -> np.ndarray:
    """Concentrate continuous posterior probability onto 1D fault crests and suppress visible flanks.

    Why this matters for DTI:
    A 29-cell 2D disk integral sums over 2D area, which would over-reward wide diffuse blobs relative
    to 1-pixel-wide geological fault traces. Multiplying ``p^gamma`` by cross-strike ridge prominence
    keeps weight concentrated along 1D fault strands while preserving continuous confidence ranking.
    """
    p = np.where(footprint & np.isfinite(prob_grid), np.clip(prob_grid, 0.0, 1.0), 0.0).astype(np.float32)
    ps = gaussian_filter(p, sigma=0.85, mode="constant")

    # Principal cross-strike normal direction from 2D Hessian eigenvector of most negative curvature
    fyy = gaussian_filter(ps, sigma=1.0, order=(2, 0), mode="constant")
    fxx = gaussian_filter(ps, sigma=1.0, order=(0, 2), mode="constant")
    fxy = gaussian_filter(ps, sigma=1.0, order=(1, 1), mode="constant")
    # Angle of steepest downward concavity (normal to ridge crest)
    theta = 0.5 * np.arctan2(2.0 * fxy, fxx - fyy)
    # Eigenvector for lambda_min points perpendicular to ridge strike when trace < 0
    ny = -np.sin(theta)
    nx = np.cos(theta)
    # Check curvature along (nx, ny) vs (-ny, nx) and pick the more negative second derivative
    c1 = fxx * (nx ** 2) + 2.0 * fxy * nx * ny + fyy * (ny ** 2)
    c2 = fxx * (ny ** 2) - 2.0 * fxy * nx * ny + fyy * (nx ** 2)
    swap = c2 < c1
    ny_opt = np.where(swap, nx, ny)
    nx_opt = np.where(swap, -ny, nx)

    h, w = p.shape
    rows, cols = np.indices((h, w), dtype=np.int32)
    dy = np.round(ny_opt).astype(np.int32)
    dx = np.round(nx_opt).astype(np.int32)
    # Ensure non-zero step
    zero_step = (dy == 0) & (dx == 0)
    dx = np.where(zero_step, 1, dx)

    r_plus = np.clip(rows + dy, 0, h - 1)
    c_plus = np.clip(cols + dx, 0, w - 1)
    r_minus = np.clip(rows - dy, 0, h - 1)
    c_minus = np.clip(cols - dx, 0, w - 1)

    neigh_max = np.maximum(ps[r_plus, c_plus], ps[r_minus, c_minus])
    prominence = np.clip(ps / (neigh_max + 1e-4), 0.25, 1.30).astype(np.float32)

    weight = ((p ** gamma) * (prominence ** 2)).astype(np.float32)
    weight[~footprint] = 0.0
    if d_vis_px is not None and flank_px > 0.0:
        weight[d_vis_px <= flank_px] = 0.0
    return weight


def submodular_dti_emit(
    weight_grid: np.ndarray,
    valid_mask: np.ndarray,
    n_dots: int,
    *,
    min_dist_px: float = 2.2,
    max_pool: int = 260_000,
) -> np.ndarray:
    """Allocate up to ``n_dots`` binary dots via Minoux (1978) lazy-greedy 300 m kernel coverage.

    Maximizes the monotone submodular expected true-positive weight:
        f(S) = sum_g weight_grid[g] * max_{x in S} k(d(x, g))
    subject to |S| <= n_dots and Euclidean spacing >= min_dist_px.
    """
    out = np.zeros(weight_grid.shape, dtype=bool)
    if n_dots <= 0:
        return out

    w = np.where(valid_mask & np.isfinite(weight_grid) & (weight_grid > 0.0), weight_grid, 0.0).astype(np.float32)
    offsets, kernel = _offsets(CELL_M, RADIUS_M)
    offsets_list = [(int(dr), int(dc), float(kv)) for (dr, dc), kv in zip(offsets, kernel)]

    h, width = w.shape
    # Initial exact marginal gain at every cell when coverage C == 0 (float64 guarantees exact upper-bound invariant)
    init_gain = np.zeros((h, width), dtype=np.float64)
    for dr, dc, kv in offsets_list:
        r0_src = max(0, dr)
        r1_src = min(h, h + dr)
        c0_src = max(0, dc)
        c1_src = min(width, width + dc)
        r0_dst = r0_src - dr
        r1_dst = r1_src - dr
        c0_dst = c0_src - dc
        c1_dst = c1_src - dc
        init_gain[r0_dst:r1_dst, c0_dst:c1_dst] += w[r0_src:r1_src, c0_src:c1_src].astype(np.float64) * kv

    init_gain[~valid_mask] = 0.0
    cand_flat = np.flatnonzero(init_gain > 0.0)
    if cand_flat.size == 0:
        return out
    if cand_flat.size > max_pool:
        gains_cand = init_gain.ravel()[cand_flat]
        keep_idx = np.argpartition(gains_cand, -max_pool)[-max_pool:]
        cand_flat = cand_flat[keep_idx]

    # Exclusion disk offsets for min_dist_px
    excl_steps = int(np.floor(min_dist_px))
    excl_offsets: list[tuple[int, int]] = []
    if min_dist_px > 0.0:
        for dr in range(-excl_steps, excl_steps + 1):
            for dc in range(-excl_steps, excl_steps + 1):
                if dr * dr + dc * dc < (min_dist_px ** 2) - 1e-9:
                    excl_offsets.append((dr, dc))

    coverage = np.zeros((h, width), dtype=np.float32)
    blocked = ~np.asarray(valid_mask, dtype=bool).copy()

    # Build Python max-heap of (-upper_bound_gain, flat_index)
    flat_gains = init_gain.ravel()
    heap: list[tuple[float, int]] = [(-float(flat_gains[idx]), int(idx)) for idx in cand_flat]
    heapq.heapify(heap)

    selected = 0
    while heap and selected < n_dots:
        neg_ub, idx = heapq.heappop(heap)
        r, c = divmod(idx, width)
        if blocked[r, c]:
            continue

        # Recompute exact current marginal gain over the 29 kernel neighbors
        gain = 0.0
        for dr, dc, kv in offsets_list:
            rr = r + dr
            cc = c + dc
            if 0 <= rr < h and 0 <= cc < width:
                wv = float(w[rr, cc])
                if wv > 0.0:
                    diff = kv - float(coverage[rr, cc])
                    if diff > 0.0:
                        gain += wv * diff

        if gain <= 0.0:
            continue

        # Lazy-greedy optimality check: if gain >= next best upper bound in heap, accept immediately
        next_ub = -heap[0][0] if heap else 0.0
        if gain + 1e-12 >= next_ub:
            out[r, c] = True
            selected += 1
            for dr, dc, kv in offsets_list:
                rr = r + dr
                cc = c + dc
                if 0 <= rr < h and 0 <= cc < width and kv > coverage[rr, cc]:
                    coverage[rr, cc] = kv
            for dr, dc in excl_offsets:
                rr = r + dr
                cc = c + dc
                if 0 <= rr < h and 0 <= cc < width:
                    blocked[rr, cc] = True
        else:
            heapq.heappush(heap, (-gain, idx))

    return out


def poisson_disk_emit(
    score_grid: np.ndarray,
    valid_mask: np.ndarray,
    n_dots: int,
    *,
    min_dist_px: float = 2.8,
    max_pool: int = 300_000,
) -> np.ndarray:
    """Standard score-ordered greedy Poisson-disk thinning comparator."""
    out = np.zeros(score_grid.shape, dtype=bool)
    if n_dots <= 0:
        return out
    s = np.where(valid_mask & np.isfinite(score_grid) & (score_grid > 0.0), score_grid, 0.0).astype(np.float32)
    cand_flat = np.flatnonzero(s > 0.0)
    if cand_flat.size == 0:
        return out
    vals = s.ravel()[cand_flat]
    if cand_flat.size > max_pool:
        keep = np.argpartition(vals, -max_pool)[-max_pool:]
        cand_flat = cand_flat[keep]
        vals = vals[keep]
    order = np.argsort(-vals, kind="mergesort")
    cand_flat = cand_flat[order]

    h, width = s.shape
    steps = int(np.floor(min_dist_px))
    excl_offsets = [
        (dr, dc)
        for dr in range(-steps, steps + 1)
        for dc in range(-steps, steps + 1)
        if dr * dr + dc * dc < (min_dist_px ** 2) - 1e-9
    ]
    blocked = ~np.asarray(valid_mask, dtype=bool).copy()
    selected = 0
    for idx in cand_flat:
        r, c = divmod(int(idx), width)
        if blocked[r, c]:
            continue
        out[r, c] = True
        selected += 1
        if selected >= n_dots:
            break
        for dr, dc in excl_offsets:
            rr = r + dr
            cc = c + dc
            if 0 <= rr < h and 0 <= cc < width:
                blocked[rr, cc] = True
    return out


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_duplicate_canary(
    candidate_surface: np.ndarray,
    candidate_dots: np.ndarray,
    footprint: np.ndarray,
    reference_files: list[dict[str, Any]],
    *,
    rank_stop: float = 0.90,
    overlap_stop: float = 0.70,
) -> dict[str, Any]:
    """Check Parallel-Run Rule 1 BEFORE placement (continuous surface) AND AFTER placement (final dots).

    ``reference_files`` is a list of dicts with ``{"id": str, "path": Path, "source_group": str}``.
    """
    surf_in = np.asarray(candidate_surface[footprint], dtype=np.float32)
    dots_mask = np.asarray(candidate_dots, dtype=bool) & footprint
    dots_in = dots_mask[footprint].astype(np.float32)
    n_cand = int(dots_mask.sum())
    if n_cand == 0:
        raise ValueError("Candidate has zero positive dots inside footprint")

    # Also construct a pre-placement surface-peak set (top n_cand unthinned local ridge maxima)
    ps = np.where(footprint & np.isfinite(candidate_surface), candidate_surface, -np.inf)
    flat_ps = ps[footprint]
    if n_cand < flat_ps.size:
        thresh = float(np.partition(flat_ps, -n_cand)[-n_cand])
        surf_top_mask = footprint & (ps >= thresh)
        # Trim ties deterministically to exact n_cand
        if int(surf_top_mask.sum()) > n_cand:
            idx_true = np.flatnonzero(surf_top_mask)
            vals_true = ps.ravel()[idx_true]
            keep = idx_true[np.argsort(-vals_true, kind="mergesort")[:n_cand]]
            surf_top_mask = np.zeros_like(footprint, dtype=bool)
            surf_top_mask.ravel()[keep] = True
    else:
        surf_top_mask = footprint.copy()

    rows: list[dict[str, Any]] = []
    max_surf_rho = -1.0
    max_dots_rho = -1.0
    max_surf_ov3 = 0.0
    max_dots_ov3 = 0.0
    duplicates: list[str] = []

    for item in reference_files:
        ref_path = Path(item["path"])
        if not ref_path.is_file():
            continue
        with rasterio.open(ref_path) as src:
            ref_arr = src.read(1)
        ref_clean = np.nan_to_num(ref_arr, nan=0.0).astype(np.float32)
        ref_in = ref_clean[footprint]
        ref_pos = (ref_clean > 0.5) & footprint
        n_ref = int(ref_pos.sum())

        surf_rho = float(spearmanr(surf_in, ref_in).statistic) if np.std(ref_in) > 0 else 0.0
        dots_rho = float(spearmanr(dots_in, ref_in).statistic) if np.std(ref_in) > 0 else 0.0

        if n_ref > 0:
            dist_to_ref = distance_transform_edt(~ref_pos)
            surf_ov3 = float((dist_to_ref[surf_top_mask] <= 3.0).mean())
            dots_ov3 = float((dist_to_ref[dots_mask] <= 3.0).mean())
            exact_shared = int((dots_mask & ref_pos).sum())
        else:
            surf_ov3 = 0.0
            dots_ov3 = 0.0
            exact_shared = 0

        is_dup = bool(
            surf_rho > rank_stop
            or dots_rho > rank_stop
            or surf_ov3 > overlap_stop
            or dots_ov3 > overlap_stop
        )
        if is_dup:
            duplicates.append(str(item["id"]))

        max_surf_rho = max(max_surf_rho, surf_rho)
        max_dots_rho = max(max_dots_rho, dots_rho)
        max_surf_ov3 = max(max_surf_ov3, surf_ov3)
        max_dots_ov3 = max(max_dots_ov3, dots_ov3)

        rows.append(
            {
                "id": str(item["id"]),
                "source_group": str(item.get("source_group", "registry")),
                "file": ref_path.name,
                "sha256": sha256_file(ref_path),
                "reference_dots": n_ref,
                "surface_spearman_rho": round(surf_rho, 6),
                "surface_topn_within_3px": round(surf_ov3, 6),
                "final_dots_spearman_rho": round(dots_rho, 6),
                "final_dots_within_3px": round(dots_ov3, 6),
                "exact_shared_dots": exact_shared,
                "duplicate": is_dup,
            }
        )

    return {
        "candidate_dots": n_cand,
        "thresholds": {
            "spearman_rho_stop_gt": rank_stop,
            "directed_3px_overlap_stop_gt": overlap_stop,
        },
        "checked_count": len(rows),
        "max_surface_spearman_rho": round(max_surf_rho, 6),
        "max_surface_topn_within_3px": round(max_surf_ov3, 6),
        "max_final_dots_spearman_rho": round(max_dots_rho, 6),
        "max_final_dots_within_3px": round(max_dots_ov3, 6),
        "duplicates": duplicates,
        "passed": len(duplicates) == 0 and len(rows) > 0,
        "entries": rows,
    }
