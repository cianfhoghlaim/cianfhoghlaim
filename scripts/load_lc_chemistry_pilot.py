"""Phase 2c loader for the LC chemistry pilot → canonical lakehouse.

Part of the ``2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-
remediation-v1`` openspec change (Phase 2c). Loads the Leaving Certificate
chemistry pilot output into the canonical lakehouse ``md:cianfhoghlaim``
per the BIEP v3 ibis-first contract:

- ``ibis.duckdb.connect("md:cianfhoghlaim")`` is the ONLY data-write
  path (never raw ``duckdb.connect`` for data writes). The single
  documented exception is the one control-plane ``CREATE DATABASE``
  statement in step 0 — ibis exposes no create-database API.
- Tables land under the ``leaving_cert`` schema per the spec scenario
  ("rows SHALL land in cianfhoghlaim.leaving_cert.chemistry"):

    - ``cianfhoghlaim.leaving_cert.chemistry_pilot_documents``    (16 rows)
    - ``cianfhoghlaim.leaving_cert.chemistry_pilot_cross_check``  (3 rows)

Environment note: the local DuckLake stack (Garage S3 :3900 + Postgres
:5433, i.e. ``get_dlt_destination(use_ducklake=True)``) is DOWN in this
environment, so the load goes via the MotherDuck-hosted lakehouse alias
directly instead of the local DuckLake catalog.

Pipeline:

- Step 0 (plumbing): ensure the ``cianfhoghlaim`` database exists on the
  MotherDuck account. Try ``ibis.duckdb.connect(uri)``; on the
  "no database/share named" failure, run ``duckdb.connect("md:")`` +
  ``CREATE DATABASE cianfhoghlaim`` (this ONE control-plane statement is
  the only raw duckdb use in this script — ibis exposes no
  create-database API), then reconnect via ibis.
- Step 1: collect the 16 ingestion rows from Phase 2a
  (``lc5_documents(subjects=("chemistry",))`` — 8 en + 8 ga chemistry
  files).
- Step 2: run the Phase 2b cross-check for 3 runs (MiniMax primary +
  Qwen secondary): ``ExtractLC6Syllabus`` on the EN + GA syllabus PDFs
  and ``ExtractChemSyllabus`` on the EN PDF. Skip with
  ``--skip-extraction`` for LLM-free re-runs (loads only the documents
  table).
- Step 3: load both tables via ``conn.create_table(..., overwrite=True)``
  from ``ibis.memtable`` (idempotent re-runs).
- Step 4: verify with the canonical helpers from
  ``notebooks/_shared/schema.py`` (``schema_introspect`` +
  ``schema_introspect_table``) and print row counts.

Secret hygiene: this script NEVER sets, reads, or prints ``*_API_KEY``
values. Before importing ``lc6_cross_check`` (the BAML runtime snapshots
``os.environ`` at import), it sets only non-secret, publicly documented
endpoint defaults — and only if absent: ``MINIMAX_BASE_URL``,
``DASHSCOPE_BASE_URL``, ``LANGFUSE_HOST``, ``USE_LOCAL_SCRAPES``.
``DASHSCOPE_API_KEY`` is never fabricated: the Qwen secondary is
expected to fail with a missing-key error until the real key lands in
the Infisical vault.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# ---------------------------------------------------------------------------
# Non-secret endpoint defaults — MUST be set before importing
# lc6_cross_check / baml_client (the BAML runtime snapshots os.environ at
# import time). Only set if absent; NEVER any *_API_KEY.
# ---------------------------------------------------------------------------
_ENDPOINT_DEFAULTS: dict[str, str] = {
    "MINIMAX_BASE_URL": "https://api.minimax.io/v1",
    "DASHSCOPE_BASE_URL": "https://coding.dashscope.aliyuncs.com/v1",
    "LANGFUSE_HOST": "http://localhost:3000",
    "USE_LOCAL_SCRAPES": "true",
}
for _name, _value in _ENDPOINT_DEFAULTS.items():
    if not os.environ.get(_name):
        os.environ[_name] = _value

import ibis  # noqa: E402
import structlog  # noqa: E402

from dlt_sources.filesystem.leaving_cert_source import lc5_documents  # noqa: E402
from notebooks._shared.db import lakehouse_uri  # noqa: E402
from notebooks._shared.schema import (  # noqa: E402
    schema_introspect,
    schema_introspect_table,
)

logger = structlog.get_logger(__name__)

LAKEHOUSE_DB_NAME = "cianfhoghlaim"
SCHEMA_NAME = "leaving_cert"
DOCUMENTS_TABLE = f"{SCHEMA_NAME}.chemistry_pilot_documents"
CROSS_CHECK_TABLE = f"{SCHEMA_NAME}.chemistry_pilot_cross_check"

CHEM_EN_PDF = (
    REPO_ROOT / "leaving_certificate/chemistry/en/SCSEC09_Chemistry_syllabus_Eng.pdf"
)
CHEM_GA_PDF = (
    REPO_ROOT
    / "leaving_certificate/chemistry/ga/SCSEC09_Chemistry_syllabus_Gaeilge.pdf"
)

# Same 3 runs as the Phase 2b dev runner (lc6_cross_check.main()).
CROSS_CHECK_RUNS: tuple[tuple[Path, str, str], ...] = (
    (CHEM_EN_PDF, "en", "ExtractLC6Syllabus"),
    (CHEM_GA_PDF, "ga", "ExtractLC6Syllabus"),
    (CHEM_EN_PDF, "en", "ExtractChemSyllabus"),
)

DOCUMENTS_SCHEMA = ibis.schema(
    {
        "id": "string",
        "file_hash": "string",
        "file_name": "string",
        "file_path": "string",
        "file_size_bytes": "int64",
        "is_image": "boolean",
        "language": "string",
        "subject": "string",
        "model_key": "string",
        "resolved_backend": "string",
        "backend_reason": "string",
        "is_exam_paper": "boolean",
        "is_syllabus": "boolean",
        "is_marking_scheme": "boolean",
    }
)

CROSS_CHECK_SCHEMA = ibis.schema(
    {
        "source_pdf": "string",
        "language": "string",
        "baml_function": "string",
        "status": "string",
        "primary_topic_count": "int64",
        "primary_learning_outcome_count": "int64",
        "primary_level": "string",
        "primary_source_pages": "int64",
        "secondary_topic_count": "int64",
        "secondary_learning_outcome_count": "int64",
        "disagreements_json": "string",
        "secondary_error": "string",
        "primary_error": "string",
        "loaded_at": "string",
    }
)


# ---------------------------------------------------------------------------
# Step 0 — plumbing: ensure the cianfhoghlaim database exists
# ---------------------------------------------------------------------------


def ensure_lakehouse_database(uri: str) -> tuple[Any, bool]:
    """Connect to the lakehouse via ibis, creating the DB if absent.

    Returns ``(conn, db_created)``. The create path uses ONE raw
    ``duckdb.connect("md:")`` control-plane statement (``CREATE
    DATABASE``) because ibis exposes no create-database API; every data
    write afterwards goes through the ibis handle.
    """
    try:
        conn = ibis.duckdb.connect(uri, read_only=False)
        logger.info("lakehouse_db_already_existed", uri=uri)
        return conn, False
    except Exception as exc:  # noqa: BLE001 — duckdb error classes vary by version
        if "no database/share named" not in str(exc).lower():
            logger.error("lakehouse_connect_failed", uri=uri, error=str(exc)[:300])
            raise
        logger.info(
            "lakehouse_db_missing",
            uri=uri,
            error=str(exc)[:200],
        )

    import duckdb

    db_name = uri.split("md:", 1)[1] if uri.startswith("md:") else uri
    logger.info("lakehouse_db_creating", db_name=db_name)
    control = duckdb.connect("md:")
    try:
        # The single documented raw-duckdb control-plane statement.
        control.execute(f"CREATE DATABASE {db_name}")
    finally:
        control.close()

    conn = ibis.duckdb.connect(uri, read_only=False)
    logger.info("lakehouse_db_created", uri=uri)
    return conn, True


# ---------------------------------------------------------------------------
# Step 1 — collect the 16 ingestion rows (Phase 2a source)
# ---------------------------------------------------------------------------


def collect_documents_rows() -> list[dict[str, Any]]:
    """Collect the chemistry ingestion rows from ``lc5_documents``.

    ``DEFAULT_LC_ROOT`` is ``__file__``-relative (repo_root /
    ``leaving_certificate``) so it resolves from any CWD; pass it
    explicitly anyway for auditability. All row fields are scalars, so
    every field is kept as-is.
    """
    from dlt_sources.filesystem.leaving_cert_source import DEFAULT_LC_ROOT

    root = DEFAULT_LC_ROOT
    if not root.exists():
        raise FileNotFoundError(f"LC root does not exist: {root}")
    rows = list(lc5_documents(root_path=str(root), subjects=("chemistry",)))
    logger.info("documents_rows_collected", count=len(rows), root=str(root))
    if len(rows) != 16:
        logger.warning("documents_row_count_unexpected", count=len(rows), expected=16)
    return rows


# ---------------------------------------------------------------------------
# Step 2 — the 3 cross-check runs (Phase 2b helper)
# ---------------------------------------------------------------------------


def _extract_pdf_text(pdf_path: Path) -> tuple[str, int]:
    """Extract the text layer of a PDF via pypdf. Returns (text, pages).

    Same pattern as ``lc6_cross_check.main()``.
    """
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages), len(reader.pages)


def _scalar(value: Any) -> Any:
    """Coerce a BAML field to a plain scalar (str/int/float/bool/None)."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def run_cross_checks() -> list[dict[str, Any]]:
    """Run the 3 Phase 2b cross-check extractions and shape load rows."""
    from dlt_sources.filesystem.lc6_cross_check import (
        MAX_TEXT_CHARS,
        extract_with_cross_check,
    )

    texts: dict[Path, str] = {}
    for pdf_path, _, _ in CROSS_CHECK_RUNS:
        if pdf_path in texts:
            continue
        if not pdf_path.exists():
            raise FileNotFoundError(f"syllabus PDF missing: {pdf_path}")
        text, page_count = _extract_pdf_text(pdf_path)
        texts[pdf_path] = text
        logger.info(
            "pdf_text_extracted",
            pdf=pdf_path.name,
            pages=page_count,
            chars=len(text),
            has_text=bool(text.strip()),
        )

    loaded_at = datetime.now(timezone.utc).isoformat()
    rows: list[dict[str, Any]] = []
    for pdf_path, language, baml_function in CROSS_CHECK_RUNS:
        text = texts[pdf_path]
        if not text.strip():
            raise ValueError(
                f"no extractable text layer in {pdf_path.name}; not fabricating text"
            )
        if len(text) > MAX_TEXT_CHARS:
            logger.info(
                "text_truncated", pdf=pdf_path.name, kept_chars=MAX_TEXT_CHARS
            )
            text = text[:MAX_TEXT_CHARS]

        result = extract_with_cross_check(
            text=text,
            subject="chemistry",
            language=language,
            source_pdf=pdf_path.name,
            baml_function=baml_function,
        )
        primary = result.primary
        secondary = result.secondary
        row = {
            "source_pdf": result.source_pdf,
            "language": result.language,
            "baml_function": result.baml_function,
            "status": result.status,
            "primary_topic_count": (
                _scalar(primary.topic_count) if primary is not None else None
            ),
            "primary_learning_outcome_count": (
                _scalar(primary.learning_outcome_count)
                if primary is not None
                else None
            ),
            "primary_level": (
                _scalar(primary.level) if primary is not None else None
            ),
            "primary_source_pages": (
                _scalar(primary.source_pages) if primary is not None else None
            ),
            "secondary_topic_count": (
                _scalar(secondary.topic_count) if secondary is not None else None
            ),
            "secondary_learning_outcome_count": (
                _scalar(secondary.learning_outcome_count)
                if secondary is not None
                else None
            ),
            "disagreements_json": json.dumps(result.disagreements),
            "secondary_error": result.secondary_error,
            "primary_error": result.primary_error,
            "loaded_at": loaded_at,
        }
        rows.append(row)
        logger.info(
            "cross_check_run",
            source_pdf=result.source_pdf,
            language=language,
            baml_function=baml_function,
            status=result.status,
            primary_topic_count=row["primary_topic_count"],
            primary_learning_outcome_count=row["primary_learning_outcome_count"],
            primary_level=row["primary_level"],
            primary_source_pages=row["primary_source_pages"],
        )
    return rows


# ---------------------------------------------------------------------------
# Step 3 — ibis-first load
# ---------------------------------------------------------------------------


def load_tables(
    conn: Any,
    documents_rows: list[dict[str, Any]],
    cross_check_rows: list[dict[str, Any]],
) -> dict[str, int]:
    """Load both pilot tables via ibis (idempotent overwrite).

    ibis 12's duckdb backend treats ``create_table(name)`` as a single
    (possibly quoted) identifier — a dotted ``name`` would land in the
    ``main`` schema as a literal dotted table name. The schema must be
    passed via the ``database`` parameter as a ``(catalog, schema)``
    tuple instead.
    """
    conn.raw_sql(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}")
    table_loc = (LAKEHOUSE_DB_NAME, SCHEMA_NAME)

    conn.create_table(
        "chemistry_pilot_documents",
        obj=ibis.memtable(documents_rows, schema=DOCUMENTS_SCHEMA),
        database=table_loc,
        overwrite=True,
    )
    logger.info("documents_table_loaded", table=DOCUMENTS_TABLE, rows=len(documents_rows))

    loaded_cross_check = 0
    if cross_check_rows:
        conn.create_table(
            "chemistry_pilot_cross_check",
            obj=ibis.memtable(cross_check_rows, schema=CROSS_CHECK_SCHEMA),
            database=table_loc,
            overwrite=True,
        )
        loaded_cross_check = len(cross_check_rows)
        logger.info(
            "cross_check_table_loaded",
            table=CROSS_CHECK_TABLE,
            rows=loaded_cross_check,
        )
    else:
        logger.info("cross_check_table_skipped", reason="--skip-extraction")

    return {"documents": len(documents_rows), "cross_check": loaded_cross_check}


# ---------------------------------------------------------------------------
# Step 4 — verification via the canonical introspection helpers
# ---------------------------------------------------------------------------


def verify(conn: Any, expect_cross_check: bool) -> dict[str, Any]:
    """Verify both tables via notebooks/_shared/schema.py helpers."""
    all_rows = schema_introspect(conn)
    pilot_rows = [
        r for r in all_rows if str(r.get("table_name", "")).startswith("chemistry_pilot")
    ]
    found_tables = sorted({str(r["table_name"]) for r in pilot_rows})
    expected = ["chemistry_pilot_cross_check", "chemistry_pilot_documents"]
    if not expect_cross_check:
        expected = ["chemistry_pilot_documents"]
    missing = [t for t in expected if t not in found_tables]
    if missing:
        raise AssertionError(
            f"schema_introspect missing pilot tables: {missing} "
            f"(found: {found_tables})"
        )

    evidence: dict[str, Any] = {}
    for qualified in (DOCUMENTS_TABLE, CROSS_CHECK_TABLE):
        if not expect_cross_check and qualified == CROSS_CHECK_TABLE:
            continue
        columns = schema_introspect_table(conn, qualified)
        column_names = [str(c["column_name"]) for c in columns]
        evidence[qualified] = column_names
        logger.info(
            "schema_introspect_table_ok",
            table=qualified,
            column_count=len(column_names),
            columns=column_names,
        )

    counts: dict[str, int] = {}
    for qualified in (DOCUMENTS_TABLE, CROSS_CHECK_TABLE):
        if not expect_cross_check and qualified == CROSS_CHECK_TABLE:
            continue
        result = conn.sql(f"SELECT count(*) AS n FROM {qualified}").execute()
        counts[qualified] = int(result["n"].iloc[0])
        logger.info("row_count", table=qualified, count=counts[qualified])

    return {"tables_found": found_tables, "columns": evidence, "counts": counts}


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Load the LC chemistry pilot into md:cianfhoghlaim"
    )
    parser.add_argument(
        "--skip-extraction",
        action="store_true",
        help="Skip the LLM cross-check runs (step 2); load only the "
        "documents table. For LLM-free re-runs.",
    )
    args = parser.parse_args(argv)

    uri = lakehouse_uri()
    logger.info(
        "pilot_load_start",
        uri=uri,
        skip_extraction=args.skip_extraction,
        MINIMAX_API_KEY_present=bool(os.environ.get("MINIMAX_API_KEY")),
        DASHSCOPE_API_KEY_present=bool(os.environ.get("DASHSCOPE_API_KEY")),
    )

    conn, db_created = ensure_lakehouse_database(uri)

    documents_rows = collect_documents_rows()

    cross_check_rows: list[dict[str, Any]] = []
    if not args.skip_extraction:
        cross_check_rows = run_cross_checks()

    loaded = load_tables(conn, documents_rows, cross_check_rows)
    verification = verify(conn, expect_cross_check=bool(cross_check_rows))

    print("=== LC chemistry pilot load summary ===")
    print(f"db_created: {db_created}")
    print(f"documents rows loaded: {loaded['documents']}")
    print(f"cross_check rows loaded: {loaded['cross_check']}")
    for row in cross_check_rows:
        print(
            f"  run: {row['source_pdf']} [{row['baml_function']}/{row['language']}] "
            f"status={row['status']} "
            f"primary topic_count={row['primary_topic_count']} "
            f"lo_count={row['primary_learning_outcome_count']} "
            f"level={row['primary_level']} "
            f"source_pages={row['primary_source_pages']}"
        )
    print("introspection evidence:")
    for qualified, columns in verification["columns"].items():
        print(f"  {qualified}: {len(columns)} columns -> {columns}")
    for qualified, count in verification["counts"].items():
        print(f"  {qualified}: {count} rows")
    logger.info("pilot_load_complete", db_created=db_created, **loaded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
