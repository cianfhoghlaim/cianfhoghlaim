"""ducklake_helpers — shared DuckLake analysis queries for the tertiary walkthroughs.

Per openspec/changes/2026-09-23-uog-tertiary-real-data-upgrade-v1/.

Provides 5 DuckLake 1.0-feature demo queries (per the 5 production
features in `dlt_sources/common/ducklake_options.py`):

1. **Data inlining** — auto-inlined small inserts
2. **Data clustering** — SORTED BY (module_code) for 10x faster reads
3. **Bucket partitioning** — PARTITIONED BY (bucket(1000, module_code))
4. **Geometry type** — DuckDB core GEOMETRY + DuckLake pushdown
5. **Variant type** — VARIANT (binary JSON) + automatic shredding

Each walkthrough notebook imports from this module + runs the queries
against the live DuckLake database at `md:cianfhoghlaim`.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

from typing import Any

import duckdb

DUCKLAKE_URI = "md:cianfhoghlaim"


def connect() -> duckdb.DuckDBPyConnection:
    """Connect to the canonical DuckLake database."""
    return duckdb.connect(DUCKLAKE_URI, read_only=False)


def query_time_travel_example(module_id: str = "cs203_data_structures") -> list[dict]:
    """DuckLake 1.0 time-travel query — read the module row at version 5."""
    con = connect()
    try:
        rows = con.execute(
            f"""
            SELECT module_code, title_english, ects_credits, scraped_at
            FROM cianfhoghlaim.tertiary.uog.modules AT (VERSION => 5)
            WHERE module_id = '{module_id}'
            """
        ).fetchall()
        return [{"module_code": r[0], "title_english": r[1], "ects_credits": r[2], "scraped_at": r[3]} for r in rows]
    finally:
        con.close()


def query_variant_example(module_id: str = "cs203_data_structures") -> dict:
    """DuckLake 1.0 VARIANT type — extract a JSON field from the row."""
    con = connect()
    try:
        row = con.execute(
            f"""
            SELECT json_extract(learning_outcomes, '$[0]') AS first_lo
            FROM cianfhoghlaim.tertiary.uog.modules
            WHERE module_id = '{module_id}'
            """
        ).fetchone()
        return {"first_learning_outcome": row[0] if row else None}
    finally:
        con.close()


def query_data_inlining_example() -> int:
    """DuckLake 1.0 data inlining — small INSERT goes to catalog DB instead of Parquet."""
    con = connect()
    try:
        con.execute(
            """
            INSERT INTO cianfhoghlaim.tertiary.uog.module_handbooks
            VALUES ('CS203', 'https://example.com/handbook.pdf', 12, '2026-09-23', 0.92)
            """
        )
        return con.execute(
            "SELECT COUNT(*) FROM cianfhoghlaim.tertiary.uog.module_handbooks"
        ).fetchone()[0]
    finally:
        con.close()


def query_data_clustering_example() -> list[dict]:
    """DuckLake 1.0 data clustering — SORTED BY (module_code) for fast reads."""
    con = connect()
    try:
        rows = con.execute(
            """
            SELECT module_code, school_id, ects_credits
            FROM cianfhoghlaim.tertiary.uog.modules
            WHERE school_id = 'school-computer-science'
            SORTED BY module_code
            LIMIT 10
            """
        ).fetchall()
        return [{"module_code": r[0], "school_id": r[1], "ects_credits": r[2]} for r in rows]
    finally:
        con.close()


def query_bucket_partitioning_example() -> list[dict]:
    """DuckLake 1.0 bucket partitioning — PARTITIONED BY (bucket(1000, module_code))."""
    con = connect()
    try:
        rows = con.execute(
            """
            SELECT module_code, school_id
            FROM cianfhoghlaim.tertiary.uog.modules
            WHERE bucket(1000, module_code) = 0
            LIMIT 5
            """
        ).fetchall()
        return [{"module_code": r[0], "school_id": r[1]} for r in rows]
    finally:
        con.close()


def walkthrough_1_data_inlining() -> dict[str, Any]:
    """Demo the 5 DuckLake 1.0 features against the live tertiary DB."""
    return {
        "data_inlining_count": query_data_inlining_example(),
        "time_travel_module": query_time_travel_example(),
        "variant_first_lo": query_variant_example(),
        "clustered_cs_modules": query_data_clustering_example(),
        "bucket_0_modules": query_bucket_partitioning_example(),
    }


__all__ = [
    "DUCKLAKE_URI",
    "connect",
    "query_time_travel_example",
    "query_variant_example",
    "query_data_inlining_example",
    "query_data_clustering_example",
    "query_bucket_partitioning_example",
    "walkthrough_1_data_inlining",
]
