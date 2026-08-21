"""
MCP server for códeolas.

Provides JSON-RPC 2.0 server for Claude Code integration via stdio.

Observability:
- Datadog APM tracing for all RPC methods
- Metrics for tool execution latency
"""

import asyncio
import json
import logging
import os
import sys
import time
from typing import Any

from .tools import execute_tool, list_tools

logger = logging.getLogger(__name__)

# Lazy import Datadog tracer
_dd_tracer = None


def _get_tracer():
    """Lazy load Datadog tracer."""
    global _dd_tracer
    if _dd_tracer is None:
        try:
            from ddtrace import tracer, patch_all

            # Patch common libraries
            patch_all()

            # Configure service name
            tracer.set_tags({
                "service.name": "codeolas-mcp",
                "env": os.getenv("DD_ENV", "development"),
            })

            _dd_tracer = tracer
            logger.info("Datadog tracer initialized")
        except ImportError:
            logger.debug("Datadog not installed")
            return None
        except Exception as e:
            logger.warning(f"Failed to initialize Datadog: {e}")
            return None
    return _dd_tracer


class MCPServer:
    """
    Model Context Protocol server.

    Implements JSON-RPC 2.0 over stdio for Claude Code integration.
    """

    def __init__(self):
        self.running = False

    async def start(self):
        """Start the server."""
        self.running = True
        logger.info("MCP server starting")

        while self.running:
            try:
                # Read line from stdin
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )

                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                # Parse JSON-RPC request
                try:
                    request = json.loads(line)
                except json.JSONDecodeError as e:
                    await self._send_error(None, -32700, f"Parse error: {e}")
                    continue

                # Handle request
                response = await self._handle_request(request)
                await self._send_response(response)

            except Exception as e:
                logger.error(f"Server error: {e}")
                await self._send_error(None, -32603, str(e))

    async def stop(self):
        """Stop the server."""
        self.running = False

    async def _handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Handle a JSON-RPC request with Datadog tracing."""
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id")

        logger.debug(f"Handling method: {method}")

        # Start Datadog span
        tracer = _get_tracer()
        span = None
        start_time = time.time()

        if tracer:
            span = tracer.trace(
                "mcp.request",
                service="codeolas-mcp",
                resource=method,
            )
            span.set_tag("mcp.method", method)
            span.set_tag("mcp.request_id", str(request_id))

        try:
            if method == "initialize":
                result = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                    },
                    "serverInfo": {
                        "name": "codeolas",
                        "version": "0.1.0",
                    },
                }

            elif method == "notifications/initialized":
                # No response needed for notifications
                return None

            elif method == "tools/list":
                result = {"tools": list_tools()}

            elif method == "tools/call":
                tool_name = params.get("name", "")
                tool_args = params.get("arguments", {})

                # Add tool-specific tags
                if span:
                    span.set_tag("mcp.tool_name", tool_name)

                # Execute tool with nested span
                tool_start = time.time()
                tool_result = await execute_tool(tool_name, tool_args)
                tool_latency_ms = (time.time() - tool_start) * 1000

                if span:
                    span.set_tag("mcp.tool_latency_ms", tool_latency_ms)

                result = {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(tool_result, default=str),
                        }
                    ]
                }

            elif method == "resources/list":
                result = {
                    "resources": [
                        {
                            "uri": "codeolas://health",
                            "name": "Health Status",
                            "description": "Indexing health status",
                            "mimeType": "application/json",
                        },
                        {
                            "uri": "codeolas://stats",
                            "name": "Statistics",
                            "description": "Indexing statistics",
                            "mimeType": "application/json",
                        },
                    ]
                }

            elif method == "resources/read":
                uri = params.get("uri", "")
                content = await self._read_resource(uri)
                result = {"contents": [content]}

            else:
                if span:
                    span.set_tag("error", True)
                    span.set_tag("error.message", f"Unknown method: {method}")
                return self._make_error(request_id, -32601, f"Unknown method: {method}")

            # Record success metrics
            latency_ms = (time.time() - start_time) * 1000
            if span:
                span.set_tag("mcp.latency_ms", latency_ms)
                span.set_tag("mcp.success", True)
                span.finish()

            return self._make_response(request_id, result)

        except Exception as e:
            logger.error(f"Error handling {method}: {e}")

            # Record error metrics
            if span:
                span.set_tag("error", True)
                span.set_tag("error.message", str(e))
                span.set_tag("error.type", type(e).__name__)
                span.finish()

            return self._make_error(request_id, -32603, str(e))

    async def _read_resource(self, uri: str) -> dict[str, Any]:
        """Read a resource."""
        from ..storage import get_lance_catalog

        catalog = get_lance_catalog()

        if uri == "codeolas://health":
            stats = catalog.get_stats()
            return {
                "uri": uri,
                "mimeType": "application/json",
                "text": json.dumps({
                    "status": "healthy",
                    "indexed": stats.get("code_chunks", {}).get("exists", False)
                }),
            }

        elif uri == "codeolas://stats":
            stats = catalog.get_stats()
            return {
                "uri": uri,
                "mimeType": "application/json",
                "text": json.dumps(stats, default=str),
            }

        else:
            return {
                "uri": uri,
                "mimeType": "text/plain",
                "text": f"Unknown resource: {uri}",
            }

    def _make_response(self, request_id: Any, result: Any) -> dict[str, Any]:
        """Make a JSON-RPC response."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result,
        }

    def _make_error(
        self,
        request_id: Any,
        code: int,
        message: str,
    ) -> dict[str, Any]:
        """Make a JSON-RPC error response."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message,
            },
        }

    async def _send_response(self, response: dict[str, Any] | None):
        """Send response to stdout."""
        if response is None:
            return

        output = json.dumps(response)
        sys.stdout.write(output + "\n")
        sys.stdout.flush()

    async def _send_error(self, request_id: Any, code: int, message: str):
        """Send error response."""
        response = self._make_error(request_id, code, message)
        await self._send_response(response)


async def _main():
    """Main entry point for MCP server."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )

    server = MCPServer()
    await server.start()


def main():
    """CLI entry point."""
    asyncio.run(_main())


if __name__ == "__main__":
    main()
