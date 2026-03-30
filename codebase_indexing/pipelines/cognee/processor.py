"""Cognee + Memgraph Knowledge Graph Processor.

Provides integration between Cognee for knowledge extraction and
Memgraph for graph storage and querying.

Reference: dlt_cognee_memgraph.py example
"""

import os
from dataclasses import dataclass
from typing import Any
import uuid


@dataclass
class MemgraphConfig:
    """Memgraph connection configuration."""
    uri: str = "bolt://localhost:7687"
    user: str = ""
    password: str = ""


class CogneeMemgraphProcessor:
    """Process documents through Cognee and store in Memgraph.

    This class integrates:
    - Cognee: AI-powered knowledge extraction
    - Memgraph: High-performance graph database

    Example:
        processor = CogneeMemgraphProcessor()
        await processor.process_documents(documents)
        results = await processor.search("What is DLT?")
    """

    def __init__(
        self,
        memgraph_config: MemgraphConfig | None = None,
        dataset_name: str = "github_knowledge",
    ):
        """Initialize the processor.

        Args:
            memgraph_config: Memgraph connection config (reads from env if None)
            dataset_name: Name for the Cognee dataset
        """
        if memgraph_config is None:
            memgraph_config = MemgraphConfig(
                uri=os.environ.get("GRAPH_DATABASE_URL", "bolt://localhost:7687"),
                user=os.environ.get("GRAPH_DATABASE_USERNAME", ""),
                password=os.environ.get("GRAPH_DATABASE_PASSWORD", ""),
            )

        self.memgraph_config = memgraph_config
        self.dataset_name = dataset_name
        self._driver = None
        self._cognee_configured = False

    @property
    def driver(self):
        """Lazy-load Neo4j/Memgraph driver."""
        if self._driver is None:
            from neo4j import GraphDatabase

            self._driver = GraphDatabase.driver(
                self.memgraph_config.uri,
                auth=(self.memgraph_config.user, self.memgraph_config.password)
                if self.memgraph_config.user else None,
            )
        return self._driver

    def _configure_cognee(self):
        """Configure Cognee with Memgraph settings."""
        if self._cognee_configured:
            return

        try:
            import cognee

            # Configure Cognee to use Memgraph
            cognee.config.set_graph_database_provider("memgraph")
            cognee.config.set_graph_database_url(self.memgraph_config.uri)
            if self.memgraph_config.user:
                cognee.config.set_graph_database_username(self.memgraph_config.user)
            if self.memgraph_config.password:
                cognee.config.set_graph_database_password(self.memgraph_config.password)

            self._cognee_configured = True
        except ImportError:
            pass

    async def process_documents(self, documents: list[dict[str, Any]]) -> None:
        """Process documents through Cognee to build knowledge graph.

        Args:
            documents: List of documents with 'content' and optional metadata
        """
        try:
            import cognee
            self._configure_cognee()

            for doc in documents:
                content = doc.get("content", "")
                if not content:
                    continue

                title = doc.get("title", "Untitled")
                print(f"Processing: {title}")

                # Add content to Cognee
                await cognee.add(content, dataset_name=self.dataset_name)

                # Add metadata if present
                metadata = {k: v for k, v in doc.items() if k not in ["content"]}
                if metadata:
                    metadata_str = ". ".join(f"{k}: {v}" for k, v in metadata.items())
                    await cognee.add(metadata_str, dataset_name=f"{self.dataset_name}_metadata")

            # Build the knowledge graph
            print("Building knowledge graph with Cognee...")
            await cognee.cognify()
            print("Knowledge graph construction completed!")

        except ImportError:
            print("Cognee not available. Using fallback extraction.")
            await self._process_without_cognee(documents)

    async def _process_without_cognee(self, documents: list[dict[str, Any]]) -> None:
        """Fallback processing without Cognee.

        Uses local entity extraction and direct Memgraph storage.
        """
        from cognee.entity_extraction import extract_entities_and_relationships

        with self.driver.session() as session:
            for doc in documents:
                content = doc.get("content", "")
                filename = doc.get("filename", str(uuid.uuid4()))

                if not content:
                    continue

                # Extract entities and relationships
                result = extract_entities_and_relationships(content)

                # Create document node
                session.run(
                    """
                    MERGE (d:Document {filename: $filename})
                    SET d.title = $title, d.summary = $summary
                    """,
                    filename=filename,
                    title=result.summary.title,
                    summary=result.summary.summary,
                )

                # Create entity nodes and relationships
                for rel in result.relationships:
                    # Create entities
                    session.run(
                        """
                        MERGE (s:Entity {value: $subject})
                        MERGE (o:Entity {value: $object})
                        MERGE (s)-[r:RELATIONSHIP {predicate: $predicate}]->(o)
                        """,
                        subject=rel.subject,
                        object=rel.object,
                        predicate=rel.predicate,
                    )

                    # Create mentions (document -> entity links)
                    session.run(
                        """
                        MATCH (d:Document {filename: $filename})
                        MATCH (e:Entity {value: $entity})
                        MERGE (d)-[:MENTIONS]->(e)
                        """,
                        filename=filename,
                        entity=rel.subject,
                    )
                    session.run(
                        """
                        MATCH (d:Document {filename: $filename})
                        MATCH (e:Entity {value: $entity})
                        MERGE (d)-[:MENTIONS]->(e)
                        """,
                        filename=filename,
                        entity=rel.object,
                    )

    async def search(self, query: str) -> list[dict[str, Any]]:
        """Search the knowledge graph.

        Args:
            query: Search query

        Returns:
            List of search results
        """
        try:
            import cognee
            self._configure_cognee()

            results = await cognee.search(query_text=query)
            return results
        except ImportError:
            return self._search_memgraph(query)

    def _search_memgraph(self, query: str) -> list[dict[str, Any]]:
        """Direct Memgraph search fallback."""
        with self.driver.session() as session:
            # Search for entities matching the query
            result = session.run(
                """
                MATCH (e:Entity)
                WHERE toLower(e.value) CONTAINS toLower($query)
                OPTIONAL MATCH (e)-[r]-(related)
                RETURN e.value as entity,
                       collect(DISTINCT {type: type(r), related: related.value}) as relationships
                LIMIT 10
                """,
                query=query,
            )

            return [dict(record) for record in result]

    def run_cypher(self, query: str, params: dict | None = None) -> list[dict[str, Any]]:
        """Execute a raw Cypher query.

        Args:
            query: Cypher query string
            params: Query parameters

        Returns:
            Query results
        """
        with self.driver.session() as session:
            result = session.run(query, params or {})
            return [dict(record) for record in result]

    def get_graph_stats(self) -> dict[str, int]:
        """Get statistics about the knowledge graph.

        Returns:
            Dictionary with node and edge counts
        """
        with self.driver.session() as session:
            # Count nodes by label
            node_counts = {}
            result = session.run("MATCH (n) RETURN labels(n)[0] as label, count(n) as count")
            for record in result:
                node_counts[record["label"]] = record["count"]

            # Count edges by type
            edge_counts = {}
            result = session.run("MATCH ()-[r]->() RETURN type(r) as type, count(r) as count")
            for record in result:
                edge_counts[record["type"]] = record["count"]

            return {
                "nodes": node_counts,
                "edges": edge_counts,
                "total_nodes": sum(node_counts.values()),
                "total_edges": sum(edge_counts.values()),
            }

    def get_entities(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get all entities from the graph.

        Args:
            limit: Maximum entities to return

        Returns:
            List of entity records
        """
        return self.run_cypher(
            "MATCH (e:Entity) RETURN e.value as entity ORDER BY e.value LIMIT $limit",
            {"limit": limit},
        )

    def get_relationships_for_entity(self, entity: str) -> list[dict[str, Any]]:
        """Get all relationships for a specific entity.

        Args:
            entity: Entity value to look up

        Returns:
            List of relationship records
        """
        return self.run_cypher(
            """
            MATCH (e:Entity {value: $entity})-[r]-(related)
            RETURN type(r) as relationship,
                   CASE WHEN startNode(r) = e THEN 'outgoing' ELSE 'incoming' END as direction,
                   related.value as related_entity,
                   r.predicate as predicate
            """,
            {"entity": entity},
        )

    def close(self):
        """Close the database connection."""
        if self._driver:
            self._driver.close()
            self._driver = None


# Convenience functions for sync usage
def process_github_issues(issues: list[dict[str, Any]], config: MemgraphConfig | None = None):
    """Process GitHub issues into knowledge graph.

    Args:
        issues: List of issue data from GitHub API
        config: Memgraph connection config
    """
    import asyncio

    processor = CogneeMemgraphProcessor(config)

    documents = [
        {
            "content": f"# {issue.get('title', '')}\n\n{issue.get('body', '')}",
            "filename": f"issue_{issue.get('number', issue.get('id'))}",
            "title": issue.get("title", ""),
            "type": "issue",
            "state": issue.get("state", ""),
            "labels": [l.get("name", "") for l in issue.get("labels", [])],
        }
        for issue in issues
    ]

    asyncio.run(processor.process_documents(documents))
    return processor


def process_markdown_files(files: list[tuple[str, str]], config: MemgraphConfig | None = None):
    """Process markdown files into knowledge graph.

    Args:
        files: List of (filename, content) tuples
        config: Memgraph connection config
    """
    import asyncio

    processor = CogneeMemgraphProcessor(config)

    documents = [
        {"filename": filename, "content": content}
        for filename, content in files
    ]

    asyncio.run(processor.process_documents(documents))
    return processor
