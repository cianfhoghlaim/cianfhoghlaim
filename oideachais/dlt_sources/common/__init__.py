"""Common utilities and constants for DLT sources.

Also installs a `sys.modules` alias for the missing `shared` package
so that every `from shared.http import …` line in the legacy DLT
sources keeps working. The alias is a *re-export* of the in-tree
`oideachais.dlt_sources.common._http_factories` module — see that
file for the contract.
"""

# Install the `shared` alias *before* importing the other sub-modules
# so any DLT source that does `from shared.http import …` resolves.
import sys as _sys
import types as _types
from oideachais.dlt_sources.common import _http_factories as _http_factories
from oideachais.dlt_sources.common import _shared_utils_stub as _shared_utils_stub

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
    # Firecrawl utilities
    "create_firecrawl_source",
    "crawl_website",
    "scrape_page",
    "map_urls",
    "get_firecrawl_client",
    # Incremental loading utilities
    "compute_content_hash",
    "make_deduplication_key",
    "with_change_detection",
    "IncrementalCrawlState",
    "create_incremental_resource",
    "add_curriculum_metadata",
    "get_equivalent_levels",
    "LEVEL_EQUIVALENCES",
]
