"""
DuckDB + DuckLake 1.0 schema helpers.

The 2026-04-13 launch of DuckLake 1.0 brought 2 new types into
DuckDB core (and therefore into DuckLake):

1. **GEOMETRY** — geospatial data with predicate-pushdown support.
   DuckLake uses file-level statistics to skip Parquet files that
   are guaranteed not to overlap the query polygon. See
   `motherduck.com/blog/announcing-ducklake-1-0-on-motherduck`.

2. **VARIANT** — a binary JSON type that supports automatic
   shredding. Filtering ``WHERE payload.user = 'alice'`` runs much
   faster than on raw JSON.

This module provides the dlt column-type helpers and the
Pydantic-compatible Python types so callers don't need to know
the dlt internals.
"""
from __future__ import annotations

from typing import Any


def geometry_column() -> dict[str, Any]:
    """Return a dlt column descriptor for a DuckDB GEOMETRY column.

    Use in `@dlt.resource(columns={...})`:

        @dlt.resource(columns={"boundary": geometry_column()})
        def boundaries():
            yield {"boundary": "POLYGON((...))"}
    """
    return {"data_type": "GEOMETRY"}


def variant_column() -> dict[str, Any]:
    """Return a dlt column descriptor for a DuckDB VARIANT column.

    Use in `@dlt.resource(columns={...})`:

        @dlt.resource(columns={"payload": variant_column()})
        def events():
            yield {"payload": {"user": "alice", "ts": "2024-01-01"}}
    """
    return {"data_type": "VARIANT"}


# Convenience aliases for the dlt column dict literal style.
GEOMETRY = geometry_column
VARIANT = variant_column
