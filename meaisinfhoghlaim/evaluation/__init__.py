"""Meaisinfhoghlaim evaluation package (BIEP v2 + BIEP v3).

Per the 2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1 change AND
the 2026-08-15-meaisinfoghlaim-ireland-england-roadmap (Plan 1).

Provides:
  - RAGAS evaluation harnesses for the BIEP v2 4-path ensemble
    (`ragas_biiep_ensemble.py`)
  - The canonical 4-metric RAGAS scorer (`ragas_metrics.py`)
  - Per-(jurisdiction, stage, subject) eval runner (`per_subject_runner.py`)
  - Per-cohort golden baseline store (`golden_baselines.py`)
  - Per-jurisdiction score aggregator (`score_aggregator.py`)
  - Operator-facing CLI (`cli.py`)
  - OCR evaluation harness (`compare.py`)

All harnesses log to the canonical MLflow experiment `biiep_v3`.
"""

# Re-exports for the per-subject RAGAS eval workflow (Plan 1)
from meaisinfhoghlaim.evaluation.ragas_metrics import (
    RagasFourMetricScore,
    RAGAS_AVAILABLE,
    compute_ragas_metrics,
)
from meaisinfhoghlaim.evaluation.per_subject_runner import (
    CohortKey,
    PerSubjectEvalResult,
    PerSubjectRunner,
)
from meaisinfhoghlaim.evaluation.golden_baselines import (
    GOLDEN_BASELINES_ROOT,
    GoldenBaseline,
    GoldenBaselineStore,
    GoldenQuestion,
)
from meaisinfhoghlaim.evaluation.score_aggregator import (
    CrossJurisdictionReport,
    JurisdictionalRagasReport,
    ScoreAggregator,
    THRESHOLD,
)


__all__ = [
    # RAGAS metrics
    "RagasFourMetricScore",
    "RAGAS_AVAILABLE",
    "compute_ragas_metrics",
    # Per-subject runner
    "CohortKey",
    "PerSubjectEvalResult",
    "PerSubjectRunner",
    # Golden baselines
    "GOLDEN_BASELINES_ROOT",
    "GoldenQuestion",
    "GoldenBaseline",
    "GoldenBaselineStore",
    # Aggregator
    "THRESHOLD",
    "JurisdictionalRagasReport",
    "CrossJurisdictionReport",
    "ScoreAggregator",
]
