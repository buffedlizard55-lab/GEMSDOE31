"""The frozen candidate procedure ("antislope-scarp lane", AS-1). One definition used by E3 *and* by the shipped file.

Surface (label-free, LiDAR bands only, valid only where 3DEP LiDAR exists):
    C = gaussian(0.8 px) of 0.5 * ( pct_rank(upface_max) + pct_rank(max(upface_max - downface_max, 0)) )

Emission (the only place the catalogue enters, and only the *visible* catalogue):
    candidates = LiDAR-valid pixels more than 2 px from a visible catalogue fault and not on one
    dots       = greedy highest-score-first Poisson-disk (minimum spacing 2.8 px = 280 m), first N accepted
"""

from __future__ import annotations

import numpy as np
from lane_common import emit, pct_rank
from scipy.ndimage import distance_transform_edt, gaussian_filter

CANDIDATE_ID = "AS-1"
BUDGET = 38_000
FLANK_PX = 2.0
MIN_DIST_PX = 2.8
TOP_FRACTION = 0.2


def surface(lid: dict, valid: np.ndarray, *, parts: bool = False):
    up = lid["upface_max"].astype(np.float32) / 255.0
    down = lid["downface_max"].astype(np.float32) / 255.0
    r_up = pct_rank(up, valid)
    r_dom = pct_rank(np.maximum(up - down, 0.0), valid)
    combined = gaussian_filter(0.5 * (r_up + r_dom), 0.8) * valid
    if parts:
        return combined, {"upface_max": r_up, "antislope_dominant": r_dom}
    return combined


def emit_candidate(surf: np.ndarray, valid: np.ndarray, visible: np.ndarray, budget: int = BUDGET) -> np.ndarray:
    d_vis = distance_transform_edt(~visible)
    cand = valid & (d_vis > FLANK_PX) & ~visible
    return emit(surf, cand, budget, min_dist_px=MIN_DIST_PX, top_fraction=TOP_FRACTION)
