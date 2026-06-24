"""
DuckLake 1.0 SQL helpers.

The 2026-04-13 launch of DuckLake 1.0 introduced 5 production
features that the oideachais quadrant uses:

1. **Data inlining** — `data_inlining_row_limit=100` is the 1.0
   default; small inserts go to the catalog database instead of
   creating separate Parquet files (solves the small-files
   problem).

2. **Data clustering** — `SORTED BY (id)` enables sort-based
   clustering. When sort columns align with query filter columns,
   this gives 10x faster reads.

3. **Bucket partitioning** — `PARTITIONED BY (bucket(1000, id))`
   creates a fixed number of buckets; useful for high-cardinality
   keys.

4. **Geometry type** — DuckDB core now has `GEOMETRY`; DuckLake
   can pushdown geospatial predicates using file-level stats.

5. **Variant type** — `VARIANT` is a binary JSON type with
   automatic shredding for fast filtering.

Per `motherduck.com/blog/announcing-ducklake-1-0-on-motherduck`:

> "Data inlining can be used not only for inserts, but also for
> updates and deletes. [...] Inlining is enabled by default on
> all new tables in DuckLake 1.0 and can be adjusted like this:
> `ALTER TABLE my_lakehouse.my_table SET (data_inlining_row_limit = 100);`"
"""
from __future__ import annotations

from typing import Final


# The 4 highest-volume tables that benefit from SORTED BY (id).
# Mirrors the "dbt-duckdb project" (celtic-data-engineering-patterns change)
# and the 3 leabharlann fact tables.
SORTED_BY_TABLES: Final[frozenset[str]] = frozenset(
    {
        "main.weekly_downloads",
        "main.language_distribution",
        "main.ocr_confidence_by_model",
        "leabharlann_books.leabharlann_books",
        "leabharlann_zotero.leabharlann_zotero",
        "leabharlann_takeout.leabharlann_takeout",
        "leabharlann_books.leabharlann_books_raw",
        "leabharlann_zotero.leabharlann_zotero_raw",
    }
)


# The 3 largest fact tables that benefit from bucket partitioning.
BUCKET_PARTITIONED_TABLES: Final[frozenset[str]] = frozenset(
    {
        "leabharlann_zotero.leabharlann_zotero",
        "leabharlann_takeout.leabharlann_takeout",
        "oideachais_unified.unified_embeddings",
    }
)


# The default data-inlining row limit (the 1.0 default).
DEFAULT_DATA_INLINING_ROW_LIMIT: Final[int] = 100


def set_data_inlining_row_limit(table: str, limit: int = DEFAULT_DATA_INLINING_ROW_LIMIT) -> str:
    """Return the SQL to set the DuckLake 1.0 inlining row limit.

    Args:
        table: Fully-qualified table name (e.g. ``"main.weekly_downloads"``).
        limit: The inlining row limit. 100 is the DuckLake 1.0 default;
               the maximum practical value is ~10000.

    Returns:
        The ``ALTER TABLE`` SQL statement.
    """
    return f"ALTER TABLE {table} SET (data_inlining_row_limit = {limit});"


def set_sorted_by(table: str, columns: tuple[str, ...] = ("id",)) -> str:
    """Return the SQL to enable DuckLake 1.0 data clustering.

    The sort columns should be the columns the most common filter
    queries use. For the oideachais high-volume tables this is
    always ``id`` (the primary key) because the typical filter is
    ``WHERE id = ?`` for the Dagster asset materialisation log.

    Args:
        table: Fully-qualified table name.
        columns: The sort columns. Default ``("id",)``.

    Returns:
        The ``ALTER TABLE`` SQL statement.
    """
    columns_str = ", ".join(columns)
    return f"ALTER TABLE {table} SET SORTED BY ({columns_str});"


def set_bucket_partition(table: str, num_buckets: int = 1000, key: str = "id") -> str:
    """Return the SQL to enable DuckLake 1.0 bucket partitioning.

    Bucket partitioning is a middle ground between fine-grained
    partitioning (which creates too many small files) and
    coarse-grained partitioning (which loses selectivity).

    Args:
        table: Fully-qualified table name.
        num_buckets: The number of buckets. 1000 is the
                     ``motherduck.com`` example.
        key: The bucketing key. Default ``"id"``.

    Returns:
        The ``ALTER TABLE`` SQL statement.
    """
    return f"ALTER TABLE {table} SET PARTITIONED BY (bucket({num_buckets}, {key}));"


def apply_ducklake_1_0_optimisations(
    table: str,
    *,
    enable_sorting: bool = True,
    enable_bucketing: bool = False,
    inlining_row_limit: int = DEFAULT_DATA_INLINING_ROW_LIMIT,
) -> list[str]:
    """Return the SQL to apply the 3 DuckLake 1.0 optimisations to a table.

    This is the canonical helper called by
    ``get_dlt_destination().post_create_hook(table)`` (and the
    ``oideachais_dbt_assets`` post-hook) when a new table is
    materialised.

    Args:
        table: Fully-qualified table name.
        enable_sorting: Whether to apply ``SORTED BY``. Default True.
        enable_bucketing: Whether to apply ``PARTITIONED BY (bucket(1000, id))``.
                          Default False (only the 3 largest fact tables).
        inlining_row_limit: The inlining row limit. Default 100 (the 1.0 default).

    Returns:
        A list of SQL statements to execute in order.
    """
    sql: list[str] = [
        set_data_inlining_row_limit(table, limit=inlining_row_limit),
    ]
    if enable_sorting:
        sql.append(set_sorted_by(table))
    if enable_bucketing:
        sql.append(set_bucket_partition(table))
    return sql


def is_sorted_by_table(table: str) -> bool:
    """Return True if `table` is in the canonical SORTED BY list."""
    return table in SORTED_BY_TABLES


def is_bucket_partitioned_table(table: str) -> bool:
    """Return True if `table` is in the canonical bucket-partitioned list."""
    return table in BUCKET_PARTITIONED_TABLES
