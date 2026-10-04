"""Strict GeoTIFF submission validator for the official GEMS grid contract.

The validator treats the sample-submission raster as a mask/grid template, requires NaN outside that mask, and
checks every scored-footprint value before upload. It deliberately does not silently clip or fill predictions.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from affine import Affine

EXPECTED_CRS_EPSG = 32611
EXPECTED_SHAPE = (3730, 3292)
EXPECTED_TRANSFORM = Affine(100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)
EXPECTED_FOOTPRINT_PIXELS = 5_167_373
EXPECTED_OUTSIDE_PIXELS = 7_111_787


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _check(name: str, passed: bool, detail: str, *, hard: bool = True) -> dict[str, Any]:
    return {"pass_": bool(passed), "detail": str(detail), "hard": bool(hard)}


def validate_submission(
    submission_path: str | Path,
    template_path: str | Path,
    *,
    require_competition_grid: bool = True,
) -> dict[str, Any]:
    """Validate one float32 GeoTIFF against the organizer's sample grid and footprint.

    Hard checks: template validity, one band, float32, exact CRS/shape/transform match, all footprint values
    finite and within `[0,1]`, no infinity anywhere, and every out-of-footprint cell NaN. No alternative zero
    collar is accepted, because the official format says outside data must be null/NaN.
    """
    submission_path = Path(submission_path)
    template_path = Path(template_path)
    if not submission_path.is_file():
        raise FileNotFoundError(submission_path)
    if not template_path.is_file():
        raise FileNotFoundError(template_path)

    with rasterio.open(template_path) as template:
        template_values = template.read(1, masked=False)
        template_crs = template.crs
        template_transform = template.transform
        template_shape = template.shape
        template_count = template.count
        template_dtype = template.dtypes
    footprint = np.isfinite(template_values)
    checks: dict[str, dict[str, Any]] = {}

    checks["template_single_band"] = _check("template_single_band", template_count == 1, f"count={template_count}")
    checks["template_epsg_32611"] = _check(
        "template_epsg_32611", template_crs is not None and template_crs.to_epsg() == EXPECTED_CRS_EPSG,
        f"EPSG:{template_crs.to_epsg() if template_crs else None}",
    )
    checks["template_float32"] = _check(
        "template_float32", template_dtype == ("float32",), f"dtypes={template_dtype}"
    )
    checks["template_has_finite_footprint"] = _check(
        "template_has_finite_footprint", bool(footprint.any()), f"{int(footprint.sum()):,} finite pixels"
    )
    if require_competition_grid:
        checks["template_expected_shape"] = _check(
            "template_expected_shape", template_shape == EXPECTED_SHAPE,
            f"{template_shape} (expected {EXPECTED_SHAPE})",
        )
        checks["template_expected_transform"] = _check(
            "template_expected_transform", template_transform == EXPECTED_TRANSFORM,
            f"{tuple(template_transform)[:6]} (expected {tuple(EXPECTED_TRANSFORM)[:6]})",
        )
        checks["template_expected_footprint"] = _check(
            "template_expected_footprint", int(footprint.sum()) == EXPECTED_FOOTPRINT_PIXELS,
            f"{int(footprint.sum()):,} (expected {EXPECTED_FOOTPRINT_PIXELS:,})",
        )
        checks["template_expected_outside"] = _check(
            "template_expected_outside", int((~footprint).sum()) == EXPECTED_OUTSIDE_PIXELS,
            f"{int((~footprint).sum()):,} (expected {EXPECTED_OUTSIDE_PIXELS:,})",
        )

    with rasterio.open(submission_path) as source:
        count = source.count
        dtypes = source.dtypes
        crs = source.crs
        transform = source.transform
        shape = source.shape
        bounds = tuple(source.bounds)
        nodata = source.nodata
        if count == 1:
            values = source.read(1, masked=False)
        else:
            values = None

    checks["single_band"] = _check("single_band", count == 1, f"count={count}")
    checks["dtype_float32"] = _check("dtype_float32", dtypes == ("float32",), f"dtypes={dtypes}")
    checks["shape_matches_template"] = _check(
        "shape_matches_template", shape == template_shape, f"{shape} vs {template_shape}"
    )
    checks["crs_matches_template"] = _check(
        "crs_matches_template", crs is not None and crs == template_crs,
        f"{crs.to_string() if crs else None} vs {template_crs.to_string() if template_crs else None}",
    )
    checks["transform_matches_template"] = _check(
        "transform_matches_template", transform == template_transform,
        f"{tuple(transform)[:6]} vs {tuple(template_transform)[:6]}",
    )

    if values is not None and shape == template_shape:
        inside = values[footprint]
        outside = values[~footprint]
        finite_inside = np.isfinite(inside)
        valid_range = bool(
            finite_inside.any() and finite_inside.all() and float(inside.min()) >= 0.0 and float(inside.max()) <= 1.0
        )
        checks["footprint_all_finite"] = _check(
            "footprint_all_finite", bool(finite_inside.all()),
            f"{int((~finite_inside).sum()):,} NaN/Inf inside {int(footprint.sum()):,} template cells",
        )
        checks["footprint_values_in_0_1"] = _check(
            "footprint_values_in_0_1", valid_range,
            f"min={float(inside.min()) if finite_inside.all() and inside.size else None}; "
            f"max={float(inside.max()) if finite_inside.all() and inside.size else None}; required finite [0,1]",
        )
        checks["no_infinite_pixels"] = _check(
            "no_infinite_pixels", not np.isinf(values).any(), f"{int(np.isinf(values).sum()):,} infinite values"
        )
        checks["outside_footprint_nan"] = _check(
            "outside_footprint_nan", bool(np.isnan(outside).all()),
            f"{int(np.isnan(outside).sum()):,}/{outside.size:,} outside pixels are NaN; finite outside pixels are forbidden",
        )
        checks["nan_mask_matches_template"] = _check(
            "nan_mask_matches_template", bool(np.array_equal(np.isnan(values), ~footprint)),
            "NaN cells exactly match the template's outside-footprint mask",
        )
        if require_competition_grid:
            checks["output_epsg_32611"] = _check(
                "output_epsg_32611", crs is not None and crs.to_epsg() == EXPECTED_CRS_EPSG,
                f"EPSG:{crs.to_epsg() if crs else None}",
            )
            checks["output_100m_pixels"] = _check(
                "output_100m_pixels", transform.a == 100.0 and transform.e == -100.0,
                f"xres={transform.a:g}, yres={transform.e:g}",
            )
    else:
        checks["footprint_all_finite"] = _check("footprint_all_finite", False, "not evaluated: band count or shape mismatch")
        checks["footprint_values_in_0_1"] = _check("footprint_values_in_0_1", False, "not evaluated: band count or shape mismatch")
        checks["no_infinite_pixels"] = _check("no_infinite_pixels", False, "not evaluated: band count or shape mismatch")
        checks["outside_footprint_nan"] = _check("outside_footprint_nan", False, "not evaluated: band count or shape mismatch")
        checks["nan_mask_matches_template"] = _check("nan_mask_matches_template", False, "not evaluated: band count or shape mismatch")

    checks["nodata_tag_nan_or_none"] = _check(
        "nodata_tag_nan_or_none", nodata is None or (isinstance(nodata, (float, np.floating)) and np.isnan(nodata)),
        f"nodata={nodata}", hard=False,
    )
    hard_failures = [name for name, item in checks.items() if item["hard"] and not item["pass_"]]
    footprint_pixels = int(footprint.sum())
    positive_pixels = int(np.count_nonzero(values[footprint] > 0)) if values is not None and shape == template_shape else None
    return {
        "file": submission_path.name,
        "bytes": submission_path.stat().st_size,
        "sha256": sha256_file(submission_path),
        "ok_to_upload_format_only": not hard_failures,
        "organizer_acceptance_verified": False,
        "hard_failures": hard_failures,
        "grid": {
            "shape": list(shape),
            "crs": crs.to_string() if crs else None,
            "transform": list(transform)[:6],
            "bounds": list(bounds),
            "dtype": list(dtypes),
            "bands": count,
            "template_footprint_pixels": footprint_pixels,
            "positive_pixels_inside": positive_pixels,
            "nodata_tag": "NaN" if isinstance(nodata, (float, np.floating)) and np.isnan(nodata) else nodata,
        },
        "checks": checks,
    }
