"""
Human-in-the-Loop RAG Agent for Crypteolas.

PydanticAI agent with state management for chunk approval workflow.
Integrates with CopilotKit/AG-UI for frontend synchronization.

Based on pattern from human-in-the-loop-rag-agent reference.
"""

import logging
import time
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ToolReturn

from .rag_state import RAGState, RAGChunk, ChunkApprovalStatus, SearchConfig, Citation

logger = logging.getLogger(__name__)

# Type variable for state
T = TypeVar("T")


@dataclass
class StateDeps(Generic[T]):
    """Dependencies with shared state."""
    state: T


# AG-UI Event Types
class EventType:
    """AG-UI event types for state synchronization."""
    STATE_SNAPSHOT = "state_snapshot"
    TEXT_MESSAGE = "text_message"
    TOOL_CALL = "tool_call"


@dataclass
class StateSnapshotEvent:
    """Event for AG-UI state synchronization."""
    type: str
    snapshot: dict[str, Any]


# Create the RAG agent
rag_agent = Agent(
    "openai:gpt-4o",
    deps_type=StateDeps[RAGState],
    system_prompt="""You are a helpful crypto/DeFi research assistant with access to a knowledge base of protocol documentation, code, and research.

When the user asks a question:
1. Use the search_knowledge_base tool to find relevant information
2. Wait for the user to approve or reject the retrieved chunks
3. Once chunks are approved, use ONLY the approved information to answer
4. Always cite your sources with the source URL or file path

Important rules:
- Never make up information - only use approved chunks
- If no chunks are approved, ask the user to approve some or search again
- When answering, include citations like [1], [2] etc. and list sources at the end
- Be concise but thorough
""",
)


@rag_agent.tool
async def search_knowledge_base(
    ctx: RunContext[StateDeps[RAGState]],
    query: str,
) -> ToolReturn:
    """
    Search the knowledge base for relevant chunks.

    This triggers the HITL approval workflow - the user must
    approve chunks before they can be used in the response.

    Args:
        query: The search query

    Returns:
        Status message and state snapshot for frontend
    """
    state = ctx.deps.state
    config = state.search_config

    start_time = time.time()

    try:
        # Perform unified search
        chunks = await _unified_search(
            query=query,
            source_types=config.source_filter or None,
            protocol=config.protocol_filter[0] if config.protocol_filter else None,
            limit=config.max_chunks,
            similarity_threshold=config.similarity_threshold,
            include_code=config.include_code,
        )

        latency_ms = (time.time() - start_time) * 1000

        # Update state
        state.update_from_search(
            query=query,
            chunks=chunks,
            latency_ms=latency_ms,
        )

        # Return with state snapshot for frontend
        return ToolReturn(
            return_value=f"Found {len(chunks)} relevant chunks. Please review and approve the ones you want to use.",
            metadata=[
                StateSnapshotEvent(
                    type=EventType.STATE_SNAPSHOT,
                    snapshot=state.to_frontend_state(),
                ),
            ],
        )

    except Exception as e:
        logger.error(f"Search failed: {e}")
        return ToolReturn(
            return_value=f"Search failed: {str(e)}",
            metadata=[],
        )


@rag_agent.tool
async def generate_response(
    ctx: RunContext[StateDeps[RAGState]],
) -> ToolReturn:
    """
    Generate a response using approved chunks.

    Only call this after the user has approved chunks.
    Uses only the approved chunk content with citations.

    Returns:
        Generated response with citations
    """
    state = ctx.deps.state

    if not state.approved_chunks:
        return ToolReturn(
            return_value="No chunks have been approved yet. Please approve some chunks first.",
            metadata=[],
        )

    # Get approved chunk texts
    approved_texts = state.get_approved_chunk_texts()

    if not approved_texts:
        return ToolReturn(
            return_value="Could not find approved chunk content.",
            metadata=[],
        )

    # Build context from approved chunks
    context_parts = []
    citations = []

    for i, chunk in enumerate(state.chunks):
        if chunk.id in state.approved_chunks:
            context_parts.append(f"[{i+1}] {chunk.text}")
            citations.append(Citation(
                chunk_id=chunk.id,
                source=chunk.source,
                title=chunk.title,
                text_preview=chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text,
                score=chunk.score,
            ))

    context = "\n\n".join(context_parts)

    # Generate response (this will be handled by the LLM)
    state.citations = citations
    state.awaiting_approval = False

    return ToolReturn(
        return_value=f"Context from approved chunks:\n\n{context}\n\nPlease synthesize a response based on this information, citing sources as [1], [2], etc.",
        metadata=[
            StateSnapshotEvent(
                type=EventType.STATE_SNAPSHOT,
                snapshot=state.to_frontend_state(),
            ),
        ],
    )


@rag_agent.tool
async def update_search_config(
    ctx: RunContext[StateDeps[RAGState]],
    similarity_threshold: float | None = None,
    max_chunks: int | None = None,
    source_filter: list[str] | None = None,
    protocol_filter: list[str] | None = None,
    include_code: bool | None = None,
) -> str:
    """
    Update search configuration.

    Args:
        similarity_threshold: Minimum similarity score (0-1)
        max_chunks: Maximum chunks to retrieve
        source_filter: Source types to include
        protocol_filter: Protocols to include
        include_code: Whether to include code search

    Returns:
        Confirmation message
    """
    state = ctx.deps.state
    config = state.search_config

    if similarity_threshold is not None:
        config.similarity_threshold = max(0.0, min(1.0, similarity_threshold))

    if max_chunks is not None:
        config.max_chunks = max(1, min(50, max_chunks))

    if source_filter is not None:
        config.source_filter = source_filter

    if protocol_filter is not None:
        config.protocol_filter = protocol_filter

    if include_code is not None:
        config.include_code = include_code

    return f"Search config updated: threshold={config.similarity_threshold}, max_chunks={config.max_chunks}"


@rag_agent.tool
async def clear_search(
    ctx: RunContext[StateDeps[RAGState]],
) -> ToolReturn:
    """
    Clear the current search and start fresh.

    Returns:
        Confirmation with state snapshot
    """
    state = ctx.deps.state
    state.clear_search()

    return ToolReturn(
        return_value="Search cleared. Ready for a new query.",
        metadata=[
            StateSnapshotEvent(
                type=EventType.STATE_SNAPSHOT,
                snapshot=state.to_frontend_state(),
            ),
        ],
    )


# =========================================================================
# Search Implementation
# =========================================================================

async def _unified_search(
    query: str,
    source_types: list[str] | None = None,
    protocol: str | None = None,
    limit: int = 10,
    similarity_threshold: float = 0.0,
    include_code: bool = True,
) -> list[RAGChunk]:
    """
    Search across all sources and return RAGChunk objects.
    """
    chunks = []

    try:
        # Import here to avoid circular imports
        from tuatha.crypteolas.cocoindex_flows.unified_embedding import unified_search, code_search

        # Search unified embeddings
        doc_results = await unified_search(
            query=query,
            source_types=source_types,
            protocol=protocol,
            limit=limit,
            similarity_threshold=similarity_threshold,
        )

        for result in doc_results.results:
            chunks.append(RAGChunk(
                id=result["id"],
                text=result["text"],
                source=result.get("url") or result.get("file_path", "unknown"),
                source_type=result.get("source_type", "unknown"),
                protocol=result.get("protocol"),
                title=result.get("title"),
                score=result.get("score", 0.0),
                status=ChunkApprovalStatus.PENDING,
            ))

        # Search code embeddings if enabled
        if include_code:
            code_results = await code_search(
                query=query,
                limit=limit // 2,  # Half the limit for code
            )

            for result in code_results.results:
                chunks.append(RAGChunk(
                    id=result["id"],
                    text=result["text"],
                    source=result.get("filename", "unknown"),
                    source_type="local",
                    language=result.get("language"),
                    chunk_type=result.get("chunk_type"),
                    start_line=result.get("start_line"),
                    end_line=result.get("end_line"),
                    score=result.get("score", 0.0),
                    status=ChunkApprovalStatus.PENDING,
                ))

    except ImportError:
        logger.warning("CocoIndex flows not available, using fallback search")
        chunks = await _fallback_search(query, source_types, protocol, limit)

    except Exception as e:
        logger.error(f"Search error: {e}")
        chunks = []

    # Sort by score and limit
    chunks.sort(key=lambda c: c.score, reverse=True)
    return chunks[:limit]


async def _fallback_search(
    query: str,
    source_types: list[str] | None = None,
    protocol: str | None = None,
    limit: int = 10,
) -> list[RAGChunk]:
    """
    Fallback search using direct LanceDB access.
    """
    try:
        from tuatha.crypteolas.storage.lance_catalog import get_lance_catalog

        catalog = get_lance_catalog()

        # Get query embedding
        from sentence_transformers import SentenceTransformer
        embedder = SentenceTransformer("BAAI/bge-m3")
        query_vector = embedder.encode(query, normalize_embeddings=True).tolist()

        # Search across source types
        results = catalog.search_all(
            query_vector=query_vector,
            source_types=source_types,
            limit=limit,
        )

        chunks = []
        for result in results:
            chunks.append(RAGChunk(
                id=result.get("id", ""),
                text=result.get("text", ""),
                source=result.get("source_url", "unknown"),
                source_type=result.get("source_type", "unknown"),
                score=1.0 - result.get("_distance", 1.0),
                status=ChunkApprovalStatus.PENDING,
            ))

        return chunks

    except Exception as e:
        logger.error(f"Fallback search failed: {e}")
        return []


# =========================================================================
# AG-UI Protocol Helpers
# =========================================================================

def create_state_snapshot_event(state: RAGState) -> dict[str, Any]:
    """Create AG-UI state snapshot event."""
    return {
        "type": EventType.STATE_SNAPSHOT,
        "snapshot": state.to_frontend_state(),
    }


def handle_frontend_state_update(
    current_state: RAGState,
    updates: dict[str, Any],
) -> RAGState:
    """
    Handle state updates from frontend.

    The frontend can update:
    - approvedChunks / rejectedChunks (chunk approval)
    - searchConfig (search parameters)
    """
    # Update approved/rejected chunks
    if "approvedChunks" in updates:
        current_state.approved_chunks = updates["approvedChunks"]

    if "rejectedChunks" in updates:
        current_state.rejected_chunks = updates["rejectedChunks"]

    # Update search config
    if "searchConfig" in updates:
        current_state.search_config = SearchConfig(**updates["searchConfig"])

    # Update awaiting_approval based on pending chunks
    pending = current_state.get_pending_chunks()
    current_state.awaiting_approval = len(pending) > 0

    return current_state
