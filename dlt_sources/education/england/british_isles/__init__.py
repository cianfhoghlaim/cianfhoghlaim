"""dlt_sources/education/england/british_isles — DLT sources.

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change, this package was migrated from its legacy jurisdiction-first
location. The `__init__.py` re-exports the local source modules.

Legacy import paths still work via re-export shims at the old locations.
"""
from __future__ import annotations

from . import _national_curriculum_helpers  # noqa: F401
from . import all_exam_boards  # noqa: F401
from . import aqa_qualifications  # noqa: F401
from . import edexcel_qualifications  # noqa: F401
from . import england_jurisdiction_pipeline  # noqa: F401
from . import national_curriculum  # noqa: F401
from . import ocr_qualifications  # noqa: F401
from . import ofsted  # noqa: F401
from . import school_info  # noqa: F401

__all__ = ['_national_curriculum_helpers', 'all_exam_boards', 'aqa_qualifications', 'edexcel_qualifications', 'england_jurisdiction_pipeline', 'national_curriculum', 'ocr_qualifications', 'ofsted', 'school_info']
