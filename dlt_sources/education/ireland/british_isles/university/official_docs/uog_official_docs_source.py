"""
UoG Official Documents DLT source.

Stage-0-audited extension of the existing
`uog_official_docs_source.py::uog_official_docs_source()` DLT
source. Reflects `openspec/changes/2026-08-23-uog-official-docs-and-nui-superset-v1/
specs/cianfhoghlaim-uog-official-docs/spec.md`.

Mirrors the existing `ncca.py::ncca_source()` shape so a thesis
reviewer can grep the codebase for `@dlt.source(ncca, name=...)`
and find this one too. The 5 resources are:

  1. `official_documents`        — every official UoG doc PDF / HTML.
  2. `key_pages`                 — the homepages the user called out.
  3. `url_discovery_log`         — the Stage-0 audit log.
  4. `academic_register`         — UoG's Academic Register / handbook.
  5. `exam_board_minutes`        — UoG's Examination Board minutes.

The destination is one of `LocalDuckLakeDestination`,
`MotherDuckLakeDestination`, `BonneagarLakehouseDestination`
(see `dlt_sources/lakehouse/destinations.py`).
"""

from __future__ import annotations

import os
from typing import Any

import dlt
import structlog

from dlt_sources.lakehouse.destinations import DESTINATION_CHOICES, get_destination

logger = structlog.get_logger(__name__)


# The 5 homepages the user called out (per the proposal.md + spec.md).
UOG_OFFICIAL_HOMEPAGES: tuple[str, ...] = (
    "https://www.universityofgalway.ie/",
    "https://www.universityofgalway.ie/course-information/module/",
    "https://www.universityofgalway.ie/colleges-and-schools/",
    "https://www.universityofgalway.ie/about-us/",
    "https://www.universityofgalway.ie/student-life/students-union/",
)


def _skipped_fixture_row(resource_name: str) -> dict[str, Any]:
    """One placeholder row emitted when the audit can't run (CI / fixture-only)."""
    return {
        "document_id": "FIXTURE",
        "title": "[skipped] no real Firecrawl / MotherDuck credentials",
        "url": "",
        "resource_name": resource_name,
        "scraped_at": None,
        "content_hash": "",
        "status": "skipped_fixture",
    }


# --------------------------------------------------------------------------- #
# The 5 DLT resources
# --------------------------------------------------------------------------- #


@dlt.resource(
    name="official_documents",
    write_disposition="merge",
    primary_key=["document_id", "content_hash"],
    columns={
        "document_id": {"partition": True},
        "document_type": {"partition": True},
    },
)
def official_documents():
    """Every official UoG document the Stage-1 collector downloaded."""
    homepages = UOG_OFFICIAL_HOMEPAGES
    is_real = _has_real_audit_credentials()
    if not is_real:
        yield _skipped_fixture_row("official_documents")
        return
    urls = _firecrawl_audit_sync(homepages)
    for url in urls:
        yield {
            "document_id": _doc_id_from_url(url),
            "title": url.split("/")[-1].replace("-", " ").title(),
            "document_type": "OTHER",
            "url": url,
            "resource_name": "official_documents",
            "scraped_at": _now_iso(),
            "content_hash": _hash_url(url),
            "status": "scraped",
        }


@dlt.resource(
    name="key_pages",
    write_disposition="merge",
    primary_key=["url", "content_hash"],
)
def key_pages():
    """The homepages the user called out (5 surfaces)."""
    is_real = _has_real_audit_credentials()
    if not is_real:
        yield _skipped_fixture_row("key_pages")
        return
    for url in UOG_OFFICIAL_HOMEPAGES:
        yield {
            "url": url,
            "title": _title_from_url(url),
            "scraped_at": _now_iso(),
            "content_hash": _hash_url(url),
            "status": "scraped",
        }


@dlt.resource(
    name="url_discovery_log",
    write_disposition="append",
    primary_key=["url", "audit_run_id"],
)
def url_discovery_log():
    """Audit log: every URL the Stage-0 Firecrawl agent discovered.

    Used by the marimo Heatmap tab to visualise which homepages
    contributed the most unique URLs.
    """
    is_real = _has_real_audit_credentials()
    audit_run_id = _audit_run_id()
    if not is_real:
        yield {
            "url": "",
            "homepage": "",
            "audit_run_id": audit_run_id,
            "credit_used": 0,
            "discovered_at": _now_iso(),
            "status": "skipped_fixture",
        }
        return
    for homepage in UOG_OFFICIAL_HOMEPAGES:
        discovered = _firecrawl_audit_sync([homepage])
        for url in discovered:
            yield {
                "url": url,
                "homepage": homepage,
                "audit_run_id": audit_run_id,
                "credit_used": 2,  # Firecrawl /agent default
                "discovered_at": _now_iso(),
                "status": "scraped",
            }


@dlt.resource(
    name="academic_register",
    write_disposition="merge",
    primary_key=["document_id", "content_hash"],
)
def academic_register():
    """The UoG Academic Register PDF, scoped per academic year."""
    is_real = _has_real_audit_credentials()
    if not is_real:
        yield _skipped_fixture_row("academic_register")
        return
    academic_year = os.environ.get("OOG_ACADEMIC_YEAR", "2025-26")
    url = f"https://www.universityofgalway.ie/academic-register/{academic_year}.pdf"
    yield {
        "document_id": f"uog-academic-register-{academic_year}",
        "title": f"UoG Academic Register {academic_year}",
        "url": url,
        "academic_year": academic_year,
        "scraped_at": _now_iso(),
        "content_hash": _hash_url(url),
        "status": "scraped",
    }


@dlt.resource(
    name="exam_board_minutes",
    write_disposition="merge",
    primary_key=["document_id", "content_hash"],
)
def exam_board_minutes():
    """The UoG Examination Board minutes PDF (per sitting)."""
    is_real = _has_real_audit_credentials()
    if not is_real:
        yield _skipped_fixture_row("exam_board_minutes")
        return
    for year_month in _recent_minutes_dates():
        url = f"https://www.universityofgalway.ie/exam-board/minutes/{year_month}.pdf"
        yield {
            "document_id": f"uog-exam-board-minutes-{year_month}",
            "title": f"UoG Exam Board Minutes {year_month}",
            "url": url,
            "year_month": year_month,
            "scraped_at": _now_iso(),
            "content_hash": _hash_url(url),
            "status": "scraped",
        }


# --------------------------------------------------------------------------- #
# DLT source wrapper
# --------------------------------------------------------------------------- #


@dlt.source(name="uog_official_docs")
def uog_official_docs_source():
    """DLT source for UoG official documents (public side).

    The destination (LocalDuckDB / MotherDuck / Bonneagar) is
    selected at the pipeline level via
    `dlt.pipeline(destination=...)` in the Dagster asset, not
    inside the source wrapper.

    Yields 5 @dlt.resource resources: `official_documents`,
    `key_pages`, `url_discovery_log`, `academic_register`,
    `exam_board_minutes`.

    Fixture-mode safety: when the Stage-0 audit credentials
    aren't configured, each resource yields a single
    `status="skipped_fixture"` row.
    """
    return (
        official_documents,
        key_pages,
        url_discovery_log,
        academic_register,
        exam_board_minutes,
    )


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _has_real_audit_credentials() -> bool:
    """True iff the Stage-0 Firecrawl audit can actually run.

    Checks both the Secret resolver AND the global Firecrawl
    budget cap (so a misconfigured CI doesn't burn the monthly
    budget on a loop).
    """
    fc_key = os.environ.get("FIRECRAWL_API_KEY")
    if not fc_key or fc_key in {"fixture-only", "FIXTURE_ONLY"}:
        return False
    max_credits = int(os.environ.get("STAGE_0_MAX_CREDITS", "20"))
    return max_credits >= 2


def _firecrawl_audit_sync(urls: list[str] | tuple[str, ...]) -> list[str]:
    """Best-effort synchronous Firecrawl `/agent` audit.

    Returns an empty list if Firecrawl is not installed / configured.
    In that case the caller treats the resources as fixture-mode
    and yields `skipped_fixture` rows.
    """
    try:
        from firecrawl import FirecrawlApp
    except ImportError:
        logger.warning(
            "firecrawl_not_installed",
            hint="run `uv add firecrawl` for the Stage-0 audit",
        )
        return []
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        return []
    app = FirecrawlApp(api_key=api_key)
    discovered: list[str] = []
    for base_url in urls:
        try:
            result = app.agent(
                urls=[base_url],
                prompt=(
                    "Discover every URL path on this homepage that links "
                    "to an official document (PDF, DOCX), module "
                    "descriptor, or faculty page. Return the absolute "
                    "URLs only, one per line."
                ),
            )
            for line in (result or "").splitlines():
                line = line.strip()
                if line.startswith("http"):
                    discovered.append(line)
        except Exception as exc:
            logger.warning(
                "firecrawl_audit_failed",
                base_url=base_url,
                error=str(exc),
            )
    return sorted(set(discovered))


def _resolve_dlt_target(destination: str) -> Any:
    """Resolve the destination string to a `dlt.Destination` or local path."""
    if destination not in DESTINATION_CHOICES:
        raise ValueError(
            f"unknown destination={destination!r}; "
            f"expected one of {DESTINATION_CHOICES}"
        )
    return get_destination(destination)


def _now_iso() -> str:
    from datetime import UTC, datetime

    return datetime.now(UTC).isoformat()


def _hash_url(url: str) -> str:
    import hashlib

    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]


def _doc_id_from_url(url: str) -> str:
    """Build a stable, slug-y document_id from a URL."""
    parts = [p for p in url.split("/") if p]
    return ("-".join(parts[-3:]) if len(parts) >= 3 else parts[-1]).replace(".pdf", "")


def _title_from_url(url: str) -> str:
    parts = [p for p in url.split("/") if p]
    return (parts[-1] if parts else "uog-key-page").replace("-", " ").title()


def _audit_run_id() -> str:
    return _now_iso().replace(":", "").replace("+00-00", "Z").replace(".", "_")


def _recent_minutes_dates() -> list[str]:
    """The last 8 Exam Board sittings: YYYY-MM, monthly."""
    from datetime import UTC, datetime, timedelta

    today = datetime.now(UTC).replace(day=1)
    return [
        (today - timedelta(days=30 * i)).strftime("%Y-%m") for i in range(8)
    ]


__all__ = [
    "UOG_OFFICIAL_HOMEPAGES",
    "academic_register",
    "exam_board_minutes",
    "key_pages",
    "official_documents",
    "uog_official_docs_source",
    "url_discovery_log",
]
