
"""dlt_sources.cultural_heritage — re-export shim.

Per Wave 1, the legacy `dlt_sources/language/` was split into
`lexicographic/`, `cultural_heritage/`, and `local_archive/`.
The CocoIndex Apps currently live in `portfolio/culture_heritage_embedding.py`
and `celtic/mythology_embedding.py`.

This module is a stub so the `defs.yaml` files at
`orchestration/defs/3_model_lifecycle/cocoindex_v1/culture_heritage_embedding/`
and `mythology_embedding/` can load.

The `heritage_embedding.py` import is commented out — it uses
`@coco.App(...)` decorator (the older v1 API) which crashes on import.
The defs.yaml files only need `culture_heritage_embedding` and
`celtic_mythology_embedding`.
"""
from __future__ import annotations
try:
    from cocoindex_flows.portfolio.culture_heritage_embedding import *  # noqa: F401,F403
except ImportError:
    pass
try:
    from cocoindex_flows.celtic.mythology_embedding import *  # noqa: F401,F403
except ImportError:
    pass
# heritage_embedding.py uses the deprecated @coco.App(...) decorator
# pattern; it's intentionally NOT re-exported here. See the Wave 3 spec.
# try:
#     from cocoindex_flows.portfolio.heritage_embedding import *  # noqa: F401,F403
# except ImportError:
#     pass
