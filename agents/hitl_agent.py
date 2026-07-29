"""
Human-in-the-Loop RAG Agent for Oideachais.

Provides teacher/developer approval workflow for content validation:
1. Content Curation: Approve AI-extracted learning outcomes
2. Exam Validation: Validate SEC exam answers with marking schemes
3. Translation Review: Review Irish translations

Based on /taighde/teanga/human-in-the-loop-rag-agent/ patterns.

Usage:
    from agents.hitl_agent import create_oideachais_hitl_agent

    agent = create_oideachais_hitl_agent()
    app = agent.to_ag_ui()
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

# Import state models
from .hitl_state import (
    ApprovalContext,
    ExamAnswer,
    LearningOutcome,
    OideachasHITLState,
    RetrievedChunk,
    SearchQuery,
)

# Check for required dependencies
try:
    from ag_ui.core import EventType, StateSnapshotEvent
    from pydantic_ai import Agent, RunContext, ToolReturn
    from pydantic_ai.ag_ui import StateDeps
    HAS_PYDANTIC_AI = True
except ImportError:
    HAS_PYDANTIC_AI = False
    logger.warning("pydantic_ai not installed, HITL agent unavailable")


# =============================================================================
# Agent Prompts
# =============================================================================

OIDEACHAIS_SYSTEM_PROMPT = """You are an AI assistant for the Oideachais Irish Education Platform.

Your role is to help teachers and curriculum developers:
1. Search and retrieve curriculum content in English and Irish
2. Extract and curate learning outcomes
3. Validate exam answers against marking schemes
4. Review Irish translations

CRITICAL WORKFLOW RULES:
- After searching, ALWAYS wait for user approval before synthesizing answers
- Check the UI state to see which sources the user has approved
- Only use approved sources when generating responses
- Respect the search_config settings (threshold, max_results, search_type)
- Support both English and Irish language queries

Available search types:
- semantic: Vector similarity search
- hybrid: Combined vector and graph search
- graph: Knowledge graph traversal

For content curation:
- Extract learning outcomes from curriculum documents
- Wait for teacher approval before confirming
- Track provenance to source documents

For exam validation:
- Align answers with official marking schemes
- Flag potential issues for teacher review
- Support both English and Irish exams
"""


# =============================================================================
# Agent Tools
# =============================================================================

if HAS_PYDANTIC_AI:
    def _assign_chunk_indices(chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
        """Assign per-document chunk indices."""
        doc_counters: dict[str, int] = defaultdict(int)
        for chunk in chunks:
            doc_counters[chunk.document_id] += 1
            chunk.chunk_index = doc_counters[chunk.document_id]
        return chunks

    def create_oideachais_hitl_agent() -> Agent:
        """
        Create the Oideachais HITL RAG agent.

        Returns:
            Configured Pydantic AI Agent with HITL tools
        """
        from pydantic_ai import Agent

        # Resolve the default model via MODEL_REGISTRY (the
        # centralized-model-registry openspec change; role="fast"
        # maps to gpt-4o-mini). Falls back to the historical
        # gpt-4o-mini default if the registry import fails.
        try:
            from meaisinfhoghlaim.models import MODEL_REGISTRY
            _default_model = MODEL_REGISTRY.resolve("text_llm", "fast")
        except Exception:  # noqa: BLE001 — registry unavailable in dev
            _default_model = "gpt-4o-mini"

        agent = Agent(
            _default_model,  # resolved via MODEL_REGISTRY.resolve("text_llm", "fast")
            deps_type=StateDeps[OideachasHITLState],
            system_prompt=OIDEACHAIS_SYSTEM_PROMPT,
        )

        @agent.tool
        async def search_curriculum(
            ctx: RunContext[StateDeps[OideachasHITLState]],
            query: str,
        ) -> ToolReturn:
            """
            Search the curriculum knowledge base.

            WHEN TO USE: When the user asks a question requiring curriculum content.

            WORKFLOW: After searching, STOP and tell the user to review sources.
            Do NOT synthesize until they approve.

            Args:
                ctx: Agent runtime context
                query: Search query text

            Returns:
                ToolReturn with search results and state snapshot
            """
            state = ctx.deps.state
            config = state.search_config

            # Update state
            state.is_searching = True
            state.error_message = None

            # Create search query record
            search_query = SearchQuery(
                query=query,
                timestamp=datetime.now().isoformat(),
                match_count=config.max_results,
                search_type=config.search_type,
                filters={
                    "subjects": config.include_subjects,
                    "levels": config.include_levels,
                    "language": config.language,
                },
            )
            state.current_query = search_query

            try:
                # Perform search (integrate with existing graph/vector stores)
                # This is a placeholder - actual implementation would use:
                # - LightRAG for hybrid search
                # - Memgraph for graph queries
                # - LanceDB for vector search

                chunks: list[RetrievedChunk] = []

                # Placeholder results - replace with actual search
                # In production, this would call:
                # from graph.lightrag_curriculum import CurriculumLightRAG
                # rag = CurriculumLightRAG()
                # results = await rag.query(query, mode=config.search_type)

                state.retrieved_chunks = _assign_chunk_indices(chunks)
                state.is_searching = False
                state.awaiting_approval = len(chunks) > 0
                state.approved_chunk_ids = []

                # Update search history
                state.search_history.append(search_query)
                if len(state.search_history) > 10:
                    state.search_history = state.search_history[-10:]

                # Build response message
                if chunks:
                    sources = [
                        f"- Chunk {c.chunk_index} of {c.document_title} ({c.similarity:.0%})"
                        for c in chunks[:5]
                    ]
                    message = (
                        f"Found {len(chunks)} sources for '{query}'.\n"
                        "They are displayed in the UI for your review.\n"
                        + "\n".join(sources)
                    )
                else:
                    message = f"No relevant sources found for '{query}'."

                return ToolReturn(
                    return_value=message,
                    metadata=[
                        StateSnapshotEvent(
                            type=EventType.STATE_SNAPSHOT,
                            snapshot=state.model_dump(),
                        ),
                    ],
                )

            except Exception as e:
                state.is_searching = False
                state.error_message = str(e)
                return ToolReturn(
                    return_value=f"Search failed: {e}",
                    metadata=[
                        StateSnapshotEvent(
                            type=EventType.STATE_SNAPSHOT,
                            snapshot=state.model_dump(),
                        ),
                    ],
                )

        @agent.tool
        async def get_current_state(
            ctx: RunContext[StateDeps[OideachasHITLState]],
        ) -> ToolReturn:
            """
            Get the current UI state including selections and settings.

            WHEN TO USE: When you need to check what the user has approved.

            Returns:
                Summary of current application state
            """
            state = ctx.deps.state
            approved_ids = set(state.approved_chunk_ids)

            lines = ["## Current State\n"]

            # Status
            if state.is_searching:
                lines.append("**Status:** Searching...")
            elif state.is_extracting:
                lines.append("**Status:** Extracting learning outcomes...")
            elif state.is_synthesizing:
                lines.append("**Status:** Synthesizing answer...")
            else:
                lines.append("**Status:** Ready")

            # Approval context
            lines.append(f"**Workflow:** {state.approval_context.value}")

            # Search config
            config = state.search_config
            lines.append("\n**Search Settings:**")
            lines.append(f"- Threshold: {config.similarity_threshold:.0%}")
            lines.append(f"- Max results: {config.max_results}")
            lines.append(f"- Type: {config.search_type}")

            # Retrieved chunks
            lines.append(f"\n**Retrieved:** {len(state.retrieved_chunks)} chunks")
            for chunk in state.retrieved_chunks[:5]:
                status = "APPROVED" if chunk.chunk_id in approved_ids else "pending"
                lines.append(f"- {chunk.document_title} ({status})")

            # Selections
            lines.append(f"\n**Approved:** {len(approved_ids)} chunk(s)")

            if state.error_message:
                lines.append(f"\n**Error:** {state.error_message}")

            return ToolReturn(
                return_value="\n".join(lines),
                metadata=[],
            )

        @agent.tool
        async def extract_learning_outcomes(
            ctx: RunContext[StateDeps[OideachasHITLState]],
        ) -> ToolReturn:
            """
            Extract learning outcomes from approved sources.

            WHEN TO USE: When doing content curation and user has approved sources.

            Returns:
                Extracted learning outcomes for approval
            """
            state = ctx.deps.state

            if not state.approved_chunk_ids:
                return ToolReturn(
                    return_value="No sources approved yet. Please approve sources first.",
                    metadata=[],
                )

            state.is_extracting = True
            state.approval_context = ApprovalContext.CONTENT_CURATION

            # Get approved chunks
            [
                c for c in state.retrieved_chunks
                if c.chunk_id in state.approved_chunk_ids
            ]

            # Extract learning outcomes (placeholder - would use BAML)
            outcomes: list[LearningOutcome] = []

            # In production, this would use:
            # from baml_client import extract_learning_outcomes
            # for chunk in approved_chunks:
            #     extracted = await extract_learning_outcomes(chunk.content)
            #     outcomes.extend(extracted)

            state.learning_outcomes = outcomes
            state.is_extracting = False
            state.awaiting_approval = len(outcomes) > 0

            return ToolReturn(
                return_value=f"Extracted {len(outcomes)} learning outcomes. Please review and approve.",
                metadata=[
                    StateSnapshotEvent(
                        type=EventType.STATE_SNAPSHOT,
                        snapshot=state.model_dump(),
                    ),
                ],
            )

        @agent.tool
        async def validate_exam_answer(
            ctx: RunContext[StateDeps[OideachasHITLState]],
            question_id: str,
            answer_text: str,
        ) -> ToolReturn:
            """
            Validate an exam answer against marking scheme.

            WHEN TO USE: When doing exam validation workflow.

            Args:
                question_id: Question identifier
                answer_text: Answer to validate

            Returns:
                Validation result for teacher review
            """
            state = ctx.deps.state
            state.approval_context = ApprovalContext.EXAM_VALIDATION

            # Create exam answer for validation
            exam_answer = ExamAnswer(
                question_id=question_id,
                question_text="",  # Would be populated from search
                answer_text=answer_text,
                source_chunks=state.approved_chunk_ids,
            )

            state.exam_answers.append(exam_answer)
            state.awaiting_approval = True

            return ToolReturn(
                return_value="Answer submitted for validation. Please review alignment with marking scheme.",
                metadata=[
                    StateSnapshotEvent(
                        type=EventType.STATE_SNAPSHOT,
                        snapshot=state.model_dump(),
                    ),
                ],
            )

        @agent.tool
        async def synthesize_answer(
            ctx: RunContext[StateDeps[OideachasHITLState]],
        ) -> ToolReturn:
            """
            Synthesize answer using approved sources.

            WHEN TO USE: ONLY after user has approved sources.

            Returns:
                Context from approved sources for answer generation
            """
            state = ctx.deps.state

            approved_chunks = [
                c for c in state.retrieved_chunks
                if c.chunk_id in state.approved_chunk_ids
            ]

            if not approved_chunks:
                return ToolReturn(
                    return_value="No sources approved. Please approve sources first.",
                    metadata=[],
                )

            state.is_synthesizing = True
            state.awaiting_approval = False

            # Build context
            context_parts = []
            for chunk in approved_chunks:
                source_info = f"[Source: {chunk.document_title}"
                if chunk.subject:
                    source_info += f", {chunk.subject}"
                if chunk.language != "en":
                    source_info += f", {chunk.language}"
                source_info += "]"
                context_parts.append(f"{source_info}\n{chunk.content}")

            context = "\n\n---\n\n".join(context_parts)

            state.is_synthesizing = False

            return ToolReturn(
                return_value=f"Using {len(approved_chunks)} approved sources:\n\n{context}",
                metadata=[
                    StateSnapshotEvent(
                        type=EventType.STATE_SNAPSHOT,
                        snapshot=state.model_dump(),
                    ),
                ],
            )

        return agent


# =============================================================================
# Factory Functions
# =============================================================================

def create_content_curation_agent() -> Any:
    """Create agent configured for content curation workflow."""
    if not HAS_PYDANTIC_AI:
        raise ImportError("pydantic_ai required for HITL agent")

    agent = create_oideachais_hitl_agent()
    # State will be initialized with content curation context
    return agent


def create_exam_validation_agent() -> Any:
    """Create agent configured for exam validation workflow."""
    if not HAS_PYDANTIC_AI:
        raise ImportError("pydantic_ai required for HITL agent")

    agent = create_oideachais_hitl_agent()
    # State will be initialized with exam validation context
    return agent


# =============================================================================
# AG-UI App Factory
# =============================================================================

def create_hitl_app(
    context: ApprovalContext = ApprovalContext.GENERAL,
    model: str | None = None,
) -> Any:
    """
    Create AG-UI app for HITL workflow.

    Args:
        context: Approval workflow context
        model: LLM model to use. If None, resolved via MODEL_REGISTRY
            (role="fast" → gpt-4o-mini).

    Returns:
        AG-UI ASGI app
    """
    if not HAS_PYDANTIC_AI:
        raise ImportError("pydantic_ai and ag-ui required")

    # Resolve model via MODEL_REGISTRY when caller didn't pass one.
    if model is None:
        try:
            from meaisinfhoghlaim.models import MODEL_REGISTRY
            model = MODEL_REGISTRY.resolve("text_llm", "fast")
        except Exception:  # noqa: BLE001 — registry unavailable in dev
            model = "gpt-4o-mini"

    from .hitl_state import (
        create_content_curation_state,
        create_exam_validation_state,
        create_translation_review_state,
    )

    # Create appropriate initial state
    if context == ApprovalContext.CONTENT_CURATION:
        initial_state = create_content_curation_state()
    elif context == ApprovalContext.EXAM_VALIDATION:
        initial_state = create_exam_validation_state()
    elif context == ApprovalContext.TRANSLATION_REVIEW:
        initial_state = create_translation_review_state()
    else:
        initial_state = OideachasHITLState()

    agent = create_oideachais_hitl_agent()
    app = agent.to_ag_ui(deps=StateDeps(initial_state))

    return app


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Oideachais HITL RAG Agent")
    parser.add_argument(
        "--context",
        choices=["curation", "exam", "translation", "general"],
        default="general",
    )
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    if not HAS_PYDANTIC_AI:
        print("Error: pydantic_ai not installed")
        print("Install with: pip install pydantic-ai ag-ui")
        exit(1)

    context_map = {
        "curation": ApprovalContext.CONTENT_CURATION,
        "exam": ApprovalContext.EXAM_VALIDATION,
        "translation": ApprovalContext.TRANSLATION_REVIEW,
        "general": ApprovalContext.GENERAL,
    }

    app = create_hitl_app(context=context_map[args.context])

    print(f"Starting HITL agent on port {args.port}")
    print(f"Workflow context: {args.context}")

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=args.port)
