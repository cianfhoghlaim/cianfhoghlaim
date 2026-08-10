"""Per-(jurisdiction, stage, subject, board, language) eval runner.

Per the 2026-08-15 meaisinfhoghlaim-ireland-england-roadmap (Plan 1).
Generalisable to Scotland (Nat 5/Higher/Adv Higher), Wales (EN/CY),
NI (CCEA), Jersey/Guernsey/IoM later.

Usage:
    runner = PerSubjectRunner()
    result = await runner.run(
        jurisdiction="ireland", stage="lc", subject="mathematics",
        board=None, language="en", golden_baselines=baselines,
    )
    print(result.summary())
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import asdict, dataclass, field
from typing import Any

from meaisinfhoghlaim.evaluation.ragas_metrics import (
    RagasFourMetricScore,
    compute_ragas_metrics,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CohortKey:
    """The canonical (jurisdiction, stage, subject, board, language) key."""

    jurisdiction: str  # ireland, england, scotland
    stage: str  # lc, gcse, a_level, primary
    subject: str  # mathematics, chemistry
    board: str | None = None  # aqa, ocr, edexcel, ccea; None for non-boarded
    language: str = "en"  # en, ga, cy

    def to_tuple(self) -> tuple[str, str, str, str | None, str]:
        return (self.jurisdiction, self.stage, self.subject, self.board, self.language)

    def __str__(self) -> str:
        board = f"/{self.board}" if self.board else ""
        return f"{self.jurisdiction}/{self.stage}/{self.subject}{board}/{self.language}"


@dataclass(slots=True)
class PerSubjectEvalResult:
    """The canonical result of a per-cohort RAGAS evaluation."""

    cohort: CohortKey
    ragas: RagasFourMetricScore
    passed_threshold: bool  # ragas.faithfulness >= 0.95 per BIEP v3 gate
    duration_s: float
    question_count: int
    golden_baseline_id: str | None
    mlflow_run_id: str | None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> dict[str, Any]:
        return {
            "cohort": str(self.cohort),
            "ragas": asdict(self.ragas),
            "passed_threshold": self.passed_threshold,
            "duration_s": round(self.duration_s, 3),
            "question_count": self.question_count,
            "golden_baseline_id": self.golden_baseline_id,
            "mlflow_run_id": self.mlflow_run_id,
            "error": self.error,
        }


class PerSubjectRunner:
    """The canonical per-cohort RAGAS evaluation runner.

    Wraps ``compute_ragas_metrics`` (from ragas_metrics.py) + the existing
    EvaluationQuestion + CurriculumEvaluationDataset classes (from
    ragas_pipeline.py) into a per-cohort orchestrator.
    """

    THRESHOLD = 0.95  # BIEP v3 faithfulness gate threshold (locked 2026-08-15)

    def __init__(
        self,
        mlflow_experiment: str = "biiep_v3",
        mlflow_client: Any | None = None,
    ) -> None:
        self.mlflow_experiment = mlflow_experiment
        self._mlflow_client = mlflow_client
        self._mlflow_available: bool | None = None

    def _get_mlflow_client(self) -> Any | None:
        if self._mlflow_available is False:
            return None
        if self._mlflow_client is not None:
            return self._mlflow_client
        try:
            import mlflow  # type: ignore[import-not-found]
            self._mlflow_client = mlflow
            self._mlflow_available = True
            return mlflow
        except ImportError:
            self._mlflow_available = False
            return None

    async def run(
        self,
        jurisdiction: str,
        stage: str,
        subject: str,
        golden_baselines: list | None = None,
        board: str | None = None,
        language: str = "en",
        threshold: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> PerSubjectEvalResult:
        cohort = CohortKey(
            jurisdiction=jurisdiction, stage=stage, subject=subject,
            board=board, language=language,
        )
        threshold = threshold if threshold is not None else self.THRESHOLD
        started = time.monotonic()

        try:
            dataset = self._build_dataset(cohort, golden_baselines)
            ragas = await self._compute_metrics(cohort, dataset)
            passed = ragas.faithfulness >= threshold
            mlflow_run_id = self._log_to_mlflow(cohort, ragas, passed, dataset, metadata or {})

            return PerSubjectEvalResult(
                cohort=cohort,
                ragas=ragas,
                passed_threshold=passed,
                duration_s=time.monotonic() - started,
                question_count=len(dataset),
                golden_baseline_id=golden_baselines[0].get("id") if golden_baselines else None,
                mlflow_run_id=mlflow_run_id,
                metadata=metadata or {},
            )
        except Exception as exc:
            logger.exception("PerSubjectRunner.run failed for cohort=%s", cohort)
            return PerSubjectEvalResult(
                cohort=cohort,
                ragas=RagasFourMetricScore.zero(),
                passed_threshold=False,
                duration_s=time.monotonic() - started,
                question_count=0,
                golden_baseline_id=None,
                mlflow_run_id=None,
                error=str(exc),
                metadata=metadata or {},
            )

    def _build_dataset(
        self, cohort: CohortKey, golden_baselines: list | None
    ) -> list:
        if golden_baselines:
            return golden_baselines
        return [
            {
                "id": f"synthetic-{cohort.subject}-q1",
                "question": f"What is the canonical learning outcome for {cohort.subject}?",
                "question_ga": None,
                "ground_truth": "[PLACEHOLDER — seed real golden baseline]",
                "ground_truth_ga": None,
                "domain": "curriculum",
                "subject": cohort.subject,
                "level": cohort.stage,
                "difficulty": "medium",
                "source": "synthetic",
                "metadata": {"synthetic": True},
            }
        ]

    async def _compute_metrics(self, cohort: CohortKey, dataset: list) -> "RagasFourMetricScore":
        return await asyncio.to_thread(compute_ragas_metrics, dataset)

    def _log_to_mlflow(
        self,
        cohort: CohortKey,
        ragas: "RagasFourMetricScore",
        passed: bool,
        dataset: list,
        metadata: dict[str, Any],
    ) -> str | None:
        mlflow = self._get_mlflow_client()
        if mlflow is None:
            logger.warning("MLflow not available; skipping log for cohort=%s", cohort)
            return None
        try:
            mlflow.set_experiment(self.mlflow_experiment)
            with mlflow.start_run(run_name=f"per_subject/{cohort}") as run:
                mlflow.log_params({
                    "jurisdiction": cohort.jurisdiction,
                    "stage": cohort.stage,
                    "subject": cohort.subject,
                    "board": cohort.board or "none",
                    "language": cohort.language,
                })
                mlflow.log_metrics({
                    "ragas.faithfulness": ragas.faithfulness,
                    "ragas.answer_relevancy": ragas.answer_relevancy,
                    "ragas.context_precision": ragas.context_precision,
                    "ragas.context_recall": ragas.context_recall,
                    "ragas.composite": ragas.composite,
                    "passed_threshold": float(passed),
                    "question_count": float(len(dataset)),
                })
                for k, v in metadata.items():
                    if isinstance(v, (str, int, float)):
                        mlflow.set_tag(k, str(v))
                return run.info.run_id
        except Exception:
            logger.exception("MLflow log failed for cohort=%s", cohort)
            return None


__all__ = [
    "CohortKey",
    "PerSubjectEvalResult",
    "PerSubjectRunner",
]
