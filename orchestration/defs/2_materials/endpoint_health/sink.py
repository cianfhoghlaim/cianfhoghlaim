"""Dagster L2 asset that probes every British Isles canonical endpoint
and writes one row per probe to the ``cianfhoghlaim.endpoint_health``
DuckLake table.

Per the
`2026-07-12-british-isles-endpoint-recovery-v1 <../../../openspec/changes/2026-07-12-british-isles-endpoint-recovery-v1/>`_
change. Cron: every 6 hours.
"""
from __future__ import annotations

import asyncio
from datetime import UTC, datetime

import dlt_sources
import pandas as pd
from dagster import AssetExecutionContext, asset


@asset(
    group_name="2_materials_endpoint_health",
    description=(
        "Probe every canonical British Isles endpoint via the "
        "endpoint_recovery helper and write one row per probe to "
        "the cianfhoghlaim.endpoint_health DuckLake table."
    ),
    compute_kind="python",
)
def endpoint_health_sink(context: AssetExecutionContext) -> dict[str, int]:
    """Run probe_all_39 and emit the result as a dlt resource."""
    from dlt_sources.common.endpoint_recovery import probe_all_39

    results = asyncio.run(probe_all_39())

    rows = [
        {
            "source_id": source_id,
            "endpoint_url": "",
            "status_code": status,
            "scraped_at": datetime.now(UTC).isoformat(),
        }
        for source_id, status in results.items()
    ]

    @dlt.resource(
        name="endpoint_health",
        write_disposition="merge",
        primary_key=["source_id", "scraped_at"],
    )
    def endpoint_health() -> list[dict]:
        return rows

    pipeline = dlt.pipeline(
        pipeline_name="endpoint_health_sink",
        destination="duckdb",
        dataset_name="cianfhoghlaim_endpoint_health",
    )
    load_info = pipeline.run(endpoint_health())
    context.log.info(
        "endpoint_health_sink_completed",
        rows=len(rows),
        load_id=str(load_info.loads_ids[0]) if load_info.loads_ids else "",
    )
    return {"rows": len(rows), "results": results}


__all__ = ["endpoint_health_sink"]
