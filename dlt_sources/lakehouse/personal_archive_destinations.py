"""DuckLake destination for the UoG personal-archive pipeline.

Defines 9 typed DuckLake tables under
``cianfhoghlaim.education.ie.personal_archive_*`` + the
``student_transcripts`` table. Each table has its columns + a
``COMMENT`` listing the partition keys, so the marimo notebook
can introspect the schema.

The 9 tables:

1. ``personal_archive_artefacts`` — one row per discovered file
2. ``personal_archive_assignments`` — one row per assignment
3. ``personal_archive_questions`` — one row per question (F-granular)
4. ``personal_archive_topics`` — one row per topic
5. ``personal_archive_reading_lists`` — one row per reading item
6. ``personal_archive_code_cells`` — one row per code cell
7. ``personal_archive_ca_marks`` — one row per CA mark
8. ``personal_archive_modules`` — one row per module summary
9. ``student_transcripts`` — one row per (student, module, year)

Reference: openspec/changes/2026-08-23-uog-personal-archive-tertiary-modules-v1/
            specs/cianfhoghlaim-personal-archive-typed-modules/spec.md
"""

from __future__ import annotations

from typing import Any

import structlog

logger = structlog.get_logger(__name__)


DEFAULT_SCHEMA: str = "cianfhoghlaim.education.ie"


# ---------------------------------------------------------------------------- #
# Per-table CREATE TABLE statements
# ---------------------------------------------------------------------------- #


_PERSONAL_ARCHIVE_ARTEFACTS_DDL: str = """
CREATE TABLE IF NOT EXISTS {schema}.personal_archive_artefacts (
  artefact_id VARCHAR NOT NULL,
  artefact_kind VARCHAR NOT NULL,
  artefact_provenance VARCHAR NOT NULL,
  module_code VARCHAR,
  module_title VARCHAR,
  programme_code VARCHAR,
  academic_year INTEGER,
  semester VARCHAR,
  file_path VARCHAR NOT NULL,
  file_hash VARCHAR NOT NULL,
  bytes BIGINT NOT NULL,
  file_extension VARCHAR NOT NULL,
  embedded_text VARCHAR,
  confidence DOUBLE NOT NULL,
  provenance_meta JSON,
  content_hash VARCHAR NOT NULL,
  scraped_at VARCHAR NOT NULL,
  institution_id VARCHAR NOT NULL,
  -- partition keys
  PRIMARY KEY (artefact_id, content_hash)
);
COMMENT ON TABLE {schema}.personal_archive_artefacts IS
  'Partition keys: institution_id, module_code, artefact_kind, academic_year, artefact_provenance';
"""


_PERSONAL_ARCHIVE_ASSIGNMENTS_DDL: str = """
CREATE TABLE IF NOT EXISTS {schema}.personal_archive_assignments (
  assignment_id VARCHAR NOT NULL,
  artefact_id VARCHAR NOT NULL,
  module_code VARCHAR NOT NULL,
  assignment_number INTEGER NOT NULL,
  assignment_title VARCHAR,
  total_marks INTEGER,
  weight_percent DOUBLE,
  submission_deadline VARCHAR,
  question_count INTEGER NOT NULL DEFAULT 0,
  institution_id VARCHAR NOT NULL,
  content_hash VARCHAR NOT NULL,
  file_path VARCHAR NOT NULL,
  confidence DOUBLE NOT NULL,
  scraped_at VARCHAR NOT NULL,
  -- partition keys
  PRIMARY KEY (assignment_id, content_hash)
);
COMMENT ON TABLE {schema}.personal_archive_assignments IS
  'Partition keys: module_code, assignment_number';
"""


_PERSONAL_ARCHIVE_QUESTIONS_DDL: str = """
CREATE TABLE IF NOT EXISTS {schema}.personal_archive_questions (
  question_id VARCHAR NOT NULL,
  assignment_id VARCHAR NOT NULL,
  module_code VARCHAR NOT NULL,
  question_number VARCHAR NOT NULL,
  question_text VARCHAR NOT NULL,
  expected_topic VARCHAR,
  max_marks INTEGER,
  my_answer_text VARCHAR,
  my_answer_latex VARCHAR,
  my_mark INTEGER,
  my_mark_breakdown VARCHAR,
  is_handwritten BOOLEAN NOT NULL DEFAULT FALSE,
  htr_backend_used VARCHAR,
  htr_confidence DOUBLE,
  answer_topic_tags VARCHAR[],
  confidence DOUBLE NOT NULL,
  scraped_at VARCHAR NOT NULL,
  -- partition keys
  PRIMARY KEY (question_id)
);
COMMENT ON TABLE {schema}.personal_archive_questions IS
  'Partition keys: module_code, question_id. F-granular — one row per question.';
"""


_PERSONAL_ARCHIVE_TOPICS_DDL: str = """
CREATE TABLE IF NOT EXISTS {schema}.personal_archive_topics (
  topic_id VARCHAR NOT NULL,
  topic_name VARCHAR NOT NULL,
  topic_category VARCHAR NOT NULL,
  module_codes VARCHAR[] NOT NULL,
  occurrence_count INTEGER NOT NULL DEFAULT 1,
  confidence DOUBLE NOT NULL,
  scraped_at VARCHAR NOT NULL,
  -- partition keys
  PRIMARY KEY (topic_id)
);
COMMENT ON TABLE {schema}.personal_archive_topics IS
  'Partition keys: topic_category';
"""


_PERSONAL_ARCHIVE_READING_LISTS_DDL: str = """
CREATE TABLE IF NOT EXISTS {schema}.personal_archive_reading_lists (
  reading_id VARCHAR NOT NULL,
  module_code VARCHAR NOT NULL,
  title VARCHAR NOT NULL,
  authors VARCHAR[] NOT NULL,
  format VARCHAR NOT NULL,
  isbn_13 VARCHAR,
  doi VARCHAR,
  url VARCHAR,
  is_essential BOOLEAN NOT NULL DEFAULT FALSE,
  confidence DOUBLE NOT NULL,
  scraped_at VARCHAR NOT NULL,
  -- partition keys
  PRIMARY KEY (reading_id)
);
COMMENT ON TABLE {schema}.personal_archive_reading_lists IS
  'Partition keys: module_code';
"""


_PERSONAL_ARCHIVE_CODE_CELLS_DDL: str = """
CREATE TABLE IF NOT EXISTS {schema}.personal_archive_code_cells (
  cell_id VARCHAR NOT NULL,
  module_code VARCHAR NOT NULL,
  notebook_path VARCHAR NOT NULL,
  cell_index INTEGER NOT NULL,
  cell_type VARCHAR NOT NULL,
  source_text VARCHAR NOT NULL,
  runtime_seconds DOUBLE,
  output_text VARCHAR,
  demonstrates_topics VARCHAR[] NOT NULL,
  confidence DOUBLE NOT NULL,
  scraped_at VARCHAR NOT NULL,
  -- partition keys
  PRIMARY KEY (cell_id)
);
COMMENT ON TABLE {schema}.personal_archive_code_cells IS
  'Partition keys: module_code, notebook_path';
"""


_PERSONAL_ARCHIVE_CA_MARKS_DDL: str = """
CREATE TABLE IF NOT EXISTS {schema}.personal_archive_ca_marks (
  ca_id VARCHAR NOT NULL,
  module_code VARCHAR NOT NULL,
  ca_label VARCHAR NOT NULL,
  ca_weight_percent DOUBLE,
  mark DOUBLE,
  max_mark DOUBLE,
  academic_year INTEGER,
  extracted_from_artefact_id VARCHAR,
  confidence DOUBLE NOT NULL,
  scraped_at VARCHAR NOT NULL,
  -- partition keys
  PRIMARY KEY (ca_id)
);
COMMENT ON TABLE {schema}.personal_archive_ca_marks IS
  'Partition keys: module_code';
"""


_PERSONAL_ARCHIVE_MODULES_DDL: str = """
CREATE TABLE IF NOT EXISTS {schema}.personal_archive_modules (
  module_code VARCHAR NOT NULL,
  module_title VARCHAR,
  programme_code VARCHAR,
  artefact_count INTEGER NOT NULL DEFAULT 0,
  assignment_count INTEGER NOT NULL DEFAULT 0,
  question_count INTEGER NOT NULL DEFAULT 0,
  topic_count INTEGER NOT NULL DEFAULT 0,
  code_cell_count INTEGER NOT NULL DEFAULT 0,
  reading_count INTEGER NOT NULL DEFAULT 0,
  transcript_grade VARCHAR,
  transcript_academic_year INTEGER,
  first_artefact_year INTEGER,
  last_artefact_year INTEGER,
  confidence DOUBLE NOT NULL,
  scraped_at VARCHAR NOT NULL,
  -- partition keys
  PRIMARY KEY (module_code)
);
COMMENT ON TABLE {schema}.personal_archive_modules IS
  'Partition keys: module_code. Per-module summary row built at the end of the pipeline.';
"""


_STUDENT_TRANSCRIPTS_DDL: str = """
CREATE TABLE IF NOT EXISTS {schema}.student_transcripts (
  student_id VARCHAR NOT NULL,
  institution_id VARCHAR NOT NULL,
  programme_code VARCHAR NOT NULL,
  programme_title VARCHAR NOT NULL,
  module_code VARCHAR NOT NULL,
  module_title VARCHAR NOT NULL,
  ects INTEGER,
  nfq_level INTEGER,
  academic_year INTEGER NOT NULL,
  semester VARCHAR,
  grade VARCHAR NOT NULL,
  is_honours BOOLEAN NOT NULL DEFAULT FALSE,
  is_resit BOOLEAN NOT NULL DEFAULT FALSE,
  transcript_pdf VARCHAR NOT NULL,
  source_url VARCHAR,
  scraped_at VARCHAR NOT NULL,
  confidence DOUBLE NOT NULL,
  file_hash VARCHAR NOT NULL,
  -- partition keys
  PRIMARY KEY (student_id, module_code, academic_year)
);
COMMENT ON TABLE {schema}.student_transcripts IS
  'Partition keys: student_id, programme_code, academic_year. Ground-truth transcript rows.';
"""


_ALL_TABLE_DDLS: tuple[str, ...] = (
    _PERSONAL_ARCHIVE_ARTEFACTS_DDL,
    _PERSONAL_ARCHIVE_ASSIGNMENTS_DDL,
    _PERSONAL_ARCHIVE_QUESTIONS_DDL,
    _PERSONAL_ARCHIVE_TOPICS_DDL,
    _PERSONAL_ARCHIVE_READING_LISTS_DDL,
    _PERSONAL_ARCHIVE_CODE_CELLS_DDL,
    _PERSONAL_ARCHIVE_CA_MARKS_DDL,
    _PERSONAL_ARCHIVE_MODULES_DDL,
    _STUDENT_TRANSCRIPTS_DDL,
)


_TABLE_NAMES: tuple[str, ...] = (
    "personal_archive_artefacts",
    "personal_archive_assignments",
    "personal_archive_questions",
    "personal_archive_topics",
    "personal_archive_reading_lists",
    "personal_archive_code_cells",
    "personal_archive_ca_marks",
    "personal_archive_modules",
    "student_transcripts",
)


# ---------------------------------------------------------------------------- #
# Public API
# ---------------------------------------------------------------------------- #


def register_personal_archive_tables(
    con: Any,
    schema_name: str = DEFAULT_SCHEMA,
) -> list[str]:
    """Create the 9 personal-archive tables if they don't exist.

    Args:
        con: A DuckDB connection (or any DB-API 2.0 compatible
            connection that supports ``.execute(...)``).
        schema_name: The DuckLake schema name (default
            ``cianfhoghlaim.education.ie``).

    Returns:
        The list of table names that were ensured.
    """
    created: list[str] = []
    # DuckDB requires the schema name to be quoted when it contains
    # more than one dot (the parser treats dotted names as
    # `catalog.schema` by default). The schema name
    # ``cianfhoghlaim.education.ie`` is a 3-part logical namespace
    # (the Mother's Duck convention), so we always quote it.
    quoted_schema = f'"{schema_name}"'
    try:
        con.execute(f"CREATE SCHEMA IF NOT EXISTS {quoted_schema}")
        con.execute(f"USE {quoted_schema}")
    except Exception as exc:  # noqa: BLE001 — DuckDB + DuckLake errors
        logger.warning(
            "personal_archive_schema_create_failed",
            schema=schema_name,
            error=str(exc),
        )

    for ddl_template, table_name in zip(_ALL_TABLE_DDLS, _TABLE_NAMES):
        # Strip the {schema}. prefix so the USE takes effect.
        ddl = ddl_template.format(schema="").strip()
        # The {schema}. substitution leaves a leading dot (".") when
        # schema=""; replace ".tablename" with "tablename" so the
        # CREATE TABLE statement reads correctly under the active schema.
        import re as _re

        ddl = _re.sub(r"\.\s*([a-zA-Z_])", r"\1", ddl, count=2)
        try:
            con.execute(ddl)
            created.append(f"{schema_name}.{table_name}")
            logger.info(
                "personal_archive_table_ready",
                table=f"{schema_name}.{table_name}",
            )
        except Exception as exc:  # noqa: BLE001 — DuckDB + DuckLake errors
            logger.warning(
                "personal_archive_table_create_failed",
                table=f"{schema_name}.{table_name}",
                error=str(exc),
            )
    return created


def get_personal_archive_table_names() -> tuple[str, ...]:
    """Return the canonical 9 table names (without schema prefix)."""
    return _TABLE_NAMES


def get_personal_archive_dialect_namespace(schema_name: str = DEFAULT_SCHEMA) -> str:
    """Return the canonical ``md:<namespace>`` namespace string."""
    return schema_name


__all__ = [
    "DEFAULT_SCHEMA",
    "register_personal_archive_tables",
    "get_personal_archive_table_names",
    "get_personal_archive_dialect_namespace",
]


# === Wave 4 (2026-08-24-wave-4-ducklake-v1-hardening-v1) re-export ===
# This file is now BOTH the legacy personal_archive implementation
# AND a re-export shim for the layer-grouped destinations. New code
# SHOULD import from `dlt_sources.common.destinations.filesystem`.
from dlt_sources.common.destinations import (  # noqa: E402,F401
    named_destinations,
    DESTINATIONS,
)
from dlt_sources.common.destinations.filesystem import get_filesystem_destination  # noqa: E402,F401
