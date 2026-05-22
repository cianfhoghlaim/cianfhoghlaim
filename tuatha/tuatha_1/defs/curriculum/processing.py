"""
Dagster assets for curriculum processing.

Assets for indexing and extracting curriculum concepts:
- indexed_pages: ColPali embeddings for syllabus pages
- extracted_concepts: Structured concepts from BAML extraction
"""

from pathlib import Path

from dagster import (
    asset,
    AssetExecutionContext,
    MaterializeResult,
    MetadataValue,
)

from .resources import CocoIndexResource, LanceDBResource, ColPaliResource


@asset(
    group_name="curriculum",
    deps=["specification_pdfs"],
    description="Index PDF pages with ColPali visual embeddings",
    compute_kind="cocoindex",
)
def indexed_pages(
    context: AssetExecutionContext,
    cocoindex_resource: CocoIndexResource,
    lancedb_resource: LanceDBResource,
) -> MaterializeResult:
    """
    Process curriculum PDFs through CocoIndex indexing flow.

    Pipeline:
    1. Convert PDF pages to images (300 DPI)
    2. Generate ColPali multi-vector embeddings
    3. Export to LanceDB syllabus_pages table

    This enables visual semantic search over curriculum documents.
    """
    context.log.info("Running curriculum document indexing flow...")

    # Run the CocoIndex flow
    result = cocoindex_resource.run_curriculum_indexing()

    # Get statistics from LanceDB
    stats = {"pages_indexed": 0, "subjects": []}

    if lancedb_resource.table_exists("syllabus_pages"):
        table = lancedb_resource.get_table("syllabus_pages")
        df = table.to_pandas()

        if len(df) > 0:
            # Count unique pages (not patches)
            unique_pages = df.groupby(["filename", "page_number"]).size()
            stats["pages_indexed"] = len(unique_pages)
            stats["subjects"] = df["subject"].unique().tolist()

    context.log.info(f"Indexed {stats['pages_indexed']} pages")

    return MaterializeResult(
        metadata={
            "pages_indexed": MetadataValue.int(stats["pages_indexed"]),
            "subjects": MetadataValue.json(stats["subjects"]),
            "flow_result": MetadataValue.text(str(result)),
            "table_name": MetadataValue.text("syllabus_pages"),
        }
    )


@asset(
    group_name="curriculum",
    deps=["indexed_pages"],
    description="Extract curriculum concepts using BAML + Qwen3-VL",
    compute_kind="baml",
)
def extracted_concepts(
    context: AssetExecutionContext,
    cocoindex_resource: CocoIndexResource,
    lancedb_resource: LanceDBResource,
) -> MaterializeResult:
    """
    Extract structured curriculum concepts from indexed pages.

    Uses BAML schemas with Qwen3-VL to extract:
    - Topic hierarchies
    - Learning outcomes
    - Visual asset requirements
    - Keywords for search

    Results are stored in LanceDB curriculum_concepts table.
    """
    context.log.info("Running concept extraction flow...")

    # Run the CocoIndex flow
    result = cocoindex_resource.run_concept_extraction()

    # Get statistics from LanceDB
    stats = {
        "concepts_extracted": 0,
        "by_subject": {},
        "by_difficulty": {},
    }

    if lancedb_resource.table_exists("curriculum_concepts"):
        table = lancedb_resource.get_table("curriculum_concepts")
        df = table.to_pandas()

        if len(df) > 0:
            stats["concepts_extracted"] = len(df)
            stats["by_subject"] = df["subject"].value_counts().to_dict()
            stats["by_difficulty"] = df["difficulty_level"].value_counts().to_dict()

    context.log.info(f"Extracted {stats['concepts_extracted']} concepts")

    return MaterializeResult(
        metadata={
            "concepts_extracted": MetadataValue.int(stats["concepts_extracted"]),
            "by_subject": MetadataValue.json(stats["by_subject"]),
            "by_difficulty": MetadataValue.json(stats["by_difficulty"]),
            "flow_result": MetadataValue.text(str(result)),
            "table_name": MetadataValue.text("curriculum_concepts"),
        }
    )


@asset(
    group_name="curriculum",
    deps=["extracted_concepts"],
    description="Concepts with visual requirements ready for generation",
    compute_kind="python",
)
def visualizable_concepts(
    context: AssetExecutionContext,
    lancedb_resource: LanceDBResource,
) -> MaterializeResult:
    """
    Filter concepts that have visual requirements for asset generation.

    Returns concepts that:
    - Have at least one visual requirement defined
    - Are not marked as already generated
    - Match specified difficulty levels
    """
    import json

    if not lancedb_resource.table_exists("curriculum_concepts"):
        context.log.warning("curriculum_concepts table not found")
        return MaterializeResult(
            metadata={
                "visualizable_count": MetadataValue.int(0),
            }
        )

    table = lancedb_resource.get_table("curriculum_concepts")
    df = table.to_pandas()

    # Filter concepts with visual requirements
    visualizable = []
    for _, row in df.iterrows():
        visual_reqs = json.loads(row.get("visual_requirements_json", "[]"))
        if visual_reqs:
            visualizable.append({
                "id": row["id"],
                "subject": row["subject"],
                "topic": row["topic_name"],
                "title": row["title"],
                "num_visuals_needed": len(visual_reqs),
            })

    # Group by subject
    by_subject = {}
    for concept in visualizable:
        subject = concept["subject"]
        if subject not in by_subject:
            by_subject[subject] = 0
        by_subject[subject] += 1

    context.log.info(f"Found {len(visualizable)} concepts ready for visualization")

    return MaterializeResult(
        metadata={
            "visualizable_count": MetadataValue.int(len(visualizable)),
            "by_subject": MetadataValue.json(by_subject),
            "sample_concepts": MetadataValue.json(visualizable[:5]),
        }
    )
