"""
Document Embedding Flow for Crypteolas.

Embeds protocol documentation, whitepapers, and audit reports
using BGE-M3 for semantic search across:
- Protocol documentation
- Technical whitepapers
- Security audit reports
- API documentation

Source: DuckDB tables populated by Firecrawl DLT
Target: LanceDB with FTS + vector indexes
"""

import datetime
from pathlib import Path

import cocoindex
import cocoindex.targets.lancedb as coco_lancedb

# Storage paths
DATA_DIR = Path(__file__).parent.parent / "storage"
LANCEDB_URI = str(DATA_DIR / "lance" / "documents")
LANCEDB_TABLE = "document_embeddings"


@cocoindex.transform_flow()
def embed_document_chunk(
    text: cocoindex.DataSlice[str],
) -> cocoindex.DataSlice[list[float]]:
    """
    Embed document text using BGE-M3.

    BGE-M3 provides strong multilingual and technical text understanding.
    """
    return text.transform(
        cocoindex.functions.SentenceTransformerEmbed(model="BAAI/bge-m3")
    )


def extract_document_type(url: str, title: str) -> str:
    """Extract document type from URL or title."""
    url_lower = url.lower()
    title_lower = title.lower() if title else ""

    if any(kw in url_lower for kw in ["whitepaper", "white-paper", "litepaper"]):
        return "whitepaper"
    if any(kw in url_lower for kw in ["audit", "security"]):
        return "audit"
    if any(kw in url_lower for kw in ["api", "reference", "swagger"]):
        return "api_docs"
    if any(kw in url_lower for kw in ["docs", "documentation", "guide"]):
        return "documentation"
    if any(kw in title_lower for kw in ["audit", "security review"]):
        return "audit"
    if any(kw in title_lower for kw in ["whitepaper", "tokenomics"]):
        return "whitepaper"

    return "documentation"


@cocoindex.flow_def(name="DocumentEmbedding")
def document_embedding_flow(
    flow_builder: cocoindex.FlowBuilder,
    data_scope: cocoindex.DataScope,
) -> None:
    """
    Define the document embedding flow.

    Sources documentation from DuckDB tables populated by Firecrawl,
    chunks by semantic sections, embeds with BGE-M3,
    and stores in LanceDB with full-text search.
    """
    import os

    ENABLE_VECTOR_INDEX = os.environ.get("ENABLE_LANCEDB_VECTOR_INDEX", "0").lower() in (
        "true",
        "1",
    )

    # Source: Local markdown files (in production, read from DuckDB)
    data_scope["doc_files"] = flow_builder.add_source(
        cocoindex.sources.LocalFile(
            path=str(DATA_DIR / "raw" / "docs"),
            glob_pattern="**/*.{md,txt,html}",
        ),
        refresh_interval=datetime.timedelta(hours=6),
    )

    document_embeddings = data_scope.add_collector()

    with data_scope["doc_files"].row() as doc:
        # Extract protocol from path
        doc["protocol"] = doc["filename"].transform(
            lambda f: f.split("/")[0] if "/" in f else "unknown"
        )

        # Chunk content by sections
        doc["chunks"] = doc["content"].transform(
            cocoindex.functions.SplitRecursively(),
            language="markdown",
            chunk_size=800,
            chunk_overlap=150,
        )

        with doc["chunks"].row() as chunk:
            # Generate embedding
            chunk["embedding"] = embed_document_chunk(chunk["text"])

            # Collect with metadata
            document_embeddings.collect(
                id=cocoindex.GeneratedField.UUID,
                filename=doc["filename"],
                protocol=doc["protocol"],
                doc_type=doc["filename"].transform(
                    lambda f: extract_document_type(f, "")
                ),
                location=chunk["location"],
                text=chunk["text"],
                doc_embedding=chunk["embedding"],
            )

    # Configure vector indexes
    vector_indexes = []
    if ENABLE_VECTOR_INDEX:
        vector_indexes.append(
            cocoindex.VectorIndexDef(
                "doc_embedding",
                cocoindex.VectorSimilarityMetric.COSINE,
            )
        )

    # Export to LanceDB
    document_embeddings.export(
        "document_embeddings",
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


@document_embedding_flow.query_handler(
    result_fields=cocoindex.QueryHandlerResultFields(
        embedding=["embedding"],
        score="score",
    ),
)
async def search_documents(
    query: str,
    protocol: str | None = None,
    doc_type: str | None = None,
    limit: int = 10,
) -> cocoindex.QueryOutput:
    """
    Search protocol documentation.

    Parameters:
        query: Search query
        protocol: Filter by protocol name
        doc_type: Filter by document type (documentation, whitepaper, audit, api_docs)
        limit: Maximum results

    Returns:
        Matching document chunks with similarity scores
    """
    db = await coco_lancedb.connect_async(LANCEDB_URI)
    table = await db.open_table(LANCEDB_TABLE)

    # Get query embedding
    query_embedding = await embed_document_chunk.eval_async(query)

    # Build search
    search = await table.search(query_embedding, vector_column_name="doc_embedding")

    # Apply filters
    filter_conditions = []
    if protocol:
        filter_conditions.append(f"protocol = '{protocol}'")
    if doc_type:
        filter_conditions.append(f"doc_type = '{doc_type}'")

    if filter_conditions:
        search = search.where(" AND ".join(filter_conditions))

    # Execute search
    search_results = await search.limit(limit).to_list()

    return cocoindex.QueryOutput(
        results=[
            {
                "id": result["id"],
                "filename": result["filename"],
                "protocol": result["protocol"],
                "doc_type": result["doc_type"],
                "text": result["text"],
                "embedding": result["doc_embedding"],
                "score": 1.0 - result["_distance"],
            }
            for result in search_results
        ],
        query_info=cocoindex.QueryInfo(
            embedding=query_embedding,
            similarity_metric=cocoindex.VectorSimilarityMetric.COSINE,
        ),
    )


async def search_audits(
    query: str,
    protocol: str | None = None,
    limit: int = 5,
) -> list[dict]:
    """
    Search specifically within audit reports.

    Useful for security analysis and vulnerability research.
    """
    results = await search_documents(
        query=query,
        protocol=protocol,
        doc_type="audit",
        limit=limit,
    )
    return results.results


async def search_whitepapers(
    query: str,
    protocol: str | None = None,
    limit: int = 5,
) -> list[dict]:
    """
    Search within protocol whitepapers.

    Useful for understanding tokenomics and protocol design.
    """
    results = await search_documents(
        query=query,
        protocol=protocol,
        doc_type="whitepaper",
        limit=limit,
    )
    return results.results
