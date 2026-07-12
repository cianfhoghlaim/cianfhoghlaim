"""Entry point for running Tuath MCP server."""

import asyncio

from .server import run_server

if __name__ == "__main__":
    asyncio.run(run_server())
