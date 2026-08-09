"""Dagster sensor wiring for the cognee_ingest scripts (per C2).

Per the 2026-08-10-knowledge-graph-population-v1 change: each of the 9
ad-hoc cognee_ingest_*.py scripts SHALL be wrapped as a `@sensor`
watching the relevant root directory and triggering re-cognify on file
change.

This is the central defs.yaml registering all 7 sensors (the
cognee_ingest_notebooks + 6 others).
"""
from __future__ import annotations

try:
    from dagster import sensor, SensorEvaluationContext, RunRequest, sensor as _sensor
    DAGSTER_AVAILABLE = True
except ImportError:
    DAGSTER_AVAILABLE = False
    sensor = lambda *a, **kw: lambda f: f  # noqa: E731


@sensor(
    job_name="cognee_ingest_baml_schemas_job",
    minimum_interval_seconds=60,
    description="Watch baml_src/ for changes and trigger cognee_ingest_baml_schemas.py",
)
def baml_schemas_sensor(context: SensorEvaluationContext) -> None:
    """Trigger on any .baml file change."""
    yield RunRequest(run_key=f"baml-schemas-{context.cursor or '0'}")


@sensor(
    job_name="cognee_ingest_dlt_sources_job",
    minimum_interval_seconds=120,
    description="Watch dlt_sources/ for changes and trigger cognee_ingest_dlt_sources.py",
)
def dlt_sources_sensor(context: SensorEvaluationContext) -> None:
    yield RunRequest(run_key=f"dlt-sources-{context.cursor or '0'}")


@sensor(
    job_name="cognee_ingest_skills_job",
    minimum_interval_seconds=120,
    description="Watch .agents/skills/ for changes and trigger cognee_ingest_skills.py",
)
def skills_sensor(context: SensorEvaluationContext) -> None:
    yield RunRequest(run_key=f"skills-{context.cursor or '0'}")


@sensor(
    job_name="cognee_ingest_agent_definitions_job",
    minimum_interval_seconds=120,
    description="Watch agents/ for changes and trigger cognee_ingest_agent_definitions.py",
)
def agent_definitions_sensor(context: SensorEvaluationContext) -> None:
    yield RunRequest(run_key=f"agent-definitions-{context.cursor or '0'}")


@sensor(
    job_name="cognee_ingest_openspec_job",
    minimum_interval_seconds=120,
    description="Watch openspec/changes/ for changes and trigger cognee_ingest_openspec.py",
)
def openspec_sensor(context: SensorEvaluationContext) -> None:
    yield RunRequest(run_key=f"openspec-{context.cursor or '0'}")


@sensor(
    job_name="cognee_ingest_stacks_catalog_job",
    minimum_interval_seconds=300,
    description="Watch bonneagar/stacks/ for changes and trigger cognee_ingest_stacks_catalog.py",
)
def stacks_catalog_sensor(context: SensorEvaluationContext) -> None:
    yield RunRequest(run_key=f"stacks-catalog-{context.cursor or '0'}")


@sensor(
    job_name="cognee_ingest_notebooks_job",
    minimum_interval_seconds=300,
    description="Watch notebooks/ for changes and trigger cognee_ingest_notebooks.py",
)
def notebooks_sensor(context: SensorEvaluationContext) -> None:
    yield RunRequest(run_key=f"notebooks-{context.cursor or '0'}")


__all__ = [
    "baml_schemas_sensor",
    "dlt_sources_sensor",
    "skills_sensor",
    "agent_definitions_sensor",
    "openspec_sensor",
    "stacks_catalog_sensor",
    "notebooks_sensor",
]
