"""Small raster helpers shared by the analysis scripts (competition grid constants included)."""

from __future__ import annotations

import numpy as np
import rasterio
from scipy.ndimage import label as cc_label

CELL_M = 100.0
CRS_EPSG = 32611
SHAPE = (3730, 3292)
TRANSFORM = (100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)
FOOTPRINT_PIXELS = 5_167_373
OUTSIDE_PIXELS = 7_111_787


def read_band(path) -> np.ndarray:
    with rasterio.open(path) as src:
        return src.read(1)


def connected_components(binary: np.ndarray) -> np.ndarray:
    """8-connected labelling used to keep fault traces separate in the variogram pair selection."""
    labels, _ = cc_label(np.asarray(binary, dtype=bool), structure=np.ones((3, 3), dtype=int))
    return labels.astype(np.int32)


def distance_km(binary: np.ndarray, cell_m: float = CELL_M) -> np.ndarray:
    from scipy.ndimage import distance_transform_edt

    return distance_transform_edt(~np.asarray(binary, dtype=bool), sampling=cell_m) / 1000.0


def quadrant_blocks(shape: tuple[int, int] = SHAPE) -> np.ndarray:
    """Four equal spatial blocks (NW, NE, SW, SE) used as the blocked cross-validation folds."""
    height, width = shape
    rows, cols = np.divmod(np.arange(height * width), width)
    blocks = ((rows >= height // 2).astype(np.int8) * 2 + (cols >= width // 2).astype(np.int8))
    return blocks.reshape(shape)
