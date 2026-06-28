"""
CocoIndex Flows for Oideachais (v1 + leabharlann).

This package has been migrated from the deprecated CocoIndex v0 API to v1.
The previous v0 code is preserved at `oideachais/cocoindex_flows/_v0_archive/`
for historical reference (see `git log` for the migration commit).

Public API (v1) — 12 v1 Apps total:

Leabharlann (3 sub-Apps in `leabharlann_embedding.py`):
- `leabharlann_books_app`, `leabharlann_zotero_app`,
  `leabharlann_takeout_app` + their `search_leabharlann_*` query
  helpers.

Indexing (1 App each):
- `codebase_indexing.codebase_app` — replaces the legacy `ccc`
  CLI; embeds the whole monorepo's source code into LanceDB
  table `codebase_chunks` for semantic search.
- `docs_skills_consolidation.docs_skills_app` — tags, embeds,
  and graph-links every file in `docs/` and `.agents/skills/`
  (BAML-driven extraction → LanceDB + FalkorDB). See
  `openspec/changes/docs-skills-consolidation-pipeline/`.
- `culture_heritage_embedding.culture_heritage_embedding_app`
  — BAML-extracted `CultureHeritageClaim` chunks from the 6
  personal-heritage Gemini Deep Research PDFs at
  `leabharlann/gemini_deep_research/culture/`.
- `api_indexing`, `filesystem_indexing`, `storage_indexing`,
  `config_indexing`, `unified_embedding` — the 5 storage +
  config + unified LanceDB indexing Apps (per
  `.agents/skills/oideachais-cocoindex-v1/SKILL.md`).

Upstream monitoring (3 Apps; from
`openspec/changes/upstream-package-monitoring/`):
- `upstream_blog_monitor.upstream_blog_monitor_app` —
  ingests Firecrawl webhook payloads for motherduck / dlthub /
  lancedb / cocoindex blog posts → LanceDB `upstream_blog_chunks`
  + FalkorDB `upstream_packages_graph`.
- `upstream_api_surface.upstream_api_surface_app` — watches
  cocoindex docs URLs + `llms-full.txt` → LanceDB
  `upstream_api_chunks` + FalkorDB `ApiChangeNode` →
  `upstream_breaking_change_sensor` Slack alerts.
- `cocoindex_v1_conformance.cocoindex_v1_conformance_app` —
  static AST linter enforcing R1-R4 conformance rules
  (REFACTORING.md item 12 enforcement precondition).

The legacy v0 modules remain on disk at their original paths for
back-compat but are NOT re-exported here. Downstream code MUST
migrate to the v1 Apps.
"""

from __future__ import annotations

# Lazy import: the legacy v0 modules break at import time on cocoindex==1.0.9.
# Each v1 module guards itself with `COCOINDEX_AVAILABLE` and degrades gracefully.

# ---------------------------------------------------------------------------
# Leabharlann (3 sub-Apps)
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Docs-Skills consolidation (1 App)
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Codebase index (ccc replacement; 1 App)
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Culture Heritage (1 App; was previously unexported)
# ---------------------------------------------------------------------------

try:
    from .culture_heritage_embedding import (  # noqa: F401
        COCOINDEX_AVAILABLE as CULTURE_HERITAGE_COCOINDEX_AVAILABLE,
    )
    from .culture_heritage_embedding import (
        DEFAULT_CULTURE_HERITAGE_ROOT,
        CultureHeritageClaimChunk,
        culture_heritage_embedding_app,
    )

    _culture_heritage_imported = True
except ImportError as e:  # pragma: no cover
    import structlog as _sl

    _sl.get_logger().warning("culture_heritage_embedding_import_failed: %s", e)
    _culture_heritage_imported = False

# ---------------------------------------------------------------------------
# API / Filesystem / Storage / Config / Unified indexing (5 Apps;
# were previously unexported; added 2026-06-25 by the
# upstream-package-monitoring change)
# ---------------------------------------------------------------------------

try:
    from .api_indexing import api_indexing_app
    _api_indexing_imported = True
except ImportError as e:  # pragma: no cover
    import structlog as _sl

    _sl.get_logger().warning("api_indexing_import_failed: %s", e)
    _api_indexing_imported = False

try:
    from .filesystem_indexing import filesystem_indexing_app
    _filesystem_indexing_imported = True
except ImportError as e:  # pragma: no cover
    import structlog as _sl

    _sl.get_logger().warning("filesystem_indexing_import_failed: %s", e)
    _filesystem_indexing_imported = False

try:
    from .storage_indexing import storage_indexing_app
    _storage_indexing_imported = True
except ImportError as e:  # pragma: no cover
    import structlog as _sl

    _sl.get_logger().warning("storage_indexing_import_failed: %s", e)
    _storage_indexing_imported = False

try:
    from .config_indexing import config_indexing_app
    _config_indexing_imported = True
except ImportError as e:  # pragma: no cover
    import structlog as _sl

    _sl.get_logger().warning("config_indexing_import_failed: %s", e)
    _config_indexing_imported = False

try:
    from .unified_embedding import unified_embedding_app
    _unified_embedding_imported = True
except ImportError as e:  # pragma: no cover
    import structlog as _sl

    _sl.get_logger().warning("unified_embedding_import_failed: %s", e)
    _unified_embedding_imported = False

# ---------------------------------------------------------------------------
# Upstream Blog Monitor (1 App; new in upstream-package-monitoring)
# ---------------------------------------------------------------------------

try:
    from .upstream_blog_monitor import (  # noqa: F401
        COCOINDEX_AVAILABLE as UPSTREAM_BLOG_MONITOR_COCOINDEX_AVAILABLE,
    )
    from .upstream_blog_monitor import (
        DEFAULT_PAYLOADS_ROOT,
        UPSTREAM_PACKAGES_GRAPH as UPSTREAM_BLOG_GRAPH,
        UpstreamBlogChunk,
        upstream_blog_monitor_app,
    )

    _upstream_blog_imported = True
except ImportError as e:  # pragma: no cover
    import structlog as _sl

    _sl.get_logger().warning("upstream_blog_monitor_import_failed: %s", e)
    _upstream_blog_imported = False

# ---------------------------------------------------------------------------
# Upstream API Surface (1 App; new in upstream-package-monitoring)
# ---------------------------------------------------------------------------

try:
    from .upstream_api_surface import (  # noqa: F401
        COCOINDEX_AVAILABLE as UPSTREAM_API_SURFACE_COCOINDEX_AVAILABLE,
    )
    from .upstream_api_surface import (
        CACHE_ROOT as UPSTREAM_API_CACHE_ROOT,
        UPSTREAM_PACKAGES_GRAPH as UPSTREAM_API_GRAPH,
        WATCHED_DOCS_URLS,
        ApiChangeChunk,
        upstream_api_surface_app,
    )

    _upstream_api_imported = True
except ImportError as e:  # pragma: no cover
    import structlog as _sl

    _sl.get_logger().warning("upstream_api_surface_import_failed: %s", e)
    _upstream_api_imported = False

# ---------------------------------------------------------------------------
# CocoIndex v1 Conformance (1 App; new in upstream-package-monitoring)
# ---------------------------------------------------------------------------

try:
    from .cocoindex_v1_conformance import (  # noqa: F401
        COCOINDEX_AVAILABLE as CONFORMANCE_COCOINDEX_AVAILABLE,
    )
    from .cocoindex_v1_conformance import (
        ConformanceReport,
        check_app_file,
        cocoindex_v1_conformance_app,
        conformance_summary,
        run_conformance_check,
    )

    _conformance_imported = True
except ImportError as e:  # pragma: no cover
    import structlog as _sl

    _sl.get_logger().warning("cocoindex_v1_conformance_import_failed: %s", e)
    _conformance_imported = False


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
    # Culture Heritage (newly exported)
    "CULTURE_HERITAGE_COCOINDEX_AVAILABLE",
    "DEFAULT_CULTURE_HERITAGE_ROOT",
    "CultureHeritageClaimChunk",
    "culture_heritage_embedding_app",
    # Storage + config + unified indexing (newly exported)
    "api_indexing_app",
    "filesystem_indexing_app",
    "storage_indexing_app",
    "config_indexing_app",
    "unified_embedding_app",
    # Upstream blog monitor (new)
    "UPSTREAM_BLOG_MONITOR_COCOINDEX_AVAILABLE",
    "DEFAULT_PAYLOADS_ROOT",
    "UPSTREAM_BLOG_GRAPH",
    "UpstreamBlogChunk",
    "upstream_blog_monitor_app",
    # Upstream API surface (new)
    "UPSTREAM_API_SURFACE_COCOINDEX_AVAILABLE",
    "UPSTREAM_API_CACHE_ROOT",
    "UPSTREAM_API_GRAPH",
    "WATCHED_DOCS_URLS",
    "ApiChangeChunk",
    "upstream_api_surface_app",
    # CocoIndex v1 conformance (new)
    "CONFORMANCE_COCOINDEX_AVAILABLE",
    "ConformanceReport",
    "check_app_file",
    "cocoindex_v1_conformance_app",
    "conformance_summary",
    "run_conformance_check",
]