"""
Author Archive Embedding Flow.

CocoIndex flow that:
  1. Reads the 3 dlt-populated DuckDB tables (UoG, Gemini, equations)
  2. Chunks semantically (`SplitRecursively`, language=markdown)
  3. Embeds with `BAAI/bge-large-en-v1.5` (English-only, 1024-d)
  4. Writes to LanceDB with IVF_HNSW + FTS indexes
  5. Exposes a `search_author_archive` query handler for semantic search

Mirrors `oideachais/cocoindex_flows/research_embedding.py:125` (the
canonical pattern) and re-uses:
  - `oideachais/cocoindex_flows/research_embedding.py:31` for `LANCEDB_URI`
  - The dlt-populated tables in DuckDB as the canonical source of truth
  - The LanceDB REST API at `lance-api.cianfhoghlaim.ie` as the target

CRITICAL CONSTRAINTS (per `oideachais/cocoindex_flows/curriculum_embedding.py`):
  - Embedding batching: MANDATORY minimum 100 per call
  - HNSW indexes: DROP before bulk inserts >50 rows, recreate after
  - DuckDB: Single-threaded access only

Reference: openspec/changes/author-archive-gemini-and-uos-ingestion/
"""

from __future__ import annotations

import datetime
import os
import re
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

# CocoIndex is optional — the module-level import is guarded so that the file
# can be imported for type-checking or unit tests even when CocoIndex isn't on
# the workstation.
try:
    import cocoindex
    import cocoindex.targets.lancedb as coco_lancedb

    COCOINDEX_AVAILABLE = True
except ImportError:
    COCOINDEX_AVAILABLE = False
    cocoindex = None  # type: ignore[assignment]
    coco_lancedb = None  # type: ignore[assignment]


# =============================================================================
# Configuration
# =============================================================================


# Re-use the same LanceDB REST endpoint as the research flow.
LANCEDB_URI = os.getenv(
    "LANCEDB_URI",
    "rest://lance-api.cianfhoghlaim.ie",
)

# English-only embedding model (per the user).
EN_MODEL = "BAAI/bge-large-en-v1.5"
EMBEDDING_DIM = 1024

# LanceDB table names.
GEMINI_TABLE = "author_archive_gemini"
UOG_TABLE = "author_archive_uog_documents"
UOG_CODE_TABLE = "author_archive_uog_code"
UOG_EQN_TABLE = "author_archive_equations"

# Chunk sizes per content kind.
GEMINI_CHUNK_SIZE = 800
GEMINI_CHUNK_OVERLAP = 150
UOG_CHUNK_SIZE = 800
UOG_CHUNK_OVERLAP = 150
CODE_CHUNK_SIZE = 1200
CODE_CHUNK_OVERLAP = 200
MIN_CHUNK_SIZE = 100

# MANDATORY: minimum batch size for embeddings (100x performance difference).
EMBEDDING_BATCH_SIZE = 100


# Default DuckDB paths — same convention as the research flow.
DEFAULT_DUCKDB_PATH = os.getenv(
    "AUTHOR_ARCHIVE_DUCKDB_PATH",
    str(Path.cwd() / "storage" / "data" / "author_archive.duckdb"),
)


# =============================================================================
# Embedding helper
# =============================================================================


if COCOINDEX_AVAILABLE:

    @cocoindex.transform_flow()
    def embed_text_chunk(
        text: cocoindex.DataSlice[str],
    ) -> cocoindex.DataSlice[list[float]]:
        """
        Embed text using `BAAI/bge-large-en-v1.5`.

        English-only, 1024-d. Same dimension as the existing BGE-M3 flow so
        the LanceDB IVF_HNSW + FTS indexes can be reused.
        """
        return text.transform(
            cocoindex.functions.SentenceTransformerEmbed(
                model=EN_MODEL,
                batch_size=EMBEDDING_BATCH_SIZE,
            )
        )

    @cocoindex.transform_flow()
    def embed_code_chunk(
        text: cocoindex.DataSlice[str],
    ) -> cocoindex.DataSlice[list[float]]:
        """Embed code with the same English model (no separate CodeBERT here).

        CodeBERT is on the existing `bunchloch_code` table — for `author_archive`
        we keep a single embedding model for simplicity and cosine parity.
        """
        return text.transform(
            cocoindex.functions.SentenceTransformerEmbed(
                model=EN_MODEL,
                batch_size=EMBEDDING_BATCH_SIZE,
            )
        )


# =============================================================================
# Metadata extractors
# =============================================================================


def extract_artifact_kind(file_path: str, file_name: str) -> str:
    """Heuristic artefact-kind label from path + filename."""
    name_lower = file_name.lower()
    path_lower = file_path.lower()
    if "placement" in name_lower or "placement" in path_lower:
        return "placement"
    if any(kw in name_lower for kw in ["assignment", "homework", "project"]):
        return "assignment"
    if any(kw in name_lower for kw in ["exam", "test", "quiz"]):
        return "exam"
    if any(kw in name_lower for kw in ["lecture", "notes", "class"]):
        return "lecture"
    if any(kw in name_lower for kw in ["action_research", "action-research"]):
        return "action_research"
    if any(kw in name_lower for kw in [".java", ".py", ".ipynb", ".js", ".ts"]):
        return "code"
    return "document"


def extract_course_code(file_path: str) -> str | None:
    """Extract a course code (e.g. `CT511`, `GA101`, `ed305`) from a path."""
    match = re.search(r"([A-Za-z]{2,3})(\d{3,4})", file_path)
    if match:
        return f"{match.group(1).upper()}{match.group(2)}"
    return None


# =============================================================================
# Flow 1 — Gemini Deep Research embeddings
# =============================================================================


if COCOINDEX_AVAILABLE:

    @cocoindex.flow(name="AuthorArchiveGeminiEmbedding")
    def gemini_embedding_flow(
        flow_builder: cocoindex.FlowBuilder,
        data_scope: cocoindex.DataScope,
    ) -> None:
        """
        Gemini Deep Research embedding flow.

        Source: DuckDB `oideachais.author_archive_gemini.documents` (populated
        by the dlt `gemini_deep_research_source`). Chunks with
        `SplitRecursively(language="markdown")` because Gemini's deep-research
        output is markdown-flavoured. Embeds with BGE-large-en-v1.5.
        """
        enable_vector_index = os.environ.get("ENABLE_LANCEDB_VECTOR_INDEX", "1").lower() in (
            "true",
            "1",
        )

        data_scope["gemini_documents"] = flow_builder.add_source(
            cocoindex.sources.DuckDB(
                connection_string=f"duckdb:///{DEFAULT_DUCKDB_PATH}",
                query="""
                    SELECT
                        file_hash as id,
                        file_path,
                        file_name,
                        domain,
                        gemini_first_page_heading,
                        content
                    FROM author_archive_gemini.documents
                    WHERE file_type = 'pdf'
                      AND content IS NOT NULL
                """,
            ),
            refresh_interval=datetime.timedelta(hours=6),
        )

        gemini_embeddings = data_scope.add_collector()

        with data_scope["gemini_documents"].row() as doc:
            doc["chunks"] = doc["content"].transform(
                cocoindex.functions.SplitRecursively(),
                language="markdown",
                chunk_size=GEMINI_CHUNK_SIZE,
                chunk_overlap=GEMINI_CHUNK_OVERLAP,
                separators=["\n\n\n", "\n\n", "\n", ". ", " "],
            )

            with doc["chunks"].row() as chunk:
                chunk["embedding"] = embed_text_chunk(chunk["text"])
                gemini_embeddings.collect(
                    id=cocoindex.GeneratedField.UUID,
                    file_hash=doc["id"],
                    file_path=doc["file_path"],
                    file_name=doc["file_name"],
                    account="gemini_deep_research",
                    domain=doc["domain"],
                    first_page_heading=doc["gemini_first_page_heading"],
                    location=chunk["location"],
                    text=chunk["text"],
                    embedding=chunk["embedding"],
                )

        vector_indexes = []
        if enable_vector_index:
            vector_indexes.append(
                cocoindex.VectorIndexDef(
                    field_name="embedding",
                    metric=cocoindex.VectorSimilarityMetric.COSINE,
                    index_type="IVF_HNSW",
                    num_partitions=256,
                    num_sub_vectors=32,
                )
            )

        gemini_embeddings.export(
            "author_archive_gemini",
            coco_lancedb.LanceDB(
                db_uri=LANCEDB_URI,
                table_name=GEMINI_TABLE,
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


# =============================================================================
# Flow 2 — University of Galway document embeddings
# =============================================================================


if COCOINDEX_AVAILABLE:

    @cocoindex.flow(name="AuthorArchiveUoGEmbedding")
    def uog_embedding_flow(
        flow_builder: cocoindex.FlowBuilder,
        data_scope: cocoindex.DataScope,
    ) -> None:
        """
        UoG document embedding flow.

        Source: DuckDB `oideachais.author_archive_uog.documents` (populated by
        `university_of_galway_source`). Same BGE-large-en-v1.5 model.
        """
        enable_vector_index = os.environ.get("ENABLE_LANCEDB_VECTOR_INDEX", "1").lower() in (
            "true",
            "1",
        )

        data_scope["uog_documents"] = flow_builder.add_source(
            cocoindex.sources.DuckDB(
                connection_string=f"duckdb:///{DEFAULT_DUCKDB_PATH}",
                query="""
                    SELECT
                        file_hash as id,
                        file_path,
                        file_name,
                        subject,
                        domain,
                        course_code,
                        content
                    FROM author_archive_uog.documents
                    WHERE file_type IN ('pdf', 'word')
                      AND content IS NOT NULL
                """,
            ),
            refresh_interval=datetime.timedelta(hours=6),
        )

        uog_embeddings = data_scope.add_collector()

        with data_scope["uog_documents"].row() as doc:
            doc["chunks"] = doc["content"].transform(
                cocoindex.functions.SplitRecursively(),
                language="markdown",
                chunk_size=UOG_CHUNK_SIZE,
                chunk_overlap=UOG_CHUNK_OVERLAP,
                separators=["\n\n\n", "\n\n", "\n", ". ", " "],
            )

            with doc["chunks"].row() as chunk:
                chunk["embedding"] = embed_text_chunk(chunk["text"])
                uog_embeddings.collect(
                    id=cocoindex.GeneratedField.UUID,
                    file_hash=doc["id"],
                    file_path=doc["file_path"],
                    file_name=doc["file_name"],
                    account="university_of_galway",
                    domain=doc["domain"],
                    subject=doc["subject"],
                    course_code=doc["course_code"],
                    artifact_kind=doc["file_path"].transform(
                        lambda p: extract_artifact_kind(p, doc["file_name"])
                    ),
                    location=chunk["location"],
                    text=chunk["text"],
                    embedding=chunk["embedding"],
                )

        vector_indexes = []
        if enable_vector_index:
            vector_indexes.append(
                cocoindex.VectorIndexDef(
                    field_name="embedding",
                    metric=cocoindex.VectorSimilarityMetric.COSINE,
                    index_type="IVF_HNSW",
                    num_partitions=256,
                    num_sub_vectors=32,
                )
            )

        uog_embeddings.export(
            "author_archive_uog",
            coco_lancedb.LanceDB(
                db_uri=LANCEDB_URI,
                table_name=UOG_TABLE,
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


# =============================================================================
# Flow 3 — UoG code embeddings (smaller, separate table)
# =============================================================================


if COCOINDEX_AVAILABLE:

    @cocoindex.flow(name="AuthorArchiveUoGCodeEmbedding")
    def uog_code_embedding_flow(
        flow_builder: cocoindex.FlowBuilder,
        data_scope: cocoindex.DataScope,
    ) -> None:
        """
        UoG code embedding flow (`software_development/` subdir).
        """
        enable_vector_index = os.environ.get("ENABLE_LANCEDB_VECTOR_INDEX", "1").lower() in (
            "true",
            "1",
        )

        data_scope["uog_code"] = flow_builder.add_source(
            cocoindex.sources.DuckDB(
                connection_string=f"duckdb:///{DEFAULT_DUCKDB_PATH}",
                query="""
                    SELECT
                        file_hash as id,
                        file_path,
                        file_name,
                        subject,
                        course_code,
                        content
                    FROM author_archive_uog.documents
                    WHERE file_type = 'code'
                      AND content IS NOT NULL
                      AND file_name NOT LIKE '%.class'
                """,
            ),
            refresh_interval=datetime.timedelta(hours=1),
        )

        code_embeddings = data_scope.add_collector()

        with data_scope["uog_code"].row() as file:
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
                code_embeddings.collect(
                    id=cocoindex.GeneratedField.UUID,
                    file_hash=file["id"],
                    file_path=file["file_path"],
                    file_name=file["file_name"],
                    account="university_of_galway",
                    subject=file["subject"],
                    course_code=file["course_code"],
                    location=chunk["location"],
                    text=chunk["text"],
                    embedding=chunk["embedding"],
                )

        vector_indexes = []
        if enable_vector_index:
            vector_indexes.append(
                cocoindex.VectorIndexDef(
                    field_name="embedding",
                    metric=cocoindex.VectorSimilarityMetric.COSINE,
                )
            )

        code_embeddings.export(
            "author_archive_uog_code",
            coco_lancedb.LanceDB(
                db_uri=LANCEDB_URI,
                table_name=UOG_CODE_TABLE,
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


# =============================================================================
# Flow 4 — Handwritten equation embeddings
# =============================================================================


if COCOINDEX_AVAILABLE:

    @cocoindex.flow(name="AuthorArchiveEquationsEmbedding")
    def equations_embedding_flow(
        flow_builder: cocoindex.FlowBuilder,
        data_scope: cocoindex.DataScope,
    ) -> None:
        """
        Handwritten-equation embedding flow.

        Source: DuckDB `oideachais.author_archive.equations` (populated by the
        OCR chain in `oideachais/ocr/author_archive_ocr.py`).
        """
        enable_vector_index = os.environ.get("ENABLE_LANCEDB_VECTOR_INDEX", "1").lower() in (
            "true",
            "1",
        )

        data_scope["equations"] = flow_builder.add_source(
            cocoindex.sources.DuckDB(
                connection_string=f"duckdb:///{DEFAULT_DUCKDB_PATH}",
                query="""
                    SELECT
                        md5(concat(file_path, ':', verbatim)) as id,
                        file_path,
                        latex,
                        verbatim,
                        context,
                        confidence
                    FROM author_archive.equations
                    WHERE latex IS NOT NULL AND length(trim(latex)) > 0
                """,
            ),
            refresh_interval=datetime.timedelta(hours=24),
        )

        eqn_embeddings = data_scope.add_collector()

        with data_scope["equations"].row() as row:
            row["combined_text"] = (
                row["latex"]
                .transform(lambda s: s)
                .transform(lambda s: f"{s}\n\n{row['verbatim']}\n\n{row['context']}")
            )
            row["embedding"] = embed_text_chunk(row["combined_text"])
            eqn_embeddings.collect(
                id=row["id"],
                file_path=row["file_path"],
                latex=row["latex"],
                verbatim=row["verbatim"],
                context=row["context"],
                confidence=row["confidence"],
                embedding=row["embedding"],
            )

        vector_indexes = []
        if enable_vector_index:
            vector_indexes.append(
                cocoindex.VectorIndexDef(
                    field_name="embedding",
                    metric=cocoindex.VectorSimilarityMetric.COSINE,
                )
            )

        eqn_embeddings.export(
            "author_archive_equations",
            coco_lancedb.LanceDB(
                db_uri=LANCEDB_URI,
                table_name=UOG_EQN_TABLE,
            ),
            primary_key_fields=["id"],
            vector_indexes=vector_indexes,
            fts_indexes=[
                cocoindex.FtsIndexDef(
                    field_name="latex",
                    parameters={"tokenizer_name": "simple"},
                )
            ],
        )


# =============================================================================
# Query handler — search across all 4 tables
# =============================================================================


if COCOINDEX_AVAILABLE:

    async def _search_single_table(
        *,
        table_name: str,
        query_embedding: list[float],
        account: str | None,
        domain: str | None,
        course_code: str | None,
        artifact_kind: str | None,
        limit: int,
    ) -> list[dict[str, Any]]:
        """Run a vector search on a single LanceDB table with the given filters."""
        db = await coco_lancedb.connect_async(LANCEDB_URI)
        table = await db.open_table(table_name)
        search = table.search(query_embedding, vector_column_name="embedding")
        conditions: list[str] = []
        if account:
            conditions.append(f"account = '{account}'")
        if domain:
            conditions.append(f"domain = '{domain}'")
        if course_code:
            conditions.append(f"course_code = '{course_code}'")
        if artifact_kind:
            conditions.append(f"artifact_kind = '{artifact_kind}'")
        if conditions:
            search = search.where(" AND ".join(conditions))
        return await search.limit(limit).to_list()

    async def _search_author_archive_impl(
        query: str,
        account: str | None = None,
        domain: str | None = None,
        artifact_kind: str | None = None,
        course_code: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Union search across the 4 author-archive tables.

        Returns a single list of dicts, ranked by cosine similarity, with
        each row tagged with the source table name.
        """
        if not COCOINDEX_AVAILABLE:
            logger.warning("cocoindex_not_available_search_disabled")
            return []

        query_embedding = await embed_text_chunk.eval_async(query)

        # Pick the right table(s) based on filters.
        tables_to_search: list[str] = []
        if artifact_kind == "equation":
            tables_to_search = [UOG_EQN_TABLE]
        else:
            tables_to_search = [GEMINI_TABLE, UOG_TABLE, UOG_CODE_TABLE]
            if account == "university_of_galway":
                tables_to_search = [UOG_TABLE, UOG_CODE_TABLE]
            elif account == "gemini_deep_research":
                tables_to_search = [GEMINI_TABLE]

        per_table_limit = max(limit, 5)
        all_results: list[dict[str, Any]] = []
        for table_name in tables_to_search:
            try:
                rows = await _search_single_table(
                    table_name=table_name,
                    query_embedding=query_embedding,
                    account=account,
                    domain=domain,
                    course_code=course_code,
                    artifact_kind=artifact_kind,
                    limit=per_table_limit,
                )
                for r in rows:
                    r["_source_table"] = table_name
                    r["score"] = 1.0 - r.get("_distance", 0.0)
                    all_results.append(r)
            except (OSError, ValueError, RuntimeError) as e:
                logger.warning(
                    "author_archive_table_search_failed",
                    table=table_name,
                    error=str(e),
                )

        # Sort by score, take top `limit`.
        all_results.sort(key=lambda r: r.get("score", 0.0), reverse=True)
        return all_results[:limit]

    # Register the canonical `@query_handler` symbol.
    if hasattr(gemini_embedding_flow, "query_handler"):

        @gemini_embedding_flow.query_handler(  # type: ignore[attr-defined]
            result_fields=cocoindex.QueryHandlerResultFields(
                embedding=["embedding"],
                score="score",
            ),
        )
        async def search_author_archive(
            query: str,
            account: str | None = None,
            domain: str | None = None,
            artifact_kind: str | None = None,
            course_code: str | None = None,
            limit: int = 10,
        ) -> cocoindex.QueryOutput:
            """
            Author-archive semantic search.

            Parameters:
                query: Search query (English natural language).
                account: Filter by `account` (`university_of_galway` | `gemini_deep_research` | `<takeout-label>`).
                domain: Filter by domain (e.g. `law`, `education`, `irish`).
                artifact_kind: Filter by artefact kind (`assignment`, `exam`, `code`, `equation`, ...).
                course_code: Filter by UoG course code (e.g. `ed305`, `ga101`).
                limit: Maximum results (default 10).
            """
            results = await _search_author_archive_impl(
                query=query,
                account=account,
                domain=domain,
                artifact_kind=artifact_kind,
                course_code=course_code,
                limit=limit,
            )
            query_embedding = await embed_text_chunk.eval_async(query)
            return cocoindex.QueryOutput(
                results=results,
                query_info=cocoindex.QueryInfo(
                    embedding=query_embedding,
                    similarity_metric=cocoindex.VectorSimilarityMetric.COSINE,
                ),
            )

    else:
        # CocoIndex version where `query_handler` isn't supported on the
        # outermost flow — fall back to a module-level alias.
        search_author_archive = _search_author_archive_impl  # type: ignore[assignment]


# =============================================================================
# Standalone runner
# =============================================================================


async def run_gemini_embedding() -> dict[str, Any]:
    """Run the Gemini embedding flow standalone (test/dev only)."""
    if not COCOINDEX_AVAILABLE:
        return {"status": "skipped", "reason": "cocoindex not installed"}
    result = await gemini_embedding_flow.evaluate_and_dump()  # type: ignore[attr-defined]
    return {"status": "success", "result": str(result)}


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "EN_MODEL",
    "EMBEDDING_DIM",
    "EMBEDDING_BATCH_SIZE",
    "LANCEDB_URI",
    "DEFAULT_DUCKDB_PATH",
    "GEMINI_TABLE",
    "UOG_TABLE",
    "UOG_CODE_TABLE",
    "UOG_EQN_TABLE",
    "COCOINDEX_AVAILABLE",
    # Flow definitions (only meaningful when cocoindex is installed)
    "gemini_embedding_flow",
    "uog_embedding_flow",
    "uog_code_embedding_flow",
    "equations_embedding_flow",
    # Query handler
    "search_author_archive",
    # Helpers
    "extract_artifact_kind",
    "extract_course_code",
    "run_gemini_embedding",
]
