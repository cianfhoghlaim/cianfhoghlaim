"""
named_destinations — DEPRECATION SHIM (Wave 1 §1.2).

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change (§1.2), this file is a re-export shim. The canonical home is
``dlt_sources.destinations`` (top-level), not
``dlt_sources.common.destinations``.

Legacy imports continue to work, but new code SHOULD import from:

    from dlt_sources.destinations import named_destinations

This shim is preserved for at least one release cycle per the
dlt_sources LEGACY_ALIASES.md precedent.
"""
from __future__ import annotations

# Re-export from the canonical top-level layer-grouped destinations package.
from dlt_sources.destinations import (  # noqa: F401
    DESTINATIONS,
    named_destinations,
)
from dlt_sources.destinations.ducklake import (  # noqa: F401
    get_ducklake_destination,
    ducklake_cianfhoghlaim_at_timestamp,
    ducklake_cianfhoghlaim_at_version,
    ducklake_cianfhoghlaim_table_changes,
)
from dlt_sources.destinations.motherduck import get_motherduck_destination  # noqa: F401
from dlt_sources.destinations.filesystem import get_filesystem_destination  # noqa: F401
from dlt_sources.destinations.iceberg import get_iceberg_destination  # noqa: F401

__all__ = [
    "DESTINATIONS",
    "named_destinations",
    "get_ducklake_destination",
    "ducklake_cianfhoghlaim_at_timestamp",
    "ducklake_cianfhoghlaim_at_version",
    "ducklake_cianfhoghlaim_table_changes",
    "get_motherduck_destination",
    "get_filesystem_destination",
    "get_iceberg_destination",
]
