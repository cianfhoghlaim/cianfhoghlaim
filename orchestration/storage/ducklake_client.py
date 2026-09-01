"""DEPRECATION SHIM — re-exports from ``dlt_sources.destinations.ducklake``.

Per Wave 4 §4.8 of the 2026-08-24 master refactor plan. This file
was previously the canonical DuckLake client implementation (per the
2026-08-08-lakehouse-extensive-hydration-v1 change) but is now
**superseded** by the canonical destination module at
``dlt_sources/destinations/ducklake.py`` (the dlt-first-party
``DuckLakeCredentials`` + the Wave 1 layer-grouped destinations +
the Wave 4 v1.0 best practices).

The historical original implementation (DuckLakeConfig + DuckLakeClient
+ hand-rolled ``ATTACH`` SQL) is preserved verbatim below for
reference + backwards compatibility. **Any new caller should import
from the canonical location**:

    # ✅ Canonical (post Wave 4):
    from dlt_sources.destinations.ducklake import get_ducklake_destination
    from dlt_sources.destinations.ducklake import get_ducklake_namespace

    # ⚠️ Legacy (still works; prints DeprecationWarning):
    from orchestration.storage.ducklake_client import DuckLakeClient  # noqa: F401
"""

from __future__ import annotations

import os
import warnings
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Re-export the canonical DuckLake v1.0 best-practice surface. Per
# Wave 4 §4.1 + §4.5 + §4.6 + §4.7, these are the canonical access
# points; the legacy ``DuckLakeClient`` / ``DuckLakeConfig`` classes
# below are preserved verbatim and emit a DeprecationWarning on
# construction.
from dlt_sources.destinations.ducklake import (  # noqa: F401
    DEFAULT_GARAGE_S3_STORAGE,
    DEFAULT_LAKEKEEPER_ENDPOINT,
    DEFAULT_POSTGRES_CATALOG,
    DUCKLAKE_NAME,
    DUCKLAKE_NAMESPACE,
    attach_as_iceberg_rest_sql,
    ducklake_cianfhoghlaim_table_changes,
    expire_snapshots_all_quadrants,
    get_ducklake_destination,
    get_ducklake_namespace,
    get_iceberg_rest_endpoint,
    set_namespace_encryption_sql,
)


# Backwards-compatible alias. The legacy ``get_dlt_destination()``
# signature used ``(use_ducklake=None, namespace="cianfhoghlaim")``;
# the canonical ``get_ducklake_destination(...)`` takes different
# params. The legacy function name is not re-exported here because
# it never existed in the canonical ``dlt_sources.destinations``
# package — callers should adopt ``get_ducklake_destination`` instead.


@dataclass
class DuckLakeConfig:
    """Resolved DuckLake connection configuration.

    DEPRECATED. Use ``dlt_sources.destinations.ducklake.DuckLakeCredentials``
    via ``get_ducklake_destination()`` instead.
    """

    s3_endpoint: str
    s3_bucket: str
    s3_region: str
    s3_access_key_id: str
    s3_secret_access_key: str
    postgres_host: str
    postgres_port: str
    postgres_db: str
    postgres_user: str
    postgres_password: str
    namespace: str  # the cianfhoghlaim namespace (e.g. "cianfhoghlaim")

    @classmethod
    def from_env(cls, namespace: str = "cianfhoghlaim") -> "DuckLakeConfig":
        """Resolve DuckLake config from environment variables.

        DEPRECATED. The canonical path is
        ``get_ducklake_destination()`` which reads the same env vars
        via the canonical env-var contract (per Wave 1
        ``_common.REQUIRED_ENV_VARS``).
        """
        warnings.warn(
            "DuckLakeConfig.from_env() is deprecated; use "
            "dlt_sources.destinations.ducklake.get_ducklake_destination() "
            "instead. This shim will be removed in a future release.",
            DeprecationWarning,
            stacklevel=2,
        )
        return cls(
            s3_endpoint=os.environ.get("GARAGE_S3_ENDPOINT", "http://localhost:3900"),
            s3_bucket=os.environ.get("GARAGE_BUCKET", f"ducklake-{namespace}"),
            s3_region=os.environ.get("AWS_REGION", "garage"),
            s3_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID")
            or os.environ.get("GARAGE_ACCESS_KEY_ID", ""),
            s3_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY")
            or os.environ.get("GARAGE_SECRET_ACCESS_KEY", ""),
            postgres_host=os.environ.get("DUCKLAKE_POSTGRES_HOST", "localhost"),
            postgres_port=os.environ.get("DUCKLAKE_POSTGRES_PORT", "5433"),
            postgres_db=os.environ.get("DUCKLAKE_POSTGRES_DB", f"ducklake_{namespace}"),
            postgres_user=os.environ.get("DUCKLAKE_POSTGRES_USER", "lakekeeper"),
            postgres_password=os.environ.get("DUCKLAKE_POSTGRES_PASSWORD", ""),
            namespace=namespace,
        )

    def duckdb_secret_sql(self) -> str:
        """Render the DuckDB secret SQL for S3 access.

        DEPRECATED. Equivalent to the canonical
        ``DuckLakeCredentials(storage=...)`` constructor.
        """
        return (
            f"CREATE OR REPLACE SECRET lakehouse_s3 ("
            f"TYPE S3, PROVIDER config, "
            f"ENDPOINT '{self.s3_endpoint}', "
            f"URL_STYLE 'path', "
            f"USE_SSL false, "
            f"REGION '{self.s3_region}', "
            f"KEY_ID '{self.s3_access_key_id}', "
            f"SECRET '{self.s3_secret_access_key}');"
        )

    def duckdb_attach_sql(self, alias: str = "lakehouse") -> str:
        """Render the DuckDB ATTACH SQL for the DuckLake catalog.

        DEPRECATED. Equivalent to the canonical
        ``get_ducklake_destination(catalog=..., storage=...)``.
        """
        return (
            f"ATTACH 'ducklake:postgres:"
            f"dbname={self.postgres_db} "
            f"host={self.postgres_host} "
            f"port={self.postgres_port} "
            f"user={self.postgres_user} "
            f"password={self.postgres_password}' "
            f"AS {alias} (DATA_PATH 's3://{self.s3_bucket}/');"
        )


class DuckLakeClient:
    """DEPRECATION SHIM for the legacy DuckLake client (Wave 4 §4.8).

    The canonical implementation is now
    ``dlt_sources.destinations.ducklake.get_ducklake_destination()``
    (the dlt-first-party ``DuckLakeCredentials`` + the Wave 4 v1.0
    best practices). New code MUST use the canonical path; this
    shim is preserved for backwards compatibility only and emits a
    ``DeprecationWarning`` on construction.
    """

    def __init__(self, storage_path: str | os.PathLike[str] | None = None, namespace: str = "cianfhoghlaim"):
        warnings.warn(
            "DuckLakeClient is deprecated; use "
            "dlt_sources.destinations.ducklake.get_ducklake_destination() "
            "instead. This shim will be removed in a future release.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.storage_path = Path(storage_path) if storage_path else Path("./storage/data/ducklake")
        self.namespace = namespace
        self.config = DuckLakeConfig.from_env(namespace=namespace)

    @contextmanager
    def connect(self, alias: str = "lakehouse") -> Generator[Any, None, None]:
        """Yield a DuckDB connection with the DuckLake catalog attached.

        DEPRECATED. The canonical path is ``get_ducklake_destination()``
        which returns a dlt destination; raw DuckDB connections should
        use ``DuckLakeResource.get_client()`` in
        ``orchestration/resources.py``.
        """
        import duckdb

        self.storage_path.mkdir(parents=True, exist_ok=True)
        conn = duckdb.connect(str(self.storage_path / "lakehouse.duckdb"))
        try:
            conn.execute(self.config.duckdb_secret_sql())
            conn.execute(self.config.duckdb_attach_sql(alias=alias))
            yield conn
        finally:
            conn.close()

    def execute(self, query: str, params: tuple | None = None) -> list[tuple]:
        """Execute a single query and return all rows.

        DEPRECATED. Use ``DuckLakeResource.get_client()`` + execute
        directly, or ``motherduck_execute_query`` for federated queries.
        """
        with self.connect() as conn:
            if params:
                return conn.execute(query, params).fetchall()
            return conn.execute(query).fetchall()

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the DuckLake catalog.

        DEPRECATED. Use the canonical
        ``select count(*) from <namespace>.information_schema.tables``
        via ``DuckLakeResource.get_client()`` instead.
        """
        with self.connect() as conn:
            result = conn.execute(
                "SELECT COUNT(*) FROM lakehouse.information_schema.tables "
                "WHERE table_schema = ? AND table_name = ?",
                (self.namespace, table_name),
            ).fetchone()
            return bool(result and result[0] > 0)


__all__ = [
    # Canonical re-exports (Wave 4 §4.8 — the new public surface)
    "DUCKLAKE_NAMESPACE",
    "DUCKLAKE_NAME",
    "DEFAULT_POSTGRES_CATALOG",
    "DEFAULT_GARAGE_S3_STORAGE",
    "DEFAULT_LAKEKEEPER_ENDPOINT",
    "get_ducklake_namespace",
    "get_ducklake_destination",
    "ducklake_cianfhoghlaim_table_changes",
    "set_namespace_encryption_sql",
    "expire_snapshots_all_quadrants",
    "get_iceberg_rest_endpoint",
    "attach_as_iceberg_rest_sql",
    # Legacy shim classes (deprecated — preserved for back-compat)
    "DuckLakeConfig",
    "DuckLakeClient",
]
