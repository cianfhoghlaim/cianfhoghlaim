"""
destinations_cianfhoghlaim — DEPRECATION SHIM (Wave 1 §1.2).

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change (§1.2, master plan §3.2, §7.1), this file is a re-export shim
for the layer-grouped destinations package
``dlt_sources.destinations`` (the canonical home at the TOP LEVEL of
the package — NOT under `dlt_sources.common.destinations`).

The single DuckLake namespace is ``ducklake_cianfhoghlaim`` (per
master plan §1.1). The 6 → 10 legacy namespace aliases all route to
this single consolidated namespace.

Legacy imports continue to work, but new code SHOULD import from:

    from dlt_sources.destinations import named_destinations

This shim is preserved for at least one release cycle per the
dlt_sources LEGACY_ALIASES.md precedent.
"""
from __future__ import annotations

# Re-export from the canonical top-level layer-grouped destinations package.
from dlt_sources.destinations import (  # noqa: F401
    DESTINATIONS,
    DUCKLAKE_NAMESPACE,
    QUADRANT_METADATA_SCHEMAS,
    named_destinations,
)
from dlt_sources.destinations.ducklake import (  # noqa: F401
    DEFAULT_POSTGRES_CATALOG,
    DEFAULT_GARAGE_S3_STORAGE,
    DUCKLAKE_NAME,
    get_ducklake_destination,
)

__all__ = [
    "DESTINATIONS",
    "DUCKLAKE_NAMESPACE",
    "QUADRANT_METADATA_SCHEMAS",
    "named_destinations",
    "DEFAULT_POSTGRES_CATALOG",
    "DEFAULT_GARAGE_S3_STORAGE",
    "DUCKLAKE_NAME",
    "get_ducklake_destination",
]
