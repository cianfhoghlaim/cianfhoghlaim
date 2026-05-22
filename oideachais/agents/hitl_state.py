"""
Human-in-the-Loop RAG State Models.

Defines shared state between Python agents and frontend for
bidirectional state synchronization via AG-UI protocol.

Based on /taighde/teanga/human-in-the-loop-rag-agent/agent/state.py

Use cases:
1. Content Curation: Approve AI-extracted learning outcomes
2. Exam Validation: Validate SEC exam answers with marking schemes
3. General HITL: Flexible approval for any retrieval scenario

Usage:
    from agents.hitl_state import OideachasHITLState, RetrievedChunk

    state = OideachasHITLState()
    state.retrieved_chunks = [chunk1, chunk2]
    state.awaiting_approval = True
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ApprovalContext(str, Enum):
    """Context types for HITL approval workflow."""

    CONTENT_CURATION = "content_curation"
    EXAM_VALIDATION = "exam_validation"
    TRANSLATION_REVIEW = "translation_review"
    GENERAL = "general"


class RetrievedChunk(BaseModel):
    """A chunk retrieved from the curriculum knowledge base.

    Represents a document chunk with similarity scoring
    and approval status for human-in-the-loop validation.
    """

    chunk_id: str = Field(description="Unique identifier for the chunk")
    document_id: str = Field(description="ID of the source document")
    content: str = Field(description="The actual text content of the chunk")
    similarity: float = Field(description="Similarity score to the query (0-1)")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )
    document_title: str = Field(description="Title of the source document")
    document_source: str = Field(description="Source/path of the document")
    chunk_index: int = Field(
        default=1,
        description="1-based index of this chunk within its document",
    )
    approved: bool = Field(
        default=False, description="Whether this chunk has been approved by the user"
    )

    # Curriculum-specific metadata
    subject: str | None = Field(default=None, description="Subject area (e.g., Irish, Maths)")
    level: str | None = Field(default=None, description="Education level (e.g., LC, JC)")
    strand: str | None = Field(default=None, description="Curriculum strand")
    language: str = Field(default="en", description="Content language (en, ga)")


class LearningOutcome(BaseModel):
    """A learning outcome extracted from curriculum content."""

    outcome_id: str = Field(description="Unique identifier")
    text_en: str = Field(description="English text")
    text_ga: str | None = Field(default=None, description="Irish translation")
    subject: str = Field(description="Subject area")
    strand: str = Field(description="Curriculum strand")
    strand_unit: str | None = Field(default=None, description="Strand unit")
    level: str = Field(description="Education level")
    approved: bool = Field(default=False, description="Human-approved status")
    source_chunk_id: str | None = Field(
        default=None, description="Source chunk ID for provenance"
    )


class ExamAnswer(BaseModel):
    """An exam answer with marking scheme alignment."""

    question_id: str = Field(description="Question identifier")
    question_text: str = Field(description="The exam question")
    answer_text: str = Field(description="AI-generated or retrieved answer")
    marking_scheme: str | None = Field(
        default=None, description="Official marking scheme if available"
    )
    alignment_score: float = Field(
        default=0.0, description="Alignment with marking scheme (0-1)"
    )
    source_chunks: list[str] = Field(
        default_factory=list, description="Source chunk IDs used"
    )
    approved: bool = Field(default=False, description="Teacher-approved status")
    feedback: str | None = Field(default=None, description="Teacher feedback")


class SearchQuery(BaseModel):
    """Model for a search query with metadata."""

    query: str = Field(description="The search query text")
    timestamp: str = Field(description="ISO timestamp when the query was made")
    match_count: int = Field(default=10, description="Number of results requested")
    search_type: str = Field(
        default="semantic", description="Type of search (semantic, hybrid, graph)"
    )
    filters: dict[str, Any] = Field(
        default_factory=dict, description="Applied filters (subject, level, etc.)"
    )


class SearchConfig(BaseModel):
    """User-configurable search parameters.

    Enables bidirectional state sync - users can adjust
    these settings in the frontend, and the agent respects them.
    """

    similarity_threshold: float = Field(
        default=0.5, description="Minimum similarity score for results (0-1)"
    )
    max_results: int = Field(default=10, description="Maximum number of results")
    search_type: str = Field(
        default="hybrid", description="Search type: 'semantic', 'hybrid', or 'graph'"
    )
    include_subjects: list[str] = Field(
        default_factory=list, description="Filter to specific subjects"
    )
    include_levels: list[str] = Field(
        default_factory=list, description="Filter to specific education levels"
    )
    language: str = Field(
        default="both", description="Content language filter: 'en', 'ga', or 'both'"
    )


class OideachasHITLState(BaseModel):
    """Shared state between oideachais agent and frontend via AG-UI.

    This model demonstrates all useAgent capabilities:
    - agent.state: All fields are readable by the frontend
    - agent.setState: approved_chunk_ids, search_config updated by frontend
    - STATE_SNAPSHOT: Full state sent after retrieval
    - STATE_DELTA: Incremental updates for approvals

    CRITICAL: Field names must match exactly in TypeScript types.
    """

    # Retrieved data (agent -> frontend)
    retrieved_chunks: list[RetrievedChunk] = Field(
        default_factory=list, description="List of chunks retrieved from knowledge base"
    )
    current_query: SearchQuery | None = Field(
        default=None, description="The current search query being processed"
    )
    search_history: list[SearchQuery] = Field(
        default_factory=list, description="History of search queries"
    )

    # Curriculum-specific retrievals
    learning_outcomes: list[LearningOutcome] = Field(
        default_factory=list, description="Extracted learning outcomes for curation"
    )
    exam_answers: list[ExamAnswer] = Field(
        default_factory=list, description="Exam answers for validation"
    )

    # Knowledge base info
    total_chunks_in_kb: int = Field(
        default=0, description="Total number of chunks in the knowledge base"
    )
    knowledge_base_status: str = Field(
        default="ready", description="Status: ready, indexing, error"
    )

    # HITL approval workflow (frontend <-> agent)
    approved_chunk_ids: list[str] = Field(
        default_factory=list, description="IDs of chunks approved by the user"
    )
    approved_outcome_ids: list[str] = Field(
        default_factory=list, description="IDs of learning outcomes approved"
    )
    approved_answer_ids: list[str] = Field(
        default_factory=list, description="IDs of exam answers approved"
    )
    awaiting_approval: bool = Field(
        default=False, description="Whether the agent is waiting for user approval"
    )
    approval_context: ApprovalContext = Field(
        default=ApprovalContext.GENERAL,
        description="Context for current approval workflow",
    )

    # User-configurable search (frontend -> agent)
    search_config: SearchConfig = Field(
        default_factory=SearchConfig, description="User-adjustable search parameters"
    )

    # UI state hints
    is_searching: bool = Field(
        default=False, description="Whether a search is currently in progress"
    )
    is_synthesizing: bool = Field(
        default=False, description="Whether the agent is synthesizing an answer"
    )
    is_extracting: bool = Field(
        default=False, description="Whether the agent is extracting learning outcomes"
    )
    error_message: str | None = Field(
        default=None, description="Error message if something went wrong"
    )

    # Session metadata
    session_id: str | None = Field(
        default=None, description="Current session identifier"
    )
    user_role: str = Field(
        default="teacher", description="User role: teacher, student, admin"
    )


class HITLResponse(BaseModel):
    """Response from HITL approval action."""

    approved: bool = Field(description="Whether the content was approved")
    approved_ids: list[str] = Field(
        default_factory=list, description="IDs of approved items"
    )
    rejected_ids: list[str] = Field(
        default_factory=list, description="IDs of rejected items"
    )
    feedback: str | None = Field(
        default=None, description="Optional user feedback"
    )
    context: ApprovalContext = Field(
        default=ApprovalContext.GENERAL, description="Approval context"
    )


# =============================================================================
# State Factory Functions
# =============================================================================

def create_content_curation_state() -> OideachasHITLState:
    """Create state configured for content curation workflow."""
    return OideachasHITLState(
        approval_context=ApprovalContext.CONTENT_CURATION,
        search_config=SearchConfig(
            search_type="hybrid",
            max_results=20,
        ),
    )


def create_exam_validation_state() -> OideachasHITLState:
    """Create state configured for exam validation workflow."""
    return OideachasHITLState(
        approval_context=ApprovalContext.EXAM_VALIDATION,
        search_config=SearchConfig(
            search_type="semantic",
            similarity_threshold=0.7,
            max_results=5,
        ),
    )


def create_translation_review_state() -> OideachasHITLState:
    """Create state configured for translation review workflow."""
    return OideachasHITLState(
        approval_context=ApprovalContext.TRANSLATION_REVIEW,
        search_config=SearchConfig(
            language="both",
            max_results=10,
        ),
    )
