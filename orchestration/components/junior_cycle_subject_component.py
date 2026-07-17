"""Junior Cycle per-subject Dagster component.

Per the 2026-08-03-biep-v3-orchestration-components-partitions-sensors-v1 change.

The 18 NCCA JC subjects (english + gaeilge + mathematics + ...) each
get a per-subject asset set (Layer 1-5).
"""
from __future__ import annotations

import logging
from typing import Any

from dagster import Component, ComponentLoadContext, Definitions

from .biep_subject_component import BIEPSubjectComponent

logger = logging.getLogger(__name__)


class JuniorCycleSubjectComponent(BIEPSubjectComponent):
    """The canonical Junior Cycle per-subject Component (Ireland)."""

    def __init__(self, subject_slug: str, language: str = "en"):
        super().__init__(jurisdiction="ireland")
        self.subject_slug = subject_slug
        self.language = language

    def build_defs(self, context: ComponentLoadContext) -> Definitions:
        if not self._validate_subject(self.subject_slug):
            raise ValueError(f"Unknown JC subject: {self.subject_slug!r}")
        logger.info(
            "JuniorCycleSubjectComponent: ireland.jc.%s.%s",
            self.subject_slug, self.language,
        )
        return super().build_defs(context)

    @staticmethod
    def _validate_subject(subject: str) -> bool:
        valid = (
            "english", "gaeilge", "mathematics", "irish_history", "geography",
            "science", "business_studies", "french", "german", "spanish",
            "italian", "home_economics", "music", "art", "technology",
            "engineering", "graphics", "wood_technology",
        )
        return subject in valid


__all__ = ["JuniorCycleSubjectComponent"]
