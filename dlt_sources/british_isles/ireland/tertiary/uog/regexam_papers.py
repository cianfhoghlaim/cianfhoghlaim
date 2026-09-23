"""regexam.nuigalway.ie Papers — authenticated DLT source for UoG past papers.

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.

The University of Galway past paper archive at
https://regexam.nuigalway.ie/regexam/paper_index_search_main_menu.asp
is gated by Microsoft 365 / Entra ID (Azure AD AppProxy at
login.microsoftonline.com/13e3b186-c446-4aab-9c6d-9ab9bb76816c).

This source mirrors the BIEP `examinations_papers.py` pattern but
consumes the per-user credential vault at
`/stedding/user_profiles/<user>/regexam/cookies.json` (the AppProxy
state cookie + the regexam session JWT, captured by the 1-time
`komodo run unlock-uo-portal --user <u>` procedure).

Honors `USE_LOCAL_SCRAPES=true` (default).

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import json
import logging
import os
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import dlt
import structlog

logger = structlog.get_logger(__name__)


SENSITIVITY = "pii"
SOURCE_KEY = "regexam_nuig_papers"
USER_PROFILE_DIR = os.environ.get(
    "UO_PORTAL_PROFILE_DIR",
    "/stedding/user_profiles",
)


@dlt.resource(
    write_disposition="merge",
    primary_key=["module_code", "year", "paper_code"],
    name="regexam_papers",
)
def regexam_papers(
    papers: list[dict[str, str]] | None = None,
    *,
    profile_name: str = "regexam-nuig",
    user_id: str | None = None,
) -> Iterator[dict[str, Any]]:
    """Iterate over the regexam.nuigalway.ie past paper archive for a user.

    Args:
        papers: optional list of paper descriptors
            `{"module_code": str, "year": int, "paper_code": str}`.
        profile_name: the persistent profile name (default:
            `regexam-nuig`).
        user_id: the per-user identifier (default: read from
            UO_PORTAL_USER env var).
    """
    user_id = user_id or os.environ.get("UO_PORTAL_USER", "default")

    papers = papers or []
    now = datetime.now(UTC).isoformat()

    if os.environ.get("USE_LOCAL_SCRAPES", "").lower() in {"1", "true", "yes", "on"}:
        logger.info("regexam_papers.local_cache_mode")
        yield from _yield_local_cache_rows(user_id)
        return

    cookies_path = f"{USER_PROFILE_DIR}/{user_id}/regexam/cookies.json"
    if not os.path.exists(cookies_path):
        logger.warning(
            "regexam_papers.no_cookies_run_unlock_first",
            user_id=user_id,
            path=cookies_path,
        )
        return

    logger.info("regexam_papers.live_scrape_start", user_id=user_id)
    yield from _yield_live_scrape_rows(user_id, cookies_path, papers, profile_name, now)


def _yield_local_cache_rows(user_id: str) -> Iterator[dict[str, Any]]:
    """Read from local cache (Phase 1 stub rows)."""
    yield {
        "module_code": "CS203",
        "year": 2024,
        "paper_code": "CS203-2024-P1",
        "pdf_url": "https://regexam.nuigalway.ie/regexam/papers/CS203-2024-P1.pdf",
        "scraped_at": datetime.now(UTC).isoformat(),
        "source": "regexam.nuigalway.ie",
        "user_id": user_id,
    }


def _yield_live_scrape_rows(
    user_id: str, cookies_path: str, papers: list[dict], profile_name: str, now: str
) -> Iterator[dict[str, Any]]:
    """Live regexam scrape using the per-user M365 cookies.

    Phase 2: implement via sruth_browser.tools.regexam_scraper
    (Playwright-native primary + Stagehand LLM fallback). For now
    this yields a stub row so the source wires cleanly.
    """
    yield {
        "module_code": "CS203",
        "year": 2024,
        "paper_code": "CS203-2024-P1",
        "pdf_url": "https://regexam.nuigalway.ie/regexam/papers/CS203-2024-P1.pdf",
        "scraped_at": now,
        "source": "regexam.nuigalway.ie",
        "user_id": user_id,
    }


@dlt.source(name="regexam_nuig_papers")
def regexam_nuig_papers_source(
    papers: list[dict[str, str]] | None = None,
    *,
    profile_name: str = "regexam-nuig",
    user_id: str | None = None,
) -> Any:
    return regexam_papers(
        papers=papers,
        profile_name=profile_name,
        user_id=user_id,
    )


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="regexam_nuig_papers",
        destination="duckdb",
        dataset_name="regexam_papers",
        dev_mode=True,
    )
    load_info = pipeline.run(regexam_nuig_papers_source())
    print(load_info)
