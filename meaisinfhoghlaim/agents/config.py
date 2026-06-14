"""
Configuration for Celtic Education ADK Agents.

Provides model settings, connection parameters, and language configuration
for the unified Celtic Education Platform.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class AgentConfig:
    """Configuration for Celtic Education AI agents."""

    # Model settings
    model_name: str = "gemini-2.0-flash"
    temperature: float = 0.7
    max_output_tokens: int = 8192

    # Storage connections
    lancedb_uri: str = field(
        default_factory=lambda: os.getenv("LANCEDB_URI", "./storage/data/lancedb")
    )
    neo4j_uri: str = field(
        default_factory=lambda: os.getenv("NEO4J_URI", "bolt://localhost:7687")
    )
    neo4j_user: str = field(default_factory=lambda: os.getenv("NEO4J_USER", "neo4j"))
    neo4j_password: str = field(
        default_factory=lambda: os.getenv("NEO4J_PASSWORD", "")
    )
    duckdb_path: str = field(
        default_factory=lambda: os.getenv(
            "DUCKDB_PATH", "./storage/data/celtic_education.duckdb"
        )
    )
    ducklake_path: str = field(
        default_factory=lambda: os.getenv("DUCKLAKE_PATH", "./storage/data/ducklake")
    )

    # Supported languages (Celtic + English)
    supported_languages: list[str] = field(
        default_factory=lambda: ["ga", "gd", "cy", "br", "gv", "kw", "en"]
    )

    # Translation model settings
    translation_models: dict = field(
        default_factory=lambda: {
            "opus_mt": "Helsinki-NLP/opus-mt-{src}-{tgt}",
            "m2m100": "facebook/m2m100_418M",
            "nllb": "facebook/nllb-200-distilled-600M",
        }
    )

    # Embedding model
    embedding_model: str = "BAAI/bge-m3"
    embedding_dim: int = 1024

    # API keys (from environment)
    google_api_key: str | None = field(
        default_factory=lambda: os.getenv("GOOGLE_API_KEY")
    )
    anthropic_api_key: str | None = field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY")
    )
    openai_api_key: str | None = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY")
    )

    # Agent behavior
    max_research_iterations: int = 3
    max_search_results: int = 10
    enable_grounding: bool = True

    # Education-specific settings
    curriculum_nations: list[str] = field(
        default_factory=lambda: ["ireland", "scotland", "wales", "england", "northern_ireland"]
    )
    default_curriculum: str = "ireland"


# Global config instance
config = AgentConfig()


# Language display names
LANGUAGE_NAMES = {
    "ga": "Irish (Gaeilge)",
    "gd": "Scottish Gaelic (Gàidhlig)",
    "cy": "Welsh (Cymraeg)",
    "br": "Breton (Brezhoneg)",
    "gv": "Manx (Gaelg)",
    "kw": "Cornish (Kernewek)",
    "en": "English",
    "sga": "Old Irish",
    "mga": "Middle Irish",
}


# Translation pair support
TRANSLATION_PAIRS = {
    # Irish pairs
    ("en", "ga"): ["opus_mt", "m2m100", "nllb"],
    ("ga", "en"): ["opus_mt", "m2m100", "nllb"],
    # Scottish Gaelic pairs
    ("en", "gd"): ["m2m100", "nllb"],
    ("gd", "en"): ["m2m100", "nllb"],
    # Welsh pairs
    ("en", "cy"): ["opus_mt", "m2m100", "nllb"],
    ("cy", "en"): ["opus_mt", "m2m100", "nllb"],
    # Inter-Celtic pairs
    ("ga", "gd"): ["m2m100"],  # Goidelic
    ("gd", "ga"): ["m2m100"],
    ("cy", "br"): ["m2m100"],  # Brythonic
    ("br", "cy"): ["m2m100"],
}


# Curriculum domains
CURRICULUM_DOMAINS = {
    "primary": "Primary Education (Ages 4-12)",
    "junior_cycle": "Junior Cycle (Ages 12-15)",
    "senior_cycle": "Senior Cycle (Ages 15-18)",
    "leaving_cert": "Leaving Certificate",
    "special_education": "Special Education Needs",
}


# Education levels by nation
EDUCATION_LEVELS = {
    "ireland": ["primary", "junior_cycle", "senior_cycle", "leaving_cert"],
    "scotland": ["early_years", "primary", "secondary", "highers", "advanced_highers"],
    "wales": ["foundation", "key_stage_2", "key_stage_3", "key_stage_4", "a_level"],
    "england": ["eyfs", "key_stage_1", "key_stage_2", "gcse", "a_level"],
    "northern_ireland": ["foundation", "key_stage_1", "key_stage_2", "gcse", "a_level"],
}


def get_language_name(code: str) -> str:
    """Get display name for a language code."""
    return LANGUAGE_NAMES.get(code, code)


def get_translation_models(source: str, target: str) -> list[str]:
    """Get available translation models for a language pair."""
    return TRANSLATION_PAIRS.get((source, target), ["m2m100", "nllb"])


def get_education_levels(nation: str) -> list[str]:
    """Get education levels for a nation."""
    return EDUCATION_LEVELS.get(nation, EDUCATION_LEVELS["ireland"])


# Curriculum frameworks by nation
CURRICULUM_FRAMEWORKS = {
    "ireland": {
        "name": "Irish National Curriculum",
        "authority": "NCCA (National Council for Curriculum and Assessment)",
        "levels": ["Primary", "Junior Cycle", "Senior Cycle/Leaving Certificate"],
        "languages": ["English", "Irish (Gaeilge)"],
        "assessment": "Junior Certificate, Leaving Certificate (CAO points)",
    },
    "england": {
        "name": "National Curriculum for England",
        "authority": "Department for Education",
        "levels": ["EYFS", "KS1", "KS2", "KS3", "KS4 (GCSE)", "KS5 (A-Level)"],
        "languages": ["English"],
        "assessment": "SATs, GCSEs, A-Levels",
    },
    "scotland": {
        "name": "Curriculum for Excellence (CfE)",
        "authority": "Education Scotland",
        "levels": ["Early Level", "First Level", "Second Level", "Third Level", "Fourth Level", "Senior Phase"],
        "languages": ["English", "Gaelic (Gàidhlig)"],
        "assessment": "National 4, National 5, Higher, Advanced Higher",
    },
    "wales": {
        "name": "Curriculum for Wales",
        "authority": "Welsh Government",
        "levels": ["Foundation", "KS2", "KS3", "KS4 (GCSE)", "KS5 (A-Level)"],
        "languages": ["English", "Welsh (Cymraeg)"],
        "assessment": "GCSEs (WJEC), A-Levels, Welsh Baccalaureate",
    },
    "northern_ireland": {
        "name": "Northern Ireland Curriculum",
        "authority": "CCEA (Council for the Curriculum, Examinations and Assessment)",
        "levels": ["Foundation Stage", "KS1", "KS2", "KS3", "KS4 (GCSE)", "KS5 (A-Level)"],
        "languages": ["English", "Irish (optional)"],
        "assessment": "GCSEs (CCEA), A-Levels",
    },
}


def get_curriculum_framework(nation: str) -> dict:
    """Get curriculum framework details for a nation."""
    return CURRICULUM_FRAMEWORKS.get(nation, CURRICULUM_FRAMEWORKS["ireland"])
