"""CV and Teaching Text Embedding Flow.

CocoIndex flow for embedding extracted CV and teaching text
and storing in LanceDB for semantic search.

This flow:
1. Reads extracted text from DuckDB (output of DLT pipeline)
2. Embeds text using sentence-transformers (multilingual model)
3. Stores embeddings in LanceDB with lang field (en/ga)
4. Writes JSON index files for the croilar web app's search UI

Usage:
    import cocoindex
    from cocoindex_flows import cv_embedding_flow

    cocoindex.init()
    cv_embedding_flow.setup()
    cocoindex.run_flows([cv_embedding_flow])
"""

import datetime
import functools
import json
import os
from pathlib import Path
from typing import Any, Literal

import cocoindex
import cocoindex.targets.lancedb as coco_lancedb

DUCKDB_PATH = os.environ.get("DUCKDB_PATH", "./croilar.duckdb")
LANCEDB_URI = os.environ.get("LANCEDB_URI", "./lancedb_data_cv")
LANCEDB_TABLE = "croilar_cv"
SEARCH_INDEX_PATH = os.environ.get("SEARCH_INDEX_PATH", "./croilar/cv/search_index.json")

EMBEDDING_MODEL = os.environ.get(
    "EMBEDDING_MODEL",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)


@functools.cache
def get_embedding_model():
    """Load multilingual sentence-transformer model."""
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMBEDDING_MODEL)


def embed_text(text: str) -> list[float]:
    """Embed text using sentence-transformers.

    Args:
        text: Text to embed (English or Gaeilge)

    Returns:
        384-dimensional embedding vector
    """
    model = get_embedding_model()
    return model.encode(text, normalize_embeddings=True).tolist()


def detect_language(text: str) -> str:
    """Detect if text is primarily English or Irish.

    Simple heuristic based on common Irish words.

    Args:
        text: Input text

    Returns:
        'en' or 'ga'
    """
    ga_markers = ["agus", "bhí", "tá", "chun", "sna", "leis", "ar an", "don"]
    text_lower = text.lower()
    ga_count = sum(1 for marker in ga_markers if marker in text_lower)
    return "ga" if ga_count >= 3 else "en"


@cocoindex.flow_def(name="CVEmbedding")
def cv_embedding_flow(
    flow_builder: cocoindex.FlowBuilder,
    data_scope: cocoindex.DataScope,
) -> None:
    """CocoIndex flow for CV text embedding.

    Reads extracted CV text from DuckDB, embeds with multilingual
    sentence-transformers, and exports to LanceDB.
    """
    data_scope["cv"] = flow_builder.add_source(
        cocoindex.sources.DuckDB(
            path=DUCKDB_PATH,
            query="""
                SELECT filepath, category, filename, extracted_text
                FROM cv_data.cv_raw
                WHERE extracted_text IS NOT NULL AND extracted_text != ''
            """,
        ),
        refresh_interval=datetime.timedelta(minutes=30),
    )

    cv_embeddings = data_scope.add_collector()

    with data_scope["cv"].row() as row:
        row["lang"] = flow_builder.transform(
            cocoindex.functions.CustomPythonFunction(detect_language),
            text=row["extracted_text"],
        )

        # Chunk long texts into segments for better search granularity
        row["segments"] = flow_builder.transform(
            cocoindex.functions.SplitText(chunk_size=500, chunk_overlap=50),
            text=row["extracted_text"],
        )

    with data_scope["cv_segments"].row() as seg:
        seg["embedding"] = flow_builder.transform(
            cocoindex.functions.CustomPythonFunction(
                embed_text,
                output_type=list[float],
                output_description="384-dimensional embedding vector",
            ),
            text=seg["text"],
        )

        cv_embeddings.collect(
            id=cocoindex.GeneratedField.UUID,
            filepath=seg["filepath"],
            category=seg["category"],
            filename=seg["filename"],
            segment_text=seg["text"],
            lang=seg["lang"],
            embedding=seg["embedding"],
        )

    cv_embeddings.export(
        "cv_embeddings",
        coco_lancedb.LanceDB(db_uri=LANCEDB_URI, table_name=LANCEDB_TABLE),
        primary_key_fields=["id"],
        vector_indexes=[
            cocoindex.VectorIndexDef(
                "embedding",
                cocoindex.VectorSimilarityMetric.COSINE_DISTANCE,
            )
        ],
    )


@cv_embedding_flow.query_handler(
    result_fields=cocoindex.QueryHandlerResultFields(
        embedding=["embedding"],
        score="score",
    ),
)
async def search_cv(
    query: str,
    lang: str | None = None,
    limit: int = 10,
) -> cocoindex.QueryOutput:
    """Search the CV text index by natural language query.

    Args:
        query: Search text
        lang: Filter by language ('en' or 'ga'), or None for both
        limit: Maximum number of results

    Returns:
        QueryOutput with matching CV segments
    """
    db = await coco_lancedb.connect_async(LANCEDB_URI)
    table = await db.open_table(LANCEDB_TABLE)

    query_embedding = embed_text(query)
    search = await table.search(query_embedding, vector_column_name="embedding")

    if lang:
        search = search.where(f"lang = '{lang}'")

    search_results = await search.limit(limit).to_list()

    results = [
        {
            "filepath": r["filepath"],
            "category": r["category"],
            "segment_text": r["segment_text"],
            "lang": r.get("lang", "en"),
            "score": 1.0 - r["_distance"],
        }
        for r in search_results
    ]

    # Write search index JSON for the web app
    index_dir = Path(SEARCH_INDEX_PATH).parent
    index_dir.mkdir(parents=True, exist_ok=True)
    with open(SEARCH_INDEX_PATH, "w") as f:
        json.dump(
            {
                "query": query,
                "lang_filter": lang,
                "result_count": len(results),
                "results": results,
            },
            f,
            indent=2,
            default=str,
        )

    return cocoindex.QueryOutput(
        results=results,
        query_info=cocoindex.QueryInfo(
            embedding=query_embedding,
            similarity_metric=cocoindex.VectorSimilarityMetric.COSINE_DISTANCE,
        ),
    )
