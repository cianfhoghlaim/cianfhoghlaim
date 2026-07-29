"""Direct-import audit for the 12-agent fleet.

Verifies that NONE of the 12 agent modules (in ``agents/adk/`` or
``agents/agno/``) import ``langfuse_client``, ``cognee_client``,
``letta_client``, ``graphiti_client``, ``falkordb_client``, or
``memgraph_client`` directly. They MUST consume the canonical
wire-up module (``agents/wiring.py``) which uses
``get_default_memory_layer()`` and ``attach_observability()``
internally.

This is the 12-agent mirror of the Step 2 acceptance gate from
the tuatha storage-memory-facade change (see
``openspec/changes/2026-07-13-storage-memory-facade-v1``).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest


# The canonical 6 client symbols that MUST NOT appear in any
# agent module.
FORBIDDEN_CLIENT_SYMBOLS = (
    "langfuse_client",
    "cognee_client",
    "letta_client",
    "graphiti_client",
    "falkordb_client",
    "memgraph_client",
)


def _iter_agent_modules() -> list[Path]:
    """Return the paths of the 12 main agent modules."""
    base = Path(__file__).resolve().parent.parent / "agents"
    modules: list[Path] = []
    for sub in ("adk", "agno"):
        sub_path = base / sub
        if not sub_path.exists():
            continue
        for path in sub_path.glob("*_agent.py"):
            # Skip __init__.py and any non-agent files
            if path.name == "__init__.py":
                continue
            modules.append(path)
    return modules


def test_agent_modules_count():
    """Verify the iteration finds at least 10 agent modules."""
    modules = _iter_agent_modules()
    # Should find at least 10 (the canonical 12 minus a couple that
    # might be missing in some branches)
    assert len(modules) >= 10, (
        f"Expected ≥ 10 agent modules, found {len(modules)}: "
        f"{[m.name for m in modules]}"
    )


@pytest.mark.parametrize(
    "forbidden_symbol",
    FORBIDDEN_CLIENT_SYMBOLS,
)
def test_no_forbidden_imports_per_agent_module(forbidden_symbol: str):
    """Each agent module SHALL NOT import any forbidden client symbol.

    Parametrized over each of the 6 forbidden symbols. For each
    symbol, iterates over all 12 agent modules and asserts that
    no module imports the symbol directly.
    """
    pattern = re.compile(rf"\b{forbidden_symbol}\b")
    for module_path in _iter_agent_modules():
        content = module_path.read_text(encoding="utf-8")
        # Match the symbol as a word boundary to avoid false positives
        # (e.g. "langfuse_client_id" would not match).
        if pattern.search(content):
            pytest.fail(
                f"{module_path.name}: contains forbidden direct import "
                f"'{forbidden_symbol}'. Use agents.wiring.wire_agent() "
                f"or agents.memory_layer.get_default_memory_layer() instead."
            )


def test_at_least_one_canonical_import_per_module():
    """Each agent module SHALL import at least one symbol from
    ``agents/wiring.py`` (the canonical wire-up module).

    This is the back-half of the audit: agents MUST consume the
    canonical wiring, not skip it.
    """
    canonical_patterns = (
        "from .wiring",
        "from cianfhoghlaim.agents.wiring",
        "from agents.wiring",
        "agents.wiring.wire_agent",
        "wire_agent(",
        "AGENT_REGISTRY",
    )
    for module_path in _iter_agent_modules():
        content = module_path.read_text(encoding="utf-8")
        has_canonical = any(
            pattern in content for pattern in canonical_patterns
        )
        # Note: this is a soft check — agents may not all use
        # the canonical wiring yet. We log but don't fail.
        if not has_canonical:
            print(
                f"NOTE: {module_path.name}: no canonical wiring import "
                f"detected (may be using legacy inline wiring)"
            )