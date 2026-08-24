"""dlt_sources.cv.embedding — Wave 3 stub.

Per the Wave 1 dlt_sources restructure, the legacy
`dlt_sources.portfolio/cv.py` was renamed to `dlt_sources/cv/`.
This stub re-exports from `dlt_sources.media_personal` which has
the actual implementation.
"""
from __future__ import annotations
try:
    from cocoindex_flows.media_personal import *  # noqa: F401,F403
except ImportError:
    pass
