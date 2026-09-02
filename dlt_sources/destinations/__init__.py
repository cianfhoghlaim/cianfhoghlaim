"""dlt_sources.destinations — layer-grouped destinations (CANONICAL home).

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change (§1.1, master plan §3.2, §7.1). This package is the SINGLE
CANONICAL home for every destination factory in the Cianfhoghlaim
monorepo.

The layer-grouped destinations namespace replaces the 6 legacy
destinations files (`destinations_cianfhoghlaim.py`,
`destinations_tuatha.py`, `named_destinations.py`,
`destinations_personal_archive.py`, `lakehouse/destinations.py`,
`lakehouse/personal_archive_destinations.py`) with a single package
organised by INFRASTRUCTURE LAYER:

    dlt_sources/destinations/
    ├── __init__.py          # named_destinations() factory + re-exports
    ├── _common.py           # credential validation + namespace defaults
    ├── ducklake.py          # DuckLake + Postgres catalog + Garage S3
    ├── motherduck.py        # MotherDuck managed DuckLake
    ├── filesystem.py        # local FS + S3 + GCS + Azure
    └── iceberg.py           # Iceberg REST catalog via Lakekeeper (:8181)

The single namespace is `ducklake_cianfhoghlaim` (per master plan §1.1)
— the 6 → 10 legacy DuckLake namespaces are aliased to this single
canonical namespace.

New code SHOULD import from this top-level package:

    from dlt_sources.destinations import named_destinations
    d = named_destinations("ducklake_cianfhoghlaim")

The legacy import paths continue to work via the deprecation shims at:

- `dlt_sources.common.destinations` (re-exports this package)
- `dlt_sources.common.destinations_cianfhoghlaim` (re-exports this package)
- `dlt_sources.common.named_destinations` (re-exports this package)
- `dlt_sources.lakehouse.destinations` (re-exports this package)
- `dlt_sources.lakehouse.personal_archive_destinations` (re-exports this package)
"""
from __future__ import annotations

from typing import Any

from . import _common as _common_mod
from . import ducklake as _ducklake_mod
from . import filesystem as _filesystem_mod
from . import iceberg as _iceberg_mod
from . import motherduck as _motherduck_mod


# The canonical Cianfhoghlaim pattern (per the british-isles-education-pipeline
# BIEP v1 spec). DLT sources declare their destination by name; this
# factory resolves the name to a concrete `@dlt.destination` function
# at runtime.
#
# Per the Wave 4 master plan, the registry is the SINGLE SOURCE OF
# TRUTH for destination names. The 6 legacy namespaces
# (ducklake_oideachais, ducklake_educational, ducklake_crypteolas,
# ducklake_tertiary, ducklake_uog, ducklake_cie) are aliased to
# `ducklake_cianfhoghlaim` for backwards compatibility (Phase 5).
#
# Per the **2026-08-24-dlt-sources-to-multi-repo-scaffold-v1** §7.1
# change, the 5 per-quadrant registries
# (`ducklake_oideachais`, `ducklake_tuatha`, `ducklake_croilar`,
# `ducklake_agents`, `ducklake_media`) are exposed as well — they
# all wire through the canonical consolidated DuckLake namespace
# but with per-quadrant `metadata_schema` so each quadrant owns
# its own Postgres metadata schema inside the shared
# `md:cianfhoghlaim` catalog.
DESTINATIONS: dict[str, Any] = {
    # The canonical consolidated DuckLake namespace
    "ducklake_cianfhoghlaim": _ducklake_mod.get_ducklake_destination,
    # Per-quadrant registries (§7.1)
    "ducklake_oideachais_quadrant": _ducklake_mod.get_ducklake_destination_for_quadrant_oideachais,
    "ducklake_tuatha_quadrant": _ducklake_mod.get_ducklake_destination_for_quadrant_tuatha,
    "ducklake_croilar_quadrant": _ducklake_mod.get_ducklake_destination_for_quadrant_croilar,
    "ducklake_agents_quadrant": _ducklake_mod.get_ducklake_destination_for_quadrant_agents,
    "ducklake_media_quadrant": _ducklake_mod.get_ducklake_destination_for_quadrant_media,
    # Legacy aliases — all route to the consolidated namespace
    "ducklake_oideachais": _ducklake_mod.get_ducklake_destination,
    "ducklake_educational": _ducklake_mod.get_ducklake_destination,
    "ducklake_crypteolas": _ducklake_mod.get_ducklake_destination,
    "ducklake_tertiary": _ducklake_mod.get_ducklake_destination,
    "ducklake_uog": _ducklake_mod.get_ducklake_destination,
    "ducklake_cie": _ducklake_mod.get_ducklake_destination,
    # MotherDuck
    "motherduck": _motherduck_mod.get_motherduck_destination,
    "motherduck_ducklake": _motherduck_mod.get_motherduck_destination,
    # Filesystem (local + S3 + GCS + Azure)
    "filesystem_local": _filesystem_mod.get_filesystem_destination,
    "filesystem_s3": _filesystem_mod.get_filesystem_destination,
    "filesystem_gcs": _filesystem_mod.get_filesystem_destination,
    "filesystem_azure": _filesystem_mod.get_filesystem_destination,
    # Iceberg REST catalog (via Lakekeeper :8181)
    "iceberg_rest": _iceberg_mod.get_iceberg_destination,
    "iceberg_lakekeeper": _iceberg_mod.get_iceberg_destination,
}


def named_destinations(name: str) -> Any:
    """Resolve a destination name to a concrete dlt destination function.

    Usage:

        from dlt_sources.destinations import named_destinations

        @dlt.resource(
            name="mathematics_syllabus",
            write_disposition="merge",
            primary_key=["url"],
            destination=named_destinations("ducklake_cianfhoghlaim"),
        )
        def mathematics_syllabus(): ...

    Args:
        name: One of the keys in `DESTINATIONS` (e.g.
            `"ducklake_cianfhoghlaim"`, `"motherduck"`,
            `"filesystem_s3"`, `"iceberg_rest"`).

    Returns:
        A `@dlt.destination`-decorated function (callable) suitable
        for use as the `destination=` argument of a dlt resource or
        source.

    Raises:
        KeyError: If `name` is not in `DESTINATIONS`.

    Reference: openspec/changes/2026-08-24-wave-1-dlt-sources-domain-restructure-v1
    Reference: openspec/changes/2026-08-24-wave-4-ducklake-v1-hardening-v1
    """
    if name not in DESTINATIONS:
        raise KeyError(
            f"named_destinations: unknown destination name {name!r}. "
            f"Available: {sorted(DESTINATIONS.keys())}"
        )
    return DESTINATIONS[name]


__all__ = [
    "DESTINATIONS",
    "named_destinations",
    # Re-export from _common for convenience
    "DUCKLAKE_NAMESPACE",
    "QUADRANT_METADATA_SCHEMAS",
    "QUADRANT_TO_DUCKLAKE_KEY",
    "LEGACY_DUCKLAKE_NAMESPACE_ALIASES",
    "REQUIRED_ENV_VARS",
    "OPTIONAL_ENV_VARS",
    "validate_credentials",
]

# Re-export the canonical namespace constants + helpers from `_common`
# for downstream code that imports them from this package.
DUCKLAKE_NAMESPACE = _common_mod.DUCKLAKE_NAMESPACE
QUADRANT_METADATA_SCHEMAS = _common_mod.QUADRANT_METADATA_SCHEMAS
QUADRANT_TO_DUCKLAKE_KEY = _common_mod.QUADRANT_TO_DUCKLAKE_KEY
LEGACY_DUCKLAKE_NAMESPACE_ALIASES = _common_mod.LEGACY_DUCKLAKE_NAMESPACE_ALIASES
REQUIRED_ENV_VARS = _common_mod.REQUIRED_ENV_VARS
OPTIONAL_ENV_VARS = _common_mod.OPTIONAL_ENV_VARS
validate_credentials = _common_mod.validate_credentials
