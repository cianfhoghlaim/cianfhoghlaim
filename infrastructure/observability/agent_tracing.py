"""
Agent-level tracing for Google ADK with Datadog LLM Observability.

Instruments:
- ADK agent runs with workflow spans
- Tool calls with task spans
- LLM completions with llm spans
"""

import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

logger = logging.getLogger(__name__)

# Lazy imports
_statsd = None


def _get_statsd():
    """Lazy load statsd client."""
    global _statsd
    if _statsd is None:
        try:
            from datadog import statsd

            _statsd = statsd
        except ImportError:
            pass
    return _statsd


def trace_adk_agent(agent_name: str) -> Callable:
    """
    Decorator to trace Google ADK agent execution.

    Captures:
    - Agent workflow duration
    - Input/output messages
    - Token usage (estimated)
    - Error states

    Usage:
        @trace_adk_agent("curriculum_search")
        async def run_agent(message: str) -> str:
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            input_message = kwargs.get("message", args[0] if args else "")
            statsd = _get_statsd()

            # Try to get LLMObs for annotation
            try:
                from ddtrace.llmobs import LLMObs
                from ddtrace.llmobs.decorators import workflow

                @workflow(name=f"adk_agent.{agent_name}")
                async def traced_func(*args, **kwargs):
                    # Annotate input
                    LLMObs.annotate(
                        input_data=str(input_message)[:1000],
                        metadata={
                            "agent_name": agent_name,
                            "model": kwargs.get("model", "gemini-2.0-flash"),
                            "education_level": kwargs.get("education_level"),
                            "subject": kwargs.get("subject"),
                        },
                        tags={
                            "language": "bilingual",
                            "pipeline": "celtic-education",
                        },
                    )

                    result = await func(*args, **kwargs)

                    # Calculate metrics
                    duration_ms = (time.time() - start_time) * 1000
                    token_estimate = len(str(result).split()) * 1.3

                    # Annotate output
                    LLMObs.annotate(
                        output_data=str(result)[:1000],
                        metrics={
                            "duration_ms": duration_ms,
                            "estimated_tokens": token_estimate,
                        },
                    )

                    return result

                result = await traced_func(*args, **kwargs)

            except ImportError:
                # Fall back to untraced execution
                result = await func(*args, **kwargs)

            # Always emit metrics
            duration_ms = (time.time() - start_time) * 1000
            if statsd:
                statsd.histogram(
                    "oideachais.agent.latency",
                    duration_ms,
                    tags=[f"agent:{agent_name}"],
                )
                statsd.increment(
                    "oideachais.agent.requests",
                    tags=[f"agent:{agent_name}", "status:success"],
                )

            return result

        return wrapper

    return decorator


def trace_tool_call(tool_name: str) -> Callable:
    """
    Decorator to trace ADK tool calls.

    Usage:
        @trace_tool_call("search_curriculum")
        def search_curriculum(tool_context, query: str) -> list:
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            statsd = _get_statsd()

            try:
                from ddtrace.llmobs import LLMObs
                from ddtrace.llmobs.decorators import task

                @task(name=f"tool.{tool_name}")
                def traced_func(*args, **kwargs):
                    import json

                    LLMObs.annotate(
                        input_data=json.dumps(kwargs, default=str)[:500],
                        metadata={"tool_name": tool_name},
                    )

                    result = func(*args, **kwargs)

                    duration_ms = (time.time() - start_time) * 1000
                    LLMObs.annotate(
                        output_data=json.dumps(result, default=str)[:500] if result else "",
                        metrics={"duration_ms": duration_ms},
                    )

                    return result

                result = traced_func(*args, **kwargs)

            except ImportError:
                result = func(*args, **kwargs)

            # Emit metrics
            duration_ms = (time.time() - start_time) * 1000
            if statsd:
                statsd.histogram(
                    "oideachais.tool.latency",
                    duration_ms,
                    tags=[f"tool:{tool_name}"],
                )

            return result

        return wrapper

    return decorator


class GeminiLLMSpan:
    """
    Context manager for tracing Gemini LLM calls.

    Usage:
        with GeminiLLMSpan(model="gemini-2.0-flash", prompt=user_message) as span:
            response = model.generate_content(user_message)
            span.set_response(response)
    """

    def __init__(self, model: str, prompt: str, **metadata):
        self.model = model
        self.prompt = prompt
        self.metadata = metadata
        self.start_time = None
        self._span = None
        self._llmobs = None

    def __enter__(self):
        self.start_time = time.time()

        try:
            from ddtrace.llmobs import LLMObs

            self._llmobs = LLMObs
            self._span = LLMObs.llm(
                model_name=self.model,
                model_provider="google",
                name=f"gemini.{self.model}",
            )
            self._span.__enter__()

            LLMObs.annotate(
                input_data=[{"role": "user", "content": self.prompt[:2000]}],
                metadata=self.metadata,
            )
        except ImportError:
            pass

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and self._llmobs:
            self._llmobs.annotate(metadata={"error": str(exc_val)})

        if self._span:
            self._span.__exit__(exc_type, exc_val, exc_tb)

    def set_response(
        self, response: Any, input_tokens: int | None = None, output_tokens: int | None = None
    ):
        """Set the LLM response and token metrics."""
        duration_ms = (time.time() - self.start_time) * 1000

        # Extract text from Gemini response
        if hasattr(response, "text"):
            output_text = response.text
        elif hasattr(response, "candidates") and response.candidates:
            output_text = response.candidates[0].content.parts[0].text
        else:
            output_text = str(response)

        # Estimate tokens if not provided
        _input_tokens = input_tokens or len(self.prompt.split())
        _output_tokens = output_tokens or len(output_text.split())

        if self._llmobs:
            self._llmobs.annotate(
                output_data=[{"role": "assistant", "content": output_text[:2000]}],
                metrics={
                    "input_tokens": _input_tokens,
                    "output_tokens": _output_tokens,
                    "total_tokens": _input_tokens + _output_tokens,
                },
            )

        # Report to statsd
        statsd = _get_statsd()
        if statsd:
            statsd.histogram("oideachais.llm.latency", duration_ms, tags=[f"model:{self.model}"])
            statsd.histogram(
                "oideachais.llm.tokens.input", _input_tokens, tags=[f"model:{self.model}"]
            )
            statsd.histogram(
                "oideachais.llm.tokens.output", _output_tokens, tags=[f"model:{self.model}"]
            )


# =============================================================================
# ML Pipeline Metrics (Phase 4 - Observability)
# =============================================================================

class MLPipelineMetrics:
    """
    Custom metrics for ML training and data pipelines.

    Metrics defined in plan:
    - ml.htr.accuracy - HTR character error rate
    - ml.tts.mos_score - TTS quality metric
    - pipeline.duchas.pages_scraped - Scraping progress
    - pipeline.embeddings.batch_size - Embedding throughput
    """

    def __init__(self):
        self._statsd = None

    @property
    def statsd(self):
        if self._statsd is None:
            self._statsd = _get_statsd()
        return self._statsd

    # HTR Metrics
    def record_htr_accuracy(
        self,
        cer: float,
        wer: float | None = None,
        model: str = "pylaia-irish",
        dialect: str | None = None,
    ):
        """Record HTR model accuracy metrics."""
        if not self.statsd:
            return

        tags = [f"model:{model}"]
        if dialect:
            tags.append(f"dialect:{dialect}")

        self.statsd.gauge("ml.htr.cer", cer, tags=tags)
        self.statsd.gauge("ml.htr.accuracy", 1.0 - cer, tags=tags)
        if wer is not None:
            self.statsd.gauge("ml.htr.wer", wer, tags=tags)

    def record_htr_training_step(
        self,
        epoch: int,
        loss: float,
        val_cer: float | None = None,
        learning_rate: float | None = None,
    ):
        """Record HTR training progress."""
        if not self.statsd:
            return

        self.statsd.gauge("ml.htr.training.epoch", epoch)
        self.statsd.gauge("ml.htr.training.loss", loss)
        if val_cer is not None:
            self.statsd.gauge("ml.htr.training.val_cer", val_cer)
        if learning_rate is not None:
            self.statsd.gauge("ml.htr.training.lr", learning_rate)

    # TTS Metrics
    def record_tts_quality(
        self,
        mos_score: float,
        dialect: str = "connacht",
        speaker_id: str | None = None,
    ):
        """Record TTS Mean Opinion Score quality metric."""
        if not self.statsd:
            return

        tags = [f"dialect:{dialect}"]
        if speaker_id:
            tags.append(f"speaker:{speaker_id}")

        self.statsd.gauge("ml.tts.mos_score", mos_score, tags=tags)

    def record_tts_synthesis(
        self,
        duration_ms: float,
        text_length: int,
        audio_duration_sec: float,
        dialect: str = "connacht",
    ):
        """Record TTS synthesis metrics."""
        if not self.statsd:
            return

        tags = [f"dialect:{dialect}"]
        rtf = duration_ms / (audio_duration_sec * 1000) if audio_duration_sec > 0 else 0

        self.statsd.histogram("ml.tts.synthesis.latency_ms", duration_ms, tags=tags)
        self.statsd.histogram("ml.tts.synthesis.rtf", rtf, tags=tags)
        self.statsd.histogram("ml.tts.synthesis.text_length", text_length, tags=tags)

    # Pipeline Metrics - Dúchas
    def record_duchas_scrape(
        self,
        pages_scraped: int,
        images_downloaded: int,
        county: str | None = None,
        success: bool = True,
    ):
        """Record Dúchas.ie scraping progress."""
        if not self.statsd:
            return

        tags = ["status:success" if success else "status:failed"]
        if county:
            tags.append(f"county:{county}")

        self.statsd.increment("pipeline.duchas.pages_scraped", pages_scraped, tags=tags)
        self.statsd.increment("pipeline.duchas.images_downloaded", images_downloaded, tags=tags)

    def record_duchas_transcription(
        self,
        page_id: str,
        confidence: float,
        text_length: int,
    ):
        """Record Dúchas transcription metrics."""
        if not self.statsd:
            return

        self.statsd.increment("pipeline.duchas.transcriptions")
        self.statsd.histogram("pipeline.duchas.transcription.confidence", confidence)
        self.statsd.histogram("pipeline.duchas.transcription.text_length", text_length)

    # Pipeline Metrics - SEC Exams
    def record_sec_extraction(
        self,
        papers_extracted: int,
        subject: str,
        year: int,
        level: str = "higher",
    ):
        """Record SEC exam paper extraction."""
        if not self.statsd:
            return

        tags = [f"subject:{subject}", f"year:{year}", f"level:{level}"]
        self.statsd.increment("pipeline.sec.papers_extracted", papers_extracted, tags=tags)

    # Pipeline Metrics - Canúint Audio
    def record_canuint_download(
        self,
        recordings_downloaded: int,
        duration_hours: float,
        dialect: str,
    ):
        """Record Canúint.ie audio download progress."""
        if not self.statsd:
            return

        tags = [f"dialect:{dialect}"]
        self.statsd.increment("pipeline.canuint.recordings", recordings_downloaded, tags=tags)
        self.statsd.gauge("pipeline.canuint.duration_hours", duration_hours, tags=tags)

    # Embedding Metrics
    def record_embedding_batch(
        self,
        batch_size: int,
        latency_ms: float,
        model: str = "bge-m3",
        source: str = "curriculum",
    ):
        """Record embedding batch processing metrics."""
        if not self.statsd:
            return

        tags = [f"model:{model}", f"source:{source}"]

        self.statsd.histogram("pipeline.embeddings.batch_size", batch_size, tags=tags)
        self.statsd.histogram("pipeline.embeddings.latency_ms", latency_ms, tags=tags)
        self.statsd.histogram(
            "pipeline.embeddings.throughput",
            batch_size / (latency_ms / 1000) if latency_ms > 0 else 0,
            tags=tags,
        )

    def record_embedding_index_operation(
        self,
        operation: str,  # "drop", "create", "rebuild"
        duration_ms: float,
        num_vectors: int,
    ):
        """Record HNSW index management operations."""
        if not self.statsd:
            return

        tags = [f"operation:{operation}"]
        self.statsd.histogram("pipeline.embeddings.index.duration_ms", duration_ms, tags=tags)
        self.statsd.gauge("pipeline.embeddings.index.vectors", num_vectors, tags=tags)

    # Curriculum LLM Metrics
    def record_curriculum_training(
        self,
        epoch: int,
        train_loss: float,
        eval_loss: float | None = None,
        perplexity: float | None = None,
    ):
        """Record curriculum LLM training metrics."""
        if not self.statsd:
            return

        self.statsd.gauge("ml.curriculum.training.epoch", epoch)
        self.statsd.gauge("ml.curriculum.training.train_loss", train_loss)
        if eval_loss is not None:
            self.statsd.gauge("ml.curriculum.training.eval_loss", eval_loss)
        if perplexity is not None:
            self.statsd.gauge("ml.curriculum.training.perplexity", perplexity)

    def record_curriculum_inference(
        self,
        latency_ms: float,
        tokens_generated: int,
        subject: str | None = None,
    ):
        """Record curriculum LLM inference metrics."""
        if not self.statsd:
            return

        tags = []
        if subject:
            tags.append(f"subject:{subject}")

        self.statsd.histogram("ml.curriculum.inference.latency_ms", latency_ms, tags=tags)
        self.statsd.histogram("ml.curriculum.inference.tokens", tokens_generated, tags=tags)


# Global metrics instance
ml_metrics = MLPipelineMetrics()
