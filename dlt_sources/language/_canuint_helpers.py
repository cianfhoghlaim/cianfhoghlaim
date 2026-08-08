"""
Shared helpers split from celtic/canuint.py

Phase 3D of openspec change.
"""

from __future__ import annotations

# See the identical note in dlt_sources/language/_tearma_helpers.py:
# dlt_sources.common.http_client always fails (imports a nonexistent
# top-level `settings` module) — use the already-fixed _http_factories.py.
from dlt_sources.common._http_factories import canuint_client


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
