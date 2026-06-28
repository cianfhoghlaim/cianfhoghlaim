"""Generators for códeolas documentation."""

# Core arch generator
from .arch import (
    ArchDocument,
    ArchGenerator,
    ArchitectureSection,
    generate_arch_docs,
)

# Changelog generator (stub; see STATUS.md)
from .changelog import ChangelogGenerator

# RepoSwarm LLM-powered generator (flow-specific)
from .reposwarm import (
    ArchDocCache,
    ArchSection,
    CacheConfig,
    GenerationConfig,
    RepoSwarmGenerator,
    RepoType,
    RepoTypeDetector,
    generate_architecture_docs,
)

__all__ = [
    "ArchDocCache",
    "ArchDocument",
    "ArchGenerator",
    "ArchSection",
    # Core arch generator
    "ArchitectureSection",
    "CacheConfig",
    # Changelog generator
    "ChangelogGenerator",
    "GenerationConfig",
    # RepoSwarm LLM-powered generator
    "RepoSwarmGenerator",
    "RepoType",
    "RepoTypeDetector",
    "generate_arch_docs",
    "generate_architecture_docs",
]
