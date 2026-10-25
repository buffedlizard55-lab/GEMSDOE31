#!/usr/bin/env python3
"""Pin and audit the nine requested owner repositories; never contact DrivenData.

Cache prior-art TIFFs ONLY for education / duplicate checking in ignored work/.
The Git blob identifier from each pinned tree is checked on retrieval. Scores
from the request remain USER-REPORTED, never organizer-confirmed.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
REPOS = ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
         "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36")


def api(endpoint, *, raw=False):
    cmd = ["gh", "api", endpoint]
    if raw:
        cmd += ["-H", "Accept: application/vnd.github.raw"]
    return subprocess.check_output(cmd, timeout=180)


def fetch_entry(item):
    path = ROOT / item["cache_file"]
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        content = api(f'repos/buffedlizard55-lab/{item["repo"]}/contents/{item["path"]}?ref={item["ref"]}', raw=True)
        path.write_bytes(content)
    content = path.read_bytes()
    blob = hashlib.sha1(f"blob {len(content)}\0".encode() + content).hexdigest()
    if blob != item["git_blob"]:
        raise ValueError(f'Git blob mismatch: {item["repo"]} {item["path"]}')
    item.update(sha256=hashlib.sha256(content).hexdigest(), bytes=len(content))
    if path.suffix == ".tif":
        with rasterio.open(path) as ds:
            a = ds.read(1)
            item.update(shape=list(ds.shape), crs=str(ds.crs), transform=list(ds.transform)[:6],
                        bands=ds.count, dtype=ds.dtypes[0], positive_pixels=int((a > 0).sum()),
                        finite_pixels=int(np.isfinite(a).sum()))
    return item


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--snapshots", default="work/prior_art")
    args = ap.parse_args()
    cache = ROOT / args.snapshots
    items, repos = [], []
    for repo in REPOS:
        d = cache / repo
        d.mkdir(parents=True, exist_ok=True)
        snapshot = d / "snapshot.json"
        if snapshot.exists():
            snap = json.loads(snapshot.read_text())
        else:
            meta = json.loads(api(f"repos/buffedlizard55-lab/{repo}"))
            ref = json.loads(api(f'repos/buffedlizard55-lab/{repo}/commits/{meta["default_branch"]}'))["sha"]
            snap = dict(repo=repo, ref=ref, tree=json.loads(api(f"repos/buffedlizard55-lab/{repo}/git/trees/{ref}?recursive=1")))
            snapshot.write_text(json.dumps(snap, indent=1) + "\n")
        if snap["tree"].get("truncated"):
            raise ValueError(f"truncated tree: {repo}")
        repos.append(dict(repo=repo, ref=snap["ref"], tree_complete=True,
                          url=f'https://github.com/buffedlizard55-lab/{repo}/tree/{snap["ref"]}'))
        for f in snap["tree"]["tree"]:
            p = f["path"]
            wanted_tif = p.startswith("docs/downloads/") and p.endswith(".tif")
            wanted_doc = p == "README.md" or (p.startswith("registry/") and p.endswith(".json"))
            if f["type"] != "blob" or not (wanted_tif or wanted_doc):
                continue
            # A complete docs/downloads inventory is the fixed registry universe,
            # not a hand-picked subset of sparse or conveniently dissimilar files.
            items.append(dict(repo=repo, ref=snap["ref"], path=p, git_blob=f["sha"],
                              cache_file=str((d / p).relative_to(ROOT)),
                              source_url=f'https://github.com/buffedlizard55-lab/{repo}/blob/{snap["ref"]}/{p}',
                              role="prior-art-only; never a candidate input"))
    with ThreadPoolExecutor(max_workers=6) as pool:
        records = list(pool.map(fetch_entry, items))
    rasters = [r for r in records if r["path"].endswith(".tif")]
    payload = dict(schema_version=1, evidence_class="OWNER-MIRROR / COMPUTED inventory",
                   captured_utc="2026-10-25", repositories=repos, records=records,
                   raster_count=len(rasters), unique_byte_rasters=len({r["sha256"] for r in rasters}),
                   scope="ALL .tif files under docs/downloads/ (including research subdirectories) in the nine pinned repositories. No claim about private, unlinked, other paths, other sites, or later revisions.",
                   score_policy="No organizer receipt. User-provided results remain USER-REPORTED. No DrivenData page contacted.")
    out = ROOT / "evidence/sibling_inventory_20261025.json"
    out.write_text(json.dumps(payload, indent=1, allow_nan=False) + "\n")
    print(json.dumps(dict(repositories=len(repos), raster_count=len(rasters),
                          unique_byte_rasters=payload["unique_byte_rasters"],
                          max_positive_pixels=max(r["positive_pixels"] for r in rasters)), indent=1))


if __name__ == "__main__":
    main()
