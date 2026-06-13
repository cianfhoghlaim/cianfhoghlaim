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
    "DUCKLAKE_DATA_PATH", "s3://ducklake/oideachais"
)

# Subject slugs for the per-subject DuckLake dataset split. The DLT
# pipeline writes each subject's tables to its own dataset
# (leaving_cert_{subject_slug}) to avoid concurrent transaction conflicts
# when 7 subjects pipeline in parallel. The API reader unions all
# subject datasets when reading.
_LEAVING_CERT_SUBJECTS: tuple[str, ...] = (
    "mathematics",
    "irish",
    "biology",
    "french",
    "history",
    "business",
    "construction_studies",
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

    # Smoke-test the connection: glob the first subject dataset.
    try:
        conn.execute(
            f"SELECT count(*) FROM glob('{_DUCKLAKE_DATA_PATH}/leaving_cert_mathematics/syllabus/*.parquet')"
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
    """Read all parquet files for a given table suffix, unioning across
    per-subject datasets (leaving_cert_{subject_slug}/{table_suffix}/*.parquet).

    Each subject has its own DuckLake dataset to avoid concurrent
    transaction conflicts during parallel DLT runs. The API reader is
    subject-agnostic at the storage layer and applies per-subject filters
    in the read_syllabus / read_past_papers etc. helpers below.
    """
    # Build a glob of per-subject paths. DuckDB's read_parquet accepts a
    # list of globs in modern versions; for older versions we union.
    glob_paths = [
        f"{_DUCKLAKE_DATA_PATH}/leaving_cert_{subject}/{table_suffix}/*.parquet"
        for subject in _LEAVING_CERT_SUBJECTS
    ]
    paths_csv = ", ".join(f"'{p}'" for p in glob_paths)
    # DLT's `replace` write_disposition writes a `<uuid>-delete.parquet`
    # tombstone file alongside the new data. We exclude those by globbing
    # only files containing 'ducklake-' (the data pattern) but not 'delete'.
    glob_paths = []
    for subject in _LEAVING_CERT_SUBJECTS:
        # Use a 2-step glob: list all files, filter in Python
        try:
            with _LOCK:
                conn = _get_conn()
                subject_path = f"{_DUCKLAKE_DATA_PATH}/leaving_cert_{subject}/{table_suffix}"
                # List files via glob
                files = conn.execute(
                    f"SELECT file FROM glob('{subject_path}/*.parquet')"
                ).fetchall()
                for (file_path,) in files:
                    if "-delete.parquet" in file_path:
                        continue
                    glob_paths.append(file_path)
        except Exception:
            continue

    if not glob_paths:
        return []

    paths_csv = ", ".join(f"'{p}'" for p in glob_paths)
    try:
        with _LOCK:
            conn = _get_conn()
            result = conn.execute(
                f"SELECT * FROM read_parquet([{paths_csv}], union_by_name=True) ORDER BY year DESC, level"
            ).fetchdf()
        return result.to_dict(orient="records")
    except Exception as exc:
        logger.warning(
            "ducklake_read_failed table=%s err=%s",
            table_suffix,
            exc,
        )
        _get_conn.cache_clear()
        return []


def read_syllabus(subject: str) -> list[dict[str, Any]]:
    """Read syllabus rows for a subject from DuckLake, deduplicated by content_hash."""
    rows = _read_table("syllabus")
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for r in rows:
        if r.get("subject") != subject:
            continue
        h = r.get("content_hash") or f"{r.get('title','')}|{r.get('year','')}|{r.get('level','')}|{r.get('language','')}"
        if h in seen:
            continue
        seen.add(h)
        out.append(r)
    return out


def read_past_papers(subject: str) -> list[dict[str, Any]]:
    """Read past_papers rows for a subject from DuckLake, deduplicated."""
    rows = _read_table("past_papers")
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for r in rows:
        if r.get("subject") != subject:
            continue
        h = r.get("content_hash") or f"{r.get('title','')}|{r.get('year','')}|{r.get('level','')}"
        if h in seen:
            continue
        seen.add(h)
        out.append(r)
    return out


def read_marking_schemes(subject: str) -> list[dict[str, Any]]:
    """Read marking_schemes rows for a subject from DuckLake, deduplicated."""
    rows = _read_table("marking_schemes")
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for r in rows:
        if r.get("subject") != subject:
            continue
        h = r.get("content_hash") or f"{r.get('title','')}|{r.get('year','')}|{r.get('level','')}"
        if h in seen:
            continue
        seen.add(h)
        out.append(r)
    return out


def read_examiner_reports(subject: str) -> list[dict[str, Any]]:
    """Read examiner_reports rows for a subject from DuckLake, deduplicated."""
    rows = _read_table("examiner_reports")
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for r in rows:
        if r.get("subject") != subject:
            continue
        h = r.get("content_hash") or f"{r.get('title','')}|{r.get('year','')}|{r.get('level','')}|{r.get('language','')}"
        if h in seen:
            continue
        seen.add(h)
        out.append(r)
    return out


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
