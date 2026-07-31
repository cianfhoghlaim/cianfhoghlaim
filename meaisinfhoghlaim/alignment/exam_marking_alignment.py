"""UC 2: ExamMarkingAlignment — the canonical q_id join between ExamPaper and MarkingScheme.

Per the 2026-08-15-meaisinfoghlaim-ireland-england-roadmap (Plan 2, UC 2).

Outputs 1 row per (paper_code, q_id, mark_allocation_id) tuple to the
canonical meaisinfoghlaim.alignment.exam_marking_alignments table.

The join uses the BAML q_id field as the canonical key:
  - ExamPaper.q_id (from baml_src/british_isles/ireland/education/lc_extraction/exam_paper_layout.baml)
  - MarkingScheme.q_id (from baml_src/british_isles/ireland/education/lc_extraction/marking_scheme.baml)
  - MarkingScheme.mark_allocation_id (per-question mark allocation)

Each ExamMarkingAlignment row carries:
  - marks_awarded + marks_available (for the canonical marks consistency check)
  - alignment_confidence (0.0-1.0; how confident we are the q_ids match)
  - partial_credit_rule + common_mistake (for the regression summary)
  - related_lo_id (the canonical learning outcome linkage from ExamPaper)

Generalisable: the same join works for any (jurisdiction, stage, subject,
board, year) where BAML emits ExamPaper + MarkingScheme with consistent
q_id naming.
"""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Iterable

from meaisinfoghlaim.alignment.schema import (
    ExamMarkingAlignment,
)

logger = logging.getLogger(__name__)


class ExamMarkingAligner:
    """The canonical ExamPaper <-> MarkingScheme joiner.

    Stateless beyond an internal cache; reuse across cohorts.
    """

    def __init__(self, alignment_confidence_threshold: float = 0.7) -> None:
        """Configure the joiner.

        Args:
            alignment_confidence_threshold: minimum confidence for emitting
                an alignment row. Below this, the joiner logs a warning and
                drops the row. The BIEP v3 default is 0.7.
        """
        self.alignment_confidence_threshold = alignment_confidence_threshold

    async def align(
        self,
        exam_paper: dict[str, Any],
        marking_scheme: dict[str, Any],
        cohort_key: str,
    ) -> list[ExamMarkingAlignment]:
        """Join one ExamPaper + one MarkingScheme on q_id.

        Args:
            exam_paper: the canonical ExamPaper dict (from BAML ExtractExamPaperLayout)
            marking_scheme: the canonical MarkingScheme dict (from BAML ExtractMarkingSchemeGuideline)
            cohort_key: the canonical cohort key (e.g. 'ireland/lc/chemistry/2024/en')

        Returns:
            list of ExamMarkingAlignment rows (1 per q_id match).
        """
        # 1. Build the q_id -> marks_available map from the ExamPaper
        marks_available_by_qid: dict[str, int] = {}
        related_lo_by_qid: dict[str, str] = {}
        for question in exam_paper.get("questions", []):
            q_id = question.get("q_id")
            if not q_id:
                continue
            marks_available_by_qid[q_id] = int(question.get("marks", 0))
            if question.get("related_lo_id"):
                related_lo_by_qid[q_id] = question["related_lo_id"]

        # 2. Build the q_id -> mark_allocation map from the MarkingScheme
        allocations_by_qid: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for allocation in marking_scheme.get("mark_allocations", []):
            q_id = allocation.get("q_id")
            if not q_id:
                continue
            allocations_by_qid[q_id].append(allocation)

        # 3. Join + emit
        alignments: list[ExamMarkingAlignment] = []
        alignment_id_seed = f"{cohort_key}"
        idx = 0
        for q_id in sorted(set(marks_available_by_qid) | set(allocations_by_qid)):
            marks_available = marks_available_by_qid.get(q_id, 0)
            for allocation in allocations_by_qid.get(q_id, []):
                idx += 1
                confidence = self._compute_confidence(q_id, marks_available_by_qid, allocation)
                if confidence < self.alignment_confidence_threshold:
                    logger.warning(
                        "Skipping low-confidence alignment for q_id=%s (%.2f < %.2f)",
                        q_id, confidence, self.alignment_confidence_threshold,
                    )
                    continue
                alignment_id = f"align-{alignment_id_seed}-{idx}"
                try:
                    alignment = ExamMarkingAlignment(
                        alignment_id=alignment_id,
                        cohort_key=cohort_key,
                        paper_code=exam_paper.get("paper_code", "unknown"),
                        q_id=q_id,
                        mark_allocation_id=allocation.get("mark_allocation_id", f"alloc-{q_id}"),
                        marks_awarded=int(allocation.get("marks_awarded", 0)),
                        marks_available=marks_available,
                        alignment_confidence=confidence,
                        partial_credit_rule=allocation.get("partial_credit_rule"),
                        common_mistake=allocation.get("common_mistake"),
                        related_lo_id=related_lo_by_qid.get(q_id),
                    )
                    alignments.append(alignment)
                except Exception as exc:
                    logger.warning(
                        "Skipping alignment for q_id=%s due to validation error: %s",
                        q_id, exc,
                    )

        logger.info(
            "Aligned %d q_ids (cohort=%s, exam=%s, marking_scheme=%s)",
            len(alignments), cohort_key,
            exam_paper.get("paper_code", "unknown"),
            marking_scheme.get("paper_code", "unknown"),
        )
        return alignments

    def _compute_confidence(
        self,
        q_id: str,
        marks_available_by_qid: dict[str, int],
        allocation: dict[str, Any],
    ) -> float:
        """Compute the q_id match confidence (0.0-1.0).

        Heuristic:
          - 1.0 if q_id appears in BOTH marks_available_by_qid + allocation
          - 0.5 if q_id appears only in allocation
          - 0.0 if q_id appears only in marks_available_by_qid (no allocation)
        """
        if q_id in marks_available_by_qid and q_id in allocation.get("q_id", ""):
            return 1.0
        if q_id in allocation.get("q_id", ""):
            return 0.5
        return 0.0


__all__ = ["ExamMarkingAligner", "ExamMarkingAlignment"]
