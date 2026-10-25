"""Label-free magnetic texture restoration (not an inversion or fault proof).

Frozen design: knowledge/2026-10-25_magrest_preregistration.md. All shifts are
integer-grid samples. No catalogue, incumbent predictions, or coordinates are
accepted by this feature builder.
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import distance_transform_edt, gaussian_filter

NAMES = ("magrest_2", "magrest_4", "magrest_concordant")
TANGENTS = ((0, 1), (1, 0), (1, 1), (1, -1))
GUARD_PX = 20


def sample_offset(a: np.ndarray, dy: int, dx: int) -> np.ndarray:
    """Return a[y+dy,x+dx], zero outside; NEVER wrap an image edge."""
    h, w = a.shape
    out = np.zeros_like(a)
    if abs(dy) >= h or abs(dx) >= w:
        return out
    ys = slice(max(0, -dy), min(h, h - dy))
    xs = slice(max(0, -dx), min(w, w - dx))
    out[ys, xs] = a[slice(max(0, dy), min(h, h + dy)), slice(max(0, dx), min(w, w + dx))]
    return out


def _ncc(left: np.ndarray, right: np.ndarray, eps: float) -> np.ndarray:
    ml = gaussian_filter(left, 1.25)
    mr = gaussian_filter(right, 1.25)
    vl = np.maximum(gaussian_filter(left * left, 1.25) - ml * ml, 0)
    vr = np.maximum(gaussian_filter(right * right, 1.25) - mr * mr, 0)
    cov = gaussian_filter(left * right, 1.25) - ml * mr
    denom = np.sqrt(vl * vr)
    corr = np.divide(cov, np.maximum(denom, eps), out=np.zeros_like(cov), where=denom > eps)
    # Roundoff can push Pearson correlation slightly beyond its mathematical bounds.
    return np.clip(corr, -1, 1)


def build_features(rtp: np.ndarray, footprint: np.ndarray) -> tuple[np.ndarray, dict]:
    a = np.asarray(rtp, dtype=np.float32)
    fp = np.asarray(footprint, dtype=bool)
    if a.ndim != 2 or a.shape != fp.shape or not fp.any():
        raise ValueError("rtp and footprint must be aligned nonempty 2-D grids")
    valid = fp & np.isfinite(a) & (np.abs(a) < 1e30)
    if not valid.any():
        raise ValueError("no finite magnetic data")
    nearest = distance_transform_edt(~valid, return_distances=False, return_indices=True)
    fill = a[tuple(nearest)]
    del nearest
    z = gaussian_filter(fill, .75) - gaussian_filter(fill, 4)
    del fill
    # Explicit zero padding makes image boundaries invalid even if a supplied
    # fixture/region is finite everywhere (EDT otherwise has asymmetric edges).
    guarded = distance_transform_edt(np.pad(valid, 1, constant_values=False))[1:-1, 1:-1] > GUARD_PX
    if not guarded.any():
        raise ValueError("no magnetic data survive the 20-pixel boundary guard")
    variance = float(np.var(z[guarded], dtype=np.float64))
    eps = max(1e-12, variance * 1e-6)
    features = np.zeros((3,) + a.shape, np.float32)
    for ty, tx in TANGENTS:
        ny, nx = -tx, ty
        left = sample_offset(z, -3 * ny, -3 * nx)
        right = sample_offset(z, 3 * ny, 3 * nx)
        base = _ncc(left, right, eps)
        del right
        responses, signs = [], []
        for d in (2, 4):
            minus = _ncc(left, sample_offset(z, 3 * ny - d * ty, 3 * nx - d * tx), eps)
            plus = _ncc(left, sample_offset(z, 3 * ny + d * ty, 3 * nx + d * tx), eps)
            sign = np.where(plus > minus, 1., np.where(minus > plus, -1., 0.)).astype(np.float32)
            best = np.maximum(minus, plus)
            coherence = np.abs(gaussian_filter(sign, 2))
            response = .5 * np.maximum(best - base, 0) * np.maximum(best, 0) * coherence
            response[~guarded] = 0
            responses.append(response.astype(np.float32))
            signs.append(sign)
            del minus, plus, best, coherence
        joint = np.sqrt(responses[0] * responses[1]) * (signs[0] == signs[1])
        for i, r in enumerate((*responses, joint)):
            np.maximum(features[i], r, out=features[i])
        del responses, signs, base, left, joint
    if not np.isfinite(features).all() or features.min() < 0 or features.max() > 1:
        raise AssertionError("invalid restoration response")
    return features, dict(feature_names=list(NAMES), valid_pixels=int(valid.sum()),
                          guarded_pixels=int(guarded.sum()), boundary_guard_px=GUARD_PX,
                          normalization_epsilon=eps, labelled_inputs_used=False,
                          diagonals_have_sqrt2_longer_sampling=True,
                          maximum_by_feature=[float(f.max()) for f in features])


def spaced_dots(surface: np.ndarray, allowed: np.ndarray, budget: int, *, min_sep=2.8) -> np.ndarray:
    """Deterministic score-ordered emitter; no incumbent dot locations are used."""
    s = np.asarray(surface)
    ok = np.asarray(allowed, bool)
    if s.ndim != 2 or s.shape != ok.shape or budget < 0 or min_sep < 0:
        raise ValueError("invalid emission arguments")
    if not np.isfinite(s[ok]).all() or (s[ok] < 0).any() or (s[ok] > 1).any():
        raise ValueError("surface must already be finite in [0,1]")
    ids = np.flatnonzero(ok & (s > 0))
    # Stable sort preserves ascending pixel index when scores tie.
    ids = ids[np.argsort(-s.ravel()[ids], kind="stable")]
    out = np.zeros(s.shape, bool)
    blocked = np.zeros(s.shape, bool)
    h, w = s.shape
    radius = int(np.ceil(min_sep))
    offsets = [(dy, dx) for dy in range(-radius, radius + 1) for dx in range(-radius, radius + 1)
               if dy * dy + dx * dx <= min_sep * min_sep]
    count = 0
    for index in ids:
        if count >= budget:
            break
        y, x = divmod(int(index), w)
        if blocked[y, x]:
            continue
        out[y, x] = True
        count += 1
        for dy, dx in offsets:
            if 0 <= y + dy < h and 0 <= x + dx < w:
                blocked[y + dy, x + dx] = True
    return out
