"""
API Routes for Celtic Education Platform.

Available routers:
- search: Semantic search endpoints
- geospatial: Map data and spatial queries
"""
from __future__ import annotations

from . import geospatial, search

__all__ = [
    "search",
    "geospatial",
]
