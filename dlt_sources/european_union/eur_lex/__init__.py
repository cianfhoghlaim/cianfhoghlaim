"""dlt_sources/european_union/eur_lex — DLT sources.

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change, this package was migrated from its legacy jurisdiction-first
location. The `__init__.py` re-exports the local source modules.

Legacy import paths still work via re-export shims at the old locations.
"""
from __future__ import annotations

from . import cjeu_case_law  # noqa: F401
from . import decisions  # noqa: F401
from . import directives  # noqa: F401
from . import regulations  # noqa: F401
from . import treaties  # noqa: F401

__all__ = ['cjeu_case_law', 'decisions', 'directives', 'regulations', 'treaties']
