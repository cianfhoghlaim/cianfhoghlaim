"""Shared AgentOS infrastructure for sruth flows.

Provides:
- TinyAuth middleware for user authentication
- A2A service-to-service authentication
- A2A client for cross-flow calls
- Service discovery registry
- Circuit breaker for resilience
"""

from .config import AgentOSConfig, get_config, init_config
from .middleware import TinyAuthMiddleware, TinyAuthUser, A2AAuthMiddleware
from .a2a import A2AClient, AgentRegistry, CircuitBreaker

__all__ = [
    "AgentOSConfig",
    "get_config",
    "init_config",
    "TinyAuthMiddleware",
    "TinyAuthUser",
    "A2AAuthMiddleware",
    "A2AClient",
    "AgentRegistry",
    "CircuitBreaker",
]
