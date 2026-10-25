#!/usr/bin/env python3
"""Restore hash-pinned public owner mirrors into ``data/`` (no DrivenData contact).

Every entry in ``registry/data_manifest.json`` names a public GitHub repository, a pinned commit,
an object path and a SHA-256. Bytes are streamed (never buffered whole in RAM) and verified before
the file is accepted. A hash match proves byte identity to that mirror only: it is **not** an
organizer-authenticated download and must never be reported as one.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "registry" / "data_manifest.json"
UA = {"User-Agent": "GEMSDOE31-research/1.0"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _download(repo: str, ref: str, remote: str, destination: Path) -> None:
    """Fetch through api.github.com; never mask a configured gh failure."""
    endpoint = f"repos/{repo}/contents/{remote}?ref={ref}"
    if shutil.which("gh"):
        with destination.open("wb") as out:
            result = subprocess.run(
                ["gh", "api", endpoint, "-H", "Accept: application/vnd.github.raw+json"],
                stdout=out, stderr=subprocess.PIPE, timeout=1800, check=False,
            )
        if result.returncode:
            text = result.stderr.decode(errors="replace")
            if any(s in text.lower() for s in ("bad credentials", "authentication", "gh auth login")):
                raise RuntimeError("GitHub connection needs attention; reconnect GitHub in Arena.")
            raise RuntimeError(f"GitHub API failed for {remote}; no fallback to an unapproved host")
        if not destination.stat().st_size:
            raise RuntimeError(f"GitHub API returned an empty object for {remote}")
        return
    request = urllib.request.Request("https://api.github.com/" + endpoint,
                                     headers={**UA, "Accept": "application/vnd.github.raw+json"})
    with urllib.request.urlopen(request, timeout=600) as response, destination.open("wb") as out:
        shutil.copyfileobj(response, out, length=1 << 20)


def restore(entry: dict, data_dir: Path) -> dict:
    dest = data_dir / entry["dest"]
    if dest.is_file() and sha256_file(dest) == entry["sha256"]:
        return {"id": entry["id"], "status": "already-verified", "bytes": dest.stat().st_size,
                "sha256": entry["sha256"], "dest": entry["dest"]}
    dest.parent.mkdir(parents=True, exist_ok=True)
    partial = dest.with_name(dest.name + ".partial")
    partial.unlink(missing_ok=True)
    parts = entry.get("parts")
    piece = dest.parent / (dest.name + ".part.tmp")
    try:
        if parts:
            with partial.open("wb") as out:
                for part in parts:
                    piece.unlink(missing_ok=True)
                    _download(entry["repo"], entry["ref"], part, piece)
                    with piece.open("rb") as src:
                        shutil.copyfileobj(src, out, length=1 << 20)
                    piece.unlink(missing_ok=True)
        else:
            _download(entry["repo"], entry["ref"], entry["path"], partial)
        actual = sha256_file(partial)
        if actual != entry["sha256"]:
            raise RuntimeError(f"hash mismatch for {entry['id']}: {actual} != {entry['sha256']}")
        partial.replace(dest)
    finally:
        partial.unlink(missing_ok=True)
        piece.unlink(missing_ok=True)
    return {"id": entry["id"], "status": "restored", "bytes": dest.stat().st_size,
            "sha256": entry["sha256"], "dest": entry["dest"],
            "repo": entry["repo"], "ref": entry["ref"]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--group", choices=("all", "core", "external"), default="all")
    parser.add_argument("--out", default="evidence/data_restore.json")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    data_dir = (ROOT / args.data_dir).resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for entry in manifest["files"]:
        if args.group not in ("all", entry["group"]):
            continue
        row = restore(entry, data_dir)
        row["group"] = entry["group"]
        row["provenance"] = entry["provenance"]
        rows.append(row)
        print(f"{row['status']:<16} {row['dest']:<48} {row['bytes']:>12,} B")
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "schema_version": 1,
        "note": ("Hash-pinned public owner mirrors. Byte identity to the mirror is proven; organizer "
                 "authenticity is NOT. DrivenData was not contacted."),
        "data_dir": str(data_dir),
        "files": rows,
        "all_verified": bool(rows) and all(r["status"] in ("restored", "already-verified") for r in rows),
    }, indent=1) + "\n")
    print(f"\n{out.relative_to(ROOT)}: all_verified="
          f"{all(r['status'] in ('restored', 'already-verified') for r in rows)}")


if __name__ == "__main__":
    main()
