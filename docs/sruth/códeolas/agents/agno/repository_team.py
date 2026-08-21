"""
Repository Analysis Team - Agno Multi-Agent Coordination.

DEPRECATED: This module is deprecated. Repository analysis capabilities
have been migrated to crypteolas ADK agents.

Update imports:
- from sruth.crypteolas.agents.adk import architecture_agent, code_analysis_agent

The functionality has been split:
- Code search → sruth.crypteolas.agents.adk.code_analysis
- Architecture analysis → sruth.crypteolas.agents.adk.architecture_agent
- Dependency analysis → sruth.crypteolas.agents.adk.architecture_agent
- Documentation → sruth.crypteolas.agents.adk.documentation_agent
"""

import warnings

warnings.warn(
    "sruth.códeolas.agents.agno.repository_team is deprecated. "
    "Use sruth.crypteolas.agents.adk agents instead: "
    "architecture_agent, code_analysis_agent, documentation_agent.",
    DeprecationWarning,
    stacklevel=2,
)

# Minimal re-export for backward compatibility with Pydantic models
from pydantic import BaseModel, Field
from typing import List, Optional


class CodeSearchResult(BaseModel):
    """Result from code search."""
    query: str
    results: List[dict] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    total_matches: int = 0


class ArchitectureReport(BaseModel):
    """Architecture analysis report."""
    directory: str
    summary: str
    key_modules: List[dict] = Field(default_factory=list)
    entry_points: List[str] = Field(default_factory=list)
    dependencies: dict = Field(default_factory=dict)
    architecture_pattern: Optional[str] = None
    recommendations: List[str] = Field(default_factory=list)


class DependencyAnalysis(BaseModel):
    """Dependency analysis result."""
    target: str
    target_type: str  # function, class, file
    callers: List[dict] = Field(default_factory=list)
    callees: List[dict] = Field(default_factory=list)
    dependency_count: int = 0
    complexity_score: Optional[float] = None


class DocumentationResult(BaseModel):
    """Documentation generation result."""
    file_path: str
    doc_type: str  # module, function, class, architecture
    content: str
    format: str = "markdown"


class RepositoryResponse(BaseModel):
    """Unified response from repository team."""
    query: str
    summary: str
    code_search: Optional[CodeSearchResult] = None
    architecture: Optional[ArchitectureReport] = None
    dependencies: Optional[DependencyAnalysis] = None
    documentation: Optional[DocumentationResult] = None
    follow_up_suggestions: List[str] = Field(default_factory=list)


# Stub functions that raise deprecation warnings
def ask_repository_team(*args, **kwargs):
    """DEPRECATED: Use crypteolas ADK agents instead."""
    raise NotImplementedError(
        "repository_team is deprecated. Use crypteolas ADK agents: "
        "from sruth.crypteolas.agents.adk import architecture_agent, code_analysis_agent"
    )


def search_code(*args, **kwargs):
    """DEPRECATED: Use crypteolas code_analysis_agent instead."""
    raise NotImplementedError(
        "search_code is deprecated. Use: "
        "from sruth.crypteolas.agents.adk import code_analysis_agent"
    )


def get_architecture(*args, **kwargs):
    """DEPRECATED: Use crypteolas architecture_agent instead."""
    raise NotImplementedError(
        "get_architecture is deprecated. Use: "
        "from sruth.crypteolas.agents.adk import architecture_agent"
    )


def analyze_dependencies(*args, **kwargs):
    """DEPRECATED: Use crypteolas architecture_agent instead."""
    raise NotImplementedError(
        "analyze_dependencies is deprecated. Use: "
        "from sruth.crypteolas.agents.adk import architecture_agent"
    )


__all__ = [
    # Models still exported for backward compatibility
    "CodeSearchResult",
    "ArchitectureReport",
    "DependencyAnalysis",
    "DocumentationResult",
    "RepositoryResponse",
    # Deprecated functions
    "ask_repository_team",
    "search_code",
    "get_architecture",
    "analyze_dependencies",
]
