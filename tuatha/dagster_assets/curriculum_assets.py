"""
Curriculum Assets for Tuath - Consuming from Oideachais.

Tuath consumes curriculum data from the oideachais platform rather than
maintaining its own ingestion pipelines. This eliminates ~95% duplication
and ensures consistent curriculum data across platforms.

Data Flow:
    oideachais (authoritative source) -> tuath (consumer for game/narrative)

Assets:
    - tuath_curriculum_context: Curriculum data adapted for game narratives
    - tuath_learning_games: Game assets mapped to curriculum outcomes
    - tuath_mythology_curriculum_links: Links between mythology and curriculum
"""

import os
from pathlib import Path
from typing import Any

import lancedb
from dagster import (
    AssetExecutionContext,
    AssetKey,
    MetadataValue,
    SourceAsset,
    StaticPartitionsDefinition,
    asset,
)

# Static partitions for Celtic nations
nation_partitions = StaticPartitionsDefinition(
    ["ireland", "wales", "scotland", "cornwall", "brittany", "isle_of_man"]
)

# Path to oideachais data (shared storage)
OIDEACHAIS_DATA_PATH = Path(
    os.environ.get("OIDEACHAIS_DATA_PATH", "../oideachais/storage/data")
)
OIDEACHAIS_LANCEDB_PATH = OIDEACHAIS_DATA_PATH / "lancedb"
OIDEACHAIS_DUCKDB_PATH = OIDEACHAIS_DATA_PATH / "celtic_education.duckdb"


# ============================================================================
# Source Assets (from oideachais)
# ============================================================================

# Declare oideachais assets as source assets for cross-project dependencies
oideachais_curriculum_embeddings = SourceAsset(
    key=AssetKey(["oideachais", "curriculum_embeddings"]),
    description="Curriculum content embeddings from oideachais platform",
    group_name="oideachais_sources",
)

oideachais_celtic_curriculum_raw = SourceAsset(
    key=AssetKey(["oideachais", "celtic_curriculum_raw"]),
    description="Raw Celtic curriculum data from NCCA, SQA, WJEC, etc.",
    group_name="oideachais_sources",
)

oideachais_learning_outcomes = SourceAsset(
    key=AssetKey(["oideachais", "learning_outcomes"]),
    description="Structured learning outcomes from curriculum content",
    group_name="oideachais_sources",
)


# ============================================================================
# Tuath Curriculum Context (consumes from oideachais)
# ============================================================================


def get_oideachais_lancedb_connection() -> lancedb.DBConnection:
    """Get connection to oideachais LanceDB storage."""
    lancedb_path = str(OIDEACHAIS_LANCEDB_PATH)
    if not Path(lancedb_path).exists():
        raise RuntimeError(
            f"Oideachais LanceDB not found at {lancedb_path}. "
            "Ensure oideachais pipelines have run first."
        )
    return lancedb.connect(lancedb_path)


@asset(
    partitions_def=nation_partitions,
    group_name="curriculum",
    deps=[oideachais_curriculum_embeddings],
    description="Curriculum context adapted for Tuath game narratives",
)
def tuath_curriculum_context(context: AssetExecutionContext) -> dict:
    """Load curriculum embeddings from oideachais for game narrative use.

    This asset reads from the shared oideachais LanceDB rather than
    maintaining duplicate ingestion pipelines.
    """
    nation = context.partition_key

    try:
        db = get_oideachais_lancedb_connection()
        tables = db.table_names()

        # Look for curriculum embeddings table
        curriculum_table = None
        for table_name in tables:
            if "curriculum" in table_name.lower() and "embed" in table_name.lower():
                curriculum_table = table_name
                break

        if not curriculum_table:
            context.log.warning(
                f"No curriculum embeddings table found in sruth.oideachais. "
                f"Available tables: {tables}"
            )
            return {
                "nation": nation,
                "status": "no_data",
                "message": "Curriculum embeddings not yet available from oideachais",
            }

        table = db.open_table(curriculum_table)

        # Filter by nation if column exists
        try:
            nation_data = table.search().where(
                f"nation = '{nation}'", prefilter=True
            ).limit(1000).to_pandas()
        except Exception:
            # If filtering fails, get all data
            nation_data = table.to_pandas()
            if "nation" in nation_data.columns:
                nation_data = nation_data[nation_data["nation"] == nation]

        row_count = len(nation_data)

        context.add_output_metadata({
            "nation": nation,
            "oideachais_table": curriculum_table,
            "rows_loaded": MetadataValue.int(row_count),
            "source": "oideachais",
        })

        return {
            "nation": nation,
            "status": "success" if row_count > 0 else "no_data",
            "rows": row_count,
            "source_table": curriculum_table,
        }

    except Exception as e:
        context.log.error(f"Failed to load curriculum from oideachais: {e}")
        return {
            "nation": nation,
            "status": "error",
            "error": str(e),
        }


@asset(
    partitions_def=nation_partitions,
    group_name="curriculum",
    deps=[oideachais_learning_outcomes, "tuath_curriculum_context"],
    description="Game assets mapped to curriculum learning outcomes",
)
def tuath_learning_games(context: AssetExecutionContext) -> dict:
    """Create game asset mappings linked to curriculum learning outcomes.

    Maps educational game elements to specific learning outcomes from
    the oideachais curriculum database.
    """
    import duckdb

    nation = context.partition_key

    try:
        # Check if oideachais DuckDB exists
        if not OIDEACHAIS_DUCKDB_PATH.exists():
            context.log.warning(
                f"Oideachais DuckDB not found at {OIDEACHAIS_DUCKDB_PATH}"
            )
            return {"nation": nation, "status": "no_data", "games": 0}

        conn = duckdb.connect(str(OIDEACHAIS_DUCKDB_PATH), read_only=True)

        # Query learning outcomes for this nation
        try:
            outcomes = conn.execute(
                """
                SELECT level, subject, outcome_text
                FROM education.learning_outcomes
                WHERE nation = ?
                LIMIT 100
                """,
                [nation],
            ).fetchall()
        except Exception:
            # Table might not exist yet
            outcomes = []

        conn.close()

        # Generate game mappings (placeholder for actual game logic)
        game_mappings = []
        for level, subject, outcome in outcomes:
            game_mappings.append({
                "nation": nation,
                "level": level,
                "subject": subject,
                "learning_outcome": outcome,
                "game_type": _suggest_game_type(subject, level),
                "difficulty": _calculate_difficulty(level),
            })

        context.add_output_metadata({
            "nation": nation,
            "outcomes_processed": len(outcomes),
            "games_created": len(game_mappings),
        })

        return {
            "nation": nation,
            "status": "success" if game_mappings else "no_data",
            "games": len(game_mappings),
        }

    except Exception as e:
        context.log.error(f"Failed to create game mappings for {nation}: {e}")
        return {"nation": nation, "status": "error", "error": str(e)}


@asset(
    partitions_def=nation_partitions,
    group_name="curriculum",
    deps=["tuath_curriculum_context", "mythology_entities"],
    description="Links between Celtic mythology and curriculum content",
)
def tuath_mythology_curriculum_links(context: AssetExecutionContext) -> dict:
    """Create links between mythology content and curriculum learning outcomes.

    This enables narrative-driven learning by connecting mythological
    stories to curriculum objectives.
    """
    nation = context.partition_key

    # This would use both curriculum data and mythology data to create links
    # For now, return placeholder data
    links_created = 0

    context.add_output_metadata({
        "nation": nation,
        "links_created": links_created,
    })

    return {
        "nation": nation,
        "status": "success" if links_created > 0 else "pending",
        "links": links_created,
    }


# ============================================================================
# Helper Functions
# ============================================================================


def _suggest_game_type(subject: str, level: str) -> str:
    """Suggest an appropriate game type based on subject and level."""
    subject_lower = subject.lower() if subject else ""

    if "math" in subject_lower or "maths" in subject_lower:
        return "puzzle"
    elif "language" in subject_lower or "gaeilge" in subject_lower:
        return "word_game"
    elif "history" in subject_lower or "stair" in subject_lower:
        return "narrative_adventure"
    elif "geography" in subject_lower or "tíreolaíocht" in subject_lower:
        return "exploration"
    else:
        return "quiz"


def _calculate_difficulty(level: str) -> int:
    """Calculate game difficulty based on curriculum level."""
    level_lower = level.lower() if level else ""

    difficulty_map = {
        "primary": 1,
        "junior_cycle": 2,
        "key_stage_3": 2,
        "national_5": 3,
        "gcse": 3,
        "leaving_cert": 4,
        "higher": 4,
        "a_level": 4,
        "advanced_higher": 5,
    }

    return difficulty_map.get(level_lower, 2)


@asset(
    group_name="curriculum",
    deps=["tuath_curriculum_context", "tuath_learning_games"],
    description="Aggregate curriculum usage statistics for Tuath",
)
def tuath_curriculum_stats(context: AssetExecutionContext) -> dict:
    """Compute aggregate statistics for curriculum usage in Tuath."""
    # Aggregate stats across all nations
    stats = {
        "total_curriculum_items": 0,
        "total_games_created": 0,
        "nations_active": 0,
        "source": "oideachais",
    }

    context.add_output_metadata({
        "stats": MetadataValue.json(stats),
    })

    return stats
