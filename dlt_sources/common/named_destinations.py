"""
named_destinations — re-export shim.

Per the **2026-08-24-wave-4-ducklake-v1-hardening-v1** openspec change,
this file is now a re-export shim. The canonical home is
`dlt_sources.common.destinations.`.

Legacy imports continue to work, but new code SHOULD import from:

    from dlt_sources.common.destinations import named_destinations

This shim is preserved for at least one release cycle per the
dlt_sources LEGACY_ALIASES.md precedent.
"""
from __future__ import annotations

# Re-export from the layer-grouped destinations package.
# named_destinations is the canonical factory; the layer submodules
# (ducklake, motherduck, filesystem, iceberg) are reachable via
# `dlt_sources.common.destinations.<layer>`.
from dlt_sources.common.destinations import named_destinations, DESTINATIONS  # noqa: F401
from dlt_sources.common.destinations.ducklake import (  # noqa: F401
    get_ducklake_destination,
    ducklake_cianfhoghlaim_at_timestamp,
    ducklake_cianfhoghlaim_at_version,
    ducklake_cianfhoghlaim_table_changes,
)
from dlt_sources.common.destinations.motherduck import get_motherduck_destination  # noqa: F401
from dlt_sources.common.destinations.filesystem import get_filesystem_destination  # noqa: F401
from dlt_sources.common.destinations.iceberg import get_iceberg_destination  # noqa: F401

# === Original file content (preserved for archaeology) ===
# Original path: dlt_sources/common/named_destinations.py
# Original line count: 154
# Wave 4: replaced with re-export shim.
#
# The original implementation is preserved in git history at commit
# b8e7e18bd (before Wave 4) — use `git show b8e7e18bd:dlt_sources/common/named_destinations.py` to view.
