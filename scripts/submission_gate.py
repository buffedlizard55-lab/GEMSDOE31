#!/usr/bin/env python3
"""Legacy diagnostic receipt only; cannot approve uploads under the current literal protocol.

    python scripts/submission_gate.py docs/downloads/<name>-allfinite.tif --convention all-finite \
        --name <name> --note "<=140 characters" --json-out docs/downloads/<name>-gate-allfinite.json

Exit code: 3 FORMAT_VALID_NOT_PROMOTED, 2 BLOCKED. No READY_TO_SUBMIT path.
Current permission is registry/release_status.json, not a legacy diagnostic pass.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gemsdoe31.gate import run_gate  # noqa: E402


def used_names(registry_path: Path) -> set[str]:
    registry = json.loads(registry_path.read_text())["rasters"]
    names: set[str] = set()
    for entry in registry:
        for variant in [entry["path"]] + [v.split(":", 1)[1] for v in entry["variants"]]:
            names.add(Path(variant).stem)
    submissions = ROOT / "registry" / "submissions.json"
    if submissions.is_file():
        text = submissions.read_text()
        names |= {n for n in json.loads(text).get("reserved_names", [])}
    return names


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tif", type=Path)
    parser.add_argument("--convention", choices=("nan-outside", "all-finite"), required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--note", required=True)
    parser.add_argument("--template", type=Path, default=ROOT / "data/sample_submission.tif")
    parser.add_argument("--labels", type=Path, default=ROOT / "data/labels.tif")
    parser.add_argument("--registry", type=Path, default=ROOT / "registry/raster_registry.json")
    parser.add_argument("--cache-dir", type=Path, default=ROOT / "data/registry_rasters")
    parser.add_argument("--evidence", type=Path, default=ROOT / "evidence/lane_e3.json")
    parser.add_argument("--procedure", type=Path, default=ROOT / "scripts/lane_candidate.py")
    parser.add_argument("--scores", type=Path, default=ROOT / "registry/user_reported_scores.json")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    procedure_sha = hashlib.sha256(args.procedure.read_bytes()).hexdigest() if args.procedure.is_file() else None
    receipt = run_gate(tif=args.tif, template=args.template, labels=args.labels, registry_path=args.registry,
                       cache_dir=args.cache_dir, convention=args.convention, name=args.name, note=args.note,
                       evidence_path=args.evidence, procedure_sha256=procedure_sha, used_names=used_names(args.registry), scores_path=args.scores)
    text = json.dumps(receipt, indent=1, default=float)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n")
    print(f"VERDICT {receipt['verdict']}  submit_recommended={receipt['submit_recommended']}")
    for key, value in receipt["gates"].items():
        print(f"  {'PASS' if value['pass'] else 'FAIL':4s} {key}: {value['detail']}")
    proj = receipt["neighbour_projection"]
    print("  neighbour projection (NOT a score):", proj.get("mean_user_reported_live_score_of_neighbours", proj.get("reason")))
    return {"FORMAT_VALID_NOT_PROMOTED": 3, "BLOCKED": 2}[receipt["verdict"]]


if __name__ == "__main__":
    raise SystemExit(main())
