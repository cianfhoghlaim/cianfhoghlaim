"""dlt_sources/law/ireland/british_isles — DLT sources.

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change, this package was migrated from its legacy jurisdiction-first
location. The `__init__.py` re-exports the local source modules.

Legacy import paths still work via re-export shims at the old locations.
"""
from __future__ import annotations

from . import citizensinformation  # noqa: F401
from . import courts_ie  # noqa: F401
from . import doj  # noqa: F401
from . import gov_ie_law  # noqa: F401
from . import injuries_ie  # noqa: F401
from . import irish_statute_book  # noqa: F401
from . import lawreform  # noqa: F401
from . import workplace_relations  # noqa: F401

__all__ = ['citizensinformation', 'courts_ie', 'doj', 'gov_ie_law', 'injuries_ie', 'irish_statute_book', 'lawreform', 'workplace_relations']
