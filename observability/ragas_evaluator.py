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
        model: str = "minimax-m3",
        embeddings_model: str = "text-embedding-3-small",
    ):
        """
        Initialize Ragas evaluator.

        Args:
            model: LLM model for evaluation. Routed through the local
                litellm gateway (LITELLM_BASE_URL, default
                http://localhost:4000/v1) as an OpenAI-compatible model
                name -- per the lakehouse-multi-subject-multi-model-
                rollout change, this used to default to
                "gemini/gemini-1.5-flash" but was never actually wired
                into the real evaluate() call below (confirmed live:
                `self.model` was dead -- ragas fell back to its own
                default OpenAI resolution regardless, which fails in
                this environment since OPENAI_API_KEY is a placeholder
                dev key, not a real one). Now defaults to "minimax-m3",
                the same real, already-working text model this repo's
                BAML clients use, routed via the local litellm gateway.
            embeddings_model: Embedding model for semantic similarity
                (not yet wired into evaluate() either -- same class of
                gap, left as a separate, smaller follow-up since none of
                the metrics this module currently calls need embeddings).
        """
        self.model = model
        self.embeddings_model = embeddings_model
        self._metrics = None
        self._initialized = False
        self._llm = None

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

            # Build a real ragas LLM wrapper pointed at the local litellm
            # gateway, so evaluate() actually uses `self.model` instead
            # of silently falling back to ragas's own default OpenAI
            # resolution (confirmed live: that default fails here, since
            # OPENAI_API_KEY is a placeholder dev key in this
            # environment, not a real one).
            self._llm = self._build_llm()

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

    def _build_llm(self):
        """Build a real ragas LLM wrapper routed through the local
        litellm gateway, so `self.model` (an OpenAI-compatible model
        name litellm already knows how to route, e.g. "minimax-m3" or
        "local/vision/qwen3-vl-8b") is what actually judges each
        evaluation, not ragas's own default OpenAI resolution.

        Returns None (not raises) on any failure -- evaluate() falls
        back to ragas's default LLM resolution in that case, same
        graceful-degradation contract as the rest of this module.
        """
        try:
            from openai import OpenAI
            from ragas.llms import llm_factory

            # NOTE: our "litellm" here is the litellm PROXY SERVICE
            # (bonneagar/stacks/litellm), reached over plain HTTP as an
            # OpenAI-compatible REST endpoint -- not the `litellm`
            # Python SDK package (confirmed live: not installed in this
            # environment). ragas's `adapter="litellm"` is for the SDK
            # client object specifically and expects instructor-SDK
            # patching that a raw HTTP client doesn't have -- confirmed
            # live: passing a plain openai.OpenAI() client with
            # adapter="litellm" produced `Completions.create() got an
            # unexpected keyword argument 'response_model'`. The correct
            # adapter for a real openai.OpenAI()-shaped client pointed
            # at any OpenAI-compatible REST endpoint (which is exactly
            # what our litellm proxy is) is the default "openai" adapter.
            base_url = (
                os.environ.get("CIANFHOGHLAIM_LITELLM_URL")
                or os.environ.get("LITELLM_BASE_URL")
                or "http://localhost:4000/v1"
            )
            api_key = os.environ.get("LITELLM_MASTER_KEY", "not-needed")
            client = OpenAI(base_url=base_url, api_key=api_key)
            return llm_factory(self.model, client=client)
        except Exception as e:  # noqa: BLE001 — best-effort, graceful fallback
            logger.warning(f"Could not build litellm-routed ragas LLM ({e}); "
                            "falling back to ragas's default LLM resolution")
            return None

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

            # Run evaluation. Pass llm=self._llm (built in _initialize())
            # so this actually uses `self.model` via the local litellm
            # gateway -- confirmed live this was previously silently
            # ignored, falling back to ragas's own default OpenAI
            # resolution regardless of what self.model was set to.
            result = evaluate(dataset, metrics=selected_metrics, llm=self._llm)

            # Parse results. Per the lakehouse-multi-subject-multi-model-
            # rollout change: ragas 0.4.x's EvaluationResult has no
            # dict-style .get() (confirmed live: `'EvaluationResult'
            # object has no attribute 'get'`) -- only `.to_pandas()` is
            # a stable public accessor, so read each metric as the mean
            # of its column (NaN-safe: pandas .mean() skips NaN rows,
            # returning NaN itself only if ALL rows are NaN for that
            # metric, which we normalize to None).
            df = result.to_pandas()

            def _metric_mean(col: str) -> float | None:
                if col not in df.columns:
                    return None
                val = df[col].mean()
                return None if val != val else float(val)  # NaN != NaN

            eval_result = EvaluationResult(
                faithfulness=_metric_mean("faithfulness"),
                answer_relevancy=_metric_mean("answer_relevancy"),
                context_precision=_metric_mean("context_precision"),
                context_recall=_metric_mean("context_recall"),
                answer_correctness=_metric_mean("answer_correctness"),
                sample_scores=df.to_dict("records"),
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
