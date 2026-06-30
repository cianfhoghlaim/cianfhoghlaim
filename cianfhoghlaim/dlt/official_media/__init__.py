"""oideachais.cianfhoghlaim.dlt.official_media — Instagram-export → British-Isles government source enrichment.

Phase 1 of the ``official-media-pipeline`` openspec change. Parses the
JSON bundle Instagram ships in the standard export format, filters
out the noise (friends, family, celebrities) via a curated allowlist
+ BAML fallback, and resolves the canonical official source
(Wikipedia + Companies House + CRO + Mastodon + Bluesky) for each
surviving profile.

Public API (the only thing the rest of the stack imports):

    from cianfhoghlaim.dlt.official_media import (
        instagram_export_source,        # @dlt.source
        allowlist_filter,                # Stage-1 + Stage-2 classifier
        source_resolver,                 # 4-lookup parallel resolver
    )
"""
from __future__ import annotations

from cianfhoghlaim.dlt.official_media.allowlist import AllowlistFilter, allowlist_filter
from cianfhoghlaim.dlt.official_media.instagram_export import (
    FOLLOWER_LIST_KINDS,
    InstagramExportParser,
    instagram_export_source,
)
from cianfhoghlaim.dlt.official_media.source_resolver import SourceResolver, source_resolver

__all__ = [
    "FOLLOWER_LIST_KINDS",
    "AllowlistFilter",
    "InstagramExportParser",
    "SourceResolver",
    "allowlist_filter",
    "instagram_export_source",
    "source_resolver",
]
