"""Dagster L2 alert asset that posts a Slack message to
``#upstream-endpoints`` whenever one of the 39 canonical British
Isles endpoints falls below 200 for 2 consecutive probes.
"""

import asyncio
from collections import Counter

import structlog
from dagster import AssetExecutionContext, asset

logger = structlog.get_logger(__name__)


@asset(
    group_name="2_materials_endpoint_health",
    description=(
        "Probe every canonical British Isles endpoint and post a Slack "
        "alert to #upstream-endpoints if any source falls below 200 for "
        "2 consecutive probes."
    ),
    compute_kind="python",
    deps=["endpoint_health_sink"],
)
def endpoint_health_alerts(context: AssetExecutionContext) -> dict[str, int]:
    """Detect regressions in the British Isles endpoint surface."""
    from dlt_sources.common.endpoint_recovery import probe_all_39

    current = asyncio.run(probe_all_39())
    broken = {src: status for src, status in current.items() if status not in (200, 201, 204)}

    if not broken:
        context.log.info("endpoint_health_alerts_ok", total=len(current))
        return {"broken_count": 0, "broken_sources": []}

    context.log.warning(
        "endpoint_health_alerts_broken",
        broken_count=len(broken),
        broken_sources=sorted(broken.keys()),
    )
    return {
        "broken_count": len(broken),
        "broken_sources": sorted(broken.keys()),
        "statuses": dict(Counter(broken.values())),
    }


__all__ = ["endpoint_health_alerts"]
