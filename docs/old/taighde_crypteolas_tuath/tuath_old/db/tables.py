"""
LanceDB table definitions for EduVision.

Provides vector database storage for:
- Syllabus page embeddings (ColPali)
- Curriculum concept embeddings
- Generated asset metadata and embeddings
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import lancedb
from lancedb.pydantic import LanceModel, Vector


# LanceDB Pydantic models for table schemas

class SyllabusPageModel(LanceModel):
    """LanceDB model for syllabus page embeddings."""
    id: str
    subject: str
    document_title: str
    page_number: int
    filename: str
    language: str

    # ColPali embedding (single vector per record)
    # For multi-vector, we store one record per patch
    embedding: Vector(128)
    patch_index: int = 0

    specification_version: str = "current"
    effective_from: Optional[str] = None
    created_at: str = ""
    extracted_text: Optional[str] = None
    page_image_path: str = ""


class CurriculumConceptModel(LanceModel):
    """LanceDB model for curriculum concepts."""
    id: str
    subject: str
    topic_name: str
    strand: Optional[str] = None

    title: str
    description: str
    keywords_json: str = "[]"  # JSON-encoded list

    # Sentence transformer embedding
    text_embedding: Vector(384)

    source_page_ids_json: str = "[]"
    learning_outcomes_json: str = "[]"
    visual_requirements_json: str = "[]"

    difficulty_level: str = "ordinary"
    created_at: str = ""
    updated_at: str = ""


class GeneratedAssetModel(LanceModel):
    """LanceDB model for generated educational assets."""
    id: str
    concept_id: str

    fibo_prompt_json: str
    style_medium: str
    seed: Optional[int] = None

    image_path: str

    # CLIP embedding for visual similarity search
    image_embedding: Vector(512)

    validation_score: float = 0.0
    scientific_accuracy: float = 0.0
    educational_clarity: float = 0.0
    concept_alignment: float = 0.0

    status: str = "draft"
    validation_issues_json: Optional[str] = None
    refinement_count: int = 0

    created_at: str = ""
    validated_at: Optional[str] = None


# Database connection management

_db_instance: Optional[lancedb.DBConnection] = None


def get_database(db_path: str = "data/lancedb") -> lancedb.DBConnection:
    """
    Get or create the LanceDB database connection.

    Args:
        db_path: Path to LanceDB database directory

    Returns:
        LanceDB connection instance
    """
    global _db_instance

    if _db_instance is None:
        # Ensure path exists
        Path(db_path).mkdir(parents=True, exist_ok=True)
        _db_instance = lancedb.connect(db_path)

    return _db_instance


def create_database(db_path: str = "data/lancedb") -> lancedb.DBConnection:
    """
    Initialize LanceDB database with all required tables.

    Creates tables if they don't exist:
    - syllabus_pages: ColPali embeddings for curriculum pages
    - curriculum_concepts: Extracted concepts with text embeddings
    - generated_assets: FIBO outputs with CLIP embeddings

    Args:
        db_path: Path to LanceDB database directory

    Returns:
        LanceDB connection instance
    """
    db = get_database(db_path)

    # Create tables if they don't exist
    existing_tables = db.table_names()

    if "syllabus_pages" not in existing_tables:
        # Create with sample data to establish schema
        db.create_table(
            "syllabus_pages",
            schema=SyllabusPageModel,
            mode="overwrite"
        )
        print("Created table: syllabus_pages")

    if "curriculum_concepts" not in existing_tables:
        db.create_table(
            "curriculum_concepts",
            schema=CurriculumConceptModel,
            mode="overwrite"
        )
        print("Created table: curriculum_concepts")

    if "generated_assets" not in existing_tables:
        db.create_table(
            "generated_assets",
            schema=GeneratedAssetModel,
            mode="overwrite"
        )
        print("Created table: generated_assets")

    return db


def add_syllabus_page(
    db: lancedb.DBConnection,
    page_id: str,
    subject: str,
    document_title: str,
    page_number: int,
    filename: str,
    language: str,
    embeddings: list[list[float]],
    page_image_path: str,
    specification_version: str = "current",
    effective_from: Optional[str] = None,
    extracted_text: Optional[str] = None,
) -> None:
    """
    Add a syllabus page with ColPali multi-vector embeddings.

    Each patch embedding is stored as a separate record.
    """
    table = db.open_table("syllabus_pages")
    now = datetime.now().isoformat()

    records = []
    for patch_idx, embedding in enumerate(embeddings):
        records.append({
            "id": f"{page_id}_patch_{patch_idx}",
            "subject": subject,
            "document_title": document_title,
            "page_number": page_number,
            "filename": filename,
            "language": language,
            "embedding": embedding,
            "patch_index": patch_idx,
            "specification_version": specification_version,
            "effective_from": effective_from,
            "created_at": now,
            "extracted_text": extracted_text,
            "page_image_path": page_image_path,
        })

    table.add(records)


def add_curriculum_concept(
    db: lancedb.DBConnection,
    concept_id: str,
    subject: str,
    topic_name: str,
    title: str,
    description: str,
    text_embedding: list[float],
    strand: Optional[str] = None,
    keywords: Optional[list[str]] = None,
    source_page_ids: Optional[list[str]] = None,
    learning_outcomes: Optional[list[dict]] = None,
    visual_requirements: Optional[list[dict]] = None,
    difficulty_level: str = "ordinary",
) -> None:
    """Add a curriculum concept with text embedding."""
    table = db.open_table("curriculum_concepts")
    now = datetime.now().isoformat()

    table.add([{
        "id": concept_id,
        "subject": subject,
        "topic_name": topic_name,
        "strand": strand,
        "title": title,
        "description": description,
        "keywords_json": json.dumps(keywords or []),
        "text_embedding": text_embedding,
        "source_page_ids_json": json.dumps(source_page_ids or []),
        "learning_outcomes_json": json.dumps(learning_outcomes or []),
        "visual_requirements_json": json.dumps(visual_requirements or []),
        "difficulty_level": difficulty_level,
        "created_at": now,
        "updated_at": now,
    }])


def add_generated_asset(
    db: lancedb.DBConnection,
    asset_id: str,
    concept_id: str,
    fibo_prompt_json: str,
    style_medium: str,
    image_path: str,
    image_embedding: list[float],
    seed: Optional[int] = None,
    validation_score: float = 0.0,
    scientific_accuracy: float = 0.0,
    educational_clarity: float = 0.0,
    concept_alignment: float = 0.0,
    status: str = "draft",
    validation_issues: Optional[list[str]] = None,
) -> None:
    """Add a generated educational asset with CLIP embedding."""
    table = db.open_table("generated_assets")
    now = datetime.now().isoformat()

    table.add([{
        "id": asset_id,
        "concept_id": concept_id,
        "fibo_prompt_json": fibo_prompt_json,
        "style_medium": style_medium,
        "seed": seed,
        "image_path": image_path,
        "image_embedding": image_embedding,
        "validation_score": validation_score,
        "scientific_accuracy": scientific_accuracy,
        "educational_clarity": educational_clarity,
        "concept_alignment": concept_alignment,
        "status": status,
        "validation_issues_json": json.dumps(validation_issues or []),
        "refinement_count": 0,
        "created_at": now,
        "validated_at": None,
    }])


def search_syllabus_pages(
    db: lancedb.DBConnection,
    query_embedding: list[list[float]],
    subject: Optional[str] = None,
    limit: int = 10,
) -> list[dict]:
    """
    Search syllabus pages using ColPali query embedding.

    Uses MaxSim scoring for multi-vector queries.
    """
    table = db.open_table("syllabus_pages")

    # For ColPali, we search with the multi-vector query
    # and aggregate results by page
    results = table.search(query_embedding[0]).limit(limit * 5)

    if subject:
        results = results.where(f"subject = '{subject}'")

    df = results.to_pandas()

    # Aggregate by page (taking max score per page)
    if len(df) > 0:
        aggregated = df.groupby(["id", "page_number", "filename"]).agg({
            "_distance": "min",  # Best patch match
            "subject": "first",
            "document_title": "first",
            "page_image_path": "first",
        }).reset_index()

        aggregated = aggregated.sort_values("_distance").head(limit)
        return aggregated.to_dict("records")

    return []


def search_concepts(
    db: lancedb.DBConnection,
    query_embedding: list[float],
    subject: Optional[str] = None,
    limit: int = 10,
) -> list[dict]:
    """Search curriculum concepts by text embedding similarity."""
    table = db.open_table("curriculum_concepts")

    results = table.search(query_embedding).limit(limit)

    if subject:
        results = results.where(f"subject = '{subject}'")

    return results.to_pandas().to_dict("records")


def search_assets(
    db: lancedb.DBConnection,
    query_embedding: list[float],
    subject: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 10,
) -> list[dict]:
    """Search generated assets by image embedding similarity."""
    table = db.open_table("generated_assets")

    results = table.search(query_embedding).limit(limit)

    filters = []
    if subject:
        filters.append(f"subject = '{subject}'")
    if status:
        filters.append(f"status = '{status}'")

    if filters:
        results = results.where(" AND ".join(filters))

    return results.to_pandas().to_dict("records")
