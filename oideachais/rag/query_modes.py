"""
Query Modes for Curriculum RAG.

Six query modes adapted from LightRAG for curriculum-specific retrieval,
plus two curriculum-specific modes for prerequisite chains and assessment alignment.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal


class CurriculumQueryMode(str, Enum):
    """
    Six query modes adapted from LightRAG for curriculum.

    Standard LightRAG modes:
    - LOCAL: Entity-focused retrieval for specific concepts
    - GLOBAL: Relationship-focused retrieval for connections
    - HYBRID: Combined LOCAL + GLOBAL
    - NAIVE: Pure vector search, no graph
    - MIX: Knowledge graph + vector chunks (default)

    Curriculum-specific modes:
    - PREREQUISITE: Follow prerequisite chains
    - ASSESSMENT: Learning outcome → exam question mapping
    """

    # Standard LightRAG modes
    LOCAL = "local"
    GLOBAL = "global"
    HYBRID = "hybrid"
    NAIVE = "naive"
    MIX = "mix"

    # Curriculum-specific modes
    PREREQUISITE = "prerequisite"
    ASSESSMENT = "assessment"


@dataclass
class CurriculumQueryParam:
    """
    Query parameters with curriculum-specific options.

    Based on LightRAG QueryParam with additions for:
    - Subject/level filtering
    - Search weighting configuration
    - Conversation context for multi-turn queries
    """

    # Query mode
    mode: CurriculumQueryMode = CurriculumQueryMode.MIX

    # Result limits
    top_k: int = 10

    # Token budgets (LightRAG pattern)
    max_entity_tokens: int = 4000
    max_relation_tokens: int = 4000
    max_total_tokens: int = 12000

    # Curriculum filters
    subject_filter: str | None = None
    level_filter: Literal["junior", "senior", "primary"] | None = None
    year_filter: str | None = None
    strand_filter: str | None = None

    # Search weighting (genizah pattern)
    semantic_weight: float = 0.7
    keyword_weight: float = 0.3

    # Graph traversal (for PREREQUISITE mode)
    max_hop_depth: int = 3

    # Assessment alignment (for ASSESSMENT mode)
    include_marking_schemes: bool = True
    exam_years: list[int] | None = None

    # Conversation context for multi-turn
    conversation_history: list[dict[str, Any]] = field(default_factory=list)

    # Caching
    use_cache: bool = True
    cache_ttl_seconds: int = 3600

    # Reranking
    apply_reranking: bool = True
    reranker_model: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "mode": self.mode.value,
            "top_k": self.top_k,
            "max_entity_tokens": self.max_entity_tokens,
            "max_relation_tokens": self.max_relation_tokens,
            "max_total_tokens": self.max_total_tokens,
            "subject_filter": self.subject_filter,
            "level_filter": self.level_filter,
            "year_filter": self.year_filter,
            "strand_filter": self.strand_filter,
            "semantic_weight": self.semantic_weight,
            "keyword_weight": self.keyword_weight,
            "max_hop_depth": self.max_hop_depth,
            "include_marking_schemes": self.include_marking_schemes,
            "exam_years": self.exam_years,
            "use_cache": self.use_cache,
            "apply_reranking": self.apply_reranking,
        }

    @classmethod
    def for_concept_lookup(cls, subject: str | None = None) -> CurriculumQueryParam:
        """Create params optimized for concept lookups."""
        return cls(
            mode=CurriculumQueryMode.LOCAL,
            top_k=5,
            subject_filter=subject,
            semantic_weight=0.8,
            keyword_weight=0.2,
        )

    @classmethod
    def for_prerequisite_chain(
        cls,
        subject: str,
        max_depth: int = 5,
    ) -> CurriculumQueryParam:
        """Create params for prerequisite chain traversal."""
        return cls(
            mode=CurriculumQueryMode.PREREQUISITE,
            subject_filter=subject,
            max_hop_depth=max_depth,
            semantic_weight=0.5,
            keyword_weight=0.5,
        )

    @classmethod
    def for_exam_preparation(
        cls,
        subject: str,
        level: Literal["junior", "senior"],
        years: list[int] | None = None,
    ) -> CurriculumQueryParam:
        """Create params for exam preparation queries."""
        return cls(
            mode=CurriculumQueryMode.ASSESSMENT,
            subject_filter=subject,
            level_filter=level,
            exam_years=years,
            include_marking_schemes=True,
            top_k=15,
        )

    @classmethod
    def for_exploration(cls) -> CurriculumQueryParam:
        """Create params for open-ended exploration."""
        return cls(
            mode=CurriculumQueryMode.HYBRID,
            top_k=20,
            semantic_weight=0.6,
            keyword_weight=0.4,
        )
