#!/usr/bin/env python3
"""Reproduce the negative CSDU exact-footprint audit against the pinned sample.

A successful process exit means the audit result was reproduced, not that the CSDU
GeoTIFF is valid or approved for submission.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gemsdoe31.submission import validate_submission  # noqa: E402
AUDIT = Path("evidence/csdu_owner_mirror_validation_20261026.json")
TEMPLATE = Path("data/sample_submission.tif")
FILES = {
    "all_finite": ("docs/downloads/gemsdoe31-csdu-stepover-8cf9dc27-allfinite.tif", "all-finite"),
    "nan_outside": ("docs/downloads/gemsdoe31-csdu-stepover-8cf9dc27-nan.tif", "nan-outside"),
}


def verify(root: Path = ROOT) -> dict:
    root = Path(root)
    receipt = json.loads((root / AUDIT).read_text())
    template_path = root / TEMPLATE
    template_sha = hashlib.sha256(template_path.read_bytes()).hexdigest()
    if template_sha != receipt["template_sha256"]:
        raise ValueError("Pinned template bytes changed from the CSDU audit receipt")

    results = {}
    for key, (relative, convention) in FILES.items():
        path = root / relative
        actual = validate_submission(path, template_path, convention=convention)
        expected = receipt["variants"][key]
        if actual["sha256"] != expected["sha256"]:
            raise ValueError(f"CSDU {key} TIFF bytes changed")
        if actual["ok_to_upload_format_only"]:
            raise ValueError(f"CSDU {key} unexpectedly passes exact-footprint validation")
        if actual["hard_failures"] != expected["hard_failures"]:
            raise ValueError(f"CSDU {key} hard-failure list differs from audit receipt")
        if actual["grid"]["template_footprint_pixels"] != expected["template_footprint_pixels"]:
            raise ValueError(f"CSDU {key} was checked against a different footprint")
        results[key] = {
            "sha256": actual["sha256"],
            "ok_to_upload_format_only": False,
            "hard_failures": actual["hard_failures"],
            "template_footprint_pixels": actual["grid"]["template_footprint_pixels"],
            "positive_pixels_inside": actual["grid"]["positive_pixels_inside"],
        }

    return {
        "audit_reproduced": True,
        "candidate_format_valid_for_pinned_sample": False,
        "holdout_tested": False,
        "registry_uniqueness_tested": False,
        "slot_approved": False,
        "verdict": "negative; forensic audit only; DO NOT SUBMIT",
        "variants": results,
    }


def main() -> None:
    print(json.dumps(verify(), indent=2))


if __name__ == "__main__":
    main()
