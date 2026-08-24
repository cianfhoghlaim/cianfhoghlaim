"""british_isles._shared — re-export shim.

The legacy `dlt_sources/british_isles/_shared/` (which existed before
the Wave 1 dlt_sources restructure) was deleted. This shim re-exports
from `cocoindex_flows._shared/` so the legacy `from ...british_isles._shared.X`
imports continue to work.
"""
from cocoindex_flows._shared import *  # noqa: F401,F403
