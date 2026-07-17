"""
cianfhoghlaim.cocoindex_flows._lifespan — Shared CocoIndex v1 lifespan.

The 12 CocoIndex v1 Apps in `cianfhoghlaim/cocoindex_flows/` previously
re-declared the same `@coco.lifespan` and 3 ContextKeys
(LANCE_DB, EMBEDDER, RESOLVED_FILE_REGISTRY) in every file
(REFACTORING.md item 12).

This module is the canonical home. Every v1 App imports from here
instead of re-declaring. The 12 files now contain only the
domain-specific processors; the shared lifespan is shared.

The 12 v1 Apps (as of 2026-06-25):

1. `leabharlann_embedding.leabharlann_books_app`
2. `leabharlann_embedding.leabharlann_zotero_app`
3. `leabharlann_embedding.leabharlann_takeout_app`
4. `docs_skills_consolidation.docs_skills_app`
5. `codebase_indexing.codebase_app`
6. `culture_heritage_embedding.culture_heritage_embedding_app`
7. `api_indexing.api_indexing_app`
8. `filesystem_indexing.filesystem_indexing_app`
9. `storage_indexing.storage_indexing_app`
10. `config_indexing.config_indexing_app`
11. `unified_embedding.unified_embedding_app`
12. `upstream_blog_monitor.upstream_blog_monitor_app`
13. `upstream_api_surface.upstream_api_surface_app`
14. `cocoindex_v1_conformance.cocoindex_v1_conformance_app`

(Counted: 14 module-level `app = coco.App(...)` declarations after
the `upstream-package-monitoring` change lands. Apps 12-14 are new
in that change. App 6 migrated from the v0-style hybrid
`@coco.flow` + `coco.index_flow` wrapper to the canonical pattern.)

Reference: the v1 pattern from
`cianfhoghlaim/cocoindex_flows/leabharlann_embedding.py:236-249` is
the original canonical lifespan; this module is its generalised form.
"""
from __future__ import annotations

import os
from collections.abc import AsyncIterator

import structlog

# Canonical env-var matrix (CIANFHOGHLAIM_*); the legacy LANCEDB_URI
# env var is honoured as a backwards-compat alias.
try:
    from cianfhoghlaim.observability.env_config import (
        LANCEDB_URL as _CIANFHOGHLAIM_LANCEDB_URL,
    )
except ImportError:  # pragma: no cover - the env-config module ships in the same wheel
    _CIANFHOGHLAIM_LANCEDB_URL = "rest://lakehouse-lance-namespace:8182"

logger = structlog.get_logger(__name__)

# CocoIndex is optional — degrade gracefully if not installed.
try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import lancedb as coco_lancedb  # type: ignore[import-not-found]
    from cocoindex.ops.sentence_transformers import (  # type: ignore[import-not-found]
        SentenceTransformerEmbedder,
    )

    COCOINDEX_AVAILABLE = True
except ImportError as e:
    logger.warning("cocoindex_v1_not_available: %s", e)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    coco_lancedb = None  # type: ignore[assignment]
    SentenceTransformerEmbedder = None  # type: ignore[assignment]


# The 3 shared ContextKeys (per the v1 best practice).
#
# `LANCE_DB` — the LanceDB async connection. Shared across all 9 Apps
#              so we have 1 LMDB state file, 1 embedder, 1 connection.
# `EMBEDDER` — the SentenceTransformer embedder. `detect_change=True`
#              so a model swap auto-re-embeds.
# `RESOLVED_FILE_REGISTRY` — the resolved file registry (used by the
#              3 v1 Apps that walk the filesystem).
if COCOINDEX_AVAILABLE:
    LANCE_DB = coco.ContextKey[coco_lancedb.LanceAsyncConnection](  # type: ignore[index]
        "cianfhoghlaim_lance_db"
    )
    EMBEDDER = coco.ContextKey[SentenceTransformerEmbedder](  # type: ignore[index]
        "cianfhoghlaim_embedder",
        detect_change=True,
    )
    RESOLVED_FILE_REGISTRY = coco.ContextKey[dict](  # type: ignore[index]
        "cianfhoghlaim_resolved_file_registry"
    )
else:
    LANCE_DB = None  # type: ignore[assignment]
    EMBEDDER = None  # type: ignore[assignment]
    RESOLVED_FILE_REGISTRY = None  # type: ignore[assignment]


# Canonical env-var defaults.
# Note: the production endpoint `rest://lance-api.cianfhoghlaim.ie`
# is no longer the default — the dev mode default is the local
# lakehouse-lance-namespace service (in the cianfhoghlaim docker
# network). For host-side dagster dev, override with
# `CIANFHOGHLAIM_LANCEDB_URL=http://127.0.0.1:8182` or set
# `LANCEDB_URI=rest://lakehouse-lance-namespace:8182` in `.env.dev.local`.
LANCEDB_URI = _CIANFHOGHLAIM_LANCEDB_URL
EMBED_MODEL = os.getenv("OIDEACHAIS_EMBED_MODEL", "BAAI/bge-large-en-v1.5")
EMBED_DIM = 1024


if COCOINDEX_AVAILABLE:

    @coco.lifespan
    async def shared_lifespan(builder: coco.EnvironmentBuilder) -> AsyncIterator[None]:  # type: ignore[no-redef]
        """Shared lifespan for all 9 oideachais v1 CocoIndex Apps.

        The original leabharlann lifespan is
        `cianfhoghlaim/cocoindex_flows/leabharlann_embedding.py:236-249`.
        This generalised form is the canonical home and is imported
        by all 9 v1 Apps.
        """
        # 1. LanceDB connection (shared).
        conn = await coco_lancedb.connect_async(LANCEDB_URI)  # type: ignore[arg-type]
        builder.provide(LANCE_DB, conn)  # type: ignore[arg-type]

        # 2. Embedder (re-used; detect_change=True so a model swap
        #    auto-re-embeds).
        builder.provide(  # type: ignore[arg-type]
            EMBEDDER,
            SentenceTransformerEmbedder(EMBED_MODEL),
        )

        # 3. Resolved file registry (the in-memory cache used by
        #    `localfs.walk_dir`).
        builder.provide(RESOLVED_FILE_REGISTRY, {})  # type: ignore[arg-type]

        yield


__all__ = [
    "COCOINDEX_AVAILABLE",
    "LANCE_DB",
    "EMBEDDER",
    "RESOLVED_FILE_REGISTRY",
    "LANCEDB_URI",
    "EMBED_MODEL",
    "EMBED_DIM",
    "shared_lifespan",
]
