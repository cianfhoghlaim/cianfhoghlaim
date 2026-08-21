"""
RAG Evaluation Pipeline for Celtic Education Platform.

Provides:
- Evaluation dataset creation from curriculum searches
- Baseline measurement and improvement tracking
- Agentic RAG evaluation (multi-query, self-correction)
- MLflow experiment tracking and comparison
- Langfuse scoring integration

Based on research achieving 22.7% improvement (65.2% → 87.9%)
using agentic RAG with multiple search terms.
"""

from .ragas_pipeline import (
    CurriculumEvaluationDataset,
    AgenticRagEvaluator,
    create_curriculum_eval_dataset,
    run_baseline_evaluation,
    run_agentic_evaluation,
    compare_evaluation_runs,
)

__all__ = [
    "CurriculumEvaluationDataset",
    "AgenticRagEvaluator",
    "create_curriculum_eval_dataset",
    "run_baseline_evaluation",
    "run_agentic_evaluation",
    "compare_evaluation_runs",
]
