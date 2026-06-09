"""
DuckLake reader for the LC API.

Reads parquet files directly from the Garage S3 bucket (`s3://ducklake/oideachais/`)
that DLT wrote via the DuckLake destination. We intentionally bypass the
DuckLake catalog (Postgres) for read-side and use direct parquet reads so
the API can scale to many subjects without contending on the catalog.

Each DLT source resource (syllabus, past_papers, marking_schemes,
examiner_reports) writes to `s3://ducklake/oideachais/leaving_cert/<table>/*.parquet`.
We glob that path and `read_parquet` into a DuckDB in-memory connection.

The reader is cached per-process (one DuckDB connection reused across
requests) so we don't pay the install/httpfs setup cost on every call.
"""
from __future__ import annotations

import logging
import os
import threading
from functools import lru_cache
from typing import Any

logger = logging.getLogger(__name__)

# ── S3 / DuckLake configuration ────────────────────────────────────────────

_GARAGE_HOST = os.environ.get("GARAGE_HOST", "lakehouse-garage")
_GARAGE_PORT = os.environ.get("GARAGE_PORT", "3900")
_GARAGE_ACCESS_KEY = os.environ.get(
    "AWS_ACCESS_KEY_ID",
    os.environ.get("GARAGE_ACCESS_KEY_ID", "GK1601f278fdaba66e60fa1f51"),
)
_GARAGE_SECRET_KEY = os.environ.get(
    "AWS_SECRET_ACCESS_KEY",
    os.environ.get("GARAGE_SECRET_ACCESS_KEY", ""),
)
_DUCKLAKE_DATA_PATH = os.environ.get(
    "DUCKLAKE_DATA_PATH", "s3://ducklake/oideachais/leaving_cert"
)

_LOCK = threading.Lock()


@lru_cache(maxsize=1)
def _get_conn() -> Any:
    """Return a cached in-memory DuckDB connection with S3 + httpfs preloaded."""
    import duckdb

    conn = duckdb.connect(":memory:")
    try:
        conn.execute("INSTALL httpfs; LOAD httpfs;")
    except Exception as exc:
        logger.warning("duckdb_httpfs_install_failed: %s", exc)

    # Configure S3 endpoint for Garage
    if _GARAGE_ACCESS_KEY:
        conn.execute(f"SET s3_access_key_id='{_GARAGE_ACCESS_KEY}';")
    if _GARAGE_SECRET_KEY:
        conn.execute(f"SET s3_secret_access_key='{_GARAGE_SECRET_KEY}';")
    conn.execute(f"SET s3_endpoint='{_GARAGE_HOST}:{_GARAGE_PORT}';")
    conn.execute("SET s3_url_style='path';")
    conn.execute("SET s3_use_ssl=false;")
    conn.execute("SET s3_region='garage';")

    # Smoke-test the connection: glob the leaving_cert root.
    try:
        conn.execute(
            f"SELECT count(*) FROM glob('{_DUCKLAKE_DATA_PATH}/syllabus/*.parquet')"
        ).fetchone()
        logger.info(
            "ducklake_reader_initialized endpoint=%s path=%s",
            f"{_GARAGE_HOST}:{_GARAGE_PORT}",
            _DUCKLAKE_DATA_PATH,
        )
    except Exception as exc:
        logger.error(
            "ducklake_reader_smoke_test_failed endpoint=%s err=%s",
            f"{_GARAGE_HOST}:{_GARAGE_PORT}",
            exc,
        )
        raise

    return conn


def _read_table(table_suffix: str) -> list[dict[str, Any]]:
    """Read all parquet files for a given table suffix and return rows."""
    path = f"{_DUCKLAKE_DATA_PATH}/{table_suffix}/*.parquet"
    try:
        with _LOCK:
            conn = _get_conn()
            result = conn.execute(
                f"SELECT * FROM read_parquet('{path}') ORDER BY year DESC, level"
            ).fetchdf()
        return result.to_dict(orient="records")
    except Exception as exc:
        # The path may not exist (e.g. marking_schemes parquet glob is empty)
        # or the parquet read may fail. Either way, return [] so the caller
        # can fall back to seed data, and clear the cache so the next call
        # gets a fresh connection.
        logger.warning(
            "ducklake_read_failed table=%s path=%s err=%s",
            table_suffix,
            path,
            exc,
        )
        _get_conn.cache_clear()
        return []


def read_syllabus(subject: str) -> list[dict[str, Any]]:
    """Read syllabus rows for a subject from DuckLake."""
    rows = _read_table("syllabus")
    return [r for r in rows if r.get("subject") == subject]


def read_past_papers(subject: str) -> list[dict[str, Any]]:
    """Read past_papers rows for a subject from DuckLake."""
    rows = _read_table("past_papers")
    return [r for r in rows if r.get("subject") == subject]


def read_marking_schemes(subject: str) -> list[dict[str, Any]]:
    """Read marking_schemes rows for a subject from DuckLake."""
    rows = _read_table("marking_schemes")
    return [r for r in rows if r.get("subject") == subject]


def read_examiner_reports(subject: str) -> list[dict[str, Any]]:
    """Read examiner_reports rows for a subject from DuckLake."""
    rows = _read_table("examiner_reports")
    return [r for r in rows if r.get("subject") == subject]


def source_active() -> bool:
    """True if at least one parquet file is readable in the DuckLake bucket."""
    try:
        rows = _read_table("syllabus")
        return len(rows) > 0
    except Exception:
        return False


def compute_topic_frequency(subject: str) -> list[dict[str, Any]]:
    """Cross-reference syllabus + examiner reports to surface the most-cited topics.

    Heuristic: count occurrences of common Leaving Cert topic keywords
    inside examiner report titles. Returns a list of {topic, count, examples}
    sorted by count descending. When the bucket has no data, returns [].
    """
    reports = read_examiner_reports(subject)
    if not reports:
        return []

    # Topic keywords for the 7 priority subjects. This is intentionally
    # lightweight — a future revision will use BAML/GLiNER to extract
    # topic mentions from the PDF markdown bodies.
    KEYWORDS: dict[str, list[str]] = {
        "mathematics": [
            "algebra", "calculus", "trigonometry", "geometry", "statistics",
            "probability", "functions", "sequences", "series", "logs",
            "matrices", "complex", "integration", "differentiation",
        ],
        "irish": [
            "gaeilge", "gramadach", "litríocht", "cluastuiscint",
            "léamhthuiscint", "ceapadóireacht", "filíocht", "prós",
        ],
        "biology": [
            "cell", "ecology", "genetics", "photosynthesis", "respiration",
            "enzymes", "dna", "evolution", "microbiology", "plant",
            "animal", "human", "reproduction",
        ],
        "french": [
            "compréhension", "écriture", "grammaire", "vocabulaire",
            "civilisation", "littérature", "aural", "oral",
        ],
        "history": [
            "ireland", "europe", "world war", "revolution", "modern",
            "early modern", "medieval", "famine", "independence", "union",
        ],
        "business": [
            "management", "marketing", "finance", "enterprise", "people",
            "environment", "global", "accounting", "strategy",
        ],
        "construction-studies": [
            "timber", "concrete", "steel", "thermal", "insulation",
            "foundations", "walls", "roof", "dpc", "cavity",
        ],
    }

    subjects = KEYWORDS.get(subject, [])
    if not subjects:
        return []

    counts: dict[str, list[str]] = {kw: [] for kw in subjects}
    for report in reports:
        title = (report.get("title") or "").lower()
        for kw in subjects:
            if kw in title:
                counts[kw].append(report.get("title", ""))

    out: list[dict[str, Any]] = []
    for kw, examples in counts.items():
        if examples:
            out.append(
                {
                    "topic": kw,
                    "count": len(examples),
                    "examples": examples[:3],
                }
            )
    out.sort(key=lambda x: x["count"], reverse=True)
    return out
