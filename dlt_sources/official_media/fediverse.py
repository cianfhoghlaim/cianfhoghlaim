"""DEPRECATION SHIM — moved to dlt_sources.official_media.fediverse.

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change (§1.8, master plan §3.2, §7.1), the canonical home is now
`dlt_sources.official_media.fediverse` (a sub-package). This shim
re-exports from the new location for backwards compatibility for at
least one release cycle.

New code SHOULD import from the new location:

    from dlt_sources.official_media.fediverse import (
        resolve_mastodon,
        resolve_bluesky,
    )

Reference:
- Master plan §3.2 ("Themed sub-trees — official_media split")
- Master plan §7.1 ("dlt_sources/ migrations — official_media")
"""
from dlt_sources.official_media.fediverse import *  # noqa: F401, F403
