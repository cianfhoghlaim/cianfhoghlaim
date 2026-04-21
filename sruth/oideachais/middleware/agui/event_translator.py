"""
AG-UI Event Translator.

Converts internal agent events to AG-UI protocol events for SSE streaming.
Supports all 17 AG-UI event types as defined in the protocol specification.
"""

from __future__ import annotations

import json
import logging
import uuid
from collections.abc import AsyncGenerator
from dataclasses import asdict, dataclass
from typing import Any

from api.ag_ui_protocol import (
    AGUIEventEmitter,
    AGUIEventType,
    RawEvent,
)

logger = logging.getLogger(__name__)


@dataclass
class AgentEvent:
    """Internal agent event representation."""

    type: str
    data: dict[str, Any] | None = None

    # Text events
    content: str | None = None
    delta: str | None = None
    message_id: str | None = None

    # Tool events
    tool_call_id: str | None = None
    tool_name: str | None = None
    tool_args: dict[str, Any] | str | None = None
    tool_result: Any | None = None
    is_error: bool = False

    # State events
    state: dict[str, Any] | None = None
    state_delta: dict[str, Any] | None = None


class EventTranslator:
    """Translates internal agent events to AG-UI protocol events.

    Maintains streaming state for proper message boundaries and ensures
    all events are emitted in the correct sequence.

    Usage:
        translator = EventTranslator(thread_id, run_id)
        async for event in translator.translate(agent_event):
            yield encode_sse(event)
    """

    def __init__(
        self,
        thread_id: str | None = None,
        run_id: str | None = None,
    ):
        self.thread_id = thread_id or str(uuid.uuid4())
        self.run_id = run_id or str(uuid.uuid4())

        # Streaming state
        self._current_message_id: str | None = None
        self._message_content = ""
        self._is_streaming_text = False

        # Tool tracking
        self._active_tool_calls: dict[str, dict] = {}

        # State tracking
        self._last_state: dict[str, Any] = {}

        self._emitter = AGUIEventEmitter()

    async def translate(
        self,
        event: AgentEvent,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Translate an agent event to AG-UI events.

        Args:
            event: Internal agent event

        Yields:
            AG-UI protocol events as dicts ready for SSE encoding
        """
        event_type = event.type.upper()

        if event_type == "RUN_STARTED":
            yield self._create_run_started()

        elif event_type == "RUN_FINISHED":
            # Close any open text message first
            async for close_event in self._close_text_message():
                yield close_event
            yield self._create_run_finished()

        elif event_type == "RUN_ERROR":
            async for close_event in self._close_text_message():
                yield close_event
            yield self._create_run_error(
                message=event.content or "An error occurred",
                code=event.data.get("code") if event.data else None
            )

        elif event_type == "TEXT_START":
            yield self._create_text_message_start()

        elif event_type == "TEXT_DELTA" or event_type == "TEXT_CONTENT":
            delta = event.delta or event.content or ""
            if delta:
                yield self._create_text_message_content(delta)

        elif event_type == "TEXT_END":
            async for close_event in self._close_text_message():
                yield close_event

        elif event_type == "TOOL_CALL_START":
            # Close text message before tool call
            async for close_event in self._close_text_message():
                yield close_event
            yield self._create_tool_call_start(
                tool_call_id=event.tool_call_id or str(uuid.uuid4()),
                name=event.tool_name or "unknown_tool"
            )

        elif event_type == "TOOL_CALL_ARGS":
            args = event.tool_args
            if isinstance(args, dict):
                args = json.dumps(args)
            yield self._create_tool_call_args(
                tool_call_id=event.tool_call_id or "",
                args=args or ""
            )

        elif event_type == "TOOL_CALL_END":
            yield self._create_tool_call_end(
                tool_call_id=event.tool_call_id or ""
            )

        elif event_type == "TOOL_RESULT":
            yield self._create_tool_result(
                tool_call_id=event.tool_call_id or "",
                result=event.tool_result,
                is_error=event.is_error
            )

        elif event_type == "STATE_SNAPSHOT":
            if event.state:
                yield self._create_state_snapshot(event.state)

        elif event_type == "STATE_DELTA":
            if event.state_delta:
                yield self._create_state_delta(event.state_delta)

        elif event_type == "RAW":
            yield self._create_raw_event(event.data or {})

        else:
            logger.warning(f"Unknown event type: {event_type}")

    async def _close_text_message(self) -> AsyncGenerator[dict[str, Any], None]:
        """Close the current text message if open."""
        if self._is_streaming_text and self._current_message_id:
            yield self._create_text_message_end()
            self._is_streaming_text = False
            self._current_message_id = None
            self._message_content = ""

    # Event creation methods

    def _create_run_started(self) -> dict[str, Any]:
        """Create RUN_STARTED event."""
        event = self._emitter.run_started(
            run_id=self.run_id,
            thread_id=self.thread_id
        )
        return self._event_to_dict(event)

    def _create_run_finished(self) -> dict[str, Any]:
        """Create RUN_FINISHED event."""
        event = self._emitter.run_finished(
            run_id=self.run_id,
            thread_id=self.thread_id
        )
        return self._event_to_dict(event)

    def _create_run_error(
        self,
        message: str,
        code: str | None = None
    ) -> dict[str, Any]:
        """Create RUN_ERROR event."""
        event = self._emitter.run_error(
            message=message,
            code=code
        )
        return self._event_to_dict(event)

    def _create_text_message_start(self) -> dict[str, Any]:
        """Create TEXT_MESSAGE_START event."""
        self._current_message_id = str(uuid.uuid4())
        self._is_streaming_text = True
        self._message_content = ""

        event = self._emitter.text_message_start(
            message_id=self._current_message_id,
            role="assistant"
        )
        return self._event_to_dict(event)

    def _create_text_message_content(self, delta: str) -> dict[str, Any]:
        """Create TEXT_MESSAGE_CONTENT event."""
        # Auto-start message if not already streaming
        if not self._is_streaming_text:
            self._current_message_id = str(uuid.uuid4())
            self._is_streaming_text = True
            self._message_content = ""

        self._message_content += delta

        event = self._emitter.text_message_content(
            message_id=self._current_message_id,
            delta=delta
        )
        return self._event_to_dict(event)

    def _create_text_message_end(self) -> dict[str, Any]:
        """Create TEXT_MESSAGE_END event."""
        event = self._emitter.text_message_end(
            message_id=self._current_message_id or str(uuid.uuid4())
        )
        return self._event_to_dict(event)

    def _create_tool_call_start(
        self,
        tool_call_id: str,
        name: str
    ) -> dict[str, Any]:
        """Create TOOL_CALL_START event."""
        self._active_tool_calls[tool_call_id] = {
            "name": name,
            "args": "",
        }

        event = self._emitter.tool_call_start(
            tool_call_id=tool_call_id,
            name=name
        )
        return self._event_to_dict(event)

    def _create_tool_call_args(
        self,
        tool_call_id: str,
        args: str
    ) -> dict[str, Any]:
        """Create TOOL_CALL_ARGS event."""
        if tool_call_id in self._active_tool_calls:
            self._active_tool_calls[tool_call_id]["args"] += args

        event = self._emitter.tool_call_args(
            tool_call_id=tool_call_id,
            delta=args
        )
        return self._event_to_dict(event)

    def _create_tool_call_end(self, tool_call_id: str) -> dict[str, Any]:
        """Create TOOL_CALL_END event."""
        tool_info = self._active_tool_calls.get(tool_call_id, {})

        event = self._emitter.tool_call_end(
            tool_call_id=tool_call_id,
            name=tool_info.get("name", "unknown")
        )
        return self._event_to_dict(event)

    def _create_tool_result(
        self,
        tool_call_id: str,
        result: Any,
        is_error: bool = False
    ) -> dict[str, Any]:
        """Create TOOL_CALL_RESULT event."""
        # Remove from active tracking
        self._active_tool_calls.pop(tool_call_id, None)

        event = self._emitter.tool_result(
            tool_call_id=tool_call_id,
            result=result,
            is_error=is_error
        )
        return self._event_to_dict(event)

    def _create_state_snapshot(self, state: dict[str, Any]) -> dict[str, Any]:
        """Create STATE_SNAPSHOT event."""
        self._last_state = state.copy()

        event = self._emitter.state_snapshot(snapshot=state)
        return self._event_to_dict(event)

    def _create_state_delta(self, delta: dict[str, Any]) -> dict[str, Any]:
        """Create STATE_DELTA event."""
        # Update tracked state
        self._last_state.update(delta)

        event = self._emitter.state_delta(delta=delta)
        return self._event_to_dict(event)

    def _create_raw_event(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create RAW event for custom data."""
        event = RawEvent(
            type=AGUIEventType.RAW,
            data=data
        )
        return self._event_to_dict(event)

    def _event_to_dict(self, event) -> dict[str, Any]:
        """Convert an event dataclass to a dict."""
        if hasattr(event, "__dict__"):
            result = {}
            for key, value in event.__dict__.items():
                if value is not None:
                    if hasattr(value, "value"):  # Enum
                        result[key] = value.value
                    else:
                        result[key] = value
            return result
        return asdict(event)


async def translate_agent_events(
    events: AsyncGenerator[AgentEvent, None],
    thread_id: str | None = None,
    run_id: str | None = None,
) -> AsyncGenerator[dict[str, Any], None]:
    """Translate a stream of agent events to AG-UI events.

    Args:
        events: Async generator of internal agent events
        thread_id: AG-UI thread ID
        run_id: AG-UI run ID

    Yields:
        AG-UI protocol events as dicts
    """
    translator = EventTranslator(thread_id, run_id)

    async for event in events:
        async for ag_ui_event in translator.translate(event):
            yield ag_ui_event
