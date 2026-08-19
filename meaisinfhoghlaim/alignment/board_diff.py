"""UC 6: BoardDiff (AQA vs OCR vs Edexcel).

Per the 2026-08-15-meaisinfoghlaim-ireland-england-roadmap (Plan 3, UC 6).

The canonical England-board differential: takes 3 board extractions
(AQA + OCR + Edexcel) of the same (subject, level) and emits structural
diffs (added modules, removed modules, content_hash_changed).

Generalisable to Northern Ireland (CCEA vs WJEC) + Scotland (SQA vs
private boards) later.
"""

from __future__ import annotations

import logging
from typing import Any

from meaisinfhoghlaim.alignment.schema import (
    Board,
    BoardDiff,
)

logger = logging.getLogger(__name__)


class BoardDiffer:
    """The canonical England-board differ."""

    def __init__(self) -> None:
        pass

    def diff(
        self,
        board_a: Board,
        board_a_syllabus: dict[str, Any],
        board_b: Board,
        board_b_syllabus: dict[str, Any],
        cohort_key: str,
    ) -> BoardDiff:
        """Diff 2 board extractions of the same (subject, level).

        Args:
            board_a: the first board (e.g. AQA)
            board_a_syllabus: the BAML ExtractUKQualSpec output for board_a
            board_b: the second board (e.g. OCR)
            board_b_syllabus: the BAML ExtractUKQualSpec output for board_b
            cohort_key: the canonical cohort key (e.g. 'england/gcse/chemistry/2024')

        Returns:
            BoardDiff with added/removed modules + content_changed flag
        """
        import uuid as _uuid
        from datetime import datetime as _dt
        from datetime import timezone as _tz
        import hashlib
        import json

        def _syllabus_hash(syllabus: dict) -> str:
            """Stable hash of the syllabus canonical form."""
            # Sort keys for determinism
            return hashlib.sha256(
                json.dumps(syllabus, sort_keys=True, default=str).encode("utf-8")
            ).hexdigest()

        hash_a = _syllabus_hash(board_a_syllabus)
        hash_b = _syllabus_hash(board_b_syllabus)

        # Find the module list per board
        modules_a = {
            m.get("module_id")
            for m in board_a_syllabus.get("modules", [])
            if m.get("module_id")
        }
        modules_b = {
            m.get("module_id")
            for m in board_b_syllabus.get("modules", [])
            if m.get("module_id")
        }
        added = sorted(modules_b - modules_a)
        removed = sorted(modules_a - modules_b)

        return BoardDiff(
            diff_id=str(_uuid.uuid4()),
            cohort_key=cohort_key,
            board_a=board_a,
            board_b=board_b,
            syllabus_hash_a=hash_a,
            syllabus_hash_b=hash_b,
            content_changed=(hash_a != hash_b),
            added_modules=added,
            removed_modules=removed,
        )


__all__ = ["BoardDiffer", "BoardDiff", "Board"]
