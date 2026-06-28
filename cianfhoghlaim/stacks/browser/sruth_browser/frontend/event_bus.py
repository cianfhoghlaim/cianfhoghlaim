"""Protocol-agnostic event bus for frontend adapters."""

import asyncio
from collections.abc import AsyncIterator
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Event types for agent communication."""

    # Lifecycle events
    RUN_STARTED = "run_started"
    RUN_FINISHED = "run_finished"
    RUN_ERROR = "run_error"

    # Text streaming
    TEXT_DELTA = "text_delta"
    TEXT_COMPLETE = "text_complete"

    # Tool calling
    TOOL_CALL_START = "tool_call_start"
    TOOL_CALL_ARGS = "tool_call_args"
    TOOL_CALL_END = "tool_call_end"
    TOOL_RESULT = "tool_result"

    # State management
    STATE_UPDATE = "state_update"
    STATE_SNAPSHOT = "state_snapshot"

    # UI resources (MCP-UI)
    UI_RESOURCE = "ui_resource"

    # Raw for protocol-specific
    RAW = "raw"


class AgentEvent(BaseModel):
    """Protocol-agnostic agent event."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Content varies by event type
    run_id: str | None = None
    thread_id: str | None = None

    # Text content
    text: str | None = None
    is_complete: bool = False

    # Tool call data
    tool_name: str | None = None
    tool_call_id: str | None = None
    tool_args: dict[str, Any] | None = None
    tool_result: Any | None = None

    # State data
    state_key: str | None = None
    state_value: Any | None = None

    # Error data
    error: str | None = None
    error_code: str | None = None

    # UI resource data
    resource_uri: str | None = None
    resource_content: Any | None = None

    # Raw data for protocol-specific events
    raw_data: Any | None = None


class EventBus:
    """Pub/sub event bus for agent events."""

    def __init__(self):
        self._subscribers: list[asyncio.Queue[AgentEvent]] = []
        self._history: list[AgentEvent] = []
        self._max_history = 1000

    async def publish(self, event: AgentEvent) -> None:
        """Publish an event to all subscribers."""
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        for queue in self._subscribers:
            await queue.put(event)

    def subscribe(self) -> asyncio.Queue[AgentEvent]:
        """Subscribe to events. Returns a queue to receive events."""
        queue: asyncio.Queue[AgentEvent] = asyncio.Queue()
        self._subscribers.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[AgentEvent]) -> None:
        """Unsubscribe from events."""
        if queue in self._subscribers:
            self._subscribers.remove(queue)

    async def stream(self, run_id: str | None = None) -> AsyncIterator[AgentEvent]:
        """Stream events, optionally filtered by run_id."""
        queue = self.subscribe()
        try:
            while True:
                event = await queue.get()
                if run_id is None or event.run_id == run_id:
                    yield event
                    if event.type in (EventType.RUN_FINISHED, EventType.RUN_ERROR):
                        break
        finally:
            self.unsubscribe(queue)

    def get_history(
        self,
        run_id: str | None = None,
        event_types: list[EventType] | None = None,
    ) -> list[AgentEvent]:
        """Get event history, optionally filtered."""
        events = self._history

        if run_id:
            events = [e for e in events if e.run_id == run_id]

        if event_types:
            events = [e for e in events if e.type in event_types]

        return events

    # Convenience methods for common events
    async def emit_run_started(
        self,
        run_id: str,
        thread_id: str | None = None,
    ) -> None:
        """Emit run started event."""
        await self.publish(
            AgentEvent(
                type=EventType.RUN_STARTED,
                run_id=run_id,
                thread_id=thread_id,
            )
        )

    async def emit_text_delta(
        self,
        run_id: str,
        text: str,
    ) -> None:
        """Emit text delta event."""
        await self.publish(
            AgentEvent(
                type=EventType.TEXT_DELTA,
                run_id=run_id,
                text=text,
            )
        )

    async def emit_text_complete(
        self,
        run_id: str,
        text: str,
    ) -> None:
        """Emit text complete event."""
        await self.publish(
            AgentEvent(
                type=EventType.TEXT_COMPLETE,
                run_id=run_id,
                text=text,
                is_complete=True,
            )
        )

    async def emit_tool_call_start(
        self,
        run_id: str,
        tool_name: str,
        tool_call_id: str,
    ) -> None:
        """Emit tool call start event."""
        await self.publish(
            AgentEvent(
                type=EventType.TOOL_CALL_START,
                run_id=run_id,
                tool_name=tool_name,
                tool_call_id=tool_call_id,
            )
        )

    async def emit_tool_result(
        self,
        run_id: str,
        tool_call_id: str,
        result: Any,
    ) -> None:
        """Emit tool result event."""
        await self.publish(
            AgentEvent(
                type=EventType.TOOL_RESULT,
                run_id=run_id,
                tool_call_id=tool_call_id,
                tool_result=result,
            )
        )

    async def emit_run_finished(
        self,
        run_id: str,
        result: Any = None,
    ) -> None:
        """Emit run finished event."""
        await self.publish(
            AgentEvent(
                type=EventType.RUN_FINISHED,
                run_id=run_id,
                raw_data=result,
            )
        )

    async def emit_error(
        self,
        run_id: str,
        error: str,
        error_code: str | None = None,
    ) -> None:
        """Emit error event."""
        await self.publish(
            AgentEvent(
                type=EventType.RUN_ERROR,
                run_id=run_id,
                error=error,
                error_code=error_code,
            )
        )
