"""AG-UI (CopilotKit) adapter.

Converts agent events to AG-UI 17-event protocol.
https://docs.copilotkit.ai/coagents/ag-ui
"""

import json
from collections.abc import AsyncIterator
from typing import Any

from ..event_bus import AgentEvent, EventType


class AGUIAdapter:
    """Adapter for AG-UI 17-event SSE protocol.

    AG-UI defines 17 standard event types for agent UI:
    - Lifecycle: RUN_STARTED, RUN_FINISHED, RUN_ERROR
    - Steps: STEP_STARTED, STEP_FINISHED
    - Text: TEXT_MESSAGE_START, TEXT_MESSAGE_CONTENT, TEXT_MESSAGE_END
    - Tool: TOOL_CALL_START, TOOL_CALL_ARGS, TOOL_CALL_END, TOOL_CALL_RESULT
    - State: STATE_SNAPSHOT, STATE_DELTA
    - Custom: RAW, CUSTOM
    """

    # Map internal events to AG-UI events
    EVENT_MAP = {
        EventType.RUN_STARTED: "RUN_STARTED",
        EventType.RUN_FINISHED: "RUN_FINISHED",
        EventType.RUN_ERROR: "RUN_ERROR",
        EventType.TEXT_DELTA: "TEXT_MESSAGE_CONTENT",
        EventType.TEXT_COMPLETE: "TEXT_MESSAGE_END",
        EventType.TOOL_CALL_START: "TOOL_CALL_START",
        EventType.TOOL_CALL_ARGS: "TOOL_CALL_ARGS",
        EventType.TOOL_CALL_END: "TOOL_CALL_END",
        EventType.TOOL_RESULT: "TOOL_CALL_RESULT",
        EventType.STATE_UPDATE: "STATE_DELTA",
        EventType.STATE_SNAPSHOT: "STATE_SNAPSHOT",
    }

    @staticmethod
    def format_event(event: AgentEvent) -> str:
        """Format an agent event as AG-UI SSE."""
        agui_type = AGUIAdapter.EVENT_MAP.get(event.type, "CUSTOM")

        payload: dict[str, Any] = {
            "type": agui_type,
            "timestamp": event.timestamp.isoformat(),
        }

        if event.run_id:
            payload["runId"] = event.run_id

        if event.thread_id:
            payload["threadId"] = event.thread_id

        # Event-specific data
        if agui_type == "RUN_STARTED":
            payload["metadata"] = {}

        elif agui_type == "RUN_FINISHED":
            payload["result"] = event.raw_data

        elif agui_type == "RUN_ERROR":
            payload["error"] = {
                "message": event.error,
                "code": event.error_code or "UNKNOWN",
            }

        elif agui_type == "TEXT_MESSAGE_CONTENT":
            payload["messageId"] = event.id
            payload["delta"] = event.text or ""

        elif agui_type == "TEXT_MESSAGE_END":
            payload["messageId"] = event.id
            payload["content"] = event.text or ""

        elif agui_type == "TOOL_CALL_START":
            payload["toolCallId"] = event.tool_call_id
            payload["toolName"] = event.tool_name

        elif agui_type == "TOOL_CALL_ARGS":
            payload["toolCallId"] = event.tool_call_id
            payload["args"] = event.tool_args

        elif agui_type == "TOOL_CALL_END":
            payload["toolCallId"] = event.tool_call_id

        elif agui_type == "TOOL_CALL_RESULT":
            payload["toolCallId"] = event.tool_call_id
            payload["result"] = event.tool_result

        elif agui_type == "STATE_DELTA":
            payload["delta"] = [{
                "op": "replace",
                "path": f"/{event.state_key}",
                "value": event.state_value,
            }]

        elif agui_type == "STATE_SNAPSHOT":
            payload["snapshot"] = event.raw_data

        elif agui_type == "CUSTOM":
            payload["name"] = event.type.value
            payload["data"] = event.model_dump(exclude_none=True)

        return f"data: {json.dumps(payload)}\n\n"

    @staticmethod
    async def stream_response(
        events: AsyncIterator[AgentEvent],
    ) -> AsyncIterator[str]:
        """Stream events as AG-UI SSE responses."""
        # Start with TEXT_MESSAGE_START for first text
        text_started = False

        async for event in events:
            # Inject TEXT_MESSAGE_START before first text
            if event.type == EventType.TEXT_DELTA and not text_started:
                start_payload = {
                    "type": "TEXT_MESSAGE_START",
                    "messageId": event.id,
                    "role": "assistant",
                }
                yield f"data: {json.dumps(start_payload)}\n\n"
                text_started = True

            yield AGUIAdapter.format_event(event)

    @staticmethod
    def parse_request(data: dict[str, Any]) -> tuple[str, str | None, dict[str, Any]]:
        """Parse AG-UI request format.

        Returns:
            Tuple of (message, thread_id, context)
        """
        messages = data.get("messages", [])
        thread_id = data.get("threadId")
        context = data.get("context", {})

        # Get last user message
        message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                # Handle different content formats
                content = msg.get("content", "")
                if isinstance(content, str):
                    message = content
                elif isinstance(content, list):
                    # Multi-part content
                    for part in content:
                        if part.get("type") == "text":
                            message = part.get("text", "")
                            break
                break

        return message, thread_id, context

    @staticmethod
    def format_capabilities() -> dict[str, Any]:
        """Return AG-UI capabilities object."""
        return {
            "streaming": True,
            "tools": True,
            "state": True,
            "interrupts": False,  # Not supported yet
            "multimodal": False,  # Not supported yet
        }
