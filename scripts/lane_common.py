"""Shared loaders for the lane experiments (grid, truth proxies, LiDAR surface helpers, reference rasters)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt, gaussian_filter
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gemsdoe31 import lane, metric  # noqa: E402
from gemsdoe31.raster import CELL_M  # noqa: E402

DATA = ROOT / "data"
INCUMBENT = ROOT / "docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif"
LIDAR_BANDS = ["ex_max", "ex_mean", "step_max", "lapneg_max", "lappos_max", "downface_max", "upface_max",
               "cross_max", "relief", "coh100", "strike", "valid"]


def read(path: Path, band: int = 1) -> np.ndarray:
    with rasterio.open(path) as src:
        return src.read(band)


def load_base() -> dict:
    labels = read(DATA / "labels.tif")
    footprint = np.isfinite(read(DATA / "sample_submission.tif"))
    catalogue = labels == 1
    sgmc = read(DATA / "external/derived_sgmc_faults_100m_u8.tif") == 1
    dist_cat_px = distance_transform_edt(~catalogue)
    far_field = sgmc & (dist_cat_px * CELL_M > metric.RADIUS_M)
    return {"footprint": footprint, "catalogue": catalogue, "sgmc": sgmc, "far_field": far_field,
            "dist_cat_px": dist_cat_px}


def load_lidar() -> dict[str, np.ndarray]:
    with rasterio.open(DATA / "external/lidar_scarp_features_u8.tif") as src:
        stack = src.read()
    return {name: stack[i] for i, name in enumerate(LIDAR_BANDS)}


def load_dots(path: Path) -> np.ndarray:
    return np.nan_to_num(read(path), nan=0.0) > 0


def pct_rank(values: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Percentile rank (0..1) inside ``valid``; 0 elsewhere."""
    out = np.zeros(values.shape, dtype=np.float32)
    ranks = rankdata(values[valid], method="average")
    out[valid] = (ranks / ranks.size).astype(np.float32)
    return out


def auc(score: np.ndarray, positives: np.ndarray, domain: np.ndarray, sample: int = 600_000, seed: int = 7) -> float:
    """Rank AUC of ``score`` for ``positives`` within ``domain`` (random subsample of negatives)."""
    rng = np.random.default_rng(seed)
    pos = np.flatnonzero((positives & domain).ravel())
    neg = np.flatnonzero((~positives & domain).ravel())
    if pos.size == 0:
        return float("nan")
    neg = rng.choice(neg, size=min(sample, neg.size), replace=False)
    flat = score.ravel()
    ranks = rankdata(np.concatenate([flat[pos], flat[neg]]))
    return float((ranks[: pos.size].sum() - pos.size * (pos.size + 1) / 2) / (pos.size * neg.size))


def emit(surface: np.ndarray, candidate_mask: np.ndarray, budget: int, min_dist_px: float = 2.8,
         top_fraction: float = 0.2, return_order: bool = False):
    """Top-fraction candidates -> greedy Poisson-disk dots, truncated at ``budget`` (highest score first)."""
    valid_scores = surface[candidate_mask]
    if valid_scores.size == 0:
        return np.zeros((0, 2), dtype=np.int32) if return_order else np.zeros(surface.shape, dtype=bool)
    cutoff = np.quantile(valid_scores, 1.0 - top_fraction)
    return lane.poisson_disk(surface, candidate_mask & (surface >= cutoff), min_dist_px, budget,
                             return_order=return_order)


def holdout_instruments(base: dict, seeds=(1, 2, 3), hidden_fraction: float = 0.5) -> list[lane.Instrument]:
    instruments = []
    for seed in seeds:
        hidden, visible = lane.hide_components(base["catalogue"], hidden_fraction, seed)
        inst = lane.make_instrument(f"catalogue-gap-seed{seed}", hidden, masked=visible)
        inst.visible = visible          # type: ignore[attr-defined]
        instruments.append(inst)
    return instruments


def discovery_instrument(base: dict) -> lane.Instrument:
    inst = lane.make_instrument("off-catalogue-sgmc", base["far_field"], masked=base["catalogue"])
    inst.visible = base["catalogue"]    # type: ignore[attr-defined]
    return inst


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=1, default=float) + "\n")
