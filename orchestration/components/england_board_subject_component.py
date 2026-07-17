"""England per-board per-subject Dagster component.

Per the 2026-08-03-biep-v3-orchestration-components-partitions-sensors-v1 change.
"""
from __future__ import annotations

import logging
from dagster import Component, ComponentLoadContext, Definitions

from .biep_subject_component import BIEPSubjectComponent

logger = logging.getLogger(__name__)


class EnglandBoardSubjectComponent(BIEPSubjectComponent):
    """The canonical England per-board (AQA / OCR / Edexcel) per-subject Component."""

    def __init__(self, exam_board: str, subject_slug: str, qualification_level: str = "gcse"):
        super().__init__(jurisdiction="england")
        self.exam_board = exam_board
        self.subject_slug = subject_slug
        self.qualification_level = qualification_level

    def build_defs(self, context: ComponentLoadContext) -> Definitions:
        if self.exam_board not in ("aqa", "ocr", "edexcel"):
            raise ValueError(f"Unknown exam board: {self.exam_board!r}")
        logger.info(
            "EnglandBoardSubjectComponent: england.%s.%s.%s",
            self.exam_board, self.qualification_level, self.subject_slug,
        )
        return super().build_defs(context)


__all__ = ["EnglandBoardSubjectComponent"]
