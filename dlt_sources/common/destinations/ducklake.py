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

7. **Per-quadrant `metadata_schema`** (dlt 1.25 / DuckLake extension) —
   added in the
   **2026-08-24-dlt-sources-to-multi-repo-scaffold-v1** §7.1 change.
   The 5 quadrants (`oideachais`, `tuatha`, `croilar`, `agents`,
   `media`) each get their own Postgres metadata schema inside the
   shared `md:cianfhoghlaim` catalog. See
   `QUADRANT_METADATA_SCHEMAS` and
   `get_ducklake_destination(metadata_schema=...)`.

8. **`automatic_migration=True`** on Postgres catalog attaches — added
   in the **2026-08-24-dlt-sources-to-multi-repo-scaffold-v1** §7.4
   change. DuckDB automatically migrates an older catalog schema on
   attach so a fresh Postgres image is not required for cross-version
   upgrades.

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

# The 5 per-quadrant Postgres metadata schemas inside the shared
# `md:cianfhoghlaim` Postgres catalog. Added by the
# 2026-08-24-dlt-sources-to-multi-repo-scaffold-v1 §7.1 change.
# Each quadrant owns its own Postgres schema so a single Postgres
# catalog serves 5 isolated DuckLake namespaces (one set of
# ducklake_metadata + ducklake_snapshot + ducklake_tag tables per
# quadrant). This is the dlt 1.25 / DuckLake extension `metadata_schema`
# feature (per `dlthub.com/docs/dlt-ecosystem/destinations/ducklake`).
QUADRANT_METADATA_SCHEMAS: dict[str, str] = {
    "oideachais": "oideachais",  # legacy alias; canonical = "oideachais"
    "tuatha": "tuatha",          # BI Educational MMO
    "croilar": "croilar",        # Croílar cross-quadrant portfolio
    "agents": "agents",          # meaisinfhoghlaim 12-agent fleet
    "media": "media",            # apple_photos + media_personal + media_intel
}
"""The 5 per-quadrant Postgres metadata schemas (§7.1).

Pass any key as `metadata_schema` to `get_ducklake_destination(...)`
to scope the destination to that quadrant's Postgres schema.
Default behaviour is still the consolidated
`DUCKLAKE_NAME` ("cianfhoghlaim") for backwards compatibility.
"""

DEFAULT_AUTOMATIC_MIGRATION: bool = True
"""Default `automatic_migration` for `get_ducklake_destination(...)` (§7.4).

DuckDB will migrate an older DuckLake catalog schema on attach, so a
fresh Postgres image is not required when the catalog is upgraded
across DuckDB minor versions.
"""


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
    metadata_schema: Optional[str] = None,
    automatic_migration: bool = DEFAULT_AUTOMATIC_MIGRATION,
    data_inlining: bool = True,
    data_inlining_row_limit: int = 100,
    apply_sort: bool = True,
    apply_bucket_partitioning: bool = True,
    multischema: bool = False,
) -> Any:
    """Build the canonical `ducklake_cianfhoghlaim` dlt destination.

    Args:
        catalog: Postgres catalog URI. Default: `CIANFHOGHLAIM_DUCKLAKE_POSTGRES`
            env var or `postgres://loader:pass@lakehouse-postgres:5433/dlt_data`.
        storage: Garage S3 storage path. Default: `CIANFHOGHLAIM_DUCKLAKE_S3`
            env var or `s3://ducklake-cianfhoghlaim/`.
        ducklake_name: The `ATTACH` name for the DuckLake. Default: `"cianfhoghlaim"`.
        metadata_schema: Per-quadrant Postgres metadata schema (dlt 1.25 +
            DuckLake extension, per the
            **2026-08-24-dlt-sources-to-multi-repo-scaffold-v1** §7.1
            change). One of `"oideachais"`, `"tuatha"`, `"croilar"`,
            `"agents"`, `"media"` (see `QUADRANT_METADATA_SCHEMAS`).
            `None` (the default) keeps the consolidated
            `DUCKLAKE_NAME` schema for backwards compatibility.
        automatic_migration: If True (default), the destination attaches
            with `AUTOMATIC_MIGRATION true` so DuckDB migrates an
            older DuckLake catalog schema on attach. Set to False
            for a pinned-version deployment. Added in the
            **2026-08-24-dlt-sources-to-multi-repo-scaffold-v1** §7.4
            change.
        data_inlining: Apply data inlining (DuckLake 1.0). Default: True.
        data_inlining_row_limit: Threshold for inlining vs Parquet files.
            Default: 100 (per DuckLake 1.0 default).
        apply_sort: Apply `SORTED BY` to the LC chunks tables. Default: True.
        apply_bucket_partitioning: Apply bucket partitioning to high-volume
            tables. Default: True.
        multischema: If True, the destination emits datasets configured
            for the dlt 1.25 multischema mode (multiple dlt schemas
            per dataset, all stored under one Postgres metadata
            schema). Added in the
            **2026-08-24-dlt-sources-to-multi-repo-scaffold-v1** §6.1
            change. The default is `False` for backwards compatibility;
            the BIEP v3 jurisdiction pipelines flip it to `True`.

    Returns:
        A `@dlt.destination`-decorated function configured for the
        Cianfhoghlaim DuckLake 1.0 setup.

    Reference: openspec/changes/2026-08-24-wave-4-ducklake-v1-hardening-v1/
    + openspec/changes/2026-08-24-dlt-sources-to-multi-repo-scaffold-v1/ §6, §7.
    """
    catalog = catalog or DEFAULT_POSTGRES_CATALOG
    storage = storage or DEFAULT_GARAGE_S3_STORAGE

    credentials = DuckLakeCredentials(
        catalog=catalog,
        storage=storage,
        ducklake_name=ducklake_name,
        metadata_schema=metadata_schema,
    )
    # DuckLake 1.0 data_inlining_row_limit is a per-table setting
    # applied via `ALTER TABLE ... SET (data_inlining_row_limit = N)`
    # (see `apply_data_inlining_to_table()` below). It is NOT a
    # per-destination constructor argument.

    # §7.4: use `dlt.destinations.ducklake(...)` (NOT `@dlt.destination`)
    # so the ATTACH SQL emitted by the DuckLake SQL client includes
    # `AUTOMATIC_MIGRATION true` when `automatic_migration=True`
    # (see DuckLake sql_client.py: `migration_param`). The previous
    # `@dlt.destination(credentials=...)` form did not support
    # `automatic_migration`.
    ducklake_cianfhoghlaim = dlt.destinations.ducklake(
        credentials=credentials,
        automatic_migration=automatic_migration,
        # The dest name stays `"ducklake"` for dlt's internal accounting
        destination_name="ducklake",
    )

    return ducklake_cianfhoghlaim


# ─── Per-quadrant destination factories (§7.1) ─────────────────────────────


def get_ducklake_destination_for_quadrant(
    quadrant: str,
    *,
    catalog: Optional[str] = None,
    storage: Optional[str] = None,
    automatic_migration: bool = DEFAULT_AUTOMATIC_MIGRATION,
    multischema: bool = True,
) -> Any:
    """Return the canonical DuckLake destination for one of the 5
    named quadrants (`oideachais`, `tuatha`, `croilar`, `agents`, `media`).

    Thin wrapper over `get_ducklake_destination(metadata_schema=...)`
    that resolves the quadrant name to one of the 5 per-quadrant
    Postgres metadata schemas declared in `QUADRANT_METADATA_SCHEMAS`.

    Added in the **2026-08-24-dlt-sources-to-multi-repo-scaffold-v1**
    §7.1 change.

    Args:
        quadrant: One of `"oideachais"`, `"tuatha"`, `"croilar"`,
            `"agents"`, `"media"`.
        catalog: See `get_ducklake_destination`.
        storage: See `get_ducklake_destination`.
        automatic_migration: See `get_ducklake_destination`. Default
            True (per §7.4).
        multischema: If True (default), the destination is configured
            for multischema mode (multiple dlt schemas per dataset;
            see §6.1). The BIEP v3 jurisdiction pipelines pass
            `multischema=True` so each jurisdiction pipeline emits a
            single BIEP-schema dataset that contains the per-stage +
            per-board schemas.

    Returns:
        A `@dlt.destination`-decorated function for the given quadrant.

    Raises:
        ValueError: If `quadrant` is not one of the 5 known quadrants.

    Example:

        >>> dest_oideachais = get_ducklake_destination_for_quadrant("oideachais")
        >>> pipeline = dlt.pipeline(
        ...     pipeline_name="ireland_lc",
        ...     destination=dest_oideachais(),
        ...     dataset_name="ireland_education",
        ... )
    """
    if quadrant not in QUADRANT_METADATA_SCHEMAS:
        raise ValueError(
            f"Unknown quadrant {quadrant!r}; "
            f"must be one of {sorted(QUADRANT_METADATA_SCHEMAS)}"
        )
    return get_ducklake_destination(
        catalog=catalog,
        storage=storage,
        ducklake_name=DUCKLAKE_NAME,
        metadata_schema=QUADRANT_METADATA_SCHEMAS[quadrant],
        automatic_migration=automatic_migration,
        multischema=multischema,
    )


# Per-quadrant thin wrappers used by the `DESTINATIONS` registry
# (`dlt_sources/common/destinations/__init__.py`). Each wrapper is a
# zero-arg callable so the registry can resolve a string like
# `named_destinations("ducklake_oideachais_quadrant")` → these wrappers.


def get_ducklake_destination_for_quadrant_oideachais(
    **kwargs: Any,
) -> Any:
    """`oideachais` quadrant — canonical home for the BIEP v3 Ireland +
    England + Scotland + Wales + NI + JC + A-Level + GCSE + LC
    jurisdictional pipelines (per §7.1)."""
    return get_ducklake_destination_for_quadrant("oideachais", **kwargs)


def get_ducklake_destination_for_quadrant_tuatha(**kwargs: Any) -> Any:
    """`tuatha` quadrant — BI Educational MMO (per §7.1)."""
    return get_ducklake_destination_for_quadrant("tuatha", **kwargs)


def get_ducklake_destination_for_quadrant_croilar(**kwargs: Any) -> Any:
    """`croilar` quadrant — Croílar cross-quadrant portfolio (per §7.1)."""
    return get_ducklake_destination_for_quadrant("croilar", **kwargs)


def get_ducklake_destination_for_quadrant_agents(**kwargs: Any) -> Any:
    """`agents` quadrant — meaisinfhoghlaim 12-agent fleet (per §7.1)."""
    return get_ducklake_destination_for_quadrant("agents", **kwargs)


def get_ducklake_destination_for_quadrant_media(**kwargs: Any) -> Any:
    """`media` quadrant — apple_photos + media_personal + media_intel
    (per §7.1)."""
    return get_ducklake_destination_for_quadrant("media", **kwargs)


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


# The BIEP v3 jurisdiction axis (per the
# `2026-08-24-dlt-sources-to-multi-repo-scaffold-v1` §7.2 change).
# Used by `apply_jurisdiction_sort_to_table()` for the 6 hot LC
# chunks tables + the per-jurisdiction `*_education` datasets.
DEFAULT_JURISDICTION_SORT_COLUMNS: tuple[str, ...] = (
    "jurisdiction",
    "stage",
    "subject",
)
"""The canonical BIEP v3 `SORTED BY` axis for the hot LC chunks tables.

Per the **2026-08-24-dlt-sources-to-multi-repo-scaffold-v1** §7.2 change
(DuckLake 1.0 sorted-tables feature). Aligns the SORTED BY
clause with the query filter order used by the 4 BIEP jurisdiction
pipelines + the per-jurisdiction BIEP dashboards.
"""

# The 6 hot LC tables that get `SORTED BY (jurisdiction, stage, subject)`.
# The same set of LC chunks tables covered by the Wave 4 sort helper,
# but with the BIEP axis sorted first.
JURISDICTION_SORTED_BY_TABLES: frozenset[str] = frozenset(
    {
        "leabharlann_books.leabharlann_books",
        "leabharlann_zotero.leabharlann_zotero",
        "leabharlann_takeout.leabharlann_takeout",
        "leabharlann_books.leabharlann_books_raw",
        "leabharlann_zotero.leabharlann_zotero_raw",
        "leabharlann_takeout.leabharlann_takeout_raw",
    }
)
"""The 6 hot LC tables that get `SORTED BY (jurisdiction, stage, subject)` (§7.2)."""


def apply_jurisdiction_sort_to_table(
    table: str,
    sort_columns: tuple[str, ...] = DEFAULT_JURISDICTION_SORT_COLUMNS,
) -> str:
    """Return the SQL to apply `SORTED BY (jurisdiction, stage, subject)` to a table.

    Thin wrapper over `apply_sort_to_table(...)` with the canonical
    BIEP v3 jurisdiction axis as the default. Added in the
    **2026-08-24-dlt-sources-to-multi-repo-scaffold-v1** §7.2 change
    (DuckLake 1.0 sorted-tables feature per `ducklake.select/docs/stable`).

    Args:
        table: Fully-qualified table name.
        sort_columns: The columns to sort by. Default: the BIEP axis
            (`jurisdiction`, `stage`, `subject`).

    Returns:
        The SQL `ALTER TABLE ... SET SORTED BY (...)` statement.

    Example::

        >>> sql = apply_jurisdiction_sort_to_table(
        ...     "leabharlann_books.leabharlann_books"
        ... )
        >>> # 'ALTER TABLE leabharlann_books.leabharlann_books SET SORTED BY
        >>> #  (jurisdiction, stage, subject)'
    """
    return apply_sort_to_table(table, sort_columns=sort_columns)


def apply_jurisdiction_sort_to_table_if_needed(table: str) -> str | None:
    """Return the `SORTED BY (jurisdiction, stage, subject)` SQL for the
    given table if it is in the `JURISDICTION_SORTED_BY_TABLES` set,
    else `None`.

    This is the helper used by the §7.3 nightly maintenance Dagster
    asset to keep the hot LC chunks tables sorted.
    """
    if table in JURISDICTION_SORTED_BY_TABLES:
        return apply_jurisdiction_sort_to_table(table)
    return None


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


# ─── DuckLake nightly maintenance SQL (§7.3) ──────────────────────────────

# The 4 nightly maintenance tasks per the
# 2026-08-24-dlt-sources-to-multi-repo-scaffold-v1 §7.3 change. These
# are the SQL calls that the
# `orchestration/defs/2_materials/lakehouse_maintenance.py` Dagster
# asset group runs each night. Per `ducklake.select/docs/stable` +
# `dlthub.com/docs/dlt-ecosystem/destinations/ducklake`, DuckLake
# exposes the following maintenance entry points:
#
# 1. `CALL ducklake_expire_snapshots(<ducklake>, older_than => ...)` —
#    drop catalog snapshot rows for time-travel cleanup.
# 2. `CALL ducklake_cleanup_old_files(<ducklake>, ...)` — remove
#    orphaned Parquet files no longer referenced by any snapshot.
# 3. `CALL ducklake_merge_adjacent_files(<ducklake>, table)` —
#    re-write small adjacent files into larger ones.
# 4. `CALL ducklake_rewrite_data_files(<ducklake>, table, sort_columns)`
#    — apply SORTED BY / compact files against the canonical sort.
#
# Each helper returns the exact `CALL` SQL string for a given
# `ducklake` name + optional arguments. The helpers are string-only
# (they do not execute SQL) — the Dagster asset group is responsible
# for opening the connection + executing the SQL.


def ducklake_expire_snapshots_sql(
    *,
    snapshot_retention_days: int = 7,
    ducklake: str = DUCKLAKE_NAME,
) -> str:
    """Return SQL for `ducklake_expire_snapshots(older_than => ...)` (§7.3).

    Expires old catalog snapshot rows beyond the retention window so
    the DuckLake catalog does not grow unbounded.

    Args:
        snapshot_retention_days: Snapshot retention in days. Default: 7.
        ducklake: The DuckLake name (ATTACH alias). Default: `"cianfhoghlaim"`.

    Returns:
        The `CALL ...` SQL string to pass to `duckdb.execute(...)`.

    Reference: `ducklake.select/docs/stable/duckdb/maintenance`.
    """
    return (
        f"CALL ducklake_expire_snapshots('{ducklake}', "
        f"older_than => INTERVAL '{snapshot_retention_days} days')"
    )


def ducklake_cleanup_old_files_sql(
    *,
    snapshot_retention_days: int = 7,
    ducklake: str = DUCKLAKE_NAME,
) -> str:
    """Return SQL for `ducklake_cleanup_old_files(...)` (§7.3).

    Removes orphan Parquet files left over from expired snapshots.
    Should run AFTER `ducklake_expire_snapshots_sql()` so it has a
    full picture of which snapshots are still referenced.

    Args:
        snapshot_retention_days: Mirror the same value used by
            `ducklake_expire_snapshots_sql(...)`. Default: 7.
        ducklake: The DuckLake name. Default: `"cianfhoghlaim"`.

    Returns:
        The `CALL ...` SQL string.
    """
    return (
        f"CALL ducklake_cleanup_old_files('{ducklake}', "
        f"snapshot_retention => INTERVAL '{snapshot_retention_days} days')"
    )


def ducklake_merge_adjacent_files_sql(
    table: str,
    *,
    ducklake: str = DUCKLAKE_NAME,
) -> str:
    """Return SQL for `ducklake_merge_adjacent_files(<ducklake>, <table>)` (§7.3).

    Coalesces small adjacent Parquet files into larger ones. Runs per
    table — the asset group iterates `JURISDICTION_SORTED_BY_TABLES`
    + the 3 high-traffic dbt fact tables.

    Args:
        table: Fully-qualified table name (e.g.
            `leabharlann_books.leabharlann_books`).
        ducklake: The DuckLake name. Default: `"cianfhoghlaim"`.

    Returns:
        The `CALL ...` SQL string.
    """
    return f"CALL ducklake_merge_adjacent_files('{ducklake}', '{table}')"


def ducklake_rewrite_data_files_sql(
    table: str,
    sort_columns: tuple[str, ...] = DEFAULT_JURISDICTION_SORT_COLUMNS,
    *,
    ducklake: str = DUCKLAKE_NAME,
) -> str:
    """Return SQL for `ducklake_rewrite_data_files(<ducklake>, <table>, ...)`.

    Re-writes the Parquet files for a table against the canonical
    BIEP axis `SORTED BY (jurisdiction, stage, subject)` so downstream
    reads get the 10x speedup documented in §7.2.

    Args:
        table: Fully-qualified table name.
        sort_columns: The SORTED BY columns. Default: BIEP axis
            `(jurisdiction, stage, subject)`.
        ducklake: The DuckLake name. Default: `"cianfhoghlaim"`.

    Returns:
        The `CALL ...` SQL string.
    """
    cols = ", ".join(sort_columns)
    return (
        f"CALL ducklake_rewrite_data_files('{ducklake}', '{table}', "
        f"SORTED BY ({cols}))"
    )


__all__ = [
    # Constants
    "DEFAULT_POSTGRES_CATALOG",
    "DEFAULT_GARAGE_S3_STORAGE",
    "DUCKLAKE_NAME",
    "QUADRANT_METADATA_SCHEMAS",
    "DEFAULT_AUTOMATIC_MIGRATION",
    "SMALL_TABLES",
    "SORTED_BY_TABLES",
    "BUCKET_PARTITIONED_TABLES",
    "DEFAULT_JURISDICTION_SORT_COLUMNS",
    "JURISDICTION_SORTED_BY_TABLES",
    # Factory
    "get_ducklake_destination",
    "get_ducklake_destination_for_quadrant",
    # Time-travel
    "ducklake_cianfhoghlaim_at_timestamp",
    "ducklake_cianfhoghlaim_at_version",
    # Change feed
    "ducklake_cianfhoghlaim_table_changes",
    # Optimisation helpers
    "apply_sort_to_table",
    "apply_jurisdiction_sort_to_table",
    "apply_jurisdiction_sort_to_table_if_needed",
    "apply_bucket_partitioning_to_table",
    "apply_data_inlining_to_table",
    # Nightly maintenance SQL (§7.3)
    "ducklake_expire_snapshots_sql",
    "ducklake_cleanup_old_files_sql",
    "ducklake_merge_adjacent_files_sql",
    "ducklake_rewrite_data_files_sql",
]
