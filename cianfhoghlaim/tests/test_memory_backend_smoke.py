"""Smoke tests for the `MemoryBackend` Protocol + `get_default_backend()` factory.

This module exercises the canonical facade at
``cianfhoghlaim/storage/memf.py`` (added by the T4 commit
``0bf713c45``) and verifies:

1. The factory resolves to a concrete backend whose ``kind``
   is one of ``{graphiti, falkordb, in_memory_lancedb}``.
2. An ``Episode`` added via the canonical facade round-trips
   through ``backend.search(...)``.
3. ``reset_default_backend()`` clears the cached singleton and
   the next ``get_default_backend()`` call returns a fresh
   instance.

These tests run in a CI hermetic environment without Graphiti or
FalkorDB reachable — the cascade
(Graphiti → FalkorDB → InMemoryLanceDB) is expected to fall
through to ``InMemoryLanceDBBackend`` per the cascade order
documented at the top of ``memf.py``.

Reference: openspec/changes/2026-07-13-storage-memory-facade-v1
(1 ADDED requirement on ``agent-memory-systems``).
"""
from __future__ import annotations

import asyncio

from cianfhoghlaim.storage.memf import (
    Episode,
    MemoryBackend,
    get_default_backend,
    reset_default_backend,
)


def test_get_default_backend_returns_implementation() -> None:
    """``get_default_backend()`` returns a ``MemoryBackend`` whose kind is one of the 3 supported kinds."""
    reset_default_backend()
    backend = asyncio.run(get_default_backend())
    assert isinstance(backend, MemoryBackend), (
        f"Expected MemoryBackend, got {type(backend).__name__}"
    )
    assert backend.kind in {"graphiti", "falkordb", "in_memory_lancedb"}, (
        f"Unexpected backend kind: {backend.kind!r}. "
        f"Expected one of {{graphiti, falkordb, in_memory_lancedb}}."
    )


def test_add_episode_round_trips() -> None:
    """An ``Episode`` added via the canonical facade round-trips through ``search(...)``."""
    reset_default_backend()
    backend = asyncio.run(get_default_backend())
    episode_body = (
        "T4 storage-memory-facade smoke test episode. "
        "This is a unique marker phrase for the round-trip test: "
        "STORAGEMEMFACADE-ROUNDTRIP-2026-07-13."
    )
    episode = Episode(
        body=episode_body,
        source="test_memory_backend_smoke",
        source_id="smoke-test-001",
    )
    asyncio.run(backend.add_episode(episode))
    # The cascade should fall through to InMemoryLanceDBBackend in CI;
    # its substring search should match the unique marker phrase.
    hits = asyncio.run(
        backend.search("STORAGEMEMFACADE-ROUNDTRIP-2026-07-13", k=1)
    )
    assert len(hits) >= 1, (
        f"Expected at least 1 search hit after adding the episode; "
        f"got {len(hits)} hits."
    )
    assert any(
        "STORAGEMEMFACADE-ROUNDTRIP-2026-07-13" in (h.snippet or "")
        for h in hits
    ), (
        f"Search hit snippets did not contain the marker phrase. "
        f"Got snippets: {[h.snippet for h in hits]}"
    )
    asyncio.run(backend.close())


def test_reset_default_backend_returns_fresh_instance() -> None:
    """``reset_default_backend()`` clears the cached singleton and the next call returns a fresh instance."""
    reset_default_backend()
    backend_a = asyncio.run(get_default_backend())
    backend_a_id = id(backend_a)
    asyncio.run(backend_a.close())

    reset_default_backend()

    backend_b = asyncio.run(get_default_backend())
    backend_b_id = id(backend_b)

    # The cached singleton was dropped, so we expect a fresh instance.
    assert backend_a_id != backend_b_id, (
        "reset_default_backend() should drop the cached singleton, "
        "but the next get_default_backend() returned the same instance."
    )
    assert isinstance(backend_b, MemoryBackend)
    asyncio.run(backend_b.close())


# ---------------------------------------------------------------------------
# Direct-execution helper: run `python -m pytest tests/test_memory_backend_smoke.py -v`
# to verify all 3 scenarios pass.
# ---------------------------------------------------------------------------

if __name__ == "__main__":  # pragma: no cover
    import sys

    import pytest

    sys.exit(pytest.main([__file__, "-v"]))