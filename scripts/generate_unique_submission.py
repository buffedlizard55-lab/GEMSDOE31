#!/usr/bin/env python3
"""Retired H-STEO prototype; intentionally cannot create or write another TIFF.

The saved 2026-10-29 artifact is format-valid but fails the required 3-pixel
registered-raster overlap gate. Its original generator is preserved in Git
history (pre-audit SHA-256 bafbd6469e25724f53b021d3d93e49ca233aec279c3f3557d52e5040b4ee4ad0)
and its measured disposition is in evidence/review_9f242e65/run_card.json.
Do not rerun it, change dot density, or reinterpret zero exact-cell intersections
as a uniqueness pass. Any future lane needs an explicit method assignment and a
new preregistration; this archived prototype is not a candidate pipeline.
"""

from __future__ import annotations

RETIRED_REASON = (
    "H-STEO is retired: the existing 9,140-dot file has 99.945% of dots within 3 px "
    "of a hash-pinned registered raster. No new TIFF after this literal STOP."
)


def main() -> int:
    raise SystemExit(RETIRED_REASON)


if __name__ == "__main__":
    raise SystemExit(main())
