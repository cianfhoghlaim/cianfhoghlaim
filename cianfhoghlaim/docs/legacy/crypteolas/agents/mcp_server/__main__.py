"""Entry point for running Crypteolas MCP server."""

import asyncio
from .server import run_server

if __name__ == "__main__":
    asyncio.run(run_server())
