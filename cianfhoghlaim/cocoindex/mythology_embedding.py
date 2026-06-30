"""
Mythology Embedding Flow for Tuath.

Embeds Celtic mythology and folklore content for NPC dialogue
and quest generation:
- Irish mythology (Tuatha Dé Danann, Fianna, Ulster Cycle)
- Welsh mythology (Mabinogion)
- Scottish folklore
- Dúchas Schools' Collection

Source: DuckDB folklore tables populated by DLT
Target: LanceDB with FTS + vector indexes
"""

import datetime
from pathlib import Path

import cocoindex
import cocoindex.targets.lancedb as coco_lancedb

# Storage paths
DATA_DIR = Path(__file__).parent.parent / "storage"
LANCEDB_URI = str(DATA_DIR / "lance" / "mythology")
LANCEDB_TABLE = "mythology_embeddings"


@cocoindex.transform_flow()
def embed_mythology_chunk(
    text: cocoindex.DataSlice[str],
) -> cocoindex.DataSlice[list[float]]:
    """
    Embed mythology text using BGE-M3.

    Good for multilingual Celtic content including archaic forms.
    """
    return text.transform(
        cocoindex.functions.SentenceTransformerEmbed(model="BAAI/bge-m3")
    )


@cocoindex.flow_def(name="MythologyEmbedding")
def mythology_embedding_flow(
    flow_builder: cocoindex.FlowBuilder,
    data_scope: cocoindex.DataScope,
) -> None:
    """
    Define the mythology embedding flow.

    Sources folklore and mythology from DuckDB tables,
    chunks by story segments, embeds with BGE-M3,
    and stores in LanceDB for NPC dialogue generation.
    """
    import os

    ENABLE_VECTOR_INDEX = os.environ.get("ENABLE_LANCEDB_VECTOR_INDEX", "0").lower() in (
        "true",
        "1",
    )

    # Source: Local mythology files
    data_scope["mythology_docs"] = flow_builder.add_source(
        cocoindex.sources.LocalFile(
            path=str(DATA_DIR / "raw" / "mythology"),
            glob_pattern="**/*.{md,txt,json}",
        ),
        refresh_interval=datetime.timedelta(hours=24),
    )

    mythology_embeddings = data_scope.add_collector()

    with data_scope["mythology_docs"].row() as doc:
        # Extract metadata from path
        doc["path_parts"] = doc["filename"].transform(
            lambda f: f.split("/") if "/" in f else [f]
        )

        # Chunk content by story segments
        doc["chunks"] = doc["content"].transform(
            cocoindex.functions.SplitRecursively(),
            language="markdown",
            chunk_size=800,
            chunk_overlap=150,
        )

        with doc["chunks"].row() as chunk:
            # Generate embedding
            chunk["embedding"] = embed_mythology_chunk(chunk["text"])

            # Collect with metadata
            mythology_embeddings.collect(
                id=cocoindex.GeneratedField.UUID,
                filename=doc["filename"],
                cycle=doc["path_parts"].transform(
                    lambda p: p[1] if len(p) > 1 else "unknown"
                ),  # tuatha_de_danann, fianna, ulster, mabinogion
                tradition=doc["path_parts"].transform(
                    lambda p: p[0] if len(p) > 0 else "unknown"
                ),  # irish, welsh, scottish
                location=chunk["location"],
                text=chunk["text"],
                mythology_embedding=chunk["embedding"],
            )

    # Configure vector indexes
    vector_indexes = []
    if ENABLE_VECTOR_INDEX:
        vector_indexes.append(
            cocoindex.VectorIndexDef(
                "mythology_embedding",
                cocoindex.VectorSimilarityMetric.COSINE,
            )
        )

    # Export to LanceDB
    mythology_embeddings.export(
        "mythology_embeddings",
        coco_lancedb.LanceDB(db_uri=LANCEDB_URI, table_name=LANCEDB_TABLE),
        primary_key_fields=["id"],
        vector_indexes=vector_indexes,
        fts_indexes=[
            cocoindex.FtsIndexDef(
                field_name="text",
                parameters={"tokenizer_name": "simple"},
            )
        ],
    )


@mythology_embedding_flow.query_handler(
    result_fields=cocoindex.QueryHandlerResultFields(
        embedding=["embedding"],
        score="score",
    ),
)
async def search_mythology(
    query: str,
    cycle: str | None = None,
    tradition: str | None = None,
    limit: int = 10,
) -> cocoindex.QueryOutput:
    """
    Search mythology content for NPC dialogue.

    Parameters:
        query: Search query (character, story, theme)
        cycle: Filter by mythological cycle
        tradition: Filter by tradition (irish, welsh, scottish)
        limit: Maximum results

    Returns:
        Matching mythology chunks for dialogue generation
    """
    db = await coco_lancedb.connect_async(LANCEDB_URI)
    table = await db.open_table(LANCEDB_TABLE)

    # Get query embedding
    query_embedding = await embed_mythology_chunk.eval_async(query)

    # Build search
    search = await table.search(query_embedding, vector_column_name="mythology_embedding")

    # Apply filters
    filter_conditions = []
    if cycle:
        filter_conditions.append(f"cycle = '{cycle}'")
    if tradition:
        filter_conditions.append(f"tradition = '{tradition}'")

    if filter_conditions:
        search = search.where(" AND ".join(filter_conditions))

    # Execute search
    search_results = await search.limit(limit).to_list()

    return cocoindex.QueryOutput(
        results=[
            {
                "id": result["id"],
                "filename": result["filename"],
                "cycle": result["cycle"],
                "tradition": result["tradition"],
                "text": result["text"],
                "embedding": result["mythology_embedding"],
                "score": 1.0 - result["_distance"],
            }
            for result in search_results
        ],
        query_info=cocoindex.QueryInfo(
            embedding=query_embedding,
            similarity_metric=cocoindex.VectorSimilarityMetric.COSINE,
        ),
    )


async def get_character_lore(
    character_name: str,
    limit: int = 5,
) -> list[dict]:
    """
    Get lore for a specific mythological character.

    Useful for generating NPC backstories and dialogue.
    """
    results = await search_mythology(
        query=character_name,
        limit=limit,
    )
    return results.results


async def get_location_lore(
    location_name: str,
    tradition: str | None = None,
    limit: int = 5,
) -> list[dict]:
    """
    Get lore for a mythological location.

    Useful for world-building and quest generation.
    """
    results = await search_mythology(
        query=location_name,
        tradition=tradition,
        limit=limit,
    )
    return results.results


async def find_similar_stories(
    story_text: str,
    source_tradition: str,
    limit: int = 5,
) -> list[dict]:
    """
    Find similar stories across Celtic traditions.

    Useful for cross-cultural quest design.
    """
    all_traditions = ["irish", "welsh", "scottish"]
    target_traditions = [t for t in all_traditions if t != source_tradition]

    results = []
    for tradition in target_traditions:
        tradition_results = await search_mythology(
            query=story_text,
            tradition=tradition,
            limit=limit,
        )
        for r in tradition_results.results:
            r["source_tradition"] = source_tradition
        results.extend(tradition_results.results)

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]
