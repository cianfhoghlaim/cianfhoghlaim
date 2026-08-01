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

from .generator import RepoSwarmGenerator, generate_architecture_docs
from .types import (
    ArchSection,
    ArchDocument,
    RepoType,
    GenerationConfig,
    CacheConfig,
)
from .detector import RepoTypeDetector
from .cache import ArchDocCache

__all__ = [
    # Main API
    "RepoSwarmGenerator",
    "generate_architecture_docs",
    # Types
    "ArchSection",
    "ArchDocument",
    "RepoType",
    "GenerationConfig",
    "CacheConfig",
    # Components
    "RepoTypeDetector",
    "ArchDocCache",
]
