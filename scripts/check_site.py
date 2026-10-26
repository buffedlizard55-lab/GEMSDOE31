#!/usr/bin/env python3
"""Static checks on the generated site: links, counts, placeholders, pictograms, claims.

The site is generated, so the failure modes worth testing are structural: a link to a file that was
never built, a page count that exceeded the site budget, a ``None`` that leaked into a table, a
download button that points at a missing artifact, or a pictogram in the navigation chrome.

Run after ``scripts/build_site.py``. Exits non-zero on any failure.
"""

from __future__ import annotations

from collections import defaultdict
from html.parser import HTMLParser
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
MAX_PAGES = 21  # +1 for Experiment 13 (RBU31/RBU31-B), added 2026-10-25
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


class _IdCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: dict[str, int] = defaultdict(int)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key == "id" and value:
                self.ids[value] += 1


def main() -> None:
    pages = sorted(DOCS.rglob("*.html"))
    if len(pages) > MAX_PAGES:
        fail(f"{len(pages)} pages generated, budget is {MAX_PAGES}")
    else:
        note(f"{len(pages)} pages (budget {MAX_PAGES})")

    for page in pages:
        html = page.read_text()
        parser = _IdCollector()
        parser.feed(html)
        for element_id, count in parser.ids.items():
            if count > 1:
                fail(f"{page.relative_to(ROOT)}: duplicate HTML id {element_id!r} appears {count} times")
        if "if dti_sgmc is not None" in html or "if dti_gap is not None" in html:
            fail(f"{page.relative_to(ROOT)}: unrendered Python conditional leaked into HTML")
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
    active_path = ROOT / "registry/current_run.json"
    active_run = active_path.exists()
    required_button = "Download MAGREST research TIFF — DO NOT SUBMIT" if active_run else "Download reference TIFF"
    if required_button not in index:
        fail(f"index.html: the {required_button!r} button is missing")
    if active_run:
        card = json.loads(active_path.read_text())
        readiness = json.loads((DOCS / "downloads/readiness.json").read_text())
        actual = hashlib.sha256((ROOT / card["file"]).read_bytes()).hexdigest()
        if actual != card["raster_sha256"] or actual != readiness["sha256"]:
            fail("readiness/current run is stale relative to the served TIFF")
        if readiness["ok_to_submit"] or card["ok_to_submit"] or card["slot_approved"]:
            fail("unsupported upload approval for this negative MAGREST run")
        if ("RESEARCH DOWNLOAD ONLY" not in index or "DO NOT SUBMIT" not in index
                or "downloads/" + Path(card["file"]).name not in index
                or card["submission_name"] not in index):
            fail("index does not prominently expose the active artifact with DO NOT SUBMIT")
        if "newest unique candidate: RBU31" in index or "Download the RBU31 submission .tif" in index:
            fail("index promotes stale RBU31 evidence over registry/current_run.json")
        if "GEMSDOE48" not in index or "99.8713%" not in index:
            fail("index does not distinguish the continuous full-support witness from the 99.8713% lattice coverage")
    if "not approved for upload" not in index.lower() and "research download only" not in index.lower():
        fail("index.html: the no-upload-approval warning is missing")
    if "Download submission TIFF" in index:
        fail("index.html: an unapproved legacy file is labeled as a submission TIFF")
    executive = (DOCS / "executive-summary.html").read_text()
    if "research download only" not in executive.lower() or "do not submit" not in executive.lower():
        fail("executive-summary.html: explicit research-only/no-upload warning is missing")
    if "No human or selector approval overrides a failed hard gate." not in executive:
        fail("executive-summary.html: failed hard-gate status is not explicit")
    if "newest candidate RBU31" in executive or "Download the RBU31 submission .tif" in executive:
        fail("executive-summary.html: stale RBU31 evidence is presented as the active run")
    old_lattice_claim = "100% of primary dots within 3 px of a registered spacing-5 lattice"
    if (old_lattice_claim in executive or "99.8713%" not in executive
            or "distinct full-support witness" not in executive or "GEMSDOE48" not in executive):
        fail("executive-summary.html: active registry witnesses are conflated or correction is missing")
    for page_name, html_text in (("index.html", index), ("executive-summary.html", executive)):
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
    for name in ("executive-summary.html", "feed.json"):
        if not (DOCS / name).exists():
            fail(f"{name} missing")

    for page_name in ("index.html", "executive-summary.html", "research.html"):
        html_text = (DOCS / page_name).read_text()
        for card_id, label in (("scgp-submod", "H31-E2"), ("hvdc-submod", "H31-HVDC"), ("h31m-submod", "H31-M")):
            if f'id="{card_id}"' in html_text:
                if "RESEARCH DOWNLOAD ONLY" not in html_text or "DO NOT SUBMIT · REGISTRY STOP" not in html_text:
                    fail(f"{page_name}: {label} research-only/registry STOP warning missing")
                if "SUBSET ONLY — NOT UNIQUENESS APPROVAL" not in html_text:
                    fail(f"{page_name}: {label} subset comparison incorrectly presented as broad uniqueness")
                if "Portal Format" in html_text or "explicit human selector sign-off" in html_text:
                    fail(f"{page_name}: {label} unsupported portal acceptance or human override wording")
                if label == "H31-M" and (
                    "candidate-specific overlap with r13-lattice-s5" not in html_text
                    or "distinct GEMSDOE48 full-support witness" not in html_text
                ):
                    fail(f"{page_name}: H31-M stop metadata conflates the lattice and continuous witness")

    research_page = (DOCS / "research.html").read_text()
    for hypothesis in (
        "Acquisition-seam-aware magnetic lineament persistence",
        "Multiscale gravity–magnetic edge-transfer coherence",
        "Piedmont drainage-deflection asymmetry",
        "Radiometric channel edge displacement",
    ):
        if hypothesis not in research_page:
            fail(f"research.html: desk-only hypothesis missing: {hypothesis}")
    if "Absolute ΔDTI: unknown" not in research_page or "not data-ready" not in research_page:
        fail("research.html: hypothesis uncertainty/data-access limits are missing")
    if "Within its interior, any new method’s dots pass within 3 pixels" in research_page:
        fail("research.html: universal witness is incorrectly attributed to the r13 lattice")

    register = (ROOT / "registry" / "submissions.json").read_text()
    if '"slot_approved": true' in register:
        fail("a submission is marked slot-approved without a promotion gate record")
    if "spacing-5 lattice covers 100% of interior within 3px for any candidate" in register:
        fail("submission register repeats the incorrect universal-coverage attribution to the r13 lattice")
    correction_path = ROOT / "evidence/registry_overlap_claim_correction_2026-10-26.json"
    if not correction_path.is_file():
        fail("registered correction for the distinct r13 lattice and GEMSDOE48 witnesses is missing")
    else:
        correction = json.loads(correction_path.read_text())
        if correction.get("corrected_facts", [{}])[0].get("three_pixel_halo_footprint_coverage") != 0.9987132726822701:
            fail("registry overlap correction no longer matches the recorded lattice coverage")
        if correction.get("corrected_facts", [{}, {}])[1].get("positive_support_pixels") != 5167373:
            fail("registry overlap correction no longer identifies the full-support witness")
    try:
        registry_data = json.loads(register)
        active_record = next((r for r in registry_data.get("files", []) if r.get("id") == "magrest-current-negative"), None)
        if active_record is None:
            fail("submission register has no active MAGREST record")
        else:
            reason = active_record.get("why_not_slot_approved", "")
            if ("100% of primary dots within 3 px of a registered spacing-5 lattice" in reason
                    or "99.8713%" not in reason or "GEMSDOE48" not in reason):
                fail("submission register: active MAGREST STOP misattributes the lattice/full-support witnesses")
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
    if ("100% of primary dots within 3 px of a registered spacing-5 lattice" in feed
            or "99.8713%" not in feed or "GEMSDOE48" not in feed):
        fail("feed.json: corrected lattice-versus-continuous support attribution is missing")

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
