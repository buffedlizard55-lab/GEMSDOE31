"""Exact 29-cell lazy-greedy monotone submodular DTI kernel allocator.

Maximizes expected kernel-weighted true-positive coverage ``sum_u W(u) max_{i in S} K(||u - i||)``
over the exact 29-offset R = 300 m triangular kernel from :mod:`gemsdoe31.metric` using Minoux
(1978) accelerated lazy greedy priority-queue updates, with fold-clean visible-catalogue halo
attenuation and deterministic tie-breaking.
"""

from __future__ import annotations

import heapq

import numpy as np
from scipy.ndimage import distance_transform_edt, gaussian_filter

from . import metric

PAD = 3  # exact pixel radius of R = 300 m kernel at 100 m cell size


def _build_disk_offsets(radius_px: float) -> tuple[np.ndarray, np.ndarray]:
    r_int = int(np.ceil(float(radius_px)))
    dy, dx = np.mgrid[-r_int : r_int + 1, -r_int : r_int + 1]
    keep = (dy * dy + dx * dx) <= (float(radius_px) * float(radius_px)) + 1e-9
    return dy[keep].astype(np.int32), dx[keep].astype(np.int32)


def _run_lazy_greedy_pass(
    er: np.ndarray,
    ec: np.ndarray,
    w_pad: np.ndarray,
    cov_pad: np.ndarray,
    blocked_pad: np.ndarray,
    dirty_pad: np.ndarray,
    selected: np.ndarray,
    *,
    dr_k: np.ndarray,
    dc_k: np.ndarray,
    kw: np.ndarray,
    sep_dy: np.ndarray,
    sep_dx: np.ndarray,
    int_dy: np.ndarray,
    int_dx: np.ndarray,
    max_dots: int,
    placed: int,
    step_stamp: int,
    p6: int = 6,
) -> tuple[int, int]:
    """Execute Minoux (1978) lazy-greedy selection over candidate coordinates ``(er, ec)``."""
    if er.size == 0 or placed >= max_dots:
        return placed, step_stamp

    # Compute exact initial marginal gains given current cov_pad state
    rp_all = er + p6
    cp_all = ec + p6
    not_blocked = ~blocked_pad[rp_all, cp_all]
    er, ec, rp_all, cp_all = er[not_blocked], ec[not_blocked], rp_all[not_blocked], cp_all[not_blocked]
    if er.size == 0:
        return placed, step_stamp

    gains = np.zeros(er.size, dtype=np.float32)
    for dr, dc, weight_k in zip(dr_k.tolist(), dc_k.tolist(), kw.tolist()):
        rem = np.maximum(weight_k - cov_pad[rp_all + dr, cp_all + dc], 0.0)
        gains += w_pad[rp_all + dr, cp_all + dc] * rem

    pos_mask = gains > 1e-12
    er, ec, gains = er[pos_mask], ec[pos_mask], gains[pos_mask]
    if er.size == 0:
        return placed, step_stamp

    init_stamp = step_stamp
    dirty_pad[er + p6, ec + p6] = init_stamp
    heap: list[tuple[float, int, int, int]] = [
        (-float(g), int(r), int(c), init_stamp)
        for g, r, c in zip(gains.tolist(), er.tolist(), ec.tolist())
    ]
    heapq.heapify(heap)

    while heap and placed < max_dots:
        neg_gain, r, c, stamp = heapq.heappop(heap)
        rp, cp = r + p6, c + p6
        if blocked_pad[rp, cp]:
            continue
        cur_stamp = int(dirty_pad[rp, cp])
        if stamp != cur_stamp:
            rr = rp + dr_k
            cc = cp + dc_k
            rem = kw - cov_pad[rr, cc]
            pos = rem > 0.0
            if not np.any(pos):
                continue
            new_gain = float(np.dot(w_pad[rr[pos], cc[pos]], rem[pos]))
            if new_gain <= 1e-12:
                continue
            heapq.heappush(heap, (-new_gain, r, c, cur_stamp))
            continue

        selected[r, c] = True
        placed += 1
        step_stamp += 1
        if placed >= max_dots:
            break

        rr = rp + dr_k
        cc = cp + dc_k
        np.maximum.at(cov_pad, (rr, cc), kw)
        blocked_pad[rp + sep_dy, cp + sep_dx] = True
        dirty_pad[rp + int_dy, cp + int_dx] = step_stamp

    return placed, step_stamp


def submodular_emit_dots(
    surface: np.ndarray,
    valid: np.ndarray,
    *,
    max_dots: int,
    visible_catalogue: np.ndarray | None = None,
    min_sep_px: float = 2.25,
    candidate_pool: int = 750_000,
    smooth_sigma: float = 0.8,
    contrast_gamma: float = 1.5,
) -> np.ndarray:
    """Allocate up to ``max_dots`` binary dots via exact 29-cell lazy-greedy submodular coverage."""
    val = np.asarray(valid, dtype=bool)
    if max_dots <= 0 or not val.any():
        return np.zeros(val.shape, dtype=bool)

    surf = np.asarray(surface, dtype=np.float32)
    fin = val & np.isfinite(surf)
    if not fin.any():
        return np.zeros(val.shape, dtype=bool)

    med_raw = float(np.median(surf[fin]))
    filled = np.where(fin, surf, med_raw).astype(np.float32)
    smoothed = gaussian_filter(filled, sigma=float(smooth_sigma)) if smooth_sigma > 0 else filled
    baseline = float(np.median(smoothed[fin]))
    excess = np.maximum(smoothed - baseline, 0.0)
    weights = np.where(fin, np.power(excess, float(contrast_gamma)), 0.0).astype(np.float32)
    if not np.any(weights > 0.0):
        # Fallback if surface is nearly constant above median
        weights = np.where(fin, np.maximum(smoothed - float(smoothed[fin].min()) + 1e-6, 0.0), 0.0).astype(np.float32)

    if visible_catalogue is not None and np.any(visible_catalogue):
        vis = np.asarray(visible_catalogue, dtype=bool)
        d_vis = distance_transform_edt(~vis)
        weights[vis] = 0.0
        flank = np.clip((d_vis - 1.0) / 1.5, 0.0, 1.0).astype(np.float32)
        weights *= flank
        eligible = fin & (d_vis > 2.0) & (weights > 0.0)
    else:
        eligible = fin & (weights > 0.0)

    if not eligible.any():
        return np.zeros(val.shape, dtype=bool)

    h, w = val.shape
    offsets, kernel = metric._offsets(metric.CELL_M, metric.RADIUS_M)
    dr_k = offsets[:, 0].astype(np.int32)
    dc_k = offsets[:, 1].astype(np.int32)
    kw = kernel.astype(np.float32)

    p6 = 6
    w_pad = np.zeros((h + 2 * p6, w + 2 * p6), dtype=np.float32)
    w_pad[p6 : p6 + h, p6 : p6 + w] = weights

    init_gain = np.zeros((h, w), dtype=np.float32)
    for dr, dc, weight_k in zip(dr_k.tolist(), dc_k.tolist(), kw.tolist()):
        init_gain += weight_k * w_pad[p6 + dr : p6 + h + dr, p6 + dc : p6 + w + dc]

    er_all, ec_all = np.nonzero(eligible & (init_gain > 0.0))
    if er_all.size == 0:
        return np.zeros(val.shape, dtype=bool)

    scores_all = init_gain[er_all, ec_all]
    order = np.lexsort((ec_all, er_all, -scores_all))
    er_all, ec_all = er_all[order], ec_all[order]

    cov_pad = np.zeros((h + 2 * p6, w + 2 * p6), dtype=np.float32)
    blocked_pad = np.zeros((h + 2 * p6, w + 2 * p6), dtype=bool)
    dirty_pad = np.zeros((h + 2 * p6, w + 2 * p6), dtype=np.int32)
    selected = np.zeros((h, w), dtype=bool)

    sep_dy, sep_dx = _build_disk_offsets(min_sep_px)
    int_dy, int_dx = _build_disk_offsets(2.0 * PAD)

    pool1 = min(int(candidate_pool), int(er_all.size))
    placed, step_stamp = _run_lazy_greedy_pass(
        er_all[:pool1],
        ec_all[:pool1],
        w_pad,
        cov_pad,
        blocked_pad,
        dirty_pad,
        selected,
        dr_k=dr_k,
        dc_k=dc_k,
        kw=kw,
        sep_dy=sep_dy,
        sep_dx=sep_dx,
        int_dy=int_dy,
        int_dx=int_dx,
        max_dots=max_dots,
        placed=0,
        step_stamp=1,
        p6=p6,
    )
    if placed < max_dots and pool1 < er_all.size:
        _run_lazy_greedy_pass(
            er_all[pool1:],
            ec_all[pool1:],
            w_pad,
            cov_pad,
            blocked_pad,
            dirty_pad,
            selected,
            dr_k=dr_k,
            dc_k=dc_k,
            kw=kw,
            sep_dy=sep_dy,
            sep_dx=sep_dx,
            int_dy=int_dy,
            int_dx=int_dx,
            max_dots=max_dots,
            placed=placed,
            step_stamp=step_stamp + 1,
            p6=p6,
        )

    return selected
