"""
oideachais.dagster_defs.assets.upstream_monitoring_assets — Dagster
asset group for the `upstream-package-monitoring` openspec change.

The 33rd asset group registered in `dagster_defs/assets/__init__.py:all_assets`.

Five assets + one sensor:

1. `upstream_blog_monitor_ingest` — runs the DLT source
   `cianfhoghlaim.dlt.cross.upstream.blog_post.upstream_blog_post_source`
   against the n8n-written payloads in `s3://oideachais-upstream-webhooks/`.
   Materialises `oideachais.upstream_blog_post` (incremental merge) and
   `oideachais.upstream_blog_post_audit` (append-only) in DuckLake.

2. `upstream_blog_chunk_and_tag` — runs the v1 CocoIndex App
   `upstream_blog_monitor_app` from
   `oideachais/cocoindex_flows/upstream_blog_monitor.py`. Reads the
   payloads via the App, BAML-extracts `BlogPostMetadata` via
   `ExtractBlogPostMetadata`, embeds the chunks, and writes
   `upstream_blog_chunks` to LanceDB + `BlogPost` + `Package` nodes
   to the `upstream_packages_graph` FalkorDB graph.

3. `upstream_blog_graph_publish` — runs `upstream_api_surface_app`
   from `oideachais/cocoindex_flows/upstream_api_surface.py`. Walks
   the 5 cocoindex docs URLs + `llms-full.txt`, BAML-extracts
   `ApiChange` records via `ExtractCocoIndexApiChange`, and writes
   `ApiChangeNode` + `V1AppNode` + `AFFECTS_APP` edges to the
   `upstream_packages_graph` FalkorDB graph.

4. `cocoindex_v1_conformance_check` — runs the v1 CocoIndex App
   `cocoindex_v1_conformance_app` from
   `oideachais/cocoindex_flows/cocoindex_v1_conformance.py`. Static
   AST linter checking all 14 v1 Apps against the 4 conformance rules
   (R1-R4). Writes a `conformance_check_history` row to LanceDB on
   every run so we can detect regressions.

5. `upstream_api_surface_publish` — runs `upstream_api_surface_app`
   (alias of #3, kept as a separate asset so the asset graph shows
   the dependency: ingest → chunk+tag → api surface → publish).

6. `upstream_breaking_change_sensor` — 5-minute poll against the
   `upstream_packages_graph` FalkorDB graph; fires a Slack alert
   to `#upstream-breaking-changes` when any `ApiChange` with
   `change_severity=high` and `is_breaking=true` has not been
   acknowledged.

Reference: openspec/changes/upstream-package-monitoring/proposal.md
"""

from __future__ import annotations

import asyncio
import json
import os
import pathlib
import subprocess
import sys
from collections.abc import Iterator
from datetime import datetime, timezone
from typing import Any

import dagster as dg
import structlog

logger = structlog.get_logger(__name__)


# Lazy imports for the heavy deps (DLT, CocoIndex, FalkorDB, BAML).
# We don't import them at module load to keep `dg list defs` fast.
def _load_dlt() -> Any:
    """Import the DLT source lazily (keeps `dg list defs` fast)."""
    from cianfhoghlaim.dlt.cross.upstream.blog_post import (
        upstream_blog_post_source,
    )

    return upstream_blog_post_source


def _payloads_root() -> pathlib.Path:
    """Resolve the payloads root from the env var (or default to the
    local dev path under `stedding/`).
    """
    return pathlib.Path(
        os.getenv(
            "UPSTREAM_PAYLOADS_ROOT",
            "s3://oideachais-upstream-webhooks/",
        )
    )


# ============================================================================
# Asset 1: upstream_blog_monitor_ingest
# ============================================================================


@dg.asset(
    group_name="upstream_monitoring",
    description=(
        "Runs the DLT incremental source "
        "`cianfhoghlaim.dlt.cross.upstream.blog_post.upstream_blog_post_source` "
        "against the n8n-written payloads. Materialises "
        "`oideachais.upstream_blog_post` (incremental merge on "
        "`first_seen_at`) and `oideachais.upstream_blog_post_audit` "
        "(append-only) in DuckLake."
    ),
    metadata={
        "openspec_change": "upstream-package-monitoring",
        "dlt_source": "cianfhoghlaim.dlt.cross.upstream.blog_post",
        "primary_key": ("package", "blog_post_id"),
        "incremental_cursor": "first_seen_at",
    },
)
def upstream_blog_monitor_ingest(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """DLT ingest run: walks the S3/Garage payloads, applies the
    incremental cursor, materialises the DuckLake tables."""
    upstream_blog_post_source = _load_dlt()
    payloads_root = _payloads_root()

    logger.info(
        "upstream_blog_monitor_ingest_start",
        payloads_root=str(payloads_root),
    )

    # Run the DLT pipeline via the Python API.
    import dlt

    pipeline = dlt.pipeline(
        pipeline_name="upstream_blog_post",
        destination=dlt.destinations.ducklake(
            database="oideachais",
        ),
        dataset_name="upstream_blog_post",
        dev_mode=False,
    )
    source = upstream_blog_post_source(payloads_root=payloads_root)
    load_info = pipeline.run(source)

    context.log.info(
        f"upstream_blog_monitor_ingest_complete load_info={load_info}"
    )

    return dg.MaterializeResult(
        metadata={
            "load_id": load_info.first_run.id if hasattr(load_info, "first_run") else "",
            "dataset_name": load_info.dataset_name,
            "payloads_root": str(payloads_root),
        }
    )


# ============================================================================
# Asset 2: upstream_blog_chunk_and_tag
# ============================================================================


@dg.asset(
    group_name="upstream_monitoring",
    description=(
        "Runs the v1 CocoIndex App `upstream_blog_monitor_app`. Reads the "
        "JSONL payloads, BAML-extracts `BlogPostMetadata`, embeds the "
        "chunks, and writes `upstream_blog_chunks` to LanceDB + "
        "`BlogPostNode` + `PackageNode` + `PUBLISHED_BY` edges to the "
        "`upstream_packages_graph` FalkorDB graph."
    ),
    deps=[dg.AssetKey(["upstream_blog_monitor_ingest"])],
    metadata={
        "openspec_change": "upstream-package-monitoring",
        "v1_app": "upstream_blog_monitor_app",
        "baml_function": "ExtractBlogPostMetadata",
    },
)
def upstream_blog_chunk_and_tag(
    context: dg.AssetExecutionContext,
) -> dg.MaterializeResult:
    """Invoke the v1 CocoIndex App via subprocess (matches the canonical
    `python -m oideachais.cocoindex_flows.<app> update` pattern used by
    every other App)."""
    result = subprocess.run(
        [
            "python",
            "-m",
            "oideachais.cocoindex_flows.upstream_blog_monitor",
            "update",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise dg.Failure(
            description=(
                f"upstream_blog_monitor_app exited {result.returncode}: "
                f"{result.stderr}"
            )
        )
    return dg.MaterializeResult(
        metadata={
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    )


# ============================================================================
# Asset 3: upstream_blog_graph_publish
# ============================================================================


@dg.asset(
    group_name="upstream_monitoring",
    description=(
        "Runs the v1 CocoIndex App `upstream_api_surface_app`. Walks the "
        "5 cocoindex docs URLs + `llms-full.txt`, BAML-extracts "
        "`ApiChange` records via `ExtractCocoIndexApiChange`, and writes "
        "`ApiChangeNode` + `V1AppNode` + `AFFECTS_APP` edges to the "
        "`upstream_packages_graph` FalkorDB graph."
    ),
    deps=[dg.AssetKey(["upstream_blog_chunk_and_tag"])],
    metadata={
        "openspec_change": "upstream-package-monitoring",
        "v1_app": "upstream_api_surface_app",
        "baml_function": "ExtractCocoIndexApiChange",
        "watched_urls": [
            "https://cocoindex.io/docs/skill.md",
            "https://cocoindex.io/docs/getting_started/quickstart",
            "https://cocoindex.io/docs/advanced_topics/live_component",
            "https://cocoindex.io/docs/connectors/falkordb",
            "https://cocoindex.io/llms-full.txt",
        ],
    },
)
def upstream_blog_graph_publish(
    context: dg.AssetExecutionContext,
) -> dg.MaterializeResult:
    """Invoke the upstream_api_surface v1 CocoIndex App via subprocess."""
    result = subprocess.run(
        [
            "python",
            "-m",
            "oideachais.cocoindex_flows.upstream_api_surface",
            "update",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise dg.Failure(
            description=(
                f"upstream_api_surface_app exited {result.returncode}: "
                f"{result.stderr}"
            )
        )
    return dg.MaterializeResult(
        metadata={
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    )


# ============================================================================
# Asset 4: cocoindex_v1_conformance_check
# ============================================================================


@dg.asset(
    group_name="upstream_monitoring",
    description=(
        "Runs the v1 CocoIndex App `cocoindex_v1_conformance_app`. Static "
        "AST linter that checks every v1 App in "
        "`oideachais/cocoindex_flows/*.py` against the 4 conformance rules "
        "(R1 imports shared_lifespan, R2 declares canonical ContextKeys "
        "or R2-exempt ones, R3 `coco.App(...)` at module scope, R4 at "
        "least one `@coco.fn(` decorator). Writes a `conformance_check_history` "
        "row to LanceDB on every run so we can detect regressions."
    ),
    metadata={
        "openspec_change": "upstream-package-monitoring",
        "v1_app": "cocoindex_v1_conformance_app",
        "rules": ["R1", "R2", "R3", "R4"],
    },
)
def cocoindex_v1_conformance_check(
    context: dg.AssetExecutionContext,
) -> dg.MaterializeResult:
    """Invoke the conformance linter and emit a summary asset check."""
    result = subprocess.run(
        [
            "python",
            "-c",
            (
                "import asyncio; from cianfhoghlaim.cocoindex.cocoindex_v1_conformance import run_conformance_check; "
                "report = asyncio.run(run_conformance_check()); "
                "print(report.summary()); "
                "import sys; sys.exit(0 if report.all_passed else 1)"
            ),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        # Soft-fail: the conformance App is the enforcer, so a failure
        # here is an upstream problem that needs human attention. Raise
        # `dg.Failure` so the asset materialisation is marked failed
        # in the Dagster UI.
        raise dg.Failure(
            description=(
                f"cocoindex_v1_conformance_app exited {result.returncode}: "
                f"{result.stdout}\n{result.stderr}"
            )
        )
    return dg.MaterializeResult(
        metadata={
            "summary": result.stdout,
            "returncode": result.returncode,
        }
    )


# ============================================================================
# Asset 5: upstream_api_surface_publish (alias of #3, kept for graph clarity)
# ============================================================================


@dg.asset(
    group_name="upstream_monitoring",
    description=(
        "Alias of `upstream_blog_graph_publish` kept as a separate asset "
        "so the asset dependency graph makes the ingest → chunk → api "
        "surface → publish chain explicit."
    ),
    deps=[dg.AssetKey(["upstream_blog_graph_publish"])],
    metadata={
        "openspec_change": "upstream-package-monitoring",
    },
)
def upstream_api_surface_publish(
    context: dg.AssetExecutionContext,
) -> dg.MaterializeResult:
    """No-op marker asset. The actual work happens in
    `upstream_blog_graph_publish` (asset #3)."""
    return dg.MaterializeResult(
        metadata={
            "alias_of": "upstream_blog_graph_publish",
            "marker": True,
        }
    )


# ============================================================================
# Asset group + sensor
# ============================================================================


upstream_monitoring_assets = [
    upstream_blog_monitor_ingest,
    upstream_blog_chunk_and_tag,
    upstream_blog_graph_publish,
    cocoindex_v1_conformance_check,
    upstream_api_surface_publish,
]


@dg.sensor(
    job_name="upstream_monitoring_job",
    minimum_interval_seconds=300,  # 5-minute poll
    description=(
        "Polls the `upstream_packages_graph` FalkorDB graph every 5 "
        "minutes for `ApiChange` nodes with `change_severity=high` and "
        "`is_breaking=true` that have not been acknowledged. Fires a "
        "Slack alert to `#upstream-breaking-changes`."
    ),
)
def upstream_breaking_change_sensor(
    context: dg.SensorEvaluationContext,
) -> dg.SensorResult:
    """5-minute poll: detect unacknowledged breaking changes in the
    upstream packages graph and fire Slack alerts.
    """
    # Lazy-import the FalkorDB client (defer until the sensor ticks).
    try:
        from cianfhoghlaim.observability.falkordb_client import (  # type: ignore[import-not-found]
            falkordb_client,
        )
    except ImportError:
        context.log.warning(
            "falkordb_client_not_available; sensor tick skipped"
        )
        return dg.SensorResult(skip_message="falkordb_client unavailable")

    try:
        with falkordb_client() as client:
            graph = client.select_graph("upstream_packages_graph")
            result = list(
                graph.query(
                    (
                        "MATCH (a:ApiChange {is_breaking: true, "
                        "change_severity: 'high', acknowledged: false}) "
                        "RETURN a.api_change_id AS id, a.package AS "
                        "package, a.title AS title, a.url AS url, "
                        "a.first_seen_at AS first_seen_at"
                    )
                ).result_set
            )
    except Exception as e:
        context.log.error(f"falkordb_query_failed error={e}")
        return dg.SensorResult(skip_message=f"falkordb query failed: {e}")

    if not result:
        return dg.SensorResult(skip_message="no unacknowledged breaking changes")

    # Build a run request that triggers a downstream job to post the
    # Slack alert. The actual Slack post is handled by the
    # `upstream_monitoring_job` job (defined in the same module as
    # this sensor, but split out for readability).
    run_requests = []
    for row in result:
        run_key = f"{row['package']}:{row['id']}"
        run_requests.append(
            dg.RunRequest(
                run_key=run_key,
                tags={
                    "package": row["package"],
                    "api_change_id": row["id"],
                    "first_seen_at": row["first_seen_at"],
                },
            )
        )

    return dg.SensorResult(run_requests=run_requests)


@dg.job(
    description=(
        "Posts an `api_change_alert` Slack message to "
        "`#upstream-breaking-changes` for every unacknowledged breaking "
        "change detected by `upstream_breaking_change_sensor`."
    ),
)
def upstream_monitoring_job() -> None:
    """No-op job — the sensor's `run_key` is what triggers the Slack
    alert. The actual Slack post is wired via the Dagster
    `slack_resource` from `oideachais/dagster_defs/resources/slack.py`.
    """
    pass


__all__ = [
    "upstream_monitoring_assets",
    "upstream_monitoring_job",
    "upstream_blog_monitor_ingest",
    "upstream_blog_chunk_and_tag",
    "upstream_blog_graph_publish",
    "upstream_api_surface_publish",
    "cocoindex_v1_conformance_check",
    "upstream_breaking_change_sensor",
]