"""
Human-in-the-Loop RAG for Crypteolas.

Provides chunk approval workflow with CopilotKit/AG-UI integration.
"""

from .rag_state import (
    RAGState,
    RAGChunk,
    ChunkApprovalStatus,
    SearchConfig,
)
from .rag_agent import (
    rag_agent,
    StateDeps,
)

__all__ = [
    "RAGState",
    "RAGChunk",
    "ChunkApprovalStatus",
    "SearchConfig",
    "rag_agent",
    "StateDeps",
]
