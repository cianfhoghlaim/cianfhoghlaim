"""
dlt_sources.filesystem — re-export shim.

The filesystem/ package has been split into 1 themed
sub-packages per the
**2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec change:

- `dlt_sources.raw_files/`

This shim re-exports everything for backwards compatibility. New code
SHOULD import from the new sub-packages directly.
"""
from dlt_sources.raw_files import *  # noqa: F401,F403
