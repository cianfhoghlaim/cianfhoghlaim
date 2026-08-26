#!/usr/bin/env python3
"""Smoke test DLT -> DuckLake plus MLflow and Langfuse telemetry."""

from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import asdict
from datetime import UTC, datetime

os.environ["USE_LOCAL_SCRAPES"] = "true"
os.environ.setdefault("DLT_ENVIRONMENT", "local")
os.environ.setdefault("USE_DUCKLAKE", "true")
os.environ.setdefault("DUCKLAKE_POSTGRES_HOST", "localhost")
os.environ.setdefault("DUCKLAKE_POSTGRES_PORT", "5433")
os.environ.setdefault("DUCKLAKE_POSTGRES_DB", "ducklake_cianfhoghlaim")
os.environ.setdefault("DUCKLAKE_POSTGRES_USER", "lakekeeper")
os.environ.setdefault("DUCKLAKE_BUCKET", "ducklake")
os.environ.setdefault("AWS_ENDPOINT_URL", "http://localhost:3900")
os.environ.setdefault("MLFLOW_TRACKING_URI", "http://localhost:5050")
os.environ.setdefault("MLFLOW_EXPERIMENT_NAME", "dlt-observability-smoke")
os.environ.setdefault("LANGFUSE_HOST", "http://localhost:3001")

import dlt

from dlt_sources.common.destinations_cianfhoghlaim import create_pipeline, observe_pipeline_run

PIPELINE_NAME = "dlt_observability_smoke"
DATASET_NAME = "dlt_observability_smoke"
TABLE_NAME = "smoke_events"
ROWS = [
    {
        "event_id": "smoke-1",
        "message": "lakehouse smoke",
        "created_at": datetime.now(UTC).isoformat(),
    }
]


@dlt.resource(name=TABLE_NAME, primary_key="event_id", write_disposition="merge")
def smoke_events():
    yield from ROWS


def main() -> int:
    pipeline = create_pipeline(
        pipeline_name=PIPELINE_NAME,
        dataset_name=DATASET_NAME,
        use_ducklake=True,
        namespace="cianfhoghlaim",
        dev_mode=False,
    )
    with observe_pipeline_run(PIPELINE_NAME, DATASET_NAME, TABLE_NAME) as observer:
        load_info = pipeline.run(smoke_events())
        receipt = observer.record(row_count=len(ROWS), load_info=load_info)
    checks = {
        "lakehouse": _verify_lakehouse(),
        "mlflow": _verify_mlflow(receipt.mlflow_run_id),
        "langfuse": _verify_langfuse(receipt.langfuse_trace_id),
    }
    print(json.dumps({"receipt": asdict(receipt), "checks": checks}, indent=2))
    return 0 if all(checks.values()) else 1


def _verify_lakehouse() -> bool:
    import duckdb

    connection = duckdb.connect()
    try:
        endpoint = os.environ["AWS_ENDPOINT_URL"].replace("http://", "").replace("https://", "")
        connection.execute(
            "INSTALL httpfs; LOAD httpfs; INSTALL postgres; LOAD postgres; INSTALL ducklake; LOAD ducklake"
        )
        connection.execute(f"SET s3_endpoint='{endpoint}'")
        connection.execute("SET s3_use_ssl=false; SET s3_url_style='path'; SET s3_region='garage'")
        connection.execute(f"SET s3_access_key_id='{os.environ['AWS_ACCESS_KEY_ID']}'")
        connection.execute(f"SET s3_secret_access_key='{os.environ['AWS_SECRET_ACCESS_KEY']}'")
        connection.execute(
            f"ATTACH 'ducklake:postgres:{_catalog_uri()}' AS smoke_lake "
            "(DATA_PATH 's3://ducklake/cianfhoghlaim/', "
            "METADATA_SCHEMA 'cianfhoghlaim', METADATA_CATALOG 'ducklake_cianfhoghlaim')"
        )
        row = connection.execute(
            f'SELECT COUNT(*) FROM smoke_lake."{DATASET_NAME}"."{TABLE_NAME}" WHERE event_id=\'smoke-1\''
        ).fetchone()
        return row is not None and row[0] == 1
    finally:
        connection.close()


def _catalog_uri() -> str:
    password = os.environ.get("DUCKLAKE_POSTGRES_PASSWORD") or os.environ["POSTGRES_PASSWORD"]
    return f"postgresql://lakekeeper:{password}@localhost:5433/ducklake_cianfhoghlaim"


def _verify_mlflow(run_id: str | None) -> bool:
    if run_id is None:
        return False
    import mlflow

    mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
    run = mlflow.get_run(run_id)
    return run.data.metrics.get("dlt.rows_loaded") == 1.0


def _verify_langfuse(trace_id: str | None) -> bool:
    if trace_id is None:
        return False
    from langfuse import get_client

    client = get_client()
    client.flush()
    for _ in range(10):
        try:
            trace = client.api.trace.get(trace_id)
        except Exception:
            time.sleep(1)
            continue
        return trace.name == PIPELINE_NAME
    return False


if __name__ == "__main__":
    sys.exit(main())
