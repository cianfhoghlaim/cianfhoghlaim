"""Polyglot memory layer over the agent reference corpus.

Per the `2026-08-14-firecrawl-corpus-and-portals` change (Phase 4a),
exposes 3 memory backends (Graphiti + LanceDB + Cognee) over the
`cianfhoghlaim.firecrawl_corpus.docs_index` table + a router that
selects the right backend based on the intent of the agent query.

The 3 backends:

| Backend | Strength | Use case |
|:--|:--|:--|
| `Graphiti` | Temporal (bi-temporal) | "What was the Dagster API in version 1.10?" |
| `LanceDB` | Vector (HNSW) | "What's the relevant chunk for this code query?" |
| `Cognee` | Cross-doc graph | "How does BAML ExtractCurriculumSyllabus relate to CocoIndex _lifespan.py?" |

The router: see `router.py:MemoryRouter.route()`.
"""
from __future__ import annotations

from .cognee_store import CogneeMemoryStore
from .graphiti_store import GraphitiMemoryStore
from .lancedb_store import LanceDBMemoryStore
from .router import MemoryRouter, MemoryRouterResult

__all__ = [
    "CogneeMemoryStore",
    "GraphitiMemoryStore",
    "LanceDBMemoryStore",
    "MemoryRouter",
    "MemoryRouterResult",
]