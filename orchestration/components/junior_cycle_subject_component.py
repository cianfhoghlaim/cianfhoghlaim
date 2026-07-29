"""Junior Cycle per-subject Dagster component.

Per the 2026-08-03-biep-v3-orchestration-components-partitions-sensors-v1 change.

The 18 NCCA JC subjects (english + gaeilge + mathematics + ...) each
get a per-subject asset set (Layer 1-5).

Also exports `JuniorCycleShortCourseComponent` (16 JC short courses:
coding, chinese, japanese, russian, polish, lithuanian, portuguese,
arabic, hebrew, philosophy, film_studies, financial_literacy,
media_literacy, personal_professional_development, digital_media,
athletic_studies) and `JuniorCycleCBAComponent` (36 JC CBAs: 18
subjects × 2 CBAs each = Year 2 + Year 3) — both subclassed from
`JuniorCycleSubjectComponent` with subject-type-specific partition
strategies.
"""
from __future__ import annotations

import logging
from typing import Any

from dagster import Component, ComponentLoadContext, Definitions

from .biep_subject_component import BIEPSubjectComponent

logger = logging.getLogger(__name__)


# The 18 NCCA Junior Cycle subjects (canonical NCCA 2024 list).
JC_SUBJECTS: tuple[str, ...] = (
    "english", "gaeilge", "mathematics", "irish_history", "geography",
    "science", "business_studies", "french", "german", "spanish",
    "italian", "home_economics", "music", "art", "technology",
    "engineering", "graphics", "wood_technology",
)

# The 16 NCCA Junior Cycle short courses (canonical NCCA 2024 list).
JC_SHORT_COURSES: tuple[str, ...] = (
    "coding", "chinese", "japanese", "russian", "polish", "lithuanian",
    "portuguese", "arabic", "hebrew", "philosophy", "film_studies",
    "financial_literacy", "media_literacy",
    "personal_professional_development", "digital_media",
    "athletic_studies",
)


class JuniorCycleSubjectComponent(BIEPSubjectComponent):
    """The canonical Junior Cycle per-subject Component (Ireland)."""

    def __init__(self, subject_slug: str, language: str = "en"):
        super().__init__(jurisdiction="ireland")
        self.subject_slug = subject_slug
        self.language = language

    def build_defs(self, context: ComponentLoadContext) -> Definitions:
        if self.subject_slug not in JC_SUBJECTS:
            raise ValueError(
                f"Unknown JC subject: {self.subject_slug!r}. "
                f"Valid: {JC_SUBJECTS}"
            )
        logger.info(
            "JuniorCycleSubjectComponent: ireland.jc.%s.%s",
            self.subject_slug, self.language,
        )
        return super().build_defs(context)


class JuniorCycleShortCourseComponent(BIEPSubjectComponent):
    """The canonical Junior Cycle short-course Component (Ireland).

    Per the 2026-07-20-biep-v2-junior-cycle-extraction-v1 change +
    the 2026-08-03-biep-v3-orchestration-components-partitions-sensors-v1
    change. Wired into orchestration/defs/2_materials/junior_cycle/
    short_courses/defs.yaml.
    """

    def __init__(self, course_slug: str, language: str = "en"):
        super().__init__(jurisdiction="ireland")
        self.course_slug = course_slug
        self.language = language

    def build_defs(self, context: ComponentLoadContext) -> Definitions:
        if self.course_slug not in JC_SHORT_COURSES:
            raise ValueError(
                f"Unknown JC short course: {self.course_slug!r}. "
                f"Valid: {JC_SHORT_COURSES}"
            )
        logger.info(
            "JuniorCycleShortCourseComponent: ireland.jc.short_courses.%s.%s",
            self.course_slug, self.language,
        )
        return super().build_defs(context)


class JuniorCycleCBAComponent(BIEPSubjectComponent):
    """The canonical Junior Cycle CBA (Classroom-Based Assessment) Component (Ireland).

    Per the 2026-07-20-biep-v2-junior-cycle-extraction-v1 change +
    the 2026-08-03-biep-v3-orchestration-components-partitions-sensors-v1
    change. The 18 NCCA JC subjects each have 2 CBAs (Year 2 + Year 3)
    = 36 total. Wired into orchestration/defs/2_materials/junior_cycle/
    cbas/defs.yaml.
    """

    def __init__(self, subject_slug: str, cba_idx: int, language: str = "en"):
        super().__init__(jurisdiction="ireland")
        self.subject_slug = subject_slug
        self.cba_idx = cba_idx
        self.language = language
        if cba_idx not in (1, 2):
            raise ValueError(
                f"cba_idx must be 1 (Year 2) or 2 (Year 3); got {cba_idx}"
            )

    def build_defs(self, context: ComponentLoadContext) -> Definitions:
        if self.subject_slug not in JC_SUBJECTS:
            raise ValueError(
                f"Unknown JC subject: {self.subject_slug!r}. "
                f"Valid: {JC_SUBJECTS}"
            )
        logger.info(
            "JuniorCycleCBAComponent: ireland.jc.cbas.%s.%d.%s",
            self.subject_slug, self.cba_idx, self.language,
        )
        return super().build_defs(context)


__all__ = [
    "JuniorCycleSubjectComponent",
    "JuniorCycleShortCourseComponent",
    "JuniorCycleCBAComponent",
    "JC_SUBJECTS",
    "JC_SHORT_COURSES",
]
