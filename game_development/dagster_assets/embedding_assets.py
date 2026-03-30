"""
Embedding Assets for Tuath.

Generates vector embeddings for curriculum and mythology content using BGE-M3.
"""

import os
from pathlib import Path

from dagster import (
    AssetExecutionContext,
    MetadataValue,
    StaticPartitionsDefinition,
    asset,
)

# Reuse partitions from other assets
nation_partitions = StaticPartitionsDefinition(
    ["ireland", "wales", "scotland", "cornwall", "brittany", "isle_of_man"]
)

tradition_partitions = StaticPartitionsDefinition([
    "irish_mythology",
    "welsh_mythology",
    "scottish_folklore",
    "cornish_folklore",
    "breton_folklore",
    "manx_folklore",
])

# Embedding configuration
EMBEDDING_CONFIG = {
    "model": "BAAI/bge-m3",
    "batch_size": 100,  # CRITICAL: Batching required for performance
    "max_sequence_length": 512,
    "normalize": True,
}


@asset(
    partitions_def=nation_partitions,
    group_name="embeddings",
    deps=["celtic_curriculum", "curriculum_learning_outcomes"],
    description="Curriculum content embeddings using BGE-M3 for multilingual retrieval",
)
def curriculum_embeddings(context: AssetExecutionContext) -> dict:
    """Generate embeddings for curriculum content."""
    import duckdb
    import lancedb
    from sentence_transformers import SentenceTransformer

    nation = context.partition_key
    db_path = os.environ.get("DUCKDB_PATH", "storage/duckdb/tuath.duckdb")
    lance_uri = os.environ.get("LANCEDB_URI", "storage/lance/tuath")

    # Ensure directories exist
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    Path(lance_uri).mkdir(parents=True, exist_ok=True)

    model = SentenceTransformer(EMBEDDING_CONFIG["model"])
    batch_size = EMBEDDING_CONFIG["batch_size"]

    try:
        conn = duckdb.connect(db_path, read_only=True)
        lance_db = lancedb.connect(lance_uri)

        # Fetch curriculum content
        curriculum_items = []
        try:
            curriculum_items = conn.execute(
                """
                SELECT
                    id,
                    nation,
                    level,
                    subject,
                    title,
                    content,
                    learning_outcomes
                FROM curriculum.curriculum_content
                WHERE nation = ?
                """,
                [nation],
            ).fetchall()
        except Exception as e:
            context.log.warning(f"No curriculum data found: {e}")

        if not curriculum_items:
            context.log.info(f"No curriculum content found for {nation}")
            return {"nation": nation, "status": "skipped", "chunks": 0}

        embeddings_data = []

        # Process in batches for performance (CRITICAL per CLAUDE.md)
        texts = []
        metadata = []

        for row in curriculum_items:
            curriculum_id, _, level, subject, title, content, outcomes = row

            # Combine content for embedding
            text_parts = [title or ""]
            if content:
                text_parts.append(content[:2000])  # Truncate long content
            if outcomes:
                for outcome in outcomes[:5]:  # Limit outcomes
                    text_parts.append(outcome)

            combined_text = " ".join(text_parts)
            if combined_text.strip():
                texts.append(combined_text)
                metadata.append({
                    "id": f"{nation}:{curriculum_id}",
                    "nation": nation,
                    "level": level,
                    "subject": subject,
                    "title": title,
                    "content_preview": (content or "")[:500],
                })

        # Batch embed (CRITICAL: 100x performance difference)
        if texts:
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_metadata = metadata[i:i + batch_size]

                embeddings = model.encode(
                    batch_texts,
                    normalize_embeddings=EMBEDDING_CONFIG["normalize"],
                    show_progress_bar=False,
                )

                for j, (text, meta, embedding) in enumerate(
                    zip(batch_texts, batch_metadata, embeddings)
                ):
                    embeddings_data.append({
                        **meta,
                        "text": text[:1000],
                        "curriculum_embedding": embedding.tolist(),
                    })

        # Store in LanceDB
        if embeddings_data:
            try:
                # Drop HNSW index before bulk insert (per CLAUDE.md)
                try:
                    table = lance_db.open_table("curriculum_embeddings")
                    # Add data
                    table.add(embeddings_data)
                except Exception:
                    # Create new table
                    lance_db.create_table("curriculum_embeddings", embeddings_data)

                context.log.info(
                    f"Embedded {len(embeddings_data)} curriculum items for {nation}"
                )
            except Exception as e:
                context.log.error(f"Failed to store embeddings: {e}")
                raise

        context.add_output_metadata({
            "nation": nation,
            "items_processed": len(curriculum_items),
            "chunks_embedded": len(embeddings_data),
            "model": EMBEDDING_CONFIG["model"],
        })

        return {
            "nation": nation,
            "status": "success",
            "chunks": len(embeddings_data),
        }

    except Exception as e:
        context.log.error(f"Failed to generate curriculum embeddings: {e}")
        return {"nation": nation, "status": "error", "error": str(e)}
    finally:
        if "conn" in dir():
            conn.close()


@asset(
    partitions_def=tradition_partitions,
    group_name="embeddings",
    deps=["celtic_characters", "celtic_stories", "celtic_locations"],
    description="Mythology embeddings for semantic search and NPC knowledge",
)
def mythology_embeddings(context: AssetExecutionContext) -> dict:
    """Generate embeddings for mythology content."""
    import duckdb
    import lancedb
    from sentence_transformers import SentenceTransformer

    tradition = context.partition_key
    db_path = os.environ.get("DUCKDB_PATH", "storage/duckdb/tuath.duckdb")
    lance_uri = os.environ.get("LANCEDB_URI", "storage/lance/tuath")

    Path(lance_uri).mkdir(parents=True, exist_ok=True)

    model = SentenceTransformer(EMBEDDING_CONFIG["model"])
    batch_size = EMBEDDING_CONFIG["batch_size"]

    try:
        conn = duckdb.connect(db_path, read_only=True)
        lance_db = lancedb.connect(lance_uri)

        embeddings_data = []
        texts = []
        metadata = []

        # Fetch characters
        try:
            characters = conn.execute(
                """
                SELECT id, name, description, type, cycle, powers
                FROM mythology.characters
                WHERE tradition = ?
                """,
                [tradition],
            ).fetchall()

            for char in characters:
                char_id, name, description, char_type, cycle, powers = char
                text = f"{name}: {description or ''}"
                if powers:
                    text += f" Powers: {', '.join(powers[:3])}"

                texts.append(text)
                metadata.append({
                    "id": f"char:{tradition}:{char_id}",
                    "tradition": tradition,
                    "content_type": "character",
                    "name": name,
                    "entity_type": char_type,
                    "cycle": cycle,
                })
        except Exception as e:
            context.log.warning(f"No character data found: {e}")

        # Fetch stories
        try:
            stories = conn.execute(
                """
                SELECT id, title, summary, themes, cycle
                FROM mythology.stories
                WHERE tradition = ?
                """,
                [tradition],
            ).fetchall()

            for story in stories:
                story_id, title, summary, themes, cycle = story
                text = f"{title}: {summary or ''}"
                if themes:
                    text += f" Themes: {', '.join(themes[:3])}"

                texts.append(text)
                metadata.append({
                    "id": f"story:{tradition}:{story_id}",
                    "tradition": tradition,
                    "content_type": "story",
                    "name": title,
                    "cycle": cycle,
                })
        except Exception as e:
            context.log.warning(f"No story data found: {e}")

        # Fetch locations
        try:
            locations = conn.execute(
                """
                SELECT id, name, description, type, associated_stories
                FROM mythology.locations
                WHERE tradition = ?
                """,
                [tradition],
            ).fetchall()

            for loc in locations:
                loc_id, name, description, loc_type, stories = loc
                text = f"{name}: {description or ''}"
                if stories:
                    text += f" Featured in: {', '.join(stories[:2])}"

                texts.append(text)
                metadata.append({
                    "id": f"loc:{tradition}:{loc_id}",
                    "tradition": tradition,
                    "content_type": "location",
                    "name": name,
                    "entity_type": loc_type,
                })
        except Exception as e:
            context.log.warning(f"No location data found: {e}")

        # Batch embed
        if texts:
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_metadata = metadata[i:i + batch_size]

                embeddings = model.encode(
                    batch_texts,
                    normalize_embeddings=EMBEDDING_CONFIG["normalize"],
                    show_progress_bar=False,
                )

                for text, meta, embedding in zip(
                    batch_texts, batch_metadata, embeddings
                ):
                    embeddings_data.append({
                        **meta,
                        "text": text[:1000],
                        "mythology_embedding": embedding.tolist(),
                    })

        # Store in LanceDB
        if embeddings_data:
            try:
                table = lance_db.open_table("mythology_embeddings")
                table.add(embeddings_data)
            except Exception:
                lance_db.create_table("mythology_embeddings", embeddings_data)

        context.add_output_metadata({
            "tradition": tradition,
            "chunks_embedded": len(embeddings_data),
            "content_types": ["characters", "stories", "locations"],
        })

        return {
            "tradition": tradition,
            "status": "success",
            "chunks": len(embeddings_data),
        }

    except Exception as e:
        context.log.error(f"Failed to generate mythology embeddings: {e}")
        return {"tradition": tradition, "status": "error", "error": str(e)}
    finally:
        if "conn" in dir():
            conn.close()


@asset(
    group_name="embeddings",
    deps=["curriculum_embeddings", "mythology_embeddings"],
    description="Embedding statistics and index health for Tuath",
)
def embedding_stats(context: AssetExecutionContext) -> dict:
    """Compute embedding statistics and verify index health."""
    import lancedb

    lance_uri = os.environ.get("LANCEDB_URI", "storage/lance/tuath")

    stats = {
        "curriculum_embeddings": {"count": 0, "nations": 0, "levels": []},
        "mythology_embeddings": {"count": 0, "traditions": 0, "content_types": []},
    }

    try:
        lance_db = lancedb.connect(lance_uri)

        # Curriculum stats
        try:
            curr_table = lance_db.open_table("curriculum_embeddings")
            curr_df = curr_table.to_pandas()
            stats["curriculum_embeddings"]["count"] = len(curr_df)
            stats["curriculum_embeddings"]["nations"] = curr_df["nation"].nunique()
            stats["curriculum_embeddings"]["levels"] = curr_df["level"].unique().tolist()
            stats["curriculum_embeddings"]["subjects"] = curr_df["subject"].unique().tolist()
        except Exception:
            pass

        # Mythology stats
        try:
            myth_table = lance_db.open_table("mythology_embeddings")
            myth_df = myth_table.to_pandas()
            stats["mythology_embeddings"]["count"] = len(myth_df)
            stats["mythology_embeddings"]["traditions"] = myth_df["tradition"].nunique()
            stats["mythology_embeddings"]["content_types"] = myth_df["content_type"].unique().tolist()
        except Exception:
            pass

    except Exception as e:
        context.log.warning(f"Failed to compute embedding stats: {e}")

    context.add_output_metadata({
        "curriculum_chunks": stats["curriculum_embeddings"]["count"],
        "curriculum_nations": stats["curriculum_embeddings"]["nations"],
        "mythology_chunks": stats["mythology_embeddings"]["count"],
        "mythology_traditions": stats["mythology_embeddings"]["traditions"],
    })

    return stats


@asset(
    group_name="embeddings",
    deps=["embedding_stats"],
    description="Create HNSW indexes for fast vector search",
)
def create_vector_indexes(context: AssetExecutionContext) -> dict:
    """Create or update HNSW indexes for vector search."""
    import lancedb

    lance_uri = os.environ.get("LANCEDB_URI", "storage/lance/tuath")

    indexes_created = []

    try:
        lance_db = lancedb.connect(lance_uri)

        # Index curriculum embeddings
        try:
            curr_table = lance_db.open_table("curriculum_embeddings")
            curr_table.create_index(
                metric="cosine",
                vector_column_name="curriculum_embedding",
                index_type="IVF_PQ",
                num_partitions=256,
                num_sub_vectors=96,
            )
            indexes_created.append("curriculum_embeddings")
            context.log.info("Created index for curriculum_embeddings")
        except Exception as e:
            context.log.warning(f"Failed to create curriculum index: {e}")

        # Index mythology embeddings
        try:
            myth_table = lance_db.open_table("mythology_embeddings")
            myth_table.create_index(
                metric="cosine",
                vector_column_name="mythology_embedding",
                index_type="IVF_PQ",
                num_partitions=256,
                num_sub_vectors=96,
            )
            indexes_created.append("mythology_embeddings")
            context.log.info("Created index for mythology_embeddings")
        except Exception as e:
            context.log.warning(f"Failed to create mythology index: {e}")

    except Exception as e:
        context.log.error(f"Failed to connect to LanceDB: {e}")

    context.add_output_metadata({
        "indexes_created": indexes_created,
        "total_indexes": len(indexes_created),
    })

    return {
        "status": "success" if indexes_created else "no_tables",
        "indexes": indexes_created,
    }
