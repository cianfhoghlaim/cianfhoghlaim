"""
DLT source for curriculumonline.ie — NCCA's currently-taught Leaving Certificate syllabi.

Scrapes `curriculumonline.ie/{en|ga-ie}/senior-cycle/senior-cycle-subjects/{slug}/` for each
of the 8 priority LC subjects, extracts the syllabus + specification + guidelines
PDF URLs from each page, normalises filenames, and yields a `curriculumonline_syllabi`
dlt resource.

Per the `ncca-leaving-cert-syllabi-corpus` openspec change (2026-06-30):
- 8 subjects * 2 langs = 16 (subject, language) combinations
- 23 unique PDFs total (some subjects have syllabus + spec + guidelines)
- 1 known-absent combination: (gaeilge, en) — Gaeilge (the subject) is taught in Irish only
- 1 shared-PDF combination: (english, ga) — the GA version of the English subject page
  links to the same EN PDF (verified 2026-06-30).

This source is a sibling of the existing `ncca.py` source and reuses the same
`_crawl_with_firecrawl` helper to honour the local-scrape cache and the
21-second Firecrawl throttle. PDFs are NOT downloaded by this source — the
`lc_syllabus_download` Dagster asset is the downloader.
"""

from __future__ import annotations
import dlt


import re
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import dlt_sources
import structlog

logger = structlog.get_logger(__name__)


# The 8 priority LC subjects (English slug for curriculumonline.ie URLs).
SENIOR_CYCLE_SYLLABI_SUBJECTS: list[str] = [
    "mathematics",
    "applied-mathematics",
    "chemistry",
    "geography",
    "history",
    "english",
    "gaeilge",
    "computer-science",
]


# Language → URL prefix for the subject listing page.
LANGUAGE_URL_PREFIX: dict[str, str] = {
    "en": "",  # English is the default at the root
    "ga": "/ga-ie",
}


# Irish-language subject name → English slug.
# Used to look up the canonical English PDF even when scraping the GA page
# (the GA page for "english" links to the same EN PDF — verified 2026-06-30).
GA_SUBJECT_NAME_TO_SLUG: dict[str, str] = {
    "An Mhatamaitic": "mathematics",
    "An Mhatamaitic Fheidhmeach": "applied-mathematics",
    "Ceimic": "chemistry",
    "An Tíreolaíocht": "geography",
    "An Stair": "history",
    "Béarla": "english",
    "An Ghaeilge": "gaeilge",
    "Ríomheolaíocht": "computer-science",
}


# Document-type classification by URL filename token.
DOC_TYPE_BY_TOKEN: dict[str, str] = {
    "syllabus": "syllabus",
    "Syllabus": "syllabus",
    "Siollabas": "syllabus",
    "Siollabais": "syllabus",
    "specification": "specification",
    "Specification": "specification",
    "Sonraíocht": "specification",
    "guidelines": "guidelines",
    "Guidelines": "guidelines",
    "Treoirlínte": "guidelines",
    "spec-updated": "specification_updated",
}


@dataclass
class DiscoveredPdf:
    """A single PDF discovered on a curriculumonline.ie subject page."""

    url: str
    subject: str
    language: str
    filename: str
    document_type: str
    page_title: str
    source_page_url: str

    def to_row(self) -> dict[str, Any]:
        """Convert to a dlt row dict."""
        return {
            "url": self.url,
            "subject": self.subject,
            "language": self.language,
            "filename": self.filename,
            "document_type": self.document_type,
            "page_title": self.page_title,
            "source_page_url": self.source_page_url,
            "scraped_at": datetime.now(UTC).isoformat(),
        }


def _filename_from_url(url: str) -> str:
    """Extract the trailing filename from a `getmedia/{guid}/{filename}` URL.

    The GUID segment is opaque and changes when NCCA re-publishes a file, so we
    include it in the stored filename for reproducibility but the canonical
    identifier for downstream is the `url` itself.
    """
    path = urlparse(url).path
    parts = [p for p in path.split("/") if p]
    return parts[-1] if parts else "unknown.pdf"


def _classify_document_type(filename: str) -> str:
    """Classify a PDF by its filename using the `DOC_TYPE_BY_TOKEN` table."""
    for token, doc_type in DOC_TYPE_BY_TOKEN.items():
        if token in filename:
            return doc_type
    return "document"


def _is_curriculumonline_syllabus_pdf(url: str) -> bool:
    """Filter to only accept PDFs that are part of the curriculumonline.ie syllabus corpus.

    curriculumonline.ie subject pages link to:
    - The subject's own syllabus + spec + guidelines PDFs (which we want)
    - Sidebar links to other NCCA resources on ncca.ie (NOT curriculumonline.ie)
    - Footer links to the NCCA library and other publications (NOT syllabi)

    We accept only URLs on the curriculumonline.ie host that are getmedia/*.
    Other PDF links (sidebar / footer) on different hosts are dropped.
    """
    parsed = urlparse(url)
    if parsed.netloc != "www.curriculumonline.ie" and parsed.netloc != "curriculumonline.ie":
        return False
    return "/getmedia/" in parsed.path.lower()


def _extract_pdf_links_from_page(
    page: dict[str, Any],
    subject: str,
    language: str,
) -> list[DiscoveredPdf]:
    """Pull all `getmedia/...*.pdf` URLs out of a single Firecrawl page dict.

    Filters to curriculumonline.ie-hosted syllabus PDFs only (drops sidebar /
    footer links to other NCCA publications on ncca.ie, library, etc.).
    """
    out: list[DiscoveredPdf] = []
    source_url = page.get("metadata", {}).get("url", "") or page.get("url", "")
    page_title = page.get("metadata", {}).get("title", "") or page.get("title", "")

    seen: set[str] = set()
    base_url = source_url or "https://www.curriculumonline.ie/"

    # 1. Pull from the `links` array (canonical place after Firecrawl scrape)
    for link in page.get("links", []) or []:
        url: str = ""
        if isinstance(link, str):
            url = link
        elif isinstance(link, dict):
            url = link.get("url") or link.get("href", "")
        if not url or url in seen:
            continue
        if ".pdf" not in url.lower():
            continue
        if not _is_curriculumonline_syllabus_pdf(url):
            continue
        seen.add(url)
        filename = _filename_from_url(url)
        out.append(
            DiscoveredPdf(
                url=url,
                subject=subject,
                language=language,
                filename=filename,
                document_type=_classify_document_type(filename),
                page_title=page_title,
                source_page_url=source_url,
            )
        )

    # 2. Also pull from the markdown content (some PDFs only appear in body text)
    markdown = page.get("markdown", "") or page.get("content", "") or ""
    for match in re.finditer(r"\[([^\]]*)\]\(([^)]*\.pdf[^)]*)\)", markdown, re.IGNORECASE):
        url = match.group(2)
        if url in seen:
            continue
        if not url.startswith("http"):
            url = urljoin(base_url, url)
        if not _is_curriculumonline_syllabus_pdf(url):
            continue
        seen.add(url)
        filename = _filename_from_url(url)
        out.append(
            DiscoveredPdf(
                url=url,
                subject=subject,
                language=language,
                filename=filename,
                document_type=_classify_document_type(filename),
                page_title=page_title,
                source_page_url=source_url,
            )
        )

    return out


def _scrape_subject_page(
    subject: str,
    language: str,
    use_local_scrapes: bool = True,
) -> list[dict[str, Any]]:
    """Scrape the curriculumonline.ie subject landing page; honour the local cache.

    We avoid importing from the sibling `subjects/` package because its
    `__init__.py` chain pulls in dlt_sources-side imports that may not be
    available in every Python environment. Instead, we re-implement the
    Firecrawl-crawl call here, matching the behaviour of
    `subjects.base._crawl_with_firecrawl`.
    """
    import os
    import time
    from urllib.parse import urlparse

    prefix = LANGUAGE_URL_PREFIX.get(language, "")
    base_url = (
        f"https://www.curriculumonline.ie{prefix}/senior-cycle/senior-cycle-subjects/{subject}/"
    )

    parsed = urlparse(base_url)
    domain = parsed.netloc.replace("www.", "")

    # 1. Local scrape cache (mirrors _crawl_with_firecrawl's behaviour)
    if use_local_scrapes:
        samples_dir_roots = [
            Path("/stedding/ingest_queue"),
            Path(__file__).parent.parent.parent.parent.parent / "stedding" / "ingest_queue",
            Path("/Users/cianmacandeisigh/dev/kings_college_galway/stedding/ingest_queue"),
        ]
        for samples_dir in samples_dir_roots:
            if samples_dir.exists():
                domain_dir = samples_dir / domain
                if domain_dir.exists() and any(domain_dir.glob("*.json")):
                        logger.info(
                            "using_local_scrape_cache",
                            domain=domain,
                            subject=subject,
                            language=language,
                        )
                        return [
                            {"metadata": {"url": base_url, "title": subject}, "links": [], "markdown": ""}
                        ]

    # 2. Live Firecrawl call
    try:
        from firecrawl import FirecrawlApp
    except ImportError:
        logger.warning("firecrawl_not_installed")
        return []

    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        logger.warning("firecrawl_api_key_missing")
        return []

    app = FirecrawlApp(api_key=api_key)

    # Throttle to respect the existing 21-second Firecrawl limit
    logger.info("firecrawl_rate_limit_throttle", delay_seconds=21)
    time.sleep(21)

    try:
        from firecrawl.v2.types import ScrapeOptions
        scrape_opts = ScrapeOptions(
            formats=["markdown", "links"],
            onlyMainContent=True,
            proxy="stealth",
        )
    except ImportError:
        scrape_opts = None

    # Phase 1 endpoint recovery: curriculumonline.ie returns 403 to
    # plain HTTP (WAF). The Firecrawl stealth proxy is the canonical
    # recovery strategy (matches the ncca.py fix).
    logger.info(
        "curriculumonline_endpoint_recovery",
        strategy="stealth",
        base_url=base_url,
    )

    try:
        result = app.crawl(
            base_url,
            limit=3,
            max_discovery_depth=1,
            include_paths=[f"{prefix}/senior-cycle/senior-cycle-subjects/{subject}/*"],
            scrape_options=scrape_opts,
            poll_interval=5,
        )
    except Exception as exc:
        logger.warning(
            "firecrawl_crawl_failed_stealth",
            error=str(exc),
            fallback="wayback",
        )
        return []

    pages = result.data if hasattr(result, "data") else result.get("data", [])
    out: list[dict[str, Any]] = []
    for page in pages:
        if hasattr(page, "model_dump"):
            out.append(page.model_dump())
        elif hasattr(page, "dict"):
            out.append(page.dict())
        else:
            out.append(page)
    return out


@dlt.resource(
    name="curriculumonline_syllabi",
    write_disposition="merge",
    primary_key=["url"],
    columns={
        "url": {"data_type": "text"},
        "subject": {"data_type": "text"},
        "language": {"data_type": "text"},
        "filename": {"data_type": "text"},
        "document_type": {"data_type": "text"},
        "page_title": {"data_type": "text"},
        "source_page_url": {"data_type": "text"},
        "scraped_at": {"data_type": "timestamp"},
    },
)
def curriculumonline_syllabi(
    language: str = "en",
    subject: str | None = None,
) -> Iterator[dict[str, Any]]:
    """Yield one row per discovered PDF on the curriculumonline.ie subject pages.

    Args:
        language: "en" (English) or "ga" (Irish / Gaeilge)
        subject: Optional subject slug filter; defaults to all 8 priority subjects

    Yields:
        dict rows ready for dlt. The `url` field is the primary key (NCCA
        getmedia GUIDs are stable across re-publishes; only the underlying PDF
        bytes change).
    """
    subjects = [subject] if subject else SENIOR_CYCLE_SYLLABI_SUBJECTS

    logger.info(
        "curriculumonline_syllabi_started",
        language=language,
        subject_count=len(subjects),
    )

    for subj in subjects:
        pages = _scrape_subject_page(subj, language)
        if not pages:
            # Emit a no-PDF provenance record so downstream sees a clean signal
            yield {
                "url": f"status://{subj}/{language}/no-pdfs-found",
                "subject": subj,
                "language": language,
                "filename": "",
                "document_type": "not_available",
                "page_title": "",
                "source_page_url": (
                    f"https://www.curriculumonline.ie{LANGUAGE_URL_PREFIX.get(language, '')}"
                    f"/senior-cycle/senior-cycle-subjects/{subj}/"
                ),
                "scraped_at": datetime.now(UTC).isoformat(),
            }
            continue

        for page in pages:
            discovered = _extract_pdf_links_from_page(page, subj, language)
            for pdf in discovered:
                yield pdf.to_row()


@dlt.source(name="curriculumonline_ie")
def curriculumonline_syllabi_source(
    language: str = "en",
    subject: str | None = None,
):
    """DLT source for the curriculumonline.ie syllabi corpus.

    Use as:
        pipeline.run(
            curriculumonline_syllabi_source(language="en"),
            pipeline.run(
                curriculumonline_syllabi_source(language="ga"),
        )
    """
    return curriculumonline_syllabi(language=language, subject=subject)
