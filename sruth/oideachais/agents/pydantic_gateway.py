"""
Pydantic AI Gateway Integration for Oideachais.

Provides multi-provider LLM routing with:
- Cost limits per request
- Automatic fallback between providers
- Integration with observability stack (Langfuse, Datadog, Logfire)
- Support for Celtic language models

Based on patterns from:
- taighde/Pydantic AI Gateway - Pydantic AI.md
- taighde/LiteLLM - Pydantic Logfire Documentation.md

Usage:
    from agents.pydantic_gateway import (
        create_curriculum_agent,
        create_translation_agent,
        GatewayConfig,
    )

    agent = create_curriculum_agent()
    result = await agent.run("Extract learning outcomes from this document")
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

# Check for required dependencies
try:
    from pydantic_ai import Agent
    HAS_PYDANTIC_AI = True
except ImportError:
    HAS_PYDANTIC_AI = False
    logger.warning("pydantic_ai not installed")

try:
    import logfire
    HAS_LOGFIRE = True
except ImportError:
    HAS_LOGFIRE = False

try:
    import litellm
    HAS_LITELLM = True
except ImportError:
    HAS_LITELLM = False


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class GatewayConfig:
    """Configuration for Pydantic AI Gateway routing."""

    # Gateway settings
    gateway_url: str = field(
        default_factory=lambda: os.getenv(
            "PYDANTIC_AI_GATEWAY_URL",
            "https://gateway.pydantic.dev/proxy"
        )
    )
    api_key: str | None = field(
        default_factory=lambda: os.getenv("PYDANTIC_AI_GATEWAY_API_KEY")
    )

    # Cost limits
    max_cost_per_request: str = "$1.00"  # Per-request cost limit
    max_cost_per_session: str = "$10.00"  # Per-session cost limit

    # Default model settings
    default_model: str = "gateway/anthropic:claude-sonnet-4-20250514"
    fallback_model: str = "gateway/google:gemini-2.0-flash"
    irish_model: str = "gateway/openai:gpt-4o"  # Best for Irish content

    # Request settings
    max_tokens: int = 8192
    temperature: float = 0.7
    timeout: int = 60

    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0


# Global config
gateway_config = GatewayConfig()


# =============================================================================
# Observability Integration
# =============================================================================

def setup_observability() -> None:
    """
    Set up observability instrumentation for LLM calls.

    Integrates with:
    - Logfire for OpenTelemetry tracing
    - LiteLLM for multi-provider routing
    - Datadog for APM
    """
    if HAS_LOGFIRE and HAS_LITELLM:
        # Instrument LiteLLM with Logfire
        logfire.instrument_litellm()
        logger.info("Logfire instrumentation enabled for LiteLLM")

    # Set up LiteLLM callbacks for Langfuse
    if HAS_LITELLM:
        langfuse_host = os.getenv("LANGFUSE_HOST")
        if langfuse_host:
            litellm.success_callback = ["langfuse"]
            litellm.failure_callback = ["langfuse"]
            logger.info(f"Langfuse callbacks enabled: {langfuse_host}")


# =============================================================================
# Model Selection
# =============================================================================

MODEL_CAPABILITIES = {
    # Claude models - best for complex reasoning
    "gateway/anthropic:claude-opus-4-5-20251101": {
        "strengths": ["complex_reasoning", "code", "long_context"],
        "cost_tier": "high",
        "max_tokens": 16384,
    },
    "gateway/anthropic:claude-sonnet-4-20250514": {
        "strengths": ["balanced", "code", "analysis"],
        "cost_tier": "medium",
        "max_tokens": 8192,
    },
    # Gemini models - good for grounding
    "gateway/google:gemini-2.0-flash": {
        "strengths": ["speed", "grounding", "multimodal"],
        "cost_tier": "low",
        "max_tokens": 8192,
    },
    "gateway/google:gemini-2.5-pro": {
        "strengths": ["reasoning", "long_context", "multimodal"],
        "cost_tier": "medium",
        "max_tokens": 32768,
    },
    # OpenAI models - good for Irish language
    "gateway/openai:gpt-4o": {
        "strengths": ["multilingual", "irish", "curriculum"],
        "cost_tier": "medium",
        "max_tokens": 16384,
    },
    "gateway/openai:gpt-4o-mini": {
        "strengths": ["speed", "cost_effective", "extraction"],
        "cost_tier": "low",
        "max_tokens": 16384,
    },
}


def select_model_for_task(
    task_type: str,
    language: str = "en",
    cost_priority: str = "balanced",
) -> str:
    """
    Select optimal model for a task.

    Args:
        task_type: Type of task (curriculum, translation, extraction, etc.)
        language: Target language (ga=Irish, en=English, etc.)
        cost_priority: Cost priority (low, balanced, high)

    Returns:
        Model identifier with gateway/ prefix
    """
    # Irish language tasks prefer GPT-4o
    if language in ("ga", "gd", "cy") or task_type == "translation":
        return "gateway/openai:gpt-4o"

    # Complex reasoning tasks
    if task_type in ("curriculum_analysis", "exam_validation", "research"):
        if cost_priority == "high":
            return "gateway/anthropic:claude-opus-4-5-20251101"
        return "gateway/anthropic:claude-sonnet-4-20250514"

    # Fast extraction tasks
    if task_type in ("extraction", "classification", "summarization"):
        return "gateway/google:gemini-2.0-flash"

    # Default balanced choice
    return gateway_config.default_model


# =============================================================================
# Agent Factories
# =============================================================================

if HAS_PYDANTIC_AI:

    def create_curriculum_agent(
        model: str | None = None,
        max_cost: str | None = None,
    ) -> Agent:
        """
        Create an agent for curriculum analysis tasks.

        Args:
            model: Model to use (defaults to gateway-routed model)
            max_cost: Maximum cost per request

        Returns:
            Configured Pydantic AI Agent
        """
        model = model or select_model_for_task("curriculum_analysis")
        cost_limit = max_cost or gateway_config.max_cost_per_request

        agent = Agent(
            model,
            model_settings={
                "max_tokens": gateway_config.max_tokens,
                "temperature": gateway_config.temperature,
                "timeout": gateway_config.timeout,
                "experimental_max_cost_limit": cost_limit,
            },
            system_prompt="""You are an expert in Celtic education curricula.

Your role is to:
1. Analyze curriculum documents from Ireland, Scotland, Wales, and England
2. Extract learning outcomes and key concepts
3. Compare curricula across nations
4. Support both English and Irish language content

IMPORTANT:
- Cite specific curriculum sources when possible
- Note differences between nations' curricula
- Preserve Irish/Welsh/Gaelic terminology
- Align with official marking schemes for exam content
""",
        )

        return agent

    def create_translation_agent(
        source_lang: str = "en",
        target_lang: str = "ga",
        max_cost: str | None = None,
    ) -> Agent:
        """
        Create an agent for Celtic language translation.

        Args:
            source_lang: Source language code
            target_lang: Target language code
            max_cost: Maximum cost per request

        Returns:
            Configured Pydantic AI Agent
        """
        model = select_model_for_task("translation", language=target_lang)
        cost_limit = max_cost or gateway_config.max_cost_per_request

        # Language name mapping
        lang_names = {
            "en": "English",
            "ga": "Irish (Gaeilge)",
            "gd": "Scottish Gaelic (Gàidhlig)",
            "cy": "Welsh (Cymraeg)",
            "br": "Breton (Brezhoneg)",
        }

        source_name = lang_names.get(source_lang, source_lang)
        target_name = lang_names.get(target_lang, target_lang)

        agent = Agent(
            model,
            model_settings={
                "max_tokens": gateway_config.max_tokens,
                "temperature": 0.3,  # Lower temperature for translation
                "timeout": gateway_config.timeout,
                "experimental_max_cost_limit": cost_limit,
            },
            system_prompt=f"""You are an expert translator for Celtic languages.

Your role is to translate from {source_name} to {target_name}.

TRANSLATION GUIDELINES:
1. Preserve educational terminology accurately
2. Use standard {target_name} (official standard where applicable)
3. For Irish: Use An Caighdeán Oifigiúil unless regional dialect specified
4. For Welsh: Use formal written Welsh for educational content
5. Maintain the meaning and tone of the original
6. Note any terms that don't have direct equivalents

OUTPUT FORMAT:
- Provide the translation
- Note any terminology decisions
- Suggest alternatives where applicable
""",
        )

        return agent

    def create_extraction_agent(
        schema_type: str = "curriculum",
        max_cost: str | None = None,
    ) -> Agent:
        """
        Create an agent for structured data extraction.

        Args:
            schema_type: Type of schema to extract (curriculum, exam, vocabulary)
            max_cost: Maximum cost per request

        Returns:
            Configured Pydantic AI Agent
        """
        model = select_model_for_task("extraction")
        cost_limit = max_cost or gateway_config.max_cost_per_request

        schema_prompts = {
            "curriculum": """Extract structured curriculum data including:
- Subject name and level
- Learning outcomes (with codes)
- Key concepts and vocabulary
- Assessment criteria
- Cross-curricular links""",
            "exam": """Extract structured exam data including:
- Question number and marks
- Topic/learning outcome reference
- Model answer points
- Marking scheme criteria
- Common mistakes to avoid""",
            "vocabulary": """Extract structured vocabulary data including:
- Term in Irish and English
- Part of speech
- Domain/subject area
- Example usage
- Related terms""",
        }

        agent = Agent(
            model,
            model_settings={
                "max_tokens": gateway_config.max_tokens,
                "temperature": 0.1,  # Low temperature for extraction
                "timeout": gateway_config.timeout,
                "experimental_max_cost_limit": cost_limit,
            },
            system_prompt=f"""You are a data extraction specialist for educational content.

EXTRACTION TASK:
{schema_prompts.get(schema_type, schema_prompts["curriculum"])}

EXTRACTION RULES:
1. Follow the exact schema structure
2. Preserve original language where specified
3. Include source references
4. Mark uncertain extractions with confidence scores
5. Return valid JSON matching the schema
""",
        )

        return agent

    def create_research_agent(
        topic: str = "education",
        max_cost: str | None = None,
    ) -> Agent:
        """
        Create an agent for educational research tasks.

        Args:
            topic: Research topic area
            max_cost: Maximum cost per request

        Returns:
            Configured Pydantic AI Agent
        """
        model = select_model_for_task("research", cost_priority="high")
        cost_limit = max_cost or "$2.00"  # Higher limit for research

        agent = Agent(
            model,
            model_settings={
                "max_tokens": 16384,  # Longer outputs for research
                "temperature": 0.8,
                "timeout": 120,  # Longer timeout
                "experimental_max_cost_limit": cost_limit,
            },
            system_prompt=f"""You are an educational research assistant specializing in {topic}.

RESEARCH CAPABILITIES:
1. Analyze educational policies and curricula
2. Compare approaches across Celtic nations
3. Identify pedagogical patterns and best practices
4. Synthesize findings from multiple sources
5. Generate evidence-based recommendations

CITATION REQUIREMENTS:
- Cite specific documents and sources
- Note publication dates and authorities
- Distinguish between official guidance and interpretation
- Flag areas of uncertainty or ongoing debate

OUTPUT STRUCTURE:
- Executive summary
- Key findings
- Detailed analysis
- Recommendations
- Sources and references
""",
        )

        return agent


# =============================================================================
# Utility Functions
# =============================================================================

def get_model_cost_tier(model: str) -> str:
    """Get the cost tier for a model."""
    return MODEL_CAPABILITIES.get(model, {}).get("cost_tier", "unknown")


def estimate_request_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    """
    Estimate the cost of a request.

    Note: This is an approximation. Actual costs may vary.
    """
    # Approximate pricing per 1M tokens (as of 2024)
    pricing = {
        "gateway/anthropic:claude-opus-4-5-20251101": {"input": 15.0, "output": 75.0},
        "gateway/anthropic:claude-sonnet-4-20250514": {"input": 3.0, "output": 15.0},
        "gateway/google:gemini-2.0-flash": {"input": 0.075, "output": 0.30},
        "gateway/google:gemini-2.5-pro": {"input": 1.25, "output": 5.0},
        "gateway/openai:gpt-4o": {"input": 2.50, "output": 10.0},
        "gateway/openai:gpt-4o-mini": {"input": 0.15, "output": 0.60},
    }

    model_pricing = pricing.get(model, {"input": 1.0, "output": 5.0})

    input_cost = (input_tokens / 1_000_000) * model_pricing["input"]
    output_cost = (output_tokens / 1_000_000) * model_pricing["output"]

    return input_cost + output_cost


# =============================================================================
# Initialization
# =============================================================================

def initialize_gateway() -> None:
    """Initialize the Pydantic AI Gateway with observability."""
    setup_observability()
    logger.info(f"Gateway initialized with default model: {gateway_config.default_model}")
    logger.info(f"Cost limit per request: {gateway_config.max_cost_per_request}")


# Auto-initialize if dependencies available
if HAS_PYDANTIC_AI:
    initialize_gateway()
