"""
Docs-Skills Consolidation CocoIndex v1 App.

Tag, embed, and graph-link every Markdown file under `docs/` and
`.agents/skills/`. Persists results to:

- LanceDB table `docs_skills_chunks` (vector index on `embedding`)
- FalkorDB graph `docs_skills_graph` (nodes: DocSkill, Concept, ConsolidationGroup;
  edges: TAGGED, CONSOLIDATED_INTO, RELATES_TO)

All extraction is BAML-driven (see `baml/processing/` cluster for the generic file processing BAML files).
The BAML client is the canonical LLM surface for this pipeline; litellm +
instructor is NOT used here (it is reserved for the CocoIndex example paths
in `docs/cocoindex/`).

Operational contract (see `openspec/changes/docs-skills-consolidation-pipeline/`):
- Phase 1 per-file is `@coco.fn(memo=True)`; unchanged files are skipped.
- Phase 2 graph build is `@coco.fn` (not memoised) so it always reconciles.
- Live mode (`cocoindex update -L ...`) is supported via `localfs.walk_dir(live=True)`.
- Failure isolation: a file that fails BAML extraction is logged and skipped;
  the asset check reports the count.

Reference patterns:
- `docs/cocoindex/meeting_notes_graph_falkordb/main.py` (entity resolution + FalkorDB)
- `docs/cocoindex/docs_to_knowledge_graph/main.py` (two-phase graph build)
- `cianfhoghlaim/cocoindex_flows/leabharlann_embedding.py` (v1 App conventions)
"""

from __future__ import annotations

import datetime
import hashlib
import os
import pathlib
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Annotated, Any

import structlog

logger = structlog.get_logger(__name__)

# CocoIndex is optional — degrade gracefully if not installed.
try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import (
        falkordb,  # type: ignore[import-not-found]
        lancedb,  # type: ignore[import-not-found]
        localfs,  # type: ignore[import-not-found]
    )
    from cocoindex.ops.sentence_transformers import (  # type: ignore[import-not-found]
        SentenceTransformerEmbedder,
    )
    from cocoindex.ops.text import RecursiveSplitter  # type: ignore[import-not-found]
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
    falkordb = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]
    localfs = None  # type: ignore[assignment]
    SentenceTransformerEmbedder = None  # type: ignore[assignment]
    RecursiveSplitter = None  # type: ignore[assignment]
    FileLike = None  # type: ignore[assignment]
    PatternFilePathMatcher = None  # type: ignore[assignment]
    IdGenerator = None  # type: ignore[assignment]


# =============================================================================
# Configuration
# =============================================================================


LANCEDB_URI = os.getenv("LANCEDB_URI", "rest://lance-api.cianfhoghlaim.ie")
FALKORDB_URI = os.getenv("FALKORDB_URI", "falkor://localhost:6379")
FALKORDB_GRAPH = os.getenv("DOCS_SKILLS_FALKORDB_GRAPH", "docs_skills_graph")
# Canonical embedder env knob: CIANFHOGHLAIM_EMBED_MODEL (per the
# centralized-model-registry openspec change). The legacy DOCS_SKILLS_EMBED_MODEL
# is honoured as a back-compat alias.
EMBED_MODEL = (
    os.getenv("CIANFHOGHLAIM_EMBED_MODEL")
    or os.getenv("DOCS_SKILLS_EMBED_MODEL")
    or "BAAI/bge-m3"
)
EMBED_DIM = int(os.getenv("CIANFHOGHLAIM_EMBED_DIM", "1024"))
DOCS_REFRESH_INTERVAL = datetime.timedelta(seconds=int(os.getenv("DOCS_SKILLS_REFRESH_SECS", "30")))
LANCEDB_TABLE = "docs_skills_chunks"

# Default source roots.
DEFAULT_DOCS_ROOT = pathlib.Path(
    os.getenv(
        "DOCS_SKILLS_DOCS_ROOT",
        str(pathlib.Path(__file__).resolve().parents[5] / "docs"),
    )
)
DEFAULT_SKILLS_ROOT = pathlib.Path(
    os.getenv(
        "DOCS_SKILLS_SKILLS_ROOT",
        str(pathlib.Path(__file__).resolve().parents[5] / ".agents" / "skills"),
    )
)


# =============================================================================
# Context keys — imported from the canonical shared lifespan
# (`cianfhoghlaim/cocoindex_flows/_lifespan.py`). Per REFACTORING.md
# item 12, every v1 App delegates to `shared_lifespan` rather than
# re-declaring `LANCE_DB` / `EMBEDDER` / `RESOLVED_FILE_REGISTRY`.
# The previous `docs_skills_lance_db` + `docs_skills_embedder`
# ContextKeys were renamed to the canonical names for the v1
# conformance check (R2).
#
# `KG_DB` is App-specific (this App uses the `docs_skills_graph`
# FalkorDB graph) and is declared below with an exemption comment.
# =============================================================================


from .._shared._lifespan import (  # noqa: E402
    EMBEDDER,  # noqa: F401 — re-exported for back-compat
    LANCE_DB,  # noqa: F401 — re-exported for back-compat
    RESOLVED_FILE_REGISTRY,  # noqa: F401 — re-exported for back-compat
    shared_lifespan_ctx,
)

if COCOINDEX_AVAILABLE:
    # R2-exempt: KG_DB is bound to the `docs_skills_graph` FalkorDB
    # graph, which is App-specific (this App declares
    # `DocSkillNode` + `ConceptNode` + `ConsolidationGroupNode`
    # schemas that only this App uses). Sharing it across Apps
    # would couple the docs-skills surface to the upstream-monitor
    # surface; keeping it scoped here preserves the modularity.
    KG_DB: Any = coco.ContextKey[falkordb.ConnectionFactory](  # type: ignore[valid-type]
        "docs_skills_kg_db"
    )
else:
    KG_DB = None  # type: ignore[assignment]


# =============================================================================
# Data models
# =============================================================================


@dataclass
class DocSkillChunk:
    """One embedded chunk of a doc or skill file."""

    id: int
    path: str
    category: str
    quadrant: str
    is_canonical: bool
    short_label: str
    chunk_text: str
    chunk_start: int
    chunk_end: int
    embedding: Annotated[Any, EMBEDDER] if COCOINDEX_AVAILABLE else Any  # type: ignore[valid-type]


@dataclass
class DocSkillNode:
    """FalkorDB node: a single file with its tag and provenance."""

    path: str  # primary key (sha256 of content)
    abs_path: str
    category: str
    quadrant: str
    confidence: float
    short_label: str
    is_canonical: bool
    byte_size: int
    last_seen: str  # ISO timestamp


@dataclass
class ConceptNode:
    """FalkorDB node: a single canonical concept name."""

    value: str  # primary key


@dataclass
class ConsolidationGroupNode:
    """FalkorDB node: a cluster of files that should be folded together."""

    group_id: str  # primary key
    canonical_path: str
    reason: str
    merge_action: str
    confidence: float
    member_count: int


@dataclass
class RelatesToEdge:
    """RELATES_TO edge payload. id is a stable hash of (subject, predicate, object)."""

    id: int
    predicate: str


# TAGGED and CONSOLIDATED_INTO carry no payload — declared without a schema so
# the FalkorDB connector auto-derives the PK from endpoints.


# =============================================================================
# Helpers
# =============================================================================


def _path_key(abs_path: pathlib.Path) -> str:
    """Stable primary key: sha256 of the relative path's POSIX form."""
    return hashlib.sha256(abs_path.as_posix().encode("utf-8")).hexdigest()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _excerpt(text: str, max_chars: int = 2000) -> str:
    """Return the first max_chars of the file for BAML triple extraction."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[... truncated for BAML ...]"


# =============================================================================
# Shared processing functions
# =============================================================================


_splitter = RecursiveSplitter() if COCOINDEX_AVAILABLE else None  # type: ignore[call-arg]


# =============================================================================
# BAML extraction (lazy import — keeps the App importable when BAML client
# is not generated yet)
# =============================================================================


def _baml():
    """Lazy import the generated BAML client."""
    from baml_client.sync_client import b as baml_sync  # type: ignore[import-not-found]

    return baml_sync


# =============================================================================
# Phase 1: per-file processing
# =============================================================================


if COCOINDEX_AVAILABLE:

    @coco.fn(memo=True)
    async def tag_doc_skill(  # type: ignore[no-redef]
        path: str, content: str
    ) -> dict[str, Any]:
        """Run BAML `ExtractDocSkillTag` on one file. Memoised on (path, sha256)."""
        try:
            result = _baml().ExtractDocSkillTag(content=_excerpt(content), path=path)
            return {
                "category": str(result.category),
                "quadrant": str(result.quadrant),
                "confidence": float(result.confidence),
                "short_label": result.short_label,
                "is_canonical": bool(result.is_canonical),
            }
        except Exception as e:
            logger.warning("baml_tag_failed", path=path, error=str(e))
            return {
                "category": "OTHER",
                "quadrant": "OTHER",
                "confidence": 0.0,
                "short_label": "",
                "is_canonical": False,
            }

    @coco.fn(memo=True)
    async def extract_triples(  # type: ignore[no-redef]
        path: str, content: str
    ) -> list[tuple[str, str, str]]:
        """Run BAML `ExtractTriples` on one file. Returns (s, p, o) tuples."""
        try:
            result = _baml().ExtractTriples(content=_excerpt(content), path=path)
            return [(str(t.subject), str(t.predicate), str(t.object)) for t in result.triples]
        except Exception as e:
            logger.warning("baml_triples_failed", path=path, error=str(e))
            return []

    @coco.fn(memo=True)
    async def process_doc_skill_file(  # type: ignore[no-redef]
        file: FileLike,  # type: ignore[valid-type]
        doc_skill_table: falkordb.TableTarget,  # type: ignore[valid-type]
        chunk_table: lancedb.TableTarget,  # type: ignore[valid-type]
        rel_table: falkordb.TableTarget,  # type: ignore[valid-type]
    ) -> dict[str, Any]:
        """
        Phase 1 per-file: tag + extract triples + embed chunks.

        Declares one `DocSkill` node in FalkorDB, N `DocSkillChunk` rows in
        LanceDB, and a list of pending (subject, predicate, object) triples
        for the Phase 2 graph pass.
        """
        text = await file.read_text()
        path = file.file_path.path.as_posix()
        node_key = _path_key(pathlib.PurePath(path))

        tag = await tag_doc_skill(path, text)
        triples = await extract_triples(path, text)

        # Declare DocSkill node (FalkorDB)
        doc_skill_table.declare_record(
            row=DocSkillNode(
                path=node_key,
                abs_path=path,
                category=tag["category"],
                quadrant=tag["quadrant"],
                confidence=tag["confidence"],
                short_label=tag["short_label"],
                is_canonical=tag["is_canonical"],
                byte_size=len(text),
                last_seen=datetime.datetime.utcnow().isoformat(),
            )
        )

        # Embed chunks (LanceDB)
        chunks = _splitter.split(text, chunk_size=2000, chunk_overlap=500, language="markdown")  # type: ignore[union-attr]
        embedder = coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        id_gen = IdGenerator()
        for chunk in chunks:
            embedding = await embedder.embed(chunk.text)
            chunk_table.declare_row(
                row=DocSkillChunk(
                    id=await id_gen.next_id(chunk.text),
                    path=path,
                    category=tag["category"],
                    quadrant=tag["quadrant"],
                    is_canonical=tag["is_canonical"],
                    short_label=tag["short_label"],
                    chunk_text=chunk.text,
                    chunk_start=chunk.start.char_offset,
                    chunk_end=chunk.end.char_offset,
                    embedding=embedding,
                )
            )

        return {
            "node_key": node_key,
            "path": path,
            "tag": tag,
            "triples": triples,
        }


# =============================================================================
# Phase 2: graph build
# =============================================================================


if COCOINDEX_AVAILABLE:

    @coco.fn
    async def build_graph(  # type: ignore[no-redef]
        per_file: list[dict[str, Any]],
        concept_table: falkordb.TableTarget,  # type: ignore[valid-type]
        rel_table: falkordb.TableTarget,  # type: ignore[valid-type]
    ) -> None:
        """
        Phase 2: declare Concept nodes + RELATES_TO edges from the per-file
        triples. Unchanged from one run to the next → this is NOT memoised
        (FalkorDB reconciles idempotently).
        """
        from cocoindex.resources.id import generate_id  # type: ignore[import-not-found]

        concepts: set[str] = set()
        for entry in per_file:
            for s, _p, o in entry["triples"]:
                concepts.add(s)
                concepts.add(o)
            for s, p, o in entry["triples"]:
                rel_id = await generate_id((s, p, o))
                rel_table.declare_record(
                    row=RelatesToEdge(id=rel_id, predicate=p),
                    from_id=s,
                    to_id=o,
                )
        for value in sorted(concepts):
            concept_table.declare_record(row=ConceptNode(value=value))


# =============================================================================
# App entry point
# =============================================================================


def _make_app():
    """Construct the docs-skills v1 App. Returns None when cocoindex is missing."""
    if not COCOINDEX_AVAILABLE:
        return None

    @coco.lifespan
    async def docs_skills_lifespan(  # type: ignore[no-redef]
        builder: coco.EnvironmentBuilder,  # type: ignore[valid-type]
    ) -> AsyncIterator[None]:
        # Delegate to the shared lifespan (REFACTORING.md item 12).
        # The shared lifespan provides LANCE_DB + EMBEDDER +
        # RESOLVED_FILE_REGISTRY; this App only adds the App-specific
        # KG_DB (the `docs_skills_graph` FalkorDB graph).
        async with shared_lifespan_ctx(builder):  # type: ignore[arg-type]
            builder.provide(
                KG_DB,
                falkordb.ConnectionFactory(  # type: ignore[call-arg]
                    uri=FALKORDB_URI,
                    graph=FALKORDB_GRAPH,
                ),
            )
            yield

    @coco.fn
    async def docs_skills_app_main(  # type: ignore[no-redef]
        docs_root: pathlib.Path, skills_root: pathlib.Path
    ) -> None:
        # FalkorDB node tables
        doc_skill_table = await falkordb.mount_table_target(
            KG_DB,
            "DocSkill",
            await falkordb.TableSchema.from_class(DocSkillNode, primary_key="path"),
            primary_key="path",
        )
        concept_table = await falkordb.mount_table_target(
            KG_DB,
            "Concept",
            await falkordb.TableSchema.from_class(ConceptNode, primary_key="value"),
            primary_key="value",
        )

        # FalkorDB edge tables
        # RELATES_TO carries a `predicate` payload; mounted with a schema so
        # each distinct triple gets its own edge.
        rel_table = await falkordb.mount_table_target(
            KG_DB,
            "RELATES_TO",
            await falkordb.TableSchema.from_class(RelatesToEdge, primary_key="id"),
            primary_key="id",
        )

        # LanceDB chunk table (one row per chunk; vector index on `embedding`)
        chunk_table = await lancedb.mount_table_target(
            LANCE_DB,
            table_name=LANCEDB_TABLE,
            table_schema=await lancedb.TableSchema.from_class(DocSkillChunk, primary_key=["id"]),
        )
        chunk_table.declare_vector_index(column="embedding")  # R4

        # Phase 1: walk both roots, mount per-file processing
        per_file_results: list[dict[str, Any]] = []

        async def _per_file(
            file: FileLike,  # type: ignore[valid-type]
            _dt: Any = doc_skill_table,
            _ct: Any = chunk_table,
            _rt: Any = rel_table,
        ) -> dict[str, Any]:
            result = await process_doc_skill_file(file, _dt, _ct, _rt)
            per_file_results.append(result)
            return result

        for sourcedir in (docs_root, skills_root):
            if not sourcedir.exists():
                logger.warning("source_root_missing", path=str(sourcedir))
                continue
            files = localfs.walk_dir(  # type: ignore[call-arg]
                sourcedir,
                recursive=True,
                path_matcher=PatternFilePathMatcher(
                    included_patterns=[
                        "**/*.md",
                        "**/*.mdx",
                        "**/*.markdown",
                        "**/*.txt",
                    ],
                    excluded_patterns=[
                        "**/node_modules/**",
                        "**/.venv/**",
                        "**/__pycache__/**",
                        "**/.turbo/**",
                        "**/dist/**",
                        "**/build/**",
                        "**/.cocoindex_code/**",
                        "**/stedding/**",
                    ],
                ),
                live=True,
            )
            async for path_key, file in files.items():
                await coco.mount(
                    coco.component_subpath("file", path_key),
                    _per_file,
                    file,
                )

        # Phase 2: graph build (one per app run, blocked on Phase 1)
        await coco.mount(
            coco.component_subpath("build_graph"),
            build_graph,
            per_file_results,
            concept_table,
            rel_table,
        )

    return coco.App(
        coco.AppConfig(name="DocsSkillsConsolidation"),
        docs_skills_app_main,
        docs_root=DEFAULT_DOCS_ROOT,
        skills_root=DEFAULT_SKILLS_ROOT,
    )


docs_skills_app = _make_app()


# =============================================================================
# Query helpers
# =============================================================================


async def search_docs_skills(
    query: str,
    limit: int = 10,
    category: str | None = None,
    quadrant: str | None = None,
) -> list[dict[str, Any]]:
    """Run a vector search against the `docs_skills_chunks` LanceDB table."""
    if not COCOINDEX_AVAILABLE:
        return []
    embedder = coco.use_context(EMBEDDER)  # type: ignore[arg-type]
    conn = coco.use_context(LANCE_DB)  # type: ignore[arg-type]
    query_vec = await embedder.embed(query)
    table = await conn.open_table(LANCEDB_TABLE)
    search = table.search(query_vec, vector_column_name="embedding")
    conditions: list[str] = []
    if category:
        conditions.append(f"category = '{category}'")
    if quadrant:
        conditions.append(f"quadrant = '{quadrant}'")
    if conditions:
        search = search.where(" AND ".join(conditions))
    rows = await search.limit(limit).to_list()
    for r in rows:
        r["score"] = 1.0 - r.get("_distance", 0.0)
    return rows


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "COCOINDEX_AVAILABLE",
    "LANCEDB_URI",
    "FALKORDB_URI",
    "FALKORDB_GRAPH",
    "EMBED_MODEL",
    "EMBED_DIM",
    "DOCS_REFRESH_INTERVAL",
    "LANCEDB_TABLE",
    "DEFAULT_DOCS_ROOT",
    "DEFAULT_SKILLS_ROOT",
    "DocSkillChunk",
    "DocSkillNode",
    "ConceptNode",
    "ConsolidationGroupNode",
    "RelatesToEdge",
    "search_docs_skills",
]
if COCOINDEX_AVAILABLE and docs_skills_app is not None:
    __all__ += ["docs_skills_app", "process_doc_skill_file", "build_graph"]
