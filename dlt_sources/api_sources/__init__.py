"""`dlt_sources.api_sources` — re-export shim.

The original
**2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec change
proposed splitting this package into 4 themed sub-packages
(`api_documentation/`, `api_github/`, `api_local/`, `crypteolas_defi/`).
That change did NOT land — only `crypteolas_defi/` was carved out. The
other three sub-packages never existed on disk.

Per the Phase 3 closure (the `cianchosaint-fail-subtree-fixes-2026-08-25`
sub-batch of `2026-08-24-dlt-sources-to-multi-repo-scaffold-v1`):
- The `api_documentation/`, `api_github/`, and `api_local/` re-exports
  are REMOVED (the sub-packages don't exist).
- The `crypteolas_defi/` re-export is KEPT (it's a real sibling
  package; the cross-cut makes sense).
- Individual API source files (`github.py`, `linkedin.py`, etc.) live
  in this directory and can still be imported lazily via
  `dlt_sources.api_sources.<module>` (each has its own independent
  set of broken `from pipelines.*` and `from _shared.config.*`
  imports that are out of scope for this Phase 3 cleanup — see the
  post-fix report §B "Open follow-ups").

New code SHOULD import from the per-source modules directly.
"""
from dlt_sources.crypteolas_defi import *  # noqa: F401,F403
