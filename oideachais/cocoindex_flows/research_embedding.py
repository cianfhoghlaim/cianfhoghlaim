"""
Research Document and Code Embedding Flows.

Migrated from sruth.taighde.cocoindex_flows.

Provides embedding flows for Bunchloch research documents:
- Document embedding: PDFs, DOCX using BGE-M3
- Code embedding: Java, Python using CodeBERT

Source: DuckDB tables populated by DLT filesystem source
Target: LanceDB via Lakehouse REST API with HNSW indexes

Critical Constraints:
- BATCH_MIN_SIZE: 100 embeddings per API call (100x performance difference)
- Drop HNSW indexes before bulk inserts >50 rows
- Recreate indexes after batch completion
"""

import datetime
import os
from pathlib import Path
from typing import Any

import cocoindex
import cocoindex.targets.lancedb as coco_lancedb

# =============================================================================
# Configuration
# =============================================================================

LANCEDB_URI = os.getenv("LANCEDB_URI", "rest://lance-api.cianfhoghlaim.ie")

# Document embedding configuration
DOC_LANCEDB_TABLE = "bunchloch_documents"
DOC_CHUNK_SIZE = 800
DOC_CHUNK_OVERLAP = 150

# Code embedding configuration
CODE_LANCEDB_TABLE = "bunchloch_code"
CODE_CHUNK_SIZE = 1200
CODE_CHUNK_OVERLAP = 200
MIN_CHUNK_SIZE = 100

# Batch size for embeddings (CRITICAL: minimum 100 for performance)
EMBEDDING_BATCH_SIZE = 100

# Supported languages with their extensions
LANGUAGE_EXTENSIONS = {
    ".java": "java",
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".class": "java_bytecode",
}


# =============================================================================
# Document Embedding Flow
# =============================================================================


@cocoindex.transform_flow()
def embed_document_chunk(
    text: cocoindex.DataSlice[str],
) -> cocoindex.DataSlice[list[float]]:
    """
    Embed document text using BGE-M3.

    BGE-M3 provides:
    - Strong multilingual support (good for Irish content)
    - 1024-dimensional dense vectors
    - Technical text understanding
    """
    return text.transform(
        cocoindex.functions.SentenceTransformerEmbed(
            model="BAAI/bge-m3",
            batch_size=EMBEDDING_BATCH_SIZE,
        )
    )


def extract_document_type(file_path: str, file_name: str) -> str:
    """Extract document type from path and filename."""
    path_lower = file_path.lower()
    name_lower = file_name.lower()

    if any(kw in name_lower for kw in ["exam", "test", "quiz"]):
        return "exam"
    if any(kw in name_lower for kw in ["assignment", "homework", "project"]):
        return "assignment"
    if any(kw in name_lower for kw in ["lecture", "notes", "class"]):
        return "lecture"
    if any(kw in name_lower for kw in ["lab", "practical"]):
        return "lab"
    if any(kw in path_lower for kw in ["oideachas", "education"]):
        return "lesson_plan"

    return "document"


def extract_subject(file_path: str) -> str:
    """Extract subject from file path."""
    path_lower = file_path.lower()

    if "comp_science" in path_lower:
        return "comp_science"
    if "gaeilge" in path_lower:
        return "gaeilge"
    if "mata" in path_lower:
        return "mata"
    if "oideachas" in path_lower:
        return "oideachas"

    return "unknown"


def extract_course_code(file_path: str) -> str | None:
    """Extract course code from path (e.g., CT511, GA101)."""
    import re

    match = re.search(r"([A-Z]{2,3})(\d{3,4})", file_path)
    return f"{match.group(1)}{match.group(2)}" if match else None


@cocoindex.flow_def(name="BunchlochDocumentEmbedding")
def document_embedding_flow(
    flow_builder: cocoindex.FlowBuilder,
    data_scope: cocoindex.DataScope,
) -> None:
    """
    Bunchloch document embedding flow.

    Sources documents from DuckDB (populated by DLT),
    chunks semantically, embeds with BGE-M3,
    and stores in LanceDB with HNSW + FTS indexes.
    """
    ENABLE_VECTOR_INDEX = os.environ.get("ENABLE_LANCEDB_VECTOR_INDEX", "1").lower() in (
        "true",
        "1",
    )

    data_scope["documents"] = flow_builder.add_source(
        cocoindex.sources.DuckDB(
            connection_string="duckdb:///bunchloch.duckdb",
            query="""
                SELECT
                    file_hash as id,
                    file_path,
                    file_name,
                    file_type,
                    subject,
                    course_code,
                    content
                FROM bunchloch.documents
                WHERE file_type IN ('pdf', 'word')
                  AND content IS NOT NULL
            """,
        ),
        refresh_interval=datetime.timedelta(hours=6),
    )

    document_embeddings = data_scope.add_collector()

    with data_scope["documents"].row() as doc:
        doc["chunks"] = doc["content"].transform(
            cocoindex.functions.SplitRecursively(),
            language="markdown",
            chunk_size=DOC_CHUNK_SIZE,
            chunk_overlap=DOC_CHUNK_OVERLAP,
            separators=["\n\n\n", "\n\n", "\n", ". ", " "],
        )

        with doc["chunks"].row() as chunk:
            chunk["embedding"] = embed_document_chunk(chunk["text"])

            document_embeddings.collect(
                id=cocoindex.GeneratedField.UUID,
                file_hash=doc["id"],
                file_path=doc["file_path"],
                file_name=doc["file_name"],
                subject=doc["subject"],
                course_code=doc["course_code"],
                doc_type=doc["file_path"].transform(
                    lambda p: extract_document_type(p, doc["file_name"])
                ),
                location=chunk["location"],
                text=chunk["text"],
                embedding=chunk["embedding"],
            )

    vector_indexes = []
    if ENABLE_VECTOR_INDEX:
        vector_indexes.append(
            cocoindex.VectorIndexDef(
                field_name="embedding",
                metric=cocoindex.VectorSimilarityMetric.COSINE,
                index_type="IVF_HNSW",
                num_partitions=256,
                num_sub_vectors=32,
            )
        )

    document_embeddings.export(
        "bunchloch_documents",
        coco_lancedb.LanceDB(
            db_uri=LANCEDB_URI,
            table_name=DOC_LANCEDB_TABLE,
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


@document_embedding_flow.query_handler(
    result_fields=cocoindex.QueryHandlerResultFields(
        embedding=["embedding"],
        score="score",
    ),
)
async def search_documents(
    query: str,
    subject: str | None = None,
    course_code: str | None = None,
    doc_type: str | None = None,
    limit: int = 10,
) -> cocoindex.QueryOutput:
    """
    Search bunchloch documents with semantic understanding.

    Parameters:
        query: Search query (natural language)
        subject: Filter by subject (comp_science, gaeilge, mata, oideachas)
        course_code: Filter by course code (CT511, GA101, etc.)
        doc_type: Filter by document type (exam, assignment, lecture, lab, lesson_plan)
        limit: Maximum results

    Returns:
        Matching document chunks with similarity scores
    """
    db = await coco_lancedb.connect_async(LANCEDB_URI)
    table = await db.open_table(DOC_LANCEDB_TABLE)

    query_embedding = await embed_document_chunk.eval_async(query)
    search = await table.search(query_embedding, vector_column_name="embedding")

    filter_conditions = []
    if subject:
        filter_conditions.append(f"subject = '{subject}'")
    if course_code:
        filter_conditions.append(f"course_code = '{course_code}'")
    if doc_type:
        filter_conditions.append(f"doc_type = '{doc_type}'")

    if filter_conditions:
        search = search.where(" AND ".join(filter_conditions))

    search_results = await search.limit(limit).to_list()

    return cocoindex.QueryOutput(
        results=[
            {
                "id": result["id"],
                "file_name": result["file_name"],
                "subject": result["subject"],
                "course_code": result["course_code"],
                "doc_type": result["doc_type"],
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


async def search_by_subject(
    query: str,
    subject: str,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Search within a specific subject."""
    results = await search_documents(query=query, subject=subject, limit=limit)
    return results.results


async def search_irish_documents(query: str, limit: int = 10) -> list[dict[str, Any]]:
    """Search Irish language documents."""
    return await search_by_subject(query, "gaeilge", limit)


async def search_cs_documents(
    query: str,
    course_code: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Search Computer Science documents."""
    results = await search_documents(
        query=query,
        subject="comp_science",
        course_code=course_code,
        limit=limit,
    )
    return results.results


# =============================================================================
# Code Embedding Flow
# =============================================================================


@cocoindex.transform_flow()
def embed_code_chunk(
    text: cocoindex.DataSlice[str],
) -> cocoindex.DataSlice[list[float]]:
    """
    Embed code using CodeBERT.

    CodeBERT provides:
    - Strong code understanding
    - Cross-language semantic similarity
    - 768-dimensional vectors
    """
    return text.transform(
        cocoindex.functions.SentenceTransformerEmbed(
            model="microsoft/codebert-base",
            batch_size=EMBEDDING_BATCH_SIZE,
        )
    )


def detect_language(file_name: str) -> str:
    """Detect programming language from file extension."""
    ext = Path(file_name).suffix.lower()
    return LANGUAGE_EXTENSIONS.get(ext, "unknown")


def should_skip_file(file_name: str) -> bool:
    """Check if file should be skipped (e.g., bytecode)."""
    ext = Path(file_name).suffix.lower()
    return ext in {".class", ".pyc", ".pyo"}


def extract_code_metadata(content: str, language: str) -> dict[str, Any]:
    """Extract metadata from code content."""
    lines = content.split("\n")
    return {
        "line_count": len(lines),
        "has_main": "main" in content.lower(),
        "has_class": "class " in content,
        "has_function": "def " in content or "function" in content or "void " in content,
        "is_test": any(kw in content.lower() for kw in ["test", "@test", "unittest"]),
    }


@cocoindex.flow_def(name="BunchlochCodeEmbedding")
def code_embedding_flow(
    flow_builder: cocoindex.FlowBuilder,
    data_scope: cocoindex.DataScope,
) -> None:
    """
    Bunchloch code embedding flow.

    Sources code from DuckDB (populated by DLT),
    chunks using Tree-sitter AST analysis,
    embeds with CodeBERT, and stores in LanceDB.
    """
    ENABLE_VECTOR_INDEX = os.environ.get("ENABLE_LANCEDB_VECTOR_INDEX", "1").lower() in (
        "true",
        "1",
    )

    data_scope["code_files"] = flow_builder.add_source(
        cocoindex.sources.DuckDB(
            connection_string="duckdb:///bunchloch.duckdb",
            query="""
                SELECT
                    file_hash as id,
                    file_path,
                    file_name,
                    subject,
                    course_code,
                    content
                FROM bunchloch.documents
                WHERE file_type = 'code'
                  AND content IS NOT NULL
                  AND file_name NOT LIKE '%.class'
            """,
        ),
        refresh_interval=datetime.timedelta(hours=1),
    )

    code_embeddings = data_scope.add_collector()

    with data_scope["code_files"].row() as file:
        file["language"] = file["file_name"].transform(detect_language)
        file["should_process"] = file["file_name"].transform(
            lambda f: not should_skip_file(f)
        )

        file["chunks"] = file["content"].transform(
            cocoindex.functions.SplitRecursively(),
            language="python",
            chunk_size=CODE_CHUNK_SIZE,
            chunk_overlap=CODE_CHUNK_OVERLAP,
        )

        with file["chunks"].row() as chunk:
            chunk["should_embed"] = chunk["text"].transform(
                lambda t: len(t.strip()) >= MIN_CHUNK_SIZE
            )
            chunk["embedding"] = embed_code_chunk(chunk["text"])
            chunk["metadata"] = chunk["text"].transform(
                lambda t: extract_code_metadata(t, file["language"])
            )

            code_embeddings.collect(
                id=cocoindex.GeneratedField.UUID,
                file_hash=file["id"],
                file_path=file["file_path"],
                file_name=file["file_name"],
                subject=file["subject"],
                course_code=file["course_code"],
                language=file["language"],
                location=chunk["location"],
                text=chunk["text"],
                line_count=chunk["metadata"]["line_count"],
                has_class=chunk["metadata"]["has_class"],
                has_function=chunk["metadata"]["has_function"],
                is_test=chunk["metadata"]["is_test"],
                embedding=chunk["embedding"],
            )

    vector_indexes = []
    if ENABLE_VECTOR_INDEX:
        vector_indexes.append(
            cocoindex.VectorIndexDef(
                field_name="embedding",
                metric=cocoindex.VectorSimilarityMetric.COSINE,
            )
        )

    code_embeddings.export(
        "bunchloch_code",
        coco_lancedb.LanceDB(
            db_uri=LANCEDB_URI,
            table_name=CODE_LANCEDB_TABLE,
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


@code_embedding_flow.query_handler(
    result_fields=cocoindex.QueryHandlerResultFields(
        embedding=["embedding"],
        score="score",
    ),
)
async def search_code(
    query: str,
    language: str | None = None,
    course_code: str | None = None,
    only_functions: bool = False,
    only_classes: bool = False,
    limit: int = 10,
) -> cocoindex.QueryOutput:
    """
    Search code with semantic understanding.

    Parameters:
        query: Search query (natural language or code snippet)
        language: Filter by programming language
        course_code: Filter by course code
        only_functions: Only return function definitions
        only_classes: Only return class definitions
        limit: Maximum results

    Returns:
        Matching code chunks with similarity scores
    """
    db = await coco_lancedb.connect_async(LANCEDB_URI)
    table = await db.open_table(CODE_LANCEDB_TABLE)

    query_embedding = await embed_code_chunk.eval_async(query)
    search = await table.search(query_embedding, vector_column_name="embedding")

    filter_conditions = []
    if language:
        filter_conditions.append(f"language = '{language}'")
    if course_code:
        filter_conditions.append(f"course_code = '{course_code}'")
    if only_functions:
        filter_conditions.append("has_function = true")
    if only_classes:
        filter_conditions.append("has_class = true")

    if filter_conditions:
        search = search.where(" AND ".join(filter_conditions))

    search_results = await search.limit(limit).to_list()

    return cocoindex.QueryOutput(
        results=[
            {
                "id": result["id"],
                "file_name": result["file_name"],
                "course_code": result["course_code"],
                "language": result["language"],
                "text": result["text"],
                "line_count": result["line_count"],
                "has_class": result["has_class"],
                "has_function": result["has_function"],
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


async def find_similar_code(
    code_snippet: str,
    exclude_file: str | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """
    Find similar code patterns across the codebase.

    Useful for:
    - Finding implementation patterns
    - Detecting similar solutions across assignments
    - Learning from existing code
    """
    results = await search_code(query=code_snippet, limit=limit + 1)

    if exclude_file:
        results.results = [r for r in results.results if r["file_name"] != exclude_file]

    return results.results[:limit]


async def search_java_code(
    query: str,
    course_code: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Search Java code specifically."""
    results = await search_code(
        query=query,
        language="java",
        course_code=course_code,
        limit=limit,
    )
    return results.results


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Document embedding
    "document_embedding_flow",
    "embed_document_chunk",
    "search_documents",
    "search_by_subject",
    "search_irish_documents",
    "search_cs_documents",
    "extract_document_type",
    "extract_subject",
    "extract_course_code",
    # Code embedding
    "code_embedding_flow",
    "embed_code_chunk",
    "search_code",
    "find_similar_code",
    "search_java_code",
    "detect_language",
    "should_skip_file",
    "extract_code_metadata",
    # Configuration
    "LANCEDB_URI",
    "EMBEDDING_BATCH_SIZE",
]
