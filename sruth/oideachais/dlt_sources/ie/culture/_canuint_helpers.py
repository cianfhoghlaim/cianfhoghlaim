"""
Shared helpers split from celtic/canuint.py

Phase 3D of openspec change.
"""

from __future__ import annotations
import re
from collections.abc import Iterator
import dlt
from bs4 import BeautifulSoup
from dlt.sources import DltResource
from observability.logging import get_logger
try:
    from shared.http import canuint_client  # noqa: F401
except ImportError:
    pass  # shared.http is unavailable; functions must lazy-import at call-time


CANUINT_BASE = "https://www.canuint.ie"

def _get_canuint_factory():
    """Get HTTP client factory for Canúint.ie."""
    return canuint_client()

def _safe_float(value: str | None) -> float | None:
    """Safely convert to float."""
    if value:
        try:
            return float(value)
        except ValueError:
            pass
    return None
