"""Per-jurisdiction RAGAS score aggregator.

Per the 2026-08-15 meaisinfhoghlaim-ireland-england-roadmap (Plan 1).

Aggregates per-cohort PerSubjectEvalResult objects into:
  - Per-(jurisdiction, stage) RAGAS report (mean of N cohorts)
  - Per-jurisdiction RAGAS report (mean of M stages)
  - Cross-jurisdiction RAGAS report (Ireland vs England)
  - Threshold-compliance matrix (which cohorts passed the 0.95 gate)

Consumed by notebooks/63_meaisin_eval_dashboard.py and the
meaisin_eval_progress Dagster asset.

Usage:
    agg = ScoreAggregator()
    for cohort, result in eval_results:
        agg.add(cohort, result)
    print(agg.jurisdiction_report("ireland").summary())
    print(agg.cross_jurisdiction_report().summary())
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable

from meaisinfhoghlaim.evaluation.per_subject_runner import (
    CohortKey,
    PerSubjectEvalResult,
)
from meaisinfhoghlaim.evaluation.ragas_metrics import RagasFourMetricScore


# BIEP v3 gate threshold (locked 2026-08-15)
THRESHOLD = 0.95


@dataclass(slots=True)
class JurisdictionalRagasReport:
    """The canonical per-(jurisdiction, stage) RAGAS report."""

    jurisdiction: str
    stage: str | None  # None = across all stages for the jurisdiction
    cohort_count: int
    mean_faithfulness: float
    mean_answer_relevancy: float
    mean_context_precision: float
    mean_context_recall: float
    mean_composite: float
    passed_count: int
    pass_rate: float

    def summary(self) -> dict:
        return {
            "jurisdiction": self.jurisdiction,
            "stage": self.stage or "all",
            "cohort_count": self.cohort_count,
            "mean_faithfulness": round(self.mean_faithfulness, 4),
            "mean_answer_relevancy": round(self.mean_answer_relevancy, 4),
            "mean_context_precision": round(self.mean_context_precision, 4),
            "mean_context_recall": round(self.mean_context_recall, 4),
            "mean_composite": round(self.mean_composite, 4),
            "passed_count": self.passed_count,
            "pass_rate": round(self.pass_rate, 4),
            "threshold": THRESHOLD,
        }


@dataclass(slots=True)
class CrossJurisdictionReport:
    """The canonical cross-jurisdiction RAGAS report (Ireland vs England)."""

    reports: dict
    cross_mean_faithfulness: float
    cross_mean_composite: float

    def summary(self) -> dict:
        return {
            "by_jurisdiction": {k: v.summary() for k, v in self.reports.items()},
            "cross_mean_faithfulness": round(self.cross_mean_faithfulness, 4),
            "cross_mean_composite": round(self.cross_mean_composite, 4),
        }


class ScoreAggregator:
    """The canonical per-jurisdiction RAGAS score aggregator."""

    def __init__(self, threshold: float = THRESHOLD) -> None:
        self.threshold = threshold
        self._results: list = []

    def add(self, cohort: CohortKey, result: PerSubjectEvalResult) -> None:
        self._results.append((cohort, result))

    def extend(self, items: Iterable) -> None:
        for cohort, result in items:
            self.add(cohort, result)

    def results(self) -> list:
        return list(self._results)

    def _aggregate(self, cohorts: list):
        if not cohorts:
            return None
        n = len(cohorts)
        mean_faithfulness = sum(r.ragas.faithfulness for _, r in cohorts) / n
        mean_answer_relevancy = sum(r.ragas.answer_relevancy for _, r in cohorts) / n
        mean_context_precision = sum(r.ragas.context_precision for _, r in cohorts) / n
        mean_context_recall = sum(r.ragas.context_recall for _, r in cohorts) / n
        mean_composite = sum(r.ragas.composite for _, r in cohorts) / n
        passed_count = sum(1 for _, r in cohorts if r.passed_threshold)
        jurisdiction = cohorts[0][0].jurisdiction
        stage = cohorts[0][0].stage
        for c, _ in cohorts[1:]:
            if c.jurisdiction != jurisdiction or c.stage != stage:
                stage = None
                break
        return JurisdictionalRagasReport(
            jurisdiction=jurisdiction,
            stage=stage,
            cohort_count=n,
            mean_faithfulness=mean_faithfulness,
            mean_answer_relevancy=mean_answer_relevancy,
            mean_context_precision=mean_context_precision,
            mean_context_recall=mean_context_recall,
            mean_composite=mean_composite,
            passed_count=passed_count,
            pass_rate=passed_count / n if n > 0 else 0.0,
        )

    def jurisdiction_report(self, jurisdiction, stage=None):
        cohorts = [
            (c, r)
            for c, r in self._results
            if c.jurisdiction == jurisdiction and (stage is None or c.stage == stage)
        ]
        return self._aggregate(cohorts)

    def all_jurisdiction_reports(self) -> list:
        jurisdictions = {c.jurisdiction for c, _ in self._results}
        return [
            r
            for j in sorted(jurisdictions)
            if (r := self.jurisdiction_report(j)) is not None
        ]

    def cross_jurisdiction_report(self) -> CrossJurisdictionReport:
        reports: dict = {}
        for j in sorted({c.jurisdiction for c, _ in self._results}):
            r = self.jurisdiction_report(j)
            if r is not None:
                reports[j] = r
        if not reports:
            return CrossJurisdictionReport(
                reports={},
                cross_mean_faithfulness=0.0,
                cross_mean_composite=0.0,
            )
        total_cohorts = sum(r.cohort_count for r in reports.values())
        if total_cohorts == 0:
            cross_faith = 0.0
            cross_composite = 0.0
        else:
            cross_faith = sum(r.mean_faithfulness * r.cohort_count for r in reports.values()) / total_cohorts
            cross_composite = sum(r.mean_composite * r.cohort_count for r in reports.values()) / total_cohorts
        return CrossJurisdictionReport(
            reports=reports,
            cross_mean_faithfulness=cross_faith,
            cross_mean_composite=cross_composite,
        )

    def threshold_compliance_matrix(self) -> dict:
        matrix: dict = defaultdict(list)
        for c, r in self._results:
            matrix[(c.jurisdiction, c.subject)].append(r.passed_threshold)
        return {k: sum(v) / len(v) for k, v in matrix.items()}


__all__ = [
    "THRESHOLD",
    "JurisdictionalRagasReport",
    "CrossJurisdictionReport",
    "ScoreAggregator",
]
