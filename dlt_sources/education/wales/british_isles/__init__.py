"""dlt_sources/education/wales/british_isles — DLT sources.

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change, this package was migrated from its legacy jurisdiction-first
location. The `__init__.py` re-exports the local source modules.

Legacy import paths still work via re-export shims at the old locations.
"""
from __future__ import annotations

from . import _curriculum_for_wales_helpers  # noqa: F401
from . import curriculum_for_wales  # noqa: F401
from . import estyn  # noqa: F401
from . import wales_jurisdiction_pipeline  # noqa: F401
from . import welsh_medium  # noqa: F401
from . import wjec_qualifications  # noqa: F401

__all__ = ['_curriculum_for_wales_helpers', 'curriculum_for_wales', 'estyn', 'wales_jurisdiction_pipeline', 'welsh_medium', 'wjec_qualifications']
