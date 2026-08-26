"""dlt_sources.common.destinations — layer-grouped destinations.

Per the **2026-08-24-wave-4-ducklake-v1-hardening-v1** openspec
change. The layer-grouped destinations namespace replaces the
6 legacy destinations files (`destinations_cianfhoghlaim.py`,
`destinations_tuatha.py`, `named_destinations.py`, etc.) with a
single package organised by INFRASTRUCTURE LAYER:

    dlt_sources/common/destinations/
    ├── __init__.py          # named_destinations() factory + re-exports
    ├── ducklake.py           # DuckLake + Postgres catalog + Garage S3
    ├── motherduck.py         # MotherDuck managed DuckLake
    ├── filesystem.py         # local FS + S3 + GCS + Azure
    └── iceberg.py            # Iceberg REST catalog via Lakekeeper (:8181)

The 6 legacy destinations files become thin re-export shims (Phase 3
of the openspec change). New code SHOULD import from this package:

    from dlt_sources.common.destinations import named_destinations
    d = named_destinations("ducklake_cianfhoghlaim")

The legacy import paths (`from dlt_sources.common.destinations_cianfhoghlaim
import ...`) continue to work via the shims.
"""
from __future__ import annotations

from typing import Any

from dlt_sources.common.destinations import ducklake as _ducklake_mod
from dlt_sources.common.destinations import filesystem as _filesystem_mod
from dlt_sources.common.destinations import iceberg as _iceberg_mod
from dlt_sources.common.destinations import motherduck as _motherduck_mod


# The canonical KCG pattern (per the british-isles-education-pipeline
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

        from dlt_sources.common.destinations import named_destinations

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

    Reference: openspec/changes/2026-08-24-wave-4-ducklake-v1-hardening-v1
    """
    if name not in DESTINATIONS:
        raise KeyError(
            f"named_destinations: unknown destination name {name!r}. "
            f"Available: {sorted(DESTINATIONS.keys())}"
        )
    return DESTINATIONS[name]


__all__ = ["DESTINATIONS", "named_destinations"]
