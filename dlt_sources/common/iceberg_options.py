"""Iceberg write path helpers.

Per the 2026-08-07-biep-v3-hardening-v1 change.

The canonical destination factory at
dlt/common/destinations_cianfhoghlaim.py currently exposes only
DuckLake + plain DuckDB writes. This module adds the parallel
Iceberg write path (for tiering to a hot/warm/cold strategy).
"""
from __future__ import annotations

from typing import Any

import dlt


def build_iceberg_local_destination(
    namespace: str = "cianfhoghlaim",
    catalog_uri: str = "http://localhost:8181",
    warehouse: str = "s3://garage/iceberg/",
) -> Any:
    """Build the canonical local Iceberg destination via dlt."""
    return dlt.destinations.iceberg(
        credentials={
            "uri": catalog_uri,
            "warehouse": warehouse,
            "namespace": namespace,
        },
    )


__all__ = ["build_iceberg_local_destination"]
