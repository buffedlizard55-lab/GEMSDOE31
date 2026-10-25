#!/usr/bin/env python3
"""Freeze the already retrieved, commit-pinned owner-repository audit inventory.

No network access, leaderboard retrieval, selection or threshold exemptions.
Raw mirrors remain ignored under data/. A future restore can use each pinned
repo/ref/path and SHA-256 without replacing any recorded pin.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOCUS = ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
         "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36")


def main() -> None:
    base = ROOT / "data/prior_audit"
    rows = []
    for name in ("all_receipts.json", "extended_receipts.json"):
        rows.extend(json.loads((base / name).read_text()))
    raster_rows = [r for r in rows if r["kind"] == "raster"]
    grouped: dict[str, dict] = {}
    errors = []
    for row in raster_rows:
        if "error" in row:
            errors.append({k: row[k] for k in ("repo", "ref", "path")}
                         | {"reason": "GitHub REST core quota exhausted; bytes not retrieved"})
            continue
        path = ROOT / row["local_path"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != row["sha256"]:
            raise ValueError(f"retrieved mirror changed: {path}")
        record = grouped.setdefault(digest, {
            "sha256": digest, "bytes": path.stat().st_size, "cache_file": row["local_path"],
            "repo_first": row["repo"], "sources": [], "source_records": [],
        })
        source = f"https://github.com/{row['repo']}/blob/{row['ref']}/{row['path']}"
        record["sources"].append(source)
        record["source_records"].append({k: row[k] for k in ("repo", "ref", "path")})
    trees = []
    for path in sorted(base.glob("*_tree.json")):
        tree = json.loads(path.read_text())
        trees.append({"repo": tree["repo"], "commit": tree["commit"],
                      "tree_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                      "tree_truncated": tree.get("truncated", False)})
    rasters = list(grouped.values())
    # Preserve every registered artifact, including dense and off-grid controls.
    # Such entries can block the gate; they are not silently filtered out.
    record = {
        "schema_version": 1, "snapshot_date_utc": "2026-10-25",
        "evidence_class": "OWNER-MIRROR-INVENTORY", "focus_repositories": list(FOCUS),
        "repositories": trees, "complete_accessible_scan": not errors,
        "published_raster_paths_expected": len(raster_rows),
        "published_raster_paths_restored": len(raster_rows) - len(errors),
        "unique_byte_rasters_restored": len(rasters), "errors": errors, "rasters": rasters,
        "scope": "Published docs/ TIFFs <10 MB in the pinned owner-family trees; includes archived and dense controls. "
                 "The nine focus repositories were inspected more deeply. Not an organizer-complete registry; "
                 "private/unlinked artifacts and later concurrent changes are unknown.",
    }
    (ROOT / "registry/prior_raster_snapshot.json").write_text(json.dumps(record, indent=1) + "\n")
    focus_rasters = [r for r in rasters if any(s["repo"].split("/")[-1] in FOCUS for s in r["source_records"])]
    focus_errors = [r for r in errors if r["repo"].split("/")[-1] in FOCUS]
    focus = dict(record, rasters=focus_rasters, errors=focus_errors,
                 complete_accessible_scan=not focus_errors,
                 scope="All retrieved published TIFFs in the nine required repositories, including historical controls; "
                       "not a complete organizer or full owner-family registry.")
    (ROOT / "registry/focus_raster_snapshot.json").write_text(json.dumps(focus, indent=1) + "\n")
    print(f"Indexed {len(trees)} repos, {len(rasters)} unique raster byte streams, {len(errors)} missing paths")


if __name__ == "__main__":
    main()
