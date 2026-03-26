"""
Ragas Evaluation Framework for Celtic Education Pipeline.

Provides:
- RAG quality evaluation (faithfulness, relevancy, context precision)
- Automated evaluation pipelines
- Integration with Langfuse for trace-based evaluation
- Integration with MLflow for experiment tracking

Reference: https://docs.ragas.io/
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# Lazy imports for optional dependency
_ragas = None
_ragas_available = None


def _get_ragas():
    """Lazy load Ragas to handle missing dependency."""
    global _ragas, _ragas_available
    if _ragas_available is None:
        try:
            import ragas

            _ragas = ragas
            _ragas_available = True
        except ImportError:
            _ragas_available = False
            logger.warning("Ragas not installed. Install with: pip install ragas")
    return _ragas if _ragas_available else None


@dataclass
class EvaluationSample:
    """A single evaluation sample for RAG evaluation."""

    question: str
    answer: str
    contexts: list[str]
    ground_truth: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationResult:
    """Results from RAG evaluation."""

    faithfulness: float | None = None
    answer_relevancy: float | None = None
    context_precision: float | None = None
    context_recall: float | None = None
    answer_correctness: float | None = None
    harmfulness: float | None = None
    sample_scores: list[dict[str, float]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "faithfulness": self.faithfulness,
            "answer_relevancy": self.answer_relevancy,
            "context_precision": self.context_precision,
            "context_recall": self.context_recall,
            "answer_correctness": self.answer_correctness,
            "harmfulness": self.harmfulness,
            "sample_count": len(self.sample_scores),
            **self.metadata,
        }


class RagasEvaluator:
    """
    RAG evaluation using Ragas metrics.

    Supports:
    - faithfulness: Is the answer grounded in the context?
    - answer_relevancy: Does the answer address the question?
    - context_precision: Are retrieved contexts relevant?
    - context_recall: Are all relevant contexts retrieved?
    - answer_correctness: Is the answer factually correct?
    - harmfulness: Safety evaluation

    Example:
        evaluator = RagasEvaluator()

        samples = [
            EvaluationSample(
                question="What are the key learning outcomes for Junior Cycle Maths?",
                answer="The key outcomes include number, algebra, geometry...",
                contexts=["Junior Cycle Mathematics Specification...", ...],
                ground_truth="Number, Algebra, Geometry, Statistics..."
            )
        ]

        result = await evaluator.evaluate(samples)
        print(f"Faithfulness: {result.faithfulness:.2f}")
    """

    def __init__(
        self,
        model: str = "gemini/gemini-1.5-flash",
        embeddings_model: str = "text-embedding-3-small",
    ):
        """
        Initialize Ragas evaluator.

        Args:
            model: LLM model for evaluation (LiteLLM format)
            embeddings_model: Embedding model for semantic similarity
        """
        self.model = model
        self.embeddings_model = embeddings_model
        self._metrics = None
        self._initialized = False

    def _initialize(self) -> bool:
        """Initialize Ragas metrics lazily."""
        if self._initialized:
            return True

        ragas = _get_ragas()
        if ragas is None:
            return False

        try:
            from ragas.metrics import (
                answer_correctness,
                answer_relevancy,
                context_precision,
                context_recall,
                faithfulness,
            )

            # Configure LLM (using LiteLLM via environment)
            os.environ.setdefault("LITELLM_MODEL", self.model)

            self._metrics = {
                "faithfulness": faithfulness,
                "answer_relevancy": answer_relevancy,
                "context_precision": context_precision,
                "context_recall": context_recall,
                "answer_correctness": answer_correctness,
            }

            self._initialized = True
            logger.info(f"Ragas evaluator initialized with model: {self.model}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Ragas: {e}")
            return False

    async def evaluate(
        self,
        samples: list[EvaluationSample],
        metrics: list[str] | None = None,
    ) -> EvaluationResult:
        """
        Evaluate RAG samples using Ragas metrics.

        Args:
            samples: List of evaluation samples
            metrics: List of metric names to compute (default: all)

        Returns:
            EvaluationResult with computed scores
        """
        if not self._initialize():
            logger.warning("Ragas not available, returning empty results")
            return EvaluationResult()

        try:
            from datasets import Dataset
            from ragas import evaluate

            # Convert samples to Ragas format
            data = {
                "question": [s.question for s in samples],
                "answer": [s.answer for s in samples],
                "contexts": [s.contexts for s in samples],
            }

            # Add ground truth if available
            if any(s.ground_truth for s in samples):
                data["ground_truth"] = [s.ground_truth or "" for s in samples]

            dataset = Dataset.from_dict(data)

            # Select metrics
            if metrics:
                selected_metrics = [
                    self._metrics[m] for m in metrics if m in self._metrics
                ]
            else:
                selected_metrics = list(self._metrics.values())

            # Run evaluation
            result = evaluate(dataset, metrics=selected_metrics)

            # Parse results
            eval_result = EvaluationResult(
                faithfulness=result.get("faithfulness"),
                answer_relevancy=result.get("answer_relevancy"),
                context_precision=result.get("context_precision"),
                context_recall=result.get("context_recall"),
                answer_correctness=result.get("answer_correctness"),
                sample_scores=result.to_pandas().to_dict("records") if hasattr(result, "to_pandas") else [],
                metadata={"sample_count": len(samples), "model": self.model},
            )

            return eval_result

        except Exception as e:
            logger.error(f"Ragas evaluation failed: {e}")
            return EvaluationResult(metadata={"error": str(e)})

    async def evaluate_single(
        self,
        question: str,
        answer: str,
        contexts: list[str],
        ground_truth: str | None = None,
    ) -> EvaluationResult:
        """
        Evaluate a single RAG response.

        Args:
            question: User question
            answer: Generated answer
            contexts: Retrieved contexts
            ground_truth: Expected answer (optional)

        Returns:
            EvaluationResult for the single sample
        """
        sample = EvaluationSample(
            question=question,
            answer=answer,
            contexts=contexts,
            ground_truth=ground_truth,
        )
        return await self.evaluate([sample])


async def evaluate_rag_response(
    question: str,
    answer: str,
    contexts: list[str],
    ground_truth: str | None = None,
    log_to_langfuse: bool = True,
    log_to_mlflow: bool = True,
    trace=None,
) -> dict[str, float]:
    """
    Evaluate a RAG response and optionally log to observability platforms.

    Args:
        question: User question
        answer: Generated answer
        contexts: Retrieved contexts
        ground_truth: Expected answer (optional)
        log_to_langfuse: Whether to log scores to Langfuse
        log_to_mlflow: Whether to log scores to MLflow
        trace: Optional Langfuse trace to attach scores to

    Returns:
        Dictionary of metric scores
    """
    evaluator = RagasEvaluator()
    result = await evaluator.evaluate_single(question, answer, contexts, ground_truth)

    scores = result.to_dict()

    # Log to Langfuse
    if log_to_langfuse and trace is not None:
        from .langfuse_config import score_trace

        for metric_name in ["faithfulness", "answer_relevancy", "context_precision"]:
            if scores.get(metric_name) is not None:
                score_trace(trace, metric_name, scores[metric_name])

    # Log to MLflow
    if log_to_mlflow:
        from .mlflow_config import log_evaluation_results, mlflow_run

        with mlflow_run("ragas_evaluation", tags={"type": "rag_quality"}):
            log_evaluation_results(
                evaluation_name="single_response",
                scores={k: v for k, v in scores.items() if isinstance(v, (int, float)) and v is not None},
            )

    return scores


async def run_evaluation_suite(
    samples: list[EvaluationSample],
    experiment_name: str = "rag_evaluation",
    log_to_mlflow: bool = True,
) -> EvaluationResult:
    """
    Run a full evaluation suite on multiple samples.

    Args:
        samples: List of evaluation samples
        experiment_name: MLflow experiment name
        log_to_mlflow: Whether to log to MLflow

    Returns:
        Aggregated EvaluationResult
    """
    evaluator = RagasEvaluator()
    result = await evaluator.evaluate(samples)

    if log_to_mlflow:
        from .mlflow_config import init_mlflow, log_evaluation_results, mlflow_run

        init_mlflow(experiment_name=f"oideachais-{experiment_name}")

        with mlflow_run(experiment_name, tags={"type": "rag_evaluation_suite"}):
            log_evaluation_results(
                evaluation_name=experiment_name,
                scores={k: v for k, v in result.to_dict().items() if isinstance(v, (int, float)) and v is not None},
                dataset_size=len(samples),
                artifacts={"sample_scores": result.sample_scores},
            )

    return result


# Convenience functions for specific evaluation scenarios
async def evaluate_curriculum_search(
    query: str,
    search_results: list[dict[str, Any]],
    agent_response: str,
) -> dict[str, float]:
    """
    Evaluate curriculum search quality.

    Args:
        query: User search query
        search_results: Retrieved curriculum documents
        agent_response: Agent's synthesized response

    Returns:
        Evaluation scores
    """
    contexts = [
        result.get("content", result.get("text", str(result)))
        for result in search_results
    ]

    return await evaluate_rag_response(
        question=query,
        answer=agent_response,
        contexts=contexts,
    )


async def evaluate_document_qa(
    question: str,
    answer: str,
    source_documents: list[str],
    expected_answer: str | None = None,
) -> dict[str, float]:
    """
    Evaluate document Q&A quality.

    Args:
        question: User question
        answer: Generated answer
        source_documents: Source document contents
        expected_answer: Expected/reference answer

    Returns:
        Evaluation scores including answer_correctness if expected_answer provided
    """
    return await evaluate_rag_response(
        question=question,
        answer=answer,
        contexts=source_documents,
        ground_truth=expected_answer,
    )
