"""England cross-board comparator Dagster component.

Per the 2026-08-03-biep-v3-orchestration-components-partitions-sensors-v1 change.

Joins AQA + OCR + Edexcel for the same subject + qualification_level
and surfaces spec differences.
"""
from __future__ import annotations

import logging
from dagster import Component, ComponentLoadContext, Definitions

from .biep_subject_component import BIEPSubjectComponent

logger = logging.getLogger(__name__)


class EnglandCrossBoardComparatorComponent(BIEPSubjectComponent):
    """The canonical England cross-board comparator Component."""

    def __init__(self, subject_slug: str, qualification_level: str = "gcse"):
        super().__init__(jurisdiction="england")
        self.subject_slug = subject_slug
        self.qualification_level = qualification_level

    def build_defs(self, context: ComponentLoadContext) -> Definitions:
        logger.info(
            "EnglandCrossBoardComparatorComponent: england.cross_board.%s.%s",
            self.subject_slug, self.qualification_level,
        )
        return super().build_defs(context)


__all__ = ["EnglandCrossBoardComparatorComponent"]
