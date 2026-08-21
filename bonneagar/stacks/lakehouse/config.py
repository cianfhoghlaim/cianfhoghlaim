"""
Lakehouse typed config (Pydantic Settings).

ADDED 2026-08-24 (lakehouse-stack-doctor-and-env-var-cleanup-v1).

A typed, validated view of the lakehouse stack's 53+ env vars. This is the
Python-side counterpart of `compose.yaml` env vars — operators can use
typed access in scripts + notebooks:

    >>> from lakehouse.config import settings
    >>> settings.garage.access_key_id
    'GK3b427f19ad3fd54647e9a1ac'

Required environment variables (the ones that Locket resolves at runtime):
- `GARAGE_RPC_SECRET`, `GARAGE_ADMIN_TOKEN`, `GARAGE_ACCESS_KEY_ID`, `GARAGE_SECRET_ACCESS_KEY`
- `POSTGRES_PASSWORD`
- `LAKEKEEPER_ENCRYPTION_KEY`
- `CLICKHOUSE_PASSWORD`
- `REDIS_PASSWORD`
- `FALKORDB_PASSWORD`
- `COGNEE_POSTGRES_PASSWORD`
- `MEMGRAPH_PASSWORD`

All other variables have sensible defaults. Pydantic validates required
fields + types at import time — scripts fail FAST if a required secret
is missing.

Usage:
    from lakehouse.config import lakehouse_settings
    print(lakehouse_settings.garage.access_key_id)
    print(lakehouse_settings.lakekeeper.metrics_port)
    print(lakehouse_settings.cognee.postgres_password)
"""
from __future__ import annotations

import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GarageSettings(BaseSettings):
    """Garage S3 storage settings (resolved by Locket from dev-baile/lakehouse-garage)."""

    rpc_secret: str = Field(..., description="Garage RPC secret (64 hex chars)")
    admin_token: str = Field(..., description="Garage admin API token")
    access_key_id: str = Field(..., description="Garage S3 access key ID")
    secret_access_key: str = Field(..., description="Garage S3 secret access key")
    rpc_port: int = Field(3901, description="Garage RPC port")
    s3_api_port: int = Field(3900, description="Garage S3 API port")
    k2v_api_port: int = Field(3902, description="Garage K2V API port")
    web_port: int = Field(3903, description="Garage web console port")
    admin_port: int = Field(3904, description="Garage admin API port")

    model_config = SettingsConfigDict(env_prefix="GARAGE_")


class PostgresSettings(BaseSettings):
    """Shared lakehouse-postgres settings (resolved by Locket from dev-baile/lakehouse)."""

    user: str = Field("lakekeeper", description="Postgres superuser name")
    password: str = Field(..., description="Postgres superuser password")
    db: str = Field("lakekeeper", description="Postgres default database")
    port: int = Field(5433, description="Postgres host port (mapped from container port 5432)")

    model_config = SettingsConfigDict(env_prefix="POSTGRES_")


class LakekeeperSettings(BaseSettings):
    """Lakekeeper Iceberg REST Catalog settings (resolved from dev-baile/lakehouse)."""

    encryption_key: str = Field(..., description="64-char hex encryption key for Lakekeeper secrets")
    base_uri: str = Field(
        "http://lakekeeper.cianfhoghlaim.ie",
        description="Lakekeeper base URI for /config endpoint URLs",
    )
    ssl_mode: str = Field("prefer", description="Postgres SSL mode (disable/allow/prefer/require)")
    port: int = Field(8181, description="Lakekeeper host port (mapped from container port 8181)")
    metrics_port: int = Field(9100, description="Lakekeeper metrics port (Prometheus)")
    pagination_size_default: int = Field(1024, description="Lakekeeper default pagination size")
    pagination_size_max: int = Field(2048, description="Lakekeeper max pagination size")
    pg_host_r: str = Field("postgres", description="Lakekeeper PG read replica host")
    pg_host_w: str = Field("postgres", description="Lakekeeper PG write host")
    use_x_forwarded_headers: bool = Field(True, description="Trust X-Forwarded-* from Pangolin")
    cache_stc_enabled: bool = Field(True, description="Enable short-term credentials cache")
    cache_warehouse_enabled: bool = Field(True, description="Enable warehouse metadata cache")
    cache_warehouse_capacity: int = Field(1000, description="Warehouse cache capacity")

    model_config = SettingsConfigDict(env_prefix="LAKEKEEPER_")


class ClickHouseSettings(BaseSettings):
    """ClickHouse columnar engine (consumed by langfuse)."""

    user: str = Field("clickhouse", description="ClickHouse user")
    password: str = Field(..., description="ClickHouse password")
    db: str = Field("default", description="ClickHouse default database")
    http_port: int = Field(8123, description="ClickHouse HTTP port")
    native_port: int = Field(9000, description="ClickHouse native port")

    model_config = SettingsConfigDict(env_prefix="CLICKHOUSE_")


class RedisSettings(BaseSettings):
    """Redis queue/cache (consumed by langfuse)."""

    password: str = Field(..., description="Redis password")
    port: int = Field(6379, description="Redis host port")
    maxmemory_policy: str = Field("allkeys-lru", description="Redis maxmemory policy")

    model_config = SettingsConfigDict(env_prefix="REDIS_")


class CogneeSettings(BaseSettings):
    """Cognee knowledge graph builder (added 2026-08-15)."""

    postgres_user: str = Field("cognee", description="Cognee DB user (dedicated, not lakekeeper)")
    postgres_password: str = Field(..., description="Cognee DB password (resolved by Locket)")
    llm_api_key: str = Field(
        "no-key-needed", description="Cognee LLM client API key (placeholder — LiteLLM uses its own)"
    )
    embedding_api_key: str = Field(
        "no-key-needed", description="Cognee embedding client API key (placeholder)"
    )
    llm_model: str = Field("deepseek/deepseek-chat", description="Default LiteLLM model for cognee")
    embedding_model: str = Field(
        "openai/text-embedding-3-small",
        description="Default LiteLLM embedding model for cognee",
    )
    port: int = Field(8000, description="Cognee host port")
    databases: str = Field(
        "cianfhoghlaim.education.aistear,cianfhoghlaim.education.primary,cianfhoghlaim.education.junior_cycle,cianfhoghlaim.education.senior_cycle,cianfhoghlaim.education.tertiary,cianfhoghlaim.education.cross_stage",
        description="Comma-separated cognee datasets",
    )

    model_config = SettingsConfigDict(env_prefix="COGNEE_")


class GraphitiSettings(BaseSettings):
    """Graphiti bi-temporal KG API (added 2026-08-15)."""

    openai_api_key: str = Field(..., description="Graphiti LLM API key (resolved by Locket)")
    openai_base_url: str = Field("http://litellm:4000/v1", description="LiteLLM base URL")
    falkordb_database: str = Field("default_db", description="FalkorDB graph database name")
    port: int = Field(8001, description="Graphiti host port")

    model_config = SettingsConfigDict(env_prefix="GRAPHITI_")


class FalkorDBSettings(BaseSettings):
    """FalkorDB graph DB + vector.so hybrid (added 2026-08-15)."""

    password: str = Field(..., description="FalkorDB auth password")
    vector_module_url: str = Field("/etc/falkordb/vector.so", description="Path to vector.so module")
    cluster_mode: str = Field("no", description="Cluster mode toggle (no/yes)")
    args: str = Field(
        "THREAD_COUNT 8 CACHE_SIZE 50 TIMEOUT_MAX 60000 TIMEOUT_DEFAULT 30000 QUERY_MEM_CAPACITY 104857600",
        description="FalkorDB module args",
    )
    port: int = Field(6379, description="FalkorDB Redis port")
    ui_port: int = Field(3000, description="FalkorDB Browser UI port")

    model_config = SettingsConfigDict(env_prefix="FALKORDB_")


class MemgraphSettings(BaseSettings):
    """Memgraph Bolt graph DB + MAGE (added 2026-08-15)."""

    user: str = Field("memgraph", description="Memgraph user")
    password: str = Field("devpassword", description="Memgraph password")
    license_file_path: str = Field("", description="Memgraph Enterprise license path (optional)")
    log_level: str = Field("WARNING", description="Memgraph log level")
    bolt_port: int = Field(7687, description="Memgraph Bolt protocol port")
    http_port: int = Field(7444, description="Memgraph HTTP port")
    lab_port: int = Field(3001, description="Memgraph Lab UI port")

    model_config = SettingsConfigDict(env_prefix="MEMGRAPH_")


class LanceNamespaceSettings(BaseSettings):
    """Lance Namespace sidecar (uses official lance-namespace-impls[iceberg] library)."""

    endpoint: str = Field("http://lakekeeper:8181", description="Lakekeeper Iceberg REST endpoint")
    warehouse: str = Field("lakehouse", description="Iceberg warehouse name")
    auth_token: str = Field("", description="Lakekeeper auth token (empty for dev)")
    lance_root: str = Field("s3://lance/", description="Lance table storage root in Garage")
    connect_timeout_millis: int = Field(10000, description="Lakekeeper connect timeout (ms)")
    read_timeout_millis: int = Field(30000, description="Lakekeeper read timeout (ms)")
    max_retries: int = Field(3, description="Lakekeeper HTTP retry count")
    port: int = Field(8182, description="Lance sidecar host port")

    model_config = SettingsConfigDict(env_prefix="")


class OlakeSettings(BaseSettings):
    """Olake CDC engine (consumed by BIEP pipeline)."""

    jdbc_password: str = Field(..., description="Olake JDBC password (resolved by Locket)")
    source_pg_password: str = Field(..., description="Olake source Postgres password")
    writer_s3_secret_key: str = Field(..., description="Olake writer S3 secret key")
    source_db_host: str = Field("postgres", description="Olake source DB host")
    source_db_name: str = Field("olake_source", description="Olake source DB name")

    model_config = SettingsConfigDict(env_prefix="OLAKE_")


class ObservabilitySettings(BaseSettings):
    """Langfuse + MLflow + Logfire settings (PR #4 will wire these fully)."""

    langfuse_host: str = Field("http://langfuse:3000", description="Langfuse server URL")
    langfuse_public_key: str = Field("", description="Langfuse public key (PK prefix)")
    langfuse_secret_key: str = Field("", description="Langfuse secret key (SK prefix)")
    mlflow_tracking_uri: str = Field("http://mlflow:5000", description="MLflow tracking URI")
    mlflow_artifact_root: str = Field(
        "s3://mlflow-artifacts/", description="MLflow S3 artifact root"
    )
    logfire_token: str = Field("", description="Pydantic Logfire write token")

    model_config = SettingsConfigDict(env_prefix="")


class MotherduckSettings(BaseSettings):
    """MotherDuck cloud DuckDB (consumed by BIEP MotherDuck Dives)."""

    token: str = Field("", description="MotherDuck auth token")
    database: str = Field("cianfhoghlaim", description="MotherDuck database name")
    mode: str = Field("byob", description="Hosting mode (managed/byob/byoc)")
    s3_bucket: str = Field("ducklake-cianfhoghlaim", description="MotherDuck S3 bucket")

    model_config = SettingsConfigDict(env_prefix="MOTHERDUCK_")


class LancedbSettings(BaseSettings):
    """LanceDB vector storage (consumed by BIEP CocoIndex Apps)."""

    api_key: str = Field(..., description="Lance Namespace API key (resolved by Locket)")
    namespace_token: str = Field("", description="Lance Namespace 0.9 contract token")
    region: str = Field("eu-west-1", description="LanceDB region")
    local_path: str = Field("./storage/data/lancedb", description="LanceDB local path")
    remote_uri: str = Field("rest://lance-api.cianfhoghlaim.ie", description="LanceDB remote URI")

    model_config = SettingsConfigDict(env_prefix="LANCEDB_")


class LakehouseSettings(BaseSettings):
    """Top-level lakehouse settings aggregating all sub-configs.

    This is the Python-side counterpart of `compose.yaml` env vars. All
    required secrets are loaded via Locket at container start.

    Usage:
        >>> from lakehouse.config import settings
        >>> settings.garage.access_key_id
        >>> settings.lakekeeper.metrics_port
        >>> settings.cognee.postgres_password
    """

    garage: GarageSettings = Field(default_factory=GarageSettings)
    postgres: PostgresSettings = Field(default_factory=PostgresSettings)
    lakekeeper: LakekeeperSettings = Field(default_factory=LakekeeperSettings)
    clickhouse: ClickHouseSettings = Field(default_factory=ClickHouseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    cognee: CogneeSettings = Field(default_factory=CogneeSettings)
    graphiti: GraphitiSettings = Field(default_factory=GraphitiSettings)
    falkordb: FalkorDBSettings = Field(default_factory=FalkorDBSettings)
    memgraph: MemgraphSettings = Field(default_factory=MemgraphSettings)
    lance_namespace: LanceNamespaceSettings = Field(default_factory=LanceNamespaceSettings)
    olake: OlakeSettings = Field(default_factory=OlakeSettings)
    observability: ObservabilitySettings = Field(default_factory=ObservabilitySettings)
    motherduck: MotherduckSettings = Field(default_factory=MotherduckSettings)
    lancedb: LancedbSettings = Field(default_factory=LancedbSettings)

    # Environment file (when imported in scripts that have a .env.local)
    env_file: Optional[str] = Field(
        None,
        description="Path to .env file (default: .env.local if present)",
    )

    model_config = SettingsConfigDict(
        env_file=os.getenv("LAKEHOUSE_ENV_FILE", "./.env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Lazy singleton — load only when accessed (so scripts can still import
# this module even if .env.local is missing)
_settings: Optional[LakehouseSettings] = None


def get_settings() -> LakehouseSettings:
    """Lazy-load the lakehouse settings (raises ValidationError on missing required).

    This function is the recommended entry point — it defers validation
    until the settings are actually accessed, so importing this module
    doesn't fail just because a required secret is missing.

    Usage:
        from lakehouse.config import get_settings
        settings = get_settings()
        print(settings.garage.access_key_id)
    """
    global _settings
    if _settings is None:
        _settings = LakehouseSettings()
    return _settings


# Note: `settings` is NOT exposed as an eager singleton because it would
# fail at module import time when required secrets are missing. Use
# `get_settings()` instead.


__all__ = [
    "GarageSettings",
    "PostgresSettings",
    "LakekeeperSettings",
    "ClickHouseSettings",
    "RedisSettings",
    "CogneeSettings",
    "GraphitiSettings",
    "FalkorDBSettings",
    "MemgraphSettings",
    "LanceNamespaceSettings",
    "OlakeSettings",
    "ObservabilitySettings",
    "MotherduckSettings",
    "LancedbSettings",
    "LakehouseSettings",
    "get_settings",
]
