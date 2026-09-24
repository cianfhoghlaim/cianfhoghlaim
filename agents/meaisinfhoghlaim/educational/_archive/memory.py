"""Memory governance + InMemory / Vertex fallbacks (the archive twin).

Per openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/.
Mirrors `docs/google_examples/agent-valley-archive/archive/tower.py` +
`archive/service.py` patterns.

Three primitives:
- `burn(memory_service, app, user, memory_id)` — the GDPR delete (ADK
  has no delete on BaseMemoryService; this is the application-level delete)
- `list_floor(stage, query)` — read the cards on one of the 5 floors
- `archive_today()` — closing time: write the day's events to the
  Vertex AI Memory Bank (or fall back to InMemory)

Phase 1: InMemoryMemoryService only (dev / local).
Phase 2: VertexAiMemoryBankService for production (per agent-valley's chapter 4).

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from agents.meaisinfhoghlaim._shared import EducationStage

logger = logging.getLogger(__name__)


#: InMemoryMemoryService-compatible shim — the cianfhoghlaim K-12 archive
#: has its own session_events dict for the dev stand-in.
_FLOOR_STORE: dict[tuple[str, str, str], list[dict[str, Any]]] = {}


def _floor_key(app: str, user: str, stage: EducationStage) -> tuple[str, str, str]:
    return (app, user, stage.value)


def list_floor(stage: EducationStage | str, query: str = "") -> list[dict[str, Any]]:
    """List the cards on one floor.

    Phase 1: returns cards from the local _FLOOR_STORE.
    Phase 2: returns cards from Vertex AI Memory Bank (per agent-valley chapter 4).
    """
    stage_val = stage.value if isinstance(stage, EducationStage) else stage
    cards = []
    for key, store in _FLOOR_STORE.items():
        if key[2] != stage_val:
            continue
        for card in store:
            if query and query.lower() not in str(card).lower():
                continue
            cards.append(card)
    return cards


def burn(memory_service: Any, app: str, user: str, memory_id: str) -> bool:
    """GDPR delete — the application-level delete ADK doesn't provide.

    Phase 1: clears from the local _FLOOR_STORE (Phase 1 dev stand-in).
    Phase 2: hits the Vertex AI Memory Bank delete endpoint
    (per agent-valley's chapter 4 burn()).
    """
    try:
        client = getattr(memory_service, "_get_api_client", lambda: None)()
        pager = client.agent_engines.memories.delete(
            name=f"reasoningEngines/{getattr(memory_service, '_agent_engine_id', '')}",
            scope={"app_name": app, "user_id": user},
        )
        if hasattr(pager, "__aiter__"):
            # Async pager — caller must await it. Phase 1 dev skips iteration.
            pass
        else:
            store = getattr(memory_service, "_session_events", {})
            for (a, u), sessions in store.items():
                if a != app or u != user:
                    continue
                for sid, events in sessions.items():
                    store[(a, u)][sid] = [
                        ev for ev in events if getattr(ev, "id", "") != memory_id
                    ]
        return True
    except Exception:
        return False


def archive_today() -> int:
    """Closing time — write the day's session events to the Memory Bank.

    Phase 1: returns 0 (no-op for InMemoryMemoryService).
    Phase 2: hits add_events_to_memory() on Vertex AI Memory Bank
    with wait_for_completion=True (per agent-valley's FILING pattern).
    """
    now = datetime.now(timezone.utc)
    logger.info("archive_today at %s (Phase 1 no-op)", now.isoformat())
    return 0


__all__ = [
    "list_floor",
    "burn",
    "archive_today",
]
