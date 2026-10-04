"""Pinned bridge to the previously audited GEMSDOE25 reference implementation and mirror caches."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np

from .h31_features import FEATURE_NAMES, build_magnetic_scale_features

SIBLING_REPOSITORY = "https://github.com/buffedlizard55-lab/GEMSDOE25"
SIBLING_REVISION = "c185edd8b09e19846cf34c16050e6cf891ecc2d0"
SIBLING_CACHE_MANIFEST_SHA256 = "95ece61d1cc12a446eaa9ff3ca32775fd2842901a7d33d094836341d95994d6f"
SIBLING_DATA_MANIFEST_SHA256 = "5a0f9b95efd7a8e77f2e0a3162fda235f8dd0253cef187165ad7c0c003321c66"

CACHE_FILES = (
    "static_ABCD.npy",
    "static_ABCD.npy.names.json",
    "addons.npy",
    "addons.npy.names.json",
    "bands/_footprint.npy",
    "bands/_labels.npy",
)
RAW_FILE_HASHES = {
    "training_features.tif": "4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5",
    "labels.tif": "7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093",
    "sample_submission.tif": "2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc",
    "external/lidar_scarp_features_u8.tif": "d580bb8bdcdb941e32fefb8b38044bc5bf04e199bf2e83498c3576e6fc465568",
    "external/geodawn_rad_u8.tif": "c22420f75999030d7cc65c9e31e50d232ea6158423bca051613a18a8b20ba682",
    "external/geodawn_extensions_u8.tif": "a35a9c6d2a14786f4dab85481ee59769213072f5dab5b2535ea82ae4d9bb7d9b",
    "external/gdr_wellspring_in_footprint.csv": "122718e65bdf55aab0ee12ad20d80062f0deb1de957225a61ad880dd5dc196ea",
}


class StackedStatic:
    """Array-like view that appends a few feature vectors without copying a 1.3 GB base memmap."""

    def __init__(self, base: np.ndarray, extra: np.ndarray):
        self.base = base
        self.extra = np.asarray(extra, dtype=np.float32)
        if base.ndim != 2 or self.extra.ndim != 2 or base.shape[1] != self.extra.shape[1]:
            raise ValueError("base and extra static matrices must align as (feature, footprint_pixel)")
        self.shape = (base.shape[0] + self.extra.shape[0], base.shape[1])
        self.ndim = 2
        self.dtype = np.dtype(np.float32)

    def __getitem__(self, key):
        if isinstance(key, tuple):
            if len(key) != 2:
                raise IndexError("static matrices require a row and column index")
            row_key, col_key = key
        else:
            row_key, col_key = key, slice(None)
        row_index = np.arange(self.shape[0])[row_key]
        if np.ndim(row_index) == 0:
            row = int(row_index)
            if row < 0 or row >= self.shape[0]:
                raise IndexError(row)
            if row < self.base.shape[0]:
                return self.base[row, col_key]
            return self.extra[row - self.base.shape[0], col_key]
        row_index = np.asarray(row_index, dtype=np.int64).reshape(-1)
        values = []
        for row in row_index.tolist():
            if row < 0 or row >= self.shape[0]:
                raise IndexError(row)
            if row < self.base.shape[0]:
                values.append(np.asarray(self.base[row, col_key], dtype=np.float32))
            else:
                values.append(np.asarray(self.extra[row - self.base.shape[0], col_key], dtype=np.float32))
        return np.stack(values, axis=0)


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def verify_sibling(sibling_root: str | Path, data_dir: str | Path, work_dir: str | Path) -> dict[str, Any]:
    root, data, work = Path(sibling_root).resolve(), Path(data_dir).resolve(), Path(work_dir).resolve()
    if not (root / ".git").exists():
        raise ValueError(f"reference sibling is not a Git checkout: {root}")
    revision = _git(root, "rev-parse", "HEAD")
    if revision != SIBLING_REVISION:
        raise ValueError(f"GEMSDOE25 revision drift: {revision} != pinned {SIBLING_REVISION}")
    status = _git(root, "status", "--porcelain")
    if status:
        raise ValueError("reference GEMSDOE25 checkout is dirty; refuse to use unpinned implementation")

    cache_manifest_path = root / "evidence" / "work_cache_hashes.json"
    data_manifest_path = root / "registry" / "data_manifest.json"
    if sha256_file(cache_manifest_path) != SIBLING_CACHE_MANIFEST_SHA256:
        raise ValueError("reference cache-hash manifest differs from its pinned SHA-256")
    if sha256_file(data_manifest_path) != SIBLING_DATA_MANIFEST_SHA256:
        raise ValueError("reference data manifest differs from its pinned SHA-256")
    cache_manifest = json.loads(cache_manifest_path.read_text())
    verified_caches: dict[str, dict[str, int | str]] = {}
    for relative in CACHE_FILES:
        path = work / relative
        expected = cache_manifest.get(relative)
        if not isinstance(expected, dict) or not path.is_file():
            raise FileNotFoundError(f"required cache or pin missing: {path}")
        actual = {"sha256": sha256_file(path), "bytes": path.stat().st_size}
        if actual != {"sha256": expected.get("sha256"), "bytes": expected.get("bytes")}:
            raise ValueError(f"derived cache drift for {relative}: {actual}")
        verified_caches[relative] = actual

    verified_inputs: dict[str, dict[str, int | str]] = {}
    for relative, expected_hash in RAW_FILE_HASHES.items():
        path = data / relative
        if not path.is_file():
            raise FileNotFoundError(f"required pinned mirror input missing: {path}")
        actual = {"sha256": sha256_file(path), "bytes": path.stat().st_size}
        if actual["sha256"] != expected_hash:
            raise ValueError(f"raw mirror hash drift for {relative}: {actual['sha256']} != {expected_hash}")
        verified_inputs[relative] = actual
    return {
        "sibling_repository": SIBLING_REPOSITORY,
        "sibling_revision": revision,
        "sibling_clean_worktree": True,
        "cache_hash_manifest_sha256": SIBLING_CACHE_MANIFEST_SHA256,
        "data_manifest_sha256": SIBLING_DATA_MANIFEST_SHA256,
        "verified_cache_hashes": verified_caches,
        "verified_input_hashes": verified_inputs,
    }


def build_context(
    sibling_root: str | Path,
    data_dir: str | Path,
    work_dir: str | Path,
    *,
    buffer_px: int,
) -> tuple[Any, Any, Any, dict[str, Any]]:
    """Load verified base caches, append H31 features virtually, and create the pinned model context."""
    if isinstance(buffer_px, bool) or not isinstance(buffer_px, int) or buffer_px < 1:
        raise ValueError("buffer_px must be a positive integer")
    root, data, work = Path(sibling_root).resolve(), Path(data_dir).resolve(), Path(work_dir).resolve()
    provenance = verify_sibling(root, data, work)
    src = str(root / "src")
    if src not in sys.path:
        sys.path.insert(0, src)

    from gems25 import holdout as holdout_module
    from gems25.experiment import Context
    from gems25.families import family_columns

    # Set before Context constructs Holdout. The pilot's 5 px collar is passed only to stage='pilot'; subsequent
    # collars are read from the measured residual variogram and are not hard-coded here.
    holdout_module.COLLAR_PX = buffer_px

    footprint = np.load(work / "bands" / "_footprint.npy", mmap_mode="r")
    labels = np.load(work / "bands" / "_labels.npy", mmap_mode="r")
    base_static = np.load(work / "static_ABCD.npy", mmap_mode="r")
    base_names = json.loads((work / "static_ABCD.npy.names.json").read_text())
    addon = np.load(work / "addons.npy", mmap_mode="r")

    hg_path = work / "bands" / "03_tmi_hg.npy"
    vg_path = work / "bands" / "09_tmi_vg.npy"
    if not hg_path.is_file() or not vg_path.is_file():
        raise FileNotFoundError("prepared 03_tmi_hg.npy and 09_tmi_vg.npy are required")
    features, feature_diagnostics = build_magnetic_scale_features(
        np.load(hg_path, mmap_mode="r"), np.load(vg_path, mmap_mode="r"), footprint
    )
    fi = np.flatnonzero(footprint.ravel())
    feature_vectors = np.asarray(features.reshape(2, -1)[:, fi], dtype=np.float32)
    del features

    static_names = list(base_names) + list(FEATURE_NAMES)
    static = StackedStatic(base_static, feature_vectors)
    context = Context(footprint, labels, static, static_names, addon)
    context.raw_grid_shape = tuple(footprint.shape)
    context.h31_feature_diagnostics = feature_diagnostics.as_dict()
    context.h31_family_columns = family_columns
    provenance["feature_build"] = feature_diagnostics.as_dict()
    provenance["numpy"] = importlib.metadata.version("numpy")
    provenance["scipy"] = importlib.metadata.version("scipy")
    provenance["scikit_learn"] = importlib.metadata.version("scikit-learn")
    provenance["rasterio"] = importlib.metadata.version("rasterio")
    return context, holdout_module, __import__("gems25.experiment", fromlist=["Cell"]), provenance
