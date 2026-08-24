"""dlt_sources.education.tertiary — 3rd-level / university education.

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change, this package contains the per-institution tertiary (3rd-level /
university) education sources. The University of Galway (UoG) is the
FIRST tertiary example, per the master refactor plan's Wave 2.

Per-institution sub-packages:

- `uog/exam_papers/` — VLM-extracted exam papers
- `uog/personal_archive/` — student assignments + notes + transcripts
- `uog/official_docs/` — module pages + faculty pages + research outputs
- `uog/students_union/` — events + society pages + club content
- `nui_federation/` — multi-institution NUI federation (UoG, UCD, UCC, NUIM)
- `british_isles/` — UK + IE universities (cross-tertiary)
"""
from __future__ import annotations
