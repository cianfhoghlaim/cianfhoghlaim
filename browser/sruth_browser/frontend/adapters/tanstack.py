"""TanStack AI SSE adapter.

Converts agent events to TanStack AI SDK format.
https://tanstack.com/start/latest/docs/framework/react/ai
"""

import json
from collections.abc import AsyncIterator
from typing import Any

from ..event_bus import AgentEvent, EventType


class TanStackAdapter:
    """Adapter for TanStack AI SSE protocol.

    TanStack AI expects SSE events in a specific format:
    - data: prefix for each line
    - JSON payload with type and content
    """

    @staticmethod
    def format_event(event: AgentEvent) -> str:
        """Format an agent event as TanStack AI SSE."""
        if event.type == EventType.TEXT_DELTA:
            # Stream text chunks
            payload = {
                "type": "text",
                "content": event.text or "",
            }
        elif event.type == EventType.TEXT_COMPLETE:
            # Complete text
            payload = {
                "type": "text",
                "content": event.text or "",
                "done": True,
            }
        elif event.type == EventType.TOOL_CALL_START:
            payload = {
                "type": "tool_call",
                "toolName": event.tool_name,
                "toolCallId": event.tool_call_id,
            }
        elif event.type == EventType.TOOL_RESULT:
            payload = {
                "type": "tool_result",
                "toolCallId": event.tool_call_id,
                "result": event.tool_result,
            }
        elif event.type == EventType.RUN_FINISHED:
            payload = {
                "type": "done",
                "result": event.raw_data,
            }
        elif event.type == EventType.RUN_ERROR:
            payload = {
                "type": "error",
                "error": event.error,
            }
        else:
            # Generic event
            payload = {
                "type": event.type.value,
                "data": event.model_dump(exclude_none=True),
            }

        return f"data: {json.dumps(payload)}\n\n"

    @staticmethod
    async def stream_response(
        events: AsyncIterator[AgentEvent],
    ) -> AsyncIterator[str]:
        """Stream events as SSE responses."""
        async for event in events:
            yield TanStackAdapter.format_event(event)

    @staticmethod
    def parse_request(data: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """Parse TanStack AI request format.

        Returns:
            Tuple of (message, context)
        """
        messages = data.get("messages", [])
        if messages:
            # Get last user message
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    return msg.get("content", ""), data.get("context", {})

        return data.get("message", ""), data.get("context", {})
