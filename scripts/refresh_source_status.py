#!/usr/bin/env python3
"""Refresh public GitHub HEAD metadata, never predictions, scores or weekly slots.

The scheduled Pages workflow publishes the dated snapshot without committing it
or changing the frozen scientific run. Failures remain explicitly unverified.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


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
    feed = json.loads((ROOT / "docs/feed.json").read_text())
    with ThreadPoolExecutor(max_workers=3) as pool:
        checks = list(pool.map(check, feed["public_sources"]))
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
