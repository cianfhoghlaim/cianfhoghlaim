"""
MCP (Model Context Protocol) server for Tuath Celtic Education.

Exposes curriculum, mythology, and FIBO generation capabilities to LLM clients.

Run with: python -m tuath.agents.mcp_server
"""

from .server import create_mcp_server, run_server

__all__ = [
    "create_mcp_server",
    "run_server",
]
