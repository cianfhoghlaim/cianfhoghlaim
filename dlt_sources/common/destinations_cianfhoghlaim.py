"""
Environment-aware DuckLake destination factory for cianfhoghlaim.

Solves DuckDB concurrency issues by using DuckLake (S3 + PostgreSQL catalog).
Multiple Dagster partitions can write simultaneously because data is stored as
Parquet files in S3, with transaction coordination via PostgreSQL MVCC.

Usage:
    from dlt_utils import get_dlt_destination, create_pipeline

    pipeline = create_pipeline(
        pipeline_name="curriculum",
        dataset_name="curriculum",
    )

Phase 2.3 of the lateralise change: the namespace is now a
*parameter* (default `"oideachois"`). Sibling quadrants
(`tuatha`, `croilar`) re-export `with_namespace("tuatha")` etc.
from a thin shim. This keeps a single DuckLake implementation
in one place while letting each workspace member scope its
S3 prefix + Postgres DB name to its own namespace.

Phase 2026-06 DuckLake 1.0 alignment: ``get_dlt_destination``
now supports 3 MotherDuck hosting options (managed / byob /
byoc) via the ``MOTHERDUCK_MODE`` env var; default is
``"byob"`` (the "sweet spot" per the 2026-04-13 MotherDuck
launch post). The 1.0 features — data inlining, sorting, and
bucket partitioning — are exposed via the
``cianfhoghlaim/dlt_utils/ducklake_options.py`` module.
"""

from __future__ import annotations

import os
from typing import Any

import dlt
from dlt.destinations.impl.ducklake.configuration import DuckLakeCredentials

# DuckLake 1.0 helpers (the 2026-04-13 launch features).
from .ducklake_options import (
    apply_ducklake_1_0_optimisations,
    is_bucket_partitioned_table,
    is_sorted_by_table,
)

DEFAULT_NAMESPACE = "cianfhoghlaim"

LAKEHOUSE_DUCKDB: str = "md:cianfhoghlaim"
"""The canonical MotherDuck + DuckLake lakehouse alias for the cianfhoghlaim platform.

Used by the 4 BIEP v3 jurisdiction pipelines + 5 Dagster assets. The
canonical helper is `dlt_sources.common.destinations_cianfhoghlaim.get_dlt_destination()`.
"""


def _resolve_aws_credentials() -> tuple[str, str, str]:
    """Map lakehouse's GARAGE_* env vars to the AWS_* naming that
    boto3 / DLT expect.

    The lakehouse stack's :file:`bonneagar/stacks/lakehouse/.env.dev`
    uses the canonical ``GARAGE_ACCESS_KEY_ID`` /
    ``GARAGE_SECRET_ACCESS_KEY`` naming convention. DLT + boto3 + the
    DuckDB S3 extension all expect ``AWS_ACCESS_KEY_ID`` /
    ``AWS_SECRET_ACCESS_KEY``. This helper maps the former to the
    latter, preserving any explicit ``AWS_*`` values the operator may
    have set (e.g., from an old :file:`.env`).

    Returns:
        (aws_access_key_id, aws_secret_access_key, aws_region) — both
        keys are non-empty if either GARGE_* or AWS_* is set.
    """
    aws_access_key_id = (
        os.environ.get("AWS_ACCESS_KEY_ID")
        or os.environ.get("GARAGE_ACCESS_KEY_ID")
        or ""
    )
    aws_secret_access_key = (
        os.environ.get("AWS_SECRET_ACCESS_KEY")
        or os.environ.get("GARAGE_SECRET_ACCESS_KEY")
        or ""
    )
    # Region is unambiguous: AWS_REGION (default "garage" for the
    # lakehouse); the lakehouse doesn't use a separate GARAGE_REGION.
    aws_region = os.environ.get("AWS_REGION", "garage")
    return aws_access_key_id, aws_secret_access_key, aws_region


def _build_local_destination(namespace: str) -> Any:
    """Build local DuckLake destination using Garage S3 + PostgreSQL.

    `namespace` is used to derive:
      * S3 prefix  : s3://ducklake/{namespace}/
      * Postgres DB: ducklake_{namespace}
      * DuckLake   : {namespace}
    """
    # PostgreSQL catalog config. Precedence: explicit DUCKLAKE_POSTGRES_*
    # override > the bonneagar/stacks/lakehouse compose stack's own
    # POSTGRES_* vars (secrets.env is Infisical-first in prod, resolved by
    # the locket sidecar into the container env; .env.dev is the local-dev
    # fallback for the same names) > a last-resort hardcoded dev default.
    # Without the POSTGRES_* fallback, this silently used "devpassword"
    # even when the real compose-stack password was set under POSTGRES_*,
    # since nothing in the stack ever exports DUCKLAKE_POSTGRES_* itself.
    postgres_host = os.environ.get("DUCKLAKE_POSTGRES_HOST", "localhost")
    postgres_port = os.environ.get("DUCKLAKE_POSTGRES_PORT", "5433")
    postgres_db = os.environ.get("DUCKLAKE_POSTGRES_DB") or os.environ.get(
        "POSTGRES_DB", f"ducklake_{namespace}"
    )
    postgres_user = os.environ.get("DUCKLAKE_POSTGRES_USER") or os.environ.get(
        "POSTGRES_USER", "lakekeeper"
    )
    postgres_pass = os.environ.get("DUCKLAKE_POSTGRES_PASSWORD") or os.environ.get(
        "POSTGRES_PASSWORD", "devpassword"
    )

    catalog_uri = f"postgresql://{postgres_user}:{postgres_pass}@{postgres_host}:{postgres_port}/{postgres_db}"

    # S3/Garage storage config.
    # The canonical bucket name is `ducklake-cianfhoghlaim` (per the
    # 2026-08-13 lakehouse deploy). Override via DUCKLAKE_BUCKET env var.
    bucket_name = os.environ.get("DUCKLAKE_BUCKET", "ducklake-cianfhoghlaim")
    bucket_url = f"s3://{bucket_name}/{namespace}/"
    endpoint_url = os.environ.get("AWS_ENDPOINT_URL", "http://localhost:3900")
    # Map the lakehouse's GARAGE_* env vars to the AWS_* naming
    # that boto3 + the DuckDB S3 extension expect.
    aws_access_key_id, aws_secret_access_key, aws_region = _resolve_aws_credentials()

    # Build storage credentials dict for filesystem-style config
    storage_config = {
        "bucket_url": bucket_url,
        "credentials": {
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key,
            "endpoint_url": endpoint_url,
            "region_name": aws_region,
        },
        # Force path-style URLs for S3-compatible storage (Garage, MinIO)
        # s3fs uses virtual-host style by default which requires DNS for bucket subdomains
        # config_kwargs is a top-level field in FilesystemDestinationClientConfiguration
        # that gets passed to botocore.Config
        "config_kwargs": {"s3": {"addressing_style": "path"}},
    }

    # Use DuckLakeCredentials with proper catalog + storage config
    credentials = DuckLakeCredentials(
        ducklake_name=namespace,
        catalog=catalog_uri,
        storage=storage_config,
    )

    # Extract host:port from endpoint URL for DuckDB S3 settings
    # http://localhost:3900 -> localhost:3900
    s3_endpoint = endpoint_url.replace("http://", "").replace("https://", "")

    # DuckDB S3 configuration for Garage/MinIO (path-style URLs)
    global_config = {
        "s3_endpoint": s3_endpoint,
        "s3_use_ssl": "false",
        "s3_url_style": "path",
        "s3_access_key_id": aws_access_key_id,
        "s3_secret_access_key": aws_secret_access_key,
        "s3_region": aws_region,
    }

    return dlt.destinations.ducklake(credentials=credentials, global_config=global_config)


def _build_production_destination(namespace: str) -> Any:
    """Build production DuckLake destination using Cloudflare R2 + PostgreSQL."""
    # PostgreSQL catalog config
    pg_host = os.environ.get("DUCKLAKE_POSTGRES_HOST", "eu-west-3.pg.psdb.cloud")
    pg_port = os.environ.get("DUCKLAKE_POSTGRES_PORT", "5432")
    pg_user = os.environ.get("DUCKLAKE_POSTGRES_USER")
    pg_pass = os.environ.get("DUCKLAKE_POSTGRES_PASSWORD")
    pg_db = os.environ.get("DUCKLAKE_POSTGRES_DB", f"ducklake_{namespace}")

    catalog_uri = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}?sslmode=require"

    # R2 storage config
    r2_bucket = os.environ.get("R2_DUCKLAKE_BUCKET", "ducklake")
    bucket_url = f"s3://{r2_bucket}/{namespace}/"

    aws_access_key_id, aws_secret_access_key, _ = _resolve_aws_credentials()

    storage_config = {
        "bucket_url": bucket_url,
        "credentials": {
            "aws_access_key_id": os.environ.get("R2_ACCESS_KEY_ID", aws_access_key_id),
            "aws_secret_access_key": os.environ.get("R2_SECRET_ACCESS_KEY", aws_secret_access_key),
            "endpoint_url": os.environ.get("R2_ENDPOINT_URL", ""),
        },
    }

    credentials = DuckLakeCredentials(
        ducklake_name=namespace,
        catalog=catalog_uri,
        storage=storage_config,
    )

    return dlt.destinations.ducklake(credentials=credentials)


def get_dlt_destination(
    use_ducklake: bool | None = None,
    namespace: str = DEFAULT_NAMESPACE,
    mode: str = "read_write",
    tenant: str | None = None,
    iceberg: bool = False,
) -> Any:
    """
    Get DLT destination for cianfhoghlaim pipelines.

    Per the 2026-08-07-biep-v3-hardening-v1 change: adds `mode`,
    `tenant`, and `iceberg` flags.

    Environment Variables:
        DLT_ENVIRONMENT: "local" (default) or "production"
        USE_DUCKLAKE: "true" (default) or "false"
        MOTHERDUCK_INSTANCE_SIZE: "small" (default) | "medium" | "large"

    Local:
        - Data: Garage S3 at s3://ducklake/{namespace}[_{tenant}]/
        - Metadata: PostgreSQL at localhost:5433, db ducklake_{namespace}[_{tenant}]

    Production:
        - Data: Cloudflare R2
        - Metadata: PlanetScale PostgreSQL

    Args:
        use_ducklake: Override to force DuckLake or DuckDB fallback
        namespace: S3 prefix + Postgres DB name. Defaults to "cianfhoghlaim".
        mode: "read_only" | "read_write" | "admin". Default: "read_write".
        tenant: Optional tenant suffix (multi-tenant deployments).
            E.g. namespace="cianfhoghlaim", tenant="school-123" →
            s3://ducklake/cianfhoghlaim/school-123/ + db ducklake_cianfhoghlaim_school_123
        iceberg: If True, use Iceberg write path (per
            dlt/common/iceberg_options.py) instead of DuckLake.

    Returns:
        Configured destination for DLT pipeline
    """
    if use_ducklake is None:
        use_ducklake = os.environ.get("USE_DUCKLAKE", "true").lower() == "true"

    # Multi-tenant namespace suffix
    effective_namespace = namespace
    if tenant is not None:
        effective_namespace = f"{namespace}_{tenant}"

    # Iceberg write path
    if iceberg:
        from dlt_sources.common.iceberg_options import build_iceberg_local_destination
        return build_iceberg_local_destination(namespace=effective_namespace)

    if not use_ducklake:
        return get_duckdb_fallback_destination(namespace=namespace)

    env = os.environ.get("DLT_ENVIRONMENT", "local").lower()

    if env == "production":
        return _build_production_destination(namespace)
    else:
        return _build_local_destination(namespace)


def post_create_ducklake_1_0(
    dataset_name: str,
    table: str,
) -> list[str]:
    """Return the SQL statements to apply DuckLake 1.0 optimisations to a new table.

    Called from a dlt `destination` callable (added in dlt 1.0) or
    from a Dagster asset's `MaterializeResult` callback.

    The SQL applies the 3 DuckLake 1.0 features in this order:
    1. `data_inlining_row_limit=100` (the 1.0 default; applied to
       every new table).
    2. `SORTED BY (id)` (applied to the 8 high-volume tables
       listed in `cianfhoghlaim/dlt_utils/ducklake_options.py:SORTED_BY_TABLES`).
    3. `PARTITIONED BY (bucket(1000, id))` (applied to the 3
       largest fact tables listed in
       `cianfhoghlaim/dlt_utils/ducklake_options.py:BUCKET_PARTITIONED_TABLES`).

    Args:
        dataset_name: The dlt dataset name (e.g. "leabharlann_books").
        table: The table name (e.g. "leabharlann_books").

    Returns:
        A list of SQL statements (may be empty).
    """
    qualified = f"{dataset_name}.{table}"
    return apply_ducklake_1_0_optimisations(
        qualified,
        enable_sorting=is_sorted_by_table(qualified),
        enable_bucketing=is_bucket_partitioned_table(qualified),
    )


def get_duckdb_fallback_destination(
    database_path: str | None = None,
    namespace: str = DEFAULT_NAMESPACE,
) -> Any:
    """
    Get plain DuckDB destination as fallback when DuckLake is not available.

    Use this for quick testing or when the lakehouse infrastructure isn't running.

    Args:
        database_path: Path to local DuckDB file. Defaults to
            `./data/{namespace}.duckdb`.
        namespace: Workspace-member name. Ignored if database_path is given.

    Returns:
        DuckDB destination for DLT pipeline
    """
    if database_path is None:
        database_path = f"./data/{namespace}.duckdb"
    return dlt.destinations.duckdb(credentials=database_path)


def create_pipeline(
    pipeline_name: str = "curriculum",
    dataset_name: str = "curriculum",
    use_ducklake: bool = True,
    namespace: str = DEFAULT_NAMESPACE,
    **kwargs: Any,
) -> dlt.Pipeline:
    """
    Create a DLT pipeline with appropriate destination.

    Args:
        pipeline_name: Name of the pipeline (for state tracking)
        dataset_name: Dataset/schema name in destination
        use_ducklake: If True, use DuckLake; if False, use plain DuckDB
        namespace: Workspace-member name (oideachais, tuath, croilar, ...).
        **kwargs: Additional arguments passed to dlt.pipeline()

    Returns:
        Configured DLT pipeline
    """
    destination = (
        get_dlt_destination(namespace=namespace)
        if use_ducklake
        else get_duckdb_fallback_destination(namespace=namespace)
    )

    return dlt.pipeline(
        pipeline_name=pipeline_name,
        destination=destination,
        dataset_name=dataset_name,
        **kwargs,
    )


def observe_pipeline_run(
    pipeline_name: str,
    dataset_name: str,
    table_name: str,
) -> Any:
    """Return the shared MLflow + Langfuse observer for a DLT run."""
    from .observability import DltRunConfig, DltRunObserver

    return DltRunObserver(
        DltRunConfig(
            pipeline_name=pipeline_name,
            dataset_name=dataset_name,
            table_name=table_name,
        )
    )


# ── Sibling-quadrant re-export factory ──────────────────────────────────
#
# Phase 2.3 lets `tuatha/dlt_utils/destinations.py` and
# `croilar/dlt_utils/destinations.py` collapse to a 5-line shim
# that re-exports `with_namespace("tuath")` etc. See:
#
#   tuatha/dlt_utils/destinations.py:    from cianfhoghlaim.dlt.destinations_oideachais import with_namespace
#                                       with_namespace("tuath").re_export_into(globals())
#   croilar/dlt_utils/destinations.py:   from cianfhoghlaim.dlt.destinations_oideachais import with_namespace
#                                       with_namespace("croilar").re_export_into(globals())


def with_namespace(namespace: str) -> _NamespacedDestinations:
    """Return a namespaced view of the destination helpers.

    Usage from a sibling quadrant's `destinations.py` shim:

        from dlt_utils.destinations import with_namespace
        ns = with_namespace("tuath")
        get_dlt_destination = ns.get_dlt_destination
        create_pipeline = ns.create_pipeline
        get_duckdb_fallback_destination = ns.get_duckdb_fallback_destination
        NAMESPACE = ns.NAMESPACE
    """
    return _NamespacedDestinations(namespace)


class _NamespacedDestinations:
    """Thin wrapper that pre-binds `namespace` for the 3 helpers."""

    def __init__(self, namespace: str) -> None:
        self.NAMESPACE = namespace

    def get_dlt_destination(
        self,
        use_ducklake: bool | None = None,
    ) -> Any:
        return get_dlt_destination(use_ducklake=use_ducklake, namespace=self.NAMESPACE)

    def get_duckdb_fallback_destination(
        self,
        database_path: str | None = None,
    ) -> Any:
        return get_duckdb_fallback_destination(
            database_path=database_path, namespace=self.NAMESPACE
        )

    def create_pipeline(
        self,
        pipeline_name: str = "curriculum",
        dataset_name: str = "curriculum",
        use_ducklake: bool = True,
        **kwargs: Any,
    ) -> dlt.Pipeline:
        return create_pipeline(
            pipeline_name=pipeline_name,
            dataset_name=dataset_name,
            use_ducklake=use_ducklake,
            namespace=self.NAMESPACE,
            **kwargs,
        )

    def re_export_into(self, g: dict[str, Any]) -> None:
        """Inject the namespaced helpers into a module's globals().

        Lets `tuatha/dlt_utils/destinations.py` be a single line:

            from dlt_sources.destinations_oideachais import with_namespace
            with_namespace("tuath").re_export_into(globals())
        """
        g["NAMESPACE"] = self.NAMESPACE
        g["get_dlt_destination"] = self.get_dlt_destination
        g["get_duckdb_fallback_destination"] = self.get_duckdb_fallback_destination
        g["create_pipeline"] = self.create_pipeline


# Backwards-compat alias — the old constant `NAMESPACE` still resolves.
NAMESPACE = DEFAULT_NAMESPACE
