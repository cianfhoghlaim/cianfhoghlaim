"""
Code Embedding Flow for Crypteolas.

Embeds code from GitHub repositories using CodeBERT for
semantic code search across:
- Repository codebases
- Issue and PR descriptions
- Commit messages

Source: DuckDB tables populated by DLT
Target: LanceDB with FTS + vector indexes
"""

import datetime
from pathlib import Path

import cocoindex
import cocoindex.targets.lancedb as coco_lancedb

# Storage paths
DATA_DIR = Path(__file__).parent.parent / "storage"
LANCEDB_URI = str(DATA_DIR / "lance" / "code")
LANCEDB_TABLE = "code_embeddings"

# Supported languages for code chunking
SUPPORTED_LANGUAGES = [
    "python",
    "javascript",
    "typescript",
    "rust",
    "go",
    "solidity",
]


@cocoindex.transform_flow()
def embed_code_chunk(
    text: cocoindex.DataSlice[str],
) -> cocoindex.DataSlice[list[float]]:
    """
    Embed code text using CodeBERT.

    CodeBERT provides strong code understanding for semantic search.
    Falls back to BGE-M3 for non-code content.
    """
    return text.transform(
        cocoindex.functions.SentenceTransformerEmbed(
            model="microsoft/codebert-base"
        )
    )


@cocoindex.transform_flow()
def embed_text_chunk(
    text: cocoindex.DataSlice[str],
) -> cocoindex.DataSlice[list[float]]:
    """
    Embed natural language text using BGE-M3.

    Used for issues, PRs, and documentation.
    """
    return text.transform(
        cocoindex.functions.SentenceTransformerEmbed(model="BAAI/bge-m3")
    )


def detect_language_from_extension(filename: str) -> str:
    """Detect programming language from file extension."""
    ext_map = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".rs": "rust",
        ".go": "go",
        ".sol": "solidity",
        ".md": "markdown",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
    }
    for ext, lang in ext_map.items():
        if filename.endswith(ext):
            return lang
    return "unknown"


@cocoindex.flow_def(name="CodeEmbedding")
def code_embedding_flow(
    flow_builder: cocoindex.FlowBuilder,
    data_scope: cocoindex.DataScope,
) -> None:
    """
    Define the code embedding flow.

    Sources code content from DuckDB tables populated by DLT,
    chunks by semantic units (functions, classes),
    embeds with CodeBERT, and stores in LanceDB.
    """
    import os

    ENABLE_VECTOR_INDEX = os.environ.get("ENABLE_LANCEDB_VECTOR_INDEX", "0").lower() in (
        "true",
        "1",
    )

    # Source: Local code files (in production, read from DuckDB)
    data_scope["code_files"] = flow_builder.add_source(
        cocoindex.sources.LocalFile(
            path=str(DATA_DIR / "raw" / "code"),
            glob_pattern="**/*.{py,js,ts,tsx,rs,go,sol,md}",
        ),
        refresh_interval=datetime.timedelta(hours=1),
    )

    code_embeddings = data_scope.add_collector()

    with data_scope["code_files"].row() as file:
        # Detect language
        file["language"] = file["filename"].transform(
            lambda f: detect_language_from_extension(f)
        )

        # Chunk code semantically
        file["chunks"] = file["content"].transform(
            cocoindex.functions.SplitRecursively(),
            language="python",  # Use Python parser as default
            chunk_size=1000,
            chunk_overlap=200,
        )

        with file["chunks"].row() as chunk:
            # Generate embedding based on content type
            chunk["embedding"] = chunk["text"].transform(
                cocoindex.functions.SentenceTransformerEmbed(
                    model="microsoft/codebert-base"
                )
            )

            # Collect with metadata
            code_embeddings.collect(
                id=cocoindex.GeneratedField.UUID,
                filename=file["filename"],
                repo=file["filename"].transform(
                    lambda f: f.split("/")[0] if "/" in f else "unknown"
                ),
                language=file["language"],
                location=chunk["location"],
                text=chunk["text"],
                code_embedding=chunk["embedding"],
            )

    # Configure vector indexes
    vector_indexes = []
    if ENABLE_VECTOR_INDEX:
        vector_indexes.append(
            cocoindex.VectorIndexDef(
                "code_embedding",
                cocoindex.VectorSimilarityMetric.COSINE,
            )
        )

    # Export to LanceDB
    code_embeddings.export(
        "code_embeddings",
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


@code_embedding_flow.query_handler(
    result_fields=cocoindex.QueryHandlerResultFields(
        embedding=["embedding"],
        score="score",
    ),
)
async def search_code(
    query: str,
    repo: str | None = None,
    language: str | None = None,
    limit: int = 10,
) -> cocoindex.QueryOutput:
    """
    Search code with semantic understanding.

    Parameters:
        query: Search query (can be natural language or code snippet)
        repo: Filter by repository
        language: Filter by programming language
        limit: Maximum results

    Returns:
        Matching code chunks with similarity scores
    """
    db = await coco_lancedb.connect_async(LANCEDB_URI)
    table = await db.open_table(LANCEDB_TABLE)

    # Get query embedding
    query_embedding = await embed_code_chunk.eval_async(query)

    # Build search
    search = await table.search(query_embedding, vector_column_name="code_embedding")

    # Apply filters
    filter_conditions = []
    if repo:
        filter_conditions.append(f"repo = '{repo}'")
    if language:
        filter_conditions.append(f"language = '{language}'")

    if filter_conditions:
        search = search.where(" AND ".join(filter_conditions))

    # Execute search
    search_results = await search.limit(limit).to_list()

    return cocoindex.QueryOutput(
        results=[
            {
                "id": result["id"],
                "filename": result["filename"],
                "repo": result["repo"],
                "language": result["language"],
                "text": result["text"],
                "embedding": result["code_embedding"],
                "score": 1.0 - result["_distance"],
            }
            for result in search_results
        ],
        query_info=cocoindex.QueryInfo(
            embedding=query_embedding,
            similarity_metric=cocoindex.VectorSimilarityMetric.COSINE,
        ),
    )


async def find_similar_code(
    code_snippet: str,
    exclude_file: str | None = None,
    limit: int = 5,
) -> list[dict]:
    """
    Find similar code patterns across repositories.

    Useful for:
    - Detecting duplicated code
    - Finding implementation patterns
    - Code reuse opportunities
    """
    results = await search_code(query=code_snippet, limit=limit + 1)

    # Filter out the source file if specified
    if exclude_file:
        results.results = [r for r in results.results if r["filename"] != exclude_file]

    return results.results[:limit]
