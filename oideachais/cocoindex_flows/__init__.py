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
- `oideachais.cocoindex_flows.docs_skills_consolidation` — v1 App that tags,
  embeds, and graph-links every file in `docs/` and `.agents/skills/`
  (BAML-driven extraction → LanceDB + FalkorDB). See
  `openspec/changes/docs-skills-consolidation-pipeline/`.
- `oideachais.cocoindex_flows.codebase_indexing` — v1 App that replaces
  the legacy `ccc` CLI; embeds the whole monorepo's source code into
  LanceDB table `codebase_chunks` for semantic search.

The legacy v0 modules remain on disk at their original paths for back-compat
but are NOT re-exported here. Downstream code MUST migrate to the v1 Apps.
"""

from __future__ import annotations

# Lazy import: the legacy v0 modules break at import time on cocoindex==1.0.9.
# Each v1 module guards itself with `COCOINDEX_AVAILABLE` and degrades gracefully.

try:
    from .leabharlann_embedding import (  # noqa: F401
        COCOINDEX_AVAILABLE as LEABHARLANN_COCOINDEX_AVAILABLE,
    )
    from .leabharlann_embedding import (
        DEFAULT_LEABHARLANN_ROOT,
        DEFAULT_TAKEOUT_ROOT,
        DEFAULT_ZOTERO_ROOT,
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
    from .leabharlann_embedding import (
        EMBED_DIM as LEABHARLANN_EMBED_DIM,
    )
    from .leabharlann_embedding import (
        EMBED_MODEL as LEABHARLANN_EMBED_MODEL,
    )
    from .leabharlann_embedding import (
        LANCEDB_URI as LEABHARLANN_LANCEDB_URI,
    )

    _leabharlann_imported = True
except ImportError as e:  # pragma: no cover
    import structlog as _sl

    _sl.get_logger().warning("leabharlann_embedding_import_failed: %s", e)
    _leabharlann_imported = False

try:
    from .docs_skills_consolidation import (  # noqa: F401
        COCOINDEX_AVAILABLE as DOCS_SKILLS_COCOINDEX_AVAILABLE,
    )
    from .docs_skills_consolidation import (
        DEFAULT_DOCS_ROOT,
        DEFAULT_SKILLS_ROOT,
        DOCS_REFRESH_INTERVAL,
        ConceptNode,
        ConsolidationGroupNode,
        DocSkillChunk,
        DocSkillNode,
        RelatesToEdge,
        docs_skills_app,
        search_docs_skills,
    )
    from .docs_skills_consolidation import (
        EMBED_DIM as DOCS_SKILLS_EMBED_DIM,
    )
    from .docs_skills_consolidation import (
        EMBED_MODEL as DOCS_SKILLS_EMBED_MODEL,
    )
    from .docs_skills_consolidation import (
        FALKORDB_GRAPH as DOCS_SKILLS_FALKORDB_GRAPH,
    )
    from .docs_skills_consolidation import (
        FALKORDB_URI as DOCS_SKILLS_FALKORDB_URI,
    )
    from .docs_skills_consolidation import (
        LANCEDB_TABLE as DOCS_SKILLS_LANCEDB_TABLE,
    )
    from .docs_skills_consolidation import (
        LANCEDB_URI as DOCS_SKILLS_LANCEDB_URI,
    )

    _docs_skills_imported = True
except ImportError as e:  # pragma: no cover
    import structlog as _sl

    _sl.get_logger().warning("docs_skills_consolidation_import_failed: %s", e)
    _docs_skills_imported = False

try:
    from .codebase_indexing import (  # noqa: F401
        COCOINDEX_AVAILABLE as CODEBASE_COCOINDEX_AVAILABLE,
    )
    from .codebase_indexing import (
        DEFAULT_REPO_ROOT,
        CodeChunk,
        codebase_app,
        search_codebase,
    )
    from .codebase_indexing import (
        EMBED_DIM as CODEBASE_EMBED_DIM,
    )
    from .codebase_indexing import (
        EMBED_MODEL as CODEBASE_EMBED_MODEL,
    )
    from .codebase_indexing import (
        LANCEDB_TABLE as CODEBASE_LANCEDB_TABLE,
    )
    from .codebase_indexing import (
        LANCEDB_URI as CODEBASE_LANCEDB_URI,
    )
    from .codebase_indexing import (
        REFRESH_INTERVAL as CODEBASE_REFRESH_INTERVAL,
    )
    from .codebase_indexing import (
        TOP_K as CODEBASE_TOP_K,
    )

    _codebase_imported = True
except ImportError as e:  # pragma: no cover
    import structlog as _sl

    _sl.get_logger().warning("codebase_indexing_import_failed: %s", e)
    _codebase_imported = False


__all__ = [
    # Leabharlann
    "LEABHARLANN_COCOINDEX_AVAILABLE",
    "LEABHARLANN_LANCEDB_URI",
    "LEABHARLANN_EMBED_MODEL",
    "LEABHARLANN_EMBED_DIM",
    "DEFAULT_LEABHARLANN_ROOT",
    "DEFAULT_TAKEOUT_ROOT",
    "DEFAULT_ZOTERO_ROOT",
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
    # Docs-Skills consolidation
    "DOCS_SKILLS_COCOINDEX_AVAILABLE",
    "DOCS_SKILLS_LANCEDB_URI",
    "DOCS_SKILLS_FALKORDB_URI",
    "DOCS_SKILLS_FALKORDB_GRAPH",
    "DOCS_SKILLS_EMBED_MODEL",
    "DOCS_SKILLS_EMBED_DIM",
    "DOCS_SKILLS_LANCEDB_TABLE",
    "DOCS_REFRESH_INTERVAL",
    "DEFAULT_DOCS_ROOT",
    "DEFAULT_SKILLS_ROOT",
    "DocSkillChunk",
    "DocSkillNode",
    "ConceptNode",
    "ConsolidationGroupNode",
    "RelatesToEdge",
    "docs_skills_app",
    "search_docs_skills",
    # Codebase index (ccc replacement)
    "CODEBASE_COCOINDEX_AVAILABLE",
    "CODEBASE_LANCEDB_URI",
    "CODEBASE_EMBED_MODEL",
    "CODEBASE_EMBED_DIM",
    "CODEBASE_LANCEDB_TABLE",
    "CODEBASE_REFRESH_INTERVAL",
    "CODEBASE_TOP_K",
    "DEFAULT_REPO_ROOT",
    "CodeChunk",
    "codebase_app",
    "search_codebase",
]
