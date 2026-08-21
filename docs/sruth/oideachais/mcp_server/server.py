"""
MCP Server for Oideachas.

Provides stdio transport for curriculum search and learning path tools.
"""

import asyncio
import json
import logging
import sys
from typing import Any

from .tools import TOOL_REGISTRY, execute_tool

logger = logging.getLogger(__name__)


class MCPServer:
    """
    MCP server with stdio transport.

    Usage:
        server = MCPServer()
        await server.run()
    """

    def __init__(self):
        self.running = False

    async def handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Handle an MCP JSON-RPC request."""
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id")

        try:
            if method == "initialize":
                return self._make_response(
                    request_id,
                    {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {"listChanged": False},
                        },
                        "serverInfo": {
                            "name": "oideachas",
                            "version": "0.1.0",
                        },
                    },
                )

            elif method == "tools/list":
                tools = [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.parameters,
                    }
                    for tool in TOOL_REGISTRY.values()
                ]
                return self._make_response(request_id, {"tools": tools})

            elif method == "tools/call":
                tool_name = params.get("name", "")
                arguments = params.get("arguments", {})

                result = await execute_tool(tool_name, arguments)

                return self._make_response(
                    request_id,
                    {
                        "content": [{"type": "text", "text": json.dumps(result, default=str)}],
                    },
                )

            elif method == "notifications/initialized":
                return None

            else:
                return self._make_error(request_id, -32601, f"Method not found: {method}")

        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return self._make_error(request_id, -32000, str(e))

    def _make_response(self, request_id: Any, result: dict) -> dict[str, Any]:
        """Create a JSON-RPC success response."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result,
        }

    def _make_error(self, request_id: Any, code: int, message: str) -> dict[str, Any]:
        """Create a JSON-RPC error response."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": code, "message": message},
        }

    async def run(self):
        """Run the MCP server with stdio transport."""
        self.running = True
        logger.info("Oideachas MCP server starting (stdio)")

        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)

        loop = asyncio.get_event_loop()
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)

        while self.running:
            try:
                line = await reader.readline()
                if not line:
                    break

                request = json.loads(line.decode("utf-8"))
                response = await self.handle_request(request)

                if response is not None:
                    response_str = json.dumps(response) + "\n"
                    sys.stdout.write(response_str)
                    sys.stdout.flush()

            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
            except Exception as e:
                logger.error(f"Server error: {e}")

        logger.info("Oideachas MCP server stopped")

    def stop(self):
        """Stop the server."""
        self.running = False


def main():
    """Entry point for MCP server."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )

    server = MCPServer()

    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        server.stop()


if __name__ == "__main__":
    main()
