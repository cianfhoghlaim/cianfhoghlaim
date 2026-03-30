"""MCP-UI JSON-RPC adapter.

Converts agent events to MCP-UI format with resources.
https://www.mcp.run/docs/ui
"""

import json
from typing import Any

from ..event_bus import AgentEvent, EventType


class MCPUIAdapter:
    """Adapter for MCP-UI JSON-RPC protocol.

    MCP-UI uses:
    - JSON-RPC 2.0 for requests
    - Resources for UI components
    - Tools for actions
    """

    @staticmethod
    def format_response(
        result: Any,
        request_id: str | int,
    ) -> dict[str, Any]:
        """Format a JSON-RPC response."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result,
        }

    @staticmethod
    def format_error(
        error: str,
        code: int,
        request_id: str | int | None,
    ) -> dict[str, Any]:
        """Format a JSON-RPC error."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": error,
            },
        }

    @staticmethod
    def event_to_resource(event: AgentEvent) -> dict[str, Any] | None:
        """Convert an agent event to an MCP-UI resource."""
        if event.type == EventType.TEXT_COMPLETE:
            return {
                "uri": f"browser://response/{event.run_id}",
                "name": "Agent Response",
                "mimeType": "text/plain",
                "text": event.text,
            }

        if event.type == EventType.TOOL_RESULT:
            return {
                "uri": f"browser://tool/{event.tool_call_id}",
                "name": f"Tool Result: {event.tool_name or 'unknown'}",
                "mimeType": "application/json",
                "text": json.dumps(event.tool_result),
            }

        if event.type == EventType.UI_RESOURCE:
            return {
                "uri": event.resource_uri or f"browser://resource/{event.id}",
                "name": "UI Resource",
                "mimeType": "application/json",
                "text": json.dumps(event.resource_content),
            }

        return None

    @staticmethod
    def parse_request(data: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
        """Parse MCP-UI JSON-RPC request.

        Returns:
            Tuple of (method, message/params, request_id)
        """
        method = data.get("method", "")
        params = data.get("params", {})
        request_id = data.get("id", "")

        if method == "tools/call":
            tool_name = params.get("name", "")
            tool_args = params.get("arguments", {})
            return tool_name, tool_args, request_id

        if method == "chat":
            message = params.get("message", "")
            return "chat", message, request_id

        return method, params, request_id

    @staticmethod
    def list_tools() -> list[dict[str, Any]]:
        """List available MCP tools."""
        return [
            {
                "name": "browser_extract",
                "description": "Extract content from a web page",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to extract from"},
                        "formats": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Output formats (markdown, html, links)",
                        },
                    },
                    "required": ["url"],
                },
            },
            {
                "name": "browser_navigate",
                "description": "Navigate to a URL",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to navigate to"},
                    },
                    "required": ["url"],
                },
            },
            {
                "name": "browser_screenshot",
                "description": "Capture a screenshot",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to screenshot"},
                        "fullPage": {"type": "boolean", "description": "Capture full page"},
                    },
                    "required": ["url"],
                },
            },
            {
                "name": "browser_research",
                "description": "Research a topic across multiple sources",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "Research topic"},
                        "maxSources": {"type": "integer", "description": "Max sources"},
                    },
                    "required": ["topic"],
                },
            },
        ]

    @staticmethod
    def list_resources() -> list[dict[str, Any]]:
        """List available MCP resources."""
        return [
            {
                "uri": "browser://health",
                "name": "Backend Health",
                "description": "Health status of all browser backends",
                "mimeType": "application/json",
            },
            {
                "uri": "browser://history",
                "name": "Event History",
                "description": "Recent agent event history",
                "mimeType": "application/json",
            },
        ]
