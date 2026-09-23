"""Canvas Materials — DLT source for UoG Canvas LMS course materials.

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.

University of Galway runs Canvas by Instructure at
https://canvas.universityofgalway.ie/ (the canonical URL — verified
during Phase 1 PoC). This DLT source has 2 backends:

1. **Primary: Canvas REST API** with a Personal Access Token
   (self-service at https://canvas.universityofgalway.ie/profile/settings
   → New Access Token; the user generates their own — no IT
   involvement). Token format: `Authorization: Bearer <token>`.
   Endpoints: `/api/v1/users/self/courses`, per-course `/modules`,
   per-module `/items`, per-file download.

2. **Fallback: Patchright + M365 OAuth** for users whose PAT endpoint
   is disabled by UoG IT (auto-fallback; no IT involvement — uses the
   user's existing M365 student credentials).

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
SOURCE_KEY = "canvas_nuig_files"
USER_PROFILE_DIR = os.environ.get(
    "UO_PORTAL_PROFILE_DIR",
    "/stedding/user_profiles",
)


def _get_canvas_token(user_id: str) -> str | None:
    """Return the user's Canvas Personal Access Token, or None if not set."""
    return os.environ.get(f"CANVAS_NUIG_TOKEN_{user_id.upper()}") or os.environ.get("CANVAS_NUIG_TOKEN")


def _get_canvas_base_url() -> str:
    """Return the Canvas base URL (default: UoG)."""
    return os.environ.get("CANVAS_NUIG_BASE_URL", "https://canvas.universityofgalway.ie")


@dlt.resource(
    write_disposition="merge",
    primary_key=["user_id", "course_id", "file_id"],
    name="canvas_materials",
)
def canvas_materials(
    *,
    user_id: str | None = None,
    file_types: list[str] | None = None,
) -> Iterator[dict[str, Any]]:
    """Iterate over the user's Canvas course materials.

    Tries the REST API first (PAT). Falls back to Patchright + M365
    OAuth if PAT is unavailable or returns 401/403.
    """
    user_id = user_id or os.environ.get("UO_PORTAL_USER", "default")
    file_types = file_types or ["pdf", "docx", "pptx", "mp4"]

    now = datetime.now(UTC).isoformat()

    if os.environ.get("USE_LOCAL_SCRAPES", "").lower() in {"1", "true", "yes", "on"}:
        logger.info("canvas_materials.local_cache_mode")
        yield from _yield_local_cache_rows(user_id, now)
        return

    token = _get_canvas_token(user_id)
    base_url = _get_canvas_base_url()

    if token:
        logger.info("canvas_materials.rest_api_primary", user_id=user_id, base_url=base_url)
        try:
            yield from _yield_via_rest_api(user_id, base_url, token, file_types, now)
            return
        except (PermissionError, ConnectionError, TimeoutError, ValueError) as exc:
            logger.warning(
                "canvas_materials.rest_api_failed_falling_back_to_patchright",
                user_id=user_id,
                error=str(exc),
            )

    cookies_path = f"{USER_PROFILE_DIR}/{user_id}/canvas/cookies.json"
    if os.path.exists(cookies_path):
        logger.info("canvas_materials.patchright_fallback", user_id=user_id)
        yield from _yield_via_patchright(user_id, cookies_path, now)
        return

    logger.warning(
        "canvas_materials.no_pat_no_cookies",
        user_id=user_id,
        hint="Set CANVAS_NUIG_TOKEN_<user> or run komodo unlock-canvas-nuig-profile --user <u>",
    )


def _yield_local_cache_rows(user_id: str, now: str) -> Iterator[dict[str, Any]]:
    yield {
        "user_id": user_id,
        "course_id": "BSC-CS-Y2",
        "file_id": "cs203-week1-slides.pdf",
        "file_type": "pdf",
        "title": "CS203 Week 1 — Introduction slides",
        "file_url": f"/stedding/user_profiles/{user_id}/canvas/cs203-week1-slides.pdf",
        "module_code": "CS203",
        "scraped_at": now,
        "source": "canvas.universityofgalway.ie",
        "backend": "local_cache",
    }


def _yield_via_rest_api(
    user_id: str, base_url: str, token: str, file_types: list[str], now: str
) -> Iterator[dict[str, Any]]:
    """Primary: Canvas REST API with PAT (no IT involvement).

    Phase 2: implement via httpx + the Canvas REST endpoints.
    For now yields a stub row.
    """
    yield {
        "user_id": user_id,
        "course_id": "BSC-CS-Y2",
        "file_id": "cs203-week1-slides.pdf",
        "file_type": "pdf",
        "title": "CS203 Week 1 — Introduction slides",
        "file_url": f"{base_url}/files/12345/download",
        "module_code": "CS203",
        "scraped_at": now,
        "source": base_url,
        "backend": "canvas_rest_api",
    }


def _yield_via_patchright(user_id: str, cookies_path: str, now: str) -> Iterator[dict[str, Any]]:
    """Fallback: Patchright + M365 OAuth cookies (no IT involvement).

    Phase 2: implement via sruth_browser.tools.canvas_scraper
    (Patchright primary + Stagehand LLM fallback). For now yields
    a stub row.
    """
    yield {
        "user_id": user_id,
        "course_id": "BSC-CS-Y2",
        "file_id": "cs203-week1-slides.pdf",
        "file_type": "pdf",
        "title": "CS203 Week 1 — Introduction slides",
        "file_url": f"/stedding/user_profiles/{user_id}/canvas/cs203-week1-slides.pdf",
        "module_code": "CS203",
        "scraped_at": now,
        "source": "canvas.universityofgalway.ie",
        "backend": "patchright",
    }


@dlt.source(name="canvas_nuig_materials")
def canvas_nuig_materials_source(
    *,
    user_id: str | None = None,
    file_types: list[str] | None = None,
) -> Any:
    return canvas_materials(user_id=user_id, file_types=file_types)


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="canvas_nuig_materials",
        destination="duckdb",
        dataset_name="canvas_materials",
        dev_mode=True,
    )
    load_info = pipeline.run(canvas_nuig_materials_source())
    print(load_info)
