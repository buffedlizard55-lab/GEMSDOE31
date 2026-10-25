#!/usr/bin/env python3
"""Build a claim-separated, exact-byte review of the requested leading artifacts."""
from __future__ import annotations

import json
from pathlib import Path

import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
# Values transcribed from the USER REQUEST, not inferred from a model or page.
FOCUS = [
    ("GEMSDOE24", "h25-1-dotted-h19-5-d1-5", "0.2477", "Sparse H19-5 D1.5 emission; prior-art only"),
    ("GEMSDOE25", "dotted-h19-5-d2-8", "0.2600", "D2.8 sparse emission; same NaN TIFF bytes as GEMSDOE24"),
    ("GEMSDOE27", "topo-gap-closure-t-v2-on-d1-5", "0.2449", "Filename/owner method: topological gap closure on D1.5; not refitted here"),
    ("GEMSDOE28", "h36-1-rung30-blind-r1", "0.2710", "Highest user-listed GEMSDOE28 claim; owner-described rung/bridge variant"),
    ("GEMSDOE28", "h27-4-r1-solo-d2-8", "0.2708", "Byte geometry: D2.8 with <=1px catalogue-flank dots deleted"),
    ("GEMSDOE28", "h32-1-prethin-tip-euler-d2-8", "0.2649", "Owner-described pre-thinning tip/Euler variant; not refitted here"),
    ("GEMSDOE28", "h38-1-hf-euler-r30-r1", "0.2707", "Owner-described high-frequency Euler variant; not refitted here"),
    ("GEMSDOE30", "d28-poisson300m-offcat-44090", "0.2600", "D2.8 replay; geometry compared, not a new mechanism"),
    ("GEMSDOE31", "h27-4-solo-d28", "0.2708", "Local legacy H27 reference; do not copy/submit as a new candidate"),
    ("GEMSDOE32", "h33-h33-2-b2", "0.2778", "Byte geometry: D2.8 with <=2px catalogue-flank dots deleted"),
    ("GEMSDOE33", "h33d-analog-tip-stepover-r30", "0.2632", "Owner-described analogue tip/stepover; independent transfer not established here"),
    ("GEMSDOE36", "anderson-geothermal-pinn-38854", "0.2750", "Owner-described Anderson orientation-constrained model; claim not an organizer receipt"),
]


def main():
    inventory = json.loads((ROOT / "evidence/sibling_inventory_20261025.json").read_text())
    tifs = [r for r in inventory["records"] if r["path"].endswith(".tif")]
    anchor = next(r for r in tifs if r["sha256"] == "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9")
    with rasterio.open(ROOT / anchor["cache_file"]) as ds:
        reference = ds.read(1) > 0
    halo = distance_transform_edt(~reference) <= 3
    rows = []
    for repo, needle, value, method in FOCUS:
        matches = [r for r in tifs if r["repo"] == repo and needle in r["path"]]
        if not matches:
            raise ValueError(f"requested prior not found: {repo} {needle}")
        item = sorted(matches, key=lambda r: ("-nan" not in r["path"], r["path"]))[0]
        with rasterio.open(ROOT / item["cache_file"]) as ds:
            m = ds.read(1) > 0
        n = int(m.sum())
        rows.append(dict(repository=repo, artifact=item["path"].split("/")[-1],
                         claim_value=value, score_evidence_class="USER-REPORTED; NOT ORGANIZER-CONFIRMED",
                         claim_source="2026-10-25 user request", organizer_receipt=None,
                         method=method, method_evidence="OWNER-MIRROR description / COMPUTED geometry where specified",
                         source_url=item["source_url"], source_ref=item["ref"], sha256=item["sha256"],
                         positive_pixels=n, exact_shared_dots_with_h33=int((m & reference).sum()),
                         fraction_within_3px_of_h33=float((m & halo).sum() / n) if n else None))
    out = dict(schema_version=1, scope="The nine requested owner sites, pinned GitHub source snapshots; not a live leaderboard feed.",
               score_policy="All listed values are claims in the owner prompt. No organizer receipts were found in the audited score registers. Geometry is not a score.",
               conflicting_leaderboard_claims=["0.3195", "0.4413"],
               live_leaderboard_verified=False, rows=rows)
    (ROOT / "registry/focus_review.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"{len(rows)} claim-separated artifact reviews across {len(set(r['repository'] for r in rows))} repositories")


if __name__ == "__main__":
    main()
