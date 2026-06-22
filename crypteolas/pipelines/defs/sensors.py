"""
Sensor definitions for triggering indexing after ingestion.

Monitors DLT ingestion completion and triggers indexing pipeline.
"""

from __future__ import annotations

from datetime import datetime

from dagster import (
    asset_sensor,
    AssetKey,
    EventLogEntry,
    RunRequest,
    SensorEvaluationContext,
    SkipReason,
)


@asset_sensor(
    asset_key=AssetKey(["crawl_dlt-hub"]),
    name="indexing_trigger_sensor",
    job_name="full_indexing_pipeline",
    minimum_interval_seconds=300,  # Check every 5 minutes
)
def indexing_trigger_sensor(
    context: SensorEvaluationContext,
    asset_event: EventLogEntry,
):
    """Trigger indexing when new documentation is ingested.

    Monitors crawl assets and triggers the full indexing pipeline
    when new documentation is available.

    Args:
        context: Sensor evaluation context
        asset_event: The asset materialization event

    Returns:
        RunRequest to trigger indexing or SkipReason
    """
    context.log.info(f"Detected new documentation at {asset_event.timestamp}")

    return RunRequest(
        run_key=f"indexing_{datetime.now().isoformat()}",
        tags={
            "triggered_by": "ingestion_sensor",
            "trigger_event": str(asset_event.dagster_event_type),
        },
    )


@asset_sensor(
    asset_key=AssetKey("docs_graph_index"),
    name="knowledge_graph_trigger_sensor",
    job_name="knowledge_graph_pipeline",
    minimum_interval_seconds=600,  # Check every 10 minutes
)
def knowledge_graph_trigger_sensor(
    context: SensorEvaluationContext,
    asset_event: EventLogEntry,
):
    """Trigger knowledge graph processing after graph indexing.

    Monitors docs_graph_index completion and triggers Cognee and
    Graphiti processing.

    Args:
        context: Sensor evaluation context
        asset_event: The asset materialization event

    Returns:
        RunRequest to trigger knowledge graph processing
    """
    return RunRequest(
        run_key=f"knowledge_{datetime.now().isoformat()}",
        tags={"triggered_by": "graph_index_sensor"},
    )


# List of all sensors
indexing_sensors = [
    indexing_trigger_sensor,
    knowledge_graph_trigger_sensor,
]
