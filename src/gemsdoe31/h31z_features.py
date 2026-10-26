"""H31-Z cross-cell LiDAR scarp-coherence operator and max-union combination.

Label-free. Catalogue distances are never used. Unit-tested on synthetic arrays
(`tests/test_h31z.py`). Frozen by `knowledge/2026-10-26_h31z_preregistration.md`:
gradient sigma 1.0 px, tensor smoothing sigma 2.5 px, coherence weight
``0.25 + 0.75 * coherence`` (soft weight, never a veto).
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter

GRAD_SIGMA_PX = 1.0
TENSOR_SIGMA_PX = 2.5
COHERENCE_FLOOR = 0.25


def structure_tensor_coherence(
    field: np.ndarray,
    *,
    grad_sigma: float = GRAD_SIGMA_PX,
    tensor_sigma: float = TENSOR_SIGMA_PX,
) -> np.ndarray:
    """Linear coherence ``(lmax - lmin) / (lmax + lmin)`` of a scalar field, in [0, 1].

    ``lmax >= lmin`` are eigenvalues of the smoothed gradient outer product.
    A straight ridge/valley has gradients aligned across cells (coherence -> 1);
    an isotropic blob or uncorrelated noise has coherence -> 0. A constant field
    yields 0 (no gradient energy). Non-finite inputs are treated as 0.
    """
    f = np.where(np.isfinite(field), field, 0.0).astype(np.float32)
    gy = gaussian_filter(f, grad_sigma, order=(1, 0), mode="nearest")
    gx = gaussian_filter(f, grad_sigma, order=(0, 1), mode="nearest")
    jxx = gaussian_filter(gx * gx, tensor_sigma, mode="nearest")
    jxy = gaussian_filter(gx * gy, tensor_sigma, mode="nearest")
    jyy = gaussian_filter(gy * gy, tensor_sigma, mode="nearest")
    # Closed-form eigenvalues of the symmetric 2x2 tensor [[jxx, jxy], [jxy, jyy]].
    trace = jxx + jyy
    disc = np.sqrt(np.maximum((jxx - jyy) ** 2 + 4.0 * jxy ** 2, 0.0))
    lmax = 0.5 * (trace + disc)
    lmin = np.maximum(0.5 * (trace - disc), 0.0)
    coh = (lmax - lmin) / (lmax + lmin + 1e-12)
    return np.clip(np.where(np.isfinite(coh), coh, 0.0), 0.0, 1.0).astype(np.float32)


def coherence_weighted(
    strength: np.ndarray,
    coherence: np.ndarray,
    valid: np.ndarray,
    *,
    floor: float = COHERENCE_FLOOR,
) -> np.ndarray:
    """``strength * (floor + (1 - floor) * coherence)``, zero where not ``valid``.

    Negative/non-finite strength is treated as 0. With the frozen floor of 0.25 a
    strong but short (incoherent) scarp keeps a quarter of its strength: coherence
    re-orders, it never vetoes.
    """
    s = np.where(np.isfinite(strength), np.maximum(strength, 0.0), 0.0).astype(np.float32)
    c = np.clip(np.where(np.isfinite(coherence), coherence, 0.0), 0.0, 1.0).astype(np.float32)
    out = (s * (np.float32(floor) + np.float32(1.0 - floor) * c)).astype(np.float32)
    out[~np.asarray(valid, dtype=bool)] = 0.0
    return out


def max_union(parts: list[np.ndarray]) -> np.ndarray:
    """Element-wise maximum of rank fields (union, not conjunction)."""
    if not parts:
        raise ValueError("max_union requires at least one field")
    out = np.asarray(parts[0], dtype=np.float32).copy()
    for p in parts[1:]:
        np.maximum(out, np.asarray(p, dtype=np.float32), out=out)
    return out
