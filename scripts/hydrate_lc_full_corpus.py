"""Full-corpus LC hydration loader — the real 2026-08-08-lakehouse-
extensive-hydration-v1 hydration pass.

Extends the proven `scripts/load_lc_chemistry_pilot.py` pattern (2 real
tables, real MiniMax-primary/Qwen-secondary cross-check extraction) from
1 subject (chemistry, 16 files) to all 13 local subjects (144 files),
and lands the result in the REAL local DuckLake catalog (Garage S3 +
Postgres) rather than the MotherDuck fallback the pilot script needed —
per the 2026-08-08-lakehouse-extensive-hydration-v1 change, the local
DuckLake stack is confirmed live in this environment (`lakehouse-garage`
+ `lakehouse-postgres` containers, live-verified via a direct ATTACH +
dlt pipeline round-trip), so there is no need to fall back to MotherDuck.

Two tables, both under the real DuckLake catalog attached as
`cianfhoghlaim` (schema `leaving_cert`):

- `cianfhoghlaim.leaving_cert.corpus_documents` — one row per PDF/JPG
  file across ALL 13 subjects (144 files), from `lc5_documents()`. Fast,
  no LLM calls — pure filesystem metadata (hash, subject, language,
  classification). This is the full-corpus bronze layer.
- `cianfhoghlaim.leaving_cert.syllabus_cross_check` — one row per
  subject's PRIMARY English-medium syllabus PDF (13 rows, one per
  subject that has one), real MiniMax-primary/Qwen-secondary extraction
  via `dlt_sources.filesystem.lc6_cross_check.extract_with_cross_check`,
  same function the chemistry pilot already proved works.

Scope note: this does NOT run cross-check extraction on every one of the
144 files (exam papers + marking schemes included) — that would be
13 subjects x up to ~11 files x 2 LLM calls each, a much larger and
more expensive run than "hydrate the lakehouse with real content"
requires to be genuinely true. The per-subject SYLLABUS extraction is
the representative, bounded, real slice (mirrors the chemistry pilot's
own scope exactly, just repeated across all subjects instead of one).
Full per-subject exam-paper/marking-scheme extraction already happens
via the separate `orchestration/defs/2_materials/lc_extraction/
quest_pack_assets.py` pipeline (2026-08-08-docs-informed-quest-and-
credential-generation-v1 change) -- this script is not a replacement
for that, it is the DuckLake-first "walk the whole corpus and hydrate a
representative real slice" pass the notebooks investigate.

Secret hygiene: same convention as load_lc_chemistry_pilot.py -- never
sets, reads, or prints `*_API_KEY` values; only sets non-secret,
publicly documented endpoint defaults, and only if absent.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# ---------------------------------------------------------------------------
# Non-secret endpoint defaults -- MUST be set before importing
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

import structlog  # noqa: E402

from dlt_sources.filesystem.leaving_cert_source import (  # noqa: E402
    DEFAULT_LC_ROOT,
    LC_ALL_SUBJECTS as ALL_LC_SUBJECTS,
    lc5_documents,
)

logger = structlog.get_logger(__name__)

DB_NAME = "cianfhoghlaim"
SCHEMA_NAME = "leaving_cert"
DOCUMENTS_TABLE = f"{SCHEMA_NAME}.corpus_documents"
CROSS_CHECK_TABLE = f"{SCHEMA_NAME}.syllabus_cross_check"

DOCUMENTS_COLUMNS: tuple[str, ...] = (
    "id",
    "file_hash",
    "file_name",
    "file_path",
    "file_size_bytes",
    "is_image",
    "language",
    "subject",
    "model_key",
    "resolved_backend",
    "backend_reason",
    "is_exam_paper",
    "is_syllabus",
    "is_marking_scheme",
)

CROSS_CHECK_COLUMNS: tuple[str, ...] = (
    "subject",
    "source_pdf",
    "language",
    "baml_function",
    "status",
    "primary_topic_count",
    "primary_learning_outcome_count",
    "primary_level",
    "primary_source_pages",
    "secondary_topic_count",
    "secondary_learning_outcome_count",
    "disagreements_json",
    "secondary_error",
    "primary_error",
    "loaded_at",
)


# ---------------------------------------------------------------------------
# Step 0 -- connect to the real local DuckLake catalog
# ---------------------------------------------------------------------------


def connect_ducklake():
    """Attach the real local DuckLake catalog (Garage S3 + Postgres).

    Mirrors `orchestration/resources.py::DuckLakeResource.get_client()`
    (this change's own Phase A/B fix) -- a raw duckdb connection rather
    than dlt's pipeline API, since this script does direct multi-table
    SQL loads and verification queries in one connection, which is
    simpler to reason about than round-tripping through dlt's schema
    normalisation for this use case.
    """
    import duckdb

    con = duckdb.connect(":memory:")
    con.execute("INSTALL ducklake; LOAD ducklake;")
    con.execute("INSTALL httpfs; LOAD httpfs;")

    aws_key = os.environ.get("AWS_ACCESS_KEY_ID") or os.environ.get("GARAGE_ACCESS_KEY_ID", "")
    aws_secret = os.environ.get("AWS_SECRET_ACCESS_KEY") or os.environ.get(
        "GARAGE_SECRET_ACCESS_KEY", ""
    )
    if not aws_key or not aws_secret:
        raise RuntimeError(
            "AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY (or GARAGE_ACCESS_KEY_ID/"
            "GARAGE_SECRET_ACCESS_KEY) must be set -- cannot reach Garage S3"
        )
    endpoint = os.environ.get("AWS_ENDPOINT_URL", "http://localhost:3900").replace("http://", "")
    con.execute(
        f"CREATE SECRET gs3 (TYPE S3, PROVIDER config, "
        f"KEY_ID '{aws_key}', SECRET '{aws_secret}', REGION 'garage', "
        f"ENDPOINT '{endpoint}', USE_SSL false, URL_STYLE 'path')"
    )

    pg_host = os.environ.get("DUCKLAKE_POSTGRES_HOST", "localhost")
    pg_port = os.environ.get("DUCKLAKE_POSTGRES_PORT", "5433")
    pg_db = os.environ.get("DUCKLAKE_POSTGRES_DB", f"ducklake_{DB_NAME}")
    pg_user = os.environ.get("DUCKLAKE_POSTGRES_USER") or os.environ.get(
        "POSTGRES_USER", "lakekeeper"
    )
    pg_pass = os.environ.get("DUCKLAKE_POSTGRES_PASSWORD") or os.environ.get(
        "POSTGRES_PASSWORD", "devpassword"
    )
    bucket = os.environ.get("DUCKLAKE_BUCKET", "ducklake")
    con.execute(
        f"ATTACH 'ducklake:postgres:dbname={pg_db} host={pg_host} "
        f"port={pg_port} user={pg_user} password={pg_pass}' "
        f"AS {DB_NAME} (DATA_PATH 's3://{bucket}/{DB_NAME}/')"
    )
    con.execute(f"USE {DB_NAME};")
    con.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME};")
    logger.info("ducklake_attached", db=DB_NAME, schema=SCHEMA_NAME, bucket=bucket)
    return con


# ---------------------------------------------------------------------------
# Step 1 -- collect the full-corpus bronze metadata rows (all 13 subjects)
# ---------------------------------------------------------------------------


def collect_documents_rows(subjects: tuple[str, ...]) -> list[dict[str, Any]]:
    """Collect metadata rows for every file under `leaving_certificate/`
    for the given subjects. Fast -- no LLM calls, pure filesystem scan.
    """
    root = DEFAULT_LC_ROOT
    if not root.exists():
        raise FileNotFoundError(f"LC root does not exist: {root}")
    rows = list(lc5_documents(root_path=str(root), subjects=subjects))
    logger.info("documents_rows_collected", count=len(rows), subjects=len(subjects))
    return rows


# ---------------------------------------------------------------------------
# Step 2 -- per-subject syllabus cross-check extraction (real LLM calls)
# ---------------------------------------------------------------------------


def _extract_pdf_text(pdf_path: Path) -> tuple[str, int]:
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages), len(reader.pages)


def _scalar(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _find_primary_syllabus_pdf(subject: str) -> tuple[Path, str] | None:
    """Find the primary syllabus PDF for a subject, preferring English.

    Reuses the classification heuristic already proven in
    `orchestration/defs/2_materials/lc_extraction/quest_pack_assets.py`
    (same repo, different layer -- this is a standalone script, not a
    Dagster asset, so it re-implements the small slice it needs rather
    than importing across the orchestration/ boundary from scripts/).
    """
    import re

    subject_dir = DEFAULT_LC_ROOT / subject
    if not subject_dir.exists():
        return None

    syllabus_keywords = ("syllabus", "specification", "siollabas", "siollabais", "foundation")
    date_suffix_re = re.compile(r"_\d{4}-\d{2}-\d{2}(?=\.pdf$)", re.IGNORECASE)

    candidates: list[tuple[Path, str]] = []
    seen: set[str] = set()
    for pdf_path in sorted(subject_dir.rglob("*.pdf")):
        normalized = date_suffix_re.sub("", pdf_path.name).lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        name_lower = pdf_path.name.lower()
        parent_lower = pdf_path.parent.name.lower()
        if not any(k in name_lower for k in syllabus_keywords):
            continue
        language = "ga" if (parent_lower == "ga" or "gaeilge" in name_lower) else "en"
        candidates.append((pdf_path, language))

    if not candidates:
        return None

    en_candidates = [c for c in candidates if c[1] == "en"]
    pool = en_candidates or candidates
    return min(pool, key=lambda c: len(c[0].name))


def run_syllabus_cross_checks(subjects: tuple[str, ...]) -> list[dict[str, Any]]:
    """Run one real MiniMax-primary/Qwen-secondary cross-check extraction
    per subject's primary syllabus PDF. Subjects with no syllabus PDF
    (or no extractable text layer) are logged and skipped -- not
    fabricated, matching this whole pipeline's existing convention.
    """
    from dlt_sources.filesystem.lc6_cross_check import extract_with_cross_check

    loaded_at = datetime.now(UTC).isoformat()
    rows: list[dict[str, Any]] = []

    for subject in subjects:
        found = _find_primary_syllabus_pdf(subject)
        if found is None:
            logger.warning("syllabus_not_found", subject=subject)
            continue
        pdf_path, language = found

        text, page_count = _extract_pdf_text(pdf_path)
        if not text.strip():
            logger.warning(
                "syllabus_no_text_layer", subject=subject, pdf=pdf_path.name
            )
            continue
        logger.info(
            "syllabus_text_extracted",
            subject=subject,
            pdf=pdf_path.name,
            pages=page_count,
            chars=len(text),
        )

        result = extract_with_cross_check(
            text=text,
            subject=subject,
            language=language,
            source_pdf=pdf_path.name,
            baml_function="ExtractLC6Syllabus",
        )
        primary = result.primary
        secondary = result.secondary
        row = {
            "subject": subject,
            "source_pdf": result.source_pdf,
            "language": result.language,
            "baml_function": result.baml_function,
            "status": result.status,
            "primary_topic_count": _scalar(primary.topic_count) if primary else None,
            "primary_learning_outcome_count": (
                _scalar(primary.learning_outcome_count) if primary else None
            ),
            "primary_level": _scalar(primary.level) if primary else None,
            "primary_source_pages": _scalar(primary.source_pages) if primary else None,
            "secondary_topic_count": (
                _scalar(secondary.topic_count) if secondary else None
            ),
            "secondary_learning_outcome_count": (
                _scalar(secondary.learning_outcome_count) if secondary else None
            ),
            "disagreements_json": json.dumps(result.disagreements),
            "secondary_error": result.secondary_error,
            "primary_error": result.primary_error,
            "loaded_at": loaded_at,
        }
        rows.append(row)
        logger.info(
            "cross_check_run",
            subject=subject,
            source_pdf=result.source_pdf,
            status=result.status,
            primary_topic_count=row["primary_topic_count"],
            primary_learning_outcome_count=row["primary_learning_outcome_count"],
        )

    return rows


# ---------------------------------------------------------------------------
# Step 3 -- load into the real DuckLake catalog
# ---------------------------------------------------------------------------


def load_tables(
    con: Any,
    documents_rows: list[dict[str, Any]],
    cross_check_rows: list[dict[str, Any]],
) -> dict[str, int]:
    import pandas as pd

    docs_df = pd.DataFrame(documents_rows)
    for col in DOCUMENTS_COLUMNS:
        if col not in docs_df.columns:
            docs_df[col] = None
    docs_df = docs_df[list(DOCUMENTS_COLUMNS)]
    con.register("_docs_df", docs_df)
    con.execute(
        f"CREATE OR REPLACE TABLE {DOCUMENTS_TABLE} AS SELECT * FROM _docs_df"
    )
    con.unregister("_docs_df")
    logger.info("documents_table_loaded", table=DOCUMENTS_TABLE, rows=len(documents_rows))

    loaded_cross_check = 0
    if cross_check_rows:
        cc_df = pd.DataFrame(cross_check_rows)
        for col in CROSS_CHECK_COLUMNS:
            if col not in cc_df.columns:
                cc_df[col] = None
        cc_df = cc_df[list(CROSS_CHECK_COLUMNS)]
        con.register("_cc_df", cc_df)
        con.execute(
            f"CREATE OR REPLACE TABLE {CROSS_CHECK_TABLE} AS SELECT * FROM _cc_df"
        )
        con.unregister("_cc_df")
        loaded_cross_check = len(cross_check_rows)
        logger.info(
            "cross_check_table_loaded", table=CROSS_CHECK_TABLE, rows=loaded_cross_check
        )
    else:
        logger.info("cross_check_table_skipped", reason="--skip-extraction or no rows")

    return {"documents": len(documents_rows), "cross_check": loaded_cross_check}


# ---------------------------------------------------------------------------
# Step 4 -- verification
# ---------------------------------------------------------------------------


def verify(con: Any, expect_cross_check: bool) -> dict[str, Any]:
    counts: dict[str, int] = {}
    tables = [DOCUMENTS_TABLE] + ([CROSS_CHECK_TABLE] if expect_cross_check else [])
    for qualified in tables:
        n = con.execute(f"SELECT count(*) FROM {qualified}").fetchone()[0]
        counts[qualified] = int(n)
        logger.info("row_count", table=qualified, count=n)

    per_subject = con.execute(
        f"SELECT subject, count(*) FROM {DOCUMENTS_TABLE} GROUP BY subject ORDER BY subject"
    ).fetchall()
    return {"counts": counts, "per_subject_documents": per_subject}


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Hydrate the real local DuckLake catalog with the full "
        "13-subject/144-file leaving_certificate/ corpus."
    )
    parser.add_argument(
        "--skip-extraction",
        action="store_true",
        help="Skip the real LLM cross-check runs (step 2); load only the "
        "full-corpus documents table. For LLM-free re-runs.",
    )
    parser.add_argument(
        "--subjects",
        nargs="*",
        default=None,
        help="Subset of subjects to process (default: all 13).",
    )
    args = parser.parse_args(argv)

    subjects = tuple(args.subjects) if args.subjects else ALL_LC_SUBJECTS
    unknown = [s for s in subjects if s not in ALL_LC_SUBJECTS]
    if unknown:
        parser.error(f"unknown subject(s): {unknown} (known: {ALL_LC_SUBJECTS})")

    logger.info(
        "hydration_start",
        subjects=len(subjects),
        skip_extraction=args.skip_extraction,
        MINIMAX_API_KEY_present=bool(os.environ.get("MINIMAX_API_KEY")),
        DASHSCOPE_API_KEY_present=bool(os.environ.get("DASHSCOPE_API_KEY")),
    )

    con = connect_ducklake()

    documents_rows = collect_documents_rows(subjects)

    cross_check_rows: list[dict[str, Any]] = []
    if not args.skip_extraction:
        cross_check_rows = run_syllabus_cross_checks(subjects)

    loaded = load_tables(con, documents_rows, cross_check_rows)
    verification = verify(con, expect_cross_check=bool(cross_check_rows))

    print("=== LC full-corpus hydration summary ===")
    print(f"subjects processed: {len(subjects)}")
    print(f"documents rows loaded: {loaded['documents']}")
    print(f"cross_check rows loaded: {loaded['cross_check']}")
    for row in cross_check_rows:
        print(
            f"  {row['subject']}: {row['source_pdf']} [{row['language']}] "
            f"status={row['status']} "
            f"topic_count={row['primary_topic_count']} "
            f"lo_count={row['primary_learning_outcome_count']} "
            f"level={row['primary_level']}"
        )
    print("per-subject document counts:")
    for subject, count in verification["per_subject_documents"]:
        print(f"  {subject}: {count}")
    print("table row counts:")
    for qualified, count in verification["counts"].items():
        print(f"  {qualified}: {count} rows")
    logger.info("hydration_complete", **loaded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
