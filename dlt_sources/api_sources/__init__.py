"""
dlt_sources.api_sources — re-export shim.

The api_sources/ package has been split into 4 themed
sub-packages per the
**2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec change:

- `dlt_sources.api_documentation/`
- `dlt_sources.api_github/`
- `dlt_sources.api_local/`
- `dlt_sources.crypteolas_defi/`

This shim re-exports everything for backwards compatibility. New code
SHOULD import from the new sub-packages directly.
"""
from dlt_sources.api_documentation import *  # noqa: F401,F403
from dlt_sources.api_github import *  # noqa: F401,F403
from dlt_sources.api_local import *  # noqa: F401,F403
from dlt_sources.crypteolas_defi import *  # noqa: F401,F403
