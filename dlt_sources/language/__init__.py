"""
dlt_sources.language — re-export shim.

The language/ package has been split into 3 themed
sub-packages per the
**2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec change:

- `dlt_sources.lexicographic/`
- `dlt_sources.cultural_heritage/`
- `dlt_sources.local_archive/`

This shim re-exports everything for backwards compatibility. New code
SHOULD import from the new sub-packages directly.
"""
from dlt_sources.lexicographic import *  # noqa: F401,F403
from dlt_sources.cultural_heritage import *  # noqa: F401,F403
from dlt_sources.local_archive import *  # noqa: F401,F403
