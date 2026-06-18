"""oideachais.dagster_defs.assets.official_media — Dagster assets for the official-media pipeline.

Phase 5 of the ``official-media-pipeline`` openspec change. Five
assets in the ``official_media`` group:

  * ``extract``              — DLT asset over the Instagram export
  * ``resolve_sources``      — 4-lookup parallel resolver
  * ``embed``                — BGE-M3 embeddings of resolved sources
  * ``cognify``              — Cognee knowledge graph
  * ``hmgcc_co_creation``    — Monthly sentinel for the 12-week co-creation window
"""
from __future__ import annotations

from .cognify import official_media_cognify
from .embed import official_media_embed
from .extract import official_media_extract
from .hmgcc_co_creation import official_media_hmgcc_co_creation
from .resolve_sources import official_media_resolve_sources

__all__ = [
    "official_media_cognify",
    "official_media_embed",
    "official_media_extract",
    "official_media_hmgcc_co_creation",
    "official_media_resolve_sources",
]
