"""
FireCrawl scraping configurations for Celtic education data.

This module provides scraping configurations for:

Education Sources (Ireland):
- curriculumonline.ie - Irish curriculum specifications
- ncca.ie - National Council for Curriculum and Assessment
- examinations.ie - State Examinations Commission
- oide.ie - Education support services

Celtic Language Sources:
- duchas.ie - Schools Collection (740k handwritten pages)
- canuint.ie - Irish dialect recordings
- hiddenheritages.ai - AI-transcribed folklore

British Isles Statistics:
- ONS Census 2021 (England/Wales)
- NRS Census 2022 (Scotland)
- CSO Census 2022 (Ireland)
- Crown Dependencies (Isle of Man, Jersey, Guernsey)

Configuration Files:
- scraping_config.yaml - Main configuration (515 lines)
- curriculumonline.yaml - Curriculum Online patterns
- ncca.yaml - NCCA patterns
- examinations.yaml - Examinations.ie patterns

JSON Discovery Results:
- curriculum_index.json - Curriculum site map
- curriculum_oide.json - OIDE resources
- ncca.json - NCCA structure
- examinations.ie.json - Exam materials
- duchas.json - Folklore collections
- canuint.json - Dialect recordings
- hiddenheritages.json - HTR transcriptions

Usage:
    from firecrawl import load_scraping_config, get_source_config

    # Load main config
    config = load_scraping_config()

    # Get specific source configuration
    duchas_config = get_source_config("duchas_ie")
    canuint_config = get_source_config("canuint_ie")
"""

from pathlib import Path
from typing import Any

import yaml


def get_config_path() -> Path:
    """Get path to firecrawl config directory."""
    return Path(__file__).parent


def load_scraping_config() -> dict[str, Any]:
    """
    Load the main scraping configuration.

    Returns:
        Dictionary with all source configurations
    """
    config_path = get_config_path() / "scraping_config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


def get_source_config(source_name: str) -> dict[str, Any] | None:
    """
    Get configuration for a specific source.

    Args:
        source_name: Source identifier (e.g., "duchas_ie", "canuint_ie")

    Returns:
        Source configuration dict or None if not found
    """
    config = load_scraping_config()
    return config.get("sources", {}).get(source_name)


def load_discovery_results(source_name: str) -> dict[str, Any] | None:
    """
    Load JSON discovery results for a source.

    Args:
        source_name: Source identifier (e.g., "duchas", "canuint")

    Returns:
        Discovery results dict or None if file not found
    """
    import json

    json_path = get_config_path() / f"{source_name}.json"
    if json_path.exists():
        with open(json_path) as f:
            return json.load(f)
    return None


def get_rate_limits(source_name: str) -> dict[str, float] | None:
    """
    Get rate limiting configuration for a source.

    Args:
        source_name: Source identifier

    Returns:
        Rate limit configuration or None
    """
    config = load_scraping_config()
    return config.get("scraping_strategy", {}).get("rate_limits", {}).get(source_name)


def get_litellm_model(task: str) -> str:
    """
    Get recommended LiteLLM model for a task.

    Args:
        task: Task type (extraction, ocr, vision, agent)

    Returns:
        Model identifier string
    """
    config = load_scraping_config()
    models = config.get("litellm", {}).get("models", {})
    return models.get(task, {}).get("default", "gemini-2.5-flash")


# Source constants for easy access
EDUCATION_SOURCES = [
    "curriculumonline",
    "ncca",
    "examinations",
    "oide",
]

CELTIC_SOURCES = [
    "duchas_ie",
    "canuint_ie",
    "hidden_heritages_ai",
]

STATISTICS_SOURCES = [
    "ons_census_2021",
    "nrs_census_2022",
    "cso_census_2022",
    "crown_dependencies",
]

# Dialect mappings from canuint.ie
DIALECT_REGIONS = {
    "munster": {
        "baronies": [71, 72, 73, 74, 75],
        "description": "Gaeilge na Mumhan",
        "counties": ["Clare", "Kerry", "Cork", "Waterford"],
    },
    "connacht": {
        "baronies": [55, 56, 57, 90, 91, 92],
        "description": "Gaeilge Chonnacht",
        "counties": ["Galway", "Mayo", "Roscommon"],
    },
    "ulster": {
        "baronies": [101, 102, 103, 104, 105],
        "description": "Gaeilge Uladh",
        "counties": ["Donegal"],
    },
}

__all__ = [
    "CELTIC_SOURCES",
    "DIALECT_REGIONS",
    "EDUCATION_SOURCES",
    "STATISTICS_SOURCES",
    "get_config_path",
    "get_litellm_model",
    "get_rate_limits",
    "get_source_config",
    "load_discovery_results",
    "load_scraping_config",
]
