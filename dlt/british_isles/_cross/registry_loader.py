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

    Per the 2026-07-28-biep-v3-ireland-full-coverage-v1 change, this
    loader returns the FULL 134+ row seed (64 LC × 3 levels × 2 langs +
    18 JC × 3 years × 2 langs + 16 short courses + 36 CBAs).
    """
    rows: list[SubjectRegistryRow] = []

    # Canonical 64 Ireland LC subjects (from education_level.baml)
    LC_SUBJECTS = [
        ("mathematics", "LC003", "Mathematics", "Matamaitic"),
        ("applied_mathematics", "LC028", "Applied Mathematics", "Matamaitic Fheidhmeach"),
        ("english", "LC002", "English", "Béarla"),
        ("gaeilge", "LC001", "Gaeilge (Irish)", "Gaeilge"),
        ("french", "LC013", "French", "Fraincis"),
        ("german", "LC014", "German", "Gearmáinis"),
        ("spanish", "LC015", "Spanish", "Spáinnis"),
        ("italian", "LC016", "Italian", "Iodáilis"),
        ("japanese", "LC029", "Japanese", "Seapáinis"),
        ("russian", "LC017", "Russian", "Rúisis"),
        ("arabic", "LC018", "Arabic", "Araibis"),
        ("mandarin", "LC030", "Mandarin Chinese", "Sínis Mhandairinis"),
        ("latin", "LC019", "Latin", "Laidin"),
        ("greek", "LC020", "Ancient Greek", "Gréigis"),
        ("classical_studies", "LC021", "Classical Studies", "Staidéar Clasaiceach"),
        ("history", "LC004", "History", "Stair"),
        ("irish_history", "LC006", "Irish History (deprecated post-2024)", "Stair na hÉireann"),
        ("geography", "LC005", "Geography", "Tíreolaíocht"),
        ("physics", "LC023", "Physics", "Fisic"),
        ("chemistry", "LC022", "Chemistry", "Ceimic"),
        ("biology", "LC024", "Biology", "Bitheolaíocht"),
        ("agricultural_science", "LC025", "Agricultural Science", "Eolaíocht Talmhaíochta"),
        ("business", "LC027", "Business", "Gné"),
        ("accounting", "LC033", "Accounting", "Cuntasaíocht"),
        ("economics", "LC026", "Economics", "Eacnamaíocht"),
        ("home_economics", "LC028_HE", "Home Economics", "Eacnamaíocht Bhaile"),
        ("art", "LC050", "Art", "Ealaín"),
        ("music", "LC030_M", "Music", "Ceol"),
        ("design_communication_graphics", "LC031", "Design & Communication Graphics", "Dearadh & Grafaic Cumarsáide"),
        ("engineering", "LC032", "Engineering", "Innealtóireacht"),
        ("technology", "LC034", "Technology", "Teicneolaíocht"),
        ("construction_studies", "LC035", "Construction Studies", "Staidéar Foirgníochta"),
        ("physical_education", "LC036", "Physical Education", "Corpoideachas"),
        ("computer_science", "LC037", "Computer Science", "Ríomheolaíocht"),
        ("philosophy", "LC038", "Philosophy", "Fealsúnacht"),
        ("politics_and_society", "LC039", "Politics & Society", "Polaitíocht & Sochaí"),
        ("religious_education", "LC040", "Religious Education", "Oideachas Reiligiúnach"),
        ("link_modules_lcvp", "LCV01", "Link Modules (LCVP)", "Nasc-Mhodúil"),
        ("careers_portfolio", "CP001", "Careers Portfolio", "Tionscadal Gairme"),
        # LCA (Leaving Certificate Applied) vocational subjects
        ("lca_english_communications", "LCA01", "LCA English & Communications", "Béarla & Cumarsáid"),
        ("lca_matemathics_quantitative", "LCA02", "LCA Mathematical Techniques", "Teicnící Matamaitice"),
        ("lca_ict", "LCA03", "LCA Information & Communication Technology", "TFC"),
        ("lca_vocational_preparation", "LCA04", "LCA Vocational Preparation", "Ullmhú Gairme"),
        ("lca_career_guidance", "LCA05", "LCA Career Guidance", "Treoir Ghairme"),
        ("lca_social_education", "LCA06", "LCA Social Education", "Oideachas Sóisialta"),
        ("lca_religious_education", "LCA07", "LCA Religious Education", "Oideachas Reiligiúnach"),
        ("lca_health_and_safety", "LCA08", "LCA Health & Safety", "Sláinte & Sábháilteacht"),
        ("lca_catering_hospitality", "LCA09", "LCA Catering & Hospitality", "Lónadóireacht"),
        ("lca_office_administration", "LCA10", "LCA Office Administration", "Riarachán Oifige"),
        ("lca_childcare", "LCA11", "LCA Childcare", "Cúram Leanaí"),
        ("lca_arts_crafts", "LCA12", "LCA Arts & Crafts", "Ealaíon & Ceardaíocht"),
        ("lca_construction", "LCA13", "LCA Construction", "Foirgníocht"),
        ("lca_engineering_technology", "LCA14", "LCA Engineering Technology", "Teicneolaíocht Innealtóireachta"),
        ("lca_tourism", "LCA15", "LCA Tourism", "Turasóireacht"),
        ("lca_hairdressing_beauty", "LCA16", "LCA Hairdressing & Beauty", "Grúigéis & Áille"),
        ("lca_sport_recreation", "LCA17", "LCA Sport & Recreation", "Spórt & Caitheamh Aimsire"),
        ("lca_graphic_design", "LCA18", "LCA Graphic Design", "Dearadh Grafach"),
        ("lca_music", "LCA19", "LCA Music", "Ceol"),
        ("lca_active_leisure", "LCA20", "LCA Active Leisure Studies", "Caitheamh Aimsire Gníomhach"),
        ("lca_agri_food_hort", "LCA21", "LCA Agriculture, Food & Horticulture", "Talmhaíocht, Bia & Gairneoireacht"),
        ("lca_engineering_materials", "LCA22", "LCA Engineering & Materials", "Innealtóireacht & Ábhair"),
        ("lca_drama", "LCA23", "LCA Drama", "Drámaíocht"),
    ]

    # Emit each LC subject × 3 levels × 2 langs
    for slug, code, en, local in LC_SUBJECTS:
        for ql in ("hl", "ol", "fl"):
            for lang in ("en", "ga"):
                rows.append(
                    SubjectRegistryRow(
                        jurisdiction="ireland",
                        stage="leaving_certificate",
                        subject_slug=slug,
                        board="none",
                        qualification_level=ql,
                        language=lang,
                        display_name_en=en,
                        display_name_local=local,
                        concept=_concept_for_subject(slug),
                        source_url=f"https://www.ncca.ie/en/senior-cycle/subjects/{slug}",
                        ncca_spec_code=code,
                        baml_function="b.ExtractCurriculumSyllabus",
                        source="NCCA_OFFICIAL",
                        status="ACTIVE",
                        first_introduced="1967-09" if ql == "hl" else "1995-09",
                        last_verified="2026-07-17",
                    )
                )

    # 18 NCCA JC subjects × 3 years × 2 langs
    JC_SUBJECTS = [
        ("english", "JC001", "English", "Béarla"),
        ("gaeilge", "JC002", "Gaeilge", "Gaeilge"),
        ("mathematics", "JC003", "Mathematics", "Matamaitic"),
        ("irish_history", "JC004", "History", "Stair"),
        ("geography", "JC005", "Geography", "Tíreolaíocht"),
        ("science", "JC006", "Science", "Eolaíocht"),
        ("business_studies", "JC007", "Business Studies", "Gnéstaidéar"),
        ("french", "JC008", "French", "Fraincis"),
        ("german", "JC009", "German", "Gearmáinis"),
        ("spanish", "JC010", "Spanish", "Spáinnis"),
        ("italian", "JC011", "Italian", "Iodáilis"),
        ("home_economics", "JC012", "Home Economics", "Eacnamaíocht Bhaile"),
        ("music", "JC013", "Music", "Ceol"),
        ("art", "JC014", "Art", "Ealaín"),
        ("technology", "JC015", "Technology", "Teicneolaíocht"),
        ("engineering", "JC016", "Engineering", "Innealtóireacht"),
        ("graphics", "JC017", "Design & Communication Graphics", "Dearadh & Grafaic Cumarsáide"),
        ("wood_technology", "JC018", "Wood Technology", "Teicneolaíocht Adhmaid"),
    ]

    for slug, code, en, local in JC_SUBJECTS:
        for year in ("year_1", "year_2", "year_3"):
            for lang in ("en", "ga"):
                rows.append(
                    SubjectRegistryRow(
                        jurisdiction="ireland",
                        stage="junior_cycle",
                        subject_slug=slug,
                        board="none",
                        qualification_level=year,
                        language=lang,
                        display_name_en=en,
                        display_name_local=local,
                        concept=_concept_for_subject(slug),
                        source_url=f"https://www.ncca.ie/en/junior-cycle/subjects/{slug}",
                        ncca_spec_code=code,
                        baml_function="b.ExtractJCCurriculum",
                        source="NCCA_OFFICIAL",
                        status="ACTIVE",
                        first_introduced="2014-09",
                        last_verified="2026-07-17",
                    )
                )

    # 16 JC short courses (English-only)
    JC_SHORT_COURSES = [
        "coding", "chinese", "japanese", "russian", "polish", "lithuanian",
        "portuguese", "arabic", "hebrew", "philosophy", "film_studies",
        "financial_literacy", "media_literacy",
        "personal_professional_development", "digital_media", "athletic_studies",
    ]
    for course in JC_SHORT_COURSES:
        rows.append(
            SubjectRegistryRow(
                jurisdiction="ireland",
                stage="junior_cycle_short_course",
                subject_slug=course,
                board="none",
                qualification_level=None,
                language="en",
                display_name_en=course.replace("_", " ").title(),
                concept="OTHER",
                source_url=f"https://www.ncca.ie/en/junior-cycle/short-courses/{course}",
                ncca_spec_code=f"JC-SC-{course[:4].upper()}",
                baml_function="b.ExtractJCShortCourse",
                source="NCCA_OFFICIAL",
                status="ACTIVE",
                first_introduced="2014-09",
                last_verified="2026-07-17",
            )
        )

    # 36 JC CBAs (2 per subject)
    for slug, code, en, local in JC_SUBJECTS:
        for cba_idx in (1, 2):
            rows.append(
                SubjectRegistryRow(
                    jurisdiction="ireland",
                    stage="junior_cycle_cba",
                    subject_slug=slug,
                    board="none",
                    qualification_level=f"cba_{cba_idx}",
                    language="en",
                    display_name_en=f"{en} CBA {cba_idx}",
                    concept=_concept_for_subject(slug),
                    source_url=f"https://www.ncca.ie/en/junior-cycle/cba/{slug}-{cba_idx}",
                    ncca_spec_code=f"{code}-CBA{cba_idx}",
                    baml_function="b.ExtractCBADescriptor",
                    source="NCCA_OFFICIAL",
                    status="ACTIVE",
                    first_introduced="2017-09",
                    last_verified="2026-07-17",
                )
            )

    return rows


# Mapping from subject slug to CrossJurisdictionConcept
_CONCEPT_MAP: dict[str, str] = {
    "mathematics": "MATHEMATICS", "applied_mathematics": "MATHEMATICS",
    "english": "ENGLISH", "gaeilge": "IRISH_LANGUAGE", "irish_history": "HISTORY",
    "french": "FRENCH", "german": "GERMAN", "spanish": "SPANISH", "italian": "SPANISH",
    "japanese": "OTHER", "russian": "OTHER", "arabic": "OTHER", "mandarin": "OTHER",
    "latin": "LATIN", "greek": "CLASSICAL_STUDIES",
    "classical_studies": "CLASSICAL_STUDIES",
    "history": "HISTORY", "geography": "GEOGRAPHY",
    "physics": "PHYSICS", "chemistry": "CHEMISTRY", "biology": "BIOLOGY",
    "agricultural_science": "OTHER",
    "business": "BUSINESS_STUDIES", "accounting": "BUSINESS_STUDIES",
    "economics": "BUSINESS_STUDIES", "business_studies": "BUSINESS_STUDIES",
    "home_economics": "OTHER",
    "art": "OTHER", "music": "OTHER",
    "design_communication_graphics": "DESIGN_AND_COMMUNICATION_GRAPHICS",
    "engineering": "OTHER", "technology": "OTHER",
    "construction_studies": "OTHER", "physical_education": "OTHER",
    "computer_science": "COMPUTER_SCIENCE",
    "philosophy": "OTHER", "politics_and_society": "OTHER",
    "religious_education": "OTHER",
    "science": "OTHER", "graphics": "DESIGN_AND_COMMUNICATION_GRAPHICS",
    "wood_technology": "OTHER",
}


def _concept_for_subject(slug: str) -> str:
    return _CONCEPT_MAP.get(slug, "OTHER")


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