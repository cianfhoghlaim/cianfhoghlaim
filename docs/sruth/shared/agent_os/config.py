"""Shared configuration for AgentOS instances.

Environment variables:
- AGENT_OS_SECRET_KEY: Secret for signing service JWTs
- AGENT_OS_SERVICE_NAME: This service's name in registry
- AGENT_OS_DB_URL: PostgreSQL URL for persistence
- AGENT_OS_CACHE_URL: Redis URL for caching (optional)
"""

import os
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Optional


@dataclass
class AgentEndpoint:
    """Configuration for an agent endpoint."""

    flow: str
    agent_id: str
    base_url: str
    requires_payment: bool = False
    timeout_seconds: int = 30


@dataclass
class AgentOSConfig:
    """Shared configuration for AgentOS instances."""

    # Service identity
    service_name: str
    service_port: int

    # Authentication
    secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiry_seconds: int = 3600

    # Database
    db_url: Optional[str] = None

    # Cache (optional)
    cache_url: Optional[str] = None

    # A2A settings
    a2a_timeout_seconds: int = 30
    a2a_retry_count: int = 3
    a2a_circuit_breaker_threshold: int = 5
    a2a_circuit_breaker_timeout: int = 60

    # Agent registry (populated from environment or discovery)
    agent_endpoints: dict[str, AgentEndpoint] = field(default_factory=dict)

    @classmethod
    def from_env(cls, service_name: str, service_port: int = 7777) -> "AgentOSConfig":
        """Create config from environment variables."""
        return cls(
            service_name=service_name,
            service_port=service_port,
            secret_key=os.environ.get("AGENT_OS_SECRET_KEY", "dev-secret-change-in-production"),
            db_url=os.environ.get("AGENT_OS_DB_URL"),
            cache_url=os.environ.get("AGENT_OS_CACHE_URL"),
            a2a_timeout_seconds=int(os.environ.get("A2A_TIMEOUT_SECONDS", "30")),
            a2a_retry_count=int(os.environ.get("A2A_RETRY_COUNT", "3")),
            a2a_circuit_breaker_threshold=int(os.environ.get("A2A_CB_THRESHOLD", "5")),
            a2a_circuit_breaker_timeout=int(os.environ.get("A2A_CB_TIMEOUT", "60")),
        )


# Global config singleton
_config: Optional[AgentOSConfig] = None


def get_config() -> AgentOSConfig:
    """Get the global config singleton."""
    global _config
    if _config is None:
        raise RuntimeError("Config not initialized. Call init_config() first.")
    return _config


def init_config(service_name: str, service_port: int = 7777) -> AgentOSConfig:
    """Initialize global config from environment."""
    global _config
    _config = AgentOSConfig.from_env(service_name, service_port)
    return _config


# Default agent endpoints for the 4 flows
DEFAULT_AGENT_ENDPOINTS = {
    # Oideachais agents (port 7772)
    "curriculum": AgentEndpoint(
        flow="oideachais",
        agent_id="curriculum-agent",
        base_url=os.environ.get("OIDEACHAIS_AGENT_OS_URL", "http://localhost:7772"),
    ),
    "translation": AgentEndpoint(
        flow="oideachais",
        agent_id="translation-agent",
        base_url=os.environ.get("OIDEACHAIS_AGENT_OS_URL", "http://localhost:7772"),
    ),
    "geospatial": AgentEndpoint(
        flow="oideachais",
        agent_id="geospatial-agent",
        base_url=os.environ.get("OIDEACHAIS_AGENT_OS_URL", "http://localhost:7772"),
    ),
    # Crypteolas agents (port 7771)
    "defi_analytics": AgentEndpoint(
        flow="crypteolas",
        agent_id="defi-analytics-agent",
        base_url=os.environ.get("CRYPTEOLAS_AGENT_OS_URL", "http://localhost:7771"),
        requires_payment=True,
    ),
    "protocol_research": AgentEndpoint(
        flow="crypteolas",
        agent_id="protocol-research-agent",
        base_url=os.environ.get("CRYPTEOLAS_AGENT_OS_URL", "http://localhost:7771"),
    ),
    "code_analysis": AgentEndpoint(
        flow="crypteolas",
        agent_id="code-analysis-agent",
        base_url=os.environ.get("CRYPTEOLAS_AGENT_OS_URL", "http://localhost:7771"),
    ),
    # Browser agents (port 7773)
    "browser_orchestrator": AgentEndpoint(
        flow="browser",
        agent_id="browser-orchestrator-agent",
        base_url=os.environ.get("BROWSER_AGENT_OS_URL", "http://localhost:7773"),
    ),
    # Aleyum agents (port 7774)
    "research": AgentEndpoint(
        flow="aleyum",
        agent_id="research-agent",
        base_url=os.environ.get("ALEYUM_AGENT_OS_URL", "http://localhost:7774"),
    ),
}
