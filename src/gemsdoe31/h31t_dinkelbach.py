"""Cost-Scaled Dinkelbach 29-Cell Submodular DTI Allocator for Lane H31-T.

Under the competition Distance-Tolerant IoU metric (`alpha=0.2, beta=0.8`,
300 m triangular kernel `K_300` over 29 grid cells):

    DTI(S) = TPw(S) / (0.8 * |G| + 0.2 * (TPw(S) + FPw(S))),

where `TPw(S) = sum_{g in G} max_{s in S} K_300(||g - s||)` is monotone
submodular while `FPw(S) = sum_{s in S} (1 - max_{g in G} K_300(||s - g||))`
adds a heterogeneous expected false-positive cost per dot:

    c_FP(i) ~= max(c_min, 1 - eta * max_{m in N_29} k_m * p(i + delta_m)).

We maximize the cost-scaled marginal gain ratio:

    r(i | S) = Delta F_w(i | S) / c_FP(i)

subject to minimum inter-dot spacing `||i - s|| >= min_spacing_px` and
visible-catalogue collar `d(visible_catalogue) > collar_px` via exact Minoux/CELF
lazy priority-queue optimization with disjoint-neighborhood (>6 px) batching.
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass

import numpy as np
from scipy import ndimage as ndi

from gemsdoe31.submodular_emit import ridge_sharpened_weight

RADIUS_PX = 3


def build_kernel_29() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return `(dr, dc, weights)` for the exact 29-cell 300 m triangular kernel."""
    drs: list[int] = []
    dcs: list[int] = []
    kws: list[float] = []
    for dr in range(-RADIUS_PX, RADIUS_PX + 1):
        for dc in range(-RADIUS_PX, RADIUS_PX + 1):
            dist = float(np.hypot(dr, dc))
            if dist <= float(RADIUS_PX) + 1.0e-9:
                w = max(0.0, 1.0 - dist / float(RADIUS_PX))
                if w > 0.0:
                    drs.append(dr)
                    dcs.append(dc)
                    kws.append(w)
    return (
        np.asarray(drs, dtype=np.int32),
        np.asarray(dcs, dtype=np.int32),
        np.asarray(kws, dtype=np.float32),
    )


KERNEL_DR, KERNEL_DC, KERNEL_W = build_kernel_29()


def _disk_offsets(radius_px: float) -> tuple[np.ndarray, np.ndarray]:
    lim = int(np.floor(radius_px + 1.0e-9))
    drs: list[int] = []
    dcs: list[int] = []
    for dr in range(-lim, lim + 1):
        for dc in range(-lim, lim + 1):
            if float(np.hypot(dr, dc)) < float(radius_px) - 1.0e-9:
                drs.append(dr)
                dcs.append(dc)
    return np.asarray(drs, dtype=np.int32), np.asarray(dcs, dtype=np.int32)


@dataclass(frozen=True)
class DinkelbachAllocationResult:
    binary_dots: np.ndarray
    n_dots: int
    total_weighted_gain: float
    total_fp_cost: float
    min_marginal_ratio: float
    mean_selected_prob: float


def emit_dinkelbach_submodular_dots(
    prob: np.ndarray,
    footprint: np.ndarray,
    visible_catalogue: np.ndarray | None = None,
    *,
    budget: int = 37_654,
    collar_px: float = 2.0,
    min_spacing_px: float = 2.4,
    cost_eta: float = 0.50,
    ridge_gamma: float = 0.35,
    pool_size: int = 260_000,
    batch_size: int = 256,
) -> DinkelbachAllocationResult:
    """Emit exact CELF cost-scaled submodular binary `{0.0, 1.0}` predictions."""
    fp = np.asarray(footprint, dtype=bool)
    H, W = fp.shape
    p = np.where(fp & np.isfinite(prob), np.clip(prob, 0.0, 1.0), 0.0).astype(np.float32)

    eligible = fp.copy()
    if visible_catalogue is not None and np.any(visible_catalogue) and collar_px > 0.0:
        d_vis = ndi.distance_transform_edt(~np.asarray(visible_catalogue, dtype=bool))
        eligible &= d_vis > float(collar_px)

    if budget <= 0 or not np.any(eligible):
        return DinkelbachAllocationResult(
            binary_dots=np.zeros((H, W), dtype=np.float32),
            n_dots=0,
            total_weighted_gain=0.0,
            total_fp_cost=0.0,
            min_marginal_ratio=0.0,
            mean_selected_prob=0.0,
        )

    w_sharp = (
        ridge_sharpened_weight(p, fp, gamma=float(ridge_gamma))
        if ridge_gamma > 0.0
        else p.copy()
    )
    w_sharp = np.where(fp, np.maximum(0.0, w_sharp), 0.0).astype(np.float32)

    # Padded 1D buffers (`pad = 4` safely covers both 3-px kernel and spacing <= 4 px)
    pad = max(RADIUS_PX, int(np.ceil(min_spacing_px)) + 1)
    Hp = H + 2 * pad
    Wp = W + 2 * pad

    w_pad = np.zeros((Hp, Wp), dtype=np.float32)
    w_pad[pad : pad + H, pad : pad + W] = w_sharp
    w_flat = w_pad.ravel()

    p_pad = np.zeros((Hp, Wp), dtype=np.float32)
    p_pad[pad : pad + H, pad : pad + W] = p
    p_flat = p_pad.ravel()

    cov_flat = np.zeros(Hp * Wp, dtype=np.float32)
    blocked_flat = np.zeros(Hp * Wp, dtype=bool)

    kern_off = (KERNEL_DR * Wp + KERNEL_DC).astype(np.int32)
    sp_dr, sp_dc = _disk_offsets(min_spacing_px)
    sp_off = (sp_dr * Wp + sp_dc).astype(np.int32)

    # Candidate pool over `eligible` ranked by sharpened ridge score
    er, ec = np.nonzero(eligible)
    cand_scores = w_sharp[er, ec]
    pos_mask = cand_scores > 0.0
    er = er[pos_mask]
    ec = ec[pos_mask]
    cand_scores = cand_scores[pos_mask]
    if er.size == 0:
        return DinkelbachAllocationResult(
            binary_dots=np.zeros((H, W), dtype=np.float32),
            n_dots=0,
            total_weighted_gain=0.0,
            total_fp_cost=0.0,
            min_marginal_ratio=0.0,
            mean_selected_prob=0.0,
        )

    if er.size > int(pool_size):
        keep = np.argpartition(cand_scores, -int(pool_size))[-int(pool_size) :]
        er = er[keep]
        ec = ec[keep]

    flat_idx = ((er + pad) * Wp + (ec + pad)).astype(np.int32)
    N = flat_idx.size

    # Vectorized initial gain & heterogeneous expected FP cost over the candidate pool
    neigh_idx = flat_idx[:, None] + kern_off[None, :]  # (N, 29)
    init_gain = (w_flat[neigh_idx] * KERNEL_W[None, :]).sum(axis=1, dtype=np.float64)
    max_kp = (p_flat[neigh_idx] * KERNEL_W[None, :]).max(axis=1)
    fp_cost = np.maximum(0.15, 1.0 - float(cost_eta) * max_kp).astype(np.float64)
    init_ratio = init_gain / fp_cost

    # Minoux/CELF max-heap storing `(-ratio, tie_idx, cand_pos)`
    heap: list[tuple[float, int, int]] = [
        (-float(init_ratio[i]), int(flat_idx[i]), int(i))
        for i in range(N)
        if init_ratio[i] > 0.0
    ]
    heapq.heapify(heap)

    selected_pos: list[int] = []
    total_gain = 0.0
    total_cost = 0.0
    min_ratio = float("inf")
    # Two candidates at distance > interact_r2 cannot share any of the 29 kernel cells
    # (max offset 3 px => 2*3 = 6 px) nor conflict under `min_spacing_px`.
    interact_r = max(2.0 * float(RADIUS_PX), float(min_spacing_px)) + 1.0e-6
    interact_r2 = interact_r * interact_r

    use_batch = max(1, int(batch_size))

    while len(selected_pos) < int(budget) and heap:
        if use_batch == 1:
            neg_ub, f_idx, c_pos = heapq.heappop(heap)
            if blocked_flat[f_idx]:
                continue
            nb = f_idx + kern_off
            rem = np.maximum(0.0, KERNEL_W - cov_flat[nb])
            gain = float(np.dot(w_flat[nb].astype(np.float64), rem.astype(np.float64)))
            if gain <= 0.0:
                continue
            ratio = gain / float(fp_cost[c_pos])
            next_ub = -heap[0][0] if heap else -1.0
            if ratio + 1.0e-12 >= next_ub:
                selected_pos.append(c_pos)
                cov_flat[nb] = np.maximum(cov_flat[nb], KERNEL_W)
                if sp_off.size:
                    blocked_flat[f_idx + sp_off] = True
                else:
                    blocked_flat[f_idx] = True
                total_gain += gain
                total_cost += float(fp_cost[c_pos])
                min_ratio = min(min_ratio, ratio)
            else:
                heapq.heappush(heap, (-ratio, f_idx, c_pos))
            continue

        # Exact batch-CELF: pop up to `use_batch` items, evaluate exact current gains,
        # and accept a prefix of strictly dominant, pairwise non-interacting items.
        popped: list[tuple[float, int, int]] = []
        while heap and len(popped) < use_batch:
            neg_ub, f_idx, c_pos = heapq.heappop(heap)
            if blocked_flat[f_idx]:
                continue
            popped.append((neg_ub, f_idx, c_pos))
        if not popped:
            break

        floor_ub = -heap[0][0] if heap else -1.0
        p_fidx = np.asarray([x[1] for x in popped], dtype=np.int32)
        p_cpos = np.asarray([x[2] for x in popped], dtype=np.int32)
        p_nb = p_fidx[:, None] + kern_off[None, :]
        p_rem = np.maximum(0.0, KERNEL_W[None, :] - cov_flat[p_nb])
        p_gains = (w_flat[p_nb] * p_rem).sum(axis=1, dtype=np.float64)
        p_ratios = p_gains / fp_cost[p_cpos]

        order = np.argsort(-p_ratios, kind="mergesort")
        # Also sort exact ties by ascending `f_idx` to match `heapq` tuple tie-breaking
        # `(-ratio, f_idx, c_pos)` identically to `batch_size=1`.
        order = sorted(
            order,
            key=lambda idx: (-float(p_ratios[idx]), int(p_fidx[idx]), int(p_cpos[idx])),
        )
        accepted_rc: list[tuple[int, int]] = []
        accepted_any = False
        prefix_open = True

        for ord_i in order:
            f_idx = int(p_fidx[ord_i])
            c_pos = int(p_cpos[ord_i])
            ratio = float(p_ratios[ord_i])
            gain = float(p_gains[ord_i])
            if gain <= 0.0:
                continue

            if (not prefix_open) or (len(selected_pos) >= int(budget)) or (ratio + 1.0e-12 < floor_ub):
                prefix_open = False
                heapq.heappush(heap, (-ratio, f_idx, c_pos))
                continue

            r_i = int(er[c_pos])
            c_i = int(ec[c_pos])
            conflict = False
            for ar, ac in accepted_rc:
                if (r_i - ar) * (r_i - ar) + (c_i - ac) * (c_i - ac) <= interact_r2:
                    conflict = True
                    break

            if conflict:
                # Stop accepting further items in this micro-batch so exact sequential
                # order & tie-breaking vs `batch_size=1` are preserved bit-for-bit.
                prefix_open = False
                heapq.heappush(heap, (-ratio, f_idx, c_pos))
                continue

            selected_pos.append(c_pos)
            accepted_rc.append((r_i, c_i))
            accepted_any = True
            nb = f_idx + kern_off
            cov_flat[nb] = np.maximum(cov_flat[nb], KERNEL_W)
            if sp_off.size:
                blocked_flat[f_idx + sp_off] = True
            else:
                blocked_flat[f_idx] = True
            total_gain += gain
            total_cost += float(fp_cost[c_pos])
            min_ratio = min(min_ratio, ratio)

        if not accepted_any and heap:
            # Fallback single exact step to guarantee strict forward progress
            neg_ub, f_idx, c_pos = heapq.heappop(heap)
            if not blocked_flat[f_idx]:
                nb = f_idx + kern_off
                rem = np.maximum(0.0, KERNEL_W - cov_flat[nb])
                gain = float(np.dot(w_flat[nb].astype(np.float64), rem.astype(np.float64)))
                if gain > 0.0:
                    ratio = gain / float(fp_cost[c_pos])
                    next_ub = -heap[0][0] if heap else -1.0
                    if ratio + 1.0e-12 >= next_ub and len(selected_pos) < int(budget):
                        selected_pos.append(c_pos)
                        cov_flat[nb] = np.maximum(cov_flat[nb], KERNEL_W)
                        if sp_off.size:
                            blocked_flat[f_idx + sp_off] = True
                        else:
                            blocked_flat[f_idx] = True
                        total_gain += gain
                        total_cost += float(fp_cost[c_pos])
                        min_ratio = min(min_ratio, ratio)
                    else:
                        heapq.heappush(heap, (-ratio, f_idx, c_pos))

    dots = np.zeros((H, W), dtype=np.float32)
    if selected_pos:
        sel_arr = np.asarray(selected_pos, dtype=np.int32)
        dots[er[sel_arr], ec[sel_arr]] = 1.0
        mean_p = float(p[er[sel_arr], ec[sel_arr]].mean())
    else:
        mean_p = 0.0
        min_ratio = 0.0

    return DinkelbachAllocationResult(
        binary_dots=dots,
        n_dots=int(len(selected_pos)),
        total_weighted_gain=float(total_gain),
        total_fp_cost=float(total_cost),
        min_marginal_ratio=float(min_ratio if np.isfinite(min_ratio) else 0.0),
        mean_selected_prob=mean_p,
    )


def emit_poisson_thinning_dots(
    prob: np.ndarray,
    footprint: np.ndarray,
    visible_catalogue: np.ndarray | None = None,
    *,
    budget: int = 37_654,
    collar_px: float = 2.0,
    min_spacing_px: float = 2.8,
    pool_size: int = 320_000,
) -> np.ndarray:
    """Matched-budget greedy `2.8 px` Poisson-disk baseline emitter (`{0.0, 1.0}`)."""
    fp = np.asarray(footprint, dtype=bool)
    H, W = fp.shape
    p = np.where(fp & np.isfinite(prob), np.clip(prob, 0.0, 1.0), 0.0).astype(np.float32)

    eligible = fp.copy()
    if visible_catalogue is not None and np.any(visible_catalogue) and collar_px > 0.0:
        d_vis = ndi.distance_transform_edt(~np.asarray(visible_catalogue, dtype=bool))
        eligible &= d_vis > float(collar_px)

    er, ec = np.nonzero(eligible & (p > 0.0))
    if er.size == 0 or budget <= 0:
        return np.zeros((H, W), dtype=np.float32)

    scores = p[er, ec]
    if er.size > int(pool_size):
        keep = np.argpartition(scores, -int(pool_size))[-int(pool_size) :]
        er = er[keep]
        ec = ec[keep]
        scores = scores[keep]

    order = np.argsort(-scores, kind="mergesort")
    er = er[order]
    ec = ec[order]

    pad = int(np.ceil(min_spacing_px)) + 1
    Wp = W + 2 * pad
    blocked = np.zeros((H + 2 * pad) * Wp, dtype=bool)
    sp_dr, sp_dc = _disk_offsets(min_spacing_px)
    sp_off = (sp_dr * Wp + sp_dc).astype(np.int32)

    dots = np.zeros((H, W), dtype=np.float32)
    picked = 0
    for idx in range(er.size):
        if picked >= int(budget):
            break
        r = int(er[idx])
        c = int(ec[idx])
        f_idx = (r + pad) * Wp + (c + pad)
        if blocked[f_idx]:
            continue
        dots[r, c] = 1.0
        if sp_off.size:
            blocked[f_idx + sp_off] = True
        else:
            blocked[f_idx] = True
        picked += 1
    return dots
