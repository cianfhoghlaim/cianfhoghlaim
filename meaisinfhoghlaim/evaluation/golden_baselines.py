"""Per-(jurisdiction, stage, subject, board, language) golden baseline store.

Per the 2026-08-15 meaisinfoghlaim-ireland-england-roadmap (Plan 1).

The golden baseline is the canonical set of question/answer pairs that
the RAGAS pipeline uses as ground truth for the per-subject evaluation.

Generalisable: same shape (CohortKey + list of GoldenQuestion pairs)
works for any (jurisdiction, stage, subject, board, language) cohort.

Storage:
  - In-memory: ``BASELINES`` dict keyed by CohortKey
  - On disk: ``stedding/education/eval_golden_baselines/`` as JSONL files

Usage:
    from meaisinfoghlaim.evaluation.golden_baselines import GoldenBaselineStore
    from meaisinfoghlaim.evaluation.per_subject_runner import CohortKey
    store = GoldenBaselineStore()
    cohort = CohortKey("ireland", "lc", "mathematics")
    baselines = store.get(cohort)
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from meaisinfoghlaim.evaluation.per_subject_runner import CohortKey

logger = logging.getLogger(__name__)


GOLDEN_BASELINES_ROOT = Path(
    os.environ.get(
        "CIANFHOGHLAIM_GOLDEN_BASELINES_ROOT",
        "stedding/education/eval_golden_baselines",
    )
)


@dataclass(slots=True)
class GoldenQuestion:
    """A single canonical question/answer pair for the golden baseline."""

    id: str
    question: str
    ground_truth: str
    question_ga: str | None = None
    ground_truth_ga: str | None = None
    domain: str = "curriculum"
    subject: str | None = None
    level: str | None = None
    difficulty: str = "medium"
    source: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class GoldenBaseline:
    """The canonical golden baseline for a single cohort."""

    cohort: CohortKey
    questions: list[GoldenQuestion]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "1.0"
    notes: str = ""

    @property
    def size(self) -> int:
        return len(self.questions)

    def to_dict(self) -> dict[str, Any]:
        return {
            "cohort": self.cohort.to_tuple(),
            "cohort_str": str(self.cohort),
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "notes": self.notes,
            "questions": [
                {
                    "id": q.id,
                    "question": q.question,
                    "ground_truth": q.ground_truth,
                    "question_ga": q.question_ga,
                    "ground_truth_ga": q.ground_truth_ga,
                    "domain": q.domain,
                    "subject": q.subject,
                    "level": q.level,
                    "difficulty": q.difficulty,
                    "source": q.source,
                    "metadata": q.metadata,
                }
                for q in self.questions
            ],
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "GoldenBaseline":
        cohort = CohortKey(*d["cohort"])
        return cls(
            cohort=cohort,
            questions=[
                GoldenQuestion(
                    id=q["id"],
                    question=q["question"],
                    ground_truth=q["ground_truth"],
                    question_ga=q.get("question_ga"),
                    ground_truth_ga=q.get("ground_truth_ga"),
                    domain=q.get("domain", "curriculum"),
                    subject=q.get("subject"),
                    level=q.get("level"),
                    difficulty=q.get("difficulty", "medium"),
                    source=q.get("source"),
                    metadata=q.get("metadata", {}),
                )
                for q in d.get("questions", [])
            ],
            created_at=datetime.fromisoformat(d.get("created_at", datetime.now(timezone.utc).isoformat())),
            updated_at=datetime.fromisoformat(d.get("updated_at", datetime.now(timezone.utc).isoformat())),
            version=d.get("version", "1.0"),
            notes=d.get("notes", ""),
        )


class GoldenBaselineStore:
    """The canonical golden baseline store.

    Reads + writes JSONL files from
    ``stedding/education/eval_golden_baselines/`` (1 file per cohort,
    named ``<jurisdiction>__<stage>__<subject>[__<board>][__<lang>].jsonl``).
    """

    def __init__(self, root: Path | str | None = None) -> None:
        self.root = Path(root) if root is not None else GOLDEN_BASELINES_ROOT
        self.root.mkdir(parents=True, exist_ok=True)
        self._cache: dict[tuple, GoldenBaseline] = {}

    @staticmethod
    def cohort_to_filename(cohort: CohortKey) -> str:
        parts = [cohort.jurisdiction, cohort.stage, cohort.subject]
        if cohort.board:
            parts.append(cohort.board)
        if cohort.language and cohort.language != "en":
            parts.append(cohort.language)
        return "__".join(parts) + ".jsonl"

    def path_for(self, cohort: CohortKey) -> Path:
        return self.root / self.cohort_to_filename(cohort)

    def get(self, cohort: CohortKey) -> list[GoldenQuestion]:
        cache_key = cohort.to_tuple()
        if cache_key in self._cache:
            return list(self._cache[cache_key].questions)
        path = self.path_for(cohort)
        if not path.exists():
            return []
        baseline = self._read(path)
        if baseline is not None:
            self._cache[cache_key] = baseline
        return list(baseline.questions) if baseline else []

    def save(self, baseline: GoldenBaseline) -> Path:
        path = self.path_for(baseline.cohort)
        baseline.updated_at = datetime.now(timezone.utc)
        with path.open("w", encoding="utf-8") as f:
            json.dump(baseline.to_dict(), f, indent=2, ensure_ascii=False)
        self._cache[baseline.cohort.to_tuple()] = baseline
        logger.info("Saved golden baseline for %s at %s (%d questions)", baseline.cohort, path, baseline.size)
        return path

    def all_cohorts(self) -> list[CohortKey]:
        cohorts: list[CohortKey] = []
        for path in sorted(self.root.glob("*.jsonl")):
            baseline = self._read(path)
            if baseline is not None:
                cohorts.append(baseline.cohort)
        return cohorts

    def _read(self, path: Path) -> GoldenBaseline | None:
        try:
            with path.open("r", encoding="utf-8") as f:
                d = json.load(f)
            return GoldenBaseline.from_dict(d)
        except Exception:
            logger.exception("Failed to read golden baseline at %s", path)
            return None


__all__ = [
    "GOLDEN_BASELINES_ROOT",
    "GoldenQuestion",
    "GoldenBaseline",
    "GoldenBaselineStore",
]
