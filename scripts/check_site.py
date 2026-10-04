#!/usr/bin/env python3
"""Static checks on the generated site: links, counts, placeholders, pictograms, claims.

The site is generated, so the failure modes worth testing are structural: a link to a file that was
never built, a page count that exceeded the site budget, a ``None`` that leaked into a table, a
download button that points at a missing artifact, or a pictogram in the navigation chrome.

Run after ``scripts/build_site.py``. Exits non-zero on any failure.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
MAX_PAGES = 20
ALLOWED_STATUS_PICTOGRAMS: set[str] = set()

FAILURES: list[str] = []
NOTES: list[str] = []


def fail(message: str) -> None:
    FAILURES.append(message)


def note(message: str) -> None:
    NOTES.append(message)


def local_links(html: str) -> list[str]:
    links = []
    for match in re.finditer(r'(?:href|src)="([^"]+)"', html):
        target = match.group(1)
        if target.startswith(("http://", "https://", "mailto:", "#", "data:")):
            continue
        links.append(target)
    return links


def main() -> None:
    pages = sorted(DOCS.rglob("*.html"))
    if len(pages) > MAX_PAGES:
        fail(f"{len(pages)} pages generated, budget is {MAX_PAGES}")
    else:
        note(f"{len(pages)} pages (budget {MAX_PAGES})")

    for page in pages:
        html = page.read_text()
        for link in local_links(html):
            path = (page.parent / urlparse(link).path).resolve()
            if not path.exists():
                fail(f"{page.relative_to(ROOT)}: broken local link {link}")
        for bad in ("None", "nan,", "{", "}"):
            if bad in ("{", "}"):
                continue
            if f">{bad}<" in html or f">{bad} " in html:
                fail(f"{page.relative_to(ROOT)}: placeholder '{bad}' rendered into the page")
        for character in html:
            if character in ALLOWED_STATUS_PICTOGRAMS:
                continue
            if unicodedata.category(character) == "So" and character not in "·×→≥≤—–":
                fail(f"{page.relative_to(ROOT)}: pictogram/symbol U+{ord(character):04X} ({character!r}) in markup")

    index = (DOCS / "index.html").read_text()
    if "Download submission TIFF" not in index:
        fail("index.html: the one-click download button is missing")
    for name in ("executive-summary.html", "feed.json"):
        if not (DOCS / name).exists():
            fail(f"{name} missing")

    register = (ROOT / "registry" / "submissions.json").read_text()
    if '"slot_approved": true' in register:
        fail("a submission is marked slot-approved without a promotion gate record")

    feed = (DOCS / "feed.json").read_text()
    if "no organizer receipt" not in feed:
        fail("feed.json does not disclose the absent organizer receipt")

    print(f"checked {len(pages)} pages and {len(local_links(''.join(p.read_text() for p in pages)))} local links")
    for item in NOTES:
        print(f"  note: {item}")
    if FAILURES:
        print(f"\n{len(FAILURES)} FAILURE(S):")
        for item in FAILURES:
            print(f"  - {item}")
        sys.exit(1)
    print("all site checks passed")


if __name__ == "__main__":
    main()
