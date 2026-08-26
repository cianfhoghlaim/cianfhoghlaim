"""
Smoke test for the ncca-leaving-cert-syllabi-corpus change.

Verifies:
1. The curriculumonline_syllabi DLT source emits the expected rows for (mathematics, en)
2. The discovered PDF URL matches the one in url-inventory.md
3. The PDF can be downloaded and written to /tmp

This test uses a stub for the dlt_sources package to bypass the pre-existing
import-time dependencies in the `ie/education/__init__.py` re-export shim.

Run:  uv run python -m scripts.smoke_test_lc_syllabus
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
import types
from pathlib import Path


# ============================================================================
# Stub the dlt_sources package before any cianfhoghlaim imports trigger it
# ============================================================================
def _stub_dlt_sources() -> None:
    """Install a stub `dlt_sources.ie.education` namespace so the `__init__.py`
    re-export shim in our target package can complete its top-level imports.
    """
    stub = types.ModuleType("dlt_sources")
    stub_ie = types.ModuleType("dlt_sources.ie")
    stub_ie_edu = types.ModuleType("dlt_sources.ie.education")

    # Provide all the names that `__init__.py` imports
    for name in [
        "ALL_JC_SUBJECTS",
        "ALL_LC_SUBJECTS",
        "ALL_LCA_SUBJECTS",
        "junior_cycle_exams_source",
        "leaving_certificate_source",
        "mathematics_exams_source",
        "science_subjects_exams_source",
        "agentic_discovery_source",
        "deep_research_source",
        "exam_pdf_download_source",
        "examinations_source",
        "oide_source",
        "oide_all_subjects_source",
        "oide_gaeilge_source",
        "oide_subject_source",
        "pdf_download_source",
        "sec_examinations_browser_source",
    ]:
        setattr(stub_ie_edu, name, (lambda *a, **kw: None) if name.endswith("source") else [])

    sys.modules["dlt_sources"] = stub
    sys.modules["dlt_sources.ie"] = stub_ie
    sys.modules["dlt_sources.ie.education"] = stub_ie_edu


_stub_dlt_sources()


# ============================================================================
# Load the new module WITHOUT going through the package __init__.py
# (bypasses the dlt_sources import chain)
# ============================================================================
_MODULE_PATH = (
    Path(__file__).parent.parent
    / "cianfhoghlaim/pipelines/ingest/ie/education/curriculumonline_syllabi.py"
)
spec = importlib.util.spec_from_file_location("curriculumonline_syllabi_smoke", _MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
# Register in sys.modules so dataclass can find __dataclass_fields__
sys.modules["curriculumonline_syllabi_smoke"] = mod
spec.loader.exec_module(mod)

SENIOR_CYCLE_SYLLABI_SUBJECTS = mod.SENIOR_CYCLE_SYLLABI_SUBJECTS
LANGUAGE_URL_PREFIX = mod.LANGUAGE_URL_PREFIX
_scrape_subject_page = mod._scrape_subject_page
_extract_pdf_links_from_page = mod._extract_pdf_links_from_page
_filename_from_url = mod._filename_from_url
_classify_document_type = mod._classify_document_type


# ============================================================================
# Test definitions
# ============================================================================
EXPECTED_URLS: dict[tuple[str, str], str] = {
    ("mathematics", "en"): (
        "https://www.curriculumonline.ie/getmedia/f6f2e822-2b0c-461e-bcd4-dfcde6decc0c/"
        "SCSEC25_Maths_syllabus_examination-2015_English.pdf"
    ),
}


def _check_discovery() -> bool:
    """Phase 1 smoke: the DLT source can discover the mathematics EN PDF."""
    print("=== Phase 1: DLT source discovery ===")
    print(f"Subjects configured: {len(SENIOR_CYCLE_SYLLABI_SUBJECTS)}")
    print(f"Languages: {list(LANGUAGE_URL_PREFIX.keys())}")

    pages = _scrape_subject_page("mathematics", "en", use_local_scrapes=False)
    if not pages:
        print("FAIL: no pages scraped for mathematics/en (network or Cloudflare issue)")
        return False
    print(f"Pages scraped: {len(pages)}")

    discovered: list = []
    for page in pages:
        discovered.extend(_extract_pdf_links_from_page(page, "mathematics", "en"))
    print(f"PDFs discovered: {len(discovered)}")
    for d in discovered:
        print(f"  - {d.filename}  ({d.document_type})  url={d.url[:80]}...")

    expected_url = EXPECTED_URLS[("mathematics", "en")]
    matched = [d for d in discovered if d.url == expected_url]
    if not matched:
        print(f"FAIL: expected URL not found: {expected_url}")
        return False
    print("PASS: expected URL is in the discovered set")
    return True


def _check_download() -> bool:
    """Phase 2 smoke: the PDF can be downloaded and saved to /tmp."""
    print("\n=== Phase 2: PDF download ===")
    expected_url = EXPECTED_URLS[("mathematics", "en")]
    target = Path("/tmp/lc_syllabus_smoke_test.pdf")

    import requests

    resp = requests.get(
        expected_url,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        },
    )
    resp.raise_for_status()
    pdf_bytes = resp.content
    target.write_bytes(pdf_bytes)
    sha = hashlib.sha256(pdf_bytes).hexdigest()
    print(f"Downloaded {len(pdf_bytes)} bytes -> {target}")
    print(f"SHA-256: {sha}")

    if not pdf_bytes.startswith(b"%PDF-"):
        print(f"FAIL: file does not start with %PDF- magic; first bytes = {pdf_bytes[:8]!r}")
        return False
    print("PASS: file is a valid PDF (starts with %PDF-)")
    return True


def main() -> int:
    if not _check_discovery():
        return 1
    if not _check_download():
        return 1
    print("\n=== ALL SMOKE TESTS PASSED ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
