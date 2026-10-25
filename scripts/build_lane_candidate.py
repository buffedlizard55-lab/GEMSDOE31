#!/usr/bin/env python3
"""Emit the frozen AS-1 candidate as a unique, format-checked GeoTIFF (NOT a promotion: see evidence/lane_e3.json).

Uses the full public catalogue as the visible set (it is masked by the organizer anyway), the template footprint
(never a feature band) as the footprint, and the same procedure file that E3 evaluated (scripts/lane_candidate.py).
Also runs the *pre-placement* surface check against every registry raster.
"""

from __future__ import annotations

import hashlib
import json
import sys
import zipfile  # noqa: F401  (kept for parity with build_submission)

import numpy as np
from build_submission import write_variants
from lane_candidate import BUDGET, CANDIDATE_ID, emit_candidate, surface
from lane_common import ROOT, load_base, load_lidar, write_json

sys.path.insert(0, str(ROOT / "src"))
from gemsdoe31 import gate  # noqa: E402

DATE = "20261025"
NOTE = "GEMSDOE31 AS-1: LiDAR antislope-scarp dots, 38k px, off-catalogue. UNSCORED. Holdout gate failed: do not rank on this."


def main() -> None:
    assert len(NOTE) <= 140, len(NOTE)
    base = load_base()
    lid = load_lidar()
    valid = (lid["valid"] > 0) & base["footprint"]
    surf = surface(lid, valid)
    dots = emit_candidate(surf, valid, base["catalogue"], BUDGET) & base["footprint"]
    dot_hash = hashlib.sha256(np.flatnonzero(dots.ravel()).astype(np.uint32).tobytes()).hexdigest()
    name = f"gemsdoe31-as1-lidar-antislope-{int(dots.sum())}dots-{DATE}-{dot_hash[:8]}"
    out_dir = ROOT / "docs/downloads/blocked"
    paths = write_variants(dots, base["footprint"], out_dir / name, name=name)

    # pre-placement check: label-free surface vs registry density (500 m blocks)
    registry = json.loads((ROOT / "registry/raster_registry.json").read_text())["rasters"]
    domain = gate.footprint_blocks(base["footprint"])
    surf_blocks = _block_mean(surf, gate.BLOCK_PX)
    rows = []
    for e in registry:
        other = gate.read_dots(ROOT / "data/registry_rasters" / e["cache_name"])
        rows.append((gate.spearman_blocks(surf_blocks, gate.block_density(other), domain), e["path"], e.get("user_reported_score")))
    rows.sort(reverse=True)
    pre = {"claim_class": "COMPUTED, label-free surface; LiDAR-valid zone only",
           "registry_rasters_compared": len(rows), "max_spearman_surface_vs_registry_density": rows[0][0],
           "limit": gate.DUPLICATE_RHO, "passes": rows[0][0] <= gate.DUPLICATE_RHO,
           "top5": [{"file": f, "spearman": r, "user_reported_score": s} for r, f, s in rows[:5]]}
    meta = {"candidate": CANDIDATE_ID, "name": name, "note": NOTE, "note_chars": len(NOTE), "dots": int(dots.sum()),
            "dot_set_sha256": dot_hash, "files": {k: str(v.relative_to(ROOT)) for k, v in paths.items()},
            "pre_placement_surface_check": pre}
    write_json(ROOT / "evidence/lane_candidate_build.json", meta)
    print(name)
    print(json.dumps(pre, indent=1, default=float)[:900])


def _block_mean(arr: np.ndarray, block: int) -> np.ndarray:
    h, w = arr.shape
    hb, wb = -(-h // block), -(-w // block)
    pad = np.zeros((hb * block, wb * block), dtype=np.float32)
    pad[:h, :w] = arr
    return pad.reshape(hb, block, wb, block).mean(axis=(1, 3))


if __name__ == "__main__":
    main()
