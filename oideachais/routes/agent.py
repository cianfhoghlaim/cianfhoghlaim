"""
Agent Chat API Routes.

Provides conversational AI endpoints:
    POST /agent/chat - Chat with education team
    POST /agent/chat/stream - Stream chat responses (SSE)
    POST /api/agent - AG-UI streaming agent endpoint (new)
    POST /agents/state - AG-UI state endpoint (new)
    GET /agent/sessions/{session_id} - Get session history
    DELETE /agent/sessions/{session_id} - Clear session

Integrates with Agno education_team for multi-agent coordination.
Also provides AG-UI protocol compliant streaming endpoint.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
import uuid
from collections.abc import AsyncGenerator
from typing import Any

import duckdb
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Database path for AG-UI agent
DB_PATH = os.environ.get(
    "DUCKDB_PATH",
    os.path.join(os.path.dirname(__file__), "../../storage/data/celtic_education.duckdb"),
)

router = APIRouter(prefix="/agent", tags=["agent"])


# =============================================================================
# Request/Response Models
# =============================================================================


class Message(BaseModel):
    """Chat message."""

    role: str = Field(..., description="Message role: user, assistant, system")
    content: str = Field(..., description="Message content")
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatRequest(BaseModel):
    """Chat request body."""

    message: str = Field(..., min_length=1, max_length=4000, description="User message")
    session_id: str | None = Field(None, description="Session ID for conversation continuity")
    language: str = Field(default="en", description="Preferred response language")
    stream: bool = Field(default=False, description="Enable streaming response")
    include_sources: bool = Field(default=True, description="Include source citations")
    agents: list[str] | None = Field(None, description="Limit to specific agents")


class ChatResponse(BaseModel):
    """Chat response."""

    message: str = Field(..., description="Assistant response")
    session_id: str = Field(..., description="Session ID for follow-up")
    sources: list[dict[str, Any]] = Field(default_factory=list)
    agents_used: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SessionInfo(BaseModel):
    """Session information."""

    session_id: str
    created_at: str
    message_count: int
    last_activity: str
    agents_used: list[str]


# =============================================================================
# Session Storage (In-Memory with SQLite fallback)
# =============================================================================

# In-memory session store (replace with Redis/SQLite for production)
_sessions: dict[str, dict[str, Any]] = {}


def get_session(session_id: str) -> dict[str, Any]:
    """Get or create a session."""
    if session_id not in _sessions:
        _sessions[session_id] = {
            "id": session_id,
            "created_at": time.time(),
            "last_activity": time.time(),
            "messages": [],
            "agents_used": set(),
        }
    return _sessions[session_id]


def update_session(
    session_id: str,
    user_message: str,
    assistant_message: str,
    agents_used: list[str],
) -> None:
    """Update session with new messages."""
    session = get_session(session_id)
    session["messages"].append({"role": "user", "content": user_message})
    session["messages"].append({"role": "assistant", "content": assistant_message})
    session["agents_used"].update(agents_used)
    session["last_activity"] = time.time()


def clear_session(session_id: str) -> bool:
    """Clear a session."""
    if session_id in _sessions:
        del _sessions[session_id]
        return True
    return False


# =============================================================================
# Agent Integration
# =============================================================================


def get_education_team():
    """Lazy-load the education team to avoid circular imports."""
    try:
        from ...agents.agno.education_team import EducationResponse, education_team
        return education_team, EducationResponse
    except ImportError as e:
        logger.warning(f"Failed to import education_team: {e}")
        return None, None


async def run_agent_async(
    message: str,
    session_id: str,
    language: str = "en",
    stream: bool = False,
) -> dict[str, Any]:
    """Run the education team agent asynchronously."""
    education_team, EducationResponse = get_education_team()

    if education_team is None:
        # Fallback response if agents not available
        return {
            "message": f"Agent system not available. Your query: {message}",
            "agents_used": [],
            "sources": [],
        }

    # Add language context if not English
    query = message
    if language != "en":
        lang_names = {"ga": "Irish", "cy": "Welsh", "gd": "Scottish Gaelic", "gv": "Manx"}
        lang_hint = f"[Respond primarily in {lang_names.get(language, language)}] "
        query = lang_hint + message

    # Add session context (last few messages)
    session = get_session(session_id)
    if session["messages"]:
        # Include last 4 messages as context
        context_messages = session["messages"][-4:]
        context = "\n".join([f"{m['role']}: {m['content']}" for m in context_messages])
        query = f"Previous context:\n{context}\n\nNew query: {query}"

    # Run the team
    try:
        # Run in thread pool since Agno may use sync operations
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: education_team.run(query, stream=False)
        )

        # Extract response content
        if hasattr(response, 'summary'):
            message_text = response.summary
        elif hasattr(response, 'content'):
            message_text = response.content
        else:
            message_text = str(response)

        # Collect sources
        sources = []
        if hasattr(response, 'research') and response.research:
            sources.extend(response.research.sources)
        if hasattr(response, 'curriculum_info') and response.curriculum_info:
            sources.append({"type": "curriculum", "results": len(response.curriculum_info.results)})

        # Collect agents used
        agents_used = []
        if hasattr(response, 'curriculum_info') and response.curriculum_info:
            agents_used.append("curriculum")
        if hasattr(response, 'research') and response.research:
            agents_used.append("research")
        if hasattr(response, 'translation') and response.translation:
            agents_used.append("translation")
        if hasattr(response, 'corpus_data') and response.corpus_data:
            agents_used.append("corpus")
        if hasattr(response, 'geospatial_data') and response.geospatial_data:
            agents_used.append("geospatial")
        if hasattr(response, 'statistics') and response.statistics:
            agents_used.append("statistics")

        return {
            "message": message_text,
            "agents_used": agents_used,
            "sources": sources,
            "follow_up": getattr(response, 'follow_up_suggestions', []),
        }

    except Exception as e:
        logger.error(f"Agent execution error: {e}")
        return {
            "message": f"I encountered an error processing your request. Please try again. Error: {str(e)}",
            "agents_used": [],
            "sources": [],
        }


async def stream_agent_response(
    message: str,
    session_id: str,
    language: str = "en",
) -> AsyncGenerator[str, None]:
    """Stream agent response as SSE events."""
    education_team, _ = get_education_team()

    if education_team is None:
        yield f"data: {json.dumps({'type': 'error', 'content': 'Agent system not available'})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        return

    # Build query with context
    query = message
    if language != "en":
        lang_names = {"ga": "Irish", "cy": "Welsh", "gd": "Scottish Gaelic", "gv": "Manx"}
        query = f"[Respond in {lang_names.get(language, language)}] {message}"

    try:
        # Start event
        yield f"data: {json.dumps({'type': 'start', 'session_id': session_id})}\n\n"

        # Run agent (Agno streaming)
        full_response = ""
        agents_used = []

        loop = asyncio.get_event_loop()

        # Since Agno's streaming is generator-based, we need to handle it carefully
        def run_stream():
            return education_team.run(query, stream=True)

        response = await loop.run_in_executor(None, run_stream)

        # If response is a generator, iterate through it
        if hasattr(response, '__iter__') and not isinstance(response, str):
            for chunk in response:
                chunk_text = str(chunk) if not hasattr(chunk, 'content') else chunk.content
                full_response += chunk_text
                yield f"data: {json.dumps({'type': 'text', 'content': chunk_text})}\n\n"
                await asyncio.sleep(0)  # Yield control
        else:
            # Non-streaming fallback
            if hasattr(response, 'summary'):
                full_response = response.summary
            else:
                full_response = str(response)
            yield f"data: {json.dumps({'type': 'text', 'content': full_response})}\n\n"

        # Update session
        update_session(session_id, message, full_response, agents_used)

        # Done event
        yield f"data: {json.dumps({'type': 'done', 'agents_used': agents_used})}\n\n"

    except Exception as e:
        logger.error(f"Streaming error: {e}")
        yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"


# =============================================================================
# API Endpoints
# =============================================================================


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Chat with the Celtic Education Team.

    Sends a message to the education team's multi-agent system.
    The team routes queries to appropriate specialist agents:
    - Curriculum Agent: NCCA/SEC content
    - Research Agent: Academic resources
    - Translation Agent: Celtic languages
    - Corpus Agent: Folklore/linguistic corpora
    - Geospatial Agent: Location-based queries
    - Statistics Agent: Education statistics
    """
    # Generate or use session ID
    session_id = request.session_id or str(uuid.uuid4())

    # Handle streaming
    if request.stream:
        return StreamingResponse(
            stream_agent_response(
                message=request.message,
                session_id=session_id,
                language=request.language,
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    # Non-streaming response
    result = await run_agent_async(
        message=request.message,
        session_id=session_id,
        language=request.language,
        stream=False,
    )

    # Update session
    update_session(
        session_id=session_id,
        user_message=request.message,
        assistant_message=result["message"],
        agents_used=result["agents_used"],
    )

    return ChatResponse(
        message=result["message"],
        session_id=session_id,
        sources=result.get("sources", []),
        agents_used=result.get("agents_used", []),
        metadata={
            "follow_up": result.get("follow_up", []),
            "language": request.language,
        },
    )


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    """
    Stream chat responses from the education team.

    Returns Server-Sent Events (SSE) with:
    - type: 'start' - Session started
    - type: 'text' - Response chunk
    - type: 'done' - Response complete
    - type: 'error' - Error occurred
    """
    session_id = request.session_id or str(uuid.uuid4())

    return StreamingResponse(
        stream_agent_response(
            message=request.message,
            session_id=session_id,
            language=request.language,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/sessions/{session_id}", response_model=SessionInfo)
async def get_session_info(session_id: str) -> SessionInfo:
    """
    Get session information and history.
    """
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = _sessions[session_id]

    return SessionInfo(
        session_id=session_id,
        created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(session["created_at"])),
        message_count=len(session["messages"]),
        last_activity=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(session["last_activity"])),
        agents_used=list(session["agents_used"]),
    )


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str) -> dict[str, str]:
    """
    Delete a session and clear its history.
    """
    if clear_session(session_id):
        return {"status": "deleted", "session_id": session_id}
    else:
        raise HTTPException(status_code=404, detail="Session not found")


@router.get("/health")
async def agent_health() -> dict[str, Any]:
    """
    Check agent system health.
    """
    education_team, _ = get_education_team()

    return {
        "status": "healthy" if education_team else "degraded",
        "education_team": "available" if education_team else "unavailable",
        "active_sessions": len(_sessions),
    }


# =============================================================================
# AG-UI Protocol Streaming Endpoint
# =============================================================================


from api.middleware.agui import (
    AgentEvent,
    AGUIStreamingAgent,
    encode_sse_event,
)


async def curriculum_agent_agui(
    message: str,
    context: dict[str, Any],
) -> AsyncGenerator[AgentEvent, None]:
    """AG-UI compliant curriculum search agent.

    Handles:
    - Curriculum search queries
    - Learning outcome lookup
    - Cross-nation comparison
    - Celtic language support

    Args:
        message: User message
        context: Request context with session info, language, etc.

    Yields:
        AgentEvent objects for AG-UI streaming
    """
    language = context.get("language", "en")
    message_lower = message.lower()

    # Detect search intent
    is_search = any(
        word in message_lower
        for word in ["search", "find", "show", "list", "what", "how", "compare"]
    )
    is_comparison = any(
        word in message_lower for word in ["compare", "comparison", "versus", "vs"]
    )

    # Extract subjects
    subjects = []
    for subject in ["mathematics", "maths", "math", "english", "science", "history", "gaeilge", "irish"]:
        if subject in message_lower:
            normalized = "mathematics" if subject in ["maths", "math"] else subject
            normalized = "gaeilge" if subject == "irish" else normalized
            if normalized not in subjects:
                subjects.append(normalized)

    # Extract level
    level = None
    for lvl in ["junior cycle", "leaving cert", "primary", "senior cycle"]:
        if lvl in message_lower:
            level = lvl.replace(" ", "_")
            break

    # Perform search if needed
    search_results = []

    if is_search or subjects:
        # Emit tool call events
        tool_call_id = str(uuid.uuid4())
        yield AgentEvent(
            type="TOOL_CALL_START",
            tool_call_id=tool_call_id,
            tool_name="search_curriculum",
        )
        yield AgentEvent(
            type="TOOL_CALL_ARGS",
            tool_call_id=tool_call_id,
            tool_args={"query": message, "subjects": subjects, "level": level},
        )

        # Execute search
        try:
            search_results = await _search_learning_outcomes_agui(
                query=message, subjects=subjects, level=level, limit=10
            )
        except Exception as e:
            logger.error(f"Search error: {e}")

        yield AgentEvent(type="TOOL_CALL_END", tool_call_id=tool_call_id)
        yield AgentEvent(
            type="TOOL_RESULT",
            tool_call_id=tool_call_id,
            tool_result={"count": len(search_results), "results": search_results[:5]},
        )

    # Emit state
    new_state = {
        "selected_subjects": subjects,
        "selected_level": level,
        "search_results": [
            {
                "id": r.get("id", ""),
                "subject": r.get("subject", ""),
                "outcome_text": r.get("outcome_text", ""),
                "level": r.get("level", ""),
                "nation": r.get("nation", "ireland"),
            }
            for r in search_results[:10]
        ],
    }
    yield AgentEvent(type="STATE_SNAPSHOT", state=new_state)

    # Generate response
    if search_results:
        if is_comparison and len(subjects) >= 2:
            response = _format_comparison_response(subjects, search_results)
        else:
            response = _format_search_response(subjects, search_results, message, level)
    elif is_search:
        response = f"I searched for learning outcomes matching '{message}' but didn't find matches. Try subjects like Mathematics, English, Science, or History."
    else:
        response = _format_help_response()

    # Stream response
    chunk_size = 20
    for i in range(0, len(response), chunk_size):
        yield AgentEvent(type="TEXT_DELTA", delta=response[i : i + chunk_size])
        await asyncio.sleep(0.01)


async def _search_learning_outcomes_agui(
    query: str,
    subjects: list[str] | None = None,
    level: str | None = None,
    limit: int = 10,
) -> list[dict]:
    """Search learning outcomes for AG-UI agent."""
    try:
        conn = duckdb.connect(DB_PATH, read_only=True)

        sql = """
            SELECT
                u.outcome_id as id,
                u.subject,
                u.title as outcome_text,
                u.curriculum_level as level,
                u.strand,
                n.nation_name as nation
            FROM int.int_unified_outcomes u
            LEFT JOIN marts.dim_nation n ON u.nation = n.nation_code
            WHERE 1=1
        """
        params = []

        if subjects:
            placeholders = ", ".join(["?" for _ in subjects])
            sql += f" AND u.subject IN ({placeholders})"
            params.extend([s.lower() for s in subjects])

        if level:
            sql += " AND u.curriculum_level ILIKE ?"
            params.append(f"%{level}%")

        if query:
            sql += " AND (u.title ILIKE ? OR u.strand ILIKE ?)"
            pattern = f"%{query}%"
            params.extend([pattern, pattern])

        sql += f" LIMIT {limit}"

        result = conn.execute(sql, params).fetchall()
        columns = [desc[0] for desc in conn.description]
        return [dict(zip(columns, row)) for row in result]
    except Exception as e:
        logger.error(f"AG-UI search error: {e}")
        return []
    finally:
        if "conn" in locals():
            conn.close()


def _format_search_response(
    subjects: list[str], results: list[dict], query: str, level: str | None
) -> str:
    """Format search results as response text."""
    if not results:
        return "No matching curriculum content found. Try a different subject or level."

    subject_str = ", ".join(s.title() for s in subjects) if subjects else "curriculum"
    level_str = level.replace("_", " ").title() if level else "all levels"

    response = f"Found {len(results)} learning outcomes for **{subject_str}** ({level_str}).\n\n"

    strands: dict[str, list] = {}
    for r in results:
        strand = r.get("strand") or "General"
        if strand not in strands:
            strands[strand] = []
        strands[strand].append(r)

    for strand, outcomes in list(strands.items())[:3]:
        response += f"### {strand}\n"
        for outcome in outcomes[:3]:
            response += f"- {outcome.get('outcome_text', '')}\n"
        response += "\n"

    return response


def _format_comparison_response(subjects: list[str], results: list[dict]) -> str:
    """Format comparison response."""
    response = f"## Curriculum Comparison: {', '.join(s.title() for s in subjects)}\n\n"
    for subject in subjects[:2]:
        subject_results = [r for r in results if r.get("subject", "").lower() == subject.lower()]
        response += f"### {subject.title()} ({len(subject_results)} outcomes)\n"
        for r in subject_results[:3]:
            response += f"- {r.get('outcome_text', '')[:100]}...\n"
        response += "\n"
    return response


def _format_help_response() -> str:
    """Format help response."""
    return """# Celtic Curriculum Assistant

I help you explore educational curricula across Celtic nations.

## Search Examples
- "Show me Junior Cycle Mathematics outcomes"
- "Find Science learning objectives"
- "What are the History topics for Leaving Cert?"

## Available Subjects
Mathematics, English, Science, History, Geography, Gaeilge

## Education Levels
- **Ireland:** Primary, Junior Cycle, Leaving Certificate
- **UK:** Key Stages, GCSE, A-Levels
- **Scotland:** Highers, Advanced Highers

What would you like to explore?"""


# Create streaming agent instance
_agui_streaming_agent = AGUIStreamingAgent(
    agent_callable=curriculum_agent_agui,
    app_name="oideachais",
    user_id="demo",
    session_timeout_seconds=1200,
)


# AG-UI Router (separate from existing /agent routes)
agui_router = APIRouter(tags=["ag-ui"])


@agui_router.post("/api/agent")
async def agui_stream_endpoint(request: Request) -> StreamingResponse:
    """
    AG-UI Protocol streaming agent endpoint.

    Receives messages and streams AG-UI events back via SSE.
    Supports all 17 AG-UI event types for full protocol compliance.
    """
    from api.middleware.agui import AGUIMessage, AGUIRequest

    try:
        body = await request.json()
    except Exception:
        body = {}

    agui_request = AGUIRequest(
        thread_id=body.get("thread_id") or body.get("threadId"),
        run_id=body.get("run_id") or body.get("runId"),
        messages=[
            AGUIMessage(**msg) if isinstance(msg, dict) else msg
            for msg in body.get("messages", [])
        ],
        state=body.get("state"),
        tools=body.get("tools"),
        language=body.get("language", "en"),
    )

    async def event_generator():
        try:
            async for event in _agui_streaming_agent.run(agui_request):
                yield encode_sse_event(event)
        except Exception as e:
            logger.error(f"AG-UI streaming error: {e}", exc_info=True)
            yield encode_sse_event({
                "type": "RUN_ERROR",
                "message": str(e),
                "code": "STREAMING_ERROR",
            })

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@agui_router.post("/agents/state")
async def agui_state_endpoint(request: Request) -> dict[str, Any]:
    """
    AG-UI state retrieval endpoint.

    Returns thread state and message history for a given thread ID.
    """
    try:
        body = await request.json()
    except Exception:
        body = {}

    thread_id = body.get("threadId") or body.get("thread_id", "")

    try:
        state = await _agui_streaming_agent.get_state(thread_id)
        messages = await _agui_streaming_agent.get_messages(thread_id)

        return {
            "threadId": thread_id,
            "threadExists": state is not None,
            "state": json.dumps(state or {}),
            "messages": json.dumps(messages),
        }
    except Exception as e:
        logger.error(f"AG-UI state error: {e}")
        return {
            "threadId": thread_id,
            "threadExists": False,
            "state": "{}",
            "messages": "[]",
            "error": str(e),
        }
