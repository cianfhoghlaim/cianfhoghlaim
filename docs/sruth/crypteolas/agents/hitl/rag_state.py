"""
RAG State for Human-in-the-Loop workflow.

Shared state between Python backend and TanStack/CopilotKit frontend.
Based on pattern from human-in-the-loop-rag-agent reference.

Features:
- Chunk approval/rejection workflow
- Search configuration management
- AG-UI state synchronization
- Citation tracking
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ChunkApprovalStatus(str, Enum):
    """Status for chunk approval workflow."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class RAGChunk(BaseModel):
    """A chunk from the knowledge base."""

    id: str = Field(description="Unique chunk identifier")
    text: str = Field(description="Chunk text content")
    source: str = Field(description="Source URL or file path")
    source_type: str = Field(description="Source type: protocol_docs, user_url, github, local")
    protocol: str | None = Field(default=None, description="Protocol name if applicable")
    title: str | None = Field(default=None, description="Document title")
    score: float = Field(description="Similarity score (0-1)")
    status: ChunkApprovalStatus = Field(
        default=ChunkApprovalStatus.PENDING,
        description="Approval status"
    )
    feedback: str | None = Field(default=None, description="User feedback on rejection")

    # Code-specific fields
    language: str | None = Field(default=None, description="Programming language")
    chunk_type: str | None = Field(default=None, description="function, class, method, etc.")
    start_line: int | None = Field(default=None)
    end_line: int | None = Field(default=None)


class SearchConfig(BaseModel):
    """Configuration for RAG search."""

    # Similarity settings
    similarity_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score for results"
    )
    max_chunks: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum chunks to retrieve"
    )

    # Filters
    source_filter: list[str] = Field(
        default_factory=list,
        description="Source types to include (empty = all)"
    )
    protocol_filter: list[str] = Field(
        default_factory=list,
        description="Protocols to include (empty = all)"
    )
    language_filter: list[str] = Field(
        default_factory=list,
        description="Programming languages to include (empty = all)"
    )

    # Search mode
    search_mode: str = Field(
        default="hybrid",
        description="Search mode: vector, fts, hybrid"
    )
    include_code: bool = Field(
        default=True,
        description="Include code embeddings in search"
    )


class Citation(BaseModel):
    """A citation for generated content."""

    chunk_id: str = Field(description="Referenced chunk ID")
    source: str = Field(description="Source URL or path")
    title: str | None = Field(default=None)
    text_preview: str = Field(description="Preview of cited text")
    score: float = Field(description="Relevance score")


class RAGState(BaseModel):
    """
    Shared state between Python backend and TanStack/CopilotKit frontend.

    This state is synchronized via AG-UI protocol using StateSnapshotEvent.
    The frontend can modify approved_chunks and search_config through
    the CopilotKit useAgent hook.
    """

    # Query state
    query: str = Field(default="", description="Current search query")
    query_timestamp: str | None = Field(default=None, description="When query was made")

    # Retrieved chunks
    chunks: list[RAGChunk] = Field(
        default_factory=list,
        description="Retrieved chunks from knowledge base"
    )

    # Approval workflow
    approved_chunks: list[str] = Field(
        default_factory=list,
        description="IDs of approved chunks"
    )
    rejected_chunks: list[str] = Field(
        default_factory=list,
        description="IDs of rejected chunks"
    )
    awaiting_approval: bool = Field(
        default=False,
        description="Whether agent is waiting for chunk approval"
    )

    # Search configuration (user-controllable)
    search_config: SearchConfig = Field(
        default_factory=SearchConfig,
        description="Search parameters"
    )

    # Generated response
    response: str | None = Field(default=None, description="Generated response text")
    citations: list[Citation] = Field(
        default_factory=list,
        description="Citations for generated response"
    )

    # Metadata
    total_chunks_found: int = Field(default=0, description="Total chunks before filtering")
    search_latency_ms: float | None = Field(default=None, description="Search time in ms")

    def get_pending_chunks(self) -> list[RAGChunk]:
        """Get chunks awaiting approval."""
        return [
            chunk for chunk in self.chunks
            if chunk.id not in self.approved_chunks
            and chunk.id not in self.rejected_chunks
        ]

    def get_approved_chunk_texts(self) -> list[str]:
        """Get text content of approved chunks."""
        return [
            chunk.text for chunk in self.chunks
            if chunk.id in self.approved_chunks
        ]

    def approve_chunk(self, chunk_id: str) -> None:
        """Approve a chunk."""
        if chunk_id not in self.approved_chunks:
            self.approved_chunks.append(chunk_id)
        if chunk_id in self.rejected_chunks:
            self.rejected_chunks.remove(chunk_id)

        # Update chunk status
        for chunk in self.chunks:
            if chunk.id == chunk_id:
                chunk.status = ChunkApprovalStatus.APPROVED
                break

    def reject_chunk(self, chunk_id: str, feedback: str | None = None) -> None:
        """Reject a chunk with optional feedback."""
        if chunk_id not in self.rejected_chunks:
            self.rejected_chunks.append(chunk_id)
        if chunk_id in self.approved_chunks:
            self.approved_chunks.remove(chunk_id)

        # Update chunk status
        for chunk in self.chunks:
            if chunk.id == chunk_id:
                chunk.status = ChunkApprovalStatus.REJECTED
                chunk.feedback = feedback
                break

    def approve_all(self) -> None:
        """Approve all pending chunks."""
        for chunk in self.chunks:
            if chunk.id not in self.approved_chunks and chunk.id not in self.rejected_chunks:
                self.approve_chunk(chunk.id)

    def clear_search(self) -> None:
        """Clear search state for new query."""
        self.query = ""
        self.query_timestamp = None
        self.chunks = []
        self.approved_chunks = []
        self.rejected_chunks = []
        self.awaiting_approval = False
        self.response = None
        self.citations = []
        self.total_chunks_found = 0
        self.search_latency_ms = None

    def update_from_search(
        self,
        query: str,
        chunks: list[RAGChunk],
        latency_ms: float,
    ) -> None:
        """Update state after a search."""
        self.query = query
        self.query_timestamp = datetime.utcnow().isoformat()
        self.chunks = chunks
        self.total_chunks_found = len(chunks)
        self.search_latency_ms = latency_ms
        self.awaiting_approval = len(chunks) > 0
        self.approved_chunks = []
        self.rejected_chunks = []
        self.response = None
        self.citations = []

    def to_frontend_state(self) -> dict[str, Any]:
        """Convert to frontend-compatible state dict."""
        return {
            "query": self.query,
            "queryTimestamp": self.query_timestamp,
            "chunks": [chunk.model_dump() for chunk in self.chunks],
            "approvedChunks": self.approved_chunks,
            "rejectedChunks": self.rejected_chunks,
            "awaitingApproval": self.awaiting_approval,
            "searchConfig": self.search_config.model_dump(),
            "response": self.response,
            "citations": [c.model_dump() for c in self.citations],
            "totalChunksFound": self.total_chunks_found,
            "searchLatencyMs": self.search_latency_ms,
        }

    @classmethod
    def from_frontend_state(cls, state: dict[str, Any]) -> "RAGState":
        """Create from frontend state dict."""
        return cls(
            query=state.get("query", ""),
            query_timestamp=state.get("queryTimestamp"),
            chunks=[RAGChunk(**c) for c in state.get("chunks", [])],
            approved_chunks=state.get("approvedChunks", []),
            rejected_chunks=state.get("rejectedChunks", []),
            awaiting_approval=state.get("awaitingApproval", False),
            search_config=SearchConfig(**state.get("searchConfig", {})),
            response=state.get("response"),
            citations=[Citation(**c) for c in state.get("citations", [])],
            total_chunks_found=state.get("totalChunksFound", 0),
            search_latency_ms=state.get("searchLatencyMs"),
        )
