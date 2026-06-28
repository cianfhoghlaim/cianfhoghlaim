"""
oideachais.dlt_sources.ie.education — Ireland education DLT sources.

Phase 3D of the openspec change re-organisation. Each sub-module in
this package is one DLT source per file (per the cross-domain-registry).
The per-source functions are re-exported at this package level for
backward compatibility with consumers that do
`from dlt_sources.ie.education import oide_source, ...`.
"""
from __future__ import annotations

# Convenience wrappers (from _examinations_helpers.py).
# Constants (from _examinations_helpers.py).
from dlt_sources.ie.education._examinations_helpers import (
    ALL_JC_SUBJECTS,
    ALL_LC_SUBJECTS,
    ALL_LCA_SUBJECTS,
    junior_cycle_exams_source,
    leaving_certificate_source,
    mathematics_exams_source,
    science_subjects_exams_source,
)
from dlt_sources.ie.education.agentic_discovery import agentic_discovery_source
from dlt_sources.ie.education.deep_research import deep_research_source
from dlt_sources.ie.education.exam_pdf_download import (
    exam_pdf_download_source,
)
from dlt_sources.ie.education.examinations import examinations_source

# Per-source re-exports (Phase 3D: one function per file at the canonical path).
# Each of these resolves to `dlt_sources.ie.education.<source_name>` (a file).
from dlt_sources.ie.education.oide import oide_source
from dlt_sources.ie.education.oide_all_subjects import oide_all_subjects_source
from dlt_sources.ie.education.oide_gaeilge import oide_gaeilge_source
from dlt_sources.ie.education.oide_subject import oide_subject_source
from dlt_sources.ie.education.pdf_download import pdf_download_source
from dlt_sources.ie.education.sec_examinations_browser import (
    sec_examinations_browser_source,
)

__all__ = [
    "ALL_JC_SUBJECTS",
    "ALL_LCA_SUBJECTS",
    "ALL_LC_SUBJECTS",
    "agentic_discovery_source",
    "deep_research_source",
    "exam_pdf_download_source",
    "examinations_source",
    "junior_cycle",
    "junior_cycle_exams_source",
    "leaving_certificate_source",
    "mathematics_exams_source",
    "oide_all_subjects_source",
    "oide_gaeilge_source",
    # Phase 3D per-source functions
    "oide_source",
    "oide_subject_source",
    "pdf_download_source",
    "science_subjects_exams_source",
    "sec_examinations_browser_source",
    # Subjects re-exports (lazy below)
    "subjects_base",
    "subjects_senior_cycle",
]
