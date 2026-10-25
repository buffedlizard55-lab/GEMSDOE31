#!/usr/bin/env python3
"""Reuse the unmodified pinned template's masked/sentinel-safe feature cache."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE_ROOT = ROOT / "data/template57"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def verify_template() -> dict:
    pin = json.loads((ROOT / "registry/shared_template.json").read_text())
    for row in pin["files"]:
        if sha256(ROOT / row["path"]) != row["sha256"]:
            raise ValueError(f"shared template was modified: {row['path']}")
    return pin


def prepare() -> dict:
    pin = verify_template()
    manifest = json.loads((ROOT / "registry/data_manifest.json").read_text())
    selected = {"training_features.tif", "labels.tif", "sample_submission.tif"}
    for row in manifest["files"]:
        if row["dest"] not in selected:
            continue
        source = ROOT / "data" / row["dest"]
        if sha256(source) != row["sha256"]:
            raise ValueError(f"raw owner-mirror hash mismatch: {source}")
        destination = CACHE_ROOT / "data/official" / row["dest"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists():
            destination.symlink_to(os.path.relpath(source, destination.parent))
    evidence = CACHE_ROOT / "evidence/feature_cache.json"
    if evidence.exists():
        receipt = json.loads(evidence.read_text())
        if receipt["source_sha256"] == sha256(ROOT / "data/training_features.tif"):
            if all(sha256(CACHE_ROOT / r["cache_file"]) == r["sha256"] for r in receipt["bands"]):
                print("Reused hash-verified shared template cache", flush=True)
                return receipt
    spec = importlib.util.spec_from_file_location("pinned_template57_prepare", ROOT / "vendor/template57/prepare_data.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load pinned template cache builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    receipt = module.cache_bands(CACHE_ROOT)
    receipt["shared_template_repository"] = pin["repository"]
    receipt["shared_template_ref"] = pin["ref"]
    receipt["cache_rebuilt_because_absent"] = True
    (ROOT / "evidence/shared_feature_cache.json").write_text(json.dumps(receipt, indent=1, allow_nan=False) + "\n")
    print(f"Prepared {receipt['count']} original-template bands; hashes recorded", flush=True)
    return receipt


if __name__ == "__main__":
    prepare()
