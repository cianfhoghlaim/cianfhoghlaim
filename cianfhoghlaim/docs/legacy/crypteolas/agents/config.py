"""
Agent configuration for Crypteolas.

Configures LLM models and shared settings for all agents.
"""

import os
from dataclasses import dataclass


@dataclass
class AgentConfig:
    """Configuration for Crypteolas agents."""

    # Primary orchestrator model (high capability)
    orchestrator_model: str = "gemini-2.0-flash"

    # Worker model for specialized tasks
    worker_model: str = "gemini-2.0-flash"

    # Fast model for simple routing/classification
    fast_model: str = "gemini-2.0-flash"

    # Embedding model for semantic search
    embedding_model: str = "BAAI/bge-m3"

    # Code embedding model
    code_embedding_model: str = "microsoft/codebert-base"

    # Max tokens for responses
    max_output_tokens: int = 4096

    # Temperature for generation
    temperature: float = 0.7

    # Search result limits
    default_search_limit: int = 10
    max_search_limit: int = 50

    # Knowledge graph settings
    enable_temporal_graph: bool = True
    enable_static_graph: bool = True

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Load configuration from environment variables."""
        return cls(
            orchestrator_model=os.environ.get(
                "CRYPTEOLAS_ORCHESTRATOR_MODEL", cls.orchestrator_model
            ),
            worker_model=os.environ.get("CRYPTEOLAS_WORKER_MODEL", cls.worker_model),
            fast_model=os.environ.get("CRYPTEOLAS_FAST_MODEL", cls.fast_model),
            max_output_tokens=int(
                os.environ.get("CRYPTEOLAS_MAX_TOKENS", cls.max_output_tokens)
            ),
            temperature=float(
                os.environ.get("CRYPTEOLAS_TEMPERATURE", cls.temperature)
            ),
        )


# Global config instance
config = AgentConfig.from_env()
