"""Dagster L2 asset that probes every British Isles canonical endpoint
and writes one row per probe to the ``cianfhoghlaim.endpoint_health``
DuckLake table.

Per the
`2026-07-12-british-isles-endpoint-recovery-v1 <../../../openspec/changes/2026-07-12-british-isles-endpoint-recovery-v1/>`_
change. Cron: every 6 hours.

Migrated to the real `dagster-dlt` integration (`@dlt_assets` +
`DagsterDltResource`) as the Phase 5 reference implementation — see
`orchestration/resources.py`'s `all_resources["dlt"]` for the resource
wired into `Definitions`. Previously this asset hand-rolled
`dlt.pipeline(...).run(...)` inside a plain `@asset` body, AND was
missing `import dlt` entirely (a pre-existing `NameError` bug, fixed as
part of this rewrite — `@dlt.resource`/`dlt.pipeline` were called
without the module ever importing `dlt`).

A custom `DagsterDltTranslator` keeps the produced asset key as
`endpoint_health_sink` (the dlt-default would be
`dlt_endpoint_health_source_endpoint_health`) so existing consumers
(`alerts.py`'s `deps=["endpoint_health_sink"]`, `defs.yaml`'s
`source_asset: 2_materials/endpoint_health/endpoint_health_sink`)
keep working unchanged.
"""

import asyncio
from datetime import UTC, datetime

import dlt
from dagster import AssetExecutionContext, AssetKey
from dagster_dlt import DagsterDltResource, DagsterDltTranslator, dlt_assets
from dagster_dlt.translator import DltResourceTranslatorData


@dlt.resource(
    name="endpoint_health",
    write_disposition="merge",
    primary_key=["source_id", "scraped_at"],
)
def endpoint_health():
    """Probe every canonical British Isles endpoint and yield one row
    per probe. The async probe runs lazily when dlt iterates this
    resource (at `dlt.run()` time), not at module-import time."""
    from dlt_sources.common.endpoint_recovery import probe_all_39

    results = asyncio.run(probe_all_39())
    for source_id, status in results.items():
        yield {
            "source_id": source_id,
            "endpoint_url": "",
            "status_code": status,
            "scraped_at": datetime.now(UTC).isoformat(),
        }


@dlt.source(name="endpoint_health_source")
def endpoint_health_source():
    yield endpoint_health()


class _EndpointHealthTranslator(DagsterDltTranslator):
    """Keeps the asset key as `endpoint_health_sink` (matching what this
    asset was named under the old hand-rolled pattern) instead of dlt's
    default `dlt_{source_name}_{resource_name}` key."""

    def get_asset_spec(self, data: DltResourceTranslatorData):
        return super().get_asset_spec(data).replace_attributes(
            key=AssetKey("endpoint_health_sink")
        )


@dlt_assets(
    dlt_source=endpoint_health_source(),
    dlt_pipeline=dlt.pipeline(
        pipeline_name="endpoint_health_sink",
        destination="duckdb",
        dataset_name="cianfhoghlaim_endpoint_health",
    ),
    name="endpoint_health_sink",
    group_name="2_materials_endpoint_health",
    dagster_dlt_translator=_EndpointHealthTranslator(),
)
def endpoint_health_sink(context: AssetExecutionContext, dlt: DagsterDltResource):
    """Run the endpoint-health probe via the real dagster-dlt resource."""
    yield from dlt.run(context=context)


__all__ = ["endpoint_health_sink"]
