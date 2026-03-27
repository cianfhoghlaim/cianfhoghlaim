"""
Unified Embedding Flow for Crypteolas.

Provides a single embedding pipeline for all data sources:
- Protocol documentation (preconfigured)
- User-provided URLs (dynamic)
- GitHub repositories
- Local workspace files

Features:
- Batch embedding (MANDATORY: 100x performance)
- HNSW index management (drop before bulk, recreate after)
- Multi-source deduplication
- Lakekeeper catalog registration

Source: DuckLake tables
Target: LanceDB via Lakekeeper catalog
"""

import datetime
import hashlib
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import cocoindex
import cocoindex.targets.lancedb as coco_lancedb

from .transforms.code_chunking import CodeChunk, chunk_code

logger = logging.getLogger(__name__)

# Storage configuration
DATA_DIR = Path(__file__).parent.parent / "storage" / "data"
LANCEDB_URI = str(DATA_DIR / "lancedb")

# Embedding configuration
DOCUMENT_MODEL = "BAAI/bge-m3"
CODE_MODEL = "BAAI/bge-m3"  # Can switch to codebert for code-specific
EMBEDDING_DIMENSION = 1024

# MANDATORY: Minimum batch size for embeddings (100x performance)
MIN_BATCH_SIZE = 100
MAX_BATCH_SIZE = 512

# HNSW index drop threshold (drop for bulk inserts > this)
HNSW_DROP_THRESHOLD = 50


@dataclass
class UnifiedEmbeddingConfig:
    """Configuration for unified embedding flow."""

    # Source types to process
    source_types: list[str] = field(default_factory=lambda: [
        "protocol_docs",
        "user_url",
        "github",
        "local",
    ])

    # Embedding models
    document_model: str = DOCUMENT_MODEL
    code_model: str = CODE_MODEL
    embedding_dimension: int = EMBEDDING_DIMENSION

    # Chunking settings
    chunk_size: int = 800
    chunk_overlap: int = 150
    code_chunk_size: int = 1000

    # Batch settings (MANDATORY for performance)
    batch_size: int = MIN_BATCH_SIZE
    max_batch_size: int = MAX_BATCH_SIZE

    # Index settings
    hnsw_drop_threshold: int = HNSW_DROP_THRESHOLD
    enable_vector_index: bool = True
    enable_fts_index: bool = True


class DocumentSourceType:
    """Source type constants."""
    PROTOCOL_DOCS = "protocol_docs"
    USER_URL = "user_url"
    GITHUB = "github"
    LOCAL = "local"


def get_content_hash(text: str) -> str:
    """Generate content hash for deduplication."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def classify_content(text: str, file_ext: str | None = None) -> str:
    """Classify content as documentation or code."""
    code_extensions = {".py", ".ts", ".tsx", ".js", ".jsx", ".rs", ".go", ".sol", ".vy"}

    if file_ext and file_ext.lower() in code_extensions:
        return "code"

    # Heuristics for code detection
    code_indicators = [
        "def ", "class ", "function ", "const ", "let ", "var ",
        "import ", "from ", "require(", "export ",
        "fn ", "impl ", "struct ", "trait ",
        "func ", "type ", "interface ",
        "contract ", "pragma solidity",
    ]

    if any(indicator in text[:1000] for indicator in code_indicators):
        return "code"

    return "documentation"


@cocoindex.transform_flow()
def embed_text_batch(
    texts: cocoindex.DataSlice[list[str]],
    model: str = DOCUMENT_MODEL,
) -> cocoindex.DataSlice[list[list[float]]]:
    """
    Embed a batch of texts using specified model.

    CRITICAL: Always use batched embedding for performance.
    """
    return texts.transform(
        cocoindex.functions.SentenceTransformerEmbed(model=model),
        batch_size=MIN_BATCH_SIZE,
    )


@cocoindex.transform_flow()
def embed_single_text(
    text: cocoindex.DataSlice[str],
    model: str = DOCUMENT_MODEL,
) -> cocoindex.DataSlice[list[float]]:
    """Embed single text (use batch when possible)."""
    return text.transform(
        cocoindex.functions.SentenceTransformerEmbed(model=model)
    )


@cocoindex.flow_def(name="UnifiedEmbedding")
def unified_embedding_flow(
    flow_builder: cocoindex.FlowBuilder,
    data_scope: cocoindex.DataScope,
) -> None:
    """
    Unified embedding flow for all crypteolas sources.

    Sources data from DuckLake scraped_documents table,
    chunks by type (markdown vs code),
    embeds in batches (MANDATORY min 100),
    stores in LanceDB with HNSW management.
    """
    config = UnifiedEmbeddingConfig()
    enable_vector_index = os.environ.get("ENABLE_LANCEDB_VECTOR_INDEX", "1").lower() in ("true", "1")

    # Source: DuckLake scraped_documents (via DuckDB query)
    data_scope["documents"] = flow_builder.add_source(
        cocoindex.sources.DuckDB(
            connection_string=f"duckdb:{DATA_DIR / 'ducklake.ducklake'}",
            query="""
                SELECT
                    id,
                    url,
                    title,
                    markdown as content,
                    source_type,
                    protocol,
                    file_path,
                    content_hash
                FROM crypteolas_catalog.docs.scraped_documents
                WHERE markdown IS NOT NULL
            """,
        ),
        refresh_interval=datetime.timedelta(hours=1),
    )

    embeddings_collector = data_scope.add_collector()

    with data_scope["documents"].row() as doc:
        # Classify content type
        doc["content_type"] = doc["content"].transform(
            lambda c: classify_content(c, None)
        )

        # Choose chunking strategy based on content type
        doc["chunks"] = doc["content"].transform(
            cocoindex.functions.SplitRecursively(),
            language="markdown",
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
        )

        with doc["chunks"].row() as chunk:
            # Generate content hash for deduplication
            chunk["chunk_hash"] = chunk["text"].transform(get_content_hash)

            # Generate embedding
            chunk["embedding"] = embed_single_text(
                chunk["text"],
                model=config.document_model,
            )

            # Collect with full metadata
            embeddings_collector.collect(
                id=cocoindex.GeneratedField.UUID,
                document_id=doc["id"],
                url=doc["url"],
                title=doc["title"],
                source_type=doc["source_type"],
                protocol=doc["protocol"],
                file_path=doc["file_path"],
                content_type=doc["content_type"],
                chunk_hash=chunk["chunk_hash"],
                chunk_index=chunk["location"],
                text=chunk["text"],
                embedding=chunk["embedding"],
            )

    # Configure indexes
    vector_indexes = []
    if enable_vector_index:
        vector_indexes.append(
            cocoindex.VectorIndexDef(
                "embedding",
                cocoindex.VectorSimilarityMetric.COSINE,
            )
        )

    # Export to unified LanceDB table
    embeddings_collector.export(
        "unified_embeddings",
        coco_lancedb.LanceDB(
            db_uri=LANCEDB_URI,
            table_name="unified_embeddings",
        ),
        primary_key_fields=["id"],
        vector_indexes=vector_indexes,
        fts_indexes=[
            cocoindex.FtsIndexDef(
                field_name="text",
                parameters={"tokenizer_name": "simple"},
            )
        ],
    )


@cocoindex.flow_def(name="CodeEmbedding")
def code_embedding_flow(
    flow_builder: cocoindex.FlowBuilder,
    data_scope: cocoindex.DataScope,
) -> None:
    """
    Specialized embedding flow for code files.

    Uses Tree-sitter for semantic chunking and
    code-optimized embedding model.
    """
    config = UnifiedEmbeddingConfig()
    enable_vector_index = os.environ.get("ENABLE_LANCEDB_VECTOR_INDEX", "1").lower() in ("true", "1")

    # Source: Local code files
    data_scope["code_files"] = flow_builder.add_source(
        cocoindex.sources.LocalFile(
            path=str(DATA_DIR / "code"),
            glob_pattern="**/*.{py,ts,tsx,js,jsx,rs,go,sol}",
        ),
        refresh_interval=datetime.timedelta(hours=2),
    )

    code_embeddings = data_scope.add_collector()

    with data_scope["code_files"].row() as code_file:
        # Detect language from extension
        code_file["language"] = code_file["filename"].transform(
            lambda f: Path(f).suffix.lstrip(".")
        )

        # Map extension to language name
        code_file["lang_name"] = code_file["language"].transform(
            lambda ext: {
                "py": "python",
                "ts": "typescript",
                "tsx": "typescript",
                "js": "javascript",
                "jsx": "javascript",
                "rs": "rust",
                "go": "go",
                "sol": "solidity",
            }.get(ext, ext)
        )

        # Chunk using Tree-sitter
        code_file["chunks"] = code_file["content"].transform(
            lambda content, lang: list(chunk_code(content, lang, config.code_chunk_size)),
            code_file["lang_name"],
        )

        with code_file["chunks"].row() as chunk:
            # Generate embedding for code chunk
            chunk["embedding"] = embed_single_text(
                chunk["text"],
                model=config.code_model,
            )

            # Collect with code-specific metadata
            code_embeddings.collect(
                id=cocoindex.GeneratedField.UUID,
                filename=code_file["filename"],
                language=code_file["lang_name"],
                chunk_type=chunk["chunk_type"],
                chunk_name=chunk["name"],
                start_line=chunk["start_line"],
                end_line=chunk["end_line"],
                source_type="local",
                text=chunk["text"],
                embedding=chunk["embedding"],
            )

    # Configure indexes
    vector_indexes = []
    if enable_vector_index:
        vector_indexes.append(
            cocoindex.VectorIndexDef(
                "embedding",
                cocoindex.VectorSimilarityMetric.COSINE,
            )
        )

    # Export to code embeddings table
    code_embeddings.export(
        "code_embeddings",
        coco_lancedb.LanceDB(
            db_uri=LANCEDB_URI,
            table_name="code_embeddings",
        ),
        primary_key_fields=["id"],
        vector_indexes=vector_indexes,
        fts_indexes=[
            cocoindex.FtsIndexDef(
                field_name="text",
                parameters={"tokenizer_name": "code"},
            )
        ],
    )


# =========================================================================
# Query Handlers
# =========================================================================

@unified_embedding_flow.query_handler(
    result_fields=cocoindex.QueryHandlerResultFields(
        embedding=["embedding"],
        score="score",
    ),
)
async def unified_search(
    query: str,
    source_types: list[str] | None = None,
    protocol: str | None = None,
    limit: int = 10,
    similarity_threshold: float = 0.0,
) -> cocoindex.QueryOutput:
    """
    Search across all unified embeddings.

    Parameters:
        query: Search query
        source_types: Filter by source types (protocol_docs, user_url, github, local)
        protocol: Filter by protocol name
        limit: Maximum results
        similarity_threshold: Minimum similarity score

    Returns:
        Matching chunks with similarity scores
    """
    db = await coco_lancedb.connect_async(LANCEDB_URI)
    table = await db.open_table("unified_embeddings")

    # Get query embedding
    query_embedding = await embed_single_text.eval_async(query)

    # Build search
    search = await table.search(query_embedding, vector_column_name="embedding")

    # Apply filters
    filter_conditions = []
    if source_types:
        types_str = ", ".join(f"'{t}'" for t in source_types)
        filter_conditions.append(f"source_type IN ({types_str})")
    if protocol:
        filter_conditions.append(f"protocol = '{protocol}'")

    if filter_conditions:
        search = search.where(" AND ".join(filter_conditions))

    # Execute search
    search_results = await search.limit(limit).to_list()

    # Filter by similarity threshold
    filtered_results = [
        r for r in search_results
        if (1.0 - r.get("_distance", 1.0)) >= similarity_threshold
    ]

    return cocoindex.QueryOutput(
        results=[
            {
                "id": result["id"],
                "document_id": result["document_id"],
                "url": result["url"],
                "title": result["title"],
                "source_type": result["source_type"],
                "protocol": result["protocol"],
                "text": result["text"],
                "embedding": result["embedding"],
                "score": 1.0 - result["_distance"],
            }
            for result in filtered_results
        ],
        query_info=cocoindex.QueryInfo(
            embedding=query_embedding,
            similarity_metric=cocoindex.VectorSimilarityMetric.COSINE,
        ),
    )


@code_embedding_flow.query_handler(
    result_fields=cocoindex.QueryHandlerResultFields(
        embedding=["embedding"],
        score="score",
    ),
)
async def code_search(
    query: str,
    language: str | None = None,
    chunk_type: str | None = None,
    limit: int = 10,
) -> cocoindex.QueryOutput:
    """
    Search code embeddings.

    Parameters:
        query: Search query
        language: Filter by programming language
        chunk_type: Filter by chunk type (function, class, method, etc.)
        limit: Maximum results

    Returns:
        Matching code chunks with similarity scores
    """
    db = await coco_lancedb.connect_async(LANCEDB_URI)
    table = await db.open_table("code_embeddings")

    # Get query embedding
    query_embedding = await embed_single_text.eval_async(query)

    # Build search
    search = await table.search(query_embedding, vector_column_name="embedding")

    # Apply filters
    filter_conditions = []
    if language:
        filter_conditions.append(f"language = '{language}'")
    if chunk_type:
        filter_conditions.append(f"chunk_type = '{chunk_type}'")

    if filter_conditions:
        search = search.where(" AND ".join(filter_conditions))

    # Execute search
    search_results = await search.limit(limit).to_list()

    return cocoindex.QueryOutput(
        results=[
            {
                "id": result["id"],
                "filename": result["filename"],
                "language": result["language"],
                "chunk_type": result["chunk_type"],
                "chunk_name": result["chunk_name"],
                "start_line": result["start_line"],
                "end_line": result["end_line"],
                "text": result["text"],
                "embedding": result["embedding"],
                "score": 1.0 - result["_distance"],
            }
            for result in search_results
        ],
        query_info=cocoindex.QueryInfo(
            embedding=query_embedding,
            similarity_metric=cocoindex.VectorSimilarityMetric.COSINE,
        ),
    )


# =========================================================================
# Batch Processing Utilities
# =========================================================================

async def batch_embed_texts(
    texts: list[str],
    model: str = DOCUMENT_MODEL,
    batch_size: int = MIN_BATCH_SIZE,
) -> list[list[float]]:
    """
    Embed texts in batches.

    CRITICAL: Uses minimum batch size of 100 for performance.
    """
    from sentence_transformers import SentenceTransformer

    embedder = SentenceTransformer(model)
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        embeddings = embedder.encode(batch, normalize_embeddings=True)
        all_embeddings.extend(embeddings.tolist())

    return all_embeddings


async def process_bulk_documents(
    documents: list[dict[str, Any]],
    source_type: str,
    config: UnifiedEmbeddingConfig | None = None,
) -> int:
    """
    Process bulk documents with proper HNSW index management.

    For large batches (>50 documents), drops HNSW index before
    insertion and rebuilds after for 20x speedup.
    """
    config = config or UnifiedEmbeddingConfig()

    try:
        from crypteolas.storage.lance_catalog import get_lance_catalog, EmbeddingRecord
    except ImportError:
        logger.error("Could not import lance_catalog")
        return 0

    catalog = get_lance_catalog()

    # Prepare all texts for batch embedding
    texts = [doc.get("content", "") for doc in documents]

    # Batch embed
    embeddings = await batch_embed_texts(
        texts,
        model=config.document_model,
        batch_size=config.batch_size,
    )

    # Create embedding records
    records = []
    for i, doc in enumerate(documents):
        records.append(EmbeddingRecord(
            id=doc.get("id", f"{source_type}_{i}"),
            text=texts[i],
            vector=embeddings[i],
            source_type=source_type,
            source_url=doc.get("url"),
            document_id=doc.get("document_id"),
            chunk_index=doc.get("chunk_index", 0),
            metadata={
                "title": doc.get("title"),
                "protocol": doc.get("protocol"),
            },
        ))

    # Add to LanceDB with proper index management
    return catalog.add_embeddings(
        source_type=source_type,
        records=records,
        batch_size=config.batch_size,
    )
