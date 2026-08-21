"""
Agent configuration for Tuath.

Configures LLM models with Celtic language support.
"""

import os
from dataclasses import dataclass


@dataclass
class AgentConfig:
    """Configuration for Tuath agents."""

    # Primary orchestrator model (high capability, multilingual)
    orchestrator_model: str = "gemini-2.0-flash"

    # Worker model for specialized tasks
    worker_model: str = "gemini-2.0-flash"

    # Fast model for simple routing/classification
    fast_model: str = "gemini-2.0-flash"

    # Irish language model (UCCIX-Llama2-13B for Irish text generation)
    irish_model: str = "uccix/uccix-llama2-13b"

    # Multilingual reasoning model (Qwen3 supports Celtic languages)
    multilingual_model: str = "qwen/qwen2.5-72b-instruct"

    # Embedding model for semantic search
    embedding_model: str = "BAAI/bge-m3"

    # Max tokens for responses
    max_output_tokens: int = 4096

    # Temperature for generation
    temperature: float = 0.7

    # Search result limits
    default_search_limit: int = 10
    max_search_limit: int = 50

    # x402 Payment settings
    enable_payments: bool = True
    free_daily_messages: int = 5
    free_daily_searches: int = 3
    message_price_usd: float = 0.01
    search_price_usd: float = 0.02
    premium_quest_price_usd: float = 0.05

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Load configuration from environment variables."""
        return cls(
            orchestrator_model=os.environ.get("TUATH_ORCHESTRATOR_MODEL", cls.orchestrator_model),
            worker_model=os.environ.get("TUATH_WORKER_MODEL", cls.worker_model),
            fast_model=os.environ.get("TUATH_FAST_MODEL", cls.fast_model),
            max_output_tokens=int(os.environ.get("TUATH_MAX_TOKENS", cls.max_output_tokens)),
            temperature=float(os.environ.get("TUATH_TEMPERATURE", cls.temperature)),
            enable_payments=os.environ.get("TUATH_ENABLE_PAYMENTS", "true").lower() == "true",
        )


# Global config instance
config = AgentConfig.from_env()
