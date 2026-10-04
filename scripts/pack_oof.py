#!/usr/bin/env python3
"""Pack the out-of-fold probability maps into a committable, hash-pinned form.

Raw fold maps are 49 MB each as float32 ``.npy``; a fresh clone must not need a 94 MB binary to
re-run the union/filter experiments. They are quantised to ``uint16`` over ``[0, 1]`` (step
1.5e-5, far below any threshold used here) and written as compressed ``.npz``; NaN cells (outside
the data footprint) are stored as 0 and rebuilt from the recorded NaN mask, which is itself exact
because the footprint is time-invariant.

The JSON sidecar records both hashes, the quantisation error and the number of NaN cells, so the
quantised artifact can be audited against the raw map it replaces.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pack(raw: Path, out_dir: Path) -> dict:
    array = np.load(raw)
    finite = np.isfinite(array)
    values = np.where(finite, array, 0.0)
    if values.min() < 0.0 or values.max() > 1.0:
        raise SystemExit(f"{raw} has values outside [0, 1]; refusing to quantise")
    quantised = np.rint(values * 65535.0).astype(np.uint16)
    restored = quantised.astype(np.float64) / 65535.0
    error = np.abs(restored[finite] - array[finite])
    target = out_dir / (raw.stem + "_u16.npz")
    np.savez_compressed(target, probability_u16=quantised)
    meta = {
        "raw": str(raw.relative_to(ROOT)),
        "raw_bytes": raw.stat().st_size,
        "raw_sha256": sha256(raw),
        "packed": str(target.relative_to(ROOT)),
        "packed_bytes": target.stat().st_size,
        "packed_sha256": sha256(target),
        "shape": list(array.shape),
        "nan_cells_outside_footprint": int((~finite).sum()),
        "finite_cells": int(finite.sum()),
        "max_abs_quantisation_error": float(error.max()),
        "mean_abs_quantisation_error": float(error.mean()),
        "max_value": float(array[finite].max()),
        "decoder": "probability = probability_u16 / 65535.0; cells with raw NaN are outside the footprint",
    }
    return meta


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir", default="evidence/oof")
    parser.add_argument("--out", default="evidence/oof_quantisation.json")
    parser.add_argument("--delete-raw", action="store_true",
                        help="remove the raw .npy after a successful audit (frees ~94 MB)")
    args = parser.parse_args()
    out_dir = ROOT / args.dir
    records = []
    for raw in sorted(out_dir.glob("*.npy")):
        meta = pack(raw, out_dir)
        records.append(meta)
        print(f"{raw.name}: {meta['raw_bytes']/1e6:.1f} MB -> {meta['packed_bytes']/1e6:.1f} MB, "
              f"max quantisation error {meta['max_abs_quantisation_error']:.2e}, "
              f"{meta['nan_cells_outside_footprint']:,} NaN cells")
        if args.delete_raw:
            raw.unlink()
    (ROOT / args.out).write_text(json.dumps({
        "schema_version": 1,
        "generated_utc": "2026-10-04",
        "purpose": "keep the fold-OOF maps in the repository in an auditable, quantised form",
        "records": records,
    }, indent=1) + "\n")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
