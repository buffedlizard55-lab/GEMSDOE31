#!/usr/bin/env python3
"""Index every prior GEMSDOE submission raster so a new candidate can be tested for uniqueness.

Sources are the owner's public ``*GEMSDOE*`` repositories. The nine focus sites (GEMSDOE24, 25, 27, 28, 30, 31,
32, 33, 36) are pinned to the commits read on 2026-10-25; every other populated GEMSDOE repository is pinned at
the head commit seen when this script ran. Files are fetched with plain ``git`` (partial, sparse, depth-1), not
with the GitHub REST API, because the REST quota is shared and was exhausted during development.

Every single-band raster on the competition grid is hashed and reduced to its emitted dot set. Rasters are not
committed: ``registry/raster_registry.json`` stores repo, commit, path, size and SHA-256 so ``--restore`` can
rebuild ``data/registry_rasters/`` and verify it. A hash proves byte identity to the owner mirror only; scores
attached to a file are the user's brief (class USER-REPORTED) and are never organizer receipts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gemsdoe31.raster import SHAPE  # noqa: E402

OUT = ROOT / "registry" / "raster_registry.json"
CACHE = ROOT / "data" / "registry_rasters"
CLONES = ROOT / "data" / "registry_clones"
OWNER = "buffedlizard55-lab"
FOCUS = {
    "GEMSDOE24": "05f6f85c695ff25546dcc2cbbfa34b3c2a8f4f4c",
    "GEMSDOE25": "0f73c51dc954306468875c02cf98634e64ac0751",
    "GEMSDOE27": "b8dd298e10884afffa05436673ac73aeaf850b8c",
    "GEMSDOE28": "f9c57a50f3e5eba578143eaef3f05233ff5bd071",
    "GEMSDOE30": "3d5bec2af5f29291617f97c9e2dfe443be6f55c3",
    "GEMSDOE31": "cf13282fcd86290f1539f0a86446c8ba7205a79b",
    "GEMSDOE32": "d781d41e809366b2d5430fbca8bf0ebccd25202f",
    "GEMSDOE33": "5ff29347a6f4d59366ddeec910ba7084fcae1087",
    "GEMSDOE36": "c9ad59ec6f969ed931d089a03044c1567a633e84",
}
EXTENDED = (
    ["GEMSDOE", "GEMSDOE2", "GEMSDOE3", "GEMSDOE4", "5GEMSDOE", "6GEMSDOE", "7GEMSDOE", "8GEMSDOE", "GEMSDOE9",
     "GEMSDOE10", "11GEMSDOE", "12GEMSDOE", "13GEMSDOE", "14GEMSDOE", "15GEMSDOE", "16GEMSDOE", "17GEMSDOE",
     "18GEMSDOE", "19GEMSDOE", "20GEMSDOE", "GEMSDOE21", "GEMSDOE22", "GEMSDOE23", "GEMSDOE26", "GEMSDOE29"]
    + [f"GEMSDOE{n}" for n in range(34, 36)] + [f"GEMSDOE{n}" for n in range(37, 55)]
    + [f"{n}GEMSDOE" for n in range(55, 63)] + [f"GEMSDOE{n}" for n in range(63, 93)]
)
SKIP_PATH_PARTS = ("sample_submission", "existing_faults", "/audit_sources/", "labels.tif")
# Owner-reported leaderboard values from the session brief, keyed by a unique file-name fragment.
USER_REPORTED = {
    "h25-1-dotted-h19-5-d1-5": 0.2477, "dotted-h19-5-d2-8": 0.2600, "topo-gap-closure-t-v2-on-d1-5": 0.2449,
    "h27-4-solo-d28": 0.2708, "h27-4-r1-solo-d2-8": 0.2708, "h32-1-prethin-tip-euler-d2-8": 0.2649,
    "h36-1-rung30-blind-r1": 0.2710, "h38-1-hf-euler-r30-r1": 0.2707, "h33d-analog-tip-stepover-r30": 0.2632,
    "h33-h33-2-b2": 0.2778, "anderson-geothermal-pinn-38854": 0.2750,
    "h19-5-powerlaw-budget-multiline-corroborated": 0.1922, "h19-4-multiline-corroborated": 0.1894,
    "lidarscarp-ridge-top2pct": 0.1461,
}


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def git(*args: str, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, check=check, capture_output=True, text=True)


def fetch_commit(repo: str, ref: str | None) -> tuple[Path, str] | None:
    """Partial depth-1 fetch of one commit (head if ``ref`` is None); returns (clone dir, commit sha)."""
    url = f"https://github.com/{OWNER}/{repo}.git"
    if ref is None:
        head = git("ls-remote", url, "HEAD", check=False)
        if head.returncode != 0 or not head.stdout.strip():
            return None
        ref = head.stdout.split()[0]
    path = CLONES / repo
    if not (path / ".git").is_dir():
        path.mkdir(parents=True, exist_ok=True)
        git("init", "-q", cwd=path)
        git("remote", "add", "origin", url, cwd=path)
    fetched = git("fetch", "-q", "--depth", "1", "--filter=blob:limit=4m", "origin", ref, cwd=path, check=False)
    if fetched.returncode != 0:
        return None
    return path, ref


def candidate_paths(clone: Path, ref: str) -> list[tuple[str, int]]:
    listing = git("ls-tree", "-r", "-l", ref, cwd=clone).stdout.splitlines()
    rows = []
    for line in listing:
        meta, path = line.split("\t", 1)
        size = int(meta.split()[3]) if meta.split()[3] != "-" else 0
        if not path.lower().endswith((".tif", ".tiff")) or any(part in path for part in SKIP_PATH_PARTS):
            continue
        if path.startswith("data/") and "docs/" not in path:
            continue
        if 150_000 <= size <= 4_000_000:        # submissions are 0.15-3 MB; inputs/features are larger
            rows.append((path, size))
    return rows


def blob_bytes(clone: Path, ref: str, path: str) -> bytes:
    return subprocess.run(["git", "show", f"{ref}:{path}"], cwd=clone, check=True, capture_output=True).stdout


def dots_of(path: Path) -> tuple[np.ndarray | None, dict]:
    with rasterio.open(path) as src:
        info = {"shape": list(src.shape), "dtype": src.dtypes[0], "count": src.count,
                "crs": src.crs.to_string() if src.crs else None}
        if src.count != 1 or tuple(src.shape) != SHAPE:
            return None, info
        values = src.read(1)
    return np.nan_to_num(values, nan=0.0) > 0, info


def restore(registry: dict) -> int:
    CACHE.mkdir(parents=True, exist_ok=True)
    bad = 0
    for entry in registry["rasters"]:
        dest = CACHE / entry["cache_name"]
        if dest.is_file() and sha256_bytes(dest.read_bytes()) == entry["sha256"]:
            continue
        fetched = fetch_commit(entry["repo"], entry["ref"])
        blob = blob_bytes(fetched[0], entry["ref"], entry["path"]) if fetched else b""
        if sha256_bytes(blob) != entry["sha256"]:
            bad += 1
            print("HASH MISMATCH / unreadable:", entry["cache_name"])
            continue
        dest.write_bytes(blob)
    print(f"restored {len(registry['rasters'])} rasters, failures: {bad}")
    return bad


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--restore", action="store_true", help="re-fetch from the registry and verify hashes")
    parser.add_argument("--focus-only", action="store_true", help="index only the nine focus sites")
    args = parser.parse_args()
    CACHE.mkdir(parents=True, exist_ok=True)
    if args.restore:
        raise SystemExit(1 if restore(json.loads(OUT.read_text())) else 0)

    sites: dict[str, str | None] = dict(FOCUS)
    if not args.focus_only:
        sites.update({name: None for name in EXTENDED if name not in FOCUS})
    rows, pinned, unreadable = [], {}, []
    for repo, ref in sites.items():
        fetched = fetch_commit(repo, ref)
        if not fetched:
            unreadable.append(repo)
            continue
        clone, commit = fetched
        pinned[repo] = commit
        for path, size in candidate_paths(clone, commit):
            cache_name = f"{repo}__{path.replace('/', '__')}"
            blob = blob_bytes(clone, commit, path)
            (CACHE / cache_name).write_bytes(blob)
            dots, info = dots_of(CACHE / cache_name)
            if dots is None:
                (CACHE / cache_name).unlink()
                continue
            flat = np.flatnonzero(dots.ravel()).astype(np.uint32)
            reported = next((v for k, v in USER_REPORTED.items() if k in path), None)
            rows.append({"repo": repo, "ref": commit, "path": path, "bytes": size, **info, "cache_name": cache_name,
                         "sha256": sha256_bytes(blob), "dots": int(flat.size),
                         "dot_set_sha256": sha256_bytes(flat.tobytes()), "user_reported_score": reported,
                         "focus_site": repo in FOCUS})
        print(f"{repo}: pinned {commit[:8]}, {len(rows)} rasters so far", flush=True)
    groups: dict[str, list[dict]] = {}
    for row in rows:
        groups.setdefault(row["dot_set_sha256"], []).append(row)
    unique = []
    for members in groups.values():
        members.sort(key=lambda r: (not r["focus_site"], r["user_reported_score"] is None, r["path"]))
        lead = members[0]
        scores = [m["user_reported_score"] for m in members if m["user_reported_score"] is not None]
        unique.append({**lead, "variants": [f"{m['repo']}:{m['path']}" for m in members],
                       "user_reported_score": max(scores, default=None),
                       "focus_site": any(m["focus_site"] for m in members)})
    keep = {u["cache_name"] for u in unique}
    for member in rows:                      # drop byte-duplicate dot sets from the cache; they are in "variants"
        if member["cache_name"] not in keep and (CACHE / member["cache_name"]).exists():
            (CACHE / member["cache_name"]).unlink()
    unique.sort(key=lambda r: (not r["focus_site"], r["repo"], r["path"]))
    OUT.write_text(json.dumps({
        "schema_version": 1, "generated_utc": "2026-10-25",
        "claim_class": "COMPUTED on owner-mirror bytes; hashes prove mirror identity only; scores are USER-REPORTED",
        "pinned_commits": pinned, "unreadable_repositories": unreadable, "files_scanned": len(rows),
        "unique_dot_sets": len(unique), "rasters": unique}, indent=1) + "\n")
    print(f"scanned {len(rows)} grid rasters -> {len(unique)} unique dot sets; unreadable repos: {unreadable}")
    shutil.rmtree(CLONES, ignore_errors=True)


if __name__ == "__main__":
    main()
