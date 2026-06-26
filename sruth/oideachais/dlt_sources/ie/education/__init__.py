"""
oideachais.dlt_sources.ie.education — Ireland education DLT sources.

Phase 3D of the openspec change re-organisation. Each sub-module in
this package is one DLT source per file (per the cross-domain-registry).
The per-source functions are re-exported at this package level for
backward compatibility with consumers that do
`from dlt_sources.ie.education import oide_source, ...`.
"""
from __future__ import annotations

# Per-source re-exports (Phase 3D: one function per file at the canonical path).
# Each of these resolves to `dlt_sources.ie.education.<source_name>` (a file).
from dlt_sources.ie.education.oide import oide_source  # noqa: F401
from dlt_sources.ie.education.oide_subject import oide_subject_source  # noqa: F401
from dlt_sources.ie.education.oide_gaeilge import oide_gaeilge_source  # noqa: F401
from dlt_sources.ie.education.oide_all_subjects import oide_all_subjects_source  # noqa: F401
from dlt_sources.ie.education.examinations import examinations_source  # noqa: F401
from dlt_sources.ie.education.sec_examinations_browser import (  # noqa: F401
    sec_examinations_browser_source,
)
from dlt_sources.ie.education.pdf_download import pdf_download_source  # noqa: F401
from dlt_sources.ie.education.exam_pdf_download import (  # noqa: F401
    exam_pdf_download_source,
)
from dlt_sources.ie.education.agentic_discovery import agentic_discovery_source  # noqa: F401
from dlt_sources.ie.education.deep_research import deep_research_source  # noqa: F401

# Convenience wrappers (from _examinations_helpers.py).
from dlt_sources.ie.education._examinations_helpers import (  # noqa: F401
    leaving_certificate_source,
    junior_cycle_exams_source,
    mathematics_exams_source,
    science_subjects_exams_source,
)

# Constants (from _examinations_helpers.py).
from dlt_sources.ie.education._examinations_helpers import (  # noqa: F401
    ALL_JC_SUBJECTS,
    ALL_LC_SUBJECTS,
    ALL_LCA_SUBJECTS,
)


__all__ = [
    # Phase 3D per-source functions
    "oide_source",
    "oide_subject_source",
    "oide_gaeilge_source",
    "oide_all_subjects_source",
    "examinations_source",
    "sec_examinations_browser_source",
    "pdf_download_source",
    "exam_pdf_download_source",
    "agentic_discovery_source",
    "deep_research_source",
    "leaving_certificate_source",
    "junior_cycle_exams_source",
    "mathematics_exams_source",
    "science_subjects_exams_source",
    "ALL_JC_SUBJECTS",
    "ALL_LC_SUBJECTS",
    "ALL_LCA_SUBJECTS",
    # Subjects re-exports (lazy below)
    "subjects_base",
    "junior_cycle",
    "subjects_senior_cycle",
]