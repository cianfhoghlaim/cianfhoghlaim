"""Sruth Shared - Common utilities for data flows.

Provides shared infrastructure for AgentOS instances:
- TinyAuth middleware for user authentication
- A2A middleware for service-to-service auth
- A2A client for cross-flow communication
- Circuit breaker for resilience
"""

from .agent_os import (
    TinyAuthMiddleware,
    A2AAuthMiddleware,
    A2AClient,
    AgentRegistry,
    CircuitBreaker,
    AgentOSConfig,
    get_config,
    init_config,
)
from .agent_os.middleware.tinyauth import TinyAuthUser

__all__ = [
    "TinyAuthMiddleware",
    "TinyAuthUser",
    "A2AAuthMiddleware",
    "A2AClient",
    "AgentRegistry",
    "CircuitBreaker",
    "AgentOSConfig",
    "get_config",
    "init_config",
]
