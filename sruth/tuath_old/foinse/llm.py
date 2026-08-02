"""
Central LLM configuration for crypteolas.

Uses LiteLLM proxy for unified model access across all agents and pipelines.
All LLM-dependent code should import from this module.

Environment Variables:
    LITELLM_BASE_URL: Base URL of the LiteLLM proxy (default: http://localhost:4000)
    LITELLM_API_BASE: Alias for LITELLM_BASE_URL for compatibility
    CRYPTEOLAS_DEFAULT_MODEL: Default model ID (default: gpt-4o-mini)
"""

import os
from typing import Optional


# LiteLLM base URL - supports both variable names for compatibility
LITELLM_BASE_URL = os.environ.get(
    "LITELLM_BASE_URL",
    os.environ.get("LITELLM_API_BASE", "http://localhost:4000")
)

# Default model ID (via LiteLLM, no provider prefix needed)
DEFAULT_MODEL = os.environ.get(
    "CRYPTEOLAS_DEFAULT_MODEL",
    "gpt-4o-mini"
)


def get_model_id(model: Optional[str] = None) -> str:
    """
    Get model ID, defaulting to configured default.

    Args:
        model: Optional model override. If None, uses DEFAULT_MODEL.

    Returns:
        Model ID string to use with LiteLLM
    """
    return model or DEFAULT_MODEL


def get_litellm_config() -> dict:
    """
    Get LiteLLM configuration dictionary.

    Returns:
        Dict with api_base and model configured for LiteLLM client.
    """
    return {
        "api_base": LITELLM_BASE_URL,
        "model": DEFAULT_MODEL,
    }


def get_litellm_model_kwargs(model: Optional[str] = None) -> dict:
    """
    Get keyword arguments for LiteLLM model instantiation.

    Args:
        model: Optional model override.

    Returns:
        Dict with id and api_base for LiteLLM initialization.
    """
    return {
        "id": get_model_id(model),
        "api_base": LITELLM_BASE_URL,
    }
