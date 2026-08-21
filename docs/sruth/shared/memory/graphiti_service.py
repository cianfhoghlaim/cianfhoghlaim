"""Graphiti temporal knowledge graph service.

Graphiti provides bi-temporal knowledge graphs for tracking:
- Valid time: When a fact is true in the real world
- Transaction time: When we recorded the fact

This is critical for curriculum versioning, exam paper tracking,
and tracking changes in educational standards over time.

Usage:
    from sruth.shared.memory.graphiti_service import GraphitiService

    service = GraphitiService()
    await service.add_entity("LearningOutcome", id="LO-001", ...)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

try:
    from graphiti import Graphiti
    from graphiti.core import GraphConfig
    from graphiti.core.edges import Edge as GraphitiEdge
    from graphiti.core.nodes import Node as GraphitiNode

    GRAPHITI_AVAILABLE = True
except ImportError:
    GRAPHITI_AVAILABLE = False
    Graphiti = None
    GraphConfig = None
    GraphitiEdge = None
    GraphitiNode = None


@dataclass
class GraphitiConfig:
    """Configuration for Graphiti temporal knowledge graph."""

    # FalkorDB connection
    uri: str = "redis://localhost:6379"
    username: str | None = None
    password: str | None = None

    # Graph name
    graph_name: str = "graphiti_graph"

    # Temporal settings
    track_valid_time: bool = True
    track_transaction_time: bool = True

    # Entity types to track
    entity_types: list[str] = field(
        default_factory=lambda: [
            "CurriculumStandard",
            "LearningOutcome",
            "Subject",
            "ExamPaper",
            "Document",
        ]
    )

    @classmethod
    def from_env(cls) -> GraphitiConfig:
        """Create configuration from environment variables."""
        return cls(
            uri=os.getenv("FALKORDB_URI", os.getenv("GRAPH_URI", "redis://localhost:6379")),
            username=os.getenv("FALKORDB_USER", os.getenv("GRAPH_USERNAME")),
            password=os.getenv("FALKORDB_PASSWORD", os.getenv("GRAPH_PASSWORD")),
            graph_name=os.getenv("GRAPHITI_GRAPH_NAME", "graphiti_graph"),
        )


@dataclass
class TemporalEntity:
    """Entity with temporal tracking."""

    entity_type: str
    id: str
    name: str
    properties: dict[str, Any] = field(default_factory=dict)

    # Temporal fields
    valid_from: datetime | None = None
    valid_to: datetime | None = None  # None means currently valid
    recorded_at: datetime | None = None

    # Source tracking
    source_document: str | None = None
    confidence: float = 1.0


@dataclass
class TemporalRelation:
    """Relationship with temporal tracking."""

    source_id: str
    target_id: str
    relation_type: str
    properties: dict[str, Any] = field(default_factory=dict)

    # Temporal fields
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    recorded_at: datetime | None = None


class GraphitiService:
    """Graphiti temporal knowledge graph service.

    Provides bi-temporal tracking for curriculum data,
    allowing us to see when facts were true and when we learned them.
    """

    def __init__(self, config: GraphitiConfig | None = None):
        """Initialize Graphiti service.

        Args:
            config: Service configuration
        """
        if not GRAPHITI_AVAILABLE:
            raise ImportError(
                "Graphiti is not installed. Install from: https://github.com/getpola/graphiti"
            )

        self.config = config or GraphitiConfig.from_env()
        self._client: Graphiti | None = None

    async def get_client(self) -> Graphiti:
        """Get or create Graphiti client."""
        if self._client is None:
            self._client = Graphiti(
                uri=self.config.uri,
                username=self.config.username,
                password=self.config.password,
                graph_name=self.config.graph_name,
            )
        return self._client

    async def add_entity(
        self,
        entity_type: str,
        id: str,
        name: str,
        properties: dict[str, Any] | None = None,
        valid_from: datetime | None = None,
        valid_to: datetime | None = None,
        source_document: str | None = None,
    ) -> str:
        """Add an entity with temporal tracking.

        Args:
            entity_type: Type of entity (CurriculumStandard, LearningOutcome, etc.)
            id: Unique identifier
            name: Human-readable name
            properties: Additional properties
            valid_from: When this entity becomes valid (default: now)
            valid_to: When this entity stops being valid (None = still valid)
            source_document: Source document reference

        Returns:
            Node UUID in the graph
        """
        client = await self.get_client()

        now = datetime.utcnow()
        valid_from = valid_from or now
        recorded_at = now

        # Combine with temporal properties
        all_properties = {
            **(properties or {}),
            "valid_from": valid_from.isoformat(),
            "recorded_at": recorded_at.isoformat(),
        }

        if valid_to:
            all_properties["valid_to"] = valid_to.isoformat()

        if source_document:
            all_properties["source_document"] = source_document

        # Create node
        node = GraphitiNode(
            label=entity_type,
            name=name,
            id=id,
            properties=all_properties,
        )

        result = await client.add_node(node)
        return result

    async def add_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        properties: dict[str, Any] | None = None,
        valid_from: datetime | None = None,
        valid_to: datetime | None = None,
    ) -> str:
        """Add a relationship with temporal tracking.

        Args:
            source_id: Source entity ID
            target_id: Target entity ID
            relation_type: Type of relationship (PART_OF, PREREQUISITE, etc.)
            properties: Additional properties
            valid_from: When relationship becomes valid
            valid_to: When relationship stops being valid

        Returns:
            Edge UUID in the graph
        """
        client = await self.get_client()

        now = datetime.utcnow()
        valid_from = valid_from or now
        recorded_at = now

        all_properties = {
            **(properties or {}),
            "valid_from": valid_from.isoformat(),
            "recorded_at": recorded_at.isoformat(),
        }

        if valid_to:
            all_properties["valid_to"] = valid_to.isoformat()

        # Create edge
        edge = GraphitiEdge(
            source_reference=source_id,
            target_reference=target_id,
            label=relation_type,
            properties=all_properties,
        )

        result = await client.add_edge(edge)
        return result

    async def get_entity_at_time(
        self,
        entity_id: str,
        at_time: datetime | None = None,
    ) -> dict[str, Any] | None:
        """Get entity state at a specific point in time.

        Args:
            entity_id: Entity identifier
            at_time: Point in time (default: now)

        Returns:
            Entity state or None
        """
        client = await self.get_client()

        at_time = at_time or datetime.utcnow()

        # Query for entity valid at the specified time
        query = f"""
        MATCH (n {{id: '{entity_id}'}})
        WHERE n.valid_from <= '{at_time.isoformat()}'
        AND (n.valid_to IS NULL OR n.valid_to > '{at_time.isoformat()}')
        RETURN n
        """

        results = await client.query(query)
        return results[0] if results else None

    async def get_entity_history(
        self,
        entity_id: str,
    ) -> list[dict[str, Any]]:
        """Get full temporal history of an entity.

        Args:
            entity_id: Entity identifier

        Returns:
            List of entity states ordered by time
        """
        client = await self.get_client()

        query = f"""
        MATCH (n {{id: '{entity_id}'}})
        RETURN n
        ORDER BY n.recorded_at DESC
        """

        results = await client.query(query)
        return results

    async def search_entity(
        self,
        entity_type: str,
        filters: dict[str, Any] | None = None,
        at_time: datetime | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Search for entities matching criteria.

        Args:
            entity_type: Type of entity
            filters: Property filters
            at_time: Point in time for temporal search
            limit: Result limit

        Returns:
            Matching entities
        """
        client = await self.get_client()

        at_time = at_time or datetime.utcnow()

        # Build query
        where_clauses = [f"n.valid_from <= '{at_time.isoformat()}'"]
        where_clauses.append("n.valid_to IS NULL OR n.valid_to > '{at_time.isoformat()}'")

        if filters:
            for key, value in filters.items():
                if isinstance(value, str):
                    where_clauses.append(f"n.{key} = '{value}'")
                else:
                    where_clauses.append(f"n.{key} = {value}")

        where_clause = " AND ".join(where_clauses)

        query = f"""
        MATCH (n:{entity_type})
        WHERE {where_clause}
        RETURN n
        LIMIT {limit}
        """

        results = await client.query(query)
        return results

    async def get_curriculum_tree(
        self,
        subject: str,
        at_time: datetime | None = None,
    ) -> dict[str, Any]:
        """Get curriculum tree for a subject at a point in time.

        Args:
            subject: Subject name
            at_time: Point in time

        Returns:
            Curriculum tree with strands, units, learning outcomes
        """
        at_time = at_time or datetime.utcnow()
        time_str = at_time.isoformat()

        query = f"""
        MATCH path = (subject:Subject {{name: '{subject}'}})-[:HAS_STRAND*]->(lo:LearningOutcome)
        WHERE all(n in nodes(path) WHERE
            n.valid_from <= '{time_str}' AND
            (n.valid_to IS NULL OR n.valid_to > '{time_str}')
        )
        RETURN path
        """

        client = await self.get_client()
        results = await client.query(query)

        # Build tree structure
        tree = {
            "subject": subject,
            "strands": {},
            "learning_outcomes": [],
        }

        for result in results:
            path = result.get("path", [])
            for node in path:
                if node.get("label") == "Strand":
                    strand_name = node.get("name")
                    if strand_name and strand_name not in tree["strands"]:
                        tree["strands"][strand_name] = {
                            "name": strand_name,
                            "units": {},
                        }
                elif node.get("label") == "StrandUnit":
                    unit_name = node.get("name")
                    # Add to parent strand
                elif node.get("label") == "LearningOutcome":
                    tree["learning_outcomes"].append(node)

        return tree

    async def track_curriculum_change(
        self,
        entity_id: str,
        old_properties: dict[str, Any],
        new_properties: dict[str, Any],
        change_description: str,
        changed_at: datetime | None = None,
    ) -> str:
        """Track a change to a curriculum entity.

        Creates a new version with valid_from set to change time,
        and sets valid_to on the old version.

        Args:
            entity_id: Entity being changed
            old_properties: Previous properties
            new_properties: New properties
            change_description: Description of the change
            changed_at: When the change occurred

        Returns:
            ID of the new entity version
        """
        changed_at = changed_at or datetime.utcnow()
        old_id = entity_id
        new_id = f"{entity_id}:{changed_at.isoformat()}"

        # Set valid_to on old entity
        await self.update_entity_validity(
            old_id,
            valid_to=changed_at,
        )

        # Create new entity version
        new_entity_id = await self.add_entity(
            entity_type=new_properties.get("entity_type", "CurriculumEntity"),
            id=new_id,
            name=new_properties.get("name", ""),
            properties={
                **new_properties,
                "previous_version": old_id,
                "change_description": change_description,
            },
            valid_from=changed_at,
        )

        return new_entity_id

    async def update_entity_validity(
        self,
        entity_id: str,
        valid_to: datetime | None = None,
    ) -> None:
        """Update validity period of an entity.

        Args:
            entity_id: Entity to update
            valid_to: New validity end time
        """
        client = await self.get_client()

        if valid_to:
            query = f"""
            MATCH (n {{id: '{entity_id}'}})
            SET n.valid_to = '{valid_to.isoformat()}'
            """
        else:
            query = f"""
            MATCH (n {{id: '{entity_id}'}})
            REMOVE n.valid_to
            """

        await client.query(query)

    async def find_prerequisite_chains(
        self,
        learning_outcome_id: str,
        max_depth: int = 5,
    ) -> list[dict[str, Any]]:
        """Find all prerequisite chains for a learning outcome.

        Args:
            learning_outcome_id: Starting LO ID
            max_depth: Maximum traversal depth

        Returns:
            List of prerequisite chains
        """
        query = f"""
        MATCH path = (lo:LearningOutcome {{id: '{learning_outcome_id}'}})<-[:PREREQUISITE*1..{max_depth}]*(prev:LearningOutcome)
        RETURN path
        """

        client = await self.get_client()
        results = await client.query(query)

        chains = []
        for result in results:
            path = result.get("path", [])
            chain = [node.get("name") for node in path]
            chains.append(chain)

        return chains

    async def close(self) -> None:
        """Close the client connection."""
        if self._client:
            await self._client.close()
            self._client = None


# ============================================================================
# Convenience Functions
# ============================================================================


async def create_curriculum_entity(
    name: str,
    entity_type: str,
    properties: dict[str, Any],
    config: GraphitiConfig | None = None,
) -> str:
    """Create a curriculum entity with temporal tracking.

    Args:
        name: Entity name
        entity_type: Type (LearningOutcome, Strand, etc.)
        properties: Entity properties
        config: Optional Graphiti configuration

    Returns:
        Entity ID
    """
    service = GraphitiService(config)
    entity_id = f"{entity_type}:{name}:{uuid4().hex[:8]}"
    await service.add_entity(
        entity_type=entity_type,
        id=entity_id,
        name=name,
        properties=properties,
    )
    await service.close()
    return entity_id
