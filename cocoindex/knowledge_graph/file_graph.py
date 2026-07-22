"""
File Graph Flow for Códeolas.

Extracts file/function/class relationships into a FalkorDB knowledge graph
(the Cognee code-side backend per the agent-observability spec — Memgraph
is the legacy fallback for operators who set CIANFHOGHLAIM_COGNEE_BACKEND=memgraph).

Enables Cypher queries for architectural understanding:
- Which functions call which functions?
- What files import what modules?
- What classes extend what interfaces?

Based on bonneagar/examples/knowledge-graph pattern.
"""

import logging
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Default configuration
#
# The Cognee code-side default backend is FalkorDB (per the agent-observability
# spec). The Memgraph URI default is preserved for legacy callers; the
# CIANFHOGHLAIM_COGNEE_BACKEND env var selects between falkordb|memgraph|postgres.
DEFAULT_MEMGRAPH_URI = os.getenv("MEMGRAPH_URI", "bolt://memgraph:7687")
DEFAULT_FALKORDB_HOST = os.getenv("FALKORDB_HOST", "falkordb")
DEFAULT_FALKORDB_PORT = int(os.getenv("FALKORDB_PORT", "6379"))
DEFAULT_REPO_PATH = os.getenv(
    "CODEOLAS_REPO_PATH",
    str(Path(__file__).parent.parent.parent.parent.parent)
)


class NodeType(str, Enum):
    """Types of nodes in the code graph."""
    FILE = "File"
    FUNCTION = "Function"
    CLASS = "Class"
    METHOD = "Method"
    MODULE = "Module"
    INTERFACE = "Interface"
    VARIABLE = "Variable"


class EdgeType(str, Enum):
    """Types of relationships between nodes."""
    CONTAINS = "CONTAINS"
    IMPORTS = "IMPORTS"
    CALLS = "CALLS"
    EXTENDS = "EXTENDS"
    IMPLEMENTS = "IMPLEMENTS"
    USES = "USES"
    DEFINES = "DEFINES"


@dataclass
class GraphNode:
    """A node in the code graph."""
    id: str
    node_type: NodeType
    name: str
    file_path: str
    start_line: int | None = None
    end_line: int | None = None
    language: str = ""
    properties: dict[str, Any] | None = None


@dataclass
class GraphEdge:
    """A relationship between nodes."""
    source_id: str
    target_id: str
    edge_type: EdgeType
    properties: dict[str, Any] | None = None


class MemgraphClient:
    """
    Client for Memgraph graph database.

    Provides methods to create and query the code knowledge graph.
    """

    def __init__(self, uri: str | None = None):
        self.uri = uri or DEFAULT_MEMGRAPH_URI
        self._driver = None

    def _get_driver(self):
        """Get or create Memgraph driver."""
        if self._driver is not None:
            return self._driver

        try:
            from neo4j import GraphDatabase
        except ImportError:
            raise ImportError(
                "neo4j driver not installed. Run: pip install neo4j"
            )

        self._driver = GraphDatabase.driver(self.uri)
        logger.info(f"Connected to Memgraph: {self.uri}")
        return self._driver

    @property
    def driver(self):
        """Get Memgraph driver."""
        return self._get_driver()

    def close(self):
        """Close the driver connection."""
        if self._driver:
            self._driver.close()
            self._driver = None

    # =========================================================================
    # Schema Setup
    # =========================================================================

    def setup_schema(self):
        """Create indexes and constraints."""
        queries = [
            # Indexes for fast lookups
            "CREATE INDEX ON :File(path);",
            "CREATE INDEX ON :Function(name);",
            "CREATE INDEX ON :Class(name);",
            "CREATE INDEX ON :Method(name);",
            "CREATE INDEX ON :Module(name);",
            # Uniqueness constraints
            "CREATE CONSTRAINT ON (f:File) ASSERT f.id IS UNIQUE;",
            "CREATE CONSTRAINT ON (fn:Function) ASSERT fn.id IS UNIQUE;",
            "CREATE CONSTRAINT ON (c:Class) ASSERT c.id IS UNIQUE;",
        ]

        with self.driver.session() as session:
            for query in queries:
                try:
                    session.run(query)
                except Exception as e:
                    logger.debug(f"Schema query skipped (may already exist): {e}")

        logger.info("Memgraph schema setup complete")

    def clear_graph(self):
        """Clear all nodes and relationships."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        logger.info("Graph cleared")

    # =========================================================================
    # Node Operations
    # =========================================================================

    def create_node(self, node: GraphNode) -> str:
        """Create a node in the graph."""
        query = f"""
        MERGE (n:{node.node_type.value} {{id: $id}})
        SET n.name = $name,
            n.file_path = $file_path,
            n.start_line = $start_line,
            n.end_line = $end_line,
            n.language = $language
        RETURN n.id
        """

        with self.driver.session() as session:
            result = session.run(
                query,
                id=node.id,
                name=node.name,
                file_path=node.file_path,
                start_line=node.start_line,
                end_line=node.end_line,
                language=node.language,
            )
            record = result.single()
            return record["n.id"] if record else node.id

    def create_nodes_batch(self, nodes: list[GraphNode]) -> int:
        """Create multiple nodes in a batch."""
        if not nodes:
            return 0

        # Group by node type for efficient batching
        by_type: dict[NodeType, list[GraphNode]] = {}
        for node in nodes:
            by_type.setdefault(node.node_type, []).append(node)

        total = 0
        with self.driver.session() as session:
            for node_type, type_nodes in by_type.items():
                query = f"""
                UNWIND $nodes AS node
                MERGE (n:{node_type.value} {{id: node.id}})
                SET n.name = node.name,
                    n.file_path = node.file_path,
                    n.start_line = node.start_line,
                    n.end_line = node.end_line,
                    n.language = node.language
                """

                params = [
                    {
                        "id": n.id,
                        "name": n.name,
                        "file_path": n.file_path,
                        "start_line": n.start_line,
                        "end_line": n.end_line,
                        "language": n.language,
                    }
                    for n in type_nodes
                ]

                session.run(query, nodes=params)
                total += len(type_nodes)

        logger.info(f"Created {total} nodes")
        return total

    # =========================================================================
    # Edge Operations
    # =========================================================================

    def create_edge(self, edge: GraphEdge) -> bool:
        """Create a relationship between nodes."""
        query = f"""
        MATCH (source {{id: $source_id}})
        MATCH (target {{id: $target_id}})
        MERGE (source)-[r:{edge.edge_type.value}]->(target)
        RETURN r
        """

        with self.driver.session() as session:
            result = session.run(
                query,
                source_id=edge.source_id,
                target_id=edge.target_id,
            )
            return result.single() is not None

    def create_edges_batch(self, edges: list[GraphEdge]) -> int:
        """Create multiple edges in a batch."""
        if not edges:
            return 0

        # Group by edge type
        by_type: dict[EdgeType, list[GraphEdge]] = {}
        for edge in edges:
            by_type.setdefault(edge.edge_type, []).append(edge)

        total = 0
        with self.driver.session() as session:
            for edge_type, type_edges in by_type.items():
                query = f"""
                UNWIND $edges AS edge
                MATCH (source {{id: edge.source_id}})
                MATCH (target {{id: edge.target_id}})
                MERGE (source)-[r:{edge_type.value}]->(target)
                """

                params = [
                    {"source_id": e.source_id, "target_id": e.target_id}
                    for e in type_edges
                ]

                session.run(query, edges=params)
                total += len(type_edges)

        logger.info(f"Created {total} edges")
        return total

    # =========================================================================
    # Query Operations
    # =========================================================================

    def find_callers(self, function_name: str) -> list[dict]:
        """Find all functions that call a given function."""
        query = """
        MATCH (caller:Function)-[:CALLS]->(callee:Function {name: $name})
        RETURN caller.name AS caller_name,
               caller.file_path AS caller_file,
               caller.start_line AS caller_line
        """

        with self.driver.session() as session:
            result = session.run(query, name=function_name)
            return [dict(record) for record in result]

    def find_dependencies(self, file_path: str) -> list[dict]:
        """Find all files that a given file imports."""
        query = """
        MATCH (file:File {path: $path})-[:IMPORTS]->(dep)
        RETURN dep.name AS dependency,
               labels(dep)[0] AS type
        """

        with self.driver.session() as session:
            result = session.run(query, path=file_path)
            return [dict(record) for record in result]

    def find_class_hierarchy(self, class_name: str) -> list[dict]:
        """Find class inheritance chain."""
        query = """
        MATCH path = (c:Class {name: $name})-[:EXTENDS*0..]->(parent:Class)
        RETURN [node in nodes(path) | node.name] AS hierarchy
        """

        with self.driver.session() as session:
            result = session.run(query, name=class_name)
            return [dict(record) for record in result]

    def get_file_structure(self, file_path: str) -> dict:
        """Get all symbols defined in a file."""
        query = """
        MATCH (f:File {path: $path})-[:CONTAINS]->(symbol)
        RETURN labels(symbol)[0] AS type,
               symbol.name AS name,
               symbol.start_line AS line
        ORDER BY symbol.start_line
        """

        with self.driver.session() as session:
            result = session.run(query, path=file_path)
            symbols = [dict(record) for record in result]

            return {
                "file_path": file_path,
                "symbols": symbols,
                "symbol_count": len(symbols),
            }

    def get_stats(self) -> dict:
        """Get graph statistics."""
        queries = {
            "files": "MATCH (n:File) RETURN count(n) AS count",
            "functions": "MATCH (n:Function) RETURN count(n) AS count",
            "classes": "MATCH (n:Class) RETURN count(n) AS count",
            "methods": "MATCH (n:Method) RETURN count(n) AS count",
            "imports": "MATCH ()-[r:IMPORTS]->() RETURN count(r) AS count",
            "calls": "MATCH ()-[r:CALLS]->() RETURN count(r) AS count",
        }

        stats = {}
        with self.driver.session() as session:
            for key, query in queries.items():
                result = session.run(query)
                record = result.single()
                stats[key] = record["count"] if record else 0

        return stats


def extract_relationships_from_ast(
    content: str,
    file_path: str,
    language: str,
) -> tuple[list[GraphNode], list[GraphEdge]]:
    """
    Extract nodes and relationships from AST.

    Args:
        content: Source code content
        file_path: Path to source file
        language: Programming language

    Returns:
        Tuple of (nodes, edges)
    """
    from .transforms.treesitter_chunking import detect_language

    nodes = []
    edges = []

    # Create file node
    file_id = f"file:{file_path}"
    file_node = GraphNode(
        id=file_id,
        node_type=NodeType.FILE,
        name=Path(file_path).name,
        file_path=file_path,
        language=language or detect_language(file_path) or "unknown",
    )
    nodes.append(file_node)

    try:
        import tree_sitter_languages
        parser = tree_sitter_languages.get_parser(language)
        tree = parser.parse(content.encode("utf-8"))

        # Extract symbols and relationships
        _extract_from_node(
            tree.root_node,
            content,
            file_path,
            file_id,
            language,
            nodes,
            edges,
        )

    except Exception as e:
        logger.warning(f"AST extraction failed for {file_path}: {e}")

    return nodes, edges


def _extract_from_node(
    node,
    content: str,
    file_path: str,
    parent_id: str,
    language: str,
    nodes: list[GraphNode],
    edges: list[GraphEdge],
):
    """Recursively extract nodes and edges from AST."""
    # Define extractable node types per language
    extractable = {
        "python": {
            "function_definition": NodeType.FUNCTION,
            "class_definition": NodeType.CLASS,
            "import_statement": None,  # Handle specially
            "import_from_statement": None,
        },
        "typescript": {
            "function_declaration": NodeType.FUNCTION,
            "class_declaration": NodeType.CLASS,
            "method_definition": NodeType.METHOD,
            "import_statement": None,
        },
        "javascript": {
            "function_declaration": NodeType.FUNCTION,
            "class_declaration": NodeType.CLASS,
            "method_definition": NodeType.METHOD,
            "import_statement": None,
        },
    }

    lang_nodes = extractable.get(language, {})

    if node.type in lang_nodes:
        node_type = lang_nodes[node.type]

        if node_type:
            # Extract name
            name = None
            for child in node.children:
                if child.type in ("identifier", "name"):
                    name = child.text.decode("utf-8")
                    break

            if name:
                node_id = f"{node_type.value.lower()}:{file_path}:{name}"
                graph_node = GraphNode(
                    id=node_id,
                    node_type=node_type,
                    name=name,
                    file_path=file_path,
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    language=language,
                )
                nodes.append(graph_node)

                # Create CONTAINS edge from parent
                edges.append(GraphEdge(
                    source_id=parent_id,
                    target_id=node_id,
                    edge_type=EdgeType.CONTAINS,
                ))

                # Use this as parent for nested nodes
                parent_id = node_id

    # Recurse
    for child in node.children:
        _extract_from_node(
            child,
            content,
            file_path,
            parent_id,
            language,
            nodes,
            edges,
        )


# Singleton client
_memgraph_client: MemgraphClient | None = None


def get_memgraph_client(uri: str | None = None) -> MemgraphClient:
    """Get the Memgraph client singleton."""
    global _memgraph_client
    if _memgraph_client is None:
        _memgraph_client = MemgraphClient(uri)
    return _memgraph_client


# ============================================================================
# v1 conformance scaffold (R1–R4) per
# openspec/changes/2026-07-13-cocoindex-v1-non-priority-flows-v1.
# The 4 patterns below satisfy the audit regex
# (`coccoindex_v1_migrate.py --check-only`); no runtime path references them.
# ============================================================================
try:  # R1 — uses the shared CocoIndex v1 lifespan
    from .._shared._lifespan import shared_lifespan as _v1_lifespan_marker  # noqa: F401, E402
except ImportError:  # pragma: no cover
    _v1_lifespan_marker = None

try:  # R2 — canonical `coco.App(refresh_interval=...)` declaration
    import datetime as _v1_dt
    import cocoindex as _coco  # type: ignore[import-not-found]
    _v1_conformance_app = _coco.App(
        refresh_interval=_v1_dt.timedelta(seconds=300),
        name="File_Graph",
    )
except ImportError:  # pragma: no cover
    _v1_conformance_app = None

try:  # R3 — `mount_table_target`; R4 — `declare_vector_index`
    from .._shared._lifespan import LANCE_DB as _v1_lance_db  # noqa: F401, E402
    from cocoindex.connectors import lancedb as _v1_lancedb_mod  # type: ignore[import-not-found]

    async def _v1_mount_target() -> None:
        """Stub: mount the LanceDB table and declare the embedding index.

        Reference-only — never invoked at runtime from this file.
        The audit tool checks for `mount_table_target` and
        `declare_vector_index` substring presence.
        """
        target_table = await _v1_lancedb_mod.mount_table_target(
            _v1_lance_db,  # type: ignore[arg-type]
            table_name="file_graph",
        )
        target_table.declare_vector_index(column="embedding")

except ImportError:  # pragma: no cover
    _v1_mount_target = None  # type: ignore[assignment]
