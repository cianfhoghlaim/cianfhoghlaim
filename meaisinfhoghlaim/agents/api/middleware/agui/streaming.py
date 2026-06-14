"""
AG-UI Streaming Agent.

Provides a high-level interface for creating AG-UI streaming endpoints
that integrate with curriculum search, translation, and other agent tools.
"""

from __future__ import annotations

import json
import logging
import uuid
from collections.abc import AsyncGenerator, Callable
from typing import Any, Protocol

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .event_translator import AgentEvent, EventTranslator
from .session_manager import SessionManager

logger = logging.getLogger(__name__)


# =============================================================================
# Request/Response Models
# =============================================================================


class AGUIMessage(BaseModel):
    """Message in AG-UI format."""

    id: str | None = None
    role: str
    content: str | None = None
    tool_call_id: str | None = None
    tool_calls: list[dict[str, Any]] | None = None


class AGUIRequest(BaseModel):
    """AG-UI run agent request."""

    thread_id: str | None = None
    run_id: str | None = None
    messages: list[AGUIMessage] = []
    state: dict[str, Any] | None = None
    tools: list[dict[str, Any]] | None = None
    language: str = "en"


class AGUIStateRequest(BaseModel):
    """Request for /agents/state endpoint."""

    threadId: str
    userId: str | None = None


# =============================================================================
# Agent Protocol
# =============================================================================


class AgentCallable(Protocol):
    """Protocol for agent implementations."""

    async def __call__(
        self,
        message: str,
        context: dict[str, Any],
    ) -> AsyncGenerator[AgentEvent, None]:
        """Process a message and yield agent events."""
        ...


# =============================================================================
# AG-UI Streaming Agent
# =============================================================================


class AGUIStreamingAgent:
    """High-level AG-UI streaming agent wrapper.

    Wraps an agent callable and provides:
    - Session management
    - Event translation to AG-UI protocol
    - SSE streaming
    - State management
    - Tool call tracking

    Usage:
        async def my_agent(message: str, context: dict) -> AsyncGenerator[AgentEvent, None]:
            yield AgentEvent(type="TEXT_DELTA", delta="Hello!")

        agent = AGUIStreamingAgent(
            agent_callable=my_agent,
            app_name="oideachais",
            user_id="demo"
        )

        # Use directly
        async for event in agent.run(request):
            print(event)

        # Or add to FastAPI
        add_agui_endpoint(app, agent, path="/api/agent")
    """

    def __init__(
        self,
        agent_callable: AgentCallable,
        app_name: str = "oideachais",
        user_id: str | None = None,
        user_id_extractor: Callable[[AGUIRequest], str] | None = None,
        session_timeout_seconds: int = 1200,
    ):
        self.agent_callable = agent_callable
        self.app_name = app_name
        self._static_user_id = user_id
        self._user_id_extractor = user_id_extractor
        self._session_timeout = session_timeout_seconds

        self._session_manager: SessionManager | None = None
        self._initialized = False

    async def _ensure_initialized(self):
        """Ensure session manager is initialized."""
        if not self._initialized:
            self._session_manager = await SessionManager.get_instance(
                session_timeout_seconds=self._session_timeout
            )
            self._initialized = True

    def _get_user_id(self, request: AGUIRequest) -> str:
        """Resolve user ID from request or static value."""
        if self._static_user_id:
            return self._static_user_id
        if self._user_id_extractor:
            return self._user_id_extractor(request)
        return f"thread_user_{request.thread_id}"

    async def run(
        self,
        request: AGUIRequest,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Run the agent and yield AG-UI events.

        Args:
            request: AG-UI run request

        Yields:
            AG-UI protocol events as dicts
        """
        await self._ensure_initialized()

        thread_id = request.thread_id or str(uuid.uuid4())
        run_id = request.run_id or str(uuid.uuid4())
        user_id = self._get_user_id(request)

        # Get or create session
        session, session_id = await self._session_manager.get_or_create_session(
            thread_id=thread_id,
            user_id=user_id,
            initial_state=request.state or {},
        )

        # Update session state if provided
        if request.state:
            await self._session_manager.update_session_state(
                session_id=session_id,
                state=request.state,
            )

        # Create event translator
        translator = EventTranslator(
            thread_id=thread_id,
            run_id=run_id,
        )

        # Get the latest user message
        user_message = ""
        for msg in reversed(request.messages):
            if msg.role == "user" and msg.content:
                user_message = msg.content
                break

        # Build context for agent
        context = {
            "thread_id": thread_id,
            "run_id": run_id,
            "session_id": session_id,
            "user_id": user_id,
            "language": request.language,
            "state": session.state.copy(),
            "messages": request.messages,
            "tools": request.tools,
        }

        try:
            # Emit RUN_STARTED
            async for event in translator.translate(
                AgentEvent(type="RUN_STARTED")
            ):
                yield event

            # Run the agent
            async for agent_event in self.agent_callable(user_message, context):
                # Translate and yield events
                async for event in translator.translate(agent_event):
                    yield event

            # Emit state snapshot
            final_state = await self._session_manager.get_session_state(session_id)
            if final_state:
                async for event in translator.translate(
                    AgentEvent(type="STATE_SNAPSHOT", state=final_state)
                ):
                    yield event

            # Close any open text message and emit RUN_FINISHED
            async for event in translator.translate(
                AgentEvent(type="RUN_FINISHED")
            ):
                yield event

        except Exception as e:
            logger.error(f"Agent execution error: {e}", exc_info=True)
            async for event in translator.translate(
                AgentEvent(
                    type="RUN_ERROR",
                    content=str(e),
                    data={"code": "AGENT_EXECUTION_ERROR"},
                )
            ):
                yield event

    async def get_state(self, thread_id: str) -> dict[str, Any] | None:
        """Get session state by thread ID.

        Args:
            thread_id: AG-UI thread ID

        Returns:
            Session state or None
        """
        await self._ensure_initialized()
        session = await self._session_manager.get_session_by_thread_id(thread_id)
        if session:
            return session.state.copy()
        return None

    async def get_messages(self, thread_id: str) -> list[dict[str, Any]]:
        """Get message history by thread ID.

        Args:
            thread_id: AG-UI thread ID

        Returns:
            List of messages
        """
        await self._ensure_initialized()
        session = await self._session_manager.get_session_by_thread_id(thread_id)
        if session:
            return [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp,
                    "tool_call_id": msg.tool_call_id,
                    "tool_calls": msg.tool_calls,
                }
                for msg in session.messages
            ]
        return []


# =============================================================================
# SSE Encoding
# =============================================================================


def encode_sse_event(event: dict[str, Any]) -> str:
    """Encode an event as SSE format.

    Args:
        event: Event dict with 'type' field

    Returns:
        SSE-formatted string
    """
    event_type = event.get("type", "message")
    data = json.dumps(event)
    return f"event: {event_type}\ndata: {data}\n\n"


# =============================================================================
# FastAPI Integration
# =============================================================================


def add_agui_endpoint(
    app: FastAPI,
    agent: AGUIStreamingAgent,
    path: str = "/api/agent",
    include_state_endpoint: bool = True,
):
    """Add AG-UI streaming endpoint to FastAPI app.

    Args:
        app: FastAPI application
        agent: AGUIStreamingAgent instance
        path: API endpoint path
        include_state_endpoint: Whether to add /agents/state endpoint
    """

    @app.post(path)
    async def agui_endpoint(request: Request) -> StreamingResponse:
        """AG-UI streaming agent endpoint."""
        try:
            body = await request.json()
        except Exception:
            body = {}

        # Parse request
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
            """Generate SSE events."""
            try:
                async for event in agent.run(agui_request):
                    yield encode_sse_event(event)
            except Exception as e:
                logger.error(f"Streaming error: {e}", exc_info=True)
                error_event = {
                    "type": "RUN_ERROR",
                    "message": str(e),
                    "code": "STREAMING_ERROR",
                }
                yield encode_sse_event(error_event)

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    if include_state_endpoint:

        @app.post("/agents/state")
        async def agents_state_endpoint(request_data: AGUIStateRequest):
            """Get thread state and message history."""
            thread_id = request_data.threadId

            try:
                state = await agent.get_state(thread_id)
                messages = await agent.get_messages(thread_id)

                return {
                    "threadId": thread_id,
                    "threadExists": state is not None,
                    "state": json.dumps(state or {}),
                    "messages": json.dumps(messages),
                }
            except Exception as e:
                logger.error(f"Error in /agents/state: {e}")
                return {
                    "threadId": thread_id,
                    "threadExists": False,
                    "state": "{}",
                    "messages": "[]",
                    "error": str(e),
                }


def create_agui_app(
    agent: AGUIStreamingAgent,
    path: str = "/api/agent",
    title: str = "Oideachais AG-UI Agent",
) -> FastAPI:
    """Create a FastAPI app with AG-UI endpoint.

    Args:
        agent: AGUIStreamingAgent instance
        path: API endpoint path
        title: App title

    Returns:
        FastAPI application
    """
    app = FastAPI(title=title)
    add_agui_endpoint(app, agent, path)
    return app
