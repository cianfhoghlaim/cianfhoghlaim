"""Tests for the Cognee `personal_archive_typed_edges.py` module.

Per the 2026-08-23-uog-personal-archive-tertiary-modules-v1 change
(WS12 — Tests + observability + thesis figures).

The 10 emitters cover the typed cross-archive edges that join the
personal archive (artefacts → questions → responses → transcript
grades; modules ↔ topics; topics ↔ lecture notes; code cells;
reading lists).
"""
from __future__ import annotations


def test_personal_archive_edges_has_10_entries():
    """`PERSONAL_ARCHIVE_EDGES` tuple has exactly 10 entries."""
    from scripts.graph_storage.cognify.rules.personal_archive_typed_edges import (
        PERSONAL_ARCHIVE_EDGES,
    )

    assert isinstance(PERSONAL_ARCHIVE_EDGES, tuple)
    assert len(PERSONAL_ARCHIVE_EDGES) == 10


def test_personal_archive_edges_emitters_have_consistent_signature():
    """All 10 emitters accept ``(graph, *iterables)`` and yield
    ``(left_node, edge_label, right_node, properties)`` tuples."""
    import inspect

    from scripts.graph_storage.cognify.rules import personal_archive_typed_edges as m

    for name in m.__all__:
        if not name.startswith("emit_"):
            continue
        fn = getattr(m, name)
        sig = inspect.signature(fn)
        # 1st positional arg is always `graph` (the Cognee client).
        params = list(sig.parameters.values())
        assert params[0].name == "graph", (
            f"{name}: first param must be 'graph', got {params[0].name}"
        )
        # 2nd positional arg is the primary iterable (artefacts /
        # questions / topics / etc.).
        assert len(params) >= 2, (
            f"{name}: must accept at least 2 positional params (graph + iterable)"
        )
