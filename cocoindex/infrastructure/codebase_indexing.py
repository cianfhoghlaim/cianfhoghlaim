"""
Codebase Indexing CocoIndex v1 App — the v1-native replacement for `ccc`.

The legacy `ccc` CLI is a wrapper around a separate CocoIndex code example
that lives in a different runtime from the rest of the data lakehouse. This
App brings the codebase semantic index onto the same primitives as every
other CocoIndex flow in this repo:

- `@coco.fn` + `@coco.fn(memo=True)` for processing
- `localfs.walk_dir(repo_root, live=True, refresh_interval=60s)` for the source
- `RecursiveSplitter` with `detect_code_language` for chunking
- `SentenceTransformerEmbedder("BAAI/bge-m3")` for embedding (shared with
  `docs_skills_consolidation.py` for consistency)
- `lancedb.mount_table_target("codebase_chunks", ...)` for the output

Code graph extraction (round 8 + phase 1):
- 7 node types (FILE, FUNCTION, CLASS, METHOD, MODULE, INTERFACE, VARIABLE)
- 7 edge types (CONTAINS, IMPORTS, CALLS, EXTENDS, IMPLEMENTS, USES, DEFINES)
- Tree-sitter AST extraction per file
- 29+ language detection via `cianfhoghlaim.cocoindex_flows.chunking.languages`

Reference pattern: `docs/cocoindex/code_embedding/main.py` (v0 reference) +
`docs/cocoindex/pdf_embedding/main.py` (v1 chunking/embedding conventions).

Operational contract:
- Live mode (`cocoindex update -L ...`) is supported.
- Excludes protect the indexer from indexing its own reference mirror
  (`docs/cocoindex/`), build artefacts (`.venv/`, `node_modules/`, `dist/`),
  and the local CocoaIndex code DB (`.cocoindex_code/`).
- Tree-sitter chunking honours `DetectProgrammingLanguage` for code-aware
  splits; Markdown uses the recursive splitter.
- HNSW index on the `embedding` column follows the platform rule
  `HNSW_DROP_THRESHOLD = 50` (drop before bulk >50 rows, recreate after).
"""

from __future__ import annotations

import datetime
import os
import pathlib
from collections.abc import AsyncIterator
from dataclasses import dataclass
from enum import Enum
from typing import Annotated, Any

import structlog

from .chunking.languages import EXTENSION_TO_LANGUAGE, get_supported_languages

logger = structlog.get_logger(__name__)

# CocoIndex is optional — degrade gracefully if not installed.
try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import (
        lancedb,  # type: ignore[import-not-found]
        localfs,  # type: ignore[import-not-found]
    )
    from cocoindex.ops.sentence_transformers import (  # type: ignore[import-not-found]
        SentenceTransformerEmbedder,
    )
    from cocoindex.ops.text import (  # type: ignore[import-not-found]
        RecursiveSplitter,
        detect_code_language,
    )
    from cocoindex.resources.file import (  # type: ignore[import-not-found]
        FileLike,
        PatternFilePathMatcher,
    )
    from cocoindex.resources.id import IdGenerator  # type: ignore[import-not-found]

    COCOINDEX_AVAILABLE = True
except ImportError as e:
    logger.warning("cocoindex_v1_not_available: %s", e)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]
    localfs = None  # type: ignore[assignment]
    SentenceTransformerEmbedder = None  # type: ignore[assignment]
    RecursiveSplitter = None  # type: ignore[assignment]
    detect_code_language = None  # type: ignore[assignment]
    FileLike = None  # type: ignore[assignment]
    PatternFilePathMatcher = None  # type: ignore[assignment]
    IdGenerator = None  # type: ignore[assignment]


# =============================================================================
# Configuration
# =============================================================================


LANCEDB_URI = os.getenv("LANCEDB_URI", "rest://lance-api.cianfhoghlaim.ie")
EMBED_MODEL = os.getenv("CODEBASE_EMBED_MODEL", "BAAI/bge-m3")
EMBED_DIM = 1024
REFRESH_INTERVAL = datetime.timedelta(seconds=int(os.getenv("CODEBASE_REFRESH_SECS", "60")))
LANCEDB_TABLE = "codebase_chunks"
LANCEDB_GRAPH_TABLE = "codebase_graph"
TOP_K = 10

# Default source root: the monorepo root (parents[5] = repo root from
# cianfhoghlaim/cocoindex_flows/codebase_indexing.py).
DEFAULT_REPO_ROOT = pathlib.Path(
    os.getenv(
        "CODEBASE_REPO_ROOT",
        str(pathlib.Path(__file__).resolve().parents[5]),
    )
)


# =============================================================================
# Code graph data model (round 8 + phase 1: 7 node types + 7 edge types)
# =============================================================================


class CodeNodeType(str, Enum):
    """7 canonical node types for the codebase knowledge graph.

    Ported from `codeolas/cocoindex_flows/file_graph.py:NodeType`."""

    FILE = "File"
    FUNCTION = "Function"
    CLASS = "Class"
    METHOD = "Method"
    MODULE = "Module"
    INTERFACE = "Interface"
    VARIABLE = "Variable"


class CodeEdgeType(str, Enum):
    """7 canonical edge types for the codebase knowledge graph.

    Ported from `codeolas/cocoindex_flows/file_graph.py:EdgeType`."""

    CONTAINS = "CONTAINS"
    IMPORTS = "IMPORTS"
    CALLS = "CALLS"
    EXTENDS = "EXTENDS"
    IMPLEMENTS = "IMPLEMENTS"
    USES = "USES"
    DEFINES = "DEFINES"


# Per-language Tree-sitter node type mappings for AST extraction.
# Ported from `codeolas/cocoindex_flows/file_graph.py:_extract_from_node`.
_LANG_AST_NODE_TYPES: dict[str, dict[str, CodeNodeType | None]] = {
    "python": {
        "function_definition": CodeNodeType.FUNCTION,
        "class_definition": CodeNodeType.CLASS,
        "import_statement": None,  # handled specially (IMPORTS edge)
        "import_from_statement": None,
    },
    "typescript": {
        "function_declaration": CodeNodeType.FUNCTION,
        "class_declaration": CodeNodeType.CLASS,
        "method_definition": CodeNodeType.METHOD,
        "import_statement": None,
    },
    "javascript": {
        "function_declaration": CodeNodeType.FUNCTION,
        "class_declaration": CodeNodeType.CLASS,
        "method_definition": CodeNodeType.METHOD,
        "import_statement": None,
    },
    "tsx": {
        "function_declaration": CodeNodeType.FUNCTION,
        "class_declaration": CodeNodeType.CLASS,
        "method_declaration": CodeNodeType.METHOD,
        "import_statement": None,
    },
    "jsx": {
        "function_declaration": CodeNodeType.FUNCTION,
        "class_declaration": CodeNodeType.CLASS,
        "import_statement": None,
    },
    "rust": {
        "function_item": CodeNodeType.FUNCTION,
        "struct_item": CodeNodeType.CLASS,
        "trait_item": CodeNodeType.INTERFACE,
        "impl_item": None,  # handled specially (IMPLEMENTS edge)
        "use_declaration": None,
    },
    "go": {
        "function_declaration": CodeNodeType.FUNCTION,
        "type_declaration": CodeNodeType.CLASS,
        "method_declaration": CodeNodeType.METHOD,
        "import_spec": None,
    },
    "java": {
        "method_declaration": CodeNodeType.METHOD,
        "class_declaration": CodeNodeType.CLASS,
        "interface_declaration": CodeNodeType.INTERFACE,
        "import_declaration": None,
    },
    "kotlin": {
        "function_declaration": CodeNodeType.FUNCTION,
        "class_declaration": CodeNodeType.CLASS,
        "import_header": None,
    },
    "ruby": {
        "method": CodeNodeType.METHOD,
        "class": CodeNodeType.CLASS,
        "module": CodeNodeType.MODULE,
    },
    "swift": {
        "function_declaration": CodeNodeType.FUNCTION,
        "class_declaration": CodeNodeType.CLASS,
    },
}


def detect_language_for_path(file_path: str) -> str | None:
    """Detect programming language for a file path.

    Uses the canonical 29+ language table at
    `cianfhoghlaim/cocoindex_flows/chunking/languages.py` (ported from
    `codeolas/chunking/languages.py`).
    """
    return EXTENSION_TO_LANGUAGE.get(pathlib.Path(file_path).suffix.lower())


# =============================================================================
# Context keys — imported from the canonical shared lifespan
# (`cianfhoghlaim/cocoindex_flows/_lifespan.py`). Per REFACTORING.md
# item 12, every v1 App delegates to `shared_lifespan` rather than
# re-declaring `LANCE_DB` / `EMBEDDER` / `RESOLVED_FILE_REGISTRY`.
# The previous `codebase_lance_db` + `codebase_embedder` ContextKeys
# are aliased to the canonical names for back-compat with downstream
# imports.
# =============================================================================


from ._lifespan import (  # noqa: E402
    EMBEDDER,  # noqa: F401 — re-exported for back-compat
    LANCE_DB,  # noqa: F401 — re-exported for back-compat
    LANCEDB_URI as _SHARED_LANCEDB_URI,
    EMBED_MODEL as _SHARED_EMBED_MODEL,
    EMBED_DIM as _SHARED_EMBED_DIM,
    RESOLVED_FILE_REGISTRY,  # noqa: F401 — re-exported for back-compat
    shared_lifespan,
)


# =============================================================================
# Data models
# =============================================================================


@dataclass
class CodeChunk:
    """One embedded chunk of a source file in the monorepo."""

    id: int
    path: str
    language: str
    filename: str
    chunk_text: str
    chunk_start: int
    chunk_end: int
    embedding: Annotated[Any, EMBEDDER] if COCOINDEX_AVAILABLE else Any  # type: ignore[valid-type]


@dataclass
class CodeNode:
    """One node in the codebase knowledge graph.

    Ported from `codeolas/cocoindex_flows/file_graph.py:GraphNode`."""

    id: str
    node_type: CodeNodeType
    name: str
    file_path: str
    start_line: int | None = None
    end_line: int | None = None
    language: str = ""
    properties: dict[str, Any] | None = None


@dataclass
class CodeEdge:
    """One edge in the codebase knowledge graph.

    Ported from `codeolas/cocoindex_flows/file_graph.py:GraphEdge`."""

    source_id: str
    target_id: str
    edge_type: CodeEdgeType
    properties: dict[str, Any] | None = None


# =============================================================================
# Splitter
# =============================================================================


_splitter = RecursiveSplitter() if COCOINDEX_AVAILABLE else None  # type: ignore[call-arg]


# =============================================================================
# Per-file processing
# =============================================================================


if COCOINDEX_AVAILABLE:

    @coco.fn(memo=True)
    async def process_codebase_file(  # type: ignore[no-redef]
        file: FileLike,  # type: ignore[valid-type]
        table: lancedb.TableTarget,  # type: ignore[valid-type]
    ) -> int:
        """
        Read one file, chunk it with the recursive splitter (using
        `detect_code_language` for code), embed each chunk, and write to
        the `codebase_chunks` LanceDB table.

        Returns the number of chunks emitted (for stats).
        """
        try:
            text = await file.read_text()
        except (UnicodeDecodeError, ValueError):
            # Binary file we cannot decode — skip silently.
            return 0
        if not text.strip():
            return 0

        path = file.file_path.path
        language = detect_code_language(filename=path.name)  # type: ignore[call-arg]
        if language is None and path.suffix in {".md", ".mdx", ".markdown"}:
            language = "markdown"

        chunks = _splitter.split(  # type: ignore[union-attr]
            text,
            chunk_size=1000,
            chunk_overlap=200,
            language=language,
        )
        if not chunks:
            return 0

        embedder = coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        id_gen = IdGenerator()
        count = 0
        for chunk in chunks:
            embedding = await embedder.embed(chunk.text)
            await table.declare_row(
                row=CodeChunk(
                    id=await id_gen.next_id(chunk.text),
                    path=path.as_posix(),
                    language=language or "unknown",
                    filename=path.name,
                    chunk_text=chunk.text,
                    chunk_start=chunk.start.char_offset,
                    chunk_end=chunk.end.char_offset,
                    embedding=embedding,
                )
            )
            count += 1
        return count


# =============================================================================
# AST-based code graph extraction (port from codeolas/file_graph.py)
# =============================================================================


def _ast_extract_nodes_and_edges(
    content: str,
    file_path: str,
    language: str,
) -> tuple[list[CodeNode], list[CodeEdge]]:
    """
    Extract code-graph nodes and edges from source content via Tree-sitter.

    Ported from `codeolas/cocoindex_flows/file_graph.py:extract_relationships_from_ast`
    (which was 60 lines). Uses the canonical 7-node / 7-edge model.
    Tree-sitter may be unavailable; in that case returns only the file node.
    """
    nodes: list[CodeNode] = []
    edges: list[CodeEdge] = []

    file_id = f"file:{file_path}"
    file_node = CodeNode(
        id=file_id,
        node_type=CodeNodeType.FILE,
        name=pathlib.Path(file_path).name,
        file_path=file_path,
        language=language or "unknown",
    )
    nodes.append(file_node)

    try:
        import tree_sitter_languages  # type: ignore[import-not-found]
    except ImportError:
        logger.debug(
            "tree_sitter_languages_not_available: file=%s", file_path
        )
        return nodes, edges

    if language not in _LANG_AST_NODE_TYPES:
        return nodes, edges
    try:
        parser = tree_sitter_languages.get_parser(language)  # type: ignore[union-attr]
        tree = parser.parse(content.encode("utf-8"))
    except Exception as e:  # noqa: BLE001
        logger.warning("AST_extraction_failed: file=%s err=%s", file_path, e)
        return nodes, edges

    _ast_walk(
        tree.root_node,  # type: ignore[union-attr]
        content,
        file_path,
        file_id,
        language,
        nodes,
        edges,
    )
    return nodes, edges


def _ast_walk(
    node: Any,
    content: str,
    file_path: str,
    parent_id: str,
    language: str,
    nodes: list[CodeNode],
    edges: list[CodeEdge],
) -> None:
    """Recursively walk a Tree-sitter AST and emit CodeNode + CodeEdge."""
    lang_map = _LANG_AST_NODE_TYPES.get(language, {})
    ast_type = getattr(node, "type", None)

    if ast_type in lang_map:
        code_type = lang_map[ast_type]
        if code_type is not None:
            name = _extract_name(node)
            if name:
                node_id = f"{code_type.value.lower()}:{file_path}:{name}"
                start_line = node.start_point[0] + 1
                end_line = node.end_point[0] + 1
                graph_node = CodeNode(
                    id=node_id,
                    node_type=code_type,
                    name=name,
                    file_path=file_path,
                    start_line=start_line,
                    end_line=end_line,
                    language=language,
                )
                nodes.append(graph_node)
                edges.append(
                    CodeEdge(
                        source_id=parent_id,
                        target_id=node_id,
                        edge_type=CodeEdgeType.CONTAINS,
                    )
                )
                parent_id = node_id

    for child in node.children:
        _ast_walk(child, content, file_path, parent_id, language, nodes, edges)


def _extract_name(node: Any) -> str | None:
    """Extract the name identifier from a Tree-sitter AST node."""
    for child in getattr(node, "children", []):
        ctype = getattr(child, "type", None)
        if ctype in ("identifier", "name", "property_identifier"):
            text = getattr(child, "text", b"")
            if isinstance(text, bytes):
                return text.decode("utf-8", errors="replace")
            return text
    return None


# =============================================================================
# Code graph App (Lancedb graph table for the 7 node + 7 edge model)
# =============================================================================


def _make_graph_app():  # noqa: ANN202
    """Construct the code graph v1 App. Returns None when cocoindex is missing.

    Writes to a second LanceDB table `codebase_graph` with the
    `(CodeNode, CodeEdge)` tuple. The downstream Dagster asset
    `codebase_code_graph` reads this table to populate Memgraph (the
    v0 path) and exposes Cypher queries via the existing
    `codeolas/cocoindex_flows/file_graph.py:MemgraphClient`.
    """
    if not COCOINDEX_AVAILABLE:
        return None

    @coco.lifespan
    async def codebase_graph_lifespan(  # type: ignore[no-redef]
        builder: coco.EnvironmentBuilder,  # type: ignore[valid-type]
    ) -> AsyncIterator[None]:
        # Delegate to the shared lifespan (REFACTORING.md item 12).
        # The shared lifespan provides LANCE_DB + EMBEDDER +
        # RESOLVED_FILE_REGISTRY; this App only adds the graph table
        # (in `codebase_graph_app_main` below).
        async with shared_lifespan(builder):  # type: ignore[arg-type]
            yield

    @coco.fn
    async def codebase_graph_app_main(  # type: ignore[no-redef]
        repo_root: pathlib.Path,
    ) -> None:
        graph_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name=LANCEDB_GRAPH_TABLE,
            table_schema=await lancedb.TableSchema.from_class(
                CodeNode, primary_key=["id"]
            ),
        )
        edge_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name=f"{LANCEDB_GRAPH_TABLE}_edges",
            table_schema=await lancedb.TableSchema.from_class(
                CodeEdge, primary_key=["source_id", "target_id", "edge_type"]
            ),
        )

        files = localfs.walk_dir(  # type: ignore[call-arg]
            repo_root,
            recursive=True,
            path_matcher=PatternFilePathMatcher(
                included_patterns=list(EXTENSION_TO_LANGUAGE.keys()),
                excluded_patterns=[
                    "**/.*",
                    "**/node_modules/**",
                    "**/__pycache__/**",
                    "**/.venv/**",
                    "**/venv/**",
                    "**/target/**",
                    "**/dist/**",
                    "**/build/**",
                    "**/.turbo/**",
                    "**/.cocoindex_code/**",
                    "**/stedding/**",
                    "**/.git/**",
                ],
            ),
            live=True,
            refresh_interval=REFRESH_INTERVAL,
        )

        @coco.fn(memo=True)
        async def process_code_graph_file(  # type: ignore[no-redef]
            file: FileLike,  # type: ignore[valid-type]
        ) -> int:
            try:
                text = await file.read_text()
            except (UnicodeDecodeError, ValueError):
                return 0
            if not text.strip():
                return 0
            path = file.file_path.path
            language = detect_language_for_path(path.as_posix())
            if not language:
                return 0
            nodes, edges = _ast_extract_nodes_and_edges(text, path.as_posix(), language)
            count = 0
            for n in nodes:
                await graph_table.declare_row(row=n)
                count += 1
            for e in edges:
                await edge_table.declare_row(row=e)
            return count

        await coco.mount_each(process_code_graph_file, files.items())

    return coco.App(
        coco.AppConfig(name="CodebaseGraph"),
        codebase_graph_app_main,
        repo_root=DEFAULT_REPO_ROOT,
    )


codebase_graph_app = _make_graph_app()


# =============================================================================
# App entry point (chunks + graph)
# =============================================================================


def _make_app():
    """Construct the codebase v1 App. Returns None when cocoindex is missing."""
    if not COCOINDEX_AVAILABLE:
        return None

    @coco.lifespan
    async def codebase_lifespan(  # type: ignore[no-redef]
        builder: coco.EnvironmentBuilder,  # type: ignore[valid-type]
    ) -> AsyncIterator[None]:
        # Delegate to the shared lifespan (REFACTORING.md item 12).
        async with shared_lifespan(builder):  # type: ignore[arg-type]
            yield

    @coco.fn
    async def codebase_app_main(repo_root: pathlib.Path) -> None:  # type: ignore[no-redef]
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name=LANCEDB_TABLE,
            table_schema=await lancedb.TableSchema.from_class(CodeChunk, primary_key=["id"]),
        )
        target_table.declare_vector_index(column="embedding")

        files = localfs.walk_dir(  # type: ignore[call-arg]
            repo_root,
            recursive=True,
            path_matcher=PatternFilePathMatcher(
                included_patterns=[
                    "*.py",
                    "*.rs",
                    "*.ts",
                    "*.tsx",
                    "*.go",
                    "*.md",
                    "*.mdx",
                    "*.toml",
                ],
                excluded_patterns=[
                    "**/.*",
                    "**/node_modules/**",
                    "**/__pycache__/**",
                    "**/.venv/**",
                    "**/venv/**",
                    "**/target/**",
                    "**/dist/**",
                    "**/build/**",
                    "**/.turbo/**",
                    "**/.cocoindex_code/**",
                    "**/stedding/**",
                    "**/.git/**",
                ],
            ),
            live=True,
            refresh_interval=REFRESH_INTERVAL,
        )
        await coco.mount_each(process_codebase_file, files.items(), target_table)

    return coco.App(
        coco.AppConfig(name="CodebaseIndex"),
        codebase_app_main,
        repo_root=DEFAULT_REPO_ROOT,
    )


codebase_app = _make_app()


# =============================================================================
# Query helpers (CLI: `bun run ccc:v1:search "..."`  ->  search_codebase(...))
# =============================================================================


async def search_codebase(
    query: str,
    limit: int = TOP_K,
    language: str | None = None,
    path_glob: str | None = None,
) -> list[dict[str, Any]]:
    """Run a vector search against the `codebase_chunks` LanceDB table."""
    if not COCOINDEX_AVAILABLE:
        return []
    embedder = coco.use_context(EMBEDDER)  # type: ignore[arg-type]
    conn = coco.use_context(LANCE_DB)  # type: ignore[arg-type]
    query_vec = await embedder.embed(query)
    table = await conn.open_table(LANCEDB_TABLE)
    search = table.search(query_vec, vector_column_name="embedding")
    conditions: list[str] = []
    if language:
        conditions.append(f"language = '{language}'")
    if path_glob:
        conditions.append(f"path LIKE '{path_glob}'")
    if conditions:
        search = search.where(" AND ".join(conditions))
    rows = await search.limit(limit).to_list()
    for r in rows:
        r["score"] = 1.0 - r.get("_distance", 0.0)
    return rows


async def search_code_graph(
    file_path: str | None = None,
    node_type: str | None = None,
    limit: int = TOP_K,
) -> list[dict[str, Any]]:
    """Run a search against the `codebase_graph` LanceDB table.

    Returns CodeNode dicts. Use `codebase_graph_edges` to traverse.
    """
    if not COCOINDEX_AVAILABLE:
        return []
    conn = coco.use_context(LANCE_DB)  # type: ignore[arg-type]
    table = await conn.open_table(LANCEDB_GRAPH_TABLE)
    search = table.to_pandas()
    if file_path:
        search = search[search["file_path"].str.contains(file_path, regex=False)]
    if node_type:
        search = search[search["node_type"] == node_type]
    return search.head(limit).to_dict(orient="records")


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "COCOINDEX_AVAILABLE",
    "LANCEDB_URI",
    "EMBED_MODEL",
    "EMBED_DIM",
    "REFRESH_INTERVAL",
    "LANCEDB_TABLE",
    "LANCEDB_GRAPH_TABLE",
    "TOP_K",
    "DEFAULT_REPO_ROOT",
    "EXTENSION_TO_LANGUAGE",
    "get_supported_languages",
    "CodeNodeType",
    "CodeEdgeType",
    "CodeNode",
    "CodeEdge",
    "CodeChunk",
    "detect_language_for_path",
    "search_codebase",
    "search_code_graph",
]
if COCOINDEX_AVAILABLE and codebase_app is not None:
    __all__.append("codebase_app")
if COCOINDEX_AVAILABLE and codebase_graph_app is not None:
    __all__.append("codebase_graph_app")
