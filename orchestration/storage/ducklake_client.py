"""
DuckLake Client — DEPRECATED, kept only for backwards compatibility.

Per the 2026-08-08-lakehouse-extensive-hydration-v1 change: this module's
docstring used to claim it was "the canonical DuckLake client... imported
by `orchestration.resources.DuckLakeResource.get_client()`" and that it
"MUST be importable as `storage.ducklake_client.DuckLakeClient`" per a
`2026-08-13-biep-v3-systematic-download-ireland-england-v1` change —
that top-level `storage` package never existed anywhere in the repo, so
every real call to `DuckLakeResource.get_client()` raised
`ModuleNotFoundError` until this pass fixed it.

The actual canonical implementation is now
`dlt_sources.common.destinations_cianfhoghlaim` — it's the only one of
the 4+ divergent DuckLake client implementations that existed across the
repo (this file, `sruth/oideachais/storage/{ducklake_client,ducklake,
config}.py`, `sruth/crypteolas/storage/ducklake_client.py`) using dlt's
first-party `DuckLakeCredentials` config object instead of hand-rolled
`ATTACH` SQL strings, and it already documents the canonical bucket name
(`ducklake-cianfhoghlaim`) and env var names. `DuckLakeResource` in
`orchestration/resources.py` now wraps that module directly and no
longer imports anything from here.

Verified (grep, root `cianfhoghlaim`/`orchestration` package only) that
nothing in the root package imports `DuckLakeClient` from this file
anymore — it's kept in place rather than deleted only because the
sibling `sruth/oideachais/` and `sruth/crypteolas/` packages (separate
`pyproject.toml` workspaces, not reachable from `orchestration/` code
regardless) still define their own near-duplicate versions of this same
class. Consolidating those is flagged as separate follow-up work, out of
scope here since it crosses a package boundary this change doesn't
otherwise touch.

Original docstring content (connection pattern, credential tiers) below
is still accurate as a description of this file's own behavior if it is
used directly — just not as "the" canonical path anymore.

    client = DuckLakeClient(storage_path="./storage/data/ducklake")
    with client.connect() as conn:
        rows = conn.execute("SELECT * FROM cianfhoghlaim.education.ireland.leaving_cycle.mathematics").fetchall()

- Local: PostgreSQL `ducklake_oideachais` (created by `lakehouse-postgres` init-db.sql)
        + Garage S3 `s3://ducklake-cianfhoghlaim/<namespace>/<dataset>/`
- Production: Cloudflare R2 + PlanetScale Postgres (override via env vars)
"""

from __future__ import annotations

import os
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class DuckLakeConfig:
    """Resolved DuckLake connection configuration."""

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

        The lakehouse stack (`bonneagar/stacks/lakehouse/.env.dev`) sets
        `GARAGE_*` style env vars; this helper maps them to the AWS_*
        style that DuckDB's S3 extension expects.
        """
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
        """Render the DuckDB secret SQL for S3 access."""
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
        """Render the DuckDB ATTACH SQL for the DuckLake catalog."""
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
    """Canonical DuckLake client for the BIEP v3 lakehouse.

    Wraps the DuckDB `ATTACH 'ducklake:...'` pattern and exposes a
    `connect()` context manager that yields a ready-to-use DuckDB
    connection with the DuckLake catalog attached.
    """

    def __init__(self, storage_path: str | os.PathLike[str] | None = None, namespace: str = "cianfhoghlaim"):
        self.storage_path = Path(storage_path) if storage_path else Path("./storage/data/ducklake")
        self.namespace = namespace
        self.config = DuckLakeConfig.from_env(namespace=namespace)

    @contextmanager
    def connect(self, alias: str = "lakehouse") -> Generator[Any, None, None]:
        """Yield a DuckDB connection with the DuckLake catalog attached.

        The connection has the `lakehouse_s3` secret + the `lakehouse`
        DuckLake ATTACH setup. Caller can then query e.g.

            SELECT * FROM lakehouse.cianfhoghlaim.education.ireland.leaving_cycle.mathematics
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
        """Execute a single query and return all rows."""
        with self.connect() as conn:
            if params:
                return conn.execute(query, params).fetchall()
            return conn.execute(query).fetchall()

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the DuckLake catalog.

        `table_name` is the unqualified table name (e.g.
        `mathematics`); the schema is the cianfhoghlaim namespace.
        """
        with self.connect() as conn:
            result = conn.execute(
                "SELECT COUNT(*) FROM lakehouse.information_schema.tables "
                "WHERE table_schema = ? AND table_name = ?",
                (self.namespace, table_name),
            ).fetchone()
            return bool(result and result[0] > 0)


__all__ = ["DuckLakeClient", "DuckLakeConfig"]
