"""
Aleyum Shared Utilities - Agentic Developer Hub.

This package contains shared utilities for the aleyum developer hub,
including database access, embeddings, MCP gateway, agent orchestration,
and observability.

Re-exports common utilities from sruth.shared and adds aleyum-specific
functionality for the merged códeolas and browser components.
"""

# Re-export from sruth.shared for convenience
from sruth.shared import (
    SerialDatabaseExecutor,
    get_executor,
    run_serial,
    CircuitBreaker,
    RateLimiter,
    retry_with_backoff,
)

# Aleyum-specific exports will be added as modules are created
# from .mcp import MCPGateway
# from .agents import AgentRouter, select_framework
# from .observability import AleyumTracer

__all__ = [
    # From sruth.shared
    "SerialDatabaseExecutor",
    "get_executor",
    "run_serial",
    "CircuitBreaker",
    "RateLimiter",
    "retry_with_backoff",
]
