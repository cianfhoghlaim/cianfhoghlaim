"""Generators for códeolas documentation."""

from . import arch_generator

# Core arch generator (from shared.codeolas)
from .arch import (
    ArchitectureSection,
    ArchDocument,
    ArchGenerator,
    generate_arch_docs,
)

# RepoSwarm LLM-powered generator (flow-specific)
from .reposwarm import (
    RepoSwarmGenerator,
    generate_architecture_docs,
    ArchSection,
    RepoType,
    GenerationConfig,
    CacheConfig,
    RepoTypeDetector,
    ArchDocCache,
)

__all__ = [
    # Legacy generator
    "arch_generator",
    # Core arch generator
    "ArchitectureSection",
    "ArchDocument",
    "ArchGenerator",
    "generate_arch_docs",
    # RepoSwarm LLM-powered generator
    "RepoSwarmGenerator",
    "generate_architecture_docs",
    "ArchSection",
    "RepoType",
    "GenerationConfig",
    "CacheConfig",
    "RepoTypeDetector",
    "ArchDocCache",
]
