"""ducklake_helpers_k12 — shared DuckLake analysis queries for the K-12 walkthroughs.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.

Mirrors notebooks/_shared/tertiary/ducklake_helpers.py — same 5
DuckLake 1.0-feature demos (data inlining + data clustering + bucket
partitioning + VARIANT type + time-travel) against the live DuckLake
database at `md:cianfhoghlaim`.

The 5 queries:
1. query_k12_data_inlining_example() — INSERT into cianfhoghlaim.education.ireland.primary
2. query_k12_data_clustering_example() — SORTED BY (area_code) for primary areas
3. query_k12_bucket_partitioning_example() — PARTITIONED BY (bucket(1000, student_id))
4. query_k12_variant_example() — VARIANT type for per-student SEN profiles
5. query_k12_time_travel_example() — read class_roster at VERSION 5

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

from typing import Any

import duckdb

DUCKLAKE_URI = "md:cianfhoghlaim"


def connect() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(DUCKLAKE_URI, read_only=False)


def query_k12_time_travel_example(class_id: str = "5th-class-a") -> list[dict]:
    """DuckLake 1.0 time-travel — read class roster at version 5."""
    con = connect()
    try:
        rows = con.execute(
            f"""
            SELECT student_id, first_name_en, last_name_en, attendance_pct_ytd
            FROM cianfhoghlaim.education.british_isles.ireland.class_roster
            AT (VERSION => 5)
            WHERE class_id = '{class_id}'
            """
        ).fetchall()
        return [{"student_id": r[0], "first_name_en": r[1], "last_name_en": r[2], "attendance_pct_ytd": r[3]} for r in rows]
    finally:
        con.close()


def query_k12_variant_example(student_id: str = "s00003") -> dict:
    """DuckLake 1.0 VARIANT — extract per-student SEN profile JSON."""
    con = connect()
    try:
        row = con.execute(
            f"""
            SELECT json_extract(subject_enrolments, '$[0]') AS first_subject
            FROM cianfhoghlaim.education.british_isles.ireland.class_roster
            WHERE student_id = '{student_id}'
            """
        ).fetchone()
        return {"first_subject": row[0] if row else None}
    finally:
        con.close()


def query_k12_data_inlining_example() -> int:
    """DuckLake 1.0 data inlining — small INSERT goes to catalog DB."""
    con = connect()
    try:
        con.execute(
            """
            INSERT INTO cianfhoghlaim.education.british_isles.ireland.aistear_learning_goals
            VALUES ('aistear-wb-3-6-3', 'Well-being', '3_to_6',
                    'Children develop a positive sense of self through safe routines and trusting relationships.',
                    NULL, NULL, NULL, NULL, 'LO-PRI-EN-1.2')
            """
        )
        return con.execute(
            "SELECT COUNT(*) FROM cianfhoghlaim.education.british_isles.ireland.aistear_learning_goals"
        ).fetchone()[0]
    finally:
        con.close()


def query_k12_data_clustering_example() -> list[dict]:
    """DuckLake 1.0 data clustering — SORTED BY (area_code) for primary areas."""
    con = connect()
    try:
        rows = con.execute(
            """
            SELECT area_code, name_en, document_year
            FROM cianfhoghlaim.education.british_isles.ireland.primary_curriculum_areas
            WHERE document_year >= 2020
            SORTED BY area_code
            LIMIT 12
            """
        ).fetchall()
        return [{"area_code": r[0], "name_en": r[1], "document_year": r[2]} for r in rows]
    finally:
        con.close()


def query_k12_bucket_partitioning_example() -> list[dict]:
    """DuckLake 1.0 bucket partitioning — PARTITIONED BY (bucket(1000, student_id))."""
    con = connect()
    try:
        rows = con.execute(
            """
            SELECT student_id, class_id, attendance_pct_ytd
            FROM cianfhoghlaim.education.british_isles.ireland.class_roster
            WHERE bucket(1000, student_id) = 0
            LIMIT 5
            """
        ).fetchall()
        return [{"student_id": r[0], "class_id": r[1], "attendance_pct_ytd": r[2]} for r in rows]
    finally:
        con.close()


def walkthrough_k12_demo() -> dict[str, Any]:
    """Demo the 5 DuckLake 1.0 features against the live K-12 data."""
    return {
        "data_inlining_count": query_k12_data_inlining_example(),
        "time_travel_class": query_k12_time_travel_example(),
        "variant_first_subject": query_k12_variant_example(),
        "clustered_primary_areas": query_k12_data_clustering_example(),
        "bucket_0_students": query_k12_bucket_partitioning_example(),
    }


__all__ = [
    "DUCKLAKE_URI",
    "connect",
    "query_k12_time_travel_example",
    "query_k12_variant_example",
    "query_k12_data_inlining_example",
    "query_k12_data_clustering_example",
    "query_k12_bucket_partitioning_example",
    "walkthrough_k12_demo",
]
