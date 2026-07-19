"""
University Deep Extraction — reusable DLT factory.

The factory in this module turns a `UniversityDeepExtractionConfig` into
a 5-resource `@dlt.source` for any British Isles university website. The
case study (`University of Galway`) lives at
`cianfhoghlaim.dlt.british_isles.ireland.education.university_of_galway_deep.py` and is a thin
wrapper around this factory.

5 resources yielded:

  1. `course_pages` — top-level catalogue pages (`/courses/**`)
  2. `module_pages` — school-subdomain module pages (`/schools/computer-science/**`)
  3. `programme_pages` — top-level programme pages (`/programmes/**`)
  4. `handbook_pdfs` — academic-year-specific handbook PDFs (`/handbooks/2025-26/`)
  5. `lecturer_pages` — per-school lecturer directory pages

The factory does NOT call the BAML extraction itself; that's the
`uog_extract_courses` / `uog_extract_modules` / `uog_extract_programmes`
Dagster assets' job (per the `cianfhoghlaim-university-deep-extraction`
spec). The DLT source just yields `(url, markdown, content_hash)` rows
that the assets materialise through the canonical
`BackendRouter.bulk_scrape` 3-stage pipeline (Crawl4AI primary, Firecrawl
paid fallback, CreditBudget guard).

Reference: openspec/changes/university-of-galway-deep-extraction/
"""
from __future__ import annotations

import asyncio
import hashlib
import os
import re
import time
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import dlt
import structlog
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

logger = structlog.get_logger(__name__)


# ── Pydantic config model ────────────────────────────────────────────────


class UniversityDeepExtractionConfig(BaseModel):
    """Per-university configuration consumed by the factory.

    Validated at `sources.yaml` load time (the
    `SourceFactory._build_university_deep_source` builder raises
    `ValueError` on missing required fields).
    """

    model_config = ConfigDict(extra="forbid")

    university_id: str = Field(
        ...,
        description="Kebab-case university id, e.g. 'ie-university-galway'",
        min_length=1,
        max_length=64,
    )
    institution_name: str = Field(
        ...,
        description="Full institution name, e.g. 'University of Galway'",
        min_length=1,
    )
    base_url: HttpUrl = Field(
        ...,
        description="Canonical base URL of the university website",
    )
    catalogue_paths: list[str] = Field(
        default_factory=list,
        description="Glob patterns under base_url for top-level course catalogue pages",
    )
    school_subdomain_paths: list[str] = Field(
        default_factory=list,
        description="Glob patterns under base_url for school / department module pages",
    )
    handbook_root_path: str = Field(
        default="/handbooks/",
        description="URL path under base_url for academic-year handbook PDFs",
    )
    academic_year: int = Field(
        default=2025,
        description="Academic year (e.g. 2025 for 2025-26 handbook)",
        ge=2000,
        le=2100,
    )
    programme_code_regex: str = Field(
        default=r"[A-Z]{2,4}\d{3,4}",
        description="Regex matching programme / course codes (e.g. 'MA335', 'CT511')",
    )
    ects_field_label: str = Field(
        default="ECTS",
        description="Label on the page that precedes the ECTS value",
    )
    prefer_free_browser: bool = Field(
        default=True,
        description="If True, prefer Crawl4AI (free) over Firecrawl (paid) for the bulk scrape",
    )

    @field_validator("catalogue_paths", "school_subdomain_paths")
    @classmethod
    def _paths_must_start_with_slash(cls, v: list[str]) -> list[str]:
        for p in v:
            if not p.startswith("/"):
                raise ValueError(f"path {p!r} must start with '/' (got {p!r})")
        return v

    @field_validator("programme_code_regex")
    @classmethod
    def _regex_must_compile(cls, v: str) -> str:
        try:
            re.compile(v)
        except re.error as exc:
            raise ValueError(f"programme_code_regex {v!r} does not compile: {exc}")
        return v

    def to_legacy_dict(self) -> dict[str, Any]:
        """Convert to a flat dict compatible with the existing
        `sources.yaml` SourceEntry model. Used by the SourceFactory
        dispatcher when the new kind is loaded from the YAML.
        """
        return {
            "university_id": self.university_id,
            "institution_name": self.institution_name,
            "base_url": str(self.base_url),
            "catalogue_paths": list(self.catalogue_paths),
            "school_subdomain_paths": list(self.school_subdomain_paths),
            "handbook_root_path": self.handbook_root_path,
            "academic_year": self.academic_year,
            "programme_code_regex": self.programme_code_regex,
            "ects_field_label": self.ects_field_label,
            "prefer_free_browser": self.prefer_free_browser,
        }


# ── Internal row type (in-memory, not the DuckLake table) ──────────────


@dataclass
class PageRow:
    """One scraped page row yielded by every DLT resource."""

    url: str
    page_kind: str  # one of: course | module | programme | handbook | lecturer
    school_slug: str | None
    raw_markdown: str
    raw_html: str
    backend_used: str
    bytes_in: int
    bytes_out: int
    content_hash: str
    scraped_at: str
    programme_code_match: str | None = None
    handbook_year: int | None = None

    def to_dlt_row(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "page_kind": self.page_kind,
            "school_slug": self.school_slug,
            "raw_markdown": self.raw_markdown,
            "raw_html": self.raw_html,
            "backend_used": self.backend_used,
            "bytes_in": self.bytes_in,
            "bytes_out": self.bytes_out,
            "content_hash": self.content_hash,
            "scraped_at": self.scraped_at,
            "programme_code_match": self.programme_code_match,
            "handbook_year": self.handbook_year,
        }


# ── Scraper (uses the canonical BackendRouter) ─────────────────────────


def _school_slug_from_url(url: str) -> str | None:
    """Best-effort derivation of the school slug from a URL path.

    Example: `https://.../schools/computer-science/courses/ct516` -> `computer-science`.
    """
    try:
        path = urlparse(url).path
    except Exception:
        return None
    parts = [p for p in path.split("/") if p]
    for i, p in enumerate(parts):
        if p in ("schools", "departments", "colleges") and i + 1 < len(parts):
            return parts[i + 1]
    return None


def _programme_code_from_url(url: str, regex: str) -> str | None:
    """First match of `regex` in the URL path, or None."""
    m = re.search(regex, urlparse(url).path)
    return m.group(0) if m else None


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


async def _scrape_one(
    url: str,
    *,
    prefer_free: bool,
    page_kind: str,
    school_slug: str | None,
    programme_code_regex: str,
    handbook_year: int | None,
) -> PageRow | None:
    """Run the 3-stage scrape (pre-research → bulk-scrape → markdown) for one URL.

    Falls back to free Crawl4AI when the credit budget is exhausted (per
    the `author-archive-pipeline` spec). Returns None on failure (with
    a warning log) so the DLT resource can yield 0 rows for that URL
    without crashing the whole asset run.
    """
    try:
        from bonneagar.stacks.browser.sruth_browser import BackendRouter, ScrapeStrategist
    except ImportError as exc:
        logger.warning(
            "browser_module_not_available",
            url=url,
            error=str(exc),
            hint="pip install -e infrastructure/browser",
        )
        return None

    strategist = ScrapeStrategist()
    try:
        result = await strategist.bulk_scrape(
            url=url,
            hint=None,
            prefer_free=prefer_free,
        )
    except Exception as exc:  # noqa: BLE001 — best-effort
        logger.warning(
            "university_bulk_scrape_failed",
            url=url,
            error=str(exc),
        )
        return None

    if not getattr(result, "success", False):
        logger.warning(
            "university_bulk_scrape_unsuccessful",
            url=url,
            backend=getattr(result, "backend_used", "unknown"),
        )
        return None

    raw_markdown = getattr(result, "markdown", "") or ""
    raw_html = getattr(result, "html", "") or ""
    if not raw_markdown and not raw_html:
        return None

    return PageRow(
        url=url,
        page_kind=page_kind,
        school_slug=school_slug or _school_slug_from_url(url),
        raw_markdown=raw_markdown,
        raw_html=raw_html,
        backend_used=getattr(result, "backend_used", "unknown"),
        bytes_in=getattr(result, "bytes_in", len(raw_html)),
        bytes_out=getattr(result, "bytes_out", len(raw_markdown)),
        content_hash=_content_hash(raw_markdown or raw_html),
        scraped_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        programme_code_match=_programme_code_from_url(url, programme_code_regex),
        handbook_year=handbook_year,
    )


def _expand_globs_to_urls(
    base_url: str,
    patterns: list[str],
) -> list[str]:
    """Convert glob patterns under base_url into concrete URLs.

    The current implementation treats each pattern as a single
    catalogue page (the user's first scrape to seed the
    `university_research_sitemap`). The downstream pre-research
    step discovers the rest of the sitemap via the
    `BackendRouter.pre_research` sitemap+sample path.

    Returns a deduplicated list of absolute URLs.
    """
    seen: set[str] = set()
    out: list[str] = []
    for p in patterns:
        # Strip the trailing `/**` glob; we want the bare path.
        clean = p.split("*", 1)[0].rstrip("/")
        url = urljoin(base_url.rstrip("/") + "/", clean.lstrip("/"))
        if url not in seen:
            seen.add(url)
            out.append(url)
    return out


# ── The 5 DLT resources ────────────────────────────────────────────────


def _make_resources(
    config: UniversityDeepExtractionConfig,
):
    """Build the 5 DLT resources for the given config.

    Resources are returned as a list (not a generator) so the caller
    can wrap them in a `@dlt.source` decorator.
    """
    base_url = str(config.base_url).rstrip("/")
    programme_code_regex = config.programme_code_regex
    prefer_free = config.prefer_free_browser

    @dlt.resource(
        name="course_pages",
        write_disposition="merge",
        primary_key=["url", "content_hash"],
        columns={
            "university_id": {"partition": True},
            "academic_year": {"partition": True},
        },
    )
    def course_pages() -> Iterator[dict[str, Any]]:
        urls = _expand_globs_to_urls(base_url, config.catalogue_paths)
        for url in urls:
            row = asyncio.run(
                _scrape_one(
                    url,
                    prefer_free=prefer_free,
                    page_kind="course",
                    school_slug=None,
                    programme_code_regex=programme_code_regex,
                    handbook_year=None,
                )
            )
            if row is None:
                continue
            d = row.to_dlt_row()
            d["university_id"] = config.university_id
            d["academic_year"] = config.academic_year
            yield d

    @dlt.resource(
        name="module_pages",
        write_disposition="merge",
        primary_key=["url", "content_hash"],
        columns={
            "university_id": {"partition": True},
            "academic_year": {"partition": True},
            "school_slug": {"partition": True},
        },
    )
    def module_pages() -> Iterator[dict[str, Any]]:
        urls = _expand_globs_to_urls(base_url, config.school_subdomain_paths)
        for url in urls:
            row = asyncio.run(
                _scrape_one(
                    url,
                    prefer_free=prefer_free,
                    page_kind="module",
                    school_slug=_school_slug_from_url(url),
                    programme_code_regex=programme_code_regex,
                    handbook_year=None,
                )
            )
            if row is None:
                continue
            d = row.to_dlt_row()
            d["university_id"] = config.university_id
            d["academic_year"] = config.academic_year
            yield d

    @dlt.resource(
        name="programme_pages",
        write_disposition="merge",
        primary_key=["url", "content_hash"],
        columns={
            "university_id": {"partition": True},
            "academic_year": {"partition": True},
        },
    )
    def programme_pages() -> Iterator[dict[str, Any]]:
        # Programme pages are usually under the same catalogue path but
        # with a different page_kind. We yield the same URLs as
        # course_pages but tagged 'programme' so the BAML extraction
        # routes them to `ExtractProgrammeDescriptor`.
        urls = _expand_globs_to_urls(base_url, config.catalogue_paths)
        for url in urls:
            row = asyncio.run(
                _scrape_one(
                    url,
                    prefer_free=prefer_free,
                    page_kind="programme",
                    school_slug=None,
                    programme_code_regex=programme_code_regex,
                    handbook_year=None,
                )
            )
            if row is None:
                continue
            d = row.to_dlt_row()
            d["university_id"] = config.university_id
            d["academic_year"] = config.academic_year
            yield d

    @dlt.resource(
        name="handbook_pdfs",
        write_disposition="merge",
        primary_key=["url", "content_hash"],
        columns={
            "university_id": {"partition": True},
            "academic_year": {"partition": True},
        },
    )
    def handbook_pdfs() -> Iterator[dict[str, Any]]:
        # Scrape the handbook root for the configured academic year.
        # The pre-research step expands the full list of PDF URLs
        # downstream; here we just seed the root page.
        root_url = urljoin(
            base_url + "/",
            config.handbook_root_path.lstrip("/").rstrip("/") + "/",
        )
        year_str = f"{config.academic_year}-{(config.academic_year + 1) % 100:02d}"
        # Try a few candidate handbook PDFs (M.Sc. AI, M.Sc. CS, B.Sc.)
        for programme_slug in ("msc-ai", "msc-cs", "bsc-cs", "bsc-maths"):
            candidate = urljoin(
                root_url,
                f"{programme_slug}-{year_str}.pdf",
            )
            row = asyncio.run(
                _scrape_one(
                    candidate,
                    prefer_free=prefer_free,
                    page_kind="handbook",
                    school_slug=None,
                    programme_code_regex=programme_code_regex,
                    handbook_year=config.academic_year,
                )
            )
            if row is None:
                continue
            d = row.to_dlt_row()
            d["university_id"] = config.university_id
            d["academic_year"] = config.academic_year
            yield d

    @dlt.resource(
        name="lecturer_pages",
        write_disposition="merge",
        primary_key=["url", "content_hash"],
        columns={
            "university_id": {"partition": True},
            "academic_year": {"partition": True},
            "school_slug": {"partition": True},
        },
    )
    def lecturer_pages() -> Iterator[dict[str, Any]]:
        # Lecturer directory pages are usually under each school subdomain.
        urls = _expand_globs_to_urls(base_url, config.school_subdomain_paths)
        for url in urls:
            lecturer_url = urljoin(url.rstrip("/") + "/", "people")
            row = asyncio.run(
                _scrape_one(
                    lecturer_url,
                    prefer_free=prefer_free,
                    page_kind="lecturer",
                    school_slug=_school_slug_from_url(url),
                    programme_code_regex=programme_code_regex,
                    handbook_year=None,
                )
            )
            if row is None:
                continue
            d = row.to_dlt_row()
            d["university_id"] = config.university_id
            d["academic_year"] = config.academic_year
            yield d

    return [
        course_pages,
        module_pages,
        programme_pages,
        handbook_pdfs,
        lecturer_pages,
    ]


# ── Public factory entry point ──────────────────────────────────────────


def create_university_deep_extraction_source(
    config: UniversityDeepExtractionConfig,
) -> Any:
    """Return a `@dlt.source` for the given per-university config.

    The returned object is a real `dlt.source` (decorated) with 5
    resources. It is not materialised; the caller decides when to
    run it through a `dlt.pipeline`.
    """
    @dlt.source(name=f"university_{config.university_id}_deep")
    def _source() -> list[Any]:
        return _make_resources(config)

    return _source


def university_deep_extraction_source_from_dict(config_dict: dict[str, Any]) -> Any:
    """Convenience helper: build the source from a flat dict
    (the shape produced by the SourceFactory's `_build_university_deep_source`).
    """
    config = UniversityDeepExtractionConfig.model_validate(config_dict)
    return create_university_deep_extraction_source(config)


__all__ = [
    "UniversityDeepExtractionConfig",
    "PageRow",
    "create_university_deep_extraction_source",
    "university_deep_extraction_source_from_dict",
]
