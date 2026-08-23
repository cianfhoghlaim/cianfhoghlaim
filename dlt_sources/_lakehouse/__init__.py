"""dlt_sources._lakehouse — DuckLake + MotherDuck + Local DuckDB destinations.

Reference: openspec/changes/2026-08-23-uog-official-docs-and-nui-superset-v1/
            specs/cianfhoghlaim-ducklake-tertiary/spec.md
"""

from .destinations import (
    DESTINATION_CHOICES,
    BonneagarLakehouseDestination,
    LakehouseConnectionError,
    LocalDuckLakeDestination,
    MotherDuckLakeDestination,
    get_destination,
)

__all__ = [
    "DESTINATION_CHOICES",
    "BonneagarLakehouseDestination",
    "LakehouseConnectionError",
    "LocalDuckLakeDestination",
    "MotherDuckLakeDestination",
    "get_destination",
]
