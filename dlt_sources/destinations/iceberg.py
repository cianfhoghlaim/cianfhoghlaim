"""dlt_sources.common.destinations.iceberg — Iceberg REST catalog (Lakekeeper :8181).

Per the **2026-08-24-wave-4-ducklake-v1-hardening-v1** openspec
change. Iceberg REST catalog interop lets external engines
(Spark, Trino, Snowflake, BigQuery) read the Cianfhoghlaim
DuckLake via the standard Iceberg REST spec.

Per `lakekeeper.io/docs`:

> "Lakekeeper is an open-source REST catalog for Apache Iceberg
>  and DuckLake. It provides OpenAPI-compatible endpoints that
>  any Iceberg client can use."

Per `ducklake.select/docs/stable/specification/catalog`:

> "DuckLake v1.0 supports Iceberg REST catalog interop via
>  METADATA_BACKEND=iceberg-rest."

The Lakekeeper deployment is documented in
`bonneagar/stacks/lakehouse/lakekeeper/`. The canonical catalog URL is
`http://lakekeeper:8181/catalog` (or external TLS endpoint in prod).

NOTE: This destination provides DuckLake→Iceberg interop. The
reverse (Iceberg→DuckLake) uses DuckLake's `iceberg_scan()` and is
out of scope.
"""
from __future__ import annotations

import os
from typing import Any, Optional

import dlt


# The canonical Lakekeeper Iceberg REST catalog URL.
DEFAULT_LAKEKEEPER_CATALOG: str = os.getenv(
    "CIANFHOGHLAIM_LAKEKEEPER_URI",
    "http://lakekeeper:8181/catalog",
)
"""The canonical Lakekeeper Iceberg REST catalog URI for the Cianfhoghlaim DuckLake."""


def get_iceberg_destination(
    catalog_uri: Optional[str] = None,
    warehouse: Optional[str] = None,
) -> Any:
    """Build the Iceberg REST catalog dlt destination.

    Args:
        catalog_uri: Lakekeeper Iceberg REST catalog URI.
            Default: `CIANFHOGHLAIM_LAKEKEEPER_URI` env var or
            `http://lakekeeper:8181/catalog`.
        warehouse: Iceberg warehouse location (where data files
            are stored). Default: the same S3 path as DuckLake
            (`s3://ducklake-cianfhoghlaim/iceberg/`).

    Returns:
        A `@dlt.destination`-decorated function configured for
        Iceberg REST catalog access via Lakekeeper.

    Reference: openspec/changes/2026-08-24-wave-4-ducklake-v1-hardening-v1/
    """
    catalog_uri = catalog_uri or DEFAULT_LAKEKEEPER_CATALOG
    warehouse = warehouse or os.getenv(
        "CIANFHOGHLAIM_ICEBERG_WAREHOUSE",
        "s3://ducklake-cianfhoghlaim/iceberg/",
    )

    @dlt.destination(
        credentials={
            "catalog_uri": catalog_uri,
            "warehouse": warehouse,
        },
        dest_name="iceberg",
    )
    def iceberg_cianfhoghlaim() -> Any:
        """Iceberg REST catalog destination via Lakekeeper.

        Provides cross-engine read access (Spark, Trino, Snowflake,
        BigQuery) to the Cianfhoghlaim DuckLake. The Lakekeeper
        deployment is in `bonneagar/stacks/lakehouse/lakekeeper/`.
        """
        return {
            "catalog_uri": catalog_uri,
            "warehouse": warehouse,
        }

    return iceberg_cianfhoghlaim


__all__ = [
    "DEFAULT_LAKEKEEPER_CATALOG",
    "get_iceberg_destination",
]
