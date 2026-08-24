"""
dlt_sources.crypteolas — re-export shim.

The crypteolas/ package has been split into 3 themed
sub-packages per the
**2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec change:

- `dlt_sources.crypteolas_chain/`
- `dlt_sources.crypteolas_docs/`
- `dlt_sources.crypteolas_defi/`

This shim re-exports everything for backwards compatibility. New code
SHOULD import from the new sub-packages directly.
"""
from dlt_sources.crypteolas_chain import *  # noqa: F401,F403
from dlt_sources.crypteolas_docs import *  # noqa: F401,F403
from dlt_sources.crypteolas_defi import *  # noqa: F401,F403
