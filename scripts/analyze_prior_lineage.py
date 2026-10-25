#!/usr/bin/env python3
"""Re-measure the prior sparse-dot lineage for education; never reuse its dots."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
# These digests come from the audited, pinned nine-repository inventory.
PINS = {
    "d15": "68d0e2e4fcc594f9a23f56c44b885fee733d026d39be55e18ad2a07289525310",
    "d28": "91eae1ca42ec845eaa8c2ba32da49806e24751743459b8a10017c479bbe639b8",
    "h27": "ab02300152248fdda04e988e2cd2a0c13f35eec42fcf670a15e8b76b19e24a73",
    "h33": "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9",
}


def main():
    inventory = json.loads((ROOT / "evidence/sibling_inventory_20261025.json").read_text())
    with rasterio.open(ROOT / "data/labels.tif") as ds:
        cat = ds.read(1) == 1
    with rasterio.open(ROOT / "data/sample_submission.tif") as ds:
        fp = np.isfinite(ds.read(1))
    distance = distance_transform_edt(~cat)
    masks, records = {}, {}
    for key, digest in PINS.items():
        item = next(r for r in inventory["records"] if r["sha256"] == digest)
        path = ROOT / item["cache_file"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError("prior artifact hash drift")
        with rasterio.open(path) as ds:
            a = ds.read(1)
        m = (a > 0) & fp
        masks[key] = m
        points = np.argwhere(m)
        nn = cKDTree(points).query(points, k=2)[0][:, 1] * 100
        records[key] = dict(source_url=item["source_url"], sha256=digest,
                            dots=int(m.sum()), dots_on_catalogue=int((m & cat).sum()),
                            dots_beyond_300m=int((m & (distance > 3)).sum()),
                            nearest_neighbor_m=dict(min=float(nn.min()), median=float(np.median(nn))))
    relations = dict(
        h27_equals_d28_prune_at_1px=bool(np.array_equal(masks["h27"], masks["d28"] & (distance > 1))),
        h33_equals_d28_prune_at_2px=bool(np.array_equal(masks["h33"], masks["d28"] & (distance > 2))),
        h33_is_subset_h27=bool(not (masks["h33"] & ~masks["h27"]).any()),
        h27_to_h33_dots_removed=int((masks["h27"] & ~masks["h33"]).sum()),
        common_beyond_300m_dots=int((masks["h33"] & masks["h27"] & masks["d28"] & (distance > 3)).sum()),
        offcat_support_equal_beyond_300m=bool(np.array_equal(masks["h33"] & (distance > 3), masks["d28"] & (distance > 3))),
    )
    out = dict(evidence_class="COMPUTED geometry / OWNER-MIRROR provenance; NOT DTI or competition scores",
               records=records, relations=relations,
               score_status="The request's historical values are USER-REPORTED; no organizer score-to-file receipt.",
               scientific_limit="Equal dot support beyond 300m does NOT imply equal kernel credit; a removed near-catalogue dot can cover nearby off-catalogue truth.")
    path = ROOT / "evidence/prior_lineage_20261025.json"
    path.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(relations, indent=1))


if __name__ == "__main__":
    main()
