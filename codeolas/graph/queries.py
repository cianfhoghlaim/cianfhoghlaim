"""
Graph queries for códeolas.

Provides Cypher query interface for code knowledge graphs.
"""

import logging
from typing import Any

from codeolas.core.config import get_config

logger = logging.getLogger(__name__)


class GraphQueries:
    """
    Query interface for code knowledge graphs.

    Provides common queries for code analysis:
    - Find callers of a function
    - Find dependencies of a file
    - Find class hierarchy
    - Find all usages of a symbol
    """

    def __init__(self):
        self._client = None

    @property
    def client(self):
        """Get Memgraph client."""
        if self._client is None:
            config = get_config()
            try:
                from neo4j import GraphDatabase

                self._client = GraphDatabase.driver(config.memgraph_uri)
            except ImportError:
                logger.warning("neo4j driver not installed")
            except Exception as e:
                logger.warning(f"Could not connect to Memgraph: {e}")

        return self._client

    def find_callers(self, function_name: str) -> list[dict[str, Any]]:
        """Find all functions that call a given function."""
        if not self.client:
            return []

        query = """
        MATCH (caller:Function)-[:CALLS]->(callee:Function {name: $name})
        RETURN caller.name AS caller_name,
               caller.file_path AS file_path,
               caller.start_line AS line
        """

        with self.client.session() as session:
            result = session.run(query, name=function_name)
            return [dict(record) for record in result]

    def find_usages(self, symbol_name: str) -> list[dict[str, Any]]:
        """Find all usages of a symbol."""
        if not self.client:
            return []

        query = """
        MATCH (user)-[:CALLS|USES|IMPORTS]->(symbol {name: $name})
        RETURN user.name AS user_name,
               labels(user)[0] AS user_type,
               user.file_path AS file_path,
               user.start_line AS line
        """

        with self.client.session() as session:
            result = session.run(query, name=symbol_name)
            return [dict(record) for record in result]

    def find_dependencies(self, file_path: str) -> list[dict[str, Any]]:
        """Find all dependencies of a file."""
        if not self.client:
            return []

        query = """
        MATCH (file:File {file_path: $path})-[:FILE_IMPORTS]->(dep)
        RETURN dep.name AS dependency,
               labels(dep)[0] AS type,
               dep.file_path AS source_file
        """

        with self.client.session() as session:
            result = session.run(query, path=file_path)
            return [dict(record) for record in result]

    def find_class_hierarchy(self, class_name: str) -> list[dict[str, Any]]:
        """Find class inheritance chain."""
        if not self.client:
            return []

        query = """
        MATCH path = (c:Class {name: $name})-[:CLASS_TO_CLASS|IMPLEMENTS*0..5]->(parent)
        RETURN [node in nodes(path) | node.name] AS hierarchy,
               length(path) AS depth
        ORDER BY depth
        """

        with self.client.session() as session:
            result = session.run(query, name=class_name)
            return [dict(record) for record in result]

    def find_interface_implementations(self, interface_name: str) -> list[dict[str, Any]]:
        """Find all classes implementing an interface."""
        if not self.client:
            return []

        query = """
        MATCH (c:Class)-[:IMPLEMENTS]->(i:Interface {name: $name})
        RETURN c.name AS class_name,
               c.file_path AS file_path,
               c.start_line AS line
        """

        with self.client.session() as session:
            result = session.run(query, name=interface_name)
            return [dict(record) for record in result]

    def get_file_structure(self, file_path: str) -> dict[str, Any]:
        """Get all symbols defined in a file."""
        if not self.client:
            return {"file_path": file_path, "symbols": [], "symbol_count": 0}

        query = """
        MATCH (f:File {file_path: $path})-[:FILE_DEFINES]->(symbol)
        RETURN labels(symbol)[0] AS type,
               symbol.name AS name,
               symbol.start_line AS line
        ORDER BY symbol.start_line
        """

        with self.client.session() as session:
            result = session.run(query, path=file_path)
            symbols = [dict(record) for record in result]

            return {
                "file_path": file_path,
                "symbols": symbols,
                "symbol_count": len(symbols),
            }

    def get_stats(self) -> dict[str, int]:
        """Get graph statistics."""
        if not self.client:
            return {}

        queries = {
            "files": "MATCH (n:File) RETURN count(n) AS count",
            "functions": "MATCH (n:Function) RETURN count(n) AS count",
            "classes": "MATCH (n:Class) RETURN count(n) AS count",
            "methods": "MATCH (n:Method) RETURN count(n) AS count",
            "imports": "MATCH ()-[r:FILE_IMPORTS]->() RETURN count(r) AS count",
            "calls": "MATCH ()-[r:CALLS]->() RETURN count(r) AS count",
        }

        stats = {}
        with self.client.session() as session:
            for key, query in queries.items():
                result = session.run(query)
                record = result.single()
                stats[key] = record["count"] if record else 0

        return stats
