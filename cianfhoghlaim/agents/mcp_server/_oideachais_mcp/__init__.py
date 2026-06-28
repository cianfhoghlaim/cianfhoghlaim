"""
Oideachas MCP Server.

Provides curriculum search and learning path tools via MCP protocol.
"""

from .server import MCPServer, main
from .tools import TOOL_REGISTRY, execute_tool, register_tool

__all__ = [
    "TOOL_REGISTRY",
    "MCPServer",
    "execute_tool",
    "main",
    "register_tool",
]
