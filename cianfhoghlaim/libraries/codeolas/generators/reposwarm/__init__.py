"""
RepoSwarm Architecture Documentation Generator.

Generates comprehensive architecture documentation using LLM analysis.
Based on RepoSwarm patterns with adaptations for local infrastructure.

Features:
- Multi-provider LLM support via LLMRouter
- DuckDB caching with TTL
- Repo type-specific prompt templates
- Mermaid diagram generation
"""

from .cache import ArchDocCache
from .detector import RepoTypeDetector
from .generator import RepoSwarmGenerator, generate_architecture_docs
from .types import (
    ArchDocument,
    ArchSection,
    CacheConfig,
    GenerationConfig,
    RepoType,
)

__all__ = [
    "ArchDocCache",
    "ArchDocument",
    # Types
    "ArchSection",
    "CacheConfig",
    "GenerationConfig",
    # Main API
    "RepoSwarmGenerator",
    "RepoType",
    # Components
    "RepoTypeDetector",
    "generate_architecture_docs",
]
