"""
dlt_sources.media — re-export shim.

The media/ package has been split into 3 themed
sub-packages per the
**2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec change:

- `dlt_sources.media_text/`
- `dlt_sources.media_comics/`
- `dlt_sources.media_games/`

This shim re-exports everything for backwards compatibility. New code
SHOULD import from the new sub-packages directly.
"""
from dlt_sources.media_text import *  # noqa: F401,F403
from dlt_sources.media_comics import *  # noqa: F401,F403
from dlt_sources.media_games import *  # noqa: F401,F403
