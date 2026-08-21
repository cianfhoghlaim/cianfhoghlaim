"""Shared DLT (Data Loading Tool) utilities for all sruth flows.

This module provides common DLT patterns, sources, and destinations
that can be reused across aleyum, crypteolas, oideachais, and other flows.
"""

from .sources import (
    BaseSource,
    BrowserSource,
    RESTSource,
)
from .destinations import (
    get_dlt_destination,
    get_iceberg_destination,
    get_duckdb_destination,
)

__all__ = [
    "BaseSource",
    "BrowserSource",
    "RESTSource",
    "get_dlt_destination",
    "get_iceberg_destination",
    "get_duckdb_destination",
]
