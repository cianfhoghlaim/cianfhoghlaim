"""MCP server implementation for browser agent."""

import asyncio
import json
import sys
from typing import Any

import structlog

from .tools import BROWSER_TOOLS, execute_tool

logger = structlog.get_logger()


class MCPServer:
    """MCP server exposing browser agent tools."""

    def __init__(self):
        self.name = "browser-agent"
        self.version = "0.1.0"

    async def handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Handle an MCP JSON-RPC request."""
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id")

        try:
            if method == "initialize":
                return self._response(
                    {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {},
                        },
                        "serverInfo": {
                            "name": self.name,
                            "version": self.version,
                        },
                    },
                    request_id,
                )

            elif method == "notifications/initialized":
                return self._response({}, request_id)

            elif method == "tools/list":
                return self._response({"tools": BROWSER_TOOLS}, request_id)

            elif method == "tools/call":
                tool_name = params.get("name", "")
                tool_args = params.get("arguments", {})

                result = await execute_tool(tool_name, tool_args)

                return self._response(
                    {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, default=str),
                            }
                        ],
                    },
                    request_id,
                )

            else:
                return self._error(f"Unknown method: {method}", -32601, request_id)

        except Exception as e:
            logger.error("mcp_request_error", method=method, error=str(e))
            return self._error(str(e), -32603, request_id)

    def _response(self, result: Any, request_id: Any) -> dict[str, Any]:
        """Format a successful response."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result,
        }

    def _error(self, message: str, code: int, request_id: Any) -> dict[str, Any]:
        """Format an error response."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message,
            },
        }

    async def run_stdio(self):
        """Run the MCP server over stdio."""
        logger.info("starting_mcp_server", name=self.name)

        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)

        writer_transport, writer_protocol = await asyncio.get_event_loop().connect_write_pipe(
            asyncio.streams.FlowControlMixin, sys.stdout
        )
        writer = asyncio.StreamWriter(writer_transport, writer_protocol, None, asyncio.get_event_loop())

        while True:
            try:
                line = await reader.readline()
                if not line:
                    break

                request = json.loads(line.decode())
                response = await self.handle_request(request)

                writer.write((json.dumps(response) + "\n").encode())
                await writer.drain()

            except json.JSONDecodeError:
                continue
            except Exception as e:
                logger.error("mcp_server_error", error=str(e))


def create_mcp_server() -> MCPServer:
    """Create an MCP server instance."""
    return MCPServer()


async def main():
    """Run the MCP server."""
    # Initialize backends
    from ..backends.router import get_router
    from ..backends.selfhosted import CDPBackend, Crawl4AIBackend
    from ..core.config import get_config

    config = get_config()
    router = get_router()

    # Try to initialize available backends
    try:
        crawl4ai = Crawl4AIBackend(config)
        await crawl4ai.initialize()
        router.register_backend(crawl4ai)
    except Exception:
        pass

    try:
        cdp = CDPBackend(config)
        await cdp.initialize()
        router.register_backend(cdp)
    except Exception:
        pass

    # Run server
    server = create_mcp_server()
    await server.run_stdio()


if __name__ == "__main__":
    asyncio.run(main())
