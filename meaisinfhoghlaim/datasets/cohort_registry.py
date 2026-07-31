"""Canonical per-cohort registry (Plan 4).

Per the 2026-08-15-meaisinfoghlaim-ireland-england-roadmap (Plan 4).

1 row per (jurisdiction, stage, subject, board, language, year) tuple.
Bilingual-aware (per Plan 2 extension): tracks which languages have been
extracted for the cohort via the ``language_pair`` dimension + the
``en_extracted`` / ``ga_extracted`` flags.

Generalisable: same registry works for Scotland / Wales / NI / Jersey /
Guernsey / IoM rollouts.

Storage:
  - In-memory: ``_cohorts`` dict keyed by ``cohort_id``
  - On disk: ``stedding/education/cohort_registry/`` as JSON files (1 per
    jurisdiction; named ``<jurisdiction>.json``)
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from meaisinfoghlaim.alignment.schema import (
    Board,
    CohortLifecycleState,
    CohortRow,
    LanguagePair,
    QualificationLevel,
)

logger = logging.getLogger(__name__)


# Canonical on-disk root for the cohort registry JSON files.
COHORT_REGISTRY_ROOT = Path(
    os.environ.get(
        "CIANFHOGHLAIM_COHORT_REGISTRY_ROOT",
        "stedding/education/cohort_registry",
    )
)


class CohortRegistry:
    """The canonical per-cohort registry.

    1 row per (jurisdiction, stage, subject, board, language, year) tuple.
    Tracks lifecycle state + bilingual extraction status + the v3 milestone
    expected_extractions count.
    """

    def __init__(self, root=None) -> None:
        self.root = Path(root) if root is not None else COHORT_REGISTRY_ROOT
        self.root.mkdir(parents=True, exist_ok=True)
        self._cache: dict = {}

    @staticmethod
    def _cohort_key(jurisdiction, stage, subject, board, language, year) -> tuple:
        """Build the canonical cohort key tuple."""
        return (jurisdiction, stage.value if isinstance(stage, QualificationLevel) else stage,
                subject, board.value if isinstance(board, Board) else board,
                language, year)

    def path_for(self, jurisdiction: str) -> Path:
        return self.root / f"{jurisdiction}.json"

    def get(self, cohort_id: str) -> CohortRow | None:
        """Get a cohort by ID."""
        return self._cache.get(cohort_id)

    def get_by_key(
        self,
        jurisdiction: str,
        stage: QualificationLevel | str,
        subject: str,
        board: Board | str = Board.NONE,
        language: str = "en",
        year: int = 2026,
    ) -> CohortRow | None:
        """Get a cohort by its canonical key tuple."""
        key = self._cohort_key(jurisdiction, stage, subject, board, language, year)
        for cohort in self._cache.values():
            if self._cohort_key(
                cohort.jurisdiction, cohort.stage, cohort.subject,
                cohort.board, cohort.language, cohort.year,
            ) == key:
                return cohort
        return None

    def all(self, jurisdiction: str | None = None) -> list:
        """Return all cohorts (optionally filtered by jurisdiction)."""
        if jurisdiction is None:
            return list(self._cache.values())
        return [
            c for c in self._cache.values()
            if c.jurisdiction == jurisdiction
        ]

    def upsert(self, cohort: CohortRow) -> None:
        """Insert or update a cohort row."""
        self._cache[cohort.cohort_id] = cohort
        cohort.updated_at = datetime.now(timezone.utc)
        self._save_to_disk(cohort.jurisdiction)

    def get_or_create(
        self,
        jurisdiction: str,
        stage: QualificationLevel | str,
        subject: str,
        board: Board | str = Board.NONE,
        language: str = "en",
        year: int = 2026,
    ) -> CohortRow:
        """Get an existing cohort row or create a placeholder."""
        existing = self.get_by_key(jurisdiction, stage, subject, board, language, year)
        if existing is not None:
            return existing
        # Normalize enums
        if isinstance(stage, str):
            stage_enum = QualificationLevel(stage)
        else:
            stage_enum = stage
        if isinstance(board, str):
            try:
                board_enum = Board(board)
            except ValueError:
                board_enum = Board.NONE
        else:
            board_enum = board
        # Bilingual-aware: if language is 'ga', default to en-ga
        language_pair = LanguagePair.EN_GA if language == "ga" else None
        cohort = CohortRow(
            cohort_id=str(uuid.uuid4()),
            jurisdiction=jurisdiction,
            stage=stage_enum.value if isinstance(stage_enum, QualificationLevel) else stage_enum,
            subject=subject,
            board=board_enum.value if isinstance(board_enum, Board) else board_enum,
            language=language,
            year=year,
            language_pair=language_pair.value if language_pair else None,
            expected_extractions=1,  # placeholder; operator updates
        )
        self.upsert(cohort)
        return cohort

    def _save_to_disk(self, jurisdiction: str) -> None:
        path = self.path_for(jurisdiction)
        cohorts = self.all(jurisdiction=jurisdiction)
        try:
            with path.open("w", encoding="utf-8") as f:
                json.dump(
                    [c.model_dump(mode="json") for c in cohorts],
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
        except Exception:
            logger.exception("Failed to save cohort registry to %s", path)


__all__ = [
    "COHORT_REGISTRY_ROOT",
    "CohortRegistry",
    "CohortRow",
    "CohortLifecycleState",
    "QualificationLevel",
    "Board",
    "LanguagePair",
]
