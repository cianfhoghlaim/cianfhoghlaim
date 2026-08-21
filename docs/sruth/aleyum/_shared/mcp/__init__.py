"""
MCP (Model Context Protocol) utilities for Aleyum.

Provides a unified MCP gateway that routes through LiteLLM for
centralized access to 25+ MCP servers with fallback chains.
"""

from .gateway import (
    MCPGateway,
    MCPToolCall,
    MCPToolResult,
    MCPServerInfo,
    MCP_SERVERS,
    TOOL_FALLBACK_CHAINS,
    call_mcp_tool,
)

__all__ = [
    "MCPGateway",
    "MCPToolCall",
    "MCPToolResult",
    "MCPServerInfo",
    "MCP_SERVERS",
    "TOOL_FALLBACK_CHAINS",
    "call_mcp_tool",
]
