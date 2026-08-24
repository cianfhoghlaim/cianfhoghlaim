"""british_isles._shared._lifespan — re-export shim.

Per the Wave 1 dlt_sources restructure, the legacy
`dlt_sources/british_isles/_shared/` was deleted. This shim
re-exports the canonical `cocoindex_flows._shared._lifespan` so
files like `british_isles/ireland/ie_law_*.py` (which use
`from ._shared._lifespan import EMBEDDER`) continue to work.
"""
from __future__ import annotations
from cocoindex_flows._shared._lifespan import *  # noqa: F401,F403

# LANCEDB_TABLE was defined in agent_registry.py originally — define
# a default value here so legacy `from ._shared._lifespan import
# LANCEDB_TABLE` imports continue to work.
LANCEDB_TABLE = "agent_registry"  # noqa: F811
