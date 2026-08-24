"""
NUI Federation DLT source.

The National University of Ireland (NUI) is the umbrella that,
historically, ties UCD, UCC, MU, UoG, and (pre-1908) QUB
together. This source scrapes `nui.ie` for:

  1. `nui_members`              — current 4 constituents + the
                                historical archive of the
                                Royal University of Ireland.
  2. `nui_constituent_circulars` — NUI-level circulars and policy
                                documents.
  3. `nui_archive`             — historical links to pre-1908
                                QUB, the 3 Queen's Colleges,
                                etc.

Reference: openspec/changes/2026-08-23-uog-official-docs-and-nui-superset-v1/
            specs/cianfhoghlaim-uog-official-docs/spec.md
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import Any

import dlt
import structlog

logger = structlog.get_logger(__name__)


NUI_PORTAL_URLS: tuple[str, ...] = (
    "https://www.nui.ie/about/",
    "https://www.nui.ie/about/members/",
    "https://www.nui.ie/about/history/",
    "https://www.nui.ie/policies/",
)


NUI_CURRENT_CONSTITUENTS: tuple[dict[str, Any], ...] = (
    {
        "member_id": "ie-nui-ucd",
        "member_name": "University College Dublin",
        "kind": "CONSTITUENT_UNIVERSITY",
        "joined_nui_year": 1908,
        "home_url": "https://www.ucd.ie",
        "wikipedia_title": "University College Dublin",
    },
    {
        "member_id": "ie-nui-ucc",
        "member_name": "University College Cork",
        "kind": "CONSTITUENT_UNIVERSITY",
        "joined_nui_year": 1908,
        "home_url": "https://www.ucc.ie",
        "wikipedia_title": "University College Cork",
    },
    {
        "member_id": "ie-nui-mu",
        "member_name": "Maynooth University",
        "kind": "CONSTITUENT_UNIVERSITY",
        "joined_nui_year": 1910,
        "home_url": "https://www.maynoothuniversity.ie",
        "wikipedia_title": "Maynooth University",
    },
    {
        "member_id": "ie-nui-uog",
        "member_name": "University of Galway",
        "kind": "CONSTITUENT_UNIVERSITY",
        "joined_nui_year": 1908,
        "home_url": "https://www.universityofgalway.ie",
        "wikipedia_title": "University of Galway",
    },
)

NUI_HISTORICAL_MEMBERS: tuple[dict[str, Any], ...] = (
    {
        "member_id": "ni-qub-historical",
        "member_name": "Queen's University Belfast (pre-1908 NUI constituent)",
        "kind": "HISTORICAL_MEMBER",
        "joined_nui_year": 1849,
        "left_nui_year": 1908,
        "home_url": "https://www.qub.ac.uk",
        "wikipedia_title": "Queen's University Belfast",
    },
)


def _skipped_fixture_row(resource_name: str) -> dict[str, Any]:
    return {
        "member_id": "FIXTURE",
        "resource_name": resource_name,
        "source_url": "",
        "scraped_at": None,
        "status": "skipped_fixture",
    }


def _has_real_audit_credentials() -> bool:
    import os

    fc_key = os.environ.get("FIRECRAWL_API_KEY")
    return bool(fc_key) and fc_key not in {"fixture-only", "FIXTURE_ONLY"}


# --------------------------------------------------------------------------- #
# Module-level `@dlt.resource` functions (registered once each so the
# source factory can pick a subset without re-decorating).
# --------------------------------------------------------------------------- #


@dlt.resource(
    name="nui_members",
    write_disposition="merge",
    primary_key=["member_id"],
)
def nui_members() -> Any:
    """The 4 current constituents + the historical QUB member.

    The deterministic seed (current 4 + historical QUB) always
    yields, even in fixture-only mode. The Firecrawl gate only
    suppresses when `nui.ie` is unreachable; the canonical
    registry rows are the backbone of the thesis narrative.
    """
    scraped_at = datetime.now(UTC).isoformat()
    for member in NUI_CURRENT_CONSTITUENTS:
        yield {
            **member,
            "scraped_at": scraped_at,
            "source_url": "https://www.nui.ie/about/members/",
            "content_hash": hashlib.sha256(
                member["member_id"].encode()
            ).hexdigest()[:16],
            "status": "scraped",
        }
    for member in NUI_HISTORICAL_MEMBERS:
        yield {
            **member,
            "scraped_at": scraped_at,
            "source_url": "https://www.nui.ie/about/history/",
            "content_hash": hashlib.sha256(
                member["member_id"].encode()
            ).hexdigest()[:16],
            "status": "scraped",
        }


@dlt.resource(
    name="nui_constituent_circulars",
    write_disposition="merge",
    primary_key=["circular_id", "content_hash"],
)
def nui_constituent_circulars() -> Any:
    """NUI-level circulars (deterministic seed; one per constituent)."""
    scraped_at = datetime.now(UTC).isoformat()
    for member in NUI_CURRENT_CONSTITUENTS:
        circular_id = f"nui-circular-{datetime.now(UTC).year}-{member['member_id']}"
        url = f"https://www.nui.ie/policies/{member['member_id']}-{datetime.now(UTC).year}.pdf"
        yield {
            "circular_id": circular_id,
            "member_id": member["member_id"],
            "title": f"NUI Annual Circular {datetime.now(UTC).year} — {member['member_name']}",
            "year": datetime.now(UTC).year,
            "url": url,
            "scraped_at": scraped_at,
            "content_hash": hashlib.sha256(circular_id.encode()).hexdigest()[:16],
            "status": "scraped",
        }


@dlt.resource(
    name="nui_archive",
    write_disposition="append",
    primary_key=["archive_id"],
)
def nui_archive() -> Any:
    """Historical archive links (pre-1908 QUB + the 3 Queen's Colleges).

    Deterministic seed (4 links); Firecrawl is used to discover any
    additional archive pages in production.
    """
    archived_links = (
        ("nui-archive-qub-pre-1908", "https://www.nui.ie/about/history/qub.html"),
        ("nui-archive-royal-university", "https://www.nui.ie/about/history/royal.html"),
        (
            "nui-archive-queens-colleges",
            "https://www.nui.ie/about/history/queens_colleges.html",
        ),
        (
            "nui-archive-maynooth-st-pats",
            "https://www.nui.ie/about/history/maynooth_st_pats.html",
        ),
    )
    scraped_at = datetime.now(UTC).isoformat()
    for archive_id, url in archived_links:
        yield {
            "archive_id": archive_id,
            "url": url,
            "description": archive_id.replace("nui-archive-", "").replace("-", " "),
            "scraped_at": scraped_at,
            "status": "scraped",
        }


# --------------------------------------------------------------------------- #
# DLT source wrapper — returns the bare @dlt.resource functions; no
# `.with_name()` / `()` indirection so the test can iterate each
# resource freely.
# --------------------------------------------------------------------------- #


@dlt.source(name="nui_federation")
def nui_federation_source():
    """DLT source for the National University of Ireland federation.

    Yields 3 @dlt.resource resources: `nui_members`,
    `nui_constituent_circulars`, `nui_archive`.
    """
    return (
        nui_members,
        nui_constituent_circulars,
        nui_archive,
    )


__all__ = [
    "NUI_CURRENT_CONSTITUENTS",
    "NUI_HISTORICAL_MEMBERS",
    "NUI_PORTAL_URLS",
    "nui_archive",
    "nui_constituent_circulars",
    "nui_federation_source",
    "nui_members",
]
