"""A2A (Agent-to-Agent) protocol support for cross-flow communication."""

from .client import A2AClient, A2AMessage, A2AResponse
from .discovery import AgentRegistry, AgentEndpoint
from .circuit_breaker import CircuitBreaker, CircuitBreakerOpen

__all__ = [
    "A2AClient",
    "A2AMessage",
    "A2AResponse",
    "AgentRegistry",
    "AgentEndpoint",
    "CircuitBreaker",
    "CircuitBreakerOpen",
]
