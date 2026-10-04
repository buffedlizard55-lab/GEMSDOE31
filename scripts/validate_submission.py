#!/usr/bin/env python3
"""Validate a GEMS submission GeoTIFF against the organizer's sample-submission grid."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gemsdoe31.submission import validate_submission  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("submission", type=Path, help="single-band prediction .tif")
    parser.add_argument("--template", type=Path, required=True, help="official sample_submission.tif or owner-mirror copy")
    parser.add_argument("--allow-synthetic-template", action="store_true", help="skip fixed production-grid constants (tests only)")
    parser.add_argument("--convention", choices=("nan-outside", "all-finite"), default="nan-outside",
                        help="outside-footprint rule to enforce (default: the official nan-outside rule)")
    parser.add_argument("--json-out", type=Path, default=None, help="optional path for a machine-readable receipt")
    args = parser.parse_args()
    result = validate_submission(
        args.submission,
        args.template,
        require_competition_grid=not args.allow_synthetic_template,
        convention=args.convention,
    )
    text = json.dumps(result, indent=2, sort_keys=True, allow_nan=False)
    print(text)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n")
    return 0 if result["ok_to_upload_format_only"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
