"""dlt_sources/education/scotland/british_isles — DLT sources.

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change, this package was migrated from its legacy jurisdiction-first
location. The `__init__.py` re-exports the local source modules.

Legacy import paths still work via re-export shims at the old locations.
"""
from __future__ import annotations

from . import _curriculum_for_excellence_helpers  # noqa: F401
from . import curriculum_for_excellence  # noqa: F401
from . import gaelic_curriculum  # noqa: F401
from . import insight_benchmarking  # noqa: F401
from . import scotland_jurisdiction_pipeline  # noqa: F401
from . import sqa_qualifications  # noqa: F401

__all__ = ['_curriculum_for_excellence_helpers', 'curriculum_for_excellence', 'gaelic_curriculum', 'insight_benchmarking', 'scotland_jurisdiction_pipeline', 'sqa_qualifications']
