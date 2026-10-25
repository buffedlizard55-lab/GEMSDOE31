#!/usr/bin/env python3
"""Reuse/restore the shared 57GEMSDOE cached stack, never a private feature fork.

Calls the vendored cache_bands function unchanged only if required. The output
must match all nineteen hashes in the pinned template's own cache receipt.
Large files and layout symlinks remain Git-ignored.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
from gems57.prepare_data import cache_bands  # noqa: E402


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def prepare(*, verify_only=False):
    pins = json.loads((ROOT / "registry/template_pins.json").read_text())
    for name, pin in pins["files"].items():
        if digest(ROOT / "vendor/gems57" / name) != pin["sha256"]:
            raise ValueError("shared template modified; no private cache fork allowed")
    manifest = json.loads((ROOT / "registry/data_manifest.json").read_text())
    for item in manifest["files"]:
        if item["id"] in {"training_features", "sample_submission"}:
            if digest(ROOT / "data" / item["dest"]) != item["sha256"]:
                raise ValueError("raw cache source hash mismatch")
    expected = pins["cached_feature_stack_reference"]["expected_band_sha256"]
    paths = [ROOT / f".cache/features/band-{i:02d}.npy" for i in range(1, 20)]
    matched = [p.is_file() and digest(p) == pin for p, pin in zip(paths, expected)]
    if all(matched):
        print("Reused template cache: all 19 band hashes match.")
        return
    if verify_only:
        raise ValueError("template cache is absent or has drifted")
    layout = ROOT / "data/official"
    layout.mkdir(parents=True, exist_ok=True)
    for name in ("training_features.tif", "sample_submission.tif"):
        target = layout / name
        if target.exists():
            if digest(target) != digest(ROOT / "data" / name):
                raise ValueError("shared-cache layout source differs")
        else:
            target.symlink_to("../" + name)
    result = cache_bands(ROOT)
    if [r["sha256"] for r in result["bands"]] != expected:
        raise ValueError("regenerated feature arrays differ from the pinned shared cache")
    print("Restored template cache through unchanged cache_bands; all 19 hashes match.")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--verify-only", action="store_true")
    args = ap.parse_args()
    prepare(verify_only=args.verify_only)


if __name__ == "__main__":
    main()
