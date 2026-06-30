"""
Letta Cloud Client for Persistent Agent Memory.

Provides:
- Connection to Letta Cloud API for stateful agents
- ProjectArchitect agent for codebase knowledge
- Archival memory for context banking
- Integration with existing agent systems

Docs: https://docs.letta.com
"""

import logging
import os
from functools import lru_cache
from typing import Any

logger = logging.getLogger(__name__)

# Lazy import for optional dependency
_letta = None
_letta_available = None


def _get_letta():
    """Lazy load Letta SDK to handle missing dependency."""
    global _letta, _letta_available
    if _letta_available is None:
        try:
            from letta_client import Letta

            _letta = Letta
            _letta_available = True
        except ImportError:
            try:
                # Fallback to old package name
                from letta import Letta

                _letta = Letta
                _letta_available = True
            except ImportError:
                _letta_available = False
                logger.warning(
                    "Letta SDK not installed. Install with: pip install letta-client"
                )
    return _letta if _letta_available else None


# Configuration from environment
LETTA_API_KEY = os.getenv("LETTA_API_KEY", "")
LETTA_BASE_URL = os.getenv("LETTA_BASE_URL", "https://api.letta.ai/v1")
LETTA_DEFAULT_AGENT_ID = os.getenv("LETTA_DEFAULT_AGENT_ID", "")

# Agent configuration
PROJECT_ARCHITECT_SYSTEM = """You are ProjectArchitect, an expert on the Cianfhoghlaim Celtic education platform.

You have deep knowledge of:
- Infrastructure patterns (bonneagar/): Docker Compose stacks, Komodo deployments, Pangolin networking
- Data pipelines (sruth/): DLT ingestion, CocoIndex transforms, Dagster orchestration
- Agent systems: AG-UI protocol, ADK routing, Agno teams
- Celtic languages: Irish, Welsh, Scottish Gaelic, Manx NLP models
- Curriculum data: NCCA, SEC, UK education boards

Your archival memory contains:
- AGENTS.md files from each directory
- CLAUDE.md project instructions
- Pattern documentation from taighde/patterns/
- Skill definitions from .claude/skills/

When answering questions:
1. Search your archival memory for relevant context
2. Cite specific files and patterns when applicable
3. Provide actionable code or configuration when asked
4. Reference the technology stack appropriately

You help developers understand and extend the Cianfhoghlaim platform."""


@lru_cache(maxsize=1)
def get_letta_client():
    """
    Get or create a configured Letta Cloud client.

    Returns:
        Letta client instance or None if unavailable.
    """
    LettaClass = _get_letta()
    if LettaClass is None:
        return None

    if not LETTA_API_KEY:
        logger.warning("LETTA_API_KEY not set, Letta disabled")
        return None

    try:
        client = LettaClass(
            base_url=LETTA_BASE_URL,
            token=LETTA_API_KEY,
        )
        logger.info(f"Letta client connected to {LETTA_BASE_URL}")
        return client
    except Exception as e:
        logger.error(f"Failed to create Letta client: {e}")
        return None


def get_or_create_architect_agent(client=None):
    """
    Get or create the ProjectArchitect agent.

    The ProjectArchitect agent maintains persistent memory about the
    Cianfhoghlaim codebase and can answer questions about architecture,
    patterns, and implementation details.

    Args:
        client: Optional Letta client. If None, creates one.

    Returns:
        Agent object or None if unavailable.
    """
    if client is None:
        client = get_letta_client()
    if client is None:
        return None

    try:
        # Check for existing agent
        agents = client.agents.list()
        for agent in agents:
            if agent.name == "ProjectArchitect":
                logger.info(f"Found existing ProjectArchitect agent: {agent.id}")
                return agent

        # Create new agent
        agent = client.agents.create(
            name="ProjectArchitect",
            system=PROJECT_ARCHITECT_SYSTEM,
            include_base_tools=True,
            llm="claude-sonnet-4-20250514",  # Use Claude for best results
        )
        logger.info(f"Created ProjectArchitect agent: {agent.id}")
        return agent

    except Exception as e:
        logger.error(f"Failed to get/create ProjectArchitect agent: {e}")
        return None


def archive_document(
    content: str,
    source: str,
    agent=None,
    client=None,
) -> bool:
    """
    Archive a document to the ProjectArchitect's memory.

    Args:
        content: Document content to archive
        source: Source identifier (e.g., file path)
        agent: Optional agent. If None, gets/creates ProjectArchitect.
        client: Optional Letta client.

    Returns:
        True if successful, False otherwise.
    """
    if client is None:
        client = get_letta_client()
    if client is None:
        return False

    if agent is None:
        agent = get_or_create_architect_agent(client)
    if agent is None:
        return False

    try:
        # Format content with source metadata
        formatted_content = f"# Source: {source}\n\n{content}"

        # Insert into archival memory
        client.agents.archival_memory.insert(
            agent_id=agent.id,
            text=formatted_content,
        )
        logger.info(f"Archived document: {source}")
        return True

    except Exception as e:
        logger.error(f"Failed to archive document {source}: {e}")
        return False


def search_memory(
    query: str,
    agent=None,
    client=None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """
    Search the ProjectArchitect's archival memory.

    Args:
        query: Search query
        agent: Optional agent. If None, gets/creates ProjectArchitect.
        client: Optional Letta client.
        limit: Maximum results to return.

    Returns:
        List of memory passages with scores.
    """
    if client is None:
        client = get_letta_client()
    if client is None:
        return []

    if agent is None:
        agent = get_or_create_architect_agent(client)
    if agent is None:
        return []

    try:
        results = client.agents.archival_memory.search(
            agent_id=agent.id,
            query=query,
            limit=limit,
        )

        return [
            {
                "text": r.text,
                "score": getattr(r, "score", None),
                "created_at": getattr(r, "created_at", None),
            }
            for r in results
        ]

    except Exception as e:
        logger.error(f"Failed to search memory: {e}")
        return []


def ask_architect(
    question: str,
    agent=None,
    client=None,
) -> str | None:
    """
    Ask the ProjectArchitect a question about the codebase.

    The agent will search its archival memory and provide a response.

    Args:
        question: Question to ask
        agent: Optional agent. If None, gets/creates ProjectArchitect.
        client: Optional Letta client.

    Returns:
        Agent response or None if unavailable.
    """
    if client is None:
        client = get_letta_client()
    if client is None:
        return None

    if agent is None:
        agent = get_or_create_architect_agent(client)
    if agent is None:
        return None

    try:
        response = client.agents.messages.create(
            agent_id=agent.id,
            messages=[{"role": "user", "content": question}],
        )

        # Extract assistant response
        for message in response.messages:
            if message.message_type == "assistant_message":
                return message.content

        return None

    except Exception as e:
        logger.error(f"Failed to ask architect: {e}")
        return None


def clear_archival_memory(
    agent=None,
    client=None,
) -> bool:
    """
    Clear all archival memory for the ProjectArchitect.

    Use with caution - this deletes all banked context.

    Args:
        agent: Optional agent. If None, gets/creates ProjectArchitect.
        client: Optional Letta client.

    Returns:
        True if successful, False otherwise.
    """
    if client is None:
        client = get_letta_client()
    if client is None:
        return False

    if agent is None:
        agent = get_or_create_architect_agent(client)
    if agent is None:
        return False

    try:
        # Get all archival memories
        memories = client.agents.archival_memory.list(agent_id=agent.id)

        # Delete each one
        for memory in memories:
            client.agents.archival_memory.delete(
                agent_id=agent.id,
                memory_id=memory.id,
            )

        logger.info(f"Cleared {len(memories)} archival memories")
        return True

    except Exception as e:
        logger.error(f"Failed to clear archival memory: {e}")
        return False


def get_memory_stats(
    agent=None,
    client=None,
) -> dict[str, Any]:
    """
    Get statistics about the ProjectArchitect's memory.

    Returns:
        Dictionary with memory statistics.
    """
    if client is None:
        client = get_letta_client()
    if client is None:
        return {"available": False, "error": "Letta client unavailable"}

    if agent is None:
        agent = get_or_create_architect_agent(client)
    if agent is None:
        return {"available": False, "error": "Agent unavailable"}

    try:
        memories = client.agents.archival_memory.list(agent_id=agent.id)

        total_chars = sum(len(m.text) for m in memories)

        return {
            "available": True,
            "agent_id": agent.id,
            "agent_name": agent.name,
            "archival_count": len(memories),
            "total_characters": total_chars,
            "estimated_tokens": total_chars // 4,  # Rough estimate
        }

    except Exception as e:
        logger.error(f"Failed to get memory stats: {e}")
        return {"available": False, "error": str(e)}
