"""cianfhoghlaim.cocoindex — CocoIndex v1 App canonical home (post-v4 + post-Phase-1 2026-06-30).

This package hosts the 14 CocoIndex v1 Apps (per `oideachais-cocoindex-v1` skill):
- 3 leabharlann_*: leabharlann_books_embedding, leabharlann_zotero_embedding, leabharlann_takeout_embedding
- 4 codebase / storage / config / api indexing
- 3 domain embeddings: unified_embedding, code_embeddings, culture_heritage_embedding
- 2 upstream monitoring: upstream_blog_monitor, upstream_api_surface
- 1 docs_skills_consolidation
- 1 cocoindex_v1_conformance (the 4-rule R1-R4 linter)

Per `oideachais-cocoindex-v1` skill REFACTORING.md item 12:
- `cocoindex/_lifespan.py` is the canonical home for the shared
  `@coco.lifespan` + 3 ContextKeys (LANCE_DB, EMBEDDER, RESOLVED_FILE_REGISTRY).
- Every v1 App imports from `_lifespan` instead of re-declaring.

CLI entry-point: `uv run cianfhoghlaim-cocoindex --help`
"""
from __future__ import annotations

__all__ = [
    # Shared lifespan
    "LANCE_DB",
    "EMBEDDER",
    "RESOLVED_FILE_REGISTRY",
    "lifespan",
    "RESOLVED_REGISTRY",
    "V1_APPS",
]


def __getattr__(name: str) -> object:
    """Lazy attribute access — defer cocoindex imports until needed."""
    if name in {"LANCE_DB", "EMBEDDER", "RESOLVED_FILE_REGISTRY", "lifespan", "RESOLVED_REGISTRY"}:
        from cianfhoghlaim.cocoindex import _lifespan

        return getattr(_lifespan, name)
    if name == "V1_APPS":
        # Canonical list of all 14 v1 Apps (post-Phase-1 2026-06-30).
        return (
            "leabharlann_books_embedding",
            "leabharlann_zotero_embedding",
            "leabharlann_takeout_embedding",
            "codebase_indexing",
            "api_indexing",
            "filesystem_indexing",
            "storage_indexing",
            "config_indexing",
            "unified_embedding",
            "code_embeddings",
            "docs_skills_consolidation",
            "culture_heritage_embedding",
            "upstream_blog_monitor",
            "upstream_api_surface",
            "agent_registry",
            "agents_md",
            "apple_photos_metadata",
            "apple_photos_chunks",
        )
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")