"""
Canonical enum types for the oideachais quadrant.

Single source of truth for:

- `Quadrant` (top-level workspace + wheel name)
- `DocumentType` (the 11 document classes handled by the
  four-directory indexing sweep)
- `EmbeddingModel` (the 3 embedders the platform uses) + the
  `BgeM3` default constant
- `Package` (the 4 upstream packages monitored by
  upstream-package-monitoring)
- `BlogPostType` (the 6 blog-post categories classified by
  ExtractBlogPostMetadata)

Re-exported from `sruth/codeolas/core/types.py` for the publishable
wheel so `crypteolas`, `tuath`, `sruth-browser`, and the cocoindex
flows can all import from one place.

Reference: openspec/changes/upstream-package-monitoring/specs/schema-type-standardization/spec.md
Reference: openspec/changes/four-directory-indexing-and-standards/proposal.md §4
"""

from __future__ import annotations

from enum import StrEnum


class Quadrant(StrEnum):
    """The 5 top-level quadrants of the Cianfhoghlaim monorepo."""

    OIDEACHAIS = "oideachais"
    MEISINFHOGHLAIM = "meaisinfhoghlaim"
    TUATHA = "tuatha"
    CROILAR = "croilar"
    SHARED = "shared"


class DocumentType(StrEnum):
    """The 11 document classes handled by the four-directory indexing sweep."""

    CURRICULUM = "curriculum"
    LEABHARLANN_PDF = "leabharlann_pdf"
    LEABHARLANN_EPUB = "leabharlann_epub"
    LEABHARLANN_TAKEOUT = "leabharlann_takeout"
    ZOTERO_PAPER = "zotero_paper"
    RESEARCH_BRIEF = "research_brief"
    OPENSPEC_CHANGE = "openspec_change"
    SKILL_MD = "skill_md"
    DOCS_MD = "docs_md"
    BAML_SCHEMA = "baml_schema"
    DAGSTER_ASSET = "dagster_asset"


class EmbeddingModel(StrEnum):
    """The 3 embedders the platform uses."""

    BGE_M3 = "BAAI/bge-m3"
    BGE_LARGE_EN_V1_5 = "BAAI/bge-large-en-v1.5"
    TEXT_EMBED_3_LARGE = "openai/text-embedding-3-large"


# Default embedder constant (per the four-directory-indexing-and-standards proposal §4.1.4).
# Matches the actual `_lifespan.py:70` default for backwards compatibility.
BgeM3 = "BAAI/bge-m3"


class Package(StrEnum):
    """The 4 upstream packages whose blogs / docs the upstream-package-monitoring
    pipeline watches.

    Used by:

    - `baml_src/upstream_monitoring.baml:ExtractBlogPostMetadata.package`
    - `baml_src/upstream_monitoring.baml:ExtractCocoIndexApiChange.package`
    - `baml_src/upstream_monitoring.baml:ExtractPackageRelease.package`
    - `infrastructure/firecrawl/monitors/upstream_packages/{name}.yml`
    - `sruth/oideachais/dlt_sources/domains/cross/upstream/blog_post.py:BlogPostRow.package`
    - `sruth/oideachais/cocoindex_flows/upstream_blog_monitor.py:BlogPostNode.package`
    """

    MOTHERDUCK = "motherduck"
    DLTHUB = "dlthub"
    LANCEDB = "lancedb"
    COCOINDEX = "cocoindex"


class BlogPostType(StrEnum):
    """The 6 blog-post categories classified by ExtractBlogPostMetadata.

    Used by:

    - `baml_src/upstream_monitoring.baml:ExtractBlogPostMetadata.blog_post_type`
    - `sruth/oideachais/cocoindex_flows/upstream_blog_monitor.py:BlogPostNode.blog_post_type`
    """

    ANNOUNCEMENT = "announcement"
    TUTORIAL = "tutorial"
    BENCHMARK = "benchmark"
    CASE_STUDY = "case_study"
    RELEASE_NOTES = "release_notes"
    API_DOC = "api_doc"


def embedding_model_string(model: EmbeddingModel) -> str:
    """Return the canonical HuggingFace / OpenAI string for an EmbeddingModel enum value.

    Convenience helper for the 6+ hard-coded `"BAAI/bge-m3"` literals
    being swept by the four-directory-indexing-and-standards migration
    (§ 4.3).
    """
    return model.value


__all__ = [
    "BgeM3",
    "BlogPostType",
    "DocumentType",
    "EmbeddingModel",
    "Package",
    "Quadrant",
    "embedding_model_string",
]
