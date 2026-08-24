
"""dlt_sources.media_personal — re-export shim.

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change, the legacy `dlt_sources/apple_photos/` was renamed to
`dlt_sources/media_personal/`. The corresponding CocoIndex Apps are
temporarily split between `media/apple_photos_chunks.py` and
`media/apple_photos_metadata.py`; they will be re-exported from here
once Wave 3 lands.

This module is a stub so the `defs.yaml` files at
`orchestration/defs/3_model_lifecycle/cocoindex_v1/apple_photos_*/`
can load.
"""
from __future__ import annotations
try:
    from cocoindex_flows.media.apple_photos_chunks import *  # noqa: F401,F403
except ImportError:
    pass
try:
    from cocoindex_flows.media.apple_photos_metadata import *  # noqa: F401,F403
except ImportError:
    pass
try:
    from cocoindex_flows.media.apple_photos_geospatial import *  # noqa: F401,F403
except ImportError:
    pass
