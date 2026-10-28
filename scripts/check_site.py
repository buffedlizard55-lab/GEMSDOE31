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
    if "not approved for upload" not in index.lower():
        fail("index.html: the no-upload-approval warning is missing")
    if "Download submission TIFF" in index:
        fail("index.html: an unapproved legacy file is labeled as a submission TIFF")
    executive = (DOCS / "executive-summary.html").read_text()
    for page_name, text in (("index.html", index), ("executive-summary.html", executive)):
        if 'id="repository-review-2026-10-28"' not in text:
            fail(f"{page_name}: current three-pass repository review notice is missing")
        if text.count('id="focus-sites"') != 1 or 'id="nine-site-decision"' in text:
            fail(f"{page_name}: duplicate or missing nine-site summary section")
        for artifact in ("repo-review-2026-10-28.md", "repo-review-2026-10-28-run-card.json"):
            if artifact not in text:
                fail(f"{page_name}: current review deliverable link {artifact} is missing")
    research_page = (DOCS / "research.html").read_text()
    if 'id="desk-hypotheses-2026-10-28"' not in research_page or "Validation status: NOT RUN" not in research_page:
        fail("research.html: current desk-only hypothesis list or blocked-validation label is missing")
    sources_page = (DOCS / "sources.html").read_text()
    if ('id="public-source-health"' not in sources_page or 'id="feed-status"' not in sources_page
            or 'id="source-health"' not in sources_page or 'src="assets/feed.js"' not in sources_page):
        fail("sources.html: public GitHub metadata widget is missing or not wired")
    # Current owner protocol restores the literal both-stage registry rule.
    if "no file is cleared to submit" not in executive.lower():
        fail("executive-summary.html: explicit no-upload decision is missing")
    if "No human sign-off can override a failed gate" not in executive:
        fail("executive-summary.html: human override of hard STOP implied")
    for name, text in (("index", index), ("executive", executive)):
        for stale in ("SUBMIT THIS FILE", "OK TO DOWNLOAD AND SUBMIT", "OK TO SUBMIT"):
            if stale in text.replace("NOT OK TO SUBMIT", "DO NOT SUBMIT"):
                fail(f"{name}: stale selector approval: {stale}")
        if "protocol-review-run-card.json" not in text:
            fail(f"{name}: current protocol receipt missing")
    for page_name, html_text in (("index.html", index), ("executive-summary.html", executive)):
        if "gemsdoe31-h31aa-slfs-flexure-37654-20261027-fdb34746" not in html_text:
            fail(f"{page_name}: H31-AA SLFS candidate name missing")
        if "d272d5babb9523a70f77e76ad6843830d67a9eabaaa60f8c3f46ca57bde9a1ef" not in html_text:
            fail(f"{page_name}: H31-AA SLFS primary -zeros.tif SHA-256 missing")
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
    # Current permissions/downloads must agree across every public entry point.
    try:
        release = json.loads((ROOT / "registry/release_status.json").read_text())
        public = json.loads((DOCS / "downloads/current-release-status.json").read_text())
        feed_data = json.loads(feed)
        source_health = json.loads((DOCS / "source-health.json").read_text())
        expected_sources = [{"repo": row["repo"], "pin": row["pin"]} for row in source_health["checks"]]
        if feed_data.get("public_sources") != expected_sources:
            fail("feed public-source targets differ from the dated metadata snapshot")
        if feed_data.get("source_health_snapshot", {}).get("file") != "source-health.json":
            fail("feed omits the source-health snapshot reference")
        if public != release or feed_data.get("current_release_status") != release:
            fail("current release status differs between register, public copy and feed")
        if feed_data["current_download"]["raster_sha256"] != release["raster_sha256"]:
            fail("feed current download differs from current release artifact")
        if release["ok_to_submit"] is not False or release["slot_approved"] is not False:
            fail("current STOP review cannot approve submission")
        if hashlib.sha256((ROOT / release["file"]).read_bytes()).hexdigest() != release["raster_sha256"]:
            fail("current release download changed since byte audit")
        for name, text in (("index", index), ("executive", executive)):
            if "current-release-status.json" not in text or Path(release["file"]).name not in text:
                fail(f"{name}: current release artifact/receipt missing")
    except (OSError, KeyError, TypeError, ValueError) as exc:
        fail(f"cannot verify canonical current release: {exc}")
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
