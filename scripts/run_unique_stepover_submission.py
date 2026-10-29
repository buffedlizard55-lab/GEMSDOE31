#!/usr/bin/env python3
"""Retired CSDU synthetic prototype; intentionally cannot build submission bytes.

The original prototype generated an ellipse footprint and an all-zero synthetic
catalogue rather than using the pinned competition template and public labels.
Its archived TIFFs consequently fail validation against data/sample_submission.tif:
1,899 of 4,000 positive cells lie outside the real footprint, and the NaN twin
has 2,610,312 missing values inside it. The historical source is preserved in
Git history (pre-audit SHA-256 112fd0441b618916247eb4b5473f081616e6373df9cf85e9ce2450730dd5c293).
See evidence/review_9f242e65/run_card.json. Do not regenerate, repair, or submit
these synthetic bytes; any future experiment needs a separately assigned method.
"""

from __future__ import annotations


RETIRED_REASON = (
    "CSDU is an invalid synthetic-grid prototype: its saved TIFFs fail validation "
    "against the pinned competition template. No TIFF was created."
)


def main() -> int:
    raise SystemExit(RETIRED_REASON)


if __name__ == "__main__":
    raise SystemExit(main())
