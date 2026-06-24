"""
oideachais.cocoindex_flows._lifespan — Shared CocoIndex v1 lifespan.

The 9 CocoIndex v1 Apps in `oideachais/cocoindex_flows/` previously
re-declared the same `@coco.lifespan` and 3 ContextKeys
(LANCE_DB, EMBEDDER, RESOLVED_FILE_REGISTRY) in every file
(REFACTORING.md item 12).

This module is the canonical home. Every v1 App imports from here
instead of re-declaring. The 9 files now contain only the
domain-specific processors; the shared lifespan is shared.

Reference: the v1 pattern from
`oideachais/cocoindex_flows/leabharlann_embedding.py:236-249` is
the original canonical lifespan; this module is its generalised form.
"""
from __future__ import annotations

import os
from collections.abc import AsyncIterator

import structlog

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
        "oideachais_lance_db"
    )
    EMBEDDER = coco.ContextKey[SentenceTransformerEmbedder](  # type: ignore[index]
        "oideachais_embedder",
        detect_change=True,
    )
    RESOLVED_FILE_REGISTRY = coco.ContextKey[dict](  # type: ignore[index]
        "oideachais_resolved_file_registry"
    )
else:
    LANCE_DB = None  # type: ignore[assignment]
    EMBEDDER = None  # type: ignore[assignment]
    RESOLVED_FILE_REGISTRY = None  # type: ignore[assignment]


# Canonical env-var defaults.
LANCEDB_URI = os.getenv("LANCEDB_URI", "rest://lance-api.cianfhoghlaim.ie")
EMBED_MODEL = os.getenv("OIDEACHAIS_EMBED_MODEL", "BAAI/bge-large-en-v1.5")
EMBED_DIM = 1024


if COCOINDEX_AVAILABLE:

    @coco.lifespan
    async def shared_lifespan(builder: coco.EnvironmentBuilder) -> AsyncIterator[None]:  # type: ignore[no-redef]
        """Shared lifespan for all 9 oideachais v1 CocoIndex Apps.

        The original leabharlann lifespan is
        `oideachais/cocoindex_flows/leabharlann_embedding.py:236-249`.
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
