"""Service discovery for A2A agent registry.

Provides a registry of known agents across all flows, enabling:
- Lookup agents by name or capability
- Get agent cards from remote services
- Dynamic discovery via well-known endpoints
"""

import asyncio
from dataclasses import dataclass, field
from typing import Optional

import httpx
import structlog

logger = structlog.get_logger()


@dataclass
class AgentEndpoint:
    """Configuration for an agent endpoint."""

    flow: str
    agent_id: str
    base_url: str
    requires_payment: bool = False
    timeout_seconds: int = 30
    description: Optional[str] = None
    capabilities: list[str] = field(default_factory=list)

    @property
    def agent_card_url(self) -> str:
        """URL for agent card discovery."""
        return f"{self.base_url}/a2a/agents/{self.agent_id}/.well-known/agent-card.json"

    @property
    def message_stream_url(self) -> str:
        """URL for streaming message endpoint."""
        return f"{self.base_url}/a2a/agents/{self.agent_id}/v1/message:stream"

    @property
    def message_send_url(self) -> str:
        """URL for blocking message endpoint."""
        return f"{self.base_url}/a2a/agents/{self.agent_id}/v1/message:send"


@dataclass
class AgentCard:
    """A2A Agent Card describing an agent's capabilities.

    Based on the A2A protocol specification:
    https://a2a-protocol.org/v0.3.0/topics/agent-discovery/#1-well-known-uri
    """

    id: str
    name: str
    description: str
    provider: str
    version: str = "1.0.0"
    capabilities: list[str] = field(default_factory=list)
    supported_formats: list[str] = field(default_factory=lambda: ["text/plain"])
    metadata: dict = field(default_factory=dict)


class AgentRegistry:
    """Registry of known agents across all flows.

    Provides lookup, caching, and dynamic discovery for A2A communication.

    Usage:
        registry = AgentRegistry()

        # Add static agents
        registry.register(AgentEndpoint(
            flow="oideachais",
            agent_id="curriculum-agent",
            base_url="http://localhost:7772",
        ))

        # Lookup and use
        agent = registry.get("curriculum")
        if agent:
            response = await client.send_message(agent, message)
    """

    def __init__(self, agents: Optional[list[AgentEndpoint]] = None):
        """Initialize registry with optional initial agents.

        Args:
            agents: Initial list of known agents
        """
        self._agents: dict[str, AgentEndpoint] = {}
        self._agent_cards: dict[str, AgentCard] = {}
        self._lock = asyncio.Lock()

        if agents:
            for agent in agents:
                self.register(agent)

    def register(self, agent: AgentEndpoint) -> None:
        """Register an agent endpoint.

        Args:
            agent: Agent endpoint configuration
        """
        # Register by full ID and short name
        self._agents[agent.agent_id] = agent
        # Also register by short name (without -agent suffix)
        short_name = agent.agent_id.replace("-agent", "")
        self._agents[short_name] = agent

        logger.debug(
            "Registered agent",
            agent_id=agent.agent_id,
            flow=agent.flow,
            base_url=agent.base_url,
        )

    def get(self, agent_name: str) -> Optional[AgentEndpoint]:
        """Get agent by name or ID.

        Args:
            agent_name: Agent name or full ID

        Returns:
            AgentEndpoint if found, None otherwise
        """
        return self._agents.get(agent_name)

    def get_by_flow(self, flow: str) -> list[AgentEndpoint]:
        """Get all agents for a specific flow.

        Args:
            flow: Flow name (e.g., "oideachais", "crypteolas")

        Returns:
            List of agents in that flow
        """
        seen = set()
        agents = []
        for agent in self._agents.values():
            if agent.flow == flow and agent.agent_id not in seen:
                agents.append(agent)
                seen.add(agent.agent_id)
        return agents

    def get_by_capability(self, capability: str) -> list[AgentEndpoint]:
        """Get all agents with a specific capability.

        Args:
            capability: Capability to search for

        Returns:
            List of agents with that capability
        """
        seen = set()
        agents = []
        for agent in self._agents.values():
            if capability in agent.capabilities and agent.agent_id not in seen:
                agents.append(agent)
                seen.add(agent.agent_id)
        return agents

    def list_all(self) -> list[AgentEndpoint]:
        """List all registered agents (deduplicated).

        Returns:
            List of all unique agent endpoints
        """
        seen = set()
        agents = []
        for agent in self._agents.values():
            if agent.agent_id not in seen:
                agents.append(agent)
                seen.add(agent.agent_id)
        return agents

    async def discover(self, agent: AgentEndpoint) -> Optional[AgentCard]:
        """Fetch agent card from remote service.

        Args:
            agent: Agent endpoint to discover

        Returns:
            AgentCard if available, None otherwise
        """
        # Check cache first
        if agent.agent_id in self._agent_cards:
            return self._agent_cards[agent.agent_id]

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(agent.agent_card_url)
                response.raise_for_status()
                data = response.json()

                card = AgentCard(
                    id=data.get("id", agent.agent_id),
                    name=data.get("name", agent.agent_id),
                    description=data.get("description", ""),
                    provider=data.get("provider", agent.flow),
                    version=data.get("version", "1.0.0"),
                    capabilities=data.get("capabilities", []),
                    supported_formats=data.get("supported_formats", ["text/plain"]),
                    metadata=data.get("metadata", {}),
                )

                # Cache the card
                async with self._lock:
                    self._agent_cards[agent.agent_id] = card

                logger.info(
                    "Discovered agent card",
                    agent_id=agent.agent_id,
                    name=card.name,
                    capabilities=card.capabilities,
                )

                return card

        except Exception as e:
            logger.warning(
                "Failed to discover agent",
                agent_id=agent.agent_id,
                url=agent.agent_card_url,
                error=str(e),
            )
            return None

    async def refresh_all(self) -> dict[str, Optional[AgentCard]]:
        """Refresh agent cards for all registered agents.

        Returns:
            Dict mapping agent_id to discovered AgentCard (or None)
        """
        results = {}
        for agent in self.list_all():
            results[agent.agent_id] = await self.discover(agent)
        return results


# Global registry singleton
_registry: Optional[AgentRegistry] = None


def get_registry() -> AgentRegistry:
    """Get the global agent registry."""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
        # Initialize with default agents from config
        from ..config import DEFAULT_AGENT_ENDPOINTS
        for name, endpoint in DEFAULT_AGENT_ENDPOINTS.items():
            _registry.register(endpoint)
    return _registry


def init_registry(agents: Optional[list[AgentEndpoint]] = None) -> AgentRegistry:
    """Initialize the global agent registry.

    Args:
        agents: Optional list of additional agents to register

    Returns:
        Initialized AgentRegistry
    """
    global _registry
    _registry = AgentRegistry()

    # Add default agents
    from ..config import DEFAULT_AGENT_ENDPOINTS
    for name, endpoint in DEFAULT_AGENT_ENDPOINTS.items():
        _registry.register(endpoint)

    # Add custom agents
    if agents:
        for agent in agents:
            _registry.register(agent)

    return _registry
