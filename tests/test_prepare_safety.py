import hashlib
import importlib.util
from pathlib import Path

import numpy as np
import rasterio
from affine import Affine

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("prepare_common", ROOT / "scripts/prepare_data.py")
prepare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare)


def write(path, bands, names, *, nodata=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(path, "w", driver="GTiff", width=bands.shape[2], height=bands.shape[1],
                       count=len(bands), dtype=str(bands.dtype), nodata=nodata,
                       crs="EPSG:32611", transform=Affine(100, 0, 243350, 0, -100, 4508550)) as ds:
        ds.write(bands)
        ds.descriptions = tuple(names)


def test_common_static_stack_never_reads_or_caches_target_geometry(tmp_path, monkeypatch):
    shape = (10, 12)
    monkeypatch.setattr(prepare, "SHAPE", shape)
    a = np.ones((19,) + shape, np.float32)
    a[0, 2, 3] = np.finfo(np.float32).min
    write(tmp_path / "training_features.tif", a, prepare.COMPETITION_BANDS)
    for path, names in (("lidar_scarp_features_u8.tif", prepare.LIDAR_BANDS),
                         ("geodawn_rad_u8.tif", prepare.RAD_BANDS),
                         ("geodawn_extensions_u8.tif", prepare.EXT_BANDS)):
        write(tmp_path / "external" / path, np.ones((len(names),) + shape, np.uint8), names)
    # No labels, SGMC, vent or probe file exists: preparing static physics must
    # succeed without touching truth/candidate geometry.
    meta = prepare.build(tmp_path, tmp_path / "prepared")
    stack = np.memmap(tmp_path / "prepared/features.f32", dtype=np.float32, mode="r",
                      shape=(len(meta["bands"]),) + shape)
    assert np.isnan(stack[0, 2, 3]), "finite Float32-min sentinel must not survive cleaning"
    assert meta["label_derived_features"] is False
    assert not any("dist_cat" in n or "sgmc" in n for n in meta["bands"])
    assert len(meta["bands"]) == 42


def test_hash_equality_does_not_hide_a_wrong_grid(tmp_path):
    path = tmp_path / "wrong-grid.tif"
    write(path, np.ones((1, 4, 5), np.float32), ["test"])
    manifest = {"files": [{"id": "wrong", "dest": path.name,
                            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}]}
    rows = prepare.verify(manifest, tmp_path)
    assert rows[0]["sha256_match"] is True
    assert rows[0]["grid_matches"] is False
