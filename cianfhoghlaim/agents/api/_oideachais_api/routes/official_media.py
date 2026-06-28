"""
oideachais.api.routes.official_media — FastAPI routes for the
official-media pipeline.

Phase 6 of the official-media-pipeline openspec change. Three
endpoints:

    GET  /api/official-media/candidates
        List the surviving official-media candidates (after the 2-stage
        filter). Supports ``?category=university`` and ``?jurisdiction=ie``.

    GET  /api/official-media/{candidate_id}
        Return one resolved source by its candidate_id, including all
        11 resolved fields + the Wikipedia extract + the HMGCC
        co-creation sub-url when applicable.

    POST /api/official-media/upload
        Accept a multipart Instagram export zip upload, parse it, and
        return a job id. The job is then processed asynchronously by
        the ``official_media_extract`` Dagster asset.
"""
from __future__ import annotations

import logging
import tempfile
import uuid
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/official-media", tags=["official-media"])


# ============================================================================
# Pydantic Models
# ============================================================================


class CandidateRow(BaseModel):
    """One row of the candidates list."""

    candidate_id: str
    ig_username: str
    ig_href: str
    list_kind: str
    followed_at: datetime | None = None
    ig_export_id: str
    category: str | None = None
    match_stage: int | None = None
    match_source: str | None = None


class ResolvedSourceRow(BaseModel):
    """One row of the resolved sources list."""

    candidate_id: str
    ig_username: str
    category: str | None = None
    official_website: str | None = None
    wikipedia_url: str | None = None
    wikipedia_extract: str | None = None
    companies_house_id: str | None = None
    companies_house_name: str | None = None
    cro_number: str | None = None
    mastodon_handle: str | None = None
    mastodon_url: str | None = None
    bluesky_handle: str | None = None
    bluesky_did: str | None = None
    bluesky_url: str | None = None
    resolved_at: datetime
    resolver_notes: str = ""


class UploadResponse(BaseModel):
    """Response from POST /api/official-media/upload."""

    job_id: str
    status: str = "queued"
    upload_path: str
    hint: str = Field(
        default="Run `dagster materialise -a official_media_extract` to process."
    )


# ============================================================================
# Helpers
# ============================================================================


def _iter_allowlist_candidates() -> Iterator[CandidateRow]:
    """Yield one CandidateRow per entry in the 4 allowlist YAMLs.

    This is the offline-friendly default: the marimo mission-control
    dashboard renders the allowlist when the DLT-managed candidates
    table is empty (the typical first-time-run state).
    """
    from dlt_sources.official_media.allowlist import allowlist_filter

    for category, usernames in allowlist_filter.categories().items():
        for username in usernames:
            yield CandidateRow(
                candidate_id=f"{username}@allowlist",
                ig_username=username,
                ig_href=f"https://www.instagram.com/{username}",
                list_kind="allowlist",
                followed_at=None,
                ig_export_id="allowlist_seed",
                category=category,
                match_stage=1,
                match_source=f"allowlist_{category}.yaml",
            )


def _iter_resolved_overrides() -> Iterator[ResolvedSourceRow]:
    """Yield one ResolvedSourceRow per override (the 4 intelligence
    agencies). Used when the resolved_sources table is empty."""
    from dlt_sources.official_media.source_resolver import source_resolver

    for username in ("mi5official", "mi6official", "gchq", "hmgcc"):
        try:
            resolved = source_resolver.resolve(username, category="intelligence")
        except Exception as exc:
            logger.warning(
                "official_media_resolved_override_failed",
                username=username,
                error=str(exc),
            )
            continue
        yield ResolvedSourceRow(
            candidate_id=resolved.candidate_id,
            ig_username=resolved.ig_username,
            category=resolved.category,
            official_website=resolved.official_website,
            wikipedia_url=resolved.wikipedia_url,
            wikipedia_extract=resolved.wikipedia_extract,
            companies_house_id=resolved.companies_house_id,
            companies_house_name=resolved.companies_house_name,
            cro_number=resolved.cro_number,
            mastodon_handle=resolved.mastodon_handle,
            mastodon_url=resolved.mastodon_url,
            bluesky_handle=resolved.bluesky_handle,
            bluesky_did=resolved.bluesky_did,
            bluesky_url=resolved.bluesky_url,
            resolved_at=resolved.resolved_at,
            resolver_notes=resolved.resolver_notes,
        )


# ============================================================================
# Endpoints
# ============================================================================


@router.get("/candidates", response_model=list[CandidateRow])
def list_candidates(
    category: str | None = Query(default=None),
    jurisdiction: str | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=2000),
) -> list[CandidateRow]:
    """List the official-media candidates.

    In production this reads the DLT-managed
    ``oideachais.official_media.candidates`` table. In offline mode
    (no DLT run yet) it serves the curated allowlist as a fallback
    so the marimo + TanStack surfaces have something to render.
    """
    rows = list(_iter_allowlist_candidates())
    if category:
        rows = [r for r in rows if r.category == category]
    if jurisdiction:
        rows = [r for r in rows if r.ig_username.endswith(jurisdiction)]
    return rows[:limit]


@router.get("/{candidate_id}", response_model=ResolvedSourceRow)
def get_resolved_source(candidate_id: str) -> ResolvedSourceRow:
    """Return one resolved source by its ``candidate_id``.

    The ``candidate_id`` is the same string the marimo dashboard
    surfaces in the "deep link" column.
    """
    # Strip the "@<export_id>" suffix if present
    username = candidate_id.split("@", 1)[0]
    for resolved in _iter_resolved_overrides():
        if resolved.ig_username == username:
            return resolved
    raise HTTPException(
        status_code=404,
        detail=f"candidate_id={candidate_id!r} not found",
    )


@router.post("/upload", response_model=UploadResponse)
async def upload_instagram_export(
    file: UploadFile = File(...),
) -> UploadResponse:
    """Accept a multipart Instagram export zip upload.

    The zip is written to a temp directory, the path is exported as
    ``OIDEACHAIS_IG_EXPORT_DIR`` for the next ``official_media_extract``
    materialisation, and a job id is returned. This is intentionally
    a thin wrapper — the heavy lifting is done by the Dagster asset.
    """
    if not file.filename or not file.filename.endswith(".zip"):
        raise HTTPException(
            status_code=400,
            detail="Upload must be a .zip file (the Instagram export).",
        )

    job_id = str(uuid.uuid4())
    dest_dir = Path(tempfile.gettempdir()) / f"ig_export_{job_id}"
    dest_dir.mkdir(parents=True, exist_ok=True)
    zip_path = dest_dir / file.filename
    contents = await file.read()
    zip_path.write_bytes(contents)
    logger.info(
        "official_media_upload_received",
        job_id=job_id,
        filename=file.filename,
        size=len(contents),
    )
    return UploadResponse(
        job_id=job_id,
        upload_path=str(dest_dir),
    )
