"""
CocoIndex Flows for Oideachais (v1 + leabharlann).

This package has been migrated from the deprecated CocoIndex v0 API to v1.
The previous v0 code is preserved at `oideachais/cocoindex_flows/_v0_archive/`
for historical reference (see `git log` for the migration commit).

Public API (v1):
- `oideachais.cocoindex_flows.leabharlann_embedding` — 3 v1 Apps
  (`leabharlann_books_app`, `leabharlann_zotero_app`, `leabharlann_takeout_app`)
  + their `search_leabharlann_*` query helpers.
- `oideachais.cocoindex_flows.curriculum_embedding_v1` — migrated curriculum
  embedding App (this change introduces the module).
- `oideachais.cocoindex_flows.research_embedding_v1` — migrated research
  embedding App (this change introduces the module).

The legacy v0 modules remain on disk at their original paths for back-compat
but are NOT re-exported here. Downstream code MUST migrate to the v1 Apps.
"""

from __future__ import annotations

# Lazy import: the legacy v0 modules break at import time on cocoindex==1.0.9.
# Each v1 module guards itself with `COCOINDEX_AVAILABLE` and degrades gracefully.

try:
    from .leabharlann_embedding import (  # noqa: F401
        COCOINDEX_AVAILABLE as LEABHARLANN_COCOINDEX_AVAILABLE,
        DEFAULT_LEABHARLANN_ROOT,
        DEFAULT_TAKEOUT_ROOT,
        DEFAULT_ZOTERO_ROOT,
        EMBED_DIM as LEABHARLANN_EMBED_DIM,
        EMBED_MODEL as LEABHARLANN_EMBED_MODEL,
        LANCEDB_URI as LEABHARLANN_LANCEDB_URI,
        LeabharlannBookChunk,
        LeabharlannTakeoutChunk,
        ZoteroPaperChunk,
        extract_arxiv_id_from_filename,
        leabharlann_books_app,
        leabharlann_takeout_app,
        leabharlann_zotero_app,
        search_leabharlann_books,
        search_leabharlann_takeout,
        search_leabharlann_zotero,
    )
    _leabharlann_imported = True
except ImportError as e:  # pragma: no cover
    import structlog as _sl

    _sl.get_logger().warning("leabharlann_embedding_import_failed: %s", e)
    _leabharlann_imported = False


__all__ = [
    # Leabharlann
    "LEABHARLANN_COCOINDEX_AVAILABLE",
    "LEABHARLANN_LANCEDB_URI",
    "LEABHARLANN_EMBED_MODEL",
    "LEABHARLANN_EMBED_DIM",
    "DEFAULT_LEABHARLANN_ROOT",
    "DEFAULT_ZOTERO_ROOT",
    "DEFAULT_TAKEOUT_ROOT",
    "LeabharlannBookChunk",
    "LeabharlannTakeoutChunk",
    "ZoteroPaperChunk",
    "extract_arxiv_id_from_filename",
    "leabharlann_books_app",
    "leabharlann_takeout_app",
    "leabharlann_zotero_app",
    "search_leabharlann_books",
    "search_leabharlann_takeout",
    "search_leabharlann_zotero",
]
