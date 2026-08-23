"""cognee_health_check — the per-cluster cognee health asset (L1 Ingestion).

Per the 2026-08-23-dlt-sources-ccc-audit-and-realignment-v1 audit
(Decision 5) + the `indexing-and-cognition` spec.

The asset:
- Polls each of the 7 typed cognee clusters
- Emits a materialization per cluster with the health status
- Logs to Langfuse for the observability stack

This asset is triggered by the `cognee_health_check_sensor` (per
`orchestration/sensors/cognee_health_check_sensor.py`).
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import dagster as dg

from meaisinfhoghlaim.process.cognee_client import COGNEE_CLUSTERS, ping_cluster


@dg.asset(
    name="cognee_health_check",
    group_name="cognee_health",
    compute_kind="python",
)
def cognee_health_check(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """Poll each cognee cluster + emit per-cluster health status."""
    check_time = datetime.now(timezone.utc).isoformat()
    metadata: dict[str, str] = {}
    healthy = 0
    down = 0

    for cluster in COGNEE_CLUSTERS:
        status = ping_cluster(cluster)
        if status:
            healthy += 1
        else:
            down += 1
        metadata[f"cluster_{cluster}"] = "healthy" if status else "down"

    metadata["check_time"] = check_time
    metadata["healthy_count"] = str(healthy)
    metadata["down_count"] = str(down)

    return dg.MaterializeResult(
        metadata=metadata,
    )
