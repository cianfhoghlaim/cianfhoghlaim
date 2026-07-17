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
    """The ibis-first connection (per the BIEP v3 spec)."""
    try:
        import ibis  # type: ignore[import-not-found]
    except ImportError as exc:
        raise ImportError(
            "ibis is required for the registry API. "
            "Install with `uv add ibis-framework[duckdb]`."
        ) from exc
    return ibis.duckdb.connect("md:cianfhoghlaim", read_only=True)


def query_by_jurisdiction(
    jurisdiction: Jurisdiction,
) -> list[SubjectRegistryRow]:
    """Return all registry rows for one jurisdiction (across all stages)."""
    conn = _ibis_conn()
    df = conn.sql(
        """
        SELECT *
        FROM cianfhoghlaim.education._registry.subjects
        WHERE jurisdiction = ?
        ORDER BY stage, subject_slug, board, qualification_level
        """,
        params=(jurisdiction,),
    ).execute()
    return [_row_to_dataclass(row) for _, row in df.iterrows()]


def query_by_concept(concept: str) -> list[SubjectRegistryRow]:
    """Return all registry rows for one cross-jurisdiction concept."""
    conn = _ibis_conn()
    df = conn.sql(
        """
        SELECT *
        FROM cianfhoghlaim.education._registry.subjects
        WHERE concept = ?
        ORDER BY jurisdiction, stage, subject_slug
        """,
        params=(concept,),
    ).execute()
    return [_row_to_dataclass(row) for _, row in df.iterrows()]


def query_by_stage(
    jurisdiction: Jurisdiction,
    stage: EducationalStage,
) -> list[SubjectRegistryRow]:
    """Return all registry rows for one (jurisdiction, stage) tuple."""
    conn = _ibis_conn()
    df = conn.sql(
        """
        SELECT *
        FROM cianfhoghlaim.education._registry.subjects
        WHERE jurisdiction = ? AND stage = ?
        ORDER BY subject_slug, board, qualification_level
        """,
        params=(jurisdiction, stage),
    ).execute()
    return [_row_to_dataclass(row) for _, row in df.iterrows()]


def query_cross_jurisdiction_bridges() -> list[dict[str, Any]]:
    """Return all cross-jurisdiction bridges (the slug-mappings)."""
    conn = _ibis_conn()
    df = conn.sql(
        "SELECT * FROM cianfhoghlaim.education._registry.cross_jurisdiction_bridges ORDER BY concept"
    ).execute()
    bridges = []
    for _, row in df.iterrows():
        bridges.append({
            "concept": row["concept"],
            "jurisdiction_slug_map": json.loads(row["jurisdiction_slug_map"]),
            "display_name": row["display_name"],
            "notes": row.get("notes"),
        })
    return bridges


def insert_subject(row: SubjectRegistryRow) -> None:
    """Insert one row into the registry (write to a separate connection)."""
    import ibis  # type: ignore[import-not-found]
    conn = ibis.duckdb.connect("md:cianfhoghlaim", read_only=False)
    conn.sql(
        """
        INSERT OR REPLACE INTO cianfhoghlaim.education._registry.subjects
        (jurisdiction, stage, subject_slug, board, qualification_level,
         language, display_name_en, display_name_local, concept,
         source_url, ncca_spec_code, baml_function, source, status,
         first_introduced, last_verified, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        params=(
            row.jurisdiction, row.stage, row.subject_slug, row.board,
            row.qualification_level, row.language,
            row.display_name_en, row.display_name_local, row.concept,
            row.source_url, row.ncca_spec_code, row.baml_function,
            row.source, row.status, row.first_introduced,
            row.last_verified, row.notes,
        ),
    ).execute()


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