"""
MCP (Model Context Protocol) server for Crypteolas.

Exposes GitHub intelligence, DeFi analytics, and code search
capabilities to LLM clients.

Run with: python -m crypteolas.agents.mcp_server
"""

from .server import create_mcp_server, run_server

__all__ = [
    "create_mcp_server",
    "run_server",
]
