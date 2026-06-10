"""
Letta Memory Service for Celtic Education Agents.

Provides:
- Conversation memory persistence across sessions
- Agent state management
- Human-in-the-loop context retention
- Multi-agent memory sharing

Letta Cloud: https://app.letta.ai
Docs: https://docs.letta.com

Usage:
    from memory import LettaMemoryService

    service = LettaMemoryService()
    await service.initialize()

    # Save conversation context
    await service.save_conversation(
        agent_name="curriculum_agent",
        messages=[...],
        session_id="user123"
    )

    # Retrieve context
    context = await service.get_context(
        agent_name="curriculum_agent",
        session_id="user123"
    )
"""

import asyncio
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

# Default configuration
LETTA_API_KEY = os.getenv("LETTA_API_KEY", "")
LETTA_BASE_URL = os.getenv("LETTA_BASE_URL", "https://api.letta.ai/v1")


@dataclass
class ConversationMessage:
    """A message in a conversation."""

    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentMemory:
    """Memory state for an agent."""

    agent_name: str
    session_id: str
    messages: list[ConversationMessage] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class LettaMemoryService:
    """
    Memory service using Letta Cloud.

    Handles:
    - Conversation memory persistence
    - Agent state management
    - Context retrieval for follow-up queries
    - Cross-session memory access
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        """
        Initialize Letta memory service.

        Args:
            api_key: Letta API key (defaults to LETTA_API_KEY env var)
            base_url: Letta API base URL (defaults to LETTA_BASE_URL env var)
        """
        self.api_key = api_key or LETTA_API_KEY
        self.base_url = base_url or LETTA_BASE_URL
        self._client = None
        self._initialized = False
        self._agents: dict[str, Any] = {}

    async def initialize(self) -> bool:
        """
        Initialize the Letta client.

        Returns:
            True if initialization successful, False otherwise.
        """
        if self._initialized:
            return True

        if not self.api_key:
            logger.warning("LETTA_API_KEY not set, memory service disabled")
            return False

        try:
            from letta import Letta

            self._client = Letta(
                api_key=self.api_key,
                base_url=self.base_url,
            )
            self._initialized = True
            logger.info(f"Letta client initialized: {self.base_url}")
            return True

        except ImportError:
            logger.warning("Letta not installed. Install with: pip install letta")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Letta: {e}")
            return False

    async def _ensure_initialized(self) -> bool:
        """Ensure service is initialized."""
        if not self._initialized:
            return await self.initialize()
        return True

    async def _get_or_create_agent(
        self,
        agent_name: str,
        system_prompt: str | None = None,
    ):
        """
        Get or create a Letta agent.

        Args:
            agent_name: Name of the agent
            system_prompt: Optional system prompt for new agents

        Returns:
            Letta agent object
        """
        if not await self._ensure_initialized():
            return None

        if agent_name in self._agents:
            return self._agents[agent_name]

        try:
            # Try to get existing agent
            agents = await asyncio.to_thread(
                self._client.agents.list
            )

            for agent in agents:
                if agent.name == agent_name:
                    self._agents[agent_name] = agent
                    return agent

            # Create new agent if not found
            default_system = f"""You are {agent_name}, part of the Celtic Education Platform.
You help users learn about Celtic languages, culture, and education across Ireland, Scotland, Wales, and other Celtic nations.
Maintain context from previous conversations and provide helpful, accurate responses.
"""
            agent = await asyncio.to_thread(
                self._client.agents.create,
                name=agent_name,
                system=system_prompt or default_system,
            )
            self._agents[agent_name] = agent
            logger.info(f"Created Letta agent: {agent_name}")
            return agent

        except Exception as e:
            logger.error(f"Failed to get/create agent {agent_name}: {e}")
            return None

    async def save_conversation(
        self,
        agent_name: str,
        messages: list[dict[str, str]],
        session_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """
        Save conversation messages to Letta memory.

        Args:
            agent_name: Name of the agent
            messages: List of messages with "role" and "content" keys
            session_id: Optional session identifier
            metadata: Additional metadata to store

        Returns:
            True if save successful, False otherwise.
        """
        if not await self._ensure_initialized():
            return False

        agent = await self._get_or_create_agent(agent_name)
        if agent is None:
            return False

        try:
            # Add each message to the agent's memory
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")

                if role == "user":
                    await asyncio.to_thread(
                        self._client.agents.messages.create,
                        agent_id=agent.id,
                        role="user",
                        content=content,
                    )
                elif role == "assistant":
                    # Store assistant responses as part of context
                    pass  # Letta handles this automatically

            logger.debug(f"Saved {len(messages)} messages for {agent_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
            return False

    async def get_context(
        self,
        agent_name: str,
        session_id: str | None = None,
        max_messages: int = 20,
    ) -> AgentMemory | None:
        """
        Retrieve conversation context for an agent.

        Args:
            agent_name: Name of the agent
            session_id: Optional session identifier
            max_messages: Maximum messages to retrieve

        Returns:
            AgentMemory object with conversation history, or None if not found.
        """
        if not await self._ensure_initialized():
            return None

        agent = await self._get_or_create_agent(agent_name)
        if agent is None:
            return None

        try:
            # Get recent messages from agent
            messages_response = await asyncio.to_thread(
                self._client.agents.messages.list,
                agent_id=agent.id,
                limit=max_messages,
            )

            messages = []
            for msg in messages_response:
                messages.append(
                    ConversationMessage(
                        role=msg.role,
                        content=msg.content,
                        timestamp=datetime.fromisoformat(msg.created_at)
                        if hasattr(msg, "created_at")
                        else datetime.now(),
                    )
                )

            return AgentMemory(
                agent_name=agent_name,
                session_id=session_id or "",
                messages=messages,
                context={"agent_id": agent.id},
            )

        except Exception as e:
            logger.error(f"Failed to get context: {e}")
            return None

    async def send_message(
        self,
        agent_name: str,
        message: str,
        session_id: str | None = None,
    ) -> str | None:
        """
        Send a message to an agent and get a response.

        This uses Letta's built-in conversation handling with memory.

        Args:
            agent_name: Name of the agent
            message: User message
            session_id: Optional session identifier

        Returns:
            Agent response string, or None on failure.
        """
        if not await self._ensure_initialized():
            return None

        agent = await self._get_or_create_agent(agent_name)
        if agent is None:
            return None

        try:
            response = await asyncio.to_thread(
                self._client.agents.messages.create,
                agent_id=agent.id,
                role="user",
                content=message,
            )

            # Extract response content
            if hasattr(response, "content"):
                return response.content
            elif isinstance(response, dict):
                return response.get("content", str(response))
            else:
                return str(response)

        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return None

    async def clear_memory(
        self,
        agent_name: str,
        session_id: str | None = None,
    ) -> bool:
        """
        Clear memory for an agent.

        Args:
            agent_name: Name of the agent
            session_id: Optional session identifier (clears all if None)

        Returns:
            True if clear successful, False otherwise.
        """
        if not await self._ensure_initialized():
            return False

        try:
            if agent_name in self._agents:
                agent = self._agents[agent_name]
                # Delete the agent (this clears all memory)
                await asyncio.to_thread(
                    self._client.agents.delete,
                    agent_id=agent.id,
                )
                del self._agents[agent_name]
                logger.info(f"Cleared memory for agent: {agent_name}")

            return True

        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")
            return False

    async def get_summary(
        self,
        agent_name: str,
    ) -> str | None:
        """
        Get a summary of the agent's memory state.

        Args:
            agent_name: Name of the agent

        Returns:
            Summary string or None.
        """
        if not await self._ensure_initialized():
            return None

        agent = await self._get_or_create_agent(agent_name)
        if agent is None:
            return None

        try:
            # Get agent's core memory/archival summary
            memory_state = await asyncio.to_thread(
                self._client.agents.get,
                agent_id=agent.id,
            )

            if hasattr(memory_state, "memory"):
                return str(memory_state.memory)
            return f"Agent {agent_name}: Active"

        except Exception as e:
            logger.error(f"Failed to get summary: {e}")
            return None


# ============================================================================
# Convenience Functions
# ============================================================================

_memory_service: LettaMemoryService | None = None


def get_memory_service() -> LettaMemoryService:
    """Get or create the singleton memory service."""
    global _memory_service
    if _memory_service is None:
        _memory_service = LettaMemoryService()
    return _memory_service


async def save_conversation(
    agent_name: str,
    messages: list[dict[str, str]],
    session_id: str | None = None,
) -> bool:
    """Convenience function to save conversation."""
    service = get_memory_service()
    return await service.save_conversation(agent_name, messages, session_id)


async def get_context(
    agent_name: str,
    session_id: str | None = None,
) -> AgentMemory | None:
    """Convenience function to get context."""
    service = get_memory_service()
    return await service.get_context(agent_name, session_id)


async def send_message(
    agent_name: str,
    message: str,
) -> str | None:
    """Convenience function to send message and get response."""
    service = get_memory_service()
    return await service.send_message(agent_name, message)
