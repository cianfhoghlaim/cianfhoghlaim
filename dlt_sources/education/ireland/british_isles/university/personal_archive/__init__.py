"""dlt_sources.british_isles.ireland.education.university.personal_archive

The transferable factory for the personal-archive pipeline. The
same code runs against any student's `leabharlann/<university>/`
corpus — parameterised on the 9 fields of
`UniversityPersonalArchiveConfig` (a Pydantic v2 BaseModel).

Reference: openspec/changes/2026-08-23-uog-personal-archive-tertiary-modules-v1/
            specs/cianfhoghlaim-personal-archive-typed-modules/spec.md
"""

from .uog_personal_archive_source import (
    UniversityPersonalArchiveConfig,
    personal_archive_source,
    uog_personal_archive_case_study,
)

__all__ = [
    "UniversityPersonalArchiveConfig",
    "personal_archive_source",
    "uog_personal_archive_case_study",
]
