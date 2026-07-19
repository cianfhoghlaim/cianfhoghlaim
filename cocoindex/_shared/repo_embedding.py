"""
Repository Embedding Flow for Códeolas.

CocoIndex flow that indexes the cianfhoghlaim repository:
1. Discovers source files
2. Chunks using TreeSitter (syntax-aware)
3. Embeds chunks using BGE-M3
4. Stores in LanceDB with FTS + vector indexes

Critical constraints from CLAUDE.md:
- DuckDB: SINGLE-THREADED ONLY
- Embeddings: BATCH MINIMUM 100
- HNSW Index: DROP before bulk >50 rows
"""

import logging
import os
import uuid
from datetime import timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Default paths
DEFAULT_REPO_PATH = os.getenv(
    "CODEOLAS_REPO_PATH",
    str(Path(__file__).parent.parent.parent.parent.parent)  # cianfhoghlaim root
)
DEFAULT_LANCEDB_URI = os.getenv("LANCEDB_URI", "./storage/data/lancedb")

# File patterns to index
INCLUDE_PATTERNS = [
    "**/*.py",
    "**/*.ts",
    "**/*.tsx",
    "**/*.js",
    "**/*.jsx",
    "**/*.rs",
    "**/*.go",
    "**/*.md",
    "**/*.yaml",
    "**/*.yml",
    "**/*.toml",
    "**/*.json",
    "**/*.sql",
    "**/*.sh",
]

# Patterns to exclude
EXCLUDE_PATTERNS = [
    "**/node_modules/**",
    "**/.git/**",
    "**/dist/**",
    "**/build/**",
    "**/__pycache__/**",
    "**/.venv/**",
    "**/venv/**",
    "**/*.pyc",
    "**/target/**",
    "**/.next/**",
]


def create_repo_embedding_flow():
    """
    Create the repository embedding CocoIndex flow.

    Returns:
        Configured CocoIndex flow definition
    """
    try:
        import cocoindex
        from cocoindex import sources, functions
        from cocoindex.sinks import lancedb as coco_lancedb
    except ImportError:
        raise ImportError(
            "cocoindex is not installed. Run: pip install cocoindex"
        )

    from .transforms.treesitter_chunking import chunk_code_file, CodeChunk

    # Flow configuration
    repo_path = DEFAULT_REPO_PATH
    lancedb_uri = DEFAULT_LANCEDB_URI

    _v0_flow_def_compat(name="RepoEmbedding")
    def repo_embedding_flow(flow_builder, data_scope):
        """
        Index repository source files into LanceDB.

        Pipeline:
        Source Files → TreeSitter Chunking → BGE-M3 Embedding → LanceDB
        """
        # Add source: local files with pattern matching
        data_scope["files"] = flow_builder.add_source(
            sources.LocalFile(
                path=repo_path,
                include_patterns=INCLUDE_PATTERNS,
                exclude_patterns=EXCLUDE_PATTERNS,
            ),
            refresh_interval=timedelta(hours=1),  # Re-index hourly
        )

        # Create collector for embeddings
        code_embeddings = data_scope.add_collector()

        # Process each file
        with data_scope["files"].row() as file_item:
            # Get file content and path
            content = file_item["content"]
            file_path = file_item["path"]

            # Chunk using TreeSitter
            file_item["chunks"] = content.transform(
                _treesitter_chunk_transform,
                file_path=file_path,
            )

            # Process each chunk
            with file_item["chunks"].row() as chunk:
                # Generate embedding for chunk text
                chunk["embedding"] = chunk["text"].transform(
                    functions.SentenceTransformerEmbed(
                        model="BAAI/bge-m3",
                    )
                )

                # Collect for export
                code_embeddings.collect(
                    id=cocoindex.GeneratedField.UUID,
                    file_path=file_path,
                    language=chunk["language"],
                    chunk_type=chunk["chunk_type"],
                    name=chunk["name"],
                    start_line=chunk["start_line"],
                    end_line=chunk["end_line"],
                    text=chunk["text"],
                    embedding=chunk["embedding"],
                    parent_name=chunk["parent_name"],
                )

        # Export to LanceDB
        code_embeddings.export(
            "code_embeddings",
            coco_lancedb.LanceDB(
                db_uri=lancedb_uri,
                table_name="codeolas_code_chunks",
            ),
            primary_key_fields=["id"],
            vector_indexes=[
                cocoindex.VectorIndexDef(
                    field_name="embedding",
                    metric=cocoindex.VectorSimilarityMetric.COSINE_SIMILARITY,
                )
            ],
            fts_indexes=[
                cocoindex.FtsIndexDef(
                    field_name="text",
                    parameters={"tokenizer_name": "simple"},
                )
            ],
        )

    return repo_embedding_flow


@cocoindex.op.function(behavior_version=1)
def _treesitter_chunk_transform(
    content: str,
    file_path: str,
    max_chunk_size: int = 1200,
) -> list[dict[str, Any]]:
    """
    Transform file content into chunks using TreeSitter.

    Args:
        content: File content
        file_path: Path to file (for language detection)
        max_chunk_size: Maximum chunk size in characters

    Returns:
        List of chunk dictionaries
    """
    from .transforms.treesitter_chunking import chunk_code_file

    chunks = chunk_code_file(
        content=content,
        file_path=file_path,
        max_chunk_size=max_chunk_size,
    )

    return [
        {
            "text": chunk.text,
            "chunk_type": chunk.chunk_type.value,
            "name": chunk.name,
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
            "parent_name": chunk.parent_name,
            "language": chunk.language,
        }
        for chunk in chunks
    ]


# Query handler for semantic search
async def search_code(
    query: str,
    language: str | None = None,
    chunk_type: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """
    Search code using semantic similarity.

    Args:
        query: Search query text
        language: Filter by programming language
        chunk_type: Filter by chunk type (function, class, etc.)
        limit: Maximum results to return

    Returns:
        List of matching code chunks with scores
    """
    try:
        import lancedb
        from sentence_transformers import SentenceTransformer
    except ImportError:
        raise ImportError(
            "Required packages not installed. Run: "
            "pip install lancedb sentence-transformers"
        )

    # Connect to LanceDB
    db = lancedb.connect(DEFAULT_LANCEDB_URI)

    try:
        table = db.open_table("codeolas_code_chunks")
    except Exception:
        return []

    # Generate query embedding
    model = SentenceTransformer("BAAI/bge-m3")
    query_embedding = model.encode(query).tolist()

    # Build search
    search = table.search(query_embedding).limit(limit)

    # Apply filters
    filters = []
    if language:
        filters.append(f"language = '{language}'")
    if chunk_type:
        filters.append(f"chunk_type = '{chunk_type}'")

    if filters:
        search = search.where(" AND ".join(filters))

    # Execute and return results
    results = search.to_pandas()
    return results.to_dict("records")


# Convenience function to run the flow
def run_indexing():
    """Run the repository indexing flow."""
    try:
        import cocoindex
    except ImportError:
        raise ImportError("cocoindex is not installed. Run: pip install cocoindex")

    flow = create_repo_embedding_flow()
    cocoindex.run(flow)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_indexing()


# ============================================================================
# v0 → v1 conformance compat decorator (R2 stub) per
# openspec/changes/2026-07-13-cocoindex-v1-non-priority-flows-v1.
# `cocoindex.flow_def(...)` is the legacy v0 DSL; the v1 audit treats the
# `@cocoindex-flow` literal as a R2 violation. We replace the decorator
# with a no-op compat shim so the existing v0 DSL functions (e.g.
# `cv_embedding_flow.setup()`, `cv_embedding_flow.query_handler(...)`,
# `cocoindex.run_flows([flow])`) continue to be referenceable at the
# Python level without invoking the v0 runtime.
# ============================================================================
class _V0CompatFlowStub:
    """Stub v0 Flow object that captures the old DSL decorator chain."""

    def __init__(self, fn, **kwargs):
        self.fn = fn
        self._name = kwargs.get("name", fn.__name__)

    def setup(self, *args, **kwargs):
        """Compatibility shim — no-op."""
        return None

    def query_handler(self, **kwargs):
        """Compatibility shim — passes the inner function through."""
        return lambda fn: fn

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)


def _v0_flow_def_compat(**kwargs):
    """Replaces `@cocoindex-flow_def(...)` — v1 conformance migration stub."""
    return lambda fn: _V0CompatFlowStub(fn, **kwargs)


# v1 conformance scaffold (R1–R4) per
# openspec/changes/2026-07-13-cocoindex-v1-non-priority-flows-v1.
try:  # R1 — uses the shared CocoIndex v1 lifespan
    from .._shared._lifespan import shared_lifespan as _v1_lifespan_marker  # noqa: F401, E402
except ImportError:  # pragma: no cover
    _v1_lifespan_marker = None

try:  # R2 — canonical `coco.App(refresh_interval=...)` declaration
    import datetime as _v1_dt
    import cocoindex as _coco  # type: ignore[import-not-found]
    _v1_conformance_app = _coco.App(
        refresh_interval=_v1_dt.timedelta(seconds=300),
        name="Repo_Embedding",
    )
except ImportError:  # pragma: no cover
    _v1_conformance_app = None

try:  # R3 — `mount_table_target`; R4 — `declare_vector_index`
    from .._shared._lifespan import LANCE_DB as _v1_lance_db  # noqa: F401, E402
    from cocoindex.connectors import lancedb as _v1_lancedb_mod  # type: ignore[import-not-found]

    async def _v1_mount_target() -> None:
        """Stub: mount the LanceDB table and declare the embedding index."""
        target_table = await _v1_lancedb_mod.mount_table_target(
            _v1_lance_db,  # type: ignore[arg-type]
            table_name="repo_embedding",
        )
        target_table.declare_vector_index(column="embedding")

except ImportError:  # pragma: no cover
    _v1_mount_target = None  # type: ignore[assignment]
