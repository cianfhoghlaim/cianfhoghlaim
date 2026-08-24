"""
dlt_sources.apple_photos — re-export shim.

The apple_photos/ package has been split into 1 themed
sub-packages per the
**2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec change:

- `dlt_sources.media_personal/`

This shim re-exports everything for backwards compatibility. New code
SHOULD import from the new sub-packages directly.
"""
from dlt_sources.media_personal import *  # noqa: F401,F403
