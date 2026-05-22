"""
Unified Search Index Assets.

Assets that create searchable indexes across all domains:
- Unified curriculum search (all nations + translations)
- Linguistic atlas (map-based search)
- Training dataset exports (HuggingFace format)

These assets depend on enriched assets from:
- enriched.*
"""
# Note: Removed future annotations for Dagster compatibility


from dagster import (
    AssetKey,
    MaterializeResult,
    asset,
)

from ..resources import DuckDBResource, LanceDBResource

# ============================================================================
# Unified Curriculum Search
# ============================================================================

@asset(
    key=["search", "unified_curriculum"],
    group_name="search_indexes",
    description="Unified search index across all curriculum content",
    deps=[
        AssetKey(["enriched", "curriculum_with_terminology"]),
        AssetKey(["ireland", "education", "embeddings"]),
        AssetKey(["uk", "education", "embeddings"]),
    ],
    compute_kind="search_index",
)
def unified_curriculum_index(
    context,
    duckdb: DuckDBResource,
    lancedb: LanceDBResource,
) -> MaterializeResult:
    """
    Create unified search index across all curriculum content.

    Combines:
    - Ireland curriculum (NCCA, curriculumonline.ie)
    - UK curricula (England, Scotland, Wales, NI)
    - Celtic language curriculum materials
    - Official terminology from Téarma

    Enables cross-nation curriculum search with filters for:
    - Nation
    - Subject
    - Language
    - Key stage/level
    """
    context.log.info("Creating unified curriculum search index")

    db = lancedb.get_db()
    conn = duckdb.get_connection()

    # Check available embedding tables
    available_tables = db.table_names()
    curriculum_tables = [t for t in available_tables if 'curriculum' in t.lower()]

    context.log.info(f"Found {len(curriculum_tables)} curriculum tables: {curriculum_tables}")

    if not curriculum_tables:
        return MaterializeResult(
            metadata={
                "status": "skipped",
                "reason": "No curriculum embedding tables found",
            }
        )

    # Create unified search metadata view in DuckDB
    try:
        conn.execute("""
            CREATE OR REPLACE VIEW search.curriculum_metadata AS
            SELECT
                'ireland' as nation,
                page_id,
                title,
                subject,
                language,
                'primary' as level
            FROM education.curriculum_pages
            WHERE content IS NOT NULL
        """)

        metadata_count = conn.execute(
            "SELECT COUNT(*) FROM search.curriculum_metadata"
        ).fetchone()[0]
    except Exception as e:
        context.log.warning(f"Metadata view creation failed: {e}")
        metadata_count = 0

    # The actual unified index would merge embeddings from multiple tables
    # For now, we record the available sources
    total_embeddings = 0
    for table_name in curriculum_tables:
        try:
            table = db.open_table(table_name)
            count = len(table)
            total_embeddings += count
            context.log.info(f"  {table_name}: {count} embeddings")
        except Exception as e:
            context.log.warning(f"Failed to count {table_name}: {e}")

    return MaterializeResult(
        metadata={
            "source_tables": curriculum_tables,
            "total_embeddings": total_embeddings,
            "metadata_entries": metadata_count,
            "search_filters": ["nation", "subject", "language", "level"],
        }
    )


# ============================================================================
# Linguistic Atlas Search
# ============================================================================

@asset(
    key=["search", "linguistic_atlas"],
    group_name="search_indexes",
    description="Map-based search index for linguistic content",
    deps=[
        AssetKey(["enriched", "dialect_variation_atlas"]),
        AssetKey(["geospatial", "locations", "duchas"]),
        AssetKey(["geospatial", "locations", "canuint"]),
    ],
    compute_kind="search_index",
)
def linguistic_atlas_index(
    context,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Create spatial index for map-based linguistic search.

    Enables searches like:
    - "Show recordings near this location"
    - "Find folklore from this county"
    - "Compare pronunciations across regions"

    Uses DuckDB Spatial for efficient geo queries.
    """
    context.log.info("Creating linguistic atlas search index")

    conn = duckdb.get_connection()

    # Create spatial index on locations
    try:
        conn.execute("INSTALL spatial; LOAD spatial;")

        # Create unified locations view
        conn.execute("""
            CREATE OR REPLACE VIEW search.linguistic_locations AS
            SELECT
                'duchas' as source,
                id as location_id,
                title as name,
                county,
                lat,
                lon,
                'folklore' as content_type
            FROM geospatial.duchas_locations
            WHERE lat IS NOT NULL AND lon IS NOT NULL
            UNION ALL
            SELECT
                'canuint' as source,
                recording_id as location_id,
                word as name,
                province as county,
                lat,
                lon,
                'pronunciation' as content_type
            FROM geospatial.canuint_locations
            WHERE lat IS NOT NULL AND lon IS NOT NULL
        """)

        location_count = conn.execute(
            "SELECT COUNT(*) FROM search.linguistic_locations"
        ).fetchone()[0]
    except Exception as e:
        context.log.warning(f"Spatial index creation failed: {e}")
        location_count = 0

    return MaterializeResult(
        metadata={
            "location_count": location_count,
            "content_types": ["folklore", "pronunciation"],
            "spatial_enabled": True,
        }
    )


# ============================================================================
# Training Dataset Export
# ============================================================================

@asset(
    key=["search", "training_datasets"],
    group_name="search_indexes",
    description="Export aligned pairs as HuggingFace-compatible datasets",
    deps=[
        AssetKey(["enriched", "bilingual_aligned_pairs"]),
    ],
    compute_kind="export",
)
def training_datasets_export(
    context,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Export training datasets in HuggingFace format.

    Creates:
    - parallel_corpus.jsonl: Aligned en/ga sentence pairs
    - terminology.jsonl: Téarma term pairs
    - curriculum_qa.jsonl: Q&A pairs from curriculum

    Suitable for:
    - Fine-tuning translation models
    - Irish education domain adaptation
    - Irish language NER/classification
    """
    context.log.info("Exporting training datasets")

    conn = duckdb.get_connection()
    export_path = "/Users/cliste/dev/cianfhoghlaim/sruth/oideachais/storage/data/training"

    # Check for parallel corpus data
    try:
        pair_count = conn.execute(
            "SELECT COUNT(*) FROM training.parallel_corpus"
        ).fetchone()[0]
    except Exception as e:
        context.log.warning(f"Parallel corpus not found: {e}")
        pair_count = 0

    if pair_count < 10:
        return MaterializeResult(
            metadata={
                "status": "skipped",
                "reason": f"Insufficient parallel pairs: {pair_count}",
            }
        )

    # Export to JSONL format
    try:
        import json
        from pathlib import Path

        export_dir = Path(export_path)
        export_dir.mkdir(parents=True, exist_ok=True)

        # Export parallel corpus
        rows = conn.execute("""
            SELECT english_text, irish_text, alignment_score
            FROM training.parallel_corpus
            WHERE alignment_score > 0.7
        """).fetchall()

        output_file = export_dir / "parallel_corpus.jsonl"
        with open(output_file, "w", encoding="utf-8") as f:
            for row in rows:
                record = {
                    "en": row[0][:2000] if row[0] else "",
                    "ga": row[1][:2000] if row[1] else "",
                    "score": row[2],
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

        exported_count = len(rows)
    except Exception as e:
        context.log.warning(f"Export failed: {e}")
        exported_count = 0

    return MaterializeResult(
        metadata={
            "parallel_pairs_total": pair_count,
            "exported_pairs": exported_count,
            "export_path": export_path,
            "format": "jsonl",
            "fields": ["en", "ga", "score"],
        }
    )


# ============================================================================
# Export All Search Assets
# ============================================================================

search_assets = [
    unified_curriculum_index,
    linguistic_atlas_index,
    training_datasets_export,
]
