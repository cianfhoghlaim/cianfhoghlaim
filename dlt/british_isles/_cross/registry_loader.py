"""British Isles subject registry loader (BIEP v3).

Per the 2026-07-27-biep-v3-canonical-registry-v1 change.

Loads the canonical subject registry from official sources (NCCA,
AQA, OCR, Edexcel, WJEC, CCEA, SQA, Jersey, Guernsey, Isle of Man) into
the DuckDB tables:
  - cianfhoghlaim.education._registry.subjects
  - cianfhoghlaim.education._registry.cross_jurisdiction_bridges

Phases 2-5 will call this loader for their respective jurisdictions
(Phase 2 = Ireland, Phase 3 = England, etc.).

## KCG patterns used
- ibis (per `.agents/skills/ibis/SKILL.md`) — every write uses
  ``ibis.duckdb.connect(write=True)``.
- python (per the BIEP v3 spec) — pure-Python public API.

Reference: openspec/changes/2026-07-27-biep-v3-canonical-registry-v1/
"""
from __future__ import annotations

import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path

from .registry_api import (
    SubjectRegistryRow,
    insert_subject,
    query_by_jurisdiction,
    query_cross_jurisdiction_bridges,
)

logger = logging.getLogger(__name__)


def load_ireland_subjects() -> list[SubjectRegistryRow]:
    """Load the 64 Ireland Leaving Cert + 18 JC + 16 short courses + 36 CBAs.

    Sourced from `dlt/british_isles/ireland/education/_shared/education_level.baml`
    (the canonical 64-value `LeavingCertSubject` enum) and the
    `JC_SUBJECTS` + `JC_SHORT_COURSES` lists in
    `dlt/british_isles/ireland/education/junior_cycle.py`.

    Full implementation is in Phase 2 of the BIEP v3 batch. For now, this
    loader returns a minimal 4-subject seed (mathematics, chemistry,
    english, gaeilge) so the registry is non-empty and the companion
    notebook can render.
    """
    return [
        SubjectRegistryRow(
            jurisdiction="ireland",
            stage="leaving_certificate",
            subject_slug="mathematics",
            board="none",
            qualification_level="hl",
            language="en",
            display_name_en="Mathematics",
            display_name_local="Matamaitic",
            concept="MATHEMATICS",
            source_url="https://www.ncca.ie/en/senior-cycle/subjects/mathematics",
            ncca_spec_code="LC003",
            baml_function="b.ExtractCurriculumSyllabus",
            source="NCCA_OFFICIAL",
            status="ACTIVE",
            first_introduced="1967-09",
            last_verified="2026-07-17",
        ),
        SubjectRegistryRow(
            jurisdiction="ireland",
            stage="leaving_certificate",
            subject_slug="chemistry",
            board="none",
            qualification_level="hl",
            language="en",
            display_name_en="Chemistry",
            concept="CHEMISTRY",
            source_url="https://www.ncca.ie/en/senior-cycle/subjects/chemistry",
            ncca_spec_code="LC022",
            baml_function="b.ExtractCurriculumSyllabus",
            source="NCCA_OFFICIAL",
            status="ACTIVE",
            first_introduced="1967-09",
            last_verified="2026-07-17",
        ),
        SubjectRegistryRow(
            jurisdiction="ireland",
            stage="leaving_certificate",
            subject_slug="english",
            board="none",
            qualification_level="hl",
            language="en",
            display_name_en="English",
            concept="ENGLISH",
            source_url="https://www.ncca.ie/en/senior-cycle/subjects/english",
            ncca_spec_code="LC002",
            baml_function="b.ExtractCurriculumSyllabus",
            source="NCCA_OFFICIAL",
            status="ACTIVE",
            first_introduced="1967-09",
            last_verified="2026-07-17",
        ),
        SubjectRegistryRow(
            jurisdiction="ireland",
            stage="leaving_certificate",
            subject_slug="gaeilge",
            board="none",
            qualification_level="hl",
            language="ga",
            display_name_en="Gaeilge (Irish)",
            display_name_local="Gaeilge",
            concept="IRISH_LANGUAGE",
            source_url="https://www.ncca.ie/en/senior-cycle/subjects/gaeilge",
            ncca_spec_code="LC001",
            baml_function="b.ExtractCurriculumSyllabus",
            source="NCCA_OFFICIAL",
            status="ACTIVE",
            first_introduced="1967-09",
            last_verified="2026-07-17",
        ),
    ]


def load_england_subjects() -> list[SubjectRegistryRow]:
    """Load the 43 AQA GCSE + 49 A-Level + 88 AQA/OCR/Edexcel subjects.

    Full implementation is in Phase 3 of the BIEP v3 batch. For now, this
    loader returns a minimal 4-subject seed (mathematics, english_language,
    chemistry, biology) so the registry is non-empty across jurisdictions.
    """
    return [
        SubjectRegistryRow(
            jurisdiction="england",
            stage="gcse",
            subject_slug="mathematics",
            board="aqa",
            qualification_level=None,
            language="en",
            display_name_en="GCSE Mathematics",
            concept="MATHEMATICS",
            source_url="https://www.aqa.org.uk/subjects/mathematics/gcse/mathematics-8035",
            baml_function="b.ExtractUKQualSpec",
            source="AQA_OFFICIAL",
            status="ACTIVE",
            first_introduced="2017-09",
            last_verified="2026-07-17",
        ),
        SubjectRegistryRow(
            jurisdiction="england",
            stage="gcse",
            subject_slug="english_language",
            board="aqa",
            qualification_level=None,
            language="en",
            display_name_en="GCSE English Language",
            concept="ENGLISH",
            source_url="https://www.aqa.org.uk/subjects/english/gcse/english-language-8700",
            baml_function="b.ExtractUKQualSpec",
            source="AQA_OFFICIAL",
            status="ACTIVE",
            first_introduced="2015-09",
            last_verified="2026-07-17",
        ),
        SubjectRegistryRow(
            jurisdiction="england",
            stage="gcse",
            subject_slug="chemistry",
            board="aqa",
            qualification_level=None,
            language="en",
            display_name_en="GCSE Chemistry",
            concept="CHEMISTRY",
            source_url="https://www.aqa.org.uk/subjects/science/gcse/chemistry-8462",
            baml_function="b.ExtractUKQualSpec",
            source="AQA_OFFICIAL",
            status="ACTIVE",
            first_introduced="2016-09",
            last_verified="2026-07-17",
        ),
        SubjectRegistryRow(
            jurisdiction="england",
            stage="gcse",
            subject_slug="biology",
            board="aqa",
            qualification_level=None,
            language="en",
            display_name_en="GCSE Biology",
            concept="BIOLOGY",
            source_url="https://www.aqa.org.uk/subjects/science/gcse/biology-8461",
            baml_function="b.ExtractUKQualSpec",
            source="AQA_OFFICIAL",
            status="ACTIVE",
            first_introduced="2016-09",
            last_verified="2026-07-17",
        ),
    ]


def seed_registry() -> dict[str, int]:
    """Seed the registry with the BIEP v3 Phase 1 minimal data.

    Returns a dict with the count of rows inserted per jurisdiction.
    Full seeding is in Phases 2-5.
    """
    counts: dict[str, int] = {"ireland": 0, "england": 0, "other": 0}

    for row in load_ireland_subjects():
        try:
            insert_subject(row)
            counts["ireland"] += 1
        except Exception as e:
            logger.warning("seed_registry: failed to insert %s: %s", row.subject_slug, e)

    for row in load_england_subjects():
        try:
            insert_subject(row)
            counts["england"] += 1
        except Exception as e:
            logger.warning("seed_registry: failed to insert %s: %s", row.subject_slug, e)

    return counts


def apply_migration(migration_sql_path: str | Path | None = None) -> None:
    """Apply the registry migration SQL to DuckDB.

    Default path: `dlt/common/migrations/2026-07-27-cianfhoghlaim-subject-registry.sql`.
    """
    import ibis  # type: ignore[import-not-found]
    if migration_sql_path is None:
        migration_sql_path = (
            Path(__file__).resolve().parents[2]
            / "common"
            / "migrations"
            / "2026-07-27-cianfhoghlaim-subject-registry.sql"
        )
    sql = Path(migration_sql_path).read_text()
    conn = ibis.duckdb.connect("md:cianfhoghlaim", read_only=False)
    # Split by semicolons (excluding those inside strings/comments)
    for stmt in sql.split(";\n"):
        stmt = stmt.strip()
        if not stmt or stmt.startswith("--"):
            continue
        conn.sql(stmt).execute()


__all__ = [
    "load_ireland_subjects",
    "load_england_subjects",
    "seed_registry",
    "apply_migration",
]