"""
dlt_sources.portfolio — re-export shim.

The portfolio/ package has been split into 3 themed
sub-packages per the
**2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec change:

- `dlt_sources.cv/`
- `dlt_sources.artwork/`
- `dlt_sources.labels/`

This shim re-exports everything for backwards compatibility. New code
SHOULD import from the new sub-packages directly.
"""
from dlt_sources.cv import *  # noqa: F401,F403
from dlt_sources.artwork import *  # noqa: F401,F403
from dlt_sources.labels import *  # noqa: F401,F403
