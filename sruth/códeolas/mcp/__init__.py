"""MCP server for códeolas.

Provides JSON-RPC 2.0 server for Claude Code integration.
"""

from .server import MCPServer, main
from .tools import (
    SearchResponse,
    SearchResult,
    StatsResponse,
    execute_tool,
    list_tools,
    register_tool,
)

__all__ = [
    # Server
    "MCPServer",
    "main",
    # Tools
    "SearchResult",
    "SearchResponse",
    "StatsResponse",
    "register_tool",
    "list_tools",
    "execute_tool",
]
