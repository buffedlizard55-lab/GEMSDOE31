import numpy as np
import rasterio
from affine import Affine

from gemsdoe31.submission import validate_submission


def _write(path, values, *, dtype="float32", crs="EPSG:32611", transform=None, nodata=np.nan):
    transform = transform or Affine(100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=values.shape[1],
        height=values.shape[0],
        count=1,
        dtype=dtype,
        crs=crs,
        transform=transform,
        nodata=nodata,
    ) as dst:
        dst.write(values.astype(dtype), 1)


def _template(path):
    values = np.full((12, 10), np.nan, dtype=np.float32)
    values[1:-1, 1:-1] = 0.0
    _write(path, values)
    return values


def test_valid_nan_outside_float32_grid_passes_format_only(tmp_path):
    template = tmp_path / "template.tif"
    _template(template)
    pred = np.full((12, 10), np.nan, dtype=np.float32)
    pred[1:-1, 1:-1] = np.linspace(0.0, 1.0, 80, dtype=np.float32).reshape(10, 8)
    candidate = tmp_path / "candidate.tif"
    _write(candidate, pred)

    result = validate_submission(candidate, template, require_competition_grid=False)

    assert result["ok_to_upload_format_only"] is True
    assert result["organizer_acceptance_verified"] is False
    assert result["hard_failures"] == []
    assert result["checks"]["footprint_values_in_0_1"]["pass_"] is True
    assert result["checks"]["outside_footprint_nan"]["pass_"] is True


def test_inside_nan_is_rejected_to_prevent_range_error(tmp_path):
    template = tmp_path / "template.tif"
    _template(template)
    pred = np.full((12, 10), np.nan, dtype=np.float32)
    pred[1:-1, 1:-1] = 0.25
    pred[5, 5] = np.nan
    candidate = tmp_path / "candidate.tif"
    _write(candidate, pred)

    result = validate_submission(candidate, template, require_competition_grid=False)

    assert result["ok_to_upload_format_only"] is False
    assert "footprint_all_finite" in result["hard_failures"]
    assert "footprint_values_in_0_1" in result["hard_failures"]


def test_below_zero_or_above_one_is_rejected_not_clipped(tmp_path):
    template = tmp_path / "template.tif"
    _template(template)
    for value in (-0.001, 1.001):
        pred = np.full((12, 10), np.nan, dtype=np.float32)
        pred[1:-1, 1:-1] = 0.5
        pred[4, 4] = value
        candidate = tmp_path / f"bad-{value}.tif"
        _write(candidate, pred)
        result = validate_submission(candidate, template, require_competition_grid=False)
        assert result["ok_to_upload_format_only"] is False
        assert "footprint_values_in_0_1" in result["hard_failures"]


def test_finite_values_outside_template_footprint_are_rejected(tmp_path):
    template = tmp_path / "template.tif"
    _template(template)
    pred = np.full((12, 10), np.nan, dtype=np.float32)
    pred[1:-1, 1:-1] = 0.4
    pred[0, 0] = 0.0
    candidate = tmp_path / "outside-zero.tif"
    _write(candidate, pred)

    result = validate_submission(candidate, template, require_competition_grid=False)

    assert result["ok_to_upload_format_only"] is False
    assert "outside_footprint_nan" in result["hard_failures"]
    assert "nan_mask_matches_template" in result["hard_failures"]


def test_shape_and_transform_mismatch_are_rejected(tmp_path):
    template = tmp_path / "template.tif"
    _template(template)
    pred = np.full((12, 10), np.nan, dtype=np.float32)
    pred[1:-1, 1:-1] = 0.5
    candidate = tmp_path / "wrong-grid.tif"
    _write(candidate, pred, transform=Affine(100.0, 0.0, 243450.0, 0.0, -100.0, 4508550.0))

    result = validate_submission(candidate, template, require_competition_grid=False)

    assert result["ok_to_upload_format_only"] is False
    assert "transform_matches_template" in result["hard_failures"]
