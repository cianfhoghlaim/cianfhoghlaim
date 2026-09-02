"""dlt_sources.common.destinations.motherduck — MotherDuck managed DuckLake.

Per the **2026-08-24-wave-4-ducklake-v1-hardening-v1** openspec
change. MotherDuck hosts the same DuckLake v1.0 format but in their
managed cloud.

Per `dlthub.com/docs/dlt-ecosystem/destinations/motherduck`:

> "MotherDuck is a managed DuckDB-in-the-cloud service. It can be
>  used as a destination for dlt pipelines via the `motherduck`
>  destination name."

Per `motherduck.com/blog/announcing-ducklake-1-0-on-motherduck`:

> "DuckLake v1.0 is available on MotherDuck with full support for
>  data inlining, snapshot/rollback, and the new Lakehouse catalog."

The `CIANFHOGHLAIM_MOTHERDUCK_TOKEN` env var must be set for the
MotherDuck destination to authenticate. Wire-up is part of a Wave 4
follow-up PR.
"""
from __future__ import annotations

import os
from typing import Any, Optional

import dlt


# The canonical MotherDuck database for the Cianfhoghlaim platform.
# Per the Wave 4 master plan, this is the SAME namespace as the local
# DuckLake (`cianfhoghlaim`) — MotherDuck and the local Postgres-backed
# DuckLake share the same logical database name so queries are
# interchangeable.
DEFAULT_MOTHERDUCK_DATABASE: str = os.getenv(
    "CIANFHOGHLAIM_MOTHERDUCK_DB",
    "md:cianfhoghlaim",
)
"""The canonical MotherDuck database for the Cianfhoghlaim DuckLake."""


def get_motherduck_destination(
    database: Optional[str] = None,
    token: Optional[str] = None,
) -> Any:
    """Build the MotherDuck-managed DuckLake dlt destination.

    Args:
        database: MotherDuck database name. Default: `md:cianfhoghlaim`.
        token: MotherDuck auth token. Default: `CIANFHOGHLAIM_MOTHERDUCK_TOKEN`
            env var. **Required** — if missing, raises RuntimeError at
            dlt pipeline construction time.

    Returns:
        A `@dlt.destination`-decorated function configured for
        MotherDuck DuckLake.

    Raises:
        RuntimeError: If `token` is missing.

    Reference: openspec/changes/2026-08-24-wave-4-ducklake-v1-hardening-v1/
    """
    database = database or DEFAULT_MOTHERDUCK_DATABASE
    token = token or os.getenv("CIANFHOGHLAIM_MOTHERDUCK_TOKEN")

    if not token:
        raise RuntimeError(
            "motherduck_destination: CIANFHOGHLAIM_MOTHERDUCK_TOKEN env var "
            "is not set. Wire-up is part of a Wave 4 follow-up PR; "
            "see openspec/changes/2026-08-24-wave-4-ducklake-v1-hardening-v1/"
        )

    @dlt.destination(
        credentials={
            "database": database,
            "token": token,
        },
        dest_name="motherduck",
    )
    def motherduck_cianfhoghlaim() -> Any:
        """MotherDuck-managed DuckLake destination.

        Per the master plan, the MotherDuck token wire-up lands in a
        follow-up PR. Until then, the destination factory raises
        RuntimeError at construction time.
        """
        return {
            "database": database,
            "token": token,
        }

    return motherduck_cianfhoghlaim


__all__ = [
    "DEFAULT_MOTHERDUCK_DATABASE",
    "get_motherduck_destination",
]
