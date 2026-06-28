"""
AG-UI Curriculum Agent for Celtic Education Platform.

Wraps the curriculum comparison agent with AG-UI middleware for
real-time streaming UI updates via SSE protocol.

Uses 17-event AG-UI protocol:
- TEXT_MESSAGE_START/CONTENT/END for streaming responses
- STATE_SNAPSHOT/STATE_DELTA for UI state updates
- TOOL_CALL_START/ARGS/END for tool execution visualization
"""

import datetime
import json
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from google.adk.agents import LlmAgent
from google.adk.planners import BuiltInPlanner
from google.genai import types as genai_types
from pydantic import BaseModel

# Import existing tools
from sruth.oideachais.tools.curriculum_search import (
    compare_curricula,
    search_curriculum,
)

from .config import CURRICULUM_FRAMEWORKS, config


# --- AG-UI Event Types ---
class AGUIEventType:
    """AG-UI SSE event types."""
    RUN_STARTED = "RUN_STARTED"
    RUN_FINISHED = "RUN_FINISHED"
    RUN_ERROR = "RUN_ERROR"
    TEXT_MESSAGE_START = "TEXT_MESSAGE_START"
    TEXT_MESSAGE_CONTENT = "TEXT_MESSAGE_CONTENT"
    TEXT_MESSAGE_END = "TEXT_MESSAGE_END"
    TOOL_CALL_START = "TOOL_CALL_START"
    TOOL_CALL_ARGS = "TOOL_CALL_ARGS"
    TOOL_CALL_END = "TOOL_CALL_END"
    STATE_SNAPSHOT = "STATE_SNAPSHOT"
    STATE_DELTA = "STATE_DELTA"
    MESSAGES_SNAPSHOT = "MESSAGES_SNAPSHOT"
    STEP_STARTED = "STEP_STARTED"
    STEP_FINISHED = "STEP_FINISHED"


# --- Structured Outputs for UI ---
class CurriculumSearchResult(BaseModel):
    """Search result for curriculum browser."""
    outcome_id: str
    nation: str
    level: str
    subject: str
    title: str
    description: str
    language: str
    similarity_score: float | None = None


class ComparisonTableRow(BaseModel):
    """Row in cross-nation comparison table."""
    topic: str
    ireland: str | None = None
    england: str | None = None
    scotland: str | None = None
    wales: str | None = None
    northern_ireland: str | None = None
    alignment_score: float | None = None


class TranslationRequest(BaseModel):
    """Request for Celtic language translation approval."""
    translation_id: str
    source_language: str
    target_language: str
    source_text: str
    translated_text: str
    domain: str
    confidence: float
    needs_review: bool


# --- AG-UI State Models ---
class CurriculumUIState(BaseModel):
    """State for curriculum browser UI."""
    search_query: str = ""
    selected_nations: list[str] = []
    selected_levels: list[str] = []
    selected_subjects: list[str] = []
    results: list[CurriculumSearchResult] = []
    comparison_table: list[ComparisonTableRow] = []
    pending_translations: list[TranslationRequest] = []
    is_loading: bool = False
    error: str | None = None


# --- AG-UI Tool Wrappers ---
async def search_curriculum_hybrid(
    query: str,
    nations: list[str] | None = None,
    levels: list[str] | None = None,
    subjects: list[str] | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    """
    Hybrid search combining vector similarity and keyword matching.

    Returns STATE_SNAPSHOT event with search results.
    """
    # Call underlying search
    results = await search_curriculum(
        query=query,
        nations=nations,
        levels=levels,
        subjects=subjects,
        limit=limit,
    )

    # Format for UI
    formatted_results = [
        CurriculumSearchResult(
            outcome_id=r.get("outcome_id", ""),
            nation=r.get("nation", ""),
            level=r.get("level", ""),
            subject=r.get("subject", ""),
            title=r.get("title", ""),
            description=r.get("description", "")[:200] + "...",
            language=r.get("language", "en"),
            similarity_score=r.get("score"),
        )
        for r in results
    ]

    return {
        "event_type": AGUIEventType.STATE_SNAPSHOT,
        "state": {
            "search_query": query,
            "selected_nations": nations or [],
            "results": [r.model_dump() for r in formatted_results],
            "is_loading": False,
        }
    }


async def compare_curricula_cross_nation(
    subject: str,
    nations: list[str],
    level: str | None = None,
) -> dict[str, Any]:
    """
    Compare curriculum coverage across nations.

    Returns STATE_DELTA event with comparison table.
    """
    # Call underlying comparison
    comparison = await compare_curricula(
        subject=subject,
        nations=nations,
        level=level,
    )

    # Format as table rows
    table_rows = []
    for topic_data in comparison.get("topics", []):
        row = ComparisonTableRow(
            topic=topic_data.get("topic", ""),
            ireland=topic_data.get("ireland"),
            england=topic_data.get("england"),
            scotland=topic_data.get("scotland"),
            wales=topic_data.get("wales"),
            northern_ireland=topic_data.get("northern_ireland"),
            alignment_score=topic_data.get("alignment_score"),
        )
        table_rows.append(row)

    return {
        "event_type": AGUIEventType.STATE_DELTA,
        "delta": [
            {"op": "replace", "path": "/comparison_table", "value": [r.model_dump() for r in table_rows]},
            {"op": "replace", "path": "/is_loading", "value": False},
        ]
    }


async def request_translation_approval(
    source_text: str,
    source_language: str,
    target_language: str,
    domain: str = "curriculum",
) -> dict[str, Any]:
    """
    Request human-in-the-loop approval for Celtic language translation.

    Pauses agent execution until user approves/rejects translation.
    """
    import uuid

    # Generate translation (placeholder - would call actual translation service)
    translated_text = f"[Translation of '{source_text[:50]}...' to {target_language}]"
    confidence = 0.85

    translation_request = TranslationRequest(
        translation_id=str(uuid.uuid4()),
        source_language=source_language,
        target_language=target_language,
        source_text=source_text,
        translated_text=translated_text,
        domain=domain,
        confidence=confidence,
        needs_review=confidence < 0.9,
    )

    return {
        "event_type": AGUIEventType.STATE_DELTA,
        "requires_approval": True,
        "approval_type": "translation",
        "delta": [
            {"op": "add", "path": "/pending_translations/-", "value": translation_request.model_dump()},
        ]
    }


# --- AG-UI Curriculum Agent ---
AGUI_CURRICULUM_INSTRUCTION = f"""
You are a curriculum assistant for the Celtic Education Platform.

**YOUR CAPABILITIES:**
1. Search curriculum content across 5 nations (Ireland, England, Scotland, Wales, NI)
2. Compare learning outcomes and topics across nations
3. Find equivalent content in different curricula
4. Support Celtic language translations (Irish, Welsh, Scottish Gaelic)

**TOOLS:**
- `search_curriculum_hybrid`: Find curriculum content by topic, nation, level
- `compare_curricula_cross_nation`: Compare a subject across nations
- `request_translation_approval`: Request translation for Celtic languages

**CURRICULUM FRAMEWORKS:**
{CURRICULUM_FRAMEWORKS}

**UI INTERACTION:**
When you search or compare, the results will update the UI automatically.
For translations requiring human review, the UI will show an approval dialog.

**RESPONSE FORMAT:**
- Start with a brief answer to the user's question
- Reference specific curriculum outcomes by code when possible
- Highlight Celtic language provisions when relevant
- Note cross-nation equivalencies

**AGE/STAGE REFERENCE:**
| Age | Ireland | England | Scotland | Wales | NI |
|-----|---------|---------|----------|-------|-----|
| 12-15 | Junior Cycle | KS3/4 | Third/Fourth | KS3/4 | KS3/4 |
| 15-16 | Junior Cert | GCSE | National 5 | GCSE | GCSE |
| 16-18 | Senior Cycle | A-Level | Higher | A-Level | A-Level |

Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
"""

agui_curriculum_agent = LlmAgent(
    name="agui_curriculum_agent",
    model=config.model_name,
    description="AG-UI enabled curriculum assistant with real-time UI updates.",
    planner=BuiltInPlanner(
        thinking_config=genai_types.ThinkingConfig(include_thoughts=True)
    ),
    instruction=AGUI_CURRICULUM_INSTRUCTION,
    tools=[
        search_curriculum_hybrid,
        compare_curricula_cross_nation,
        request_translation_approval,
    ],
    output_key="curriculum_response",
)


# --- FastAPI Integration ---
def create_agui_app() -> FastAPI:
    """Create FastAPI app with AG-UI SSE endpoint."""
    app = FastAPI(title="Curriculum AG-UI Agent")

    @app.post("/agent")
    async def run_agent(request: Request):
        """AG-UI SSE endpoint for curriculum agent."""
        body = await request.json()
        messages = body.get("messages", [])
        state = body.get("state", {})

        async def event_stream():
            # Emit RUN_STARTED
            yield f"event: {AGUIEventType.RUN_STARTED}\n"
            yield f"data: {json.dumps({'run_id': 'curriculum_run_1'})}\n\n"

            # Run agent (simplified - actual implementation would stream)
            try:
                result = await agui_curriculum_agent.run(
                    messages=messages,
                    context=state,
                )

                # Emit TEXT_MESSAGE events
                yield f"event: {AGUIEventType.TEXT_MESSAGE_START}\n"
                yield f"data: {json.dumps({'message_id': 'msg_1'})}\n\n"

                # Stream response content
                content = result.get("curriculum_response", "")
                for chunk in [content[i:i+50] for i in range(0, len(content), 50)]:
                    yield f"event: {AGUIEventType.TEXT_MESSAGE_CONTENT}\n"
                    yield f"data: {json.dumps({'content': chunk})}\n\n"

                yield f"event: {AGUIEventType.TEXT_MESSAGE_END}\n"
                yield f"data: {json.dumps({})}\n\n"

                # Emit RUN_FINISHED
                yield f"event: {AGUIEventType.RUN_FINISHED}\n"
                yield f"data: {json.dumps({'status': 'success'})}\n\n"

            except Exception as e:
                yield f"event: {AGUIEventType.RUN_ERROR}\n"
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )

    return app


# Export for use
__all__ = [
    "AGUIEventType",
    "ComparisonTableRow",
    "CurriculumSearchResult",
    "CurriculumUIState",
    "TranslationRequest",
    "agui_curriculum_agent",
    "create_agui_app",
]
