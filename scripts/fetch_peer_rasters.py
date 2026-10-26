#!/usr/bin/env python3
"""Fetch the nine focus sites' top rasters, hash-verified, for LEARNING ONLY.

Source of truth: ``evidence/h33_forensics_20261025.json`` pinning repo, ref,
published path and SHA-256 per requested artifact. Bytes land in
``data/prior_audit/<REPO>/<published path>`` (git-ignored) and a receipt is
written to ``evidence/regime31/peer_fetch.json``. These rasters are used for
proxy scoring and the duplicate canary — never as candidate inputs or dots.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from download_competition_data import _download  # noqa: E402


def sha256_file(path: Path) -> str:
    d = hashlib.sha256()
    with path.open("rb") as h:
        for chunk in iter(lambda: h.read(1 << 20), b""):
            d.update(chunk)
    return d.hexdigest()


def main() -> int:
    forensics = json.loads((ROOT / "evidence/h33_forensics_20261025.json").read_text())
    rows = []
    for entry in forensics["requested_site_comparison"]:
        repo = entry["repo"]
        if repo == "GEMSDOE31":
            local = ROOT / entry["published_paths_matching_request"][0]
            rows.append({"repo": repo, "path": str(local.relative_to(ROOT)), "status": "local",
                         "sha256_match": sha256_file(local) == entry["sha256"]})
            print(repo, "local", rows[-1]["sha256_match"], flush=True)
            continue
        # forensics "file" = data/prior_audit/<REPO>/<published path>
        published = "/".join(Path(entry["file"]).parts[3:])
        dest = ROOT / "data/prior_audit" / repo / published
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not (dest.is_file() and sha256_file(dest) == entry["sha256"]):
            _download(f"buffedlizard55-lab/{repo}", entry["ref"], published, dest)
        ok = dest.is_file() and sha256_file(dest) == entry["sha256"]
        rows.append({"repo": repo, "ref": entry["ref"], "published_path": published,
                     "dest": str(dest.relative_to(ROOT)), "sha256": entry["sha256"],
                     "sha256_match": bool(ok), "bytes": dest.stat().st_size if dest.is_file() else 0,
                     "reported_value_class": entry["reported_value_class"],
                     "organizer_confirmed_score": None})
        print(repo, published, "hash_ok=", ok, flush=True)
        if not ok:
            raise SystemExit(f"hash mismatch fetching {repo}:{published}")
    out = ROOT / "evidence/regime31/peer_fetch.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"evidence_class": "COMPUTED (hash-verified fetch)",
                               "use": "learning/proxy/uniqueness only; never candidate input",
                               "files": rows}, indent=1) + "\n")
    print(f"wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
