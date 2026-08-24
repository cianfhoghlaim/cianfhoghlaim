
"""dlt_sources.cv — re-export shim.

Per Wave 1, the legacy `dlt_sources/portfolio/` was split into
`cv/`, `artwork/`, `labels/`. The CocoIndex App currently lives
in `media/cv_embedding.py`.

This module is a stub so the `defs.yaml` files at
`orchestration/defs/3_model_lifecycle/cocoindex_v1/cv_embedding/`
can load.
"""
from __future__ import annotations
try:
    from cocoindex_flows.media.cv_embedding import *  # noqa: F401,F403
except ImportError:
    pass
