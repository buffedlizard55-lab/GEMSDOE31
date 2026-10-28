#!/usr/bin/env python3
"""Refresh public GitHub HEAD metadata, never predictions, scores or weekly slots.

This optional snapshot utility reads its target list from the public source-health
snapshot or the generated feed. It does not contact DrivenData or re-audit changed
repository contents. The Sources page also performs public metadata checks in the
visitor's browser and falls back to the dated snapshot.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPO_RE = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
SHA_RE = re.compile(r"[0-9a-f]{40}\Z")


def load_targets(root=ROOT):
    """Load the bounded public GitHub metadata targets, with a snapshot fallback."""
    root = Path(root)
    feed_path = root / "docs/feed.json"
    feed = json.loads(feed_path.read_text()) if feed_path.is_file() else {}
    targets = feed.get("public_sources")
    if not targets:
        health_path = root / "docs/source-health.json"
        if health_path.is_file():
            health = json.loads(health_path.read_text())
            targets = [{"repo": row.get("repo"), "pin": row.get("pin")}
                       for row in health.get("checks", [])]
    if not isinstance(targets, list) or not targets:
        raise ValueError("no public_sources targets in feed.json or source-health.json")

    clean = []
    seen = set()
    for source in targets:
        if not isinstance(source, dict):
            raise ValueError("public source target must be an object")
        repo, pin = source.get("repo"), source.get("pin")
        if not isinstance(repo, str) or not REPO_RE.fullmatch(repo):
            raise ValueError(f"invalid public GitHub repository target: {repo!r}")
        if not isinstance(pin, str) or not SHA_RE.fullmatch(pin):
            raise ValueError(f"invalid audited commit pin for {repo}")
        if repo in seen:
            raise ValueError(f"duplicate public GitHub repository target: {repo}")
        seen.add(repo)
        clean.append({"repo": repo, "pin": pin})
    return clean


def check(source):
    repo = source["repo"]
    try:
        result = subprocess.run(["gh", "api", f"repos/{repo}/commits?per_page=1"],
                                capture_output=True, text=True, timeout=45, check=False)
        if result.returncode:
            raise RuntimeError("GitHub API query failed; metadata not verified")
        head = json.loads(result.stdout)[0]
        return {**source, "ok": True, "current": head["sha"], "date": head["commit"]["committer"]["date"]}
    except (OSError, RuntimeError, subprocess.TimeoutExpired, KeyError, IndexError, ValueError) as error:
        return {**source, "ok": False, "error": str(error)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="docs/source-health.json")
    args = ap.parse_args()
    targets = load_targets(ROOT)
    with ThreadPoolExecutor(max_workers=3) as pool:
        checks = list(pool.map(check, targets))
    good = sum(r["ok"] for r in checks)
    report = {"schema_version": 1, "evidence_class": "PUBLIC-GITHUB-METADATA",
              "checked_utc": datetime.now(timezone.utc).isoformat(), "verified_count": good,
              "total": len(checks), "checks": checks,
              "limitation": "Public repository HEAD metadata only; changed sources are not scientifically re-audited. No leaderboard, receipt, weekly-cap or upload access."}
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1, allow_nan=False) + "\n")
    print(f"{good}/{len(checks)} public GitHub metadata queries verified; no scientific or submission state changed")


if __name__ == "__main__":
    main()
