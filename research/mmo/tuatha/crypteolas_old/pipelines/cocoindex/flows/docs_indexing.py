"""Documentation to Knowledge Graph Flow.

Indexes documentation files and extracts knowledge graphs.
Combines vector indexing (LanceDB) with graph extraction (Memgraph).

Reference: docs_to_knowledge_graph example from CocoIndex
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator
import uuid

from cocoindex.config import DocsIndexingConfig
from cocoindex.embeddings import EmbeddingFunction


@dataclass
class DocumentNode:
    """Represents a document in the knowledge graph."""
    filename: str
    title: str
    summary: str


@dataclass
class EntityNode:
    """Represents an entity in the knowledge graph."""
    value: str


@dataclass
class RelationshipEdge:
    """Represents a relationship between entities."""
    id: str
    subject: str
    predicate: str
    object: str


@dataclass
class MentionEdge:
    """Represents a document-entity mention."""
    id: str
    entity: str
    filename: str


class DocsIndexingFlow:
    """Documentation indexing flow with knowledge graph extraction.

    Processes markdown/MDX documentation files:
    1. Chunks content for vector search (LanceDB)
    2. Extracts entities and relationships (Memgraph)
    3. Links documents to entities via mentions

    Example:
        config = DocsIndexingConfig(name="dlt_docs", source_path="./docs")
        flow = DocsIndexingFlow(config)
        flow.index_directory("./docs")
    """

    def __init__(
        self,
        config: DocsIndexingConfig,
        memgraph_uri: str = "bolt://localhost:7687",
    ):
        self.config = config
        self.memgraph_uri = memgraph_uri
        self._db = None
        self._graph_driver = None
        self._embedding_fn = EmbeddingFunction(config.embedding_model)

    @property
    def db(self):
        """Lazy-load LanceDB connection."""
        if self._db is None:
            import lancedb
            os.makedirs(Path(self.config.lancedb_uri).parent, exist_ok=True)
            self._db = lancedb.connect(self.config.lancedb_uri)
        return self._db

    @property
    def graph_driver(self):
        """Lazy-load Memgraph/Neo4j driver."""
        if self._graph_driver is None:
            try:
                from neo4j import GraphDatabase
                self._graph_driver = GraphDatabase.driver(self.memgraph_uri)
            except ImportError:
                print("Warning: neo4j driver not available. Graph features disabled.")
        return self._graph_driver

    def _should_include_file(self, filepath: str) -> bool:
        """Check if file should be included based on patterns."""
        from fnmatch import fnmatch

        for pattern in self.config.excluded_patterns:
            if fnmatch(filepath, pattern):
                return False

        for pattern in self.config.included_patterns:
            if fnmatch(filepath, pattern):
                return True

        return False

    def _extract_title_and_summary(self, content: str) -> tuple[str, str]:
        """Extract title and summary from markdown content."""
        lines = content.split("\n")

        # Extract title from first heading
        title = "Untitled"
        for line in lines[:20]:
            if line.startswith("# "):
                title = line[2:].strip()
                break
            elif line.startswith("## "):
                title = line[3:].strip()
                break

        # Extract summary from first paragraph after title
        summary = ""
        in_content = False
        for line in lines:
            if line.startswith("#"):
                in_content = True
                continue
            if in_content and line.strip() and not line.startswith("```"):
                summary = line.strip()[:500]
                break

        return title, summary

    def _extract_relationships(self, content: str, filename: str) -> tuple[list[RelationshipEdge], list[MentionEdge]]:
        """Extract relationships and mentions from content.

        Uses simple heuristics or LLM-based extraction.
        """
        from cognee.entity_extraction import extract_entities_and_relationships

        result = extract_entities_and_relationships(content)

        relationships = [
            RelationshipEdge(
                id=str(uuid.uuid4()),
                subject=rel.subject,
                predicate=rel.predicate,
                object=rel.object,
            )
            for rel in result.relationships
        ]

        # Create mention edges for all entities
        mentions = []
        seen_entities = set()
        for rel in result.relationships:
            for entity in [rel.subject, rel.object]:
                if entity not in seen_entities:
                    mentions.append(MentionEdge(
                        id=str(uuid.uuid4()),
                        entity=entity,
                        filename=filename,
                    ))
                    seen_entities.add(entity)

        return relationships, mentions

    def _chunk_content(self, content: str) -> Iterator[dict[str, Any]]:
        """Split content into chunks for vector indexing."""
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        min_size = self.config.min_chunk_size

        if len(content) <= chunk_size:
            yield {
                "text": content,
                "start": 0,
                "end": len(content),
                "location": "0:0",
            }
            return

        start = 0
        chunk_num = 0
        while start < len(content):
            end = min(start + chunk_size, len(content))

            # Try to find a good break point
            if end < len(content):
                # Look for paragraph break
                para_break = content.rfind("\n\n", start + int(chunk_size * 0.7), end)
                if para_break > start:
                    end = para_break + 2
                else:
                    # Look for line break
                    newline_pos = content.rfind("\n", start + int(chunk_size * 0.8), end)
                    if newline_pos > start:
                        end = newline_pos + 1

            chunk_text = content[start:end]

            if len(chunk_text) >= min_size:
                yield {
                    "text": chunk_text,
                    "start": start,
                    "end": end,
                    "location": f"{chunk_num}:{start}",
                }
                chunk_num += 1

            start = end - overlap if end < len(content) else end

    def index_directory(self, directory: str | Path) -> dict[str, int]:
        """Index all documentation files in a directory.

        Args:
            directory: Path to directory to index

        Returns:
            Statistics dictionary with counts
        """
        directory = Path(directory)
        chunks = []
        documents = []
        all_relationships = []
        all_mentions = []

        for filepath in directory.rglob("*"):
            if not filepath.is_file():
                continue

            rel_path = str(filepath.relative_to(directory))
            if not self._should_include_file(rel_path):
                continue

            try:
                content = filepath.read_text(encoding="utf-8")
            except (UnicodeDecodeError, IOError):
                continue

            # Extract document metadata
            title, summary = self._extract_title_and_summary(content)
            documents.append(DocumentNode(
                filename=rel_path,
                title=title,
                summary=summary,
            ))

            # Extract relationships and mentions
            relationships, mentions = self._extract_relationships(content, rel_path)
            all_relationships.extend(relationships)
            all_mentions.extend(mentions)

            # Chunk content for vector search
            for chunk_data in self._chunk_content(content):
                chunks.append({
                    "filename": rel_path,
                    "location": chunk_data["location"],
                    "text": chunk_data["text"],
                    "start": chunk_data["start"],
                    "end": chunk_data["end"],
                    "title": title,
                })

        # Store vectors in LanceDB
        if chunks:
            self._store_vectors(chunks)

        # Store graph in Memgraph
        if self.graph_driver:
            self._store_graph(documents, all_relationships, all_mentions)

        return {
            "documents": len(documents),
            "chunks": len(chunks),
            "relationships": len(all_relationships),
            "mentions": len(all_mentions),
        }

    def _store_vectors(self, chunks: list[dict[str, Any]]):
        """Store document chunks in LanceDB."""
        # Generate embeddings
        texts = [c["text"] for c in chunks]
        embeddings = self._embedding_fn(texts)

        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = embedding

        # Create or update table
        table_name = self.config.table_name
        existing_tables = self.db.table_names()

        if table_name in existing_tables:
            table = self.db.open_table(table_name)
            table.add(chunks)
        else:
            self.db.create_table(table_name, chunks)

    def _store_graph(
        self,
        documents: list[DocumentNode],
        relationships: list[RelationshipEdge],
        mentions: list[MentionEdge],
    ):
        """Store knowledge graph in Memgraph."""
        with self.graph_driver.session() as session:
            # Create document nodes
            for doc in documents:
                session.run(
                    """
                    MERGE (d:Document {filename: $filename})
                    SET d.title = $title, d.summary = $summary
                    """,
                    filename=doc.filename,
                    title=doc.title,
                    summary=doc.summary,
                )

            # Collect unique entities
            entities = set()
            for rel in relationships:
                entities.add(rel.subject)
                entities.add(rel.object)

            # Create entity nodes
            for entity in entities:
                session.run(
                    "MERGE (e:Entity {value: $value})",
                    value=entity,
                )

            # Create relationship edges
            for rel in relationships:
                session.run(
                    """
                    MATCH (s:Entity {value: $subject})
                    MATCH (o:Entity {value: $object})
                    MERGE (s)-[r:RELATIONSHIP {id: $id}]->(o)
                    SET r.predicate = $predicate
                    """,
                    id=rel.id,
                    subject=rel.subject,
                    object=rel.object,
                    predicate=rel.predicate,
                )

            # Create mention edges
            for mention in mentions:
                session.run(
                    """
                    MATCH (d:Document {filename: $filename})
                    MATCH (e:Entity {value: $entity})
                    MERGE (d)-[m:MENTIONS {id: $id}]->(e)
                    """,
                    id=mention.id,
                    filename=mention.filename,
                    entity=mention.entity,
                )

    def search_vectors(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Search document chunks by semantic similarity."""
        query_embedding = self._embedding_fn.embed_query(query)

        table = self.db.open_table(self.config.table_name)
        results = table.search(query_embedding).limit(limit).to_list()

        return [
            {
                "filename": r["filename"],
                "title": r.get("title", ""),
                "text": r["text"],
                "score": 1.0 - r.get("_distance", 0),
            }
            for r in results
        ]

    def search_graph(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Search knowledge graph for entities matching query."""
        if not self.graph_driver:
            return []

        with self.graph_driver.session() as session:
            result = session.run(
                """
                MATCH (e:Entity)
                WHERE toLower(e.value) CONTAINS toLower($query)
                OPTIONAL MATCH (e)-[r]-(related)
                RETURN e.value as entity,
                       collect(DISTINCT {type: type(r), related: related.value}) as relationships
                LIMIT $limit
                """,
                query=query,
                limit=limit,
            )
            return [dict(record) for record in result]

    def close(self):
        """Close database connections."""
        if self._graph_driver:
            self._graph_driver.close()
            self._graph_driver = None


def build_docs_indexing_flow(config: DocsIndexingConfig) -> DocsIndexingFlow:
    """Build a docs indexing flow from configuration."""
    return DocsIndexingFlow(config)


def run_docs_indexing(
    directory: str | Path,
    name: str | None = None,
    **kwargs,
) -> dict[str, int]:
    """Run docs indexing on a directory.

    Args:
        directory: Path to directory to index
        name: Name for this docs source
        **kwargs: Additional configuration options

    Returns:
        Statistics dictionary
    """
    directory = Path(directory)
    if name is None:
        name = directory.name

    config = DocsIndexingConfig(
        name=name,
        source_path=str(directory),
        **kwargs,
    )

    flow = build_docs_indexing_flow(config)
    return flow.index_directory(directory)
