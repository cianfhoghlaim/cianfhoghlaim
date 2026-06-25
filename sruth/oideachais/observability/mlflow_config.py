"""
MLflow Configuration for Celtic Education Pipeline.

Provides:
- Experiment tracking for agent runs and evaluations
- Model registry for prompt versioning
- Artifact logging for evaluation results
- Integration with Dagster assets

Deployed at: mlflow.cianfhoghlaim.ie
"""

import logging
import os
from collections.abc import Callable
from contextlib import contextmanager
from functools import wraps
from typing import Any

logger = logging.getLogger(__name__)

# Lazy imports for optional dependency
_mlflow = None
_mlflow_available = None


def _get_mlflow():
    """Lazy load MLflow to handle missing dependency."""
    global _mlflow, _mlflow_available
    if _mlflow_available is None:
        try:
            import mlflow

            _mlflow = mlflow
            _mlflow_available = True
        except ImportError:
            _mlflow_available = False
            logger.warning("MLflow not installed. Install with: pip install mlflow")
    return _mlflow if _mlflow_available else None


# Default configuration
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
MLFLOW_EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "oideachais-celtic-education")


def init_mlflow(
    tracking_uri: str | None = None,
    experiment_name: str | None = None,
) -> bool:
    """
    Initialize MLflow tracking.

    Args:
        tracking_uri: MLflow server URI (default: MLFLOW_TRACKING_URI env var)
        experiment_name: Experiment name (default: MLFLOW_EXPERIMENT_NAME env var)

    Returns:
        True if initialization successful, False otherwise.
    """
    mlflow = _get_mlflow()
    if mlflow is None:
        return False

    uri = tracking_uri or MLFLOW_TRACKING_URI
    experiment = experiment_name or MLFLOW_EXPERIMENT_NAME

    try:
        mlflow.set_tracking_uri(uri)
        mlflow.set_experiment(experiment)
        logger.info(f"MLflow initialized: tracking_uri={uri}, experiment={experiment}")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize MLflow: {e}")
        return False


@contextmanager
def mlflow_run(
    run_name: str | None = None,
    tags: dict[str, str] | None = None,
    nested: bool = False,
):
    """
    Context manager for MLflow run tracking.

    Args:
        run_name: Name for the run
        tags: Optional tags for the run
        nested: Whether this is a nested run

    Yields:
        MLflow run object if available, None otherwise.

    Example:
        with mlflow_run("agent_evaluation", tags={"agent": "curriculum_search"}):
            mlflow.log_param("query", query)
            mlflow.log_metric("latency_ms", 150)
    """
    mlflow = _get_mlflow()
    if mlflow is None:
        yield None
        return

    default_tags = {
        "pipeline": "oideachais",
        "environment": os.getenv("DD_ENV", "development"),
    }
    if tags:
        default_tags.update(tags)

    try:
        with mlflow.start_run(run_name=run_name, tags=default_tags, nested=nested) as run:
            yield run
    except Exception as e:
        logger.error(f"MLflow run failed: {e}")
        yield None


def log_agent_metrics(
    agent_name: str,
    query: str,
    response_length: int,
    latency_ms: float,
    token_count: int | None = None,
    success: bool = True,
    metadata: dict[str, Any] | None = None,
):
    """
    Log agent execution metrics to MLflow.

    Args:
        agent_name: Name of the agent
        query: User query
        response_length: Length of agent response
        latency_ms: Response latency in milliseconds
        token_count: Optional token count
        success: Whether the request was successful
        metadata: Additional metadata to log
    """
    mlflow = _get_mlflow()
    if mlflow is None:
        return

    try:
        # Log parameters
        mlflow.log_param("agent_name", agent_name)
        mlflow.log_param("query_length", len(query))
        mlflow.log_param("success", success)

        # Log metrics
        mlflow.log_metric("response_length", response_length)
        mlflow.log_metric("latency_ms", latency_ms)
        if token_count:
            mlflow.log_metric("token_count", token_count)

        # Log additional metadata
        if metadata:
            for key, value in metadata.items():
                if isinstance(value, (int, float)):
                    mlflow.log_metric(key, value)
                else:
                    mlflow.log_param(key, str(value)[:250])  # Truncate long values

    except Exception as e:
        logger.warning(f"Failed to log agent metrics: {e}")


def log_search_metrics(
    query: str,
    num_results: int,
    latency_ms: float,
    top_score: float | None = None,
    filters: dict[str, Any] | None = None,
):
    """
    Log search/retrieval metrics to MLflow.

    Args:
        query: Search query
        num_results: Number of results returned
        latency_ms: Search latency in milliseconds
        top_score: Score of top result
        filters: Applied search filters
    """
    mlflow = _get_mlflow()
    if mlflow is None:
        return

    try:
        mlflow.log_param("query", query[:500])  # Truncate
        mlflow.log_metric("num_results", num_results)
        mlflow.log_metric("search_latency_ms", latency_ms)
        if top_score is not None:
            mlflow.log_metric("top_score", top_score)
        if filters:
            for key, value in filters.items():
                if value is not None:
                    mlflow.log_param(f"filter_{key}", str(value))

    except Exception as e:
        logger.warning(f"Failed to log search metrics: {e}")


def log_evaluation_results(
    evaluation_name: str,
    scores: dict[str, float],
    dataset_size: int | None = None,
    artifacts: dict[str, Any] | None = None,
):
    """
    Log evaluation results to MLflow.

    Args:
        evaluation_name: Name of the evaluation run
        scores: Dictionary of metric scores (e.g., faithfulness, relevancy)
        dataset_size: Size of evaluation dataset
        artifacts: Artifacts to log (e.g., predictions, errors)
    """
    mlflow = _get_mlflow()
    if mlflow is None:
        return

    try:
        mlflow.log_param("evaluation_name", evaluation_name)
        if dataset_size:
            mlflow.log_param("dataset_size", dataset_size)

        # Log scores as metrics
        for metric_name, score in scores.items():
            mlflow.log_metric(metric_name, score)

        # Log artifacts
        if artifacts:
            import json
            import tempfile

            for name, data in artifacts.items():
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".json", delete=False
                ) as f:
                    json.dump(data, f, indent=2, default=str)
                    mlflow.log_artifact(f.name, artifact_path=name)

    except Exception as e:
        logger.warning(f"Failed to log evaluation results: {e}")


def track_agent_run(agent_name: str):
    """
    Decorator to track agent execution with MLflow.

    Args:
        agent_name: Name of the agent to track.

    Example:
        @track_agent_run("curriculum_search")
        async def search_curriculum(query: str):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            import time

            mlflow = _get_mlflow()
            if mlflow is None:
                return await func(*args, **kwargs)

            start_time = time.time()
            success = True
            result = None

            try:
                with mlflow_run(
                    run_name=f"{agent_name}_run",
                    tags={"agent": agent_name, "type": "agent_execution"},
                ):
                    result = await func(*args, **kwargs)
                    return result
            except Exception:
                success = False
                raise
            finally:
                latency_ms = (time.time() - start_time) * 1000
                try:
                    log_agent_metrics(
                        agent_name=agent_name,
                        query=str(kwargs.get("query", args[0] if args else ""))[:500],
                        response_length=len(str(result)) if result else 0,
                        latency_ms=latency_ms,
                        success=success,
                    )
                except Exception:
                    pass

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            import time

            mlflow = _get_mlflow()
            if mlflow is None:
                return func(*args, **kwargs)

            start_time = time.time()
            success = True
            result = None

            try:
                with mlflow_run(
                    run_name=f"{agent_name}_run",
                    tags={"agent": agent_name, "type": "agent_execution"},
                ):
                    result = func(*args, **kwargs)
                    return result
            except Exception:
                success = False
                raise
            finally:
                latency_ms = (time.time() - start_time) * 1000
                try:
                    log_agent_metrics(
                        agent_name=agent_name,
                        query=str(kwargs.get("query", args[0] if args else ""))[:500],
                        response_length=len(str(result)) if result else 0,
                        latency_ms=latency_ms,
                        success=success,
                    )
                except Exception:
                    pass

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


# Pre-defined experiment configurations
EXPERIMENTS = {
    # Core agent experiments
    "agent_evaluation": {
        "name": "oideachais-agent-evaluation",
        "description": "Evaluation of ADK agents for curriculum search",
    },
    "rag_quality": {
        "name": "oideachais-rag-quality",
        "description": "RAG pipeline quality metrics with Ragas",
    },
    "embedding_comparison": {
        "name": "oideachais-embedding-comparison",
        "description": "Embedding model comparison for curriculum documents",
    },
    "prompt_optimization": {
        "name": "oideachais-prompt-optimization",
        "description": "Agent prompt A/B testing and optimization",
    },
    "bilingual_alignment": {
        "name": "oideachais-bilingual-alignment",
        "description": "English-Irish sentence alignment quality metrics",
    },
    # ML Training experiments (Phase 4)
    "htr": {
        "name": "oideachais-htr",
        "description": "Irish handwriting recognition (PyLaia HTR)",
        "metrics": ["cer", "wer", "accuracy", "val_loss"],
        "model_registry": "pylaia-irish-htr",
    },
    "tts": {
        "name": "oideachais-tts",
        "description": "Irish dialect text-to-speech (Chatterbox TTS)",
        "metrics": ["mos_score", "mel_loss", "duration_loss"],
        "model_registry": "chatterbox-irish-tts",
    },
    "curriculum": {
        "name": "oideachais-curriculum",
        "description": "Bilingual curriculum LLM (UCCIX fine-tuning)",
        "metrics": ["train_loss", "eval_loss", "perplexity", "irlbench_score"],
        "model_registry": "irish-curriculum-llm",
    },
    "rag": {
        "name": "oideachais-rag",
        "description": "RAG evaluation with Ragas metrics",
        "metrics": ["faithfulness", "answer_relevancy", "context_precision", "context_recall"],
    },
    "ocr": {
        "name": "oideachais-ocr",
        "description": "Document extraction (Granite-Docling fine-tuning)",
        "metrics": ["cer", "table_f1", "layout_accuracy"],
        "model_registry": "granite-docling-irish",
    },
}


def setup_experiment(experiment_key: str) -> str | None:
    """
    Set up MLflow experiment by key.

    Args:
        experiment_key: Key from EXPERIMENTS dict

    Returns:
        Experiment name if successful, None otherwise.
    """
    mlflow = _get_mlflow()
    if mlflow is None:
        return None

    if experiment_key not in EXPERIMENTS:
        logger.warning(f"Unknown experiment key: {experiment_key}")
        return None

    exp_config = EXPERIMENTS[experiment_key]
    exp_name = exp_config["name"]

    try:
        mlflow.set_experiment(exp_name)
        logger.info(f"MLflow experiment set: {exp_name}")
        return exp_name
    except Exception as e:
        logger.error(f"Failed to set experiment: {e}")
        return None


def log_model_to_registry(
    model_name: str,
    model_path: str,
    metrics: dict[str, float],
    tags: dict[str, str] | None = None,
    description: str | None = None,
):
    """
    Log trained model to MLflow Model Registry.

    Args:
        model_name: Name for the registered model
        model_path: Path to model artifacts
        metrics: Model performance metrics
        tags: Optional tags
        description: Optional model description
    """
    mlflow = _get_mlflow()
    if mlflow is None:
        return

    try:
        # Log model
        with mlflow.start_run():
            # Log metrics
            for name, value in metrics.items():
                mlflow.log_metric(name, value)

            # Log tags
            if tags:
                for key, value in tags.items():
                    mlflow.set_tag(key, value)

            # Log model artifact
            mlflow.log_artifacts(model_path, artifact_path="model")

            # Register model
            model_uri = f"runs:/{mlflow.active_run().info.run_id}/model"
            result = mlflow.register_model(model_uri, model_name)

            if description:
                from mlflow.tracking import MlflowClient
                client = MlflowClient()
                client.update_model_version(
                    name=model_name,
                    version=result.version,
                    description=description,
                )

            logger.info(f"Model registered: {model_name} v{result.version}")

    except Exception as e:
        logger.error(f"Failed to register model: {e}")


def get_experiment(experiment_key: str) -> str:
    """
    Get experiment name by key.

    Args:
        experiment_key: Key from EXPERIMENTS dict

    Returns:
        Experiment name string
    """
    if experiment_key in EXPERIMENTS:
        return EXPERIMENTS[experiment_key]["name"]
    return MLFLOW_EXPERIMENT_NAME
