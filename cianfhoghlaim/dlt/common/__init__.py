"""Common utilities and constants for DLT sources.

Also installs a `sys.modules` alias for the missing `shared` package
so that every `from shared.http import …` line in the legacy DLT
sources keeps working. The alias is a *re-export* of the in-tree
`oideachais.cianfhoghlaim.dlt.common._http_factories` module — see that
file for the contract.
"""

# Install the `shared` alias *before* importing the other sub-modules
# so any DLT source that does `from shared.http import …` resolves.
import sys as _sys
import types as _types

from cianfhoghlaim.dlt.common import _http_factories as _http_factories
from cianfhoghlaim.dlt.common import _shared_utils_stub as _shared_utils_stub

# shared package root
if "shared" not in _sys.modules:
    _pkg = _types.ModuleType("shared")
    _pkg.__path__ = []  # type: ignore[attr-defined]
    _sys.modules["shared"] = _pkg

# shared.http — re-export of _http_factories
_sys.modules.setdefault("shared.http", _http_factories)
_sys.modules.setdefault("shared.utils", _shared_utils_stub)

from .firecrawl_source import (
    crawl_website,
    create_firecrawl_source,
    get_firecrawl_client,
    map_urls,
    scrape_page,
)
from .incremental import (
    LEVEL_EQUIVALENCES,
    IncrementalCrawlState,
    add_curriculum_metadata,
    compute_content_hash,
    create_incremental_resource,
    get_equivalent_levels,
    make_deduplication_key,
    with_change_detection,
)

__all__ = [
    "LEVEL_EQUIVALENCES",
    "IncrementalCrawlState",
    "add_curriculum_metadata",
    # Incremental loading utilities
    "compute_content_hash",
    "crawl_website",
    # Firecrawl utilities
    "create_firecrawl_source",
    "create_incremental_resource",
    "get_equivalent_levels",
    "get_firecrawl_client",
    "make_deduplication_key",
    "map_urls",
    "scrape_page",
    "with_change_detection",
]
