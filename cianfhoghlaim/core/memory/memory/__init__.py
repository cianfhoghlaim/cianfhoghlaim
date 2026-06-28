"""
Memory module for Celtic Education Platform.

Provides:
- CelticMemoryService: Cognee-based memory for linguistic data
- CogneeConfig: Configuration for graph and vector databases
- Education-specific memory features (curriculum, episodic)

Usage:
    from memory import CelticMemoryService, CogneeConfig

    config = CogneeConfig.for_celtic_education()
    service = CelticMemoryService(config)

    # Celtic linguistics
    await service.add_vocabulary(words, language="irish")
    results = await service.search("cognates of teach")

    # Education features via EducationConfig
    await service.add_manuscript(transcription, source="duchas")
"""

from .cognee_config import (
    CelticLanguageConfig,
    CogneeConfig,
    EducationConfig,
    EmbeddingConfig,
    EmbeddingProvider,
    GraphConfig,
    GraphProvider,
    LLMConfig,
    LLMProvider,
    VectorConfig,
    VectorProvider,
    configure_cognee,
    get_cognee_config,
    init_cognee,
)
from .cognee_service import (
    CelticEntity,
    CelticMemoryService,
    CelticRelationship,
    SearchResult,
)

__all__ = [
    # Data classes
    "CelticEntity",
    "CelticLanguageConfig",
    # Main classes
    "CelticMemoryService",
    "CelticRelationship",
    "CogneeConfig",
    "EducationConfig",
    "EmbeddingConfig",
    "EmbeddingProvider",
    # Config components
    "GraphConfig",
    # Enums
    "GraphProvider",
    "LLMConfig",
    "LLMProvider",
    "SearchResult",
    "VectorConfig",
    "VectorProvider",
    # Helper functions
    "configure_cognee",
    "get_cognee_config",
    "init_cognee",
]
