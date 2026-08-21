"""
Bi-Temporal Edge Model for Curriculum Knowledge Graph.

Implements Graphiti-style temporal tracking:
- Reality time: When fact was true in reality (valid_at/invalid_at)
- System time: When system recorded the fact (created_at/expired_at)
- Edge invalidation: Soft-delete with history preservation
- Episodes: Atomic memory units for traceability

Based on research from taighde_scoil:
- Graphiti bi-temporal model
- Edge invalidation preserves history
- Episodes as memory units with temporal chains
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
import uuid


class EdgeStatus(Enum):
    """Status of a temporal edge."""

    CURRENT = "current"  # valid_at <= now < invalid_at AND expired_at IS NULL
    SUPERSEDED = "superseded"  # Replaced by newer edge version
    INVALIDATED = "invalidated"  # Explicitly marked invalid in reality
    EXPIRED = "expired"  # System expired (e.g., during reprocessing)


class EpisodeSourceType(Enum):
    """Types of episode sources."""

    CONVERSATION = "conversation"  # User conversation thread
    DOCUMENT = "document"  # Document ingestion
    EXTRACTION = "extraction"  # BAML extraction
    USER_INPUT = "user_input"  # Direct user input
    AGENT = "agent"  # Agent-generated
    CURRICULUM_UPDATE = "curriculum_update"  # Curriculum change event


@dataclass
class TemporalEdge:
    """
    Bi-temporal edge with both reality time and system time.

    Reality Time (valid_at/invalid_at):
        When the relationship was true in the real world.
        Example: "Learning Outcome X was part of Strand Y from 2020-2024"

    System Time (created_at/expired_at):
        When the system knew about this relationship.
        Example: "We recorded this on 2024-01-15, updated on 2024-06-01"
    """

    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str = ""
    target_id: str = ""
    relation_type: str = ""

    # Human-readable fact description
    fact: str = ""  # e.g., "Junior Cycle Irish requires Learning Outcome 1.1"

    # Reality time (bi-temporal dimension 1)
    valid_at: datetime = field(default_factory=datetime.utcnow)
    invalid_at: datetime | None = None  # None means currently valid

    # System time (bi-temporal dimension 2)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expired_at: datetime | None = None  # None means current version

    # Provenance
    episode_id: str | None = None
    confidence: float = 1.0
    source_document_id: str | None = None
    extraction_method: str | None = None

    # Additional properties
    properties: dict[str, Any] = field(default_factory=dict)

    @property
    def is_current(self) -> bool:
        """Check if edge is currently valid in both dimensions."""
        now = datetime.utcnow()
        reality_valid = self.valid_at <= now and (self.invalid_at is None or now < self.invalid_at)
        system_valid = self.expired_at is None
        return reality_valid and system_valid

    @property
    def status(self) -> EdgeStatus:
        """Get current status of the edge."""
        if self.expired_at is not None:
            return EdgeStatus.EXPIRED
        if self.invalid_at is not None:
            return EdgeStatus.INVALIDATED
        return EdgeStatus.CURRENT

    def to_cypher_properties(self) -> dict[str, Any]:
        """Convert to Cypher-compatible property dict."""
        return {
            "edge_id": self.id,
            "fact": self.fact,
            "valid_at": self.valid_at.isoformat(),
            "invalid_at": self.invalid_at.isoformat() if self.invalid_at else None,
            "created_at": self.created_at.isoformat(),
            "expired_at": self.expired_at.isoformat() if self.expired_at else None,
            "episode_id": self.episode_id,
            "confidence": self.confidence,
            "source_document_id": self.source_document_id,
            "extraction_method": self.extraction_method,
            **self.properties,
        }

    def invalidate(
        self,
        invalid_at: datetime | None = None,
        reason: str = "superseded",
    ) -> "TemporalEdge":
        """
        Create invalidated copy of this edge.

        Does not modify the original edge - returns new instance.
        """
        return TemporalEdge(
            id=self.id,
            source_id=self.source_id,
            target_id=self.target_id,
            relation_type=self.relation_type,
            fact=self.fact,
            valid_at=self.valid_at,
            invalid_at=invalid_at or datetime.utcnow(),
            created_at=self.created_at,
            expired_at=self.expired_at,
            episode_id=self.episode_id,
            confidence=self.confidence,
            source_document_id=self.source_document_id,
            extraction_method=self.extraction_method,
            properties={**self.properties, "invalidation_reason": reason},
        )


@dataclass
class Episode:
    """
    Atomic memory unit - a discrete event with temporal context.

    Every piece of information enters through an Episode,
    enabling full traceability and temporal queries.

    Episodes form chains via FOLLOWED_BY relationships,
    enabling conversation threading and context retrieval.
    """

    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""

    # Content
    body: str = ""
    body_type: str = "text"  # text, json, structured

    # Source tracking
    source_type: EpisodeSourceType = EpisodeSourceType.DOCUMENT
    source_description: str = ""

    # Temporal - bi-temporal for episodes too
    reference_time: datetime = field(default_factory=datetime.utcnow)  # Reality time
    transaction_time: datetime = field(default_factory=datetime.utcnow)  # System time

    # Context
    user_id: str | None = None
    thread_id: str | None = None
    agent_name: str | None = None

    # Extracted data
    entities_extracted: list[dict[str, Any]] = field(default_factory=list)
    edges_created: list[str] = field(default_factory=list)

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_cypher_properties(self) -> dict[str, Any]:
        """Convert to Cypher-compatible property dict."""
        return {
            "id": self.id,
            "name": self.name,
            "body": self.body[:10000] if self.body else "",  # Truncate for graph storage
            "body_type": self.body_type,
            "source_type": self.source_type.value
            if isinstance(self.source_type, EpisodeSourceType)
            else self.source_type,
            "source_description": self.source_description,
            "reference_time": self.reference_time.isoformat(),
            "transaction_time": self.transaction_time.isoformat(),
            "user_id": self.user_id,
            "thread_id": self.thread_id,
            "agent_name": self.agent_name,
            "entities_count": len(self.entities_extracted),
            "edges_count": len(self.edges_created),
        }


@dataclass
class TemporalQuery:
    """
    Parameters for temporal queries.

    Supports:
    - Point-in-time queries (as_of)
    - Range queries (from_time, to_time)
    - System time queries (transaction_time)
    """

    # Reality time constraints
    as_of: datetime | None = None  # Point-in-time query
    from_time: datetime | None = None  # Range start
    to_time: datetime | None = None  # Range end

    # System time constraints (for audit/debug)
    transaction_time: datetime | None = None

    # Filter options
    include_invalidated: bool = False
    include_expired: bool = False

    def to_cypher_conditions(self, edge_alias: str = "r") -> str:
        """Generate Cypher WHERE conditions for temporal filtering."""
        conditions = []

        if self.as_of:
            pit = self.as_of.isoformat()
            conditions.append(f"{edge_alias}.valid_at <= datetime('{pit}')")
            conditions.append(
                f"({edge_alias}.invalid_at IS NULL OR {edge_alias}.invalid_at > datetime('{pit}'))"
            )

        if self.from_time:
            from_ts = self.from_time.isoformat()
            conditions.append(f"{edge_alias}.valid_at >= datetime('{from_ts}')")

        if self.to_time:
            to_ts = self.to_time.isoformat()
            conditions.append(f"{edge_alias}.valid_at <= datetime('{to_ts}')")

        if self.transaction_time:
            tx_ts = self.transaction_time.isoformat()
            conditions.append(f"{edge_alias}.created_at <= datetime('{tx_ts}')")
            conditions.append(
                f"({edge_alias}.expired_at IS NULL OR {edge_alias}.expired_at > datetime('{tx_ts}'))"
            )

        if not self.include_invalidated:
            conditions.append(f"{edge_alias}.invalid_at IS NULL")

        if not self.include_expired:
            conditions.append(f"{edge_alias}.expired_at IS NULL")

        return " AND ".join(conditions) if conditions else "TRUE"


@dataclass
class CurriculumChange:
    """
    Represents a change in the curriculum over time.

    Used for tracking and visualizing curriculum evolution.
    """

    change_type: str  # added, removed, modified
    entity_type: str  # learning_outcome, strand, strand_unit
    entity_id: str
    entity_code: str | None = None

    # What changed
    old_value: dict[str, Any] | None = None
    new_value: dict[str, Any] | None = None

    # When
    effective_date: datetime = field(default_factory=datetime.utcnow)
    detected_date: datetime = field(default_factory=datetime.utcnow)

    # Context
    subject_code: str | None = None
    education_level: str | None = None
    source_document_id: str | None = None
    episode_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage/serialization."""
        return {
            "change_type": self.change_type,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "entity_code": self.entity_code,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "effective_date": self.effective_date.isoformat(),
            "detected_date": self.detected_date.isoformat(),
            "subject_code": self.subject_code,
            "education_level": self.education_level,
            "source_document_id": self.source_document_id,
            "episode_id": self.episode_id,
        }


# Type aliases for clarity
EdgeId = str
EpisodeId = str
NodeId = str
