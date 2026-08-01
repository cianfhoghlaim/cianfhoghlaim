"""
Temporal Graph Client for Bi-Temporal Knowledge Graph.

Implements Graphiti-style temporal tracking:
- Reality time queries (what was true at a point in time)
- System time queries (what the system knew at a point in time)
- Edge invalidation with history preservation
- Episode management for traceability

Extends the base MemgraphClient with temporal operations.
"""

import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Generator

from .memgraph_client import MemgraphClient
from .temporal import (
    CurriculumChange,
    EdgeStatus,
    Episode,
    EpisodeSourceType,
    TemporalEdge,
    TemporalQuery,
)

logger = logging.getLogger(__name__)


class TemporalGraphClient(MemgraphClient):
    """
    Graph client with bi-temporal edge support.

    Extends MemgraphClient with:
    - Temporal edge creation and management
    - Episode tracking
    - Point-in-time queries
    - Edge version history
    """

    # =========================================================================
    # Schema Setup
    # =========================================================================

    def setup_temporal_schema(self) -> dict:
        """Create indexes and constraints for temporal data."""
        schema_queries = [
            # Episode constraints and indexes
            "CREATE CONSTRAINT IF NOT EXISTS ON (e:Episode) ASSERT e.id IS UNIQUE",
            "CREATE INDEX IF NOT EXISTS FOR (e:Episode) ON (e.reference_time)",
            "CREATE INDEX IF NOT EXISTS FOR (e:Episode) ON (e.thread_id)",
            "CREATE INDEX IF NOT EXISTS FOR (e:Episode) ON (e.source_type)",
            # Temporal edge property indexes (on relationships)
            # Note: Memgraph indexes relationships differently
        ]

        results = []
        for query in schema_queries:
            try:
                self.execute_write(query)
                results.append({"query": query[:50], "status": "success"})
            except Exception as e:
                results.append({"query": query[:50], "status": "error", "error": str(e)})
                logger.warning(f"Schema setup warning: {e}")

        logger.info("Temporal schema setup complete")
        return {"operations": results}

    # =========================================================================
    # Temporal Edge Operations
    # =========================================================================

    def create_temporal_edge(self, edge: TemporalEdge) -> dict:
        """
        Create a temporal edge between two nodes.

        The edge includes both reality time and system time tracking.
        """
        query = """
        MATCH (source {id: $source_id})
        MATCH (target {id: $target_id})
        CREATE (source)-[r:TEMPORAL_EDGE {
            edge_id: $edge_id,
            relation_type: $relation_type,
            fact: $fact,
            valid_at: datetime($valid_at),
            invalid_at: $invalid_at,
            created_at: datetime($created_at),
            expired_at: $expired_at,
            episode_id: $episode_id,
            confidence: $confidence,
            source_document_id: $source_document_id,
            extraction_method: $extraction_method
        }]->(target)
        RETURN r
        """

        params = {
            "source_id": edge.source_id,
            "target_id": edge.target_id,
            "edge_id": edge.id,
            "relation_type": edge.relation_type,
            "fact": edge.fact,
            "valid_at": edge.valid_at.isoformat(),
            "invalid_at": edge.invalid_at.isoformat() if edge.invalid_at else None,
            "created_at": edge.created_at.isoformat(),
            "expired_at": edge.expired_at.isoformat() if edge.expired_at else None,
            "episode_id": edge.episode_id,
            "confidence": edge.confidence,
            "source_document_id": edge.source_document_id,
            "extraction_method": edge.extraction_method,
        }

        return self.execute_write(query, params)

    def invalidate_edge(
        self,
        edge_id: str,
        invalid_at: datetime | None = None,
        reason: str = "superseded",
    ) -> dict:
        """
        Soft-delete an edge by setting invalid_at.

        Preserves the edge for historical queries.
        """
        query = """
        MATCH ()-[r:TEMPORAL_EDGE {edge_id: $edge_id}]->()
        WHERE r.invalid_at IS NULL
        SET r.invalid_at = datetime($invalid_at),
            r.invalidation_reason = $reason
        RETURN r.edge_id as edge_id, r.invalid_at as invalid_at
        """

        return self.execute_write(
            query,
            {
                "edge_id": edge_id,
                "invalid_at": (invalid_at or datetime.utcnow()).isoformat(),
                "reason": reason,
            },
        )

    def expire_edge(
        self,
        edge_id: str,
        expired_at: datetime | None = None,
    ) -> dict:
        """
        System-expire an edge (e.g., during reprocessing).

        Sets expired_at in system time.
        """
        query = """
        MATCH ()-[r:TEMPORAL_EDGE {edge_id: $edge_id}]->()
        WHERE r.expired_at IS NULL
        SET r.expired_at = datetime($expired_at)
        RETURN r.edge_id as edge_id, r.expired_at as expired_at
        """

        return self.execute_write(
            query,
            {
                "edge_id": edge_id,
                "expired_at": (expired_at or datetime.utcnow()).isoformat(),
            },
        )

    def supersede_edge(
        self,
        old_edge_id: str,
        new_edge: TemporalEdge,
    ) -> dict:
        """
        Replace an edge with a new version.

        1. Invalidates the old edge
        2. Creates the new edge
        3. Creates SUPERSEDED_BY relationship
        """
        # Invalidate old edge
        self.invalidate_edge(old_edge_id, reason="superseded")

        # Create new edge
        self.create_temporal_edge(new_edge)

        # Create supersession relationship
        query = """
        MATCH ()-[old:TEMPORAL_EDGE {edge_id: $old_id}]->()
        MATCH ()-[new:TEMPORAL_EDGE {edge_id: $new_id}]->()
        CREATE (old)-[:SUPERSEDED_BY]->(new)
        RETURN old.edge_id as old, new.edge_id as new
        """

        return self.execute_write(
            query,
            {"old_id": old_edge_id, "new_id": new_edge.id},
        )

    # =========================================================================
    # Point-in-Time Queries
    # =========================================================================

    def query_edges_at_time(
        self,
        temporal_query: TemporalQuery,
        source_id: str | None = None,
        target_id: str | None = None,
        relation_type: str | None = None,
    ) -> list[dict]:
        """
        Query edges valid at a specific point in time.

        Supports both reality time and system time filtering.
        """
        conditions = [temporal_query.to_cypher_conditions("r")]

        if source_id:
            conditions.append(f"source.id = '{source_id}'")
        if target_id:
            conditions.append(f"target.id = '{target_id}'")
        if relation_type:
            conditions.append(f"r.relation_type = '{relation_type}'")

        where_clause = " AND ".join(conditions)

        query = f"""
        MATCH (source)-[r:TEMPORAL_EDGE]->(target)
        WHERE {where_clause}
        RETURN r.edge_id as edge_id,
               source.id as source_id,
               target.id as target_id,
               r.relation_type as relation_type,
               r.fact as fact,
               r.valid_at as valid_at,
               r.invalid_at as invalid_at,
               r.confidence as confidence
        ORDER BY r.valid_at DESC
        """

        return self.execute(query)

    def get_curriculum_at_time(
        self,
        subject_code: str,
        as_of: datetime,
    ) -> list[dict]:
        """
        Get the curriculum tree as it existed at a specific point in time.

        Returns strands, units, and learning outcomes valid at that time.
        """
        as_of_str = as_of.isoformat()

        query = f"""
        MATCH (sub:Subject {{code: $subject_code}})
        MATCH (sub)-[r1:HAS_STRAND]->(st:Strand)
        WHERE r1.valid_at <= datetime('{as_of_str}')
        AND (r1.invalid_at IS NULL OR r1.invalid_at > datetime('{as_of_str}'))

        OPTIONAL MATCH (st)-[r2:HAS_UNIT]->(su:StrandUnit)
        WHERE r2.valid_at <= datetime('{as_of_str}')
        AND (r2.invalid_at IS NULL OR r2.invalid_at > datetime('{as_of_str}'))

        OPTIONAL MATCH (su)-[r3:HAS_OUTCOME]->(lo:LearningOutcome)
        WHERE r3.valid_at <= datetime('{as_of_str}')
        AND (r3.invalid_at IS NULL OR r3.invalid_at > datetime('{as_of_str}'))

        RETURN sub.code as subject,
               collect(DISTINCT {{
                   strand: st.name_en,
                   units: collect(DISTINCT {{
                       unit: su.name_en,
                       outcomes: collect(DISTINCT lo.code)
                   }})
               }}) as curriculum
        """

        return self.execute(query, {"subject_code": subject_code})

    def get_edge_history(self, edge_id: str) -> list[dict]:
        """
        Get the full version history of an edge.

        Follows SUPERSEDED_BY chain to find all versions.
        """
        query = """
        MATCH path = (first)-[:SUPERSEDED_BY*0..]->(current)
        WHERE first.edge_id = $edge_id OR current.edge_id = $edge_id
        UNWIND nodes(path) as version
        WITH version
        ORDER BY version.created_at
        RETURN version.edge_id as edge_id,
               version.fact as fact,
               version.valid_at as valid_at,
               version.invalid_at as invalid_at,
               version.created_at as created_at,
               version.expired_at as expired_at,
               CASE WHEN version.invalid_at IS NOT NULL THEN 'invalidated'
                    WHEN version.expired_at IS NOT NULL THEN 'expired'
                    ELSE 'current' END as status
        """

        return self.execute(query, {"edge_id": edge_id})

    def compare_curriculum_versions(
        self,
        subject_code: str,
        time_a: datetime,
        time_b: datetime,
    ) -> dict:
        """
        Compare curriculum between two points in time.

        Returns added, removed, and modified outcomes.
        """
        outcomes_a = set()
        outcomes_b = set()

        # Get outcomes at time A
        results_a = self.get_curriculum_at_time(subject_code, time_a)
        for row in results_a:
            for strand in row.get("curriculum", []):
                for unit in strand.get("units", []):
                    for code in unit.get("outcomes", []):
                        outcomes_a.add(code)

        # Get outcomes at time B
        results_b = self.get_curriculum_at_time(subject_code, time_b)
        for row in results_b:
            for strand in row.get("curriculum", []):
                for unit in strand.get("units", []):
                    for code in unit.get("outcomes", []):
                        outcomes_b.add(code)

        return {
            "time_a": time_a.isoformat(),
            "time_b": time_b.isoformat(),
            "subject": subject_code,
            "added": list(outcomes_b - outcomes_a),
            "removed": list(outcomes_a - outcomes_b),
            "unchanged": list(outcomes_a & outcomes_b),
            "total_a": len(outcomes_a),
            "total_b": len(outcomes_b),
        }

    # =========================================================================
    # Episode Management
    # =========================================================================

    def create_episode(self, episode: Episode) -> dict:
        """
        Create an episode node.

        Episodes are atomic memory units for traceability.
        """
        query = """
        CREATE (e:Episode {
            id: $id,
            name: $name,
            body: $body,
            body_type: $body_type,
            source_type: $source_type,
            source_description: $source_description,
            reference_time: datetime($reference_time),
            transaction_time: datetime($transaction_time),
            user_id: $user_id,
            thread_id: $thread_id,
            agent_name: $agent_name,
            entities_count: $entities_count,
            edges_count: $edges_count
        })
        RETURN e
        """

        return self.execute_write(
            query,
            {
                "id": episode.id,
                "name": episode.name,
                "body": episode.body[:10000] if episode.body else "",
                "body_type": episode.body_type,
                "source_type": episode.source_type.value
                if isinstance(episode.source_type, EpisodeSourceType)
                else episode.source_type,
                "source_description": episode.source_description,
                "reference_time": episode.reference_time.isoformat(),
                "transaction_time": episode.transaction_time.isoformat(),
                "user_id": episode.user_id,
                "thread_id": episode.thread_id,
                "agent_name": episode.agent_name,
                "entities_count": len(episode.entities_extracted),
                "edges_count": len(episode.edges_created),
            },
        )

    def link_episode_chain(
        self,
        previous_episode_id: str,
        next_episode_id: str,
    ) -> dict:
        """
        Create FOLLOWED_BY relationship between episodes.

        Enables conversation threading and context retrieval.
        """
        query = """
        MATCH (prev:Episode {id: $prev_id})
        MATCH (next:Episode {id: $next_id})
        CREATE (prev)-[r:FOLLOWED_BY {
            created_at: datetime()
        }]->(next)
        RETURN prev.id as previous, next.id as next
        """

        return self.execute_write(
            query,
            {"prev_id": previous_episode_id, "next_id": next_episode_id},
        )

    def get_episode_chain(
        self,
        thread_id: str,
        limit: int = 50,
    ) -> list[dict]:
        """
        Get the episode chain for a conversation thread.

        Returns episodes in chronological order.
        """
        query = """
        MATCH (e:Episode {thread_id: $thread_id})
        OPTIONAL MATCH path = (first:Episode)-[:FOLLOWED_BY*]->(e)
        WHERE first.thread_id = $thread_id
        WITH e, length(path) as depth
        ORDER BY e.reference_time
        LIMIT $limit
        RETURN e.id as id,
               e.name as name,
               e.body as body,
               e.source_type as source_type,
               e.reference_time as reference_time,
               depth
        """

        return self.execute(query, {"thread_id": thread_id, "limit": limit})

    def get_episode_context(
        self,
        episode_id: str,
        context_window: int = 5,
    ) -> dict:
        """
        Get context around an episode.

        Returns preceding and following episodes.
        """
        query = """
        MATCH (e:Episode {id: $episode_id})
        OPTIONAL MATCH (prev:Episode)-[:FOLLOWED_BY*1..$window]->(e)
        OPTIONAL MATCH (e)-[:FOLLOWED_BY*1..$window]->(next:Episode)
        RETURN e as current,
               collect(DISTINCT prev) as previous,
               collect(DISTINCT next) as following
        """

        results = self.execute(
            query.replace("$window", str(context_window)),
            {"episode_id": episode_id},
        )

        if results:
            return {
                "current": results[0].get("current"),
                "previous": results[0].get("previous", []),
                "following": results[0].get("following", []),
            }
        return {}

    def link_edge_to_episode(self, edge_id: str, episode_id: str) -> dict:
        """Link a temporal edge to its source episode."""
        query = """
        MATCH ()-[r:TEMPORAL_EDGE {edge_id: $edge_id}]->()
        MATCH (e:Episode {id: $episode_id})
        SET r.episode_id = $episode_id
        CREATE (e)-[:PRODUCED]->(r)
        RETURN e.id as episode, r.edge_id as edge
        """

        return self.execute_write(
            query,
            {"edge_id": edge_id, "episode_id": episode_id},
        )

    # =========================================================================
    # Curriculum Change Tracking
    # =========================================================================

    def record_curriculum_change(self, change: CurriculumChange) -> dict:
        """
        Record a curriculum change event.

        Creates a change node linked to the affected entity.
        """
        query = """
        CREATE (c:CurriculumChange {
            id: randomUUID(),
            change_type: $change_type,
            entity_type: $entity_type,
            entity_id: $entity_id,
            entity_code: $entity_code,
            old_value: $old_value,
            new_value: $new_value,
            effective_date: datetime($effective_date),
            detected_date: datetime($detected_date),
            subject_code: $subject_code,
            education_level: $education_level,
            source_document_id: $source_document_id,
            episode_id: $episode_id
        })
        RETURN c.id as change_id
        """

        return self.execute_write(
            query,
            {
                "change_type": change.change_type,
                "entity_type": change.entity_type,
                "entity_id": change.entity_id,
                "entity_code": change.entity_code,
                "old_value": str(change.old_value) if change.old_value else None,
                "new_value": str(change.new_value) if change.new_value else None,
                "effective_date": change.effective_date.isoformat(),
                "detected_date": change.detected_date.isoformat(),
                "subject_code": change.subject_code,
                "education_level": change.education_level,
                "source_document_id": change.source_document_id,
                "episode_id": change.episode_id,
            },
        )

    def get_curriculum_changes(
        self,
        subject_code: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        change_type: str | None = None,
    ) -> list[dict]:
        """
        Query curriculum changes with optional filters.
        """
        conditions = []

        if subject_code:
            conditions.append(f"c.subject_code = '{subject_code}'")
        if from_date:
            conditions.append(f"c.effective_date >= datetime('{from_date.isoformat()}')")
        if to_date:
            conditions.append(f"c.effective_date <= datetime('{to_date.isoformat()}')")
        if change_type:
            conditions.append(f"c.change_type = '{change_type}'")

        where_clause = " AND ".join(conditions) if conditions else "TRUE"

        query = f"""
        MATCH (c:CurriculumChange)
        WHERE {where_clause}
        RETURN c.id as id,
               c.change_type as change_type,
               c.entity_type as entity_type,
               c.entity_code as entity_code,
               c.effective_date as effective_date,
               c.subject_code as subject_code
        ORDER BY c.effective_date DESC
        """

        return self.execute(query)


# ============================================================================
# High-Level Temporal Graph Interface
# ============================================================================


class TemporalCurriculumGraph:
    """
    High-level interface for temporal curriculum operations.

    Provides semantic methods for common temporal operations.
    """

    def __init__(self):
        self.client = TemporalGraphClient()

    def close(self) -> None:
        """Close the client."""
        self.client.close()

    def setup(self) -> None:
        """Setup temporal schema."""
        self.client.setup_temporal_schema()

    def create_episode_from_conversation(
        self,
        thread_id: str,
        content: str,
        user_id: str | None = None,
        agent_name: str | None = None,
    ) -> Episode:
        """Create an episode from a conversation turn."""
        episode = Episode(
            name=f"Conversation {thread_id}",
            body=content,
            source_type=EpisodeSourceType.CONVERSATION,
            source_description="User conversation",
            thread_id=thread_id,
            user_id=user_id,
            agent_name=agent_name,
        )

        self.client.create_episode(episode)
        return episode

    def create_episode_from_document(
        self,
        document_id: str,
        content: str,
        document_type: str,
    ) -> Episode:
        """Create an episode from document processing."""
        episode = Episode(
            name=f"Document {document_id}",
            body=content,
            body_type="structured",
            source_type=EpisodeSourceType.DOCUMENT,
            source_description=f"Ingestion of {document_type}",
        )

        self.client.create_episode(episode)
        return episode

    def add_temporal_relationship(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        fact: str,
        episode_id: str | None = None,
        valid_from: datetime | None = None,
        confidence: float = 1.0,
    ) -> TemporalEdge:
        """Add a temporal relationship between entities."""
        edge = TemporalEdge(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            fact=fact,
            valid_at=valid_from or datetime.utcnow(),
            episode_id=episode_id,
            confidence=confidence,
        )

        self.client.create_temporal_edge(edge)

        if episode_id:
            self.client.link_edge_to_episode(edge.id, episode_id)

        return edge

    def get_curriculum_snapshot(
        self,
        subject: str,
        as_of: datetime,
    ) -> list[dict]:
        """Get curriculum state at a point in time."""
        return self.client.get_curriculum_at_time(subject, as_of)

    def get_curriculum_diff(
        self,
        subject: str,
        from_time: datetime,
        to_time: datetime,
    ) -> dict:
        """Get curriculum changes between two times."""
        return self.client.compare_curriculum_versions(subject, from_time, to_time)

    def get_conversation_context(
        self,
        thread_id: str,
        limit: int = 10,
    ) -> list[dict]:
        """Get conversation history for a thread."""
        return self.client.get_episode_chain(thread_id, limit)


# Singleton access
_temporal_graph: TemporalCurriculumGraph | None = None


def get_temporal_graph() -> TemporalCurriculumGraph:
    """Get the temporal curriculum graph singleton."""
    global _temporal_graph
    if _temporal_graph is None:
        _temporal_graph = TemporalCurriculumGraph()
    return _temporal_graph
