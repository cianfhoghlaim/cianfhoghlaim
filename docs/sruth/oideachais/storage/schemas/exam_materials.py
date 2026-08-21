"""
SEC Exam Materials Schema for DuckLake.

Defines the schema for storing SEC (State Examinations Commission)
exam materials scraped from examinations.ie.

Table: exam_materials
- Primary key: Composite of subject, year, material_type, pdf_url
- Supports both Leaving Certificate and Junior Cycle
- Tracks scraper method for comparison (stagehand vs cdp)

Usage:
    from sruth.oideachais.storage.schemas.exam_materials import (
        EXAM_MATERIALS_SCHEMA,
        init_exam_materials_schema,
    )

    # Initialize schema in DuckLake
    init_exam_materials_schema(ducklake_client)
"""

from typing import Any

# ============================================================================
# Schema Definition
# ============================================================================

EXAM_MATERIALS_SCHEMA = {
    # Primary identifier
    "id": "VARCHAR",  # Composite: {subject}_{year}_{level}_{material_type}_{hash}
    # Core metadata
    "subject": "VARCHAR",  # Subject slug (e.g., "mathematics", "english", "gaeilge")
    "year": "INTEGER",  # Examination year
    "level": "VARCHAR",  # "leaving_certificate" or "junior_cycle"
    # Paper details
    "material_type": "VARCHAR",  # "paper", "marking_scheme", "examiner_report", "aural"
    "exam_level": "VARCHAR",  # "Higher", "Ordinary", "Foundation", "Common"
    "paper_number": "INTEGER",  # 1 or 2 (NULL if not applicable)
    "language": "VARCHAR",  # "en", "ga", or "bilingual"
    # Content references
    "title": "VARCHAR",  # Document title from link text
    "pdf_url": "VARCHAR",  # Direct URL to PDF (primary dedupe key)
    "s3_key": "VARCHAR",  # Storage location in Garage (when downloaded)
    "file_size_bytes": "BIGINT",  # PDF file size (when downloaded)
    # Metadata
    "content_hash": "VARCHAR",  # SHA256 hash of URL for deduplication
    "scraped_at": "TIMESTAMP",  # When record was scraped
    "scraper_method": "VARCHAR",  # "stagehand" or "cdp" for comparison
    "source_url": "VARCHAR",  # URL of the archive results page
}

# Schema name in DuckLake
EXAM_MATERIALS_SCHEMA_NAME = "examinations"
EXAM_MATERIALS_TABLE_NAME = "exam_materials"

# All Leaving Certificate subjects (from examinations.ie)
LEAVING_CERT_SUBJECTS = [
    "accounting",
    "agricultural-science",
    "applied-mathematics",
    "arabic",
    "art",
    "biology",
    "business",
    "chemistry",
    "classical-studies",
    "computer-science",
    "construction-studies",
    "design-and-communication-graphics",
    "economics",
    "engineering",
    "english",
    "french",
    "gaeilge",
    "geography",
    "german",
    "history",
    "home-economics",
    "italian",
    "japanese",
    "latin",
    "mathematics",
    "music",
    "physical-education",
    "physics",
    "physics-and-chemistry",
    "politics-and-society",
    "religious-education",
    "spanish",
    "technology",
]

# Junior Cycle subjects
JUNIOR_CYCLE_SUBJECTS = [
    "applied-technology",
    "business-studies",
    "classics",
    "engineering",
    "english",
    "gaeilge",
    "geography",
    "graphics",
    "history",
    "home-economics",
    "mathematics",
    "modern-foreign-languages",
    "music",
    "physical-education",
    "religious-education",
    "science",
    "visual-art",
    "wood-technology",
]

# Valid material types
MATERIAL_TYPES = [
    "paper",
    "marking_scheme",
    "examiner_report",
    "aural",
    "coursework",
    "practical",
]

# Valid exam levels
EXAM_LEVELS = [
    "Higher",
    "Ordinary",
    "Foundation",
    "Common",
]


# ============================================================================
# Schema Initialization
# ============================================================================


def init_exam_materials_schema(ducklake_client) -> None:
    """
    Initialize exam materials schema in DuckLake.

    Creates the 'examinations' schema and 'exam_materials' table.

    Args:
        ducklake_client: DuckLakeClient instance
    """
    # Create schema
    ducklake_client.create_schema(EXAM_MATERIALS_SCHEMA_NAME)

    # Create table
    ducklake_client.create_table(
        table_name=EXAM_MATERIALS_TABLE_NAME,
        schema=EXAM_MATERIALS_SCHEMA_NAME,
        columns=EXAM_MATERIALS_SCHEMA,
    )


def exam_material_from_dict(data: dict[str, Any]) -> dict[str, Any]:
    """
    Convert scraper output to DuckLake record format.

    Adds the composite ID and normalizes field values.

    Args:
        data: Raw exam material data from scraper

    Returns:
        Normalized record for DuckLake insertion
    """
    from datetime import datetime
    import hashlib

    subject = data.get("subject", "")
    year = data.get("year", 0)
    level = data.get("level", "")
    material_type = data.get("material_type", "")
    pdf_url = data.get("pdf_url", "")

    # Generate composite ID
    id_hash = hashlib.sha256(pdf_url.encode()).hexdigest()[:16]
    record_id = f"{subject}_{year}_{level}_{material_type}_{id_hash}"

    return {
        "id": record_id,
        "subject": subject,
        "year": year,
        "level": level,
        "material_type": material_type,
        "exam_level": data.get("exam_level"),
        "paper_number": data.get("paper_number"),
        "language": data.get("language", "en"),
        "title": data.get("title"),
        "pdf_url": pdf_url,
        "s3_key": data.get("s3_key"),
        "file_size_bytes": data.get("file_size_bytes"),
        "content_hash": data.get("content_hash", id_hash),
        "scraped_at": data.get("scraped_at", datetime.utcnow().isoformat()),
        "scraper_method": data.get("scraper_method", "stagehand"),
        "source_url": data.get("source_url", "https://www.examinations.ie/exammaterialarchive/"),
    }


def validate_exam_material(record: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate an exam material record.

    Args:
        record: Record to validate

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Required fields
    required_fields = ["subject", "year", "level", "material_type", "pdf_url"]
    for field in required_fields:
        if not record.get(field):
            errors.append(f"Missing required field: {field}")

    # Validate year
    year = record.get("year")
    if year and not (2000 <= year <= 2100):
        errors.append(f"Invalid year: {year}")

    # Validate level
    level = record.get("level")
    if level and level not in ["leaving_certificate", "junior_cycle"]:
        errors.append(f"Invalid level: {level}")

    # Validate material_type
    material_type = record.get("material_type")
    if material_type and material_type not in MATERIAL_TYPES:
        errors.append(f"Invalid material_type: {material_type}")

    # Validate exam_level
    exam_level = record.get("exam_level")
    if exam_level and exam_level not in EXAM_LEVELS:
        errors.append(f"Invalid exam_level: {exam_level}")

    # Validate language
    language = record.get("language")
    if language and language not in ["en", "ga", "bilingual"]:
        errors.append(f"Invalid language: {language}")

    return len(errors) == 0, errors


__all__ = [
    "EXAM_MATERIALS_SCHEMA",
    "EXAM_MATERIALS_SCHEMA_NAME",
    "EXAM_MATERIALS_TABLE_NAME",
    "LEAVING_CERT_SUBJECTS",
    "JUNIOR_CYCLE_SUBJECTS",
    "MATERIAL_TYPES",
    "EXAM_LEVELS",
    "init_exam_materials_schema",
    "exam_material_from_dict",
    "validate_exam_material",
]
