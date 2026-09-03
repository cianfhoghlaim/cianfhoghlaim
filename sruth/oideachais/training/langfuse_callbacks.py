"""
Langfuse Callbacks for Celtic Education Training.

Provides LLM cost tracking and tracing for fine-tuning runs:
- Token usage tracking across training steps
- Cost estimation per model/run
- Generation quality sampling
- Integration with existing MLflow callbacks

Usage:
    from training import LangfuseTrainingCallback, GaelicOCRMLflowCallback

    langfuse_callback = LangfuseTrainingCallback()
    mlflow_callback = GaelicOCRMLflowCallback(...)

    trainer = UnslothTrainer(config, callbacks=[mlflow_callback, langfuse_callback])
    trainer.train()
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from transformers import TrainerCallback, TrainerControl, TrainerState
from transformers.training_args import TrainingArguments

logger = logging.getLogger(__name__)

# Lazy import Langfuse
_langfuse_client = None


def _get_langfuse():
    """Lazy load Langfuse client."""
    global _langfuse_client
    if _langfuse_client is None:
        try:
            from langfuse import Langfuse

            _langfuse_client = Langfuse(
                public_key=os.getenv("LANGFUSE_PUBLIC_KEY", ""),
                secret_key=os.getenv("LANGFUSE_SECRET_KEY", ""),
                host=os.getenv("LANGFUSE_HOST", "http://localhost:3000"),
            )
        except ImportError:
            logger.warning("Langfuse not installed")
            return None
        except Exception as e:
            logger.warning(f"Failed to initialize Langfuse: {e}")
            return None
    return _langfuse_client


@dataclass
class TrainingCostEstimate:
    """Estimated costs for a training run."""

    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    estimated_cost_usd: float = 0.0
    model_name: str = ""
    training_steps: int = 0
    epochs: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_tokens": self.total_tokens,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "estimated_cost_usd": round(self.estimated_cost_usd, 4),
            "model_name": self.model_name,
            "training_steps": self.training_steps,
            "epochs": self.epochs,
        }


# Cost estimates per 1K tokens (approximate)
MODEL_COSTS = {
    "gemini-2.0-flash": {"input": 0.0001, "output": 0.0004},
    "gemini-2.5-flash": {"input": 0.00015, "output": 0.0006},
    "gemini-2.5-pro": {"input": 0.00125, "output": 0.005},
    "claude-sonnet": {"input": 0.003, "output": 0.015},
    "claude-haiku": {"input": 0.00025, "output": 0.00125},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "qwen3-vl": {"input": 0.0, "output": 0.0},  # Local model
    "olmocr2": {"input": 0.0, "output": 0.0},  # Local model
}


class LangfuseTrainingCallback(TrainerCallback):
    """
    Langfuse callback for training cost tracking.

    Tracks:
    - Token usage per training step
    - Estimated costs based on model
    - Generation samples for quality assessment
    - Training progress metrics
    """

    def __init__(
        self,
        model_name: str = "qwen3-vl",
        project_name: str = "oideachas-training",
        log_every_n_steps: int = 100,
        log_generations: bool = True,
    ):
        """
        Initialize Langfuse callback.

        Args:
            model_name: Name of the model being trained
            project_name: Langfuse project name
            log_every_n_steps: Log metrics every N steps
            log_generations: Whether to log sample generations
        """
        self.model_name = model_name
        self.project_name = project_name
        self.log_every_n_steps = log_every_n_steps
        self.log_generations = log_generations

        self._trace = None
        self._session_id = None
        self._cost_estimate = TrainingCostEstimate(model_name=model_name)
        self._start_time = None

    def on_train_begin(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs,
    ) -> None:
        """Called at the start of training."""
        langfuse = _get_langfuse()
        if langfuse is None:
            return

        self._start_time = datetime.now()
        self._session_id = f"training_{self._start_time.strftime('%Y%m%d_%H%M%S')}"

        try:
            self._trace = langfuse.trace(
                name=f"training_{self.model_name}",
                session_id=self._session_id,
                metadata={
                    "model_name": self.model_name,
                    "project": self.project_name,
                    "training_started": self._start_time.isoformat(),
                    "max_steps": state.max_steps,
                    "num_train_epochs": args.num_train_epochs,
                    "per_device_train_batch_size": args.per_device_train_batch_size,
                    "gradient_accumulation_steps": args.gradient_accumulation_steps,
                },
                tags=["training", "celtic-education", self.model_name],
            )
            logger.info(f"Langfuse training trace started: {self._session_id}")
        except Exception as e:
            logger.warning(f"Failed to create Langfuse trace: {e}")

    def on_log(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        logs: dict[str, float] | None = None,
        **kwargs,
    ) -> None:
        """Called when logging metrics."""
        if logs is None or self._trace is None:
            return

        langfuse = _get_langfuse()
        if langfuse is None:
            return

        # Only log every N steps
        if state.global_step % self.log_every_n_steps != 0:
            return

        try:
            # Create span for this logging event
            span = self._trace.span(
                name=f"step_{state.global_step}",
                metadata={
                    "step": state.global_step,
                    "epoch": state.epoch,
                },
            )

            # Log metrics
            for key, value in logs.items():
                if isinstance(value, (int, float)):
                    span.update(metadata={key: value})

            # Track token estimates (approximation based on batch size)
            batch_tokens = args.per_device_train_batch_size * 512  # Approximate tokens per sample
            self._cost_estimate.total_tokens += batch_tokens
            self._cost_estimate.prompt_tokens += batch_tokens
            self._cost_estimate.training_steps = state.global_step

            span.end()

        except Exception as e:
            logger.warning(f"Failed to log to Langfuse: {e}")

    def on_evaluate(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        metrics: dict[str, float] | None = None,
        **kwargs,
    ) -> None:
        """Called after evaluation."""
        if metrics is None or self._trace is None:
            return

        langfuse = _get_langfuse()
        if langfuse is None:
            return

        try:
            # Create evaluation span
            span = self._trace.span(
                name=f"eval_step_{state.global_step}",
                metadata={
                    "type": "evaluation",
                    "step": state.global_step,
                    "metrics": metrics,
                },
            )

            # Add scores for key metrics
            if "eval_loss" in metrics:
                langfuse.score(
                    trace_id=self._trace.id,
                    name="eval_loss",
                    value=metrics["eval_loss"],
                )

            if "eval_cer" in metrics:
                langfuse.score(
                    trace_id=self._trace.id,
                    name="character_error_rate",
                    value=metrics["eval_cer"],
                )

            span.end()

        except Exception as e:
            logger.warning(f"Failed to log evaluation to Langfuse: {e}")

    def on_train_end(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs,
    ) -> None:
        """Called at end of training."""
        if self._trace is None:
            return

        langfuse = _get_langfuse()
        if langfuse is None:
            return

        # Calculate final cost estimate
        self._cost_estimate.epochs = state.epoch or 0.0
        self._cost_estimate.training_steps = state.global_step

        model_costs = MODEL_COSTS.get(self.model_name, {"input": 0.0, "output": 0.0})
        self._cost_estimate.estimated_cost_usd = (
            (self._cost_estimate.prompt_tokens / 1000) * model_costs["input"] +
            (self._cost_estimate.completion_tokens / 1000) * model_costs["output"]
        )

        try:
            # Update trace with final metrics
            self._trace.update(
                metadata={
                    "training_completed": datetime.now().isoformat(),
                    "total_steps": state.global_step,
                    "final_epoch": state.epoch,
                    "best_metric": state.best_metric,
                    "cost_estimate": self._cost_estimate.to_dict(),
                },
            )

            # Add final scores
            if state.best_metric is not None:
                langfuse.score(
                    trace_id=self._trace.id,
                    name="best_metric",
                    value=state.best_metric,
                )

            langfuse.score(
                trace_id=self._trace.id,
                name="estimated_cost_usd",
                value=self._cost_estimate.estimated_cost_usd,
            )

            # Flush to ensure all data is sent
            langfuse.flush()

            logger.info(
                f"Training complete. Estimated cost: ${self._cost_estimate.estimated_cost_usd:.4f}"
            )

        except Exception as e:
            logger.warning(f"Failed to finalize Langfuse trace: {e}")


class LangfuseGenerationCallback(TrainerCallback):
    """
    Langfuse callback for logging LLM generations during inference/evaluation.

    Use this for tracking individual generation calls, not training.
    """

    def __init__(
        self,
        model_name: str = "gemini-2.0-flash",
        session_id: str | None = None,
    ):
        self.model_name = model_name
        self.session_id = session_id or f"inference_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self._generations: list[dict] = []

    def log_generation(
        self,
        prompt: str,
        response: str,
        latency_ms: float,
        token_usage: dict[str, int] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Log a single generation to Langfuse.

        Args:
            prompt: Input prompt
            response: Model response
            latency_ms: Latency in milliseconds
            token_usage: Token usage dict
            metadata: Additional metadata
        """
        langfuse = _get_langfuse()
        if langfuse is None:
            return

        try:
            trace = langfuse.trace(
                name=f"generation_{self.model_name}",
                session_id=self.session_id,
                metadata=metadata or {},
                tags=["generation", "celtic-education"],
            )

            generation = trace.generation(
                name="llm_call",
                model=self.model_name,
                input=prompt,
                output=response,
                usage=token_usage,
                metadata={"latency_ms": latency_ms},
            )

            # Calculate cost
            model_costs = MODEL_COSTS.get(self.model_name, {"input": 0.001, "output": 0.002})
            if token_usage:
                cost = (
                    (token_usage.get("prompt_tokens", 0) / 1000) * model_costs["input"] +
                    (token_usage.get("completion_tokens", 0) / 1000) * model_costs["output"]
                )
                langfuse.score(
                    trace_id=trace.id,
                    name="cost_usd",
                    value=cost,
                )

            langfuse.flush()

            self._generations.append({
                "prompt": prompt[:100],
                "response": response[:100],
                "latency_ms": latency_ms,
                "cost_estimate": cost if token_usage else 0.0,
            })

        except Exception as e:
            logger.warning(f"Failed to log generation: {e}")

    def get_session_summary(self) -> dict[str, Any]:
        """Get summary of all generations in this session."""
        if not self._generations:
            return {"count": 0, "total_latency_ms": 0, "total_cost": 0}

        total_latency = sum(g["latency_ms"] for g in self._generations)
        total_cost = sum(g.get("cost_estimate", 0) for g in self._generations)

        return {
            "count": len(self._generations),
            "total_latency_ms": total_latency,
            "avg_latency_ms": total_latency / len(self._generations),
            "total_cost": total_cost,
        }
