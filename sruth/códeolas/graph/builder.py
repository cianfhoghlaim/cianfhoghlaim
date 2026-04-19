"""
Graph builder for códeolas.

Builds code knowledge graphs from AST analysis.
Uses 40+ relationship types from Knowledge Graph pattern.
"""

import logging
from pathlib import Path
from typing import Any

from sruth.códeolas.core.config import get_config
from sruth.códeolas.core.types import (
    CodeChunk,
    EdgeType,
    GraphEdge,
    GraphNode,
    NodeType,
    RelationshipType,
    SourceRange,
)

logger = logging.getLogger(__name__)


class GraphBuilder:
    """
    Builds code knowledge graphs from source files.

    Extracts nodes (files, functions, classes) and edges (calls, imports, extends)
    using Tree-sitter AST parsing.
    """

    def __init__(self, repo_path: str | Path | None = None):
        config = get_config()
        self.repo_path = Path(repo_path) if repo_path else Path(config.repo_path)
        self._client = None

    @property
    def client(self):
        """Get Memgraph client (lazy initialization)."""
        if self._client is None:
            config = get_config()
            try:
                from neo4j import GraphDatabase

                self._client = GraphDatabase.driver(config.memgraph_uri)
                logger.info(f"Connected to Memgraph: {config.memgraph_uri}")
            except ImportError:
                logger.warning("neo4j driver not installed, graph features unavailable")
            except Exception as e:
                logger.warning(f"Could not connect to Memgraph: {e}")

        return self._client

    async def build_from_chunks(
        self,
        chunks: list[CodeChunk],
    ) -> dict[str, Any]:
        """
        Build graph from code chunks.

        Args:
            chunks: List of code chunks

        Returns:
            Statistics about the graph built
        """
        nodes = []
        edges = []

        # Create file nodes
        files: dict[str, GraphNode] = {}
        for chunk in chunks:
            file_path = chunk.file_path
            if file_path not in files:
                file_id = f"file:{file_path}"
                files[file_path] = GraphNode(
                    id=file_id,
                    node_type=NodeType.FILE,
                    name=Path(file_path).name,
                    file_path=file_path,
                    language=chunk.language,
                )
                nodes.append(files[file_path])

        # Create chunk nodes
        for chunk in chunks:
            node = self._chunk_to_node(chunk)
            nodes.append(node)

            # Create CONTAINS edge from file
            file_id = f"file:{chunk.file_path}"
            edges.append(
                GraphEdge(
                    source_id=file_id,
                    target_id=node.id,
                    edge_type=RelationshipType.FILE_DEFINES,
                )
            )

        # Store in Memgraph if available
        if self.client:
            await self._store_graph(nodes, edges)

        return {
            "nodes_created": len(nodes),
            "edges_created": len(edges),
            "files": len(files),
        }

    def _chunk_to_node(self, chunk: CodeChunk) -> GraphNode:
        """Convert a CodeChunk to a GraphNode."""
        from sruth.códeolas.core.types import ChunkType

        # Map chunk type to node type
        type_map = {
            ChunkType.FUNCTION: NodeType.FUNCTION,
            ChunkType.CLASS: NodeType.CLASS,
            ChunkType.METHOD: NodeType.METHOD,
            ChunkType.MODULE: NodeType.MODULE,
            ChunkType.INTERFACE: NodeType.INTERFACE,
            ChunkType.STRUCT: NodeType.CLASS,
            ChunkType.ENUM: NodeType.ENUM,
            ChunkType.LAMBDA: NodeType.LAMBDA,
            ChunkType.PROPERTY: NodeType.PROPERTY,
            ChunkType.CONSTRUCTOR: NodeType.CONSTRUCTOR,
        }

        node_type = type_map.get(chunk.chunk_type, NodeType.FUNCTION)

        # Generate unique ID
        node_id = f"{node_type.value.lower()}:{chunk.file_path}:{chunk.start_line}"
        if chunk.name:
            node_id = f"{node_type.value.lower()}:{chunk.file_path}:{chunk.name}"

        return GraphNode(
            id=node_id,
            node_type=node_type,
            name=chunk.name or f"anonymous_{chunk.start_line}",
            file_path=chunk.file_path,
            source_range=chunk.source_range,
            start_line=chunk.start_line,
            end_line=chunk.end_line,
            language=chunk.language,
        )

    async def _store_graph(
        self,
        nodes: list[GraphNode],
        edges: list[GraphEdge],
    ) -> None:
        """Store graph in Memgraph."""
        if not self.client:
            return

        with self.client.session() as session:
            # Create nodes
            for node in nodes:
                query = f"""
                MERGE (n:{node.node_type.value} {{id: $id}})
                SET n.name = $name,
                    n.file_path = $file_path,
                    n.start_line = $start_line,
                    n.end_line = $end_line,
                    n.language = $language
                """
                session.run(
                    query,
                    id=node.id,
                    name=node.name,
                    file_path=node.file_path,
                    start_line=node.start_line,
                    end_line=node.end_line,
                    language=node.language,
                )

            # Create edges
            for edge in edges:
                edge_type = (
                    edge.edge_type.value
                    if hasattr(edge.edge_type, "value")
                    else str(edge.edge_type)
                )
                query = f"""
                MATCH (source {{id: $source_id}})
                MATCH (target {{id: $target_id}})
                MERGE (source)-[r:{edge_type}]->(target)
                """
                session.run(
                    query,
                    source_id=edge.source_id,
                    target_id=edge.target_id,
                )

        logger.info(f"Stored {len(nodes)} nodes and {len(edges)} edges in Memgraph")
