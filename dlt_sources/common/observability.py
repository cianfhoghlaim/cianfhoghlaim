"""Shared DLT run observability for DuckLake, MLflow, and Langfuse."""

from __future__ import annotations

import os
import time
from contextlib import AbstractContextManager, nullcontext
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class DltRunConfig:
    pipeline_name: str
    dataset_name: str
    table_name: str
    tracking_uri: str = field(
        default_factory=lambda: os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5050")
    )
    experiment_name: str = field(
        default_factory=lambda: os.getenv("MLFLOW_EXPERIMENT_NAME", "dlt-pipelines")
    )
    langfuse_enabled: bool = True
    mlflow_enabled: bool = True


@dataclass(frozen=True, slots=True)
class DltRunReceipt:
    pipeline_name: str
    dataset_name: str
    table_name: str
    row_count: int
    load_id: str | None
    mlflow_run_id: str | None
    langfuse_trace_id: str | None
    duration_ms: float


class DltRunObserver:
    """Instrument one DLT run without making telemetry a load dependency."""

    def __init__(self, config: DltRunConfig) -> None:
        self.config = config
        self._started_at = 0.0
        self._mlflow: Any | None = None
        self._mlflow_run: Any | None = None
        self._langfuse: Any | None = None
        self._langfuse_observation: Any | None = None
        self._langfuse_context: AbstractContextManager[Any] = nullcontext()

    def __enter__(self) -> DltRunObserver:
        self._started_at = time.perf_counter()
        self._start_mlflow()
        self._start_langfuse()
        return self

    def record(self, *, row_count: int, load_info: Any) -> DltRunReceipt:
        duration_ms = (time.perf_counter() - self._started_at) * 1_000
        load_id = _load_id(load_info)
        attributes = self._attributes(load_id=load_id, row_count=row_count)
        if self._mlflow is not None and self._mlflow_run is not None:
            self._mlflow.log_metrics(
                {
                    "dlt.rows_loaded": float(row_count),
                    "dlt.duration_ms": duration_ms,
                    "dlt.success": 1.0,
                }
            )
            self._mlflow.set_tags(attributes)
        if self._langfuse_observation is not None:
            self._langfuse_observation.update(
                output={"row_count": row_count, "load_id": load_id},
                metadata={**attributes, "duration_ms": duration_ms},
            )
        return DltRunReceipt(
            pipeline_name=self.config.pipeline_name,
            dataset_name=self.config.dataset_name,
            table_name=self.config.table_name,
            row_count=row_count,
            load_id=load_id,
            mlflow_run_id=_run_id(self._mlflow_run),
            langfuse_trace_id=_trace_id(self._langfuse_observation),
            duration_ms=duration_ms,
        )

    def __exit__(self, exc_type: Any, exc: BaseException | None, traceback: Any) -> bool:
        if exc is not None:
            duration_ms = (time.perf_counter() - self._started_at) * 1_000
            if self._mlflow is not None and self._mlflow_run is not None:
                self._mlflow.log_metrics({"dlt.duration_ms": duration_ms, "dlt.success": 0.0})
                self._mlflow.set_tag("dlt.error", str(exc)[:500])
            if self._langfuse_observation is not None:
                self._langfuse_observation.update(
                    level="ERROR", status_message=str(exc), metadata={"duration_ms": duration_ms}
                )
        self._langfuse_context.__exit__(exc_type, exc, traceback)
        if self._langfuse is not None:
            self._langfuse.flush()
        if self._mlflow is not None and self._mlflow_run is not None:
            self._mlflow.end_run(status="FAILED" if exc is not None else "FINISHED")
        return False

    def _attributes(self, *, load_id: str | None, row_count: int) -> dict[str, str]:
        return {
            "component": "dlt",
            "pipeline_name": self.config.pipeline_name,
            "dataset_name": self.config.dataset_name,
            "table_name": self.config.table_name,
            "load_id": load_id or "unknown",
            "row_count": str(row_count),
        }

    def _start_mlflow(self) -> None:
        if not self.config.mlflow_enabled:
            return
        try:
            import mlflow

            mlflow.set_tracking_uri(self.config.tracking_uri)
            mlflow.set_experiment(self.config.experiment_name)
            self._mlflow_run = mlflow.start_run(
                run_name=self.config.pipeline_name,
                tags=self._attributes(load_id=None, row_count=0),
            )
            self._mlflow = mlflow
        except Exception:  # observability must not make the DLT load fail
            self._mlflow = None
            self._mlflow_run = None

    def _start_langfuse(self) -> None:
        if not self.config.langfuse_enabled:
            return
        if not os.getenv("LANGFUSE_PUBLIC_KEY") or not os.getenv("LANGFUSE_SECRET_KEY"):
            return
        try:
            from langfuse import get_client

            self._langfuse = get_client()
            self._langfuse_context = self._langfuse.start_as_current_observation(
                name=self.config.pipeline_name,
                as_type="span",
                input={"dataset_name": self.config.dataset_name, "table_name": self.config.table_name},
                metadata=self._attributes(load_id=None, row_count=0),
            )
            self._langfuse_observation = self._langfuse_context.__enter__()
        except Exception:  # observability must not make the DLT load fail
            self._langfuse = None
            self._langfuse_observation = None
            self._langfuse_context = nullcontext()


def _load_id(load_info: Any) -> str | None:
    load_ids = getattr(load_info, "loads_ids", None)
    return str(load_ids[-1]) if isinstance(load_ids, list) and load_ids else None


def _run_id(run: Any | None) -> str | None:
    run_id = getattr(getattr(run, "info", None), "run_id", None)
    return str(run_id) if run_id is not None else None


def _trace_id(observation: Any | None) -> str | None:
    trace_id = getattr(observation, "trace_id", None) or getattr(observation, "id", None)
    return str(trace_id) if trace_id is not None else None


__all__ = ["DltRunConfig", "DltRunObserver", "DltRunReceipt"]
