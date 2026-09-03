"""A2A client for cross-flow agent communication.

Provides a high-level client for calling agents across different flows
using the A2A protocol.
"""

import asyncio
import json
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Optional

import httpx
import structlog

from ..config import get_config
from ..middleware.a2a_auth import create_service_token
from .discovery import AgentEndpoint, get_registry
from .circuit_breaker import CircuitBreaker, CircuitBreakerOpen, get_circuit_breaker_registry

logger = structlog.get_logger()


@dataclass
class A2AMessage:
    """Message to send to an agent via A2A protocol."""

    content: str
    session_id: Optional[str] = None
    context: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

    def to_a2a_payload(self) -> dict:
        """Convert to A2A protocol message format."""
        return {
            "message": {
                "parts": [
                    {
                        "type": "text",
                        "text": self.content,
                    }
                ],
            },
            "sessionId": self.session_id,
            "context": self.context,
            "metadata": self.metadata,
        }


@dataclass
class A2AResponse:
    """Response from an A2A agent call."""

    content: str
    session_id: Optional[str] = None
    artifacts: list[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    status: str = "completed"

    @classmethod
    def from_a2a_payload(cls, data: dict) -> "A2AResponse":
        """Parse A2A protocol response."""
        # Extract text content from response
        content_parts = []
        message = data.get("message", {})
        for part in message.get("parts", []):
            if part.get("type") == "text":
                content_parts.append(part.get("text", ""))

        return cls(
            content="\n".join(content_parts),
            session_id=data.get("sessionId"),
            artifacts=data.get("artifacts", []),
            metadata=data.get("metadata", {}),
            status=data.get("status", "completed"),
        )


@dataclass
class A2AStreamEvent:
    """A streaming event from an A2A agent."""

    event_type: str
    data: dict
    raw: str = ""


class A2AClient:
    """Client for making A2A calls to remote agents.

    Handles:
    - Service authentication via JWT
    - User context passthrough
    - Circuit breaker protection
    - Streaming and blocking modes
    - Retry logic

    Usage:
        client = A2AClient()

        # Blocking call
        response = await client.send_message(
            agent="curriculum",
            message="Search for algebra topics",
            user_id="user@example.com",
        )

        # Streaming call
        async for event in client.stream_message(
            agent="research",
            message="Analyze this paper",
        ):
            print(event.data)
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout_seconds: int = 30,
        retry_count: int = 3,
        use_circuit_breaker: bool = True,
    ):
        """Initialize A2A client.

        Args:
            base_url: Base URL for direct calls (bypasses registry)
            timeout_seconds: Request timeout
            retry_count: Number of retries on failure
            use_circuit_breaker: Enable circuit breaker protection
        """
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        self.retry_count = retry_count
        self.use_circuit_breaker = use_circuit_breaker
        self._registry = get_registry()
        self._cb_registry = get_circuit_breaker_registry()

    def _get_service_headers(self, user_id: Optional[str] = None) -> dict:
        """Get headers for authenticated A2A call."""
        try:
            config = get_config()
            token = create_service_token(
                service_name=config.service_name,
                user_id=user_id,
            )
            headers = {
                "Content-Type": "application/json",
                "X-Service-Token": token,
            }
            if user_id:
                headers["X-User-ID"] = user_id
            return headers
        except RuntimeError:
            # Config not initialized - return minimal headers
            return {"Content-Type": "application/json"}

    def _resolve_agent(self, agent: str | AgentEndpoint) -> AgentEndpoint:
        """Resolve agent name to endpoint."""
        if isinstance(agent, AgentEndpoint):
            return agent

        endpoint = self._registry.get(agent)
        if not endpoint:
            raise ValueError(f"Unknown agent: {agent}. Register it first.")
        return endpoint

    async def send_message(
        self,
        agent: str | AgentEndpoint,
        message: str | A2AMessage,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        context: Optional[dict] = None,
    ) -> A2AResponse:
        """Send a blocking message to an agent.

        Args:
            agent: Agent name or endpoint
            message: Message content or A2AMessage object
            user_id: User ID to pass through
            session_id: Session ID for conversation continuity
            context: Additional context for the agent

        Returns:
            A2AResponse with agent's response

        Raises:
            CircuitBreakerOpen: If circuit is open
            httpx.HTTPError: On network errors
        """
        endpoint = self._resolve_agent(agent)

        # Build message
        if isinstance(message, str):
            a2a_msg = A2AMessage(
                content=message,
                session_id=session_id,
                context=context or {},
            )
        else:
            a2a_msg = message
            if session_id:
                a2a_msg.session_id = session_id
            if context:
                a2a_msg.context.update(context)

        # Get circuit breaker if enabled
        cb = None
        if self.use_circuit_breaker:
            cb = await self._cb_registry.get(endpoint.flow)

        async def _do_request() -> A2AResponse:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    endpoint.message_send_url,
                    json=a2a_msg.to_a2a_payload(),
                    headers=self._get_service_headers(user_id),
                )
                response.raise_for_status()
                return A2AResponse.from_a2a_payload(response.json())

        # Execute with circuit breaker
        if cb:
            return await cb.call(_do_request)
        else:
            return await _do_request()

    async def stream_message(
        self,
        agent: str | AgentEndpoint,
        message: str | A2AMessage,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        context: Optional[dict] = None,
    ) -> AsyncIterator[A2AStreamEvent]:
        """Stream message to an agent, yielding events.

        Args:
            agent: Agent name or endpoint
            message: Message content or A2AMessage object
            user_id: User ID to pass through
            session_id: Session ID for conversation continuity
            context: Additional context for the agent

        Yields:
            A2AStreamEvent for each server-sent event

        Raises:
            CircuitBreakerOpen: If circuit is open
            httpx.HTTPError: On network errors
        """
        endpoint = self._resolve_agent(agent)

        # Build message
        if isinstance(message, str):
            a2a_msg = A2AMessage(
                content=message,
                session_id=session_id,
                context=context or {},
            )
        else:
            a2a_msg = message
            if session_id:
                a2a_msg.session_id = session_id
            if context:
                a2a_msg.context.update(context)

        # Check circuit breaker before streaming
        cb = None
        if self.use_circuit_breaker:
            cb = await self._cb_registry.get(endpoint.flow)
            if cb.is_open:
                raise CircuitBreakerOpen(cb.name, cb.time_until_retry)

        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream(
                    "POST",
                    endpoint.message_stream_url,
                    json=a2a_msg.to_a2a_payload(),
                    headers=self._get_service_headers(user_id),
                ) as response:
                    response.raise_for_status()

                    event_type = ""
                    data_buffer = []

                    async for line in response.aiter_lines():
                        if not line:
                            # Empty line = end of event
                            if event_type and data_buffer:
                                data_str = "\n".join(data_buffer)
                                try:
                                    data = json.loads(data_str)
                                except json.JSONDecodeError:
                                    data = {"raw": data_str}

                                yield A2AStreamEvent(
                                    event_type=event_type,
                                    data=data,
                                    raw=data_str,
                                )

                            event_type = ""
                            data_buffer = []
                        elif line.startswith("event:"):
                            event_type = line[6:].strip()
                        elif line.startswith("data:"):
                            data_buffer.append(line[5:].strip())

            # Record success
            if cb:
                await cb._on_success()

        except Exception as e:
            # Record failure
            if cb:
                await cb._on_failure(e)
            raise

    async def call_agent(
        self,
        agent: str,
        message: str,
        user_id: Optional[str] = None,
        stream: bool = False,
        **kwargs,
    ) -> A2AResponse | AsyncIterator[A2AStreamEvent]:
        """Convenience method to call an agent by name.

        Args:
            agent: Agent name (e.g., "curriculum", "defi_analytics")
            message: Message to send
            user_id: Optional user ID
            stream: If True, return streaming iterator
            **kwargs: Additional arguments

        Returns:
            A2AResponse or AsyncIterator[A2AStreamEvent]
        """
        if stream:
            return self.stream_message(agent, message, user_id=user_id, **kwargs)
        else:
            return await self.send_message(agent, message, user_id=user_id, **kwargs)


# Convenience function for simple calls
async def call_agent(
    agent: str,
    message: str,
    user_id: Optional[str] = None,
    **kwargs,
) -> A2AResponse:
    """Quick function to call an agent.

    Usage:
        from sruth.shared.agent_os.a2a import call_agent

        response = await call_agent("curriculum", "Find algebra topics")
        print(response.content)
    """
    client = A2AClient()
    return await client.send_message(agent, message, user_id=user_id, **kwargs)
