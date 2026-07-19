"""British Isles subject registry API (BIEP v3).

Per the 2026-07-27-biep-v3-canonical-registry-v1 change.

This module is the canonical Python API for the registry stored in:
  - cianfhoghlaim.education._registry.subjects
  - cianfhoghlaim.education._registry.jurisdiction_overrides
  - cianfhoghlaim.education._registry.cross_jurisdiction_bridges

The registry is the source of truth for the BIEP v3 generic pipelines
(Phases 2-5). Each jurisdiction pipeline queries the registry to
discover which (subject, stage, board, qualification_level, language)
tuples to materialise.

## KCG patterns used
- ibis (per `.agents/skills/ibis/SKILL.md`) — every query uses
  ``ibis.duckdb.connect()`` (NO raw ``duckdb.connect()``).
- python (per the BAML client conventions) — the public API is
  pure-Python so the same module is reusable from BAML
  ``@function`` definitions.

Reference: openspec/changes/2026-07-27-biep-v3-canonical-registry-v1/
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal

Jurisdiction = Literal[
    "ireland", "england", "scotland", "wales",
    "northern_ireland", "jersey", "guernsey", "isle_of_man",
]

EducationalStage = Literal[
    "primary", "junior_cycle", "senior_cycle", "leaving_certificate",
    "gcse", "as_level", "a_level", "national_5", "higher", "advanced_higher",
    "foundation",
]

AwardingBody = Literal[
    "none", "aqa", "ocr", "edexcel", "wjec", "ccea", "sqa",
]

QualificationLevel = Literal[
    "hl", "ol", "fl", "foundation_tier", "higher_tier",
    "untiered", "year_1", "year_2", "year_3", "ty",
]

Language = Literal["en", "ga", "cy", "gd", "gv"]

# The canonical BIEP v3 registry schema.
# Defaults to `{DEFAULT_SUBJECTS_TABLE}` (MotherDuck
# convention), but `BIEP_REGISTRY_SCHEMA` env var can override (e.g.,
# `cianchoghlaim.education.subjects` for DuckLake which doesn't support
# dotted schema names).
DEFAULT_REGISTRY_SCHEMA: str = os.getenv(
    "BIEP_REGISTRY_SCHEMA",
    "cianchoghlaim.education._registry",
)
DEFAULT_SUBJECTS_TABLE: str = f"{DEFAULT_REGISTRY_SCHEMA}.subjects"


@dataclass
class SubjectRegistryRow:
    """One row in the cianfhoghlaim.education._registry.subjects table."""

    jurisdiction: Jurisdiction
    stage: EducationalStage
    subject_slug: str
    board: AwardingBody = "none"
    qualification_level: QualificationLevel | None = None
    language: Language = "en"

    display_name_en: str = ""
    display_name_local: str | None = None
    concept: str = ""
    source_url: str | None = None
    ncca_spec_code: str | None = None

    baml_function: str = ""
    source: str = "USER_SUBMITTED"
    status: str = "ACTIVE"
    first_introduced: str | None = None
    last_verified: str | None = None
    notes: str | None = None

    def to_tuple(self) -> tuple[str, ...]:
        """The composite primary key as a flat tuple."""
        return (
            self.jurisdiction, self.stage, self.subject_slug,
            self.board, self.qualification_level or "", self.language,
        )


def _ibis_conn():
    """The duckdb-first connection (per the BIEP v3 spec).

    Honors `BIEP_REGISTRY_URI` env var to override the default
    `md:cianfhoghlaim` MotherDuck connection (e.g., for local dev against
    DuckLake or a test DuckDB file).

    For DuckLake URIs (`ducklake:postgres:...`), the function attaches
    the DuckLake catalog and sets it as the default schema, then returns
    a connection bound to that catalog. For MotherDuck or plain DuckDB
    file URIs, returns a plain connection.

    NOTE: This previously used ibis.duckdb.connect() but was switched to
    raw duckdb.connect() because ibis >= 10 removed the `params=`
    keyword from SQLBackend.sql(). The raw duckdb API provides native
    parameterized queries via the second positional argument.
    """
    import duckdb  # type: ignore[import-not-found]
    uri = os.getenv("BIEP_REGISTRY_URI", "md:cianfhoghlaim")
    schema = os.getenv("BIEP_REGISTRY_SCHEMA", DEFAULT_REGISTRY_SCHEMA)

    # If the schema has a dotted prefix (e.g., "lakehouse.education"),
    # the part before the dot is the DuckDB ATTACH catalog name.
    # Strip it for INSERT/SELECT statements so they reference the
    # schema without the catalog prefix (since USE lakehouse; makes
    # `lakehouse.education.subjects` resolve as `education.subjects`).
    if "." in schema:
        attach_catalog = schema.split(".")[0]
        schema_only = schema.split(".", 1)[1]
    else:
        attach_catalog = None
        schema_only = schema

    conn = duckdb.connect(uri, read_only=True)
    if attach_catalog is not None and uri.startswith("ducklake:"):
        # ATTACH the DuckLake catalog (the URI already has the
        # attach clause; we just need to USE it).
        try:
            conn.execute(f"USE {attach_catalog};")
        except duckdb.Error:
            # Some URIs (like md:cianfhoghlaim) don't need USE.
            pass

    # Stash the stripped schema on the connection object so callers
    # can access it via conn.schema if needed (also used by insert).
    conn._biep_schema = schema_only  # type: ignore[attr-defined]
    return conn


def query_by_jurisdiction(
    jurisdiction: Jurisdiction,
) -> list[SubjectRegistryRow]:
    """Return all registry rows for one jurisdiction (across all stages)."""
    import duckdb  # type: ignore[import-not-found]
    uri = os.getenv("BIEP_REGISTRY_URI", "md:cianfhoghlaim")
    conn = duckdb.connect(uri, read_only=True)
    df = conn.execute(
        f"""
        SELECT *
        FROM {DEFAULT_SUBJECTS_TABLE}
        WHERE jurisdiction = ?
        ORDER BY stage, subject_slug, board, qualification_level
        """,
        [jurisdiction],
    ).fetch_df()
    conn.close()
    return [_row_to_dataclass(row) for _, row in df.iterrows()]


def query_by_concept(concept: str) -> list[SubjectRegistryRow]:
    """Return all registry rows for one cross-jurisdiction concept."""
    import duckdb  # type: ignore[import-not-found]
    uri = os.getenv("BIEP_REGISTRY_URI", "md:cianfhoghlaim")
    conn = duckdb.connect(uri, read_only=True)
    df = conn.execute(
        f"""
        SELECT *
        FROM {DEFAULT_SUBJECTS_TABLE}
        WHERE concept = ?
        ORDER BY jurisdiction, stage, subject_slug
        """,
        [concept],
    ).fetch_df()
    conn.close()
    return [_row_to_dataclass(row) for _, row in df.iterrows()]


def query_by_stage(
    jurisdiction: Jurisdiction,
    stage: EducationalStage,
) -> list[SubjectRegistryRow]:
    """Return all registry rows for one (jurisdiction, stage) tuple."""
    import duckdb  # type: ignore[import-not-found]
    uri = os.getenv("BIEP_REGISTRY_URI", "md:cianfhoghlaim")
    conn = duckdb.connect(uri, read_only=True)
    df = conn.execute(
        f"""
        SELECT *
        FROM {DEFAULT_SUBJECTS_TABLE}
        WHERE jurisdiction = ? AND stage = ?
        ORDER BY subject_slug, board, qualification_level
        """,
        [jurisdiction, stage],
    ).fetch_df()
    conn.close()
    return [_row_to_dataclass(row) for _, row in df.iterrows()]


def query_cross_jurisdiction_bridges() -> list[dict[str, Any]]:
    """Return all cross-jurisdiction bridges (the slug-mappings)."""
    import duckdb  # type: ignore[import-not-found]
    uri = os.getenv("BIEP_REGISTRY_URI", "md:cianfhoghlaim")
    conn = duckdb.connect(uri, read_only=True)
    df = conn.execute(
        f"SELECT * FROM {DEFAULT_REGISTRY_SCHEMA}.cross_jurisdiction_bridges ORDER BY concept"
    ).fetch_df()
    conn.close()
    bridges = []
    for _, row in df.iterrows():
        bridges.append({
            "concept": row["concept"],
            "jurisdiction_slug_map": json.loads(row["jurisdiction_slug_map"]),
            "display_name": row["display_name"],
            "notes": row.get("notes"),
        })
    return bridges
    bridges = []
    for _, row in df.iterrows():
        bridges.append({
            "concept": row["concept"],
            "jurisdiction_slug_map": json.loads(row["jurisdiction_slug_map"]),
            "display_name": row["display_name"],
            "notes": row.get("notes"),
        })
    return bridges


def insert_subject(row: SubjectRegistryRow, conn: Any | None = None) -> None:
    """Insert one row into the registry (write to a separate connection).

    Honors `BIEP_REGISTRY_URI` env var (same as `_ibis_conn`).

    Uses raw duckdb (not ibis) because the ibis SQLBackend.sql() API
    no longer accepts `params=` in ibis >= 10. The raw duckdb API is
    stable and provides native parameterized queries.

    Skips the insert if the row already exists (idempotent). For
    DuckLake (no PK constraints), this check-then-insert pattern is
    the safest atomic-ish approach.

    Pass an existing `conn` for batch ingestion (avoids the cost of
    opening + closing a connection per row). If `conn` is None, opens
    a new connection per call.
    """
    import duckdb  # type: ignore[import-not-found]
    uri = os.getenv("BIEP_REGISTRY_URI", "md:cianfhoghlaim")
    schema = os.getenv("BIEP_REGISTRY_SCHEMA", DEFAULT_REGISTRY_SCHEMA)

    # For DuckLake catalogs, USE the attached catalog so the schema
    # references resolve (otherwise `education.subjects` doesn't exist).
    if "." in schema and uri.startswith("ducklake:"):
        attach_catalog = schema.split(".")[0]
        effective_schema = schema.split(".", 1)[1]
    else:
        attach_catalog = None
        effective_schema = schema

    full_table = f"{effective_schema}.subjects"

    owns_conn = conn is None
    if owns_conn:
        conn = duckdb.connect(uri, read_only=False)
        if attach_catalog:
            try:
                conn.execute(f"USE {attach_catalog};")
            except duckdb.Error:
                pass

    try:
        # Check if the row already exists for this composite key.
        existing = conn.execute(
            f"""
            SELECT 1 FROM {full_table}
            WHERE jurisdiction = ? AND stage = ? AND subject_slug = ?
              AND board = ? AND qualification_level = ? AND language = ?
            LIMIT 1
            """,
            [
                row.jurisdiction, row.stage, row.subject_slug, row.board,
                row.qualification_level, row.language,
            ],
        ).fetchall()
        if existing:
            return  # idempotent — already exists

        conn.execute(
            f"""
            INSERT INTO {full_table}
            (jurisdiction, stage, subject_slug, board, qualification_level,
             language, display_name_en, display_name_local, concept,
             source_url, ncca_spec_code, baml_function, source, status,
             first_introduced, last_verified, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                row.jurisdiction, row.stage, row.subject_slug, row.board,
                row.qualification_level, row.language,
                row.display_name_en, row.display_name_local, row.concept,
                row.source_url, row.ncca_spec_code, row.baml_function,
                row.source, row.status, row.first_introduced,
                row.last_verified, row.notes,
            ],
        )
    finally:
        if owns_conn:
            conn.close()


def _row_to_dataclass(row: Any) -> SubjectRegistryRow:
    """Convert an ibis DataFrame row to a SubjectRegistryRow."""
    return SubjectRegistryRow(
        jurisdiction=row["jurisdiction"],
        stage=row["stage"],
        subject_slug=row["subject_slug"],
        board=row.get("board") or "none",
        qualification_level=row.get("qualification_level") or None,
        language=row.get("language") or "en",
        display_name_en=row.get("display_name_en", ""),
        display_name_local=row.get("display_name_local"),
        concept=row.get("concept", ""),
        source_url=row.get("source_url"),
        ncca_spec_code=row.get("ncca_spec_code"),
        baml_function=row.get("baml_function", ""),
        source=row.get("source", "USER_SUBMITTED"),
        status=row.get("status", "ACTIVE"),
        first_introduced=row.get("first_introduced"),
        last_verified=row.get("last_verified"),
        notes=row.get("notes"),
    )


__all__ = [
    "Jurisdiction",
    "EducationalStage",
    "AwardingBody",
    "QualificationLevel",
    "Language",
    "SubjectRegistryRow",
    "query_by_jurisdiction",
    "query_by_concept",
    "query_by_stage",
    "query_cross_jurisdiction_bridges",
    "insert_subject",
]