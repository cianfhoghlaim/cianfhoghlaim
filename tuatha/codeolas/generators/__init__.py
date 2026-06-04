"""Generators for códeolas documentation."""

# Core arch generator
from .arch import (
    ArchitectureSection,
    ArchDocument,
    ArchGenerator,
    generate_arch_docs,
)

# Changelog generator (stub; see STATUS.md)
from .changelog import ChangelogGenerator

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
    # Core arch generator
    "ArchitectureSection",
    "ArchDocument",
    "ArchGenerator",
    "generate_arch_docs",
    # Changelog generator
    "ChangelogGenerator",
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
