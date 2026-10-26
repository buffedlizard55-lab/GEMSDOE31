#!/usr/bin/env python3
"""Static checks on the generated site: links, counts, placeholders, pictograms, claims.

The site is generated, so the failure modes worth testing are structural: a link to a file that was
never built, a page count that exceeded the site budget, a ``None`` that leaked into a table, a
download button that points at a missing artifact, or a pictogram in the navigation chrome.

Run after ``scripts/build_site.py``. Exits non-zero on any failure.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
MAX_PAGES = 22  # +1 for Experiment 13 (RBU31/RBU31-B), +1 for XFCOH31 decision page, added 2026-10-26
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
    active_run = (ROOT / "registry/current_run.json").exists()
    required_button = "Download new research TIFF" if active_run else "Download reference TIFF"
    if required_button not in index:
        fail(f"index.html: the {required_button!r} button is missing")
    if active_run:
        card = json.loads((ROOT / "registry/current_run.json").read_text())
        readiness = json.loads((DOCS / "downloads/readiness.json").read_text())
        actual = hashlib.sha256((ROOT / card["file"]).read_bytes()).hexdigest()
        if actual != card["raster_sha256"] or actual != readiness["sha256"]:
            fail("readiness/current run is stale relative to the served TIFF")
        if readiness["ok_to_submit"] or card["ok_to_submit"]:
            fail("unsupported upload approval for this negative MAGREST run")
        if "DO NOT SUBMIT" not in index or "downloads/" + Path(card["file"]).name not in index:
            fail("index does not prominently expose the new artifact with DO NOT SUBMIT")
        if card["submission_name"] not in index:
            fail("index does not name the active registered run in its leading content")
        archived_h31s = "gemsdoe31-h31s-udap-sslic-37654-20261026-9355f21d9f"
        if index.find(card["submission_name"]) > index.find(archived_h31s):
            fail("index features a historical H31-S artifact before the active registered run")
    if "not approved for upload" not in index.lower():
        fail("index.html: the no-upload-approval warning is missing")
    if "Download submission TIFF" in index:
        fail("index.html: an unapproved legacy file is labeled as a submission TIFF")
    executive = (DOCS / "executive-summary.html").read_text()
    if "do not submit" not in executive.lower() or "ok_to_submit = false" not in executive:
        fail("executive-summary.html: explicit current-run no-upload status is missing")
    if active_run:
        card = json.loads((ROOT / "registry/current_run.json").read_text())
        archived_h31s = "gemsdoe31-h31s-udap-sslic-37654-20261026-9355f21d9f"
        if card["submission_name"] not in executive or executive.find(card["submission_name"]) > executive.find(archived_h31s):
            fail("executive-summary.html: the active run must be named before historical H31-S content")
    if "Human sign-off cannot override a failed gate" not in executive:
        fail("executive-summary.html: human selector is incorrectly implied to override a hard stop")
    research = (DOCS / "research.html").read_text()
    if ("0.05882" not in research or "0.05556" not in research
            or "0.07693" in research or "≈ 0.0770" in research):
        fail("research.html: the H33 marginal break-even explanation is stale or algebraically incorrect")
    data_status_path = DOCS / "data" / "submissions.json"
    if active_run:
        if not data_status_path.is_file():
            fail("docs/data/submissions.json is missing")
        else:
            data_status = json.loads(data_status_path.read_text())
            card = json.loads((ROOT / "registry/current_run.json").read_text())
            record = data_status.get("current_run", {})
            if (record.get("name") != card["submission_name"]
                    or record.get("sha256") != card["raster_sha256"]
                    or record.get("ok_to_submit") is not False
                    or data_status.get("current_recommended", {}).get("name") is not None):
                fail("docs/data/submissions.json disagrees with the active run card or no-submit decision")
    for page_name, html_text in (("index.html", index), ("executive-summary.html", executive)):
        if "gemsdoe31-tgtd-submod-37654-20261025-ab35d4e8" not in html_text:
            fail(f"{page_name}: H31-J TGTD-Submod candidate name missing")
        if "04e886cd8f7759e05d5fabb5d7222aaed0d16fda59fdf81e5934c5508eaf3fa3" not in html_text:
            fail(f"{page_name}: H31-J TGTD-Submod primary -zeros.tif SHA-256 missing")
        if "44142a9671e4beaa4872a8d5fc11e061f8050ac3e48a4573b415329227536657" not in html_text:
            fail(f"{page_name}: H31-J TGTD-Submod primary -zeros.zip SHA-256 missing")
        if "GEMSDOE31 H31-J TGTD+GDR1391 geotherm+PTCF 4-quad OOF 300m submod 37654d b2px (ab35d4e8)" not in html_text:
            fail(f"{page_name}: H31-J TGTD-Submod portal note missing")
        if html_text.find("gemsdoe31-tgtd-submod-37654-20261025-ab35d4e8") > html_text.find("gemsdoe31-scgp-submod-37654-20261025-fa735287"):
            fail(f"{page_name}: H31-J TGTD-Submod must appear at the top above prior candidates")
        if "gemsdoe31-scgp-submod-37654-20261025-fa735287" not in html_text:
            fail(f"{page_name}: H31-E2 SCGP-Submod candidate name missing")
        if "d5ae3715c4ee727195ec6c023d5c852497538c3e60ff559997984f397b4d2fa8" not in html_text:
            fail(f"{page_name}: H31-E2 SCGP-Submod primary SHA-256 missing")
        if "gemsdoe31-h31-hvdc-submod300-37654-20261025-43714168" not in html_text:
            fail(f"{page_name}: H31-HVDC-Submod300 candidate name missing")
        if "2851825a2a33b3a7539aff02131d7a1d59becb5c2e89d1b9a0212652e1e8b1b2" not in html_text:
            fail(f"{page_name}: H31-HVDC-Submod300 primary SHA-256 missing")
        if "gemsdoe31-h31m-bstep-xmod-submod-20261025-37654" not in html_text:
            fail(f"{page_name}: H31-M BStep-XMod-Submod candidate name missing")
        if "ad9784c07456d9bbd897c5b47de56c96659bc619b0b23c5238c3d17846a3f3a6" not in html_text:
            fail(f"{page_name}: H31-M BStep-XMod-Submod primary SHA-256 missing")
        if "gemsdoe31-h31t-transtension-dinkelbach-20261025-b37654" not in html_text:
            fail(f"{page_name}: H31-T Transtension-Dinkelbach candidate name missing")
        if "83fbc267a754d5d58c950baddc92891b53a4cad2c2f90a114f1c2177b4567298" not in html_text:
            fail(f"{page_name}: H31-T Transtension-Dinkelbach primary SHA-256 missing")
    for name in ("executive-summary.html", "feed.json"):
        if not (DOCS / name).exists():
            fail(f"{name} missing")

    for page_name in ("index.html", "executive-summary.html", "research.html"):
        html_text = (DOCS / page_name).read_text()
        for card_id, label in (
            ("scgp-submod", "H31-E2"),
            ("hvdc-submod", "H31-HVDC"),
            ("h31m-submod", "H31-M"),
            ("h31t-dinkelbach", "H31-T"),
        ):
            if f'id="{card_id}"' in html_text:
                if "RESEARCH DOWNLOAD ONLY" not in html_text or "DO NOT SUBMIT · REGISTRY STOP" not in html_text:
                    fail(f"{page_name}: {label} research-only/registry STOP warning missing")
                if "SUBSET ONLY — NOT UNIQUENESS APPROVAL" not in html_text:
                    fail(f"{page_name}: {label} subset comparison incorrectly presented as broad uniqueness")
                if "Portal Format" in html_text or "explicit human selector sign-off" in html_text:
                    fail(f"{page_name}: {label} unsupported portal acceptance or human override wording")

    register = (ROOT / "registry" / "submissions.json").read_text()
    if '"slot_approved": true' in register:
        fail("a submission is marked slot-approved without a promotion gate record")
    try:
        registry_data = json.loads(register)
        for record in registry_data.get("files", []):
            if not record.get("zip"):
                continue
            archive = ROOT / record["zip"]
            if not archive.is_file():
                fail(f"registered submission ZIP is missing: {record['zip']}")
                continue
            digest = record.get("sha256_zip", "")
            if len(digest) != 64 or hashlib.sha256(archive.read_bytes()).hexdigest() != digest:
                fail(f"registered submission ZIP digest is missing, malformed, or stale: {record['zip']}")
            if record.get("bytes_zip") != archive.stat().st_size:
                fail(f"registered submission ZIP byte count is stale: {record['zip']}")
    except (KeyError, TypeError, ValueError) as exc:
        fail(f"cannot verify submission ZIP metadata: {exc}")

    feed = (DOCS / "feed.json").read_text()
    if "no organizer receipt" not in feed:
        fail("feed.json does not disclose the absent organizer receipt")
    if active_run:
        feed_data = json.loads(feed)
        current_download = feed_data.get("current_download", {})
        if (current_download.get("name") != card["submission_name"]
                or current_download.get("sha256") != card["raster_sha256"]
                or current_download.get("ok_to_submit") is not False
                or current_download.get("slot_approved") is not False):
            fail("feed.json disagrees with registry/current_run.json or the no-submit decision")
        scope_note = json.loads((ROOT / "registry/focus_unique_2026.json").read_text()).get("scope_note", "")
        if ("not an exhaustive global uniqueness audit" not in scope_note
                or not any(phrase in scope_note for phrase in (
                    "not approved to submit", "no artifact in this file is approved to submit"))):
            fail("focus_unique_2026.json does not disclose its pairwise-only scope and submission block")

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
