"""Canonical 4-metric RAGAS scorer for the meaisinfoghlaim evaluation harness.

Per the 2026-08-15 meaisinfoghlaim-ireland-england-roadmap (Plan 1).

The 4 canonical metrics:
  - faithfulness      (the answer is grounded in the retrieved context)
  - answer_relevancy  (the answer addresses the question)
  - context_precision (the retrieved context is relevant)
  - context_recall    (the retrieved context covers the ground truth)

Plus the composite RAGAS score (the mean of the 4 metrics).

Graceful degradation: when the ``ragas`` package is not installed,
``RAGAS_AVAILABLE = False`` and ``compute_ragas_metrics`` falls back to
a deterministic synthetic scorer (Jaccard token-overlap) so the pipeline
can run end-to-end in dev/CI without the heavy ML dependencies.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Sequence

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class RagasFourMetricScore:
    """The canonical 4-metric RAGAS score for a single cohort evaluation.

    All metric values are in [0.0, 1.0]. The composite is the arithmetic
    mean of the 4 metrics. The BIEP v3 faithfulness gate threshold
    (locked 2026-08-15) is 0.95 -- ``passed_threshold = (faithfulness >= 0.95)``.
    """

    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float
    composite: float = field(init=False)

    def __post_init__(self) -> None:
        for name in ("faithfulness", "answer_relevancy", "context_precision", "context_recall"):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"RagasFourMetricScore.{name} must be in [0.0, 1.0]; got {value}"
                )
        object.__setattr__(
            self,
            "composite",
            round(
                (
                    self.faithfulness
                    + self.answer_relevancy
                    + self.context_precision
                    + self.context_recall
                )
                / 4.0,
                4,
            ),
        )

    def passed_threshold(self, threshold: float = 0.95) -> bool:
        """The BIEP v3 gate check: ``faithfulness >= threshold``."""
        return self.faithfulness >= threshold

    @classmethod
    def zero(cls) -> "RagasFourMetricScore":
        """The canonical zero score (used for failure cases)."""
        return cls(
            faithfulness=0.0,
            answer_relevancy=0.0,
            context_precision=0.0,
            context_recall=0.0,
        )

    def summary(self) -> dict[str, float]:
        return {
            "faithfulness": self.faithfulness,
            "answer_relevancy": self.answer_relevancy,
            "context_precision": self.context_precision,
            "context_recall": self.context_recall,
            "composite": self.composite,
            "passed_threshold": self.passed_threshold(),
        }


# Try to import the real RAGAS package; fall back to deterministic synthetic
# scorer if unavailable.
try:
    from ragas.metrics import (  # type: ignore[import-not-found]
        faithfulness as _r_faithfulness,
        answer_relevance as _r_answer_relevance,
        context_precision as _r_context_precision,
        context_recall as _r_context_recall,
    )
    from ragas import evaluate as _r_evaluate  # type: ignore[import-not-found]
    RAGAS_AVAILABLE = True
except ImportError:
    RAGAS_AVAILABLE = False
    _r_evaluate = None  # type: ignore[assignment]


def compute_ragas_metrics(dataset: Sequence[dict[str, Any]]) -> RagasFourMetricScore:
    """Compute the 4-metric RAGAS score for a cohort dataset.

    Args:
        dataset: a list of golden baseline dicts. Each dict must contain:
          - "question": str
          - "ground_truth": str
          - "contexts": list[str]  (the retrieved context chunks; optional)
          - "answer": str         (the system answer; optional)

    Returns:
        The canonical ``RagasFourMetricScore`` for the dataset.

    Falls back to a deterministic synthetic scorer (Jaccard token-overlap)
    when the real RAGAS package is not installed.
    """
    if not dataset:
        return RagasFourMetricScore.zero()

    if RAGAS_AVAILABLE and _r_evaluate is not None:
        try:
            from meaisinfoghlaim.evaluation.ragas_biiep_ensemble import (
                evaluate_ensemble as _evaluate_ensemble,
            )
            ragas_score_obj = _evaluate_ensemble(dataset)
            return RagasFourMetricScore(
                faithfulness=float(getattr(ragas_score_obj, "faithfulness", 0.0)),
                answer_relevancy=float(getattr(ragas_score_obj, "answer_relevancy", 0.0)),
                context_precision=float(getattr(ragas_score_obj, "context_precision", 0.0)),
                context_recall=float(getattr(ragas_score_obj, "context_recall", 0.0)),
            )
        except Exception:
            logger.exception("Real RAGAS eval failed; falling back to synthetic scorer")

    return _synthetic_ragas_score(dataset)


def _synthetic_ragas_score(dataset: Sequence[dict[str, Any]]) -> RagasFourMetricScore:
    """Deterministic synthetic RAGAS score (dev / CI fallback).

    Computes each metric as the average Jaccard similarity over the dataset:
      - faithfulness      = avg(jaccard(answer, context))
      - answer_relevancy  = avg(jaccard(answer, question))
      - context_precision = avg(jaccard(context, ground_truth))
      - context_recall    = avg(jaccard(ground_truth, context))
    """
    if not dataset:
        return RagasFourMetricScore.zero()

    faithfulness_vals: list[float] = []
    answer_relevancy_vals: list[float] = []
    context_precision_vals: list[float] = []
    context_recall_vals: list[float] = []

    for item in dataset:
        answer_tokens = _tokenize(item.get("answer", ""))
        context_tokens = _tokenize(" ".join(item.get("contexts", [])))
        question_tokens = _tokenize(item.get("question", ""))
        ground_truth_tokens = _tokenize(item.get("ground_truth", ""))

        if context_tokens and answer_tokens:
            faithfulness_vals.append(_jaccard(answer_tokens, context_tokens))
        if answer_tokens and question_tokens:
            answer_relevancy_vals.append(_jaccard(answer_tokens, question_tokens))
        if context_tokens and ground_truth_tokens:
            context_precision_vals.append(_jaccard(context_tokens, ground_truth_tokens))
            context_recall_vals.append(_jaccard(ground_truth_tokens, context_tokens))

    return RagasFourMetricScore(
        faithfulness=_avg(faithfulness_vals),
        answer_relevancy=_avg(answer_relevancy_vals),
        context_precision=_avg(context_precision_vals),
        context_recall=_avg(context_recall_vals),
    )


def _tokenize(text: str) -> set[str]:
    """Whitespace + case-folded tokenization."""
    return {tok for tok in (text or "").lower().split() if tok}


def _jaccard(a: set[str], b: set[str]) -> float:
    """Jaccard similarity in [0.0, 1.0]."""
    if not a or not b:
        return 0.0
    intersection = a & b
    union = a | b
    return len(intersection) / len(union)


def _avg(vals: list[float]) -> float:
    return round(sum(vals) / len(vals), 4) if vals else 0.0


__all__ = [
    "RagasFourMetricScore",
    "compute_ragas_metrics",
    "RAGAS_AVAILABLE",
]
