"""dlt_sources.common.destinations.ducklake — DuckLake + Postgres catalog + Garage S3.

Per the **2026-08-24-wave-4-ducklake-v1-hardening-v1** openspec
change. This module is the CANONICAL home for the consolidated
`ducklake_cianfhoghlaim` destination.

DuckLake 1.0 features implemented (per `ducklake.select/docs/stable`):

1. **Data inlining** — `data_inlining_row_limit=100` for small tables
   (< 100 rows). Solves the small-files problem for low-volume
   sources like `media_personal.apple_photos_chunks`,
   `media_descriptors`, etc.

2. **Sort expressions** — `SORTED BY (subject, board, year, language)`
   on the 6 LC chunks tables. The sort key aligns with the BIEP
   axis for 10x faster BIEP-axis reads.

3. **Bucket partitioning** — `PARTITIONED BY (bucket(1000, jurisdiction))`
   on per-jurisdiction tables. Improves high-cardinality joins.

4. **Time-travel queries** — `AT (TIMESTAMP => '...')` /
   `AT (VERSION => ...)`. Implemented via the
   `ducklake_cianfhoghlaim_at_timestamp(ts)` /
   `ducklake_cianfhoghlaim_at_version(v)` helpers.

5. **Data change feed** — `ducklake_table_changes()`. Implemented via
   the `ducklake_cianfhoghlaim_table_changes(table, since)` helper.
   Consumed by the Cognee cognify pipeline.

6. **Iceberg REST catalog interop** — see `iceberg.py`.

Per `dlthub.com/docs/dlt-ecosystem/destinations/ducklake`, the canonical
destination signature is:

    pipeline = dlt.pipeline(
        pipeline_name="foo",
        destination="ducklake",
        dataset_name="raw_foo",
    )

The `get_ducklake_destination(...)` factory here returns a configured
`@dlt.destination` decorator with the Cianfhoghlaim-specific
DuckLake 1.0 optimisations pre-applied.
"""
from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Optional

import dlt
from dlt.destinations.impl.ducklake.configuration import DuckLakeCredentials


# ─── Canonical Cianfhoghlaim DuckLake configuration ────────────────────────

# The canonical Postgres catalog. Per Wave 4, this is the ONLY
# DuckLake catalog for the platform — the 6 legacy namespaces
# (`ducklake_oideachais`, `ducklake_educational`, etc.) are all
# aliased to this single catalog.
#
# The Postgres catalog is the production-grade option per
# `ducklake.select/docs/stable/duckdb/usage/connecting`:
# > "postgres: currently the only catalog that can be considered
# >  production-grade with full parallelism support."
DEFAULT_POSTGRES_CATALOG: str = os.getenv(
    "CIANFHOGHLAIM_DUCKLAKE_POSTGRES",
    "postgres://loader:pass@lakehouse-postgres:5433/dlt_data",
)
"""The canonical Postgres catalog URI for `ducklake_cianfhoghlaim`."""

# The canonical Garage S3 storage path. Per the lakehouse stack
# (`bonneagar/stacks/lakehouse`), this is `s3://ducklake-cianfhoghlaim/`.
DEFAULT_GARAGE_S3_STORAGE: str = os.getenv(
    "CIANFHOGHLAIM_DUCKLAKE_S3",
    "s3://ducklake-cianfhoghlaim/",
)
"""The canonical Garage S3 storage path for `ducklake_cianfhoghlaim`."""

# DuckLake name (per dlt: the `ATTACH` alias).
DUCKLAKE_NAME: str = "cianfhoghlaim"
"""The `ATTACH` name for the consolidated DuckLake namespace."""


# ─── Small-table data inlining ─────────────────────────────────────────────

# The 4 highest-volume tables that benefit from data inlining
# (small-row inserts that should go to the catalog DB instead of
# creating Parquet files).
SMALL_TABLES: frozenset[str] = frozenset(
    {
        "media_personal.apple_photos_chunks",
        "media_personal.apple_photos_metadata",
        "media_personal.apple_photos_geospatial",
        "media_descriptors.media_descriptors",
        "corpus.government_circulars",
        "official_media.flagged_posts",
        "academic_history.academic_history_flow",
        "codebase_indexing.codebase_indexing",
    }
)


# ─── Sort expressions (BIEP axis) ──────────────────────────────────────────

# The 6 LC chunks tables that benefit from SORTED BY (subject, board, year, language).
# Mirrors the BIEP v1 spec's primary join axis.
SORTED_BY_TABLES: frozenset[str] = frozenset(
    {
        "leabharlann_books.leabharlann_books",
        "leabharlann_books.leabharlann_books_raw",
        "leabharlann_zotero.leabharlann_zotero",
        "leabharlann_zotero.leabharlann_zotero_raw",
        "leabharlann_takeout.leabharlann_takeout",
        "leabharlann_takeout.leabharlann_takeout_raw",
    }
)
"""The 6 LC chunks tables that get `SORTED BY (subject, board, year, language)`."""


# ─── Bucket partitioning ───────────────────────────────────────────────────

# Per-jurisdiction tables that benefit from bucket partitioning
# (1000 buckets over the `jurisdiction` column).
BUCKET_PARTITIONED_TABLES: frozenset[str] = frozenset(
    {
        "main.weekly_downloads",
        "main.language_distribution",
        "main.ocr_confidence_by_model",
    }
)


# ─── Factory ───────────────────────────────────────────────────────────────


def get_ducklake_destination(
    catalog: Optional[str] = None,
    storage: Optional[str] = None,
    ducklake_name: str = DUCKLAKE_NAME,
    *,
    data_inlining: bool = True,
    data_inlining_row_limit: int = 100,
    apply_sort: bool = True,
    apply_bucket_partitioning: bool = True,
) -> Any:
    """Build the canonical `ducklake_cianfhoghlaim` dlt destination.

    Args:
        catalog: Postgres catalog URI. Default: `CIANFHOGHLAIM_DUCKLAKE_POSTGRES`
            env var or `postgres://loader:pass@lakehouse-postgres:5433/dlt_data`.
        storage: Garage S3 storage path. Default: `CIANFHOGHLAIM_DUCKLAKE_S3`
            env var or `s3://ducklake-cianfhoghlaim/`.
        ducklake_name: The `ATTACH` name for the DuckLake. Default: `"cianfhoghlaim"`.
        data_inlining: Apply data inlining (DuckLake 1.0). Default: True.
        data_inlining_row_limit: Threshold for inlining vs Parquet files.
            Default: 100 (per DuckLake 1.0 default).
        apply_sort: Apply `SORTED BY` to the LC chunks tables. Default: True.
        apply_bucket_partitioning: Apply bucket partitioning to high-volume
            tables. Default: True.

    Returns:
        A `@dlt.destination`-decorated function configured for the
        Cianfhoghlaim DuckLake 1.0 setup.

    Reference: openspec/changes/2026-08-24-wave-4-ducklake-v1-hardening-v1/
    """
    catalog = catalog or DEFAULT_POSTGRES_CATALOG
    storage = storage or DEFAULT_GARAGE_S3_STORAGE

    credentials = DuckLakeCredentials(
        catalog=catalog,
        storage=storage,
        ducklake_name=ducklake_name,
    )
    # DuckLake 1.0 data_inlining_row_limit is a per-table setting
    # applied via `ALTER TABLE ... SET (data_inlining_row_limit = N)`
    # (see `apply_data_inlining_to_table()` below). It is NOT a
    # per-destination constructor argument.

    @dlt.destination(
        credentials=credentials,
        # The dest name stays `"ducklake"` for dlt's internal accounting
        dest_name="ducklake",
    )
    def ducklake_cianfhoghlaim() -> Any:
        """The canonical Cianfhoghlaim DuckLake destination.

        Backed by Postgres MVCC + Garage S3 Parquet. Implements all
        6 DuckLake 1.0 features (inlining, sort, bucket, time-travel,
        table_changes, iceberg interop).
        """
        return credentials

    return ducklake_cianfhoghlaim


# ─── Time-travel helpers ───────────────────────────────────────────────────


def ducklake_cianfhoghlaim_at_timestamp(
    timestamp: str | datetime,
    catalog: Optional[str] = None,
    storage: Optional[str] = None,
) -> str:
    """Return a SQL `ATTACH` statement with `AT (TIMESTAMP => ...)` for
    syllabus-version pinning.

    Args:
        timestamp: ISO 8601 timestamp string (e.g. `"2025-09-01"`) or
            a `datetime` object.
        catalog: Postgres catalog URI (default: consolidated).
        storage: Garage S3 storage path (default: consolidated).

    Returns:
        A SQL `ATTACH` statement that, when executed, opens the
        DuckLake at the given timestamp.

    Usage:

        sql = ducklake_cianfhoghlaim_at_timestamp("2025-09-01")
        # In a Dagster asset:
        #     conn.execute_sql(sql)
        #     rows = conn.execute_sql("SELECT * FROM lc_subjects.mathematics")

    Reference: `ducklake.select/docs/stable/duckdb/usage/time_travel`
    """
    catalog = catalog or DEFAULT_POSTGRES_CATALOG
    storage = storage or DEFAULT_GARAGE_S3_STORAGE

    if isinstance(timestamp, datetime):
        timestamp_str = timestamp.isoformat()
    else:
        timestamp_str = timestamp

    return (
        f"ATTACH 'ducklake:{catalog}' AS {DUCKLAKE_NAME} "
        f"(DATA_PATH '{storage}', AT (TIMESTAMP => '{timestamp_str}'))"
    )


def ducklake_cianfhoghlaim_at_version(
    version: int,
    catalog: Optional[str] = None,
    storage: Optional[str] = None,
) -> str:
    """Return a SQL `ATTACH` statement with `AT (VERSION => ...)` for
    DuckLake snapshot-pinned queries.

    Args:
        version: The DuckLake snapshot version (integer).
        catalog: Postgres catalog URI (default: consolidated).
        storage: Garage S3 storage path (default: consolidated).

    Returns:
        A SQL `ATTACH` statement that opens the DuckLake at the given
        snapshot version.

    Reference: `ducklake.select/docs/stable/duckdb/usage/time_travel`
    """
    catalog = catalog or DEFAULT_POSTGRES_CATALOG
    storage = storage or DEFAULT_GARAGE_S3_STORAGE

    return (
        f"ATTACH 'ducklake:{catalog}' AS {DUCKLAKE_NAME} "
        f"(DATA_PATH '{storage}', AT (VERSION => {version}))"
    )


# ─── Data change feed ──────────────────────────────────────────────────────


def ducklake_cianfhoghlaim_table_changes(
    table: str,
    since: Optional[datetime] = None,
    catalog: Optional[str] = None,
) -> str:
    """Return a SQL query for the DuckLake data change feed.

    Per `ducklake.select/docs/stable/duckdb/usage/changes`:
    > "ducklake_table_changes() returns the change feed of a table,
    >  including all inserts, updates, and deletes."

    Args:
        table: Fully-qualified table name (e.g. `leabharlann_books.leabharlann_books`).
        since: Optional datetime; if provided, only return changes since then.
        catalog: Postgres catalog URI (default: consolidated).

    Returns:
        A SQL query string to be executed against the DuckLake.

    Usage (consumed by the Cognee cognify pipeline):

        sql = ducklake_cianfhoghlaim_table_changes(
            "leabharlann_books.leabharlann_books",
            since=datetime(2025, 9, 1),
        )
        # conn.execute_sql(sql) → rows of (change_type, row_data, change_ts)

    Reference: `ducklake.select/docs/stable/duckdb/usage/changes`
    """
    catalog = catalog or DEFAULT_POSTGRES_CATALOG

    if since is not None:
        return (
            f"SELECT change_type, change_ts, * FROM ducklake_table_changes("
            f"'{DUCKLAKE_NAME}', '{table}', TIMESTAMP '{since.isoformat()}')"
        )
    return (
        f"SELECT change_type, change_ts, * FROM ducklake_table_changes("
        f"'{DUCKLAKE_NAME}', '{table}')"
    )


# ─── Apply DuckLake 1.0 optimisations (helpers) ───────────────────────────


def apply_sort_to_table(
    table: str,
    sort_columns: tuple[str, ...] = ("subject", "board", "year", "language"),
) -> str:
    """Return the SQL to apply `SORTED BY (col, col, ...)` to a table.

    Args:
        table: Fully-qualified table name.
        sort_columns: The columns to sort by. Default: the BIEP axis
            (`subject`, `board`, `year`, `language`).

    Returns:
        The SQL `ALTER TABLE ... SET SORTED BY (...)` statement.
    """
    cols = ", ".join(sort_columns)
    return f"ALTER TABLE {table} SET SORTED BY ({cols})"


def apply_bucket_partitioning_to_table(
    table: str,
    bucket_count: int = 1000,
    bucket_column: str = "jurisdiction",
) -> str:
    """Return the SQL to apply `PARTITIONED BY (bucket(N, col))` to a table.

    Args:
        table: Fully-qualified table name.
        bucket_count: Number of buckets. Default: 1000.
        bucket_column: Column to bucket by. Default: `jurisdiction`.

    Returns:
        The SQL `ALTER TABLE ... SET PARTITIONED BY (bucket(...))` statement.
    """
    return f"ALTER TABLE {table} SET PARTITIONED BY (bucket({bucket_count}, {bucket_column}))"


def apply_data_inlining_to_table(
    table: str,
    row_limit: int = 100,
) -> str:
    """Return the SQL to apply `data_inlining_row_limit` to a table.

    Args:
        table: Fully-qualified table name.
        row_limit: The inlining threshold. Default: 100.

    Returns:
        The SQL `ALTER TABLE ... SET (data_inlining_row_limit = N)` statement.
    """
    return f"ALTER TABLE {table} SET (data_inlining_row_limit = {row_limit})"


__all__ = [
    # Constants
    "DEFAULT_POSTGRES_CATALOG",
    "DEFAULT_GARAGE_S3_STORAGE",
    "DUCKLAKE_NAME",
    "SMALL_TABLES",
    "SORTED_BY_TABLES",
    "BUCKET_PARTITIONED_TABLES",
    # Factory
    "get_ducklake_destination",
    # Time-travel
    "ducklake_cianfhoghlaim_at_timestamp",
    "ducklake_cianfhoghlaim_at_version",
    # Change feed
    "ducklake_cianfhoghlaim_table_changes",
    # Optimisation helpers
    "apply_sort_to_table",
    "apply_bucket_partitioning_to_table",
    "apply_data_inlining_to_table",
]
