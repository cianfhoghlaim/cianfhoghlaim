"""FastAPI webhook bridge for upstream breaking-change alerts.

The four Firecrawl-driven upstream monitors can POST a typed
breaking-change payload here. This route validates the envelope and
forwards it to the n8n workflow at
``https://n8n.cianfhoghlaim.ie/webhook/upstream-breaking-change``.
"""

from __future__ import annotations

import asyncio
import json
import os
import urllib.error
import urllib.request
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

try:
    from fastapi import APIRouter, HTTPException  # type: ignore[import-not-found]
    from pydantic import BaseModel, Field  # type: ignore[import-not-found]

    FASTAPI_AVAILABLE = True
except ImportError as exc:  # pragma: no cover - FastAPI optional in CI
    logger.warning("fastapi_not_available: %s", exc)
    APIRouter = None  # type: ignore[assignment]
    HTTPException = None  # type: ignore[assignment]
    BaseModel = object  # type: ignore[assignment, misc]

    class _FieldFallback:
        def __call__(self, *args: Any, **kwargs: Any) -> Any:
            return None

    Field = _FieldFallback()  # type: ignore[assignment]

    FASTAPI_AVAILABLE = False


N8N_WEBHOOK_URL = os.getenv(
    "N8N_UPSTREAM_BREAKING_CHANGE_WEBHOOK_URL",
    "https://n8n.cianfhoghlaim.ie/webhook/upstream-breaking-change",
)

router = (
    APIRouter(prefix="/upstream", tags=["upstream-monitoring"])
    if FASTAPI_AVAILABLE
    else None
)


class UpstreamBreakingChangeAlert(BaseModel):  # type: ignore[misc]
    """Validated alert envelope sent by upstream Firecrawl monitors."""

    package: str = Field(description="MOTHERDUCK, DLTHUB, LANCEDB, or COCOINDEX")
    version: str = Field(default="0.0.0")
    release_date: str = Field(default="")
    source_url: str = Field(default="")
    release_notes_url: str = Field(default="")
    breaking_changes: list[str] = Field(default_factory=list)
    new_features: list[str] = Field(default_factory=list)
    deprecations: list[str] = Field(default_factory=list)
    detected_at: str = Field(default="")
    content_sha256: str = Field(default="")
    severity: str = Field(default="BREAKING")


class UpstreamWebhookResponse(BaseModel):  # type: ignore[misc]
    """Response returned by the bridge after n8n dispatch."""

    forwarded: bool
    n8n_webhook_url: str
    package: str
    version: str


def _post_to_n8n(payload: dict[str, Any], webhook_url: str = N8N_WEBHOOK_URL) -> bool:
    """POST the alert to n8n using stdlib urllib."""
    body = json.dumps(payload, default=str).encode("utf-8")
    request = urllib.request.Request(
        webhook_url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            status = getattr(response, "status", 200)
            return 200 <= int(status) < 300
    except (urllib.error.URLError, TimeoutError) as exc:
        logger.warning("upstream_n8n_webhook_failed", error=str(exc))
        return False


async def _forward_alert(alert: UpstreamBreakingChangeAlert) -> UpstreamWebhookResponse:
    """Validate and forward one upstream alert to n8n."""
    if not alert.breaking_changes:
        raise HTTPException(  # type: ignore[misc]
            status_code=400,
            detail="breaking_changes must contain at least one item",
        )

    payload = alert.model_dump() if hasattr(alert, "model_dump") else dict(alert)
    forwarded = await asyncio.to_thread(_post_to_n8n, payload, N8N_WEBHOOK_URL)
    if not forwarded:
        raise HTTPException(  # type: ignore[misc]
            status_code=502,
            detail="failed to forward upstream alert to n8n",
        )

    return UpstreamWebhookResponse(
        forwarded=True,
        n8n_webhook_url=N8N_WEBHOOK_URL,
        package=alert.package,
        version=alert.version,
    )


if router is not None:

    @router.post(
        "/breaking-change",
        response_model=UpstreamWebhookResponse,
        summary="Forward upstream breaking-change alerts to n8n",
    )
    async def upstream_breaking_change_webhook(  # type: ignore[no-redef]
        alert: UpstreamBreakingChangeAlert,
    ) -> UpstreamWebhookResponse:
        """Receive a breaking-change alert and trigger the n8n workflow."""
        return await _forward_alert(alert)

    @router.post(
        "/webhook",
        response_model=UpstreamWebhookResponse,
        include_in_schema=False,
    )
    async def upstream_webhook_alias(  # type: ignore[no-redef]
        alert: UpstreamBreakingChangeAlert,
    ) -> UpstreamWebhookResponse:
        """Compatibility alias for monitor configs that POST to /webhook."""
        return await _forward_alert(alert)


__all__ = [
    "FASTAPI_AVAILABLE",
    "N8N_WEBHOOK_URL",
    "UpstreamBreakingChangeAlert",
    "UpstreamWebhookResponse",
    "router",
]
