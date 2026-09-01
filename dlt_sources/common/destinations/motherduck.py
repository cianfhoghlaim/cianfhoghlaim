"""dlt_sources.common.destinations.motherduck — DEPRECATION SHIM.

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change (§1.2). The canonical home is now
`dlt_sources.destinations.motherduck`. This module is preserved as a
re-export shim for at least one release cycle.

New code SHOULD import from the top-level:

    from dlt_sources.destinations.motherduck import get_motherduck_destination

Legacy imports continue to work:

    from dlt_sources.common.destinations.motherduck import get_motherduck_destination
"""
from __future__ import annotations

from dlt_sources.destinations.motherduck import *  # noqa: F401, F403
