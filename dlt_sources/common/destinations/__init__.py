"""dlt_sources.common.destinations — DEPRECATION SHIM.

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change (§1.1 + §1.2, master plan §3.2, §7.1). The canonical home for
the layer-grouped destinations is now
`dlt_sources.destinations` (top-level). This sub-package is preserved
as a re-export shim for at least one release cycle.

Legacy imports continue to work:

    from dlt_sources.common.destinations import named_destinations
    from dlt_sources.common.destinations.ducklake import get_ducklake_destination
    from dlt_sources.common.destinations.motherduck import get_motherduck_destination
    from dlt_sources.common.destinations.filesystem import get_filesystem_destination
    from dlt_sources.common.destinations.iceberg import get_iceberg_destination

New code SHOULD import from the top-level `dlt_sources.destinations`:

    from dlt_sources.destinations import named_destinations

Reference:
- Master plan §3.2 ("The canonical dlt_sources/ layout — Wave 1 target")
- Master plan §7.1 ("The dlt_sources/ migrations" — destinations split)
- openspec/changes/2026-08-24-wave-1-dlt-sources-domain-restructure-v1
"""
from __future__ import annotations

# Re-export everything from the canonical top-level locations so that
# every legacy import path resolves transparently.
from dlt_sources.destinations import (  # noqa: F401
    DESTINATIONS,
    DUCKLAKE_NAMESPACE,
    QUADRANT_METADATA_SCHEMAS,
    named_destinations,
)
from dlt_sources.destinations import _common as _common_shim  # noqa: F401
from dlt_sources.destinations import ducklake as _ducklake_shim  # noqa: F401
from dlt_sources.destinations import filesystem as _filesystem_shim  # noqa: F401
from dlt_sources.destinations import iceberg as _iceberg_shim  # noqa: F401
from dlt_sources.destinations import motherduck as _motherduck_shim  # noqa: F401

__all__ = [
    "DESTINATIONS",
    "DUCKLAKE_NAMESPACE",
    "QUADRANT_METADATA_SCHEMAS",
    "named_destinations",
]
